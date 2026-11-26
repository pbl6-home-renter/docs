# P13-05 — FE/Mobile: Ẩn QR thanh toán khi landlord bị khóa

**Trạng thái:** 🟡 Open
**Người phụ trách (đề xuất):** `ThaiBao11125` (Web) + Mobile (PM giao)
**Người review:** PM/leader
**Ước lượng:** 1 point
**Phụ thuộc:** P13-04
**Repo / branch:** `fe`, `mobile` · `feature/p13-05-hide-qr-locked-landlord`

> **Đọc trước khi code:** [`decisions.md`](../decisions.md) (P13-D103).

## Mục tiêu

Tenant xem hóa đơn của landlord đang bị khóa **không thấy** mã QR và thông tin chuyển khoản. Hóa đơn, hợp đồng vẫn hiển thị đầy đủ.

## Phạm vi

- Dùng field `landlordLocked` từ P13-04 trên hóa đơn/hợp đồng của tenant.
- `landlordLocked = true` → ẩn khối QR / số tài khoản. **Không** thêm câu hướng dẫn thanh toán nào (P13-D103).
- Hiện nhãn nhỏ "Tài khoản chủ trọ đã bị khóa" cạnh tên landlord ở chi tiết hóa đơn/hợp đồng (cùng chuỗi i18n với P13-06).
- Mobile: chỉ làm nếu màn hóa đơn tenant đang hiển thị QR.

## Acceptance

- [ ] Landlord bị khóa → không còn QR/thông tin chuyển khoản trên mọi hóa đơn của tenant.
- [ ] Mở khóa → QR hiện lại (sau khi tải lại dữ liệu).
- [ ] Không có câu chữ nào hướng dẫn thanh toán thay thế.

## Definition of Done

- [ ] Web: `npm run build`, `npm run lint`, `npm run i18n:check` pass; không viết file test.
- [ ] Mobile: `./gradlew :app-tenant:assembleDebug` pass (nếu có thay đổi).
- [ ] Ảnh chụp trước/sau trong PR.
