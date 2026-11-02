# P7-08 — Liệt kê và đọc conversation theo membership

**Assignee:** `baoduong17` · **Iteration:** It6 · **Ước lượng:** 3 points
**Repo:** `community-service` · **Phụ thuộc:** P7-04–07 · **Trạng thái:** 🟡 Open

## Context agent

Đọc backend `AGENTS.md` và query/presentation skills; OpenAPI `GET /conversations` (`getConversations`) và `GET /conversations/{conversationId}` (`getConversationsConversationid`) sau P7-01; Conversation list/detail response schemas; BL-03/09/11/12, ERD-13 và P6-D76.

## Acceptance

- [ ] `GET /conversations` chỉ trả conversation mà user có membership đọc được; giữ offset `pageNo/pageSize` theo API.
- [ ] Filter `contextType+contextId` chỉ tra context đã có, không tự tạo conversation.
- [ ] Trả `unreadCount` và `lastMessage` theo schema đã duyệt; không dùng field domain cũ `roomId/contractId`.
- [ ] `lastMessage.senderName` lấy từ `Message.senderNameSnapshot`; không gọi Identity trong list query.
- [ ] Detail/list members trả `displayName` từ ConversationMember theo P6-D76.
- [ ] Detail kiểm tra membership: active xem đầy đủ; read-only xem theo `leftSequence`; người chưa từng là member không đọc được.
- [ ] Offset pagination boundaries and error codes match OpenAPI; manual Apidog checks, build/lint pass.

## Không làm

- Không cập nhật read cursor tại GET; không implement message list, Socket, context creation hoặc user lookup chéo service.
