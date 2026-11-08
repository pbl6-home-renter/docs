# P8-02 — FE: quản lý BillingSetting/RatePolicy và áp dụng cho tòa

**Epic:** Phase 8  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** `ThaiBao11125`  
**Người review:** FE reviewer / PM  
**Ước lượng:** 3 points · 12 giờ (**tối đa 3 points và khoảng 15 file mỗi PR**)  
**Phụ thuộc:** P6-02c (RatePolicy API), P6-02d (BillingSetting API); không tạo lại backend issue  
**Repo / branch:** `fe/` · `feature/p8-02-billing-policy-ui`  
**Issue:** `docs#TBD`

> **Đọc trước khi code:** đọc `fe/AGENTS.md`, `fe/.agents/skills/fe-feature-workflow/SKILL.md`, `fe-structure/SKILL.md`, `fe-code-style/SKILL.md`, `fe-ui-ux/SKILL.md`. Các skill là chuẩn về kiến trúc, tên file, form, state và component; issue này chỉ chốt business behavior/UI.

## Mục tiêu

Landlord quản lý BillingSetting và RatePolicy qua API Tenancy hiện có, xem cấu hình đang dùng và áp dụng policy cho building/room theo operation đã có. FE không tự tính giá invoice và không dựng endpoint thay backend.

## Quyết định áp dụng

- Backend API thuộc P6-02c/d; phần này chỉ làm FE. Nếu các API chưa merge, có thể làm UI theo OpenAPI đã duyệt nhưng không giả định response hoặc tự tạo mock backend.
- P6-D72 yêu cầu thiếu electricity hoặc water rate thì invoice bị chặn `RATE_MISSING`; UI phải trình bày lỗi từ server, không tự tạo rate mặc định.
- Ownership do backend kiểm tra. Ẩn nút không thay thế authorization.
- Nếu API contract thiếu thao tác bắt buộc cho màn hình, ghi blocker gắn với P6-02c/d; không mở rộng scope thành API mới trong issue FE.

## Contract

- Dùng operations của P6-02c cho list/create/update/deactivate/batch apply RatePolicy và P6-02d cho BillingSetting; xác minh path/operationId/request/response trực tiếp trong `api-docs` trước khi code.
- Dùng API client/interceptor, query/mutation và error mapping hiện có trong `fe/`; không gọi service trực tiếp hoặc lưu business data riêng trong local storage.
- Success/error code và enum lấy từ OpenAPI; chưa có operation thì ghi blocker, không đặt tên route/code.

### Mapping field

| Field API | Thành phần UI | Validation/ghi chú |
|---|---|---|
| building/room ID | bộ chọn phạm vi áp dụng | chỉ dùng resource user được API trả về |
| policy ID/name/status | danh sách và lựa chọn policy | trạng thái lấy từ server, không tự suy từ tên |
| loại phí/utility | field chọn trong form | enum theo DTO hiện có |
| đơn giá/đơn vị | field tiền và đơn vị | precision/min/max/currency format theo contract |
| hiệu lực hoặc cấu hình bậc | form chi tiết policy | hiển thị đúng schema; không tự tính tổng invoice |

## Tham chiếu code

- Rà `fe/src/features/buildings/`, API hooks/query keys, form schema và invalidation hiện có; ưu tiên tái sử dụng component/form conventions thay vì tạo framework mới.
- Rà `api-docs` cho P6-02c/d và module mẫu của FE có list/detail/form tương tự.

## Các bước triển khai

### Bước 1 — Đối chiếu API và điều hướng

- **Cách làm:** xác định route/menu, operations, DTO, role và query invalidation; ghi mapping thực tế vào PR.
- **Kiểm tra bước:** với tài khoản landlord, list policy tải qua API; tài khoản không có quyền nhận lỗi theo contract.

### Bước 2 — Danh sách và chi tiết policy

- **Cách làm:** thêm loading/empty/error, bảng/list policy, thông tin phạm vi và thao tác được backend hỗ trợ; giữ filter/building context theo router convention.
- **Kiểm tra bước:** danh sách rỗng hiện empty state; đổi building làm tải lại dữ liệu đúng; refresh giữ được route/filter hợp lệ.

### Bước 3 — Form tạo/sửa và áp dụng

- **Cách làm:** form chỉ gồm field được DTO cho phép; validate theo contract; áp policy cho building/room qua operation hiện có; sau success invalidate/refetch dữ liệu liên quan.
- **Kiểm tra bước:** tạo/sửa thành công thấy giá trị mới sau refresh; 422 gắn lỗi đúng field; 409/403 không báo thành công và không mất draft.

### Bước 4 — Case lỗi và accessibility

- **Cách làm:** xử lý submit lặp, timeout, policy stale/deactivated, mất quyền giữa lúc form mở; dùng label, focus/error summary và dialog xác nhận theo FE skill.
- **Kiểm tra bước:** submit liên tiếp chỉ gửi một mutation; lỗi mạng có thể retry sau khi kiểm tra trạng thái server.

## Ngoài phạm vi

- Viết hoặc thay đổi RatePolicy/BillingSetting API, migration hay business rule backend.
- Tính invoice/total ở trình duyệt, tạo rate mặc định hoặc sửa dữ liệu ngoài quyền landlord.
- Gộp chức năng invoice screens thuộc issue P6-06c.

## Blocker

- Ghi blocker nếu P6-02c/d chưa có operation/schema cần cho flow; đính path/operationId đang thiếu và chờ API owner, không mock để coi là hoàn thành.

## Acceptance

- [ ] Landlord xem được cấu hình và policy áp dụng đúng building/room.
- [ ] Create/update/apply dùng API thật; field validation khớp DTO; state sau refresh khớp server.
- [ ] Empty/loading/error/conflict/forbidden state rõ; thao tác submit không bị gửi trùng.
- [ ] Không có phép tính giá nghiệp vụ ở FE và không có dữ liệu mock giả làm kết quả thật.

## Definition of Done

- [ ] Các bước kiểm tra được chạy và ghi request/ảnh UI trong PR.
- [ ] Tuân thủ `fe/AGENTS.md` và bốn skill FE; `npm run build`, `npm run lint`, `npm run i18n:check` pass theo repo.
- [ ] PR ≤ 3 points/~15 file, liên kết GitHub issue sau khi tạo và có FE reviewer approve.
