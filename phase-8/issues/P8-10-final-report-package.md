# P8-10 — Viết báo cáo cuối kỳ theo mẫu và bàn giao DOCX/PDF

**Epic:** Phase 8  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** PM/người được PM giao viết  
**Người review:** PM  
**Ước lượng:** 3 points · 12 giờ (**tối đa 3 points và khoảng 15 file mỗi PR**)  
**Phụ thuộc:** P8-09 và bằng chứng các issue trước  
**Repo / branch:** `pm/` · `docs/p8-10-final-report`  
**Issue:** `docs#TBD`

> **Phạm vi người viết:** thành viên được giao viết báo cáo theo mẫu. Assistant chỉ chuẩn bị issue và không viết báo cáo thay thành viên.

## Mục tiêu

Hoàn thiện báo cáo cuối kỳ theo `MauBaoCao_PBL6_Final.doc`, giữ cấu trúc và yêu cầu của mẫu, bàn giao bản DOCX và PDF trên Google Drive team folder.

## Quyết định áp dụng

- Mẫu gốc là nguồn chuẩn cho thứ tự chương, heading, layout và mục bắt buộc; không ghi đè file mẫu.
- Nội dung chỉ dựa trên implementation, issue/PR, sơ đồ và smoke evidence đã được owner xác nhận.
- Ghi rõ chức năng chưa hoàn thành, giới hạn và N/A có lý do; không tự tạo số liệu, ảnh hoặc kết quả kiểm thử.
- Giữ P8-07/08 chưa mô tả cho tới khi PM cung cấp flow; báo cáo không được trình bày các flow này như đã triển khai.

## Contract đầu vào và mapping bằng chứng

| Nội dung báo cáo | Nguồn kiểm chứng | Quy tắc |
|---|---|---|
| Chức năng/kiến trúc | repo, issue gốc P5/P6/P7, PR đã merge | phân biệt thiết kế với phần chạy thật |
| API/DB | OpenAPI, migration, sơ đồ DB được duyệt | khớp implementation hiện tại |
| RabbitMQ/context/notification | P8-06, P8-07/08 nếu được chốt, event evidence | chỉ ghi đúng producer/consumer và retry đã kiểm chứng |
| Kết quả smoke | P8-09 evidence | giữ run ID, role và giới hạn; không suy rộng từ một case |
| Hình/bảng | screenshot/sơ đồ có nguồn | che secrets/PII, có caption và tham chiếu |

## Tham chiếu tài liệu

- Mẫu: `MauBaoCao_PBL6_Final.doc` ở workspace root.
- Source evidence: issue files và PR liên quan trong `pm/phase-8/issues/`, tracker P5/P6/P7, thư mục/Drive evidence của team.

## Các bước triển khai

### Bước 1 — Phân tích mẫu

- **Cách làm:** mở mẫu gốc, lập checklist heading, bảng/hình, phụ lục, tài liệu tham khảo và yêu cầu định dạng.
- **Kiểm tra bước:** checklist phủ toàn bộ mục bắt buộc theo đúng thứ tự mẫu.

### Bước 2 — Thu thập evidence

- **Cách làm:** xin owner xác nhận từng phần; lưu link PR, API/DB/diagram, screenshots và P8-09 smoke report.
- **Kiểm tra bước:** mỗi claim trong outline có source và owner; nội dung chưa có source được gắn TBD thay vì tự suy ra.

### Bước 3 — Viết và review

- **Cách làm:** điền nội dung theo mẫu; thống nhất tên service/thuật ngữ; kiểm tra số liệu, caption, mục lục và references.
- **Kiểm tra bước:** PM/owner rà tính đúng đắn; mọi nội dung chưa hoàn thành được mô tả trung thực.

### Bước 4 — Xuất và bàn giao

- **Cách làm:** lưu DOCX mới, xuất PDF, mở kiểm tra từng trang, tải cả hai lên Drive và cấp quyền team.
- **Kiểm tra bước:** DOCX mở được, PDF không vỡ trang, Drive link truy cập được bằng account thành viên.

## Ngoài phạm vi

- Viết nội dung chưa được owner xác nhận; tạo kết quả test hoặc hình minh họa giả.
- Thay đổi mẫu gốc hoặc nộp báo cáo thay người được giao.

## Blocker

- Thiếu template/evidence/owner response thì ghi mục còn thiếu, người cần cung cấp và ngày cần; không tự hoàn thiện bằng dữ liệu phỏng đoán.

## Acceptance

- [ ] Mọi mục bắt buộc trong mẫu được điền hoặc ghi N/A có lý do.
- [ ] Claim kỹ thuật và số liệu truy được tới source/evidence đã xác nhận.
- [ ] P8-07/08 chỉ được mô tả nếu PM đã cung cấp flow và implementation có bằng chứng.
- [ ] DOCX/PDF mở được, hình/bảng đọc rõ, không lộ secrets/PII; Drive link hoạt động.

## Definition of Done

- [ ] PM duyệt nội dung và hình thức; checklist mục mẫu hoàn tất.
- [ ] DOCX và PDF nằm trên Drive team folder; issue có link, tên file, người review và ngày bàn giao.
- [ ] Không ghi đè mẫu gốc; báo cáo không tuyên bố hoàn tất phần chưa có evidence.
