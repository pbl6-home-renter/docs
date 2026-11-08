# P7-01 — Đồng bộ OpenAPI Chat v1 với thiết kế đã duyệt

**Assignee:** `baoduong17`
**Iteration:** It5
**Ước lượng:** 2 points
**Repo:** `api-docs`
**Phụ thuộc:** —
**Trạng thái:** 🟢 Done

## Bối cảnh cho agent

Trước khi code Community Chat, đồng bộ OpenAPI hiện có với thiết kế generic đã duyệt. API source là `api-docs/src/openapi.yaml` và các YAML được tham chiếu; không sửa bundle bằng tay. Đọc issue này, [P7-D01](../discovery/decisions.md), [Community design §3–4, §6](../../phase-6/discovery/community-service-design.md), `pm/phase-6/decisions.md` (D75), và `api-docs/package.json`.

Các chỗ đã thấy cần rà soát: response detail conversation còn ví dụ `type/roomId/contractId`; message list example còn `senderId` và thiếu sequence; mô tả `CONVERSATION_ARCHIVED` không khớp quy tắc contract kết thúc vẫn chat; rà lại create direct/group, membership, role, message và mark-read để các request/response/examples khớp thiết kế v1. Đây là sửa tài liệu theo quyết định có sẵn, không mở thêm business rule.

## Phạm vi

- Rà các path `api-docs/src/paths/chat/*.yaml`, schema và request/response DTO được các path tham chiếu.
- Giữ route đã duyệt: `/conversations`, `/conversations/{conversationId}`, `/conversations/{conversationId}/members`, `/messages?conversationId=...`, `POST /messages`, `POST /messages/mark-read`.
- Cập nhật ví dụ cũ để dùng `kind`, `contextType/contextId`, `senderUserId/senderType`, `sequence`, `clientMessageId` và fields thực có trong schema.
- Không đổi API đã duyệt nếu không có mâu thuẫn được giải quyết bằng decision mới.

## Điều đã chốt áp dụng

- Generic direct/group; direct duy nhất cho cặp user chuẩn hóa; group người tạo là admin.
- Tin có sequence; retry gửi dùng `clientMessageId`; mark-read dùng `lastReadSequence`.
- Membership bị thu hồi chuyển read-only; không tự đóng chat khi contract kết thúc.
- Không edit/delete message, mention, Issue panel hoặc `@issue`.

## Acceptance

- [ ] Các path/schema/examples của Chat không còn field domain cũ (`roomId`, `contractId`, `type: room`) khi response là conversation generic.
- [ ] Message list/send examples phản ánh sender, type, sequence và idempotency fields của schema.
- [ ] Status/error descriptions không nói conversation tự archived khi contract kết thúc.
- [ ] Không thêm endpoint/field/role/business rule mới ngoài thiết kế đã duyệt.
- [ ] `npm run lint` và `npm run bundle` trong `api-docs` chạy thành công; cập nhật `reference/rentify.json` bằng script bundle.

## Không làm

- Không triển khai Community code, Apidog sync hoặc event publisher.
- Nếu phát hiện hai quyết định đã duyệt mâu thuẫn nhau, dừng phần đó và ghi blocker; không tự chọn phương án.
