# P10-17 — Danh sách và chi tiết khách thuê trên Web

**Loại:** Frontend · **Trạng thái:** ⚪ Blocked — P10-16  
**Owner đề xuất:** `ThaiBao11125` · **Reviewer:** FE Lead / PM · **Repo:** `fe`  
**Phụ thuộc:** P10-16 · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## User story

Là chủ nhà, tôi muốn mở danh sách khách thuê và xem thông tin liên quan của từng người để theo dõi hợp đồng, kể cả khách chưa có tài khoản. Hiện hai route `/tenants` và `/tenants/:id` đang hiển thị `DashboardOverview`.

## Các bước triển khai

1. Map contract P10-16: định danh, fields, filter, sort, pagination, lỗi và điều hướng từ contract/room. **Kiểm tra:** tài khoản landlord có dữ liệu và tài khoản không có dữ liệu trả đúng DTO.
2. Thay placeholder list bằng bảng/card responsive; thêm query hook, query key gồm params, loading/error/empty/filtered-empty và trạng thái người chưa liên kết nếu API phân biệt. **Kiểm tra:** filter/pagination và F5 không làm sai tập kết quả; lỗi API có retry.
3. Thay placeholder detail bằng trang read-only theo contract, link tới các contract mà API cho phép; không dùng user directory chung hoặc dựng tên/SĐT. **Kiểm tra:** direct URL, ID không tồn tại và ID của landlord khác có response/hiển thị phù hợp.
4. Dùng `ROUTES`, primitive và i18n `vi/en`; chạy build/lint/i18n, kiểm tra mobile/desktop, bàn phím và tài khoản không có tenantId.

## Acceptance

- Người dùng thấy đúng danh sách/chi tiết được backend trả về và truy cập được từ menu, không xem được dữ liệu landlord khác.
- Không bỏ sót khách chưa có account do filter phía FE; loading/error/empty và pagination hoạt động đúng.
- PR có ảnh đã ẩn PII, ví dụ luồng và kết quả build/lint/i18n; không tạo trang CRUD ngoài contract.
