# P10-20 — API đọc nhật ký quản trị

**Loại:** Backend · **Trạng thái:** ⚪ Blocked — P10-10 chốt nguồn log và quyền  
**Owner đề xuất:** BE Lead / người được phân công · **Reviewer:** API owner / PM · **Repo:** service được P10-10 chỉ định, `api-docs`, `api-gateway` nếu cần  
**Phụ thuộc:** P10-10 · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## Bối cảnh và mục tiêu

Admin user flow có audit log cho một số thao tác; `GET /audit-logs` và `GET /audit-logs/{id}` trong OpenAPI đang designing, chưa thấy controller. Chưa xác nhận runtime audit store, event nào bắt buộc, retention và dữ liệu nhạy cảm được phép lưu. P10-10 phải chốt các điểm này và chỉ định service owner trước khi triển khai.

## Triển khai

1. Kiểm tra log/producer hiện có, định nghĩa nguồn và fields, quyền admin, filter/timezone, retention và redaction theo decision. Đối chiếu filter `actorUserId`, `entityType`, `from/to` và pagination trong YAML. **Kiểm tra:** mỗi ví dụ có nguồn thật và không chứa credential/token/PII ngoài scope.
2. Triển khai read API list/detail theo schema đã duyệt và ownership của service; nếu chưa có producer hay persistence, tách công việc đó thành issue phụ được review, không coi log ứng dụng là audit store. **Kiểm tra:** record do fixture/producer hợp lệ được trả đúng; ID không có trả lỗi theo contract.
3. Giữ audit record chỉ đọc và pagination ổn định; triển khai định dạng export chỉ khi P10-10 duyệt và contract được cập nhật. **Kiểm tra:** filter actor/entity/date và page không lặp/thiếu; user thường bị từ chối cả list/detail.
4. Test authorization, filter, trang rỗng, ID không tồn tại và redaction; build/lint/test, đồng bộ OpenAPI/bundle và xác minh qua Gateway.

## Acceptance

- Admin đọc được dữ liệu audit từ nguồn đã chốt, user không có quyền bị chặn; không phát lộ mật khẩu/token hoặc trường bị cấm.
- List/detail, filter/pagination, error và định dạng hỗ trợ khớp contract đã duyệt; không tạo audit log giả để làm UI.
- Có evidence test, ví dụ response đã ẩn dữ liệu nhạy cảm và liên kết tới producer/store đã được chốt.
