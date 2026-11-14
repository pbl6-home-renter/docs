# P10-27 — Giao diện tìm bạn ở ghép cho tenant

**Loại:** Frontend · **Trạng thái:** ⏪ Deferred — P10-25/26 và PM chốt scope  
**Owner đề xuất:** `ThaiBao11125` · **Reviewer:** FE Lead / PM · **Repo:** `fe`  
**Phụ thuộc:** P10-25, P10-26, P10-11 · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## Mục tiêu

Route `/roommates` và `/roommates/profile` hiện là placeholder. Sau khi matching được PM đưa vào scope, tenant có tài khoản có thể quản lý profile, xem danh sách và xử lý match request theo API được duyệt. Đây là Stretch; không giả định AI score hay dữ liệu mẫu.

## Triển khai

1. Map DTO, quyền, state machine và thao tác được duyệt từ P10-25/26; chia PR profile, list/detail, request nếu vượt giới hạn. **Kiểm tra:** mọi field/UI action có API và role tương ứng.
2. Thay placeholder bằng trang/profile form, danh sách/detail và luồng gửi/phản hồi/rút request; query/mutation keys, invalidation, loading/empty/error và i18n. **Kiểm tra:** hai user qua Gateway thấy đúng thay đổi, user không có quyền không gọi thành công mutation.
3. Kiểm tra state đã thay đổi khi hai tab cùng thao tác, retry/lỗi mạng, tenant chưa opt-in và role khác; không render điểm tương thích AI khi API chưa hỗ trợ. **Kiểm tra:** stale state được refetch, không báo thành công giả.
4. Chạy build/lint/i18n, test bàn phím và mobile; lưu evidence che PII.

## Acceptance

- UI chỉ hiển thị tính năng đã được duyệt, dùng dữ liệu thực và thể hiện đúng state/permission; error, empty và pagination được xử lý.
- Tenant không tham gia và landlord/admin không truy cập được thao tác ngoài quyền theo contract; không có AI score giả.
