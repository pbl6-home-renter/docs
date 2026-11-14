# Phase 10 — Hoàn thiện tính đúng đắn của dữ liệu vận hành

Mục tiêu: xử lý các khoảng trống đã xác minh trong quản lý phòng, số liệu tòa, hợp đồng và tài khoản Web; đồng thời phân loại các API chưa có đủ bằng chứng triển khai. Xem [báo cáo rà soát](discovery/audit.md) và [kiểm kê operation](discovery/api-inventory.md); không thay thế backlog Phase 5–9.

Thứ tự: P10-01 độc lập; P10-02 trước P10-03; backend P10-04 đã merge, FE search còn lại; P10-05/07 phụ thuộc API hiện có; P10-06 cần kiểm tra hợp đồng nháp end-to-end; P10-08/09 đã merge và chờ nghiệm thu; P10-10/11 chờ quyết định. Xem [tracker](issues/README.md). Các owner là đề xuất theo tracker trước, chưa phải phân công đã xác nhận. Mỗi PR tối đa 3 points và khoảng 15 file; tách PR nếu cần. PM review trước merge; lịch và ước lượng chờ xác nhận.

Các task bổ sung: P10-12 → P10-13 (reminder), P10-15 lite theo D7 dùng hợp đồng tenant thay cho P10-14, P10-16 → P10-17 (khách thuê), P10-10 → P10-19/20 → P10-21/22 (admin); P10-18 kiểm chứng Chat v2 và P10-23 chờ chốt rule chọn tenant. P10-28/29 được đưa vào phạm vi theo P10-D86; favorite, Matching và VietQR tiếp tục chờ xác nhận hoặc deferred. Payment/settlement tiếp tục theo P6-05 và decision hiện hành.

Giữ Payment, settlement, OCR và các scope khác đã deferred ngoài phase; không tạo lại P8/P9. IssueReport theo P10-D86. Thay đổi API phải cập nhật `api-docs` và bundle theo quy ước repo. Kiểm chứng sau các PR liên quan bằng API và giao diện với dữ liệu nhiều tòa/phòng; theo dõi lỗi và quyền truy cập trên môi trường thử nghiệm.
