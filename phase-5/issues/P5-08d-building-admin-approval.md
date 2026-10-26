# P5-08d — Admin duyệt/từ chối Building

**Epic:** [P5-08](P5-08-tenancy-building-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** leminhkhai345  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 5 points · 10–14 giờ  
**Phụ thuộc:** P5-08b (có thể làm song song P5-08c)  
**Repo / branch:** `Tenancy-Service` · `feature/p5-08d-building-admin-approval`

## Mục tiêu

Admin xem hàng đợi Building (lọc theo trạng thái, chủ nhà, địa bàn), xem chi tiết kèm thông tin chủ nhà, và approve/reject Building `pending`. Chỉ Building `approved` mới được tạo Room (P5-09b) và hiển thị công khai (P5-08e).

## Contract

| Endpoint | operationId | File `api-doc` | Success |
|---|---|---|---|
| `GET /admin/buildings` | `getAdminBuildings` | `src/paths/buildings/admin-buildings.yaml` | `200 BUILDINGS_ADMIN_FETCHED` + `pagination` |
| `GET /admin/buildings/{buildingId}` | `getAdminBuildingsBuildingid` | `src/paths/buildings/admin-buildings-buildingId.yaml` | `200 BUILDING_ADMIN_FETCHED` |
| `POST /buildings/{buildingId}/approve` | `postBuildingsBuildingidApprove` | `src/paths/buildings/buildings-buildingId-approve.yaml` | `200 BUILDING_APPROVED` |
| `POST /buildings/{buildingId}/reject` | `postBuildingsBuildingidReject` | `src/paths/buildings/buildings-buildingId-reject.yaml` | `200 BUILDING_REJECTED` |

- Role: `admin` cho cả 4 endpoint.
- List: `filter[status|landlordId|province|ward|q]`, `sort` (mặc định `createdAt`), `order` (mặc định **`asc`** — hàng đợi cũ nhất trước), `pageNo`, `pageSize`.
- DTO: `src/responses/dtos/buildings/admin-building-list-response-dto.yaml` (cần `landlordName`, `landlordPhone`), `admin-building-detail-response-dto.yaml` (object `landlord {id, name, phone, email, cccdNumber}`), `building-approve-response-dto.yaml`, `building-reject-response-dto.yaml`.
- Request: `src/requests/buildings/building-approve-request-dto.yaml` và `building-reject-request-dto.yaml` — **cả hai đều `note` bắt buộc**, 1–500 ký tự.
- Lỗi: `404 RESOURCE_NOT_FOUND`, `409 BUILDING_NOT_PENDING`, `422 NOTE_REQUIRED` / `VALIDATION_FAILED`, `403 FORBIDDEN`.

## Tham chiếu code (đã có trong repo)

| Cần | Copy pattern từ |
|---|---|
| Command handler UoW + outbox | `src/modules/building/application/commands/building-create/` (P5-08b) |
| Query service + filter/sort/pagination | `Identity-Service/src/modules/users/infrastructure/services/user-query.service.ts` (`findUsersAdmin`), `IBuildingQueryService` (P5-08c, nếu đã merge thì mở rộng; nếu chưa thì tạo port/service theo mô tả ở P5-08c Bước 2) |
| Gọi Identity lấy tên/SĐT chủ nhà | Port `src/shared/application/ports/internal-http-client.port.ts` (`IInternalHttpClient.get`, inject `INTERNAL_HTTP_DI_TOKEN.CLIENT`); ví dụ dùng: `Identity-Service/src/modules/users/infrastructure/services/tenancy-user-stats.service.ts` |
| Endpoint Identity sẵn có | `GET /internal/users?ids=<uuid,uuid>` (`Identity-Service/src/modules/users/presentation/http/controllers/user-internal.controller.ts`) → `[{ id, name, email, phone, role, status, isDeleted }]` |
| Domain đã có (**dùng lại**) | `BuildingEntity.approve(reviewedBy, note?)`, `BuildingEntity.reject(reviewedBy, note)` (phát `BuildingApproved/RejectedEvent`), `InvalidBuildingStatusTransitionException` (409 `BUILDING_NOT_PENDING`), `BuildingNoteRequiredException` (422 `NOTE_REQUIRED`), `findByIdForUpdate()` |

## Các bước triển khai

### Bước 1 — Pull code và chuẩn bị dữ liệu test

- **Cách làm:**
  - Pull `main` (đã có P5-08b), tạo branch `feature/p5-08d-building-admin-approval`.
  - Chạy cả `Identity-Service` (port 3001) và `Tenancy-Service`; trong `.env` của Tenancy đặt `IDENTITY_SERVICE_URL=http://localhost:3001` và `SERVICE_TOKEN` giống Identity.
  - Lấy token admin (`npm run seed:admin` bên Identity) và tạo 3 Building `pending` bằng token landlord.
- **Kiểm tra bước:** `curl -H "X-Service-Token: $SERVICE_TOKEN" "http://localhost:3001/internal/users?ids=<landlordId>"` trả tên/SĐT chủ nhà.

### Bước 2 — Adapter lấy thông tin chủ nhà từ Identity

- **File tạo:**
  - `src/modules/building/application/ports/landlord-directory.port.ts`: `ILandlordDirectory.findByIds(ids: Uuid[]): Promise<Map<Uuid, LandlordSummary>>`, `LandlordSummary = { id, name, phone, email }`.
  - `src/modules/building/infrastructure/services/identity-landlord-directory.service.ts`: gọi `client.get<LandlordSummary[]>(PeerService.IDENTITY, '/internal/users', { query: { ids: ids.join(',') } })`; ids rỗng → trả `Map` rỗng, không gọi HTTP.
- **File sửa:** `building.di-token.ts` thêm `LANDLORD_DIRECTORY`; `building.module.ts` đăng ký provider.
- **Cách làm:** đây là dữ liệu hiển thị ⇒ nếu Identity lỗi (`PeerServiceUnavailableException`) thì list **vẫn trả** với `landlordName`/`landlordPhone` = `""` và log warn; detail cũng vậy. (Theo comment trong port: hiển thị thì fallback, quyết định thì fail closed.)
- **Kiểm tra bước:** `npm run build` pass.

### Bước 3 — Query list/detail cho admin

- **File tạo/sửa:**
  - `src/modules/building/application/queries/models/admin-building-filter.model.ts`: `{ status?, landlordId?, province?, ward?, q? }`.
  - `IBuildingQueryService` + `BuildingQueryService` (**sửa** nếu P5-08c đã tạo): thêm `findAdminBuildings(q)` và `findAdminBuildingById(id)`. Filter `q` = `LOWER(building.name) LIKE :q OR LOWER(building.address) LIKE :q`; `withSort({ whitelist: ['createdAt', 'name', 'status'], defaultSort: 'createdAt', defaultOrder: 'asc', alias: 'building' })`.
  - `src/modules/building/application/queries/building-list-admin/` và `building-get-admin/` (query + handler): handler lấy page Building → gom `landlordId` duy nhất → `landlordDirectory.findByIds` → trả `{ building, landlord }[]`.
  - `src/modules/building/presentation/http/requests/building-list-admin.query.request.dto.ts` (`extends OffsetPaginationQueryRequestDto<AdminBuildingFilter>`, `@IsIn` cho status, `@IsUUID` cho landlordId).
  - `src/modules/building/presentation/http/responses/admin-building-list.response.dto.ts`, `admin-building-detail.response.dto.ts`.
- **Kiểm tra bước:** `npm run build` pass.

### Bước 4 — Controller admin (GET)

- **File tạo:** `src/modules/building/presentation/http/controllers/admin-building.controller.ts` — `@Controller('admin/buildings')`, `@Roles(UserRole.ADMIN)`:
  - `@Get()` `operationId: 'getAdminBuildings'`, `@ResponseCode(BUILDINGS_ADMIN_FETCHED)`, trả `PaginatedResponseDto.create(...)`.
  - `@Get(':buildingId')` `operationId: 'getAdminBuildingsBuildingid'`, `@ResponseCode(BUILDING_ADMIN_FETCHED)`; không thấy → `BuildingNotFoundException`.
- **File sửa:** `building-response-code.constant.ts` thêm `BUILDINGS_ADMIN_FETCHED`, `BUILDING_ADMIN_FETCHED`, `BUILDING_APPROVED`, `BUILDING_REJECTED`; `building.module.ts` đăng ký controller + handler.
- **Kiểm tra bước:** token admin: list mặc định Building cũ nhất trước, có `landlordName`; `filter[status]=pending&filter[q]=thanh` lọc đúng. Token landlord → `403`.

### Bước 5 — Command approve

- **File tạo:**
  - `src/modules/building/application/commands/building-approve/building-approve.command(.handler).ts`: `BuildingApproveCommand(adminId, buildingId, note)`.
  - `src/modules/building/presentation/http/requests/review-building.request.ts`: `@IsString() @Length(1,500) note` (dùng chung cho approve/reject).
  - `src/modules/building/presentation/http/responses/building-approve.response.dto.ts`: `{ id, status, reviewedAt }`.
- **Cách làm (handler):** UoW: `findByIdForUpdate(id, ctx)` → `null` ⇒ `BuildingNotFoundException` → `building.approve(command.adminId, command.note)` (domain ném 409 nếu không `pending`) → `save` → append outbox (`BuildingApproved`).
- **File sửa:** `building.controller.ts` (controller `buildings` từ P5-08b) thêm `@Post(':buildingId/approve') @HttpCode(200) @Roles(UserRole.ADMIN)`, `operationId: 'postBuildingsBuildingidApprove'`.
- **Kiểm tra bước:** approve Building `pending` → `200`, DB có `reviewed_by` = id admin, `reviewed_at`, `note`; outbox có `BuildingApproved`.

### Bước 6 — Command reject

- **File tạo:** `src/modules/building/application/commands/building-reject/building-reject.command(.handler).ts`; `.../responses/building-reject.response.dto.ts` (`{ id, status, reviewNote, reviewedAt }`).
- **Cách làm:** như Bước 5 nhưng gọi `building.reject(adminId, note)`. Note rỗng/khoảng trắng phải ra `422 NOTE_REQUIRED` (domain `validateNote`) — DTO chỉ chặn thiếu field/sai kiểu (`422 VALIDATION_FAILED`).
- **File sửa:** `building.controller.ts` thêm `@Post(':buildingId/reject')`, `operationId: 'postBuildingsBuildingidReject'`.
- **Kiểm tra bước:** reject → `200`, `status = rejected`; outbox có `BuildingRejected`; approve/reject lại Building đó → `409 BUILDING_NOT_PENDING`.

### Bước 7 — Build, lint, Swagger

- **Kiểm tra bước:** `npm run build` + `npm run lint` pass; Swagger có đủ 4 `operationId`.

## Quyết định tạm thời / Ngoài phạm vi

- **Approve cũng bắt buộc `note`** theo contract (domain cho phép optional) ⇒ DTO bắt buộc, domain giữ nguyên.
- **`cccdNumber` = `null`:** `/internal/users` không trả CCCD; ghi `TODO` và câu hỏi cho API owner (bỏ field hoặc mở rộng internal lookup).
- **`ownershipDocuments` = `[]`, `documentsCount` = `0`:** media flow chưa có (P5-08b chưa lưu liên kết media), ghi `TODO(media)`.
- **`totalRooms` = `0`, `occupancyRate` = `"0%"`:** chờ bảng `rooms` (P5-09b); ghi `TODO(room)`.
- **`submittedAt` = `createdAt`** (chưa có luồng nộp lại hồ sơ).
- **`format` (xlsx/csv/pdf):** chỉ làm `json`; ghi blocker cho API owner như P5-08c.
- Không gửi notification cho landlord (community-service chưa có); event trong outbox là đủ.

## Cập nhật `api-doc` (bắt buộc trước khi đóng issue)

- [ ] **Xóa `district`**: `src/responses/dtos/buildings/admin-building-detail-response-dto.yaml` (property + `required`) và example trong `src/paths/buildings/admin-buildings-buildingId.yaml`.
- [ ] Thêm `enum` cho `filter.status` trong `admin-buildings.yaml`.
- [ ] Sequence diagram cho `getAdminBuildings`, `getAdminBuildingsBuildingid` (có bước Tenancy → Identity `/internal/users`), `postBuildingsBuildingidApprove`, `postBuildingsBuildingidReject` (có outbox event). Tham khảo `src/paths/auth/register.yaml`.
- [ ] `x-apidog-status: designing` → `released` cho 4 endpoint; sync Apidog; link PR `api-doc` vào issue.

## Manual verification (Apidog)

1. Token landlord gọi 4 endpoint → `403 FORBIDDEN`.
2. `GET /admin/buildings` → Building cũ nhất trước, có `landlordName`/`landlordPhone`; tắt Identity → vẫn `200` với tên rỗng.
3. Approve Building `pending` với `note` → `200 BUILDING_APPROVED`, có `reviewedAt`; outbox `BuildingApproved`. Thiếu `note` → `422 VALIDATION_FAILED`.
4. Reject với `note: "   "` → `422 NOTE_REQUIRED`; có note → `200 BUILDING_REJECTED`, `status = rejected`.
5. Approve/reject Building đã xử lý → `409 BUILDING_NOT_PENDING`; id không tồn tại → `404`.

## Definition of Done

- [ ] Bước 1–7 đã qua phần Kiểm tra bước.
- [ ] `npm run build` + `npm run lint` pass.
- [ ] PR vào `main` ghi `Closes pbl6-home-renter/docs#54` + link các file `api-doc` đã dùng.
- [ ] baoduong17 approve; PR `api-doc` merge cùng lúc.
