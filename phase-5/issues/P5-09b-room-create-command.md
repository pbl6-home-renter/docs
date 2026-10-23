# P5-09b — Create Room trong Building đã duyệt

**Epic:** [P5-09](P5-09-tenancy-room-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** BE member  
**Người review:** BE Lead, API owner  
**Ước lượng:** 5 points · 10–14 giờ  
**Phụ thuộc:** P5-09a, P5-08b (pattern), P5-08d (Building `approved`)

## Mục tiêu

Triển khai `POST /rooms` end-to-end theo pattern UoW + Outbox của P5-08b, kèm validation quan hệ Room–Building.

## Contract

- `api-docs/src/paths/rooms/rooms.yaml` (`post`).
- Role: landlord. `landlord_id` lấy từ JWT, không nhận từ body.

## Việc cần làm

- [ ] Controller + DTO validation theo request schema; map DTO sang command.
- [ ] Handler: mở UoW → load Building qua repository → kiểm tra rule → `Room.create(...)` → save → append outbox → commit.
- [ ] Rule quan hệ Building:
  - Building không tồn tại hoặc đã xóa → `404`.
  - Building không thuộc landlord hiện tại → `403 FORBIDDEN`.
  - Building chưa `approved` → `422 BUILDING_NOT_APPROVED`.
- [ ] Tên phòng trùng trong cùng Building → `409 DUPLICATE_ROOM`.
- [ ] Map domain event `RoomCreated` sang integration event (`message_id`, `event_type`, `aggregate_id`, timestamp).
- [ ] Phân biệt lỗi không tìm thấy dữ liệu và lỗi vi phạm business rule.

## Cập nhật `api-docs` (bắt buộc trước khi đóng issue)

- [ ] Viết/cập nhật **sequence diagram** cho `POST /rooms` khớp implementation (load Building, transaction + outbox). Tham khảo `src/paths/auth/register.yaml`.
- [ ] Đổi tag `x-apidog-status: designing` → `released` cho endpoint đã chạy và verify xong.
- [ ] Sync lên Apidog và link PR `api-docs` vào issue.

## Manual verification

1. Tạo Room trong Building `approved` của mình → `201`, `status = available`.
2. Building không tồn tại → `404`; Building của landlord khác → `403`.
3. Building `pending`/`rejected` → `422 BUILDING_NOT_APPROVED`.
4. Trùng tên trong cùng Building → `409 DUPLICATE_ROOM`; trùng tên ở Building khác → thành công.
5. Buộc lỗi trước commit → không còn Room hoặc outbox row dở dang.
