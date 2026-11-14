# P10-30 — Đối chiếu cấu hình VietQR và thông tin nhận tiền

**Loại:** Contract / Backend / FE · **Trạng thái:** ⏪ Deferred — chờ PM chốt scope  
**Owner đề xuất:** PM / Identity & Tenancy owners · **Reviewer:** API owner · **Repo:** `api-docs`, service liên quan, `fe`  
**Phụ thuộc:** P10-11, P6-D61/D72 · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## Bối cảnh và ranh giới

OpenAPI có `PUT /buildings/{buildingId}/vietqr-config` trạng thái designing; chưa thấy controller tương ứng. Trong khi đó Identity profile có payout account, P6-D61 hoãn Payment/settlement và P6-D72 bỏ VietQR khỏi invoice response. Không được mặc định thiết kế thêm cấu hình QR cấp tòa hoặc thanh toán chỉ vì YAML còn tồn tại.

## Các bước triển khai sau quyết định

1. PM/API owner đối chiếu Identity payout account, flow tòa nhà, P6-D61/D72 và YAML; quyết định giữ, sửa hay retire operation, ownership và field nào được dùng. **Kiểm tra:** có decision và matrix nguồn dữ liệu; không có hai nguồn cấu hình mâu thuẫn.
2. Nếu được duyệt triển khai, tách backend contract/authorization/persistence và FE form thành PR hoặc issue con; xác định quyền owner, validation, lỗi và cách ẩn dữ liệu tài khoản. **Kiểm tra:** landlord khác không đọc/sửa được, thông tin lưu và hiển thị theo contract.
3. Nếu operation không còn thuộc scope, cập nhật contract/status và các điểm UI phụ thuộc theo quyết định; không tự thay đổi trạng thái API trước review. **Kiểm tra:** UI không gợi ý cấu hình không có thật và client migration được ghi rõ.
4. Kiểm thử API/FE theo quyết định: permission, lỗi, reload, redaction, build/lint/i18n; không thêm payment processing hoặc reconciliation ngoài scope.

## Acceptance

- Có quyết định rõ API tồn tại hay retire, nguồn dữ liệu và quyền; công việc implementation chỉ bắt đầu sau khi decision được duyệt.
- Không công bố QR/thu tiền giả hoặc rò thông tin tài khoản; mọi cập nhật contract và FE có bằng chứng kiểm tra.
