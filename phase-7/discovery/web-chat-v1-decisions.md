# Quyết định cho Web Chat v1

> **Trạng thái:** Phạm vi và hành vi sản phẩm đã được PM chốt qua từng câu hỏi ngày 03/11/2026. Đây là nguồn quyết định sản phẩm; contract API/event hiện hành được đối chiếu trong [trạng thái Web Chat hiện tại](web-chat-v1-current-status.md) và tài liệu API của các repo.
> **Nền tảng:** `fe/` (React trên web), tập trung giao diện desktop. Ứng dụng Android là một client riêng.
> **Nguồn thiết kế backend:** [Community Service design](../../phase-6/discovery/community-service-design.md) và [Phase 7 plan](../README.md).

## 1. Phạm vi mốc đầu

| Hạng mục | Quyết định đã chốt |
|---|---|
| Loại hội thoại | Chat 1:1 và nhóm tự do. Chat theo hợp đồng/tòa nhà làm sau. |
| Vai trò dùng Web Chat v1 | Landlord và Tenant. FE không hiển thị menu/màn Chat cho Admin trong mốc đầu; route cần kiểm tra vai trò. Quyền chat ở backend là quyết định riêng. |
| Màn Chat | Desktop hai cột: danh sách hội thoại bên trái, tin nhắn bên phải. Trình duyệt điện thoại vẫn dùng được với layout một cột tối giản; không tối ưu sâu vì mobile app là client riêng. |
| Chức năng chính | Xem danh sách, tìm hội thoại theo tên người/nhóm, tải lịch sử, gửi tin chữ, hiển thị tổng tin chưa đọc và đánh dấu đã đọc. |
| Mở chat 1:1 | Nếu hai người đã từng chat, chọn người đó mở ngay hội thoại và lịch sử cũ. Nếu chưa từng chat, chỉ mở khung soạn, chưa tạo conversation. Chat 1:1 mới chỉ xuất hiện trong danh sách của hai bên sau tin đầu tiên. Nhóm được tạo và xuất hiện ngay khi user xác nhận **Tạo nhóm**, dù chưa có tin. |
| Gửi tin đầu tiên của chat 1:1 | Dùng hai API hiện có: tạo/khôi phục conversation rồi gửi message. Nếu bước gửi lỗi và DB còn conversation trống, không hiện conversation đó trong danh sách của hai bên; FE giữ tin chờ và retry khi trang còn mở. Không yêu cầu transaction gộp hai API trong v1. |
| Tạo nhóm | Chọn ít nhất hai người khác (tổng tối thiểu ba người kể cả người tạo). Tên nhóm tùy chọn; nếu bỏ trống, dùng tên mặc định tạo từ các thành viên ban đầu. |
| Tìm người | Bổ sung API cho Landlord/Tenant đã đăng nhập tìm **Landlord/Tenant đang hoạt động** theo tên; không đưa Admin vào kết quả. Mốc đầu chỉ trả ID và tên. FE dùng avatar chữ cái; ảnh đại diện user để sau. API `GET /users` hiện tại dành riêng cho admin nên không dùng cho luồng này. |
| Người trùng tên | Kết quả tìm kiếm v1 vẫn chỉ hiện tên. PM chấp nhận khả năng user chọn nhầm khi có hai tài khoản trùng tên; chưa bổ sung email/điện thoại/mã nhận diện trong UI. |
| Cách tìm tên | Tìm người và tìm hội thoại đều không phân biệt chữ hoa/thường hoặc dấu tiếng Việt. Ví dụ gõ `Nguyen` có thể tìm `Nguyễn`; cách chuẩn hóa và phân trang được thiết kế ở API. |
| Tên chat 1:1 | Hiển thị `displayName` của người còn lại đã lưu trong `ConversationMember` khi bắt đầu chat. Nếu người đó đổi tên hồ sơ sau này, tên chat cũ chưa cập nhật trong v1; tìm hội thoại cũng dùng tên đã lưu. |
| Ảnh và quản lý nhóm | Gửi ảnh chat, sửa tên/ảnh nhóm và thêm/xóa/đổi vai trò thành viên nằm ở mốc sau. |

## 2. Socket, thông báo chat và unread

| Tình huống | Quyết định đã chốt |
|---|---|
| Vòng đời kết nối | Sau khi đăng nhập, FE duy trì một kết nối Socket dùng chung cho chat và notification. Khi refresh JWT thì kết nối lại bằng token mới; logout thì ngắt kết nối. |
| Tin mới khi đang ở trang khác | Cập nhật badge trên menu Chat và hiện thông báo nhỏ trong ứng dụng. Thông báo gồm tên người gửi, tên hội thoại và một đoạn ngắn của tin nhắn. **Đây là bản sửa cuối cùng cho câu 13**; lựa chọn chỉ hiện tên trước đó đã bị thay thế. |
| Badge menu Chat | Đếm tổng số **tin nhắn** chưa đọc trong tất cả hội thoại; nếu vượt 9 thì hiển thị `9+`. |
| Tin hệ thống trong unread | Tin hệ thống vẫn hiện trong lịch sử nhưng không tăng unread/badge. Tin do người dùng hoặc bot gửi được tính unread nếu chưa đọc. |
| Nguồn sự kiện toàn ứng dụng | Community phát thêm sự kiện tin mới tới kênh riêng của từng user để FE cập nhật badge/thông báo ở mọi trang. Client không phải join mọi hội thoại sau đăng nhập chỉ để nhận badge. |
| Nội dung sự kiện tin mới | Event gọn gồm `messageId`, `conversationId`, `sequence`, `senderUserId`, `senderName`, `conversationName`, `type`, `contentPreview`, `createdAt`. FE khử trùng bằng `messageId`, hiện toast, tăng unread và cập nhật list tại chỗ. Mở ứng dụng/reconnect hoặc nhận thay đổi trạng thái đọc từ thiết bị khác thì tải lại tổng unread từ REST; không cần gọi API sau mỗi tin. Tên event chính thức và contract JSON sẽ được ghi trong API docs. |
| Đang xem đúng hội thoại | Tin mới hiện trực tiếp trong khung chat; không hiện thêm thông báo nhỏ. |
| Đang cuộn xem tin cũ | Tin mới vẫn chưa đọc; hiện nút **Tin mới** để cuộn xuống. Chỉ mark-read khi user đã nhìn thấy tin mới. |
| Tab trình duyệt ở nền | Không mark-read; đợi user quay lại tab và nhìn thấy tin. |
| Thông báo của hệ điều hành | Chưa xin quyền Browser Notification ở mốc đầu; dùng badge và thông báo trong ứng dụng khi user đang dùng web. |

## 3. Gửi tin và mất kết nối

| Tình huống | Quyết định đã chốt |
|---|---|
| Gửi tin chữ | Gửi qua REST với `clientMessageId`; Socket nhận tin mới sau khi backend lưu. FE khử trùng lặp giữa phản hồi REST, Socket và lần đồng bộ lại. |
| Mạng lỗi hoặc phản hồi bị mất | FE tự thử gửi lại khi có mạng, dùng **cùng** `clientMessageId` để backend trả tin cũ nếu lần đầu đã lưu. Giữ trạng thái tin đang chờ trên màn hình trong lúc trang còn mở. |
| Tải lại/đóng trang | Không lưu hàng đợi tin chờ gửi qua lần tải lại; chỉ tự gửi lại khi trang hiện tại còn mở. |
| Reconnect | Dùng REST tải tin còn thiếu theo cursor/sequence; Socket là kênh realtime, không phải nguồn lịch sử duy nhất. |

## 4. Ảnh chụp khảo sát ban đầu ngày 03/11 (lưu lịch sử)

Các bảng dưới đây ghi lại câu hỏi và trạng thái mã nguồn tại thời điểm khảo sát ban đầu, không phải backlog hiện tại. Nhiều API/event trong bảng đã được chốt và triển khai sau đó. Dùng [trạng thái Web Chat hiện tại](web-chat-v1-current-status.md) cùng mã nguồn/API docs để xác định việc còn lại; không mở lại các mục lịch sử nếu không có bằng chứng sai lệch mới.

1. Xác định route và response của API tìm Landlord/Tenant đang hoạt động theo tên cho Landlord/Tenant. Mốc đầu chỉ lộ ID và tên; phân trang, loại Admin và user hiện tại khỏi kết quả. Khi `q` rỗng hoặc thiếu, API vẫn trả một trang user để picker có danh sách ban đầu. Identity hiện có `GET /users` dành cho admin. FE dùng avatar chữ cái, ảnh đại diện user để sau.
2. Bổ sung truy vấn tìm hội thoại theo tên người/nhóm trên toàn bộ hội thoại của user, không chỉ lọc trang đã tải. Danh sách cần ẩn direct conversation chưa có message và lọc `kind=direct|group` cho mốc FE này. Tìm tên chat 1:1 theo `ConversationMember.displayName` của người còn lại.
3. Thiết kế sự kiện Socket gọn gửi tới user room khi có tin chat mới: `messageId`, `conversationId`, `sequence`, `senderUserId`, `senderName`, `conversationName`, `type`, `contentPreview`, `createdAt`. FE tự cập nhật unread/list; không đưa unread count vào event. Đồng bộ lại qua REST khi mở app/reconnect hoặc sau read-state từ thiết bị khác. Tránh phát hai toast cho cùng `messageId` khi vừa nhận event ở conversation room vừa nhận event ở user room.
4. **Đã chốt endpoint tổng unread:** thêm `GET /conversations/unread-summary` trả `totalUnreadCount` cho user đang đăng nhập. FE dùng để khởi tạo/đồng bộ lại badge; `GET /conversations` hiện phân trang nên không cộng một trang để suy ra tổng.
5. Đối chiếu `POST /conversations` với quy tắc nhóm tối thiểu ba thành viên. FE và backend phải cùng từ chối request nhóm chỉ có một người khác hoặc nhóm rỗng.
6. Cung cấp tên người còn lại theo người xem trong list/detail direct bằng snapshot `ConversationMember.displayName`; tìm hội thoại direct theo cùng snapshot. Tên group mặc định lấy từ những thành viên ban đầu và cần ổn định sau khi thành viên thay đổi. Không lấy tên từ nội dung message snapshot để làm tên hội thoại. Ảnh user để sau, FE dùng avatar chữ cái.
7. Đối chiếu API cursor, `clientMessageId`, mark-read và Socket contract hiện tại; cập nhật OpenAPI và `api-docs/docs/community-socket-v1.md` khi bổ sung contract.
8. **Đã chốt route tra cứu direct:** mở rộng `GET /conversations?kind=direct&otherUserId=<uuid>` để trả 0 hoặc 1 conversation mà không tạo mới. Direct chưa có message được xem như chưa có chat hiển thị, nên kết quả rỗng; khi bấm gửi, `POST /conversations` resolve lại ID cũ. Nếu có lịch sử thì FE mở ngay. Khi direct cũ từng ở trạng thái read-only, cần khớp quy tắc mở lại đã chốt trước đây.

### Kết quả rà soát code ngày 03/11/2026 — trạng thái lịch sử, không phải trạng thái hiện tại

| Phần | Hiện trạng đã kiểm tra | Cần làm rõ hoặc xử lý |
|---|---|---|
| Tìm user | Identity `GET /users` bị giới hạn role admin. Media đã hỗ trợ ảnh đại diện của owner `user`, nhưng User entity và response tìm user hiện chưa trả `avatarMediaId`; chưa thấy API tìm avatar theo owner. | Đã chốt mốc đầu chỉ trả ID/tên và dùng avatar chữ cái. Cần thiết kế API tìm user cho user thường. |
| Danh sách conversation | `GET /conversations` phân trang offset, có `title`, `avatarMediaId`, `unreadCount` từng hội thoại và last message; không có tên/ảnh người còn lại trong chat direct, không có tham số tìm tên. | Cần thêm tên direct theo `ConversationMember.displayName` của người còn lại, tìm kiếm trên server và tổng unread toàn bộ hội thoại. |
| Tạo group | Request hiện cho phép `memberUserIds` rỗng/thiếu; handler lưu `title=null` khi người tạo bỏ trống. | Áp quy tắc tối thiểu ba thành viên và chốt cách tạo tên mặc định ổn định. |
| Direct chưa có tin | `POST /conversations` tạo membership cho cả hai và phát `conversation:available` ngay; `GET /conversations` hiện trả cả conversation không có message. | Đã chốt chỉ ẩn direct trống trong list của hai bên. Khi gửi tin đầu tiên thành công, conversation cần xuất hiện và cập nhật qua Socket/refetch; nếu gửi lỗi, FE retry cùng `clientMessageId`. |
| Tìm direct cũ trước khi gửi | Chưa có API chỉ đọc để tra cứu conversation theo cặp user; `POST /conversations` hiện tạo mới nếu chưa có. | Đã chọn mở rộng `GET /conversations?kind=direct&otherUserId=...`; chỉ trả chat có history. Cần bổ sung query, quyền và OpenAPI. |
| Socket | Community đã có JWT handshake, `session:ready`, join/leave, `message:created` theo conversation room, `conversation:read-updated` theo user room và `conversation:available`. Chưa có sự kiện tin mới theo user room. | Đã chốt payload gọn và FE cập nhật state tại chỗ; cần bổ sung event, cơ chế refetch khi reconnect/read-state và chống toast trùng. |
| Unread | Count hiện đếm message chưa đọc của người khác, không lọc `message_type`; system message từ system member hiện có thể được tính. | Đã chốt loại system khỏi unread, giữ user/bot. Cần sửa phép tính nhất quán ở list, tổng unread và mark-read. |
| FE navigation | Landlord và tenant có menu Chat. Admin có route `/chat` chung nhưng chưa có menu Chat. | Đã chốt Web Chat v1 chỉ dành cho landlord/tenant; cần chặn route chung với Admin, không chỉ ẩn menu. Phạm vi backend đối với Admin cần làm rõ nếu API chat vẫn mở cho mọi user đăng nhập. |
| FE kỹ thuật (trạng thái ban đầu) | Khi lập kế hoạch, `/chat` và `/chat/:id` còn là placeholder, chưa có `socket.io-client`; API client dùng Axios/refresh token và menu có badge tĩnh. | Đây là ghi nhận tại thời điểm khảo sát ban đầu; trạng thái triển khai mới nhất nằm ở mục **Trạng thái chuẩn bị FE** bên dưới. |
| Token Socket khi ứng dụng rảnh | Community chủ động ngắt Socket khi JWT hết hạn; FE hiện chỉ có logic refresh token qua Axios khi REST trả 401. | FE cần chủ động làm mới token/reconnect cho Socket dù không có REST request trong thời gian dài. |
| Migrations và chạy thử | Community hiện có entity chat nhưng thư mục migrations mới có outbox/inbox; user đã nhận tự xử lý migration trước đó. | Trước khi chạy thử chat end-to-end cần schema DB khớp entity; không suy ra rằng code compile là flow đã chạy được. |

**Lưu ý luồng direct:** Backend hiện có hai lệnh tách biệt: `POST /conversations` tạo/khôi phục chat và `POST /messages` gửi tin. Nếu lệnh đầu thành công nhưng lệnh thứ hai lỗi, DB có thể còn conversation chưa có tin. PM đã chấp nhận trường hợp này với điều kiện direct trống không hiện trong danh sách; không thêm API tạo-và-gửi nguyên tử ở v1.

Đây là kết quả đọc mã nguồn, chưa xác nhận chạy end-to-end vì môi trường DB/Socket của dự án chưa được chuẩn bị trong lượt rà soát này.

### Bản phác thảo API/Socket ngày 03/11 — bản nháp lịch sử

Các dòng dưới đây là đề xuất kỹ thuật tại thời điểm khảo sát để chuyển hành vi sản phẩm thành contract. Chúng có thể đã được cập nhật trong OpenAPI và code; không dùng chúng làm contract hiện hành nếu khác với API docs hoặc [trạng thái hiện tại](web-chat-v1-current-status.md).

| Owner | Route/event đề xuất | Input hoặc payload chính | Kết quả/quy tắc |
|---|---|---|---|
| Identity | `GET /users/directory?q=&pageNo=&pageSize=` | `q` tìm tên không phân biệt dấu/hoa thường. | Chỉ Landlord/Tenant active được gọi và xuất hiện; bỏ caller/Admin. Response phân trang chỉ có `{ id, name }`. |
| Community | `GET /conversations?hasContext=false&q=&pageNo=&pageSize=` | `q` tìm tên direct của người còn lại hoặc title group; không phân biệt dấu/hoa thường. | Phân trang trên DB; chỉ hội thoại của caller. Direct chưa có message không xuất hiện. Group vừa tạo vẫn xuất hiện. `hasContext=false` tách chat tự do khỏi contextual chat về sau. |
| Community | `GET /conversations?kind=direct&otherUserId=<uuid>` | Chỉ caller và `otherUserId`, không có side effect. | Trả 0 hoặc 1 direct có history; FE mở lịch sử cũ nếu có, nếu không thì mở composer nháp. Direct trống trong DB không xuất hiện. |
| Community | `GET /conversations/unread-summary` | JWT của caller. | `{ totalUnreadCount: number }`, tính tất cả hội thoại được phép xem; loại system message, giữ user/bot. |
| Community | `POST /conversations` (group) | `memberUserIds` có ít nhất 2 ID khác caller; `title` tùy chọn. | Server từ chối nhóm dưới 3 user. Nếu bỏ title, lưu tên được dựng từ snapshot các thành viên đầu tiên, giữ ổn định khi thêm/xóa member sau đó. |
| Community | `chat:message-received` trên user room | `{ messageId, conversationId, sequence, senderUserId, senderName, conversationName, type, contentPreview, createdAt }`. | Phát sau khi lưu tin user/bot cho các session được phép; FE khử trùng bằng `messageId`, không tăng unread hay hiện toast cho tin tự gửi. `message:created` trong conversation room vẫn dùng để hiển thị history đang mở. |

`ConversationListResponseDto` và detail cần thêm tên hiển thị theo **người đang xem**: direct dùng `displayName` của người còn lại đã lưu trên membership; group dùng `title`. FE không gọi Identity cho từng hàng trong danh sách. Khi Socket reconnect hoặc nhận read-state từ thiết bị khác, FE lấy lại `unread-summary`; khi vào một conversation, FE tải history qua REST cursor.

**Cần đối chiếu trong review:** thứ tự route tĩnh `/conversations/unread-summary` trước `/:conversationId`; quy tắc `kind`/`hasContext`/`otherUserId` khi kết hợp sai; giới hạn query tìm kiếm và phân trang; title mặc định dài hơn 255 ký tự; event cho session của chính sender; trạng thái read-only; payload lỗi và mã response theo convention hiện tại. Đây là việc thiết kế kỹ thuật, không mở thêm tính năng sản phẩm.

## 5. Trình tự thiết kế và triển khai tiếp theo

1. Chốt các bổ sung backend/API/event ở mục 4; ghi request/response/payload, quyền và trường hợp lỗi.
2. Tách backlog FE theo thứ tự: nền Socket toàn ứng dụng → danh sách/tìm kiếm/tạo conversation → history/UI desktop → gửi tin/retry → unread/mark-read/toast. Các thay đổi backend cần có issue phụ thuộc riêng.
3. Sau khi hợp đồng được duyệt, triển khai từng lát dọc có thể dùng được, giữ ảnh và quản lý nhóm cho mốc sau.

## 6. Lựa chọn FE đã chốt trong vòng hỏi trực tiếp

Các lựa chọn dưới đây bổ sung cho mục 1–5; khi có khác biệt, dùng quyết định mới hơn ở bảng này. Đây là quyết định về hành vi sản phẩm, chưa phải xác nhận đã code xong.

| Nhóm | Quyết định |
|---|---|
| Cấu hình | `SOCKET_PATH` được export riêng trong `fe/src/config/routes.config.ts`; không hard-code trong hook. |
| Khung trang | `/chat` giữ sidebar/header của DashboardLayout; danh sách trái và lịch sử phải cuộn riêng. Khi chưa chọn hội thoại, cột phải hiện gợi ý chọn chat. |
| Dòng hội thoại | Avatar chữ, tên, preview tin cuối, thời gian và badge chưa đọc. Danh sách tải trang tiếp khi cuộn gần cuối. Từ khóa tìm hội thoại đồng bộ URL. |
| Header chat | Tên và avatar; nhóm hiện thêm số thành viên. |
| Lịch sử | Tin liên tiếp cùng người gửi trong nhóm được gộp; chỉ tin đầu của chuỗi hiện tên. Có mốc ngày và giờ dưới từng tin. Cuộn gần đầu tự tải tin cũ và giữ vị trí xem. |
| Mở chat và đọc | Mở ở tin mới nhất. Khi thấy tin cuối, coi các tin trước đó là đã đọc theo read cursor. Khi đã ở gần cuối, tin mới tự cuộn theo; khi đang xem tin cũ, giữ vị trí và hiện nút “Tin mới”. |
| Composer | Enter gửi, Shift+Enter xuống dòng. Read-only ẩn ô nhập và hiện thông báo không thể gửi tin. Chữ gõ dở được giữ riêng từng hội thoại trong bộ nhớ, mất khi F5. |
| Chat mới | Một nút “Chat mới” mở lựa chọn chat 1:1 hoặc tạo nhóm. Danh sách người dùng có ô tìm, vẫn hiện trang user khi từ khóa rỗng, và tự tải thêm khi cuộn; API tìm người vì vậy phải cho phép thiếu `q`. Tạo nhóm trên một màn: chọn người, tên tùy chọn, bấm tạo. Draft 1:1 chưa có conversation chỉ tồn tại khi trang đang mở; F5 không khôi phục người nhận. |
| Gửi tin | Tin hiện ngay với trạng thái “Đang gửi”. Lỗi mạng tự retry khi có mạng; timeout/5xx retry có giới hạn và backoff. Mọi lần retry dùng cùng `clientMessageId`. Lỗi 4xx không tự retry. Hết lượt retry thì giữ nội dung và hiện nút **Thử lại**. |
| Tin hệ thống | Hiện trong lịch sử và làm preview ở danh sách; dùng câu có tên người thực hiện, ví dụ “An đã thêm Bình vào nhóm”. Tin hệ thống làm nhóm lên đầu nhưng không cộng unread. Backend cần snapshot tên actor và cung cấp payload cho FE dịch vi/en. |
| Ảnh và bot | Web v1 hiển thị ảnh nhận được trong lịch sử, bấm mở ảnh lớn bằng Dialog; chưa gửi ảnh. Card bot có tên, nội dung và nút mở đối tượng nếu có link, nhưng chỉ triển khai sau khi backend có contract bot. |
| Socket mất kết nối | REST vẫn xem/gửi được; hiện “Đang kết nối lại”, phục hồi dữ liệu khi Socket quay lại. |
| Toast | Bấm toast tin mới mở `/chat/:id`. Tin đến lúc tab ở nền không hiện toast cũ khi quay lại; chỉ đồng bộ badge/danh sách. |
| Composer | Không hiện bộ đếm ký tự; chặn nhập/gửi khi đạt giới hạn backend. |
| Tạo nhóm | Khi chưa chọn đủ hai người khác ngoài người tạo, vô hiệu hóa nút **Tạo nhóm** và nhắc chọn thêm. Tạo thành công thì đóng hộp thoại và mở nhóm mới. |
| Bố cục tin | Tin của mình căn phải; tin người khác căn trái. Tin liên tiếp trong nhóm chỉ hiện tên ở tin đầu chuỗi. |
| Typing indicator | Chưa làm trong v1. |
| Cập nhật cache từ Socket | Cập nhật list/history/unread trong TanStack Query cache ngay; chỉ refetch khi reconnect hoặc đồng bộ read-state từ thiết bị khác, không gọi REST sau mỗi event. |
| Retry gửi tin | Network/timeout/5xx: retry có giới hạn và backoff với cùng `clientMessageId`; sau khi hết lượt giữ nội dung và hiện **Thử lại**. Lỗi 4xx giữ nội dung để sao chép, không tự retry và không có nút retry. |
| Tin gửi lỗi | Giữ nội dung để người dùng bôi đen và sao chép thủ công; không thêm nút **Sao chép** riêng. |
| Trạng thái rỗng/lỗi | Danh sách chat trống có thông báo và nút **Chat mới**; tìm kiếm không có kết quả có nút xóa từ khóa. Lịch sử tải thêm bị lỗi thì giữ tin đã tải và hiện **Thử tải lại**; tải lần đầu lỗi thì hiện trạng thái lỗi kèm nút thử lại. |
| Nội dung composer | Không gửi nội dung chỉ có khoảng trắng; trim khoảng trắng đầu/cuối nhưng giữ xuống dòng bên trong. Không hiện bộ đếm và chặn ở giới hạn backend. |
| Draft chat mới | Khi soạn tin đầu cho người chưa từng chat, giữ draft riêng theo từng người nhận trong bộ nhớ nếu chuyển sang người khác; F5 vẫn làm mất draft. |
| Sequence | Thống nhất `sequence` trên wire là chuỗi bigint, ví dụ `"42"`; sửa OpenAPI đang ghi `integer/int64` để khớp backend và giữ độ chính xác trong JS. |
| Mở 1:1 với người mới | Không gọi `POST /conversations` khi chỉ chọn người. FE giữ người nhận và mở composer trong bộ nhớ. Khi gửi tin đầu tiên mới gọi `POST /conversations`, sau đó `POST /messages`; direct conversation trống không hiện trong danh sách nếu bước gửi tin thất bại. Nếu đã có lịch sử, mở hội thoại cũ ngay bằng truy vấn `GET /conversations?kind=direct&otherUserId=...`. |

### Quyết định đồng bộ hợp đồng và kiến trúc FE

| Mục | Đã chốt |
|---|---|
| Kiểu sequence/cursor trên wire | Dùng chuỗi thập phân cho mọi sequence/cursor: `message.sequence`, `lastMessage.sequence`, `lastReadSequence`, `leftSequence`, request mark-read và Socket payload. Không serialize bigint thành JSON number. |
| System message actor | Mỗi payload system có `actorDisplayName` snapshot cùng `actorUserId`; FE dùng snapshot để dựng câu vi/en mà không tra cứu thêm. |
| `lastMessage` trong conversation list | Trả thêm `payload` có discriminator và union giống Message; FE dùng payload để dịch preview system. Payload null với message không có payload. |
| Trạng thái Socket cho UI | Mở rộng context hiện tại để cung cấp `{ socket, status }`, trạng thái gồm `idle`, `connecting`, `connected`, `reconnecting`. |
| Listener realtime toàn app | Tạo `ChatRealtimeBridge` dưới `AppProvider` để nhận user-room event, cập nhật Query cache/unread và toast. ChatPage chỉ xử lý event của conversation đang mở. |
| User-room event | Giữ contract đã chốt: `chat:message-received` phát tới user room của member active, gồm cả sender để đồng bộ các tab/thiết bị; chỉ cho `text`/`image`/`bot`, không cho `system`. FE khử trùng theo `messageId`, không tạo toast/unread cho tin của chính user. |

### Trạng thái chuẩn bị FE

Trong worktree FE hiện tại đã có nền triển khai Web Chat v1; đây là trạng thái code, chưa phải xác nhận tích hợp end-to-end:

| Phần | Đã chuẩn bị |
|---|---|
| Route và bố cục | `/chat` và `/chat/:id` cho Landlord/Tenant; giữ Dashboard sidebar/header, danh sách và khung hội thoại cuộn riêng; mobile có layout một cột cơ bản. |
| API và cache | API wrappers dùng helper phân trang offset/cursor chung; query/mutation hooks dùng TanStack Query cho danh sách, tìm user, detail, history, unread, tạo nhóm và mark-read. |
| State giao diện | Draft và tin đang gửi/thất bại giữ trong hook bộ nhớ theo conversation hoặc người nhận; dữ liệu server nằm trong Query cache. Không khôi phục draft/pending sau reload. |
| Realtime | Socket session dùng chung sau đăng nhập, context cung cấp trạng thái kết nối; `ChatRealtimeBridge` nhận event toàn app và đồng bộ list/unread/toast. Chat window join conversation hiện hành và nhận message/read/access events. |
| Hành vi chat | Tra direct cũ trước; direct mới chỉ tạo khi gửi tin đầu. Có tạo nhóm, history cursor, optimistic send với retry cùng `clientMessageId`, mark-read khi đang thấy tin mới nhất, dịch system message, xem ảnh nhận được. |
| Thành phần giao diện | Conversation list, dialog chat mới, chat window/feed/composer, message item và preview ảnh được tách thành component nhỏ; nội dung vi/en dùng i18n. |

### Các phụ thuộc được ghi nhận ngày 03/11 — cần xác minh theo trạng thái hiện tại

1. Khi lập khảo sát, cần đồng bộ Community/OpenAPI để mọi `sequence` và cursor là chuỗi thập phân, bao gồm response member/list, mark-read và Socket payload.
2. Đồng bộ system-message payload: cần `actorDisplayName` snapshot và `lastMessage.payload` có discriminator để FE dịch lịch sử/preview. FE hiện dùng nhãn bản địa hóa chung nếu snapshot actor bị thiếu; đây chỉ là fallback, không thay đổi contract đã chốt.
3. Community cần phát `chat:message-received` tới user room theo contract; nếu chưa có event thì FE vẫn tải REST được nhưng badge/toast đa trang không realtime.
4. Cần chạy thử Gateway với hai tài khoản và DB đã migrate để xác nhận auth Socket, join, REST cursor, retry/idempotency, unread đồng bộ và media download. Hiện chưa có xác nhận kiểm tra này.

Các ghi chú này mô tả thời điểm 03/11, không xác nhận trạng thái branch/PR hiện tại. Trạng thái FE mới hơn và các bước còn lại được ghi tại [rà soát sau demo](web-chat-v1-current-status.md); trạng thái commit/merge phải kiểm tra trên repo tương ứng.

## 7. Tài liệu tham chiếu

- `api-docs/docs/community-socket-v1.md` — Socket hiện có: `session:ready`, join/leave, `message:created`, `conversation:read-updated`, `conversation:available`.
- `api-docs/src/paths/chat/` — REST conversation và message hiện có.
- `fe/src/app/routes/roles/common.routes.tsx` — route Chat và phân quyền Landlord/Tenant.
- `fe/src/features/chat/` — API, query hooks, components và page Web Chat v1.
- `fe/src/features/realtime/` — Socket session dùng chung và trạng thái kết nối.
- `fe/src/lib/api/` và `fe/src/stores/auth-store.ts` — API client và vòng đời token.
