# P7-10 — Thu hồi membership khi kick hoặc tự rời

**Assignee:** `baoduong17` · **Iteration:** It6 · **Ước lượng:** 3 points
**Repo:** `community-service` · **Phụ thuộc:** P7-05, P7-09 · **Trạng thái:** 🟡 Open

## Context agent

Đọc backend `AGENTS.md`, feature workflow, API `DELETE /conversations/{conversationId}/members/{userId}` (`removeConversationMember`) và `DELETE /conversations/{conversationId}/members/me` (`leaveConversation`) sau P7-01; BL-02/03/10/23, ERD-01/13.

## Hành vi đã chốt

Kick chỉ do admin group; user active có thể tự rời group. Không hard-delete membership. Khi thu hồi, chuyển `read_only`, set `leftAt` và `leftSequence` tới sequence cuối hiện có. User đó không gửi tin mới; chỉ đọc tới mốc này. Nếu admin cuối cùng rời/bị kick, admin chuyển cho member còn lại tham gia sớm nhất.

## Acceptance

- [ ] Hai endpoint đúng method/path/auth/schema/status theo OpenAPI.
- [ ] Membership chuyển read-only và đóng băng read boundary atomically với thay đổi group.
- [ ] Admin cuối không để group không có admin nếu còn member đủ điều kiện; chọn member theo `joinedAt` sớm nhất.
- [ ] Nếu thao tác làm group không còn member nào, dừng và ghi blocker cho PM; không tự xóa/đóng conversation hay tạo system participant thay người.
- [ ] Kick/leave tạo system message đúng contract; không gửi FCM.
- [ ] Chốt rõ `leftSequence` có bao gồm system message kick/leave hay không trước khi code boundary; nếu OpenAPI/design sau P7-01 chưa quy định, ghi blocker, không tự chọn thứ tự.
- [ ] Apidog kiểm tra self-leave, kick quyền sai, kick admin cuối và đọc tới `leftSequence`; build/lint pass.

## Không làm

- Không hard-delete history/membership, khóa conversation khi checkout, hoặc xử lý ContractMember/building sync.
