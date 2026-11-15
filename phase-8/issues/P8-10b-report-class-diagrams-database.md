# P8-10b — Sơ đồ lớp hệ thống, ERD và tài liệu khởi tạo cơ sở dữ liệu

**Epic:** [P8-10](P8-10-final-report-package.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** `leminhkhai345` (Lê Minh Khai)  
**Người review:** `baoduong17` / `ThaiBao11125` (Lead Report Author)  
**Ước lượng:** 2 points · 8 giờ (**tối đa 3 points và khoảng 15 file mỗi PR**)  
**Phụ thuộc:** P8-01, P8-06  
**Repo / branch:** `docs/` · `docs/p8-10b-report-class-diagrams-db`  
**Issue:** `docs#TBD`

> **Đọc trước khi thực hiện:** Đọc `Report/AGENTS.md`, `Report/khungbaocao.md` và `Report/phancong.md`. Mọi sơ đồ lớp và mô hình thực thể quan hệ ERD phải bám sát chính xác các entity, bảng cơ sở dữ liệu và thuộc tính thực tế trong mã nguồn của cả 3 vi dịch vụ.

## Mục tiêu

Xây dựng và bàn giao đầy đủ sơ đồ lớp hệ thống (Class Diagram) và mô hình thực thể quan hệ ERD cho cả 3 vi dịch vụ (Identity, Tenancy, Community), cùng tài liệu hướng dẫn khởi tạo cơ sở dữ liệu và thực thi migration để người phụ trách chính báo cáo (`ThaiBao11125`) tích hợp vào mục 1.4 và mục 5.3 của báo cáo đồ án.

## Quyết định áp dụng

- Thống nhất mô hình cơ sở dữ liệu riêng biệt: mỗi vi dịch vụ sở hữu cơ sở dữ liệu PostgreSQL độc lập, quan hệ giữa các dịch vụ thể hiện qua các khóa ngoại logic (UUID).
- Sơ đồ lớp được chuẩn hóa theo chuẩn UML, thể hiện rõ các thuộc tính, phương thức cốt lõi và quan hệ (1-1, 1-n, n-n).
- Tham khảo thêm mã nguồn entity của `Identity-Service/`, `Tenancy-Service/` và `community-service/` để tổng hợp đầy đủ các thực thể.
- Bàn giao dưới dạng sơ đồ nét cao (mermaid / PNG) kèm mô tả thuộc tính và các câu lệnh chạy migration chuẩn xác.

## Chi tiết các nội dung cần bàn giao

| Mã mục | Tên mục trong khung báo cáo | Nội dung kỹ thuật và sơ đồ cần bàn giao |
|---|---|---|
| 1.4.1 | Sơ đồ lớp dịch vụ định danh và xác thực tài khoản | Vẽ sơ đồ lớp chi tiết các thực thể: tài khoản người dùng (User), hồ sơ cá nhân (Profile), hồ sơ chủ trọ (LandlordProfile), thiết bị nhận thông báo (Device), vai trò (Role) và quyền hạn (Permission) |
| 1.4.2 | Sơ đồ lớp dịch vụ quản lý bất động sản và thuê trọ | Vẽ sơ đồ lớp toàn diện bao gồm: bất động sản (Building), tầng (Floor), phòng trọ (Room), tiện ích (Amenity), tài sản (Asset), hợp đồng thuê phòng (Contract), văn bản ký tay (SignedContract), thành viên phòng (ContractMember), cấu hình biểu giá dịch vụ (BillingSetting, RatePolicy), công tơ, chỉ số điện nước (MeterReading), hóa đơn (Invoice) và bản ghi thanh toán (PaymentRecord) |
| 1.4.3 | Sơ đồ lớp dịch vụ tương tác và cộng đồng | Vẽ sơ đồ lớp chi tiết các thực thể: cuộc hội thoại (Conversation), thành viên hội thoại (ConversationMember), tin nhắn thời gian thực (Message), tệp đính kèm (Attachment), thông báo (Notification) và báo cáo sự cố (IssueReport) |
| 5.3 | Khởi tạo cơ sở dữ liệu và thực thi di chuyển dữ liệu | Cung cấp danh mục các câu lệnh thực thi di chuyển lược đồ bảng dữ liệu cho từng dịch vụ và nạp bộ dữ liệu mẫu ban đầu |

## Tham chiếu mã nguồn và lược đồ

- `Identity-Service/src/` (thư mục entity, TypeORM/Prisma migration).
- `Tenancy-Service/src/` (thư mục entity, migration của building, room, contract, billing, meter reading, invoice).
- `community-service/src/` (thư mục entity conversation, message, notification).
- Tài liệu thiết kế cơ sở dữ liệu trong `docs/`.

## Các bước triển khai

### Bước 1 — Thiết kế sơ đồ lớp Dịch vụ định danh (Mục 1.4.1)
- **Cách làm:** Trích xuất các thực thể trong `Identity-Service`, vẽ sơ đồ lớp thể hiện rõ các bảng User, Profile, LandlordProfile, Device, Role.
- **Kiểm tra bước:** Thuộc tính và kiểu dữ liệu (UUID, string, enum) khớp chính xác với schema database.

### Bước 2 — Thiết kế sơ đồ lớp Dịch vụ thuê trọ (Mục 1.4.2)
- **Cách làm:** Tổng hợp các thực thể bất động sản, hợp đồng (phần Khai trực tiếp code) và phần biểu giá, hóa đơn (tham khảo code của Nhật) thành một sơ đồ lớp hoàn chỉnh.
- **Kiểm tra bước:** Thể hiện rõ các quan hệ giữa Building, Room, Contract, Member, BillingSetting, MeterReading, Invoice.

### Bước 3 — Thiết kế sơ đồ lớp Dịch vụ cộng đồng (Mục 1.4.3)
- **Cách làm:** Tham khảo entity trong `community-service` của Chí Bảo để vẽ sơ đồ lớp Conversation, Message, Notification, IssueReport.
- **Kiểm tra bước:** Các quan hệ giữa conversation, member và message được biểu diễn chính xác.

### Bước 4 — Soạn thảo hướng dẫn Migration và Seed dữ liệu (Mục 5.3)
- **Cách làm:** Kiểm tra và liệt kê các câu lệnh `npm run migration:run`, `npm run seed` từ thư mục gốc hoặc từng service; kiểm tra khả năng chạy mượt mà từ DB trống.
- **Kiểm tra bước:** Câu lệnh chạy thành công, không gặp lỗi foreign key hoặc thiếu extension.

### Bước 5 — Bàn giao cho Lead Author (`ThaiBao11125`)
- **Cách làm:** Bàn giao tài liệu markdown và các tệp sơ đồ để tích hợp vào `Report/01_chuong1.md` và `Report/05_chuong5.md`.
- **Kiểm tra bước:** `ThaiBao11125` xác nhận nhận đủ 3 sơ đồ lớp và hướng dẫn migration.

## Ngoài phạm vi

- Viết nội dung mô tả chức năng chi tiết hoặc kịch bản kiểm thử.
- Sơ đồ kiến trúc (P8-10a), sơ đồ tuần tự (P8-10c), sơ đồ use case (P8-10d).

## Blocker

- Không có. Nếu cần làm rõ schema của Billing/Invoice hoặc Community thì trao đổi trực tiếp với `huynhtiennhat0403` hoặc `baoduong17`.

## Acceptance

- [ ] Đủ 3 sơ đồ lớp (1.4.1, 1.4.2, 1.4.3) đúng chuẩn UML, rõ ràng thuộc tính và mối quan hệ.
- [ ] Mục 5.3 có hướng dẫn chi tiết các lệnh migration và seed dữ liệu cho từng vi dịch vụ.
- [ ] Bàn giao toàn bộ sản phẩm đúng hạn cho `ThaiBao11125`.

## Definition of Done

- [ ] `baoduong17` và `ThaiBao11125` duyệt chất lượng sơ đồ lớp.
- [ ] Toàn bộ nội dung được tích hợp vào tài liệu báo cáo của dự án.
