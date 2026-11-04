# Giao việc cho Claude trước Goal Web Chat v1

> Ngày lập: 04/11/2026. Phạm vi dựa trên [quyết định Web Chat v1](web-chat-v1-decisions.md) và [khảo sát mức sẵn sàng](web-chat-v1-readiness-audit.md). Đây là prompt để người dùng sao chép vào phiên Claude Code; chưa giao việc hoặc sửa code ở các repo đích. Claude sở hữu backend/contract, Codex sở hữu FE. Mỗi prompt là một phiên làm việc và một nhánh riêng.

## Cách chia việc

| Thứ tự | Việc | Repo | Giao Claude? | Phụ thuộc | Kết quả bàn giao |
|---|---|---|---|---|---|
| C0 | Đóng contract Web Chat v1 | `api-docs` | Có | Quyết định PM | OpenAPI + Socket doc nhất quán, chưa code |
| C1 | Directory tìm người | `Identity-Service` | Có | C0 contract | API ID/tên cho Landlord/Tenant |
| C2 | Rule tạo nhóm | `community-service` | Có | C0 contract | Min 3 người, title mặc định |
| C3 | Unread đúng nghĩa + summary | `community-service` | Có | C2 trên cùng nhánh/base | Một cách tính unread, endpoint summary |
| C4 | List/search/lookup conversation | `community-service` | Có | C3 trên cùng nhánh/base | Tìm toàn DB, direct trống ẩn, tên theo viewer |
| C5 | Event tin mới theo user room | `community-service` | Có | C4 trên cùng nhánh/base | Một event gọn để FE cập nhật mọi trang |
| G1 | Socket FE, màn chat và tích hợp | `fe` | Codex làm song song | Contract C0; API thật để kiểm chứng cuối | Luồng chat desktop end-to-end |

C0 cố định contract chung trước; Codex có thể làm nền FE trong lúc Claude hoàn thành C0. Sau đó Claude làm C1–C5, Codex tiếp tục FE theo contract đã ghi. Không cần Codex review/duyệt từng task của Claude; chỉ hỏi người dùng khi phải đổi business rule hoặc phạm vi. C1 có thể chạy song song với C2 vì khác repo. C2 → C3 → C4 → C5 phải tuần tự vì cùng sửa Community. Gateway đã route prefix `/users` về Identity và `/conversations` về Community; chưa cần task Gateway riêng nếu giữ các path đề xuất. DB migration/schema và `unaccent` extension do người dùng xử lý theo thỏa thuận trước đây; Claude phải báo chính xác prerequisite, không tự viết migration tay hoặc tuyên bố đã chạy DB.

Các prompt dưới đây yêu cầu Claude đọc `AGENTS.md`/skill của repo đích. Chúng chỉ nêu phạm vi sản phẩm; nếu thấy mâu thuẫn code/contract, Claude phải báo cụ thể, không tự nới scope.

## Prompt C0 — Đóng API và Socket contract

```text
Bạn làm một task tài liệu trong workspace D:\DUT\Ki 7\PBL6, chỉ sửa repo api-docs/. Không code service/FE. Hãy đọc quy ước repo và các nguồn theo thứ tự:
1. pm/phase-7/discovery/web-chat-v1-decisions.md
2. pm/phase-7/discovery/web-chat-v1-readiness-audit.md
3. api-docs/src/openapi.yaml, api-docs/src/paths/chat/conversations.yaml, api-docs/src/paths/chat/messages.yaml, api-docs/docs/community-socket-v1.md
4. api-docs/src/paths/users/users.yaml và schemas liên quan.

Mục tiêu: chuyển các quyết định Web Chat v1 thành contract có thể implement. Giữ response envelope, pagination, x-apidog-status, status/code/error và naming convention đang có. Cụ thể:
- GET /users/directory?q&pageNo&pageSize: auth Landlord/Tenant; chỉ tìm active Landlord/Tenant, loại caller/Admin/locked/deleted; tìm tên không phân biệt dấu tiếng Việt và chữ hoa/thường; response mỗi user chỉ id, name. Dùng path riêng để không thay quyền GET /users của Admin.
- Mở rộng GET /conversations: lọc chat tự do (`hasContext=false` hoặc tên query rõ nghĩa tương đương), q tìm theo group title hoặc displayName của người còn lại trong direct, kind=direct&otherUserId để lookup 0/1 mà không ghi DB. Mặc định/hành vi kết hợp query cần được mô tả tường minh; direct chưa có message không xuất hiện, group mới tạo chưa có message vẫn xuất hiện. Response list/detail có displayName theo người xem; direct dùng snapshot ConversationMember, group dùng title.
- GET /conversations/unread-summary: trả { totalUnreadCount }; tổng của tất cả conversation user được đọc; không tính system, có tính user/bot; read-only chỉ tới leftSequence.
- POST /conversations kind=group: ít nhất hai memberUserIds khác caller, title tùy chọn; không nhập thì server lưu tên mặc định từ snapshot thành viên ban đầu, giới hạn 255.
- Tài liệu Socket: thêm một event user-room cho message mới, payload { messageId, conversationId, sequence, senderUserId, senderName, conversationName, type, contentPreview, createdAt }; sequence là string như message REST. Chốt tên event, preview tối đa, hành vi user/bot/system, session của sender, direct đầu tiên và tránh toast trùng với message:created. Event không chứa unread count. Giữ các event cũ.
- Đảm bảo thứ tự route tĩnh /conversations/unread-summary với /conversations/{conversationId} được mô tả và không bị parse thành UUID; mô tả lỗi query sai, quyền, mã response.

Không đổi rule sản phẩm, không thêm ảnh/quản lý nhóm/context chat vào v1. Nếu cần DB extension để search không dấu, ghi prerequisite rõ trong contract và báo lại, không đoán đã có. Chạy npm run lint và npm run bundle trong api-docs nếu môi trường cho phép; ghi rõ lệnh nào thành công/thất bại. Trước khi kết thúc, tóm tắt contract đã sửa và danh sách file; chỉ hỏi người dùng nếu phải thay đổi business rule hoặc phạm vi. Các lựa chọn kỹ thuật còn lại hãy chọn hợp lý, ghi rõ để Codex dùng cùng contract. Không push/PR. Không sửa pm/ vì tài liệu PM đang được xử lý ở phiên khác.
```

## Prompt C1 — Identity directory tìm người

```text
Bạn implement riêng B1 trong Identity-Service/ của workspace D:\DUT\Ki 7\PBL6. Trước khi sửa, đọc Identity-Service/AGENTS.md, các skill BE tương ứng và contract GET /users/directory trong api-docs/ do C0 tạo; đọc pm/phase-7/discovery/web-chat-v1-decisions.md và web-chat-v1-readiness-audit.md. Nếu C0 chưa ghi contract thì hoàn thành C0 trước, đừng tự tạo API shape khác.

Yêu cầu: endpoint chỉ cho Landlord/Tenant active đã đăng nhập tìm user active thuộc Landlord/Tenant theo tên; loại chính caller, Admin, locked, deleted. Chỉ trả id/name, không lộ email, phone, role hay avatar. Query q tìm không phân biệt dấu tiếng Việt và hoa/thường, phân trang/sort ổn định trên DB. Dùng CQRS + query port theo cấu trúc Identity, DTO validation, success/error code và Swagger khớp OpenAPI. Không tái dùng GET /users của Admin theo cách làm rộng quyền endpoint đó. Gateway hiện có prefix /users → Identity; xác minh route hiện có và chỉ sửa Gateway nếu thực sự thiếu.

Giới hạn: không đổi schema User hoặc làm avatar; không viết migration. Nếu search không dấu phụ thuộc PostgreSQL unaccent/extension/index chưa có trong DB, ghi rõ lệnh/prerequisite cần người dùng áp dụng và giới hạn chưa thể kiểm thử; đừng giả vờ endpoint đã chạy với DB. Không fallback sang lọc kết quả sau khi phân trang vì sai totalItems. Không thêm package chỉ để xử lý một query nếu DB hiện có cách phù hợp.

Nghiệm thu: q='Nguyen' tìm được Nguyễn; q='an' không phân biệt hoa/thường/dấu; kết quả không chứa caller/Admin/locked/deleted và tối đa chỉ có id/name; pageNo/pageSize/totalItems đúng. Chạy npm run build, npm run lint; nếu có DB dev thì kiểm chứng truy vấn thật, nếu chưa có thì báo chưa kiểm chứng runtime. Không sửa repo khác, không push/PR; đưa diff summary, lệnh đã chạy, mọi prerequisite và giới hạn. Nếu code/contract lệch nhau, ghi blocker cụ thể trước khi tự đổi contract.
```

## Prompt C2 — Quy tắc tạo group

```text
Bạn implement riêng B5 trong community-service/ của workspace D:\DUT\Ki 7\PBL6. Đọc community-service/AGENTS.md, các skill BE liên quan, contract POST /conversations do C0 cập nhật trong api-docs/, pm/phase-7/discovery/web-chat-v1-decisions.md và web-chat-v1-readiness-audit.md. Chỉ bắt đầu sau khi C0 đã ghi contract chung.

Hiện code conversation-create cho phép memberUserIds rỗng và lưu title=null. Sửa để group tự do có ít nhất 2 người khác caller, tổng tối thiểu 3 người; UUID trùng/caller tự thêm không được tính để qua ngưỡng. Caller vẫn là admin. Nếu title bị bỏ trống hoặc chỉ whitespace, server lưu một title ổn định từ snapshot displayName của người tạo và các thành viên ban đầu theo quy tắc đã duyệt, không tính lại khi nhóm đổi người. Xử lý tên dài hơn giới hạn 255 và tên trùng một cách nhất quán. Direct behavior và context chat giữ nguyên. Validation hình dạng ở DTO, bất biến ở domain hoặc application đúng quy ước repo; dùng domain exception/code theo pattern hiện có, không tạo helper thừa.

Nghiệm thu: group 0/1 người khác bị từ chối; group >=2 người khác được tạo, title mặc định tồn tại và ổn định; title do caller nhập được giữ; caller admin, member khác member; không tạo group nếu Identity user lookup thất bại. Chạy npm run build, npm run lint. Không tạo/chạy migration hoặc sửa shared/; nếu schema không cho phép giải pháp thì báo prerequisite. Không sửa list/search/unread/Socket hay repo khác. Không push/PR; báo file đổi, kết quả kiểm tra và giới hạn còn lại.
```

## Prompt C3 — Unread và summary

```text
Bạn implement riêng B3 trong community-service/ của workspace D:\DUT\Ki 7\PBL6, trên branch/base đã chứa C2. Đọc community-service/AGENTS.md và skill BE, contract GET /conversations/unread-summary do C0 ghi, pm/phase-7/discovery/web-chat-v1-decisions.md và web-chat-v1-readiness-audit.md.

Hiện count unread trong message.repository.ts và typeorm-conversation-page.query.ts chưa loại message_type='system'. Tạo một quy tắc nhất quán cho list unreadCount, detail unreadCount, POST /messages/mark-read và endpoint tổng unread. Chỉ đếm tin từ member khác, type text/image/bot; system vẫn ở history nhưng không tăng unread. Tôn trọng membership active/read_only, leftSequence, lastReadSequence và isDeleted; summary tính toàn bộ hội thoại được phép đọc, không chỉ page đầu; userId lấy từ JWT, không nhận từ client. Static route /conversations/unread-summary phải đứng/resolve đúng trước :conversationId. Không sửa behavior cursor tăng dần.

Nghiệm thu: cùng một tập dữ liệu, tổng unread bằng tổng unreadCount của mọi conversation có quyền đọc; system=0, user/bot được tính, tin mình gửi=0; read-only không đếm sau leftSequence; mark-read một thiết bị trả unread mới và Socket read-updated hiện có vẫn đúng. Endpoint response/status/code khớp OpenAPI. Chạy npm run build, npm run lint; không có DB thì nêu rõ chưa chạy truy vấn thật. Không viết migration, không sửa repo khác, không sửa UI hoặc search. Không push/PR; gửi diff summary và rủi ro còn lại.
```

## Prompt C4 — List, search và direct lookup

```text
Bạn implement riêng B2 trong community-service/ của workspace D:\DUT\Ki 7\PBL6, trên branch/base đã chứa C3. Đọc community-service/AGENTS.md, skill BE, GET /conversations contract do C0 ghi, pm/phase-7/discovery/web-chat-v1-decisions.md và web-chat-v1-readiness-audit.md. Đọc kỹ TypeOrmConversationPageQuery, ConversationListRequestDto, ConversationDetailResponseDto và membership status.

Mở rộng GET /conversations để: lọc chat tự do theo context null; q tìm trên DB theo group title hoặc ConversationMember.displayName của người còn lại đối với direct, không phân biệt dấu tiếng Việt/hoa thường; kind=direct&otherUserId trả tối đa một direct đã có history, chỉ đọc và không tạo/reactivate membership. Mọi page/list/totalItems phải cùng filter trước phân trang. Direct chưa có message bị ẩn với cả hai người; group vừa tạo chưa có message vẫn hiện. Response list/detail có displayName phù hợp viewer: direct lấy snapshot member đối diện, group lấy title đã lưu; không gọi Identity từng hàng. Không đổi rule quyền: chỉ member active/read_only được đọc theo ranh giới hiện có. Sort vẫn mới nhất trước, tie-break ổn định. Tránh N+1 query.

Nghiệm thu: A tìm chat với B đã có tin mở đúng ID/history; nếu chưa có tin, lookup 0 kết quả và GET list không hiện chat trống; group trống hiện; q='Nguyen' tìm được Nguyễn ở group/direct; pageSize/totalItems đúng trên toàn DB; không lộ conversation người ngoài; filter kết hợp sai trả lỗi contract. Chạy npm run build, npm run lint; nếu không có DB thì báo chưa kiểm chứng SQL runtime. Không viết migration, không sửa unread (đã thuộc C3), không sửa Socket/FE/repo khác. Nếu cần unaccent/index chưa có, báo prerequisite rõ. Không push/PR; bàn giao file đổi, lệnh chạy và vấn đề còn lại.
```

## Prompt C5 — Event tin mới theo user room

```text
Bạn implement riêng B4 trong community-service/ của workspace D:\DUT\Ki 7\PBL6, trên branch/base đã chứa C4. Đọc community-service/AGENTS.md và skill BE liên quan, pm/phase-7/discovery/web-chat-v1-decisions.md, web-chat-v1-readiness-audit.md và contract event user-room do C0 ghi trong api-docs/docs/community-socket-v1.md.

Hiện ChatGateway chỉ phát message:created tới conversation room. Bổ sung event mới tới user room của từng thành viên được phép nhận tin chat mới để FE cập nhật badge/toast trên mọi trang mà không join mọi conversation. Payload đúng contract C0: messageId, conversationId, sequence dạng string, senderUserId, senderName, conversationName theo từng recipient, type, contentPreview, createdAt. Chỉ phát sau khi message đã lưu thành công, không phát lại khi POST /messages retry cùng clientMessageId. Text preview ngắn theo contract; ảnh/bot/system xử lý theo contract. Không tạo Notification inbox row. Giữ message:created hiện có cho conversation room và read-updated/available/access-revoked; không nới quyền join.

Chú ý: tên direct khác nhau theo từng người nhận, group dùng title; không dùng tên từ lastMessage. Không gửi event tới member đã mất quyền; read-only chỉ có history giới hạn qua REST, không nhận tin mới. Session của sender phải theo đúng contract để tab gửi và tab còn lại không lệch list; FE sẽ không tạo toast/unread cho chính sender. Tránh N+1 Identity lookup; tên có snapshot trong ConversationMember. Nếu payload cần truy vấn thêm member/conversation, dùng port đúng tầng Clean Architecture, không truy cập DB service khác.

Nghiệm thu: A gửi một tin, B ở trang khác nhận đúng một user-room event; B đang join chat nhận cả hai loại event nhưng có cùng messageId để FE khử trùng; retry cùng clientMessageId không phát lại; C đã bị kick không nhận; direct recipient thấy tên chat theo viewer; group dùng title; system message không tạo chat toast/unread. Chạy npm run build, npm run lint; nếu chưa có DB thì báo rõ chưa chạy tích hợp thật. Không viết migration, không sửa FE hoặc repo khác. Không push/PR; gửi diff summary, contract thực tế và mọi giới hạn.
```

## Phần Codex làm song song trong Goal chính

Codex chỉ sửa `fe/`: nền Socket dùng chung, route/guard, directory + list + history, draft direct + gửi text/retry, unread/mark-read/toast và UI desktop. FE lấy contract C0 làm chuẩn; trong lúc C1–C5 chưa xong, chỉ làm phần nền và giao diện dùng DTO đã ghi, không dựng mock API thành dữ liệu thật. Hai bên không sửa cùng repo. Sau khi backend sẵn sàng và người dùng áp schema DB, kiểm chứng hai tài khoản/two tabs qua Gateway rồi xử lý chênh lệch contract nếu có. Nếu xuất hiện thay đổi business rule hoặc phạm vi, hỏi người dùng chốt; khác biệt kỹ thuật nhỏ thì hai bên đồng bộ contract mà không cần một vòng duyệt riêng.

