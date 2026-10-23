# P5-09c — Landlord quản lý Room

**Epic:** [P5-09](P5-09-tenancy-room-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** BE member  
**Người review:** BE Lead, API owner  
**Ước lượng:** 5 points · 10–14 giờ  
**Phụ thuộc:** P5-09b

## Mục tiêu

Cho landlord liệt kê, sửa, xóa Room của mình và đánh dấu phòng sẵn sàng cho thuê.

## Contract

| Endpoint | File |
|---|---|
| `GET /me/rooms` | `api-docs/src/paths/rooms/me-rooms.yaml` |
| `PATCH /rooms/{roomId}` | `api-docs/src/paths/rooms/rooms-roomId.yaml` |
| `DELETE /rooms/{roomId}` | `api-docs/src/paths/rooms/rooms-roomId.yaml` |
| `POST /rooms/{roomId}/mark-ready` | `api-docs/src/paths/rooms/rooms-roomId-mark-ready.yaml` |

## Việc cần làm

### Query

- [ ] `GET /me/rooms` với filter/sort/pagination theo contract (offset pagination); chỉ trả Room có `landlord_id` = user hiện tại.

### Command

- [ ] `PATCH`: gọi `room.update(...)`; Room của landlord khác → `403`, không tồn tại → `404`. Append `RoomUpdated` vào outbox.
- [ ] `DELETE`: soft-delete qua aggregate, append `RoomDeleted` vào outbox.
- [ ] `mark-ready`: chuyển trạng thái qua aggregate; chuyển không hợp lệ → `409 INVALID_ROOM_TRANSITION`. Append `RoomStatusChanged` vào outbox.
- [ ] Mọi command đi qua UoW như pattern P5-08b.

## Quyết định tạm thời và blocker

- **`ROOM_HAS_ACTIVE_CONTRACT`:** domain Contract chưa tồn tại → **bỏ qua check này** khi xóa. Ghi `TODO` tại handler delete.
- **Lifecycle của `mark-ready`:** `api-docs/note.md` ghi nhận conflict — API dùng trạng thái `cleaning`, còn database chỉ có `available|occupied|maintenance`. Không tự thêm `cleaning`. Trước khi làm `mark-ready`, hỏi API owner/PM chốt transition (tạm hiểu là `maintenance → available`); nếu chưa chốt thì làm 3 endpoint còn lại trước và ghi blocker.

## Cập nhật `api-docs` (bắt buộc trước khi đóng issue)

- [ ] Viết/cập nhật **sequence diagram** cho từng endpoint (`GET /me/rooms`, `PATCH`, `DELETE`, `mark-ready`) khớp implementation. Tham khảo `src/paths/auth/register.yaml`.
- [ ] Cập nhật enum/transition của `mark-ready` theo kết quả chốt lifecycle.
- [ ] Đổi tag `x-apidog-status: designing` → `released` cho endpoint đã chạy và verify xong.
- [ ] Sync lên Apidog và link PR `api-docs` vào issue.

## Manual verification

1. List chỉ trả Room của landlord đang đăng nhập; pagination đúng.
2. Sửa/xóa Room của landlord khác → `403`; Room không tồn tại → `404`.
3. Xóa → Room không còn trong list; outbox có `RoomDeleted`.
4. `mark-ready` đúng transition → thành công; sai transition → `409 INVALID_ROOM_TRANSITION`.
