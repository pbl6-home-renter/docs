# P10-31 — Link đại diện hợp đồng bằng SĐT ở create/activate

**Trạng thái:** 🔵 Code local + unit/SQL pass — chờ review/deploy, concurrency staging
**Ưu tiên:** P0 · **Repo:** Tenancy-Service · **Owner đề xuất:** BE Contract  
**Phụ thuộc:** Projection/consumer P9-01/02 hiện có · **Scope:** M; tách PR regression nếu vượt khoảng 5 file

## Mục tiêu và cách sửa

Đã triển khai create/activate theo phone projection; SQL regression xác nhận account có trước, draft cũ và tenant access. [Evidence](../discovery/mobile-backend-implementation.md). Chưa khẳng định deploy hay concurrency qua các connection độc lập.

Tenant đã có account active vẫn có thể không được link khi landlord tạo hợp đồng chỉ bằng tên/SĐT. Create chưa tra projection; activate sao chép ID NULL sang representative. Dùng lại TenantUserProjectionPort để resolve khi chưa có ID ở create; ở activate thử lại cho draft cũ trước khi tạo representative và activation snapshot. Giữ ID tường minh, phone không khớp thì giữ NULL. Khóa phone trước contract/room theo thứ tự chung với consumer; activate đọc phone snapshot trước và kiểm tra lại dưới khóa. Không gọi Identity đồng bộ trong transaction.

## Acceptance

- [ ] Account trước hợp đồng: cùng phone chuẩn hóa → contract và representative được gán đúng ID; draft vẫn là draft cho tới activate, snapshot activation chứa ID tenant.
- [ ] Draft cũ NULL và projection đến sau create vẫn link khi activate; không ghi đè ID có sẵn; chỉ auto-link account khớp trong projection active hiện có.
- [ ] Consumer đến trước/sau create/activate không mất link; mutation/outbox cùng transaction, không tạo duplicate representative/chat event hoặc deadlock do đảo thứ tự khóa.

## Verification

Thêm regression cho account có trước + tenantId NULL (fixture activation hiện chỉ có sẵn ID), `0/+84`, không match, ID tường minh và rollback outbox. Chạy Jest focused contract-create/activate/member-add/identity-lifecycle; build/lint Tenancy. Có integration test concurrency bằng DB thật trước nghiệm thu. GET `/me/contracts` và `/me/room-hub` bằng tenant liên quan sau activate phải trả hợp đồng/phòng.

**File dự kiến:** hai handler `contract-create`/`contract-activate` và regression spec tương ứng; các case concurrency ở PR test riêng nếu cần. API request không cần thêm trường.

**Tham chiếu:** [plan](../../tasks/plan.md), P9-D83/D84/D85, P10-23 không phải dependency.
