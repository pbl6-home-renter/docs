# ADMIN WEB WIREFRAMES SPECIFICATION (LOW-FIDELITY)
**Hệ thống:** Rentify Property Rental Management
**Nền tảng:** Responsive Desktop Web (Viewport 1440 × 1024 px)
**Vai trò:** System Administrator (Super Admin & Sub-Admin)
**Nguồn căn cứ:** Phase 1 Approved Plan, `updated_admin_user_flow.md`, Linear Comments `PBL-29`

---

## 1. MẪU BỐ CỤC CHUẨN (APPLICATION SHELL - 1440 × 1024 px)

```
+---------------------------------------------------------------------------------------------------------------+
| LOGO: RENTIFY ADMIN  |  Trang chủ > Quản lý Người dùng                     | [Chuông Thông Báo] [Avatar Admin v] |
+----------------------+----------------------------------------------------------------------------------------+
| [DASHBOARD]          | TIÊU ĐỀ TRANG: QUẢN LÝ NGƯỜI DÙNG                                                      |
|  * Tổng quan         | [Tìm kiếm...           ] [Role: Tất cả v] [Trạng thái: Tất cả v]    [+ Xuất dữ liệu]   |
|                      +----------------------------------------------------------------------------------------+
| [NGƯỜI DÙNG] (Active)| | ID   | Họ và tên   | SĐT        | Email          | Role     | Trạng thái | Thao tác  | |
|  * Danh sách User    | |------|-------------|------------|----------------|----------|------------|-----------| |
|                      | | U01  | Nguyễn Văn A| 0901234567 | a@gmail.com    | LANDLORD | [Active]   | [Chi tiết]| |
| [ĐỘI NGŨ ADMIN]      | | U02  | Trần Thị B  | 0912345678 | b@gmail.com    | TENANT   | [Active]   | [Chi tiết]| |
|  * Quản lý Admin     | | U03  | Lê Văn C    | 0988888888 | c@gmail.com    | LANDLORD | [Locked]   | [Chi tiết]| |
|                      | +----------------------------------------------------------------------------------------+
| [CẤU HÌNH HỆ THỐNG]  | Trang 1 / 10  [ < Trước ] [ 1 ] [ 2 ] [ 3 ] ... [ 10 ] [ Sau > ]                       |
|  * Tham số kỹ thuật  |                                                                                        |
|                      |                                                                                        |
| [AUDIT LOGS]         |                                                                                        |
|  * Nhật ký giám sát  |                                                                                        |
|                      |                                                                                        |
| [ĐĂNG XUẤT]          |                                                                                        |
+----------------------+----------------------------------------------------------------------------------------+
```

---

## 2. CHI TIẾT CÁC MÀN HÌNH QUẢN TRỊ (ADMIN SCREENS)

### SCR-ADM-01: Admin Login Screen (`/admin/login`)
* **Mục đích:** Xác thực danh tính quản trị viên, kiểm tra role `ADMIN` trong JWT.
* **Layout:** Card căn giữa màn hình (440px width), bề mặt nền xám nhạt (`#F5F5F5`).
* **Wireframe:**
```
+-------------------------------------------------------------+
|                                                             |
|                   +-----------------------+                 |
|                   |     RENTIFY ADMIN     |                 |
|                   |  Đăng nhập Quản trị   |                 |
|                   +-----------------------+                 |
|                   | Email / Số điện thoại |                 |
|                   | [ admin@rentify.vn  ] |                 |
|                   |                       |                 |
|                   | Mật khẩu              |                 |
|                   | [ **********       O] |                 |
|                   |                       |                 |
|                   | [X] Ghi nhớ đăng nhập |                 |
|                   |                       |                 |
|                   | [   ĐĂNG NHẬP NGAY  ] |                 |
|                   +-----------------------+                 |
|                   | (c) 2026 Rentify Team |                 |
|                                                             |
+-------------------------------------------------------------+
```

---

### SCR-ADM-02: Admin Dashboard (`/admin/dashboard`)
* **Mục đích:** Tổng quan hệ thống, sức khỏe hạ tầng, cảnh báo khẩn cấp.
* **Wireframe:**
```
+----------------------+----------------------------------------------------------------------------------------+
| [SIDEBAR ADMIN]      | BẢNG ĐIỀU KHIỂN QUẢN TRỊ HỆ THỐNG                                [Bộ lọc: 30 ngày qua v]|
|                      +--------------------+-------------------+--------------------+--------------------------+
|                      | TỔNG NGƯỜI DÙNG    | TỔNG BẤT ĐỘNG SẢN | TỶ LỆ LẤP ĐẦY      | DOANH THU HỆ THỐNG       |
|                      | 1,248 Users        | 142 Tòa - 1,850 P | 84.5% Occupied     | 3,420,000,000 đ          |
|                      | (+12% tháng này)   | (+4 tòa mới)      | [||||||||||--]     | (+8.2% cùng kỳ)          |
|                      +--------------------+-------------------+--------------------+--------------------------+
|                      | CẢNH BÁO KỸ THUẬT & HẠ TẦNG            | TRẠNG THÁI DỊCH VỤ LIÊN KẾT                   |
|                      | [!] 2 Webhook thanh toán VietQR bị lỗi | * Cổng thanh toán: [ MOCK GATEWAY (R1) - BẬT ]|
|                      |     (Đã tự động chuyển hàng đợi retry) | * AI Adapter:      [ GOOGLE GEMINI (D3)      ]|
|                      | [!] 1 Tài khoản có dấu hiệu brute-force| * Cron Quét Nợ:    [ ĐANG CHẠY (2h/lần)      ]|
|                      |     (IP: 118.69.xxx.xxx - Đã tạm khóa) |                                              |
|                      +----------------------------------------+-----------------------------------------------+
|                      | NHẬT KÝ HOẠT ĐỘNG QUẢN TRỊ GẦN ĐÂY     [Xem toàn bộ nhật ký Audit Logs ->]             |
|                      | * 09:15 - Super Admin vừa tạo tài khoản Sub-Admin: admin_phuong@rentify.vn             |
|                      | * 08:40 - Hệ thống kích hoạt khóa tài khoản User: 0905123456 (Lý do: Vi phạm điều khoản)|
|                      | * 00:00 - Cron job hoàn tất đối soát hóa đơn định kỳ kỳ T08/2026                       |
+----------------------+----------------------------------------------------------------------------------------+
```

---

### SCR-ADM-03: User Management Directory (`/admin/users`)
* **Mục đích:** Tìm kiếm, phân loại và quản trị danh sách người dùng toàn hệ thống.
* **Ràng buộc UI:** Hiển thị role enum đơn (`ADMIN` | `LANDLORD` | `TENANT`), không dùng array.
* **Wireframe:**
```
+----------------------+----------------------------------------------------------------------------------------+
| [SIDEBAR ADMIN]      | QUẢN LÝ NGƯỜI DÙNG TOÀN HỆ THỐNG                                                       |
|                      |                                                                                        |
|                      | [ Ô tìm kiếm: Nhập Tên, SĐT, Email...   ] [Vai trò: Tất cả v] [Trạng thái: Tất cả v]   |
|                      +----------------------------------------------------------------------------------------+
|                      | ID   | Họ và tên     | Số điện thoại | Email           | Vai trò  | Trạng thái | Hành động |
|                      |------|---------------|---------------|-----------------|----------|------------|-----------|
|                      | #101 | Thái Bảo      | 0905111222    | bao@gmail.com   | LANDLORD | [Active]   | [Chi tiết]|
|                      | #102 | Thu Phương    | 0905333444    | phuong@gmail.com| TENANT   | [Active]   | [Chi tiết]|
|                      | #103 | Khải Lê       | 0905555666    | khai@gmail.com  | LANDLORD | [Locked]   | [Chi tiết]|
|                      | #104 | Hoàng Long    | 0905777888    | long@gmail.com  | TENANT   | [Active]   | [Chi tiết]|
|                      +----------------------------------------------------------------------------------------+
|                      | Đang hiển thị 1-10 trong tổng số 1,248 người dùng          [ Trang 1 / 125 ] [<] [>]    |
+----------------------+----------------------------------------------------------------------------------------+
```

---

### SCR-ADM-04: User Detail & Action Drawer (`/admin/users/:id`)
* **Mục đích:** Xem chi tiết người dùng, khóa tài khoản hoặc đổi role có kiểm tra ràng buộc tài sản.
* **Ràng buộc UI:** Bị chặn đổi role nếu tài khoản Landlord đang sở hữu Tòa nhà/Phòng/HĐ hoạt động.
* **Wireframe (Drawer trượt từ phải sang):**
```
+-----------------------------------------------------------------------+=======================================+
|                                                                       | CHI TIẾT NGƯỜI DÙNG              [X]  |
|                                                                       +---------------------------------------+
|                                                                       | [Avatar]  THÁI BẢO                    |
|                                                                       |           ID: #101 - [LANDLORD]       |
|                                                                       |           Trạng thái: [Đang hoạt động]|
|                                                                       +---------------------------------------+
|                                                                       | THÔNG TIN ĐỊNH DANH                   |
|                                                                       | * Số điện thoại: 0905111222           |
|                                                                       | * Email:         bao@gmail.com        |
|                                                                       | * Ngày tham gia: 15/08/2026           |
|                                                                       | * Xác minh CCCD: ĐÃ XÁC MINH          |
|                                                                       +---------------------------------------+
|                                                                       | TÀI SẢN & DỮ LIỆU ĐANG VẬN HÀNH       |
|                                                                       | * Tòa nhà sở hữu:   3 Tòa             |
|                                                                       | * Phòng quản lý:    24 Phòng          |
|                                                                       | * HĐ đang hiệu lực: 20 Hợp đồng       |
|                                                                       +---------------------------------------+
|                                                                       | THAO TÁC QUẢN TRỊ                     |
|                                                                       | [ ! KHÓA TÀI KHOẢN NÀY ]              |
|                                                                       |                                       |
|                                                                       | [ THAY ĐỔI VAI TRÒ (ROLE) ]           |
|                                                                       |                                       |
|                                                                       | [!] CẢNH BÁO RÀNG BUỘC (Khi bấm đổi): |
|                                                                       | "Không thể chuyển vai trò của User này|
|                                                                       |  vì đang sở hữu 3 tòa nhà và 20 HĐ.   |
|                                                                       |  Vui lòng thanh lý tài sản trước!"    |
+-----------------------------------------------------------------------+=======================================+
```

---

### SCR-ADM-05: Admin Team Management (`/admin/admins`)
* **Mục đích:** Phân cấp quản trị đội ngũ: Super Admin (Root) vs Sub-Admin.
* **Ràng buộc UI:** Sub-Admin không được xóa lẫn nhau; Tài khoản Root không thể bị xóa/thu hồi quyền.
* **Wireframe:**
```
+----------------------+----------------------------------------------------------------------------------------+
| [SIDEBAR ADMIN]      | QUẢN LÝ ĐỘI NGŨ QUẢN TRỊ VIÊN (SUPER ADMIN ONLY)              [ + Thêm Admin Mới ]     |
|                      +----------------------------------------------------------------------------------------+
|                      | Tên Admin       | Email                | Phân cấp      | Ngày cấp quyền | Thao tác     |
|                      |-----------------|----------------------|---------------|----------------|--------------|
|                      | Root Admin      | root@rentify.vn      | [SUPER ADMIN] | Khởi tạo HT    | [Khóa cứng]  |
|                      | Nguyễn Quản Trị | admin_nguyen@rentify | [SUB-ADMIN]   | 20/08/2026     | [Thu hồi quy]|
|                      | Trần Điều Hành  | admin_tran@rentify   | [SUB-ADMIN]   | 01/09/2026     | [Thu hồi quy]|
|                      +----------------------------------------------------------------------------------------+
|                      | [i] Ghi chú bảo mật:                                                                   |
|                      | - Super Admin có toàn quyền tạo mới và xóa bỏ Sub-Admin.                              |
|                      | - Tài khoản Root không thể bị xóa hoặc thay đổi quyền bởi bất kỳ ai.                  |
+----------------------+----------------------------------------------------------------------------------------+
```

---

### SCR-ADM-06: System Configuration (`/admin/settings`)
* **Mục đích:** Cấu hình tham số kỹ thuật (Mock Payment R1, AI Provider Adapter D3, Cron bot).
* **Wireframe:**
```
+----------------------+----------------------------------------------------------------------------------------+
| [SIDEBAR ADMIN]      | CẤU HÌNH THAM SỐ VẬN HÀNH HỆ THỐNG                                                     |
|                      +----------------------------------------------------------------------------------------+
|                      | 1. CỔNG THANH TOÁN (PAYMENT GATEWAY - R1)                                              |
|                      |    [ ON ] Bật chế độ Mock Payment Gateway (Dùng cho môi trường demo / chấm điểm)      |
|                      |    * Ghi chú: Khi bật, các giao diện thanh toán sẽ có nút giả lập quét mã thành công. |
|                      +----------------------------------------------------------------------------------------+
|                      | 2. AI ADAPTER PROVIDER (DECISION D3)                                                   |
|                      |    ( ) OpenAI API (GPT-4o-mini)                                                        |
|                      |    (*) Google Gemini API (Gemini 1.5 Flash - Adapter đo lường chi phí)                 |
|                      |    API Key: [ **************************************** ]                               |
|                      +----------------------------------------------------------------------------------------+
|                      | 3. TỰ ĐỘNG HÓA & CRON JOBS                                                             |
|                      |    Chu kỳ quét hóa đơn quá hạn: [ 2 ] giờ / lần                                        |
|                      |    [X] Tự động bắn thông báo nhắc nợ qua Bot Property Chat khi hóa đơn quá hạn 3 ngày |
|                      +----------------------------------------------------------------------------------------+
|                      |                                                          [  LƯU CẤU HÌNH HỆ THỐNG  ]   |
+----------------------+----------------------------------------------------------------------------------------+
```

---

### SCR-ADM-07: Audit & System Logs (`/admin/logs`)
* **Mục đích:** Giám sát nhật ký hoạt động hệ thống và kiểm toán an ninh.
* **Wireframe:**
```
+----------------------+----------------------------------------------------------------------------------------+
| [SIDEBAR ADMIN]      | NHẬT KÝ KIỂM TOÁN HỆ THỐNG (AUDIT LOGS)                       [ Xuất File CSV / JSON ] |
|                      | [Khoảng thời gian: Hôm nay v] [Phân loại sự kiện: Tất cả v] [Tìm kiếm: IP/Actor...   ] |
|                      +----------------------------------------------------------------------------------------+
|                      | Thời gian       | Tác nhân (Actor)  | Loại sự kiện    | Địa chỉ IP     | Chi tiết log  |
|                      |-----------------|-------------------|-----------------|----------------|---------------|
|                      | 06/09 09:15:02  | Super Admin       | USER_CREATE     | 14.161.xxx.xxx | Tạo Sub-Admin |
|                      | 06/09 08:30:11  | VietQR Webhook    | PAYMENT_WEBHOOK | 118.69.xxx.xxx | Khớp HĐ #8812 |
|                      | 06/09 07:12:45  | System Bot        | CRON_REMINDER   | localhost      | Quét 14 HĐ trễ|
|                      | 05/09 23:45:10  | Sub-Admin Nguyễn  | USER_LOCK       | 27.67.xxx.xxx  | Khóa user #103|
|                      +----------------------------------------------------------------------------------------+
|                      | Hiển thị 50 log mới nhất thời gian thực                       [ < Trước ] [ Sau > ]    |
+----------------------+----------------------------------------------------------------------------------------+
```

