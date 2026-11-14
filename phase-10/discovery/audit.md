# Rà soát Phase 10 — 13/11/2026

## Phạm vi và độ tin cậy

Đối chiếu tĩnh yêu cầu/decision, tracker P5–P9, API contract và các entrypoint liên quan trong bốn repo. Đây không phải xác nhận đã chạy end-to-end hoặc kiểm kê mọi nhánh/PR; một TODO hoặc file tồn tại không đủ chứng minh feature đã xong. Chưa kết nối tracker từ xa và chưa đổi trạng thái issue cũ. API docs được dùng làm contract đối chiếu, không phải repo kiểm kê thứ năm.

| Repo | Baseline lúc đọc | Lưu ý |
|---|---|---|
| `fe` | `feature/shared-user-avatar`, `7b7411b` | Có thay đổi chat/media chưa commit, gồm file mới; không coi là đã merge. |
| `community-service` | `feature/chat-v2-after-sequence`, `fbc7c97` | Có thay đổi chat attachment và migration chưa commit. |
| `Tenancy-Service` | `main`, `3f91141` | Workspace sạch; commit P9-02, P9-04 và reconcile xuất hiện trong log. |
| `Identity-Service` | `main`, `7fd1b84` | Có thay đổi media/attachment và migration chưa commit. |
| `api-docs` | `docs/chat-v2-after-sequence` | Có thay đổi contract và bundle chưa commit; không xác nhận trạng thái deploy. |

Không đọc hoặc thay đổi file môi trường, private key hay dữ liệu người dùng. Scope hiện hành theo `requirement.md`, Phase 6 decisions và P9-D83/D84; OCR, Payment/settlement và IssueReport không tự đưa vào phase này.

## Phát hiện xác nhận và issue

| Phát hiện / bằng chứng | Tác động | Quyết định |
|---|---|---|
| `Tenancy-Service/src/modules/room/application/commands/room-delete/room-delete.command.handler.ts` khóa và xóa Room nhưng để TODO kiểm tra active Contract; P2-D50 và P5-09c xác nhận kiểm tra đã hoãn. | Có thể xóa phòng vẫn có contract hiệu lực. | [P10-01](../issues/P10-01-room-delete-active-contract.md). |
| `my-building-list.response.dto.ts`, `my-building-detail.response.dto.ts`, `admin-building-detail.response.dto.ts` gán occupancy cố định; P5-08c/d gọi đây là dữ liệu tạm. | Landlord/admin nhìn số phòng thuê và tỷ lệ sai. | [P10-02](../issues/P10-02-building-occupancy.md). |
| `fe/src/features/buildings/hooks/use-building-list.ts` cộng Room từ một page nhưng dùng tổng tòa từ pagination; `building-list-columns.tsx` parse chuỗi `%` như number rồi thêm dấu `%`. | Tổng hợp sai phạm vi và hiển thị tỷ lệ sai. | [P10-03](../issues/P10-03-web-building-metrics.md). |
| Cùng hook FE giới hạn search ở 100 bản ghi đầu; `api-docs/src/paths/buildings/me-buildings.yaml` chưa có filter search. | Không tìm thấy tòa phù hợp ngoài trang đã tải. | [P10-04](../issues/P10-04-building-search.md). |
| `room-detail.response.dto.ts` để contract/member/readings rỗng; `fe/src/features/rooms/pages/room-detail-page.tsx` truyền các field này cho card và kết luận trống. `GET /rooms/{id}` là public trong OpenAPI. | Phòng có contract/readings có thể bị mô tả sai; không thể lấp TODO bằng cách công khai dữ liệu nhạy cảm. | [P10-05](../issues/P10-05-room-detail-data.md), dùng API landlord có auth sau khi xác minh contract. |
| OpenAPI có hai operation apply-template/generate-draft; FE có client, nhưng `Tenancy-Service` hiện không có route tương ứng; P6-01c ghi Done. | Luồng ký tay bị ngắt trên baseline hiện tại; chưa xác minh môi trường chạy. | [P10-06](../issues/P10-06-contract-template-regression.md). |
| OpenAPI có `GET /me/contracts`; FE menu tenant dùng `/contracts`, route chỉ cho landlord. | Tenant không mở được hợp đồng từ menu. | [P10-07](../issues/P10-07-tenant-contracts-web.md). |
| `landlord-dashboard-page.tsx` chỉ tải 20 tòa và dùng items rỗng khi request lỗi. | Tổng bị cắt ở trang đầu, lỗi bị mô tả là không có tòa. | [P10-08](../issues/P10-08-landlord-dashboard-metrics.md). |
| Identity đã có `PUT /me/password`; FE có API/schema/mutation nhưng không có consumer, settings placeholder. | User không có UI đổi mật khẩu. | [P10-09](../issues/P10-09-change-password-web.md). |
| Admin dashboard/audit là placeholder; OpenAPI đang designing và chưa thấy controller. | Chưa có dữ liệu thật cho UI; Payment volume và nguồn cross-service chưa chốt. | [P10-10](../issues/P10-10-admin-dashboard-audit.md) chờ PM/API owner. |

## Đối chiếu operation và phạm vi

[Kiểm kê 130 operation](api-inventory.md) được lập từ bundle OpenAPI hiện có và so với `operationId` trong controller. 93 operation có tên trùng; 37 cần đối chiếu theo method/path hoặc service sở hữu. Đây là bước sàng lọc, không phải số API thiếu. Ví dụ `refreshSession`, `logoutSession`, `getUserById`, `updateUserById`, `deleteUserById` không trùng tên nhưng controller đã có route tương ứng. API `designing` không mặc nhiên bị thiếu; `deprecated` không phải yêu cầu triển khai.

Room hub/favorite, roommate/matching, IssueReport, bot reminders, VietQR/payment và các placeholder Web liên quan được ghi ở [P10-11](../issues/P10-11-unimplemented-api-scope-review.md) để PM chốt trạng thái và tách issue triển khai khi có rule. Phần nào thuộc P5–P9 thì tiếp tục dùng ID cũ. Các API chưa được kiểm tra method/path thủ công toàn bộ vẫn là `unknown`; không suy ra tính đầy đủ của hệ thống từ bảng kiểm kê.

P10-03: đã sửa trực tiếp format phần trăm desktop/mobile trong workspace FE; phần tổng hợp đúng phạm vi và dependency P10-02 còn mở, không đánh dấu Done.

## Việc giữ issue cũ hoặc cần xác minh

- **P8-02–05:** FE đã có thư mục billing, users và tenant invoice, nhưng sự tồn tại của UI không xác nhận đủ acceptance. Tiếp tục dùng issue P8 tương ứng; P8-09 giữ smoke chung. Không sao chép sang Phase 10.
- **P9-01/02/04:** Tenancy log có `dc993d6`, `3f91141`, `30993b6`; community code có contract context subscriber. Tracker vẫn ghi Open. Cần đối chiếu đủ các repo, deploy, PR và acceptance rồi cập nhật tracker theo bằng chứng, không tự chuyển Done. P9-01 còn mô tả acceptance registration cũ trong khi P9-D84 yêu cầu chỉ link sau email verification; sửa issue gốc theo D84 khi đồng bộ.
- **P9-03, P9-05–09:** tiếp tục theo ID gốc; chưa có đủ bằng chứng về toàn bộ flow broker, notification, lock/grace và smoke để kết luận hoàn thành. Không tạo issue trùng.
- **Community/Identity media:** `media-owner-resolver.registry.ts` đã map `CONVERSATION` sang `CommunityConversationOwnerResolver`; `UnavailableOwnerResolver` vẫn được map cho `MESSAGE` và `ISSUE_REPORT`. Chat attachment đang dùng scope conversation và có thay đổi chưa commit; IssueReport deferred. TODO chung trong file resolver không đủ chứng minh cần issue mới. Cần kiểm tra PR/delivery thực tế trước khi xử lý các owner type còn lại.
- **Building certificates:** DTO đặt mảng rỗng ban đầu, nhưng `my-building.controller.ts` và `admin-building.controller.ts` gán dữ liệu media về sau. Không coi default DTO là bằng chứng tính năng thiếu; quyền và failure path cần xem trong P6-04/P6-12 hiện có.
- **Room public/media:** `room-get-detail.query.handler.ts` đã resolve `photoUrls`; ghi chú TODO ở response DTO có thể đã cũ. Public search và landlord contact thuộc P5-09d; chỉ kết luận sau khi đối chiếu acceptance gốc và API thực tế.
- **Chat v2:** handoff tại `phase-7/discovery/web-chat-v2-backend-handoff.md` nói chưa kiểm tra end-to-end và các nhánh hiện còn thay đổi. P7-18 là issue kiểm chứng chat hiện có; dùng lại để theo dõi bằng chứng phù hợp, không khẳng định chat v2 đã hoàn thành hoặc tạo bản sao.
- **P8-07/08:** là placeholder chưa có flow, không tự gán nội dung; P9-08 đã mô tả invoice notification. Các điểm còn mơ hồ phải được PM/API owner chốt trước khi giao.

## Giới hạn rà soát

Chưa chạy service, kiểm tra DB/Gateway/RabbitMQ/Socket, tình trạng staging, PR hay GitHub issue. Chưa kiểm toán đầy đủ mọi endpoint, bảo mật hoặc UI state; các phát hiện trên là backlog được xác nhận từ phần đã kiểm tra, không bảo đảm đã phát hiện mọi task còn thiếu. Ownership, ước lượng, ngày giao và trạng thái thực tế cần PM xác nhận. Các thay đổi chưa commit thuộc workspace hiện tại được giữ nguyên.
