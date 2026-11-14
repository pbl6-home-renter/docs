# Tracker issue Phase 10

Issue dưới đây là file Markdown nội bộ; `docs#TBD` chưa phải GitHub issue. Owner chỉ là đề xuất, estimate chưa chốt. Giữ các issue P5–P9 và ID gốc cho công việc đã được giao; xem [audit](../discovery/audit.md).

| ID | Issue | Repo | Owner đề xuất | Trạng thái | Phụ thuộc |
|---|---|---|---|---|---|
| P10-01 | [Chặn xóa phòng có hợp đồng hiệu lực](P10-01-room-delete-active-contract.md) | Tenancy, api-docs | `leminhkhai345` | 🔵 In progress — đã merge, chờ nghiệm thu | P5-09c, P6-01d |
| P10-02 | [Trả số liệu phòng thực tế cho tòa](P10-02-building-occupancy.md) | Tenancy, api-docs | `leminhkhai345` | 🔵 In progress — đã merge, chờ nghiệm thu | P5-08c/d, P5-09b |
| P10-03 | [Hiển thị số liệu tòa đúng phạm vi trên Web](P10-03-web-building-metrics.md) | fe | `ThaiBao11125` | 🔵 In progress — còn thẻ số liệu theo trang | P10-02 |
| P10-04 | [Tìm tòa trên toàn bộ danh sách](P10-04-building-search.md) | Tenancy, api-docs, fe | BE `leminhkhai345`; FE `ThaiBao11125` | 🔵 In progress — còn frontend search | P5-08c, P6-03a |
| P10-05 | [Hiển thị hợp đồng và chỉ số thật ở trang phòng](P10-05-room-detail-data.md) | fe | `ThaiBao11125` | 🔵 In progress — thiếu bảo đảm kỳ mới nhất | P6-01e1, P6-02e; xác minh contract |
| P10-06 | [Khôi phục áp mẫu và sinh hợp đồng nháp](P10-06-contract-template-regression.md) | Tenancy, api-docs, fe | `leminhkhai345` | 🔵 In progress — đã merge, chờ nghiệm thu | P6-01c, P6-04 |
| P10-07 | [Tenant xem hợp đồng trên Web](P10-07-tenant-contracts-web.md) | fe | `ThaiBao11125` | 🔵 In progress — đã merge, chờ nghiệm thu | P6-01e2, Gateway |
| P10-08 | [Sửa tổng quan chủ nhà](P10-08-landlord-dashboard-metrics.md) | fe | `ThaiBao11125` | 🔵 In progress — đã merge, chờ nghiệm thu | P5-08c |
| P10-09 | [Đổi mật khẩu trên Web](P10-09-change-password-web.md) | fe | `ThaiBao11125` | 🔵 In progress — đã merge, chờ nghiệm thu | Identity `PUT /me/password` |
| P10-10 | [Chốt dashboard và nhật ký quản trị](P10-10-admin-dashboard-audit.md) | PM, API, BE, fe | PM / BE Lead | ⚪ Blocked | Quyết định PM/API owner |
| P10-11 | [Phân loại API chưa triển khai và chốt scope](P10-11-unimplemented-api-scope-review.md) | PM, api-docs | PM / API owner | ⚪ Blocked | Quyết định PM |
| P10-12 | [API bot reminder thủ công](P10-12-bot-reminder-api.md) | community, api-docs | `baoduong17` | ⚪ Blocked | CB-15, template contract |
| P10-13 | [Web gửi bot reminder](P10-13-bot-reminder-web.md) | fe | `ThaiBao11125` | ⚪ Blocked | P10-12 |
| P10-14 | [API phòng của tenant](P10-14-tenant-room-hub-api.md) | Tenancy, api-docs | `leminhkhai345` | ⚪ Blocked | P10-11, P6-01e1/e2 |
| P10-15 | [Web phòng và dashboard tenant](P10-15-tenant-room-web.md) | fe | `ThaiBao11125` | 🔵 In progress — thiếu trạng thái thanh toán | P10-07; trạng thái thanh toán cho hóa đơn chưa thanh toán |
| P10-16 | [API danh sách và chi tiết khách thuê](P10-16-landlord-tenants-api.md) | Tenancy, api-docs | `leminhkhai345` | ⚪ Blocked | P6-01e1, P9-01/02, privacy |
| P10-17 | [Web quản lý khách thuê](P10-17-landlord-tenants-web.md) | fe | `ThaiBao11125` | ⚪ Blocked | P10-16 |
| P10-18 | [Kiểm chứng Chat v2 và attachment](P10-18-chat-v2-integration.md) | fe, Community, Identity, Gateway | FE + Community owner | 🟡 Open | P7-D83, PR liên quan |
| P10-19 | [API dashboard quản trị](P10-19-admin-dashboard-api.md) | BE owner, api-docs | BE Lead | ⚪ Blocked | P10-10 |
| P10-20 | [API nhật ký quản trị](P10-20-admin-audit-api.md) | BE owner, api-docs | BE Lead | ⚪ Blocked | P10-10 |
| P10-21 | [Web dashboard quản trị](P10-21-admin-dashboard-web.md) | fe | `ThaiBao11125` | ⚪ Blocked | P10-19 |
| P10-22 | [Web nhật ký quản trị](P10-22-admin-audit-web.md) | fe | `ThaiBao11125` | ⚪ Blocked | P10-20 |
| P10-23 | [Chọn tenant khi tạo hợp đồng/thành viên](P10-23-contract-tenant-selection.md) | fe, api-docs | `ThaiBao11125` | ⚪ Blocked | PM chốt D74/P9 và directory |
| P10-24 | [Phòng yêu thích: API và Web](P10-24-favorite-rooms.md) | BE owner, fe, api-docs | BE / `ThaiBao11125` | ⏪ Deferred | P10-11, P5-09d |
| P10-25 | [API hồ sơ tìm bạn ở ghép](P10-25-roommate-profile-api.md) | BE owner, api-docs | BE Lead | ⏪ Deferred | P10-11, P1-13 |
| P10-26 | [API yêu cầu tìm bạn ở ghép](P10-26-match-requests-api.md) | BE owner, api-docs | BE Lead | ⏪ Deferred | P10-25 |
| P10-27 | [Web tìm bạn ở ghép](P10-27-roommate-web.md) | fe | `ThaiBao11125` | ⏪ Deferred | P10-25/26 |
| P10-28 | [API báo sự cố](P10-28-issue-report-api.md) | BE owner, api-docs | BE Lead | ⏪ Deferred | P10-11, decision IssueReport |
| P10-29 | [Web báo và quản lý sự cố](P10-29-issue-report-web.md) | fe | `ThaiBao11125` | ⏪ Deferred | P10-28 |
| P10-30 | [Đối chiếu cấu hình VietQR](P10-30-vietqr-config.md) | PM, API, Identity, Tenancy, fe | PM / service owners | ⏪ Deferred | P10-11, P6-D61/D72 |

Checkpoint: sau API liên quan kiểm tra contract, ownership và concurrency; sau FE kiểm tra Gateway với dữ liệu thật và nhiều role. P10-10/11 chốt phạm vi cho các issue phụ thuộc; P6-02g4/P8-05 và P9-05–09 giữ ID gốc. Không đánh dấu Done chỉ dựa trên file source hoặc build.
