# Khảo sát mức sẵn sàng triển khai Web Chat v1

> Ngày rà soát: 04/11/2026. Đây là khảo sát mã nguồn và contract, chưa chạy thử end-to-end vì chưa có Community DB/schema trong phiên này. [Quyết định sản phẩm đã chốt](web-chat-v1-decisions.md) là nguồn cho phạm vi; tài liệu này ghi khoảng cách giữa quyết định và code hiện tại. Chưa bắt đầu code FE.

## 1. Kết luận để mở Goal

Có thể mở Goal triển khai **nếu Goal bao gồm cả các phụ thuộc Identity, Community và API docs dưới đây**. Nếu Goal chỉ được phép sửa `fe/`, cần hoàn tất các mục **B1–B5** trước; FE không thể tự tạo dữ liệu/contract còn thiếu. Thứ tự hợp lý: đóng contract → hoàn thiện API/event nguồn → dựng Socket và dữ liệu FE → hoàn thiện chat desktop → kiểm chứng tích hợp.

| Mã | Mức | Owner | Khoảng cách đã xác nhận | Điều kiện đạt |
|---|---|---|---|---|
| B1 | Chặn | Identity + Gateway + api-docs | `GET /users` chỉ cho Admin; chưa có directory để Landlord/Tenant tìm Landlord/Tenant active bằng tên. Tìm admin hiện tại chỉ dùng `LOWER`, chưa tìm không dấu. | API directory xác thực, loại caller/Admin/locked/deleted, chỉ trả `id`, `name`, phân trang và tìm không dấu/không phân biệt hoa thường. Gateway chuyển route tới Identity. |
| B2 | Chặn | Community + api-docs | `GET /conversations` chưa có `q`, `kind`, `otherUserId` hoặc lọc chat tự do; vẫn trả direct trống. List chỉ trả `title`, nên direct không có tên người còn lại. | Query tìm và phân trang trên toàn bộ DB; direct trống ẩn; group trống hiện; lookup cặp user 0/1 không ghi DB; list/detail cung cấp display name theo người xem. |
| B3 | Chặn | Community + api-docs | Chưa có `GET /conversations/unread-summary`; list và repository hiện tính cả `system` message là unread. | Có tổng unread của tất cả hội thoại, chỉ đếm user/bot; list/detail/mark-read và event đồng nhất cách tính, tôn trọng giới hạn đọc của read-only member. |
| B4 | Chặn | Community + api-docs | `message:created` chỉ phát tới conversation room, còn FE cần nhận tin mới ở mọi trang mà không join tất cả room. | Event tin mới tới user room với payload đã chốt; không phát cho người mất quyền; không tạo toast/unread cho sender; event `message:created` cũ vẫn hoạt động cho màn chat. |
| B5 | Chặn | Community + api-docs | `POST /conversations` hiện cho tạo group chỉ với người tạo và để `title=null` nếu không truyền. | Từ chối group dưới 3 user; tạo tên mặc định từ snapshot ban đầu, ổn định và không vượt giới hạn cột; group mới xuất hiện ngay. |
| F1 | FE | FE | `/chat` và `/chat/:id` là placeholder; Admin vẫn truy cập route chung bằng URL. | Route chỉ cho Landlord/Tenant, desktop hai cột, URL detail hợp lệ/không tồn tại có trạng thái rõ. |
| F2 | FE | FE | Chưa có `socket.io-client`; token refresh chỉ chạy khi Axios nhận 401. | Một Socket sau login, dùng Gateway origin/path, xử lý token sắp hết hạn, `session:ready`, reconnect, join lại chat đang mở, logout ngắt. |
| F3 | FE | FE | Sidebar hỗ trợ badge tĩnh nhưng chưa lấy unread; QueryClient có `staleTime=5 phút`, `refetchOnWindowFocus=false`; logout chỉ reset Auth queries. | Badge động `9+`, đồng bộ REST lúc khởi tạo/reconnect/đọc ở thiết bị khác; xoá cache chat và các dữ liệu theo user khi đổi tài khoản/logout. |
| F4 | FE | FE | Chưa có chat API/hook/state/i18n. | Search user/chat, draft direct, tạo group, history cursor, gửi text/retry, mark-read khi nhìn thấy, toast đúng ngữ cảnh, đủ loading/empty/error. |
| I1 | Tích hợp | BE/FE | Community entities có nhưng migrations chat chưa được tạo/chạy trong môi trường này. | Schema đúng entity trước khi thử thật; chạy hai tài khoản/two tabs qua Gateway; không coi build thành công là xác nhận end-to-end. |

## 2. Contract hiện có dùng được ngay

| Luồng | Hiện trạng mã nguồn | FE cần lưu ý |
|---|---|---|
| Gửi text | `POST /messages` nhận `conversationId`, `clientMessageId`, `type=text`, `content` tối đa 4000; lưu thành công mới phát `message:created`; retry cùng ID trả message cũ. | Giữ cùng UUID khi tự retry; hợp nhất REST response với Socket bằng `id`/`clientMessageId`. Không lưu hàng đợi qua reload theo quyết định v1. |
| Lịch sử | `GET /messages?conversationId&cursor&pageSize` trả mới trước, cursor opaque, mặc định 30/tối đa 100. `sequence` ở response là **string** dù mark-read nhận số nguyên. | Tải trang cũ theo `nextCursor`; render tăng dần trong khung; so sánh sequence an toàn, tránh ép sang số lớn tùy tiện. |
| Đọc | `POST /messages/mark-read` nhận `lastReadSequence`; server chỉ cho cursor tiến lên, không vượt tin cuối hoặc `leftSequence` của member read-only. | Chỉ gửi sequence cao nhất thật sự thấy khi tab đang hoạt động; không mark-read chỉ vì đã tải data. |
| Socket | Socket.IO v4, path `/api/v1/community/socket.io`, websocket-only, `auth.token`; `session:ready`, `conversation:join/leave`, `message:created`, `conversation:read-updated`, `conversation:available`, `conversation:access-revoked`. | Chỉ join conversation đang mở; đợi `session:ready`, xử lý ack lỗi; REST là nguồn phục hồi sau reconnect. |
| Tạo direct | `POST /conversations` resolve cặp và tạo/khôi phục member; phát `conversation:available` ngay cả khi chưa có tin. | Khi chọn user mới chỉ mở composer nháp; gọi create lúc gửi tin đầu. Event available cho direct trống phải được FE bỏ qua, không hiện chat trống. |

## 3. Quy tắc FE cần đặc tả đủ trước khi code

| Trường hợp | Quy tắc triển khai đề xuất theo quyết định đã chốt |
|---|---|
| Tên/chat search | Backend tìm không dấu và không phân biệt hoa thường; FE debounce, bỏ request cũ khi từ khóa thay đổi; khi không có kết quả hiển thị empty state riêng. Group tìm bằng tên lưu, direct tìm bằng snapshot tên người còn lại. |
| Tên và preview | List/detail cần `displayName` theo viewer; toast có tên người gửi, tên chat, preview ngắn. Tin system có thể ở lịch sử/lastMessage nhưng không tăng unread hay tạo chat toast. Khi thêm event user-room phải xác định preview text rỗng/ảnh/bot. |
| Chat trống | Group đã tạo xuất hiện ngay. Direct chưa có message không xuất hiện với cả A và B, kể cả `conversation:available` hoặc bước create thành công mà send lỗi. |
| First send direct | FE giữ một draft theo `otherUserId`; lần gửi đầu: create/resolve rồi send. Nếu create xong mà send lỗi, giữ `conversationId` và `clientMessageId` trong bộ nhớ để retry; gửi thành công thì điều hướng `/chat/:id` và đưa chat lên list. |
| Tin mới trên chat đang mở | `message:created` cập nhật khung; user-room event có thể đến cùng lúc. Khử trùng bằng `messageId`; không toast. Nếu đang xem tin cũ hoặc tab nền thì chưa mark-read, hiện nút **Tin mới**. |
| Badge/toast ở trang khác | Event user-room chỉ cập nhật FE tại chỗ; hiển thị toast khi tab đang hoạt động. `9+` là cách hiển thị, giá trị nội bộ vẫn là tổng thật. Reconnect/refocus cần reconcile REST vì Socket không giữ replay. |
| Quyền bị thu hồi | `conversation:access-revoked` phải rời room, ngừng send/retry, bỏ view nếu đang mở và làm mới list/unread. Direct/group read-only vẫn có thể đọc phần history được phép qua REST; FE không cho gửi khi read-only. |
| Chuyển user/logout | Đóng Socket, xóa pending message và cache dữ liệu chat theo tài khoản. Auth store hiện giữ token trong localStorage; không để query cache của user A xuất hiện ở user B cùng tab. |
| Mở URL trực tiếp | F5 `/chat/:id` phải tải detail/history theo quyền; 403/404 có trạng thái cụ thể. `/chat` không được mở cho Admin dù route nằm trong `commonRoutes`. |

## 4. Những điểm kỹ thuật cần đóng trong contract, không cần hỏi thêm PM

1. **Tên event và JSON**: cố định tên user-room event, chuẩn `messageId`/`id`, `sequence` string, preview tối đa bao nhiêu ký tự, xử lý bot/system và chính session người gửi. Ghi vào `api-docs/docs/community-socket-v1.md`.
2. **Query combinations**: quyết định `kind`, `otherUserId`, `q`, lọc context và phân trang khi phối hợp; lỗi khi `otherUserId` không đi cùng `kind=direct`. Route `/conversations/unread-summary` phải ưu tiên trước `/:conversationId`.
3. **Search PostgreSQL**: chọn cách tìm không dấu chạy được trong schema triển khai (ví dụ `unaccent`/normalized search column), có index và quy tắc sắp xếp ổn định. Không lọc một page ở FE vì sai tổng số và bỏ sót kết quả.
4. **Group title**: tên mặc định ghép snapshot thành viên lúc tạo, xử lý trùng tên và cắt theo giới hạn 255; lưu title thật ở backend. FE chỉ hiển thị, không tự tạo tên khác.
5. **Token refresh**: tách khả năng refresh dùng chung cho Axios và Socket hoặc cơ chế tương đương; tránh hai refresh đồng thời làm vô hiệu refresh token quay vòng. Socket phải lấy JWT mới khi reconnect.
6. **Response và lỗi**: thêm success/error code cho các endpoint mới, nhất quán envelope/pagination, mô tả 401/403/404/422/503 để FE dùng đúng và dịch i18n.
7. **Cập nhật list theo event**: xác định event cho người gửi ở tab khác và cho first message làm direct vừa hiện; refetch list khi dữ liệu không có trong page/cache, không tăng unread của chính sender.

## 5. Checklist kiểm chứng khi môi trường sẵn sàng

- Hai user khác vai trò Landlord/Tenant tìm nhau bằng tên có/không dấu; Admin/locked/deleted/self không xuất hiện. Hai user trùng tên không làm crash UI.
- Chọn người chưa chat: composer nháp, chưa có chat trống trong list; gửi tin đầu thành công thì cả hai thấy chat; ngắt mạng giữa create và send rồi tự retry không sinh tin trùng.
- Chọn người đã chat: mở đúng lịch sử cũ; group tạo với hai người khác và tên mặc định/tùy chọn; group trống vẫn hiện; nhóm thiếu thành viên bị từ chối.
- Tin từ tab B khi tab A ở trang khác: badge/toast một lần; khi A ở đúng chat: tin chỉ hiện trong khung. Tab nền hoặc cuộn xem tin cũ chưa mark-read; quay lại thấy tin rồi mới giảm badge.
- Đăng nhập cùng user ở hai tab/thiết bị: mark-read đồng bộ; F5/reconnect khôi phục đúng tổng unread và messages; logout rồi đăng nhập user khác không lộ cache cũ.
- Member read-only không gửi/join room; REST chỉ trả history tới `leftSequence`. System message xuất hiện trong history nhưng không tăng unread.
- Qua Gateway ở local/deploy: REST base URL và Socket origin/path đúng, WebSocket upgrade/CORS hợp lệ, token hết hạn được refresh/reconnect; Community DB migration đã áp dụng.

## 6. Phạm vi Goal FE v1

Goal FE nên giao rõ hai phần: (1) bàn giao/đợi B1–B5 và contract API docs, (2) triển khai F1–F4 theo lát dọc. Không kéo ảnh chat, chỉnh nhóm, chat hợp đồng/tòa nhà, notification inbox hoặc browser notification vào Goal Web Chat v1. Socket dùng chung cho notification ở tầng kết nối, nhưng UI notification vẫn là mốc sau.

