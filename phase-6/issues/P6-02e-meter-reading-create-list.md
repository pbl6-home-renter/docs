# P6-02e — MeterReading: nhập tay từng chỉ số và liệt kê

**Epic:** [P6-02](P6-02-tenancy-billing-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** huynhtiennhat0403  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 5 points · 10–14 giờ  
**Phụ thuộc:** P6-02a, P5-09b (bảng `rooms` + Room tồn tại)  
**Repo / branch:** `Tenancy-Service` · `feature/p6-02e-meter-reading`  
**Issue:** `docs#TBD`

## Mục tiêu

Landlord chốt chỉ số điện/nước của một phòng cho một kỳ `YYYY-MM` (nhập tay, có ảnh chứng cứ), và xem lại danh sách chỉ số. Mỗi chỉ số ghi xong phát event `meter_reading.recorded` để Invoice (P6-02g) dùng sau.

## Contract (sau P6-02a)

| Endpoint | operationId | Success | Lỗi riêng |
|---|---|---|---|
| `POST /meter-readings` | `postMeterReadings` | `201 METER_READING_CREATED` + `Location` | `409 DUPLICATE_METER_READING`, `422 CURRENT_READING_INVALID`, `EVIDENCE_REQUIRED`, `VALIDATION_FAILED` |
| `GET /meter-readings` | `getMeterReadings` | `200 METER_READINGS_FETCHED` + `pagination` | `422` |

- File: `api-doc/src/paths/billing/meter-readings.yaml`; request `api-doc/src/requests/rooms/meter-reading-create-request-dto.yaml`; response `api-doc/src/responses/dtos/rooms/meter-reading-create-response-dto.yaml`, `meter-reading-list-response-dto.yaml`.
- Filter list: `roomId`, `type`, `period`.
- Bảng: `database-design.md` §2.11 — `room_id`, `type` (`electricity|water`), `period varchar(7)`, `previous_reading numeric`, `current_reading numeric`, `reading_date date null`, `is_baseline bool`; **UNIQUE `(room_id, type, period)`**.
- Rule: `current ≥ previous` (EC1 — sai → `CURRENT_READING_INVALID`); kỳ đầu/thay đồng hồ dùng `isBaseline=true`; consumption lẻ giữ decimal (EC5); số dạng string trong API, `numeric` trong DB, **không dùng float**.
- Role: `landlord`; phòng của landlord khác → `403`.

## Tham chiếu code

| Cần | Copy pattern từ |
|---|---|
| Aggregate + event | `src/modules/building/domain/entities/building.entity.ts`, `src/modules/building/domain/events/building-created.event.ts` |
| Command UoW + outbox, controller, list query | `src/modules/rate-policy/` (P6-02c) |
| Load Room check quyền | `ROOM_DI_TOKEN.REPOSITORY` (`src/modules/room/room.module.ts`) |
| Map lỗi unique Postgres | `src/shared/infrastructure/database/postgres-error-code.ts` |
| Cột decimal ↔ string | `latitude` trong `src/modules/building/infrastructure/persistence/building.typeorm-entity.ts` (`type: 'decimal'`, field kiểu `string`) |

## Các bước triển khai

### Bước 1 — Chạy service và dữ liệu thử

- **Cách làm:** `npm run migration:run && npm run start:dev`; chuẩn bị 2 room của landlord A (cùng building) và 1 room của landlord B. Tạo sẵn 1 UUID bất kỳ làm `evidenceMediaId` (media flow chưa có).
- **Kiểm tra bước:** health `200`; `SELECT id, landlord_id FROM rooms` thấy dữ liệu thử.

### Bước 2 — Domain `MeterReading`

- **File tạo** (`src/modules/meter-reading/domain/`):
  - `enums/meter-type.enum.ts` (`electricity`, `water`).
  - `value-objects/reading-period.vo.ts`: validate regex `^[0-9]{4}-(0[1-9]|1[0-2])$`.
  - `value-objects/meter-value.vo.ts`: chuỗi decimal ≥ 0 (`^\d+(\.\d{1,3})?$`), so sánh bằng cách chuẩn hóa string (hoặc `decimal.js` nếu repo đã có — kiểm `package.json` trước, **không thêm thư viện mới khi chưa hỏi BE Lead**).
  - `entities/meter-reading.props.ts`, `entities/meter-reading.entity.ts`: `static record({ landlordId, roomId, buildingId, type, period, previousReading, currentReading, readingDate, isBaseline })`, getter `consumption` (= current − previous, string).
  - `constants/meter-reading-event.constants.ts` (`METER_READING_AGGREGATE_TYPE = 'MeterReading'`, `meter_reading.recorded`), `events/meter-reading-recorded.event.ts` (payload: `id, roomId, buildingId, type, period, previousReading, currentReading`).
  - `exceptions/current-reading-invalid.exception.ts` (`422 CURRENT_READING_INVALID`), `duplicate-meter-reading.exception.ts` (`409 DUPLICATE_METER_READING`), `evidence-required.exception.ts` (`422 EVIDENCE_REQUIRED`).
  - `repositories/meter-reading.repository.ts`: `save`, `findLatestBefore(roomId, type, period, ctx?)`, `existsFor(roomId, type, period, ctx?)`, `findPage(landlordId, query)`.
- **Cách làm:** `record` ném `CurrentReadingInvalidException` khi `current < previous`; `isBaseline=false` thì `previous` do handler cung cấp (không tin client — xem bước 4).
- **Kiểm tra bước:** `npm run build` pass.

### Bước 3 — Persistence + migration

- **File tạo:** `src/modules/meter-reading/infrastructure/persistence/meter-reading.typeorm-entity.ts` (`@Entity('meter_readings')`; thêm cột `landlord_id uuid` và `building_id uuid` để lọc theo landlord/tòa không cần join — ghi chú lệch so với §2.11 trong PR; `@Check` `current_reading >= previous_reading`, `previous_reading >= 0`, regex `period`; unique index `UQ_meter_readings_room_type_period` `WHERE is_deleted = false`), `mappers/meter-reading.mapper.ts`, `meter-reading.repository.ts`.
- **Cách làm:** `npm run migration:generate -- src/database/migrations/CreateMeterReadingsTable` → mở file, chỉ giữ phần `meter_readings`.
- **Kiểm tra bước:** `migration:run` → `migration:revert` → `migration:run` pass; insert tay 2 dòng trùng `(room_id,type,period)` → lỗi unique.

### Bước 4 — `POST /meter-readings`

- **File tạo:** `application/commands/meter-reading-create/meter-reading-create.command.ts` + `.handler.ts`; `presentation/http/requests/create-meter-reading.request.ts` (`@IsUUID roomId`, `@IsEnum type`, `@Matches period`, `@IsNumberString previousReading/currentReading`, `@IsOptional @IsDateString readingDate`, `@IsBoolean isBaseline`, `@IsOptional() @IsUUID evidenceMediaId` — để optional ở DTO để handler trả đúng `EVIDENCE_REQUIRED` thay vì `VALIDATION_FAILED`); `responses/meter-reading.response.dto.ts`; `constants/meter-reading-response-code.constant.ts`.
- **Cách làm (handler trong `unitOfWork.run`):**
  1. `roomRepository.findById(roomId)` → `404`; `room.landlordId !== user.id` → `403`.
  2. `existsFor(roomId, type, period, ctx)` → `409 DUPLICATE_METER_READING`.
  3. `isBaseline=false`: `prev = findLatestBefore(...)`; không có kỳ trước → `422 VALIDATION_FAILED` ("cần chỉ số baseline trước"); dùng `prev.currentReading` làm `previousReading` (xử lý giá trị client gửi theo quyết định P6-02a #8).
  4. `isBaseline=true`: dùng `previousReading` client gửi.
  5. `evidenceMediaId` thiếu → `EvidenceRequiredException`; có thì chỉ nhận, `TODO(media)` link `Media(owner_type='meter_reading')`.
  6. `MeterReadingEntity.record(...)` → save → append outbox → return. Bắt lỗi unique Postgres → `409` (race).
- **Kiểm tra bước:** baseline `2026-10` = 1200/1200 → `201`; kỳ `2026-11` current 1380 → `201`, `previousReading=1200`; gửi lại `2026-11` → `409`; current 1100 → `422 CURRENT_READING_INVALID`.

### Bước 5 — `GET /meter-readings`

- **File tạo:** `application/queries/meter-reading-list/…`; `presentation/http/requests/meter-reading-list.request.ts` (extends `OffsetPaginationQueryRequestDto<{ roomId?; type?; period? }>`).
- **Cách làm:** lọc `landlord_id = user.id` + filter; sort whitelist `period`, `createdAt` (default `period desc`).
- **Kiểm tra bước:** `filter[period]=2026-11` chỉ trả kỳ 11; landlord B không thấy dữ liệu A.

### Bước 6 — Controller, module

- **File tạo:** `presentation/http/controllers/meter-reading.controller.ts` (`@Controller('meter-readings')`, `@Roles(UserRole.LANDLORD)`), `meter-reading.module.ts` (imports `CqrsModule`, `OutboxModule`, `RoomModule`), `meter-reading.di-token.ts`.
- **File sửa:** `src/app.module.ts` thêm `MeterReadingModule`.
- **Kiểm tra bước:** Swagger hiện 2 operation; `npm run build` + `npm run lint` pass; `outbox_messages` có `meter_reading.recorded` sau mỗi lần tạo.

## Quyết định tạm thời / Ngoài phạm vi

- Không sửa/xóa chỉ số đã chốt trong It5 (sửa chỉ số khi chưa phát hành hóa đơn → bàn ở P6-02g).
- Media chứng cứ: chỉ nhận UUID, `TODO(media)`.
- `readingDate` chỉ lưu; prorate dùng ở P6-02g.

## Cập nhật `api-doc` (bắt buộc trước khi đóng issue)

- [ ] Sequence diagram `postMeterReadings` (Gateway → Tenancy → load Room → check trùng → transaction + outbox).
- [ ] `x-apidog-status: released` cho 2 endpoint; sync Apidog.

## Manual verification (Apidog)

1. Các case ở bước 4 (baseline, kỳ sau, trùng `409`, chỉ số lùi `422`).
2. Phòng của landlord khác → `403`; room không tồn tại → `404`; token tenant → `403`.
3. `period=2026-13` → `422 VALIDATION_FAILED`; thiếu `evidenceMediaId` → `422 EVIDENCE_REQUIRED`.
4. Lỗi giả sau append outbox → `500`, không có row mới.

## Definition of Done

- [ ] Bước 1–6 qua phần Kiểm tra bước.
- [ ] `npm run build` + `npm run lint` pass.
- [ ] PR vào `main` ghi `Closes pbl6-home-renter/docs#TBD` + link file `api-doc`.
- [ ] baoduong17 approve.
