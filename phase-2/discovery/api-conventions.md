# Quy ước API — v1

> **Trạng thái:** Bản nháp, chờ BE và PM review  
> **Owner:** BE  
> **Đầu vào:** P2-04, user flow, `database-design.md`, `utility-billing-calculations.md`, các quyết định D13, D18, D29, D33–D37
> **Đầu ra sử dụng:** `openapi.yaml` trong `pbl6-backend` (P2-06)  
> **Cập nhật:** 2026-09-25

## Phạm vi

Tài liệu này quy định pattern chung cho REST API NestJS dùng bởi Web React và Mobile Kotlin. Tài liệu **không thêm endpoint, entity hay feature mới**; P2-06 sẽ thiết kế từng endpoint theo các quy ước này.

Các quy ước phải giữ nghiệp vụ đã chốt: tenant không bắt buộc có tài khoản (D29), hợp đồng chỉ có giá trị trong app khi upload file ký tay (D18), hóa đơn sinh theo từng phòng, hỗ trợ thanh toán một phần và void thay vì xóa (D33, D37), và số công tơ luôn có ảnh chứng cứ kể cả khi hiệu chỉnh số OCR (D34, D35).

> **Nguồn nghiệp vụ thay thế:** `phase-1/business-rules.md` chưa từng được publish nên không dùng làm input cho P2. P2-06 phải đối chiếu `requirement.md`, `phase-0/feature-list.md`, decision logs Phase 0/1, `phase-1/discovery/user_flow/`, `phase-1/discovery/database-design.md` và `phase-1/discovery/utility-billing-calculations.md`. Đây là nguồn thay thế khi viết P2-06; các reference `business-rules.md` còn lại cần được PM cập nhật theo danh sách này.

## 1. Response Wrapper Format — Định dạng phản hồi chuẩn

Mọi response đều phải trả **HTTP status code**. Ngoại trừ `204 No Content`, response tải file, và response xác nhận webhook bên thứ ba, response JSON thành công có field `statusCode`, `code` và `data`; response lỗi JSON chỉ có `statusCode` và `code`.

Ba ngoại lệ không dùng JSON wrapper vì: `204` theo HTTP không được có body; response tải file là binary stream cần `Content-Type` và `Content-Disposition`; webhook acknowledgement chỉ trả status/body đúng contract của provider (thường `200` hoặc `204`). Vì vậy chúng không có field JSON `statusCode`/`code`/`data`, nhưng vẫn có HTTP status code.

- `statusCode` trùng với HTTP status code.
- Với success response, `code` là mã thành công nghiệp vụ ổn định do lập trình viên đặt theo action (ví dụ `ROOM_FETCHED`, `INVOICE_CREATED`). Mã được viết in hoa, snake_case và giữ nguyên đúng như OpenAPI đã công bố.
- Với error response, `code` là mã lỗi nghiệp vụ ổn định để client rẽ nhánh. Mã được viết in hoa và giữ nguyên đúng như OpenAPI đã công bố; có thể có khoảng trắng và dấu nháy đơn khi cần, ví dụ `CAN'T DELETE`.
- `data` chứa một resource, mảng resource hoặc kết quả action khi thành công; response lỗi không có `data`, `message` hay `details`.
- Response list thành công có thêm `pagination`.
- `201 Created` phải có header `Location` trỏ đến resource mới. `200 OK` dùng cho đọc/cập nhật/action đồng bộ. `202 Accepted` chỉ dùng khi OpenAPI mô tả rõ action bất đồng bộ và cách client theo dõi kết quả.

Ví dụ response một resource:

```json
{
  "statusCode": 200,
  "code": "ROOM_FETCHED",
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
  "code": "VALIDATION FAILED"
}
```

Client xử lý luồng chung bằng HTTP `statusCode` và `code`. Không trả `message`, `details`, stack trace, SQL, credential, prompt AI hay dữ liệu CCCD trong response lỗi.

## 2. Pagination — Phân trang

Collection endpoint có thể dùng một trong hai strategy: **offset** cho màn hình cần số trang/tổng bản ghi rõ ràng (dashboard, trang quản trị), hoặc **cursor** cho danh sách lớn hay có dữ liệu thay đổi liên tục. Mỗi operation trong OpenAPI phải chọn và khai báo **một** strategy; không có query param chung để client đổi strategy trên cùng endpoint.

Mọi collection response có `pagination.type` làm discriminator. `pageSize` là số nguyên dương, mặc định `20`, tối đa `100` cho cả hai strategy. Giá trị phân trang sai hoặc trộn query param giữa hai strategy trả `422` với `code: VALIDATION FAILED`; cursor không hợp lệ dùng `code: INVALID CURSOR`.

### Offset pagination

| Query param | Quy ước | Mặc định / giới hạn |
|---|---|---|
| `pageNo` | Số nguyên dương, bắt đầu từ 1 | `1` |
| `pageSize` | Số nguyên dương | `20`, tối đa `100` |

```json
{
  "statusCode": 200,
  "code": "ROOMS_FETCHED",
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
    "type": "offset",
    "pageNo": 1,
    "pageSize": 20,
    "totalItems": 2,
    "totalPages": 1,
    "hasNextPage": false,
    "hasPreviousPage": false
  }
}
```

`totalItems` và `totalPages` bắt buộc có với offset pagination. `hasNextPage` và `hasPreviousPage` được backend tính từ `pageNo`, `pageSize` và `totalItems`; client không tự suy luận. Không tự âm thầm sửa `pageNo` hoặc `pageSize` sai về giá trị mặc định.

### Cursor pagination

| Query param | Quy ước | Mặc định / giới hạn |
|---|---|---|
| `cursor` | Opaque cursor do server cấp từ `pagination.nextCursor` của response trước; không parse, sửa hoặc tự tạo ở client | Không gửi ở trang đầu |
| `pageSize` | Số nguyên dương | `20`, tối đa `100` |

```json
{
  "statusCode": 200,
  "code": "NOTIFICATIONS_FETCHED",
  "data": [
    {
      "id": "7d7fbbac-7701-4143-b5c6-0b62620356e0",
      "title": "Hóa đơn tháng 09/2026 đã được phát hành.",
      "createdAt": "2026-09-15T03:00:00.000Z"
    }
  ],
  "pagination": {
    "type": "cursor",
    "pageSize": 20,
    "nextCursor": "eyJjcmVhdGVkQXQiOiIyMDI2LTA5LTE1VDAzOjAwOjAwLjAwMFoiLCJpZCI6IjdkN2ZiYmFjLTc3MDEtNDE0My1iNWM2LTBiNjI2MjAzNTZlMCJ9",
    "hasNextPage": true
  }
}
```

- Cursor pagination chỉ đi về phía trước. Khi không còn trang sau, response trả `hasNextPage: false` và `nextCursor: null`.
- Cursor là opaque và phải bao gồm đủ thông tin sắp xếp để không lặp hoặc bỏ sót record. Cursor hết hạn, không hợp lệ, sai filter/sort hoặc thuộc actor khác đều trả `422` với `code: INVALID CURSOR`.
- Endpoint cursor phải có thứ tự ổn định và unique: OpenAPI khai báo sort cố định hoặc tập field sort được phép; backend luôn thêm `id` làm tie-breaker cuối. Không trả `totalItems` hoặc `totalPages` vì việc đếm làm mất lợi thế hiệu năng của cursor.
- Khi client thay filter, sort hoặc `pageSize`, client phải bỏ cursor cũ và bắt đầu lại từ trang đầu.

## 3. Error Codes — Mã lỗi

Mọi error response JSON dùng cấu trúc sau (không có `data`):

```json
{
  "statusCode": 422,
  "code": "VALIDATION FAILED"
}
```

- `statusCode` là HTTP status code.
- `code` là mã lỗi cụ thể, bắt buộc với mọi error response JSON và ổn định giữa các phiên bản không breaking. Client có thể dùng `code` để hiển thị hoặc rẽ nhánh theo lỗi nghiệp vụ; mỗi operation trong OpenAPI phải khai báo các giá trị `code` có thể trả về. Ví dụ `CAN'T DELETE` dùng khi resource không thể bị xóa do trạng thái, liên kết hoặc quy tắc retention; response này dùng HTTP `409`.
- Không trả `message`, `details`, `rejectedValue`, stack trace, SQL, credential, prompt AI hay dữ liệu CCCD trong error response.

Ví dụ lỗi không thể xóa resource:

```json
{
  "statusCode": 409,
  "code": "CAN'T DELETE"
}
```

| HTTP status | Error `code` ví dụ | Khi dùng |
|---|---|---|
| `200` | — | Đọc, cập nhật hoặc action đồng bộ thành công |
| `201` | — | Tạo resource thành công; kèm `Location` |
| `202` | — | Đã nhận action bất đồng bộ; OpenAPI nêu cách theo dõi |
| `204` | — | Thành công nhưng không có body |
| `400` | `BAD REQUEST` | JSON, query, header hoặc media type sai cú pháp |
| `401` | `INVALID TOKEN` | Thiếu, hết hạn hoặc token không hợp lệ |
| `403` | `FORBIDDEN` | Đã xác thực nhưng không có quyền thực hiện action |
| `404` | `NOT FOUND` | Resource không tồn tại hoặc bị ẩn vì ownership |
| `409` | `CONFLICT`, `CAN'T DELETE`, `IDEMPOTENCY KEY REUSED` | Trùng resource, conflict state, không thể xóa resource, hoặc tái dùng idempotency key với payload khác |
| `422` | `VALIDATION FAILED`, `INVALID CURSOR` | Request đúng cú pháp nhưng lỗi validation, cursor không hợp lệ hoặc vi phạm rule nghiệp vụ |
| `429` | `RATE LIMIT EXCEEDED` | Vượt rate limit |
| `500` | `INTERNAL ERROR` | Lỗi không mong đợi phía server |

Validation dùng `422` và `code: VALIDATION FAILED`; response không trả chi tiết theo field. Rule nghiệp vụ không gắn với một field cũng dùng `422`, với `code` được OpenAPI của operation quy định.

## 4. Authentication & Authorization — Xác thực và phân quyền

- Endpoint bảo vệ dùng `Authorization: Bearer <access-token>` và OpenAPI scheme `http`/`bearer`, `bearerFormat: JWT`.
- JWT chỉ chứa: `sub` (UUID user), `role` (`tenant`, `landlord`, `admin`), `iat`, `exp`. Không đưa mật khẩu, CCCD, URL media hoặc profile thay đổi thường xuyên vào token.
- **Access token TTL là 15 phút.** Khi hết hạn, client gọi `POST /api/v1/auth/refresh` một lần trước khi yêu cầu đăng nhập lại; token access không được lưu lâu dài ở browser storage.
- **Refresh strategy:** login và refresh tạo refresh token opaque ngẫu nhiên; token có lifetime cố định **30 ngày kể từ lúc login**. Backend chỉ lưu hash của token, session/family và thời điểm hết hạn. `POST /auth/refresh` chỉ nhận refresh token qua cookie, vô hiệu token cũ ngay khi dùng và cấp access token + refresh token mới, nhưng không kéo dài mốc hết hạn 30 ngày ban đầu.
- Refresh token được gửi trong cookie `HttpOnly`, `Secure`, `SameSite=Lax`, `Path=/api/v1/auth`; không trả trong JSON, log hoặc error response. Mobile lưu cookie này qua cookie jar được mã hóa của ứng dụng; access token chỉ giữ trong memory hoặc secure storage ngắn hạn.
- Dùng lại refresh token đã bị rotate, token hết hạn hoặc session đã revoke đều trả `401`; backend revoke toàn bộ refresh-token family và client phải xóa session cục bộ rồi đăng nhập lại. Logout revoke refresh session hiện tại và xóa cookie.
- `PUBLIC` là mức truy cập endpoint, **không** là role lưu trong database. Endpoint public chỉ trả field an toàn của phòng/BĐS đã được duyệt.
- Mỗi user chỉ có đúng một role bất biến theo D13. Không có role hierarchy kế thừa quyền: quyền là tổ hợp của role, action và ownership.
- RBAC luôn đi kèm ownership check: landlord chỉ thao tác dữ liệu thuộc quyền quản lý; tenant chỉ xem/thanh toán hợp đồng liên kết với mình; admin có quyền được khai báo rõ ở từng endpoint.
- Khi tenant bị khóa, quyền xem/thanh toán hợp đồng hiện tại vẫn phải tuân theo user flow; không dùng role guard chung để chặn nhầm quyền này.
- `/me` là **ngoại lệ tự phục vụ duy nhất** (profile, bảo mật, tuỳ biến cá nhân) và **không bao giờ** trỏ tới tài nguyên của người dùng khác.
- Quyền truy cập bản ghi `Media` **kế thừa từ tài nguyên cha** qua `ownerType`/`ownerId`; do đó các thao tác trên Media có cột quyền **để trống có chủ ý**, và server nạp rule của tài nguyên cha thay vì so sánh role.

## 5. Request Validation — Quy ước validate request

NestJS DTO validation là nguồn kiểm tra phía server. Từ chối field JSON không khai báo; chỉ transform field đã định kiểu; không ép giá trị sai thành giá trị hợp lệ.

| Dữ liệu | Quy ước |
|---|---|
| Bắt buộc / nullable | Mọi field đã khai báo trong JSON request body phải xuất hiện. Field bắt buộc không được `null`; field nullable không có giá trị phải gửi rõ là `null`, không được thiếu field. |
| Chuỗi | Trim khoảng trắng đầu/cuối nếu khoảng trắng không có nghĩa; không dùng chuỗi rỗng để biểu diễn không có giá trị — dùng `null`. Min/max length nằm trong OpenAPI endpoint. |
| Date | `YYYY-MM-DD`; không dùng format theo locale. Billing period là `YYYY-MM`. |
| Timestamp | ISO 8601 UTC với hậu tố `Z`, ví dụ `2026-09-15T03:00:00.000Z`. |
| Tiền | **API contract:** mọi giá trị tiền/đơn giá VND là JSON integer, ví dụ `"rentPrice": 3500000`; không nhận số lẻ, float hoặc chuỗi tiền. **Dấu âm:** chỉ `otherFees[].amount` được âm, với nghĩa giảm trừ/miễn giảm (ví dụ `-100000`). Tiền thuê, tiền cọc, đơn giá, payment và `totalAmount` phải `>= 0`; nếu giảm trừ làm tổng hóa đơn âm thì backend từ chối tạo invoice, tổng bằng `0` vẫn hợp lệ (D33). **Tính toán:** client không tự tính hoặc làm tròn tiền. Backend dùng PostgreSQL `numeric`/Decimal, không dùng JavaScript float/double, rồi trả kết quả cuối cùng là VND nguyên. Quy tắc tính và làm tròn invoice theo `utility-billing-calculations.md`. |
| Số đo thập phân | Chỉ số công tơ, diện tích và số lượng thập phân dùng JSON string, ví dụ `"1380.5"`, `"18.5"`, để không mất chính xác qua JavaScript/Kotlin. |
| Số điện thoại | Chấp nhận `0xxxxxxxxx` hoặc `+84xxxxxxxxx`; chuẩn hóa bằng cách đổi tiền tố `+84` thành `0`, sau đó lưu và trả về dạng `0xxxxxxxxx` (ví dụ `+84912345678` → `0912345678`). Endpoint public không trả số điện thoại. |
| Boolean / enum | Dùng JSON boolean và enum đã khai báo, không dùng `0`/`1` hay display label. |

Upload file dùng quy trình **2 bước presign**, **không** dùng `multipart/form-data` từ client; backend **không bao giờ nhận file bytes qua multipart**. Các bước: (1) `POST /media/presign-upload` — body gồm `ownerType`, `ownerId`, `purpose`, `fileName`, `contentType`, `size`; response trả `mediaId`, `uploadUrl` (signed URL) và `requiredHeaders`; (2) client `PUT` file thẳng lên storage với đúng header, sau đó gọi `POST /media/{mediaId}/complete-upload` để backend chốt bản ghi `Media`. MVP chỉ chấp nhận `image/jpeg`, `image/png`, `image/webp`, `application/pdf`; OpenAPI từng endpoint phải nêu giới hạn kích thước. Response trả resource `Media` theo envelope chuẩn; **không lộ storage path, URL public vĩnh viễn hay media nhạy cảm**.

## 6. Naming Conventions — Quy ước đặt tên

| Thành phần | Quy ước | Ví dụ |
|---|---|---|
| Base path | `/api/v1` | `/api/v1/rooms` |
| Collection path | Danh từ số nhiều, lowercase kebab-case | `/match-requests` |
| Resource path | UUID ở path param camelCase | `/rooms/{roomId}` |
| CRUD path | Không dùng động từ | `POST /rooms`, `PATCH /rooms/{roomId}` |
| Domain action | Động từ rõ ràng ở subpath khi không phải CRUD | `POST /invoices/issue-invoice`, `POST /media/{mediaId}/complete-upload`, `POST /payments/record-cash-payment` |
| JSON field / query param | `camelCase` | `createdAt`, `buildingId` |
| Database field | Không expose trực tiếp | `created_at` → `createdAt` |
| Enum | lowercase snake_case | `pending` |
| Header custom | Pascal-Case có dấu gạch nối | `Idempotency-Key`, `X-Request-Id` |

UUID dùng dạng canonical lowercase. URL không có trailing slash. Resource không tồn tại và resource bị ẩn do ownership đều trả `404` để không lộ dữ liệu.

**Lưu ý về domain action:** action cấp collection (không có parent id trong path) nhận danh sách ID trong body (ví dụ `POST /invoices/issue-invoice` nhận `invoiceIds[]`). **Endpoint generic `/bulk` hoặc `/batch` bị cấm** — mọi thao tác nhiều bản ghi phải mang tên nghiệp vụ tường minh.

## 7. Versioning & Base URL — Phiên bản và URL gốc

- Base URL phụ thuộc environment; client không hard-code host. Path chuẩn là `/api/v1`.
- Thay đổi breaking dùng major path mới, ví dụ `/api/v2`. Thêm hoặc xóa field trong JSON request/response body là breaking change vì client luôn nhận và gửi đủ field theo schema.
- Endpoint tương lai bị deprecate trả `Deprecation: true`, `Sunset` và `Link` tới endpoint thay thế (nếu có). Chỉ được xóa sau migration period được duyệt hoặc khi chuyển major version.
- API production dùng HTTPS. JSON mặc định UTF-8, trừ `multipart/form-data` và response tải file đã khai báo.

## 8. Rate Limiting — Giới hạn tần suất

Con số cụ thể là **cấu hình deployment** (không hard-code trong OpenAPI); BE chịu trách nhiệm quyết định và ghi vào `infrastructure/rate-limit.md` trước khi P2-06 freeze.

| Nhóm endpoint | Hạn mức tham chiếu (có thể điều chỉnh) |
|---|---|
| Auth (login, register, refresh) | 10 req / phút / IP |
| Upload (ảnh, hợp đồng) | 20 req / phút / user |
| Payment khởi tạo | 5 req / phút / user |
| Public search / listing | 60 req / phút / IP |
| Các endpoint khác (authenticated) | 120 req / phút / user |

- Policy có thể khác nhau cho từng nhóm (auth, upload, payment, public search).
- Khi áp dụng, response trả thêm header: `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`.
- Khi vượt hạn mức: `429 Too Many Requests`, header `Retry-After` và error envelope chuẩn.

> **Deferred:** Con số trên là tham chiếu ban đầu. BE phải xác nhận và cập nhật trước P2-06 freeze dựa trên hạ tầng thực tế.

## 9. Timestamp & Timezone — Thời gian và múi giờ

- Mọi instant lưu và trả về là UTC ISO 8601 (`createdAt`, `updatedAt`, `issuedAt`...).
- Ngày không kèm thời gian (`startDate`, `endDate`, `dueDate`) dùng `YYYY-MM-DD`.
- Tính kỳ hóa đơn, ngày đến hạn và quy tắc theo lịch dùng `Asia/Ho_Chi_Minh`. Client không tự tính ngày billing từ timezone của thiết bị.
- `period` luôn là tháng dương lịch `YYYY-MM`.

## 10. Null Fields — Field `null`

- **JSON response:** mọi field đã khai báo trong response schema phải xuất hiện. Khi field chưa có giá trị hoặc không áp dụng, trả rõ `null`; không bỏ field và không dùng chuỗi rỗng thay cho `null`. Ví dụ invoice `pending` trả `issuedAt: null`; hợp đồng không liên kết tenant account theo D29 trả `tenantId: null`.
- **JSON request:** mọi field đã khai báo trong request schema phải xuất hiện. Field không có giá trị gửi `null`; không gửi chuỗi rỗng hoặc bỏ field. OpenAPI phải nêu rõ field nào nullable; `null` cho field non-nullable trả `422` với `code: VALIDATION FAILED`.
- Với `PATCH`, client gửi toàn bộ field có thể chỉnh sửa. `null` nghĩa là xóa/clear giá trị khi rule nghiệp vụ cho phép; nếu field không cho phép clear, backend trả `422`. Client muốn giữ giá trị phải gửi lại giá trị hiện tại, không dùng field thiếu để biểu thị "không thay đổi".
- Quy tắc này chỉ áp dụng cho JSON body và JSON response. Query/path/header không biểu diễn được JSON `null`: tham số tùy chọn như cursor trang đầu có thể không gửi; OpenAPI nêu rõ điều đó.
- `false`, `0` và `[]` là giá trị hợp lệ, không thay bằng `null`. Chỉ dùng `null` khi thật sự không có giá trị.

## 11. Filtering & Sorting — Lọc và sắp xếp

Collection endpoint dùng ba query param chung `filter`, `sort` và `order`. Mỗi endpoint chỉ khai báo các filter và field sort được phép trong OpenAPI.

| Query param | Quy ước | Default |
|---|---|---|
| `filter` | Object có field được endpoint cho phép, serialized theo OpenAPI `deepObject`; ví dụ `filter[status]=available` | Không filter |
| `sort` | **Một** field từ whitelist của endpoint; ví dụ `createdAt` | Field mặc định do endpoint khai báo, ví dụ `createdAt` |
| `order` | `asc` hoặc `desc` | `asc` |
| `format` | **Chỉ dùng trên collection `GET`** để tải file: `xlsx`, `csv`, `pdf`, `json`; **không được khai báo trên resource-detail `GET`** (detail luôn trả JSON) | `json`, tức response JSON kèm `pagination` |

- Filter dùng `deepObject`: `GET /rooms?filter[status]=available&filter[buildingId]=<uuid>&sort=rentPrice&order=desc`. Multi-value enum filter dùng dấu phẩy, ví dụ `filter[invoiceStatus]=pending,issued`. **D39:** không có `overdue`/`partially_paid` trong enum hóa đơn — công nợ được tính ở server từ Σ `Payment` success (`GET /debts` cũng đã bỏ, xem D53).
- Client chỉ được gửi **một** `sort`. `sort` lặp lại hoặc chứa dấu phẩy trả `422` với `code: VALIDATION FAILED`; server không tự chọn field đầu tiên.
- `order` chỉ áp dụng cho `sort`. Gửi `order` mà không có `sort` dùng default sort của endpoint; order hoặc field sort không nằm trong whitelist trả `422` với `code: VALIDATION FAILED`.
- OpenAPI từng endpoint phải khai báo field filter, whitelist `sort`, default sort, default order và pagination strategy. Backend có thể thêm `id:asc` làm tie-breaker nội bộ để thứ tự ổn định qua các trang; đây không phải multi-field sort do client yêu cầu.
- **Export** không có endpoint riêng. Client gọi chính collection `GET` kèm `format`; `json` (hoặc không gửi) trả response chuẩn kèm `pagination`, còn `xlsx`/`csv`/`pdf` trả file stream với `Content-Type` và `Content-Disposition` và không có JSON wrapper. `format` không hợp lệ trả `422` với `code: VALIDATION FAILED`. Endpoint không có ý định export thì không khai báo `format`. **Endpoint xuất riêng (`*/export`) bị cấm**, bao gồm cả route tải một tài liệu đơn lẻ — tài liệu đơn lẻ lấy bằng cách filter collection, còn route detail luôn trả JSON.

## 12. Soft Delete vs Hard Delete — Xóa mềm và xóa cứng

Không cho client hard-delete dữ liệu tài chính, pháp lý, audit hoặc bằng chứng. **Soft delete** nghĩa là record vẫn được giữ để audit/retention nhưng bị ẩn khỏi kết quả thông thường; domain biểu diễn bằng cờ `is_deleted` trong Base Entity (xem `phase-1/discovery/database-design.md` §2.0) — **không có cột `deletedAt`** và không cần migration thêm cột cho flag này.

| Nhóm resource | Quy ước v1 |
|---|---|
| User | **Soft delete** qua admin `DELETE /users/{userId}` (không có self-service delete). |
| Building | **Soft delete** qua `DELETE /buildings/{buildingId}`. |
| Media | **Soft delete** qua `DELETE /media/{mediaId}` cho media của chính người gọi. |
| Invoice | **Soft delete** qua action `cancel`; giữ snapshot, payment và liên kết invoice thay thế (D33, D37). |
| Payment, AuditLog, MeterReading, Contract, ContractMember, IssueReport, Message, Conversation | **Soft delete / retention**; không có public `DELETE`. Các bảng này **không bao giờ bị cascade** khi User/Building xóa mềm — giữ nguyên cho truy vết tài chính/pháp lý/audit, chỉ ẩn khỏi list thông thường. |
| Room, RatePolicy, BillingSetting, RoommateProfile, Notification | **Soft delete** qua lifecycle action như `terminate`, `deactivate`, `close`, `cancel`, `leave`, `dismiss`. `MatchRequest` nằm ngoài danh sách: enum status có `pending`, `accepted`, `rejected`, `withdrawn`, và `withdrawn` là một trạng thái nghiệp vụ chứ không phải xoá mềm — bản ghi được giữ nguyên. Xem D50. |
| LandlordProfile, NotificationPreference | **Soft delete / retention**; không có public hard delete. |
| ConversationMember, MessageMention và các bảng join/snapshot nội bộ | **Soft delete / retention** nội bộ; không có endpoint CRUD/`DELETE` trực tiếp. |
| FavoriteRoom, PushDevice | User được xóa record của chính mình; có thể **hard delete** vì không mang giá trị tài chính/pháp lý/audit. |

### Phạm vi cascade (cascade boundary)

Khi `DELETE /users/{userId}` hoặc `DELETE /buildings/{buildingId}` đặt `is_deleted = true`, cờ này **chỉ cascade sang các con trực tiếp mang tính vận hành** (ví dụ: `LandlordProfile`, `PushDevice`, `NotificationPreference`, `RoommateProfile`, `FavoriteRoom`, `MatchRequest`, `Room`, `RatePolicy`, `BillingSetting`; **không** có `VietQrReceiverConfig` vì D39 đã bỏ bảng này). **Các bảng tài chính/pháp lý/audit sau đây KHÔNG bị cascade**: `Contract`, `ContractMember`, `Invoice`, `Payment`, `MeterReading`, `IssueReport`, `Message`, `Conversation`, `AuditLog`. Chúng giữ nguyên dữ liệu để tra cứu và chỉ bị ẩn khỏi danh sách khi tài nguyên cha đã xóa mềm.

Database table không tự động tương đương một public API resource. Với mọi bảng/resource chưa liệt kê, mặc định **soft delete** và không expose `DELETE`; P2-06 chỉ thêm lifecycle action sau khi user flow, ownership, retention và audit requirement được xác định rõ.

## 13. Idempotency Key — Chống tạo thanh toán trùng

`POST` có thể tạo hoặc ghi nhận payment bắt buộc có header `Idempotency-Key`. Header là UUID do client sinh, áp dụng tối thiểu cho khởi tạo thanh toán và landlord xác nhận thu tiền mặt.

- Server lưu key, actor đã xác thực, request fingerprint và response kết quả tối thiểu 24 giờ.
- Gửi lại cùng key và cùng request trả lại nguyên status/body ban đầu.
- Dùng lại cùng key với payload khác trả `409` và `code: IDEMPOTENCY KEY REUSED`; không xử lý request mới.
- Webhook payment dùng provider event/transaction ID đã ký để deduplicate và verify signature; không tin idempotency key do client gửi.
- Idempotency chỉ xử lý retry; đối soát theo `Invoice.code` (không theo amount) và webhook tới invoice `void` vẫn tuân theo D33⑤ + D39 (ghi `Payment` + cờ `needs_review`).
- **Business-named bulk actions** `POST /invoices/issue-invoice` và `POST /invoices/send-reminder` **cũng bắt buộc `Idempotency-Key`**, cùng retention 24h và hành vi `409 IDEMPOTENCY KEY REUSED` khi tái dùng key với payload khác. Lỗi nghiệp vụ từng bản ghi được trả **bên trong response** (trong `failed[]`) chứ không phải là HTTP error.

## 14. Batch / Bulk Operations — Thao tác hàng loạt

### Quy tắc chung

Luật chung vẫn là **không có bulk/import generic** (`/bulk`, `/batch`), **sinh hóa đơn theo từng phòng** (D33), và **không dùng bulk** cho: payment, hợp đồng đã ký, chốt số công tơ/OCR, evidence, thay đổi trạng thái property, khóa/mở khóa user. Import ngoài scope MVP (D19).

### Hai bulk action có tên nghiệp vụ (v1)

API v1 có **chính xác hai** bulk action, đều mang tên nghiệp vụ tường minh (không dùng `/bulk` hay `/batch`):

1. `POST /invoices/issue-invoice` — phát hành nhiều hóa đơn chờ
2. `POST /invoices/send-reminder` — nhắc **ngày thu dự kiến** cho nhiều hóa đơn (theo `BillingSetting.remind_day`). **D39:** không phải "nhắc quá hạn" — không tồn tại `overdue`/`due_date`; đây chỉ là nhắc một lần, không block, không ghi trạng thái.

Cả hai tuân theo pattern sau (tham chiếu quyết định **D43** trong `phase-2/discovery/decisions.md`):

- **Request:** body chứa mảng ID tường minh (`invoiceIds[]`), có **giới hạn số item do OpenAPI khai báo** (item cap); không hỗ trợ "all records".
- **Ownership/permission:** server kiểm tra quyền của **từng ID** riêng lẻ.
- **Response:** trả kết quả **theo từng bản ghi**, tách thành `succeeded[]` và `failed[]` (mỗi item gồm `id` + `code` nghiệp vụ). Một bản ghi lỗi **không làm fail cả lô** (partial success allowed — **không atomic**).
- **Counts:** response có trường đếm `requested`, `succeeded.length`, `failed.length`.
- **Idempotency:** bắt buộc header `Idempotency-Key` (xem §13), retention 24h, `409 IDEMPOTENCY KEY REUSED` khi tái dùng key với payload khác.
- **Cấm bulk** cho: signed contract, meter/OCR commit, evidence, property status change, user lock/unlock. Xem chi tiết D43.

Collection `GET` có filter/pagination và array là field thuộc **một** resource (ví dụ `otherFees[]` của invoice) không được xem là batch/bulk operation.

## Checklist cho P2-06

Mỗi operation trong OpenAPI cần khai báo: method/path, request schema, response envelope, lỗi chung, access class/auth, ownership rule, pagination strategy (`offset` hoặc `cursor`) cùng filter/sort/`format` nếu là list, header `Location` nếu trả `201 Created`, lifecycle precondition nếu là action, và `Idempotency-Key` nếu action có ảnh hưởng payment.

## Review còn lại

- **BE:** triển khai DTO/exception filter NestJS, JWT lifetime/refresh, giới hạn upload, rate limit và tên entity sau khi P2-04 chốt.
- **PM:** xác nhận public-field boundary, tenant-lock exception và không có quy ước nào làm rộng MVP.
- **P2-04:** đối chiếu ERD cuối trước khi P2-06 freeze; tài liệu này không tự giải quyết các khác biệt schema đang mở.
