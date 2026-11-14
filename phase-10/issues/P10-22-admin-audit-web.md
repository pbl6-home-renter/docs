# P10-22 — Danh sách và chi tiết nhật ký quản trị trên Web

**Loại:** Frontend · **Trạng thái:** ⚪ Blocked — P10-20  
**Owner đề xuất:** `ThaiBao11125` · **Reviewer:** FE Lead / PM · **Repo:** `fe`  
**Phụ thuộc:** P10-20 · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## User story

Là admin, tôi muốn tìm và xem nhật ký quản trị theo các bộ lọc được duyệt để kiểm tra lịch sử thao tác. Route `/admin/audit-logs` hiện là placeholder; UI phụ thuộc contract và dữ liệu thật từ P10-20.

## Các bước triển khai

1. Map DTO list/detail, filter actor/entity/date, pagination, quyền và lỗi đã chốt; không cung cấp export nếu API chưa hỗ trợ. **Kiểm tra:** API trả fixture audit được redaction theo contract.
2. Thêm API/query hooks và danh sách có loading, empty, filtered-empty, error/retry, sort/filter/pagination hợp lệ trên URL. **Kiểm tra:** đổi filter reset trang hợp lý; F5 giữ filter và trang không vượt giới hạn.
3. Thêm chi tiết read-only qua dialog/route theo UI conventions; chỉ render field API cho phép. **Kiểm tra:** ID không có và user thường không đọc được record, không in thông tin nhạy cảm ra console.
4. Thêm bản dịch `vi/en`, accessibility và responsive; chạy build/lint/i18n, kiểm thử admin và user thường qua Gateway.

## Acceptance

- Admin tìm, phân trang và mở detail đúng record thật, phạm vi/ngày hiển thị rõ; tenant/landlord bị chặn.
- Không mô phỏng audit, không lộ field bị redaction; có evidence loading/error/empty và kết quả kiểm tra.
