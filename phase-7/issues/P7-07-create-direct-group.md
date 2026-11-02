# P7-07 — Tạo direct/group conversation

**Assignee:** `baoduong17` · **Iteration:** It6 · **Ước lượng:** 3 points
**Repo:** `community-service` · **Phụ thuộc:** P7-01, P7-04–06 · **Trạng thái:** 🟡 Open

## Agent brief

Đọc `community-service/AGENTS.md`, backend workflow/presentation skills, `api-docs/src/paths/chat/conversations.yaml` (`POST`, `createConversation`) sau P7-01, request/response schemas, BL-01/BL-09, ERD-08 và P6-D76 trong Community design.

## Hành vi đã chốt

- Mọi user đã đăng nhập được mở direct chat hoặc tạo group; user hiện tại lấy từ JWT, không từ body.
- Direct: đúng một conversation cho cặp user đã chuẩn hóa; request sau trả/mở lại conversation cũ, kích hoạt lại membership cũ nếu cần.
- Group: tạo conversation mới chưa có ảnh đại diện; caller được thêm làm admin; request có danh sách thành viên ban đầu, caller không bắt buộc nằm trong danh sách.
- Ảnh đại diện được upload sau khi conversation đã tạo, rồi gắn qua `PATCH /conversations/{conversationId}` trong P7-12 sau khi CB-07 Media resolver sẵn sàng.
- Kiểm tra user ID đầu vào bằng Identity `GET /internal/users?ids=...`; từ chối ID không tồn tại/đã xóa bằng 422 và fail closed nếu Identity không sẵn sàng (503). Không đọc Identity DB trực tiếp.
- Lưu `displayName` lấy từ Identity trên ConversationMember; client không được gửi tên member.

## Acceptance

- [ ] `POST /conversations` tuân đúng request/response/status/code của OpenAPI sau P7-01.
- [ ] Direct pair được chuẩn hóa ổn định; request đồng thời không tạo hai conversation.
- [ ] Group có creator admin và member ban đầu không trùng; lỗi validation khớp API.
- [ ] `recipientUserId`/`memberUserIds` được kiểm tra qua Identity internal lookup; ID không tồn tại hoặc đã xóa không tạo conversation.
- [ ] Tên member lấy từ Identity và lưu vào ConversationMember theo P6-D76.
- [ ] Request tạo conversation không nhận `avatarMediaId`; ảnh group được xử lý riêng ở P7-12 sau khi đã có `conversationId`.
- [ ] Mọi command ghi Conversation + Membership cùng transaction; không nhận `createdByUserId`/admin ID từ client.
- [ ] Apidog/Swagger happy path cho direct mới, direct mở lại và tạo group; build/lint pass.

## Không làm

- Không làm CRUD membership sau khi tạo, list/detail, ảnh upload, context chat theo event hoặc bot.
- Không upload hoặc cập nhật ảnh đại diện trong issue này; P7-12 phụ thuộc CB-07 để xác thực media.
