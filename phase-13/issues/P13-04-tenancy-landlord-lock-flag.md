# P13-04 — BE: Tenancy ghi nhận landlord bị khóa, ẩn tòa và trả cờ cho tenant

**Trạng thái:** 🟡 Open
**Người phụ trách (đề xuất):** `baoduong17`
**Người review:** `leminhkhai345`
**Ước lượng:** 2 points
**Phụ thuộc:** P13-01 (cùng sửa `identity-lifecycle.subscriber.ts`, làm sau để tránh xung đột)
**Repo / branch:** `Tenancy-Service`, `api-docs` · `feature/p13-04-landlord-lock-flag`

> **Đọc trước khi code:** [`decisions.md`](../decisions.md) (P13-D103), `AGENTS.md` và skill của repo.

## Mục tiêu

- Tòa nhà của landlord bị khóa **không xuất hiện** ở tìm kiếm và xem chi tiết công khai; mở khóa thì tự hiện lại.
- Tenant xem hợp đồng/hóa đơn biết được landlord đang bị khóa (để FE ẩn QR ở P13-05).

## Thiết kế

- Tenancy lưu tập landlord đang bị khóa (bảng mới, ví dụ `locked_landlords(user_id, locked_at)`), cập nhật trong `identity-lifecycle.subscriber.ts`:
  - `user.locked` với role landlord → thêm dòng.
  - `user.unlocked` → xóa dòng.
  - Idempotent: nhận trùng event không lỗi (inbox dedup đã có).
- **Không** đổi `BuildingStatus` (`pending/approved/rejected`) để mở khóa không phải duyệt lại.
- Lấp dữ liệu lần đầu: landlord đang bị khóa tại thời điểm deploy. Cách làm (gọi internal Identity hoặc script một lần) ghi trong PR.

## Phạm vi

| Hạng mục | Vị trí | Thay đổi |
|---|---|---|
| Tìm kiếm công khai | `building/application/queries/building-search-public/` | Loại tòa có landlord trong tập bị khóa |
| Chi tiết công khai | `building/application/queries/building-get-public/` | Landlord bị khóa → `404` như tòa không tồn tại |
| Hợp đồng của tenant | `GET /me/contracts`, `GET /contracts/:id` | Thêm field `landlordLocked: boolean` |
| Hóa đơn của tenant | `invoice/application/queries/invoice-my-list/`, `invoice-detail/` | Thêm field `landlordLocked: boolean` |
| api-docs | schema hợp đồng, hóa đơn, mô tả endpoint tìm kiếm | Thêm field, ghi rõ quy tắc ẩn tòa; bundle |

Các màn quản lý của landlord và admin **không** bị ảnh hưởng.

## Acceptance

- [ ] Khóa landlord → tòa của họ biến mất khỏi `GET /buildings` (công khai); `GET /buildings/:id` công khai trả `404`.
- [ ] Mở khóa → tòa hiện lại, trạng thái duyệt không đổi.
- [ ] Tenant gọi danh sách/chi tiết hợp đồng, hóa đơn → `landlordLocked = true` khi landlord bị khóa, `false` sau khi mở khóa.
- [ ] Admin vẫn thấy tòa ở màn quản trị.
- [ ] Event `user.locked` của tenant không thêm dòng vào tập landlord bị khóa.

## Definition of Done

- [ ] Unit test cho subscriber và hai query công khai; `npm test`, `npm run build`, `npm run lint` pass.
- [ ] Migration sinh bằng `migration:generate`, chạy và revert được.
- [ ] api-docs bundle; mỗi repo một PR, ≥ 1 reviewer.
