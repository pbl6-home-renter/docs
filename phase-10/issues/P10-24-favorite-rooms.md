# P10-24 — Phòng yêu thích: API và giao diện tenant

**Loại:** Backend + FE · **Trạng thái:** ⏪ Deferred — chờ PM chốt scope qua P10-11  
**Owner đề xuất:** BE / `ThaiBao11125` · **Reviewer:** PM / API owner · **Repo:** service owner sau khi chốt, `api-docs`, `fe`  
**Phụ thuộc:** P10-11, P5-09d · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## Bối cảnh và mục tiêu

Là tenant, tôi muốn lưu và xem phòng yêu thích để tìm lại sau. OpenAPI có `GET/POST /me/favorite-rooms` và `DELETE /me/favorite-rooms/{roomId}` ở trạng thái designing; chưa thấy controller tương ứng trong các service đã rà. P5-09 parent đã ghi favorite room cần module/issue sau. User flow tenant trên Web chưa đầy đủ.

## Quyết định và thực hiện

1. PM xác nhận feature có trong phase; API owner chốt ownership, danh sách/trạng thái phòng đã xóa hoặc không còn public, response, idempotency và quyền tenant. **Kiểm tra:** có ví dụ phòng public, unavailable, đã xóa và user khác.
2. Sau phê duyệt, hoàn thiện persistence/API theo contract: mỗi user thao tác tài nguyên của mình, đảm bảo không tạo favorite trùng khi retry; cập nhật OpenAPI/bundle. **Kiểm tra:** thêm hai lần, list theo tenant, xóa hai lần theo semantics đã duyệt, user khác không thấy list.
3. Bổ sung thao tác lưu/bỏ lưu tại màn tìm phòng được duyệt và trang danh sách yêu thích; query invalidation, loading/error/empty và i18n. **Kiểm tra:** refresh, phân trang, API lỗi và trạng thái phòng thay đổi.
4. Chạy BE build/lint/test phù hợp, FE build/lint/i18n và thử qua Gateway với hai tenant. Tách PR backend và FE theo dependency.

## Acceptance

- Sau khi scope được duyệt, tenant thêm/xóa/xem đúng danh sách của mình, dữ liệu không trùng khi retry; các trạng thái phòng không public được xử lý theo contract.
- FE không dùng dữ liệu giả, error không báo thành công; evidence bao gồm permission, pagination và hai phiên người dùng.
- Trước phê duyệt, chỉ rà/ghi blocker; không tạo thay đổi code hoặc coi endpoint designing là released.
