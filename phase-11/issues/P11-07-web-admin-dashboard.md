# P11-07 — Web: màn Admin dashboard

**Trạng thái:** 🟡 Open  
**Người phụ trách (đề xuất):** `ThaiBao11125`  
**Người review:** FE Lead  
**Ước lượng:** 2 points · khoảng 8 giờ  
**Phụ thuộc:** P11-01 (contract, dùng mock Apidog để dựng UI); nối API thật sau P11-02 và P11-03  
**Repo / branch:** `fe` · `feature/p11-07-admin-dashboard`  
**Quyết định áp dụng:** [P11-D92](../decisions.md#d92--admin-dashboard-và-audit-log)

## User story

> Là **admin**, khi vào trang chủ quản trị tôi muốn **thấy ngay số tài khoản, số tòa đang chờ duyệt và tỉ lệ lấp đầy phòng**, để **biết hôm nay có việc gì cần xử lý mà không phải mở từng danh sách**.

## Hiện trạng

`ROUTES.ADMIN.DASHBOARD` trong `fe/src/app/routes/roles/admin.routes.tsx` đang render placeholder `DashboardOverview`.

## Mô tả

- Trang mới thay placeholder, gọi **song song** 2 query TanStack Query: `GET /users/stats` và `GET /dashboard`.
- **Nhóm "Người dùng"** (từ `/users/stats`): thẻ Tổng tài khoản, Chủ trọ, Người thuê, Đang bị khóa, Chưa xác thực email.
- **Nhóm "Tòa nhà & phòng"** (từ `/dashboard`): thẻ Tòa đang hoạt động, **Tòa chờ duyệt** (bấm vào → danh sách duyệt tòa `ROUTES.ADMIN.BUILDINGS`, lọc `pending`), Tòa bị từ chối, Tổng phòng, Tỉ lệ lấp đầy (%), và biểu đồ phân bổ phòng theo trạng thái (trống / đang thuê / bảo trì).
- Thẻ "Đang bị khóa" bấm vào → `ROUTES.ADMIN.USERS` lọc trạng thái `locked` (nếu màn danh sách user đã có filter này).
- Dòng nhỏ "Cập nhật lúc …" lấy từ `generatedAt`, kèm nút làm mới.
- **Lỗi riêng từng nhóm:** một API lỗi thì chỉ nhóm đó hiện thông báo lỗi + nút "Thử lại"; nhóm còn lại vẫn hiển thị.
- Dùng lại component thẻ thống kê/biểu đồ đã có ở dashboard landlord nếu phù hợp; không thêm thư viện chart mới nếu dự án đã có.
- Toàn bộ chuỗi qua i18n (vi + en).

## Acceptance criteria

- [ ] **Given** admin đăng nhập, **when** mở `/admin`, **then** thấy 2 nhóm thẻ với số liệu khớp response API.
- [ ] **Given** `occupancyRate = 62.5`, **then** hiển thị "62,5%" (định dạng theo locale vi).
- [ ] **Given** `/dashboard` trả lỗi 500, **then** nhóm "Tòa nhà & phòng" hiện lỗi + nút Thử lại, nhóm "Người dùng" vẫn hiện số liệu.
- [ ] **Given** đang tải, **then** hiển thị skeleton cho từng nhóm, không nhảy layout.
- [ ] **Given** bấm thẻ "Tòa chờ duyệt", **then** chuyển sang danh sách duyệt tòa.
- [ ] **Given** tài khoản landlord/tenant truy cập `/admin`, **then** bị chặn như các route admin khác.
- [ ] Giao diện đọc được ở chiều rộng điện thoại (thẻ xuống dòng, không cuộn ngang).
- [ ] Chuyển ngôn ngữ vi/en, không còn chuỗi hard-code.

## Definition of Done

- [ ] Không viết file test. `npm run build`, `npm run lint`, `npm run i18n:check` pass.
- [ ] Ảnh chụp màn hình desktop + mobile + trạng thái lỗi đính kèm PR.
- [ ] Đã nối API thật (không còn mock) trước khi đóng issue.
