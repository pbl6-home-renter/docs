# P6-02f — Chốt chỉ số hàng loạt theo tòa

**Epic:** [P6-02](P6-02-tenancy-billing-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** huynhtiennhat0403  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 2 points · 4–6 giờ  
**Phụ thuộc:** P6-02e  
**Repo / branch:** `Tenancy-Service` · `feature/p6-02f-meter-reading-bulk`  
**Issue:** `docs#76`

## Mục tiêu

Cuối tháng landlord nhập chỉ số điện/nước cho nhiều phòng của một tòa trong **một request**; tất cả được ghi trong một transaction (all-or-nothing) và trả bảng tổng hợp tiêu thụ.

## Contract (sau P6-02a)

- Endpoint: `POST /meter-readings/bulk` — `api-doc/src/paths/billing/meter-readings-bulk.yaml` (`postBulkMeterReadings`).
- Request: `api-doc/src/requests/rooms/bulk-meter-reading-create-request-dto.yaml` — `buildingId`, `recordedMonth` (= `period`), `readingMethod`, `readings[] { roomId, type, previousReading?, currentReading, evidenceMediaId }`.
- Response: `api-doc/src/responses/dtos/rooms/bulk-meter-reading-response-dto.yaml` — `201 METER_READINGS_BULK_RECORDED`, `results[]` theo phòng (`electricityReadingId`, `electricityUsage`, `waterReadingId`, `waterUsage`, `status`, `note`), tổng `totalElectricityUsage`, `totalWaterUsage`.
- Lỗi: `404` (building), `403`, `409 DUPLICATE_READING`, `422 CURRENT_READING_INVALID`, `EVIDENCE_REQUIRED`, `VALIDATION_FAILED`.

## Tham chiếu code

- Domain/repository/exception: `src/modules/meter-reading/` (P6-02e) — **gọi lại cùng logic, không copy-paste**.
- Load Building: `BUILDING_DI_TOKEN.REPOSITORY` (`src/modules/building/building.module.ts`).

## Các bước triển khai

### Bước 1 — Tách logic ghi 1 chỉ số thành service dùng chung

- **File tạo:** `src/modules/meter-reading/application/services/meter-reading-recorder.service.ts` với `record(input, user, ctx): Promise<MeterReadingEntity>` chứa các bước 2–6 của handler P6-02e (trừ mở UoW).
- **File sửa:** `application/commands/meter-reading-create/meter-reading-create.command.handler.ts` gọi service trong `unitOfWork.run`.
- **Kiểm tra bước:** chạy lại manual verification của P6-02e → kết quả không đổi.

### Bước 2 — Request/Response DTO

- **File tạo** (`src/modules/meter-reading/presentation/http/`): `requests/bulk-create-meter-readings.request.ts` (`@ValidateNested({ each: true })`, `@ArrayMinSize(1)`, `@IsEnum` cho `readingMethod`), `responses/bulk-meter-reading.response.dto.ts`; thêm `METER_READINGS_BULK_RECORDED` vào response code constant.
- **Kiểm tra bước:** `npm run build` pass.

### Bước 3 — Command handler bulk

- **File tạo:** `application/commands/meter-reading-bulk-create/…command.ts` + `.handler.ts`.
- **Cách làm (trong một `unitOfWork.run`):**
  1. `buildingRepository.findById(buildingId)` → `404`; khác landlord → `403`.
  2. Trong request có 2 dòng trùng `(roomId, type)` → `409 DUPLICATE_READING` (trước khi đụng DB).
  3. Mỗi `roomId` phải thuộc `buildingId` (load room, so `room.buildingId`) → sai thì `422 VALIDATION_FAILED`.
  4. Lặp gọi `MeterReadingRecorder.record(...)` với `period = recordedMonth`; lỗi `DUPLICATE_METER_READING` của service → đổi sang `409 DUPLICATE_READING` (code của endpoint bulk). Bất kỳ lỗi nào ném ra → cả transaction rollback.
  5. Gom kết quả theo `roomId`; `status = SUCCESS` (hoặc `WARNING` theo quyết định P6-02a #9); cộng tổng usage bằng phép cộng decimal-string.
- **Kiểm tra bước:** request 3 phòng × 2 loại → 6 row trong `meter_readings`, 6 row `meter_reading.recorded` trong outbox.

### Bước 4 — Route

- **File sửa:** `presentation/http/controllers/meter-reading.controller.ts`: `@Post('bulk')` khai báo **trước** mọi route có `:id` (nếu có) để không bị bắt nhầm; `operationId: 'postBulkMeterReadings'`; `meter-reading.module.ts` import `BuildingModule`, đăng ký handler + service.
- **Kiểm tra bước:** Swagger hiện operation; `npm run build` + `npm run lint` pass.

## Quyết định tạm thời / Ngoài phạm vi

- `readingMethod` chỉ log, không lưu (DB không có cột).
- Giới hạn `readings` tối đa 200 phần tử (`@ArrayMaxSize(200)`) — đề xuất thêm vào contract nếu API owner đồng ý.
- OCR ở P6-02h; media chứng cứ `TODO(media)`.

## Cập nhật `api-doc` (bắt buộc trước khi đóng issue)

- [ ] Sequence diagram bulk (một transaction, rollback toàn bộ khi 1 dòng lỗi).
- [ ] `x-apidog-status: released`; sync Apidog.

## Manual verification (Apidog)

1. 2 phòng × điện + nước, kỳ mới → `201`, tổng usage đúng (tính tay so sánh).
2. Một dòng `currentReading` nhỏ hơn kỳ trước → `422 CURRENT_READING_INVALID` và **không** dòng nào được ghi.
3. Gửi lại cùng kỳ → `409 DUPLICATE_READING`; 2 dòng trùng trong body → `409`.
4. Room thuộc tòa khác → `422`; tòa của landlord khác → `403`.

## Definition of Done

- [ ] Bước 1–4 qua phần Kiểm tra bước; P6-02e vẫn pass sau refactor.
- [ ] `npm run build` + `npm run lint` pass.
- [ ] PR vào `main` ghi `Closes pbl6-home-renter/docs#76` + link file `api-doc`.
- [ ] baoduong17 approve.
