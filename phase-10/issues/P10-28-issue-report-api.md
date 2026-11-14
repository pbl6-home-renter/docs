# P10-28 — API báo và xử lý sự cố thuê trọ

**Loại:** Backend · **Trạng thái:** ⏪ Deferred — IssueReport ngoài scope theo P6-D61/P9-D83  
**Owner đề xuất:** BE Lead / người được giao · **Reviewer:** PM / API owner · **Repo:** service owner sau khi chốt, `api-docs`  
**Phụ thuộc:** P10-11, decision scope IssueReport · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## Mục tiêu và bằng chứng

OpenAPI có sáu operation designing: `GET /me/issues`, `GET/POST /issues`, `GET/PATCH /issues/{id}`, `POST /issues/{id}/cancel`; chưa thấy IssueReport module trong các service đã rà. Tenant hoặc landlord muốn theo dõi sự cố theo user flow. P6-D61/P9-D83 hiện defer feature và notification, nên issue này là backlog chờ scope, không phải approval thực hiện.

## Triển khai sau khi scope được duyệt

1. PM chốt actor, ai tạo/nhận/xem/sửa/hủy, liên kết room/contract, lifecycle, ảnh, privacy và notification; đối chiếu user flow cũ với quyết định mới, chỉ định service owner. **Kiểm tra:** state/action matrix và ví dụ tenant đã rời, landlord khác, tenant không login được review.
2. Đồng bộ OpenAPI, implement persistence, authorization và các operation theo contract được duyệt; ảnh chỉ qua Media policy/owner contract được chốt, không dùng `UnavailableOwnerResolver` như thể đã hỗ trợ. **Kiểm tra:** người không thuộc resource không đọc/sửa được; retry hoặc concurrent action không làm mất invariant.
3. Tách producer notification/outbox thành issue con nếu PM chốt; không lẫn với P9-08 invoice notification. **Kiểm tra:** event retry idempotent và không phát notice cho recipient sai nếu được duyệt.
4. Test state transitions, ownership, pagination, ảnh và failure; build/lint/test, API docs lint/bundle và kiểm tra Gateway. Tách PR/issue nếu phạm vi vượt giới hạn.

## Acceptance

- Operation được duyệt xử lý đúng state, actor và ownership; không lộ mô tả/ảnh cho user không được phép.
- Có quyết định scope và contract trước khi implement, bằng chứng API và tests; không triển khai tự động feature `@issue` khi chưa được duyệt.
