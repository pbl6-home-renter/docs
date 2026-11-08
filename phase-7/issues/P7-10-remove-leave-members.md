# P7-10 — Thu hồi membership khi kick hoặc tự rời

**Assignee:** `baoduong17` · **Iteration:** It6 · **Ước lượng:** 3 points
**Repo:** `community-service` · **Phụ thuộc:** P7-05, P7-09 · **Trạng thái:** 🟢 Done

## Context agent

Đọc backend `AGENTS.md`, feature workflow, API `DELETE /conversations/{conversationId}/members/{userId}` (`removeConversationMember`) và `DELETE /conversations/{conversationId}/members/me` (`leaveConversation`) sau P7-01; BL-02/03/10/23, ERD-01/13.

## Hành vi đã chốt

Kick chỉ do admin group; user active có thể tự rời group. Không hard-delete membership. Khi thu hồi, chuyển `read_only`, set `leftAt` và `leftSequence` tới sequence cuối cùng của các system message được ghi trong transaction rời/kick. User đó không gửi tin mới; chỉ đọc tới mốc này.

Mỗi kick/rời tạo một system message riêng (`member_kicked` hoặc `member_left`). Nếu admin cuối cùng rời/bị kick, admin chuyển cho thành viên user **active** còn lại có `joinedAt` sớm nhất (tie-break bằng `createdAt`, rồi `id`) và tạo thêm system message `admin_transferred`. `leftSequence` của người rời/kick bao gồm cả message chuyển admin. Thành viên read-only không đủ điều kiện nhận admin. Nếu sau thao tác không còn thành viên user active, từ chối toàn bộ transaction với `409 GROUP_MUST_RETAIN_ACTIVE_MEMBER`; không xóa/đóng conversation.

## Acceptance

- [ ] Hai endpoint đúng method/path/auth/schema/status theo OpenAPI.
- [ ] Membership chuyển read-only và đóng băng read boundary atomically với thay đổi group.
- [ ] Admin cuối không để group không có admin nếu còn member đủ điều kiện; chọn member theo `joinedAt` sớm nhất.
- [ ] Nếu thao tác làm group không còn member nào, dừng và ghi blocker cho PM; không tự xóa/đóng conversation hay tạo system participant thay người.
- [ ] Kick/leave tạo system message riêng theo payload contract; chuyển admin tạo system message riêng; không gửi FCM.
- [ ] `leftSequence` bao gồm toàn bộ system message kick/leave và chuyển admin trong cùng transaction; member read-only thấy được các message này.
- [ ] Khi không còn user active, trả 409 `GROUP_MUST_RETAIN_ACTIVE_MEMBER` và rollback toàn bộ thay đổi.
- [ ] Apidog kiểm tra self-leave, kick quyền sai, kick admin cuối và đọc tới `leftSequence`; build/lint pass.

## Không làm

- Không hard-delete history/membership, khóa conversation khi checkout, hoặc xử lý ContractMember/building sync.
