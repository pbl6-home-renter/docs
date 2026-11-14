# P10-28 — API báo và xử lý sự cố thuê trọ

**Loại:** Backend · **Trạng thái:** 🔵 In progress — PR nháp, chờ migration và xác minh  
**Owner đề xuất:** BE Lead / người được giao · **Reviewer:** PM / API owner · **Repo:** service owner sau khi chốt, `api-docs`  
**Phụ thuộc:** P10-11, [P10-D86](../decisions.md) · **Ước lượng:** chưa chốt · **Issue:** [docs#151](https://github.com/pbl6-home-renter/docs/issues/151)

**PR nháp:** [Community #37](https://github.com/pbl6-home-renter/community-service/pull/37) · [Tenancy #53](https://github.com/pbl6-home-renter/Tenancy-Service/pull/53) · [Identity #41](https://github.com/pbl6-home-renter/Identity-Service/pull/41) · [Gateway #11](https://github.com/pbl6-home-renter/api-gateway/pull/11) · [API docs #67](https://github.com/pbl6-home-renter/api-doc/pull/67)

**Bàn giao đang dở:** Đã thêm mã API, gateway, kiểm tra quyền Media và producer notification. Chưa sinh migration `issue_reports` vì PostgreSQL cục bộ không sẵn sàng; trước khi chạy feature, cấu hình database phát triển riêng, chạy `npm run migration:generate -- src/database/migrations/CreateIssueReports` trong `community-service`, review migration để loại thay đổi ngoài scope rồi áp dụng theo quy trình repo. Chưa xác nhận end-to-end.

## Mục tiêu và bằng chứng

OpenAPI có sáu operation designing: `GET /me/issues`, `GET/POST /issues`, `GET/PATCH /issues/{id}`, `POST /issues/{id}/cancel`. Tenant hoặc landlord muốn theo dõi sự cố theo user flow. [P10-D86](../decisions.md) đưa IssueReport, ảnh và notification vào scope, thay thế quyết định defer trước đây cho phần việc này.

## Triển khai

1. Áp dụng actor, room/contract, lifecycle, ảnh, privacy và notification theo P10-D86. **Kiểm tra:** state/action matrix và ví dụ tenant đã rời, landlord khác, tenant không login được review.
2. Đồng bộ OpenAPI, implement persistence, authorization và các operation theo contract được duyệt; ảnh chỉ qua Media policy/owner contract được chốt, không dùng `UnavailableOwnerResolver` như thể đã hỗ trợ. **Kiểm tra:** người không thuộc resource không đọc/sửa được; retry hoặc concurrent action không làm mất invariant.
3. Triển khai producer notification/outbox theo P10-D86; không lẫn với P9-08 invoice notification. **Kiểm tra:** event retry idempotent và không phát notice cho recipient sai.
4. Test state transitions, ownership, pagination, ảnh và failure; build/lint/test, API docs lint/bundle và kiểm tra Gateway. Tách PR/issue nếu phạm vi vượt giới hạn.

## Acceptance

- Operation được duyệt xử lý đúng state, actor và ownership; không lộ mô tả/ảnh cho user không được phép.
- Có quyết định scope và contract trước khi implement, bằng chứng API và tests; không triển khai tự động feature `@issue` khi chưa được duyệt.
