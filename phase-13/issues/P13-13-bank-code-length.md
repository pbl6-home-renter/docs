# P13-13 — BE: Cho phép mã ngân hàng ngắn trong tài khoản nhận tiền

**Trạng thái:** 🟡 Open
**Người phụ trách (đề xuất):** `huynhtiennhat0403`
**Người review:** `baoduong17` (API owner)
**Ước lượng:** 0.5 point
**Phụ thuộc:** —
**Repo / branch:** `Identity-Service`, `api-docs`, `fe` · `fix/p13-13-bank-code-length`

## Bối cảnh

`bankCode` đang yêu cầu 4–20 ký tự ở cả hai nơi:

- `Identity-Service/src/modules/landlord-profiles/domain/value-objects/payout-account.vo.ts:17`
- `Identity-Service/src/modules/users/presentation/http/requests/payout-account.request.dto.ts:16` (`@Length(4, 20)`)

Các mã ngân hàng phổ biến như `MB`, `VCB`, `ACB`, `TCB`, `BID`, `VPB` bị từ chối, nên landlord không lưu được tài khoản nhận tiền.

## Phạm vi

- Nới giới hạn thành **2–20 ký tự** ở value object và request DTO (cùng thông điệp lỗi, chỉ đổi số).
- api-docs: sửa `minLength` của `bankCode`, bundle.
- fe: nếu schema zod của form tài khoản nhận tiền cũng chặn 4 ký tự thì sửa cho khớp.
- **Không** đổi sang mã BIN Napas 6 chữ số trong task này. Việc chuẩn hóa theo VietQR thuộc spike VietQR (P11-D93), làm khi tích hợp thật.

## Acceptance

- [ ] `PATCH /me` với `bankCode = "MB"` → `200`, lưu thành công.
- [ ] `bankCode = "A"` hoặc dài hơn 20 ký tự → `422` với mã lỗi như cũ.
- [ ] Form Web nhận được `VCB`, `MB`.

## Definition of Done

- [ ] Unit test value object; `npm test`, `npm run build`, `npm run lint` pass.
- [ ] api-docs bundle; fe `npm run build`, `npm run lint` pass (nếu có sửa).
