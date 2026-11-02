# P7-13 — Gửi message và đọc history

**Assignee:** `baoduong17` · **Iteration:** It6 · **Ước lượng:** 3 points
**Repo:** `community-service` · **Phụ thuộc:** P7-05, P7-06, P7-07 · **Trạng thái:** 🟡 Open

## Context agent

Đọc backend `AGENTS.md`, feature workflow/API presentation skills; OpenAPI `GET /messages?conversationId=...` (`getMessages`) và `POST /messages` (`postMessages`) sau P7-01; Message request/response schemas; BL-03/07/13/14, ERD-11/13 và P6-D76.

## Hành vi đã chốt

Chỉ active member gửi. Read-only member xem tới `leftSequence`; người mới được add/re-add theo rule ERD-10. Hỗ trợ text; image message tham chiếu mediaId đã upload xong và thuộc conversation. Không edit/delete. Retry cùng `(senderMemberId, clientMessageId)` trả lại message cũ.

## Acceptance

- [ ] Send/list endpoint đúng contract; history phân trang bằng opaque cursor, không offset.
- [ ] Sequence tăng an toàn; retry cùng client ID không tạo bản ghi mới.
- [ ] Validate đúng loại nội dung: text có content hợp lệ; image có mediaId được Media authorization xác nhận. Không nhận file khác.
- [ ] Gửi message không tạo business Notification row; lưu xong mới phát event realtime ở task Socket.
- [ ] Apidog kiểm tra active/read-only/non-member, retry, cursor và ảnh; build/lint pass.
- [ ] Message lưu `senderNameSnapshot` từ ConversationMember theo P6-D76; response list/send trả `senderName`; client không gửi tên người gửi.

## Không làm

- Không FCM, Socket implementation, bot message, mention, edit/delete hoặc delivery history.
