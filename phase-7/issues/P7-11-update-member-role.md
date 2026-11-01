# P7-11 — Đổi vai trò admin/member trong group

**Assignee:** `baoduong17` · **Iteration:** It6 · **Ước lượng:** 2 points
**Repo:** `community-service` · **Phụ thuộc:** P7-05, P7-07 · **Trạng thái:** 🟡 Open

## Agent brief

Đọc backend `AGENTS.md`, feature/presentation skills, OpenAPI `PUT /conversations/{conversationId}/members/{userId}/role` (`updateConversationMemberRole`) sau P7-01; BL-02/10/23 và schema ConversationMember.

## Quy tắc đã chốt

Admin group được đổi `admin ↔ member`, có thể bổ nhiệm thêm admin. Không thể hạ quyền admin cuối cùng. User hiện tại lấy từ JWT; không cho non-admin đổi role. Mỗi đổi role tạo system message.

## Acceptance

- [ ] Request chỉ nhận role `admin|member`; endpoint kiểm tra caller là admin của group.
- [ ] Chặn hạ admin cuối; trả mã lỗi đúng OpenAPI.
- [ ] Role change và system message được ghi cùng transaction; không cho đổi role trong direct conversation. Nếu payload action chưa được xác định trong OpenAPI/design sau P7-01, ghi blocker, không tự phát minh cấu trúc.
- [ ] Apidog kiểm tra promote, demote khi còn admin khác, demote admin cuối và caller không có quyền; build/lint pass.

## Không làm

- Không kick/leave, sửa title/avatar, gửi FCM hoặc tự đặt error code nếu OpenAPI chưa định nghĩa.
