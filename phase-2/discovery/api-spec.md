# PBL6 — Đặc tả API v1

**Trạng thái:** Bản nháp đã đối chiếu UI, chờ BE/FE/Mobile chốt các migration ở §14  
**Phụ trách:** Backend  
**Base path:** `/api/v1`  
**Client chính:** React Web (chủ nhà/admin, tenant responsive) và Kotlin Android (tenant, landlord-lite)  
**Nguồn đối chiếu:** `requirement(1).md`, các user flow, `database-design.md`, `api-conventions.md`, P2-06 và hai file UI Stitch Mobile/Web.  
**Giao diện:** Đã rà soát 77 màn Mobile và 105 màn Web. Bảng đối chiếu màn hình–API ở [§13](#13-đối-chiếu-ui-với-api).

---

## 1. Mục tiêu và phạm vi hợp đồng API

Đây là blueprint bằng Markdown để tạo `openapi.yaml` theo P2-06. Contract bao phủ: tìm phòng công khai, vận hành cho thuê, hợp đồng ký tay, ghi số/OCR (kể cả phiên ghi hàng loạt của chủ nhà), hóa đơn–thanh toán, chat cư dân/chat trực tiếp/chat ghép bạn, sự cố, ghép bạn, thông báo và quản trị.

Không bổ sung thuê ngắn hạn, ký điện tử/OTP, tương tác social feed, Zalo, import dữ liệu hàng loạt, gọi thoại/video-call hoặc tạo admin/đổi role. UI có các kênh chat nên API hỗ trợ chat phòng, chat tòa, chat trực tiếp chủ nhà và chat sau khi match thành công.

### 1.1 Nhãn quyền truy cập

| Nhãn | Ý nghĩa |
|---|---|
| `PUBLIC` | Không cần access token; chỉ trả dữ liệu an toàn của phòng/tòa đã duyệt. |
| `AUTH` | Đã xác thực; vẫn phải kiểm tra ownership ghi ở endpoint. |
| `TENANT` | Tenant đã xác thực; tenant bị khóa chỉ được gọi endpoint ghi rõ `locked allowed`. |
| `LANDLORD` | Chủ nhà đang hoạt động; ownership phải truy ra `landlordId`. |
| `ADMIN` | Tài khoản admin duy nhất được seed. |

Resource không tồn tại hoặc bị che do ownership đều trả `404 NOT FOUND`. Endpoint bảo vệ dùng `Authorization: Bearer <accessToken>`.

### 1.2 Phản hồi, dữ liệu và lỗi chung

Trừ `204`, tải file nhị phân và webhook, response JSON thành công theo envelope:

```json
{
  "statusCode": 200,
  "message": "Lấy thông tin phòng thành công.",
  "data": {}
}
```

Danh sách có thêm `pagination`; lỗi chỉ có `statusCode` và `code`, ví dụ `{"statusCode":422,"code":"VALIDATION FAILED"}`. `201` bắt buộc có header `Location`. Tiền là VND integer; chỉ số công tơ/diện tích là JSON string thập phân; timestamp dùng UTC ISO-8601, ngày dùng `YYYY-MM-DD`, kỳ hóa đơn dùng `YYYY-MM`.

Mọi field đã khai báo trong JSON body/response phải xuất hiện. Field nullable gửi `null`, không bỏ field. `PATCH` nhận đủ editable representation, không dùng partial merge.

| Kiểu danh sách | Query chuẩn | Dùng cho |
|---|---|---|
| Offset | `pageNo` (mặc định 1), `pageSize` (20, tối đa 100), `filter[...]`, `sort`, `order` | Admin, dashboard, quản lý phòng/tòa cần tổng số trang. |
| Cursor | `cursor`, `pageSize` (20, tối đa 100), `filter[...]`, `sort`, `order` | Tin nhắn, thông báo, tìm phòng công khai, feed ghép bạn. |

Sai phân trang/filter/sort trả `422 VALIDATION FAILED`; cursor sai hoặc hết hiệu lực trả `422 INVALID CURSOR`. Mọi endpoint bảo vệ có thể trả thêm `401 INVALID TOKEN`, `403 FORBIDDEN`, `404 NOT FOUND`, `429 RATE LIMIT EXCEEDED`, `500 INTERNAL ERROR`.

---

## 2. Xác thực, phiên và tài khoản

| Method và path | Quyền | Request | Response `data` | Quy tắc/lỗi bổ sung |
|---|---|---|---|---|
| `POST /auth/register` | PUBLIC | `RegisterRequest` | `AuthSession` (201) | Chỉ nhận role `tenant` hoặc `landlord`; role bất biến. Trùng email/phone: `409 CONFLICT`. Admin không đăng ký qua API. |
| `POST /auth/login` | PUBLIC | `LoginRequest` | `AuthSession` | Landlord/admin bị khóa: `403 ACCOUNT LOCKED`; tenant khóa nhận phiên hạn chế. Sai thông tin: `401 INVALID CREDENTIALS`. |
| `POST /auth/refresh` | Cookie | Không có JSON body | `AuthSession` | Rotate refresh cookie; token/family không hợp lệ: `401 INVALID TOKEN`. |
| `POST /auth/logout` | AUTH | Không body | 204 | Thu hồi refresh session hiện tại và xóa cookie. |
| `GET /auth/me` | AUTH | — | `CurrentUser` | Khởi động app và route theo role. |
| `POST /auth/password-reset-requests` | PUBLIC | `{ "email": "string" }` | `{ "accepted": true }` (202) | Màn Quên mật khẩu. Luôn trả 202 để không lộ tài khoản; gửi reset link/token ngoài băng. |
| `POST /auth/password-resets` | PUBLIC | `{ "token", "newPassword", "confirmPassword" }` | `{ "resetAt": "timestamp" }` | Màn Đặt lại mật khẩu. Token một lần, có hạn; thành công thu hồi mọi refresh session. Lỗi: `422 INVALID OR EXPIRED RESET TOKEN`. |
| `PUT /me/password` | AUTH | `ChangePasswordRequest` | `{ changedAt, revokedOtherSessions }` | Đổi mật khẩu khi đã đăng nhập; xác thực `currentPassword`, thu hồi mọi session khác nhưng giữ session hiện tại. Sai mật khẩu cũ: `401 INVALID CREDENTIALS`; policy/confirm sai: `422 VALIDATION FAILED`. |

`AuthSession = { accessToken, expiresIn, user: CurrentUser }`; refresh token không bao giờ nằm trong JSON. Refresh cookie là `HttpOnly`, `Secure`, `SameSite=Lax`, `Path=/api/v1/auth`; access token sống 15 phút, refresh family hết hạn cố định sau 30 ngày kể từ login.

`CurrentUser` gồm `id`, `fullName`, `email`, `phone`, `role`, `userStatus`, `lockedAt`, `createdAt`, `updatedAt`; không bao giờ chứa password hash. Tenant bị khóa chỉ được xem/thanh toán hợp đồng hiện tại, profile, thông báo và auth. Landlord bị khóa không được dùng portal chủ nhà.

### 2.1 Profile, thiết bị và Media

| Method và path | Quyền | Request | Response `data` | Quy tắc |
|---|---|---|---|---|
| `GET /me/profile` | AUTH | — | `UserProfile` | Hồ sơ của chính mình. |
| `PATCH /me/profile` | AUTH | `UpdateMyProfileRequest` | `UserProfile` | Sửa `fullName`, `email`, `phone`, `avatarMediaId`; role/status không sửa được. `avatarMediaId=null` gỡ avatar về mặc định. |
| `GET /me/sessions` | AUTH | Offset; `sort=lastActiveAt\|createdAt` | `AuthSessionDevice[]` | Danh sách session của chính mình; chỉ trả metadata thiết bị/IP đã che vị trí gần đúng, refresh token không bao giờ lộ. |
| `DELETE /me/sessions/{sessionId}` | AUTH | — | 204 | Thu hồi một session khác của chính mình; session hiện tại trả `409 CAN'T REVOKE CURRENT SESSION`, dùng logout thay thế. |
| `POST /me/sessions/revoke-others` | AUTH | `{ "currentPassword": "string" }` | `{ revokedCount }` | Thu hồi tất cả session khác sau khi xác thực mật khẩu hiện tại. |
| `GET /me/favorites` | TENANT | Offset list | `FavoriteRoom[]` | Danh sách đã lưu. |
| `POST /me/favorites` | TENANT | `{ "roomId": "uuid" }` | `FavoriteRoom` (201) | Phòng phải còn public/available; trùng: `409 CONFLICT`. |
| `DELETE /me/favorites/{roomId}` | TENANT | — | 204 | Chỉ xóa favorite của mình. |
| `GET /me/push-devices` | AUTH | Offset list | `PushDevice[]` | Không lộ token thiết bị cho người khác. |
| `POST /me/push-devices` | AUTH | `PushDeviceRequest` | `PushDevice` (201) | Upsert theo token; `platform=android|web`. |
| `DELETE /me/push-devices/{deviceId}` | AUTH | — | 204 | Thiết bị của chính mình. |
| `POST /media` | AUTH | `multipart/form-data`: `file`, `ownerType`, `ownerId`, `purpose` | `Media` (201) | Check quyền sửa resource cha; mặc định nhận jpeg/png/webp/pdf. Riêng `ownerType=issue_report`, `purpose=issue_evidence` nhận thêm `video/mp4` tối đa 25 MiB. |
| `GET /media/{mediaId}` | AUTH hoặc PUBLIC theo cha | — | Binary stream | Kiểm quyền theo resource cha; trả `Content-Type`, `Content-Disposition`, không dùng JSON envelope. |
| `DELETE /media/{mediaId}` | AUTH | — | 204 | Uploader/nguời có quyền sửa cha; signed contract/evidence bị retention: `409 CAN'T DELETE`. |

`UserProfile = CurrentUser + { avatar: Media|null, roommateProfile: RoommateProfile|null }`. `Media` có `id`, `ownerType`, `ownerId`, `purpose`, `fileType`, `mimeType`, `sizeBytes`, URL được ủy quyền tạm thời và timestamps; không lộ storage path.

`ChangePasswordRequest = { currentPassword, newPassword, confirmPassword }`. `AuthSessionDevice` gồm `id`, `deviceLabel`, `clientType`, `ipAddressMasked`, `approximateLocation`, `isCurrent`, `lastActiveAt`, `createdAt`; không trả refresh token, user-agent thô hay định vị chính xác.

---

## 3. Tìm phòng công khai và cổng người thuê

### 3.1 Tòa nhà, phòng và AI mô tả phòng

| Method và path | Quyền | Query/request | Response `data` | Phân trang và quy tắc |
|---|---|---|---|---|
| `GET /rooms` | PUBLIC | `filter[province]`, `filter[ward]`, `filter[minRentPrice]`, `filter[maxRentPrice]`, `filter[minArea]`, `filter[maxArea]`, `filter[amenities]`, `filter[genderPolicy]`, `filter[latitude]`, `filter[longitude]`, `filter[radiusKm]`; `sort=rentPrice\|area\|createdAt\|distance` | `PublicRoomCard[]` | Cursor; mặc định `createdAt desc`. Chỉ tòa approved, phòng available, landlord active. `distance` cần tọa độ. |
| `GET /rooms/{roomId}` | PUBLIC | — | `PublicRoomDetail` | Không trả hợp đồng, tenant, evidence hoặc thông tin riêng của chủ nhà. |
| `GET /buildings/{buildingId}` | PUBLIC | — | `PublicBuildingDetail` | Chỉ khi tòa approved và có ít nhất một phòng public. |
| `POST /ai/room-descriptions` | LANDLORD | `RoomDescriptionRequest` | `{ description, generatedBy }` | Tạo bản nháp; FE lưu qua room PATCH. `generatedBy=llm|rule_based`. |

`PublicRoomCard` gồm id, tòa, tên, diện tích, giá, tiện nghi, sức chứa, quy định giới tính, trạng thái, cover ảnh và địa chỉ/tọa độ thô. `PublicRoomDetail` bổ sung mô tả, gallery, tòa/địa chỉ/tọa độ và trường liên hệ đã được PM phê duyệt. Chính sách public phone còn mở ở §14.

### 3.2 Hợp đồng và hub “Phòng của tôi”

| Method và path | Quyền | Query | Response `data` | Quy tắc |
|---|---|---|---|---|
| `GET /me/contracts` | TENANT (locked allowed) | `filter[status]`, `sort=startDate\|updatedAt` | `TenantContractCard[]` | Offset; chỉ HĐ liên kết qua `tenantId` hoặc `ContractMember.tenantId` active. |
| `GET /contracts/{contractId}` | Tenant member / landlord sở hữu / ADMIN | — | `ContractDetail` | Tenant chỉ đọc. |
| `GET /contracts/{contractId}/members` | Tenant member / landlord sở hữu / ADMIN | — | `ContractMember[]` | Tenant chỉ đọc; CCCD chỉ chính chủ, landlord sở hữu hoặc admin xem media. |
| `GET /contracts/{contractId}/room-conversation` | Thành viên chat hiện tại/gần đây | — | `Conversation` | Route chat phòng; chat archive chỉ đọc. |

`ContractDetail` chứa room/landlord/tenant summary an toàn, `contractStatus`, cọc, tiền thuê, ngày bắt đầu/kết thúc, mô tả, số xe, `signedDocument` và timestamps; không nhúng dữ liệu CCCD/file nhạy cảm.

---

## 4. API vận hành bất động sản của chủ nhà

### 4.1 Tòa nhà và phòng

| Method và path | Quyền | Request | Response `data` | Điều kiện/lỗi |
|---|---|---|---|---|
| `GET /landlord/buildings` | LANDLORD | Offset; `filter[status]`, `filter[province]`, `sort=name\|createdAt\|buildingStatus` | `Building[]` | Tòa do mình sở hữu. |
| `POST /landlord/buildings` | LANDLORD | `CreateBuildingRequest` | `Building` (201) | Cần ít nhất một `ownershipProofMediaId`; tạo `pending`; thiếu bằng chứng: `422 OWNERSHIP PROOF REQUIRED`. |
| `GET /landlord/buildings/{buildingId}` | LANDLORD | — | `BuildingDetail` | Chỉ tòa của mình. |
| `PATCH /landlord/buildings/{buildingId}` | LANDLORD | `UpdateBuildingRequest` | `BuildingDetail` | Có thể nộp lại sau reject; quy tắc đổi địa chỉ/chứng từ approved cần chốt. |
| `GET /landlord/buildings/{buildingId}/rooms` | LANDLORD | Offset; `filter[status]`, `sort=name\|floorNumber\|rentPrice` | `Room[]` | Tòa của mình. |
| `GET /landlord/rooms` | LANDLORD | Offset; `filter[buildingId]`, `filter[status]`, `sort=createdAt\|rentPrice\|name` | `Room[]` | Màn quản lý phòng. |
| `POST /landlord/rooms` | LANDLORD | `CreateRoomRequest` | `Room` (201) | Tòa phải approved; nếu không: `422 BUILDING NOT APPROVED`. |
| `GET /landlord/rooms/{roomId}` | LANDLORD | — | `LandlordRoomDetail` | Phòng của mình. |
| `PATCH /landlord/rooms/{roomId}` | LANDLORD | `UpdateRoomRequest` | `LandlordRoomDetail` | Không cho trạng thái mâu thuẫn với HĐ active: `409 CONFLICT`. |
| `POST /landlord/rooms/{roomId}/mark-ready` | LANDLORD | `{ "note": "string|null" }` | `Room` | Chỉ sau checkout/dọn phòng; cần enum `cleaning_pending`. |

`CreateBuildingRequest`/`UpdateBuildingRequest`: `name`, `province`, `ward`, `address`, `latitude`, `longitude`, `ownershipProofMediaIds`.  
`CreateRoomRequest`/`UpdateRoomRequest`: `buildingId` (chỉ create), `floorNumber`, `name`, `description`, `area`, `amenities`, `maxOccupancy`, `genderPolicy`, `rentPrice`, `coverMediaId`, `galleryMediaIds`, `electricityPolicyId`, `waterPolicyId`.

### 4.2 Đơn giá dịch vụ, chu kỳ thanh toán và quét nợ

| Method và path | Quyền | Request/query | Response `data` | Ghi chú |
|---|---|---|---|---|
| `GET /landlord/rate-policies` | LANDLORD | Offset; `filter[type]`, `filter[scope]`, `filter[buildingId]`, `filter[roomId]`, `filter[active]`, `sort=createdAt\|name` | `RatePolicy[]` | Danh sách policy của mình, gồm policy mặc định cấp landlord. |
| `POST /landlord/rate-policies` | LANDLORD | `RatePolicyRequest` | `RatePolicy` (201) | Tạo active policy mới sẽ deactivate policy trùng cũ trong transaction + audit. |
| `GET /landlord/rate-policies/{policyId}` | LANDLORD | — | `RatePolicy` | — |
| `PATCH /landlord/rate-policies/{policyId}` | LANDLORD | `RatePolicyRequest` | `RatePolicy` | Ưu tiên tạo mới/deactivate cũ để giữ lịch sử. Đã dùng bởi invoice issued: `409 CAN'T EDIT POLICY`. |
| `POST /landlord/rate-policies/{policyId}/deactivate` | LANDLORD | — | `RatePolicy` | Kế thừa policy cấp trên. |
| `PUT /landlord/buildings/{buildingId}/rate-policies` | LANDLORD | `RatePolicyBatchRequest`, `Idempotency-Key` | `RatePolicy[]` | Lưu toàn bộ biểu phí của wizard tạo tòa trong một transaction: mỗi policy thay thế bằng version mới/deactivate version cũ, không tạo generic bulk endpoint. |
| `GET /landlord/billing-settings` | LANDLORD | `filter[buildingId]`, `filter[roomId]` | `BillingSetting[]` | Trả setting của mình và effective setting theo scope. |
| `PUT /landlord/billing-settings/default` | LANDLORD | `BillingSettingRequest` | `BillingSetting` | Default cấp landlord; cần migration DB ở OQ-05. |
| `PUT /landlord/buildings/{buildingId}/billing-settings` | LANDLORD | `BillingSettingRequest` | `BillingSetting` | Tòa của mình. |
| `PUT /landlord/rooms/{roomId}/billing-settings` | LANDLORD | `BillingSettingRequest` | `BillingSetting` | Phòng của mình. |
| `POST /landlord/billing-settings/{billingSettingId}/deactivate` | LANDLORD | — | `BillingSetting` | Quay về cấu hình kế thừa. |

`RatePolicyRequest = { scope, buildingId, roomId, name, type, rateKind, unitPrice, tierPresetCode, steps, isActive }`. `scope=landlord|building|room`; scope `landlord` có cả `buildingId` và `roomId` là `null`, hai scope còn lại có đúng một target id. `steps` chỉ dùng khi PM cho phép biểu giá tùy chỉnh; mặc định `tiered` phải dùng `tierPresetCode` do server seed để khớp D31. Các `rateKind` khác yêu cầu `unitPrice`.

`BillingSettingRequest = { readingCloseMode, readingCloseDay, dueRule, dueDays, dueDayOfNextMonth, preDueReminder, overdueReminder, botEnabled, isActive }`:

- `readingCloseMode=fixed_day|last_day`; `readingCloseDay` bắt buộc khi là `fixed_day` (1–28), còn lại `null`.
- `dueRule=days_after_issue|fixed_day_next_month`; `dueDays` hoặc `dueDayOfNextMonth` bắt buộc tương ứng (1–28), field còn lại là `null`.
- `preDueReminder = { enabled, daysBeforeDue, sendAt, channels }`; `overdueReminder = { enabled, firstSendAt, repeatEveryDays, channels }`; `channels` chỉ có `in_app|push` trong MVP.

Các field lịch được backend tính theo `Asia/Ho_Chi_Minh`; client không tự suy ra ngày đến hạn hay thời điểm gửi nhắc nợ.

| Method và path | Quyền | Request/query | Response `data` | Ghi chú UI |
|---|---|---|---|---|
| `GET /landlord/rate-policy-presets` | LANDLORD | `filter[type]=electricity|water` | `RatePolicyPreset[]` | Màn EVN chọn khung do server seed; không hard-code mức giá ở client. |
| `POST /landlord/rate-policies/quote` | LANDLORD | `RatePolicyQuoteRequest` | `RatePolicyQuote` | Mô phỏng tiền điện/nước/dịch vụ trong form; chỉ là preview, không ghi DB. |

`RatePolicyBatchRequest = { policies: RatePolicyRequest[] }`; mỗi item phải có `scope=building`, `buildingId` đúng với path và không có `roomId`. `tiered` dùng `tierPresetCode` theo D31, không nhận bảng giá tự do trong MVP. Request được validate toàn bộ trước khi ghi; lỗi một policy thì rollback cả lần lưu.

### 4.3 Tài khoản nhận tiền VietQR theo tòa

UI có màn chọn ngân hàng, nhập số tài khoản, xác minh tên chủ tài khoản, cấu hình chi nhánh/cú pháp nội dung và xem trước QR. Đây khác payment intent của invoice.

| Method và path | Quyền | Request | Response `data` | Quy tắc |
|---|---|---|---|---|
| `GET /landlord/buildings/{buildingId}/vietqr-config` | LANDLORD | — | `VietQrConfig|null` | Số tài khoản phải được che. |
| `POST /landlord/vietqr-account-verifications` | LANDLORD | `{ "bankCode", "accountNumber" }` | `VietQrAccountVerification` | Gọi adapter provider/NAPAS đã duyệt; trả tên xác minh, có thời hạn ngắn, không tạo khả năng nhận tiền. |
| `PUT /landlord/buildings/{buildingId}/vietqr-config` | LANDLORD | `VietQrConfigRequest` | `VietQrConfig` | Cần `verificationId` thành công, ghi audit. |
| `GET /landlord/buildings/{buildingId}/vietqr-preview` | LANDLORD | `amount`, `roomId`, `period` tùy chọn | `VietQrPreview` | Chỉ xem trước; QR hóa đơn thật lấy từ payment intent. |

`VietQrConfigRequest = { bankCode, accountNumber, verificationId, branchName, transferContentPattern }`. `VietQrConfig` trả id, tòa, bank, số đã che, tên chủ TK, chi nhánh, pattern, `verifiedAt`, `updatedAt`. Cần thêm entity/table `VietQrReceiverConfig`.

### 4.4 Dashboard chủ nhà

| Method và path | Quyền | Query | Response `data` | Mục đích |
|---|---|---|---|---|
| `GET /landlord/dashboard` | LANDLORD | `period` (mặc định tháng hiện tại), `buildingId` tùy chọn | `LandlordDashboard` | Card tổng quan, room map, doanh thu và công nợ. |
| `GET /landlord/analytics/revenue` | LANDLORD | `fromPeriod`, `toPeriod`, `buildingId`, `groupBy=month\|building` | `RevenueSeries[]` | Dữ liệu biểu đồ chi tiết. |

`LandlordDashboard = { period, roomCounts, expectedRevenue, collectedAmount, outstandingAmount, overdueInvoiceCount, rooms: RoomMapItem[] }`.

---

## 5. Hợp đồng, thành viên và trả phòng

| Method và path | Quyền | Request | Response `data` | Điều kiện/lifecycle |
|---|---|---|---|---|
| `GET /landlord/contracts` | LANDLORD | Offset; `filter[roomId]`, `filter[status]`, `filter[period]`, `sort=startDate\|endDate\|createdAt` | `Contract[]` | HĐ của mình. |
| `POST /landlord/contracts` | LANDLORD | `CreateContractRequest` | `ContractDetail` (201) | Phòng hợp lệ, chưa có HĐ active; tạo `draft`; tenant account là tùy chọn theo D29. |
| `PATCH /landlord/contracts/{contractId}` | LANDLORD | `UpdateContractRequest` | `ContractDetail` | Chỉ draft. |
| `GET /lease-templates` | LANDLORD | `filter[propertyType]` tùy chọn | `LeaseTemplate[]` | Danh mục mẫu hợp đồng seed hiển thị ở bước 2; trả `id`, `code`, `name`, `summary`, `pageCount`, `previewAvailable`. |
| `GET /lease-templates/{templateId}/preview` | LANDLORD | — | PDF binary | Xem trước mẫu chưa điền dữ liệu; không phải hợp đồng của tenant. |
| `POST /landlord/contracts/{contractId}/template` | LANDLORD | `{ "templateId": "uuid|null", "customTemplateMediaId": "uuid|null" }` | `ContractDetail` | Chọn đúng một mẫu seed hoặc file tự soạn; cả hai `null` dùng mẫu mặc định. |
| `GET /landlord/contracts/{contractId}/template-download` | LANDLORD | — | PDF/document binary | Xuất mẫu đã điền sẵn; engine/field cần chốt. |
| `POST /landlord/contracts/{contractId}/signed-document` | LANDLORD | `{ "mediaId": "uuid" }` | `ContractDetail` | File phải có purpose `contract_signed`; chỉ wet-sign. |
| `POST /landlord/contracts/{contractId}/activate` | LANDLORD | Không body | `ContractDetail` | Cần file ký; active HĐ, occupied room, tạo room chat và link tenant account trong một transaction. |
| `GET /landlord/contracts/{contractId}/members` | LANDLORD | — | `ContractMember[]` | — |
| `POST /landlord/contracts/{contractId}/members` | LANDLORD | `ContractMemberRequest` | `ContractMember` (201) | Add member + chat member nếu đã có account; đối chiếu phone. |
| `PATCH /landlord/contracts/{contractId}/members/{memberId}` | LANDLORD | `ContractMemberRequest` | `ContractMember` | Sửa contact/identity, chạy lại link account. |
| `POST /landlord/contracts/{contractId}/members/{memberId}/leave` | LANDLORD | `{ "leftAt": "YYYY-MM-DD" }` | `ContractMember` | Đánh dấu rời đi, dừng quyền chat mới nhưng giữ lịch sử. |
| `GET /landlord/contracts/{contractId}/members/export` | LANDLORD | `format=csv|xlsx` | Binary stream | Xuất danh sách cư dân của hợp đồng; không xuất CCCD/ảnh CCCD, chỉ các trường được landlord đang sở hữu quyền xem. |
| `POST /landlord/contracts/{contractId}/checkout/final-readings` | LANDLORD | `FinalMeterReadingsRequest` | `CheckoutProgress` | UI “Chốt chỉ số cuối kỳ”, giữ bằng chứng và tính tiêu thụ. |
| `POST /landlord/contracts/{contractId}/checkout/final-invoice` | LANDLORD | `{ "period", "note" }` | `InvoiceDetail` (201) | UI “Hóa đơn quyết toán”. |
| `POST /landlord/contracts/{contractId}/checkout/deposit-settlements` | LANDLORD | `DepositSettlementRequest`, `Idempotency-Key` | `DepositSettlement` (201) | UI hoàn/khấu trừ cọc, tạo chứng cứ payment liên kết. |
| `POST /landlord/contracts/{contractId}/checkout/complete` | LANDLORD | `{ "handoverNote": "string|null" }` | `CheckoutResult` | Sau các bước bắt buộc: terminate HĐ, archive chat, room thành `cleaning_pending`. |

`CreateContractRequest`/`UpdateContractRequest` gồm `roomId`, `tenantId`, `tenantName`, `tenantPhone`, `depositAmount`, `monthlyRent`, `startDate`, `endDate`, `description`, `vehicleCount`. Nếu `tenantId=null` thì tên và phone bắt buộc. `ContractMemberRequest = { tenantId, tenantName, tenantPhone, joinedAt, cccdFrontMediaId, cccdBackMediaId }`.

`FinalMeterReadingsRequest = { electricity: CreateMeterReadingRequest, water: CreateMeterReadingRequest, endDate }`. `DepositSettlementRequest = { originalDepositAmount, deductions: [{ name, amount }], refundAmount, method, note }`; `method` là `cash` hoặc cổng online được bật.

---

## 6. Ghi số công tơ, OCR và hóa đơn

### 6.1 Ghi số đơn lẻ

| Method và path | Quyền | Request/query | Response `data` | Quy tắc |
|---|---|---|---|---|
| `GET /landlord/rooms/{roomId}/meter-readings` | LANDLORD | Offset; `filter[type]`, `filter[period]`, `sort=period\|createdAt` | `MeterReading[]` | Phòng của mình. |
| `GET /contracts/{contractId}/meter-readings` | Tenant member / landlord sở hữu | `filter[type]`, `filter[period]` | `MeterReading[]` | Tenant chỉ đọc; locked tenant của HĐ hiện tại được phép. |
| `POST /landlord/rooms/{roomId}/meter-readings/ocr-preview` | LANDLORD | `{ "type", "period", "evidenceMediaId" }` | `OcrPreview` | OCR ảnh đã upload, chưa tạo reading chính thức. |
| `POST /landlord/rooms/{roomId}/meter-readings` | LANDLORD | `CreateMeterReadingRequest` | `MeterReading` (201) | Cần ít nhất một evidence media; unique room/type/period. |
| `POST /landlord/rooms/{roomId}/meter-readings/combined` | LANDLORD | `CombinedMeterReadingsRequest`, `Idempotency-Key` | `MeterReading[]` (201) | Form ghi đồng thời điện và nước; derive previous reading ở server, validate và ghi cả hai record atomically. |
| `POST /contracts/{contractId}/meter-readings/camera-submissions` | Tenant member | `TenantMeterCaptureRequest` | `MeterCaptureSubmission` (201) | Tenant chỉ chụp từ camera; landlord xác nhận thành canonical reading. |
| `POST /landlord/meter-capture-submissions/{submissionId}/confirm` | LANDLORD | `CreateMeterReadingRequest` | `MeterReading` (201) | Xác thực ảnh tenant gửi. |

`CreateMeterReadingRequest = { type, period, previousReading, currentReading, readingDate, isBaseline, evidenceMediaIds }`. `CombinedMeterReadingsRequest = { period, readingDate, electricity: { currentReading, evidenceMediaIds }, water: { currentReading, evidenceMediaIds }, note }`. Readings là string thập phân, `currentReading >= previousReading`. `OcrPreview = { currentReading, confidence, warnings }` chỉ là gợi ý đến khi chủ nhà xác nhận.

### 6.2 Phiên ghi chỉ số hàng loạt của chủ nhà

UI Web có 3 màn: chọn các phòng active của tòa, ghi/OCR/tự lưu từng phòng và tổng kết partial success. Đây là **workflow batch**, không phải `/bulk` generic: mỗi phòng vẫn tạo `MeterReading` và evidence riêng, atomic.

| Method và path | Quyền | Request/query | Response `data` | Hành vi UI |
|---|---|---|---|---|
| `POST /landlord/buildings/{buildingId}/meter-reading-batches` | LANDLORD | `{ "period": "YYYY-MM" }` | `MeterReadingBatch` (201) | Tạo/tiếp tục session draft cho phòng có HĐ active. Trùng session mở: `409 CONFLICT`. |
| `GET /landlord/meter-reading-batches/{batchId}` | LANDLORD | — | `MeterReadingBatchDetail` | Dashboard tiến độ, phòng đủ điều kiện, chỉ số cũ và vị trí resume. |
| `GET /landlord/meter-reading-batches/{batchId}/items` | LANDLORD | Offset; `filter[status]`, `filter[floorNumber]`, `sort=roomName\|floorNumber` | `MeterReadingBatchItem[]` | Danh sách phòng và trạng thái. |
| `PUT /landlord/meter-reading-batches/{batchId}/items/{itemId}` | LANDLORD | `BulkMeterReadingItemRequest` | `MeterReadingBatchItem` | Auto-save draft: OCR, sửa tay, ảnh và ghi chú. |
| `POST /landlord/meter-reading-batches/{batchId}/items/{itemId}/confirm` | LANDLORD | `BulkMeterReadingItemRequest` | `MeterReadingBatchItem` | Validate, tạo/cập nhật atomically hai meter reading của một phòng. |
| `POST /landlord/meter-reading-batches/{batchId}/items/{itemId}/skip` | LANDLORD | `{ "reason": "string" }` | `MeterReadingBatchItem` | Bắt buộc lý do; summary hiển thị phòng cần xử lý lại. |
| `POST /landlord/meter-reading-batches/{batchId}/complete` | LANDLORD | Không body | `MeterReadingBatchSummary` | Khóa session, trả số confirmed/skipped và tự tạo invoice pending **từng phòng** đủ điều kiện. |

`MeterReadingBatch = { id, buildingId, period, status: draft|in_progress|completed, totalRooms, confirmedRooms, skippedRooms, createdAt, updatedAt }`. `BulkMeterReadingItemRequest` chứa dữ liệu điện/nước, evidence, `ocrConfidence`, note. Cần entity persisted `MeterReadingBatch`/item vì bảng `MeterReading` hiện tại không đủ mô tả phiên.

### 6.3 Hóa đơn

| Method và path | Quyền | Request/query | Response `data` | Điều kiện/lỗi |
|---|---|---|---|---|
| `GET /landlord/invoices` | LANDLORD | Offset; `filter[roomId]`, `filter[buildingId]`, `filter[status]`, `filter[period]`, `sort=period\|totalAmount\|issuedAt` | `Invoice[]` | Hóa đơn của mình. |
| `GET /landlord/invoices/export` | LANDLORD | Cùng filter `/landlord/invoices`, `format=csv|xlsx` | Binary stream | Xuất danh sách hóa đơn, không gồm raw gateway payload. |
| `GET /contracts/{contractId}/invoices` | Tenant member / landlord sở hữu | Offset; `filter[status]`, `filter[period]`, `sort=period\|issuedAt` | `Invoice[]` | Tenant được xem HĐ hiện tại/lịch sử. |
| `GET /contracts/{contractId}/invoices/statement` | Tenant member / landlord sở hữu | `year`, `format=pdf|csv` | Binary stream | Sao kê theo năm của một hợp đồng; tenant chỉ tải sao kê hợp đồng mình là member. |
| `GET /invoices/{invoiceId}` | Tenant member / landlord sở hữu / ADMIN | — | `InvoiceDetail` | Che ownership bằng 404. |
| `GET /invoices/{invoiceId}/document` | Tenant member / landlord sở hữu / ADMIN | — | PDF binary | “Tải phiếu báo thu (PDF)”; chỉ có khi invoice đã issue, có `Content-Disposition`. |
| `POST /landlord/rooms/{roomId}/invoices/generate` | LANDLORD | `{ "period": "YYYY-MM" }` | `InvoiceDetail` (201) | Tạo một pending invoice cho một phòng; thiếu readings/config: `422`; trùng: `409 CONFLICT`. |
| `PATCH /landlord/invoices/{invoiceId}` | LANDLORD | `UpdatePendingInvoiceRequest` | `InvoiceDetail` | Chỉ pending; sửa `otherFees`, note, backend tính lại tổng. |
| `POST /landlord/invoices/{invoiceId}/issue` | LANDLORD | Không body | `InvoiceDetail` | Freeze snapshot, set `issuedAt`, gửi card chat/notification. |
| `POST /landlord/invoices/{invoiceId}/cancel` | LANDLORD | `{ "reason": "string" }` | `InvoiceDetail` | Không delete; giữ audit, cho phép tạo bản thay thế. |
| `GET /invoices/{invoiceId}/payment-summary` | Tenant member / landlord sở hữu | — | `PaymentSummary` | Đã thu, còn nợ, thu dư và status. |

`InvoiceDetail` có code, contract/room summary, period, rent, breakdown, other fees, total, paid/outstanding amount, status, issued/due date, note và payment summary. `UpdatePendingInvoiceRequest = { otherFees: [{ name, amount }], note }`; chỉ `otherFees[].amount` được âm. Backend dùng Decimal/Postgres numeric, trả VND integer; tổng âm: `422 TOTAL NEGATIVE`.

### 6.4 Công nợ quá hạn và nhắc nợ thủ công

Màn “Danh sách công nợ quá hạn” là danh sách dẫn xuất từ invoice có `status=overdue`; không tạo bảng Debt độc lập. `OverdueDebt` phải có room/building, invoice code, tenant contact đã được landlord sở hữu quyền xem, outstanding amount, overdue days, `lastReminderAt` và `reminderCount`.

| Method và path | Quyền | Request/query | Response `data` | Quy tắc |
|---|---|---|---|---|
| `GET /landlord/debts` | LANDLORD | Offset; `filter[buildingId]`, `filter[overdueDays]=lt5|5_10|gt10`, `filter[period]`, `sort=overdueDays\|outstandingAmount\|dueDate` | `OverdueDebt[]` + `DebtSummary` | Dữ liệu cho card dashboard và danh sách công nợ. |
| `POST /landlord/invoices/{invoiceId}/reminders` | LANDLORD | `{ "channels": ["in_app","push"], "note": "string|null" }` | `ReminderDispatch` (201) | Nút “Nhắc nợ” từng dòng; tạo bot/chat card và notification theo preference. |
| `POST /landlord/debt-reminder-campaigns` | LANDLORD | `{ "invoiceIds": ["uuid"], "channels": ["in_app","push"], "note": "string|null" }` | `DebtReminderCampaign` (202) | Nút “Gửi nhắc nợ hàng loạt”; workflow có resource/audit riêng, không dùng `/bulk` generic. |
| `GET /landlord/debt-reminder-campaigns/{campaignId}` | LANDLORD | — | `DebtReminderCampaign` | Client poll khi campaign còn `processing`; trả thành công/thất bại theo từng invoice. |
| `GET /landlord/debts/export` | LANDLORD | Cùng filter `/landlord/debts`, `format=csv|xlsx|pdf` | Binary stream | Nút “Xuất báo cáo”; format phải được FE/PM chốt trước freeze. |

---

## 7. Thanh toán và cổng thanh toán

| Method và path | Quyền | Request | Response `data` | Quy tắc |
|---|---|---|---|---|
| `POST /invoices/{invoiceId}/payment-intents` | Tenant member / landlord sở hữu | `CreatePaymentIntentRequest`, `Idempotency-Key` | `PaymentIntent` (201 hoặc 200 replay) | Mọi member có thể trả; `vietqr`, `vnpay`, `momo` nếu bật. |
| `POST /invoices/{invoiceId}/cash-payments` | LANDLORD | `CashPaymentRequest`, `Idempotency-Key` | `Payment` (201 hoặc 200 replay) | Chủ nhà xác nhận số tiền mặt thực nhận; cho phép trả một phần/thu dư. |
| `GET /invoices/{invoiceId}/payments` | Tenant member / landlord sở hữu | Cursor; `sort=createdAt` | `Payment[]` | Không trả raw gateway response cho tenant. |
| `POST /webhooks/payments/{provider}` | Provider ký request | Body/signature của provider | Provider acknowledgement | Verify signature/event id, deduplicate, ghi audit; không dùng JSON wrapper chung. |

`CreatePaymentIntentRequest = { method: vietqr|vnpay|momo|mock, amount }`; `PaymentIntent` có payment id, invoice id, method, amount, status, expiresAt và QR/redirect payload. `CashPaymentRequest = { amount, payerMemberId, note }`. Cùng `Idempotency-Key` + body trả nguyên response cũ; cùng key body khác: `409 IDEMPOTENCY KEY REUSED`. Invoice chuyển `pending → partially_paid → paid` theo tổng payment success; thu dư được lưu, không tự hoàn. Webhook thành công vào invoice cancel sẽ set `needsReview=true`.

---

## 8. Chat và sự cố

### 8.1 Cuộc trò chuyện, Hộp thư và tin nhắn

| Method và path | Quyền | Request/query | Response `data` | Quy tắc |
|---|---|---|---|---|
| `GET /conversations` | AUTH | Cursor; `filter[type]`, `sort=updatedAt` | `ConversationSummary[]` | Chỉ conversation mình là member. |
| `GET /me/inbox` | AUTH | Cursor; `filter[channel]=resident\|match`, `filter[unread]` | `InboxThread[]` | Màn Inbox, gộp thread được phép xem. |
| `GET /contracts/{contractId}/landlord-conversation` | Tenant member / landlord sở hữu | — | `Conversation` | Chat trực tiếp tenant–chủ nhà; tạo khi activate HĐ nếu chưa có. |
| `GET /buildings/{buildingId}/community-conversation` | Cư dân hiện tại / landlord sở hữu | — | `Conversation` | Chat cộng đồng tòa; membership suy từ HĐ active. |
| `GET /match-requests/{matchRequestId}/conversation` | Hai bên match accepted | — | `Conversation` | Chat ghép bạn riêng, không public. |
| `GET /conversations/{conversationId}` | Conversation member | — | `Conversation` | Conversation archive chỉ đọc. |
| `GET /conversations/{conversationId}/messages` | Conversation member | Cursor, cố định `createdAt asc` | `Message[]` | Lịch sử theo policy `leftAt`. |
| `POST /conversations/{conversationId}/messages` | Active conversation member | `CreateMessageRequest` | `Message` (201) | Text/image/file; archived/rời nhóm: `409 CONVERSATION READ ONLY`. |
| `GET /conversations/{conversationId}/members` | Conversation member | — | `ConversationMember[]` | Autocomplete `@mention`. |

`CreateMessageRequest = { type: text|image|file, content, attachmentMediaIds, mentionedUserIds }`. Bot message do server sinh. Icon gọi thoại/video trong UI không có endpoint vì ngoài MVP.

### 8.2 Báo và xử lý sự cố

| Method và path | Quyền | Request/query | Response `data` | Quy tắc |
|---|---|---|---|---|
| `GET /issues` | LANDLORD | Offset; `filter[roomId]`, `filter[buildingId]`, `filter[status]`, `sort=createdAt\|status\|closedAt` | `IssueReport[]` | Tab Sự cố tập trung của chủ nhà. |
| `GET /landlord/issues/export` | LANDLORD | Cùng filter `/issues`, `format=csv|xlsx` | Binary stream | Xuất báo cáo sự cố theo phạm vi landlord. |
| `GET /contracts/{contractId}/issues` | Tenant member / landlord sở hữu | Offset; `filter[status]`, `sort=createdAt\|closedAt` | `IssueReport[]` | Room hub; locked tenant hiện tại được xem. |
| `POST /contracts/{contractId}/issues` | Tenant member / landlord sở hữu | `CreateIssueRequest` | `IssueReport` (201) | Tạo open, post bot card, gửi notification. |
| `GET /issues/{issueId}` | Reporter/member/landlord/ADMIN | — | `IssueReport` | — |
| `PATCH /issues/{issueId}` | Landlord sở hữu | `UpdateIssueRequest` | `IssueReport` | Đổi status gửi chat + notification. |
| `POST /issues/{issueId}/cancel` | Landlord sở hữu | `{ "note": "string|null" }` | `IssueReport` | Set `cancelled`, không delete. |

`CreateIssueRequest = { category, priority, title, description, evidenceMediaIds, notifyTenant }`; `category=electricity|air_conditioner|water_sanitary|door_access|structure|other`, `priority=low|medium|urgent`, tối đa 5 evidence. `UpdateIssueRequest = { status: open|in_progress|resolved, note }`. `Media` cho issue phải chấp nhận `image/jpeg`, `image/png`, `image/webp` và `video/mp4` (video tối đa 25 MiB); nếu không duyệt video thì UI phải bỏ nút quay video.

---

## 9. Ghép bạn cùng phòng

| Method và path | Quyền | Request/query | Response `data` | Quy tắc |
|---|---|---|---|---|
| `GET /roommate-profiles` | PUBLIC | Cursor; `filter[preferredArea]`, `filter[budgetMin]`, `filter[budgetMax]`, `filter[moveInOn]`, `sort=createdAt\|moveInOn` | `PublicRoommateProfile[]` | Chỉ profile visible; không like/comment/ranking. |
| `GET /roommate-profiles/{userId}` | PUBLIC | — | `PublicRoommateProfile` | Contact bị ẩn nếu chưa match. |
| `GET /me/roommate-profile` | TENANT | — | `RoommateProfile|null` | Profile của mình. |
| `PUT /me/roommate-profile` | TENANT | `RoommateProfileRequest` | `RoommateProfile` | Tạo/cập nhật đầy đủ profile 1:1. |
| `POST /me/roommate-profile/visibility` | TENANT | `{ "isVisible": true }` | `RoommateProfile` | Ẩn/hiện không xóa. |
| `GET /match-requests` | TENANT | Cursor; `filter[direction]=sent\|received`, `filter[status]`, `sort=createdAt\|respondedAt` | `MatchRequest[]` | Request của mình. |
| `POST /match-requests` | TENANT | `{ "targetId": "uuid" }` | `MatchRequest` (201) | Cần own profile; chặn self/trùng/cặp đảo: `409 MATCH REQUEST EXISTS`. |
| `POST /match-requests/{matchRequestId}/respond` | Target tenant | `{ "decision": "accepted|rejected" }` | `MatchRequest` | Chỉ pending; accepted mở contact theo policy. |
| `DELETE /match-requests/{matchRequestId}` | Requester tenant | — | `MatchRequest` | Người gửi hủy request đang `pending`; không hard-delete, set `status=cancelled`; request đã accepted/rejected trả `409 CONFLICT`. |
| `GET /match-requests/{matchRequestId}` | Requester/target | — | `MatchRequestDetail` | `contact` chỉ populated khi accepted. |
| `POST /match-requests/{matchRequestId}/co-tenant-invitations` | Member match accepted | `{ "roomId": "uuid", "message": "string|null" }` | `CoTenantInvitation` (201) | Nút “Gửi lời mời đồng thuê”; không tự tạo ContractMember pháp lý. |
| `POST /match-requests/{matchRequestId}/compatibility-score` | Requester/target | Không body | `CompatibilityScore` | Stretch AI, không trả prompt/trace. |

`RoommateProfileRequest = { lifestyle, personality, budgetMin, budgetMax, bio, preferredArea, moveInOn, isVisible, avatarMediaId }`.

---

## 10. Thông báo và quản trị

### 10.1 Thông báo

| Method và path | Quyền | Request/query | Response `data` |
|---|---|---|---|
| `GET /me/notifications` | AUTH | Cursor; `filter[type]`, `filter[read]`, `createdAt desc` | `Notification[]` |
| `POST /me/notifications/{notificationId}/read` | AUTH | — | `Notification` (idempotent) |
| `GET /me/notification-preferences` | AUTH | — | `NotificationPreference[]` |
| `PUT /me/notification-preferences/{type}` | AUTH | `{ "enabled": true }` | `NotificationPreference`; `type=invoice|chat|issue|match|account` |
| `PUT /me/notification-preferences/all` | AUTH | `{ "enabled": true }` | `NotificationPreference[]` | Map đúng công tắc “Cho phép thông báo” trong UI; update atomically toàn bộ nhóm preference. |

### 10.2 Admin

| Method và path | Quyền | Request/query | Response `data` | Quy tắc |
|---|---|---|---|---|
| `GET /admin/dashboard` | ADMIN | `period` tùy chọn | `AdminDashboard` | Card users/properties/finance theo UI. |
| `GET /admin/users` | ADMIN | Offset; `filter[role]`, `filter[userStatus]`, `filter[q]`, `sort=createdAt\|fullName\|role\|userStatus` | `AdminUser[]` | Tìm tên/email/phone. |
| `GET /admin/users/{userId}` | ADMIN | — | `AdminUserDetail` | Không trả password hash. |
| `POST /admin/users/{userId}/lock` | ADMIN | `{ "reason": "string" }` | `AdminUserDetail` | Lifecycle effect + audit/notification; không khóa admin duy nhất. |
| `POST /admin/users/{userId}/unlock` | ADMIN | `{ "restoreAction": "restore_contracts|terminate_contracts|null" }` | `AdminUserDetail` | Áp dụng HĐ suspended của landlord. |
| `GET /admin/buildings` | ADMIN | Offset; `filter[status]`, `filter[landlordId]`, `filter[q]`, `sort=createdAt\|buildingStatus` | `Building[]` | Hàng đợi duyệt. |
| `GET /admin/buildings/{buildingId}` | ADMIN | — | `AdminBuildingReviewDetail` | Xem ownership proof được ủy quyền. |
| `POST /admin/buildings/{buildingId}/review` | ADMIN | `{ "decision": "approved|rejected", "note": "string|null" }` | `BuildingDetail` | Reject phải có note; ghi reviewer/time/audit, gửi landlord notification. |
| `GET /admin/audit-logs` | ADMIN | Offset; filter action/actor/entity/from/to, `sort=createdAt` | `AuditLog[]` | Append-only, phải redact secret/CCCD. |
| `GET /admin/audit-logs/{auditLogId}` | ADMIN | — | `AuditLog` | Chi tiết đã redact. |
| `GET /admin/audit-logs/export` | ADMIN | Cùng filter `/admin/audit-logs`, `format=csv|json` | Binary stream | Xuất log đã redact; không có endpoint export riêng cho từng record vì `GET /admin/audit-logs/{auditLogId}` đã đủ. |

Khóa landlord sẽ ẩn property public và suspend HĐ active. Khóa tenant vẫn xem/trả tiền HĐ hiện tại nhưng không match, save room hoặc tạo thuê mới. Grace-period chạy nền, không cần endpoint client.

---

## 11. Thành phần OpenAPI dùng lại

`openapi.yaml` phải tái sử dụng component thay vì lặp schema ở mỗi path.

| Nhóm | Schema cần có |
|---|---|
| Envelope | `SuccessResponse`, `CreatedResponse`, `OffsetPagination`, `CursorPagination`, `ErrorResponse` |
| Security | `bearerAuth`, parameter `IdempotencyKey`, header `X-Request-Id` |
| Identity | `CurrentUser`, `UserProfile`, `RegisterRequest`, `LoginRequest`, `AuthSession`, `AuthSessionDevice`, `ChangePasswordRequest`, `PasswordResetRequest`, `PasswordReset`, `PushDevice` |
| Property | `Building`, `BuildingDetail`, `Room`, `PublicRoomCard`, `PublicRoomDetail`, `RatePolicy`, `RatePolicyPreset`, `RatePolicyQuote`, `BillingSetting`, `VietQrConfig`, `VietQrAccountVerification`, `VietQrPreview`, `Media` |
| Contract/chat | `Contract`, `ContractDetail`, `ContractMember`, `LeaseTemplate`, `Conversation`, `ConversationMember`, `Message` |
| Billing | `MeterReading`, `OcrPreview`, `CombinedMeterReadingsRequest`, `MeterReadingBatch`, `MeterReadingBatchItem`, `MeterReadingBatchSummary`, `Invoice`, `InvoiceDetail`, `InvoiceBreakdownItem`, `Payment`, `PaymentIntent`, `PaymentSummary`, `DepositSettlement`, `OverdueDebt`, `DebtSummary`, `ReminderDispatch`, `DebtReminderCampaign` |
| Collaboration/admin | `IssueReport`, `RoommateProfile`, `PublicRoommateProfile`, `MatchRequest`, `Notification`, `NotificationPreference`, `AdminUser`, `AdminUserDetail`, `AuditLog`, `AdminDashboard` |

Enum tập trung: `role: landlord|tenant|admin`; `userStatus: active|locked`; `buildingStatus: pending|approved|rejected`; `roomStatus: available|occupied|maintenance|cleaning_pending` **(cần migration DB)**; `contractStatus: draft|signed|active|suspended|expired|terminated`; `ratePolicyScope: landlord|building|room` **(cần migration DB)**; `ratePolicyType: electricity|water|wifi|cleaning|parking|maintenance|other` **(cần migration DB nếu giữ “phí phụ khác” trong UI)**; `rateKind: flat|tiered|per_head|per_area_m2|per_vehicle`; `meterReadingBatchStatus: draft|in_progress|completed`; `meterReadingBatchItemStatus: pending|draft|confirmed|skipped`; `invoiceStatus: pending|partially_paid|paid|overdue|cancel`; `paymentMethod: vietqr|vnpay|momo|cash|mock`; `paymentStatus: pending|success|failed`; `issueStatus: open|in_progress|resolved|cancelled`; `issuePriority: low|medium|urgent` **(cần migration DB)**; `conversationType: room|building|direct`; `messageType: text|image|file|bot`; `matchStatus: pending|accepted|rejected|cancelled` **(cần migration DB)**; `debtReminderCampaignStatus: processing|completed|completed_with_errors|failed`.

---

## 12. Thời gian thực và xử lý bất đồng bộ

REST là nguồn dữ liệu chuẩn. Socket.io chỉ phát event để client đang mở app refresh; FCM đánh thức client offline rồi client gọi REST.

| Server event | Người nhận | Payload tối thiểu |
|---|---|---|
| `message.created` | Conversation members | `conversationId`, `messageId`, `createdAt` |
| `invoice.issued`, `invoice.updated` | Member HĐ hiện tại + landlord | `invoiceId`, `contractId`, `status` |
| `issue.updated` | Reporter/member phòng/landlord | `issueId`, `contractId`, `status` |
| `match-request.created`, `match-request.updated` | Target hoặc hai bên | `matchRequestId`, `status` |
| `notification.created` | User sở hữu notification | `notificationId`, `type` |

Event không chứa CCCD, evidence hợp đồng, raw payment payload hay nội dung chat dài; client phải re-fetch resource. OCR, render mẫu, AI score và payment redirect chỉ trả `202` khi OpenAPI có polling resource rõ ràng; bản v1 hiện dùng preview/action đồng bộ.

---

## 13. Đối chiếu UI với API

Màn hình chỉ biểu diễn state như splash/loading/success/generic error/logout confirmation/empty state/locked-restricted explanation/QR preview không tạo endpoint mới; chúng tiêu thụ kết quả endpoint dưới đây.

| Nhóm màn hình UI Mobile/Web | Endpoint backing | Bổ sung trong bản này |
|---|---|---|
| Login, sign-up, quên/đặt lại mật khẩu, locked/restricted, logout | `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/me`, `/auth/password-reset-requests`, `/auth/password-resets` | Password recovery. |
| Hồ sơ bảo mật: đổi mật khẩu, avatar, session thiết bị | `/me/password`, `/me/profile`, `/me/sessions` | Bổ sung session revocation và avatar `null`. |
| Danh sách/bản đồ/filter phòng, chi tiết, phòng đã lưu, profile tenant | `GET /rooms`, `GET /rooms/{roomId}`, `/me/favorites`, `/me/profile` | Dùng public search filters. |
| Feed ghép bạn, profile, request, match, mời đồng thuê | `/roommate-profiles`, `/me/roommate-profile`, `/match-requests`, resolver conversation, co-tenant invitation | Match chat và invitation. |
| Hub tenant, danh sách/chi tiết HĐ, members, invoice, payment | `/me/contracts`, `/contracts/{id}`, `/contracts/{id}/members`, `/contracts/{id}/invoices`, `/invoices/{id}` | Giữ contract đã có. |
| Inbox, chat chủ nhà, chat phòng/tòa, chat match | `/me/inbox`, resolver conversation, `/conversations/{id}/messages` | Resolver endpoint rõ ràng. |
| Tòa/phòng, flow thêm tòa 3 bước, ownership proof, room map | `/landlord/buildings`, `/landlord/rooms`, `/media` | — |
| Fixed/EVN/per-person rates, due-date/debt scan | `/landlord/rate-policies`, `/landlord/billing-settings` | `rateKind` map ba UI mode. |
| VietQR theo tòa, verify và preview | VietQR endpoints §4.3 | Entity + endpoint mới. |
| Ghi số đơn/OCR và ghi 15 phòng hàng loạt | Meter reading endpoints §6 | Workflow-batch có auto-save/skip/summary. |
| Preview/edit/cancel/issue invoice, cash/QR payment | Invoice/payment endpoints §6–§7 | — |
| PDF phiếu báo thu, công nợ quá hạn, nhắc từng phòng/hàng loạt, xuất báo cáo | `GET /invoices/{id}/document`, `/landlord/debts`, invoice reminder, debt reminder campaign, debt export | Bổ sung sau khi audit UI. |
| Xuất thành viên, invoice, sao kê, issue và audit log | Các endpoint `.../export` và invoice statement | Bổ sung theo `api_bosung.md`, áp dụng redaction/ownership. |
| Final meter, final invoice, settlement cọc, bàn giao và dọn phòng | Checkout endpoints §5 | Thay checkout đơn bằng từng bước UI. |
| Issues, notification center/settings | `/issues`, `/contracts/{id}/issues`, `/me/notifications`, `/me/notification-preferences` | — |
| Admin dashboard/users/lock/property review/audit | `/admin/dashboard`, `/admin/users`, `/admin/buildings`, `/admin/audit-logs` | — |

Trong bảng, checkout rút gọn; path đầy đủ là `/landlord/contracts/{contractId}/checkout/...`.

---

## 14. Điểm cần chốt / vướng mắc

| ID | Vấn đề | Ảnh hưởng | Hành động đề xuất |
|---|---|---|---|
| OQ-01 | Đã rà soát ZIP UI. | Map UI–API có ở §13. | PM/FE/Mobile xác nhận tên endpoint/payload khi review. |
| OQ-02 | P2-06 yêu cầu `openapi.yaml`, còn file này là `api-spec.md`. | Chưa import Swagger/Apidog trực tiếp. | BE chuyển blueprint này thành OpenAPI 3.0, validate và import Apidog. |
| OQ-03 | Requirement long-term-only nhưng tenant/shared flow có thuê ngắn hạn theo ngày. | Không thêm endpoint short-term. | PM xóa/sửa flow mâu thuẫn hoặc thêm scope/schema phase riêng. |
| OQ-04 | UI checkout cần trạng thái dọn phòng. | Enum Room chưa đủ. | Thêm `cleaning_pending` hoặc lifecycle model riêng. |
| OQ-05 | Flow có default rate/billing theo landlord nhưng DB chỉ scope building/room. | API dùng `scope=landlord` nhưng DB chưa persist được. | Migration cho `RatePolicy`/`BillingSetting`: cho phép `scope=landlord`, hai target id `null`, unique index phù hợp. |
| OQ-06 | UI nhập số tầng nhưng Building DB chưa có `floorCount`. | Không lưu/trả field. | Thêm field hoặc bỏ khỏi UI. |
| OQ-07 | Form HĐ có CCCD/address, DB thiếu các field tương ứng. | DTO chưa thỏa form nếu không tự bịa storage. | Chốt fields mới hoặc chỉ dùng media CCCD/template-only address. |
| OQ-08 | UI flow nói DOC nhưng API convention chỉ jpeg/png/webp/pdf. | Whitelist MIME mâu thuẫn. | Cho phép DOC/DOCX hoặc sửa UI thành PDF/image. |
| OQ-09 | UI room detail có phone chủ nhà nhưng convention cấm public phone. | `landlordContact` chưa chốt. | Chọn masking/contact request/field public được duyệt. |
| OQ-10 | Tenant camera-only không thể chứng minh nguồn camera chỉ bằng multipart upload. | Có thể bypass UX. | Mobile/BE thêm trusted capture metadata hoặc xem là UX restriction. |
| OQ-11 | Invoice DTO có `fixed_per_period` nhưng rate policy chưa có enum tương ứng. | Mapping tính phí mơ hồ. | Chuẩn hóa enum + publish utility calculation doc. |
| OQ-12 | Chưa có grace duration, policy hoàn cọc, webhook contract, rate/upload limits. | Không freeze được lifecycle/webhook. | PM/BE/Finance chốt trước implementation. |
| OQ-13 | Chưa có P2-01 feature map để check cơ học toàn bộ primary screen. | Không chứng minh coverage 100% bằng map. | PM gửi feature-platform map hiện tại. |
| OQ-14 | UI cần batch session, convention v1 từng nói không có bulk write. | UI không thể chỉ dùng single-room API. | Phê duyệt exception workflow-batch §6.2; từng room/evidence vẫn atomic. |
| OQ-15 | UI VietQR cần receiver config, verify, preview nhưng DB chưa có entity. | Không sinh QR hóa đơn đúng tài khoản nhận. | Thêm `VietQrReceiverConfig` và verification ref an toàn. |
| OQ-16 | UI có direct landlord/building/accepted-match chat, nhưng membership/unique rule chưa đủ chi tiết. | Có thể tạo chat trùng hoặc lộ chat. | Thêm constraint và rule membership theo HĐ/tòa/match request. |
| OQ-17 | UI có icon gọi và đề xuất tạo lịch hẹn xem phòng. | Voice/call/appointment chưa có scope/data model. | Đánh dấu visual-only/Phase 1+ hoặc thêm business rule, calendar/privacy/schema. |
| OQ-18 | UI reset password nhưng DB chưa có reset token/session revocation model. | Không thể triển khai reset an toàn. | Thêm record hash, expiring, single-use; revoke refresh sessions khi reset thành công. |
| OQ-19 | UI công nợ có nhắc từng phòng/hàng loạt và xuất báo cáo. | Bản trước không có endpoint hoặc audit cho thao tác này. | Dùng §6.4; chốt format export và retention của campaign. |
| OQ-20 | UI billing có ngày chốt, rule hạn và lịch nhắc chi tiết, DB chỉ có `due_days`/`remind_days`. | Không lưu được setting UI, cron chạy sai. | Migration `BillingSetting` theo `BillingSettingRequest` ở §4.2; chỉ hỗ trợ `in_app|push` trong MVP. |
| OQ-21 | UI Issue có category, priority và video, DB/API cũ chỉ có title/description/ảnh. | Không render hoặc lưu đúng form báo sự cố. | Migration `IssueReport`; mở MIME `video/mp4` hoặc bỏ video khỏi UI. |
| OQ-22 | `database-design.md` nói chat cũ vẫn gửi được sau checkout, nhưng user flow/UI và §5 yêu cầu archive read-only. | Rủi ro lộ chat/liên lạc sau khi trả phòng. | Chốt read-only; thêm `Conversation.status=active|archived` hoặc rule theo Contract status. |
| OQ-23 | UI thể hiện Zalo/SMS, tạm trú, tài sản/bảo trì và điều phối kỹ thuật. | Những nội dung này ngoài MVP hiện tại. | Gắn nhãn Phase 1+ hoặc bỏ khỏi UI; không tạo API v1 khi chưa mở scope. |
| OQ-24 | UI cho tạo phí phụ tùy ý, DB `RatePolicy.type` chưa có `other`. | Không lưu được phí không thuộc wifi/rác/gửi xe/bảo trì. | Thêm `other` hoặc giới hạn UI vào enum hiện có. |
| OQ-25 | `api_bosung.md` đề xuất endpoint cấu hình biểu phí theo nhiều item. | API convention v1 mặc định không bulk write. | Chỉ chấp nhận exception `PUT /landlord/buildings/{buildingId}/rate-policies` cho wizard UI; transaction all-or-nothing, version policy/audit đầy đủ. |
| OQ-26 | `api_bosung.md` đề xuất Zalo/SMS, sự cố chung cấp tòa và admin tạo user. | Trái MVP hoặc thiếu model/flow/ownership. | Không thêm vào v1: reminder chỉ `in_app|push`; IssueReport vẫn phải gắn room/contract; admin chỉ lock/unlock/review, không tạo user/role. |

---

## 15. Checklist tạo `openapi.yaml`

- [ ] Chuyển mọi hàng endpoint thành OpenAPI 3.0+ path dưới `/api/v1`.
- [ ] Khai báo bearer security, role và ownership cho từng operation.
- [ ] Dùng component schema/envelope/error chung ở §11.
- [ ] Khai báo chính xác filter/sort/default/pagination của từng list endpoint.
- [ ] Thêm `Idempotency-Key` cho mọi endpoint tạo payment/settlement.
- [ ] Khai báo multipart, MIME và giới hạn upload cho Media.
- [ ] Chốt các OQ đang mở trước khi freeze; bỏ endpoint tạm nếu scope bác bỏ.
- [ ] Validate YAML và import vào Apidog.
- [ ] FE Web và Mobile xác nhận từng màn/action với OpenAPI cuối.
