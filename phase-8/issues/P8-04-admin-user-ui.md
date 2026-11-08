# P8-04 — FE: quản trị người dùng qua Identity API

**Epic:** Phase 8  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** `ThaiBao11125`  
**Người review:** FE reviewer / PM  
**Ước lượng:** 3 points · 12 giờ (**tối đa 3 points và khoảng 15 file mỗi PR**)  
**Phụ thuộc:** P4-12 đã cung cấp Identity Admin User API  
**Repo / branch:** `fe/` · `feature/p8-04-admin-user-management`  
**Issue:** `docs#TBD`

> **Đọc trước khi code:** đọc `fe/AGENTS.md` và `fe/.agents/skills/fe-feature-workflow/SKILL.md`, `fe-structure/SKILL.md`, `fe-code-style/SKILL.md`, `fe-ui-ux/SKILL.md`. API source là OpenAPI/Identity implementation P4-12.

## Mục tiêu

Admin tra cứu danh sách và chi tiết user, cập nhật field được phép, khóa/mở khóa và xóa user bằng endpoint Identity đã có. FE không bổ sung business API hoặc tự quyết định trạng thái tài khoản.

## Quyết định áp dụng

- P4-12 đã triển khai API Admin Users; dùng đúng list/detail/update/lock/unlock/delete contract hiện tại.
- Chỉ role admin vào route; backend tiếp tục là lớp phân quyền cuối cùng.
- Không hiển thị password, token, secret hoặc field không có trong response công khai.
- Lock/unlock/delete cần xác nhận rõ user mục tiêu; disable action khi request đang chạy.

## Contract

Trước khi code lập bảng method/path/operationId/query/body/response/error từ OpenAPI P4-12. Không giả định filter hoặc paging nếu spec không có. Các thao tác tương ứng list, detail, update, action lock/unlock và soft-delete theo API hiện hành.

### Mapping field

| API field/action | UI | Validation/giới hạn |
|---|---|---|
| list filters/page | query controls | chỉ gửi query được OpenAPI khai báo |
| user summary/detail | bảng và trang chi tiết | không render credential/secret |
| update DTO | form chỉnh sửa | allowlist field, giữ field không được sửa read-only |
| lock/unlock | action + trạng thái account | state đổi sau response thành công |
| delete | dialog xác nhận | xử lý soft-delete, 404/409 theo contract |

## Tham chiếu code

- Rà route/menu admin, route guard, DataTable/pagination, dialog xác nhận và API error mapper hiện có trong FE.
- Dùng response/query patterns hiện có; không tạo user store riêng hoặc mock list.

## Các bước triển khai

### Bước 1 — Route và list

- **Cách làm:** thêm trang dưới admin route, bảo vệ role theo convention; nối list/filter/pagination theo OpenAPI.
- **Kiểm tra bước:** admin thấy data thật; landlord/tenant truy cập direct URL bị chặn; trang rỗng có empty state.

### Bước 2 — Chi tiết và cập nhật

- **Cách làm:** tải detail theo ID; form chỉ gồm update DTO; xử lý 422 tại field và refetch sau success.
- **Kiểm tra bước:** update thành công phản ánh ở list và detail; ID không tồn tại hiện 404 state.

### Bước 3 — Khóa/mở khóa/xóa

- **Cách làm:** dialog nêu rõ user và action; gọi endpoint; refetch sau success; không optimistic update trạng thái trước server.
- **Kiểm tra bước:** lỗi 403/409 giữ trạng thái cũ; nhấn nhanh nhiều lần không gửi duplicate mutation.

### Bước 4 — Trạng thái và khả năng truy cập

- **Cách làm:** xử lý loading, empty, error, stale user bị thay đổi từ phiên khác; đảm bảo keyboard focus/labels.
- **Kiểm tra bước:** refresh/back hoạt động; dialog trả focus đúng; lỗi mạng có nút retry.

## Ngoài phạm vi

- Thay Identity API, phân quyền server, reset password hoặc thay đổi role nếu operation không hỗ trợ.
- Tự khóa/xóa user bằng cách chỉ ẩn UI; route guard không thay thế backend authorization.

## Blocker

- Nếu operation cần thiết không có trong OpenAPI/Identity, ghi blocker và đề xuất API owner xác nhận; không tự tạo endpoint.

## Acceptance

- [ ] Admin sử dụng đủ list/detail/update/lock/unlock/delete theo API; quyền được bảo vệ ở route và backend.
- [ ] Search/paging chỉ dùng field contract hỗ trợ; lỗi 401/403/404/409/422 phân biệt rõ.
- [ ] Confirm destructive action, chặn double submit, refetch state sau mutation.
- [ ] Không lộ credential/token; không dùng mock làm dữ liệu thật.

## Definition of Done

- [ ] Bằng chứng UI/API cho role admin và non-admin; ảnh che PII.
- [ ] FE lint/build/i18n check pass theo repo; issue không làm thay đổi API.
- [ ] PR ≤ 3 points/~15 file, FE reviewer approve.
