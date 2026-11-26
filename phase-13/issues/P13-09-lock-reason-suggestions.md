# P13-09 — FE: Gợi ý lý do khi admin khóa tài khoản

**Trạng thái:** 🟡 Open
**Người phụ trách (đề xuất):** `ThaiBao11125`
**Người review:** PM/leader
**Ước lượng:** 0.5 point
**Phụ thuộc:** —
**Repo / branch:** `fe` · `feature/p13-09-lock-reason-suggestions`

## Mục tiêu

Admin khóa tài khoản nhanh và thống nhất hơn: bấm một gợi ý là lý do được điền sẵn vào ô, vẫn sửa tay được.

## Hiện trạng

`fe/src/features/users/components/admin/user-lock-dialog.tsx` chỉ có một ô `Textarea` tự do (`lockReason`, tối đa 500 ký tự). Không có gợi ý.

## Phạm vi

- Thêm một hàng chip phía trên ô lý do, gồm 6 gợi ý theo tài liệu nghiệp vụ:
  1. Lừa đảo hoặc thu tiền sai thỏa thuận
  2. Tin đăng giả, ảnh và thông tin phòng không đúng thực tế
  3. Quấy rối, đe dọa người dùng khác
  4. Spam tin nhắn hoặc quảng cáo
  5. Giả mạo danh tính
  6. Nội dung không phù hợp
- Bấm chip → `setValue('lockReason', <nội dung>, { shouldValidate: true })`. Ô đã có nội dung thì **thay thế**; admin có thể sửa hoặc bổ sung chi tiết sau đó.
- Chuỗi gợi ý đặt trong i18n (`users.json`, `vi`/`en`). Giá trị gửi lên BE là chuỗi theo ngôn ngữ đang chọn, BE không đổi.

## Acceptance

- [ ] Mở hộp thoại khóa → thấy 6 chip.
- [ ] Bấm chip → ô lý do được điền đúng chuỗi, lỗi "bắt buộc nhập" (nếu có) biến mất.
- [ ] Sửa tay sau khi bấm chip vẫn được; giới hạn 500 ký tự vẫn áp dụng.

## Definition of Done

- [ ] `npm run build`, `npm run lint`, `npm run i18n:check` pass; không viết file test.
- [ ] Ảnh chụp hộp thoại trong PR.
