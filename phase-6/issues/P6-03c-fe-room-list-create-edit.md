# P6-03c — Danh sách, tạo, sửa, xóa Room trong một Building

**Epic:** [P6-03](P6-03-fe-landlord-building-room-screens.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** ThaiBao11125  
**Người review:** baoduong17  
**Ước lượng:** 5 points · 10–14 giờ  
**Phụ thuộc:** P6-03a; BE P5-09b (`POST /rooms`), P5-09c (`GET /me/rooms`, `PATCH`/`DELETE /rooms/{id}`, `mark-ready`)  
**Repo / branch:** `fe` · `feature/p6-03c-room-management`  
**Issue:** `docs#TBD`

## Mục tiêu

Trong trang chi tiết Tòa nhà **đã duyệt**, landlord thấy danh sách phòng (LL-07), thêm phòng (LL-08), xem/sửa/xóa một phòng (LL-09) và đánh dấu phòng sẵn sàng cho thuê. Tòa nhà chưa duyệt thì nút "Thêm phòng" bị khóa kèm giải thích.

## Contract

- `api-doc/src/paths/rooms/me-rooms.yaml` → `getMeRooms`: `filter[buildingId]`, `filter[status]`, phân trang; `200 ROOMS_MY_FETCHED`, item `RoomMyListResponseDto`.
- `api-doc/src/paths/rooms/rooms.yaml` → `postRooms`: body `RoomCreateRequestDto` (`api-doc/src/requests/rooms/room-create-request-dto.yaml`); `201 ROOM_CREATED`; `409 DUPLICATE_ROOM`; `422 BUILDING_NOT_APPROVED | VALIDATION_FAILED`.
- `api-doc/src/paths/rooms/rooms-roomId.yaml`:
  - `getRoomsRoomid`: `200 ROOM_FETCHED`, `RoomDetailResponseDto`.
  - `patchRoomsRoomid`: `RoomUpdateRequestDto`, `200 ROOM_UPDATED`.
  - `deleteRoomsRoomid`: `204`.
- `api-doc/src/paths/rooms/rooms-roomId-mark-ready.yaml` → `postRoomsRoomidMarkReady`: `200 ROOM_MARKED_READY`, `409 INVALID_ROOM_TRANSITION`.
- Tiện nghi phòng: allowlist trong `docs` (`docs/room-amenities`, commit 25/10 "define supported room amenities") và schema amenities trong `room-create-request-dto.yaml`.

## Tham chiếu code

| Cần | Copy pattern từ |
|---|---|
| Feature/API/hook/query key | `src/features/buildings/*` (P6-03a) |
| Form | `src/features/buildings/hooks/use-building-form.ts` (P6-03b) hoặc `src/features/auth/hooks/register/use-register-form.ts` |
| Select giới tính/trạng thái | `src/components/ui/select-dropdown.tsx` |
| Số tiền, diện tích | `src/components/ui/number-input.tsx` |

## Các bước triển khai

### Bước 1 — Đọc contract Room và dữ liệu mẫu

- **Cách làm:**
  - Tạo branch `feature/p6-03c-room-management`.
  - Trên staging: tạo Building và nhờ admin duyệt (hoặc dùng seed), tạo 1 phòng bằng Apidog.
  - Ghi danh sách field `RoomCreateRequestDto`, enum `genderPolicy`, `status`, key amenities vào comment issue.
- **Kiểm tra bước:** Apidog `POST /rooms` trả `201 ROOM_CREATED`.

### Bước 2 — Feature `rooms`: types, API, hooks

- **File tạo:**
  - `src/features/rooms/types/room.dto.ts`, `src/features/rooms/enums/{room-status,gender-policy}.enum.ts`.
  - `src/features/rooms/api/room.api.ts`: `getMyRooms(params)`, `getRoom(id)`, `createRoom(body)`, `updateRoom(id, body)`, `deleteRoom(id)`, `markRoomReady(id)`.
  - `src/features/rooms/hooks/`: `use-my-rooms-query.ts`, `use-room-query.ts`, `use-create-room-mutation.ts`, `use-update-room-mutation.ts`, `use-delete-room-mutation.ts`, `use-mark-room-ready-mutation.ts`.
- **File sửa:** `src/lib/react-query.ts`: `queryKeys.rooms = { all, myList(params), detail(id) }`.
- **Kiểm tra bước:** `npm run build` pass.

### Bước 3 — Danh sách phòng trong Building (LL-07)

- **File tạo:** `src/features/rooms/components/building-room-list.tsx` (nhúng vào `building-detail-page.tsx` của P6-03a).
- **Cách làm:**
  - Gọi `getMyRooms({ filter: { buildingId } })`.
  - Hiển thị dạng lưới card: Tên phòng, Tầng, Diện tích, Giá, Trạng thái (màu theo status).
  - Building chưa `approved` → hiện `alert-banner` "Cần chờ Admin duyệt dãy trọ trước khi thêm phòng", ẩn nút thêm.
- **Kiểm tra bước:** Building approved có 0 phòng → empty state + nút "Thêm phòng".

### Bước 4 — Form thêm/sửa phòng (LL-08)

- **File tạo:**
  - `src/features/rooms/validations/room.validation.ts` (zod theo min/max trong contract).
  - `src/features/rooms/components/room-form.tsx` (dùng chung cho tạo và sửa).
  - `src/features/rooms/pages/room-create-page.tsx`, `room-edit-page.tsx`.
- **Cách làm:**
  - Field: Tên/số phòng, Tầng, Diện tích, Giá thuê, Số người tối đa, Giới tính, Tiện nghi (checkbox theo allowlist), Mô tả.
  - `buildingId` lấy từ URL, không cho chọn.
  - `409 DUPLICATE_ROOM` → lỗi gắn vào field Tên; `422 BUILDING_NOT_APPROVED` → toast và quay về chi tiết Building.
  - Sửa: chỉ gửi `dirtyFields`.
- **Kiểm tra bước:** tạo 2 phòng trùng tên → lần 2 báo lỗi ở field Tên.

### Bước 5 — Chi tiết phòng, mark-ready, xóa (LL-09)

- **File tạo:** `src/features/rooms/pages/room-detail-page.tsx`, `src/features/rooms/components/delete-room-dialog.tsx`.
- **Cách làm:**
  - Card tổng quan + badge trạng thái; nút "Sẵn sàng cho thuê" chỉ hiện khi status cho phép (theo mô tả transition trong `rooms-roomId-mark-ready.yaml`); `409 INVALID_ROOM_TRANSITION` → toast.
  - Nút Sửa → `/buildings/:id/rooms/:roomId/edit`; nút Xóa → dialog → `204` → quay về Building.
  - Chưa có Menu tiện ích (LL-10) vì cần Contract; để placeholder "Chưa có hợp đồng — Thêm hợp đồng (sắp có)".
- **Kiểm tra bước:** mark-ready phòng mới → badge đổi; gọi lại lần 2 → toast lỗi đúng code.

### Bước 6 — Route, i18n

- **File sửa:**
  - `src/app/routes/roles/landlord.routes.tsx`: `/buildings/:id/rooms/new`, `/buildings/:id/rooms/:roomId`, `/buildings/:id/rooms/:roomId/edit`.
  - `src/i18n/locales/{vi,en}/rooms.json` (namespace mới, đăng ký trong `i18n.ts` + `i18next.d.ts`), `common.json` cho `ROOM_*`, `DUPLICATE_ROOM`, `BUILDING_NOT_APPROVED`, `INVALID_ROOM_TRANSITION`.
- **Kiểm tra bước:** `npm run build`, `npm run lint`, `npm run i18n:check` pass.

## Quyết định tạm thời / Ngoài phạm vi

- Không làm Room Map dạng sơ đồ màu (LL-01/LL-07 bản trực quan): dùng lưới card.
- Không upload ảnh phòng (cover/gallery) trong task này; làm sau khi P6-04 ổn định.
- Không làm tìm kiếm public `GET /rooms` (thuộc tenant/mobile).

## Manual verification

1. Building `pending` → không thêm được phòng, có thông báo.
2. Building `approved` → tạo phòng → xuất hiện trong lưới.
3. Tên trùng → `409 DUPLICATE_ROOM` ở field.
4. Sửa giá phòng → chi tiết cập nhật.
5. Mark-ready → trạng thái đổi; xóa phòng → biến mất.

## Definition of Done

- [ ] Bước 1–6 qua phần Kiểm tra bước.
- [ ] `npm run build` + `npm run lint` + `npm run i18n:check` pass.
- [ ] PR có ảnh LL-07/08/09 và `Closes pbl6-home-renter/docs#TBD`.
