# P10-21 — Màn dashboard quản trị với dữ liệu thật

**Loại:** Frontend · **Trạng thái:** ⚪ Blocked — P10-19  
**Owner đề xuất:** `ThaiBao11125` · **Reviewer:** FE Lead / PM · **Repo:** `fe`  
**Phụ thuộc:** P10-19 · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## User story

Là admin, tôi muốn xem dashboard theo các metric và kỳ được duyệt để theo dõi vận hành. Route `/admin` hiện là `DashboardOverview` placeholder. Những field chưa có nguồn, đặc biệt Payment, không được hiển thị bằng dữ liệu giả.

## Các bước triển khai

1. Đối chiếu DTO, role, filter thời gian và behavior lỗi từ API P10-19; map từng metric sang nhãn i18n và đơn vị. **Kiểm tra:** response mẫu được API owner xác nhận tương ứng đúng thẻ.
2. Tạo API client/query key, màn `/admin` dùng primitive sẵn có; tách loading, empty và error, hỗ trợ filter nếu contract cho phép. **Kiểm tra:** thay đổi filter refetch đúng; lỗi service không hiển thị số 0 giả.
3. Bảo vệ route theo role, điều hướng phù hợp, dịch `vi/en` và responsive. **Kiểm tra:** tenant/landlord không xem được dữ liệu; 360px và desktop không che nội dung.
4. Chạy build/lint/i18n và kiểm thử thực tế qua Gateway bằng admin và user thường; ghi ảnh, dữ liệu fixture và bằng chứng không dùng mock.

## Acceptance

- Admin xem được metric được duyệt đúng dữ liệu và kỳ, quyền được kiểm tra ở backend lẫn route; không có card giả.
- Empty/loading/error và filter hoạt động theo contract, không hồi quy route admin khác; kiểm tra build/lint/i18n pass.
