# Đề xuất thiết kế Community Service: Chat và Notification

> **Trạng thái:** Bản nháp để chốt phạm vi và thiết kế; chưa phải đặc tả được duyệt để code.  
> **Phạm vi lịch:** Độc lập, chưa gán iteration. Phase 6 hiện xếp Community/Chat/Notification là Stretch.  
> **Nguyên tắc:** Xác nhận ERD → business logic → API trước khi mở task triển khai.

## 1. Mục tiêu

Thiết kế một `community-service` hỗ trợ hội thoại generic, thông báo nghiệp vụ và gửi push cho web/mobile. Tài liệu này tách rõ message chat khỏi notification inbox:

- **Chat history** lưu các message để thành viên mở lại hội thoại và tải tiếp sau khi offline.
- **Notification inbox** chỉ lưu thông báo nghiệp vụ, ví dụ invoice hoặc issue; không lưu message chat.
- Sự kiện chat vẫn có thể đẩy realtime qua Socket.io hoặc FCM nhưng không tạo bản ghi trong notification inbox.
- Email forgot/reset password tiếp tục thuộc Identity Service.

## 2. Phạm vi đã chốt

| Hạng mục | Trạng thái/phạm vi |
|---|---|
| Chat theo phòng/hợp đồng | Làm trước; mỗi hợp đồng có một hội thoại riêng để lịch sử không trộn giữa các kỳ thuê. |
| Chat trực tiếp giữa hai người | Hỗ trợ. API hiện tại mô tả accept MatchRequest sẽ tạo hoặc resolve direct conversation; điều kiện này cần đối chiếu ở bước business logic. |
| Chat chung tòa nhà | Có trong hướng mở rộng generic nhưng triển khai sau chat phòng/direct. |
| Chat history | Lưu bền vững trong Community DB. |
| Business notification history | Lưu inbox cho các event nghiệp vụ đã duyệt như invoice/issue; không ghi message chat vào inbox. |
| Kênh realtime/push | Socket.io cho client đang mở; FCM cho mobile khi nền/offline. Web push qua FCM chưa nằm trong phạm vi đã chốt. |
| PushDevice | Chuyển ownership từ Identity sang Community. Identity vẫn xác thực JWT và sở hữu email reset password. |
| Bot reminder | Hiển thị như participant chat; landlord chọn và bấm gửi. Không gửi tự động theo cron. |

Không đưa `@issue`, Issue panel hoặc mention vào phạm vi triển khai.

## 3. ERD đề xuất — cần review và xác nhận

Conversation dùng `contextType + contextId` để thêm loại context mà không phải thêm một cột FK nullable mới cho từng loại. Vì Room/Contract/Building thuộc service/database khác, context ID được xem là tham chiếu ngoài service; Community phải xác thực context/quyền qua integration đã thống nhất, không truy cập DB của service khác.

| Entity | Trách nhiệm và dữ liệu chính trong bản nháp | Quan hệ/ràng buộc cần xác nhận |
|---|---|---|
| `Conversation` | ID, `contextType`, `contextId`, title tùy chọn, timestamps. Context phòng hiện ánh xạ theo `contract`; building có thể thêm sau. Direct conversation dùng participant pair thay cho context nghiệp vụ. | Unique một conversation cho mỗi contract context. Cách bảo đảm một direct conversation duy nhất cho một cặp user cần quyết định ở ERD. |
| `ConversationMember` | Conversation, participant, joined/left time và read cursor. | User participant và bot participant cần biểu diễn thế nào; member rời nhóm còn đọc history theo quy tắc hiện tại. |
| `Message` | Conversation, sender, loại (`text`, `image`, `file`, `bot`), content/media reference, thời gian tạo. | Sender phải đại diện được user hoặc bot; message chỉ ghi sau khi kiểm tra quyền gửi. |
| `Notification` | Recipient, business event/type, event reference hoặc deduplication key, payload/deep link, `readAt`, thời gian tạo. | Chỉ business notifications; chốt unique/dedup rule để RabbitMQ redelivery không sinh inbox item trùng. |
| `NotificationPreference` | Recipient, nhóm sự kiện và trạng thái bật/tắt. | Chốt preference điều khiển lưu inbox, FCM hay cả hai; đề xuất luôn lưu inbox khi event nghiệp vụ đủ điều kiện, preference chỉ điều khiển delivery. |
| `PushDevice` | User, token, platform, `lastSeenAt`. | Token duy nhất; user chỉ đăng ký/thu hồi thiết bị của mình. Chuyển dữ liệu token trước cutover nếu môi trường đã có dữ liệu. |

### Quan hệ khái niệm

```text
Conversation 1 ─── * ConversationMember
Conversation 1 ─── * Message
User          1 ─── * ConversationMember (participant=user)
Bot           1 ─── * ConversationMember (participant=system/bot)
User          1 ─── * Notification (business events only)
User          1 ─── * PushDevice
```

Đây là quan hệ ở mức thiết kế, chưa quyết định khóa/cột cuối cùng. ERD phải chốt cách biểu diễn bot participant và sender trước khi đóng API.

## 4. Business logic cần xác nhận

| Luồng | Quy tắc đã có hoặc đề xuất | Cần chốt trước API |
|---|---|---|
| Resolve chat phòng | Một chat theo từng hợp đồng; landlord và tenant/member hợp đồng được tham gia. | Thành viên hợp đồng mới được thêm tự động lúc nào; sau checkout được gửi tin mới hay chỉ đọc history? Tài liệu hiện nói giữ history, nhưng quyền sau checkout cần thống nhất. |
| Direct chat | API spec hiện ghi accept MatchRequest tạo/resolves direct chat. | Có cho phép nhắn người lạ khi chưa accept match không? Có một chat duy nhất mỗi cặp hay mỗi match request? |
| Chat tòa nhà | Dùng `contextType=building` ở giai đoạn sau. | Xác định membership/role trước khi triển khai giai đoạn này. |
| Gửi message | Chỉ thành viên hiện hành được gửi; message được lưu rồi mới phát Socket.io. | Quy định file loại/kích thước dựa trên Media contract hiện tại; xử lý gửi trùng/retry. |
| Đọc message | Lưu read cursor theo member; history tải cursor khi reconnect. | Quy tắc tăng/giảm unread khi member rời hoặc được thêm lại. |
| Business notification | Event invoice/issue và các nhóm đã duyệt tạo inbox item cho recipient được server xác định. | Chốt event → recipient → loại notification → deep link; không lấy recipient tùy ý từ client. |
| Chat delivery | Tin chat được phát realtime; FCM mobile khi app nền/offline, không tạo notification inbox item. | Chốt có lưu trạng thái delivery push riêng hay chỉ log vận hành. |
| Bot reminder | Landlord chọn reminder/context rồi bấm gửi; bot tạo message/card trong conversation. | Chốt các loại reminder, nội dung/template, context hợp lệ và quyền landlord; không có cron auto-send. |
| PushDevice | Token thuộc Community; API yêu cầu JWT và suy ra owner từ authenticated user. | Chốt route Gateway và quy trình token migration/cutover. |

## 5. API và event contract — thiết kế sau khi chốt ERD/rules

Rà soát API hiện có trong `api-docs` trước khi sửa. API dự kiến cần bao phủ:

- Resolve/list/detail conversation theo context; message list cursor, send, mark-read.
- Notification inbox cursor, unread filter, mark-one/all và preferences cho business notifications.
- PushDevice register/update/revoke dưới ownership của Community.
- Socket.io auth, join/leave conversation, new-message event, unread update và notification business event.
- FCM payload cho Android, deep link và token invalidation.
- Action landlord gửi bot reminder.

Trước khi freeze contract cần có bảng event rõ ràng:

| Event nguồn | Recipient rule | Inbox item? | Socket/FCM? | Trạng thái |
|---|---|---|---|---|
| Invoice | Chưa chốt theo actor/contract | Có | Có theo preference | Cần xác nhận |
| Issue | Chưa chốt theo owner/participant | Có | Có theo preference | Cần xác nhận |
| Chat message | Thành viên hội thoại trừ sender | Không | Socket; FCM Android khi phù hợp | Quy tắc delivery cần xác nhận |
| Bot reminder | Thành viên hội thoại theo quyền | Không mặc định tạo business inbox item | Socket/FCM theo chat delivery | Landlord phải bấm gửi |

Tenancy hiện có outbox cho một số event building/room/contract; event invoice/OCR/issue cần được đối chiếu với code và contract thực tế. Chỉ consumer event đã được thống nhất mới được đưa vào API/ERD chính thức.

## 6. Các cổng review trước khi code

| Gate | Deliverable | Điều kiện để qua gate |
|---|---|---|
| **A — ERD** | ERD v1, ownership theo service, index/uniqueness và bot participant model | Chốt context identity, direct uniqueness, member lifecycle và inbox schema. |
| **B — Business logic** | Ma trận role/permission, use case và event-recipient-delivery matrix | Chốt post-checkout access, direct chat eligibility, preference, push và bot manual send. |
| **C — API** | OpenAPI/Apidog, Socket event contract và deep link mapping | Request/response, quyền, lỗi, pagination và event payload khớp ERD/rules. |
| **D — Implementation backlog** | Epic/task tách backend, Gateway, web, Android và migration | Chỉ tạo sau khi A–C được xác nhận; có acceptance criteria và dependency cho từng task. |

Không bắt đầu scaffold/migration/API implementation trước khi Gate A–C được duyệt. Sau khi duyệt, triển khai theo dependency: service/PushDevice → chat core → Socket/client chat → business inbox/FCM → bot manual reminder → building chat.

## 7. Kiểm thử và tiêu chí nghiệm thu thiết kế

- ERD biểu diễn được contract chat, direct chat và context building tương lai mà không thêm cột riêng cho từng loại context.
- Message chat history và business notification history tách riêng; message chat không sinh inbox item.
- Quy tắc quyền bao phủ member hiện hành, member đã rời và người không thuộc hội thoại.
- Event redelivery không tạo notification trùng; push lỗi không làm mất business inbox.
- Socket reconnect khôi phục bằng API cursor; FCM chỉ dùng cho delivery mobile theo rule đã duyệt.
- Bot không gửi nếu landlord chưa chủ động trigger; không có lịch tự động gửi.
- `@issue`, Issue panel và mention không xuất hiện trong ERD/API/tasks của phạm vi này.

## 8. Tài liệu tham chiếu

- `pm/phase-0/discovery/decisions.md` — D24′ Property Chat.
- `pm/phase-1/discovery/database-design.md` — Conversation, ConversationMember, Message, Notification, NotificationPreference, PushDevice hiện tại.
- `pm/phase-2/discovery/api-spec.md` — API Conversation, Message, Notification, PushDevice và flow accept MatchRequest.
- `boilerplate/docs/architecture.md` và `boilerplate/docs/transactional-outbox-design.md` — kiến trúc service và event delivery.
