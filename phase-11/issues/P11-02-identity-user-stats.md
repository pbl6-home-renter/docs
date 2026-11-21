# P11-02 — Identity: thống kê người dùng `GET /users/stats`

**Trạng thái:** 🟡 Open  
**Người phụ trách (đề xuất):** `huynhtiennhat0403`  
**Người review:** BE Lead  
**Ước lượng:** 1 point · khoảng 4 giờ  
**Phụ thuộc:** P11-01 (contract)  
**Repo / branch:** `Identity-Service` · `feature/p11-02-user-stats`  
**Quyết định áp dụng:** [P11-D92](../decisions.md#d92--admin-dashboard-và-audit-log)

## User story

> Là **admin hệ thống**, tôi muốn **xem tổng số tài khoản theo vai trò và trạng thái**, để **biết nền tảng đang có bao nhiêu chủ trọ, người thuê và bao nhiêu tài khoản đang bị khóa**.

## Mô tả

- Thêm query `user-stats` (CQRS) trong module `users`, đọc bảng `users` bằng `COUNT ... GROUP BY role` và `GROUP BY status` (2 query hoặc 1 query `FILTER`).
- Route thêm vào `user-admin.controller.ts` (đã có `@Roles(UserRole.ADMIN)`).
- **Lưu ý route:** controller đang có `@Get(':userId')`. Phải khai báo `@Get('stats')` **trước** `:userId`, hoặc đảm bảo `:userId` dùng `ParseUUIDPipe`, để `stats` không bị hiểu nhầm là id.
- Không cần thay đổi gateway: prefix `/users` đã route về Identity.

## Acceptance criteria

- [ ] **Given** admin đăng nhập, **when** gọi `GET /api/v1/<identity>/users/stats`, **then** nhận `200 USER_STATS_FETCHED` với đủ field theo contract P11-01.
- [ ] **Given** DB có 1 admin, 3 landlord (1 bị khóa), 5 tenant (2 chưa xác thực email), **then** response là `totalUsers = 9`, `byRole = {admin: 1, landlord: 3, tenant: 5}`, `byStatus = {active: 6, locked: 1, pendingVerification: 2}`.
- [ ] **Given** token của landlord hoặc tenant, **then** `403 FORBIDDEN`. Không có token → `401`.
- [ ] **Given** gọi `GET /users/<uuid hợp lệ>`, **then** vẫn chạy đúng API chi tiết user (không bị route `stats` chặn).
- [ ] `byRole` và `byStatus` luôn có đủ key; role/trạng thái không có ai thì trả `0`.
- [ ] Gọi qua gateway (`/api/v1/users/stats`) cũng thành công.

## Definition of Done

- [ ] Unit test cho query handler (đủ key, giá trị 0) trong `test/unit/users/application/`.
- [ ] `npm run build`, `npm run lint`, `npm test` pass; check dependency rule không in gì.
- [ ] Swagger hiển thị đúng `operationId`; `x-apidog-status` trong `api-docs` đổi sang `released` sau khi verify.
- [ ] Ảnh chụp/export Apidog các case trên đính kèm PR.
