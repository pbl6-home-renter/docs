# Plan sửa Backend cho mobile tenant — 18/11/2026

**Điều chỉnh theo yêu cầu người dùng:** bỏ P10-32 và toàn bộ CLI maintenance/bootstrap, API snapshot, dry-run/apply cùng hướng dẫn sửa dữ liệu cũ. Giữ consumer RabbitMQ hiện có và các sửa lỗi create/activate, response phòng, ảnh, favorite. P10-D91 thay thế phạm vi script của plan gốc.

Trạng thái cập nhật 18/11/2026: người dùng đã duyệt triển khai. Backend và OpenAPI đã có code local, có test unit/SQL PostgreSQL; chưa merge/deploy hoặc sửa dữ liệu server. Xem [bằng chứng triển khai và phần cần nghiệm thu](../phase-10/discovery/mobile-backend-implementation.md). Các phát hiện bên dưới giữ lại baseline audit trước khi sửa. Task theo dõi tại [Phase 10](../phase-10/issues/README.md), không tạo `tasks/todo.md` trùng tracker. Favorite backend/API được duyệt theo P10-D90, thay thế trạng thái deferred của plan gốc cho slice này.

## Phạm vi và bối cảnh

Người dùng báo tạo hợp đồng phía landlord bằng đúng SĐT nhưng mobile tenant không thấy phòng; yêu cầu kiểm tra thêm A1/A2/A3/A6 trong danh sách Backend gửi ngày 18/11. Ưu tiên khôi phục luồng đang thuê và đồng bộ response với mobile. Không đổi rule tenant phải có tài khoản mới được landlord tạo hợp đồng.

Rentify đang ở đợt hardening/demo It7, 16–22/11 theo `PROJECT_PLAN.md`; các sửa lỗi liên quan thuộc backlog Phase 9/10. Plan này chưa gán thời gian hay người thực hiện chính thức. Các quyết định nền: P0-D29 cho tenant không login; P9-D83/D84/D85 cho liên kết tenant active qua projection SĐT và transactional outbox/inbox; P10-D87 cho room hub. Không cần mở tenant picker P10-23 để sửa lỗi liên kết tự động.

## Bằng chứng đã kiểm tra

Baseline local: Tenancy `a49af96`, Identity `97e59cc`, api-docs `35ae4ad`, fe `07ce0aa`, mobile `5bbc3a5`. Đây là HEAD trong workspace, chưa xác nhận trùng image đang deploy. Giữ nguyên thay đổi tài liệu có sẵn trong `pm/phase-8/` và `pm/Report/`.

| Vấn đề | Kết luận | Bằng chứng |
|---|---|---|
| Đúng SĐT nhưng chưa thấy phòng | Có lỗ hổng BE: account có trước hợp đồng có thể không được link | `contract-create.command.handler.ts` chỉ nhận `command.tenantId`; `contract-activate.command.handler.ts` tạo representative từ `contract.tenantId`, không tra projection ở cả hai bước |
| Vì sao thêm member có thể link mà đại diện không link | Hai luồng xử lý khác nhau | `contract-member-add` và `contract-member-update` đã dùng `TenantUserProjectionPort`, còn create/activate chưa dùng |
| Account đăng ký sau hợp đồng | Đã có consumer reconcile, cần xác minh môi trường thật | `IdentityLifecycleSubscriber.onUserChanged` chuẩn hóa phone, chỉ nhận tenant active, ghi projection và link record NULL trong một transaction; inbox dedup |
| Điều kiện xem hợp đồng/phòng | API xác thực bằng user ID, không dùng phone làm quyền | `applyContractTenantAccess` yêu cầu `contract.tenantId` hoặc member hiện tại khớp user ID; `/me/room-hub` chỉ trả active; Web lọc active qua `/me/contracts` |
| Hợp đồng vừa tạo | Mới ở trạng thái draft | `ContractEntity.create` luôn đặt DRAFT; activate cần media hợp đồng đã ký. Chưa có mã/trạng thái hợp đồng cụ thể của người dùng |
| A1: địa chỉ danh sách | Xác nhận trên gateway: thiếu `ward`, `buildingName` | GET `/api/v1/rooms?pageSize=5` trả 200, 4 phòng. Repository đã select ward nhưng DTO bỏ ward; chưa select buildingName |
| A1: địa chỉ chi tiết | Xác nhận trên gateway cho một phòng: thiếu `address`, `ward`, `province` | GET `/rooms/06dffafa-62f4-4e28-bf3f-d1a2f3ab2f5b` trả 200. Detail query/DTO chưa map các trường này. Spec detail hiện cũng chưa khai báo địa chỉ, khác nhận định trong file đầu vào |
| A2: ảnh | Xác nhận 4 phòng công khai đều có danh sách media/URL rỗng; spec list vẫn dùng thumbnailUrl | BE có lookup URL từ Identity, chưa có ảnh thật để xác minh chuỗi upload → attach → hiển thị. Không kết luận hỏng storage chỉ vì ảnh rỗng |
| A3: chủ trọ | Lỗi implementation được xác nhận | Detail DTO đặt `landlord = null` và TODO không điền dữ liệu. Gateway trả null ở mẫu kiểm tra. Identity thực tế đã có GET nội bộ `/internal/users?ids=...` trả name/phone |
| A6: yêu thích | Local chưa triển khai, không chỉ là giả thuyết thiếu tenant profile | Gateway route `/me/favorite-rooms` trỏ Tenancy; tìm toàn bộ `Tenancy-Service/src` không có controller/service/persistence favorite; list gán cứng `isFavorited = false`. Spec còn designing; đã có P10-24 |

Các HTTP trên được gọi không token, chỉ đọc dữ liệu công khai. Chưa kiểm tra authenticated `/me/contracts`, `/me/room-hub`, favorite hoặc DB/queue trên server; 404 favorite khi đã login là thông tin do báo cáo cung cấp, không phải kết quả tự tái hiện ở lượt này.

Mobile local chỉ có MainActivity mẫu, không có màn/API đang được báo lỗi. Vì vậy chưa xác nhận mobile thực tế gọi `/me/contracts`, `/me/room-hub`, hay dùng nhầm `/rooms` / `/me/rooms`. `/rooms` là tìm phòng available công khai; `/me/rooms` dành landlord; hai route này không thay cho phòng đang thuê của tenant. Tài liệu nhắc `CreateRoomActivity`/`BuildingWardResolver` thuộc bản mobile khác bản local, chưa được tự kiểm chứng.

## Nguyên nhân và cách đối chiếu ca thực tế

Luồng có lỗi rõ trong code:

1. Tenant đã xác minh email, event Identity tạo projection user ID ↔ phone.
2. Landlord tạo hợp đồng chỉ nhập tên/SĐT. Handler không tra projection, lưu `tenantId = NULL`.
3. Khi activate, representative cũng được tạo với ID NULL; snapshot `contract.activated` không có tenant này.
4. API tenant kiểm tra user ID nên không trả hợp đồng/phòng đó. Không có event Identity mới thì consumer không tự chạy lại để bù.

Đây là nguyên nhân khả dĩ mạnh, chưa phải xác nhận record cụ thể của người dùng. Trước khi sửa dữ liệu ca này, đọc status hợp đồng, ID đại diện/member, account role/status, phone chuẩn hóa, projection và chuỗi outbox/inbox tương ứng. Không sửa mobile bằng cách bỏ phân quyền hoặc cho tenant tự gửi phone để lấy phòng.

Phân nhánh debug: draft → chưa phải phòng đang thuê; active + ID NULL → kiểm tra/link theo plan; active + ID đúng nhưng API rỗng → kiểm tra membership/filter/quyền; API có dữ liệu nhưng UI rỗng → kiểm tra DTO, endpoint, cache của đúng bản mobile. Phòng occupied biến mất khỏi `/rooms` là hành vi tìm kiếm công khai, không phải bằng chứng mất quyền phòng đang thuê.

## Quyết định thiết kế đề xuất

- Tái sử dụng `TenantPhone` và projection active tenant hiện có. `0...` và `+84...` cùng chuẩn; không fuzzy match hoặc tự gán account khi phone khác. `tenantId` đã chỉ định được giữ theo contract hiện hành, không tự chuyển liên kết lịch sử.
- Resolve ở create; activate kiểm tra lại khi ID vẫn NULL để hỗ trợ draft cũ và projection đến muộn. Gán ID trước khi tạo representative và activation snapshot. Không gọi HTTP Identity trong transaction create/activate.
- Đồng bộ thứ tự khóa phone → contract → room/member với consumer/member mutation. Activate cần đọc snapshot phone trước khóa và re-read/validate dưới khóa; không thêm phone lock sau khi đã khóa contract gây đảo thứ tự với consumer.
- Không bổ sung maintenance/bootstrap/replay script cho dữ liệu cũ. Liên kết tenant tiếp tục qua create/activate và consumer lifecycle hiện có theo P10-D91.
- Response phòng lấy địa chỉ/tên tòa từ building, contact từ Identity qua internal GET. Chỉ map contact `id/name/phone` theo spec; không đưa email/full internal response ra public API. Lỗi Identity không được che thành contact giả.
- Chốt `photoUrls` làm contract ảnh list/detail theo yêu cầu đầu vào; đối chiếu consumer còn dùng thumbnailUrl trước khi xóa field cũ. Bỏ district ở các schema địa chỉ phòng liên quan, không xóa trường district của domain khác như roommate chỉ do trùng tên.
- Favorite dùng lại P10-24. Việc lập plan không tự đổi trạng thái deferred/designing thành đã triển khai. Thống nhất rule với API owner trong task trước code; không giả lập thành công hoặc trả 200 rỗng để che module chưa có.

## Task theo thứ tự

| Thứ tự | Task | Phụ thuộc | Mục tiêu |
|---|---|---|---|
| 1 | [P10-31](../phase-10/issues/P10-31-contract-representative-phone-link.md) | P9-01/02 hiện có | Link representative ở create/activate, kiểm thử thứ tự event và cạnh tranh |
| — | [P10-32](../phase-10/issues/P10-32-tenant-link-reconciliation.md) | — | Đã bỏ theo yêu cầu người dùng; không có script fallback/repair |
| 3 | [P10-33](../phase-10/issues/P10-33-room-address-response.md) | Độc lập | Trả địa chỉ và tên tòa cho list/detail |
| 4 | [P10-34](../phase-10/issues/P10-34-landlord-contact-lookup.md) | Internal users API đã có | Port/adapter contact chủ trọ |
| 5 | [P10-35](../phase-10/issues/P10-35-room-landlord-response.md) | P10-34 | Điền landlord vào detail và kiểm tra response |
| 6 | [P10-36](../phase-10/issues/P10-36-room-photo-contract-and-smoke.md) | Độc lập | Chuẩn hóa spec ảnh, kiểm tra ảnh thật; upload UI mobile là follow-up riêng |
| 7 | [P10-24 hiện có](../phase-10/issues/P10-24-favorite-rooms.md) | Rule/ownership trong P10-24 | Thiết kế/triển khai favorite theo backlog, không tạo module trùng |
| 8 | [P10-37](../phase-10/issues/P10-37-mobile-backend-contract-verification.md) | Các bản sửa liên quan | Đồng bộ spec/bundle và nghiệm thu qua đúng bản mobile |

Mỗi thay đổi API kèm YAML nguồn và bundle trong cùng đợt giao tương ứng; P10-37 là kiểm tra tổng hợp, không phải lý do trì hoãn spec đến cuối. Các task có file dự kiến/AC/verification trong issue. Chia riêng PR backend, spec hoặc test khi vượt khoảng 5 file thay đổi chức năng; luôn giữ dependency và contract nhất quán. Chưa ước lượng points/giờ vì chưa có đúng source mobile và dữ liệu ca lỗi.

## Checkpoint và nghiệm thu

- [ ] Sau P10-31: tenant đã có account → tạo draft → ký/activate → API trả phòng; consumer lifecycle hiện có tiếp tục liên kết representative/member và chat theo nghiệp vụ gốc. Không có bước chạy script repair.
- [ ] Sau P10-33/35: list có `buildingName/ward`, detail có `address/ward/province/landlord`; lỗi phụ thuộc và phòng không tồn tại được kiểm tra; không lộ thêm field Identity.
- [ ] Sau P10-36/24: ảnh đã complete và attach tải được bằng GET nội dung ảnh; favorite lưu/xóa/list theo đúng user, tenant mới chưa lưu nhận 200 rỗng sau khi tính năng đã triển khai.
- [ ] P10-37: đúng mobile branch/build; parse response thật; tenant khác không thấy phòng/hợp đồng của ca thử; empty/error phân biệt; refetch sau activate/reconcile hiển thị dữ liệu; spec bundle khớp server.
- [ ] PM review các PR theo quy ước repo; chỉ đánh dấu Done khi có evidence, không dùng unit test thay cho nghiệm thu deploy.

Ma trận liên kết bắt buộc: account trước hợp đồng; hợp đồng trước account đã verify; account verify trước/sau activation; event Identity đã consume trước deploy; `0`/`+84`; ID tường minh; phone không khớp; account pending/locked/deleted/sai role; event trùng; hai tenant khác phòng; draft và active. Với member đã rời, kiểm tra rule truy cập hiện hành riêng, không nhân tiện đổi rule đại diện trong bản sửa phone-link.

## Kiểm tra đã chạy

Tại `Tenancy-Service`:

```powershell
npm.cmd test -- --runInBand --runTestsByPath test/unit/contract/application/contract-activate.command.handler.spec.ts test/unit/contract/application/contract-member-add.command.handler.spec.ts test/unit/contract/presentation/messaging/identity-lifecycle.subscriber.spec.ts test/unit/contract/application/room-hub-list.spec.ts
```

Kết quả: **4 suite, 33 test pass**. Activation fixture hiện dùng tenantId có sẵn, nên không chứng minh được account có trước + chỉ nhập phone hoạt động. Chưa chạy build vì chưa thay đổi application code. Khi triển khai: test regression từng task, `npm run build`, `npm run lint`; tại api-docs chạy `npm run lint` và `npm run bundle`. Android dùng `gradlew.bat :app-tenant:assembleDebug` trên đúng source; nếu có upload landlord thì thêm build app-landlord.

## Rủi ro và điểm chưa xác định

| Điểm | Tác động | Xử lý |
|---|---|---|
| Chưa có contract/account cụ thể | Không thể khẳng định nguyên nhân cho chính record được báo | Thu thập ID và GET có quyền trong P10-32/37; không cần chia sẻ password/token trong tài liệu |
| Mobile source khác bản local | Không kiểm tra được endpoint, DTO hoặc cache đang dùng | Ghi branch/build dùng nghiệm thu; chỉ điều chỉnh app sau khi xem source đúng |
| Account cũ chưa có event projection | Sửa create/activate vẫn không tìm được account | Kiểm tra chuỗi event/projection hiện có; không bổ sung bootstrap/repair script theo P10-D91 |
| Projection stale hoặc xung đột số điện thoại | Có thể gán nhầm ID nếu event chưa đồng bộ | Kiểm tra nguồn Identity và consumer lifecycle hiện có; không ghi đè link có sẵn |
| Race giữa activate/consumer/reconcile | Có thể mất link, deadlock hoặc chat thiếu tenant | Thứ tự khóa chung, snapshot activation sau resolve, outbox/inbox và test concurrency |
| Identity contact không có hoặc lỗi | Detail không thể đáp ứng contact bắt buộc như spec | Phân biệt not-found/outage; nếu có dữ liệu hợp lệ nhưng tạm unavailable thì trả lỗi phụ thuộc chuẩn; không trả object giả. Trường hợp chủ trọ đã xóa cần chốt policy trước khi release |
| Favorite đang deferred trong PM | Không thể hứa lỗi đã hết chỉ vì có route gateway | Giữ task P10-24 với plan cụ thể; xác nhận rule trước implementation, chưa đổi released |
| Claim 401 chứng minh route Media tồn tại | Có thể do middleware auth chung trả trước routing | Đã thấy Media implementation trong code; bằng chứng thực tế phải là upload/authenticated response, không chỉ 401 |

Plan chỉ sửa các lỗi đã nêu; không tự mở picker, thanh toán, OCR hay chức năng roommate. Không gọi SSH, không đọc secrets, không thay đổi dữ liệu live trong đợt audit này.
