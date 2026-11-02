# P7-06 — Lưu Message, sequence và idempotency key

**Assignee:** `baoduong17` · **Iteration:** It5 · **Ước lượng:** 3 points
**Repo:** `community-service` · **Phụ thuộc:** P7-04, P7-05 · **Trạng thái:** 🟡 Open

## Context agent

Đọc backend `AGENTS.md` và skills `be-feature-workflow`, `be-structure`, `be-naming`; ERD v1/ERD-06/ERD-11; `api-docs/src/schemas/chat/message.yaml` và endpoint message sau P7-01.

## Quy tắc đã chốt

Message lưu chung text/image/system/bot; v1 không sửa/xóa. `sequence` tăng dần trong conversation. Client message retry idempotent theo `(senderMemberId, clientMessageId)`. V1 một ảnh tối đa mỗi image message; binary nằm Media Service, Community chỉ lưu `mediaId`. Message chat không tạo Notification inbox row. Theo P6-D76, Message lưu `senderNameSnapshot` lấy từ ConversationMember lúc gửi.

## Phạm vi và acceptance

- [ ] Tạo Message domain/persistence/migration với conversation, sender member, `senderNameSnapshot`, type, nội dung/media/payload, sequence, client ID và timestamps theo ERD/API.
- [ ] DB ràng buộc unique `(conversationId, sequence)` và idempotency key khi client ID có giá trị.
- [ ] Sequence có thể được cấp an toàn khi nhiều message của cùng conversation được ghi đồng thời; mô tả concurrency strategy trong PR.
- [ ] Không có foreign key sang Identity/Media service.
- [ ] Migration run/revert/run, build/lint pass.

## Không làm

- Không implement send/history endpoint, Socket/FCM, upload R2, bot renderer hoặc edit/delete.
