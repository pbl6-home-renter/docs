# P7-09 — Xem và thêm thành viên conversation

**Assignee:** `baoduong17` · **Iteration:** It6 · **Ước lượng:** 3 points
**Repo:** `community-service` · **Phụ thuộc:** P7-05, P7-07 · **Trạng thái:** 🟡 Open

## Context agent

Đọc backend `AGENTS.md`, feature/presentation skills; OpenAPI `GET/POST /conversations/{conversationId}/members` sau P7-01; ConversationMember schema; BL-02/08/23, ERD-10 và P6-D76 trong Community design.

## Hành vi đã chốt

Chỉ admin group được thêm thành viên; người được thêm xem toàn bộ lịch sử. Nếu member từng read-only thì kích hoạt lại row cũ, cập nhật `displayName` từ Identity và đặt cursor đọc đến message mới nhất tại thời điểm re-add. Member mới cũng lấy tên từ Identity trước transaction. BL-23 yêu cầu thay đổi thành viên có system message; ghi message cùng transaction. Socket sẽ được nối ở task realtime; system message không gửi FCM.

## Acceptance

- [ ] `GET members` trả member active/read-only và `displayName` theo quyền đọc của caller.
- [ ] `POST members` chỉ cho admin group; không cho thêm trùng user hoặc thêm vào direct/context conversation nếu API không cho phép.
- [ ] Re-add dùng membership row cũ, đặt active và cursor theo ERD-10; add mới xem toàn bộ history.
- [ ] Thay đổi membership và system message được ghi atomic; nếu payload action chưa được xác định trong OpenAPI/design sau P7-01, ghi blocker và không tự phát minh cấu trúc.
- [ ] Apidog kiểm tra admin/member, duplicate, re-add và non-member; build/lint pass.

## Không làm

- Không kick/leave/role update hoặc Socket/FCM.
