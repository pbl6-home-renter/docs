# P13-03 — Gỡ quyền thanh toán của tài khoản bị khóa (chỉnh lại P12-09/P12-10)

**Trạng thái:** 🟡 Open
**Người phụ trách (đề xuất):** người đã làm P12-09 (`leminhkhai345` / `baoduong17`) + P12-10 (`ThaiBao11125`)
**Người review:** PM/leader
**Ước lượng:** 1 point
**Phụ thuộc:** —
**Repo / branch:** `Tenancy-Service`, `fe`, `api-docs` · `fix/p13-03-locked-account-remove-payment`

> **Đọc trước khi code:** [`decisions.md`](../decisions.md) (P13-D102 thay phần thanh toán của P12-D100).

## Bối cảnh

P12-09 (BE) và P12-10 (FE) đã làm theo P12-D100, gồm cả "tài khoản bị khóa vẫn thanh toán được hóa đơn". P13-D102 bỏ phần thanh toán vì app chưa có luồng thanh toán online. Phần **chỉ đọc** giữ nguyên, không làm lại.

## Phạm vi

1. **Rà soát** code đã merge của P12-09/P12-10, liệt kê vào comment của issue mọi chỗ mở thanh toán cho tài khoản bị khóa.
2. **BE:** gỡ `@AllowLocked()` khỏi mọi endpoint ghi liên quan thanh toán (nếu đã thêm). Giữ `@AllowLocked()` trên các endpoint GET chỉ đọc.
3. **FE:** khi `user.status === locked`, ẩn nút/màn thanh toán; banner khóa không nhắc tới thanh toán.
4. **api-docs:** sửa mô tả các endpoint đã ghi "hỗ trợ tài khoản bị khóa thanh toán"; bundle.

## Acceptance

- [ ] Tài khoản bị khóa gọi bất kỳ endpoint ghi nào liên quan hóa đơn/thanh toán → `403 ACCOUNT_LOCKED`.
- [ ] Tài khoản bị khóa vẫn xem được phòng, hợp đồng, hóa đơn của mình (không hồi quy P12-09/P12-10).
- [ ] Web không hiện nút thanh toán cho tài khoản bị khóa.

## Definition of Done

- [ ] BE: `npm test`, `npm run build`, `npm run lint` pass. FE: `npm run build`, `npm run lint`, `npm run i18n:check` pass.
- [ ] api-docs bundle; mỗi repo một PR, ghi chung issue này.
- [ ] Nếu rà soát không thấy chỗ nào mở thanh toán: ghi kết quả vào issue và đóng, không cần PR.
