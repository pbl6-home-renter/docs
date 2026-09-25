# PBL6 — API Spec v1 (thiết kế theo resource/database)

**Trạng thái:** Bản thiết kế rút gọn, đối chiếu các màn hình Web/Mobile hiện có  
**Base path:** `/api/v1`  
**Nguồn:** `database-design.md`, `api-conventions.md`, yêu cầu và các luồng UI hiện có.

---

## 1. Nguyên tắc thiết kế

API được gom theo **resource/bảng dữ liệu**, không gom theo role. Vì vậy không dùng các prefix như `/landlord/*` hay `/tenant/*` cho dữ liệu dùng chung.

- Ví dụ: cả chủ nhà lẫn người thuê đều gọi `GET /contracts`, `GET /invoices`, `GET /issues`; server tự lọc theo quan hệ của người gọi.
- JWT chỉ xác thực danh tính (`sub`, `role`). Quyền thật sự được quyết định bằng `ownerUserId`, `LandlordProfile`, `ContractMember`, `ConversationMember` và trạng thái bản ghi.
- Chỉ dùng `/admin/*` cho thao tác kiểm duyệt/quản trị không thuộc dữ liệu vận hành thông thường.
- Các API chỉ phục vụ UI hiện tại hoặc bắt buộc để UI hoạt động. Tác vụ hiếm được gộp thành endpoint tổng quát thay vì tách nhiều endpoint nhỏ.
- Không xóa cứng các chứng từ, hóa đơn, thanh toán, hợp đồng hoặc chỉ số đã phát hành. Dùng trạng thái/hủy để giữ lịch sử.

### 1.1 Xác thực, phiên và quy ước chung

- Access token là JWT ngắn hạn, gửi bằng `Authorization: Bearer <token>`.
- Refresh token thuộc một **AuthSession nội bộ**, lưu cookie `HttpOnly; Secure; SameSite` trên web hoặc secure storage trên mobile. Client không đọc refresh token.
- `POST /auth/logout` thu hồi **phiên hiện tại**. Không mở API quản lý nhiều phiên (`/me/sessions`) vì UI chưa có màn hình này.
- Response, lỗi, phân trang, format thời gian và `Idempotency-Key` tuân theo `api-conventions.md`. Danh sách dùng `offset`, `limit`, `sort`; tối đa `limit=100`.
- Mọi `POST/PATCH/PUT/DELETE` cần JWT đều ghi `actorUserId` vào `AuditLog` khi thay đổi dữ liệu nghiệp vụ quan trọng.

### 1.2 Quy tắc truy cập theo quan hệ

| Resource | Ai được đọc | Ai được thay đổi |
|---|---|---|
| `Building`, `Room` | Public chỉ đọc phòng/tòa đã duyệt và đang hiển thị; người đăng nhập đọc thêm theo quan hệ | Chủ sở hữu tòa/phòng; admin chỉ duyệt/khóa |
| `Contract`, `ContractMember` | Chủ nhà quản lý hợp đồng; tenant là thành viên hợp đồng | Chủ nhà tạo/sửa trước kích hoạt; tenant chỉ xác nhận/chỉnh thông tin của chính mình khi được phép |
| `MeterReading`, `Invoice`, `Payment` | Chủ nhà quản lý; tenant có hợp đồng liên quan | Chủ nhà ghi số/phát hành/hủy; tenant tạo thanh toán của hóa đơn mình |
| `IssueReport` | Tenant trong hợp đồng và chủ nhà liên quan | Tenant tạo/hủy issue của mình; chủ nhà cập nhật xử lý |
| `Conversation`, `Message` | Chỉ `ConversationMember` | Chỉ thành viên; không có API xóa lịch sử chat trong v1 |
| `FavoriteRoom`, `RoommateProfile`, `MatchRequest`, `Notification` | Theo chủ sở hữu/thành viên | Theo chủ sở hữu và rule trạng thái |

> `role` không thay thế kiểm tra quan hệ. Ví dụ tenant không thể gọi hóa đơn của tenant khác, dù cùng role `tenant`.

### 1.3 Mapping bảng → nhóm API

| Bảng database | Nhóm endpoint |
|---|---|
| `User`, `LandlordProfile`, `PushDevice` | §2 — `auth`, `/me`, `/me/push-devices`; `LandlordProfile` là quan hệ nội bộ, không tách namespace. |
| `Media` | §3 — `/media`. |
| `Building`, `Room`, `FavoriteRoom` | §4–5 — `/buildings`, `/rooms`, `/me/favorite-rooms`. |
| `RoommateProfile`, `MatchRequest` | §5 — `/roommate-profiles`, `/match-requests`. |
| `RatePolicy`, `BillingSetting` | §6 — `/rate-policies`, `/billing-settings`. |
| `Contract`, `ContractMember` | §7 — `/contracts` và nested `/contracts/{id}/members`. |
| `MeterReading` | §8 — `/rooms/{id}/meter-readings`; batch là extension UI có migration riêng. |
| `Invoice`, `Payment` | §9 — `/invoices`, `/payments`, `/debts` (view từ Invoice). |
| `IssueReport` | §10 — `/issues`. |
| `Conversation`, `ConversationMember`, `Message`, `MessageMention` | §11 — `/conversations`; membership/mention được service quản lý theo quan hệ. |
| `Notification`, `NotificationPreference` | §12 — `/notifications`, `/me/notification-preference`. |
| `AuditLog` | §13 — chỉ đọc qua `/admin/audit-logs`. |

---

## 2. User và AuthSession

`User` là bảng danh tính. `AuthSession` và reset token là bảng/bản ghi kỹ thuật nội bộ, không phải resource UI độc lập.

| Method & path | Quyền | Body/query chính | Kết quả | Ghi chú |
|---|---|---|---|---|
| `POST /auth/register` | PUBLIC | `email, password, fullName, phone, role` | `User` an toàn + access token | Chỉ nhận `tenant` hoặc `landlord`; không tạo admin qua API. |
| `POST /auth/login` | PUBLIC | `email, password` | access token + thiết lập refresh session | Trả `403 ACCOUNT_LOCKED` khi bị khóa. |
| `POST /auth/refresh` | Refresh session | — | access token mới | Rotation refresh token. |
| `POST /auth/logout` | AUTH | — | `204` | Thu hồi AuthSession hiện tại. |
| `POST /auth/password-reset-requests` | PUBLIC | `email` | `202` | Luôn trả kết quả trung tính để tránh dò email. |
| `POST /auth/password-resets` | PUBLIC | `token, newPassword` | `204` | Token một lần, có hạn. |
| `GET /me` | AUTH | — | `CurrentUser` | Dùng bootstrap app: profile, role, trạng thái khóa. |
| `PATCH /me` | AUTH | `fullName, phone` | `User` | Không cho đổi email/role tại đây. Avatar là `Media(ownerType=user)`. |
| `PUT /me/password` | AUTH | `currentPassword, newPassword, confirmPassword` | `204` | Đổi mật khẩu khi đăng nhập; thu hồi refresh token cũ trừ phiên hiện tại. |
| `POST /me/push-devices` | AUTH | `platform, pushToken` | `PushDevice` | Hỗ trợ nhận notification trên mobile/web. |
| `DELETE /me/push-devices/{deviceId}` | AUTH, owner | — | `204` | Gỡ token thiết bị hiện tại/đã đăng ký. |

`LandlordProfile` chỉ là quan hệ 1–1 đánh dấu tài khoản chủ nhà và điểm kế thừa cấu hình; bảng hiện không có dữ liệu hồ sơ độc lập cần CRUD. Policy/billing mặc định được quản lý trong §6, không tạo `/landlord-profile/*` riêng.

---

## 3. Media

`Media` là file dùng chung bởi phòng, hợp đồng, chỉ số, issue, avatar… Server phải kiểm tra quyền trên **bản ghi cha** trước khi trả file private.

| Method & path | Quyền | Body/query chính | Kết quả | Ghi chú |
|---|---|---|---|---|
| `POST /media` | AUTH | multipart `file, ownerType, ownerId, purpose` | `Media` | Đúng với thiết kế polymorphic. `purpose` hợp lệ theo `ownerType`, ví dụ `cover_photo`, `cccd_front`, `contract_signed`, `meter_reading_evidence`. |
| `GET /media/{mediaId}` | Theo resource cha | — | redirect/signed URL hoặc stream | Media phòng công khai được đọc public; CCCD/hợp đồng chỉ người có quyền. |
| `DELETE /media/{mediaId}` | AUTH, quyền sửa resource cha | — | `204` | Soft-delete. Server chặn xóa chứng từ đã bị khóa, ví dụ file ký của hợp đồng active. |

Tạo Building/Room/ContractMember trước, sau đó upload Media với `ownerType` và `ownerId` tương ứng. Các endpoint tạo MeterReading/IssueReport có thể nhận multipart evidence và tạo Media cùng transaction để tránh vòng lặp ID.

---

## 4. Building và Room

Đây là luồng tìm phòng và quản lý bất động sản. Một path phục vụ nhiều role; query `view` chỉ thay đổi tập dữ liệu trả về, không phải một namespace role.

### 4.1 Building

| Method & path | Quyền | Body/query chính | Kết quả | Ghi chú |
|---|---|---|---|---|
| `GET /buildings` | PUBLIC/AUTH | `q, province, ward, view=public\|owned\|resident, offset, limit, sort` | `Building[]` | `public` chỉ tòa đã duyệt; `owned` chỉ chủ sở hữu; `resident` chỉ tòa có hợp đồng của tôi. |
| `POST /buildings` | AUTH | `name, province, ward, address, latitude?, longitude?` | `Building` | Người tạo trở thành chủ sở hữu qua `LandlordProfile`; status ban đầu `pending`. Upload `ownership_proof` qua Media sau khi có ID. |
| `GET /buildings/{buildingId}` | PUBLIC/AUTH | — | `BuildingDetail` | Public dùng bản dữ liệu đã publish; owner/resident thấy dữ liệu phù hợp. |
| `PATCH /buildings/{buildingId}` | AUTH, owner | Các trường có thể sửa | `Building` | Không đổi owner qua endpoint này. |
| `PUT /buildings/{buildingId}/vietqr-config` | AUTH, owner | `bankCode, accountNo, accountName, template?` | cấu hình VietQR | Upsert cấu hình; cần bảng bổ sung nêu ở §15. UI cài đặt thanh toán dùng endpoint này. |
| `GET /buildings/{buildingId}/vietqr-config` | AUTH, owner | — | cấu hình VietQR | Hóa đơn chỉ nhận payload QR đã được tạo, không lộ số tài khoản tùy tiện. |

### 4.2 Room

| Method & path | Quyền | Body/query chính | Kết quả | Ghi chú |
|---|---|---|---|---|
| `GET /rooms` | PUBLIC/AUTH | `q, province, ward, minPrice, maxPrice, minArea, amenities[], availableOnly?, view=public\|managed\|mine, offset, limit, sort` | `RoomCard[]` | Endpoint tìm kiếm, lọc, map và danh sách phòng quản lý/phòng đang thuê. |
| `POST /buildings/{buildingId}/rooms` | AUTH, building owner | `name, floorNumber?, area?, maxOccupancy?, genderPolicy, rentPrice, description?, amenities` | `Room` | Giữ quan hệ tạo room với Building nhưng resource trả về vẫn là `Room`. Ảnh upload qua Media sau khi có ID. |
| `GET /rooms/{roomId}` | PUBLIC/AUTH | — | `RoomDetail` | Có giá hiển thị, tiện ích, ảnh, availability; không lộ dữ liệu tenant khác. |
| `PATCH /rooms/{roomId}` | AUTH, room/building owner | Các trường có thể sửa, `status?` | `Room` | Chỉ owner thay đổi giá, sức chứa, trạng thái. |
| `POST /rooms/{roomId}/ready` | AUTH, owner | — | `Room` | Xác nhận phòng đã dọn, chuyển `cleaning_pending` sang `available`; dùng ở UI checkout. |

`RoomDetail` trả `effectiveRatePolicySummary` tính theo thứ tự room → building → landlord; client không tự tính giá điện/nước.

---

## 5. FavoriteRoom, RoommateProfile và MatchRequest

### 5.1 FavoriteRoom

| Method & path | Quyền | Body/query chính | Kết quả | Ghi chú |
|---|---|---|---|---|
| `GET /me/favorite-rooms` | AUTH | `offset, limit` | `RoomCard[]` | Danh sách yêu thích của chính mình. |
| `POST /me/favorite-rooms` | AUTH | `roomId` | `FavoriteRoom` | Idempotent; phòng không public trả `404`. |
| `DELETE /me/favorite-rooms/{roomId}` | AUTH, owner | — | `204` | Bỏ yêu thích. |

### 5.2 RoommateProfile và MatchRequest

| Method & path | Quyền | Body/query chính | Kết quả | Ghi chú |
|---|---|---|---|---|
| `GET /roommate-profiles` | AUTH | `preferredArea?, budgetMin?, budgetMax?, moveInFrom?, moveInTo?, offset, limit` | `RoommateProfile[]` | Chỉ profile đã bật `isVisible`. |
| `GET /me/roommate-profile` | AUTH | — | `RoommateProfile` hoặc `404` | Lấy profile của tôi. |
| `PUT /me/roommate-profile` | AUTH | `bio?, lifestyle?, personality?, budgetMin?, budgetMax?, preferredArea?, moveInOn?, isVisible` | `RoommateProfile` | Upsert profile. |
| `GET /match-requests` | AUTH | `direction=incoming\|outgoing, status?, offset, limit` | `MatchRequest[]` | Server lọc người gửi/người nhận. |
| `POST /match-requests` | AUTH | `receiverUserId, message?` | `MatchRequest` | Không gửi cho chính mình; không tạo trùng request pending. |
| `POST /match-requests/{matchRequestId}/accept` | AUTH, receiver | — | `MatchRequest` + `conversationId` | Tạo/lấy direct conversation khi accept. |
| `POST /match-requests/{matchRequestId}/reject` | AUTH, receiver | — | `MatchRequest` | Chỉ đổi request `pending`. |
| `DELETE /match-requests/{matchRequestId}` | AUTH, requester | — | `204` | Người gửi hủy request `pending`; dùng soft-delete để không vi phạm unique pair. |

---

## 6. RatePolicy và BillingSetting

Hai bảng này cấu hình vận hành, áp dụng theo chuỗi Room → Building → LandlordProfile. Không tách `/landlord/rate-policies`.

| Method & path | Quyền | Body/query chính | Kết quả | Ghi chú |
|---|---|---|---|---|
| `GET /rate-policies` | AUTH | `scope?, buildingId?, roomId?, type?, active?` | `RatePolicy[]` | Owner đọc policy của mình; tenant chỉ thấy summary đã áp dụng qua room/invoice. |
| `POST /rate-policies` | AUTH, owner | `scope=landlord\|building\|room, buildingId?, roomId?, name, type, rateKind, unitPrice?, steps?` | `RatePolicy` | Một policy ứng với một loại phí. Scope dưới chỉ được chọn một. |
| `POST /rate-policies/batch` | AUTH, owner | `scope, buildingId?/roomId?, policies[]` | `RatePolicy[]` | Lưu bộ biểu phí từ một màn hình UI trong một transaction; thay thế các policy active cùng `type`. |
| `PATCH /rate-policies/{ratePolicyId}` | AUTH, owner | `name` | `RatePolicy` | Không sửa đơn giá active; thay giá bằng record mới. |
| `POST /rate-policies/{ratePolicyId}/deactivate` | AUTH, owner | — | `RatePolicy` | Thay vì xóa; dùng khi có policy mới hoặc muốn kế thừa cấp trên. |
| `GET /billing-settings` | AUTH | `scope?, buildingId?, roomId?` | `BillingSetting[]` | Lấy cấu hình hạn thanh toán/nhắc nợ của tài sản mình. |
| `POST /billing-settings` | AUTH, owner | `scope=landlord\|building\|room, buildingId?, roomId?, dueDays, remindDays, botEnabled` | `BillingSetting` | Scope tương tự RatePolicy. |
| `PATCH /billing-settings/{billingSettingId}` | AUTH, owner | Các trường cấu hình | `BillingSetting` | Áp dụng kỳ sau; server kiểm tra ngày hợp lệ. |

---

## 7. Contract và ContractMember

Hợp đồng ký tay: file signed là chứng từ pháp lý. Mọi API hợp đồng chung dùng `/contracts`; chủ nhà và tenant chỉ thấy hợp đồng có quan hệ với mình.

### 7.1 Contract

| Method & path | Quyền | Body/query chính | Kết quả | Ghi chú |
|---|---|---|---|---|
| `GET /contracts` | AUTH | `roomId?, status?, view=current\|history, offset, limit, sort` | `Contract[]` | Owner thấy hợp đồng phòng mình; member thấy hợp đồng mình tham gia. |
| `POST /contracts` | AUTH, room owner | `roomId, tenantId?, tenantName?, tenantPhone?, monthlyRent, depositAmount, startDate, endDate, description?, vehicleCount?` | `Contract` | Tạo `draft`. Nếu không có `tenantId`, bắt buộc tenantName + tenantPhone. |
| `GET /contracts/{contractId}` | AUTH, related | — | `ContractDetail` | Gồm members, tài liệu, status và quyền action. |
| `PATCH /contracts/{contractId}` | AUTH, owner | Trường draft | `Contract` | Chỉ `draft`/`signed` được sửa. |
| `GET /contract-templates` | AUTH, owner | — | template metadata | Danh sách template seed/config; không cần bảng nghiệp vụ riêng trong v1. |
| `GET /contract-templates/{templateKey}` | AUTH, owner | — | template metadata + preview URL | Xem trước một mẫu trước khi gắn vào contract. |
| `PUT /contracts/{contractId}/template` | AUTH, owner | `templateKey` | `Contract` | Chọn template trước khi xuất. |
| `POST /contracts/{contractId}/documents/draft` | AUTH, owner | — | `Media` / signed download URL | Sinh PDF dự thảo từ snapshot hợp đồng. |
| `POST /contracts/{contractId}/activate` | AUTH, owner | — | `Contract` | Chỉ khi có Media `contract_signed` và member hợp lệ; tạo conversation phòng nếu cần. |
| `POST /contracts/{contractId}/checkout/final-meter-readings` | AUTH, owner | `readings[]` | `MeterReading[]` | Ghi chỉ số cuối khi trả phòng. |
| `POST /contracts/{contractId}/checkout/final-invoice` | AUTH, owner | `depositDeduction?, otherAdjustments?` | `Invoice` | Lập hóa đơn cuối từ chỉ số cuối/snapshot. |
| `POST /contracts/{contractId}/checkout/complete` | AUTH, owner | `completedOn` | `Contract` + `Room` | Kết thúc hợp đồng sau khi xử lý hóa đơn cuối; Room → `cleaning_pending`. |

### 7.2 ContractMember

| Method & path | Quyền | Body/query chính | Kết quả | Ghi chú |
|---|---|---|---|---|
| `POST /contracts/{contractId}/members` | AUTH, owner | `tenantId?, tenantName?, tenantPhone?, joinedAt?` | `ContractMember` | Tenant có thể chưa có tài khoản. CCCD được upload Media `cccd_front`/`cccd_back` sau khi có member ID. |
| `PATCH /contracts/{contractId}/members/{memberId}` | AUTH, owner / chính member | Trường được phép | `ContractMember` | Tenant chỉ sửa thông tin liên hệ của mình khi contract cho phép. |
| `POST /contracts/{contractId}/members/{memberId}/leave` | AUTH, owner | `leftOn` | `ContractMember` | Kết thúc tư cách thành viên, giữ lịch sử. |
| `GET /contracts/{contractId}/members/export` | AUTH, owner | `format=xlsx\|csv` | signed download URL / file stream | Xuất danh sách thành viên/cư dân của hợp đồng phòng ra file Excel/CSV theo nút trên UI. |

---

## 8. MeterReading

`MeterReading` thuộc Room và có unique `(roomId, meterType, period)`. Chỉ owner ghi số; tenant xem dữ liệu đã dùng để phát hành hóa đơn của hợp đồng mình.

| Method & path | Quyền | Body/query chính | Kết quả | Ghi chú |
|---|---|---|---|---|
| `GET /rooms/{roomId}/meter-readings` | AUTH, related | `meterType?, period?, offset, limit` | `MeterReading[]` | Dùng cho lịch sử/kỳ hóa đơn. |
| `POST /rooms/{roomId}/meter-readings/ocr-preview` | AUTH, owner | multipart `type, period, evidenceFile` | `{suggestedCurrentReading, confidence, warnings[]}` | Chỉ preview; người dùng xác nhận bằng API ghi số. |
| `POST /rooms/{roomId}/meter-readings` | AUTH, owner | multipart `type, period, currentReading, readingDate?, evidenceFile, source=manual\|ocr` | `MeterReading` | Server suy ra `previousReading`, kiểm tra không lùi/trùng kỳ và tạo Media `meter_reading_evidence`. |
| `POST /buildings/{buildingId}/meter-reading-batches` | AUTH, owner | `period, type, items[{roomId,currentReading,evidenceUploadKey?}]` | batch summary | Ghi nhanh nhiều phòng từ UI; atomic theo từng item, trả lỗi từng phòng. Cần bảng bổ sung §15. |

---

## 9. Invoice và Payment

Invoice là snapshot bất biến khi phát hành. Không sửa line item đã `issued`; nếu cần điều chỉnh, hủy và phát hành lại theo rule nghiệp vụ.

### 9.1 Invoice

| Method & path | Quyền | Body/query chính | Kết quả | Ghi chú |
|---|---|---|---|---|
| `GET /invoices` | AUTH | `roomId?, contractId?, status?, period?, view=managed\|mine, offset, limit, sort` | `Invoice[]` | Một endpoint cho danh sách hóa đơn chủ nhà và tenant. |
| `POST /rooms/{roomId}/invoices` | AUTH, owner | `contractId, period, otherFees?, note?` | `Invoice` preview | Tính tiền phòng/pro-rate và breakdown ở server từ meter/policy; `otherFees.amount` có thể âm. |
| `GET /invoices/{invoiceId}` | AUTH, related | — | `InvoiceDetail` | Gồm line items, balance, QR payload khi có thể thanh toán. |
| `PATCH /invoices/{invoiceId}` | AUTH, owner | `otherFees?, note?` | `Invoice` | Chỉ `pending` khi chưa `issuedAt`; mọi chỉnh sửa được audit. |
| `POST /invoices/{invoiceId}/issue` | AUTH, owner | — | `Invoice` | Chốt snapshot, set `issuedAt` và gửi notification. Hạn thanh toán resolve từ BillingSetting. |
| `POST /invoices/{invoiceId}/cancel` | AUTH, owner | `reason` | `Invoice` | Không xóa; `invoiceStatus=cancel`. Có thể tạo Invoice thay thế cùng kỳ. |
| `GET /invoices/{invoiceId}/document` | AUTH, related | — | signed PDF URL | Bản in hóa đơn cho màn chi tiết; PDF tạo từ Invoice snapshot. |
| `GET /debts` | AUTH, owner | `buildingId?, overdueOnly=true, offset, limit` | `Invoice[]` + totals | Màn công nợ; là view từ Invoice, không tạo bảng `Debt` riêng. |
| `POST /debts/reminders` | AUTH, owner | `invoiceIds[], channel=app` | `{acceptedCount, skipped[]}` | Gộp nhắc từng/bulk. V1 chỉ notification trong app, không Zalo/SMS. |
| `GET /debts/export` | AUTH, owner | `buildingId?, overdueOnly?, format=csv` | signed download URL | Export từ đúng filter màn công nợ; tác vụ hiếm nên không tạo resource report riêng. |
| `GET /invoices/export` | AUTH, owner | `buildingId?, period?, status?, format=xlsx\|csv` | signed download URL / file stream | Xuất danh sách toàn bộ hóa đơn phát hành theo kỳ/tòa nhà/trạng thái ra file Excel/CSV theo nút trên UI. |

### 9.2 Payment

| Method & path | Quyền | Body/query chính | Kết quả | Ghi chú |
|---|---|---|---|---|
| `GET /invoices/{invoiceId}/payments` | AUTH, related | `offset, limit` | `Payment[]` | Người thuê và chủ nhà cùng xem giao dịch của hóa đơn hợp lệ. |
| `POST /invoices/{invoiceId}/payment-intents` | AUTH, contract member | `provider=vnpay\|momo\|vietqr\|mock, amount` | `Payment` pending + checkout params | Với VietQR trả payload QR; với cổng trả URL/deep link. `Idempotency-Key` bắt buộc. |
| `POST /invoices/{invoiceId}/cash-payments` | AUTH, owner | `amount, paidAt, note?` | `Payment` | Ghi nhận tiền mặt; không cho tenant tự đánh dấu đã trả. |
| `POST /payments/webhooks/{provider}` | Provider signed | raw provider payload | `204` | Endpoint nội bộ/public theo chữ ký provider; cập nhật Payment/Invoice idempotent. |

---

## 10. IssueReport

V1 chỉ xử lý sự cố gắn với phòng/hợp đồng, đúng phạm vi UI và bảng `IssueReport`; không thêm module tài sản/bảo trì riêng.

| Method & path | Quyền | Body/query chính | Kết quả | Ghi chú |
|---|---|---|---|---|
| `GET /issues` | AUTH | `roomId?, contractId?, status?, view=managed\|mine, offset, limit, sort` | `IssueReport[]` | Chủ nhà xem issue của phòng quản lý; tenant xem issue hợp đồng mình. |
| `POST /issues` | AUTH, related | multipart `roomId, title, description?, evidenceFiles?` | `IssueReport` | Tenant tạo cho phòng thuộc hợp đồng; owner có thể tạo thay tenant chưa có tài khoản. Server tạo Media `issue_photo` cùng transaction. |
| `GET /issues/{issueId}` | AUTH, related | — | `IssueReportDetail` | Gồm trạng thái hiện tại, note và evidence có quyền xem. |
| `PATCH /issues/{issueId}` | AUTH, owner/creator theo field | `status?, note?` | `IssueReport` | Tenant chỉ hủy issue `open` của mình; owner cập nhật `in_progress/resolved`. |
| `GET /issues/export` | AUTH, owner | `buildingId?, status?, priority?, format=xlsx` | signed download URL / file stream | Xuất báo cáo danh sách sự cố theo bộ lọc tòa nhà/trạng thái ra file Excel theo nút trên UI. |

---

## 11. Conversation, ConversationMember, Message và MessageMention

Conversation được tạo/lấy theo ngữ cảnh hiện có; không cho client tùy ý tạo room/building conversation trùng lặp. Chat trực tiếp sau ghép bạn dùng MatchRequest đã accept.

| Method & path | Quyền | Body/query chính | Kết quả | Ghi chú |
|---|---|---|---|---|
| `GET /conversations` | AUTH | `type?, offset, limit, sort=lastMessageAt` | `Conversation[]` | Chỉ conversation có `ConversationMember` là tôi. |
| `GET /conversations/{conversationId}` | AUTH, member | — | `ConversationDetail` | Gồm member và quyền chat. |
| `GET /conversations/{conversationId}/messages` | AUTH, member | `before?, limit` | `Message[]` | Cursor `before` cho chat; không dùng offset. |
| `POST /conversations/{conversationId}/messages` | AUTH, member | `content?, mediaIds?, mentionUserIds?` | `Message` | Cần ít nhất content hoặc media; backend tạo `MessageMention`. |
| `POST /conversations/{conversationId}/read` | AUTH, member | `lastReadMessageId` | `204` | Cập nhật unread/read marker của membership. |
| `GET /contracts/{contractId}/conversation` | AUTH, related | — | `Conversation` | Resolve chat phòng/hợp đồng, tạo khi hợp đồng active nếu chưa có. |
| `GET /buildings/{buildingId}/conversation` | AUTH, resident/owner | — | `Conversation` | Resolve chat tòa. |

---

## 12. Notification, NotificationPreference và PushDevice

| Method & path | Quyền | Body/query chính | Kết quả | Ghi chú |
|---|---|---|---|---|
| `GET /notifications` | AUTH | `unreadOnly?, offset, limit, sort=createdAt` | `Notification[]` | Notification của chính mình. |
| `POST /notifications/{notificationId}/read` | AUTH, owner | — | `204` | Đánh dấu đã đọc. |
| `POST /notifications/read-all` | AUTH | — | `204` | Màn inbox dùng để đọc toàn bộ. |
| `GET /me/notification-preference` | AUTH | — | `NotificationPreference` | Lấy các toggle hiện có. |
| `PUT /me/notification-preference` | AUTH | `items[{type=invoice\|chat\|issue\|match\|account, enabled}]` | `NotificationPreference[]` | Upsert preference của tôi theo từng nhóm. |

---

## 13. Admin và AuditLog

Các endpoint này mang prefix `/admin` vì là nghiệp vụ quản trị toàn hệ thống, không phải biến thể role của resource vận hành.

| Method & path | Quyền | Body/query chính | Kết quả | Ghi chú |
|---|---|---|---|---|
| `GET /admin/dashboard` | ADMIN | `from?, to?` | KPI dashboard | Tổng quan user, building, room, invoice, payment, issue. |
| `GET /admin/users` | ADMIN | `q, role?, status?, offset, limit` | `User[]` | Danh sách tài khoản người dùng, lọc theo vai trò/trạng thái hoặc từ khóa tìm kiếm. |
| `POST /admin/users` | ADMIN | `fullName, email, phone, role, tempPassword?, sendWelcomeEmail?` | `User` | Quản trị viên chủ động tạo tài khoản chủ nhà hoặc người dùng từ nút 'Thêm người dùng' trên UI. |
| `GET /admin/users/export` | ADMIN | `q?, role?, status?, format=xlsx` | signed download URL / file stream | Xuất danh sách tài khoản người dùng theo bộ lọc ra file Excel theo nút trên UI. |
| `GET /admin/users/{userId}` | ADMIN | — | `UserDetail` | Có lịch sử trạng thái phù hợp. |
| `POST /admin/users/{userId}/lock` | ADMIN | `reason` | `User` | Khóa tài khoản, giữ audit. |
| `POST /admin/users/{userId}/unlock` | ADMIN | `reason?` | `User` | Mở khóa tài khoản. |
| `GET /admin/buildings` | ADMIN | `status?, q, offset, limit` | `Building[]` | Hàng chờ kiểm duyệt tòa. |
| `POST /admin/buildings/{buildingId}/approve` | ADMIN | `note?` | `Building` | Hiển thị public sau khi đủ điều kiện. |
| `POST /admin/buildings/{buildingId}/reject` | ADMIN | `note` | `Building` | Lưu note từ chối; chủ nhà nhận notification. |
| `GET /admin/audit-logs` | ADMIN | `actorUserId?, entityType?, entityId?, from?, to?, offset, limit` | `AuditLog[]` | Truy vấn lịch sử nhật ký kiểm toán hệ thống. |
| `GET /admin/audit-logs/export` | ADMIN | `actorUserId?, entityType?, entityId?, from?, to?, format=csv\|json` | signed download URL / file stream | Xuất lịch sử nhật ký kiểm toán theo khoảng thời gian/bộ lọc ra file theo nút trên UI. |
| `GET /admin/audit-logs/{auditLogId}/export` | ADMIN | `format=csv\|json` | signed download URL / file stream | Xuất chi tiết một bản ghi kiểm toán cụ thể ra file theo popup UI. |

---

## 14. Coverage UI và các API cố ý không đưa vào

### 14.1 Luồng UI được giữ

| Luồng UI | Resource/API chính |
|---|---|
| Đăng nhập, đăng ký, quên mật khẩu | `User`, `AuthSession` (§2) |
| Tìm phòng, map, chi tiết, yêu thích | `Building`, `Room`, `FavoriteRoom` (§4–5) |
| Tìm bạn ở ghép | `RoommateProfile`, `MatchRequest`, `Conversation` (§5, §11) |
| Quản lý tòa/phòng, giá, cài đặt hóa đơn, VietQR | `Building`, `Room`, `RatePolicy`, `BillingSetting` (§4, §6) |
| Hợp đồng ký tay, thành viên, trả phòng | `Contract`, `ContractMember`, `Media` (§3, §7) |
| OCR/ghi số đơn lẻ và nhiều phòng | `MeterReading` (§8) |
| Hóa đơn, thanh toán, công nợ, nhắc nợ | `Invoice`, `Payment` (§9) |
| Báo sự cố | `IssueReport` (§10) |
| Tin nhắn, thông báo | `Conversation`, `Message`, `Notification` (§11–12) |
| Dashboard/kiểm duyệt/khóa user | Admin, `AuditLog` (§13) |

### 14.2 Đã loại khỏi v1

- `/tenant/*`, `/landlord/*`: thay toàn bộ bằng resource chung và kiểm tra quan hệ.
- Quản lý thiết bị/phiên đăng nhập (`GET /me/sessions`, revoke other devices): giữ phiên hiện tại ở v1. Các chức năng xuất file Excel/PDF (hóa đơn, thành viên, sự cố, audit log, người dùng) và tạo người dùng quản trị được hỗ trợ tương ứng với các nút bấm trên giao diện Web.
- Zalo/SMS, gọi thoại/video, lịch hẹn, quản lý tài sản–kỹ thuật viên, khai báo tạm trú, social feed, import dữ liệu, AI viết mô tả: không thuộc scope/không có UI được chốt.
- API tạo admin, đổi role, xóa cứng hợp đồng/hóa đơn/thanh toán/chỉ số/chứng từ: không an toàn hoặc không cần UI.
- Quote giá, preset giá, campaign nhắc nợ có trạng thái/polling: thay bằng tính giá server-side và `POST /debts/reminders` đơn giản.

---

## 15. Migration/tables cần chốt trước khi triển khai

Các resource dưới đây xuất hiện trong UI nhưng chưa được mô tả đủ trong `database-design.md`; cần migration rõ ràng, không “giấu” dữ liệu vào JSON tùy tiện.

| Cần bổ sung/chỉnh | Lý do |
|---|---|
| `AuthSession`, `PasswordResetToken` | Refresh-token rotation, logout và reset password ở §2. Hai bảng kỹ thuật, không cần endpoint quản lý session. |
| `RatePolicy.scope`, `BillingSetting.scope` có thêm giá trị `landlord` | Database mô tả chuỗi kế thừa room → building → landlord nhưng enum hiện chỉ có building/room; cần thống nhất trước khi dùng default cấp chủ nhà ở §6. |
| `VietQrReceiverConfig` (`buildingId`, bank/account data đã mã hóa, active) | UI cài đặt VietQR; không nên nhét tài khoản nhận tiền vào `Building`. |
| `MeterReadingBatch`, `MeterReadingBatchItem` | Lưu kết quả ghi số nhiều phòng, retry/audit từng item ở §8. |
| `Room.status` có `cleaning_pending` | Phù hợp luồng checkout → dọn → `POST /rooms/{id}/ready`. |
| `MatchRequest` có trạng thái `cancelled` hoặc unique index partial theo `is_deleted=false` | Cho phép người gửi hủy request pending rồi gửi lại mà vẫn giữ lịch sử. |
| `ConversationMember.lastReadMessageId/lastReadAt` | Hiển thị unread chính xác cho chat. |

## 16. Quyết định cần chốt với BE/FE

1. Chọn danh sách trạng thái chuẩn cho `Room`, `Contract`, `Invoice`, `Payment`, `IssueReport`, `MatchRequest`; dùng enum dùng chung giữa OpenAPI, BE và FE.
2. Chốt provider thanh toán thật (`vnpay`, `momo` hay chỉ `vietqr`) trước khi implement intent/webhook.
3. Chốt quy tắc khi số điện/nước thấp hơn kỳ trước: block, cần xác nhận, hay tạo issue review.
4. Chốt chính sách tenant chưa có tài khoản trong `ContractMember` và cách mời/liên kết tài khoản sau này.

Sau khi bốn điểm trên được chốt, tài liệu này có thể chuyển trực tiếp thành `openapi.yaml`; không cần tạo các namespace role riêng.

---

## 17. Chi tiết Kỹ thuật các API và Trường Dữ liệu

---

### 17.1 Nhóm User & AuthSession (Người dùng & Xác thực phiên)

#### 1. POST /auth/register
* **Method:** `POST`
* **Endpoint:** `/auth/register`
* **Quyền hạn:** `PUBLIC`
* **Dẫn chứng UI:**
  - Thư mục: `4._ng_k_ch_nh_sign_up/code.html`, `4._ng_k_sign_up/code.html`, `5._ng_k_sign_up/code.html`
  - Vị trí UI: Form đăng ký tài khoản khách hàng / chủ trọ mới, gồm các trường: Họ và tên, Email, Số điện thoại, Vai trò (Người thuê / Chủ trọ), Mật khẩu và Xác nhận mật khẩu, checkbox đồng ý điều khoản dịch vụ và nút bấm **"Đăng ký tài khoản"**.
* **Request Payload (application/json):**
```json
{
  "fullName": "Nguyễn Văn An",
  "email": "nguyenvanan@example.com",
  "phoneNumber": "0912345678",
  "password": "Password123@",
  "role": "TENANT"
}
```
*Giải thích trường Request:*
- `fullName` *(string, required)*: Họ và tên đầy đủ của người dùng, tối đa 255 ký tự.
- `email` *(string, required)*: Địa chỉ email duy nhất trong hệ thống, đúng định dạng RFC 5322.
- `phoneNumber` *(string, required)*: Số điện thoại di động Việt Nam (10 chữ số, bắt đầu bằng đầu số hợp lệ).
- `password` *(string, required)*: Mật khẩu tối thiểu 8 ký tự, gồm ít nhất 1 chữ hoa, 1 số và 1 ký tự đặc biệt.
- `role` *(string, required)*: Enum vai trò khởi tạo: `TENANT` (Khách thuê) hoặc `LANDLORD` (Chủ nhà).
* **Response Mẫu (201 Created):**
```json
{
  "statusCode": 201,
  "message": "Đăng ký tài khoản thành công",
  "data": {
    "user": {
      "id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
      "fullName": "Nguyễn Văn An",
      "email": "nguyenvanan@example.com",
      "phoneNumber": "0912345678",
      "role": "TENANT",
      "isActive": true,
      "isPhoneVerified": false,
      "isEmailVerified": false,
      "createdAt": "2026-09-23T08:30:00Z"
    },
    "tokens": {
      "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refreshToken": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "expiresIn": 86400
    }
  }
}
```

---

#### 2. POST /auth/login
* **Method:** `POST`
* **Endpoint:** `/auth/login`
* **Quyền hạn:** `PUBLIC`
* **Dẫn chứng UI:**
  - Thư mục: `1._ng_nh_p_ch_nh_login/code.html`, `1._ng_nh_p_login/code.html`, `1._ng_nh_p_qu_n_tr_vi_n_admin_login/code.html`
  - Vị trí UI: Form đăng nhập chính gồm ô nhập Số điện thoại/Email, Mật khẩu, checkbox "Ghi nhớ đăng nhập" và nút **"Đăng nhập"**.
* **Request Payload (application/json):**
```json
{
  "identifier": "0912345678",
  "password": "Password123@",
  "rememberMe": true
}
```
*Giải thích trường Request:*
- `identifier` *(string, required)*: Số điện thoại hoặc Email tài khoản.
- `password` *(string, required)*: Mật khẩu đăng nhập.
- `rememberMe` *(boolean, optional)*: Duy trì phiên đăng nhập lâu dài (kéo dài thời hạn refresh token).
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Đăng nhập thành công",
  "data": {
    "user": {
      "id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
      "fullName": "Nguyễn Văn An",
      "email": "nguyenvanan@example.com",
      "phoneNumber": "0912345678",
      "avatarUrl": "https://storage.rentify.vn/avatars/user1.png",
      "role": "TENANT",
      "isActive": true
    },
    "tokens": {
      "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refreshToken": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "expiresIn": 86400
    }
  }
}
```

---

#### 3. POST /auth/refresh
* **Method:** `POST`
* **Endpoint:** `/auth/refresh`
* **Quyền hạn:** `Refresh session` (Cần refreshToken hợp lệ)
* **Dẫn chứng UI:**
  - Thư mục: Tự động chạy ngầm trên tất cả các trang web (`rentify_tenant_interface`, dashboard) khi access token hết hạn (HTTP 401 interceptor).
* **Request Payload (application/json):**
```json
{
  "refreshToken": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Làm mới phiên đăng nhập thành công",
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.new...",
    "refreshToken": "8d0f7780-8536-41ef-055c-f18gd2g01bf8",
    "expiresIn": 86400
  }
}
```

---

#### 4. POST /auth/logout
* **Method:** `POST`
* **Endpoint:** `/auth/logout`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `4._x_c_nh_n_ng_xu_t_logout_confirmation/code.html`, `6._x_c_nh_n_ng_xu_t_logout_modal_1/code.html`, `7._x_c_nh_n_ng_xu_t_logout_modal/code.html`
  - Vị trí UI: Nút "Đăng xuất" trên menu tài khoản cá nhân & Modal xác nhận "Bạn có chắc chắn muốn đăng xuất?" kèm nút xác nhận **"Đăng xuất"**.
* **Request Payload (application/json):**
```json
{
  "refreshToken": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Đăng xuất thành công",
  "data": null
}
```

---

#### 5. POST /auth/password-reset-requests
* **Method:** `POST`
* **Endpoint:** `/auth/password-reset-requests`
* **Quyền hạn:** `PUBLIC`
* **Dẫn chứng UI:**
  - Thư mục: `2._qu_n_m_t_kh_u_forgot_password_1/code.html`, `2._qu_n_m_t_kh_u_forgot_password_2/code.html`, `3._qu_n_m_t_kh_u_forgot_password/code.html`
  - Vị trí UI: Form quên mật khẩu, trường nhập "Email hoặc Số điện thoại" đã đăng ký và nút **"Gửi mã xác nhận OTP"**.
* **Request Payload (application/json):**
```json
{
  "identifier": "nguyenvanan@example.com",
  "deliveryChannel": "EMAIL"
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Mã xác thực khôi phục mật khẩu đã được gửi thành công",
  "data": {
    "resetTokenId": "b1fe3c44-5d6e-47f2-901a-123456789abc",
    "deliveryMasked": "n***n@example.com",
    "expiresInSeconds": 300
  }
}
```

---

#### 6. POST /auth/password-resets
* **Method:** `POST`
* **Endpoint:** `/auth/password-resets`
* **Quyền hạn:** `PUBLIC`
* **Dẫn chứng UI:**
  - Thư mục: `3._t_l_i_m_t_kh_u_reset_password_1/code.html`, `4._t_l_i_m_t_kh_u_reset_password/code.html`
  - Vị trí UI: Form đặt lại mật khẩu gồm ô nhập 6 chữ số OTP, Mật khẩu mới, Xác nhận mật khẩu mới và nút **"Cập nhật mật khẩu"**.
* **Request Payload (application/json):**
```json
{
  "resetTokenId": "b1fe3c44-5d6e-47f2-901a-123456789abc",
  "otpCode": "654321",
  "newPassword": "NewPassword123@"
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Đặt lại mật khẩu thành công. Vui lòng đăng nhập lại.",
  "data": null
}
```

---

#### 7. GET /me
* **Method:** `GET`
* **Endpoint:** `/me`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: Header góc phải trên mọi trang, `31._h_s_c_nh_n_profile/code.html`, `50._h_s_c_nh_n_profile_1/code.html`
  - Vị trí UI: Thẻ tóm tắt thông tin người dùng ở góc trên thanh điều hướng và tab "Thông tin cá nhân".
* **Request:** Không có payload.
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy thông tin tài khoản thành công",
  "data": {
    "id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    "fullName": "Nguyễn Văn An",
    "email": "nguyenvanan@example.com",
    "phoneNumber": "0912345678",
    "avatarUrl": "https://storage.rentify.vn/avatars/user1.png",
    "role": "TENANT",
    "identityCardNumber": "079201001234",
    "identityCardIssuedDate": "2021-05-15",
    "identityCardIssuedPlace": "Cục Cảnh sát QLHC về TTXH",
    "permanentAddress": "123 Lê Lợi, Phường Bến Nghé, Quận 1, TP. Hồ Chí Minh",
    "isActive": true,
    "isPhoneVerified": true,
    "isEmailVerified": true,
    "createdAt": "2026-09-23T08:30:00Z"
  }
}
```

---

#### 8. PATCH /me
* **Method:** `PATCH`
* **Endpoint:** `/me`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `31._h_s_c_nh_n_profile/code.html`, `50._h_s_c_nh_n_profile_1/code.html`, `50._h_s_c_nh_n_profile_2/code.html`
  - Vị trí UI: Form cập nhật thông tin cá nhân: Họ tên, Số CCCD, Ngày cấp, Nơi cấp, Địa chỉ thường trú, Avatar và nút **"Lưu thay đổi"**.
* **Request Payload (application/json):**
```json
{
  "fullName": "Nguyễn Văn An",
  "avatarUrl": "https://storage.rentify.vn/avatars/new-avatar.png",
  "identityCardNumber": "079201001234",
  "identityCardIssuedDate": "2021-05-15",
  "identityCardIssuedPlace": "Cục Cảnh sát QLHC về TTXH",
  "permanentAddress": "123 Lê Lợi, Phường Bến Nghé, Quận 1, TP. Hồ Chí Minh"
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Cập nhật hồ sơ cá nhân thành công",
  "data": {
    "id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    "fullName": "Nguyễn Văn An",
    "email": "nguyenvanan@example.com",
    "phoneNumber": "0912345678",
    "avatarUrl": "https://storage.rentify.vn/avatars/new-avatar.png",
    "role": "TENANT",
    "identityCardNumber": "079201001234",
    "identityCardIssuedDate": "2021-05-15",
    "identityCardIssuedPlace": "Cục Cảnh sát QLHC về TTXH",
    "permanentAddress": "123 Lê Lợi, Phường Bến Nghé, Quận 1, TP. Hồ Chí Minh",
    "updatedAt": "2026-09-23T09:15:00Z"
  }
}
```

---

#### 9. PUT /me/password
* **Method:** `PUT`
* **Endpoint:** `/me/password`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `31._h_s_c_nh_n_profile/code.html` (Tab Đổi mật khẩu / Bảo mật)
  - Vị trí UI: Form gồm ô Mật khẩu hiện tại, Mật khẩu mới, Xác nhận mật khẩu mới và nút **"Đổi mật khẩu"**.
* **Request Payload (application/json):**
```json
{
  "currentPassword": "Password123@",
  "newPassword": "NewSecurePassword456@"
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Đổi mật khẩu thành công. Vui lòng sử dụng mật khẩu mới cho lần đăng nhập sau.",
  "data": null
}
```

---

#### 10. POST /me/push-devices
* **Method:** `POST`
* **Endpoint:** `/me/push-devices`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: Khởi tạo trên trình duyệt web khi người dùng bấm "Cho phép nhận thông báo" trên prompt Web Push Notification.
* **Request Payload (application/json):**
```json
{
  "deviceToken": "fcm_token_chrome_web_push_xyz123...",
  "deviceType": "WEB",
  "browserName": "Chrome 128 on macOS"
}
```
* **Response Mẫu (201 Created):**
```json
{
  "statusCode": 201,
  "message": "Đăng ký thiết bị nhận thông báo thành công",
  "data": {
    "deviceId": "dev_99887766-5544-3322-1100-aabbccddeeff",
    "registeredAt": "2026-09-23T09:20:00Z"
  }
}
```

---

#### 11. DELETE /me/push-devices/{deviceId}
* **Method:** `DELETE`
* **Endpoint:** `/me/push-devices/{deviceId}`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `32._c_i_t_th_ng_b_o_notification_settings/code.html`, `51._c_i_t_th_ng_b_o_notification_settings_1/code.html`
  - Vị trí UI: Danh sách thiết bị đã liên kết trong cài đặt thông báo, nút icon thùng rác **"Gỡ thiết bị"**.
* **Request:** Path parameter `deviceId` (string).
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Hủy đăng ký thiết bị nhận thông báo thành công",
  "data": null
}
```

---

### 17.2 Nhóm Media (Tài liệu, Ảnh, Tệp đính kèm)

#### 12. POST /media
* **Method:** `POST`
* **Endpoint:** `/media`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `11._t_i_gi_y_t_s_h_u_b_c_2_3_upload_documents_step_2_3/code.html`, `22._t_i_l_n_h_p_ng_k_upload_signed_lease/code.html`, `30._b_o_c_o_s_c_m_i_report_an_issue/code.html`, `30._ch_p_nh_c_ng_t_qua_webcam_webcam_meter_photo/code.html`
  - Vị trí UI: Vùng kéo thả file/nút "Tải ảnh lên" (Dropzone) hoặc nút chụp webcam công tơ điện nước.
* **Request Payload (multipart/form-data):**
  - `file`: Binary file (JPEG, PNG, PDF, v.v., tối đa 20MB).
  - `entityType`: String (`ROOM`, `BUILDING`, `CONTRACT`, `ISSUE_REPORT`, `METER_READING`, `PAYMENT`, `USER_AVATAR`).
  - `entityId`: UUID (optional khi upload draft).
* **Response Mẫu (201 Created):**
```json
{
  "statusCode": 201,
  "message": "Tải lên tệp tin thành công",
  "data": {
    "id": "c3d4e5f6-7a8b-9c0d-1e2f-3a4b5c6d7e8f",
    "mediaUrl": "https://storage.rentify.vn/uploads/2026/09/meter_photo_p101.jpg",
    "fileName": "meter_photo_p101.jpg",
    "fileType": "image/jpeg",
    "fileSizeBytes": 2048500,
    "mediaType": "IMAGE",
    "entityType": "METER_READING",
    "entityId": null,
    "createdAt": "2026-09-23T09:25:00Z"
  }
}
```

---

#### 13. GET /media/{mediaId}
* **Method:** `GET`
* **Endpoint:** `/media/{mediaId}`
* **Quyền hạn:** `Theo resource cha`
* **Dẫn chứng UI:**
  - Thư mục: `23._xem_h_p_ng_thu_view_lease/code.html`, `29._chi_ti_t_s_c_issue_detail_popup/code.html`
  - Vị trí UI: Xem trước ảnh chụp công tơ, xem ảnh giấy tờ quyền sở hữu hoặc bấm tải file hợp đồng đã ký.
* **Request:** Path parameter `mediaId` (UUID).
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy thông tin tệp tin thành công",
  "data": {
    "id": "c3d4e5f6-7a8b-9c0d-1e2f-3a4b5c6d7e8f",
    "mediaUrl": "https://storage.rentify.vn/uploads/2026/09/meter_photo_p101.jpg?signed=true&expires=1727083500",
    "fileName": "meter_photo_p101.jpg",
    "fileType": "image/jpeg",
    "fileSizeBytes": 2048500,
    "mediaType": "IMAGE",
    "createdAt": "2026-09-23T09:25:00Z"
  }
}
```

---

#### 14. DELETE /media/{mediaId}
* **Method:** `DELETE`
* **Endpoint:** `/media/{mediaId}`
* **Quyền hạn:** `AUTH, quyền sửa resource cha`
* **Dẫn chứng UI:**
  - Thư mục: `16._th_m_ph_ng_m_i_add_new_room/code.html`, `30._b_o_c_o_s_c_m_i_report_an_issue/code.html`
  - Vị trí UI: Nút icon "X" xóa ảnh đã đính kèm trong danh sách thumbnail trước khi nộp form.
* **Request:** Path parameter `mediaId` (UUID).
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Xóa tệp tin thành công",
  "data": null
}
```

---

### 17.3 Nhóm Building & Room (Quản lý Tòa nhà & Phòng trọ)

#### 15. GET /buildings
* **Method:** `GET`
* **Endpoint:** `/buildings`
* **Quyền hạn:** `PUBLIC/AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `9._danh_s_ch_t_a_nh_building_list/code.html`, `8b._b_ng_i_u_khi_n_v_n_h_nh_y_dashboard_full_state/code.html`
  - Vị trí UI: Bảng danh sách các tòa nhà quản lý của chủ trọ, bộ lọc theo tên tòa nhà, địa bàn quận/huyện, trạng thái hoạt động và phân trang.
* **Query Parameters:**
  - `keyword` *(string, optional)*: Tìm kiếm theo tên tòa nhà hoặc địa chỉ.
  - `status` *(string, optional)*: `DRAFT`, `PENDING_APPROVAL`, `ACTIVE`, `REJECTED`, `INACTIVE`.
  - `city` *(string, optional)*: Lọc theo tỉnh/thành phố.
  - `pageNo` *(integer, default=1)*: Số trang.
  - `pageSize` *(integer, default=10)*: Số bản ghi mỗi trang.
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy danh sách tòa nhà thành công",
  "data": {
    "items": [
      {
        "id": "e4f5a6b7-c8d9-0123-ef45-6789abcdef01",
        "name": "Tòa nhà Rentify Central Park",
        "addressLine": "123 Nguyễn Thị Minh Khai",
        "ward": "Phường Võ Thị Sáu",
        "district": "Quận 3",
        "city": "TP. Hồ Chí Minh",
        "totalFloors": 5,
        "totalRooms": 20,
        "occupiedRooms": 18,
        "status": "ACTIVE",
        "coverImageUrl": "https://storage.rentify.vn/buildings/central_park_cover.jpg",
        "createdAt": "2026-08-01T10:00:00Z"
      }
    ],
    "pagination": {
      "pageNo": 1,
      "pageSize": 10,
      "totalItems": 1,
      "totalPages": 1
    }
  }
}
```

---

#### 16. POST /buildings
* **Method:** `POST`
* **Endpoint:** `/buildings`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `10._th_m_t_a_nh_b_c_1_3_add_building_step_1_3/code.html`, `11._t_i_gi_y_t_s_h_u_b_c_2_3_upload_documents_step_2_3/code.html`
  - Vị trí UI: Form thêm mới tòa nhà (Bước 1/3 thông tin chung & Bước 2/3 giấy tờ sở hữu) kèm nút bấm **"Lưu và Tiếp tục"** / **"Hoàn tất tạo tòa nhà"**.
* **Request Payload (application/json):**
```json
{
  "name": "Tòa nhà Rentify Central Park",
  "addressLine": "123 Nguyễn Thị Minh Khai",
  "ward": "Phường Võ Thị Sáu",
  "district": "Quận 3",
  "city": "TP. Hồ Chí Minh",
  "totalFloors": 5,
  "ownershipDocumentMediaIds": [
    "c3d4e5f6-7a8b-9c0d-1e2f-3a4b5c6d7e8f",
    "d4e5f6a7-8b9c-0d1e-2f3a-4b5c6d7e8f90"
  ]
}
```
* **Response Mẫu (201 Created):**
```json
{
  "statusCode": 201,
  "message": "Tạo tòa nhà mới thành công. Hồ sơ đang chờ kiểm duyệt.",
  "data": {
    "id": "e4f5a6b7-c8d9-0123-ef45-6789abcdef01",
    "landlordId": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    "name": "Tòa nhà Rentify Central Park",
    "addressLine": "123 Nguyễn Thị Minh Khai",
    "ward": "Phường Võ Thị Sáu",
    "district": "Quận 3",
    "city": "TP. Hồ Chí Minh",
    "totalFloors": 5,
    "totalRooms": 0,
    "status": "PENDING_APPROVAL",
    "createdAt": "2026-09-23T09:30:00Z"
  }
}
```

---

#### 17. GET /buildings/{buildingId}
* **Method:** `GET`
* **Endpoint:** `/buildings/{buildingId}`
* **Quyền hạn:** `PUBLIC/AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `13._chi_ti_t_t_a_nh_building_detail/code.html`
  - Vị trí UI: Màn hình chi tiết tòa nhà: thẻ thông số tổng quan (số phòng trống, đã thuê, tỷ lệ lấp đầy), thông tin pháp lý, danh sách phòng và tiện ích tòa nhà.
* **Request:** Path parameter `buildingId` (UUID).
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy chi tiết tòa nhà thành công",
  "data": {
    "id": "e4f5a6b7-c8d9-0123-ef45-6789abcdef01",
    "landlordId": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    "name": "Tòa nhà Rentify Central Park",
    "addressLine": "123 Nguyễn Thị Minh Khai",
    "ward": "Phường Võ Thị Sáu",
    "district": "Quận 3",
    "city": "TP. Hồ Chí Minh",
    "totalFloors": 5,
    "totalRooms": 20,
    "occupiedRooms": 18,
    "availableRooms": 2,
    "status": "ACTIVE",
    "documents": [
      {
        "id": "c3d4e5f6-7a8b-9c0d-1e2f-3a4b5c6d7e8f",
        "fileName": "so_hong_toa_nha.pdf",
        "mediaUrl": "https://storage.rentify.vn/uploads/so_hong_toa_nha.pdf"
      }
    ],
    "vietQrConfigured": true,
    "createdAt": "2026-08-01T10:00:00Z"
  }
}
```

---

#### 18. PATCH /buildings/{buildingId}
* **Method:** `PATCH`
* **Endpoint:** `/buildings/{buildingId}`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `13._chi_ti_t_t_a_nh_building_detail/code.html`
  - Vị trí UI: Modal "Chỉnh sửa thông tin tòa nhà" kèm nút **"Lưu cập nhật"**.
* **Request Payload (application/json):**
```json
{
  "name": "Tòa nhà Rentify Central Park (Khu B)",
  "totalFloors": 6
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Cập nhật thông tin tòa nhà thành công",
  "data": {
    "id": "e4f5a6b7-c8d9-0123-ef45-6789abcdef01",
    "name": "Tòa nhà Rentify Central Park (Khu B)",
    "totalFloors": 6,
    "updatedAt": "2026-09-23T09:35:00Z"
  }
}
```

---

#### 19. PUT /buildings/{buildingId}/vietqr-config
* **Method:** `PUT`
* **Endpoint:** `/buildings/{buildingId}/vietqr-config`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `14._c_u_h_nh_t_i_kho_n_vietqr_t_a_nh_configure_building_vietqr/code.html`
  - Vị trí UI: Form cấu hình tài khoản nhận tiền VietQR: Ngân hàng thụ hưởng, Số tài khoản, Tên chủ tài khoản, mã nạp và nút **"Lưu cấu hình VietQR"**.
* **Request Payload (application/json):**
```json
{
  "bankCode": "ICB",
  "bankName": "VietinBank - Ngân hàng TMCP Công Thương Việt Nam",
  "accountNumber": "102876543210",
  "accountHolderName": "NGUYEN VAN AN",
  "qrTemplate": "compact2",
  "isActive": true
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Cấu hình tài khoản VietQR tòa nhà thành công",
  "data": {
    "buildingId": "e4f5a6b7-c8d9-0123-ef45-6789abcdef01",
    "bankCode": "ICB",
    "bankName": "VietinBank - Ngân hàng TMCP Công Thương Việt Nam",
    "accountNumberMasked": "1028****3210",
    "accountHolderName": "NGUYEN VAN AN",
    "isActive": true,
    "updatedAt": "2026-09-23T09:40:00Z"
  }
}
```

---

#### 20. GET /buildings/{buildingId}/vietqr-config
* **Method:** `GET`
* **Endpoint:** `/buildings/{buildingId}/vietqr-config`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `14._c_u_h_nh_t_i_kho_n_vietqr_t_a_nh_configure_building_vietqr/code.html`
  - Vị trí UI: Thẻ hiển thị tài khoản nhận tiền VietQR hiện tại của tòa nhà kèm mã QR demo.
* **Request:** Path parameter `buildingId` (UUID).
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy cấu hình VietQR thành công",
  "data": {
    "buildingId": "e4f5a6b7-c8d9-0123-ef45-6789abcdef01",
    "bankCode": "ICB",
    "bankName": "VietinBank",
    "accountNumber": "102876543210",
    "accountHolderName": "NGUYEN VAN AN",
    "qrTemplate": "compact2",
    "isActive": true
  }
}
```

---

#### 21. GET /rooms
* **Method:** `GET`
* **Endpoint:** `/rooms`
* **Quyền hạn:** `PUBLIC/AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `8._trang_ch_danh_s_ch_ph_ng_home_room_list/code.html`, `15._s_danh_s_ch_ph_ng_room_list_room_map/code.html`
  - Vị trí UI: Danh sách lưới thẻ phòng trọ kèm thanh tìm kiếm, bộ lọc khoảng giá thuê, diện tích, số người ở, tiện ích và chế độ xem bản đồ vị trí.
* **Query Parameters:**
  - `buildingId` *(UUID, optional)*: Lọc theo tòa nhà cụ thể.
  - `status` *(string, optional)*: `AVAILABLE`, `OCCUPIED`, `MAINTENANCE`, `CLEANING_PENDING`.
  - `minPrice` / `maxPrice` *(integer, optional)*: Khoảng giá thuê (VNĐ).
  - `minArea` / `maxArea` *(number, optional)*: Khoảng diện tích (m2).
  - `pageNo` / `pageSize` *(integer)*: Phân trang.
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy danh sách phòng thành công",
  "data": {
    "items": [
      {
        "id": "f5a6b7c8-d9e0-1234-fa56-789abcdef012",
        "buildingId": "e4f5a6b7-c8d9-0123-ef45-6789abcdef01",
        "buildingName": "Tòa nhà Rentify Central Park",
        "roomNumber": "P.302",
        "floor": 3,
        "areaSqm": 28.5,
        "basePriceMonthly": 4500000,
        "depositAmount": 4500000,
        "maxOccupants": 3,
        "status": "AVAILABLE",
        "coverImageUrl": "https://storage.rentify.vn/rooms/p302_main.jpg",
        "amenities": ["AIR_CONDITIONER", "WATER_HEATER", "BALCONY", "WIFI"]
      }
    ],
    "pagination": {
      "pageNo": 1,
      "pageSize": 12,
      "totalItems": 1,
      "totalPages": 1
    }
  }
}
```

---

#### 22. POST /buildings/{buildingId}/rooms
* **Method:** `POST`
* **Endpoint:** `/buildings/{buildingId}/rooms`
* **Quyền hạn:** `AUTH, building owner`
* **Dẫn chứng UI:**
  - Thư mục: `16._th_m_ph_ng_m_i_add_new_room/code.html`
  - Vị trí UI: Form thêm mới phòng trọ: Số phòng, Tầng, Diện tích, Giá thuê hàng tháng, Tiền đặt cọc, Số người ở tối đa, Checkbox các tiện nghi phòng và nút **"Tạo phòng mới"**.
* **Request Payload (application/json):**
```json
{
  "roomNumber": "P.302",
  "floor": 3,
  "areaSqm": 28.5,
  "basePriceMonthly": 4500000,
  "depositAmount": 4500000,
  "maxOccupants": 3,
  "description": "Phòng khép kín đầy đủ máy lạnh, ban công thoáng mát.",
  "amenities": ["AIR_CONDITIONER", "WATER_HEATER", "BALCONY"],
  "mediaIds": [
    "c3d4e5f6-7a8b-9c0d-1e2f-3a4b5c6d7e8f"
  ]
}
```
* **Response Mẫu (201 Created):**
```json
{
  "statusCode": 201,
  "message": "Thêm phòng mới thành công",
  "data": {
    "id": "f5a6b7c8-d9e0-1234-fa56-789abcdef012",
    "buildingId": "e4f5a6b7-c8d9-0123-ef45-6789abcdef01",
    "roomNumber": "P.302",
    "floor": 3,
    "areaSqm": 28.5,
    "basePriceMonthly": 4500000,
    "depositAmount": 4500000,
    "maxOccupants": 3,
    "status": "AVAILABLE",
    "createdAt": "2026-09-23T09:45:00Z"
  }
}
```

---

#### 23. GET /rooms/{roomId}
* **Method:** `GET`
* **Endpoint:** `/rooms/{roomId}`
* **Quyền hạn:** `PUBLIC/AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `11._chi_ti_t_ph_ng_room_detail/code.html`, `17._chi_ti_t_ph_ng_room_detail_1/code.html`, `22._trung_t_m_ph_ng_c_a_t_i_my_room_hub/code.html`
  - Vị trí UI: Màn hình chi tiết phòng: Bộ sưu tập ảnh phòng, biểu phí dịch vụ (điện nước), thông tin tòa nhà, vị trí bản đồ, thông tin người thuê hiện tại (nếu là chủ nhà/khách thuê).
* **Request:** Path parameter `roomId` (UUID).
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy chi tiết phòng thành công",
  "data": {
    "id": "f5a6b7c8-d9e0-1234-fa56-789abcdef012",
    "building": {
      "id": "e4f5a6b7-c8d9-0123-ef45-6789abcdef01",
      "name": "Tòa nhà Rentify Central Park",
      "addressLine": "123 Nguyễn Thị Minh Khai, P. Võ Thị Sáu, Q.3, TP.HCM"
    },
    "roomNumber": "P.302",
    "floor": 3,
    "areaSqm": 28.5,
    "basePriceMonthly": 4500000,
    "depositAmount": 4500000,
    "maxOccupants": 3,
    "status": "AVAILABLE",
    "description": "Phòng khép kín đầy đủ máy lạnh, ban công thoáng mát.",
    "amenities": ["AIR_CONDITIONER", "WATER_HEATER", "BALCONY"],
    "images": [
      "https://storage.rentify.vn/rooms/p302_1.jpg",
      "https://storage.rentify.vn/rooms/p302_2.jpg"
    ],
    "currentContract": null,
    "createdAt": "2026-09-23T09:45:00Z"
  }
}
```

---

#### 24. PATCH /rooms/{roomId}
* **Method:** `PATCH`
* **Endpoint:** `/rooms/{roomId}`
* **Quyền hạn:** `AUTH, room/building owner`
* **Dẫn chứng UI:**
  - Thư mục: `17._chi_ti_t_ph_ng_room_detail_1/code.html`
  - Vị trí UI: Nút "Chỉnh sửa thông tin phòng" và Modal cập nhật giá phòng, tiền cọc, tiện ích hoặc trạng thái bảo trì.
* **Request Payload (application/json):**
```json
{
  "basePriceMonthly": 4700000,
  "depositAmount": 4700000,
  "status": "MAINTENANCE"
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Cập nhật thông tin phòng thành công",
  "data": {
    "id": "f5a6b7c8-d9e0-1234-fa56-789abcdef012",
    "roomNumber": "P.302",
    "basePriceMonthly": 4700000,
    "depositAmount": 4700000,
    "status": "MAINTENANCE",
    "updatedAt": "2026-09-23T09:50:00Z"
  }
}
```

---

#### 25. POST /rooms/{roomId}/ready
* **Method:** `POST`
* **Endpoint:** `/rooms/{roomId}/ready`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `47._tr_ng_th_i_ch_d_n_v_sinh_nghi_m_thu_pending_cleanup_status/code.html`
  - Vị trí UI: Thẻ cảnh báo phòng đang ở trạng thái `CLEANING_PENDING` (chờ dọn dẹp sau khi khách cũ trả phòng) kèm nút bấm nổi bật **"Nghiệm thu hoàn tất & Sẵn sàng cho thuê"**.
* **Request Payload (application/json):**
```json
{
  "inspectionNotes": "Đã hoàn thành dọn vệ sinh, sơn lại tường và thay bóng đèn mới."
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Nghiệm thu phòng thành công. Trạng thái phòng chuyển sang SẴN SÀNG CHO THUÊ.",
  "data": {
    "id": "f5a6b7c8-d9e0-1234-fa56-789abcdef012",
    "roomNumber": "P.302",
    "status": "AVAILABLE",
    "updatedAt": "2026-09-23T09:55:00Z"
  }
}
```

---

### 17.4 Nhóm FavoriteRoom, RoommateProfile & MatchRequest (Phòng yêu thích & Tìm bạn ở ghép)

#### 26. GET /me/favorite-rooms
* **Method:** `GET`
* **Endpoint:** `/me/favorite-rooms`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `10._ph_ng_l_u_saved_rooms/code.html`, `12._ph_ng_l_u_saved_rooms/code.html`
  - Vị trí UI: Danh sách thẻ các phòng trọ khách thuê đã nhấn lưu/thích, hiển thị giá phòng, địa chỉ, ảnh đại diện và nút liên hệ/xem chi tiết.
* **Query Parameters:**
  - `pageNo` *(integer, default=1)*
  - `pageSize` *(integer, default=10)*
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy danh sách phòng yêu thích thành công",
  "data": {
    "items": [
      {
        "favoriteId": "b2c3d4e5-6789-0123-bcde-456789abcdef",
        "roomId": "f5a6b7c8-d9e0-1234-fa56-789abcdef012",
        "roomNumber": "P.302",
        "buildingName": "Tòa nhà Rentify Central Park",
        "address": "123 Nguyễn Thị Minh Khai, P. Võ Thị Sáu, Q.3, TP.HCM",
        "basePriceMonthly": 4500000,
        "coverImageUrl": "https://storage.rentify.vn/rooms/p302_main.jpg",
        "savedAt": "2026-09-22T14:20:00Z"
      }
    ],
    "pagination": {
      "pageNo": 1,
      "pageSize": 10,
      "totalItems": 1,
      "totalPages": 1
    }
  }
}
```

---

#### 27. POST /me/favorite-rooms
* **Method:** `POST`
* **Endpoint:** `/me/favorite-rooms`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `8._trang_ch_danh_s_ch_ph_ng_home_room_list/code.html`, `11._chi_ti_t_ph_ng_room_detail/code.html`
  - Vị trí UI: Nút icon hình trái tim góc phải trên thẻ phòng hoặc trang chi tiết phòng.
* **Request Payload (application/json):**
```json
{
  "roomId": "f5a6b7c8-d9e0-1234-fa56-789abcdef012"
}
```
* **Response Mẫu (201 Created):**
```json
{
  "statusCode": 201,
  "message": "Đã lưu phòng vào danh sách yêu thích",
  "data": {
    "favoriteId": "b2c3d4e5-6789-0123-bcde-456789abcdef",
    "roomId": "f5a6b7c8-d9e0-1234-fa56-789abcdef012",
    "savedAt": "2026-09-23T10:00:00Z"
  }
}
```

---

#### 28. DELETE /me/favorite-rooms/{roomId}
* **Method:** `DELETE`
* **Endpoint:** `/me/favorite-rooms/{roomId}`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `10._ph_ng_l_u_saved_rooms/code.html`, `12._ph_ng_l_u_saved_rooms/code.html`
  - Vị trí UI: Nút icon trái tim được active hoặc nút "Bỏ lưu" trên thẻ phòng đã lưu.
* **Request:** Path parameter `roomId` (UUID).
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Đã xóa phòng khỏi danh sách yêu thích",
  "data": null
}
```

---

#### 29. GET /roommate-profiles
* **Method:** `GET`
* **Endpoint:** `/roommate-profiles`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `11._gh_p_b_n_c_ng_ph_ng_match_feed/code.html`
  - Vị trí UI: Bảng tin hồ sơ người đang tìm bạn ở ghép: bộ lọc theo Giới tính, Khoảng ngân sách hàng tháng, Khu vực mong muốn, Thói quen sinh hoạt (hút thuốc, nuôi thú cưng, giờ giấc làm việc).
* **Query Parameters:**
  - `gender` *(string, optional)*: `MALE`, `FEMALE`, `OTHER`.
  - `targetDistrict` *(string, optional)*: Quận mong muốn tìm phòng.
  - `maxBudget` *(integer, optional)*: Ngân sách tối đa (VNĐ).
  - `pageNo` / `pageSize` *(integer)*: Phân trang.
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy danh sách hồ sơ ở ghép thành công",
  "data": {
    "items": [
      {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "userId": "b5c6d7e8-9012-3456-cdef-789012345678",
        "fullName": "Trần Thị Mai",
        "gender": "FEMALE",
        "birthYear": 2002,
        "occupation": "Lập trình viên UI/UX",
        "targetDistrict": "Quận 3",
        "maxBudget": 3000000,
        "cleanlinessLevel": 4,
        "sleepSchedule": "EARLY_BIRD",
        "hasPet": false,
        "isSmoker": false,
        "bio": "Sinh hoạt ngăn nắp, yên tĩnh, đi làm giờ hành chính.",
        "avatarUrl": "https://storage.rentify.vn/avatars/user_mai.jpg"
      }
    ],
    "pagination": {
      "pageNo": 1,
      "pageSize": 10,
      "totalItems": 1,
      "totalPages": 1
    }
  }
}
```

---

#### 30. GET /me/roommate-profile
* **Method:** `GET`
* **Endpoint:** `/me/roommate-profile`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `12._chi_ti_t_h_s_b_n_c_ng_ph_ng_profile_detail/code.html`, `13._t_o_ch_nh_s_a_h_s_gh_p_ph_ng_create_edit_profile/code.html`
  - Vị trí UI: Xem hồ sơ tìm bạn ở ghép của chính bản thân và nút chuyển sang màn hình chỉnh sửa.
* **Request:** Không có payload.
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy thông tin hồ sơ ở ghép thành công",
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "targetCity": "TP. Hồ Chí Minh",
    "targetDistrict": "Quận 3",
    "targetMoveInDate": "2026-10-01",
    "maxBudget": 3500000,
    "genderPreference": "MALE",
    "cleanlinessLevel": 5,
    "sleepSchedule": "NIGHT_OWL",
    "hasPet": false,
    "isSmoker": false,
    "bio": "Thân thiện, thích nấu ăn cuối tuần, tìm bạn giữ vệ sinh chung.",
    "isActive": true
  }
}
```

---

#### 31. PUT /me/roommate-profile
* **Method:** `PUT`
* **Endpoint:** `/me/roommate-profile`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `13._t_o_ch_nh_s_a_h_s_gh_p_ph_ng_create_edit_profile/code.html`
  - Vị trí UI: Form tạo/sửa hồ sơ ở ghép: Ngân sách, Địa bàn tìm kiếm, Thói quen sinh hoạt, Slider mức độ sạch sẽ, Checkbox thú cưng/hút thuốc và nút **"Lưu hồ sơ ở ghép"**.
* **Request Payload (application/json):**
```json
{
  "targetCity": "TP. Hồ Chí Minh",
  "targetDistrict": "Quận 3",
  "targetMoveInDate": "2026-10-01",
  "maxBudget": 3500000,
  "genderPreference": "MALE",
  "cleanlinessLevel": 5,
  "sleepSchedule": "NIGHT_OWL",
  "hasPet": false,
  "isSmoker": false,
  "bio": "Thân thiện, thích nấu ăn cuối tuần, tìm bạn giữ vệ sinh chung.",
  "isActive": true
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lưu hồ sơ tìm bạn ở ghép thành công",
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "isActive": true,
    "updatedAt": "2026-09-23T10:05:00Z"
  }
}
```

---

#### 32. GET /match-requests
* **Method:** `GET`
* **Endpoint:** `/match-requests`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `14._danh_s_ch_y_u_c_u_gh_p_ph_ng_requests/code.html`
  - Vị trí UI: 2 tab: "Yêu cầu đã nhận" và "Yêu cầu đã gửi" kèm trạng thái Đang chờ / Đã chấp nhận / Đã từ chối.
* **Query Parameters:**
  - `type` *(string, required)*: `RECEIVED` hoặc `SENT`.
  - `status` *(string, optional)*: `PENDING`, `ACCEPTED`, `REJECTED`, `CANCELLED`.
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy danh sách yêu cầu ghép phòng thành công",
  "data": {
    "items": [
      {
        "id": "m1a2b3c4-d5e6-7890-abcd-ef1234567890",
        "sender": {
          "userId": "b5c6d7e8-9012-3456-cdef-789012345678",
          "fullName": "Trần Thị Mai",
          "avatarUrl": "https://storage.rentify.vn/avatars/user_mai.jpg",
          "occupation": "Lập trình viên UI/UX"
        },
        "introductionMessage": "Chào bạn, mình thấy thói quen sinh hoạt và khu vực thuê của 2 đứa rất hợp nhau, kết nối nhé!",
        "status": "PENDING",
        "createdAt": "2026-09-23T08:15:00Z"
      }
    ]
  }
}
```

---

#### 33. POST /match-requests
* **Method:** `POST`
* **Endpoint:** `/match-requests`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `11._gh_p_b_n_c_ng_ph_ng_match_feed/code.html`, `12._chi_ti_t_h_s_b_n_c_ng_ph_ng_profile_detail/code.html`
  - Vị trí UI: Nút "Gửi lời mời ghép đôi" kèm popup nhập lời nhắn chào hỏi.
* **Request Payload (application/json):**
```json
{
  "targetProfileId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "introductionMessage": "Chào bạn, mình thấy bạn cũng đang tìm phòng khu vực Quận 3 với ngân sách tương đương, mong muốn làm quen!"
}
```
* **Response Mẫu (201 Created):**
```json
{
  "statusCode": 201,
  "message": "Gửi yêu cầu ghép phòng thành công",
  "data": {
    "id": "m1a2b3c4-d5e6-7890-abcd-ef1234567890",
    "status": "PENDING",
    "createdAt": "2026-09-23T10:10:00Z"
  }
}
```

---

#### 34. POST /match-requests/{matchRequestId}/accept
* **Method:** `POST`
* **Endpoint:** `/match-requests/{matchRequestId}/accept`
* **Quyền hạn:** `AUTH, receiver`
* **Dẫn chứng UI:**
  - Thư mục: `14._danh_s_ch_y_u_c_u_gh_p_ph_ng_requests/code.html`, `15._gh_p_i_th_nh_c_ng_match_success/code.html`
  - Vị trí UI: Nút màu xanh **"Đồng ý ghép"** trên thẻ yêu cầu nhận được, chuyển hướng tới màn hình ghép đôi thành công.
* **Request:** Path parameter `matchRequestId` (UUID).
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Đã chấp nhận ghép phòng thành công. Cuộc trò chuyện đã được khởi tạo.",
  "data": {
    "matchRequestId": "m1a2b3c4-d5e6-7890-abcd-ef1234567890",
    "status": "ACCEPTED",
    "conversationId": "conv_998877-6655-4433-2211-00aabbccddee"
  }
}
```

---

#### 35. POST /match-requests/{matchRequestId}/reject
* **Method:** `POST`
* **Endpoint:** `/match-requests/{matchRequestId}/reject`
* **Quyền hạn:** `AUTH, receiver`
* **Dẫn chứng UI:**
  - Thư mục: `14._danh_s_ch_y_u_c_u_gh_p_ph_ng_requests/code.html`
  - Vị trí UI: Nút xám viền đỏ **"Từ chối"** trên thẻ yêu cầu nhận được.
* **Request:** Path parameter `matchRequestId` (UUID).
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Đã từ chối yêu cầu ghép phòng",
  "data": {
    "matchRequestId": "m1a2b3c4-d5e6-7890-abcd-ef1234567890",
    "status": "REJECTED"
  }
}
```

---

#### 36. DELETE /match-requests/{matchRequestId}
* **Method:** `DELETE`
* **Endpoint:** `/match-requests/{matchRequestId}`
* **Quyền hạn:** `AUTH, requester`
* **Dẫn chứng UI:**
  - Thư mục: `14._danh_s_ch_y_u_c_u_gh_p_ph_ng_requests/code.html` (Tab Yêu cầu đã gửi)
  - Vị trí UI: Nút **"Hủy yêu cầu"** trên thẻ lời mời đang ở trạng thái PENDING.
* **Request:** Path parameter `matchRequestId` (UUID).
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Hủy yêu cầu ghép phòng thành công",
  "data": null
}
```

---

### 17.5 Nhóm RatePolicy & BillingSetting (Chính sách Đơn giá Dịch vụ & Cài đặt Hóa đơn)

#### 37. GET /rate-policies
* **Method:** `GET`
* **Endpoint:** `/rate-policies`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `12._ch_n_lo_i_n_gi_d_ch_v_b_c_3_3_choose_utility_rate_type/code.html`, `18._b_ng_ti_n_ch_v_n_h_nh_ph_ng_room_utility_menu_1/code.html`
  - Vị trí UI: Bảng danh sách cấu hình biểu giá dịch vụ (Điện, Nước, Internet, Vệ sinh, Gửi xe) của tòa nhà hoặc phòng.
* **Query Parameters:**
  - `entityType` *(string, required)*: `ROOM`, `BUILDING`, `LANDLORD`.
  - `entityId` *(UUID, required)*: ID tòa nhà hoặc phòng cần truy vấn.
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy danh sách đơn giá dịch vụ thành công",
  "data": {
    "items": [
      {
        "id": "rp_11223344-5566-7788-9900-aabbccddeeff",
        "entityType": "BUILDING",
        "entityId": "e4f5a6b7-c8d9-0123-ef45-6789abcdef01",
        "utilityType": "ELECTRICITY",
        "rateType": "FIXED",
        "unitPrice": 3800,
        "tierConfig": null,
        "isActive": true
      },
      {
        "id": "rp_22334455-6677-8899-0011-bbccddeeff00",
        "entityType": "BUILDING",
        "entityId": "e4f5a6b7-c8d9-0123-ef45-6789abcdef01",
        "utilityType": "WATER",
        "rateType": "PER_OCCUPANT",
        "unitPrice": 100000,
        "tierConfig": null,
        "isActive": true
      }
    ]
  }
}
```

---

#### 38. POST /rate-policies
* **Method:** `POST`
* **Endpoint:** `/rate-policies`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `12a._c_u_h_nh_n_gi_c_nh_configure_fixed_rate/code.html`, `12b._c_u_h_nh_bi_u_l_y_ti_n_evn_configure_evn_tiered_rate/code.html`, `12c._c_u_h_nh_kho_n_tr_n_g_i_theo_u_ng_i_configure_per_person_flat_rate/code.html`
  - Vị trí UI: Form cài đặt đơn giá từng loại dịch vụ theo loại hình: Cố định (đơn giá/kWh), Lũy tiến EVN 6 bậc, hoặc Khoán theo đầu người/phòng.
* **Request Payload (application/json):**
```json
{
  "entityType": "BUILDING",
  "entityId": "e4f5a6b7-c8d9-0123-ef45-6789abcdef01",
  "utilityType": "ELECTRICITY",
  "rateType": "FIXED",
  "unitPrice": 3800,
  "tierConfig": null
}
```
* **Response Mẫu (201 Created):**
```json
{
  "statusCode": 201,
  "message": "Thiết lập đơn giá dịch vụ thành công",
  "data": {
    "id": "rp_11223344-5566-7788-9900-aabbccddeeff",
    "utilityType": "ELECTRICITY",
    "rateType": "FIXED",
    "unitPrice": 3800,
    "isActive": true
  }
}
```

---

#### 39. POST /rate-policies/batch
* **Method:** `POST`
* **Endpoint:** `/rate-policies/batch`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `12._ch_n_lo_i_n_gi_d_ch_v_b_c_3_3_choose_utility_rate_type/code.html`
  - Vị trí UI: Bước 3/3 tạo tòa nhà: Form tổng hợp các tiện ích và nút bấm **"Lưu cấu hình toàn bộ đơn giá"**.
* **Request Payload (application/json):**
```json
{
  "entityType": "BUILDING",
  "entityId": "e4f5a6b7-c8d9-0123-ef45-6789abcdef01",
  "policies": [
    {
      "utilityType": "ELECTRICITY",
      "rateType": "FIXED",
      "unitPrice": 3800
    },
    {
      "utilityType": "WATER",
      "rateType": "PER_OCCUPANT",
      "unitPrice": 100000
    },
    {
      "utilityType": "INTERNET",
      "rateType": "FIXED",
      "unitPrice": 100000
    },
    {
      "utilityType": "PARKING",
      "rateType": "PER_OCCUPANT",
      "unitPrice": 120000
    }
  ]
}
```
* **Response Mẫu (201 Created):**
```json
{
  "statusCode": 201,
  "message": "Lưu toàn bộ đơn giá dịch vụ thành công",
  "data": {
    "savedCount": 4
  }
}
```

---

#### 40. PATCH /rate-policies/{ratePolicyId}
* **Method:** `PATCH`
* **Endpoint:** `/rate-policies/{ratePolicyId}`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `18._b_ng_ti_n_ch_v_n_h_nh_ph_ng_room_utility_menu_1/code.html`
  - Vị trí UI: Modal sửa đơn giá của dịch vụ kèm nút **"Cập nhật đơn giá"**.
* **Request Payload (application/json):**
```json
{
  "unitPrice": 4000
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Cập nhật đơn giá dịch vụ thành công",
  "data": {
    "id": "rp_11223344-5566-7788-9900-aabbccddeeff",
    "unitPrice": 4000,
    "updatedAt": "2026-09-23T10:15:00Z"
  }
}
```

---

#### 41. POST /rate-policies/{ratePolicyId}/deactivate
* **Method:** `POST`
* **Endpoint:** `/rate-policies/{ratePolicyId}/deactivate`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `18._b_ng_ti_n_ch_v_n_h_nh_ph_ng_room_utility_menu_1/code.html`
  - Vị trí UI: Nút gạt Toggle tắt/kích hoạt hoặc nút icon "Tạm ngừng dịch vụ".
* **Request:** Path parameter `ratePolicyId` (UUID).
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Đã ngừng áp dụng chính sách đơn giá này",
  "data": {
    "id": "rp_11223344-5566-7788-9900-aabbccddeeff",
    "isActive": false
  }
}
```

---

#### 42. GET /billing-settings
* **Method:** `GET`
* **Endpoint:** `/billing-settings`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `37._c_i_t_chu_k_thanh_to_n_qu_t_n_billing_cycle_debt_scan_settings/code.html`, `38._thi_t_l_p_ng_y_ch_t_h_n_thanh_to_n_due_date_settings/code.html`
  - Vị trí UI: Khối thông tin cài đặt chu kỳ thanh toán: Ngày chốt chỉ số hàng tháng, Ngày đến hạn thanh toán hóa đơn, Chu kỳ tự động quét nợ.
* **Query Parameters:**
  - `entityType` *(string)*: `BUILDING` hoặc `ROOM`.
  - `entityId` *(UUID)*.
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy cấu hình thanh toán thành công",
  "data": {
    "id": "bs_33445566-7788-9900-1122-ccddeeff0011",
    "entityType": "BUILDING",
    "entityId": "e4f5a6b7-c8d9-0123-ef45-6789abcdef01",
    "closingDay": 25,
    "paymentDueDays": 5,
    "autoScanDebt": true,
    "lateFeeDailyPercent": 0.05
  }
}
```

---

#### 43. POST /billing-settings
* **Method:** `POST`
* **Endpoint:** `/billing-settings`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `37._c_i_t_chu_k_thanh_to_n_qu_t_n_billing_cycle_debt_scan_settings/code.html`
  - Vị trí UI: Form khởi tạo chu kỳ chốt hóa đơn và hạn nộp tiền cho tòa nhà/phòng mới.
* **Request Payload (application/json):**
```json
{
  "entityType": "BUILDING",
  "entityId": "e4f5a6b7-c8d9-0123-ef45-6789abcdef01",
  "closingDay": 25,
  "paymentDueDays": 5,
  "autoScanDebt": true,
  "lateFeeDailyPercent": 0.05
}
```
* **Response Mẫu (201 Created):**
```json
{
  "statusCode": 201,
  "message": "Thiết lập cấu hình thanh toán thành công",
  "data": {
    "id": "bs_33445566-7788-9900-1122-ccddeeff0011",
    "closingDay": 25,
    "paymentDueDays": 5
  }
}
```

---

#### 44. PATCH /billing-settings/{billingSettingId}
* **Method:** `PATCH`
* **Endpoint:** `/billing-settings/{billingSettingId}`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `38._thi_t_l_p_ng_y_ch_t_h_n_thanh_to_n_due_date_settings/code.html`
  - Vị trí UI: Nút **"Lưu cấu hình hạn thanh toán"**.
* **Request Payload (application/json):**
```json
{
  "closingDay": 28,
  "paymentDueDays": 7
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Cập nhật cấu hình chu kỳ thanh toán thành công",
  "data": {
    "id": "bs_33445566-7788-9900-1122-ccddeeff0011",
    "closingDay": 28,
    "paymentDueDays": 7,
    "updatedAt": "2026-09-23T10:20:00Z"
  }
}
```

---

### 17.6 Nhóm Contract & ContractMember (Hợp đồng Thuê, Ký tay & Thành viên phòng)

#### 45. GET /contracts
* **Method:** `GET`
* **Endpoint:** `/contracts`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `21._danh_s_ch_h_p_ng_thu_lease_list/code.html`
  - Vị trí UI: Bảng danh sách hợp đồng thuê: Cột Mã hợp đồng, Phòng, Người đại diện thuê, Thời hạn thuê, Giá thuê, Tiền cọc, Trạng thái (Hiệu lực, Bản nháp, Sắp hết hạn, Đã chấm dứt) và bộ lọc theo trạng thái/tòa nhà.
* **Query Parameters:**
  - `status` *(string, optional)*: `DRAFT`, `PENDING_SIGNATURE`, `ACTIVE`, `EXPIRING_SOON`, `TERMINATED`.
  - `buildingId` *(UUID, optional)*.
  - `pageNo` / `pageSize` *(integer)*.
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy danh sách hợp đồng thuê thành công",
  "data": {
    "items": [
      {
        "id": "c1d2e3f4-a5b6-7890-cdef-123456789012",
        "roomNumber": "P.302",
        "buildingName": "Tòa nhà Rentify Central Park",
        "primaryTenantName": "Nguyễn Văn An",
        "primaryTenantPhone": "0912345678",
        "startDate": "2026-09-01",
        "endDate": "2027-08-31",
        "rentalPriceMonthly": 4500000,
        "depositAmount": 4500000,
        "status": "ACTIVE",
        "hasSignedDocument": true
      }
    ],
    "pagination": {
      "pageNo": 1,
      "pageSize": 10,
      "totalItems": 1,
      "totalPages": 1
    }
  }
}
```

---

#### 46. POST /contracts
* **Method:** `POST`
* **Endpoint:** `/contracts`
* **Quyền hạn:** `AUTH, room owner`
* **Dẫn chứng UI:**
  - Thư mục: `19._t_o_h_p_ng_m_i_create_lease/code.html`
  - Vị trí UI: Form tạo hợp đồng mới: Chọn phòng, Người đại diện thuê (họ tên, SĐT, CCCD), Ngày bắt đầu, Ngày kết thúc, Giá thuê hàng tháng, Tiền cọc, Ngày nộp tiền hàng tháng và nút bấm **"Tạo dự thảo hợp đồng"**.
* **Request Payload (application/json):**
```json
{
  "roomId": "f5a6b7c8-d9e0-1234-fa56-789abcdef012",
  "primaryTenant": {
    "fullName": "Nguyễn Văn An",
    "phoneNumber": "0912345678",
    "identityCardNumber": "079201001234"
  },
  "startDate": "2026-10-01",
  "endDate": "2027-09-30",
  "rentalPriceMonthly": 4500000,
  "depositAmount": 4500000,
  "paymentDayOfMonth": 5,
  "paymentCycleMonths": 1,
  "templateKey": "STANDARD_ROOM_LEASE_V1"
}
```
* **Response Mẫu (201 Created):**
```json
{
  "statusCode": 201,
  "message": "Tạo hợp đồng thuê mới thành công (trạng thái DRAFT)",
  "data": {
    "id": "c1d2e3f4-a5b6-7890-cdef-123456789012",
    "roomId": "f5a6b7c8-d9e0-1234-fa56-789abcdef012",
    "status": "DRAFT",
    "createdAt": "2026-09-23T10:25:00Z"
  }
}
```

---

#### 47. GET /contracts/{contractId}
* **Method:** `GET`
* **Endpoint:** `/contracts/{contractId}`
* **Quyền hạn:** `AUTH, related`
* **Dẫn chứng UI:**
  - Thư mục: `23._xem_h_p_ng_thu_view_lease/code.html`
  - Vị trí UI: Màn hình chi tiết hợp đồng: Thông tin các bên, Điều khoản thuê, Danh sách thành viên ở chung, Tài liệu hợp đồng ký tay đã scan/chụp ảnh, Lịch sử thay đổi.
* **Request:** Path parameter `contractId` (UUID).
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy chi tiết hợp đồng thành công",
  "data": {
    "id": "c1d2e3f4-a5b6-7890-cdef-123456789012",
    "roomId": "f5a6b7c8-d9e0-1234-fa56-789abcdef012",
    "roomNumber": "P.302",
    "building": {
      "id": "e4f5a6b7-c8d9-0123-ef45-6789abcdef01",
      "name": "Tòa nhà Rentify Central Park",
      "address": "123 Nguyễn Thị Minh Khai, P. Võ Thị Sáu, Q.3, TP.HCM"
    },
    "landlord": {
      "fullName": "Lê Văn Chủ",
      "phoneNumber": "0909000111"
    },
    "primaryTenant": {
      "fullName": "Nguyễn Văn An",
      "phoneNumber": "0912345678",
      "identityCardNumber": "079201001234"
    },
    "startDate": "2026-10-01",
    "endDate": "2027-09-30",
    "rentalPriceMonthly": 4500000,
    "depositAmount": 4500000,
    "paymentDayOfMonth": 5,
    "status": "ACTIVE",
    "signedContractMediaUrl": "https://storage.rentify.vn/contracts/signed_lease_c1d2.pdf",
    "createdAt": "2026-09-23T10:25:00Z"
  }
}
```

---

#### 48. PATCH /contracts/{contractId}
* **Method:** `PATCH`
* **Endpoint:** `/contracts/{contractId}`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `19._t_o_h_p_ng_m_i_create_lease/code.html` (chế độ sửa bản nháp)
  - Vị trí UI: Nút "Chỉnh sửa thông tin hợp đồng" khi hợp đồng ở trạng thái DRAFT.
* **Request Payload (application/json):**
```json
{
  "rentalPriceMonthly": 4600000,
  "depositAmount": 4600000,
  "endDate": "2027-10-31"
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Cập nhật hợp đồng thuê thành công",
  "data": {
    "id": "c1d2e3f4-a5b6-7890-cdef-123456789012",
    "rentalPriceMonthly": 4600000,
    "depositAmount": 4600000,
    "updatedAt": "2026-09-23T10:30:00Z"
  }
}
```

---

#### 49. GET /contract-templates
* **Method:** `GET`
* **Endpoint:** `/contract-templates`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `20._ch_n_m_u_h_p_ng_choose_lease_template/code.html`
  - Vị trí UI: Danh sách các thẻ mẫu hợp đồng thuê trọ chuẩn: Mẫu phòng đơn, Mẫu căn hộ mini, Mẫu homestay ký túc xá có tóm tắt điều khoản.
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy danh sách mẫu hợp đồng thành công",
  "data": {
    "templates": [
      {
        "templateKey": "STANDARD_ROOM_LEASE_V1",
        "title": "Mẫu Hợp đồng Thuê phòng Trọ Chuẩn 2026",
        "description": "Điều khoản đầy đủ theo quy định Bộ Xây Dựng, rõ ràng về đặt cọc và dịch vụ điện nước.",
        "isDefault": true
      },
      {
        "templateKey": "MINI_APARTMENT_LEASE_V1",
        "title": "Mẫu Hợp đồng Chung cư Mini / Studio",
        "description": "Bao gồm quy định nội thất tài sản bàn giao và nội quy quản lý chung.",
        "isDefault": false
      }
    ]
  }
}
```

---

#### 50. GET /contract-templates/{templateKey}
* **Method:** `GET`
* **Endpoint:** `/contract-templates/{templateKey}`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `20._ch_n_m_u_h_p_ng_choose_lease_template/code.html`
  - Vị trí UI: Modal xem trước toàn bộ nội dung mẫu văn bản hợp đồng.
* **Request:** Path parameter `templateKey` (string).
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy nội dung mẫu hợp đồng thành công",
  "data": {
    "templateKey": "STANDARD_ROOM_LEASE_V1",
    "title": "Mẫu Hợp đồng Thuê phòng Trọ Chuẩn 2026",
    "contentMarkdown": "# CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\n## HỢP ĐỒNG THUÊ PHÒNG TRỌ\n..."
  }
}
```

---

#### 51. PUT /contracts/{contractId}/template
* **Method:** `PUT`
* **Endpoint:** `/contracts/{contractId}/template`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `20._ch_n_m_u_h_p_ng_choose_lease_template/code.html`
  - Vị trí UI: Nút bấm **"Áp dụng mẫu này cho hợp đồng"**.
* **Request Payload (application/json):**
```json
{
  "templateKey": "STANDARD_ROOM_LEASE_V1"
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Áp dụng mẫu hợp đồng thành công",
  "data": {
    "contractId": "c1d2e3f4-a5b6-7890-cdef-123456789012",
    "templateKey": "STANDARD_ROOM_LEASE_V1"
  }
}
```

---

#### 52. POST /contracts/{contractId}/documents/draft
* **Method:** `POST`
* **Endpoint:** `/contracts/{contractId}/documents/draft`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `21._xu_t_file_pdf_export_lease_pdf/code.html`
  - Vị trí UI: Nút bấm **"Xuất file PDF hợp đồng nháp để in ký tay"**.
* **Request Payload (application/json):**
```json
{
  "includeWatermark": false
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Khởi tạo tài liệu hợp đồng PDF thành công",
  "data": {
    "documentPdfUrl": "https://storage.rentify.vn/generated/contracts/draft_c1d2e3f4.pdf",
    "generatedAt": "2026-09-23T10:35:00Z"
  }
}
```

---

#### 53. POST /contracts/{contractId}/activate
* **Method:** `POST`
* **Endpoint:** `/contracts/{contractId}/activate`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `22._t_i_l_n_h_p_ng_k_upload_signed_lease/code.html`
  - Vị trí UI: Dropzone tải ảnh/PDF hợp đồng đã ký và nút bấm xác nhận **"Kích hoạt hợp đồng thuê"** (chuyển trạng thái sang ACTIVE và phòng sang OCCUPIED).
* **Request Payload (application/json):**
```json
{
  "signedContractMediaId": "c3d4e5f6-7a8b-9c0d-1e2f-3a4b5c6d7e8f",
  "initialDepositCollected": true,
  "notes": "Hợp đồng đã có chữ ký 2 bên và nhận đủ 4.500.000 VNĐ tiền cọc."
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Hợp đồng thuê đã được kích hoạt thành công",
  "data": {
    "id": "c1d2e3f4-a5b6-7890-cdef-123456789012",
    "status": "ACTIVE",
    "roomStatus": "OCCUPIED",
    "activatedAt": "2026-09-23T10:40:00Z"
  }
}
```

---

#### 54. POST /contracts/{contractId}/checkout/final-meter-readings
* **Method:** `POST`
* **Endpoint:** `/contracts/{contractId}/checkout/final-meter-readings`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `43._ch_t_ch_s_tr_ph_ng_final_meter_reading/code.html`
  - Vị trí UI: Form chốt chỉ số điện và nước ngày trả phòng, ảnh bằng chứng đồng hồ và nút **"Xác nhận số đo kết thúc"**.
* **Request Payload (application/json):**
```json
{
  "electricityFinalReading": 12850.5,
  "electricityProofMediaId": "c3d4e5f6-7a8b-9c0d-1e2f-3a4b5c6d7e8f",
  "waterFinalReading": 320.0,
  "waterProofMediaId": "d4e5f6a7-8b9c-0d1e-2f3a-4b5c6d7e8f90",
  "readingDate": "2026-09-23"
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Đã chốt chỉ số điện nước kết thúc hợp đồng",
  "data": {
    "electricityConsumption": 145.5,
    "waterConsumption": 6.0,
    "readingDate": "2026-09-23"
  }
}
```

---

#### 55. POST /contracts/{contractId}/checkout/final-invoice
* **Method:** `POST`
* **Endpoint:** `/contracts/{contractId}/checkout/final-invoice`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `44._h_a_n_quy_t_to_n_ti_n_ph_ng_final_settlement_invoice/code.html`, `45._quy_t_to_n_ti_n_c_c_ho_n_tr_deposit_settlement/code.html`
  - Vị trí UI: Màn hình quyết toán trả phòng: Tính toán tiền phòng các ngày lẻ, tiền điện nước cuối kỳ, khấu trừ hư hỏng tài sản và số tiền hoàn cọc thực tế cho khách. Nút **"Tạo hóa đơn quyết toán & Hoàn cọc"**.
* **Request Payload (application/json):**
```json
{
  "deductions": [
    {
      "reason": "Hư hỏng tay nắm cửa phòng tắm",
      "amount": 150000
    }
  ],
  "refundDepositAmount": 4350000,
  "paymentMethod": "VIETQR"
}
```
* **Response Mẫu (201 Created):**
```json
{
  "statusCode": 201,
  "message": "Tạo hóa đơn quyết toán trả phòng thành công",
  "data": {
    "settlementInvoiceId": "inv_77889900-1122-3344-5566-aabbccddeeff",
    "totalCharges": 150000,
    "originalDeposit": 4500000,
    "netRefundToTenant": 4350000,
    "status": "PENDING_PAYMENT"
  }
}
```

---

#### 56. POST /contracts/{contractId}/checkout/complete
* **Method:** `POST`
* **Endpoint:** `/contracts/{contractId}/checkout/complete`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `46._x_c_nh_n_ho_n_t_t_tr_ph_ng_confirm_move_out_complete/code.html`
  - Vị trí UI: Modal xác nhận "Đã hoàn tất thanh lý hợp đồng và bàn giao chìa khóa", nút bấm **"Xác nhận hoàn tất trả phòng"** (chuyển hợp đồng sang TERMINATED và phòng sang CLEANING_PENDING).
* **Request Payload (application/json):**
```json
{
  "moveOutNotes": "Khách đã bàn giao đủ 2 chìa khóa cổng và 1 thẻ thang máy."
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Quy trình trả phòng hoàn tất. Hợp đồng đã thanh lý.",
  "data": {
    "contractId": "c1d2e3f4-a5b6-7890-cdef-123456789012",
    "contractStatus": "TERMINATED",
    "roomStatus": "CLEANING_PENDING",
    "terminatedAt": "2026-09-23T10:45:00Z"
  }
}
```

---

#### 57. POST /contracts/{contractId}/members
* **Method:** `POST`
* **Endpoint:** `/contracts/{contractId}/members`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `24._th_m_th_nh_vi_n_m_i_add_new_member/code.html`
  - Vị trí UI: Form thêm thành viên phòng: Họ và tên, Số điện thoại, Số CCCD, Ngày bắt đầu ở, Quan hệ (Bạn bè/Người thân) và nút **"Thêm thành viên"**.
* **Request Payload (application/json):**
```json
{
  "fullName": "Lê Văn Bình",
  "phoneNumber": "0987654321",
  "identityCardNumber": "079202005678",
  "moveInDate": "2026-10-05",
  "isPrimaryTenant": false
}
```
* **Response Mẫu (201 Created):**
```json
{
  "statusCode": 201,
  "message": "Thêm thành viên phòng thành công",
  "data": {
    "id": "mem_11223344-aabb-ccdd-eeff-001122334455",
    "contractId": "c1d2e3f4-a5b6-7890-cdef-123456789012",
    "fullName": "Lê Văn Bình",
    "stayStatus": "ACTIVE",
    "createdAt": "2026-09-23T10:50:00Z"
  }
}
```

---

#### 58. PATCH /contracts/{contractId}/members/{memberId}
* **Method:** `PATCH`
* **Endpoint:** `/contracts/{contractId}/members/{memberId}`
* **Quyền hạn:** `AUTH, owner / chính member`
* **Dẫn chứng UI:**
  - Thư mục: `23._danh_s_ch_th_nh_vi_n_member_list/code.html`, `24._danh_s_ch_th_nh_vi_n_member_list/code.html`
  - Vị trí UI: Nút icon cây bút "Chỉnh sửa thông tin thành viên" trên dòng danh sách thành viên.
* **Request Payload (application/json):**
```json
{
  "fullName": "Lê Văn Bình",
  "phoneNumber": "0987654322"
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Cập nhật thông tin thành viên thành công",
  "data": {
    "id": "mem_11223344-aabb-ccdd-eeff-001122334455",
    "fullName": "Lê Văn Bình",
    "phoneNumber": "0987654322",
    "updatedAt": "2026-09-23T10:55:00Z"
  }
}
```

---

#### 59. POST /contracts/{contractId}/members/{memberId}/leave
* **Method:** `POST`
* **Endpoint:** `/contracts/{contractId}/members/{memberId}/leave`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `25._x_c_nh_n_x_a_th_nh_vi_n_confirm_remove_member/code.html`
  - Vị trí UI: Modal cảnh báo "Xác nhận thành viên rời khỏi phòng / Xóa thành viên", nút **"Xác nhận rời phòng"**.
* **Request Payload (application/json):**
```json
{
  "moveOutDate": "2026-09-23",
  "reason": "Chuyển công tác sang chi nhánh khác"
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Đã cập nhật trạng thái thành viên rời phòng thành công",
  "data": {
    "id": "mem_11223344-aabb-ccdd-eeff-001122334455",
    "stayStatus": "MOVED_OUT",
    "moveOutDate": "2026-09-23"
  }
}
```

---

#### 60. GET /contracts/{contractId}/members/export
* **Method:** `GET`
* **Endpoint:** `/contracts/{contractId}/members/export`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `23._danh_s_ch_th_nh_vi_n_member_list/code.html`, `24._danh_s_ch_th_nh_vi_n_member_list/code.html`
  - Vị trí UI: Nút bấm **"Xuất danh sách (Excel/CSV)"** trên đầu bảng thành viên phục vụ khai báo lưu trú / tạm trú công an.
* **Query Parameters:**
  - `format` *(string, default=xlsx)*: `xlsx` hoặc `csv`.
* **Response Mẫu (200 OK - File Stream):**
  - Headers: `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, `Content-Disposition: attachment; filename="danh_sach_thanh_vien_p302.xlsx"`

---

### 17.7 Nhóm MeterReading (Ghi Chỉ số Điện Nước & Nhận diện OCR)

#### 61. GET /rooms/{roomId}/meter-readings
* **Method:** `GET`
* **Endpoint:** `/rooms/{roomId}/meter-readings`
* **Quyền hạn:** `AUTH, related`
* **Dẫn chứng UI:**
  - Thư mục: `26._ghi_ch_s_ph_ng_l_single_meter_reading/code.html`
  - Vị trí UI: Bảng lịch sử chỉ số công tơ điện/nước các tháng trước của phòng: Ngày ghi, Chỉ số cũ, Chỉ số mới, Lượng tiêu thụ và ảnh bằng chứng.
* **Query Parameters:**
  - `utilityType` *(string, optional)*: `ELECTRICITY` hoặc `WATER`.
  - `fromMonth` / `toMonth` *(string, optional)*: Định dạng `YYYY-MM`.
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy lịch sử chỉ số đồng hồ thành công",
  "data": {
    "items": [
      {
        "id": "mr_12345678-90ab-cdef-1234-567890abcdef",
        "roomId": "f5a6b7c8-d9e0-1234-fa56-789abcdef012",
        "utilityType": "ELECTRICITY",
        "readingDate": "2026-08-25",
        "previousReading": 12500.0,
        "currentReading": 12680.5,
        "consumption": 180.5,
        "proofMediaUrl": "https://storage.rentify.vn/readings/t8_p302_elec.jpg",
        "recordedBy": "Lê Văn Chủ"
      }
    ]
  }
}
```

---

#### 62. POST /rooms/{roomId}/meter-readings/ocr-preview
* **Method:** `POST`
* **Endpoint:** `/rooms/{roomId}/meter-readings/ocr-preview`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `30._ch_p_nh_c_ng_t_qua_webcam_webcam_meter_photo/code.html`, `31._k_t_qu_nh_n_di_n_s_c_ocr_ocr_result/code.html`
  - Vị trí UI: Nút chụp ảnh webcam / tải ảnh công tơ lên và màn hình hiển thị kết quả OCR AI bóc tách số đo tự động kèm độ chính xác (Confidence Score).
* **Request Payload (application/json):**
```json
{
  "utilityType": "ELECTRICITY",
  "mediaId": "c3d4e5f6-7a8b-9c0d-1e2f-3a4b5c6d7e8f"
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Nhận diện chỉ số qua OCR thành công",
  "data": {
    "detectedReading": 12850.5,
    "confidence": 0.96,
    "boundingBox": { "x": 120, "y": 80, "width": 240, "height": 70 },
    "previousReading": 12680.5,
    "calculatedConsumption": 170.0,
    "isAbnormal": false
  }
}
```

---

#### 63. POST /rooms/{roomId}/meter-readings
* **Method:** `POST`
* **Endpoint:** `/rooms/{roomId}/meter-readings`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `26._ghi_ch_s_ph_ng_l_single_meter_reading/code.html`, `31._k_t_qu_nh_n_di_n_s_c_ocr_ocr_result/code.html`
  - Vị trí UI: Form chốt chỉ số phòng lẻ: Ô nhập Chỉ số điện mới, Chỉ số nước mới, Ngày ghi và nút **"Lưu chỉ số & Tạo hóa đơn"**.
* **Request Payload (application/json):**
```json
{
  "readings": [
    {
      "utilityType": "ELECTRICITY",
      "readingDate": "2026-09-25",
      "currentReading": 12850.5,
      "proofMediaId": "c3d4e5f6-7a8b-9c0d-1e2f-3a4b5c6d7e8f"
    },
    {
      "utilityType": "WATER",
      "readingDate": "2026-09-25",
      "currentReading": 320.0,
      "proofMediaId": "d4e5f6a7-8b9c-0d1e-2f3a-4b5c6d7e8f90"
    }
  ]
}
```
* **Response Mẫu (201 Created):**
```json
{
  "statusCode": 201,
  "message": "Lưu chỉ số điện nước thành công",
  "data": {
    "roomId": "f5a6b7c8-d9e0-1234-fa56-789abcdef012",
    "savedReadings": [
      {
        "utilityType": "ELECTRICITY",
        "previousReading": 12680.5,
        "currentReading": 12850.5,
        "consumption": 170.0
      },
      {
        "utilityType": "WATER",
        "previousReading": 314.0,
        "currentReading": 320.0,
        "consumption": 6.0
      }
    ]
  }
}
```

---

#### 64. POST /buildings/{buildingId}/meter-reading-batches
* **Method:** `POST`
* **Endpoint:** `/buildings/{buildingId}/meter-reading-batches`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `27._b_t_u_ghi_ch_s_h_ng_lo_t_bulk_reading_entry/code.html`, `28._ti_n_tr_nh_ghi_ch_s_h_ng_lo_t_bulk_reading_flow/code.html`, `29._b_o_c_o_t_ng_k_t_ghi_ch_s_h_ng_lo_t_bulk_reading_summary/code.html`
  - Vị trí UI: Luồng ghi số hàng loạt theo tầng/dãy phòng, bảng tổng kết số đo toàn tòa và nút **"Lưu hàng loạt và phát hành hóa đơn"**.
* **Request Payload (application/json):**
```json
{
  "readingDate": "2026-09-25",
  "items": [
    {
      "roomId": "f5a6b7c8-d9e0-1234-fa56-789abcdef012",
      "electricityReading": 12850.5,
      "waterReading": 320.0,
      "electricityMediaId": "c3d4e5f6-7a8b-9c0d-1e2f-3a4b5c6d7e8f",
      "waterMediaId": "d4e5f6a7-8b9c-0d1e-2f3a-4b5c6d7e8f90"
    },
    {
      "roomId": "e1f2a3b4-5678-90ab-cdef-112233445566",
      "electricityReading": 8940.0,
      "waterReading": 210.0,
      "electricityMediaId": null,
      "waterMediaId": null
    }
  ]
}
```
* **Response Mẫu (201 Created):**
```json
{
  "statusCode": 201,
  "message": "Ghi nhận chỉ số hàng loạt thành công",
  "data": {
    "batchId": "batch_8899aabb-ccdd-eeff-0011-223344556677",
    "totalRooms": 2,
    "successCount": 2,
    "warningsCount": 0
  }
}
```

---

### 17.8 Nhóm Invoice & Payment (Hóa đơn, Công nợ & Thanh toán VietQR)

#### 65. GET /invoices
* **Method:** `GET`
* **Endpoint:** `/invoices`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `25._danh_s_ch_h_a_n_invoice_list/code.html`, `33._danh_s_ch_h_a_n_ph_t_h_nh_issued_invoice_list/code.html`
  - Vị trí UI: Bảng danh sách hóa đơn: Mã hóa đơn, Phòng, Kỳ thanh toán, Tổng tiền, Đã trả, Còn nợ, Hạn nộp, Trạng thái (Đã phát hành, Đã thanh toán, Quá hạn, Đã hủy) kèm bộ lọc theo tháng và trạng thái.
* **Query Parameters:**
  - `status` *(string, optional)*: `DRAFT`, `PENDING_PAYMENT`, `PARTIALLY_PAID`, `PAID`, `OVERDUE`, `CANCELLED`.
  - `buildingId` *(UUID, optional)*.
  - `billingMonth` *(string, optional)*: Định dạng `YYYY-MM`.
  - `pageNo` / `pageSize` *(integer)*.
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy danh sách hóa đơn thành công",
  "data": {
    "items": [
      {
        "id": "inv_1001-2002-3003-4004-500560067007",
        "invoiceNumber": "HD-202609-P302",
        "roomNumber": "P.302",
        "buildingName": "Tòa nhà Rentify Central Park",
        "tenantName": "Nguyễn Văn An",
        "billingPeriod": "01/09/2026 - 30/09/2026",
        "totalAmount": 5350000,
        "paidAmount": 0,
        "remainingAmount": 5350000,
        "dueDate": "2026-10-05",
        "status": "PENDING_PAYMENT"
      }
    ],
    "pagination": {
      "pageNo": 1,
      "pageSize": 10,
      "totalItems": 1,
      "totalPages": 1
    }
  }
}
```

---

#### 66. POST /rooms/{roomId}/invoices
* **Method:** `POST`
* **Endpoint:** `/rooms/{roomId}/invoices`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `32._xem_tr_c_h_a_n_invoice_preview/code.html`
  - Vị trí UI: Màn hình tạo dự thảo hóa đơn cho phòng: tính tiền phòng tháng tới, tiền điện nước tháng này, phụ phí và nút **"Tạo dự thảo hóa đơn"**.
* **Request Payload (application/json):**
```json
{
  "billingPeriodStart": "2026-09-01",
  "billingPeriodEnd": "2026-09-30",
  "dueDate": "2026-10-05",
  "customItems": [
    {
      "itemType": "OTHER",
      "description": "Phí giặt ủi chung",
      "quantity": 1,
      "unitPrice": 50000
    }
  ],
  "discountAmount": 0
}
```
* **Response Mẫu (201 Created):**
```json
{
  "statusCode": 201,
  "message": "Tạo dự thảo hóa đơn thành công",
  "data": {
    "id": "inv_1001-2002-3003-4004-500560067007",
    "invoiceNumber": "HD-202609-P302",
    "totalAmount": 5400000,
    "status": "DRAFT",
    "createdAt": "2026-09-23T11:00:00Z"
  }
}
```

---

#### 67. GET /invoices/{invoiceId}
* **Method:** `GET`
* **Endpoint:** `/invoices/{invoiceId}`
* **Quyền hạn:** `AUTH, related`
* **Dẫn chứng UI:**
  - Thư mục: `26._chi_ti_t_h_a_n_invoice_detail/code.html`
  - Vị trí UI: Màn hình chi tiết hóa đơn: Bảng kê chi tiết từng dòng dịch vụ (Tiền phòng, Tiền điện theo số kWh, Tiền nước theo khối/đầu người, Internet, Rác), Mã VietQR thanh toán nhanh, Lịch sử các lần nộp tiền.
* **Request:** Path parameter `invoiceId` (UUID).
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy chi tiết hóa đơn thành công",
  "data": {
    "id": "inv_1001-2002-3003-4004-500560067007",
    "invoiceNumber": "HD-202609-P302",
    "roomNumber": "P.302",
    "tenant": {
      "fullName": "Nguyễn Văn An",
      "phoneNumber": "0912345678"
    },
    "billingPeriodStart": "2026-09-01",
    "billingPeriodEnd": "2026-09-30",
    "issueDate": "2026-09-25",
    "dueDate": "2026-10-05",
    "items": [
      {
        "itemType": "RENT",
        "description": "Tiền thuê phòng tháng 09/2026",
        "quantity": 1,
        "unitPrice": 4500000,
        "totalPrice": 4500000
      },
      {
        "itemType": "ELECTRICITY",
        "description": "Tiền điện (Chỉ số cũ: 12680.5 - Mới: 12850.5, Tiêu thụ: 170 kWh)",
        "quantity": 170,
        "unitPrice": 3800,
        "totalPrice": 646000
      },
      {
        "itemType": "WATER",
        "description": "Tiền nước khoán (2 người)",
        "quantity": 2,
        "unitPrice": 100000,
        "totalPrice": 200000
      }
    ],
    "subtotalAmount": 5346000,
    "discountAmount": 0,
    "totalAmount": 5346000,
    "paidAmount": 0,
    "remainingAmount": 5346000,
    "status": "PENDING_PAYMENT",
    "vietQrUrl": "https://api.vietqr.io/image/970415-102876543210-compact2.jpg?amount=5346000&addInfo=HD202609P302"
  }
}
```

---

#### 68. PATCH /invoices/{invoiceId}
* **Method:** `PATCH`
* **Endpoint:** `/invoices/{invoiceId}`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `34._ch_nh_s_a_ho_c_h_y_h_a_n_edit_cancel_invoice/code.html`
  - Vị trí UI: Form chỉnh sửa hóa đơn (khi đang là DRAFT): sửa các khoản giảm trừ, phụ phí bổ sung và nút **"Lưu thay đổi hóa đơn"**.
* **Request Payload (application/json):**
```json
{
  "discountAmount": 100000,
  "dueDate": "2026-10-07"
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Cập nhật hóa đơn thành công",
  "data": {
    "id": "inv_1001-2002-3003-4004-500560067007",
    "discountAmount": 100000,
    "totalAmount": 5246000,
    "remainingAmount": 5246000,
    "updatedAt": "2026-09-23T11:05:00Z"
  }
}
```

---

#### 69. POST /invoices/{invoiceId}/issue
* **Method:** `POST`
* **Endpoint:** `/invoices/{invoiceId}/issue`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `35._ph_t_h_nh_h_a_n_th_nh_c_ng_issue_invoice/code.html`
  - Vị trí UI: Nút bấm **"Phát hành hóa đơn"** (chuyển trạng thái từ DRAFT sang PENDING_PAYMENT, sinh mã VietQR và gửi thông báo Zalo/Push tới người thuê).
* **Request Payload (application/json):**
```json
{
  "sendNotification": true
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Phát hành hóa đơn thành công. Đã gửi thông báo tới khách thuê.",
  "data": {
    "id": "inv_1001-2002-3003-4004-500560067007",
    "status": "PENDING_PAYMENT",
    "issuedAt": "2026-09-23T11:10:00Z"
  }
}
```

---

#### 70. POST /invoices/{invoiceId}/cancel
* **Method:** `POST`
* **Endpoint:** `/invoices/{invoiceId}/cancel`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `34._ch_nh_s_a_ho_c_h_y_h_a_n_edit_cancel_invoice/code.html`
  - Vị trí UI: Nút đỏ **"Hủy hóa đơn"** kèm modal nhập Lý do hủy bỏ hóa đơn.
* **Request Payload (application/json):**
```json
{
  "cancellationReason": "Ghi nhầm chỉ số đồng hồ điện nước kỳ trước."
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Đã hủy bỏ hóa đơn",
  "data": {
    "id": "inv_1001-2002-3003-4004-500560067007",
    "status": "CANCELLED",
    "cancellationReason": "Ghi nhầm chỉ số đồng hồ điện nước kỳ trước."
  }
}
```

---

#### 71. GET /invoices/{invoiceId}/document
* **Method:** `GET`
* **Endpoint:** `/invoices/{invoiceId}/document`
* **Quyền hạn:** `AUTH, related`
* **Dẫn chứng UI:**
  - Thư mục: `26._chi_ti_t_h_a_n_invoice_detail/code.html`
  - Vị trí UI: Nút bấm **"In phiếu thu / Xuất PDF hóa đơn"** góc trên bên phải trang chi tiết.
* **Response Mẫu (200 OK - PDF Stream):**
  - Headers: `Content-Type: application/pdf`, `Content-Disposition: inline; filename="hoa_don_HD202609P302.pdf"`
```json
{
  "statusCode": 200,
  "message": "Lấy tài liệu hóa đơn thành công",
  "data": {
    "pdfUrl": "https://storage.rentify.vn/generated/invoices/HD202609P302.pdf"
  }
}
```

---

#### 72. GET /debts
* **Method:** `GET`
* **Endpoint:** `/debts`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `39._danh_s_ch_c_ng_n_qu_h_n_debt_list/code.html`
  - Vị trí UI: Bảng thống kê công nợ quá hạn: Phòng, Khách thuê, Số ngày quá hạn, Số tiền nợ gốc, Số lần đã nhắc nợ, Trạng thái nhắc nhở.
* **Query Parameters:**
  - `buildingId` *(UUID, optional)*.
  - `minOverdueDays` *(integer, optional)*.
  - `pageNo` / `pageSize` *(integer)*.
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy danh sách công nợ quá hạn thành công",
  "data": {
    "totalDebtAmount": 10592000,
    "overdueInvoicesCount": 2,
    "items": [
      {
        "invoiceId": "inv_1001-2002-3003-4004-500560067007",
        "roomNumber": "P.302",
        "tenantName": "Nguyễn Văn An",
        "tenantPhone": "0912345678",
        "remainingAmount": 5246000,
        "overdueDays": 8,
        "lastReminderSentAt": "2026-09-20T09:00:00Z",
        "reminderCount": 1
      }
    ]
  }
}
```

---

#### 73. POST /debts/reminders
* **Method:** `POST`
* **Endpoint:** `/debts/reminders`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `39._danh_s_ch_c_ng_n_qu_h_n_debt_list/code.html`
  - Vị trí UI: Nút bấm **"Gửi nhắc nợ tất cả"** hoặc nút bấm riêng từng dòng **"Nhắc nợ qua SMS/Push"**.
* **Request Payload (application/json):**
```json
{
  "invoiceIds": [
    "inv_1001-2002-3003-4004-500560067007"
  ],
  "channel": "ALL",
  "customMessage": "Kính gửi quý khách, hóa đơn tiền phòng tháng 9 đã quá hạn 8 ngày, vui lòng thanh toán sớm để đảm bảo dịch vụ sinh hoạt."
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Đã gửi thông báo nhắc nợ thành công tới 1 khách thuê",
  "data": {
    "sentCount": 1,
    "timestamp": "2026-09-23T11:15:00Z"
  }
}
```

---

#### 74. GET /debts/export
* **Method:** `GET`
* **Endpoint:** `/debts/export`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `39._danh_s_ch_c_ng_n_qu_h_n_debt_list/code.html`
  - Vị trí UI: Nút bấm **"Xuất file Excel công nợ"** trên thanh công cụ bảng công nợ.
* **Query Parameters:**
  - `buildingId` *(UUID, optional)*.
  - `format` *(string, default=xlsx)*: `xlsx` hoặc `csv`.
* **Response Mẫu (200 OK - File Stream):**
  - Headers: `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, `Content-Disposition: attachment; filename="bao_cao_cong_no_20260923.xlsx"`

---

#### 75. GET /invoices/export
* **Method:** `GET`
* **Endpoint:** `/invoices/export`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `25._danh_s_ch_h_a_n_invoice_list/code.html`, `33._danh_s_ch_h_a_n_ph_t_h_nh_issued_invoice_list/code.html`
  - Vị trí UI: Nút bấm **"Xuất danh sách (Excel)"** tại màn hình quản lý hóa đơn.
* **Query Parameters:**
  - `buildingId` *(UUID, optional)*.
  - `status` *(string, optional)*.
  - `month` *(string, optional)*: `YYYY-MM`.
* **Response Mẫu (200 OK - File Stream):**
  - Headers: `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, `Content-Disposition: attachment; filename="danh_sach_hoa_don_thang_09_2026.xlsx"`

---

#### 76. GET /invoices/{invoiceId}/payments
* **Method:** `GET`
* **Endpoint:** `/invoices/{invoiceId}/payments`
* **Quyền hạn:** `AUTH, related`
* **Dẫn chứng UI:**
  - Thư mục: `26._chi_ti_t_h_a_n_invoice_detail/code.html`
  - Vị trí UI: Tab "Lịch sử thanh toán" bên trong trang chi tiết hóa đơn: Bảng ghi nhận ngày giờ, phương thức thanh toán, số tiền, mã tham chiếu ngân hàng, người duyệt.
* **Request:** Path parameter `invoiceId` (UUID).
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy lịch sử thanh toán hóa đơn thành công",
  "data": {
    "payments": [
      {
        "id": "pay_9988-7766-5544-3322-1100aabbccdd",
        "paymentMethod": "VIETQR",
        "amount": 5246000,
        "paymentTime": "2026-09-23T11:20:00Z",
        "transactionReference": "VQR20260923112001",
        "status": "SUCCESS"
      }
    ]
  }
}
```

---

#### 77. POST /invoices/{invoiceId}/payment-intents
* **Method:** `POST`
* **Endpoint:** `/invoices/{invoiceId}/payment-intents`
* **Quyền hạn:** `AUTH, contract member`
* **Dẫn chứng UI:**
  - Thư mục: `27._thanh_to_n_payment/code.html`
  - Vị trí UI: Màn hình người thuê thanh toán online: chọn phương thức VietQR động hoặc Cổng thanh toán, nút **"Tiến hành thanh toán"**.
* **Request Payload (application/json):**
```json
{
  "paymentMethod": "VIETQR",
  "amount": 5246000
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Tạo giao dịch thanh toán thành công",
  "data": {
    "paymentIntentId": "pi_11223344-5566-7788-9900-aabbccddeeff",
    "qrCodeString": "00020101021238540010A0000007270124...",
    "qrImageUrl": "https://api.vietqr.io/image/970415-102876543210-compact2.jpg?amount=5246000&addInfo=HD202609P302",
    "accountNumber": "102876543210",
    "accountName": "NGUYEN VAN AN",
    "bankName": "VietinBank",
    "amount": 5246000,
    "content": "HD202609P302",
    "expiresAt": "2026-09-23T11:50:00Z"
  }
}
```

---

#### 78. POST /invoices/{invoiceId}/cash-payments
* **Method:** `POST`
* **Endpoint:** `/invoices/{invoiceId}/cash-payments`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `36._x_c_nh_n_thanh_to_n_ti_n_m_t_confirm_cash_payment/code.html`
  - Vị trí UI: Form chủ trọ xác nhận đã thu tiền mặt trực tiếp: Số tiền thực thu, Ngày thu tiền, Ghi chú, Ảnh chụp phiếu biên nhận tiền mặt và nút **"Xác nhận đã thu tiền mặt"**.
* **Request Payload (application/json):**
```json
{
  "amount": 5246000,
  "paymentTime": "2026-09-23T11:25:00Z",
  "notes": "Khách đưa tiền mặt trực tiếp tại phòng bảo vệ.",
  "receiptMediaId": "c3d4e5f6-7a8b-9c0d-1e2f-3a4b5c6d7e8f"
}
```
* **Response Mẫu (201 Created):**
```json
{
  "statusCode": 201,
  "message": "Xác nhận thu tiền mặt thành công. Hóa đơn đã được gạch nợ.",
  "data": {
    "paymentId": "pay_cash_9988-7766-5544-3322",
    "invoiceId": "inv_1001-2002-3003-4004-500560067007",
    "status": "PAID",
    "remainingAmount": 0
  }
}
```

---

#### 79. POST /payments/webhooks/{provider}
* **Method:** `POST`
* **Endpoint:** `/payments/webhooks/{provider}`
* **Quyền hạn:** `Provider signed` (Xác thực chữ ký HMAC từ ngân hàng/cổng thanh toán)
* **Dẫn chứng UI:**
  - Thư mục: Tự động đối soát và cập nhật tức thì trạng thái hóa đơn trên UI sang màu xanh **"Đã thanh toán"** (qua SSE hoặc WebSocket).
* **Request Payload (application/json):**
```json
{
  "gateway": "vietqr",
  "transactionId": "TXN_20260923987654",
  "orderId": "HD-202609-P302",
  "amount": 5246000,
  "bankCode": "ICB",
  "signature": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Xử lý webhook thanh toán thành công",
  "data": {
    "status": "SUCCESS",
    "reconciled": true
  }
}
```

---

### 17.9 Nhóm IssueReport (Báo cáo Sự cố & Xử lý Khiếu nại)

#### 80. GET /issues
* **Method:** `GET`
* **Endpoint:** `/issues`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `28._danh_s_ch_s_c_room_issue_list/code.html`, `40._danh_s_ch_s_c_issues_tab/code.html`
  - Vị trí UI: Danh sách các sự cố bảo trì: Tiêu đề sự cố, Phòng, Danh mục (Điện, Nước, Thiết bị, An ninh), Mức độ ưu tiên (Khẩn cấp, Cao, Bình thường), Trạng thái xử lý (Chờ tiếp nhận, Đang xử lý, Đã hoàn thành).
* **Query Parameters:**
  - `status` *(string, optional)*: `PENDING`, `IN_PROGRESS`, `RESOLVED`, `CANCELLED`.
  - `priority` *(string, optional)*: `LOW`, `NORMAL`, `HIGH`, `URGENT`.
  - `buildingId` *(UUID, optional)*.
  - `pageNo` / `pageSize` *(integer)*.
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy danh sách sự cố thành công",
  "data": {
    "items": [
      {
        "id": "iss_5566-7788-9900-aabb-ccddeeff0011",
        "title": "Vòi xịt bồn cầu bị rò rỉ nước",
        "roomNumber": "P.302",
        "buildingName": "Tòa nhà Rentify Central Park",
        "reporterName": "Nguyễn Văn An",
        "issueCategory": "PLUMBING",
        "priority": "HIGH",
        "status": "IN_PROGRESS",
        "createdAt": "2026-09-22T15:30:00Z"
      }
    ],
    "pagination": {
      "pageNo": 1,
      "pageSize": 10,
      "totalItems": 1,
      "totalPages": 1
    }
  }
}
```

---

#### 81. POST /issues
* **Method:** `POST`
* **Endpoint:** `/issues`
* **Quyền hạn:** `AUTH, related`
* **Dẫn chứng UI:**
  - Thư mục: `30._b_o_c_o_s_c_m_i_report_an_issue/code.html`, `42._t_o_phi_u_y_u_c_u_s_c_m_i_landlord_creates_an_issue/code.html`
  - Vị trí UI: Form gửi yêu cầu sửa chữa sự cố mới: Tiêu đề, Chọn danh mục, Mức độ ưu tiên, Mô tả chi tiết, Đính kèm ảnh/video hư hỏng và nút **"Gửi báo cáo sự cố"**.
* **Request Payload (application/json):**
```json
{
  "roomId": "f5a6b7c8-d9e0-1234-fa56-789abcdef012",
  "title": "Vòi xịt bồn cầu bị rò rỉ nước",
  "issueCategory": "PLUMBING",
  "priority": "HIGH",
  "description": "Nước rò rỉ liên tục từ dây dẫn vòi xịt gây tràn sàn vệ sinh.",
  "mediaIds": [
    "c3d4e5f6-7a8b-9c0d-1e2f-3a4b5c6d7e8f"
  ]
}
```
* **Response Mẫu (201 Created):**
```json
{
  "statusCode": 201,
  "message": "Gửi báo cáo sự cố thành công",
  "data": {
    "id": "iss_5566-7788-9900-aabb-ccddeeff0011",
    "status": "PENDING",
    "createdAt": "2026-09-23T11:30:00Z"
  }
}
```

---

#### 82. GET /issues/{issueId}
* **Method:** `GET`
* **Endpoint:** `/issues/{issueId}`
* **Quyền hạn:** `AUTH, related`
* **Dẫn chứng UI:**
  - Thư mục: `29._chi_ti_t_s_c_issue_detail_popup/code.html`, `41._chi_ti_t_s_c_issue_detail_popup/code.html`
  - Vị trí UI: Popup chi tiết sự cố: Mô tả, Ảnh/video hiện trường, Tiến độ xử lý, Lịch hẹn thợ sửa chữa, Chi phí ước tính.
* **Request:** Path parameter `issueId` (UUID).
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy chi tiết sự cố thành công",
  "data": {
    "id": "iss_5566-7788-9900-aabb-ccddeeff0011",
    "title": "Vòi xịt bồn cầu bị rò rỉ nước",
    "roomNumber": "P.302",
    "reporter": {
      "fullName": "Nguyễn Văn An",
      "phoneNumber": "0912345678"
    },
    "issueCategory": "PLUMBING",
    "priority": "HIGH",
    "status": "IN_PROGRESS",
    "description": "Nước rò rỉ liên tục từ dây dẫn vòi xịt gây tràn sàn vệ sinh.",
    "images": [
      "https://storage.rentify.vn/issues/voi_xit_ro_ri.jpg"
    ],
    "assignedTechnician": "Nguyễn Thợ Điện Nước (0901234888)",
    "scheduledAt": "2026-09-23T14:00:00Z",
    "createdAt": "2026-09-22T15:30:00Z"
  }
}
```

---

#### 83. PATCH /issues/{issueId}
* **Method:** `PATCH`
* **Endpoint:** `/issues/{issueId}`
* **Quyền hạn:** `AUTH, owner/creator theo field`
* **Dẫn chứng UI:**
  - Thư mục: `29._chi_ti_t_s_c_issue_detail_popup/code.html`, `41._chi_ti_t_s_c_issue_detail_popup/code.html`
  - Vị trí UI: Nút cập nhật trạng thái "Tiếp nhận xử lý" / "Nghiệm thu hoàn thành", Form cập nhật người xử lý và chi phí sửa chữa.
* **Request Payload (application/json):**
```json
{
  "status": "RESOLVED",
  "resolutionNotes": "Đã thay mới toàn bộ cụm dây vòi xịt inox 304.",
  "repairCost": 120000
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Cập nhật tiến độ sự cố thành công",
  "data": {
    "id": "iss_5566-7788-9900-aabb-ccddeeff0011",
    "status": "RESOLVED",
    "resolvedAt": "2026-09-23T11:35:00Z"
  }
}
```

---

#### 84. GET /issues/export
* **Method:** `GET`
* **Endpoint:** `/issues/export`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: `40._danh_s_ch_s_c_issues_tab/code.html`
  - Vị trí UI: Nút bấm **"Xuất báo cáo sự cố (Excel)"** tại thanh công cụ quản lý bảo trì.
* **Query Parameters:**
  - `buildingId` *(UUID, optional)*.
  - `status` *(string, optional)*.
  - `format` *(string, default=xlsx)*: `xlsx` hoặc `csv`.
* **Response Mẫu (200 OK - File Stream):**
  - Headers: `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, `Content-Disposition: attachment; filename="bao_cao_su_co_20260923.xlsx"`

---

### 17.10 Nhóm Conversation & Message (Hộp thư, Tin nhắn & Trao đổi nội bộ)

#### 85. GET /conversations
* **Method:** `GET`
* **Endpoint:** `/conversations`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `16._h_p_th_inbox/code.html`, `48._h_p_th_inbox_1/code.html` đến `48._h_p_th_inbox_5/code.html`
  - Vị trí UI: Danh sách hộp thư trò chuyện: Cuộc trò chuyện riêng chủ trọ - khách thuê, Nhóm phòng, Nhóm tòa nhà, Trò chuyện tìm bạn ở ghép; kèm tin nhắn cuối cùng, thời gian và số tin chưa đọc (Unread badge).
* **Query Parameters:**
  - `type` *(string, optional)*: `DIRECT_LANDLORD_TENANT`, `ROOM_GROUP`, `BUILDING_GROUP`, `ROOMMATE_MATCH`.
  - `pageNo` / `pageSize` *(integer)*.
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy danh sách cuộc trò chuyện thành công",
  "data": {
    "items": [
      {
        "id": "conv_9988-7766-5544-3322-1100aabbccdd",
        "type": "ROOM_GROUP",
        "title": "Nhóm Phòng P.302 - Central Park",
        "lastMessage": {
          "content": "Chủ nhà: Đã tiếp nhận yêu cầu sửa vòi nước nhé!",
          "senderName": "Lê Văn Chủ",
          "sentAt": "2026-09-23T11:32:00Z"
        },
        "unreadCount": 2,
        "updatedAt": "2026-09-23T11:32:00Z"
      }
    ]
  }
}
```

---

#### 86. GET /conversations/{conversationId}
* **Method:** `GET`
* **Endpoint:** `/conversations/{conversationId}`
* **Quyền hạn:** `AUTH, member`
* **Dẫn chứng UI:**
  - Thư mục: `49._chi_ti_t_cu_c_tr_chuy_n_chat_thread_detail_1/code.html` đến `49._chi_ti_t_cu_c_tr_chuy_n_chat_thread_detail_5/code.html`
  - Vị trí UI: Header khung chat: Tên nhóm/người đối thoại, Danh sách thành viên tham gia, Tệp đã chia sẻ, Nút cài đặt thông báo hội thoại.
* **Request:** Path parameter `conversationId` (UUID).
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy chi tiết cuộc trò chuyện thành công",
  "data": {
    "id": "conv_9988-7766-5544-3322-1100aabbccdd",
    "type": "ROOM_GROUP",
    "title": "Nhóm Phòng P.302 - Central Park",
    "members": [
      {
        "userId": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
        "fullName": "Nguyễn Văn An",
        "role": "TENANT",
        "avatarUrl": "https://storage.rentify.vn/avatars/user1.png"
      },
      {
        "userId": "b5c6d7e8-9012-3456-cdef-789012345678",
        "fullName": "Lê Văn Chủ",
        "role": "LANDLORD",
        "avatarUrl": "https://storage.rentify.vn/avatars/landlord.png"
      }
    ],
    "createdAt": "2026-09-01T08:00:00Z"
  }
}
```

---

#### 87. GET /conversations/{conversationId}/messages
* **Method:** `GET`
* **Endpoint:** `/conversations/{conversationId}/messages`
* **Quyền hạn:** `AUTH, member`
* **Dẫn chứng UI:**
  - Thư mục: `49._chi_ti_t_cu_c_tr_chuy_n_chat_thread_detail_1/code.html`
  - Vị trí UI: Dòng thời gian hiển thị bong bóng tin nhắn (tin nhắn văn bản, ảnh, tệp đính kèm, thông báo hệ thống) kèm tính năng cuộn lên tải thêm tin nhắn cũ.
* **Query Parameters:**
  - `beforeCursor` *(string, optional)*: ID tin nhắn làm mốc phân trang lùi.
  - `limit` *(integer, default=30)*.
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy tin nhắn hội thoại thành công",
  "data": {
    "items": [
      {
        "id": "msg_0011-2233-4455-6677-8899aabbccdd",
        "senderId": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
        "senderName": "Nguyễn Văn An",
        "content": "Dạ em gửi ảnh vòi xịt bị rò rỉ nước ạ!",
        "attachmentMediaUrl": "https://storage.rentify.vn/issues/voi_xit_ro_ri.jpg",
        "createdAt": "2026-09-23T11:30:00Z"
      }
    ],
    "hasMore": false
  }
}
```

---

#### 88. POST /conversations/{conversationId}/messages
* **Method:** `POST`
* **Endpoint:** `/conversations/{conversationId}/messages`
* **Quyền hạn:** `AUTH, member`
* **Dẫn chứng UI:**
  - Thư mục: `49._chi_ti_t_cu_c_tr_chuy_n_chat_thread_detail_1/code.html`
  - Vị trí UI: Khung nhập tin nhắn bên dưới: Ô nhập văn bản, Icon đính kèm ảnh, Icon mặt cười và nút bấm **"Gửi"** (hoặc phím Enter).
* **Request Payload (application/json):**
```json
{
  "content": "Dạ thợ mấy giờ qua kiểm tra được ạ bác?",
  "attachmentMediaId": null,
  "replyToMessageId": "msg_0011-2233-4455-6677-8899aabbccdd",
  "mentionedUserIds": []
}
```
* **Response Mẫu (201 Created):**
```json
{
  "statusCode": 201,
  "message": "Gửi tin nhắn thành công",
  "data": {
    "id": "msg_0011-2233-4455-6677-8899aabbccee",
    "conversationId": "conv_9988-7766-5544-3322-1100aabbccdd",
    "content": "Dạ thợ mấy giờ qua kiểm tra được ạ bác?",
    "senderId": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    "createdAt": "2026-09-23T11:38:00Z"
  }
}
```

---

#### 89. POST /conversations/{conversationId}/read
* **Method:** `POST`
* **Endpoint:** `/conversations/{conversationId}/read`
* **Quyền hạn:** `AUTH, member`
* **Dẫn chứng UI:**
  - Thư mục: Tự động kích hoạt khi người dùng nhấp mở hội thoại trong `48._h_p_th_inbox_1/code.html` để xóa chấm đỏ báo tin chưa đọc.
* **Request Payload (application/json):**
```json
{
  "lastReadMessageId": "msg_0011-2233-4455-6677-8899aabbccee"
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Đã đánh dấu đọc tin nhắn",
  "data": {
    "conversationId": "conv_9988-7766-5544-3322-1100aabbccdd",
    "unreadCount": 0
  }
}
```

---

#### 90. GET /contracts/{contractId}/conversation
* **Method:** `GET`
* **Endpoint:** `/contracts/{contractId}/conversation`
* **Quyền hạn:** `AUTH, related`
* **Dẫn chứng UI:**
  - Thư mục: `18._tr_chuy_n_nh_m_ph_ng_tr_property_group_chat_room/code.html`, `23._xem_h_p_ng_thu_view_lease/code.html`
  - Vị trí UI: Nút bấm **"Nhắn tin cho các bên trong hợp đồng"** tại màn hình chi tiết hợp đồng / phòng trọ.
* **Request:** Path parameter `contractId` (UUID).
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy phòng chat của hợp đồng thành công",
  "data": {
    "conversationId": "conv_9988-7766-5544-3322-1100aabbccdd",
    "type": "ROOM_GROUP"
  }
}
```

---

#### 91. GET /buildings/{buildingId}/conversation
* **Method:** `GET`
* **Endpoint:** `/buildings/{buildingId}/conversation`
* **Quyền hạn:** `AUTH, resident/owner`
* **Dẫn chứng UI:**
  - Thư mục: `19._tr_chuy_n_nh_m_t_a_nh_property_group_chat_building/code.html`
  - Vị trí UI: Nút bấm **"Nhóm chat cư dân tòa nhà"** tại trang chi tiết tòa nhà.
* **Request:** Path parameter `buildingId` (UUID).
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy nhóm chat cư dân tòa nhà thành công",
  "data": {
    "conversationId": "conv_bld_112233-4455-6677-8899",
    "title": "Cộng đồng Cư dân - Rentify Central Park"
  }
}
```

---

### 17.11 Nhóm Notification & Preference (Thông báo Hệ thống & Cài đặt Nhận tin)

#### 92. GET /notifications
* **Method:** `GET`
* **Endpoint:** `/notifications`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: Dropdown chuông thông báo trên Header điều hướng tất cả màn hình.
  - Vị trí UI: Danh sách thông báo đẩy: Hóa đơn mới phát hành, Nhắc nhở hạn thanh toán, Cập nhật trạng thái sự cố, Yêu cầu ghép phòng mới.
* **Query Parameters:**
  - `unreadOnly` *(boolean, optional)*: `true` / `false`.
  - `pageNo` / `pageSize` *(integer)*.
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy danh sách thông báo thành công",
  "data": {
    "unreadTotal": 3,
    "items": [
      {
        "id": "notif_1122-3344-5566-7788",
        "title": "Hóa đơn tiền phòng tháng 09/2026",
        "content": "Chủ nhà đã phát hành hóa đơn HD-202609-P302 với tổng số tiền 5.346.000 VNĐ.",
        "type": "INVOICE_ISSUED",
        "targetUrl": "/invoices/inv_1001-2002-3003-4004-500560067007",
        "isRead": false,
        "createdAt": "2026-09-23T11:10:00Z"
      }
    ]
  }
}
```

---

#### 93. POST /notifications/{notificationId}/read
* **Method:** `POST`
* **Endpoint:** `/notifications/{notificationId}/read`
* **Quyền hạn:** `AUTH, owner`
* **Dẫn chứng UI:**
  - Thư mục: Dropdown chuông thông báo Header.
  - Vị trí UI: Nhấp chuột vào một thông báo chưa đọc trong danh sách.
* **Request:** Path parameter `notificationId` (UUID).
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Đã đánh dấu đọc thông báo",
  "data": {
    "id": "notif_1122-3344-5566-7788",
    "isRead": true
  }
}
```

---

#### 94. POST /notifications/read-all
* **Method:** `POST`
* **Endpoint:** `/notifications/read-all`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: Dropdown chuông thông báo Header.
  - Vị trí UI: Nút bấm văn bản **"Đánh dấu tất cả là đã đọc"** trên đầu menu thông báo.
* **Request:** Không có payload.
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Đã đánh dấu đọc tất cả thông báo",
  "data": {
    "markedCount": 3
  }
}
```

---

#### 95. GET /me/notification-preference
* **Method:** `GET`
* **Endpoint:** `/me/notification-preference`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `32._c_i_t_th_ng_b_o_notification_settings/code.html`, `51._c_i_t_th_ng_b_o_notification_settings_1/code.html` đến `51._c_i_t_th_ng_b_o_notification_settings_3/code.html`
  - Vị trí UI: Màn hình Cài đặt thông báo: Các nút gạt Bật/Tắt theo kênh (Email, Web Push, SMS) và theo sự kiện (Hóa đơn, Nhắc nợ, Báo cáo sự cố, Tin nhắn cộng đồng).
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy cài đặt thông báo thành công",
  "data": {
    "channels": {
      "email": true,
      "webPush": true,
      "sms": false
    },
    "events": {
      "invoiceIssued": true,
      "debtReminder": true,
      "issueStatusChanged": true,
      "newMessage": true,
      "contractExpiring": true
    }
  }
}
```

---

#### 96. PUT /me/notification-preference
* **Method:** `PUT`
* **Endpoint:** `/me/notification-preference`
* **Quyền hạn:** `AUTH`
* **Dẫn chứng UI:**
  - Thư mục: `32._c_i_t_th_ng_b_o_notification_settings/code.html`
  - Vị trí UI: Nút bấm **"Lưu cài đặt thông báo"**.
* **Request Payload (application/json):**
```json
{
  "channels": {
    "email": true,
    "webPush": true,
    "sms": false
  },
  "events": {
    "invoiceIssued": true,
    "debtReminder": true,
    "issueStatusChanged": true,
    "newMessage": false,
    "contractExpiring": true
  }
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Cập nhật cài đặt thông báo thành công",
  "data": {
    "updatedAt": "2026-09-23T11:45:00Z"
  }
}
```

---

### 17.12 Nhóm Admin & AuditLog (Quản trị Hệ thống & Kiểm toán)

#### 97. GET /admin/dashboard
* **Method:** `GET`
* **Endpoint:** `/admin/dashboard`
* **Quyền hạn:** `ADMIN`
* **Dẫn chứng UI:**
  - Thư mục: `6._b_ng_i_u_khi_n_qu_n_tr_vi_n_admin_dashboard/code.html`
  - Vị trí UI: Dashboard quản trị viên: 4 thẻ thống kê tổng quan (Tổng người dùng, Tổng bất động sản, Doanh thu giao dịch hệ thống, Tỷ lệ lấp đầy), Biểu đồ tăng trưởng người dùng và Danh sách bất động sản chờ phê duyệt.
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy số liệu bảng điều khiển quản trị thành công",
  "data": {
    "totalUsers": 1250,
    "totalLandlords": 320,
    "totalTenants": 930,
    "totalBuildings": 145,
    "pendingApprovalBuildings": 8,
    "totalRooms": 1580,
    "occupancyRate": 89.2,
    "systemTransactionVolumeMonthly": 3450000000
  }
}
```

---

#### 98. GET /admin/users
* **Method:** `GET`
* **Endpoint:** `/admin/users`
* **Quyền hạn:** `ADMIN`
* **Dẫn chứng UI:**
  - Thư mục: `7._danh_s_ch_ng_i_d_ng_user_list/code.html`
  - Vị trí UI: Bảng quản lý người dùng: Cột Họ tên, Email, Số điện thoại, Vai trò (ADMIN, LANDLORD, TENANT), Trạng thái (Hoạt động / Bị khóa), Ngày tham gia và bộ lọc theo Vai trò/Trạng thái.
* **Query Parameters:**
  - `role` *(string, optional)*: `ADMIN`, `LANDLORD`, `TENANT`.
  - `isActive` *(boolean, optional)*.
  - `search` *(string, optional)*: Tìm kiếm theo họ tên, email hoặc số điện thoại.
  - `pageNo` / `pageSize` *(integer)*.
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy danh sách người dùng thành công",
  "data": {
    "items": [
      {
        "id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
        "fullName": "Nguyễn Văn An",
        "email": "nguyenvanan@example.com",
        "phoneNumber": "0912345678",
        "role": "TENANT",
        "isActive": true,
        "createdAt": "2026-09-01T10:00:00Z"
      }
    ],
    "pagination": {
      "pageNo": 1,
      "pageSize": 10,
      "totalItems": 1250,
      "totalPages": 125
    }
  }
}
```

---

#### 99. POST /admin/users
* **Method:** `POST`
* **Endpoint:** `/admin/users`
* **Quyền hạn:** `ADMIN`
* **Dẫn chứng UI:**
  - Thư mục: `7._danh_s_ch_ng_i_d_ng_user_list/code.html`
  - Vị trí UI: Nút bấm **"Thêm người dùng mới"** góc trên bên phải bảng người dùng & Modal tạo tài khoản do Admin khởi tạo (nhập Họ tên, Email, Số điện thoại, Vai trò, Mật khẩu ban đầu).
* **Request Payload (application/json):**
```json
{
  "fullName": "Vũ Minh Hùng",
  "email": "vuminhhung@example.com",
  "phoneNumber": "0933112233",
  "role": "LANDLORD",
  "temporaryPassword": "InitPassword2026@"
}
```
* **Response Mẫu (201 Created):**
```json
{
  "statusCode": 201,
  "message": "Quản trị viên tạo người dùng mới thành công",
  "data": {
    "id": "usr_9988-7766-5544-3322-1100aabbccdd",
    "fullName": "Vũ Minh Hùng",
    "email": "vuminhhung@example.com",
    "phoneNumber": "0933112233",
    "role": "LANDLORD",
    "isActive": true,
    "createdAt": "2026-09-23T11:50:00Z"
  }
}
```

---

#### 100. GET /admin/users/export
* **Method:** `GET`
* **Endpoint:** `/admin/users/export`
* **Quyền hạn:** `ADMIN`
* **Dẫn chứng UI:**
  - Thư mục: `7._danh_s_ch_ng_i_d_ng_user_list/code.html`
  - Vị trí UI: Nút bấm **"Xuất danh sách (Excel)"** tại thanh công cụ phía trên bảng quản lý người dùng.
* **Query Parameters:**
  - `role` *(string, optional)*.
  - `isActive` *(boolean, optional)*.
  - `format` *(string, default=xlsx)*: `xlsx` hoặc `csv`.
* **Response Mẫu (200 OK - File Stream):**
  - Headers: `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, `Content-Disposition: attachment; filename="danh_sach_nguoi_dung_rentify.xlsx"`

---

#### 101. GET /admin/users/{userId}
* **Method:** `GET`
* **Endpoint:** `/admin/users/{userId}`
* **Quyền hạn:** `ADMIN`
* **Dẫn chứng UI:**
  - Thư mục: `8._chi_ti_t_ng_i_d_ng_user_detail/code.html`
  - Vị trí UI: Màn hình chi tiết người dùng: Hồ sơ định danh (CCCD, địa chỉ thường trú), Lịch sử sở hữu tòa nhà / hợp đồng thuê phòng, Lịch sử đăng nhập và nhật ký vi phạm.
* **Request:** Path parameter `userId` (UUID).
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy chi tiết hồ sơ người dùng thành công",
  "data": {
    "id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    "fullName": "Nguyễn Văn An",
    "email": "nguyenvanan@example.com",
    "phoneNumber": "0912345678",
    "role": "TENANT",
    "identityCardNumber": "079201001234",
    "isActive": true,
    "activeContractCount": 1,
    "createdAt": "2026-09-01T10:00:00Z"
  }
}
```

---

#### 102. POST /admin/users/{userId}/lock
* **Method:** `POST`
* **Endpoint:** `/admin/users/{userId}/lock`
* **Quyền hạn:** `ADMIN`
* **Dẫn chứng UI:**
  - Thư mục: `9a._kh_a_t_i_kho_n_lock_account/code.html`
  - Vị trí UI: Modal cảnh báo màu đỏ "Khóa tài khoản người dùng" kèm ô nhập Lý do khóa, Thời hạn khóa và nút bấm **"Xác nhận khóa tài khoản"**.
* **Request Payload (application/json):**
```json
{
  "lockReason": "Vi phạm điều khoản cộng đồng: Đăng tin giả mạo và quấy rối người thuê khác.",
  "durationDays": 30
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Khóa tài khoản người dùng thành công",
  "data": {
    "userId": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    "isActive": false,
    "lockReason": "Vi phạm điều khoản cộng đồng: Đăng tin giả mạo và quấy rối người thuê khác.",
    "lockedUntil": "2026-10-23T11:55:00Z"
  }
}
```

---

#### 103. POST /admin/users/{userId}/unlock
* **Method:** `POST`
* **Endpoint:** `/admin/users/{userId}/unlock`
* **Quyền hạn:** `ADMIN`
* **Dẫn chứng UI:**
  - Thư mục: `9b._m_kh_a_t_i_kho_n_unlock_account/code.html`
  - Vị trí UI: Modal xác nhận "Mở khóa tài khoản" kèm ô nhập Ghi chú mở khóa và nút bấm **"Mở khóa tài khoản"**.
* **Request Payload (application/json):**
```json
{
  "unlockReason": "Người dùng đã giải trình khiếu nại thành công và cam kết tuân thủ quy chế."
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Mở khóa tài khoản người dùng thành công",
  "data": {
    "userId": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    "isActive": true,
    "unlockedAt": "2026-09-23T11:58:00Z"
  }
}
```

---

#### 104. GET /admin/buildings
* **Method:** `GET`
* **Endpoint:** `/admin/buildings`
* **Quyền hạn:** `ADMIN`
* **Dẫn chứng UI:**
  - Thư mục: `10._h_ng_i_ph_duy_t_b_t_ng_s_n_property_approval_queue/code.html`
  - Vị trí UI: Danh sách hàng đợi bất động sản chờ phê duyệt: Tên tòa nhà, Chủ sở hữu, Địa chỉ, Số phòng, Ngày nộp hồ sơ, Nút xem xét kiểm duyệt.
* **Query Parameters:**
  - `status` *(string, default=PENDING_APPROVAL)*: `PENDING_APPROVAL`, `ACTIVE`, `REJECTED`.
  - `pageNo` / `pageSize` *(integer)*.
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy danh sách hàng đợi phê duyệt bất động sản thành công",
  "data": {
    "items": [
      {
        "id": "e4f5a6b7-c8d9-0123-ef45-6789abcdef01",
        "buildingName": "Tòa nhà Rentify Central Park",
        "landlordName": "Lê Văn Chủ",
        "landlordPhone": "0909000111",
        "address": "123 Nguyễn Thị Minh Khai, P. Võ Thị Sáu, Q.3, TP.HCM",
        "totalRooms": 20,
        "submittedAt": "2026-09-23T09:30:00Z",
        "status": "PENDING_APPROVAL"
      }
    ],
    "pagination": {
      "pageNo": 1,
      "pageSize": 10,
      "totalItems": 1,
      "totalPages": 1
    }
  }
}
```

---

#### 105. POST /admin/buildings/{buildingId}/approve
* **Method:** `POST`
* **Endpoint:** `/admin/buildings/{buildingId}/approve`
* **Quyền hạn:** `ADMIN`
* **Dẫn chứng UI:**
  - Thư mục: `11._chi_ti_t_ph_duy_t_b_t_ng_s_n_property_approval_detail/code.html`
  - Vị trí UI: Màn hình thẩm định hồ sơ: Nút xanh lá nổi bật **"Phê duyệt bất động sản"** kèm ô ghi chú kiểm duyệt.
* **Request Payload (application/json):**
```json
{
  "approvalNotes": "Hồ sơ giấy chứng nhận quyền sở hữu nhà ở hợp lệ và chính chủ."
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Phê duyệt bất động sản thành công. Tòa nhà đã chính thức hiển thị công khai.",
  "data": {
    "buildingId": "e4f5a6b7-c8d9-0123-ef45-6789abcdef01",
    "status": "ACTIVE",
    "approvedAt": "2026-09-23T12:00:00Z"
  }
}
```

---

#### 106. POST /admin/buildings/{buildingId}/reject
* **Method:** `POST`
* **Endpoint:** `/admin/buildings/{buildingId}/reject`
* **Quyền hạn:** `ADMIN`
* **Dẫn chứng UI:**
  - Thư mục: `12._t_ch_i_ph_duy_t_reject_property/code.html`
  - Vị trí UI: Modal "Từ chối phê duyệt bất động sản" kèm ô chọn Danh mục lý do từ chối (Ảnh mờ, Sai địa chỉ, Thiếu giấy tờ) và nút bấm **"Xác nhận từ chối"**.
* **Request Payload (application/json):**
```json
{
  "rejectionReason": "Hình ảnh giấy phép kinh doanh/giấy tờ sở hữu bị mờ, không nhận diện được số hiệu văn bản.",
  "requiredAction": "Vui lòng chụp lại rõ nét giấy chứng nhận quyền sở hữu và nộp lại hồ sơ."
}
```
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Đã từ chối phê duyệt bất động sản. Thông báo đã gửi đến chủ nhà.",
  "data": {
    "buildingId": "e4f5a6b7-c8d9-0123-ef45-6789abcdef01",
    "status": "REJECTED",
    "rejectionReason": "Hình ảnh giấy phép kinh doanh/giấy tờ sở hữu bị mờ, không nhận diện được số hiệu văn bản.",
    "rejectedAt": "2026-09-23T12:05:00Z"
  }
}
```

---

#### 107. GET /admin/audit-logs
* **Method:** `GET`
* **Endpoint:** `/admin/audit-logs`
* **Quyền hạn:** `ADMIN`
* **Dẫn chứng UI:**
  - Thư mục: `13._nh_t_k_ki_m_to_n_audit_logs/code.html`
  - Vị trí UI: Bảng tra cứu nhật ký kiểm toán hệ thống: Thời gian, Người thực hiện (Tên, Email, Vai trò), Hành động (Tạo, Sửa, Khóa, Duyệt), Đối tượng (Người dùng, Tòa nhà, Hợp đồng, Hóa đơn), Địa chỉ IP và Nút xem chi tiết thay đổi.
* **Query Parameters:**
  - `actorUserId` *(UUID, optional)*.
  - `entityType` *(string, optional)*: `USER`, `BUILDING`, `CONTRACT`, `INVOICE`, `PAYMENT`.
  - `from` / `to` *(string, optional)*: Thời gian bắt đầu / kết thúc (ISO-8601).
  - `pageNo` / `pageSize` *(integer)*.
* **Response Mẫu (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Lấy danh sách nhật ký kiểm toán thành công",
  "data": {
    "items": [
      {
        "id": "aud_11223344-5566-7788-9900-aabbccddeeff",
        "actor": {
          "userId": "adm_0011-2233-4455-6677",
          "fullName": "Admin Hệ Thống",
          "role": "ADMIN"
        },
        "action": "LOCK_USER",
        "entityType": "USER",
        "entityId": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
        "ipAddress": "14.232.208.105",
        "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
        "createdAt": "2026-09-23T11:55:00Z"
      }
    ],
    "pagination": {
      "pageNo": 1,
      "pageSize": 10,
      "totalItems": 1,
      "totalPages": 1
    }
  }
}
```

---

#### 108. GET /admin/audit-logs/export
* **Method:** `GET`
* **Endpoint:** `/admin/audit-logs/export`
* **Quyền hạn:** `ADMIN`
* **Dẫn chứng UI:**
  - Thư mục: `13._nh_t_k_ki_m_to_n_audit_logs/code.html`
  - Vị trí UI: Nút bấm **"Xuất file Excel"** trên thanh công cụ bảng nhật ký kiểm toán.
* **Query Parameters:**
  - `from` / `to` *(string, optional)*.
  - `entityType` *(string, optional)*.
  - `format` *(string, default=xlsx)*: `xlsx` hoặc `csv`.
* **Response Mẫu (200 OK - File Stream):**
  - Headers: `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, `Content-Disposition: attachment; filename="audit_logs_20260923.xlsx"`

---

#### 109. GET /admin/audit-logs/{auditLogId}/export
* **Method:** `GET`
* **Endpoint:** `/admin/audit-logs/{auditLogId}/export`
* **Quyền hạn:** `ADMIN`
* **Dẫn chứng UI:**
  - Thư mục: `14._chi_ti_t_nh_t_k_ki_m_to_n_audit_log_detail_popup/code.html`
  - Vị trí UI: Nút bấm **"Xuất chi tiết bản ghi (JSON/CSV)"** bên trong popup xem chi tiết lịch sử kiểm toán.
* **Query Parameters:**
  - `format` *(string, default=json)*: `json` hoặc `csv`.
* **Response Mẫu (200 OK - File Stream):**
  - Headers: `Content-Type: application/json`, `Content-Disposition: attachment; filename="audit_log_detail_aud1122.json"`
```json
{
  "auditLogId": "aud_11223344-5566-7788-9900-aabbccddeeff",
  "actorUserId": "adm_0011-2233-4455-6677",
  "action": "LOCK_USER",
  "entityType": "USER",
  "entityId": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
  "oldValues": {
    "isActive": true
  },
  "newValues": {
    "isActive": false,
    "lockReason": "Vi phạm điều khoản cộng đồng: Đăng tin giả mạo và quấy rối người thuê khác."
  },
  "ipAddress": "14.232.208.105",
  "createdAt": "2026-09-23T11:55:00Z"
}
```
