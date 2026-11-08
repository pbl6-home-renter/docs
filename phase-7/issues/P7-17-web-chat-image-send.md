# P7-17 — Gửi ảnh trong Web Chat

**Assignee:** `ThaiBao11125` · **Iteration:** Chưa gán · **Ước lượng:** 3 points
**Repo:** `fe` · **Phụ thuộc:** P7-13, CB-07 Media · **Trạng thái:** 🟢 Done

## Quy tắc đã chốt

- Một message có tối đa một ảnh; ảnh dùng R2 presigned upload, Community chỉ lưu `mediaId`.
- Upload gắn với conversation (`ownerType=conversation`, `ownerId=conversationId`); không cần tạo message nháp trước.
- Chấp nhận ảnh theo policy Media hiện tại; không hỗ trợ file đính kèm khác trong v1.
- Message giữ idempotency key khi retry; ảnh đã upload nhưng gửi message thất bại cần hiển thị trạng thái/đường thử lại theo hành vi chat đã chốt.

## Acceptance

- [ ] Chọn và xem trước một ảnh trước khi gửi; validate loại/dung lượng theo Media policy.
- [ ] Upload presign → PUT → complete rồi gửi `mediaId` trong message.
- [ ] Bubble optimistic giữ ổn định; lỗi upload/send có thể thử lại mà không tạo message trùng.
- [ ] Lịch sử hiện ảnh và viewer ảnh lớn dùng chung component hiện có.
- [ ] Có trạng thái upload/error, accessibility và i18n; build/lint/i18n check pass.
