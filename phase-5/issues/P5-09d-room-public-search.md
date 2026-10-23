# P5-09d — Tìm kiếm và xem chi tiết Room

**Epic:** [P5-09](P5-09-tenancy-room-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** BE member  
**Người review:** BE Lead, API owner  
**Ước lượng:** 3 points · 6–8 giờ  
**Phụ thuộc:** P5-09b, P5-08e

## Mục tiêu

Cho tenant/khách tìm phòng trên sàn công khai và cho các role xem chi tiết Room theo quyền.

## Contract

| Endpoint | File |
|---|---|
| `GET /rooms` | `api-docs/src/paths/rooms/rooms.yaml` (`get`) |
| `GET /rooms/{roomId}` | `api-docs/src/paths/rooms/rooms-roomId.yaml` (`get`) |

## Việc cần làm

- [ ] `GET /rooms` (public): chỉ trả Room `available`, chưa xóa, thuộc Building `approved`. Response không trả `status` (theo `note.md`).
- [ ] Filter, pagination và response schema theo đúng contract; không tự thêm field.
- [ ] `GET /rooms/{roomId}`: public/landlord/tenant/admin theo contract; Room không đọc được theo quyền → `403`/`404` đúng contract.
- [ ] Field phụ thuộc Media/Contract chưa có dữ liệu → ghi blocker cho API owner thay vì tự định nghĩa.

## Cập nhật `api-docs` (bắt buộc trước khi đóng issue)

- [ ] **Xóa field `district`** (lỗi contract, đã chốt bỏ): `src/responses/dtos/rooms/public-room-list-response-dto.yaml` và example trong `src/paths/rooms/rooms.yaml`.
- [ ] Viết/cập nhật **sequence diagram** cho `GET /rooms` và `GET /rooms/{roomId}` khớp implementation. Tham khảo `src/paths/auth/register.yaml`.
- [ ] Đổi tag `x-apidog-status: designing` → `released` cho endpoint đã chạy và verify xong.
- [ ] Sync lên Apidog và link PR `api-docs` vào issue.

## Manual verification

1. Room thuộc Building chưa `approved` hoặc Room không `available` không xuất hiện trong kết quả tìm kiếm.
2. Filter/pagination trả đúng kết quả theo contract; response không có `district`.
3. Xem chi tiết Room với từng role cho kết quả đúng quyền.
