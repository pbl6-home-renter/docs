# P13-06 — Nhãn "Tài khoản đã bị khóa" trong chat

**Trạng thái:** 🟡 Open
**Người phụ trách (đề xuất):** `huynhtiennhat0403` (community) + `ThaiBao11125` (Web) + Mobile (PM giao)
**Người review:** PM/leader
**Ước lượng:** 2 points
**Phụ thuộc:** —
**Repo / branch:** `community-service`, `fe`, `mobile`, `api-docs` · `feature/p13-06-chat-locked-label`

> **Đọc trước khi code:** [`decisions.md`](../decisions.md) (P13-D103), `AGENTS.md` và skill của từng repo.

## Mục tiêu

Trong chat phòng/tòa, thành viên đang bị khóa hiện nhãn **"Tài khoản đã bị khóa"** cạnh tên. Người khác vẫn đọc lịch sử tin nhắn bình thường. Mở khóa thì nhãn tự mất, không gửi thông báo cho ai.

## Hiện trạng

- community-service **chưa nhận** event `user.locked` / `user.unlocked` từ Identity.
- Người bị khóa gọi API chat → `403 ACCOUNT_LOCKED` (giữ nguyên, đây chính là "không gửi tin mới").

## Phạm vi

1. **community-service**
   - Thêm consumer cho `user.locked` / `user.unlocked` (exchange Identity, inbox dedup như các consumer khác).
   - Lưu trạng thái khóa theo user (bảng mới hoặc cột trên bảng thành viên hiện có, chọn theo cấu trúc module `conversation`).
   - Trả thêm `isLocked: boolean` cho từng thành viên ở API danh sách thành viên / chi tiết hội thoại.
   - Lấp dữ liệu lần đầu cho user đang bị khóa lúc deploy (ghi cách làm trong PR).
2. **api-docs:** thêm field `isLocked` vào schema thành viên hội thoại; bundle.
3. **fe:** hiện nhãn cạnh tên thành viên bị khóa trong khung chat và danh sách thành viên; key i18n `vi`/`en`.
4. **mobile:** như Web, nếu màn chat đã có trên mobile.

## Acceptance

- [ ] Khóa tenant A → trong chat phòng của A, landlord và bạn cùng phòng thấy nhãn cạnh tên A.
- [ ] Khóa landlord → tenant thấy nhãn cạnh tên landlord.
- [ ] Mở khóa → nhãn biến mất; không có thông báo nào gửi cho người khác.
- [ ] Event trùng không tạo lỗi hay dữ liệu trùng.

## Definition of Done

- [ ] community: unit test consumer; `npm test`, `npm run build`, `npm run lint` pass.
- [ ] fe: `npm run build`, `npm run lint`, `npm run i18n:check` pass; không viết file test.
- [ ] api-docs bundle; mỗi repo một PR, ghi chung issue này.

## Ngoài phạm vi

- Ẩn hồ sơ, chặn thao tác ghép bạn: [P13-08](P13-08-roommate-locked-user.md).
- Thay đổi bot nhắc / sự cố khi landlord bị khóa (P13-D107).
