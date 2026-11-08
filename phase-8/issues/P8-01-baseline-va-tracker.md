# P8-01 — Chốt baseline Phase 8 và đồng bộ tracker

**Epic:** Phase 8  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** PM  
**Người review:** PM  
**Ước lượng:** 2 points · 6 giờ (**tối đa 3 points và khoảng 15 file mỗi PR**)  
**Phụ thuộc:** —  
**Repo / branch:** `pm/` · `docs/p8-01-baseline-tracker`  
**Issue:** `docs#TBD`

> **Đọc trước khi cập nhật:** đọc `pm/AGENTS.md`, `.agents/skills/pm-context/SKILL.md`, `requirement.md`, `PROJECT_PLAN.md`, README và decisions Phase 6/7. Ưu tiên theo thứ tự source of truth của PM workspace. Chỉ ghi điều đã xác minh; điều chưa rõ phải để blocker, không tự suy diễn trạng thái hay nghiệp vụ.

## Mục tiêu

Chốt baseline có đường dẫn/bằng chứng cho các repo, API, DB và FE để làm đầu vào giao việc Phase 8. Đồng bộ trạng thái P7/P6 theo xác nhận của PM, sửa encoding tracker Phase 6 và lập danh sách các issue P5/P6 được dùng lại thay vì tạo issue trùng.

## Quyết định áp dụng

- Theo xác nhận PM: P7-01–18, P6-11 và P6-12 đã hoàn tất; đánh dấu Done trong tracker và issue file tương ứng.
- Giữ các issue P5/P6 đã có GitHub ID; không tạo bản P8 khác cho cùng phạm vi.
- P6-09 và P6-10a/b đã được PM yêu cầu dọn khỏi backlog hoạt động; không khôi phục chúng.
- P6-06b/c/d vẫn được giữ trong tracker theo xác nhận trước đó.
- P8-07/08 được dành chỗ cho flow PM sẽ cung cấp; hiện không tạo issue file, không đặt owner và không mở rộng phạm vi.

## Baseline cần bàn giao

| Repo / nhóm | Cần xác minh | Bằng chứng cần ghi |
|---|---|---|
| `Tenancy-Service/` | Building/Room, Contract/Member, MeterReading, BillingSetting/RatePolicy, Invoice; controller/use case/entity/migration | Đường dẫn file, endpoint và trạng thái thực tế của từng phần |
| `Identity-Service/` | `/me`, media, admin users; guard và DTO | Path/operationId OpenAPI cùng implementation hiện có |
| `community-service/` | Conversation/Member, inbox/preferences, RabbitMQ publisher/consumer, Socket/FCM | Module, queue/routing, event schema, persistence và trạng thái vận hành |
| `fe/` | Routes/pages/API clients cho landlord, tenant, admin; loading/error/empty states | Đường dẫn component/route và tính năng đã có |
| `api-docs/` | Endpoint/spec liên quan các issue carry-over | Path YAML, operationId, request/response/error schema và bundle command |
| Gateway/DB | Route tới từng service, schema/migration/unique key liên quan | Route config và entity/migration đang dùng; không ghi giá trị secret |

## Phân biệt issue mới và issue dùng lại

- Ghi bảng đối chiếu P8 scope với P5-08b/c/d, P5-09b/c; P6-01e1/e3, P6-02c/d/e/f/g2/g3/g4/h và P6-06a/b/c/d.
- Đánh dấu rõ phần UI mới, API đã có, API còn nằm trong issue P5/P6 và issue nào đã Done.
- Không dùng tên module hoặc file DTO đơn lẻ làm bằng chứng “đã triển khai”; đối chiếu route/controller, use case, persistence và FE call.

## Các bước triển khai

### Bước 1 — Kiểm kê repo và issue

- **Cách làm:** rà tracker P4–P7, issue files và repo code; lập bảng phạm vi/owner/status/GitHub ID cho từng issue được Phase 8 dùng lại.
- **Kiểm tra bước:** mọi dòng có đường dẫn issue và trạng thái; P8 không có mục trùng với issue đã tồn tại.

### Bước 2 — Chốt baseline API/DB/FE

- **Cách làm:** theo bảng Baseline, ghi endpoint, schema, module, migration và phần FE có thật; ghi riêng sai khác giữa OpenAPI và implementation.
- **Kiểm tra bước:** mỗi kết luận “có/chưa có” kèm đường dẫn file hoặc request/route có thể tái hiện.

### Bước 3 — Đồng bộ tracker và encoding

- **Cách làm:** giữ ID GitHub P5/P6; đánh dấu trạng thái theo xác nhận PM; đổi owner các task backend được giao lại sang `leminhkhai345`; xóa các P8 issue trùng; cập nhật danh sách P8-01–P8-10, để P8-07/08 là chỗ dành riêng chưa có issue.
- **Kiểm tra bước:** mở tracker bằng UTF-8, rà từng link nội bộ và so trạng thái với issue files.

## Ngoài phạm vi

- Không sửa code service, schema DB hoặc OpenAPI trong issue baseline.
- Không tạo issue GitHub mới hoặc thay đổi trạng thái GitHub từ bên ngoài workspace.
- Không viết flow Community/notification thuộc P8-07/08 thay PM.

## Blocker

- Nếu repo không truy cập được hoặc trạng thái implementation mâu thuẫn giữa code/spec, ghi chính xác nguồn và owner cần xác nhận; không tự chọn một nguồn ngoài thứ tự ưu tiên đã quy định.

## Acceptance

- [ ] P7-01–18 và P6-11/12 hiển thị Done theo xác nhận PM; trạng thái việc khác không tự đổi.
- [ ] Tracker Phase 6 hiển thị tiếng Việt đúng UTF-8, không còn mojibake; P6-09/10a/10b không xuất hiện trong backlog hoạt động.
- [ ] Danh sách P5/P6 dùng lại giữ nguyên ID/GitHub ID; không còn P8 file mô tả cùng implementation.
- [ ] Baseline API/DB/FE có nguồn kiểm chứng và ghi rõ chỗ chưa rõ.
- [ ] P8-07/08 không có nội dung nghiệp vụ, owner hoặc assignee.

## Definition of Done

- [ ] Mọi bước có kiểm tra cụ thể; tracker, issue file và liên kết nội bộ đồng nhất.
- [ ] Diff chỉ gồm tài liệu trong phạm vi; `git diff --check` sạch.
- [ ] PR ghi `Closes pbl6-home-renter/docs#<số issue>` sau khi issue GitHub được tạo; PM review.
