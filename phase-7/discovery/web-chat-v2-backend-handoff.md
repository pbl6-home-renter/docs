# Bàn giao backend Chat v2 cho FE

> Ngày 12/11/2026. Quyết định sản phẩm: [web-chat-v2-decisions.md](web-chat-v2-decisions.md) (P7-D83). Contract: `api-docs/src/paths/chat/messages*.yaml`, `api-docs/docs/community-socket-v1.md`.

## Nhánh

| Repo | Nhánh | Nội dung |
|---|---|---|
| `community-service` | `feature/chat-v2-backend` | Đã xem, đang nhập, tìm tin, `maxSequence`, trả lời trích dẫn, migration, unit test |
| `api-docs` | `feature/chat-v2-contract` | OpenAPI + tài liệu Socket, đã bundle `reference/rentify.json` |
| `pm` | `docs/chat-v2-decisions` | Quyết định P7-D83 và tài liệu này |

Chưa push, chưa mở PR.

## REST

| Endpoint | Thay đổi |
|---|---|
| `GET /api/v1/messages` | Thêm query `maxSequence` (tùy chọn, `^[1-9]\d{0,17}$`). Mỗi item có thêm `replyTo`. |
| `GET /api/v1/messages/search` | **Mới.** `conversationId`, `q` (2–100 ký tự sau trim), `cursor`, `pageSize` (mặc định 30). Mã thành công `MESSAGES_SEARCHED`. |
| `POST /api/v1/messages` | Body thêm `replyToMessageId` (tùy chọn). Response thêm `replyTo`. Lỗi mới `422 MESSAGE_REPLY_TARGET_INVALID`. |
| `POST /api/v1/messages/mark-read` | Không đổi contract; phát thêm `conversation:member-read`. |

`ConversationDetail.members[].lastReadSequence` đã có sẵn, dùng để khởi tạo trạng thái đã xem.

### JSON mẫu

`GET /messages/search?conversationId=…&q=voi xit`

```json
{
  "statusCode": 200,
  "code": "MESSAGES_SEARCHED",
  "data": [
    {
      "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "sequence": "40",
      "senderName": "Trần Thị B",
      "type": "image",
      "contentPreview": "Vòi xịt nhà tắm bị rỉ",
      "createdAt": "2026-09-23T11:20:00.000Z"
    }
  ],
  "pagination": { "type": "cursor", "pageSize": 30, "nextCursor": null, "hasNextPage": false }
}
```

Mở tin tìm được: `GET /messages?conversationId=…&maxSequence=40` → trang đầu kết thúc ở tin `sequence=40` (tin đích là phần tử đầu tiên vì sắp `sequence` giảm dần); trang cũ hơn dùng `nextCursor` như thường. Không có API tải tin **mới hơn** đích; nút “về tin mới nhất” gọi lại `GET /messages` không có `maxSequence`.

`POST /messages`

```json
{
  "conversationId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "clientMessageId": "a95a1d13-f91c-4c71-9c61-24b498d0fd0e",
  "type": "text",
  "content": "Dạ thợ mấy giờ qua kiểm được ạ",
  "mediaId": null,
  "replyToMessageId": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
}
```

`replyTo` (trong response gửi tin, lịch sử và `message:created`):

```json
{ "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7", "senderName": "Trần Thị B", "type": "image", "contentPreview": "Vòi xịt nhà tắm bị rỉ", "isUnavailable": false }
```

Tin gốc đã xóa:

```json
{ "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7", "senderName": null, "type": null, "contentPreview": null, "isUnavailable": true }
```

## Socket

| Hướng | Event | Payload |
|---|---|---|
| client → server | `conversation:typing` | `{ conversationId, isTyping }`; ack tùy chọn `{ ok: true, code: "SENT", conversationId }` hoặc `{ ok: false, code: "UNAUTHORIZED" \| "INVALID_CONVERSATION_ID" \| "INVALID_PAYLOAD" \| "FORBIDDEN" }` |
| server → room (trừ socket gửi) | `conversation:typing` | `{ conversationId, userId, isTyping }` |
| server → room | `conversation:member-read` | `{ conversationId, userId, lastReadSequence }` |
| server → room | `message:created` | Như cũ + `replyTo` (`null` nếu không trả lời; system message luôn `null`) |

## Điểm FE cần biết (khác hoặc chi tiết hơn bảng kế hoạch)

1. `replyTo` khi tin gốc không khả dụng trả `null` cho `senderName`/`type`/`contentPreview` (không chỉ bật `isUnavailable`) để không lộ nội dung đã xóa.
2. `contentPreview` của ảnh là **caption** (cắt 120 ký tự), ảnh không caption là `""`; FE tự gắn nhãn “Ảnh” theo `type` bằng i18n. Khác `chat:message-received` (vẫn là `Đã gửi ảnh` như v1).
3. `conversation:typing` chỉ chuyển tiếp khi socket **đã join** room; FE cần join trước. Tab khác của chính user cũng nhận event, nên bỏ qua khi `userId` là mình. Server không phát `isTyping:false` khi socket ngắt — dựa vào timeout 4 giây.
4. `conversation:member-read` chỉ phát cho member `active`; mark-read không tăng cursor thì không phát.
5. Retry `POST /messages` cùng `clientMessageId` trả đúng tin đã lưu; `replyTo` được tính lại theo trạng thái hiện tại của tin gốc.

## Migration

`src/database/migrations/1794496738151-AddMessageReplyTo.ts` (sinh bằng `npm run migration:generate`): thêm cột `messages.reply_to_message_id uuid NULL` và FK `FK_messages_reply_to_message_id` → `messages(id)` `ON DELETE RESTRICT`. **Đã chạy** `migration:run` trên DB dev dùng chung ngày 12/11/2026 (`migration:show` báo 7/7 đã áp dụng). Service nào chạy code cũ vẫn tương thích vì cột mới cho phép `NULL`.

## Kết quả kiểm tra

- `community-service`: `npm run build` sạch; `oxlint src/ test/` sạch; Prettier sạch trên các file đã sửa; `npx jest` 19 suite / 79 test pass (thêm test cho mark-read → member-read, `maxSequence` + giới hạn read-only, search quyền, reply hợp lệ/khác hội thoại/system/đã xóa/không tồn tại, retry idempotent, typing gateway: chưa join, bị loại, payload sai). Ba lệnh grep dependency rule không có kết quả mới (một dòng có sẵn ở `conversation-create.command.handler.ts`).
- SQL tìm kiếm được kiểm tra bằng cách sinh câu lệnh TypeORM (không kết nối DB): gấp dấu bằng `TRANSLATE` như tìm hội thoại, `%`/`_` được escape.
- `api-docs`: `npm run lint` hợp lệ (14 warning có sẵn, không thêm), `npm run bundle` đã chạy. `GET /messages/search` để `x-apidog-status: designing` cho tới khi thử tay trên service.
- **Chưa kiểm tra end-to-end** với DB/Socket thật (migration đã chạy, nhưng chưa thử tay API/Socket trên service). Việc tích hợp hai tài khoản, nhóm ba người, reconnect, người bị loại thuộc phần Codex.

## Giới hạn đã biết

- Tìm kiếm dùng `LIKE` trên nội dung đã gấp dấu, quét tin của một hội thoại; đủ cho quy mô dự án, chưa có index full-text.
- Gấp dấu chỉ áp dụng cho ký tự dựng sẵn (NFC). Từ khóa được chuẩn hóa NFC; nội dung lưu ở dạng NFD (hiếm) sẽ không khớp.
