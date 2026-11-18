# Phase 10 — Các issue đã hoàn thành code

Danh sách này chỉ gồm các issue đã hoàn thành code và merge. Các issue còn lại được giữ trong workspace để review và giao task; các kiểm thử tích hợp còn thiếu được ghi trong từng issue.

| ID | Issue | Repo | Owner đề xuất | Trạng thái |
|---|---|---|---|---|
| P10-01 | [Chặn xóa phòng có hợp đồng hiệu lực](P10-01-room-delete-active-contract.md) | Tenancy, api-docs | `leminhkhai345` | 🟢 Done — code đã merge |
| P10-02 | [Trả số liệu phòng thực tế cho tòa](P10-02-building-occupancy.md) | Tenancy, api-docs | `leminhkhai345` | 🟢 Done — code đã merge |
| P10-03 | [Hiển thị số liệu tòa đúng phạm vi trên Web](P10-03-web-building-metrics.md) | fe | `ThaiBao11125` | 🟢 Done — code đã merge |
| P10-04 | [Tìm tòa trên toàn bộ danh sách được phép xem](P10-04-building-search.md) | Tenancy, api-docs, fe | `leminhkhai345`, `ThaiBao11125` | 🟢 Done — code đã merge |
| P10-05 | [Hiển thị hợp đồng và chỉ số thật ở trang phòng](P10-05-room-detail-data.md) | fe | `ThaiBao11125` | 🟢 Done — code đã merge |
| P10-06 | [Áp mẫu và sinh hợp đồng nháp](P10-06-contract-template-regression.md) | Tenancy, api-docs, fe | `leminhkhai345` | 🟢 Done — code đã merge |
| P10-07 | [Tenant xem hợp đồng trên Web](P10-07-tenant-contracts-web.md) | fe | `ThaiBao11125` | 🟢 Done — code đã merge |
| P10-08 | [Sửa tổng quan chủ nhà](P10-08-landlord-dashboard-metrics.md) | fe | `ThaiBao11125` | 🟢 Done — code đã merge |
| P10-09 | [Đổi mật khẩu trên Web](P10-09-change-password-web.md) | fe | `ThaiBao11125` | 🟢 Done — code đã merge |

## Plan sửa Backend cho mobile — 18/11/2026

Người dùng đã duyệt triển khai theo P10-D90. Code local và kết quả kiểm tra được ghi tại [evidence](../discovery/mobile-backend-implementation.md), [plan](../../tasks/plan.md). Trạng thái dưới đây tách code local với review/deploy/nghiệm thu; không tự đóng backlog P9. Owner vẫn chỉ là đề xuất.

| ID | Issue | Repo | Owner đề xuất | Trạng thái |
|---|---|---|---|---|
| P10-31 | [Link đại diện hợp đồng theo SĐT ở create/activate](P10-31-contract-representative-phone-link.md) | Tenancy | BE Contract | 🔵 Code local + unit/SQL pass — chờ review/deploy và concurrency staging |
| P10-32 | [Đã bỏ công cụ reconcile/bootstrap](P10-32-tenant-link-reconciliation.md) | — | — | ⏪ Bỏ theo yêu cầu người dùng — P10-D91 |
| P10-33 | [Địa chỉ và tên tòa trong response phòng](P10-33-room-address-response.md) | Tenancy, api-docs | BE Room / API owner | 🔵 Code/spec local đã kiểm tra — chờ deploy/mobile |
| P10-34 | [Adapter contact chủ trọ](P10-34-landlord-contact-lookup.md) | Tenancy | BE Room | 🔵 Code local đã kiểm tra — chờ review/deploy |
| P10-35 | [Điền landlord vào chi tiết phòng](P10-35-room-landlord-response.md) | Tenancy, api-docs | BE Room | 🔵 Code/spec local đã kiểm tra — chờ deploy/mobile |
| P10-36 | [Contract ảnh phòng và smoke ảnh thật](P10-36-room-photo-contract-and-smoke.md) | api-docs, Media | API / Media owner | 🔵 Spec/URL filtering xong — còn smoke upload ảnh thật |
| P10-24 | [Yêu thích phòng — dùng lại backlog hiện có](P10-24-favorite-rooms.md) | Tenancy, api-docs, mobile/fe | BE / API / client owner | 🔵 BE/API được duyệt, code + SQL pass — cần migration/deploy/client |
| P10-37 | [Nghiệm thu Backend trên mobile tenant](P10-37-mobile-backend-contract-verification.md) | mobile, api-docs, pm | Mobile / BE / API owner | ⚪ Backend tests pass — chờ source/build mobile và deploy |
