# P4-13 — Xây dựng Database Seeder & Khởi tạo Tài khoản Quản trị viên (Admin Initializer)

**Status:** 🟢 Done
**Assignee:** BE Dev  
**Stakeholders / Reviewers:** BE Lead, PM, DevOps / Infra  
**Created:** 2026-10-11  
**Due date:** 2026-10-14  
**Priority:** 🔴 High / Blocker (Bắt buộc để đăng nhập & kiểm thử phân hệ Web Admin)  

**Input:**
- Quyết định kiến trúc: D13 (Web hỗ trợ Landlord Ops Console & Admin)
- Ràng buộc đăng ký: `pm/phase-2/discovery/api-spec.md` (§2 Auth: API 1 cấm public đăng ký vai trò `admin`)
- Cấu hình CSDL TypeORM hiện tại của `identity-service`

**Deliverables:**
- Bổ sung cấu hình thông tin tài khoản quản trị viên mặc định vào `.env.example`.
- Script hoặc dịch vụ Seeder độc lập phục vụ khởi tạo tài khoản Admin ban đầu.
- Tích hợp lệnh CLI chạy Seeder vào quy trình khởi chạy ứng dụng / migration.
- Hướng dẫn vận hành và kiểm thử đăng nhập tài khoản quản trị.

---

## 1. Bối cảnh & Yêu cầu kỹ thuật

### 1. Lý do cần cơ chế Seeding tài khoản Admin
- Endpoint đăng ký tài khoản công khai (`POST /auth/register`) nghiêm cấm tạo người dùng có vai trò `admin`.
- Để phục vụ kiểm thử phân hệ Admin Console và duyệt dữ liệu trong môi trường phát triển, hệ thống cần có cơ chế tự động khởi tạo sẵn ít nhất một tài khoản Quản trị viên ban đầu.

### 2. Yêu cầu nghiệp vụ & Tính lũy thừa (Idempotency)
- **Nguồn cấu hình:** Thông tin tài khoản Admin mặc định (email, mật khẩu, tên, số điện thoại) được lấy từ các biến môi trường định nghĩa trong `.env`.
- **Mã hóa an toàn:** Mật khẩu của tài khoản Admin phải được băm bảo mật theo cùng thuật toán bcrypt đang sử dụng trong hệ thống trước khi lưu vào cơ sở dữ liệu.
- **Tính lũy thừa (Idempotency):**
  - Trước khi khởi tạo, script phải kiểm tra sự tồn tại của tài khoản quản trị viên (theo email cấu hình).
  - Nếu tài khoản đã tồn tại: bỏ qua và ghi nhận thông báo tương ứng, tuyệt đối không ném lỗi trùng khóa chính và không ghi đè mật khẩu đang dùng của tài khoản.
  - Nếu tài khoản chưa tồn tại: tiến hành tạo mới với vai trò `admin` và trạng thái `active`.
- **Khởi chạy linh hoạt:** Hỗ trợ chạy script qua lệnh dòng lệnh thủ công và có thể tích hợp vào tiến trình khởi động container/môi trường phát triển.

---

## 2. Tiêu chí nghiệm thu (Definition of Done)

1. **Khởi tạo dữ liệu thành công:**
   - Chạy script seeder tạo thành công tài khoản quản trị viên với vai trò `admin` và trạng thái `active` trong cơ sở dữ liệu `identity_db`.
2. **Đảm bảo tính Idempotent:**
   - Thực thi lại script nhiều lần liên tiếp không gây lỗi hệ thống và không phát sinh bản ghi trùng lặp.
3. **Kiểm thử đăng nhập thực tế:**
   - Sử dụng thông tin đăng nhập của Admin vừa khởi tạo gọi vào `POST /auth/login` đăng nhập thành công.
   - Token trả về chứa định danh và vai trò `admin`, có thể sử dụng để truy cập các route quản trị của hệ thống.
