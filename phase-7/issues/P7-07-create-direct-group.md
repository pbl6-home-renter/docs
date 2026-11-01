# P7-07 — Tạo direct/group conversation

**Assignee:** `baoduong17` · **Iteration:** It6 · **Ước lượng:** 3 points
**Repo:** `community-service` · **Phụ thuộc:** P7-01, P7-04–06 và CB-07 Media · **Trạng thái:** 🟡 Open

## Agent brief

Đọc `community-service/AGENTS.md`, backend workflow/presentation skills, `api-docs/src/paths/chat/conversations.yaml` (`POST`, `createConversation`) sau P7-01, request/response schemas, và BL-01/BL-09, ERD-08 trong Community design.

## Hành vi đã chốt

- Mọi user đã đăng nhập được mở direct chat hoặc tạo group; user hiện tại lấy từ JWT, không từ body.
- Direct: đúng một conversation cho cặp user đã chuẩn hóa; request sau trả/mở lại conversation cũ, kích hoạt lại membership cũ nếu cần.
- Group: tạo conversation mới; caller được thêm làm admin; request có danh sách thành viên ban đầu, caller không bắt buộc nằm trong danh sách.

## Acceptance

- [ ] `POST /conversations` tuân đúng request/response/status/code của OpenAPI sau P7-01.
- [ ] Direct pair được chuẩn hóa ổn định; request đồng thời không tạo hai conversation.
- [ ] Group có creator admin và member ban đầu không trùng; lỗi validation khớp API.
- [ ] Nếu request có `avatarMediaId`, chỉ chấp nhận sau khi CB-07 Media resolver xác minh media complete, đúng conversation owner và purpose; tuyệt đối không lưu ID chưa được xác thực.
- [ ] Mọi command ghi Conversation + Membership cùng transaction; không nhận `createdByUserId`/admin ID từ client.
- [ ] Apidog/Swagger happy path cho direct mới, direct mở lại và tạo group; build/lint pass.
- [ ] Nếu cần xác minh `recipientUserId/memberUserIds` tồn tại, chỉ dùng API nội bộ đã được duyệt; không truy vấn Identity DB. Nếu chưa có contract lookup, ghi blocker trước khi tự chọn hành vi cho ID không tồn tại.

## Không làm

- Không làm CRUD membership sau khi tạo, list/detail, ảnh upload, context chat theo event hoặc bot.
- Không bỏ qua xác thực `avatarMediaId`; nếu CB-07 chưa sẵn sàng, chờ dependency thay vì tin ID từ client.
