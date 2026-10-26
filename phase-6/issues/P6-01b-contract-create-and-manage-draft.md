# P6-01b — Tạo và quản lý hợp đồng nháp

**Epic:** [P6-01](P6-01-tenancy-contract-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** leminhkhai345  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 5 points · 10–14 giờ  
**Phụ thuộc:** P6-01a, P5-09b (đã tạo được Room)  
**Repo / branch:** `Tenancy-Service` · `feature/p6-01b-contract-draft`  
**Issue:** `docs#TBD`

## Mục tiêu

Landlord tạo được HĐ nháp cho phòng của mình (`201 CONTRACT_CREATED`), xem danh sách và chi tiết, và sửa ghi chú khi HĐ còn `draft`. Tenant có tài khoản và là người trong HĐ thì xem được chi tiết HĐ đó.

## Contract

| Endpoint | operationId | Role | Thành công | Lỗi nghiệp vụ |
|---|---|---|---|---|
| `POST /contracts` | `postContracts` | landlord | `201 CONTRACT_CREATED` + header `Location` | `409 ACTIVE_CONTRACT_EXISTS`, `422 TENANT_IDENTITY_INVALID`, `422 VALIDATION_FAILED` |
| `GET /contracts` | `getContracts` | landlord | `200 CONTRACTS_FETCHED` + `pagination` offset | `422 VALIDATION_FAILED` |
| `GET /contracts/{contractId}` | `getContractsContractid` | landlord, tenant | `200 CONTRACT_FETCHED` | `403`, `404` |
| `PATCH /contracts/{contractId}` | `patchContractsContractid` | landlord | `200 CONTRACT_UPDATED` | `409 CONTRACT_NOT_DRAFT` |

- File:
  - `api-doc/src/paths/contracts/contracts.yaml`, `contracts-contractId.yaml`;
  - request `src/requests/contracts/contract-create-request-dto.yaml`, `contract-update-request-dto.yaml`;
  - response `src/responses/dtos/contracts/contract-create-response-dto.yaml`, `contract-list-response-dto.yaml`, `contract-detail-response-dto.yaml`.
- Filter `GET /contracts`: `filter[roomId]`, `filter[buildingId]`, `filter[status]`, `filter[tenantId]`; `pageNo`, `pageSize` (≤ 100). Chỉ hỗ trợ `format=json` (xem Ngoài phạm vi).
- Rule:
  - `landlordId` lấy từ JWT;
  - Room phải tồn tại, chưa xóa, thuộc landlord đó, nếu không trả `403 FORBIDDEN`;
  - phòng đã có HĐ `active` thì trả `409 ACTIVE_CONTRACT_EXISTS`.

## Tham chiếu code

| Cần | Copy pattern từ |
|---|---|
| Command handler UoW + outbox | `src/modules/building/application/commands/building-create/` (P5-08b) hoặc `src/modules/sample/application/commands/sample-create/` |
| Query handler | `src/modules/sample/application/queries/sample-get-by-id/` |
| Controller, `@Roles`, `@CurrentUser`, `Location` header | `building.controller.ts` (P5-08b) |
| Query DTO phân trang | `src/shared/presentation/pagination/offset-pagination.request.dto.ts`, `paginated.response.dto.ts` |
| Đọc Room | `ROOM_DI_TOKEN.REPOSITORY` → `RoomRepository.findById` (`src/modules/room/domain/repositories/room.repository.ts`) |

## Các bước triển khai

### Bước 1 — Đọc contract và chốt các điểm mâu thuẫn

- **Cách làm:**
  - Đọc các file ở mục Contract.
  - Xác nhận với API owner các điểm trong bảng "Sửa contract" của epic: `DAILY`, `tenantCccd`, `paymentDueDay`.
  - Ghi quyết định vào comment issue.
- **Kiểm tra bước:** có comment chốt quyết định của baoduong17 trước khi code request DTO.

### Bước 2 — Create command

- **File tạo:** `src/modules/contract/application/commands/contract-create/contract-create.command.ts` và `.command.handler.ts`.
- **Cách làm:**
  - Handler inject `CONTRACT_DI_TOKEN.REPOSITORY`, `ROOM_DI_TOKEN.REPOSITORY`, `UNIT_OF_WORK_DI_TOKEN`, `OUTBOX_DI_TOKEN.REPOSITORY`.
  - Trong `unitOfWork.run(ctx => …)`:
    1. `room = roomRepository.findByIdForUpdate(roomId, ctx)`. `null` hoặc `room.landlordId !== landlordId` thì ném exception `403 FORBIDDEN`. Tạo `contract-forbidden.exception.ts` (status `403`, code `FORBIDDEN`).
    2. `contractRepository.existsActiveByRoom(roomId, ctx)` trả `true` thì ném `ActiveContractExistsException`.
    3. `ContractEntity.create({...})` → `save` → `outboxRepository.append(pullDomainEvents → OutboxMessage.fromDomainEvent)`.
  - Bắt lỗi unique violation (`postgres-error-code.ts`) của index `UQ_contracts_room_active` rồi map sang `ActiveContractExistsException` (phòng race condition).
- **Kiểm tra bước:** `npm run build` pass.

### Bước 3 — Update command (chỉ khi draft)

- **File tạo:** `.../commands/contract-update/contract-update.command.ts` và `.command.handler.ts`.
- **Cách làm:**
  - `findByIdForUpdate`; `null` thì `ContractNotFoundException`;
  - `contract.landlordId !== landlordId` thì `403`;
  - `contract.updateDraft({ description })` (domain tự ném `CONTRACT_NOT_DRAFT`);
  - `save` + append outbox.
- **Kiểm tra bước:** build pass.

### Bước 4 — Queries

- **File tạo:**
  - `.../queries/contract-get-by-id/`: handler nhận `(contractId, user: AuthenticatedUser)`. Landlord phải là chủ; tenant phải có `contract.tenantId === user.id`. Sai thì `403`, không thấy thì `404`.
  - `.../queries/contract-list/`: gọi `findPageByLandlord(user.id, { pageNo, pageSize, filter })`.
    - Response cần `roomName` và `contractCode`. `roomName` lấy bằng join `rooms` trong repository (cùng DB). `contractCode` sinh dạng `HD-<6 ký tự đầu id>`, ghi `TODO` nếu API owner muốn cột riêng.
    - `filter[buildingId]` join `rooms.building_id`.
- **Kiểm tra bước:** build pass.

### Bước 5 — DTO, response code, controller

- **File tạo** (trong `src/modules/contract/presentation/http/`):
  - `requests/create-contract.request.ts`, đúng rule YAML:
    - `@IsUUID() roomId`;
    - `@IsOptional() @IsUUID() tenantId`;
    - `@Length(1,254) tenantName`;
    - `@Matches(/^(0[0-9]{9}|\+84[0-9]{9})$/) tenantPhone`;
    - `@Length(9,12) tenantCccd`;
    - `@IsInt() @Min(0) depositAmount, rentPrice`;
    - `@IsOptional() @IsInt() @Min(1) @Max(28) paymentDueDay`;
    - `@IsDateString() startDate, endDate`;
    - `@IsOptional() @IsInt() @Min(0) vehicleCount`;
    - `@IsOptional() @IsString() templateKey`;
    - `@IsOptional() @IsObject() templateVariables`.
  - `requests/update-contract.request.ts` (`description` 1–500, nullable).
  - `requests/list-contracts.query.ts`, kế thừa `OffsetPaginationQueryRequestDto` cùng filter.
  - `responses/contract-create.response.dto.ts`, `contract-detail.response.dto.ts`, `contract-list-item.response.dto.ts`, mỗi class có `fromDomain`/`fromReadModel`.
  - `constants/contract-response-code.constant.ts`: `CONTRACT_CREATED`, `CONTRACTS_FETCHED`, `CONTRACT_FETCHED`, `CONTRACT_UPDATED`.
  - `controllers/contract.controller.ts`:
    - `@Controller('contracts')`, 4 route;
    - `@Roles(UserRole.LANDLORD)`, riêng GET detail dùng `@Roles(UserRole.LANDLORD, UserRole.TENANT)`;
    - `operationId` đúng như bảng Contract.
- **File sửa:** `contract.module.ts`, thêm `CqrsModule`, `OutboxModule`, `RoomModule` (đọc repository Room), controller và handler.
- **Kiểm tra bước:**
  - Swagger `/api/v1/tenancy/swagger` có đủ 4 operation;
  - body có field lạ trả `422 UNEXPECTED_FIELD`.

### Bước 6 — Kiểm tra outbox và rollback

- **Cách làm:**
  - Tạo HĐ, rồi `SELECT event_type FROM outbox_messages ORDER BY sequence DESC LIMIT 1` phải ra `ContractCreated`.
  - Tạm `throw` sau `outboxRepository.append`: API trả `500`, không còn row ở `contracts` lẫn `outbox_messages`. Xóa dòng throw.
- **Kiểm tra bước:** ghi kết quả query vào PR.

## Quyết định tạm thời / Ngoài phạm vi

- `format=xlsx|csv|pdf` cho `GET /contracts`: chưa làm, trả `422 VALIDATION_FAILED` khi khác `json` (ghi `TODO(export)`).
- `templateVariables` ở create: nhận và validate là object, **chưa lưu** (mẫu áp ở P6-01c).
- Kiểm tra `tenantId` có tồn tại bên Identity: chưa làm (internal HTTP client chỉ GET; ghi `TODO`).

## Cập nhật `api-doc`

- [ ] Sequence diagram cho `postContracts` (Gateway → Tenancy → DB: rooms lock + contracts + outbox → Relay → RabbitMQ) và cho `getContracts`, `getContractsContractid`, `patchContractsContractid`.
- [ ] Sửa `contract-create-request-dto.yaml` theo quyết định ở Bước 1.
- [ ] `x-apidog-status` → `released` cho 4 endpoint; sync Apidog.

## Manual verification (Apidog)

1. Landlord tạo HĐ cho phòng của mình, tenant ẩn danh (`tenantId = null`) → `201 CONTRACT_CREATED`, `status = draft`, có header `Location`.
2. `tenantId = null` và thiếu `tenantPhone` → `422`.
3. Phòng của landlord khác → `403 FORBIDDEN`.
4. Phòng đã có HĐ `active` (update tay DB) → `409 ACTIVE_CONTRACT_EXISTS`.
5. `GET /contracts?filter[status]=draft&pageSize=1` → `200`, `pagination.type = offset`.
6. `PATCH` khi HĐ `active` → `409 CONTRACT_NOT_DRAFT`.
7. Token tenant trong HĐ → `GET /contracts/{id}` `200`; tenant khác → `403`.

## Definition of Done

- [ ] Bước 1–6 đã qua phần Kiểm tra bước.
- [ ] `npm run build` + `npm run lint` pass.
- [ ] PR ghi `Closes pbl6-home-renter/docs#TBD` + link file `api-doc`.
- [ ] baoduong17 approve; PR `api-doc` merge cùng lúc.
