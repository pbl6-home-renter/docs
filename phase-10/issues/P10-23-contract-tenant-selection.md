# P10-23 — Chốt và hoàn thiện chọn tenant khi tạo hợp đồng/thành viên

**Loại:** FE / contract alignment · **Trạng thái:** ⚪ Blocked — PM chốt xung đột rule  
**Owner đề xuất:** `ThaiBao11125` · **Reviewer:** PM / Identity owner · **Repo:** `fe`, `api-docs` nếu contract đổi  
**Phụ thuộc:** P9-01/02, P6-D74, P9-D83/D84 · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## Bối cảnh

Form tạo contract và thêm member hiện nhập tay tên/SĐT. `fe/AGENTS.md` yêu cầu cả chọn account qua directory và nhập tay, trong khi P6-D74 từng loại chọn account khỏi Phase 6; P9-D83/D84 đã thay đổi việc liên kết qua số điện thoại. Chưa có decision rõ ràng trong phần đã rà về việc Phase 10 bổ sung picker. Theo P6-D75, dev không tự chọn rule từ hai nguồn mâu thuẫn.

## Các bước triển khai

1. PM/API owner đối chiếu D74, P9-D83/D84, quyền `/users/directory` và DTO contract/member; ghi decision mới nhất: có/không picker, trường được hiển thị, role được tìm và cách xử lý tenant chưa đăng ký. **Kiểm tra:** có ví dụ tenant có account, chưa có account và account sai role/quyền.
2. Nếu picker được duyệt, dùng directory API có quyền và pagination thực, thêm hai chế độ chọn/tự nhập; chọn account điền thông tin theo DTO được phép, không khóa luồng nhập tay. **Kiểm tra:** chọn user và nhập tay tạo payload đúng, không gửi tenantId của user khác ngoài lựa chọn.
3. Xử lý tìm kiếm rỗng/lỗi, hủy lựa chọn, thay đổi phone và liên kết lại theo quyết định; bảo vệ dữ liệu directory ở backend. **Kiểm tra:** lỗi directory không làm mất khả năng nhập tay, user không có quyền không thấy dữ liệu riêng.
4. Chạy FE build/lint/i18n, kiểm tra hai form, cross-user, offline và mobile; nếu contract thiếu field hoặc quyền, liên kết issue backend thay vì gửi field tự đặt.

## Acceptance

- Có decision giải quyết mâu thuẫn; khi được duyệt, hai luồng chọn account và nhập tay hoạt động với cả tạo contract và thêm member.
- Landlord vẫn tạo được dữ liệu tenant không login theo P0-D29; không lộ directory hoặc liên kết user ngoài quyền.
- Bằng chứng gồm payload đã ẩn thông tin nhạy cảm, test thành công/lỗi và kết quả kiểm tra FE.
