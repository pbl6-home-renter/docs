# P10-25 — API hồ sơ tìm bạn ở ghép

**Loại:** Backend · **Trạng thái:** ⏪ Deferred — matching là Stretch theo P1-D28  
**Owner đề xuất:** BE Lead / người được giao · **Reviewer:** PM / API owner · **Repo:** service owner sau khi chốt, `api-docs`  
**Phụ thuộc:** P10-11, P1-13 · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## User story và phạm vi

Tenant có tài khoản muốn tạo/cập nhật hồ sơ tìm bạn và xem các hồ sơ phù hợp với quy tắc hiển thị được chấp thuận. OpenAPI designing có `GET /roommate-profiles`, `GET /roommate-profiles/{id}`, `GET/PUT /me/roommate-profile`; chưa thấy module tương ứng trong các service đã rà. P1-D28 và D29 yêu cầu coi matching là Stretch, chỉ dành cho người dùng tham gia.

## Triển khai sau khi được duyệt

1. Đọc P1-13 và API schemas, chốt opt-in, quyền xem, ẩn hồ sơ, field nhạy cảm, lọc/pagination và user bị khóa; xác định service/DB owner. **Kiểm tra:** bảng field, actor và ví dụ public/private được PM/API owner duyệt.
2. Đồng bộ contract và persistence/migration theo quy trình service; implementation GET/PUT của chính user cùng list/detail theo điều kiện đã duyệt. **Kiểm tra:** user không sửa được profile người khác, profile chưa opt-in không xuất hiện ngoài phạm vi.
3. Test tạo/sửa/không tìm thấy, lọc/pagination, ownership, dữ liệu nhạy cảm và retry; chạy build/lint/test, API docs lint/bundle và Gateway smoke.

## Acceptance

- Tenant quản lý profile của chính mình và xem hồ sơ theo quyền/opt-in đã chốt; không dùng tên, ảnh hoặc dữ liệu liên hệ giả.
- API error, pagination và privacy khớp contract; không triển khai AI scoring hoặc match request trong issue này.
- Issue chỉ được chuyển sang implementation khi PM xác nhận Stretch vào phạm vi; chưa có decision thì giữ deferred.
