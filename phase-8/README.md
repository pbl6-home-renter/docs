# Phase 8 — Kế hoạch triển khai

**Mục tiêu:** hoàn thiện các màn Web còn thiếu, nối context event qua RabbitMQ và bàn giao báo cáo cuối kỳ. Thời lượng dự kiến ba tuần từ kickoff; PM chốt lịch chi tiết khi giao việc.

## Quyết định và ranh giới

- Chỉ triển khai Web; Android ngoài phạm vi. Chat P7 đã hoàn tất.
- Giữ issue P5/P6/P7 đã tạo và GitHub ID hiện tại; không tạo lại cùng đầu việc dưới P8.
- P8-07/08 chưa có nội dung hoặc owner. PM sẽ mô tả flow và giao người sau.
- Issue backend đổi API phải cập nhật `api-docs` cùng implementation và cùng PR; không có issue OpenAPI độc lập.
- Không làm payment, settlement, overdue, reminder, reconciliation, QR hoặc tự tìm/liên kết tenant bằng số điện thoại.

## Issue P8 mới

| ID | Nội dung | Người phụ trách | Phụ thuộc |
|---|---|---|---|
| P8-01 | Baseline repo/API/DB/FE, đồng bộ trạng thái được PM xác nhận, sửa encoding tracker P6 | PM | — |
| P8-02 | FE: CRUD BillingSetting/RatePolicy, chọn policy cho tòa | `ThaiBao11125` | P6-02c/d |
| P8-03 | FE: hồ sơ cá nhân và media | `ThaiBao11125` | P4-05, P6-04 |
| P8-04 | FE: quản trị user qua Identity API hiện có | `ThaiBao11125` | P4-12 |
| P8-05 | FE tenant: xem invoice và mở notification deep link | `ThaiBao11125` | P6-02g4, P7-15 |
| P8-06 | Tenancy: context event qua transactional outbox | `leminhkhai345` | P8-01, P5-08b |
| P8-07 | Chờ PM viết flow Community | Chưa giao | Chưa chốt |
| P8-08 | Chờ PM viết flow notification invoice | Chưa giao | Chưa chốt |
| P8-09 | Smoke xuyên hệ thống và lưu bằng chứng | FE `ThaiBao11125`; BE `leminhkhai345`, `baoduong17` | P8-02–P8-06 và issue P5/P6 dùng lại; thêm P8-07/08 sau khi chốt flow |
| P8-10 | Báo cáo cuối kỳ theo mẫu, DOCX/PDF trên Google Drive | PM/người được giao viết | P8-09 |

Chi tiết xem [tracker và nội dung issue](issues/README.md). Mỗi PR tối đa 3 points và khoảng 15 file.

## Issue P5/P6/P7 dùng lại

| Phạm vi | Issue gốc được giữ |
|---|---|
| Building/Room backend | P5-08b/c/d, P5-09b/c |
| Contract/Member/checkout backend | P6-01e1/e3 |
| MeterReading đơn/lô, baseline và OCR | P6-02e/f/h |
| RatePolicy/BillingSetting API | P6-02c/d |
| Invoice generate/manage/tenant API | P6-02g2/g3/g4 |
| Màn Web Building/Room/Contract/MeterReading/Invoice | P6-03 đã Done; P6-06a/b/c/d là issue gốc cần tiếp tục theo trạng thái tracker |
| Community inbox/chat integration | P7-15/P7-18 đã Done; chỉ dùng lại API và evidence |

Các backend issue P5/P6 được giao lại cho `leminhkhai345` giữ nguyên ID GitHub. Trong issue gốc, bỏ dependency P6-09 đã dọn và đồng bộ API docs song song với implementation.
