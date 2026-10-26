# P5-09c — Landlord quản lý Room

**Epic:** [P5-09](P5-09-tenancy-room-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** huynhtiennhat0403  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 5 points · 10–14 giờ  
**Phụ thuộc:** P5-09b  
**Repo / branch:** `Tenancy-Service` · `feature/p5-09c-room-landlord-management`

## Mục tiêu

Landlord liệt kê Room của mình (offset pagination), sửa, xóa mềm và đánh dấu phòng sẵn sàng cho thuê. Mọi command đi qua UoW + outbox như P5-08b/P5-09b.

## Contract

| Endpoint | operationId | File | Success |
|---|---|---|---|
| `GET /me/rooms` | `getMeRooms` | `api-doc/src/paths/rooms/me-rooms.yaml` | `200 ROOMS_MY_FETCHED` + `pagination` |
| `PATCH /rooms/{roomId}` | `patchRoomsRoomid` | `api-doc/src/paths/rooms/rooms-roomId.yaml` | `200 ROOM_UPDATED` |
| `DELETE /rooms/{roomId}` | `deleteRoomsRoomid` | `api-doc/src/paths/rooms/rooms-roomId.yaml` | `204` |
| `POST /rooms/{roomId}/mark-ready` | `postRoomsRoomidMarkReady` | `api-doc/src/paths/rooms/rooms-roomId-mark-ready.yaml` | `200 ROOM_MARKED_READY` |

- DTO: `src/requests/rooms/room-update-request-dto.yaml` (`minProperties: 1`, chỉ `name`, `rentPrice`, `area`), `src/responses/dtos/rooms/my-room-list-response-dto.yaml` (required thêm `activeIssuesCount`), `room-update-response-dto.yaml`, `room-ready-mark-response-dto.yaml`.
- Filter `GET /me/rooms`: `filter[buildingId]` (uuid), `filter[status]`, `sort`, `order`, `pageSize` (1–100, mặc định 20), `pageNo`.
- Role: `landlord`. Lỗi: `404 RESOURCE_NOT_FOUND`, `403 FORBIDDEN`, `409 INVALID_ROOM_TRANSITION` (mark-ready), `409 ROOM_HAS_ACTIVE_CONTRACT` (delete — tạm bỏ qua), `422 VALIDATION_FAILED`.

## Tham chiếu code (đã có trong repo)

| Cần | Copy pattern từ |
|---|---|
| Command + UoW + outbox | `src/modules/room/application/commands/room-create/` (P5-09b) |
| Query handler | `src/modules/sample/application/queries/sample-get-by-id/` |
| Offset pagination | `src/shared/presentation/pagination/offset-pagination.request.dto.ts` (`OffsetPaginationQueryRequestDto`), `paginated.response.dto.ts`, `src/shared/application/pagination/offset-page-query.ts`, `paginated-result.ts`, `src/shared/infrastructure/database/pagination/offset.paginator.ts` (`TypeOrmOffsetPaginator`), `sort.helper.ts` |
| Domain (**dùng lại**) | `Room.update()`, `Room.delete()`, `Room.changeStatus()`, `RoomRepository.findByIdForUpdate()`, `existsByBuildingAndName(buildingId, name, exceptRoomId)` |
| Lock + đọc trong transaction | `findByIdForUpdate(id, ctx)` (đã có ở cả Room và Building repository) |

## Các bước triển khai

### Bước 1 — Pull P5-09b, chạy service, chuẩn bị dữ liệu

- **Cách làm:** pull `main` (đã có P5-09b), `npm run migration:run && npm run start:dev`; tạo 2 landlord, mỗi người 1 Building approved + 3 Room qua `POST /rooms`.
- **Kiểm tra bước:** `SELECT landlord_id, count(*) FROM rooms GROUP BY 1;` đúng dữ liệu vừa tạo.

### Bước 2 — Exception và helper kiểm tra quyền sở hữu

- **File tạo** (`src/modules/room/domain/exceptions/`):
  - `room-not-found.exception.ts` → `DomainException(msg, 404, 'RESOURCE_NOT_FOUND')`.
  - `invalid-room-transition.exception.ts` → `DomainException(msg, 409, 'INVALID_ROOM_TRANSITION')`.
  - Dùng lại `RoomForbiddenException` (P5-09b).
- **File tạo:** `src/modules/room/application/services/room-ownership.ts`: hàm `loadOwnedRoomForUpdate(repo, roomId, landlordId, ctx)` → `findByIdForUpdate` → `null`/`isDeleted` ⇒ `RoomNotFoundException`; `room.landlordId !== landlordId` ⇒ `RoomForbiddenException`. Ba command dưới dùng chung.
- **Kiểm tra bước:** `npm run build` pass.

### Bước 3 — Query `GET /me/rooms`

- **File sửa:** `src/modules/room/domain/repositories/room.repository.ts` thêm `findPageByLandlord(landlordId: Uuid, query: OffsetPageQuery<{ buildingId?: Uuid; status?: RoomStatus }>): Promise<PaginatedResult<Room>>`.
- **File sửa:** `src/modules/room/infrastructure/persistence/room.repository.ts`: implement bằng QueryBuilder `where landlord_id = :id AND is_deleted = false` + filter + `applySortingToQueryBuilder` (whitelist sort: `createdAt`, `name`, `rentPrice`) + `TypeOrmOffsetPaginator`.
- **File tạo:**
  - `application/queries/room-my-list/room-my-list.query.ts` + `.query.handler.ts`.
  - `presentation/http/requests/my-rooms-query.request.ts` (extends `OffsetPaginationQueryRequestDto`, `filter.buildingId` `@IsUUID()`, `filter.status` `@IsEnum(RoomStatus)`).
  - `presentation/http/responses/room-my-list.response.dto.ts` theo `my-room-list-response-dto.yaml`; `activeIssuesCount` tạm trả `0` (`TODO(community)`).
- **File sửa:** `room.controller.ts` thêm controller `me/rooms` (hoặc `@Get('/me/rooms')` trong controller riêng `MeRoomController` với `@Controller('me/rooms')`), `@Roles(UserRole.LANDLORD)`, `@ResponseCode('ROOMS_MY_FETCHED')`, trả `PaginatedResponseDto`.
- **Kiểm tra bước:** landlord A chỉ thấy 3 phòng của mình; `pageSize=2` ⇒ `totalPages=2`, `hasNextPage=true`; `filter[status]=xyz` ⇒ `422`.

### Bước 4 — Command `PATCH /rooms/{roomId}`

- **File tạo:** `application/commands/room-update/room-update.command.ts` + `.command.handler.ts`; `presentation/http/requests/update-room.request.ts` (chỉ `name`, `rentPrice`, `area` — tất cả optional, reject body rỗng ⇒ `422`); `responses/room-update.response.dto.ts`.
- **Cách làm (handler):** `unitOfWork.run` → `loadOwnedRoomForUpdate` → nếu đổi `name`: `existsByBuildingAndName(room.buildingId, name, room.id)` ⇒ `DuplicateRoomException` → `room.update({ name, rentPrice, area: Number(area) })` → save → append outbox (`RoomUpdated`).
- **Controller:** `@Patch(':roomId') @Roles(LANDLORD) @ResponseCode('ROOM_UPDATED')`, `@Param('roomId', ParseUUIDPipe)`.
- **Kiểm tra bước:** sửa phòng của mình ⇒ `200`; phòng của landlord B ⇒ `403`; uuid không tồn tại ⇒ `404`; body `{}` ⇒ `422`.

### Bước 5 — Command `DELETE /rooms/{roomId}`

- **File tạo:** `application/commands/room-delete/` (command + handler).
- **Cách làm:** `unitOfWork.run` → `loadOwnedRoomForUpdate` → `room.delete()` → save → append outbox (`RoomDeleted`). Bỏ qua check hợp đồng, để `// TODO(contract): throw ROOM_HAS_ACTIVE_CONTRACT when an active contract exists`.
- **Controller:** `@Delete(':roomId') @HttpCode(204) @Roles(LANDLORD)`.
- **Kiểm tra bước:** xóa ⇒ `204`; `GET /me/rooms` không còn phòng đó; outbox có `RoomDeleted`; xóa lại ⇒ `404`.

### Bước 6 — Chốt lifecycle `mark-ready` rồi triển khai

- **Vấn đề (contract vs domain):** `my-room-list-response-dto.yaml`/`room-detail-response-dto.yaml` có enum status `available, occupied, maintenance, cleaning, pending_cleanup`; domain `RoomStatus` và DB enum `room_status_enum` chỉ có `available | occupied | maintenance`. `api-doc/note.md` (mục Room) đã ghi conflict này.
- **Cách làm:**
  1. **Trước khi code**, comment trên issue hỏi baoduong17 chốt một trong hai: (a) giữ 3 trạng thái, `mark-ready` = `maintenance → available`, và xóa `cleaning`/`pending_cleanup` khỏi contract; (b) thêm `cleaning` vào domain + migration `ALTER TYPE room_status_enum ADD VALUE 'cleaning'`, `mark-ready` = `cleaning → available`. **Khuyến nghị (a)** vì Contract/checkout chưa tồn tại.
  2. Theo phương án đã chốt: thêm method `markReady()` vào `Room` (`src/modules/room/domain/entities/room.entity.ts`): chỉ cho phép từ trạng thái nguồn đã chốt, ngược lại ném `InvalidRoomTransitionException`; bên trong gọi `changeStatus(RoomStatus.AVAILABLE)` để tái dùng event `RoomStatusChanged`.
  3. Tạo `application/commands/room-mark-ready/` (command + handler: `loadOwnedRoomForUpdate` → `room.markReady()` → save → outbox) và `responses/room-mark-ready.response.dto.ts` (`id`, `status`).
  4. Controller: `@Post(':roomId/mark-ready') @HttpCode(200) @Roles(LANDLORD) @ResponseCode('ROOM_MARKED_READY')`.
- Nếu đến giữa sprint vẫn chưa chốt: merge Bước 3–5 trước, để Bước 6 thành blocker trên issue.
- **Kiểm tra bước:** phòng `maintenance` ⇒ `200`, `status = available`; phòng đang `available` ⇒ `409 INVALID_ROOM_TRANSITION`; outbox có `RoomStatusChanged`.

### Bước 7 — Hoàn thiện module và Swagger

- **File sửa:** `room.module.ts` đăng ký mọi handler mới (`commandHandlers`, `queryHandlers` như `sample.module.ts`).
- **Kiểm tra bước:** `npm run build` + `npm run lint` pass; Swagger hiện đủ 4 `operationId` đúng như bảng Contract.

## Quyết định tạm thời / Ngoài phạm vi

- **`ROOM_HAS_ACTIVE_CONTRACT`:** domain Contract chưa có ⇒ bỏ qua khi xóa, để `TODO(contract)`.
- **`activeIssuesCount`:** community-service chưa có ⇒ trả `0`, `TODO(community)`.
- **PATCH chỉ sửa `name`, `rentPrice`, `area`** đúng contract hiện tại; không tự mở rộng (`api-doc/note.md` đã ghi câu hỏi này cho API owner).
- **`mark-ready`:** chỉ làm sau khi lifecycle được chốt (Bước 6).

## Cập nhật `api-doc` (bắt buộc trước khi đóng issue)

- [ ] Sequence diagram cho `getMeRooms`, `patchRoomsRoomid`, `deleteRoomsRoomid`, `postRoomsRoomidMarkReady` khớp implementation (load + lock Room, ownership 404/403, transaction + outbox). Tham khảo `src/paths/auth/register.yaml`.
- [ ] Cập nhật enum status trong `my-room-list-response-dto.yaml`, `room-detail-response-dto.yaml` và mô tả transition của `mark-ready` theo phương án đã chốt.
- [ ] `x-apidog-status: designing` → `released` cho endpoint đã verify; sync Apidog; link PR `api-doc` vào issue.

## Manual verification (Apidog)

1. `GET /me/rooms` chỉ trả Room của landlord đang đăng nhập; filter `buildingId`/`status` và pagination đúng.
2. PATCH/DELETE/mark-ready Room của landlord khác → `403`; Room không tồn tại → `404`.
3. PATCH đổi tên trùng phòng khác trong cùng Building → `409 DUPLICATE_ROOM`; body rỗng → `422`.
4. DELETE → `204`, Room biến mất khỏi list, outbox có `RoomDeleted`.
5. mark-ready đúng transition → `200 ROOM_MARKED_READY`; sai → `409 INVALID_ROOM_TRANSITION`.
6. Token tenant → `403`; không token → `401`.

## Definition of Done

- [ ] Bước 1–7 đã qua phần Kiểm tra bước (Bước 6 có quyết định lifecycle được ghi trên issue).
- [ ] `npm run build` + `npm run lint` pass.
- [ ] PR vào `main` ghi `Closes pbl6-home-renter/docs#58` + link file `api-doc` đã dùng.
- [ ] baoduong17 approve; PR `api-doc` merge cùng lúc.
