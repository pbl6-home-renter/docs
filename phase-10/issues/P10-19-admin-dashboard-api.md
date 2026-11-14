# P10-19 — API số liệu dashboard quản trị

**Loại:** Backend · **Trạng thái:** ⚪ Blocked — P10-10 chốt nguồn và contract  
**Owner đề xuất:** BE Lead / người được phân công · **Reviewer:** API owner / PM · **Repo:** service được P10-10 chỉ định, `api-docs`, `api-gateway` nếu cần  
**Phụ thuộc:** P10-10 · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## Mục tiêu và bối cảnh

Là admin, tôi muốn xem các chỉ số vận hành được phép để theo dõi hệ thống. `GET /dashboard` đang `designing`, không thấy controller trong ba service đã rà; schema còn `systemTransactionVolume` dù Payment deferred. P10-10 phải chốt metric, ownership, filter ngày, nguồn và cách xử lý service lỗi trước khi code.

## Các bước triển khai

1. Nhận decision từ P10-10, lập mapping từng metric tới nguồn và khoảng thời gian, quyền admin và endpoint thực tế. Sửa YAML/schema để loại hoặc biểu diễn đúng metric deferred. **Kiểm tra:** mỗi field đều có ví dụ dữ liệu nguồn và kết quả kỳ vọng; metric chưa có nguồn không có số giả.
2. Triển khai endpoint ở service owner được duyệt; tổng hợp theo kiến trúc database-per-service, không đọc DB riêng của service khác. Áp dụng validation `from/to`, role admin và quy tắc unavailable đã chốt. **Kiểm tra:** admin nhận số đúng; landlord/tenant bị từ chối; khoảng ngày sai trả error theo contract.
3. Test các tập rỗng, dữ liệu nhiều tenant/building, filter ngày và service nguồn lỗi; kiểm tra count không nhân bản do join. **Kiểm tra:** đối chiếu số với dữ liệu seed và truy vấn nguồn có cùng filter.
4. Cập nhật API docs/sequence diagram, Gateway nếu route sai, bundle; chạy build/lint/test service và kiểm thử qua Gateway.

## Acceptance

- Chỉ admin thấy các metric được phê duyệt, giá trị khớp nguồn và thời gian; error/partial data theo decision, không trả 0 để che lỗi.
- `systemTransactionVolume` và các trường chưa có nguồn không được mô phỏng; API tương thích với contract mới đã review.
- Có test authorization, filter ngày, zero-data và source unavailable cùng bằng chứng Gateway.
