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

Các mục dưới là task mới chuẩn bị từ kiểm tra code và API công khai, chưa phải code đã hoàn thành. Xem [kết quả audit và plan](../../tasks/plan.md). Không thay đổi trạng thái các issue đã merge hoặc tự đóng backlog P9; owner dưới đây chỉ là đề xuất.

| ID | Issue | Repo | Owner đề xuất | Trạng thái |
|---|---|---|---|---|
| P10-31 | [Link đại diện hợp đồng theo SĐT ở create/activate](P10-31-contract-representative-phone-link.md) | Tenancy | BE Contract | 🟡 Open — P0 |
| P10-32 | [Projection và reconcile hợp đồng cũ](P10-32-tenant-link-reconciliation.md) | Tenancy, Identity nếu cần | BE Contract / Identity | 🟡 Open — P0 |
| P10-33 | [Địa chỉ và tên tòa trong response phòng](P10-33-room-address-response.md) | Tenancy, api-docs | BE Room / API owner | 🟡 Open — P0 |
| P10-34 | [Adapter contact chủ trọ](P10-34-landlord-contact-lookup.md) | Tenancy | BE Room | 🟡 Open — P0 |
| P10-35 | [Điền landlord vào chi tiết phòng](P10-35-room-landlord-response.md) | Tenancy, api-docs nếu cần | BE Room | 🟡 Open — P0 |
| P10-36 | [Contract ảnh phòng và smoke ảnh thật](P10-36-room-photo-contract-and-smoke.md) | api-docs, Media nếu cần | API / Media owner | 🟡 Open — P1 |
| P10-24 | [Yêu thích phòng — dùng lại backlog hiện có](P10-24-favorite-rooms.md) | Tenancy, api-docs, mobile/fe | BE / API / client owner | ⏪ Deferred implementation; đã bổ sung plan kiểm tra |
| P10-37 | [Nghiệm thu Backend trên mobile tenant](P10-37-mobile-backend-contract-verification.md) | mobile, api-docs, pm | Mobile / BE / API owner | 🟡 Open — cần source/build mobile đúng để nghiệm thu |
