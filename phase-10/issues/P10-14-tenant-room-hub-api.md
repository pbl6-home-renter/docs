# P10-14 — Cung cấp dữ liệu phòng của tenant qua API

**Loại:** Backend · **Trạng thái:** ⚪ Blocked — chốt response và access rule  
**Owner đề xuất:** `leminhkhai345` · **Reviewer:** API owner / PM · **Repo:** `Tenancy-Service`, `api-docs`  
**Phụ thuộc:** P6-01e1/e2, P6-02g4, P10-11 · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## Bối cảnh

Tenant flow có trang phòng hiện tại. OpenAPI `GET /me/room-hub` đang `designing`; controller room hiện có `/me/rooms` phục vụ landlord, chưa thấy endpoint hub. Schema nháp chứa payment/issue trong khi P6-D61 và P9-D83 đang deferred; không thể triển khai đầy đủ theo example cũ mà không đối chiếu decision.

## User story và blocker

Là tenant có hợp đồng được liên kết, tôi muốn xem thông tin phòng thuộc quyền của mình. PM/API owner cần chốt: khi có nhiều hợp đồng đang có quyền thì chọn hoặc trả danh sách thế nào; các field được hiển thị, trạng thái `không có phòng` và dữ liệu được phép truy cập. Chỉ sau khi contract được chốt mới triển khai phần phụ thuộc; không tự gán payment, issue hay số công nợ.

## Các bước triển khai

1. Đối chiếu `me-room-hub.yaml`, `MyRoomHubResponseDto`, P6-D61/D63/D71 và `GET /me/contracts`; ghi field → nguồn → quyền → tình trạng scope. Cập nhật decision/API sau phê duyệt. **Kiểm tra:** có ví dụ tenant đại diện, thành viên, đã rời và không có phòng.
2. Xây dựng read model/query và endpoint theo contract đã chốt; tái sử dụng điều kiện quyền từ `GET /me/contracts`, bảo vệ user khác và phòng đã xóa theo decision. Không query theo phone hoặc đọc DB của service khác. **Kiểm tra:** tenant A không nhận room/contract của B; trạng thái đã rời xử lý đúng contract.
3. Ánh xạ dữ liệu sẵn có sang DTO; phân biệt dữ liệu không có và nguồn lỗi theo contract, không điền giá trị mặc định giả. **Kiểm tra:** tập dữ liệu không có invoice/readings và nguồn lỗi trả đúng behavior đã duyệt.
4. Test domain/application và integration cần thiết cho ownership, nhiều contract, rỗng và soft-delete; chạy build/lint/test, cập nhật OpenAPI và bundle, thử qua Gateway.

## Acceptance

- Response chứa đúng phòng/contract thuộc quyền tenant theo decision mới; tenant khác và member đã rời không thấy dữ liệu trái phép.
- Không có payment/issue/OCR giả; field và lỗi khớp contract được phê duyệt, có bằng chứng API qua Gateway.
- Trường hợp nhiều phòng và không có phòng được định nghĩa trước khi đóng blocker; không suy diễn từ ví dụ một phòng.
