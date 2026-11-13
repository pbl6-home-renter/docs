# Đề xuất thiết kế Community Service: Chat và Notification

> **Làm rõ email (2026-11-07):** Identity vẫn sở hữu nghiệp vụ forgot/reset password và tạo nội dung email đã render. Identity publish `email.send_requested` qua transactional outbox; Community tiêu thụ queue và gửi bằng SMTP với `From` lấy từ cấu hình Community. Community lưu metadata/trạng thái `EmailDelivery` trong 90 ngày, không lưu body, không retry cùng request ID khi SMTP lỗi. Email nghiệp vụ Invoice chưa nằm trong phạm vi hiện tại.

> **Trạng thái:** ERD v1 và API/event contract v1 đã được duyệt; implementation được xếp ở Phase 7.
> **Phạm vi lịch:** Bắt đầu It5 (02/11–08/11) song song với Phase 6; xem [Phase 7 plan](../../phase-7/README.md).
> **Cách làm:** Chốt phạm vi → ERD → business logic → API/event contract → tạo backlog → code.

## 1. Mục tiêu và cách hiểu

`community-service` cung cấp chat generic cho các ngữ cảnh khác nhau và chức năng nhận/gửi notification cho web/mobile.

- **Chat message** được lưu để mở lại xem lịch sử và tải tiếp sau khi offline.
- **Notification inbox** chỉ lưu thông báo nghiệp vụ như invoice/issue; không lưu message chat.
- Tin nhắn chat vẫn có thể được đẩy realtime qua Socket.io và gửi push FCM cho mobile, nhưng không tạo bản ghi trong business notification inbox.
- Forgot/reset password email tiếp tục do Identity Service gửi.
- Notification Service không tự quyết định ai là người nhận notification nghiệp vụ. Service sở hữu nghiệp vụ gửi event kèm danh sách recipient; Community lưu và phân phối. Với chat, Community tự xác định các thành viên còn trong conversation.

## 2. Phạm vi triển khai

| Phần | Phạm vi |
|---|---|
| Chat theo hợp đồng | Một conversation cho mỗi hợp đồng; người tham gia được đồng bộ theo ContractMember. Kick khỏi chat chuyển thành viên sang read-only; kết thúc hợp đồng không đóng chat. |
| Chat tự do | Chat 1:1 hoặc nhóm giữa người dùng; không cần gắn với phòng/tòa/hợp đồng. Admin nhóm có quyền thêm, sửa vai trò và xóa thành viên. |
| Chat theo tòa nhà | Một conversation cho tòa, tạo khi tòa được tạo; chủ tòa là admin, người có contract trong tòa được thêm vào. Checkout không tự kick; admin kick thì read-only. |
| Chat history | Lưu message trong Community DB; text/ảnh, một ảnh mỗi message. Không sửa/xóa message ở bản đầu. |
| Business notification | Lưu inbox và phân phối các event nghiệp vụ như invoice/issue theo recipient do service nguồn chỉ định. |
| Realtime và push | Socket.io cho client đang mở; FCM cho Android khi app nền/offline. |
| PushDevice | Thuộc Community Service; Identity vẫn xác thực user/JWT và gửi email reset password. |
| Bot reminder | Bot xuất hiện như participant; landlord chủ động chọn và bấm gửi. Không tự động gửi theo cron. |

Không triển khai chat `@issue`, Issue panel, mention hoặc MessageMention trong phạm vi này.

## 3. ERD đề xuất để review

Đề xuất một lõi chat dùng chung cho mọi loại hội thoại. Lõi chỉ quản lý conversation, thành viên, vai trò, message và read cursor; không chứa nhánh logic riêng cho Room, Building hay Contract. Conversation có thể có một tham chiếu context tùy chọn (`contextType + contextId`), dùng để tìm conversation tương ứng; đây không phải FK hoặc phụ thuộc trực tiếp vào database domain khác. Quy tắc tạo chat theo contract/tòa và đồng bộ thành viên nằm trong adapter xử lý event của service nguồn. Chat tự do được tạo trực tiếp qua API của Community.

| Entity | Vai trò | Quan hệ và quy tắc đề xuất |
|---|---|---|
| `Conversation` | Hội thoại generic, người tạo, tên/avatar tùy chọn, loại hiển thị và context tham chiếu tùy chọn. | Lõi không hardcode unique theo domain. Integration áp dụng khóa idempotent cho context (`contextType + contextId`); chat tự do có thể là direct hoặc group. |
| `ConversationMember` | User hoặc bot tham gia conversation; lưu vai trò, trạng thái, thời điểm vào/rời và read cursor. | Vai trò lõi của user: `admin/member`; người tạo nhóm là admin ban đầu. Admin có thể thêm thành viên, đổi vai trò hoặc loại thành viên qua cùng application service. Event domain cũng dùng application service này để đồng bộ thành viên. |
| `Message` | Lưu sender, loại tin, nội dung/media và thời điểm gửi. | Gắn với một conversation; sender có thể là user hoặc bot. Lưu message trước khi phát Socket.io/FCM. |
| `Notification` | Lưu business notification theo từng recipient, gồm loại, nội dung/payload điều hướng và trạng thái đọc. | Community nhận recipient list từ event; cùng một event được RabbitMQ gửi lại cũng không tạo item trùng. Không lưu chat message. |
| `NotificationPreference` | Lưu lựa chọn nhận delivery theo từng nhóm `chat`/`invoice`/`issue`. | Tắt nhóm thì không gửi push thiết bị và không hiện toast Web; business notification vẫn lưu/hiện trong inbox và Socket vẫn phát để đồng bộ. Recipient vẫn do service nguồn chỉ định. Quy tắc này được cập nhật bởi P7-D82. |
| `PushDevice` | Token FCM, platform và thời điểm hoạt động cuối của thiết bị. | User có thể có nhiều thiết bị; chỉ user hiện tại được đăng ký/thu hồi thiết bị của mình. |

### Cách biểu diễn context

| Trường hợp | Context tham chiếu | Cách tạo và quản lý thành viên |
|---|---|---|
| Chat theo hợp đồng | `contract` + Contract ID | Tenancy phát event; adapter tìm conversation theo context và đồng bộ ContractMember. |
| Chat tòa nhà | `building` + Building ID | Event tạo tòa khởi tạo conversation; adapter đồng bộ thành viên có contract trong tòa. |
| Chat tự do 1:1/nhóm | Không có | Người tạo nhóm là admin ban đầu; admin quản lý thành viên qua API chat. |

Tên cột, enum, index và biểu diễn bot participant sẽ được chốt ở Gate ERD; bảng trên là mô hình đề xuất, chưa phải migration.

### ERD v1 đề xuất — cấu trúc dữ liệu

Đây là thiết kế để review, không phải migration. ID user, contract và building là ID tham chiếu ngoài Community; không tạo foreign key sang database service khác.

| Entity | Field chính dự kiến | Ràng buộc/ghi chú |
|---|---|---|
| `Conversation` | `id`, `kind` (`direct`/`group`), `contextType?`, `contextId?`, `directPairKey?`, `title?`, `avatarMediaId?`, `createdByUserId?`, timestamps | Context là cặp tùy chọn; unique `(contextType, contextId)` cho chat theo resource. Direct dùng unique `directPairKey` từ cặp user đã chuẩn hóa. Nhóm tự do không có context. |
| `ConversationMember` | `id`, `conversationId`, `participantType` (`user`/`system`), `userId?`, `displayName`, `systemParticipantKey?`, `role` (`admin`/`member`), `status` (`active`/`read_only`), `joinedAt`, `leftAt?`, `leftSequence?`, `lastReadSequence` | `displayName` lấy từ Identity lúc thêm/kích hoạt member. Giữ membership row khi rời; chỉ đọc message tới `leftSequence`. Thêm lại thì kích hoạt row cũ, cập nhật displayName và đặt read cursor tới tin mới nhất hiện tại. |
| `Message` | `id`, `conversationId`, `sequence`, `senderMemberId`, `senderNameSnapshot`, `clientMessageId?`, `messageType` (`text`/`image`/`system`/`bot`), `text?`, `mediaId?`, `payload?`, `createdAt` | `senderNameSnapshot` copy từ ConversationMember khi gửi, bất biến theo thời gian. Unique `(conversationId, sequence)` và `(senderMemberId, clientMessageId)` khi client ID có giá trị. Một ảnh tối đa mỗi message; chỉ tham chiếu Media ID. Không sửa/xóa ở bản đầu. System/bot message dùng cùng bảng. |
| `Notification` | `id`, `sourceService`, `eventId`, `recipientUserId`, `type`, `title`, `body`, `deepLink?`, `data`, `readAt?`, `createdAt` | Một row cho mỗi event/recipient; unique `(sourceService, eventId, recipientUserId)`. Lưu snapshot, không FK recipient tới Identity. |
| `NotificationPreference` | `id`, `userId`, `category` (`chat`/`invoice`/`issue`), `pushEnabled` | Unique `(userId, category)`. API field `pushEnabled` điều khiển push thiết bị và toast Web; không ẩn/xóa inbox. Quy tắc hiện hành theo P7-D82. |
| `PushDevice` | `id`, `userId`, `platform`, `token`, `lastSeenAt`, `revokedAt?` | Một user có nhiều device; token không được gắn đồng thời với nhiều user. Đăng ký/thu hồi theo user từ JWT. |

`directPairKey` và `sequence` là tên logic để review; tên cột, kiểu dữ liệu, partial index, cách lưu payload và chính sách xóa sẽ được chốt trước migration.

## 4. Business logic đề xuất

Các quy tắc trong mục này được đưa ra để chốt lần lượt. Trạng thái `Đã chốt` phản ánh quyết định của người dùng; `Cần xác nhận` là đề xuất chưa được xem là yêu cầu cuối cùng.

| Mã | Quyết định | Đề xuất hiện tại | Trạng thái |
|---|---|---|---|
| BL-01 | Ai được tạo chat tự do 1:1 hoặc nhóm? | Mọi user đã đăng nhập có thể bắt đầu chat 1:1 hoặc tạo nhóm; người tạo nhóm là admin ban đầu. | Đã chốt |
| BL-02 | Quyền của admin nhóm | Thêm/xóa thành viên, đổi vai trò, sửa tên/ảnh nhóm và chỉ định thêm admin; thay đổi thành viên được ghi thành system message. | Đã chốt |
| BL-03 | Thành viên rời hoặc bị xóa khỏi chat tự do | Không gửi được tin mới; chỉ xem message tới lúc rời/bị xóa. Khi được thêm lại, xem toàn bộ history. | Đã chốt |
| BL-04 | Thành viên chat theo hợp đồng | ContractMember added/linked joins the contract chat; individual leave or checkout makes that member read-only. The conversation remains available for history within the member's `leftSequence` boundary (P9-D85). | Đã chốt |
| BL-05 | Thành viên chat tòa nhà | Tạo chat khi tạo tòa; chủ tòa là admin; người có contract trong tòa được thêm; checkout không tự xóa khỏi chat. | Đã chốt |
| BL-06 | Business notification | Service nguồn cung cấp recipient; Community lưu inbox và phân phối Socket/push theo preference. | Đã chốt |
| BL-07 | Chat và notification history | Lưu message chat trong lịch sử chat; chỉ notification nghiệp vụ được lưu trong inbox. | Đã chốt |
| BL-08 | Người mới được thêm vào nhóm xem lịch sử từ thời điểm nào? | Xem toàn bộ lịch sử của nhóm. | Đã chốt |
| BL-09 | Chat 1:1 giữa cùng một cặp user | Chỉ một conversation cho mỗi cặp; các lần mở sau dùng lại conversation hiện có. | Đã chốt |
| BL-10 | Admin cuối cùng rời nhóm hoặc bị xóa | Tự động chuyển quyền admin cho thành viên còn lại có thời điểm tham gia sớm nhất. | Đã chốt |
| BL-11 | Landlord kick ContractMember khỏi chat hợp đồng | Không gửi được tin mới; chỉ xem message tới lúc bị kick. Khi được thêm lại, xem toàn bộ history. | Đã chốt |
| BL-12 | Admin tòa kick thành viên khỏi chat building | Không gửi được tin mới; chỉ xem message tới lúc bị kick. Khi được thêm lại, xem toàn bộ history. | Đã chốt |
| BL-13 | Sửa/xóa message đã gửi | Bản đầu không hỗ trợ sửa/xóa; nội dung message giữ nguyên sau khi gửi. | Đã chốt |
| BL-14 | Loại nội dung message | Hỗ trợ văn bản và ảnh; chưa hỗ trợ các loại tệp khác. Ảnh dùng Media Service nếu phù hợp. | Đã chốt |
| BL-15 | Read state của chat | Số tin chưa đọc theo từng hội thoại và thao tác mark-read; không có dấu đã xem trên từng message. | Đã chốt |
| BL-16 | Notification inbox khi user tắt một nhóm | Notification vẫn được lưu và hiển thị trong inbox; preference tắt push delivery và toast Web theo P7-D82. | Đã chốt, cập nhật 07/11/2026 |
| BL-17 | Fan-out notification tới nhiều phiên/thiết bị | Lưu một inbox notification cho mỗi recipient/event; gửi cùng `notificationId` qua các phiên Socket đang kết nối và các PushDevice mobile đã đăng ký để client khử trùng lặp. | Đã chốt |
| BL-18 | Đồng bộ trạng thái đã đọc giữa các thiết bị | Trạng thái đọc thuộc inbox của user; mark-read trên thiết bị nào cũng đồng bộ sang các thiết bị khác. | Đã chốt |
| BL-19 | Mức cấu hình notification preference | User bật/tắt delivery push thiết bị và toast Web theo từng nhóm chat, invoice, issue; inbox vẫn lưu theo BL-16. | Đã chốt, cập nhật 07/11/2026 |
| BL-20 | Tắt push riêng cho từng conversation | Bản đầu chỉ có preference chung cho toàn bộ chat; chưa có mute riêng từng conversation. | Đã chốt |
| BL-21 | Các loại business notification tích hợp ban đầu | Invoice và issue; event type khác bổ sung sau khi có nhu cầu cụ thể. | Đã chốt |
| BL-22 | Thao tác với notification inbox | Chỉ hỗ trợ mark-read/mark-all-read; không cho user xóa notification ở bản đầu. | Đã chốt |
| BL-23 | Hiển thị lịch sử thay đổi nhóm | Hiện system message cho đổi tên/ảnh nhóm, thêm/xóa thành viên và đổi vai trò. | Đã chốt |

| Mã ERD | Quyết định dữ liệu | Mô hình đề xuất | Trạng thái |
|---|---|---|---|
| ERD-01 | Lưu user đã rời/bị kick khỏi chat | Giữ `ConversationMember`, đánh dấu read-only: được đọc history nhưng không gửi message mới. | Đã chốt |
| ERD-02 | Mở lại direct chat sau khi một bên đã rời | Dùng lại conversation theo cặp user và kích hoạt lại quyền gửi cho cả hai. | Đã chốt |
| ERD-03 | Lưu ảnh chat | Dùng Media Service/R2 hiện có; presign dùng `ownerType=conversation`, `ownerId=conversationId`, `purpose=chat_attachment`; client upload/download trực tiếp qua URL có thời hạn, Community lưu media ID, không lưu binary. | Đã chốt |
| ERD-04 | Biểu diễn bot participant | Bot là participant hệ thống trong ConversationMember, không tạo tài khoản đăng nhập; bot chỉ gửi khi landlord chủ động trigger. | Đã chốt |
| ERD-05 | Số ảnh trong một message | Mỗi message chứa tối đa một ảnh; nhiều ảnh được gửi thành nhiều message riêng. | Đã chốt |
| ERD-06 | Lưu system message và bot message | Lưu chung trong `Message` với `messageType` phân biệt text/image/system/bot; payload có cấu trúc theo loại. | Đã chốt |
| ERD-07 | Nội dung lưu trong notification inbox | Lưu snapshot type/title/body/deep link/data cùng recipient và source event ID; không cần gọi service nguồn để render inbox. | Đã chốt |
| ERD-08 | Chống tạo trùng direct conversation | Lưu cặp user ID đã chuẩn hóa theo thứ tự và đặt unique constraint cho direct conversation. | Đã chốt |
| ERD-09 | Chống tạo trùng contextual conversation | Unique constraint trên `contextType + contextId`; mỗi contract/building chỉ có một conversation. | Đã chốt |
| ERD-10 | Thêm lại thành viên từng rời/bị xóa khỏi nhóm | Kích hoạt lại membership cũ, giữ history và đặt read cursor tới message mới nhất khi được thêm lại. | Đã chốt |
| ERD-11 | Thứ tự message và read cursor | `Message.sequence` tăng dần trong mỗi conversation; membership lưu `lastReadSequence` để phân trang và tính unread ổn định. | Đã chốt |
| ERD-12 | Preference push chưa được user chỉnh | Mặc định bật cho chat/invoice/issue; chỉ gửi nếu user có thiết bị đăng ký và OS cho phép push. | Đã chốt |
| ERD-13 | Thành viên read-only xem được tin gửi sau khi rời không? | Chỉ đọc message tới `leftSequence`; khi được thêm lại thì xem toàn bộ history. | Đã chốt |

Các quy tắc business trong bảng trên đã được xác nhận. Những lựa chọn kỹ thuật ở ERD/API tiếp tục được đề xuất và review riêng trước khi code.

| Luồng | Quy tắc nghiệp vụ |
|---|---|
| Thêm member hợp đồng | Khi landlord thêm ContractMember, Tenancy phát event; adapter tìm chat theo contract và thêm user. Xử lý event lặp không tạo membership trùng. Thành viên mới xem được toàn bộ lịch sử. |
| Landlord kick member khỏi chat hợp đồng | Khi landlord chủ động loại ContractMember, adapter đánh dấu membership read-only và ghi `leftSequence`; người đó không gửi tin mới, chỉ đọc đến message cuối tại thời điểm bị kick. |
| Kết thúc hợp đồng | Checkout emits `contract_member.left` for remaining members. They remain in the contract conversation as read-only, cannot send, and can read only through `leftSequence` calculated from the event's `occurredAt`. Contract termination itself does not delete the conversation or create a leave event; see P9-D85. |
| Tạo chat hợp đồng | Tạo/resolution một conversation cho mỗi contract; hợp đồng mới trong cùng phòng có conversation và lịch sử riêng. |
| Chat tự do | Hỗ trợ direct 1:1 và nhóm, không gắn context domain. Người tạo là admin ban đầu; admin có thể thêm/xóa thành viên, đổi vai trò, sửa tên/ảnh nhóm và chỉ định thêm admin. Thay đổi thành viên được lưu thành system message để thành viên thấy lịch sử. Người bị xóa hoặc tự rời không gửi được tin mới nhưng vẫn xem lịch sử; người mới được thêm xem toàn bộ lịch sử hiện có. Nếu admin cuối cùng rời/bị xóa, quyền admin chuyển cho thành viên còn lại tham gia sớm nhất. Mỗi cặp user chỉ có một direct conversation, được mở lại khi cần; MatchRequest không bắt buộc. |
| Tạo tòa và chat tòa | Event tạo tòa khởi tạo conversation building. Chủ sở hữu tòa được gán vai trò quản trị chat; thành viên có ContractMember trong tòa được đồng bộ qua adapter. Kết thúc hợp đồng không tự xóa thành viên khỏi chat tòa; landlord/admin có thể chủ động kick. Người bị kick chỉ đọc tới message cuối tại thời điểm bị kick. Nếu service triển khai sau khi tòa đã tồn tại, cần bootstrap conversation một lần. |
| Message và history | Chỉ member active được gửi. Người rời/bị kick ở chat tự do/contract/building chỉ đọc message tới `leftSequence`; thành viên mới được thêm xem toàn bộ history. Message không sửa/xóa sau khi gửi trong bản đầu. Mỗi member có read cursor riêng; hiển thị số unread theo conversation và mark-read, không có read receipt trên từng message. |
| Chat realtime/offline | Phát message qua Socket.io cho client đang mở; Android nền/offline nhận FCM nếu bật thông báo chat. Khi reconnect, client tải message còn thiếu từ API. Không cần bảng lịch sử delivery riêng. |
| Bot reminder | Landlord chọn ngữ cảnh/nội dung reminder và xác nhận gửi; bot tạo message trong chat. Không có scheduler tự phát. |
| Business notification | Service nguồn xác định recipient và gửi event; Community không tra cứu hợp đồng để quyết định người nhận. Community lưu một notification cho mỗi recipient/event, sau đó fan-out cùng notification ID qua Socket tới các session đang kết nối và FCM tới các thiết bị đã đăng ký. Client khử trùng lặp theo notification ID; preference điều khiển FCM và toast Web theo P7-D82, không lọc inbox hay Socket sync. |

Các quy tắc trên là đề xuất dựa trên yêu cầu hiện có và thông lệ chat nhóm; cần được rà soát tại buổi chốt business logic trước khi đóng API.

## 5. Mẫu event notification cho service nguồn

Service nghiệp vụ chịu trách nhiệm xác định recipient. Event gửi sang Community chứa `eventId`, loại event, danh sách `recipientUserIds` và dữ liệu cần để tạo notification. Community không tự tìm thêm người nhận.

Ví dụ minh họa khi Tenancy phát hành invoice:

```json
{
  "eventId": "<uuid> unique per source event",
  "eventType": "invoice.issued",
  "sourceService": "tenancy-service",
  "recipientUserIds": ["<tenant-user-id>"],
  "notification": {
    "type": "invoice",
    "title": "Hóa đơn mới",
    "body": "Hóa đơn kỳ <period> đã được phát hành.",
    "data": {
      "invoiceId": "<invoice-id>",
      "deepLink": "/invoices/<invoice-id>"
    }
  }
}
```

`recipientUserIds` trong ví dụ do Tenancy chọn theo business rule của invoice. Community kiểm tra event/idempotency, lưu từng notification và gửi socket/FCM; nó không tự suy ra tenant từ contract. Service phát event khác, ví dụ issue owner, dùng cùng envelope nhưng tự cung cấp danh sách người nhận phù hợp.

## 6. API/event contract v1 — đã duyệt

ERD v1 và API/event contract v1 đã được duyệt. OpenAPI YAML chuẩn và bundle `api-docs/reference/rentify.json` đã cập nhật. Apidog đồng bộ sau khi thay đổi được merge theo quy trình repo; chưa triển khai service hoặc Gateway.

| Nhóm | Endpoint/event dự kiến | Mục đích và quyền chính |
|---|---|---|
| Conversation | `GET /conversations` | Liệt kê conversation của user hiện tại, phân trang offset (`pageNo`, `pageSize`); trả unread count và last message. |
| Conversation | `POST /conversations` | Tạo chat tự do 1:1/nhóm; direct tìm lại chat của cặp đã có, group tạo mới. |
| Conversation | `GET /conversations?contextType=&contextId=` | Tra cứu conversation đã được tạo bởi event context; chỉ thành viên mới xem được. Mỗi context có tối đa một conversation. |
| Conversation | `GET /conversations/{id}` / `PATCH /conversations/{id}` | Xem chi tiết; admin sửa tên/ảnh nhóm. |
| Members | `POST /conversations/{id}/members`, `PUT /conversations/{id}/members/{userId}/role`, `DELETE /conversations/{id}/members/{userId}` | Admin thêm user, đổi role hoặc kick; kick chặn gửi/realtime và giữ quyền đọc theo mốc leftSequence. |
| Members | `DELETE /conversations/{id}/members/me` | User tự rời chat tự do; áp dụng trạng thái read-only. |
| Messages | `GET /messages?conversationId=&beforeSequence=&limit=` | Tải message theo cursor/sequence, sau khi xác thực quyền đọc. |
| Messages | `POST /messages` | Gửi text hoặc image reference; body có `conversationId`; client không gửi trực tiếp loại system/bot. |
| Read state | `POST /messages/mark-read` | Body gồm `conversationId` và `lastReadSequence`; đồng bộ unread giữa thiết bị. |
| Bot | `POST /conversations/{id}/bot-reminders` | Landlord chọn mẫu `ocr_result`, `invoice`, hoặc `contract_expiring` kèm `resourceId`, rồi xác nhận gửi; Community dựng bot message. `clientMessageId` giúp retry an toàn. Không có cron tự gửi. |
| Notification | `GET /notifications?unreadOnly=&cursor=&limit=` | Đọc business inbox, gồm invoice/issue; inbox thuộc user hiện tại. |
| Notification | `POST /notifications/{id}/mark-read`, `POST /notifications/mark-all-read` | Mark một/all; không xóa notification. |
| Preference | `GET /me/notification-preference`, `PUT /me/notification-preference` | Đọc/cập nhật push theo nhóm chat/invoice/issue; giữ route hiện có. |
| PushDevice | `POST /me/push-devices`, `DELETE /me/push-devices/{deviceId}` | Đăng ký/thu hồi thiết bị thuộc Community; token không nhận từ userId trong body. |
| Socket.io | `conversation.message.created`, `conversation.updated`, `conversation.member.updated`, `conversation.read-state.updated`, `notification.created` | Gửi realtime tới session đã xác thực; server kiểm tra membership trước khi join room. |
| RabbitMQ | Context/building created, ContractMember added/removed, `notification.requested` | Đồng bộ membership/context hoặc business notification; xử lý event idempotent. Tên/payload phải khớp event contract nguồn. |

Quy ước đã duyệt: chat 1:1 duy nhất theo cặp user; group tạo mới và người tạo là admin. Chat 1:1 mở lại sẽ kích hoạt membership cũ cho hai bên. Member thêm lại vào nhóm xem toàn bộ history; member read-only chỉ xem tới `leftSequence`. `POST /messages` nhận `clientMessageId` để retry không tạo trùng; `lastReadSequence` chỉ được tiến lên. Source service cung cấp recipient và snapshot nội dung notification; Community tạo một inbox row cho mỗi recipient/event và phát Socket để đồng bộ inbox. Community áp dụng preference khi gửi FCM; FE áp dụng cùng preference khi hiện toast Web. Tắt một category không ẩn inbox hoặc chặn Socket sync. Group/system changes tạo system message + Socket, không FCM. Push chat gửi tới tất cả thiết bị mobile đã đăng ký; client khử trùng theo ID.

### Quyết định API đã chốt

| Mã | Quyết định | Đề xuất | Trạng thái |
|---|---|---|---|
| API-01 | Tạo chat direct và group | Một `POST /conversations` với `kind=direct|group`; direct trả conversation hiện có cho cặp user, group tạo mới. Context chat được tra cứu theo context. | Đã chốt |
| API-02 | Thành viên ban đầu khi tạo group | Body nhận `memberUserIds[]`; server tự thêm người gọi làm admin, các user còn lại thành member. | Đã chốt |
| API-03 | Ai tạo contextual conversation | Event từ service domain tạo sẵn conversation/member; client dùng `GET /conversations?contextType=&contextId=` để lấy chat. | Đã chốt |
| API-04 | Gắn ảnh upload trước khi tạo message | Presign theo `ownerType=conversation`, `ownerId=conversationId`; Message lưu `mediaId`. Upload cần membership active; download qua Media Service phải kiểm tra quyền đọc message liên kết, gồm giới hạn `leftSequence` với member read-only. | Đã chốt |
| API-05 | Đổi vai trò thành viên qua API | `PATCH /conversations/{id}/members/{userId}` chỉ nhận `role=admin|member`; chỉ admin được gọi và không được hạ quyền admin cuối cùng. | Đã chốt |
| API-06 | Retry gửi message sau timeout | Client gửi `clientMessageId`; Community idempotent theo `(senderMemberId, clientMessageId)` để retry không tạo tin trùng. | Đã chốt |
| API-07 | Cập nhật read cursor | Client gửi `lastReadSequence`; Community kiểm tra sequence thuộc conversation và chỉ cho cursor tiến lên. | Đã chốt |
| API-08 | Nội dung business notification do service nào dựng | Service nguồn gửi recipient list cùng type/title/body/deepLink/data; Community lưu snapshot và phân phối. | Đã chốt |
| API-09 | Route PushDevice sau khi chuyển ownership | Giữ `POST/DELETE /me/push-devices`, đổi Gateway route từ Identity sang Community để client không đổi URL. | Đã chốt |
| API-10 | Kênh service domain gửi integration event | RabbitMQ với transactional outbox ở service nguồn; Community consumer idempotent và xác nhận sau khi lưu. | Đã chốt |
| API-11 | Chuyển PushDevice từ Identity sang Community | Không backfill token vì Identity hiện chưa có PushDevice; client register token với Community khi dùng app. | Đã chốt |
| API-12 | Nội dung push chat | FCM có tên người gửi và preview text; ảnh hiển thị nhãn “Đã gửi ảnh”; payload có conversation/message ID để mở đúng chat. | Đã chốt |
| API-13 | Cách đặt route cho message | Giữ endpoint phẳng theo `api-spec`: `GET /messages?conversationId=...`, `POST /messages`, `POST /messages/mark-read`. | Đã chốt |
| API-14 | Client join Socket conversation | JWT trong handshake; client yêu cầu join conversation; server kiểm tra membership active rồi mới cho nhận event realtime. Khi bị kick, Community loại session khỏi room. Read-only chỉ tải history tới `leftSequence` qua REST. | Đã chốt |
| API-15 | Push cho system message đổi nhóm | Lưu vào history và phát Socket cho thành viên active; không gửi FCM. FCM chat dành cho message do user/bot gửi. | Đã chốt |
| API-16 | Gửi bot reminder | Landlord chọn mẫu `ocr_result`, `invoice`, hoặc `contract_expiring`, gửi `resourceId` và `clientMessageId`; Community tạo bot message theo mẫu. Chỉ gửi khi landlord chủ động bấm; không có lịch tự động. | Đã chốt |

### Mẫu contract API để review

Các mẫu dưới đây minh họa shape của request/response đã được duyệt. Chi tiết nội dung từng mẫu bot reminder sẽ lấy từ resource tương ứng và được chuẩn hóa trong bước triển khai template.

**Tạo chat direct hoặc nhóm** — người gọi lấy từ JWT; không nhận sender/admin ID tùy ý từ client.

```json
POST /conversations
{
  "kind": "group",
  "title": "Nhóm trao đổi",
  "memberUserIds": ["<user-id-1>", "<user-id-2>"]
}
```

```json
{
  "data": {
    "id": "<conversation-id>",
    "kind": "group",
    "title": "Nhóm trao đổi",
    "members": [
      { "userId": "<caller-id>", "role": "admin", "status": "active" },
      { "userId": "<user-id-1>", "role": "member", "status": "active" },
      { "userId": "<user-id-2>", "role": "member", "status": "active" }
    ]
  }
}
```

Với `kind=direct`, request chỉ định `targetUserId`; Community tìm/tạo chat duy nhất cho cặp user và kích hoạt lại membership nếu trước đó có người rời.

**Tra cứu chat theo context**

```text
GET /conversations?contextType=contract&contextId=<contract-id>
```

Trả conversation đã được tạo từ integration event; user không phải member thì bị từ chối. Không có conversation tương ứng thì trả `404 CONVERSATION_NOT_FOUND`.

**Gửi message**

```json
POST /messages
{
  "conversationId": "<conversation-id>",
  "clientMessageId": "<uuid-generated-by-client>",
  "type": "image",
  "mediaId": "<completed-media-id>"
}
```

Message text gửi `type=text` và `text`; image gửi `type=image` và `mediaId`. Server xác thực active membership, media đã upload xong và thuộc conversation; retry cùng `clientMessageId` trả lại message đã tạo.

Với ảnh, client xin presigned URL từ Media Service bằng `ownerType=conversation`, `ownerId=<conversationId>`, `purpose=chat_attachment`; upload/complete xong mới gửi `POST /messages` kèm `mediaId`. Media Service dùng Community để kiểm tra membership active khi upload và quyền đọc message liên kết khi tải ảnh. Member read-only chỉ tải ảnh thuộc message có sequence `<= leftSequence`. Message chỉ tham chiếu media đã complete và cùng conversation.

**Mark-read và notification inbox**

```json
POST /messages/mark-read
{ "conversationId": "<conversation-id>", "lastReadSequence": 42 }
```

```text
GET /notifications?unreadOnly=true&cursor=<opaque>&limit=20
```

`PUT /me/notification-preference` nhận danh sách category `chat|invoice|issue` và API field `pushEnabled`. Theo P7-D82, giá trị này áp dụng cho push thiết bị và toast Web; inbox vẫn được lưu và đồng bộ. `POST /me/push-devices` nhận token/platform; owner luôn suy ra từ JWT.

### Event contract v1 đề xuất

Mọi event RabbitMQ có envelope chung `eventId`, `eventType`, `schemaVersion`, `sourceService`, `occurredAt`, `payload`. Event consumer lưu dấu đã xử lý cùng transaction với dữ liệu nghiệp vụ; redelivery không tạo conversation/member/message/notification trùng.

| Event (tên minh họa, cần map với outbox hiện có) | Producer gửi tối thiểu | Community xử lý |
|---|---|---|
| `building.created` | `buildingId`, `ownerUserId` | Tạo conversation context `building`; owner là admin. |
| `contract.activated` | `contractId`, `buildingId`, `roomId`, `landlordId`, `tenantUserIds[]` | Create one contract conversation with the landlord admin and linked tenants from the snapshot; then apply stored member events. |
| `contract_member.added` / `contract_member.linked` | `contractId`, `contractMemberId`, `tenantUserId` (nullable for added) | Add a resolved tenant to the contract chat. Before activation, store the event; do not create a conversation without its admin. |
| `contract_member.left` | `contractId`, `contractMemberId`, `tenantUserId` nullable, date-only `leftAt` | Keep an existing member read-only. Compute `leftSequence` at envelope `occurredAt`; individual leave and checkout use this event. No separate kick event is emitted by checkout. |
| `notification.requested` | `recipientUserIds[]`, `notification.type/title/body/deepLink/data` | Lưu một snapshot inbox cho mỗi recipient/event; tạo delivery tới session Socket và PushDevice theo preference. |

Tên event/payload cuối cùng phải khớp code outbox của Tenancy và từng service producer. Community không truy vấn domain DB và không tự suy ra recipient business notification.

### Event realtime và FCM

| Kênh | Event/payload tối thiểu | Quy tắc |
|---|---|---|
| Socket | `message.created` gồm `conversationId`, `messageId`, `sequence`, `sender`, `type`, `text/mediaId`, `createdAt`; `conversation.updated/member.updated`; `conversation.read-state.updated`; `notification.created/read-state.updated` | Server chỉ phát tới user/session được phép; read-only member không nhận message sau `leftSequence`. |
| FCM chat | `messageId`, `conversationId`, sender name, preview text hoặc “Đã gửi ảnh”, deep link | Gửi tới các PushDevice mobile của recipient active nếu preference `chat` bật; client khử trùng lặp theo `messageId`; system message không FCM. Không tạo notification inbox row cho chat message. |
| FCM business notification | `notificationId`, type, title/body, data/deep link | Một inbox row mỗi recipient/event; cùng notification ID dùng để client khử trùng lặp giữa session và thiết bị. |
| Email | Forgot/reset password | Tiếp tục do Identity gửi; không đưa email business notification vào Community. |

## 7. Các bước review trước khi code

| Bước | Nội dung | Kết quả cần duyệt |
|---|---|---|
| **1. Chốt phạm vi** | Rà bảng phạm vi, chat hợp đồng/chat tự do/chat tòa, notification inbox và push. | Đã rà; tiếp tục giữ tài liệu ở trạng thái thiết kế cho tới khi các gate còn lại được duyệt. |
| **2. Chốt business logic** | Xác nhận từng quy tắc BL và rà use case/event-recipient-delivery. | BL-01–BL-23 đã được xác nhận. |
| **3. Chốt ERD** | Rà entity/field/ràng buộc tại §3 và các quyết định ERD; chưa tạo migration. | ERD v1 đã được user duyệt. |
| **4. Chốt API và event contract** | OpenAPI v1, request/response, Socket events, event envelope và FCM payload tại §6. | API/event contract v1 đã duyệt và đã cập nhật trong `api-docs/src`; bundle đã tạo. Chưa code. |
| **5. Tạo implementation backlog** | Tách task backend, gateway, web, Android và migration theo dependency; mỗi task có acceptance criteria. | Bản đề xuất đã tạo tại [community-service-implementation-backlog.md](community-service-implementation-backlog.md); chưa mở issue code, chưa gán người/iteration. |

## 8. Kiểm tra thiết kế

- Hợp đồng mới tạo conversation riêng; member add/remove được đồng bộ, còn chat không bị khóa khi hợp đồng kết thúc.
- Tòa mới tạo chat tòa; chủ tòa là group admin và member có contract trong tòa được đồng bộ đúng.
- Lõi chat hỗ trợ direct và nhóm tự do; vai trò và thao tác thành viên dùng chung, không cần context contract/building.
- Quy tắc contract/building được thực hiện qua integration event và không tạo nhánh domain-specific trong lõi chat.
- Chat history và business notification inbox là hai luồng dữ liệu riêng.
- Recipient của business notification luôn đến từ service phát event; Community chỉ lưu và phân phối.
- Không có tự động gửi bot reminder, không có `@issue`, Issue panel hoặc mention trong phạm vi.

## 9. Tài liệu tham chiếu

- `pm/phase-0/discovery/decisions.md` — D24′ Property Chat.
- `pm/phase-1/discovery/database-design.md` — thiết kế Conversation, Message, Notification và PushDevice hiện tại.
- `pm/phase-2/discovery/api-spec.md` — API Chat/Notification và integration MatchRequest hiện tại.
- `boilerplate/docs/architecture.md` và `boilerplate/docs/transactional-outbox-design.md` — kiến trúc service và giao event.
