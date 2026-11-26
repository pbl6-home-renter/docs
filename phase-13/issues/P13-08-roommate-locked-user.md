# P13-08 — BE: Ghép bạn với tài khoản bị khóa

**Trạng thái:** 🟡 Open
**Người phụ trách (đề xuất):** BE Tenancy (PM giao)
**Người review:** `leminhkhai345`
**Ước lượng:** 1 point
**Phụ thuộc:** —
**Repo / branch:** `Tenancy-Service`, `api-docs` · `feature/p13-08-roommate-locked-user`

> **Đọc trước khi code:** [`decisions.md`](../decisions.md) (P13-D106), P10-D88/P10-D89 (ghép bạn).

## Mục tiêu

Tenant bị khóa không xuất hiện trong tìm kiếm bạn ở ghép và không bị kéo vào giao dịch ghép đôi mới. Lời mời cũ **được giữ nguyên** để mở khóa xong là dùng tiếp, không cần khôi phục.

## Quy tắc

| Tình huống | Hành vi |
|---|---|
| Tìm kiếm hồ sơ (`roommate-profile-search`) | Loại hồ sơ của tenant đang bị khóa. **Không** đổi lựa chọn `isVisible` của họ |
| Xem hồ sơ theo id của người bị khóa | `404` |
| Gửi lời mời tới người đang bị khóa (`match-request-create`) | Chặn, `409` (mã do API owner đặt) |
| Chấp nhận / từ chối lời mời mà bên kia đang bị khóa (`match-request-transition`) | Chặn, `409` |
| Người bị khóa tự thao tác | Đã bị chặn bởi `ActiveUserGuard` (`403 ACCOUNT_LOCKED`) |
| Lời mời đang chờ lúc khóa | Giữ nguyên trạng thái |
| Mở khóa | Hồ sơ tự hiện lại; lời mời dùng tiếp như bình thường |

## Thiết kế

- Dùng projection `tenant_users` đã có: tenant bị khóa bị xóa khỏi projection khi nhận `user.locked`, thêm lại khi `user.unlocked`. Lọc theo projection này, không thêm bảng mới.

## Acceptance

- [ ] Khóa tenant A → A không còn trong kết quả tìm kiếm của người khác; xem hồ sơ A → `404`.
- [ ] B gửi lời mời cho A → `409`; B chấp nhận lời mời A gửi trước đó → `409`.
- [ ] Mở khóa A → A hiện lại trong tìm kiếm, B chấp nhận được lời mời cũ.

## Definition of Done

- [ ] Unit test cho query search và hai command; `npm test`, `npm run build`, `npm run lint` pass.
- [ ] api-docs: thêm mã lỗi `409` và ghi chú quy tắc; bundle.
- [ ] PR vào `main`, ≥ 1 reviewer.
