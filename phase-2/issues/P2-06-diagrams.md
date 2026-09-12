# P2-06 — Process Diagrams

**Status:** 🟡 Open
**Owner:** PM + BE
**Input:** P2-01, P2-04, P2-05, user_flow/*.md
**Output:** `discovery/diagrams/`

---

## Background

Có đầy đủ feature map, ERD, API spec. Giờ cần vẽ diagram mô tả **quy trình nghiệp vụ** — giúp team hiểu flow trước khi code.

## Mục đích

Tạo 3 loại diagram: use case, sequence, activity — cover toàn bộ key flows.

## Chi tiết thực hiện

### 1. Use Case Diagrams (mỗi role 1 diagram)

| Role | Actor chính | Use cases |
|------|------------|-----------|
| Landlord | Chủ trọ | Quản lý BĐS, Quản lý phòng, Tạo HĐ, Chốt điện nước, Lập hóa đơn, Theo dõi thanh toán, Quản lý sự cố, Chat, Cài đặt đơn giá |
| Tenant | Khách thuê | Tìm phòng, Xem chi tiết, Ghép bạn, Xem hóa đơn, Thanh toán, Báo sự cố, Chat, Xem hợp đồng |
| Admin | Quản trị viên | Quản lý user, Duyệt BĐS, Cấu hình biểu giá, Xem audit log |
| Shared | Cả hai | Đăng nhập, Quản lý profile, Đọc thông báo |

- Format: mermaid `classDiagram` hoặc `usecaseDiagram`

### 2. Sequence Diagrams (key flows)

Chọn 6–8 flow quan trọng nhất:

| # | Flow | Actors |
|---|------|--------|
| 1 | Đăng nhập (Google OTP) | User → BE → Google OAuth |
| 2 | Tạo hợp đồng + upload signed | Landlord → BE → DB |
| 3 | Chốt số điện nước (OCR) | Landlord → BE → OCR → DB |
| 4 | Auto-sinh hóa đơn | BE (cron) → DB → FCM |
| 5 | Thanh toán QR | Tenant → BE → Payment Gateway → DB |
| 6 | Property Chat realtime | Tenant/Landlord → BE → Socket.io → DB |
| 7 | Báo sự cố @issue | Tenant → BE → Bot → Landlord |
| 8 | AI Auto-Description | Landlord → BE → AI Service → BE |

- Format: mermaid `sequenceDiagram`

### 3. Activity Diagrams (2–3 flow chính)

| Flow | Nội dung |
|------|----------|
| Utility Closing | Từ bắt đầu kỳ → OCR baseline → chốt hàng tháng → đủ data → tạo invoice |
| Invoice Lifecycle | Draft → Pending → Issued → Paid / Partially Paid / Overdue / Void |
| Payment Reconciliation | QR generated → tenant pay → webhook → confirm → update invoice |

- Format: mermaid `flowchart` (activity style)

## Definition of Done

- [ ] Folder `discovery/diagrams/` tồn tại
- [ ] Use case diagram cho 4 roles — mermaid syntax valid
- [ ] Sequence diagrams cho 8 flows — mermaid syntax valid
- [ ] Activity diagrams cho 3 flows — mermaid syntax valid
- [ ] Mỗi diagram có title + 1 dòng mô tả context
- [ ] Diagrams nhất quán với user flow + API spec
- [ ] PM đã review và approve
