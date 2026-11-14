# P10-16 — Dữ liệu danh sách và chi tiết khách thuê cho chủ nhà

**Loại:** Backend / contract · **Trạng thái:** ⚪ Blocked — chốt định nghĩa khách thuê và privacy  
**Owner đề xuất:** `leminhkhai345` · **Reviewer:** API owner / PM · **Repo:** `Tenancy-Service`, `api-docs`  
**Phụ thuộc:** P6-01e1, P9-01/02 · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## Bối cảnh

FE có menu `/tenants` và `/tenants/:id` nhưng chỉ render placeholder; contract member và contract đã lưu thông tin tenant, kể cả tenant không có tài khoản. Chưa xác minh có API tổng hợp landlord hiện hành phù hợp. `GET /users/directory` là directory hệ thống, không phải danh sách khách thuê riêng của một landlord.

## Quyết định cần chốt

PM/API owner xác định nguồn dữ liệu và định danh khi một người có nhiều contract hoặc không có `tenantId`, dữ liệu lịch sử so với đang ở, filter/pagination, trường liên hệ và quyền landlord. Phải giữ P0-D29: landlord vận hành được với tenant không login. Không tự dùng phone làm khóa định danh xuyên hệ thống hoặc lộ profile Identity toàn cục.

## Triển khai

1. Đối chiếu contract/member APIs hiện có và luồng landlord; chứng minh có thể tái sử dụng hay cần API mới. Ghi ví dụ hai contract cùng người, tenant NULL và đã rời; API owner cập nhật contract sau khi quyết định. **Kiểm tra:** mỗi trường trong response có nguồn và quyền rõ ràng.
2. Nếu API hiện có không đủ, bổ sung query và endpoint đã duyệt; filter landlord theo ownership ở backend, hỗ trợ phân trang và truy cập chi tiết theo định danh được chốt. **Kiểm tra:** A chỉ thấy dữ liệu thuộc A; B không truy cập được chi tiết của A; tenant chưa có account vẫn được biểu diễn.
3. Xử lý contract/member đã rời hoặc soft-delete đúng quyết định, không truy xuất Identity bằng danh sách phone. **Kiểm tra:** các ví dụ lịch sử, trùng người, tên/SĐT trống khớp contract.
4. Viết test authorization, pagination, dữ liệu không liên kết và cross-owner; build/lint/test, cập nhật OpenAPI/bundle và kiểm thử Gateway.

## Acceptance

- Landlord truy vấn được tập khách thuê được định nghĩa, kể cả tenant không có tài khoản, không lộ thông tin của landlord khác.
- Quy tắc nhận diện, lịch sử và điều kiện rỗng được PM chốt, có ví dụ trong API contract; không tạo bản ghi user mới chỉ để hiển thị.
- Có bằng chứng request/response và test cho ownership, nhiều contract và pagination.
