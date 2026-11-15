# P10-14 — Cung cấp dữ liệu phòng của tenant qua API

**Loại:** Backend · **Trạng thái:** 🔵 In progress — PR chờ review, chờ kiểm thử tích hợp

**Owner đề xuất:** `leminhkhai345` · **Reviewer:** API owner / PM · **Repo:** `Tenancy-Service`, `api-docs`  
**Phụ thuộc:** P6-01e1/e2, P6-02g4, P10-11 · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## Bối cảnh

Tenant flow có trang phòng hiện tại. OpenAPI `GET /me/room-hub` đang `designing`; controller room hiện có `/me/rooms` phục vụ landlord, chưa thấy endpoint hub. Schema nháp chứa payment/issue trong khi P6-D61 và P9-D83 đang deferred; không thể triển khai đầy đủ theo example cũ mà không đối chiếu decision.

## User story và blocker

Là tenant có hợp đồng được liên kết, tôi muốn xem thông tin phòng thuộc quyền của mình. PM/API owner cần chốt: khi có nhiều hợp đồng đang có quyền thì chọn hoặc trả danh sách thế nào; các field được hiển thị, trạng thái `không có phòng` và dữ liệu được phép truy cập. Chỉ sau khi contract được chốt mới triển khai phần phụ thuộc; không tự gán payment, issue hay số công nợ.

## Thiết kế và triển khai 15/11/2026

Theo [P10-D87](../decisions.md), endpoint trả danh sách phân trang các hợp đồng active và phòng tương ứng, rỗng khi không có kết quả. Quyền tenant và thành viên dùng chung điều kiện `/me/contracts`; bỏ bản ghi phòng, tòa hoặc hợp đồng đã xóa mềm. Response dùng dữ liệu thật trong Tenancy, không suy đoán thanh toán hoặc sự cố. [Tenancy PR #56](https://github.com/pbl6-home-renter/Tenancy-Service/pull/56) và [API contract PR #70](https://github.com/pbl6-home-renter/api-doc/pull/70) đang chờ review; còn kiểm thử PostgreSQL/Gateway trước khi nghiệm thu.

## Các bước triển khai

1. Đối chiếu `me-room-hub.yaml`, `MyRoomHubResponseDto`, P6-D61/D63/D71 và `GET /me/contracts`; ghi field → nguồn → quyền → tình trạng scope. Cập nhật decision/API sau phê duyệt. **Kiểm tra:** có ví dụ tenant đại diện, thành viên, đã rời và không có phòng.
2. Xây dựng read model/query và endpoint theo contract đã chốt; tái sử dụng điều kiện quyền từ `GET /me/contracts`, bảo vệ user khác và phòng đã xóa theo decision. Không query theo phone hoặc đọc DB của service khác. **Kiểm tra:** tenant A không nhận room/contract của B; trạng thái đã rời xử lý đúng contract.
3. Ánh xạ dữ liệu sẵn có sang DTO; phân biệt dữ liệu không có và nguồn lỗi theo contract, không điền giá trị mặc định giả. **Kiểm tra:** tập dữ liệu không có invoice/readings và nguồn lỗi trả đúng behavior đã duyệt.
4. Test domain/application và integration cần thiết cho ownership, nhiều contract, rỗng và soft-delete; chạy build/lint/test, cập nhật OpenAPI và bundle, thử qua Gateway.

## Acceptance

- Response chứa đúng phòng/contract thuộc quyền tenant theo decision mới; tenant khác và member đã rời không thấy dữ liệu trái phép.
- Không có payment/issue/OCR giả; field và lỗi khớp contract được phê duyệt, có bằng chứng API qua Gateway.
- Trường hợp nhiều phòng và không có phòng được định nghĩa trước khi đóng blocker; không suy diễn từ ví dụ một phòng.
