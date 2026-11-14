# P10-15 — Màn phòng của tôi và tổng quan tenant trên Web

**Loại:** Frontend · **Trạng thái:** 🔵 In progress — thiếu trạng thái thanh toán  
**Owner đề xuất:** `ThaiBao11125` · **Reviewer:** FE Lead / PM · **Repo:** `fe`  
**Phụ thuộc:** P10-07; trạng thái thanh toán đáng tin cậy cho tóm tắt hóa đơn chưa thanh toán · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## Cập nhật triển khai 14/11/2026

PM đã chốt D7 lite dùng /me/contracts và /me/invoices, không dùng /me/room-hub. [FE #41](https://github.com/pbl6-home-renter/fe/pull/41) và dependency [FE #39](https://github.com/pbl6-home-renter/fe/pull/39) đã merge phần phòng và hợp đồng. /me/invoices chỉ cho biết issued, không có trạng thái thanh toán nên chưa thể xác định hóa đơn chưa thanh toán gần nhất; còn kiểm thử Gateway và quyền tenant.

## Bối cảnh và mục tiêu

Tenant menu hiện trỏ `/rooms`, nhưng route đó được `ProtectedRoute` giới hạn landlord; dashboard tenant là placeholder. Người thuê cần xem dữ liệu phòng thuộc quyền và đi tới hợp đồng/hóa đơn mà không thấy hành động quản trị của landlord.

## Triển khai

1. Theo D7 lite, map hợp đồng active từ /me/contracts thành các card phòng; không dùng /me/room-hub. Rà dispatcher để tenant và landlord dùng cùng URL mà không xung đột guard. **Kiểm tra:** landlord route cũ tiếp tục hoạt động, tenant đăng nhập vào được trang của mình.
2. Thêm API/query hook dùng session hiện tại, query keys đầy đủ và component read-only cho dữ liệu được contract cho phép; không tái sử dụng mutation landlord. **Kiểm tra:** hai tenant khác phòng chỉ thấy dữ liệu được API cấp; tài khoản không liên kết thấy empty state được duyệt.
3. Nối dashboard tenant và điều hướng tới phòng, hợp đồng P10-07 và invoice P8-05 khi khả dụng. Tách loading/error/empty; i18n đầy đủ `vi/en`. **Kiểm tra:** API lỗi không bị hiện là tenant chưa có phòng, refresh URL giữ đúng role.
4. Chạy build/lint/i18n; kiểm tra qua Gateway với tenant đại diện/member/đã rời, nhiều phòng nếu được hỗ trợ, 360px/desktop và bàn phím.

## Acceptance

- Tenant mở được phòng và dashboard bằng dữ liệu thực, không thấy các thao tác chỉnh sửa, xóa hoặc quản lý của landlord.
- Đúng quyền với tài khoản khác, loading/empty/error tách bạch; không hiển thị payment, issue hay số tiền giả.
- Các liên kết hoạt động theo dependency; có bằng chứng FE/Gateway và không hồi quy màn landlord.
