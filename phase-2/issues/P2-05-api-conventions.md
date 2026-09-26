# P2-05 — API Conventions (Generic Patterns)

**Status:** 🟡 Open
**Owner:** BE
**Input:** P2-04 (ERD v1 — chưa có file), `phase-1/discovery/database-design.md`, user_flow/*.md
**Output:** `discovery/api-conventions.md`

---

## Background

Trước khi design chi tiết từng endpoint (P2-06), cần establish **generic patterns** chung cho toàn bộ API — đảm bảo consistency giữa tất cả endpoints mà BE/Mobile/FE sẽ implement.

## Mục đích

Define và document các conventions: response format, pagination, error handling, auth scheme, request validation, naming — làm **input cho P2-06 (API Spec)**.

## Chi tiết thực hiện

### 1. Response Wrapper Format

Standardize format response body cho mọi endpoint — cover 3 trường hợp: single object, list, error. Đảm bảo response luôn có cấu trúc đồng nhất.

### 2. Pagination

Chọn 1 style (cursor-based hoặc offset) và áp dụng nhất quán cho toàn bộ list endpoints. Xác định default/max page size và response structure.

### 3. Error Codes & Messages

- HTTP status codes usage mapping (200, 201, 400, 401, 403, 404, 409, 422, 500)
- Custom error code format: `DOMAIN_ERROR_CODE`
- Error response structure với `code`; không dùng `message`/`details[]` (xem §3 của `api-conventions.md`)
- Validation errors format (field-level)

### 4. Authentication & Authorization

- JWT Bearer token scheme
- Token payload structure
- Role-based access: `public`, `tenant`, `landlord`, `admin`, `system` (`tenant_contract` removed)
- Public vs protected endpoints pattern
- `/me` là ngoại lệ tự phục vụ duy nhất — không bao giờ trỏ tới tài nguyên người khác
- Quyền `Media` kế thừa từ `ownerType`/`ownerId` — cột quyền để trống, server nạp rule cha

### 5. Request Validation

- Required vs optional fields convention
- Date/time format (ISO 8601)
- Phone number format
- Money/amount format
- File upload convention: **2-step presign** (`POST /media/presign-upload` → client PUT → `POST /media/{mediaId}/complete-upload`); backend không nhận multipart; allowed MIME: `image/jpeg`, `image/png`, `image/webp`, `application/pdf`; size limit per endpoint
- Query parameter types and defaults

### 6. Naming Conventions

Define convention cho: paths, fields, query params, headers, enums — đảm bảo consistency xuyên suốt API.
- Domain action examples: `POST /invoices/issue-invoice`, `POST /media/{mediaId}/complete-upload`, `POST /payments/record-cash-payment`
- Collection-level business action: no parent ID in path, receives IDs in body
- Generic `/bulk` or `/batch` forbidden

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
- `format` (`xlsx`/`csv`/`pdf`/`json`) **chỉ áp dụng cho collection `GET`**, không khai báo trên resource-detail `GET` (detail luôn trả JSON)
- Không có endpoint xuất riêng (`*/export`) — cấm cả route tải một tài liệu đơn lẻ; tài liệu đơn lẻ lấy bằng filter collection

### 12. Soft Delete vs Hard Delete

- Entity nào cần giữ data lịch sử (soft delete) vs xóa sạch (hard delete)?
- Ảnh hưởng đến foreign key relationships
- **Soft delete dùng cờ `is_deleted` trong Base Entity** (không có `deletedAt`); schema đã có sẵn cột này
- **Cascade boundary tường minh:** `DELETE /users/{userId}` và `DELETE /buildings/{buildingId}` chỉ cascade mềm sang con vận hành; **không bao giờ cascade** sang `Contract`, `ContractMember`, `Invoice`, `Payment`, `MeterReading`, `IssueReport`, `Message`, `Conversation`, `AuditLog` (giữ cho tài chính/pháp lý/audit)
- `User` → soft delete qua admin `DELETE /users/{userId}` (không có self-service)
- `Building` → soft delete qua `DELETE /buildings/{buildingId}`
- `Media` → soft delete qua `DELETE /media/{mediaId}` cho media của chính người gọi
- `FavoriteRoom`, `PushDevice` → có thể hard delete

### 13. Idempotency Key

- Payment endpoints cần idempotency key để prevent duplicate payment do retry
- Header convention cho idempotency key
- **Business-named bulk invoice actions** (`POST /invoices/issue-invoice`, `POST /invoices/send-reminder`) **cũng bắt buộc `Idempotency-Key`** — cùng retention 24h, cùng `409 IDEMPOTENCY KEY REUSED` behavior; per-record business failures trả trong response body (`failed[]`) chứ không phải HTTP error

### 14. Batch / Bulk Operations

- Quy tắc chung: không generic `/bulk`/`/batch`, không import, sinh hóa đơn theo từng phòng (D33)
- **Hai bulk action có tên nghiệp vụ trong v1:**
  - `POST /invoices/issue-invoice`
  - `POST /invoices/send-reminder`
- Pattern: explicit `invoiceIds[]` trong body, item cap (OpenAPI), per-item ownership check, per-item result (`id` + `code`) split `succeeded[]`/`failed[]`, counts, **không atomic** (partial success allowed), bắt buộc `Idempotency-Key`
- Cấm bulk cho: signed contract, meter/OCR commit, evidence, property status change, user lock/unlock
- Tham chiếu quyết định D43 trong `phase-2/discovery/decisions.md`

## Definition of Done

- [x] File `discovery/api-conventions.md` tồn tại
- [x] Response wrapper format đã define (single, list, error)
- [x] Pagination style đã chọn + response structure
- [x] Error code format + HTTP status mapping
- [x] Auth scheme (JWT) + role hierarchy
- [x] Request validation rules (date, money, phone, file)
- [x] Naming conventions (paths, fields, headers)
- [x] Timestamp timezone + format
- [x] Null vs omitted fields rule
- [x] Filtering & sorting query params pattern
- [x] Soft delete vs hard delete decision per entity
- [x] Idempotency key convention (payment endpoints)
- [x] Batch/bulk operations decision
- [ ] BE đã review và approve
- [ ] PM đã confirm conventions match business requirements
- [x] Document sẵn sàng làm input cho P2-06 (API Spec)

**Open items (stay open):**
- Rate-limit numbers (chỉ là tham chiếu, BE xác nhận trước P2-06 freeze — xem `api-conventions.md` §8)
- P2-04 ERD reconciliation (đối chiếu ERD cuối trước khi P2-06 freeze)
