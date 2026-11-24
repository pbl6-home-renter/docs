# Phase 12 — Tracker

Bảng này là nguồn trạng thái chính thức; cập nhật cùng lúc với file issue.

| ID | Issue | Repo | Owner đề xuất | Ước lượng | Phụ thuộc | Trạng thái |
|---|---|---|---|---|---|---|
| P12-01 | [Nền tảng thông báo: quy ước payload và registry trên Web](P12-01-notification-conventions.md) | `community-service`, `fe` | PM/leader | 2 points | — | 🔵 In review |
| P12-02 | [Thông báo khóa/mở tài khoản theo quy ước mới](P12-02-identity-account-lock-notification.md) | `Identity-Service`, `community-service`, `fe`, `api-doc` | `huynhtiennhat0403` | 1 point | P12-01 | 🔵 In progress |
| P12-03 | [Thông báo khóa hợp đồng và hóa đơn phát hành theo quy ước mới](P12-03-tenancy-existing-notifications.md) | `Tenancy-Service`, `fe` | `leminhkhai345` | 2 points | P12-01 | 🟡 Open |
| P12-04 | [Báo landlord khi admin duyệt hoặc từ chối tòa](P12-04-building-review-notification.md) | `Tenancy-Service`, `fe`, `api-docs` | `baoduong17` | 2 points | P12-01 | 🟡 Open |
| P12-05 | [Báo admin khi có tòa mới chờ duyệt](P12-05-building-pending-review-notification.md) | `Identity-Service`, `Tenancy-Service`, `fe` | `huynhtiennhat0403` (Identity) + `baoduong17` (Tenancy) | 3 points | P12-01, P12-04 | 🟡 Open |
| P12-06 | [Báo tenant khi hóa đơn đã phát hành bị hủy](P12-06-invoice-voided-notification.md) | `Tenancy-Service`, `fe` | `leminhkhai345` | 1 point | P12-01, P12-03 | 🟡 Open |
| P12-07 | [Báo tenant khi hợp đồng được kích hoạt hoặc trả phòng](P12-07-contract-lifecycle-notification.md) | `Tenancy-Service`, `fe` | BE Tenancy (PM giao) | 2 points | P12-01 | 🟡 Open |
| P12-08 | [Thông báo thành viên được thêm, liên kết và rời hợp đồng](P12-08-contract-member-notification.md) | `Tenancy-Service`, `fe` | BE Tenancy (PM giao) | 2 points | P12-01 | 🟡 Open |

**Tổng:** 15 points. Owner là **đề xuất**, PM xác nhận khi giao.
