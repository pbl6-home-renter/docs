# Quy ước API — v1

> **Trạng thái:** Bản nháp, chờ BE và PM review  
> **Owner:** BE  
> **Đầu vào:** P2-04, user flow, `database-design.md`, các quyết định D18, D29, D33–D37  
> **Đầu ra sử dụng:** `openapi.yaml` trong `pbl6-backend` (P2-06)  
> **Cập nhật:** 2026-09-15

## Phạm vi

Tài liệu này quy định pattern chung cho REST API NestJS dùng bởi Web React và Mobile Kotlin. Tài liệu **không thêm endpoint, entity hay feature mới**; P2-06 sẽ thiết kế từng endpoint theo các quy ước này.

Các quy ước phải giữ nghiệp vụ đã chốt: tenant không bắt buộc có tài khoản (D29), hợp đồng chỉ có giá trị trong app khi upload file ký tay (D18), hóa đơn sinh theo từng phòng, hỗ trợ thanh toán một phần và void thay vì xóa (D33, D37), và số công tơ luôn có ảnh chứng cứ kể cả khi hiệu chỉnh số OCR (D34, D35).

> **Lưu ý:** `phase-1/business-rules.md` được các issue cũ tham chiếu nhưng hiện không tồn tại trong workspace. Bản nháp này đối chiếu `requirement.md`, decisions Phase 0/1, user flow, database design và `utility-billing-calculations.md`; PM cần xác nhận nguồn thay thế trước khi freeze P2-06.

## 1. Response Wrapper Format — Định dạng phản hồi chuẩn

Ngoại trừ `204 No Content`, response tải file, và response xác nhận webhook bên thứ ba, mọi response JSON đều có `statusCode` và `message`. Response thành công có thêm `data`.

- `statusCode` trùng với HTTP status code.
- `message` là thông điệp ngắn, an toàn để hiển thị cho người dùng.
- `data` chứa một resource, mảng resource hoặc kết quả action khi thành công; response lỗi không có field này.
- Response list có thêm `pagination`; response lỗi có thêm `errorCode` và `errors`.
- `201 Created` phải có header `Location` trỏ đến resource mới. `200 OK` dùng cho đọc/cập nhật/action đồng bộ. `202 Accepted` chỉ dùng khi OpenAPI mô tả rõ action bất đồng bộ và cách client theo dõi kết quả.

Ví dụ response một resource:

```json
{
  "statusCode": 200,
  "message": "Lấy thông tin phòng thành công.",
  "data": {
    "id": "4a8c559a-a010-4c42-b564-c79c05a3c22a",
    "name": "P.201",
    "rentPrice": 3500000,
    "createdAt": "2026-09-15T03:00:00.000Z",
    "updatedAt": "2026-09-15T03:00:00.000Z"
  }
}
```

Ví dụ lỗi validation:

```json
{
  "statusCode": 422,
  "message": "Một hoặc nhiều trường không hợp lệ.",
  "errorCode": "VALIDATION_FAILED",
  "errors": [
    {
      "field": "phone",
      "rule": "matches",
      "message": "Số điện thoại Việt Nam không hợp lệ."
    }
  ]
}
```

Client xử lý logic bằng `errorCode`, không dựa vào `message`. `errors` là mảng chi tiết theo field; nếu lỗi không gắn với field thì trả `[]`. Không trả stack trace, SQL, credential, prompt AI hay dữ liệu CCCD trong response lỗi.

## 2. Pagination — Phân trang

Toàn bộ collection thông thường dùng **offset pagination** để dashboard và trang quản trị có số trang/tổng bản ghi rõ ràng.

| Query param | Quy ước | Mặc định / giới hạn |
|---|---|---|
| `pageNo` | Số nguyên dương, bắt đầu từ 1 | `1` |
| `pageSize` | Số nguyên dương | `20`, tối đa `100` |

```json
{
  "statusCode": 200,
  "message": "Lấy danh sách phòng thành công.",
  "data": [
    {
      "id": "4a8c559a-a010-4c42-b564-c79c05a3c22a",
      "name": "P.201",
      "rentPrice": 3500000,
      "status": "available",
      "createdAt": "2026-09-15T03:00:00.000Z",
      "updatedAt": "2026-09-15T03:00:00.000Z"
    },
    {
      "id": "93ab7ec2-dc61-4f41-8502-8f5e6a3d6f19",
      "name": "P.202",
      "rentPrice": 3800000,
      "status": "occupied",
      "createdAt": "2026-09-15T03:00:00.000Z",
      "updatedAt": "2026-09-15T03:00:00.000Z"
    }
  ],
  "pagination": {
    "pageNo": 1,
    "pageSize": 20,
    "totalItems": 2,
    "totalPages": 1
  }
}
```

Giá trị `pageNo` hoặc `pageSize` sai trả `422 VALIDATION_FAILED`; không tự âm thầm sửa về giá trị mặc định. Không trộn cursor pagination vào endpoint list v1.

## 3. Error Codes & Messages — Mã lỗi và thông điệp

`errorCode` có định dạng `DOMAIN_REASON`, viết hoa và dùng dấu gạch dưới. Các mã nghiệp vụ đã có trong billing spec phải giữ nguyên: `READING_MISSING`, `METER_REVERSED`, `RATE_MISSING`, `AREA_MISSING`, `HEADCOUNT_ZERO`, `VEHICLE_COUNT_MISSING`, `TIER_CONFIG_INVALID`, `INVOICE_DUPLICATE`, `INVOICE_VOIDED`, `TOTAL_NEGATIVE`.

| HTTP | Khi dùng | Mã ví dụ |
|---|---|---|
| `200` | Đọc, cập nhật hoặc action đồng bộ thành công | — |
| `201` | Tạo resource thành công | — |
| `202` | Đã nhận action bất đồng bộ | — |
| `204` | Thành công nhưng không có body | — |
| `400` | JSON/header/media type sai cú pháp | `REQUEST_MALFORMED` |
| `401` | Thiếu, hết hạn hoặc token không hợp lệ | `AUTH_UNAUTHENTICATED` |
| `403` | Đã xác thực nhưng không được làm action | `AUTH_FORBIDDEN` |
| `404` | Không tồn tại hoặc không có quyền nhìn thấy resource | `RESOURCE_NOT_FOUND` |
| `409` | Trùng resource, state conflict, tái dùng idempotency key sai | `RESOURCE_CONFLICT` |
| `422` | Body hợp lệ cú pháp nhưng vi phạm validate/nghiệp vụ | `VALIDATION_FAILED`, `RATE_MISSING` |
| `429` | Vượt rate limit | `RATE_LIMITED` |
| `500` | Lỗi không mong đợi phía server | `INTERNAL_ERROR` |

`errors` là mảng lỗi theo field khi có thể trả an toàn; không có chi tiết thì trả mảng rỗng.

## 4. Authentication & Authorization — Xác thực và phân quyền

- Endpoint bảo vệ dùng `Authorization: Bearer <access-token>` và OpenAPI scheme `http`/`bearer`, `bearerFormat: JWT`.
- JWT chỉ chứa: `sub` (UUID user), `role` (`tenant`, `landlord`, `admin`), `iat`, `exp`. Không đưa mật khẩu, CCCD, URL media hoặc profile thay đổi thường xuyên vào token.
- `PUBLIC` là mức truy cập endpoint, **không** là role lưu trong database. Endpoint public chỉ trả field an toàn của phòng/BĐS đã được duyệt.
- Mỗi user chỉ có đúng một role bất biến theo D13. Không có role hierarchy kế thừa quyền: quyền là tổ hợp của role, action và ownership.
- RBAC luôn đi kèm ownership check: landlord chỉ thao tác dữ liệu thuộc quyền quản lý; tenant chỉ xem/thanh toán hợp đồng liên kết với mình; admin có quyền được khai báo rõ ở từng endpoint.
- Khi tenant bị khóa, quyền xem/thanh toán hợp đồng hiện tại vẫn phải tuân theo user flow; không dùng role guard chung để chặn nhầm quyền này.

## 5. Request Validation — Quy ước validate request

NestJS DTO validation là nguồn kiểm tra phía server. Từ chối field JSON không khai báo; chỉ transform field đã định kiểu; không ép giá trị sai thành giá trị hợp lệ.

| Dữ liệu | Quy ước |
|---|---|
| Bắt buộc / tùy chọn | Field bắt buộc phải có và không `null`. Field tùy chọn có thể omit. |
| Chuỗi | Trim khoảng trắng đầu/cuối nếu khoảng trắng không có nghĩa; min/max length nằm trong OpenAPI endpoint. |
| Date | `YYYY-MM-DD`; không dùng format theo locale. Billing period là `YYYY-MM`. |
| Timestamp | ISO 8601 UTC với hậu tố `Z`, ví dụ `2026-09-15T03:00:00.000Z`. |
| Tiền | Mọi tiền và đơn giá VND gửi/nhận qua API là số nguyên JSON, không dùng float. `otherFees[].amount` được âm chỉ cho giảm trừ hợp lệ theo D33; tổng hóa đơn không âm. Backend tính bằng PostgreSQL `numeric`/Decimal. |
| Số đo thập phân | Chỉ số công tơ, diện tích và số lượng thập phân dùng JSON string, ví dụ `"1380.5"`, `"18.5"`, để không mất chính xác qua JavaScript/Kotlin. |
| Số điện thoại | Chấp nhận `0xxxxxxxxx` hoặc `+84xxxxxxxxx`; chuẩn hóa lưu và trả về là `+84xxxxxxxxx`. Endpoint public không trả số điện thoại. |
| Boolean / enum | Dùng JSON boolean và enum đã khai báo, không dùng `0`/`1` hay display label. |

Upload file dùng `multipart/form-data`, với một part `file` và metadata được endpoint yêu cầu (ví dụ `purpose`). MVP chỉ chấp nhận `image/jpeg`, `image/png`, `image/webp`, `application/pdf`; OpenAPI từng endpoint phải nêu giới hạn kích thước. Response trả resource `Media` theo envelope chuẩn; không lộ storage path, URL public vĩnh viễn hay media nhạy cảm.

## 6. Naming Conventions — Quy ước đặt tên

| Thành phần | Quy ước | Ví dụ |
|---|---|---|
| Base path | `/api/v1` | `/api/v1/rooms` |
| Collection path | Danh từ số nhiều, lowercase kebab-case | `/match-requests` |
| Resource path | UUID ở path param camelCase | `/rooms/{roomId}` |
| CRUD path | Không dùng động từ | `POST /rooms`, `PATCH /rooms/{roomId}` |
| Domain action | Động từ rõ ràng ở subpath khi không phải CRUD | `POST /invoices/{invoiceId}/issue` |
| JSON field / query param | `camelCase` | `createdAt`, `buildingId` |
| Database field | Không expose trực tiếp | `created_at` → `createdAt` |
| Enum | lowercase snake_case | `partially_paid` |
| Header custom | Pascal-Case có dấu gạch nối | `Idempotency-Key`, `X-Request-Id` |

UUID dùng dạng canonical lowercase. URL không có trailing slash. Resource không tồn tại và resource bị ẩn do ownership đều trả `404` để không lộ dữ liệu.

## 7. Versioning & Base URL — Phiên bản và URL gốc

- Base URL phụ thuộc environment; client không hard-code host. Path chuẩn là `/api/v1`.
- Thay đổi breaking dùng major path mới, ví dụ `/api/v2`. Thêm field optional không phải breaking change của v1.
- Endpoint tương lai bị deprecate trả `Deprecation: true`, `Sunset` và `Link` tới endpoint thay thế (nếu có). Chỉ được xóa sau migration period được duyệt hoặc khi chuyển major version.
- API production dùng HTTPS. JSON mặc định UTF-8, trừ `multipart/form-data` và response tải file đã khai báo.

## 8. Rate Limiting — Giới hạn tần suất

- Hạn mức là cấu hình deployment, không hard-code một con số trong OpenAPI nếu hạ tầng chưa enforce được.
- Có thể áp policy khác nhau cho auth, upload, payment và public search.
- Khi áp dụng, response có `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`.
- Khi vượt hạn mức, trả `429`, header `Retry-After` và error envelope chuẩn với mã `RATE_LIMITED`.

## 9. Timestamp & Timezone — Thời gian và múi giờ

- Mọi instant lưu và trả về là UTC ISO 8601 (`createdAt`, `updatedAt`, `issuedAt`...).
- Ngày không kèm thời gian (`startDate`, `endDate`, `dueDate`) dùng `YYYY-MM-DD`.
- Tính kỳ hóa đơn, ngày đến hạn và quy tắc theo lịch dùng `Asia/Ho_Chi_Minh`. Client không tự tính ngày billing từ timezone của thiết bị.
- `period` luôn là tháng dương lịch `YYYY-MM`.

## 10. Null vs Omitted Fields — `null` và field bị omit

- Field optional trong **request**: omit nghĩa là không gửi giá trị. Với `PATCH`, omit nghĩa là không thay đổi field.
- Field nullable trong **response**: trả `null` khi giá trị được biết là chưa có/không áp dụng, ví dụ `tenantId: null` theo D29 hoặc `issuedAt: null` khi invoice `pending`.
- Không omit field response chỉ để biểu diễn `null`; field phải được mô tả nullable rõ trong OpenAPI.
- Không dùng `null` để xóa field bắt buộc. Endpoint cho phép clear field phải khai báo nullable và validate nghiệp vụ riêng.

## 11. Filtering & Sorting — Lọc và sắp xếp

| Query param | Quy ước | Default |
|---|---|---|
| `sort` | Một field API được endpoint cho phép sort | `createdAt` nếu áp dụng |
| `order` | `asc` hoặc `desc` | `desc` |
| Filter | Query param camelCase theo từng resource | `status`, `buildingId`, `createdFrom`, `createdTo`, `q` |

- Multi-value enum filter dùng dấu phẩy: `status=pending,overdue`.
- OpenAPI từng endpoint phải liệt kê field filter/sort hỗ trợ. Filter hoặc sort không hợp lệ trả `422 VALIDATION_FAILED`, không bị bỏ qua âm thầm.
- Server dùng `id` làm tie-breaker cuối để thứ tự ổn định qua các trang.

## 12. Soft Delete vs Hard Delete — Xóa mềm và xóa cứng

Không cho client hard-delete dữ liệu tài chính, pháp lý, audit hoặc bằng chứng. Dùng action nghiệp vụ thay vì để client ép state tùy ý.

| Nhóm resource | Quy ước v1 |
|---|---|
| Invoice | Không `DELETE`; dùng action `void`. Invoice cũ, snapshot, payment và liên kết invoice thay thế được giữ lại (D33, D37). |
| Payment, AuditLog, MeterReading, hợp đồng đã ký, ảnh OCR/evidence | Không có public delete. Giữ để audit/chứng cứ; chỉnh sửa qua record hoặc action được nghiệp vụ cho phép. |
| Contract, Building, Room, policy/fee, BillingSetting, IssueReport, Conversation, Message, RoommateProfile, MatchRequest, Notification | Không hard-delete endpoint. Dùng lifecycle action như `terminate`, `deactivate`, `close`, `cancel`, `leave`, `dismiss` hoặc soft-delete/retention process của domain. |
| FavoriteRoom, PushDevice | User được xóa record của chính mình; có thể hard delete vì không mang giá trị tài chính/pháp lý/audit. |
| User | Không mặc định có self-service hard delete. Chính sách deactivation/retention cần được phê duyệt riêng. |

## 13. Idempotency Key — Chống tạo thanh toán trùng

`POST` có thể tạo hoặc ghi nhận payment bắt buộc có header `Idempotency-Key`. Header là UUID do client sinh, áp dụng tối thiểu cho khởi tạo thanh toán và landlord xác nhận thu tiền mặt.

- Server lưu key, actor đã xác thực, request fingerprint và response kết quả tối thiểu 24 giờ.
- Gửi lại cùng key và cùng request trả lại nguyên status/body ban đầu.
- Dùng lại cùng key với payload khác trả `409 IDEMPOTENCY_KEY_REUSED`.
- Webhook payment dùng provider event/transaction ID đã ký để deduplicate và verify signature; không tin idempotency key do client gửi.
- Idempotency chỉ xử lý retry; đối soát theo invoice code và webhook tới invoice `void` vẫn tuân theo D33.

## 14. Batch / Bulk Operations — Thao tác hàng loạt

Không có generic endpoint `/bulk` trong API v1. P2-06 chỉ được thêm batch action khi user flow thật sự cần, action phải có tên rõ, giới hạn số item và response kết quả cho từng item.

Đặc biệt, sinh hóa đơn là **theo từng phòng**, không phải batch endpoint (D33). Client không được gửi array vào endpoint dành cho một resource đơn lẻ.

## Checklist cho P2-06

Mỗi operation trong OpenAPI cần khai báo: method/path, request schema, response envelope, lỗi chung, access class/auth, ownership rule, pagination/filter/sort nếu là list, lifecycle precondition nếu là action, và `Idempotency-Key` nếu action có ảnh hưởng payment.

## Review còn lại

- **BE:** xác nhận DTO/exception filter NestJS, JWT lifetime/refresh, giới hạn upload, rate limit và tên entity sau khi P2-04 chốt.
- **PM:** xác nhận public-field boundary, tenant-lock exception và không có quy ước nào làm rộng MVP.
- **P2-04:** đối chiếu ERD cuối trước khi P2-06 freeze; tài liệu này không tự giải quyết các khác biệt schema đang mở.
