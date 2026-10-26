# P6-02h — OCR preview chỉ số công tơ *(outline — It6)*

**Epic:** [P6-02](P6-02-tenancy-billing-vertical-slice.md)  
**Trạng thái:** ⚪ Outline — **chờ BE Lead chốt phương án OCR**  
**Người phụ trách:** huynhtiennhat0403 (đề xuất)  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** ~5 points (ước lượng lại sau khi chốt OCR)  
**Phụ thuộc:** P6-02e, Media presign upload (baoduong17, It5), quyết định OCR  
**Repo:** `Tenancy-Service`  
**Issue:** `docs#TBD`

## Mục tiêu

Landlord chụp ảnh công tơ → server đọc ra con số gợi ý → landlord **xác nhận hoặc sửa tay** rồi mới ghi bằng `POST /meter-readings` (F5: OCR + xác nhận tay; D35: OCR sai/mờ → sửa tay). Endpoint này **chỉ preview, không ghi DB**.

## Contract

- `POST /meter-readings/preview-ocr-result` — `api-doc/src/paths/billing/meter-readings-preview-ocr-result.yaml` (`postMeterReadingsPreviewOcrResult`).
- Request `api-doc/src/requests/rooms/ocr-meter-reading-preview-request-dto.yaml`: `roomId`, `mediaId`, `type`.
- Response `api-doc/src/responses/dtos/rooms/ocr-meter-reading-preview-response-dto.yaml`, code `OCR_RESULT_PREVIEWED`.
- Lỗi: `422 OCR_RESULT_INVALID`, `EVIDENCE_REQUIRED`, `VALIDATION_FAILED`.

## Quyết định cần chốt (BE Lead)

Theo `pm/phase-3/discovery/microservices-architecture.md` §2.3 (AI đã bỏ, OCR "chờ PM chốt"):

| Phương án | Ưu | Nhược |
|---|---|---|
| A. Tesseract chạy trong `tenancy-service` (`tesseract.js` hoặc binary trong Docker image) | Không cần service mới, không tốn API key | Độ chính xác với công tơ cơ (số lăn) thấp; tăng RAM EC2 |
| B. Gọi API vision LLM (OpenAI/Gemini) qua adapter | Chính xác hơn | Cần key/ngân sách (rủi ro R1 trong `PROJECT_PLAN.md`) |
| C. Bỏ OCR khỏi MVP, chỉ nhập tay + ảnh chứng cứ | Không rủi ro | Mất một điểm nhấn của `requirement.md` |

## Các bước chính (sau khi chốt)

1. Lấy file ảnh theo `mediaId` (media service/identity — phụ thuộc thiết kế Media upload).
2. Adapter `OcrPort` (`src/modules/meter-reading/application/ports/ocr.port.ts`) + implementation theo phương án đã chọn — để đổi provider không phải sửa handler.
3. Chuẩn hóa kết quả: chỉ giữ chữ số, so với `currentReading` kỳ trước; nhỏ hơn hoặc không đọc được → `422 OCR_RESULT_INVALID` kèm gợi ý nhập tay.
4. Timeout + giới hạn kích thước ảnh; không lưu kết quả OCR.
5. Sequence diagram + `released`.
