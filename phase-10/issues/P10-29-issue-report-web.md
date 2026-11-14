# P10-29 — Giao diện báo và quản lý sự cố trên Web

**Loại:** Frontend · **Trạng thái:** 🔵 In progress — PR nháp, chờ backend và xác minh  
**Owner đề xuất:** `ThaiBao11125` · **Reviewer:** FE Lead / PM · **Repo:** `fe`  
**Phụ thuộc:** P10-28, P10-11, [P10-D86](../decisions.md) · **Ước lượng:** chưa chốt · **Issue:** [docs#152](https://github.com/pbl6-home-renter/docs/issues/152)

**PR nháp:** [Web #47](https://github.com/pbl6-home-renter/fe/pull/47) · [API docs #67](https://github.com/pbl6-home-renter/api-doc/pull/67) · [Community #37](https://github.com/pbl6-home-renter/community-service/pull/37)

**Bàn giao đang dở:** Đã nối danh sách, tạo, chi tiết, cập nhật, hủy và upload ảnh với API; cần migration của P10-28 và kiểm tra tích hợp trên môi trường của dự án trước khi đánh dấu hoàn thành.

## Mục tiêu

Route issue list, tạo mới và chi tiết hiện là `DashboardOverview` placeholder. Theo P10-D86, user phù hợp cần có màn hình theo API P10-28, hỗ trợ ảnh thật và dịch notification theo key từ backend.

## Triển khai

1. Đối chiếu actor, trạng thái, fields, upload và permissions đã duyệt trong P10-28; map action theo role, không suy ra quyền từ việc ẩn nút. **Kiểm tra:** có ví dụ landlord, tenant được phép và user ngoài phạm vi.
2. Xây dựng list/detail/form bằng API thật, i18n và primitive, query invalidation và pagination; hiển thị loading/empty/error riêng. **Kiểm tra:** user tạo, xem, sửa/hủy theo state được chốt; API lỗi không mất form hoặc thông báo thành công.
3. Nếu contract ảnh được duyệt, dùng Media upload và quyền từ API; xử lý upload thất bại, không lưu link giả. **Kiểm tra:** file sai quyền/không complete không được đính kèm.
4. Test hai role, direct URL trái phép, stale state, mobile, keyboard; chạy FE build/lint/i18n và smoke Gateway.

## Acceptance

- Mỗi role chỉ thấy và thực hiện các thao tác được backend cấp quyền; list/detail/form phản ánh dữ liệu và trạng thái thật.
- Không dựng IssueReport, notification hay upload giả; dùng contract và backend theo P10-D86.
