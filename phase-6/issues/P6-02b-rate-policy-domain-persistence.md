# P6-02b — RatePolicy domain và persistence

**Epic:** [P6-02](P6-02-tenancy-billing-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** huynhtiennhat0403  
**Người review:** baoduong17 (BE Lead)  
**Ước lượng:** 3 points · 6–8 giờ  
**Phụ thuộc:** P6-02a (contract đã chốt)  
**Repo / branch:** `Tenancy-Service` · `feature/p6-02b-rate-policy-domain`  
**Issue:** `docs#TBD`

## Mục tiêu

Có aggregate `RatePolicy` (1 bộ/scope, `rates` jsonb — D39) với đầy đủ rule validate D31–D33, bảng `rate_policies` có migration chạy được, và repository dùng được trong UoW. Chưa có HTTP endpoint.

## Contract

- Shape đã chốt ở P6-02a: `api-doc/src/schemas/billing/rate-policy.yaml`, `api-doc/src/schemas/billing/rate-item.yaml`.
- Bảng: `pm/phase-1/discovery/database-design.md` §2.9 (`landlord_id`, `scope`, `building_id`, `room_id`, `rates jsonb`, `is_active`).
- Rule: `utility-billing-calculations.md` §1 (ma trận rate kind), §11 EC13, §12 D33.

## Tham chiếu code (đã có trong repo)

| Cần | Copy pattern từ |
|---|---|
| Aggregate + `reconstitute` + `addDomainEvent` | `src/modules/building/domain/entities/building.entity.ts`, `building.props.ts` |
| Value object có validate | `src/modules/room/domain/value-objects/room-amenities.vo.ts` |
| Event constants + event class | `src/modules/building/domain/constants/building-event.constants.ts`, `src/modules/building/domain/events/building-created.event.ts` |
| Exception có HTTP code | `src/modules/building/domain/exceptions/building-not-found.exception.ts` (`DomainException(message, status, code)`) |
| TypeORM entity + `@Check` + partial index | `src/modules/building/infrastructure/persistence/building.typeorm-entity.ts` |
| Mapper, repository `withTransaction`, `findByIdForUpdate` | `src/modules/room/infrastructure/persistence/mappers/room.mapper.ts`, `room.repository.ts` |
| Module + DI token | `src/modules/room/room.module.ts`, `room.di-token.ts` |

## Các bước triển khai

### Bước 1 — Chạy service local

- **Cách làm:** pull `main`, tạo branch; `npm ci && npm run migration:run && npm run start:dev`.
- **Kiểm tra bước:** `GET http://localhost:3002/api/v1/tenancy/health` → `200`. Nếu `migration:run` lỗi `relation already exists` ở `CreateBuildingsTable` → chờ fix của P5-08b bước 1 (không tự sửa trong task này). Bảng `rooms` phải tồn tại (P5-09b).

### Bước 2 — Enum và value object `RateItem`

- **File tạo:**
  - `src/modules/rate-policy/domain/enums/rate-policy-scope.enum.ts`: `BUILDING = 'building'`, `ROOM = 'room'`.
  - `.../domain/enums/rate-type.enum.ts`: `electricity|water|wifi|cleaning|parking|maintenance|other`.
  - `.../domain/enums/rate-kind.enum.ts`: `flat|tiered|fixed_per_period|per_head|per_area_m2|per_vehicle`.
  - `.../domain/enums/billing-unit.enum.ts`: `kwh|m3|room|person|m2|vehicle|day|occurrence`.
  - `.../domain/value-objects/rate-item.vo.ts`: `RateItem.create({ type, name, rateKind, unitPrice, steps, billingUnit })`.
  - `.../domain/exceptions/invalid-rate-kind.exception.ts` (`422 INVALID_RATE_KIND`), `tier-config-invalid.exception.ts` (`422 TIER_CONFIG_INVALID`).
- **Cách làm (validate trong `RateItem.create`):**
  - `name` trim 1–100 ký tự.
  - `electricity` chỉ nhận `flat` | `tiered`; `per_head` chỉ cho `water` và phí (`wifi`…`other`); `water` không nhận `per_area_m2`/`per_vehicle` (D33) → sai thì `InvalidRateKindException`.
  - `tiered`: `unitPrice` phải `null`, `steps` ≥ 1 bậc, bậc đầu `from = 0`, mỗi bậc `from` = `to` bậc trước, chỉ bậc cuối `to = null`, `price ≥ 0` → sai thì `TierConfigInvalidException` (EC13).
  - Không phải `tiered`: `unitPrice` bắt buộc, là chuỗi decimal ≥ 0 (regex `^\d+(\.\d{1,2})?$`), `steps` phải `null`.
  - Giữ tiền ở dạng **string** (không parse sang `number`).
- **Kiểm tra bước:** viết file thử nhanh `src/modules/rate-policy/domain/value-objects/rate-item.vo.spec.ts` (nếu repo chưa có test runner thì chạy bằng `npx ts-node -r tsconfig-paths/register` một script tạm) cho 4 case: điện `per_head` → lỗi; tiered thiếu bậc ∞ → lỗi; nước `per_head` 100000 → ok; EVN 6 bậc → ok. Xóa script tạm nếu không giữ test.

### Bước 3 — Aggregate `RatePolicyEntity` và event

- **File tạo:**
  - `.../domain/entities/rate-policy.props.ts`: `CreateRatePolicyProps { landlordId, scope, buildingId: Uuid|null, roomId: Uuid|null, rates: RateItem[] }`, `RatePolicyProps` thêm `id, isActive, createdAt, updatedAt, isDeleted`.
  - `.../domain/entities/rate-policy.entity.ts` (extends `AggregateRoot`): `static create`, `static reconstitute`, `replaceRates(rates)`, `activate()`, `deactivate()`, getter.
  - `.../domain/constants/rate-policy-event.constants.ts`: `RATE_POLICY_AGGREGATE_TYPE = 'RatePolicy'`, events `rate_policy.created|updated|deactivated` (theo format `building.created`).
  - `.../domain/events/rate-policy-created.event.ts`, `rate-policy-updated.event.ts`, `rate-policy-deactivated.event.ts` (payload: `id, landlordId, scope, buildingId, roomId, isActive`).
  - `.../domain/exceptions/policy-not-active.exception.ts` (`409 POLICY_NOT_ACTIVE`), `rate-policy-not-found.exception.ts` (`404 RESOURCE_NOT_FOUND`).
- **Cách làm:**
  - `create`: `scope=building` ⇒ `buildingId` bắt buộc, `roomId=null`; `scope=room` ⇒ `roomId` bắt buộc, `buildingId` = building của phòng (handler truyền vào) → sai thì `ValidationException`. `rates` ≥ 1 mục, không trùng `type` (mỗi loại phí 1 mục — §4 `pickRate`). `isActive = true`.
  - `deactivate()` khi đang tắt → `PolicyNotActiveException`.
  - Mỗi hành vi `addDomainEvent(...)`.
- **Kiểm tra bước:** `npm run build` pass.

### Bước 4 — TypeORM entity, mapper, migration

- **File tạo:**
  - `src/modules/rate-policy/infrastructure/persistence/rate-policy.typeorm-entity.ts`: `@Entity('rate_policies')` extends `AbstractEntity`; cột `landlordId uuid`, `scope enum`, `buildingId uuid null`, `roomId uuid null`, `rates jsonb default '[]'`, `isActive boolean default true`.
    - `@Check('CHK_rate_policies_scope_target', "(scope = 'building' AND building_id IS NOT NULL AND room_id IS NULL) OR (scope = 'room' AND room_id IS NOT NULL)")`.
    - Unique partial index 1 bộ/scope: `UQ_rate_policies_building` trên `building_id` `WHERE scope = 'building' AND is_deleted = false`; `UQ_rate_policies_room` trên `room_id` `WHERE scope = 'room' AND is_deleted = false`.
  - `.../persistence/mappers/rate-policy.mapper.ts`: `toDomain` (map `rates` jsonb → `RateItem.reconstitute`), `toPersistence` (key DB dạng snake: `rate_kind`, `unit_price`, `billing_unit` như §2.9).
  - Migration: `npm run migration:generate -- src/database/migrations/CreateRatePoliciesTable` → **mở file, chỉ giữ** `CREATE TYPE`/`CREATE TABLE "rate_policies"`/index của bảng này; xóa mọi câu tạo bảng khác (lỗi đã gặp ở `CreateBuildingsTable`).
- **Kiểm tra bước:** `npm run migration:run` rồi `npm run migration:revert` rồi `npm run migration:run` đều pass; `\d rate_policies` trong psql thấy 2 unique index + check.

### Bước 5 — Repository và module

- **File tạo:**
  - `.../domain/repositories/rate-policy.repository.ts`: extends `BaseRepository<RatePolicyEntity>`, thêm `findById`, `findByIdForUpdate(id, ctx)`, `findByBuilding(buildingId, ctx?)`, `findByRoom(roomId, ctx?)`, `findPage(landlordId, query: OffsetPageQuery<{scope?, roomId?, buildingId?}>)`.
  - `.../infrastructure/persistence/rate-policy.repository.ts`: `TypeOrmRatePolicyRepository` dùng `withTransaction(...)` như `TypeOrmRoomRepository`; `findPage` dùng `TypeOrmPaginator.offset(...)` (`src/shared/infrastructure/database/pagination/typeorm.paginator.ts`).
  - `src/modules/rate-policy/rate-policy.di-token.ts`, `rate-policy.module.ts` (imports `TypeOrmModule.forFeature([RatePolicyTypeormEntity])`, export `RATE_POLICY_DI_TOKEN.REPOSITORY`).
- **File sửa:** `src/app.module.ts` — thêm `RatePolicyModule`.
- **Kiểm tra bước:** `npm run build` + `npm run lint` pass; service khởi động không lỗi DI.

## Quyết định tạm thời / Ngoài phạm vi

- Không có endpoint (P6-02c). Không làm resolve `room → building` (dùng khi tính hóa đơn, P6-02g).
- Preset EVN/phí định kỳ (D31/D32) là seed — **chưa làm**, ghi `TODO(seed-presets)` trong `rate-item.vo.ts`.

## Manual verification

1. Migration up/down/up sạch trên DB trống.
2. Insert tay 2 bộ scope building cùng `building_id` → lỗi unique.
3. Kết quả 4 case validate ở bước 2 ghi vào PR.

## Definition of Done

- [ ] Bước 1–5 qua phần Kiểm tra bước.
- [ ] `npm run build` + `npm run lint` pass.
- [ ] PR vào `main` ghi `Closes pbl6-home-renter/docs#TBD`, link `api-doc/src/schemas/billing/rate-policy.yaml`.
- [ ] baoduong17 approve.
