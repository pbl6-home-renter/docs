# Quyết định cho Web Chat v2

> **Trạng thái:** Chốt ngày 12/11/2026 theo kế hoạch chung Chat v2 (Claude làm backend và contract, Codex làm `fe/` và kiểm tra tích hợp). Tài liệu này **bổ sung** cho [Web Chat v1](web-chat-v1-decisions.md); không sửa lịch sử v1. Ở v1, typing và trạng thái đã xem từng tin nằm ngoài phạm vi; v2 đưa hai tính năng này vào.
> **Contract:** `api-docs/src/paths/chat/messages*.yaml` và `api-docs/docs/community-socket-v1.md`. Khi tài liệu này và API docs khác nhau ở chi tiết kỹ thuật, API docs là contract hiện hành.

## 1. Phạm vi v2

| Tính năng | Quyết định |
|---|---|
| Đã xem | Người gửi thấy ai đã xem tin của mình. Chat 1:1 hiện trạng thái đã xem; nhóm hiện số người đã xem và mở được danh sách tên. Trạng thái luôn hiển thị, không có tùy chọn tắt. |
| Đang nhập | Hiện “đang nhập” của thành viên khác trong hội thoại đang mở. Không lưu DB, không gửi nội dung đang gõ. |
| Tìm nội dung tin | Tìm trong một hội thoại theo nội dung tin chữ/bot và caption ảnh; không phân biệt hoa/thường hoặc dấu tiếng Việt. Mở được tin tìm thấy và quay về tin mới nhất. |
| Trả lời trích dẫn | Trả lời một tin chữ/ảnh/bot trong cùng hội thoại; tin trả lời hiện khối trích dẫn. Tin gốc về sau không còn khả dụng thì hiện placeholder. |
| Sửa FE | Hiện caption ảnh trong bubble, mốc ngày, gom bubble, màu hội thoại đang mở, khung tải ổn định, dán/kéo ảnh. |
| Không làm | Trạng thái “Đã nhận” (chưa có xác nhận tin đã tới thiết bị). Reaction, thu hồi, ghim, tắt tiếng, chia sẻ file thuộc đợt sau. |

## 2. Đã xem

- Giữ `conversation:read-updated` (tới user room của người đọc) như v1.
- Sau khi mark-read commit **và cursor thực sự tăng**, server phát thêm `conversation:member-read` tới room hội thoại: `{ conversationId, userId, lastReadSequence }` (`lastReadSequence` là chuỗi thập phân).
- Chỉ thành viên `active` được tính: mark-read của thành viên `read_only` không phát `conversation:member-read`.
- FE tính trạng thái từ `ConversationDetail.members[].lastReadSequence` (đã có), cập nhật theo event và chỉ nhận cursor lớn hơn cursor đang giữ. Khi reconnect, FE tải lại detail vì event có thể bị mất.

## 3. Đang nhập

- Client gửi `conversation:typing` với `{ conversationId, isTyping }`; server phát cùng tên event với `{ conversationId, userId, isTyping }` cho **các socket khác** trong room (tab khác của chính user vẫn nhận; FE bỏ qua `userId` của mình).
- Server chỉ chuyển tiếp khi socket đã join room và người gửi vẫn là thành viên `active` (kiểm tra lại DB mỗi lần). Thành viên bị loại đã bị đưa khỏi room nên không gửi/nhận được.
- FE gửi tín hiệu bắt đầu tối đa mỗi 2 giây, tự ẩn sau 4 giây nếu không nhận tín hiệu mới, và dọn trạng thái khi đổi hội thoại/reconnect.

## 4. Tìm tin và mở tin tìm được

- `GET /messages/search?conversationId&q&cursor&pageSize`: `q` sau trim (chuẩn hóa NFC) dài 2–100 ký tự. Kết quả mới nhất trước, phân trang cursor như lịch sử.
- Chỉ tìm tin `text`, `bot` và caption của `image`; bỏ tin `system` và tin đã xóa. Quyền xem giống `GET /messages`: thành viên `read_only` chỉ thấy tới `leftSequence`.
- `contentPreview` là nội dung (hoặc caption) cắt tối đa 120 ký tự (117 + `...`).
- `GET /messages` nhận thêm `maxSequence` (tùy chọn): trả trang tin có `sequence <= maxSequence`, rồi phân trang tin cũ hơn bằng cursor hiện có; không vượt `leftSequence` của thành viên `read_only`.

## 5. Trả lời trích dẫn

- `POST /messages` nhận `replyToMessageId` (tùy chọn). Tin gốc phải cùng hội thoại, chưa xóa, thuộc loại `text`/`image`/`bot`; sai thì trả `422 MESSAGE_REPLY_TARGET_INVALID` (không phân biệt “không tồn tại” với “khác hội thoại” để không lộ dữ liệu).
- Người gửi luôn là thành viên `active` nên xem được mọi tin trong hội thoại; tin gốc luôn có `sequence` nhỏ hơn tin trả lời nên thành viên `read_only` xem được tin trả lời thì cũng xem được tin gốc.
- Response gửi tin, lịch sử và `message:created` có `replyTo: { id, senderName, type, contentPreview, isUnavailable } | null`. Khi tin gốc không còn khả dụng: giữ `id`, `isUnavailable=true`, còn `senderName`, `type`, `contentPreview` là `null` để không lộ nội dung đã xóa.
- `contentPreview` của ảnh là caption (cắt 120 ký tự) hoặc `""` nếu không có caption; FE tự gắn nhãn theo `type` bằng i18n.
- Retry cùng `clientMessageId` trả đúng tin đã lưu (kèm `replyTo` tính lại theo trạng thái hiện tại của tin gốc), không kiểm tra lại tin gốc và không tạo bản sao.

## 6. Tương thích

Mọi trường request mới đều tùy chọn; client cũ (Android, FE trước v2) tiếp tục hoạt động và bỏ qua field/event mới.
