# P5-08b — Create Building (slice mẫu UoW + Outbox)

**Epic:** [P5-08](P5-08-tenancy-building-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** leminhkhai345  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 5 points · 10–14 giờ  
**Phụ thuộc:** P5-08a  
**Repo / branch:** `Tenancy-Service` · `feature/p5-08b-building-create`

## Mục tiêu

Landlord gọi `POST /api/v1/buildings` tạo được Building ở trạng thái `pending`, nhận `201 BUILDING_CREATED`; cùng transaction ghi outbox để relay publish `BuildingCreated`. Đây là **slice mẫu**: các command khác của Building và Room làm theo đúng pattern này.

## Contract

- Endpoint: `api-doc/src/paths/buildings/buildings.yaml` (`post` → `postBuildings`).
- Request: `api-doc/src/requests/buildings/building-create-request-dto.yaml`.
- Role: `landlord`. Response `201`, code `BUILDING_CREATED`, header `Location: /api/v1/buildings/{id}`.
- Rule: Building mới luôn `status = pending`; `landlord_id` lấy từ JWT (`@CurrentUser()`), **không** nhận từ body.
- Lỗi: `422 VALIDATION_FAILED`, `401`, `403 FORBIDDEN`.

## Tham chiếu code (đã có trong repo)

| Cần | Copy pattern từ |
|---|---|
| Command + handler (UoW + outbox) | `src/modules/sample/application/commands/sample-create/` |
| Controller, `@Roles`, `@ResponseCode`, `@ApiSuccessResponse` | `src/modules/sample/presentation/http/controllers/sample.controller.ts` |
| Request DTO (class-validator) | `src/modules/sample/presentation/http/requests/create-sample.request.ts` |
| Response DTO `fromDomain` | `src/modules/sample/presentation/http/responses/sample.response.dto.ts` |
| Response code constant | `src/modules/sample/presentation/http/constants/sample-response-code.constant.ts` |
| Đăng ký CQRS handler trong module | `src/modules/sample/sample.module.ts` |
| Domain đã có (**dùng lại, không viết lại**) | `BuildingEntity.create()` trong `src/modules/building/domain/entities/building.entity.ts`, `BUILDING_DI_TOKEN.REPOSITORY` |
| Lấy user từ token | `CurrentUser` (`src/shared/presentation/decorators/auth/current-user.decorator.ts`) → `AuthenticatedUser` |

## Các bước triển khai

### Bước 1 — Chạy service local và sửa migration chạy được từ DB trống

- **Vấn đề:** `src/database/migrations/1792981146173-CreateBuildingsTable.ts` được `migration:generate` sinh ra có cả `CREATE TABLE "processed_events"`, `"samples"`, `"outbox_messages"` + 3 index outbox. Các bảng này đã được tạo bởi `1760500000000-CreateOutboxAndInboxTables.ts`/`1760600000000-AddOutboxSequence.ts` ⇒ trên DB mới `migration:run` lỗi `relation already exists`.
- **File sửa:** `src/database/migrations/1792981146173-CreateBuildingsTable.ts`.
- **Cách làm:**
  - Tạo DB trống `tenancy_db` local (Docker Postgres), copy `.env.example` → `.env`.
  - Chạy `npm ci && npm run migration:run` để thấy lỗi.
  - Trong `up()` chỉ giữ: `CREATE TYPE buildings_status_enum`, `CREATE TABLE "buildings"`, 2 index `IDX_buildings_*`. Trong `down()` chỉ giữ phần drop tương ứng.
  - Kiểm tra `processed_events` có trong migration inbox chưa (`grep -rn processed_events src/database/migrations`); nếu chưa có thì để nó trong một migration riêng `CreateProcessedEventsTable`, không gộp vào buildings.
  - Nếu DB staging đã chạy migration cũ: báo BE Lead trước khi merge (không sửa lịch sử migration đã chạy trên staging mà không thống nhất).
- **Kiểm tra bước:** `npm run schema:drop && npm run migration:run` chạy hết không lỗi; `npm run start:dev` lên, `GET http://localhost:3002/api/v1/tenancy/health` trả `200`; Swagger mở tại `/api/v1/tenancy/swagger`.

### Bước 2 — Đồng bộ domain với contract (field thiếu)

- **Vấn đề:** contract có `totalFloors`, `description`, `amenities`, nhưng `CreateBuildingProps`/bảng `buildings` chưa có. `district` là lỗi contract đã chốt bỏ (xem mục Quyết định).
- **File sửa/tạo:**
  - `src/modules/building/domain/entities/building.props.ts` (sửa): thêm `totalFloors: number | null`, `description: string | null`, `amenities: Record<string, boolean> | null` vào `CreateBuildingProps` (optional khi create) và `BuildingProps`.
  - `src/modules/building/domain/entities/building.entity.ts` (sửa): getter + gán trong `create`/`reconstitute`/`update`; validate `totalFloors >= 1`, `description` ≤ 1000 ký tự (dùng `assertText` sẵn có).
  - `src/modules/building/infrastructure/persistence/building.typeorm-entity.ts` + `mappers/building.mapper.ts` (sửa): thêm 3 cột `total_floors int null`, `description text null`, `amenities jsonb null`.
  - Migration mới: `npm run migration:generate -- src/database/migrations/AddBuildingDetails` → **mở file kiểm tra chỉ có `ALTER TABLE "buildings" ADD ...`**, xóa mọi dòng thừa.
- **Kiểm tra bước:** `npm run migration:run` pass; `npm run build` pass.

### Bước 3 — Command và handler

- **File tạo:**
  - `src/modules/building/application/commands/building-create/building-create.command.ts`: `BuildingCreateCommand(landlordId: Uuid, name, province, ward, address, totalFloors?, description?, amenities?)`.
  - `.../building-create/building-create.command.handler.ts`: copy nguyên khung `SampleCreateCommandHandler`.
- **Cách làm:**
  - Inject `BUILDING_DI_TOKEN.REPOSITORY`, `UNIT_OF_WORK_DI_TOKEN`, `OUTBOX_DI_TOKEN.REPOSITORY`.
  - Trong `unitOfWork.run(ctx => …)`: `BuildingEntity.create({... , latitude: DEFAULT_BUILDING_COORDINATE.latitude, longitude: DEFAULT_BUILDING_COORDINATE.longitude })` → `buildingRepository.save(building, ctx)` → `outboxRepository.append(building.pullDomainEvents().map(OutboxMessage.fromDomainEvent), ctx)` → `return building`.
  - Tạo `src/modules/building/domain/constants/building-default-coordinate.constant.ts` = `{ latitude: 0, longitude: 0 }` kèm `// TODO(geocoding): replace with real geocode`.
- **Kiểm tra bước:** `npm run build` pass.

### Bước 4 — Request/Response DTO và response code

- **File tạo:**
  - `src/modules/building/presentation/http/requests/create-building.request.ts`: field + rule y hệt `building-create-request-dto.yaml` (sau khi bỏ `district`): `@IsString() @Length(1,254) name`, `@Length(1,100) province/ward`, `@Length(1,254) address`, `@IsOptional() @IsInt() @Min(1) totalFloors`, `@IsOptional() @MaxLength(1000) description`, `@IsOptional() @IsObject() amenities`, `@IsArray() @ArrayMinSize(1) @IsUUID('all',{each:true}) ownershipCertificateMediaIds`.
  - `.../responses/building.response.dto.ts`: field theo schema response `201` trong `buildings.yaml`, có `static fromDomain(entity)`.
  - `.../constants/building-response-code.constant.ts`: `BUILDING_CREATED = 'BUILDING_CREATED'`.
- **Kiểm tra bước:** body thừa field (ví dụ `landlordId`) phải bị `422 UNEXPECTED_FIELD` nhờ `AppValidationPipe` (đã bật whitelist).

### Bước 5 — Controller, đăng ký module

- **File tạo:** `src/modules/building/presentation/http/controllers/building.controller.ts`
  - `@ApiTags('Buildings') @ApiBearerAuth() @Controller('buildings')`.
  - `@Post() @Roles(UserRole.LANDLORD) @HttpCode(201) @ResponseCode(BUILDING_CREATED)`, `operationId: 'postBuildings'`.
  - `create(@Body() req, @CurrentUser() user: AuthenticatedUser, @Res({ passthrough: true }) res)` → `commandBus.execute(new BuildingCreateCommand(user.id, …))` → `res.setHeader('Location', \`/api/v1/buildings/${b.id}\`)` → `BuildingResponseDto.fromDomain(b)`.
- **File sửa:** `src/modules/building/building.module.ts`: thêm `CqrsModule`, `OutboxModule` vào `imports`, `BuildingController` vào `controllers`, `BuildingCreateCommandHandler` vào `providers` (theo `sample.module.ts`).
- **Kiểm tra bước:** Swagger hiện `POST /buildings`; gọi bằng token landlord trả `201`.

### Bước 6 — Kiểm tra outbox và rollback

- **Cách làm:**
  - Sau khi tạo: `SELECT event_type, status FROM outbox_messages ORDER BY sequence DESC LIMIT 1;` → `BuildingCreated`, chuyển `PUBLISHED` sau khi relay chạy (cần RabbitMQ local).
  - Tạm `throw new Error('test')` sau `outboxRepository.append` → gọi API → `500`, **không** có row mới ở `buildings` lẫn `outbox_messages`. Xóa dòng throw.
- **Kiểm tra bước:** hai kết quả trên đúng; ghi lại query + kết quả vào PR.

## Quyết định tạm thời / Ngoài phạm vi

- **Geocoding:** chưa làm; lat/long = constant mặc định (`0`) có `TODO`.
- **`ownershipCertificateMediaIds`:** nhận và validate format theo contract, **chưa lưu** liên kết media (media flow chưa có). Ghi `TODO(media)`.
- **`district`:** PM đã xác nhận là lỗi contract (VN bỏ cấp Quận/Huyện). Không thêm cột; xóa khỏi `api-doc` (mục dưới).
- `PATCH/DELETE`, admin approve, search: thuộc P5-08c/d/e.

## Cập nhật `api-doc` (bắt buộc trước khi đóng issue)

- [ ] Xóa `district` ở `src/requests/buildings/building-create-request-dto.yaml` (property + `required`), request example trong `src/paths/buildings/buildings.yaml`, và `src/schemas/common/address-hierarchy.yaml`.
- [ ] Sequence diagram trong `description` của `postBuildings`: Gateway → Tenancy → DB (transaction: buildings + outbox) → Relay → RabbitMQ. Tham khảo `src/paths/auth/register.yaml`.
- [ ] `x-apidog-status: designing` → `released`; sync Apidog; link PR `api-doc` vào issue.

## Manual verification (Apidog)

1. Token landlord, body hợp lệ → `201 BUILDING_CREATED`, `status = pending`, header `Location` đúng, lat/long = 0.
2. Thiếu `name` / `ownershipCertificateMediaIds = []` → `422 VALIDATION_FAILED`.
3. Gửi thêm `landlordId` trong body → `422 UNEXPECTED_FIELD`.
4. Token tenant → `403 FORBIDDEN`; không token → `401`.
5. Bước 6 (outbox + rollback) đã chạy và ghi kết quả vào PR.

## Definition of Done

- [ ] Bước 1–6 đã qua phần Kiểm tra bước; `migration:run` chạy được từ DB trống.
- [ ] `npm run build` + `npm run lint` pass.
- [ ] PR vào `main` ghi `Closes pbl6-home-renter/docs#52` + link file `api-doc` đã dùng.
- [ ] baoduong17 approve; PR `api-doc` merge cùng lúc.
