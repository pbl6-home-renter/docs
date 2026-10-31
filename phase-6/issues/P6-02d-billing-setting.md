# P6-02d — BillingSetting domain + API

**Epic:** [P6-02](P6-02-tenancy-billing-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** huynhtiennhat0403  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 3 points · 6–8 giờ  
**Phụ thuộc:** P6-02a, P6-02c (copy pattern scope building/room)  
**Repo / branch:** `Tenancy-Service` · `feature/p6-02d-billing-setting`  
**Issue:** `docs#74`

## Mục tiêu

Landlord đặt "ngày thu dự kiến" (`paymentDueDay`) và ngày gợi ý nhắc (`remindDay`) cho tòa hoặc phòng. Theo D39 đây **chỉ là thông tin hiển thị** — không sinh `overdue`, không chặn thao tác. Hai ngày được chọn độc lập trong khoảng 1–28; `remindDay` có thể sau `paymentDueDay`.

## Contract (sau P6-02a)

| Endpoint | operationId | Success | Lỗi riêng |
|---|---|---|---|
| `POST /billing-settings` | `postBillingSettings` | `201 BILLING_SETTING_CREATED` + `Location: /api/v1/billing-settings/{billingSettingId}` | `409 ACTIVE_SETTING_EXISTS`, `422 VALIDATION_FAILED` |
| `PATCH /billing-settings/{billingSettingId}` | `patchBillingSettingsBillingsettingid` | `200 BILLING_SETTING_UPDATED` | `404`, `422` |
| `GET /billing-settings` | `getBillingSettings` | `200 BILLING_SETTINGS_FETCHED` + `pagination` | `422` |

- File: `api-doc/src/paths/billing/billing-settings.yaml`, `billing-settings-billingSettingId.yaml`; request/response `api-doc/src/requests/rooms/billing-setting-*.yaml`, `api-doc/src/responses/dtos/rooms/billing-setting-*.yaml`.
- Bảng: `database-design.md` §2.10 (`landlord_id`, `scope`, `building_id`, `room_id`, `payment_due_day smallint default 5`, `remind_day smallint null`, `bot_enabled default true`, `is_active default true`).
- Role: `landlord`.
- Create cấp `building`: client gửi `scope` + `buildingId`, không gửi `roomId`. Create cấp `room`: client gửi `scope` + `roomId`, không gửi `buildingId`; server kiểm tra quyền sở hữu Room, lấy `buildingId` từ Room và lưu/trả cả hai ID. `id` của BillingSetting do server tạo và luôn có trong response; PATCH chỉ dùng `billingSettingId` trên path, không nhận scope/target trong body.
- Mỗi building/room chỉ có một setting chưa xóa mềm, kể cả khi `isActive=false`. POST trùng trả `409 ACTIVE_SETTING_EXISTS`; chủ trọ PATCH bản cũ để sửa hoặc bật lại. Chưa thêm `GET /billing-settings/{billingSettingId}` trong task này.

## Tham chiếu code

- Toàn bộ cấu trúc module, check quyền building/room, 409 khi trùng scope: **copy từ `src/modules/rate-policy/`** (P6-02b, P6-02c).
- Aggregate mẫu: `src/modules/building/domain/entities/building.entity.ts`.

## Các bước triển khai

### Bước 1 — Chạy service

- **Cách làm:** pull `main` (đã có P6-02c), `npm run migration:run && npm run start:dev`.
- **Kiểm tra bước:** `GET /api/v1/tenancy/health` → `200`; endpoint rate-policies chạy (dùng lại dữ liệu thử của P6-02c).

### Bước 2 — Domain

- **File tạo** (`src/modules/billing-setting/domain/`):
  - `enums/billing-setting-scope.enum.ts` (hoặc import `RatePolicyScope` nếu team đồng ý dùng chung — ghi rõ trong PR).
  - `entities/billing-setting.props.ts`, `entities/billing-setting.entity.ts`: `create`, `reconstitute`, `update({ paymentDueDay?, remindDay?, botEnabled?, isActive? })`.
  - `constants/billing-setting-event.constants.ts` (`billing_setting.created|updated`), `events/billing-setting-created.event.ts`, `billing-setting-updated.event.ts`.
  - `exceptions/billing-setting-not-found.exception.ts` (`404 RESOURCE_NOT_FOUND`), `active-setting-exists.exception.ts` (`409 ACTIVE_SETTING_EXISTS`). Không tạo `DUE_DAYS_INVALID` cho quan hệ giữa hai ngày; từng ngày ngoài 1–28 trả `422 VALIDATION_FAILED`.
  - `repositories/billing-setting.repository.ts`.
- **Cách làm:** `paymentDueDay`, `remindDay` ∈ [1, 28] và không so sánh thứ tự; scope/target giống RatePolicy (`building` ⇒ `buildingId`; `room` ⇒ `roomId` + `buildingId` do server tra từ Room).
- **Kiểm tra bước:** `npm run build` pass.

### Bước 3 — Persistence + migration

- **File tạo:** `src/modules/billing-setting/infrastructure/persistence/billing-setting.typeorm-entity.ts` (`@Entity('billing_settings')`, `@Check` 1–28 cho 2 cột ngày, check scope/target như `rate_policies`, 2 unique partial index theo `building_id`/`room_id` cho bản ghi chưa xóa mềm, không phụ thuộc `is_active`), `mappers/billing-setting.mapper.ts`, `billing-setting.repository.ts`.
- **Cách làm:** `npm run migration:generate -- src/database/migrations/CreateBillingSettingsTable` → mở file, **chỉ giữ** phần của `billing_settings`.
- **Kiểm tra bước:** `migration:run` → `migration:revert` → `migration:run` pass.

### Bước 4 — Command/Query + controller

- **File tạo:**
  - `application/commands/billing-setting-create/…`, `billing-setting-update/…`, `application/queries/billing-setting-list/…`.
  - `presentation/http/requests/create-billing-setting.request.ts`, `update-billing-setting.request.ts` (`@Min(1) @Max(28)`), `billing-setting-list.request.ts` (filter `scope`, `roomId`).
  - `presentation/http/responses/billing-setting.response.dto.ts`, `constants/billing-setting-response-code.constant.ts`.
  - `presentation/http/controllers/billing-setting.controller.ts` (`@Controller('billing-settings')`, `@Roles(UserRole.LANDLORD)`).
  - `billing-setting.module.ts`, `billing-setting.di-token.ts`.
- **File sửa:** `src/app.module.ts` thêm `BillingSettingModule`.
- **Cách làm:** handler create/update chạy trong `unitOfWork.run` + append outbox (y hệt P6-02c bước 4–5); list luôn lọc `landlord_id = user.id`.
- **Kiểm tra bước:** Swagger hiện 3 operation; `npm run build` + `npm run lint` pass.

## Quyết định tạm thời / Ngoài phạm vi

- Không có job nhắc/bot gửi card (`botEnabled` chỉ lưu cờ; bot thuộc community-service — Stretch).
- Resolve setting có hiệu lực theo `room → building` cho hiển thị: làm khi FE/Invoice cần (P6-02g). Việc tra `buildingId` của Room khi tạo setting cấp phòng vẫn phải làm trong P6-02d.

## Cập nhật `api-doc` (bắt buộc trước khi đóng issue)

- [ ] Sequence diagram cho `postBillingSettings`.
- [ ] `x-apidog-status: released` cho 3 endpoint; sync Apidog.

## Manual verification (Apidog)

1. Tạo setting tòa `paymentDueDay=5`, `remindDay=3` → `201` với `data.id` và `Location` trỏ tới ID đó; tạo lại cùng tòa → `409 ACTIVE_SETTING_EXISTS`.
2. `paymentDueDay=31` → `422 VALIDATION_FAILED`; `remindDay=10`, `paymentDueDay=5` → hợp lệ. Tắt setting rồi POST lại cùng tòa/phòng → `409`; PATCH bản cũ để sửa và bật lại.
3. Tạo setting phòng chỉ với `roomId` → response có `roomId` và `buildingId` thực tế của phòng.
4. PATCH setting của landlord khác → `403`; id không tồn tại → `404`.
5. GET với `filter[scope]=room` chỉ trả setting phòng của mình.

## Definition of Done

- [ ] Bước 1–4 qua phần Kiểm tra bước.
- [ ] `npm run build` + `npm run lint` pass.
- [ ] PR vào `main` ghi `Closes pbl6-home-renter/docs#74` + link file `api-doc`.
- [ ] baoduong17 approve.
