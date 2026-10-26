# P6-01a — Contract domain model, persistence và migration

**Epic:** [P6-01](P6-01-tenancy-contract-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** leminhkhai345  
**Người review:** baoduong17 (BE Lead)  
**Ước lượng:** 3 points · 6–8 giờ  
**Phụ thuộc:** P5-09a (bảng `rooms` phải có migration)  
**Repo / branch:** `Tenancy-Service` · `feature/p6-01a-contract-domain`  
**Issue:** `docs#TBD`

## Mục tiêu

Có aggregate `ContractEntity` với đầy đủ state machine (`draft → signed → active`, cùng các trạng thái kết thúc), repository TypeORM và migration bảng `contracts` chạy được từ DB trống. Task này chưa có endpoint.

## Contract

- Field lấy theo `api-doc/src/requests/contracts/contract-create-request-dto.yaml` và `src/responses/dtos/contracts/contract-detail-response-dto.yaml`.
- Bảng theo `pm/phase-1/discovery/database-design.md` §2.7.
- Status enum: `draft | signed | active | suspended | expired | terminated`.
- Ràng buộc DB:
  - `contract_tenant_identity_check`: `tenant_id IS NOT NULL OR (tenant_name, tenant_phone không rỗng)`;
  - `start_date < end_date`;
  - `deposit_amount >= 0`, `rent_price >= 0`;
  - partial unique index `(room_id) WHERE status = 'active' AND is_deleted = false`.

## Tham chiếu code

| Cần | Copy pattern từ |
|---|---|
| Aggregate, `create`/`reconstitute`, domain event | `src/modules/building/domain/entities/building.entity.ts`, `building.props.ts`, `domain/events/building-created.event.ts` |
| Event name constant | `src/modules/building/domain/constants/building-event.constants.ts` |
| Domain exception (status + code) | `src/modules/building/domain/exceptions/invalid-building-status-transition.exception.ts` |
| Repository interface + TypeORM impl + mapper | `src/modules/building/domain/repositories/building.repository.ts`, `infrastructure/persistence/building.repository.ts`, `mappers/building.mapper.ts` |
| TypeORM entity | `src/modules/room/infrastructure/persistence/room.typeorm-entity.ts` |
| Module + DI token | `src/modules/building/building.module.ts`, `building.di-token.ts` |

## Các bước triển khai

### Bước 1 — Chạy service local từ DB trống

- **Cách làm:**
  - Pull `main` sau khi P5-08b (sửa migration buildings) và P5-09b (migration rooms) đã merge.
  - `npm ci && npm run schema:drop && npm run migration:run && npm run start:dev`.
- **Kiểm tra bước:** `GET http://localhost:3002/api/v1/tenancy/health` trả `200`; bảng `buildings` và `rooms` đã tồn tại.

### Bước 2 — Enum, props, events, exceptions

- **File tạo** (trong `src/modules/contract/domain/`):
  - `enums/contract-status.enum.ts` gồm 6 giá trị ở trên.
  - `entities/contract.props.ts`:
    - `CreateContractProps { landlordId, roomId, tenantId: Uuid | null, tenantName, tenantPhone, tenantCccd, depositAmount, rentPrice, paymentDueDay: number | null, startDate: string /* YYYY-MM-DD */, endDate, vehicleCount: number | null, templateKey: string | null }`;
    - `ContractProps = CreateContractProps & { id, status, description, signedContractMediaId, draftDocumentMediaId, activatedAt, createdAt, updatedAt, isDeleted }`;
    - `UpdateContractProps` chỉ gồm `description` (theo `contract-update-request-dto.yaml`).
  - `constants/contract-event.constants.ts`: `CONTRACT_CREATED`, `CONTRACT_UPDATED`, `CONTRACT_ACTIVATED`.
  - `events/contract-created.event.ts`, `contract-updated.event.ts`, `contract-activated.event.ts` (copy khung từ `building-created.event.ts`).
  - Exceptions:
    - `contract-not-found.exception.ts` (`404`, `RESOURCE_NOT_FOUND`);
    - `contract-not-draft.exception.ts` (`409`, `CONTRACT_NOT_DRAFT`);
    - `contract-not-ready.exception.ts` (`409`, `CONTRACT_NOT_READY`);
    - `tenant-identity-invalid.exception.ts` (`422`, `TENANT_IDENTITY_INVALID`);
    - `active-contract-exists.exception.ts` (`409`, `ACTIVE_CONTRACT_EXISTS`).
- **Kiểm tra bước:** `npm run build` pass.

### Bước 3 — Aggregate `ContractEntity`

- **File tạo:** `src/modules/contract/domain/entities/contract.entity.ts`.
- **Cách làm:**
  - `static create(props)`:
    - validate: `tenantId` null thì `tenantName` và `tenantPhone` phải khác rỗng, nếu không ném `TenantIdentityInvalidException`;
    - validate `startDate < endDate`; số tiền `>= 0`; `paymentDueDay` 1–28;
    - `status = draft`; add `ContractCreatedEvent`.
  - `static reconstitute(props)` (không phát event).
  - `updateDraft(input)`: `assertDraft()`, gán `description`, gọi `touch()`, add `ContractUpdatedEvent`.
  - `applyTemplate(templateKey)` và `attachDraftDocument(mediaId)`: chỉ cho phép khi đang `draft`.
  - `activate(signedMediaId: Uuid, now: Date)`:
    - chỉ cho phép từ `draft | signed`, nếu không ném `ContractNotReadyException`;
    - gán `signedContractMediaId`, `status = active`, `activatedAt = now`;
    - add `ContractActivatedEvent(contractId, roomId, landlordId, tenantId)`.
  - Private helpers `assertDraft()`, `assertNotDeleted()`, `touch()` (copy từ Building).
- **Kiểm tra bước:** viết test nhỏ `contract.entity.spec.ts`, hoặc script `ts-node` tạm, cho 3 case:
  - tenant ẩn danh thiếu phone → lỗi;
  - `activate` khi `active` → lỗi;
  - `create` → `pullDomainEvents()` có 1 event.

### Bước 4 — Persistence

- **File tạo** (trong `src/modules/contract/`):
  - `domain/repositories/contract.repository.ts`:
    - `findById`, `findByIdForUpdate(id, ctx)`;
    - `existsActiveByRoom(roomId, ctx?)`;
    - `findPageByLandlord(landlordId, query: OffsetPageQuery<ContractListFilter>)`, dùng `PaginatedResult` từ `shared/application/pagination`.
  - `infrastructure/persistence/contract.typeorm-entity.ts`, bảng `contracts`. Cột snake_case: `landlord_id`, `room_id`, `tenant_id`, `tenant_name`, `tenant_phone`, `tenant_cccd`, `status` (enum), `deposit_amount bigint`, `rent_price bigint`, `payment_due_day int null`, `start_date date`, `end_date date`, `vehicle_count int null`, `description text null`, `template_key varchar(100) null`, `draft_document_media_id uuid null`, `signed_contract_media_id uuid null`, `activated_at timestamptz null`.
  - `infrastructure/persistence/mappers/contract.mapper.ts`.
  - `infrastructure/persistence/contract.repository.ts`: phân trang dùng `TypeOrmOffsetPaginator` (`src/shared/infrastructure/database/pagination/offset.paginator.ts`).
  - `contract.di-token.ts`, `contract.module.ts`.
- **File sửa:** `src/app.module.ts`, thêm `ContractModule` vào `imports`.
- **Kiểm tra bước:** `npm run build` pass; app khởi động không lỗi DI.

### Bước 5 — Migration

- **Cách làm:**
  - `npm run migration:generate -- src/database/migrations/CreateContractsTable`.
  - **Mở file và xóa mọi câu lệnh không thuộc `contracts`.** Đây là lỗi đã gặp ở migration buildings: `generate` sinh lại outbox/samples.
  - Thêm tay vào `up()`:
    - `CONSTRAINT "CHK_contracts_tenant_identity" CHECK (tenant_id IS NOT NULL OR (NULLIF(BTRIM(tenant_name),'') IS NOT NULL AND NULLIF(BTRIM(tenant_phone),'') IS NOT NULL))`;
    - `CHECK (start_date < end_date)`;
    - `CREATE UNIQUE INDEX "UQ_contracts_room_active" ON contracts (room_id) WHERE status = 'active' AND is_deleted = false`;
    - index `(landlord_id) WHERE is_deleted = false`.
  - `down()` drop đúng thứ tự ngược lại.
- **Kiểm tra bước:**
  - `npm run schema:drop && npm run migration:run` pass, sau đó `npm run migration:revert` pass;
  - `\d contracts` trong psql hiện đủ CHECK và index;
  - insert tay 2 row `active` cùng `room_id` thì row thứ hai bị lỗi unique.

## Quyết định tạm thời / Ngoài phạm vi

- `rentalType`: chờ API owner chốt bỏ `DAILY` (xem epic). Trong lúc chờ, **không** lưu cột này; mặc định coi là `MONTHLY`.
- `tenant_cccd`: thêm cột theo đề xuất ở epic. Nếu API owner quyết bỏ thì xóa cột trước khi merge.
- `ContractMember` (bảng `contract_members`) thuộc P6-01e.
- Các trạng thái `suspended`/`expired`/`terminated`: chỉ khai báo enum, chưa có method chuyển trạng thái.

## Cập nhật `api-doc`

- [ ] Không có endpoint. Nếu chốt bỏ `DAILY`/giữ `tenantCccd`, mở PR `api-doc` sửa `contract-create-request-dto.yaml` và link vào issue.

## Manual verification

1. Migration chạy và revert được trên DB trống.
2. Test hoặc script ở Bước 3 pass cả 3 case.
3. CHECK tenant identity: insert `tenant_id NULL, tenant_phone NULL` thì bị DB từ chối.

## Definition of Done

- [ ] Bước 1–5 đã qua phần Kiểm tra bước.
- [ ] `npm run build` + `npm run lint` pass.
- [ ] PR ghi `Closes pbl6-home-renter/docs#TBD`; đính kèm output `\d contracts`.
- [ ] baoduong17 approve.
