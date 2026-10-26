# P5-09b — Create Room trong Building đã duyệt

**Epic:** [P5-09](P5-09-tenancy-room-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** huynhtiennhat0403  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 5 points · 10–14 giờ  
**Phụ thuộc:** P5-09a, P5-08b (pattern + **sửa migration buildings**), P5-08d (Building `approved`)  
**Repo / branch:** `Tenancy-Service` · `feature/p5-09b-room-create`

## Mục tiêu

Landlord gọi `POST /api/v1/rooms` tạo được Room trong Building **đã duyệt và thuộc chính mình**, nhận `201 ROOM_CREATED` với `status = available`; cùng transaction ghi outbox để relay publish `RoomCreated`. Làm theo đúng pattern slice mẫu P5-08b.

## Contract

- Endpoint: `api-doc/src/paths/rooms/rooms.yaml` (`post` → `postRooms`).
- Request: `api-doc/src/requests/rooms/room-create-request-dto.yaml`.
- Response: `api-doc/src/responses/dtos/rooms/room-create-response-dto.yaml` (required: `id`, `buildingId`, `name`, `status`, `rentPrice`).
- Role: `landlord`. Response `201`, code `ROOM_CREATED`, header `Location: /api/v1/rooms/{id}`.
- Rule: `landlord_id` lấy từ JWT (`@CurrentUser()`), **không** nhận từ body.
- Lỗi: `404 RESOURCE_NOT_FOUND` (Building không tồn tại/đã xóa), `403 FORBIDDEN` (Building của landlord khác), `422 BUILDING_NOT_APPROVED`, `409 DUPLICATE_ROOM` (trùng tên trong cùng Building), `422 VALIDATION_FAILED`, `401`.

## Tham chiếu code (đã có trong repo)

| Cần | Copy pattern từ |
|---|---|
| Command + handler (UoW + outbox) | `src/modules/building/application/commands/building-create/` (sau P5-08b) hoặc `src/modules/sample/application/commands/sample-create/` |
| Controller, `@Roles`, `@ResponseCode`, `@ApiSuccessResponse`, header `Location` | `building.controller.ts` (P5-08b), `src/modules/sample/presentation/http/controllers/sample.controller.ts` |
| Request/Response DTO | `src/modules/sample/presentation/http/requests/create-sample.request.ts`, `.../responses/sample.response.dto.ts` |
| Domain Room (**dùng lại**) | `Room.create()` trong `src/modules/room/domain/entities/room.entity.ts`, `ROOM_DI_TOKEN.REPOSITORY`, `RoomRepository.existsByBuildingAndName()` |
| Domain Building (đọc chéo module) | `BUILDING_DI_TOKEN.REPOSITORY` → `BuildingRepository.findById()`, `BuildingStatus.APPROVED` (`src/modules/building/domain/enums/building-status.enum.ts`) |
| Exception pattern | `src/modules/building/domain/exceptions/building-not-found.exception.ts` (`DomainException(message, status, code)`) |
| Lấy user từ token | `CurrentUser` (`src/shared/presentation/decorators/auth/current-user.decorator.ts`) → `AuthenticatedUser` |

## Các bước triển khai

### Bước 1 — Tạo migration bảng `rooms` và chạy được từ DB trống

- **Vấn đề:** P5-09a đã có `RoomTypeormEntity` (`@Entity('rooms')`) nhưng `src/database/migrations/` **chưa có migration tạo bảng `rooms`**. Service sẽ lỗi `relation "rooms" does not exist` khi gọi repository.
- **Phụ thuộc:** P5-08b Bước 1 (gỡ phần tạo trùng `outbox_messages`/`processed_events`/`samples` khỏi `1792981146173-CreateBuildingsTable.ts`) phải merge trước, nếu không `migration:run` trên DB trống vẫn lỗi.
- **File tạo:** `src/database/migrations/<timestamp>-CreateRoomsTable.ts`.
- **Cách làm:**
  - `npm run migration:generate -- src/database/migrations/CreateRoomsTable` trên DB đã chạy hết migration hiện có.
  - **Mở file kiểm tra**: chỉ được có `CREATE TYPE room_gender_policy_enum`, `CREATE TYPE room_status_enum`, `CREATE TABLE "rooms"` và index; xóa mọi dòng thừa (bảng khác, `ALTER` không liên quan).
  - Thêm tay: `CONSTRAINT "FK_rooms_building" FOREIGN KEY ("building_id") REFERENCES "buildings"("id")` (cùng DB tenancy nên được phép); **không** FK tới `landlord_id` (user nằm ở identity DB).
  - Thêm index: `IDX_rooms_building` (`building_id`) `WHERE is_deleted = false`, `IDX_rooms_landlord` (`landlord_id`) `WHERE is_deleted = false`, `IDX_rooms_status` (`status`) `WHERE is_deleted = false`.
  - Unique tên phòng trong Building: `CREATE UNIQUE INDEX "UQ_rooms_building_name" ON "rooms" ("building_id", lower("name")) WHERE is_deleted = false` (chặn race condition, bổ sung cho check ở handler).
  - CHECK: `rent_price >= 0`, `area IS NULL OR area > 0`, `max_occupancy IS NULL OR max_occupancy >= 1`, `floor_number IS NULL OR floor_number >= 1`.
  - `down()` drop theo thứ tự ngược.
- **Kiểm tra bước:** `npm run schema:drop && npm run migration:run` chạy hết không lỗi; `\d rooms` trong psql thấy FK + index; `npm run migration:revert` rồi `migration:run` lại vẫn pass.

### Bước 2 — Đồng bộ domain Room với contract (field thiếu/khác kiểu)

- **Vấn đề (contract vs domain):**
  - Contract có `roomType` (string 1–100) và `depositAmount` (integer ≥ 0, **required**) — domain/bảng **chưa có**.
  - Contract có `photoMediaIds` — media flow chưa có (xem Quyết định tạm thời).
  - Contract `floorNumber` **required, ≥ 1**; domain cho `null`. Contract `area` là **string thập phân, required**; domain là `number | null`.
  - `amenities`: allowlist contract (`aircon, fridge, wcInside, waterHeater, mezzanine, table, chair`) **khớp** `ROOM_AMENITY_KEYS` trong `room-amenities.vo.ts` — không cần sửa, chỉ dùng lại để validate.
- **File sửa:**
  - `src/modules/room/domain/entities/room.props.ts`: thêm `roomType: string | null`, `depositAmount: number` vào `RoomFields`; `CreateRoomProps` nhận `roomType?`, `depositAmount` bắt buộc.
  - `src/modules/room/domain/entities/room.entity.ts`: getter, gán trong `create`/`reconstitute`/`currentFields`; `assertValidFields` kiểm `depositAmount` là số nguyên ≥ 0, `roomType` ≤ 100 ký tự.
  - `src/modules/room/infrastructure/persistence/room.typeorm-entity.ts` + `mappers/room.mapper.ts`: cột `room_type varchar(100) null`, `deposit_amount numeric not null default 0` (transformer giống `rentPrice`).
  - Migration: nếu Bước 1 chưa merge thì gộp cột vào `CreateRoomsTable`; nếu đã merge thì `migration:generate -- .../AddRoomTypeAndDeposit`, kiểm tra file chỉ có `ALTER TABLE "rooms" ADD ...`.
  - Giữ `area`/`rentPrice` là `number` trong domain; **convert string → number ở presentation** (`Number(req.area)`), response trả lại `area` dạng string (`toFixed(1)` hoặc `String(...)`) đúng contract.
- **Kiểm tra bước:** `npm run migration:run` + `npm run build` pass.

### Bước 3 — Exception cho rule quan hệ Building

- **File tạo** (`src/modules/room/domain/exceptions/`):
  - `building-not-approved.exception.ts` → `DomainException(msg, 422, 'BUILDING_NOT_APPROVED')`.
  - `duplicate-room.exception.ts` → `DomainException(msg, 409, 'DUPLICATE_ROOM')`.
  - `room-forbidden.exception.ts` → `DomainException(msg, 403, 'FORBIDDEN')`.
- **Cách làm:** Building không tồn tại dùng lại `BuildingNotFoundException` (`404 RESOURCE_NOT_FOUND`) từ module building — không tạo bản sao.
- **Kiểm tra bước:** `npm run build` pass.

### Bước 4 — Command và handler

- **File tạo:**
  - `src/modules/room/application/commands/room-create/room-create.command.ts`: `RoomCreateCommand(landlordId: Uuid, buildingId: Uuid, name, roomType?, floorNumber, area: number, rentPrice, depositAmount, maxOccupancy?, genderPolicy, amenities?)`.
  - `.../room-create/room-create.command.handler.ts`: copy khung `BuildingCreateCommandHandler`.
- **Cách làm:**
  - Inject `ROOM_DI_TOKEN.REPOSITORY`, `BUILDING_DI_TOKEN.REPOSITORY`, `UNIT_OF_WORK_DI_TOKEN`, `OUTBOX_DI_TOKEN.REPOSITORY`.
  - Trong `unitOfWork.run(ctx => …)`, **đúng thứ tự** để phân biệt not-found và vi phạm rule:
    1. `buildingRepository.findById(buildingId, ctx)` → `null` hoặc đã xóa ⇒ `BuildingNotFoundException`.
    2. `building.landlordId !== landlordId` ⇒ `RoomForbiddenException`.
    3. `building.status !== BuildingStatus.APPROVED` ⇒ `BuildingNotApprovedException`.
    4. `roomRepository.existsByBuildingAndName(buildingId, name)` ⇒ `DuplicateRoomException`.
    5. `Room.create({...})` → `roomRepository.save(room, ctx)` → `outboxRepository.append(room.pullDomainEvents().map(OutboxMessage.fromDomainEvent), ctx)` → `return room`.
  - Bắt lỗi unique `UQ_rooms_building_name` từ Postgres (dùng `postgres-error-code.ts`, mã `23505`) và map sang `DuplicateRoomException` cho trường hợp race.
- **Kiểm tra bước:** `npm run build` pass.

### Bước 5 — Request/Response DTO và response code

- **File tạo** (`src/modules/room/presentation/http/`):
  - `requests/create-room.request.ts`: `@IsUUID() buildingId`, `@Length(1,254) name`, `@IsOptional() @Length(1,100) roomType`, `@IsInt() @Min(1) floorNumber`, `@IsNumberString() area`, `@IsInt() @Min(0) rentPrice`, `@IsInt() @Min(0) depositAmount`, `@IsOptional() @IsInt() @Min(1) maxOccupancy`, `@IsEnum(GenderPolicy) genderPolicy`, `@IsOptional() @IsObject() amenities` (validate key thuộc `ROOM_AMENITY_KEYS` và value boolean — viết custom validator hoặc check ở handler bằng `isRoomAmenityKey`), `@IsOptional() @IsArray() @IsUUID('all',{each:true}) photoMediaIds`.
  - `responses/room-create.response.dto.ts`: field theo `room-create-response-dto.yaml`, `static fromDomain(room)`.
  - `constants/room-response-code.constant.ts`: `ROOM_CREATED = 'ROOM_CREATED'`.
- **Kiểm tra bước:** body có amenity lạ (`"pool": true`) hoặc thừa `landlordId` ⇒ `422`.

### Bước 6 — Controller, đăng ký module

- **File tạo:** `src/modules/room/presentation/http/controllers/room.controller.ts`
  - `@ApiTags('Rooms') @ApiBearerAuth() @Controller('rooms')`.
  - `@Post() @Roles(UserRole.LANDLORD) @HttpCode(201) @ResponseCode(ROOM_CREATED)`, `operationId: 'postRooms'`.
  - `create(@Body() req, @CurrentUser() user: AuthenticatedUser, @Res({ passthrough: true }) res)` → `commandBus.execute(new RoomCreateCommand(user.id, …))` → set header `Location` → `RoomCreateResponseDto.fromDomain(room)`.
- **File sửa:** `src/modules/room/room.module.ts`: thêm `CqrsModule`, `OutboxModule`, **`BuildingModule`** (đã export `BUILDING_DI_TOKEN.REPOSITORY`) vào `imports`; `RoomController` vào `controllers`; `RoomCreateCommandHandler` vào `providers`.
- **Kiểm tra bước:** Swagger `/api/v1/tenancy/swagger` hiện `POST /rooms`; gọi bằng token landlord với Building approved trả `201`.

### Bước 7 — Kiểm tra outbox và rollback

- **Cách làm:**
  - Sau khi tạo: `SELECT event_type, status FROM outbox_messages ORDER BY sequence DESC LIMIT 1;` → `RoomCreated`, sang `PUBLISHED` sau khi relay chạy (RabbitMQ local).
  - Tạm `throw new Error('test')` sau `outboxRepository.append` → `500`, **không** có row mới ở `rooms` lẫn `outbox_messages`. Xóa dòng throw.
- **Kiểm tra bước:** ghi query + kết quả vào PR.

## Quyết định tạm thời / Ngoài phạm vi

- **`photoMediaIds`:** nhận và validate format UUID theo contract, **chưa lưu** liên kết media. Ghi `TODO(media)`.
- **`area`:** domain giữ `number`; chỉ convert ở presentation. Ghi nhận khác biệt string/number trong `api-doc/note.md` đã có — không đổi contract.
- **Building approved check:** đọc trực tiếp `BuildingRepository` (cùng service, cùng DB) — không gọi HTTP, không dùng event.
- `GET/PATCH/DELETE`, `mark-ready`, public search: thuộc P5-09c/d.

## Cập nhật `api-doc` (bắt buộc trước khi đóng issue)

- [ ] Sequence diagram trong `description` của `postRooms`: Gateway → Tenancy → load Building (404/403/422) → check trùng tên (409) → DB transaction (rooms + outbox) → Relay → RabbitMQ. Tham khảo `src/paths/auth/register.yaml`.
- [ ] Bổ sung `404` vào responses của `postRooms` nếu contract chưa có (hiện có `400/401/403/409/422/429/500/503`) — cần API owner duyệt.
- [ ] `x-apidog-status: designing` → `released`; sync Apidog; link PR `api-doc` vào issue.

## Manual verification (Apidog)

1. Building `approved` của mình, body hợp lệ → `201 ROOM_CREATED`, `status = available`, header `Location` đúng.
2. `buildingId` không tồn tại → `404`; Building của landlord khác → `403 FORBIDDEN`.
3. Building `pending`/`rejected` → `422 BUILDING_NOT_APPROVED`.
4. Trùng tên trong cùng Building (khác hoa/thường) → `409 DUPLICATE_ROOM`; trùng tên ở Building khác → `201`.
5. Thiếu `depositAmount`/`floorNumber`, amenity ngoài allowlist, thừa `landlordId` → `422`.
6. Token tenant → `403`; không token → `401`.
7. Bước 7 (outbox + rollback) đã chạy và ghi kết quả vào PR.

## Definition of Done

- [ ] Bước 1–7 đã qua phần Kiểm tra bước; `migration:run` chạy được từ DB trống (có bảng `rooms`).
- [ ] `npm run build` + `npm run lint` pass.
- [ ] PR vào `main` ghi `Closes pbl6-home-renter/docs#57` + link file `api-doc` đã dùng.
- [ ] baoduong17 approve; PR `api-doc` merge cùng lúc.
