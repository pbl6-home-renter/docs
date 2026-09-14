# P2-05 — API Conventions (Generic Patterns)

**Status:** 🟡 Open
**Owner:** BE
**Input:** P2-04 (ERD v1), business-rules, user_flow/*.md
**Output:** `discovery/api-conventions.md`

---

## Background

Trước khi design chi tiết từng endpoint (P2-06), cần establish **generic patterns** chung cho toàn bộ API — đảm bảo consistency giữa tất cả endpoints mà BE/Mobile/FE sẽ implement.

## Mục đích

Define và document các conventions: response format, pagination, error handling, auth scheme, request validation, naming — làm **input cho P2-06 (API Spec)**.

## Chi tiết thực hiện

### 1. Response Wrapper Format

Standardize format response body cho mọi endpoint — cover 3 trường hợp: single object, list, error. Đảmbé response luôn có cấu trúc đồng nhất.

### 2. Pagination

Chọn 1 style (cursor-based hoặc offset) và apply一致 cho toàn bộ list endpoints. Xác định default/max page size và response structure.

### 3. Error Codes & Messages

- HTTP status codes usage mapping (200, 201, 400, 401, 403, 404, 409, 422, 500)
- Custom error code format: `DOMAIN_ERROR_CODE`
- Error response structure với `code`, `message`, `details[]`
- Validation errors format (field-level)

### 4. Authentication & Authorization

- JWT Bearer token scheme
- Token payload structure
- Role-based access: `PUBLIC`, `TENANT`, `LANDLORD`, `ADMIN`
- Public vs protected endpoints pattern

### 5. Request Validation

- Required vs optional fields convention
- Date/time format (ISO 8601)
- Phone number format
- Money/amount format
- File upload convention (multipart/form-data)
- Query parameter types and defaults

### 6. Naming Conventions

Define convention cho: paths, fields, query params, headers, enums — đảm bảo consistency xuyên suốt API.

### 7. Versioning & Base URL

- API version pattern
- Base URL structure
- Deprecation headers for future versions

### 8. Rate Limiting

- Rate limit headers
- 429 Too Many Requests response format

### 9. Timestamp & Timezone

- Timezone rule (UTC hay local?)
- Timestamp format nhất quán cho created_at, updated_at, etc.

### 10. Null vs Omitted Fields

- Response JSON nên omit field khi không có giá trị, hay trả `null`?

### 11. Filtering & Sorting

- Query params pattern cho listing endpoints (filter by status, sort by date…)
- Multi-filter support
- Sort direction convention

### 12. Soft Delete vs Hard Delete

- Entity nào cần giữ data lịch sử (soft delete) vs xóa sạch (hard delete)?
- Ảnh hưởng đến foreign key relationships

### 13. Idempotency Key

- Payment endpoints cần idempotency key để prevent duplicate payment do retry
- Header convention cho idempotency key

### 14. Batch / Bulk Operations

- Có endpoint nào cần xử lý nhiều record 1 lần không?
- Pattern cho bulk request/response

## Definition of Done

- [ ] File `discovery/api-conventions.md` tồn tại
- [ ] Response wrapper format đã define (single, list, error)
- [ ] Pagination style đã chọn + response structure
- [ ] Error code format + HTTP status mapping
- [ ] Auth scheme (JWT) + role hierarchy
- [ ] Request validation rules (date, money, phone, file)
- [ ] Naming conventions (paths, fields, headers)
- [ ] Timestamp timezone + format
- [ ] Null vs omitted fields rule
- [ ] Filtering & sorting query params pattern
- [ ] Soft delete vs hard delete decision per entity
- [ ] Idempotency key convention (payment endpoints)
- [ ] Batch/bulk operations decision
- [ ] BE đã review và approve
- [ ] PM đã confirm conventions match business requirements
- [ ] Document sẵn sàng làm input cho P2-06 (API Spec)
