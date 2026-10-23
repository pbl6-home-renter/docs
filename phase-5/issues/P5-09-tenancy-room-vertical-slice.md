# P5-09 — Room vertical slice (Epic)

> Chuyển từ `P4-25` (Phase 4) sang Phase 5 và tách thành sub-issue `P5-09a` → `P5-09d`. Phụ thuộc Building epic [P5-08](P5-08-tenancy-building-vertical-slice.md).

**Trạng thái:** 🟡 Open  
**Người phụ trách:** BE member  
**Người review:** BE Lead, API owner, PM  
**Ước lượng:** 16 points (tổng sub-issue)  
**Độ ưu tiên:** High  
**Phụ thuộc:** P5-08a, P5-08b (pattern), P5-08d (Building `approved`)

## Bối cảnh

Room phụ thuộc vào Building và cần thể hiện rõ validation quan hệ giữa aggregate và persistence record. Task này kế thừa pattern từ Building vertical slice (P5-08b) nhưng không được rút gọn thành CRUD thiếu domain rule.

Issue này là issue cha. Công việc thực tế được giao qua các sub-issue bên dưới; issue cha chỉ đóng khi toàn bộ sub-issue đã Done.

## Sub-issue

| ID | Task | Endpoint | Estimate | Phụ thuộc |
|---|---|---|---|---|
| [P5-09a](P5-09a-room-domain-persistence.md) | Domain model và persistence | — | 3 pts | P5-08a |
| [P5-09b](P5-09b-room-create-command.md) | Create Room trong Building đã duyệt | `POST /rooms` | 5 pts | P5-09a, P5-08b, P5-08d |
| [P5-09c](P5-09c-room-landlord-management.md) | Landlord quản lý Room | `GET /me/rooms`, `PATCH /rooms/{id}`, `DELETE /rooms/{id}`, `POST /rooms/{id}/mark-ready` | 5 pts | P5-09b |
| [P5-09d](P5-09d-room-public-search.md) | Tìm kiếm và xem chi tiết Room | `GET /rooms`, `GET /rooms/{id}` | 3 pts | P5-09b, P5-08e |

Thứ tự: `P5-09a → P5-09b → (P5-09c ∥ P5-09d)`.

## Ngoài phạm vi epic này

- Favorite rooms (`GET/POST /me/favorite-rooms`, `DELETE /me/favorite-rooms/{id}`) — module `favorite-room` riêng theo P4-21, tạo issue sau.
- Room hub (`GET /me/room-hub`) — cần domain Contract (`ACTIVE_CONTRACT_NOT_FOUND`).
- Rate policy và billing setting cấp room.
- Media ảnh phòng (`cover_photo`, `gallery_photo`).
- Check `ROOM_HAS_ACTIVE_CONTRACT` khi xóa — domain Contract chưa tồn tại (xem P5-09c).

## Tiêu chí nghiệm thu chung

- Room API chạy được trên tenancy database.
- Quan hệ Building–Room được kiểm tra ở đúng application/domain boundary.
- Không có cross-database foreign key tới Identity Service.
- Outbox được ghi cùng transaction nếu Room phát integration event; không publish trực tiếp từ handler.
- Nếu có consumer: ghi inbox và business side effect trong cùng transaction; duplicate event không làm thay đổi dữ liệu lần hai.
- Mỗi endpoint đã triển khai có **sequence diagram** trong `api-docs` khớp implementation và được đổi tag `x-apidog-status: designing` → `released`.
- Field `district` đã bị xóa khỏi contract Room (lỗi contract, xem P5-09d).
- Manual verification và API contract được bàn giao đầy đủ.

## Nguồn tham chiếu

- `pm/phase-1/discovery/database-design.md` §2.5 — bảng `rooms`.
- `api-docs/src/paths/rooms/*.yaml` — endpoint contract.
- `api-docs/note.md` — các conflict đã ghi nhận về Room status.
