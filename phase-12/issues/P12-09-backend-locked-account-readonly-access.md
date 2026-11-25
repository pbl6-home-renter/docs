# P12-09 — BE: Cho phép tài khoản bị khóa truy cập thông tin chỉ đọc và thanh toán hóa đơn

**Trạng thái:** 🟡 Open
**Người phụ trách (đề xuất):** BE Team (`leminhkhai345` / `baoduong17`)
**Người review:** BE Lead
**Ước lượng:** 3 points
**Phụ thuộc:** P12-01, P12-02
**Repo / branch:** `Identity-Service`, `Tenancy-Service`, `api-doc` · `feature/p12-09-backend-locked-account-readonly-access`

> **Đọc trước khi code:** `decisions.md` (P12-D99, P12-D100), `AGENTS.md` và skill trong `.agents/skills/` của từng repo. Nguồn mâu thuẫn: `decisions.md` > `docs/notifications.md` > issue.

## 1. Mục tiêu & Bối cảnh

- **Hiện trạng:** Khi Admin khóa tài khoản (`status = 'locked'`), người dùng bị chặn toàn bộ quyền truy cập do `ActiveUserGuard` trên các service chặn mọi request (ném lỗi `403 Forbidden` với mã `ACCOUNT_LOCKED`) trừ các endpoint gắn decorator `@AllowLocked()`. Hiện tại chỉ có `GET /me`, `POST /auth/logout` bên Identity và một số endpoint tòa nhà bên Tenancy có `@AllowLocked()`. Người dùng bị khóa không thể xem lại phòng đang thuê, hợp đồng, hóa đơn và không thể thực hiện thanh toán hóa đơn.
- **Kỳ vọng:** Người dùng bị khóa vẫn có thể đăng nhập vào hệ thống và xem các thông tin liên quan của bản thân ở chế độ chỉ đọc (Read-only) gồm: thông tin tòa nhà, phòng đang thuê, hợp đồng, hóa đơn và **vẫn thực hiện được chức năng thanh toán**. Các thao tác thay đổi dữ liệu khác (chỉnh sửa thông tin cá nhân, cập nhật mật khẩu, tạo hợp đồng mới, sửa đổi hợp đồng, thêm thành viên, tạo/sửa hóa đơn, v.v.) vẫn bị chặn nghiêm ngặt như cũ.

## 2. Quyết định áp dụng

- `P12-D99` — Locked users may read their own notifications and receive notification Socket events; other business access remains blocked.
- `P12-D100` — Locked users read-only access & payment execution allowance.

## 3. Yêu cầu kỹ thuật & Phạm vi endpoint Backend

### 3.1. Identity-Service
1. **Kiểm tra đăng nhập (`POST /auth/login`):**
   - Đảm bảo tài khoản có `status = 'locked'` vẫn được phép đăng nhập bình thường để nhận access token và refresh token (JWT payload mang `status: 'locked'`).
   - Đã được hỗ trợ ở tầng Auth, cần bổ sung integration test xác nhận.
2. **Quản lý thông tin cá nhân (`UserController`):**
   - Giữ quyền đọc thông tin cá nhân: `GET /me` (hiện tại `UserController` đang gắn `@AllowLocked()` ở class level).
   - **Chặn chỉnh sửa cá nhân khi bị khóa:** Bỏ `@AllowLocked()` ở cấp class; chuyển decorator `@AllowLocked()` chỉ áp dụng cho `GET /me`. Các endpoint ghi gồm:
     - `PATCH /me` (cập nhật thông tin cá nhân, payout account) -> **Chặn** đối với tài khoản `status = 'locked'` (trả về `403 ACCOUNT_LOCKED`).
     - `PUT /me/password` (đổi mật khẩu) -> **Chặn** đối với tài khoản `status = 'locked'` (trả về `403 ACCOUNT_LOCKED`).
   - `POST /auth/logout`: Giữ nguyên `@AllowLocked()` để người dùng bị khóa có thể đăng xuất.

### 3.2. Tenancy-Service
Mở quyền truy cập có kiểm soát bằng decorator `@AllowLocked()` (hoặc `@AllowLocked(UserRole.TENANT, UserRole.LANDLORD)` tùy nghiệp vụ) cho các endpoint sau:

1. **Thông tin Tòa nhà & Phòng đang thuê:**
   - `GET /me/room-hub` (`RoomHubController`): Cho phép Tenant bị khóa xem danh sách phòng đang thuê và trạng thái hiện tại (`@AllowLocked(UserRole.TENANT)`).
   - `GET /rooms/:roomId` (`RoomController`): Cho phép xem thông tin chi tiết phòng (`@AllowLocked()`).
   - `GET /me/rooms` (`RoomController`): Cho phép Tenant/Landlord xem danh sách phòng của mình (`@AllowLocked()`).
   - `GET /me/buildings`, `GET /buildings/:buildingId` (`MyBuildingController`, `BuildingController`): Cho phép xem danh sách và chi tiết tòa nhà (`@AllowLocked()`).
   - **Chặn ghi:** Các thao tác `POST /rooms`, `PATCH /rooms/:id`, `DELETE /rooms/:id`, `POST /buildings`, `PATCH /buildings/:id` **tuyệt đối không** gắn `@AllowLocked()`.

2. **Hợp đồng thuê phòng (Contracts & Members):**
   - `GET /me/contracts` (`ContractMyController`): Cho phép Tenant bị khóa xem danh sách hợp đồng của bản thân (`@AllowLocked(UserRole.TENANT)`).
   - `GET /contracts/:contractId` (`ContractController`): Cho phép xem chi tiết hợp đồng của mình (`@AllowLocked()`).
   - `GET /contract-members` (`ContractMemberController`): Cho phép xem danh sách thành viên trong hợp đồng (`@AllowLocked()`).
   - `GET /contracts` (`ContractController`): Cho phép Landlord xem danh sách hợp đồng của mình (`@AllowLocked(UserRole.LANDLORD)`).
   - **Chặn ghi:** Các thao tác tạo hợp đồng `POST /contracts`, sửa draft `PUT /contracts/:id`, kích hoạt `POST /contracts/:id/activate`, thêm/sửa thành viên `POST /contract-members`, `PATCH /contract-members/:id`, `POST /contract-members/:id/leave` **tuyệt đối không** gắn `@AllowLocked()`.

3. **Hóa đơn & Thanh toán (Invoices & Payments):**
   - `GET /me/invoices` (`InvoiceMyController`): Cho phép Tenant bị khóa xem danh sách hóa đơn cần thanh toán của mình (`@AllowLocked(UserRole.TENANT)`).
   - `GET /invoices/:invoiceId` (`InvoiceController`): Cho phép xem chi tiết hóa đơn (`@AllowLocked()`).
   - `GET /invoices` (`InvoiceController`): Cho phép Landlord xem danh sách hóa đơn (`@AllowLocked(UserRole.LANDLORD)`).
   - **Chức năng thanh toán:** Mở quyền thực hiện thanh toán hóa đơn cho tài khoản bị khóa:
     - Endpoint thanh toán (tùy theo spec thanh toán tích hợp như `POST /payments/create-intent`, `POST /payments/record-cash-payment` hoặc endpoint liên quan thanh toán hóa đơn) phải cho phép tài khoản bị khóa thực hiện giao dịch thanh toán cho các hóa đơn hợp lệ mang `issued` status của chính mình (`@AllowLocked(UserRole.TENANT)`).
   - **Chặn ghi nghiệp vụ hóa đơn:** Các thao tác lập hóa đơn `POST /invoices/generate`, phát hành `POST /invoices/issue-invoice`, sửa `PATCH /invoices/:id`, hủy `POST /invoices/:id/cancel-invoice` **tuyệt đối không** gắn `@AllowLocked()`.

### 3.3. API Documentation (`api-doc`)
- Cập nhật tài liệu OpenAPI mô tả rõ mã phản hồi `403 ACCOUNT_LOCKED` và gắn chú thích các endpoint hỗ trợ truy cập khi tài khoản ở trạng thái `locked` (Read-only và Thanh toán hóa đơn).

## 4. Tiêu chí nghiệm thu (Acceptance Criteria)

- [ ] **Đăng nhập thành công:** Tài khoản bị khóa đăng nhập thành công qua `POST /auth/login`, nhận JWT với claim `status = 'locked'`.
- [ ] **Xem thông tin cá nhân:** Gọi `GET /me` trả về `200 OK` chứa thông tin cá nhân của user bị khóa.
- [ ] **Chặn sửa thông tin cá nhân:** Gọi `PATCH /me` hoặc `PUT /me/password` từ tài khoản bị khóa trả về `403 Forbidden` với error code `ACCOUNT_LOCKED`.
- [ ] **Xem danh sách & chi tiết phòng/tòa nhà:** 
  - Tenant bị khóa gọi `GET /me/room-hub`, `GET /rooms/:id`, `GET /me/rooms` trả về `200 OK`.
  - Landlord bị khóa gọi `GET /me/buildings`, `GET /buildings/:id` trả về `200 OK`.
- [ ] **Xem danh sách & chi tiết hợp đồng:**
  - Tenant bị khóa gọi `GET /me/contracts`, `GET /contracts/:id`, `GET /contract-members` (thuộc hợp đồng của mình) trả về `200 OK`.
  - Không thể tạo hợp đồng mới (`POST /contracts` trả về `403 ACCOUNT_LOCKED`).
  - Không thể sửa hợp đồng hoặc thêm/xóa thành viên (trả về `403 ACCOUNT_LOCKED`).
- [ ] **Xem hóa đơn & thực hiện thanh toán:**
  - Tenant bị khóa gọi `GET /me/invoices`, `GET /invoices/:id` trả về `200 OK`.
  - Tenant bị khóa thực hiện thao tác thanh toán hóa đơn thành công.
  - Không thể phát sinh hành động thay đổi dữ liệu hóa đơn như hủy hóa đơn hay cập nhật phụ phí (`403 ACCOUNT_LOCKED`).
- [ ] **Unit / Integration tests:** Đầy đủ test case cho `ActiveUserGuard` và các controller liên quan ở cả 2 service; toàn bộ suite test chạy pass.
