# Rà soát độ bao phủ Phase 10 — 14/11/2026

> **Cập nhật sau rà soát:** Đã tạo P10-12–30 để tách bot reminder, phòng tenant, quản lý khách thuê, kiểm chứng Chat v2, admin, chọn tenant và các capability đang deferred. Xem [tracker](../issues/README.md) để biết trạng thái và blocker mới nhất; các bảng bên dưới giữ nhận định tại thời điểm kiểm tra ban đầu.

## Kết luận và phương pháp

**Chưa đủ để nói đã cover toàn bộ API và FE.** Phase 10 có các issue cụ thể P10-01–09, hai issue discovery P10-10/11 và cần tiếp tục tính cả issue Phase 6–9. Nhiều nhóm trong P10-11 chưa có task implementation độc lập, acceptance hoặc owner. Tài liệu kiểm kê `api-inventory.md` được tạo lượt trước bị lỗi mã hóa tiếng Việt (`?` thay cho chữ có dấu) và dùng `operationId` làm dấu hiệu sơ bộ; không dùng nó để kết luận số API thiếu. Cần tạo lại inventory có kiểm tra method/path và đối chiếu YAML nguồn.

Rà soát tĩnh `pm`, OpenAPI, controller, route FE, Gateway và một số use case tại workspace hiện tại. Có thể có route/flow tồn tại nhưng chưa được phát hiện hoặc code chưa hoạt động đúng; chỉ kết luận theo bằng chứng cụ thể. Chưa gọi service, xem PR, trạng thái deploy hay dữ liệu thật.

| Repo | Branch và commit | Trạng thái ảnh hưởng nhận định |
|---|---|---|
| `fe` | `feature/user-avatar-url` · `15975a9` | Hai file hiển thị occupancy còn sửa chưa commit. |
| `community-service` | `feature/user-avatar-url` · `49f445f` | Rất nhiều file thay đổi chưa commit; chỉ phản ánh workspace, không khẳng định đã merge/deploy. |
| `Tenancy-Service` | `feature/user-avatar-url` · `3f91141` | Không có thay đổi chưa commit được báo. |
| `Identity-Service` | `feature/user-avatar-url` · `4d2efff` | Có sửa media/user và file mới chưa commit. |
| `api-docs` | `feature/user-avatar-url` · `b90ef8f` | Workspace sạch theo git status. |

## API — phát hiện theo nhóm

| Nhóm và bằng chứng | Trạng thái / issue |
|---|---|
| `PUT /contracts/{id}/apply-template`, `POST /contracts/{id}/generate-draft-document`: có OpenAPI và FE client; `Tenancy-Service/.../contract.controller.ts` không khai báo route; chỉ có GET template. | Khoảng thiếu trên baseline; P10-06 đã có. P6-01c ghi Done, cần kiểm tra commit/nhánh/deploy trước khi kết luận regression. |
| `GET /me/room-hub`: có YAML designing nhưng không thấy controller; `room.controller.ts` có `/me/rooms` cho flow khác. | Chỉ gom vào P10-11. Cần task contract + backend + FE nếu chốt scope; contract hub chứa cả issue/payment đã deferred. |
| `GET/POST/DELETE /me/favorite-rooms`; 4 operation roommate profile; 5 operation match request: OpenAPI designing, không thấy implementation theo tên/path trong các service đã rà. | P10-11 chỉ là discovery, chưa có issue implementation. P1-D28 đánh dấu matchmaking Stretch; cần xác minh owner, API và scope trước khi giao. |
| 6 operation `/issues`/`/me/issues`: OpenAPI designing; không thấy module IssueReport trong các service. | Đã ghi nhận P10-11; IssueReport theo P6-D61/P9-D83 là deferred, không được mặc định tính vào MVP. |
| `POST /conversations/{id}/bot-reminders`: OpenAPI designing, không thấy route/handler; Phase 7 backlog CB-15 đã mô tả reminder thủ công, không có cron. | Không có issue implementation riêng trong P10-01–11; cần tách CB-15 sau khi xác minh template/resource contract. `ocr_result` cần đối chiếu D78 vì OCR đã hoãn. |
| `GET /dashboard`, `GET /audit-logs`, `GET /audit-logs/{id}`: designing; không thấy controller trong service rà soát; FE admin placeholder. | P10-10 là discovery chứ chưa phải task backend/FE giao code. Transaction volume phụ thuộc payment deferred; cần chốt nguồn dữ liệu. |
| `PUT /buildings/{id}/vietqr-config`: designing; không thấy route tương ứng trong bốn repo. | P10-11 chỉ theo dõi phạm vi; đối chiếu P6-D61/D72 và Identity payout account trước khi giao. |
| Payment + deposit settlement: 6 operation trong bundle `deprecated`; chưa rà Payment service vì không thuộc bốn repo yêu cầu. | Deferred theo P6-D61, không gọi là thiếu trong MVP hay khẳng định implementation của repo khác. |
| `POST /auth/refresh`, `/auth/logout` và GET/PATCH/DELETE `/users/{id}`: operationId không trùng tên nhưng route có trong Identity controllers. | Sai lệch tên không phải API thiếu; API status/Swagger alignment có thể kiểm tra riêng. |
| `GET /me/invoices`: Tenancy có controller và YAML developing; `api-gateway/src/constants/route-paths.constants.ts` không có prefix `/me/invoices` và `/me` trỏ Identity. | Gateway có khả năng chuyển request sang sai service; P6-02g4 ghi gateway pending và P8-05 FE phụ thuộc. Cần kiểm tra route resolver, không tạo issue trùng nếu tiếp tục P6-02g4. |
| P9-D83 `system` category và lock events: Community `notification-category.enum.ts` chưa có `system`; Tenancy identity lifecycle constants chưa có `user.locked`/`user.unlocked`. | Là gap cụ thể đã có P9-05–07, còn Open; không thay bằng P10 issue hoặc kết luận đã end-to-end. Invoice notification theo P9-08 và smoke P9-09 vẫn cần kiểm chứng. |

## Web — màn hình và khả năng chưa được bao phủ đủ

| Luồng | Code / ảnh hưởng | Coverage |
|---|---|---|
| Chủ nhà: danh sách và chi tiết khách thuê | `/tenants` và `/tenants/:id` render `DashboardOverview` trong `landlord.routes.tsx`; chưa có màn nghiệp vụ. | Không có issue implementation riêng P10; cần đối chiếu API/query có quyền và rule dữ liệu trước khi chia FE/BE. |
| Tenant: phòng của tôi và dashboard | Menu tenant trỏ `/rooms`, route hiện thuộc landlord; tenant dashboard render `DashboardOverview`; room hub API còn designing. | P10-11 chỉ discovery, không có FE/BE task riêng. Không nhầm `/me/rooms` landlord với tenant room hub. |
| Tenant: hợp đồng | Menu tenant trỏ route contract được bảo vệ landlord, chưa thấy FE `/me/contracts`. | Đã có P10-07. |
| Tenant: hóa đơn | Có route dispatcher và feature tenant invoice; Gateway thiếu prefix `/me/invoices` như trên. | P8-05 + P6-02g4, cần E2E, không coi sự tồn tại của component là xong. |
| Admin: thống kê và audit | `/admin`, `/admin/audit-logs` là placeholder. | P10-10 discovery; còn thiếu issue code tách backend/FE khi chốt contract. |
| Settings/password | Settings placeholder; FE có API/mutation đổi mật khẩu nhưng chưa có consumer. | P10-09 cover đổi password; không tự hiểu issue này cover mọi mục settings. Notification preference đã có feature riêng cần kiểm thử qua P7-15. |
| Tenant: roommate/profile và issue report | Route roommate, issue list/detail/create là placeholder. | P10-11 chỉ discovery; theo decision hiện hành roommate matching Stretch và IssueReport deferred. |
| Form tạo hợp đồng/thêm thành viên | `contract-create-form-fields.tsx` và `add-member-modal.tsx` chỉ nhập tên/SĐT; FE AGENTS yêu cầu chọn tài khoản hoặc nhập tay, còn P6-D74 từng loại directory khỏi Phase 6. P9-02 đã bổ sung link existing tenant ở backend. | Có xung đột tài liệu/quy tắc, cần PM xác nhận áp dụng decision mới nhất trước khi mở task FE; không gọi đây là thiếu nghiệp vụ đã duyệt. |
| Chat v2 và attachment | Có code/handoff P7-D83 và nhánh Community/Identity đang thay đổi; v2 handoff ghi chưa E2E. P7-18 là kiểm chứng v1, không mặc nhiên cover toàn bộ v2. | Cần task kiểm chứng v2 read receipt, typing, search, reply, reconnect, quyền và attachments theo contract/nhánh hiện hành; kiểm tra issue hiện có trước khi tạo mới. |

## Điểm chất lượng issue cần sửa trước khi giao

- P10-11 quá rộng: gom nhiều capability và bị blocked; không thể xem là đã cover các task implementation của từng actor/repo.
- P10-10 chỉ quyết định nghiệp vụ, chưa có implementation issue khi điều kiện được duyệt.
- P10-02, P10-03, P10-04 và P10-08 tự đưa ra chi tiết tính toán, phạm vi thẻ hoặc search mới; theo P6-D75 issue không tự chốt business rule. Cần API owner/PM xác nhận và sửa contract/decision khi cần trước khi giao.
- Tracker P10-03 ghi đang thực hiện vì sửa format; không đồng nghĩa backend occupancy hoặc thống kê toàn bộ đã hoàn thành.
- Tracker P9 vẫn Open dù có một số commit P9; cập nhật trạng thái sau khi đối chiếu acceptance và evidence, không tự đánh Done.

## Giới hạn và thứ tự tiếp theo

1. Lập lại ma trận theo từng method/path từ YAML canonical, ánh xạ Gateway → service controller → handler → FE → issue/status; giữ nhãn `unknown` nếu chưa xác minh. Đối chiếu mọi operation, không dùng tên operationId hoặc `x-apidog-status` làm bằng chứng duy nhất.
2. Hoàn tất và kiểm thử carry-over P6-02g4, P8-05, P9-05–09; kiểm tra P10-06 trên môi trường tích hợp.
3. Tách implementation task cho bot reminder thủ công, tenant room/dashboard, quản lý tenant và chat v2 sau khi đối chiếu scope/issue gốc. Với room hub, admin dashboard/audit và các scope deferred, ghi decision/blocker cụ thể.
4. Không có bằng chứng từ rà soát này cho phép khẳng định toàn bộ API/FE đã kiểm kê đầy đủ hoặc đã sẵn sàng release.
