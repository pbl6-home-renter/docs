# Phase 11 — Tracker

Bảng này là nguồn trạng thái chính thức; cập nhật cùng lúc với file issue.

| ID | Issue | Repo | Owner đề xuất | Ước lượng | Phụ thuộc | Trạng thái |
|---|---|---|---|---|---|---|
| P11-01 | [Cập nhật contract dashboard, users/stats và audit-logs](P11-01-admin-contract.md) | api-docs | `baoduong17` (API owner) | 2 pts | — | 🟡 Open |
| P11-02 | [Identity: thống kê người dùng `GET /users/stats`](P11-02-identity-user-stats.md) | Identity-Service | `huynhtiennhat0403` | 1 pt | P11-01 | 🟡 Open |
| P11-03 | [Tenancy: thống kê tòa và phòng `GET /dashboard`](P11-03-tenancy-dashboard.md) | Tenancy-Service | `leminhkhai345` | 2 pts | P11-01 | 🟡 Open |
| P11-10 | [Boilerplate: decorator `@Audited` và port `AuditRecorder` generic](P11-10-shared-audit-decorator.md) | boilerplate → Identity, Tenancy, community | `huynhtiennhat0403` | 2 pts | — | 🟡 Open |
| P11-04 | [Identity: bảng audit log và ghi thao tác admin trên user](P11-04-identity-audit-user-actions.md) | Identity-Service | `huynhtiennhat0403` | 3 pts | P11-01, P11-10 | 🟡 Open |
| P11-05 | [Identity: ghi audit khi admin duyệt/từ chối tòa](P11-05-identity-audit-building-review.md) | Identity-Service | `huynhtiennhat0403` | 2 pts | P11-04, P11-10 | 🟡 Open |
| P11-06 | [Identity: API đọc audit log](P11-06-identity-audit-read-api.md) | Identity-Service | `baoduong17` | 2 pts | P11-04 | 🟡 Open |
| P11-07 | [Web: màn Admin dashboard](P11-07-web-admin-dashboard.md) | fe | `ThaiBao11125` | 2 pts | P11-01; nối API sau P11-02, P11-03 | 🟡 Open |
| P11-08 | [Web: màn Audit logs](P11-08-web-audit-logs.md) | fe | `ThaiBao11125` | 2 pts | P11-01; nối API sau P11-06 | 🟡 Open |
| P11-09 | [Spike: so sánh dịch vụ VietQR có sandbox](P11-09-vietqr-sandbox-spike.md) | pm (tài liệu), PoC branch tùy chọn | `leminhkhai345` | 3 pts | — | 🟡 Open |

## Web — các màn còn thiếu (API đã có)

| ID | Issue | Repo | Owner đề xuất | Ước lượng | Phụ thuộc | Trạng thái |
|---|---|---|---|---|---|---|
| P11-11 | [Màn Quản lý khách thuê cho chủ trọ](P11-11-web-landlord-tenants.md) | fe | `ThaiBao11125` | 3 pts | P10-16 (đã merge) | 🟡 Open |
| P11-12 | [Lưu phòng yêu thích cho người thuê](P11-12-web-favorite-rooms.md) | fe | `ThaiBao11125` | 2 pts | P10-24 BE (đã merge, cần deploy) | 🟡 Open |
| P11-13 | [Chủ trọ chọn khôi phục/chấm dứt hợp đồng sau khi được mở khóa](P11-13-web-contract-lock-decision.md) | fe | `ThaiBao11125` | 2 pts | P9-06/07 (đã merge) | 🟡 Open |
| P11-14 | [Màn "Phòng của tôi" dùng API room-hub](P11-14-web-tenant-room-hub.md) (ưu tiên thấp) | fe | `ThaiBao11125` | 1 pt | API owner đổi status `/me/room-hub` | 🟡 Open |

**Tổng:** 29 points (FE: 12 points cho `ThaiBao11125` — nên cân nhắc chia bớt cho người khác). P11-10 nằm cạnh P11-04 trong bảng vì là bước nền của audit log; ID giữ nguyên, không đánh số lại.

**Chưa tạo task (chờ quyết định hoặc phụ thuộc):** chọn tài khoản tenant khi tạo hợp đồng (P10-23, chờ PM chốt rule); nút "Sinh mô tả bằng AI" (chờ có AI service); ghi nhận thanh toán / biểu đồ doanh thu (chờ kết quả spike P11-09 và quyết định mở lại P6-05).
