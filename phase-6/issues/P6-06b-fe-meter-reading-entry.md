# P6-06b — Nhập chỉ số điện nước theo tòa và kỳ, kèm ảnh minh chứng (Web)

**Epic:** [P6-06](P6-06-fe-contract-invoice-screens.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** ThaiBao11125  
**Người review:** baoduong17  
**Ước lượng:** 3 points · 6–8 giờ  
**Phụ thuộc:** BE P6-02e (`POST/GET /meter-readings`), P6-02f (`POST /meter-readings/bulk`), P6-02h (`source`/`ocrValue`, `evidenceMediaId`, baseline kỳ đầu, `PATCH` có khóa kỳ); FE P6-03c (API phòng)
**Repo / branch:** `fe` · `feat/p6-06b-meter-reading-entry`  
**Iteration:** It6 (09/11–15/11)  
**Issue:** `docs#103`

> **Đọc trước khi code:** `fe/AGENTS.md` và skill trong `fe/.agents/skills/` (`fe-feature-workflow` → `fe-structure` → `fe-code-style` → `fe-ui-ux` + `references/*`), `fe/docs/media-upload-guide.md`. Issue **không** quy định cách đặt file, đặt tên hay style — nếu issue nói khác skill thì làm theo skill. Nguồn mâu thuẫn xử lý theo [`P6-D75`](../decisions.md#d75--thứ-tự-ưu-tiên-nguồn-và-cách-xử-lý-câu-hỏi-mở): `decisions.md` > `api-docs` > skill > issue.

## Mục tiêu

Landlord mở **Chỉ số điện nước**, chọn tòa + kỳ (`YYYY-MM`), thấy bảng mọi phòng có HĐ với chỉ số cũ/mới của điện và nước; nhập tay hoặc chụp ảnh để AI gợi ý số, xác nhận rồi lưu (từng phòng hoặc cả tòa một lần). Mỗi chỉ số đã lưu có ảnh minh chứng; phòng có hóa đơn đã phát hành của kỳ thì hiện **Đã khóa**.

## Quyết định áp dụng

- `P6-D70` — response reading có `evidenceMediaId` (null = chưa có ảnh) → FE biết trạng thái ảnh sau F5; sau khi upload ảnh gọi `PATCH /meter-readings/{id} { evidenceMediaId }`; chỉ sửa được reading **mới nhất** của phòng + loại (`409 METER_READING_NOT_LATEST`); không có xóa; bulk remains atomic; a missing baseline returns `BASELINE_REQUIRED` and rolls back all submitted readings (P6-D60); kỳ đầu `previous` = chỉ số bàn giao.
- `P6-D66` — giữ bulk; không gửi `evidenceMediaId` lúc tạo; ảnh minh chứng upload **sau** khi tạo reading (`ownerType=meter_reading`, `ownerId=<readingId>`, `purpose=meter_reading_evidence`), FE bắt buộc có ảnh; thêm `source: manual|ocr`, `ocrValue?`; kỳ (`period`) là khóa, không có `readingDate`; sửa bị chặn khi kỳ đã có hóa đơn `issued` → `409 PERIOD_ALREADY_INVOICED`.
- `P6-D67` mô tả OCR ở `ai-service`, nhưng endpoint OCR không nằm trong backlog/API contract đang dùng cho issue này. Không tự gọi endpoint đó; chỉ triển khai nhập tay với `source=manual`. Mở rộng OCR cần flow/API được PM và API owner xác nhận riêng.
- `P6-D69` — upload sau khi có id thật.
- `P1-D35` — luôn phải có ảnh công tơ làm minh chứng.
- `P6-D65` — chỉ số là string decimal, không ép `number`.

## Contract

| Endpoint | Thành công | Lỗi cần xử lý trên UI |
|---|---|---|
| `GET /meter-readings?filter[buildingId]&filter[period]` (`api-docs/src/paths/billing/meter-readings.yaml`, `getMeterReadings`) | `200 METER_READINGS_FETCHED` | `422 VALIDATION_FAILED` |
| `POST /meter-readings` (`postMeterReadings`) | `201 METER_READING_CREATED` | `409 DUPLICATE_METER_READING`, `422 CURRENT_READING_INVALID`, `BASELINE_REQUIRED`, `VALIDATION_FAILED` |
| `POST /meter-readings/bulk` (`meter-readings-bulk.yaml`, `postBulkMeterReadings`) | `201 METER_READINGS_BULK_RECORDED` (`results[]` có `electricityReadingId`, `waterReadingId`; successful results only) | `409 DUPLICATE_READING`, `422 CURRENT_READING_INVALID` (theo P6-02f) |
| `PATCH /meter-readings/{meterReadingId}` (`patchMeterReadingsMeterreadingid`) `{ currentReading?, evidenceMediaId? }` | `200 METER_READING_UPDATED` | `409 PERIOD_ALREADY_INVOICED`, `409 METER_READING_NOT_LATEST`, `422 CURRENT_READING_INVALID` |
| `GET /invoices?filter[buildingId]&filter[period]&filter[status]=issued` | `200 INVOICES_FETCHED` | — (dùng để tính phòng bị khóa) |
| Media presign → PUT → complete (`features/media`) | `MEDIA_UPLOAD_COMPLETED` | `MEDIA_TYPE_NOT_ALLOWED`, `MEDIA_FILE_TOO_LARGE` |

Danh sách phòng: `GET /me/rooms?filter[buildingId]` (P6-03c). Chỉ số kỳ trước: `GET /meter-readings` với `period` liền trước.

### Mapping field

| DTO field | UI | Validation / ghi chú |
|---|---|---|
| `roomId`, `type` (`electricity`/`water`) | dòng phòng × cột Điện / Nước | lấy từ dòng, không cho nhập |
| `period` (bulk: tên field theo api-docs sau ) | Picker "Kỳ" trên thanh lọc | `^[0-9]{4}-(0[1-9]\|1[0-2])$`, lưu trên URL |
| `previousReading` (response) | cột "Chỉ số cũ" (chỉ đọc) | lấy từ kỳ trước hoặc chỉ số bàn giao cùng kỳ (`P6-D70`); chưa có → nhãn "Chưa có chỉ số bàn giao" |
| `currentReading` | ô "Chỉ số mới" | bắt buộc, `^(0\|[1-9][0-9]*)(\.[0-9]+)?$`; FE cảnh báo khi < chỉ số cũ, BE quyết định (`CURRENT_READING_INVALID`) |
| `isBaseline` | checkbox "Chỉ số bàn giao / thay đồng hồ" (chỉ trong Dialog từng phòng) | mặc định `false` |
| `source` | không hiển thị; `ocr` nếu số đến từ AI (kể cả đã sửa), ngược lại `manual` | enum `manual\|ocr` |
| `ocrValue` | không hiển thị | không gửi trong luồng nhập tay |
| `consumption` (response) | cột "Tiêu thụ" | chỉ đọc |
| file ảnh | nút "Chụp/Chọn ảnh" mỗi ô | bắt buộc trước khi Lưu |
| `evidenceMediaId` (response; PATCH body) | biểu tượng ảnh / nhãn "Thiếu ảnh" | `null` → "Thiếu ảnh" + nút "Tải lại ảnh"; có id → mở ảnh bằng `useMediaObjectUrl` |

## Tham chiếu code

- Feature mới: `fe/src/features/meter-readings/`. Copy pattern từ `fe/src/features/buildings/` (DTO, api, hooks, list page). Bảng nhập dùng primitive `fe/src/components/ui/` (`input`, `number-input`, `badge`, `dialog`), không cần DataTable phân trang (một tòa ≤ vài chục phòng).
- Upload sau khi tạo: `fe/src/features/media/utils/upload-media.ts` (`uploadMedia`, `validateMediaFile`), `hooks/use-media-upload.ts`, `MediaCaptureSource` trong `types/media.dto.ts`; pattern trạng thái từng file (uploading/completed/error + retry) như `fe/src/features/buildings/hooks/use-ownership-proof-uploader.ts`.
- Format: `formatMonth` trong `fe/src/lib/utils/format.ts`.
- Route placeholder có sẵn: `/meter-readings` trong `fe/src/app/routes/roles/landlord.routes.tsx`; menu landlord **chưa có** mục này (`fe/src/config/navigation.config.ts`).

## Các bước triển khai

### Bước 1 — Đọc contract hiện hành và chuẩn bị dữ liệu

- **Cách làm:** đọc `meter-readings*.yaml` và xác nhận `source`/`ocrValue` theo P6-D67. Không gọi endpoint OCR đã bị gỡ khỏi phạm vi; nếu `ai-service` chưa có endpoint OCR đang được công bố thì luồng nhập tay vẫn hoạt động, OCR để ngoài phạm vi. Trên staging: tòa có 3 phòng có HĐ active, baseline kỳ trước đã nhập bằng Apidog.
- **Kiểm tra bước:** xác nhận API đọc/ghi MeterReading trong `api-docs`; không phụ thuộc endpoint OCR đã bị gỡ khỏi phạm vi.

### Bước 2 — Tầng dữ liệu `meter-readings`

- **Cách làm:** DTO, API, query keys, hook cho list, create, bulk và `PATCH`. Namespace `meterReadings` theo `fe-structure` §5.
- **Kiểm tra bước:** `npm run build` pass.

### Bước 3 — Trang `/meter-readings`: chọn tòa + kỳ, bảng phòng

- **Cách làm:** thanh lọc Tòa + Kỳ (mặc định tháng hiện tại, lưu trên URL). Bảng: Phòng | Điện (cũ / mới / tiêu thụ) | Nước (cũ / mới / tiêu thụ) | Ảnh | Trạng thái. Phòng có hóa đơn `issued` của kỳ → badge **Đã khóa**, ô chỉ đọc. Ô ảnh lấy từ `evidenceMediaId` của reading (không lưu trạng thái ảnh ở client). Chưa chọn tòa → empty state hướng dẫn.
- **Kiểm tra bước:** chọn tòa + kỳ có dữ liệu → thấy chỉ số cũ đúng kỳ trước; F5 giữ tòa và kỳ.

### Bước 4 — Nhập chỉ số và giữ ảnh minh chứng

- **Cách làm:** nhập chỉ số bằng tay, hỗ trợ chọn/chụp ảnh minh chứng. Không gửi ảnh tới endpoint OCR trong phạm vi issue này. Upload ảnh sau khi tạo reading theo P6-D66/D69.
- **Kiểm tra bước:** nhập chỉ số và ảnh minh chứng hoạt động; lỗi upload không làm mất giá trị đã nhập, có thể thử tải lại.

### Bước 5 — Lưu từng phòng và lưu cả tòa, rồi upload ảnh

- **Cách làm:**
  - **Từng phòng:** Dialog "Nhập chỉ số phòng X" (điện + nước, có checkbox bàn giao) → `POST /meter-readings` từng loại → upload ảnh với `ownerId = id` vừa nhận → `PATCH /meter-readings/{id} { evidenceMediaId }`.
  - **Cả tòa:** nút "Lưu tất cả" gửi `POST /meter-readings/bulk` cho các dòng đã nhập đủ số **và** ảnh; dòng thiếu ảnh bị đánh dấu, không gửi. `BASELINE_REQUIRED` → show the missing-baseline error and a link to the single-room baseline dialog; the whole request is rolled back. Keep all unsaved input so the user can fix and resubmit. Lỗi cả lô (`409`/`422` theo P6-02f) → chỉ ra dòng lỗi nếu response có. Thành công → upload ảnh tuần tự theo `electricityReadingId`/`waterReadingId`, mỗi ảnh xong gọi `PATCH { evidenceMediaId }`.
  - Upload ảnh hoặc `PATCH` lỗi → reading đã tồn tại với `evidenceMediaId = null`: ô hiện "Thiếu ảnh" + nút "Tải lại ảnh" (không tạo reading lần nữa); F5 vẫn thấy "Thiếu ảnh".
- **Kiểm tra bước:** lưu cả tòa 3 phòng → 6 reading + 6 ảnh; tắt mạng giữa lúc upload ảnh → ô "Thiếu ảnh" (F5 vẫn còn), bật mạng bấm "Tải lại ảnh" → hết cảnh báo; one room lacks a baseline → `BASELINE_REQUIRED`, no readings are saved for any of the three rooms; fix the baseline and resubmit.

### Bước 6 — Sửa chỉ số và trạng thái khóa kỳ

- **Cách làm:** chỉ reading **mới nhất** của phòng + loại và chưa khóa có nút Sửa (Dialog `currentReading` → `PATCH`); không có Xóa (`P6-D70`). `409 PERIOD_ALREADY_INVOICED` → toast i18n, làm mới bảng để ô chuyển **Đã khóa**; `409 METER_READING_NOT_LATEST` → toast "Chỉ sửa được chỉ số mới nhất", làm mới bảng.
- **Kiểm tra bước:** phát hành hóa đơn của 1 phòng (Apidog) → F5 thấy phòng đó khóa; sửa reading qua Apidog → `409`, UI tương ứng hiển thị đúng; mở kỳ cũ đã có kỳ sau → không có nút Sửa.

### Bước 7 — Route, menu, i18n, rà soát

- **Cách làm:** thay placeholder `/meter-readings` bằng trang thật; thêm mục menu landlord `meterReadings` (`titleKey` đã có `navigation.meterReadings` trong `common.json`). Text vào `src/i18n/locales/vi/meterReadings.json` rồi `en/meterReadings.json` cùng key; `apiSuccess.*`/`apiErrors.*` cho mọi mã ở bảng Contract.
- **Kiểm tra bước:** 360px: bảng chuyển dạng thẻ theo phòng, không cuộn ngang; `npm run build`, `npm run lint`, `npm run i18n:check` pass.

## Ngoài phạm vi

- LL-19 camera live trong trình duyệt và LL-18c luồng "Phòng 3/20" từng bước: thay bằng bảng theo tòa + input `capture` (đủ cho `P6-D66` bulk).
- `readingDate`, `readingMethod` — bỏ theo `P6-D66` (kỳ là khóa).
- Nhập chỉ số từ Chi tiết phòng (LL-18): làm sau khi trang chi tiết phòng (P6-03c) có chỗ gắn; Dialog từng phòng ở đây dùng lại được.
- Tenant tự chụp công tơ (mobile).
- Xóa reading, sửa reading không phải mới nhất (`P6-D70`).

## Blocker

- Không có. (Trạng thái ảnh, `PATCH`, bulk thiếu baseline đã chốt ở `P6-D70`; BE giao ở P6-02h/P6-02f.)

## Acceptance

- [ ] Chọn tòa + kỳ → bảng phòng có chỉ số cũ, giữ trên URL.
- [ ] Nhập tay lưu reading với `source=manual`; không gọi endpoint OCR đã bị gỡ.
- [ ] Không có ảnh → không lưu được ô đó; lưu xong → ảnh `meter_reading_evidence` gắn đúng `readingId` và `GET /meter-readings` trả `evidenceMediaId`; F5 vẫn hiện đúng "có ảnh" / "Thiếu ảnh".
- [ ] Bulk 3 phòng → `201 METER_READINGS_BULK_RECORDED`; one room lacks a baseline → `BASELINE_REQUIRED` and no readings saved; một dòng nhỏ hơn chỉ số cũ → `422 CURRENT_READING_INVALID` hiển thị đúng dòng.
- [ ] Chỉ reading mới nhất có nút Sửa; kỳ đã phát hành hóa đơn → ô khóa; ép sửa → `409 PERIOD_ALREADY_INVOICED` / `METER_READING_NOT_LATEST` hiển thị đúng.

## Definition of Done

- [ ] Mọi bước qua phần Kiểm tra bước; mọi ô Acceptance được người làm tick, kèm ảnh/video luồng nhập chỉ số và upload minh chứng trong PR.
- [ ] `npm run build` + `npm run lint` + `npm run i18n:check` pass; không có file `*.test.ts`; key có ở cả `vi` và `en`.
- [ ] Không sửa file ngoài phạm vi; PR vào `main` ghi `Closes pbl6-home-renter/docs#103`, ≥ 1 reviewer approve.
