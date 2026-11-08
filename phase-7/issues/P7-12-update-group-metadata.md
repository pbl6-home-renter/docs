# P7-12 — Sửa tên và ảnh đại diện group

**Assignee:** `baoduong17` · **Iteration:** It6 · **Ước lượng:** 2 points
**Repo:** `community-service` · **Phụ thuộc:** P7-04, P7-06–07 và CB-07 Media · **Trạng thái:** 🟢 Done

## Context agent

Đọc backend `AGENTS.md`, feature/presentation skills; OpenAPI `PATCH /conversations/{conversationId}` (`updateConversation`) sau P7-01; ERD Conversation; BL-02/23. Ảnh chat dùng Media Service/R2, `ownerType=conversation`, `ownerId=conversationId`, không upload qua Community.

## Quy tắc đã chốt

Chỉ admin group đổi title/avatar; không áp dụng cho direct. Mỗi thay đổi có system message. Mỗi message ảnh chỉ có một media ID. Client upload qua presigned URL trước, sau đó Community chỉ lưu ID.

## Acceptance

- [ ] PATCH chỉ nhận field được OpenAPI cho phép; hỗ trợ nullable avatar để gỡ ảnh nếu contract quy định.
- [ ] Caller phải là active admin của group; không sửa direct conversation.
- [ ] Chỉ bắt đầu phần avatar sau khi CB-07 Media resolver sẵn sàng; xác minh media đã complete, owner conversation đúng và purpose hợp lệ. Không tự dùng `chat_attachment` cho group avatar nếu Media contract không quy định; tuyệt đối không tin ID từ client.
- [ ] Cập nhật metadata và system message atomic; không FCM cho system change.
- [ ] Manual Apidog kiểm tra admin/member, direct, title và avatar authorization; build/lint pass.

## Phụ thuộc / không làm

Không làm partial avatar support hoặc bỏ qua authorization trước CB-07. Không xây upload endpoint hoặc lưu binary.
