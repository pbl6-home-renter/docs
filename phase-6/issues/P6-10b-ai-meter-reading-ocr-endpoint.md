# P6-10b — `POST /ai/meter-readings/ocr`: đọc số công tơ bằng Claude vision

**Epic:** [P6-10](P6-10-ai-service-meter-ocr.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** baoduong17  
**Người review:** huynhtiennhat0403  
**Ước lượng:** 3 points · 6–8 giờ  
**Phụ thuộc:** P6-10a, P6-09 (contract `paths/ai/`)  
**Repo / branch:** `ai-service` · `feature/p6-10b-meter-ocr`  
**Iteration:** It6 (09/11–15/11)  
**Issue:** `docs#109`

> Đọc `AGENTS.md` + `.agents/skills/` của repo trước khi code.

## Mục tiêu

Landlord gửi ảnh công tơ, nhận `200 METER_READING_OCR_COMPLETED` với `{ value: "01234.5", confidence: 0.92 }` trong ≤ 15 s; ảnh không đọc được thì `value: null` (không phải lỗi).

## Quyết định áp dụng

- `P6-D67` — vision LLM, structured output, ảnh JPEG/PNG/WebP ≤ 5 MB, timeout 15 s, chỉ gợi ý, không lưu ảnh/kết quả.
- `P1-D35` — FE luôn cho sửa tay; service không cần "đoán" khi ảnh mờ — trả `null`.
- `P6-D65` — số là string decimal (không trả `number`).

## Contract

- `api-docs/src/paths/ai/ai-meter-readings-ocr.yaml` (tạo ở P6-09).
- Request `multipart/form-data`: `image` (file), `meterType: electricity | water`.
- Response `200 METER_READING_OCR_COMPLETED`: `{ value: string | null, confidence: number (0–1), meterType }`.
- Lỗi: `401`, `403` (không phải landlord), `413 IMAGE_TOO_LARGE`, `415 MEDIA_TYPE_NOT_ALLOWED`, `422 VALIDATION_FAILED` (thiếu `image`/sai `meterType`), `429 TOO_MANY_REQUESTS` (gateway), `502 OCR_UNAVAILABLE` (lỗi Claude API), `504 OCR_TIMEOUT`.

### Mapping field

| Field | Nguồn | Ghi chú |
|---|---|---|
| `image` | multipart | kiểm tra MIME bằng magic bytes, không tin `Content-Type` client gửi |
| `meterType` | multipart | enum |
| `value` | structured output của model | regex `^\d+(\.\d+)?$`; sai định dạng → `null` |
| `confidence` | structured output | clamp 0–1 |

## Tham chiếu code

- Module mẫu: `boilerplate/src/modules/sample/` (layout command/controller/exception); không cần repository.
- Error envelope + response code: theo skill `be-api-presentation`.
- Claude SDK: `@anthropic-ai/sdk`, tài liệu vision (ảnh base64) và structured outputs (`output_config.format` với JSON schema). Đọc tài liệu chính thức, không đoán chữ ký hàm.

## Các bước triển khai

### Bước 1 — Port + adapter

- **Cách làm:**
  - Port trong `application/`: `IMeterOcrEngine.read({ image: Buffer, mediaType, meterType }): Promise<{ value: string | null; confidence: number }>`.
  - Adapter trong `infrastructure/`: `ClaudeMeterOcrEngine` dùng `@anthropic-ai/sdk`.
    - Model lấy từ env `AI_OCR_MODEL`, mặc định `claude-haiku-5-5` (rẻ, đủ cho đọc số). Không hard-code key; `ANTHROPIC_API_KEY` từ env.
    - Client `timeout: 15_000` (ms), `maxRetries: 0` (để tổng thời gian không vượt 15 s).
    - Gửi ảnh dạng `{ type: "image", source: { type: "base64", media_type, data } }` + prompt ngắn: đọc dãy số trên mặt công tơ `<meterType>`, bỏ qua số seri/nhãn, chữ số màu đỏ là phần thập phân; không chắc thì trả `value: null`.
    - Structured output JSON schema `{ value: string|null, confidence: number }`, `additionalProperties: false`.
    - Kiểm tra `stop_reason`: `refusal` hoặc `max_tokens` → coi như `value: null, confidence: 0`.
    - Lỗi SDK: bắt theo class (`Anthropic.APIConnectionTimeoutError` → `OcrTimeoutException`; `Anthropic.RateLimitError`/`APIError` → `OcrUnavailableException`). Đây là chỗ **duy nhất** được try/catch — để chuyển lỗi hạ tầng thành domain exception, không phải để log.
- **Kiểm tra bước:** script tạm (không commit) gọi adapter với 3 ảnh mẫu trong thư mục `samples/` (chụp công tơ điện cơ, công tơ điện tử, công tơ nước) → in kết quả; ghi bảng kết quả vào PR.

### Bước 2 — Command + controller

- **Cách làm:** command `meter-reading-ocr` (theo skill `be-naming`), controller `POST /ai/meter-readings/ocr`, `@Roles('landlord')`, `FileInterceptor('image', { limits: { fileSize: 5 * 1024 * 1024 } })`. Kiểm tra magic bytes (JPEG `FF D8 FF`, PNG `89 50 4E 47`, WebP `RIFF....WEBP`).
- **Kiểm tra bước:**
  ```bash
  curl -H "Authorization: Bearer $LANDLORD" -F image=@samples/elec-1.jpg -F meterType=electricity \
    http://localhost:3005/api/v1/ai/meter-readings/ocr
  # → 200 {"code":"METER_READING_OCR_COMPLETED","data":{"value":"...","confidence":...}}
  ```

### Bước 3 — Lỗi và giới hạn

- **Kiểm tra bước:**
  - File 6 MB → `413 IMAGE_TOO_LARGE`.
  - File `.pdf` đổi đuôi `.jpg` → `415 MEDIA_TYPE_NOT_ALLOWED`.
  - `meterType=gas` → `422 VALIDATION_FAILED`.
  - Ảnh không phải công tơ (ảnh phòng) → `200` với `value: null`.
  - `ANTHROPIC_API_KEY` sai → `502 OCR_UNAVAILABLE`; đặt `AI_OCR_TIMEOUT_MS=1` → `504 OCR_TIMEOUT`.
  - Log không chứa ảnh base64 hay API key.

### Bước 4 — Swagger, `api-docs`, deploy

- **Kiểm tra bước:** Swagger khớp `api-docs/src/paths/ai/ai-meter-readings-ocr.yaml`; gọi qua gateway staging với ảnh mẫu → `200`.

## Ngoài phạm vi

- Lưu ảnh hoặc kết quả OCR (Tenancy lưu `ocrValue`, Identity lưu ảnh — `P6-D66`).
- Fallback sang model khác khi model chính từ chối.
- So sánh với chỉ số kỳ trước (Tenancy làm).

## Acceptance

- [ ] Happy path với 3 ảnh mẫu, bảng kết quả (giá trị thật / OCR / confidence) đính kèm PR.
- [ ] 6 case lỗi ở Bước 3 đúng mã.
- [ ] Thời gian phản hồi p95 trên 10 lần gọi ≤ 15 s (ghi số đo vào PR).
- [ ] Không token → `401`; token tenant → `403`.

## Definition of Done

- [ ] `npm run build` + `npm run lint` pass; không có file test; không sửa `src/shared`.
- [ ] Endpoint `x-apidog-status: released`, có sequence diagram.
- [ ] PR ghi `Closes pbl6-home-renter/docs#<số>`.
