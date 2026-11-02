# P7-11 — Đổi vai trò admin/member trong group

**Assignee:** `baoduong17` · **Iteration:** It6 · **Ước lượng:** 2 points
**Repo:** `community-service` · **Phụ thuộc:** P7-05, P7-07 · **Trạng thái:** 🟡 Open

## Agent brief

Đọc backend `AGENTS.md`, feature/presentation skills, OpenAPI `PUT /conversations/{conversationId}/members/{userId}/role` (`updateConversationMemberRole`) sau P7-01; BL-02/10/23 và schema ConversationMember.

## Quy tắc đã chốt

Admin active của group được đổi vai trò user active giữa `admin ↔ member`, có thể bổ nhiệm thêm admin. Không thể hạ quyền admin cuối cùng. User hiện tại lấy từ JWT; không cho non-admin đổi role. Khi role thực sự thay đổi, ghi system message `member_role_changed` với payload `{ action, actorUserId, member: { userId, displayName }, oldRole, newRole }` trong cùng transaction. Nếu role đích đã là role hiện tại thì trả thành công nhưng không tạo message trùng. Không gửi FCM.

## Acceptance

- System payload: `member_role_changed` với `actorUserId`, snapshot `member`, `oldRole`, `newRole`; nếu role đích giống hiện tại thì không ghi system message.
- Chỉ active user member được đổi role; system message và cập nhật role cùng transaction, không gửi FCM.
- Lỗi hạ admin cuối: `409 LAST_ADMIN_CANNOT_BE_DEMOTED`.

- [ ] Request chỉ nhận role `admin|member`; endpoint kiểm tra caller và target đều là user active member của group.
- [ ] Chặn hạ admin cuối; trả `409 LAST_ADMIN_CANNOT_BE_DEMOTED`.
- [ ] Role change và system message đúng payload P7-D79 được ghi cùng transaction; không cho đổi role trong direct conversation. Role không đổi thì không ghi system message.
- [ ] Apidog kiểm tra promote, demote khi còn admin khác, demote admin cuối và caller không có quyền; build/lint pass.

## Không làm

- Không kick/leave, sửa title/avatar, gửi FCM hoặc tự đặt error code nếu OpenAPI chưa định nghĩa.
