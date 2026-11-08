# Tracker issue Phase 8

Copy các file issue P8-01–P8-06 và P8-09–P8-10 lên GitHub khi PM tạo issue; sau đó thay `docs#TBD` bằng số issue được cấp. P8-07/08 được giữ làm mã chờ flow PM, hiện không có file issue, owner hoặc assignee.

## Issue Phase 8 mới

| ID | Issue | Người phụ trách | Ước lượng | Trạng thái | Phụ thuộc |
|---|---|---|---:|---|---|
| P8-01 | [Chốt baseline Phase 8 và đồng bộ tracker](P8-01-baseline-va-tracker.md) | PM | 2 points · 6 giờ | 🟡 Open | — |
| P8-02 | [FE: BillingSetting/RatePolicy](P8-02-billing-policy-ui.md) | `ThaiBao11125` | 3 points · 12 giờ | 🟡 Open | P6-02c/d |
| P8-03 | [FE: hồ sơ cá nhân và media](P8-03-profile-media-ui.md) | `ThaiBao11125` | 2 points · 8 giờ | 🟡 Open | P4-05, P6-04 |
| P8-04 | [FE: quản trị người dùng](P8-04-admin-user-ui.md) | `ThaiBao11125` | 3 points · 12 giờ | 🟡 Open | P4-12 |
| P8-05 | [FE tenant: invoice và notification deep link](P8-05-tenant-invoice-ui.md) | `ThaiBao11125` | 2 points · 8 giờ | 🟡 Open | P6-02g4, P7-15 |
| P8-06 | [Tenancy: context event qua outbox](P8-06-tenancy-context-outbox.md) | `leminhkhai345` | 3 points · 12 giờ | 🟡 Open | P8-01, P5-08b |
| P8-07 | **Chờ PM viết flow Community** | Chưa giao | — | Chưa tạo issue | — |
| P8-08 | **Chờ PM viết flow notification invoice** | Chưa giao | — | Chưa tạo issue | — |
| P8-09 | [Kiểm chứng smoke xuyên hệ thống](P8-09-e2e-smoke.md) | FE `ThaiBao11125`; BE `leminhkhai345`, `baoduong17` | 3 points · 12 giờ | 🟡 Open | P8-02–P8-06 và issue carry-over; thêm P8-07/08 sau khi chốt flow |
| P8-10 | [Báo cáo cuối kỳ DOCX/PDF](P8-10-final-report-package.md) | PM/người được giao viết | 3 points · 12 giờ | 🟡 Open | P8-09 |

## Dùng lại issue P5/P6/P7 đã có

Các issue sau giữ nguyên ID/GitHub ID; không tạo lại dưới Phase 8:

| Công việc | Issue gốc |
|---|---|
| Building/Room backend | P5-08b/c/d, P5-09b/c |
| Contract/Member/checkout backend | P6-01e1/e3 |
| MeterReading đơn/lô, baseline/OCR | P6-02e/f/h |
| RatePolicy/BillingSetting backend API | P6-02c/d |
| Invoice generate/manage/tenant API | P6-02g2/g3/g4 |
| Màn landlord Contract/Member/MeterReading/Invoice | P6-06a/b/c/d theo trạng thái hiện có trong tracker P6 |
| Community inbox và kiểm chứng chat Web | P7-15, P7-18 (Done; chỉ tái sử dụng API/evidence) |

Backend issue được giao lại cho `leminhkhai345` giữ GitHub ID gốc. Mỗi PR tối đa 3 points và khoảng 15 file; tách PR trong cùng issue nếu vượt giới hạn.
