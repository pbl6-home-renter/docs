# P6-02c — API RatePolicy (tạo, batch tòa, sửa, tắt, liệt kê)

**Epic:** [P6-02](P6-02-tenancy-billing-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** huynhtiennhat0403  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 5 points · 10–14 giờ  
**Phụ thuộc:** P6-02b, P5-09b (Room tồn tại trong DB), P5-08b (pattern)  
**Repo / branch:** `Tenancy-Service` · `feature/p6-02c-rate-policy-api`  
**Issue:** `docs#73`

## Mục tiêu

Landlord cấu hình được bộ đơn giá cho tòa (wizard bước 3) và cho từng phòng, sửa giá tại chỗ, tắt bộ phòng để kế thừa giá tòa, và xem danh sách — qua 5 endpoint dưới đây.

## Contract (sau P6-02a)

| Endpoint | operationId | Success | Lỗi riêng |
|---|---|---|---|
| `POST /buildings/{buildingId}/rate-policies/batch` | `postBuildingRatePoliciesBatch` | `201 RATE_POLICIES_BATCH_CREATED` | `404 BUILDING_NOT_FOUND`, `422 BUILDING_ID_MISMATCH`, `RATE_POLICIES_REQUIRED`, `INVALID_RATE_KIND`, `TIER_CONFIG_INVALID` |
| `POST /rate-policies` | `postRatePolicies` | `201 RATE_POLICY_CREATED` + `Location` | `409 ACTIVE_POLICY_EXISTS`, `422 INVALID_RATE_KIND`, `TIER_CONFIG_INVALID` |
| `PATCH /rate-policies/{ratePolicyId}` | `patchRatePoliciesRatepolicyid` | `200 RATE_POLICY_UPDATED` | `404`, `422` |
| `POST /rate-policies/{ratePolicyId}/deactivate-policy` | `postRatePoliciesRatepolicyidDeactivatePolicy` | `200 RATE_POLICY_DEACTIVATED` | `404`, `409 POLICY_NOT_ACTIVE` |
| `GET /rate-policies` | `getRatePolicies` | `200 RATE_POLICIES_FETCHED` + `pagination` | `422 VALIDATION_FAILED` |

- File: `api-doc/src/paths/billing/rate-policies.yaml`, `rate-policies-ratePolicyId.yaml`, `rate-policies-ratePolicyId-deactivate-policy.yaml`, `api-doc/src/paths/buildings/buildings-buildingId-rate-policies-batch.yaml`.
- Role: `landlord` cho tất cả. Building/Room/RatePolicy của landlord khác → `403 FORBIDDEN`.

## Tham chiếu code

| Cần | Copy pattern từ |
|---|---|
| Command handler UoW + outbox | `src/modules/sample/application/commands/sample-create/sample-create.command.handler.ts`; slice `POST /buildings` của P5-08b |
| Query handler | `src/modules/sample/application/queries/sample-get-by-id/sample-get-by-id.query.handler.ts` |
| Controller, `@Roles`, `@ResponseCode`, `@ApiSuccessResponse`, `@CurrentUser` | `src/modules/sample/presentation/http/controllers/sample.controller.ts`, `src/shared/presentation/decorators/auth/current-user.decorator.ts` |
| Query list (`pageNo/pageSize/sort/order/filter`) | `src/shared/presentation/pagination/offset-pagination.request.dto.ts`, `paginated.response.dto.ts` |
| Load building/room để check quyền | `BUILDING_DI_TOKEN.REPOSITORY` (`BuildingModule`), `ROOM_DI_TOKEN.REPOSITORY` (`RoomModule`) |
| Domain đã có | `RatePolicyEntity`, `RateItem`, repository từ P6-02b |

## Các bước triển khai

### Bước 1 — Chạy service và dữ liệu thử

- **Cách làm:** `npm run migration:run && npm run start:dev`; tạo qua API (hoặc insert tay) 1 building của landlord A, 1 room trong building đó, 1 building của landlord B. Lấy access token landlord A, B, tenant từ Identity (Apidog env).
- **Kiểm tra bước:** `GET /api/v1/tenancy/health` → `200`; có đủ dữ liệu thử.

### Bước 2 — Request/Response DTO và response code

- **File tạo** (trong `src/modules/rate-policy/presentation/http/`):
  - `requests/rate-item.request.ts`: `type` (`@IsEnum(RateType)`), `name` (`@Length(1,100)`), `rateKind` (`@IsEnum(RateKind)`), `unitPrice` (`@IsOptional() @IsNumberString()`), `steps` (`@IsOptional() @IsArray() @ValidateNested({each:true}) @Type(() => RateStepRequest)`), `billingUnit` (`@IsEnum(BillingUnit)`).
  - `requests/create-rate-policy.request.ts`: `scope`, `buildingId?`, `roomId?`, `rates` (`@ArrayMinSize(1) @ValidateNested`).
  - `requests/batch-building-rate-policies.request.ts`: `buildingId`, `ratePolicies: RateItemRequest[]` (tên field theo contract đã chốt).
  - `requests/update-rate-policy.request.ts`: `rates?`, `isActive?`.
  - `requests/rate-policy-list.request.ts`: extends `OffsetPaginationQueryRequestDto<{ scope?; roomId?; buildingId? }>`.
  - `responses/rate-policy.response.dto.ts`: `id, landlordId, scope, buildingId, roomId, rates, isActive, createdAt, updatedAt`, `static fromDomain`.
  - `constants/rate-policy-response-code.constant.ts`: `RATE_POLICY_CREATED`, `RATE_POLICIES_BATCH_CREATED`, `RATE_POLICY_UPDATED`, `RATE_POLICY_DEACTIVATED`, `RATE_POLICIES_FETCHED`.
- **Kiểm tra bước:** `npm run build` pass.

### Bước 3 — `POST /buildings/{buildingId}/rate-policies/batch`

- **File tạo:** `src/modules/rate-policy/application/commands/building-rate-policies-batch/…command.ts` + `…command.handler.ts`.
- **Cách làm:**
  - Controller: `buildingId` path ≠ `buildingId` body → `422 BUILDING_ID_MISMATCH` (exception mới `building-id-mismatch.exception.ts`). `ratePolicies` rỗng → `422 RATE_POLICIES_REQUIRED`.
  - Handler trong `unitOfWork.run`: `buildingRepository.findById` → không có → `404 BUILDING_NOT_FOUND` (exception riêng trong module rate-policy, code đúng contract) → `building.landlordId !== user.id` → `403`.
  - `ratePolicyRepository.findByBuilding(buildingId, ctx)`: chưa có → `RatePolicyEntity.create(scope=building)`; đã có → `replaceRates(...)` (+ `activate()` nếu đang tắt). Save + append outbox.
- **Kiểm tra bước:** gọi 2 lần liên tiếp → lần 2 cập nhật **cùng** `id`, DB chỉ 1 row scope building cho tòa đó.

### Bước 4 — `POST /rate-policies`

- **File tạo:** `.../commands/rate-policy-create/…`.
- **Cách làm:**
  - `scope=building`: check building như bước 3. `scope=room`: `roomRepository.findById` → `404`; `room.landlordId !== user.id` → `403`; lấy `buildingId = room.buildingId`.
  - Đã có bộ cho target (kể cả `isActive=false`) → `409 ACTIVE_POLICY_EXISTS`. Bắt thêm lỗi unique Postgres (`src/shared/infrastructure/database/postgres-error-code.ts`) để race condition cũng ra `409`.
  - Header `Location: /api/v1/rate-policies/{id}` (như P5-08b bước 5).
- **Kiểm tra bước:** tạo bộ room → `201`; tạo lại → `409`.

### Bước 5 — `PATCH` và `deactivate-policy`

- **File tạo:** `.../commands/rate-policy-update/…`, `.../commands/rate-policy-deactivate/…`.
- **Cách làm:** `findByIdForUpdate(id, ctx)` → `404` → check `landlordId` → `replaceRates`/`activate`/`deactivate()` → save + outbox. Deactivate bộ đang tắt → `409 POLICY_NOT_ACTIVE` (từ domain).
- **Kiểm tra bước:** tắt bộ room → `isActive=false`; tắt lần 2 → `409`; `PATCH {isActive:true}` bật lại.

### Bước 6 — `GET /rate-policies`

- **File tạo:** `.../queries/rate-policy-list/rate-policy-list.query.ts` + handler.
- **Cách làm:** luôn lọc `landlord_id = user.id`; filter `scope`, `roomId`, `buildingId`; sort whitelist `createdAt` (default `desc`); trả `PaginatedResponseDto.create(...)`.
- **Kiểm tra bước:** landlord B không thấy bộ của landlord A; `pageSize=101` → `422`.

### Bước 7 — Controller và module

- **File tạo:** `src/modules/rate-policy/presentation/http/controllers/rate-policy.controller.ts` (`@Controller('rate-policies')`, 4 route) và `building-rate-policy.controller.ts` (`@Controller('buildings/:buildingId/rate-policies')`, route `@Post('batch')`). Tất cả `@Roles(UserRole.LANDLORD)`, `operationId` đúng bảng Contract.
- **File sửa:** `src/modules/rate-policy/rate-policy.module.ts`: imports `CqrsModule`, `OutboxModule`, `BuildingModule`, `RoomModule`; controllers; providers command/query handler.
- **Kiểm tra bước:** Swagger `/api/v1/tenancy/swagger` hiện đủ 5 operation; `npm run build` + `npm run lint` pass.

## Quyết định tạm thời / Ngoài phạm vi

- Preset EVN/phí mẫu (D31/D32) chưa có endpoint — FE tạm gửi `steps` EVN 6 bậc từ hằng số phía client. `TODO(seed-presets)`.
- Không cho `DELETE` (D39: tắt = `is_active`).
- Gateway route `/rate-policies` và `/buildings/*/rate-policies` sang tenancy: nhờ baoduong17 kiểm tra trong `api-gateway`.

## Cập nhật `api-doc` (bắt buộc trước khi đóng issue)

- [ ] Sequence diagram cho batch và `POST /rate-policies` (Gateway → Tenancy → load Building/Room → DB transaction + outbox).
- [ ] `x-apidog-status: released` cho 5 endpoint đã verify; sync Apidog.

## Manual verification (Apidog)

1. Batch EVN 6 bậc + nước `per_head` 100000 + wifi `fixed_per_period` 100000 cho tòa của mình → `201`.
2. Batch điện `per_head` → `422 INVALID_RATE_KIND`; tiered bậc cuối `to=5000` → `422 TIER_CONFIG_INVALID`.
3. Batch path/body `buildingId` khác nhau → `422 BUILDING_ID_MISMATCH`; tòa không tồn tại → `404 BUILDING_NOT_FOUND`; tòa landlord khác → `403`.
4. Tạo bộ room hai lần → `201` rồi `409 ACTIVE_POLICY_EXISTS`.
5. Deactivate 2 lần → `200` rồi `409 POLICY_NOT_ACTIVE`; token tenant → `403`.
6. Lỗi giả sau `outboxRepository.append` → `500`, không có row `rate_policies`/`outbox_messages` mới.

## Definition of Done

- [ ] Bước 1–7 qua phần Kiểm tra bước.
- [ ] `npm run build` + `npm run lint` pass.
- [ ] PR vào `main` ghi `Closes pbl6-home-renter/docs#73` + link các file `api-doc` ở mục Contract.
- [ ] baoduong17 approve; export Apidog đính kèm PR.
