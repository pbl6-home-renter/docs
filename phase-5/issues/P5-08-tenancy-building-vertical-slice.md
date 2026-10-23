# P5-08 — Building vertical slice (Epic)

> Chuyển từ `P4-24` (Phase 4) sang Phase 5 và tách thành sub-issue `P5-08a` → `P5-08e`.

**Trạng thái:** 🟡 Open  
**Người phụ trách:** BE member  
**Người review:** BE Lead, API owner, PM  
**Ước lượng:** 21 points (tổng sub-issue)  
**Độ ưu tiên:** High  
**Phụ thuộc:** P4-21

## Bối cảnh

Thay vì triển khai rời rạc từng layer, Building cần được làm thành một vertical slice chạy từ request đến database và outbox. Đây là slice mẫu để team triển khai Room (`P5-09`) và các domain tiếp theo.

Issue này là issue cha. Công việc thực tế được giao qua các sub-issue bên dưới; issue cha chỉ đóng khi toàn bộ sub-issue đã Done.

## Sub-issue

| ID | Task | Endpoint | Estimate | Phụ thuộc |
|---|---|---|---|---|
| [P5-08a](P5-08a-building-domain-persistence.md) | Domain model và persistence | — | 3 pts | P4-21 |
| [P5-08b](P5-08b-building-create-command.md) | Create Building — slice mẫu UoW + Outbox | `POST /buildings` | 5 pts | P5-08a |
| [P5-08c](P5-08c-building-landlord-management.md) | Landlord quản lý Building | `GET /me/buildings`, `GET /me/buildings/{id}`, `PATCH /buildings/{id}`, `DELETE /buildings/{id}` | 5 pts | P5-08b |
| [P5-08d](P5-08d-building-admin-approval.md) | Admin duyệt/từ chối Building | `GET /admin/buildings`, `GET /admin/buildings/{id}`, `POST /buildings/{id}/approve`, `POST /buildings/{id}/reject` | 5 pts | P5-08b |
| [P5-08e](P5-08e-building-public-search.md) | Tìm kiếm và xem Building public | `GET /buildings`, `GET /buildings/{id}` | 3 pts | P5-08d |

Thứ tự: `P5-08a → P5-08b → (P5-08c ∥ P5-08d) → P5-08e`.

## Ngoài phạm vi epic này

- `POST /buildings/{id}/rate-policies/batch` và `PUT /buildings/{id}/vietqr-config` — thuộc nhóm billing/payment, tạo issue riêng sau.
- Media (`cover_photo`, `gallery_photo`, `ownership_proof`) — chưa có media flow; không validate `ownershipCertificateMediaIds`.
- Geocoding thật cho `latitude`/`longitude` — tạm dùng giá trị mặc định (xem P5-08b).
- Check `BUILDING_HAS_ACTIVE_CONTRACT` khi xóa — domain Contract chưa tồn tại (xem P5-08c).

## Tiêu chí nghiệm thu chung (áp dụng cho mọi sub-issue có write operation)

- API chạy được với tenancy database.
- Aggregate và outbox row được ghi trong cùng transaction.
- Khi rollback, không còn aggregate hoặc outbox row dở dang.
- Không publish trực tiếp RabbitMQ từ controller/command handler; relay publish sau commit.
- Route, schema và error code khớp `api-docs`; API owner đã cập nhật contract nếu có thay đổi.
- Mỗi endpoint đã triển khai có **sequence diagram** trong `api-docs` khớp implementation và được đổi tag `x-apidog-status: designing` → `released`.
- Manual verification được ghi lại trong PR/issue.

## Sửa contract: bỏ field `district`

`district` trong `api-docs` là lỗi (địa chỉ chỉ còn Tỉnh/TP → Phường/Xã, khớp bảng `buildings`). Mỗi sub-issue xóa `district` ở các file contract mình đụng tới — danh sách file nằm trong từng issue (P5-08b, P5-08c, P5-08d, P5-09d). Không thêm cột `district` vào database.

## Luồng xử lý chuẩn

```text
HTTP Request
  → Controller/DTO validation
  → Command Handler
  → UoW transaction
  → Building Aggregate
  → Repository save + Outbox append
  → Commit database
  → Relay publish integration event
```

## Nguồn tham chiếu

- `pm/phase-1/discovery/database-design.md` — bảng `buildings`.
- `api-docs/src/paths/buildings/*.yaml` — endpoint contract.
- `boilerplate` — UoW, Transactional Outbox, relay.
