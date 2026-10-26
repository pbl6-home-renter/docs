# P5-08c — Landlord quản lý Building

**Epic:** [P5-08](P5-08-tenancy-building-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** leminhkhai345  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 5 points · 10–14 giờ  
**Phụ thuộc:** P5-08b  
**Repo / branch:** `Tenancy-Service` · `feature/p5-08c-building-landlord-management`

## Mục tiêu

Landlord xem danh sách và chi tiết Building **của chính mình**, sửa Building chưa duyệt, và xóa mềm Building. Command đi qua UoW + outbox như P5-08b; query đọc qua query service riêng, không đưa query logic vào entity.

## Contract

| Endpoint | operationId | File `api-doc` | Success |
|---|---|---|---|
| `GET /me/buildings` | `getMeBuildings` | `src/paths/buildings/me-buildings.yaml` | `200 BUILDINGS_MY_FETCHED` + `pagination` |
| `GET /me/buildings/{buildingId}` | `getMeBuildingsBuildingid` | `src/paths/buildings/me-buildings-buildingId.yaml` | `200 BUILDING_MY_FETCHED` |
| `PATCH /buildings/{buildingId}` | `patchBuildingsBuildingid` | `src/paths/buildings/buildings-buildingId.yaml` (`patch`) | `200 BUILDING_UPDATED` |
| `DELETE /buildings/{buildingId}` | `deleteBuildingsBuildingid` | `src/paths/buildings/buildings-buildingId.yaml` (`delete`) | `204` |

- Role: `landlord` cho cả 4 endpoint.
- DTO: `src/responses/dtos/buildings/my-building-list-response-dto.yaml`, `my-building-detail-response-dto.yaml`, `building-update-response-dto.yaml`; request `src/requests/buildings/building-update-request-dto.yaml` (chỉ `name`, `address`).
- List: `filter[status]`, `sort` (mặc định `createdAt`), `order` (mặc định `desc`), `pageNo`, `pageSize` (1–100).
- Rule: Building của landlord khác → `404 RESOURCE_NOT_FOUND` (không lộ sự tồn tại). Building `approved` → `PATCH` trả `409 APPROVED_BUILDING_LOCKED`.
- Lỗi: `401`, `403 FORBIDDEN`, `404 RESOURCE_NOT_FOUND`, `409`, `422 VALIDATION_FAILED`.

## Tham chiếu code (đã có trong repo)

| Cần | Copy pattern từ |
|---|---|
| Command handler UoW + outbox | `src/modules/building/application/commands/building-create/` (tạo ở P5-08b) |
| Controller Building, response code constant | `src/modules/building/presentation/http/controllers/building.controller.ts`, `.../constants/building-response-code.constant.ts` (P5-08b) |
| Query handler đơn giản | `src/modules/sample/application/queries/sample-get-by-id/` |
| Query service + list có filter/sort/pagination | `Identity-Service/src/modules/users/application/ports/user-query-service.port.ts` + `infrastructure/services/user-query.service.ts` (`findUsersAdmin`) |
| Query request DTO list | `Identity-Service/src/modules/users/presentation/http/requests/user-list-admin.query.request.dto.ts` (kế thừa `OffsetPaginationQueryRequestDto`) |
| Pagination dùng chung | `src/shared/infrastructure/database/pagination/typeorm.paginator.ts` (`TypeOrmPaginator.offset(qb, q).withSort({...}).paginate(mapper)`), `src/shared/presentation/pagination/paginated.response.dto.ts` |
| Domain đã có (**dùng lại**) | `BuildingEntity.update()` (đã ném `ApprovedBuildingLockedException` 409), `BuildingEntity.delete()` (phát `BuildingDeletedEvent`), `BuildingRepository.findByIdForUpdate()`, `BuildingNotFoundException` (404 `RESOURCE_NOT_FOUND`) |

## Các bước triển khai

### Bước 1 — Pull code P5-08b và chạy local

- **Cách làm:**
  - Pull `main` (đã có P5-08b), tạo branch `feature/p5-08c-building-landlord-management`.
  - `npm ci && npm run migration:run && npm run start:dev`.
  - Tạo sẵn 2 Building bằng `POST /buildings` với 2 token landlord khác nhau (A, B) để test.
- **Kiểm tra bước:** `GET /api/v1/tenancy/health` = `200`; DB có 2 row `buildings` khác `landlord_id`.

### Bước 2 — Query service cho Building (read side)

- **File tạo:**
  - `src/modules/building/application/ports/building-query-service.port.ts`: interface `IBuildingQueryService` với `findMyBuildings(landlordId: Uuid, q: OffsetPageQuery<MyBuildingFilter>): Promise<PaginatedResult<BuildingEntity>>` và `findMyBuildingById(landlordId: Uuid, id: Uuid): Promise<BuildingEntity | null>`.
  - `src/modules/building/application/queries/models/my-building-filter.model.ts`: `{ status?: BuildingStatus }`.
  - `src/modules/building/infrastructure/services/building-query.service.ts`: implement bằng `createQueryBuilder('building')` + `where building.isDeleted = false AND building.landlordId = :landlordId`; nếu có `filter.status` thì `andWhere`; `TypeOrmPaginator.offset(qb, q).withSort({ whitelist: ['createdAt', 'name', 'status'], defaultSort: 'createdAt', defaultOrder: 'desc', alias: 'building' }).paginate(BuildingMapper.toDomain)`.
- **File sửa:** `src/modules/building/building.di-token.ts`: thêm `QUERY_SERVICE: Symbol('BUILDING_QUERY_SERVICE')`.
- **Cách làm:** detail cũng lọc `landlordId` ngay trong query (không lấy ra rồi mới so sánh) ⇒ Building người khác trả `null` → 404.
- **Kiểm tra bước:** `npm run build` pass.

### Bước 3 — Query + handler + response DTO

- **File tạo:**
  - `src/modules/building/application/queries/building-list-mine/building-list-mine.query(.handler).ts`.
  - `src/modules/building/application/queries/building-get-mine/building-get-mine.query(.handler).ts`: `null` → `throw new BuildingNotFoundException(id)`.
  - `src/modules/building/presentation/http/requests/building-list-mine.query.request.dto.ts`: `extends OffsetPaginationQueryRequestDto<MyBuildingFilter>`; validate `filter.status` ∈ `pending|approved|rejected` (`@IsIn`).
  - `src/modules/building/presentation/http/responses/my-building-list.response.dto.ts`, `my-building-detail.response.dto.ts`: field đúng schema (`fromDomain`). Map `note` → `rejectionReason` (list, chỉ khi `rejected`) và `reviewNote` (detail).
- **Cách làm:** các field chưa có nguồn dữ liệu trả giá trị tạm theo mục *Quyết định tạm thời* (không bỏ field `required`).
- **Kiểm tra bước:** `npm run build` pass.

### Bước 4 — Controller cho 2 endpoint GET

- **File tạo:** `src/modules/building/presentation/http/controllers/my-building.controller.ts` — `@Controller('me/buildings')`, `@Roles(UserRole.LANDLORD)`.
  - `@Get()` `operationId: 'getMeBuildings'`, `@ResponseCode(BUILDINGS_MY_FETCHED)` → `PaginatedResponseDto.create({ data: result.data.map(MyBuildingListResponseDto.fromDomain), pagination: result.pagination })` (giống `user-admin.controller.ts`).
  - `@Get(':buildingId')` `operationId: 'getMeBuildingsBuildingid'`, `@ResponseCode(BUILDING_MY_FETCHED)`; dùng `ParseUUIDPipe` hoặc validator `is-uuid` có sẵn trong `src/shared/presentation/validators/is-uuid.decorator.ts`.
- **File sửa:** `building-response-code.constant.ts` thêm `BUILDINGS_MY_FETCHED`, `BUILDING_MY_FETCHED`, `BUILDING_UPDATED`, `BUILDING_DELETED`; `building.module.ts` thêm controller, query handlers, provider `{ provide: BUILDING_DI_TOKEN.QUERY_SERVICE, useClass: BuildingQueryService }`.
- **Kiểm tra bước:** token A gọi list chỉ thấy Building của A; `pageSize=1` trả `pagination.totalPages` đúng; gọi detail Building của B → `404`.

### Bước 5 — Command `PATCH /buildings/{buildingId}`

- **File tạo:**
  - `src/modules/building/application/commands/building-update/building-update.command(.handler).ts`: `BuildingUpdateCommand(landlordId, buildingId, name?, address?)`.
  - `src/modules/building/presentation/http/requests/update-building.request.ts`: `@IsOptional() @IsString() @Length(1,254)` cho `name`, `address`.
  - `src/modules/building/presentation/http/responses/building-update.response.dto.ts`: `id, name, address, status`.
- **Cách làm (handler):** `unitOfWork.run(ctx => …)`: `findByIdForUpdate(id, ctx)` → `null` hoặc `landlordId !== command.landlordId` ⇒ `BuildingNotFoundException` → `building.update({ name, address })` (domain tự ném `409 APPROVED_BUILDING_LOCKED`) → `save` → `outboxRepository.append(pullDomainEvents().map(OutboxMessage.fromDomainEvent), ctx)`.
- **File sửa:** `building.controller.ts` thêm `@Patch(':buildingId') @Roles(UserRole.LANDLORD)`, `operationId: 'patchBuildingsBuildingid'`, `@ResponseCode(BUILDING_UPDATED)`.
- **Kiểm tra bước:** sửa Building `pending` → `200`; outbox có `BuildingUpdated`; body rỗng `{}` → xem *Quyết định tạm thời*.

### Bước 6 — Command `DELETE /buildings/{buildingId}`

- **File tạo:** `src/modules/building/application/commands/building-delete/building-delete.command(.handler).ts` (copy khung `src/modules/sample/application/commands/sample-delete/`).
- **Cách làm (handler):** trong UoW: `findByIdForUpdate` + check owner như Bước 5 → `building.delete()` → `buildingRepository.save(building, ctx)` (mapper ghi `isDeleted = true`; **không** gọi `repository.delete()` vì sẽ mất domain event) → append outbox. Để `// TODO(contract): throw BUILDING_HAS_ACTIVE_CONTRACT khi có Contract`.
- **File sửa:** `building.controller.ts` thêm `@Delete(':buildingId') @HttpCode(204) @Roles(UserRole.LANDLORD)`, `operationId: 'deleteBuildingsBuildingid'`.
- **Kiểm tra bước:** xóa → `204`; list không còn Building đó; outbox có `BuildingDeleted`; gọi xóa lần 2 → `404`.

### Bước 7 — Build, lint, Swagger

- **Kiểm tra bước:** `npm run build` + `npm run lint` pass; Swagger tại `/api/v1/tenancy/swagger` có đủ 4 `operationId` trên.

## Quyết định tạm thời / Ngoài phạm vi

- **`BUILDING_HAS_ACTIVE_CONTRACT`:** domain Contract chưa có → bỏ qua check, để `TODO` ở handler delete.
- **`totalRooms`, `occupiedRooms`, `occupancyRate`:** bảng `rooms` chưa có migration (P5-09b) và chưa có Contract ⇒ trả `0`, `0`, `"0%"`, ghi `TODO(room)`. Khi P5-09b merge, thay `totalRooms` bằng `COUNT(rooms)` (subquery trong `BuildingQueryService`).
- **`ownershipCertificateUrls` = `[]`, `vietQrConfigured` = `false`, `ratePolicies` = `[]`:** media/billing chưa có, ghi `TODO`.
- **`format` (xlsx/csv/pdf) trên `GET /me/buildings`:** chỉ làm `json`. Ghi blocker cho API owner: đề xuất bỏ `format` khỏi list endpoint hoặc dời sang phase sau; không tự làm export.
- **`PATCH` body rỗng `{}`:** contract không có `minProperties`; domain `update()` vẫn phát `BuildingUpdated`. Tạm giữ hành vi domain (trả `200`), ghi câu hỏi cho API owner trong issue về việc thêm `minProperties: 1`.
- `filter[status]` trong contract là `string` không có enum — validate theo enum `BuildingStatus` và đề xuất bổ sung `enum` vào contract.

## Cập nhật `api-doc` (bắt buộc trước khi đóng issue)

- [ ] **Xóa `district`** (lỗi contract, đã chốt bỏ): `src/responses/dtos/buildings/my-building-detail-response-dto.yaml` (property + `required`) và example trong `src/paths/buildings/me-buildings-buildingId.yaml`.
- [ ] Thêm `enum: [pending, approved, rejected]` cho `filter.status` trong `me-buildings.yaml`.
- [ ] Sequence diagram cho `getMeBuildings`, `getMeBuildingsBuildingid`, `patchBuildingsBuildingid`, `deleteBuildingsBuildingid` (command: Gateway → Tenancy → DB transaction buildings + outbox → Relay → RabbitMQ). Tham khảo `src/paths/auth/register.yaml`.
- [ ] `x-apidog-status: designing` → `released` cho 4 endpoint; sync Apidog; link PR `api-doc` vào issue.

## Manual verification (Apidog)

1. Token landlord A: `GET /me/buildings` chỉ trả Building của A; `filter[status]=pending`, `pageSize=1&pageNo=2` đúng `pagination`.
2. `GET /me/buildings/{id của B}` bằng token A → `404 RESOURCE_NOT_FOUND`.
3. `PATCH` Building `pending` → `200 BUILDING_UPDATED`, outbox có `BuildingUpdated`.
4. `PATCH` Building `approved` (approve bằng SQL hoặc sau P5-08d) → `409 APPROVED_BUILDING_LOCKED`.
5. `PATCH` với field ngoài contract (`province`) → `422 UNEXPECTED_FIELD`; `name: ""` → `422 VALIDATION_FAILED`.
6. `DELETE` → `204`; list không còn; outbox có `BuildingDeleted`. Token tenant gọi bất kỳ endpoint nào → `403`.

## Definition of Done

- [ ] Bước 1–7 đã qua phần Kiểm tra bước.
- [ ] `npm run build` + `npm run lint` pass.
- [ ] PR vào `main` ghi `Closes pbl6-home-renter/docs#53` + link các file `api-doc` đã dùng.
- [ ] baoduong17 approve; PR `api-doc` merge cùng lúc.
