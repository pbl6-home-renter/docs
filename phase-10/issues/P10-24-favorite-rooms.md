# P10-24 — Phòng yêu thích: API và giao diện tenant

> **↪ Phase 11 (2026-11-21):** phần client Web thay bằng P11-12; phần BE/API giữ ở đây. Xem [tracker Phase 11](../../phase-11/issues/README.md).

**Loại:** Backend + client · **Trạng thái:** 🔵 BE/API được duyệt theo P10-D90, code local + SQL pass; chưa migration/deploy/client
**Owner đề xuất:** BE / `ThaiBao11125` · **Reviewer:** PM / API owner · **Repo:** service owner sau khi chốt, `api-docs`, `fe`  
**Phụ thuộc:** P10-11, P5-09d · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## Bối cảnh và mục tiêu

**Implementation 18/11/2026:** người dùng duyệt triển khai toàn bộ plan, supersede deferral cho BE/API. Tenancy đã có GET/POST/DELETE, migration composite key, query isFavorited theo user; room unavailable/không public được ẩn nhưng vẫn bỏ lưu được. POST trùng 409; DELETE không có bản ghi 404; list trống 200 không cần profile. [Evidence](../discovery/mobile-backend-implementation.md). FE/mobile integration và live acceptance chưa hoàn thành; audit bên dưới ghi lại thời điểm trước implementation.

**Audit 18/11/2026:** người dùng yêu cầu kiểm tra A6 và lập plan sửa. Local gateway đã route `/me/favorite-rooms` tới Tenancy, nhưng chưa có favorite controller/persistence trong `Tenancy-Service/src`; room list hiện gán cứng `isFavorited = false`. Vì vậy không có bằng chứng cần tạo tenant profile để khắc phục. Chưa tự tái hiện HTTP authenticated trên server. Giữ nguyên trạng thái implementation deferred/designing; yêu cầu audit/plan không được hiểu là tính năng đã release. Xem [plan](../../tasks/plan.md).

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

## Thứ tự PR đề xuất sau khi chốt rule

1. Backend persistence theo tenant user ID với uniqueness `(tenantId, roomId)` và soft-delete/restore semantics rõ; implement GET/POST/DELETE theo contract đã chốt. Tenant mới chưa lưu phòng trả 200 với `data: []`, không yêu cầu hồ sơ phụ. Thử tenant khác, retry, phòng không tồn tại/không public và pagination. Scope M: entity/migration/repository và test, tách controller/query thành PR kế tiếp nếu quá lớn.
2. Backend nối `isFavorited` vào list theo viewer authenticated, anonymous là false; cập nhật YAML/ví dụ/bundle và đồng bộ error/idempotency cho POST/DELETE. Test trạng thái sau add/remove và hai account, build/lint/Jest phù hợp; api-docs lint/bundle.
3. Mobile/Web tích hợp trên source đúng: lưu/bỏ lưu, list, query invalidation, empty/error; build client và smoke qua gateway. Không báo lưu thành công khi server còn trả 404. Theo dõi bằng chứng tổng thể tại P10-37.

**Owner/repo đề xuất cụ thể:** Tenancy cho dữ liệu favorite; Identity chỉ xác thực tài khoản hiện có. API owner xác nhận policy phòng unavailable/đã xóa và semantics POST trùng/DELETE lại trước implementation, không tự đổi contract dựa trên giả thuyết thiếu profile.
