# Phase 13 — Tracker

Bảng này là nguồn trạng thái chính thức; cập nhật cùng lúc với file issue.

| ID | Issue | Repo | Owner đề xuất | Review | Ước lượng | Phụ thuộc | Trạng thái |
|---|---|---|---|---|---|---|---|
| P13-01 | [BE: Gỡ saga tạm ngưng hợp đồng khi khóa landlord](P13-01-remove-landlord-lock-saga-backend.md) | `Tenancy-Service`, `api-docs` | `leminhkhai345` | `baoduong17` | 3 points | — | 🟡 Open |
| P13-02 | [FE: Gỡ giao diện tạm ngưng hợp đồng](P13-02-remove-landlord-lock-saga-frontend.md) | `fe` | `ThaiBao11125` | PM/leader | 1 point | P13-01 | 🟡 Open |
| P13-03 | [Gỡ quyền thanh toán của tài khoản bị khóa (chỉnh P12-09/P12-10)](P13-03-locked-account-remove-payment.md) | `Tenancy-Service`, `fe`, `api-docs` | người làm P12-09 + `ThaiBao11125` | PM/leader | 1 point | — | 🟡 Open |
| P13-04 | [BE: Tenancy ghi nhận landlord bị khóa, ẩn tòa, trả cờ cho tenant](P13-04-tenancy-landlord-lock-flag.md) | `Tenancy-Service`, `api-docs` | `baoduong17` | `leminhkhai345` | 2 points | P13-01 | 🟡 Open |
| P13-05 | [FE/Mobile: Ẩn QR thanh toán khi landlord bị khóa](P13-05-hide-payment-qr-locked-landlord.md) | `fe`, `mobile` | `ThaiBao11125` + Mobile | PM/leader | 1 point | P13-04 | 🟡 Open |
| P13-06 | [Nhãn "Tài khoản đã bị khóa" trong chat](P13-06-chat-locked-user-label.md) | `community-service`, `fe`, `mobile`, `api-docs` | `huynhtiennhat0403` + `ThaiBao11125` + Mobile | PM/leader | 2 points | — | 🟡 Open |
| P13-07 | [Hóa đơn: landlord đánh dấu "Đã thu"](P13-07-invoice-mark-paid.md) | `Tenancy-Service`, `api-docs`, `fe`, `mobile` | `leminhkhai345` + `ThaiBao11125` + Mobile | `baoduong17`, PM/leader | 3 points | — | 🟡 Open |
| P13-08 | [BE: Ghép bạn với tài khoản bị khóa](P13-08-roommate-locked-user.md) | `Tenancy-Service`, `api-doc`, `docs` | BE Tenancy (PM giao) | `leminhkhai345` | 1 point | — | 🔵 In progress |
| P13-09 | [FE: Gợi ý lý do khi admin khóa tài khoản](P13-09-lock-reason-suggestions.md) | `fe` | `ThaiBao11125` | PM/leader | 0.5 point | — | 🟡 Open |
| P13-10 | [FE: Nhắc landlord cập nhật dữ liệu sau khi mở khóa](P13-10-post-unlock-banner.md) | `fe` | `ThaiBao11125` | PM/leader | 1 point | P13-07 | 🟡 Open |
| P13-11 | [Báo cáo vi phạm và khiếu nại (issue tổng)](P13-11-report-and-appeal-deferred.md) | nhiều repo | PM/leader | — | = P13-15…19 | P13-09 | 🟡 Open (D109) |

### Sửa lỗi từ feedback review (26/11/2026)

| ID | Issue | Repo | Owner đề xuất | Review | Ước lượng | Phụ thuộc | Trạng thái |
|---|---|---|---|---|---|---|---|
| P13-12 | [BE: Sửa tính tiền điện/nước khoán theo đầu người](P13-12-invoice-per-head-utility-fix.md) | `Tenancy-Service` | `leminhkhai345` | `baoduong17` | 1 point | — | 🟡 Open · ưu tiên cao |
| P13-13 | [BE: Cho phép mã ngân hàng ngắn](P13-13-bank-code-length.md) | `Identity-Service`, `api-docs`, `fe` | `huynhtiennhat0403` | `baoduong17` | 0.5 point | — | 🟡 Open |
| P13-14 | [Hóa đơn hiển thị minh bạch](P13-14-invoice-detail-transparency.md) | `Tenancy-Service`, `api-docs`, `fe` | `baoduong17` + `ThaiBao11125` | `leminhkhai345`, PM/leader | 3 points | P13-12 | 🟡 Open |

### Báo cáo vi phạm và khiếu nại (P13-11, duyệt ở D109 ngày 27/11/2026)

| ID | Issue | Repo | Owner đề xuất | Review | Ước lượng | Phụ thuộc | Trạng thái |
|---|---|---|---|---|---|---|---|
| P13-15 | [BE: Khiếu nại khóa tài khoản](P13-15-be-account-appeal.md) | `Identity-Service`, `api-docs` | `huynhtiennhat0403` | `baoduong17` | 3 points | — | 🔵 In review |
| P13-16 | [BE: Báo cáo vi phạm](P13-16-be-user-report.md) | `Identity-Service`, `api-docs` | `huynhtiennhat0403` | `baoduong17` | 2 points | P13-15 | 🔵 In review |
| P13-17 | [FE: Trang tài khoản bị khóa, khiếu nại](P13-17-fe-account-appeal.md) | `fe` | `ThaiBao11125` | PM/leader | 2 points | P13-15 | 🔵 In review |
| P13-18 | [FE: Gửi báo cáo, hàng chờ báo cáo](P13-18-fe-user-report.md) | `fe` | `ThaiBao11125` | PM/leader | 2 points | P13-16, P13-09 | 🔵 In review |
| P13-19 | [Mobile: Khiếu nại và báo cáo](P13-19-mobile-report-and-appeal.md) | `mobile` | Mobile (PM giao) | PM/leader | 3 points | P13-15, P13-16 | ⏸ Blocked (mobile chưa có nền tảng) |

Feedback cùng đợt đã có task, **không tạo mới**: tài khoản bị khóa bị 403 khi xem hóa đơn và `PATCH /me` vẫn lọt → **P12-09**; thiếu `messageKey` `invoice.issued` → **P12-03**; thiếu thông báo hủy hóa đơn → **P12-06**.

**Tổng:** 32 points (20 points ban đầu + 12 points của P13-15…19; P13-11 là issue tổng, không tính riêng). Owner là **đề xuất**, PM xác nhận khi giao.
