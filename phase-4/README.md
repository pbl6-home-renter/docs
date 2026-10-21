# Phase 4 — Core Features & Service Implementations (W9–12)

> **Checkpoint:** W11 (M4) — Demo Feature-Complete trên Staging / EC2.  
> **Trọng tâm mở đầu:** Hoàn thiện `identity-service` (Auth, User Profile, JWKS) theo chuẩn Clean Architecture & Microservice để mở khoá luồng đăng nhập cho Mobile và Web.

## 1. Mục tiêu & Định hướng Phase 4

Phase 4 là giai đoạn chuyển đổi toàn bộ hệ thống từ khung sườn (Scaffolding / Mock) sang **triển khai mã nguồn nghiệp vụ thực tế**.
Để tránh tình trạng dàn trải và quá tải cho 1 backend engineer, Phase 4 được chia thành các sprint nhỏ tuần tự:

1. **Sprint 1 (Ngay lập tức):** Triển khai trọn vẹn **`identity-service`** (Auth, JWT, Refresh Token, User Profile, JWKS) để Mobile và Web có thể login thật và lưu session.
2. **Sprint 2:** Triển khai **`tenancy-service`** (Building, Room, Contract cơ bản) — mở khóa luồng duyệt phòng và thông tin thuê trọ.
3. **Sprint 3:** Triển khai **Điện nước, Hóa đơn & Thanh toán VietQR** (Utility Closing, Invoice, VietQR sandbox).
4. **Sprint 4:** Tích hợp **Property Chat & Sự cố** (Community service, Socket.io, FCM).

---

## 2. Danh sách Task Phase 4

Xem chi tiết bảng theo dõi, phân công và tiến độ tại: **[issues/README.md](issues/README.md)**.

## 3. Phase 4 closure — 2026-10-21

Phase 4 is closed for documentation and checkpoint reporting. Completed work is marked `Done` in the issue table; unfinished work remains visible and carries over instead of being treated as complete.

### Completed and verified

- Identity foundation, database migrations, registration/login, profile/guards, RS256/JWKS, password reset, admin management and admin seeder.
- Web foundation and application shell/base UI work recorded in the corresponding frontend issues.
- Supabase/keepalive setup and EC2 staging infrastructure.
- Boilerplate integration now includes transactional Outbox/Inbox, Unit of Work and RabbitMQ publisher/relay infrastructure.

### Carry-over to Phase 5

- Identity refresh/logout end-to-end completion (`P4-04`).
- Apidog/token automation and API contract governance (`P4-15`, `P4-27`).
- Remaining frontend refinement and auth/API integration (`P4-10`, `P4-17`).
- Tenancy service bootstrap and Building/Room vertical slices (`P4-21`, `P4-24`, `P4-25`).
