# P12-10 — FE: Mở quyền truy cập chỉ đọc và chức năng thanh toán cho tài khoản bị khóa

**Trạng thái:** 🟡 Open
**Người phụ trách (đề xuất):** FE Team / FE Lead
**Người review:** FE Lead, PM
**Ước lượng:** 3 points
**Phụ thuộc:** P12-01, P12-02, P12-09
**Repo / branch:** `fe` · `feature/p12-10-frontend-locked-account-readonly-access`

> **Đọc trước khi code:** `decisions.md` (P12-D99, P12-D100), `AGENTS.md` và các quy tắc giao diện trong repo `fe`.

## 1. Mục tiêu & Bối cảnh

- **Hiện trạng:** Trong `fe/src/app/routes/protected-route.tsx`, khi phát hiện `user.status === UserStatus.LOCKED`, hệ thống điều hướng toàn bộ request sang trang cấm truy cập (`ROUTES.FORBIDDEN` - `/403`). Người dùng bị khóa không thể truy cập bất kỳ màn hình nào trong Dashboard, kể cả thông tin hợp đồng hay hóa đơn cần thanh toán.
- **Kỳ vọng:** 
  1. Người dùng có tài khoản bị khóa vẫn đăng nhập và truy cập được các màn hình liên quan của bản thân trong hệ thống ở chế độ **chỉ đọc (Read-only)**:
     - Tòa nhà / Phòng đang thuê (`/me/rooms`, `/me/room-hub`, chi tiết phòng).
     - Hợp đồng của tôi (`/contracts`, `/contracts/:id`).
     - Hóa đơn của tôi (`/invoices`, `/invoices/:id`).
  2. Người dùng bị khóa **vẫn thực hiện được chức năng thanh toán hóa đơn** (quét mã VietQR / xem thông tin thanh toán hoặc thực hiện giao dịch thanh toán).
  3. Hiển thị thông báo trạng thái tài khoản đang bị khóa rõ ràng (ví dụ: Banner cảnh báo màu vàng/cam trên đầu trang Dashboard layout) để người dùng nắm rõ lý do các nút tạo mới/chỉnh sửa bị vô hiệu hóa.
  4. Ẩn hoặc vô hiệu hóa (disabled) các nút thao tác làm thay đổi dữ liệu:
     - Ẩn/chặn form chỉnh sửa thông tin cá nhân và đổi mật khẩu trong `/profile`, `/settings`.
     - Ẩn các nút "Tạo hợp đồng", "Kích hoạt", "Chỉnh sửa hợp đồng", "Thêm thành viên", "Rời hợp đồng".
     - Ẩn/vô hiệu hóa các nút "Tạo phòng", "Cập nhật thông tin phòng", "Đổi trạng thái phòng".

## 2. Quyết định áp dụng

- `P12-D99` — Cho phép tài khoản bị khóa truy cập thông báo và nhận sự kiện thông báo.
- `P12-D100` — Cho phép tài khoản bị khóa truy cập các trang thông tin cá nhân/hợp đồng/hóa đơn ở chế độ chỉ đọc và giữ tính năng thanh toán.

## 3. Yêu cầu kỹ thuật & Phạm vi thay đổi Frontend

### 3.1. Route Guard (`fe/src/app/routes/protected-route.tsx`)
- Không điều hướng cưỡng chế sang `/403` ngay lập tức đối với mọi route khi `user.status === UserStatus.LOCKED`.
- Cấu hình danh sách các route được phép truy cập khi tài khoản bị khóa (Allowlist for Locked Users):
  - Thông báo: `ROUTES.NOTIFICATIONS` (theo P12-02 / P12-D99).
  - Hợp đồng: `ROUTES.TENANT.CONTRACTS`, `ROUTES.TENANT.CONTRACT_DETAIL(':id')`, `ROUTES.LANDLORD.CONTRACTS` (nếu là landlord).
  - Hóa đơn: `ROUTES.INVOICES`, `ROUTES.INVOICE_DETAIL(':id')`.
  - Phòng & Tòa nhà: `ROUTES.TENANT.ROOMS`, `ROUTES.ROOM_DETAIL(':id')`, `ROUTES.LANDLORD.BUILDINGS`, `ROUTES.LANDLORD.BUILDING_DETAIL(':id')`.
  - Tổng quan / Dashboard (nếu cần xem danh sách phòng thuê / widget chỉ đọc): `ROUTES.DASHBOARD`.
  - Xem profile cá nhân ở chế độ chỉ đọc: `ROUTES.PROFILE`.
- Các route cấm thao tác hoặc nhạy cảm (như tạo hợp đồng, quản lý cài đặt nâng cao) khi người dùng cố truy cập trực tiếp bằng URL sẽ được chuyển hướng sang `/403` hoặc trang danh sách tương ứng.

### 3.2. Cảnh báo toàn cục (Global Banner / Header notification)
- Trong `fe/src/app/layouts/dashboard-layout.tsx` hoặc `header.tsx`:
  - Khi `user.status === UserStatus.LOCKED`, hiển thị một Banner cảnh báo cố định ở đầu trang: "Tài khoản của bạn hiện đang bị khóa. Bạn chỉ có thể xem thông tin và thanh toán hóa đơn. Các thao tác chỉnh sửa dữ liệu đã bị vô hiệu hóa." (kèm đa ngôn ngữ `vi`/`en`).

### 3.3. Chế độ chỉ đọc (Read-only UI) trên từng màn hình
1. **Màn hình Profile & Settings (`/profile`, `/settings`):**
   - Vô hiệu hóa hoặc ẩn nút lưu/chỉnh sửa thông tin cá nhân.
   - Ẩn/vô hiệu hóa form đổi mật khẩu hoặc hiển thị thông báo "Tài khoản bị khóa không thể đổi thông tin".
2. **Màn hình Hợp đồng (`/contracts`, `/contracts/:id`):**
   - Ẩn nút "Tạo hợp đồng", "Kích hoạt hợp đồng", "Chấm dứt hợp đồng", "Trả phòng".
   - Ẩn các nút thao tác thành viên: "Thêm thành viên", "Xóa/Mời ra khỏi hợp đồng", "Rời hợp đồng".
   - Vẫn hiển thị đầy đủ thông tin hợp đồng, thành viên, điều khoản, file đính kèm.
3. **Màn hình Hóa đơn & Thanh toán (`/invoices`, `/invoices/:id`):**
   - Vẫn hiển thị đầy đủ chi tiết hóa đơn, các khoản phí, trạng thái hóa đơn.
   - **Giữ nguyên và kích hoạt nút Thanh toán / QR thanh toán** để Tenant có thể hoàn tất nghĩa vụ trả phí hóa đơn.
   - Vô hiệu hóa nút tạo mới hóa đơn, cập nhật phụ phí hoặc hủy hóa đơn đối với tài khoản landlord bị khóa.
4. **Màn hình Phòng / Tòa nhà:**
   - Ẩn các nút "Thêm phòng", "Thêm tòa nhà", "Chỉnh sửa", "Xóa".

### 3.4. Xử lý lỗi API (Global Error Handling)
- Trong interceptor HTTP (`fe/src/lib/http` hoặc React Query error handler): Nếu nhận lỗi `403 ACCOUNT_LOCKED` từ các thao tác ghi (POST/PATCH/PUT/DELETE), hiển thị Toast thông báo lỗi rõ ràng theo i18n thay vì để crash giao diện.

## 4. Tiêu chí nghiệm thu (Acceptance Criteria)

- [ ] **Đăng nhập & Điều hướng:** Tài khoản có trạng thái `locked` sau khi đăng nhập không bị đẩy ra `/403`, truy cập được vào các trang:
  - Danh sách và chi tiết phòng đang thuê.
  - Danh sách và chi tiết hợp đồng của mình.
  - Danh sách và chi tiết hóa đơn của mình.
  - Màn hình thông báo (`/notifications`).
- [ ] **Banner cảnh báo tài khoản:** Banner thông báo tài khoản bị khóa hiển thị rõ ràng trên giao diện, hỗ trợ song ngữ `vi`/`en`.
- [ ] **Thực hiện thanh toán:** Tenant bị khóa vẫn xem được thông tin thanh toán (VietQR / thông tin tài khoản) và bấm thực hiện chức năng thanh toán thành công.
- [ ] **Vô hiệu hóa chỉnh sửa:**
  - Không thể bấm gửi form sửa thông tin cá nhân hay đổi mật khẩu.
  - Các nút tạo hợp đồng, chỉnh sửa hợp đồng, thêm/xóa thành viên trên UI hợp đồng được ẩn hoặc disabled.
  - Cố tình gọi API ghi sẽ nhận thông báo lỗi dễ hiểu và không làm hỏng trạng thái trang.
- [ ] **Build & Quality:**
  - `npm run build`, `npm run lint`, `npm run i18n:check` pass.
  - Đảm bảo đầy đủ key dịch thuật trong `locales/vi/` và `locales/en/`.
  - Không gây gián đoạn trải nghiệm của tài khoản bình thường (`status = 'active'`).
