# PBL6 — Đặc tả API v1

> **Trạng thái:** hợp đồng API chuẩn cho P2-06 / bàn giao OpenAPI
> **Base path:** `/api/v1`
> **Quy mô:** 109 endpoint trong 24 nhóm domain; mục 27 mô tả chi tiết từng endpoint theo tỉ lệ 1:1. *(106/24 sau D49, rồi +3 endpoint theo D50)*
> **Nguồn:** `api-conventions.md`, `phase-1/discovery/database-design.md`, các luồng người dùng, `utility-billing-calculations.md`
> **Phạm vi:** quản lý nhà trọ cho thuê. Tài liệu này không bổ sung tính năng sản phẩm mới.

---

## 2. Auth

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 1 | `POST /auth/register` | `public` | Đăng ký tài khoản tenant hoặc landlord | Body: `email`, `phone`, `password`, `name`, `role`; role không được là `admin`; response đặt refresh cookie. |
| 2 | `POST /auth/login` | `public` | Bắt đầu phiên làm việc | Body: `identifier`, `password`, `rememberMe`; response chứa access token và đặt refresh cookie. |
| 3 | `POST /auth/refresh` | `tenant`, `landlord`, `admin` | Xoay vòng phiên refresh | Không có body token; đọc refresh cookie, xoay token, trả access token mới. |
| 4 | `POST /auth/logout` | `tenant`, `landlord`, `admin` | Thu hồi phiên hiện tại | Thu hồi phiên refresh hiện tại và xoá cookie. |
| 5 | `POST /auth/password-reset-requests` | `public` | Yêu cầu link đặt lại mật khẩu | Body: `email`; luôn trả kết quả trung tính giống nhau. |
| 6 | `POST /auth/password-resets` | `public` | Dùng token đặt lại mật khẩu một lần | Body: `token`, `newPassword`; token dùng một lần và có thời hạn. |

---

## 3. User

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 7 | `GET /me` | `tenant`, `landlord`, `admin` | Lấy profile hiện tại | Dữ liệu khởi tạo phiên: `id`, `name`, `email`, `phone`, `role`, `status` và tóm tắt ảnh đại diện. Chủ nhà nhận thêm `payoutAccount` (D39). |
| 8 | `PATCH /me` | `tenant`, `landlord`, `admin` | Cập nhật profile hiện tại | Body: `name`, `phone`; chủ nhà gửi thêm `payoutAccount` (3 trường, gửi đủ cả ba). `email` và `role` không đổi được ở đây. Bị chặn khi còn hóa đơn `pending`. |
| 9 | `PUT /me/password` | `tenant`, `landlord`, `admin` | Đổi mật khẩu hiện tại | Body: `currentPassword`, `newPassword`, `confirmPassword`; thu hồi các phiên khác. |
| 10 | `GET /users` | `admin` | Liệt kê và tìm kiếm người dùng | Bộ lọc: `filter[role]`, `filter[status]`, `filter[q]`, `sort`, `order`; hỗ trợ `format`. |
| 11 | `GET /users/{userId}` | `admin` | Đọc một người dùng kèm tổng quan vận hành | Trả profile, số tòa nhà/hợp đồng liên quan và trạng thái. |
| 12 | `PATCH /users/{userId}` | `admin` | Sửa thông tin tài khoản người dùng | Chỉ sửa `name`, `phone`, `email`. Không sửa được `role` hay `status`; hai việc đó là action riêng (API 13, API 14). |
| 13 | `POST /users/{userId}/lock` | `admin` | Khoá một tài khoản đang hoạt động | **Giữ dạng action, không nhét vào PATCH**, vì khoá là chuyển trạng thái có điều kiện và phải ghi audit log. Body: `lockReason` bắt buộc. |
| 14 | `POST /users/{userId}/unlock` | `admin` | Mở khoá tài khoản đang bị khoá | Không có body. Mở khoá là chuyển `status` từ `locked` về `active` và xoá `lockedAt`. |
| 15 | `DELETE /users/{userId}` | `admin` | Xóa mềm một người dùng | Đặt `is_deleted = true` và cascade mềm sang bảng con; chứng từ tài chính/pháp lý/kiểm toán được giữ nguyên. Xem mục 28.4. |

---

## 4. PushDevice (Pending)

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 16 | `POST /me/push-devices` | `tenant`, `landlord`, `admin` | Đăng ký device token | Body: `platform` (`android` hoặc `web`), `token`; upsert theo token. |
| 17 | `DELETE /me/push-devices/{deviceId}` | `tenant`, `landlord`, `admin` | Gỡ device token | Chỉ xóa được bản ghi device của chính người dùng hiện tại. |

---

## 5. Media

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 18 | `POST /media/presign-upload` | `tenant`, `landlord`, `admin` | Xin URL upload đã ký | Body: `ownerType`, `ownerId`, `purpose`, `fileName`, `contentType`, `size`; trả `mediaId`, `uploadUrl` và `requiredHeaders`. Chưa có bản ghi hoàn chỉnh cho tới khi hoàn tất API 19. |
| 19 | `POST /media/{mediaId}/complete-upload` | `tenant`, `landlord`, `admin` | Chốt upload | Không có body; xác minh tệp đã nằm trên storage rồi chuyển bản ghi sang trạng thái sẵn sàng đọc. Phải khớp `ownerType`/`ownerId`/`purpose` với API 18. |
| 20 | `GET /media/{mediaId}` | *(để trống)* | Đọc hoặc stream một tệp | Cột quyền để trống có chủ ý: quyền kế thừa từ tài nguyên cha qua `ownerType`/`ownerId`. Chỉ `public` khi media thuộc building/room đã duyệt; media riêng tư theo quyền cha. |
| 21 | `DELETE /media/{mediaId}` | `tenant`, `landlord`, `admin` | Xóa mềm tệp đã tải lên | Chỉ cho phép khi người gọi sửa được tài nguyên cha; media hợp đồng/bằng chứng đã ký vẫn được giữ lại. |

---

## 6. Building

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 22 | `GET /buildings` | `public` | Sàn tìm kiếm tòa nhà đã duyệt | Chỉ trả tòa nhà `status = approved`. Bộ lọc: `filter[province]`, `filter[ward]`, `filter[q]`; `sort`, `order`; hỗ trợ `format`. DTO chỉ gồm trường công khai. |
| 23 | `GET /buildings/landlord` | `landlord` | Danh sách tòa nhà chủ nhà sở hữu | Tự lọc theo `landlordId` của người gọi; client không gửi `landlordId`. Bộ lọc: `filter[status]`; `sort`, `order`; hỗ trợ `format`. DTO có thêm tổng số phòng và tỷ lệ lấp đầy. **Không có trường cấu hình VietQR** (D39 — cấu hình QR thuộc hồ sơ chủ nhà, xem `GET /me`). |
| 24 | `GET /buildings/admin` | `admin` | Xem và quản lý mọi tòa nhà trong hệ thống | Bộ lọc: `filter[status]`, `filter[landlordId]`, `filter[province]`, `filter[ward]`, `filter[q]`; `sort`, `order`; hỗ trợ `format`. Mặc định `filter[status]=pending` để lấy hàng đợi duyệt. |
| 25 | `POST /buildings` | `landlord` | Gửi tòa nhà để duyệt | Body: `name`, `province`, `ward`, `address`; server tự geocode `latitude`/`longitude`; status là `pending`. |
| 26 | `GET /buildings/{buildingId}` | `public` | Chi tiết công khai của một tòa nhà đã duyệt | Chỉ trả trường công khai. Tòa nhà `pending` hoặc `rejected` trả `404` để không lộ trạng thái duyệt. |
| 27 | `GET /buildings/{buildingId}` | `landlord`. `admin` | Chi tiết quản trị của tòa nhà chủ nhà sở hữu | Chỉ trả về khi `building.landlordId` khớp người gọi, nếu không `404` hoặc `admin`. |
| 28 | `PATCH /buildings/{buildingId}` | `landlord` | Chủ nhà sửa thông tin tòa nhà của mình | Chỉ sửa `name`, `description`. |
| 29 | `PATCH /buildings/{buildingId}/status` | `admin` | Admin duyệt/từ chối tòa nhà đang chờ | **Giữ dạng action, không nhét vào PATCH.** Chuyển `status` từ `pending` sang `approved` hoặc `rejected` và ghi audit log. Body: `note` tuỳ chọn. |
| 30 | `DELETE /buildings/{buildingId}` | `landlord` | Xóa mềm một tòa nhà | Đặt `is_deleted = true` và cascade mềm sang phòng, chính sách giá và cài đặt hóa đơn. Hợp đồng, hóa đơn, thanh toán và kiểm toán được giữ nguyên. Xem mục 28.4. |

---

## 7. Room

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 33 | `GET /rooms` | `public` | Sàn tìm kiếm phòng còn trống | Chỉ trả phòng `status = available` thuộc tòa nhà `approved`. Bộ lọc: `filter[province]`, `filter[ward]`, `filter[minPrice]`, `filter[maxPrice]`, `filter[genderPolicy]`, `sort`, `order`; hỗ trợ `format`. |
| 34 | `GET /rooms/landlord` | `landlord` | Chủ nhà quản lý toàn bộ phòng thuộc tòa nhà của mình | Tự lọc theo `landlordId` qua `Building`. Bộ lọc: `filter[buildingId]`, `filter[status]` (`available`/`occupied`/`cleaning`), `sort`, `order`; hỗ trợ `format`. |
| 35 | `POST /rooms` | `landlord` | Tạo phòng trong một tòa nhà | Body: `buildingId`, `name`, `floorNumber`, `area`, `amenities`, `maxOccupancy`, `genderPolicy`, `rentPrice`, `description`; không dùng path lồng building. |
| 36 | `GET /rooms/{roomId}` | `public` | Đọc một phòng | Gồm trường công khai, tình trạng khả dụng, tóm tắt media và tóm tắt chính sách giá đang hiệu lực. |
| 37 | `PATCH /rooms/{roomId}` | `landlord` | Chủ nhà sửa thông tin phòng của mình | Body chứa mọi field phòng sửa được. `landlordId` và `buildingId` không đổi qua route này. |
| 38 | `DELETE /rooms/{roomId}` | `landlord` | Xóa mềm một phòng | Đặt `is_deleted = true`, cascade theo mục 28.4. Phòng đang có hợp đồng hiệu lực trả `409 ROOM HAS ACTIVE CONTRACT`. Xem D50. |

---

## 8. FavoriteRoom

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 39 | `GET /favorite-rooms` | `tenant` | Liệt kê phòng đã lưu | Phân trang offset; hỗ trợ `format`; chỉ trả bản ghi của chính tenant hiện tại. |
| 40 | `POST /favorite-rooms` | `tenant` | Lưu một phòng | Body: `roomId`; idempotent cho cùng cặp tenant/phòng. |
| 41 | `DELETE /favorite-rooms/{roomId}` | `tenant` | Bỏ lưu một phòng | Xóa bản ghi của tenant hiện tại; trả `204`. |

---

## 9. RoommateProfile

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 42 | `GET /roommate-profiles` | `tenant` | Duyệt feed hồ sơ tìm bạn ở | Bộ lọc: `filter[preferredArea]`, `filter[budgetMin]`, `filter[budgetMax]`, `filter[moveInFrom]`, `filter[moveInTo]`; chỉ trả hồ sơ `isVisible=true` và không phải của chính người gọi. |
| 43 | `GET /roommate-profiles/{roommateProfileId}` | `tenant` | Đọc một hồ sơ tìm bạn ở theo định danh | Chỉ trả hồ sơ `isVisible=true`; tenant không xem được hồ sơ `isVisible=false` của người khác. |
| 44 | `GET /roommate-profile` | `tenant` | Đọc profile của chính mình | Trả `RoommateProfile` của tenant hiện tại, kể cả khi `isVisible=false`, hoặc `404` nếu chưa tạo. |
| 45 | `PUT /roommate-profile` | `tenant` | Tạo hoặc cập nhật profile của chính mình | Body theo field database: `lifestyle`, `personality`, `budgetMin`, `budgetMax`, `bio`, `preferredArea`, `moveInOn`, `isVisible`. |

---

## 10. MatchRequest

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 46 | `GET /match-requests` | `tenant` | Liệt kê yêu cầu đến hoặc đi | Bộ lọc: `filter[direction]` (`incoming`/`outgoing`), `filter[status]`, phân trang. Không có quyền admin. |
| 47 | `POST /match-requests` | `tenant` | Gửi yêu cầu tìm bạn ở | Body: `targetId`; người gửi là tenant hiện tại; chặn tự gửi cho mình và chặn trùng cặp `(requesterId, targetId)` vì cặp này là duy nhất trong database. `MatchRequest` không có cột message nên yêu cầu không mang văn bản tự do. |
| 48 | `POST /match-requests/{matchRequestId}/accept-request` | `tenant` | Chấp nhận yêu cầu | Chỉ tenant nhận được yêu cầu mới chấp nhận; tạo hoặc resolve một conversation loại `direct`. |
| 49 | `POST /match-requests/{matchRequestId}/reject-request` | `tenant` | Từ chối yêu cầu | Chỉ tenant nhận được yêu cầu mới từ chối; chỉ yêu cầu `pending` mới chuyển trạng thái. |
| 50 | `DELETE /match-requests/{matchRequestId}` | `tenant` | Người gửi rút yêu cầu | **Chỉ `requester`** mới rút được; bên nhận dùng `reject-request`. Chuyển `status` từ `pending` sang `withdrawn`. Không có body. Xem D50. |

---

## 11. RatePolicy

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 51 | `GET /rate-policies` | `landlord` | Liệt kê chính sách đơn giá và phí định kỳ | Bộ lọc: `filter[scope]`, `filter[buildingId]`, `filter[roomId]`, `filter[type]`, `filter[isActive]`. Không có quyền admin: admin không quản lý cấu hình giá của chủ nhà. |
| 52 | `POST /rate-policies` | `landlord` | Tạo một chính sách đơn giá hoặc phí | Body: `scope`, `buildingId`, `roomId`, `name`, `rate`; đúng một định danh cha theo phạm vi. |
| 53 | `PATCH /rate-policies/{ratePolicyId}` | `landlord` | Đổi tên chính sách | Chỉ sửa được `name`, `rate`, `is_active`; đổi giá tạo bản ghi mới và vô hiệu hoá bản ghi cũ. |

---

## 12. BillingSetting (Đang thiếu API get by ID, coi thử ở phần UI ra răng, cần thì thêm vô)

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 54 | `GET /billing-settings` | `landlord` | Liệt kê cài đặt thanh toán và nhắc hóa đơn | Bộ lọc: `filter[scope]`, `filter[buildingId]`, `filter[roomId]`, `filter[isActive]`. Không có quyền admin, đồng bộ với RatePolicy. |
| 55 | `POST /billing-settings` | `landlord` | Tạo một cài đặt hóa đơn | Body: `scope`, `buildingId`, `roomId`, `dueDays`, `remindDays`, `botEnabled`; ngày thanh toán không lưu trên Contract. |
| 56 | `PATCH /billing-settings/{billingSettingId}` | `landlord` | Cập nhật cài đặt hóa đơn | Body gồm các field sửa được `dueDays`, `remindDays`, `botEnabled`; ngày phải nằm trong khoảng cho phép của database. |

---

## 13. ContractTemplate

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 57 | `GET /contract-templates` | `landlord` | Liệt kê mẫu khả dụng | Dữ liệu tĩnh seed trong code; không có route tạo, sửa hoặc xóa. |
| 58 | `GET /contract-templates/{contractTemplateId}` | `landlord` | Đọc một mẫu | Trả tiêu đề, phiên bản và các biến bắt buộc. |

---

## 14. Contract (64 - 67 đang phân vân)

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 59 | `GET /contracts/tenant` | `tenant` | Tenant xem hợp đồng mình tham gia hoặc đứng tên | Lấy hợp đồng qua `Contract.tenantId` và các bản ghi `ContractMember` đang hoạt động của người gọi. Bộ lọc: `filter[status]`, `filter[roomId]`; hỗ trợ `format`. |
| 60 | `GET /contracts/landlord` | `landlord` | Chủ nhà quản lý hợp đồng trong các phòng của mình | Tự lọc theo `landlordId` qua `Room`. Bộ lọc: `filter[roomId]`, `filter[buildingId]`, `filter[status]`, `filter[tenantId]`; hỗ trợ `format`. |
| 61 | `POST /contracts` | `landlord` | Tạo hợp đồng nháp | Body: `roomId`, `tenantId` (nullable), `tenantName`, `tenantPhone`, `depositAmount`, `rentPrice`, `startDate`, `endDate`, `description`, `vehicleCount`; quy tắc tài khoản liên kết và liên hệ theo D29. |
| 62 | `GET /contracts/{contractId}` | `landlord`, `tenant` | Đọc một hợp đồng | Chỉ hợp đồng liên kết với `tenantId` của người gọi hoặc có bản ghi `ContractMember` đang hoạt động mới hiển thị. Không có quyền admin. |
| 63 | `PATCH /contracts/{contractId}` | `landlord` | Sửa hợp đồng nháp | Chỉ hợp đồng `draft` mới sửa được; sau khi kích hoạt, tệp hợp đồng đã ký là nguồn pháp lý. |
| 64 | `PUT /contracts/{contractId}/template` | `landlord` | Áp mẫu vào hợp đồng nháp | Body: `contractTemplateId`; chỉ thay nội dung nháp do hệ thống sinh. |
| 65 | `POST /contracts/{contractId}/generate-draft-document` | `landlord` | Sinh tài liệu nháp | Body: biến mẫu tuỳ chọn; trả về bản ghi Media có `purpose=contract_template`. |
| 66 | `POST /contracts/{contractId}/activate-contract` | `landlord` | Kích hoạt hợp đồng đã ký | **Giữ dạng action, không chuyển sang PATCH**, vì kích hoạt là một bước vòng đời có điều kiện: cần tệp đã ký hợp lệ và chuyển trạng thái từ `draft`/`signed` sang `active`. Body: `signedContractMediaId`. |
| 67 | `POST /contracts/{contractId}/complete-checkout` | `landlord` | Hoàn tất trả phòng | **Giữ dạng action** vì bước này phát sinh hóa đơn quyết toán, tức là có side effect ngoài bản ghi hợp đồng. Body: `completedOn`; dùng các thao tác chỉ số và hóa đơn riêng cho phần quyết toán. Trạng thái DB liên quan đang pending, xem mục 28.2. |

---

## 15. ContractMember

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 68 | `POST /contract-members` | `landlord` | Thêm một thành viên vào hợp đồng | Body: `contractId`, `tenantId` (nullable), `tenantName`, `tenantPhone`, `joinedAt`; media CCCD dùng `ownerType=contract_member`. |
| 69 | `PATCH /contract-members/{contractMemberId}` | `landlord` | Cập nhật liên hệ hoặc ngày của thành viên | Chỉ landlord được sửa. Path param là `contractMemberId`, không phải `memberId`, để khớp tên bảng. |
| 70 | `POST /contract-members/{contractMemberId}/leave` | `landlord` | Ghi nhận thành viên rời đi | **Không dùng DELETE** vì cần giữ mốc thời gian rời hợp đồng và lịch sử thành viên.|
| 71 | `GET /contract-members` | `landlord`, `tenant` | Liệt kê thành viên | **Bắt buộc có `filter[contractId]`**; landlord xem hợp đồng của mình, tenant chỉ xem thành viên của hợp đồng mình tham gia. Hỗ trợ `format`; không dùng path lồng contract. |

---

## 16. MeterReading

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 72 | `GET /meter-readings` | `landlord` | Liệt kê chỉ số đồng hồ | Bộ lọc: `filter[roomId]`, `filter[type]`, `filter[period]`; phân trang. |
| 73 | `POST /meter-readings/ocr-result` | `landlord` | Xem trước kết quả chuẩn hoá OCR | Body: `roomId`, `mediaId`, `type` (media đã qua bước `presign-upload`); trả kết quả để rà soát và không bao giờ tự xác nhận bằng chứng. |
| 74 | `POST /meter-readings` | `landlord` | Tạo một chỉ số đã xác nhận | Body: `roomId`, `type`, `period`, `previousReading`, `currentReading`, `readingDate`, `isBaseline`, `evidenceMediaId`; khóa duy nhất là `(roomId, type, period)`; mỗi lần gọi một chỉ số, không phải lô theo tòa nhà. |

---

## 17. Invoice

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 75 | `GET /invoices/tenant` | `tenant` | Tenant xem hóa đơn cần thanh toán của chính mình | Lấy hóa đơn qua `Contract` mà người gọi tham gia. Bộ lọc: `filter[status]`, `filter[period]`, `filter[contractId]` |
| 76 | `GET /invoices/landlord` | `landlord` | Chủ nhà quản lý hóa đơn các phòng, theo dõi công nợ quá hạn | Tự lọc theo `landlordId` qua `Contract` và `Room`. Bộ lọc: `filter[contractId]`, `filter[roomId]`, `filter[buildingId]`, `filter[status]`, `filter[period]` |
| 77 | `POST /invoices` | `landlord` | Tạo hóa đơn | |
| 78 | `GET /invoices/{invoiceId}` | `landlord`, `tenant` | Đọc hóa đơn kèm tổng hợp thanh toán | Gồm snapshot bất biến `breakdown` và `otherFees`, `totalAmount`, số tiền đã trả và số tiền còn lại. Không có quyền admin. |
| 79 | `PATCH /invoices/{invoiceId}` | `landlord` | Sửa hóa đơn đang chờ | Chỉ sửa được các field của hóa đơn `pending` hoặc do hệ thống sinh; hóa đơn đã phát hành phải huỷ và tạo lại, không sửa tại chỗ. |
| 80 | `POST /invoices/issue-invoice` | `landlord` | Phát hành nhiều hóa đơn chờ theo lô | **Bulk action.** Body: `invoiceIds[]`, `sendNotification` tuỳ chọn; yêu cầu header `Idempotency-Key`. Đặt `issuedAt` cho từng hóa đơn; `code` ổn định đã gán lúc tạo chính là giá trị mà payload VietQR và webhook mang. Trả kết quả theo từng hóa đơn. |
| 81 | `POST /invoices/{invoiceId}/cancel-invoice` | `landlord` | Huỷ một hóa đơn sai | Body: `note`; đặt trạng thái `void` và ghi lý do vào audit log. Vẫn là thao tác một hóa đơn vì huỷ cần lý do riêng. |
| 82 | `POST /invoices/send-reminder` | `landlord` | Nhắc ngày thu dự kiến cho nhiều hóa đơn theo lô | **Bulk action.** Body: `invoiceIds[]`, `channel`; yêu cầu header `Idempotency-Key`. **D39:** nhắc theo `BillingSetting.remind_day`, không lọc theo "quá hạn" (không có `overdue`); chỉ hóa đơn `issued` chưa thu đủ mới nhận được; trả kết quả theo từng hóa đơn. |

---

## 18. Payment (Pending)

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 83 | `GET /me/payments` | `tenant` | Tenant xem các giao dịch mình đã thanh toán | Lấy thanh toán qua `Invoice` thuộc hợp đồng của người gọi. Bộ lọc: `filter[invoiceId]`, `filter[method]`, `filter[paymentStatus]`; hỗ trợ `format`. |
| 84 | `GET /payments` | `landlord` | Chủ nhà đối soát dòng tiền và lịch sử nhận tiền | Tự lọc theo `landlordId` qua `Invoice` → `Contract` → `Room`. Bộ lọc: `filter[invoiceId]`, `filter[contractId]`, `filter[method]`, `filter[paymentStatus]`; hỗ trợ `format`. |
| 85 | `POST /payments/create-intent` | `tenant` | Tạo ý định thanh toán | Body: `invoiceId`, `method`; bắt buộc `Idempotency-Key`; số tiền lấy từ hóa đơn trừ khi có quy tắc trả một phần. |
| 86 | `POST /payments/record-cash-payment` | `landlord` | Ghi nhận thanh toán tiền mặt | Body: `invoiceId`, `amount`, `transactionId` tuỳ chọn, `receiptMediaId`; bắt buộc `Idempotency-Key`. |
| 87 | `POST /payments/webhooks/{provider}` | `system` | Nhận callback đã ký từ provider | Bắt buộc kiểm chữ ký provider và chống gọi lặp; phản hồi xác nhận theo hợp đồng provider và không dùng JSON wrapper. |

---

## 19. IssueReport

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 88 | `GET /issues/tenant` | `tenant` | Tenant xem các sự cố mình đã báo cáo | Tự lọc theo `reporterId` của người gọi. Bộ lọc: `filter[status]`, `filter[roomId]`; `sort`, `order`; hỗ trợ `format`. |
| 89 | `GET /issues/landlord` | `landlord` | Chủ nhà theo dõi sự cố ở các tòa nhà của mình | Tự lọc theo `landlordId` qua `Room` và `Building`. Bộ lọc: `filter[roomId]`, `filter[buildingId]`, `filter[status]`; `sort`, `order`; hỗ trợ `format`. |
| 90 | `POST /issues` | `tenant`, `landlord` | Báo cáo sự cố | Body: `roomId`, `title`, `description`, `conversationId` tuỳ chọn, `issuePhotoMediaIds`, và `reporterId` khi landlord báo thay tenant thụ động; media dùng `ownerType=issue_report`, `purpose=issue_photo`. |
| 91 | `GET /issues/{issueId}` | `landlord`, `tenant` | Đọc chi tiết sự cố | Tenant chỉ truy cập được trong phạm vi phòng và ngữ cảnh sự cố của mình. |
| 92 | `PATCH /issues/{issueId}` | `landlord` | Chủ nhà cập nhật tiến trình, ghi chú hoặc đóng sự cố | Chỉ `landlord` sở hữu tòa nhà chứa phòng của sự cố. Đóng sự cố là đặt `status` = `resolved` hoặc `closed`. |
| 93 | `POST /issues/{issueId}/cancel` | `tenant` | Tenant huỷ báo cáo của chính mình khi sự cố còn `open` | **Giữ dạng action, không nhét vào PATCH.** Chỉ huỷ được sự cố `open` do chính người gọi báo. Không có body. |

---

## 20. Conversation

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 94 | `GET /conversations` | `tenant`, `landlord` | Liệt kê các hội thoại của người gọi | Bộ lọc: `filter[type]` (`room`, `building`, `direct`); chỉ thấy bản ghi `ConversationMember` của mình. **Không có quyền admin.** |
| 95 | `GET /conversations/{conversationId}` | `tenant`, `landlord` | Đọc chi tiết hội thoại | Bắt buộc kiểm tra thành viên; unread count và tin nhắn cuối là dữ liệu dựng sẵn. Không có quyền admin. |
| 96 | `POST /conversations/resolve-conversation` | `tenant`, `landlord` | Lấy hội thoại của phòng hoặc tòa nhà | Body: đúng một trong `contractId` hoặc `buildingId`; trả hội thoại đã có, chỉ tạo mới khi vòng đời cho phép. Không có quyền admin. |

---

## 21. Message (Pending)

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 97 | `GET /messages` | `tenant`, `landlord` | Liệt kê tin nhắn trong một hội thoại | Bộ lọc: `filter[conversationId]`; phân trang cursor; không dùng path lồng conversation. Không có quyền admin. |
| 98 | `POST /messages` | `tenant`, `landlord` | Gửi tin nhắn | Body: `conversationId`, `type`, `content`, `mediaId` tuỳ chọn; media đính kèm dùng `ownerType=message`. Không có quyền admin. |
| 99 | `POST /messages/mark-read` | `tenant`, `landlord` | Đánh dấu đã đọc một hội thoại | Body: `conversationId`, `lastReadMessageId`; con trỏ đã đọc là điều kiện migration vì bảng hiện tại chưa có cột này. Không có quyền admin. |

---

## 22. Notification (Pending)

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 100 | `GET /notifications` | `tenant`, `landlord`, `admin` | Liệt kê thông báo | Bộ lọc: `filter[unreadOnly]`; phân trang cursor; `data` gồm tổng số chưa đọc. |
| 101 | `POST /notifications/{notificationId}/mark-read` | `tenant`, `landlord`, `admin` | Đánh dấu đã đọc một thông báo | Chỉ thông báo của chính người dùng hiện tại mới được thay đổi. |
| 102 | `POST /notifications/mark-all-read` | `tenant`, `landlord`, `admin` | Đánh dấu đã đọc toàn bộ thông báo chưa đọc | Action vòng đời có tên; không có endpoint bulk chung và không vượt phạm vi người dùng. |

---

## 23. NotificationPreference (Pending)

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 103 | `GET /me/notification-preference` | `tenant`, `landlord`, `admin` | Đọc tuỳ biến thông báo | Trả một bản ghi cho mỗi `type` (`invoice`, `chat`, `issue`, `match`, `account`). |
| 104 | `PUT /me/notification-preference` | `tenant`, `landlord`, `admin` | Thay toàn bộ tuỳ biến thông báo | Body: `preferences[]` gồm `type` và `enabled`; đây là tài nguyên của một người dùng, không phải lô chéo người dùng. |

---

## 24. AuditLog (Pending)

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 105 | `GET /audit-logs` | `admin` | Tìm kiếm nhật ký chỉ ghi thêm | Bộ lọc: `filter[actorUserId]`, `filter[entityType]`, `from`, `to`; hỗ trợ `format`. |
| 106 | `GET /audit-logs/{auditLogId}` | `admin` | Đọc hoặc xuất một bản ghi kiểm toán | Mặc định trả JSON; giá trị `format` khác JSON như `csv` hoặc `pdf` có thể trả luồng tệp. |

---

## 25. Dashboard (Pending)

| Mã | Method & path | Quyền | Mục đích | Lưu ý |
|---|---|---|---|---|
| 107 | `GET /dashboard` | `admin` | Đọc số liệu tổng hợp hệ thống | Query: `from`, `to`; chỉ đọc, gom nhiều domain, không phải bảng CRUD. |

---

## 27. Hợp đồng API chi tiết

### 27.1 Auth

#### 1 · `POST /auth/register` — Đăng ký tài khoản

- **Quyền:** `public`
- **Body:** `{ "email":"lan@example.com", "phone":"0901234567", "password":"...", "name":"Lê Văn An", "role":"tenant" }`
- **Success:** `201` `{ "statusCode":201, "code":"REGISTERED", "data":{"id":"<uuid>","role":"tenant","status":"active"} }`; đặt refresh cookie; `Location: /api/v1/me`
- **Lỗi:** `409 DUPLICATE EMAIL` · `422 VALIDATION FAILED` · `422 ROLE NOT ALLOWED`
- **UI:** `4._ng_k_ch_nh_sign_up/code.html` · `4._ng_k_sign_up/code.html` · `5._ng_k_sign_up/code.html`

#### 2 · `POST /auth/login` — Bắt đầu phiên làm việc

- **Quyền:** `public`
- **Body:** `{ "identifier":"lan@example.com", "password":"...", "rememberMe":true }`
- **Success:** `200` `{ "statusCode":200, "code":"LOGGED_IN", "data":{"accessToken":"<jwt>","expiresIn":900} }`; đặt refresh cookie
- **Lỗi:** `401 INVALID TOKEN` · `403 ACCOUNT LOCKED` · `422 VALIDATION FAILED`
- **UI:** `1._ng_nh_p_ch_nh_login/code.html` · `1._ng_nh_p_login/code.html` · `1._ng_nh_p_qu_n_tr_vi_n_admin_login/code.html`

#### 3 · `POST /auth/refresh` — Xoay vòng phiên refresh

- **Quyền:** `tenant`, `landlord`, `admin`
- **Body:** không có; đọc cookie `refreshToken`
- **Success:** `200` `{ "statusCode":200, "code":"SESSION_REFRESHED", "data":{"accessToken":"<jwt>","expiresIn":900} }`; xoay cookie
- **Lỗi:** `401 INVALID TOKEN` · `401 SESSION REVOKED`
- **UI:** không có màn hình riêng — endpoint nền, client tự làm mới phiên đăng nhập

#### 4 · `POST /auth/logout` — Thu hồi phiên hiện tại

- **Quyền:** `tenant`, `landlord`, `admin`
- **Body:** không có
- **Success:** `204`; xoá refresh cookie
- **Lỗi:** `401 INVALID TOKEN`
- **UI:** `4._x_c_nh_n_ng_xu_t_logout_confirmation/code.html` · `6._x_c_nh_n_ng_xu_t_logout_modal_1/code.html` · `7._x_c_nh_n_ng_xu_t_logout_modal/code.html`

#### 5 · `POST /auth/password-reset-requests` — Yêu cầu link đặt lại mật khẩu

- **Quyền:** `public`
- **Body:** `{ "email":"lan@example.com" }`
- **Success:** `202` `{ "statusCode":202, "code":"PASSWORD_RESET_REQUESTED", "data":{"accepted":true} }`
- **Lỗi:** `422 VALIDATION FAILED`
- **UI:** `2._qu_n_m_t_kh_u_forgot_password_1/code.html` · `2._qu_n_m_t_kh_u_forgot_password_2/code.html` · `3._qu_n_m_t_kh_u_forgot_password/code.html`

#### 6 · `POST /auth/password-resets` — Dùng token đặt lại mật khẩu

- **Quyền:** `public`
- **Body:** `{ "token":"<opaque>", "newPassword":"..." }`
- **Success:** `204`
- **Lỗi:** `422 VALIDATION FAILED` · `409 TOKEN USED` · `409 TOKEN EXPIRED`
- **UI:** `3._t_l_i_m_t_kh_u_reset_password_1/code.html` · `4._t_l_i_m_t_kh_u_reset_password/code.html`

### 27.2 User

#### 7 · `GET /me` — Lấy profile hiện tại

- **Quyền:** `tenant`, `landlord`, `admin`
- **Success:** `200` `{ "statusCode":200, "code":"CURRENT_USER_FETCHED", "data":{"id":"<uuid>","name":"Lê Văn An","email":"lan@example.com","phone":"0901234567","role":"tenant","status":"active","payoutAccount":null } }`
- **Lỗi:** `401 INVALID TOKEN`
- **UI:** `31._h_s_c_nh_n_profile/code.html` · `50._h_s_c_nh_n_profile_1/code.html`

> `/me` là tài nguyên của chính người đang đăng nhập, nên không cần truyền `userId` và không thể chỉ tới người khác.

> **`payoutAccount` (D39, chỉ có khi `role = landlord`).** Gộp tài khoản nhận tiền vào hồ sơ chủ nhà, thay cho bảng `VietQrReceiverConfig` và hai endpoint `/vietqr-configs` đã bị gỡ. Cấu trúc: `{ "bankCode":"970415", "accountNumber":"**43210", "accountName":"NGUYEN VAN AN" }`. `accountNumber` được mask khi đọc. Với `tenant` và `admin`, trường này luôn là `null` và không gửi lên được. Đây là nguồn duy nhất của hợp đồng API cho tài khoản nhận tiền — không có endpoint nào khác đọc hoặc sửa nó.

#### 8 · `PATCH /me` — Cập nhật profile hiện tại

- **Quyền:** `tenant`, `landlord`, `admin`
- **Body:** `{ "name":"Lê Văn An", "phone":"0901234567" }` · *(chủ nhà, D39)* `{ "payoutAccount":{ "bankCode":"970415", "accountNumber":"102876543210", "accountName":"NGUYEN VAN AN" } }`
- **Success:** `200` `{ "statusCode":200, "code":"PROFILE_UPDATED", "data":{"id":"<uuid>","name":"Lê Văn An","phone":"0901234567","payoutAccount":{"bankCode":"970415","accountNumber":"**43210","accountName":"NGUYEN VAN AN"}} }`
- **Lỗi:** `422 VALIDATION FAILED` · `409 DUPLICATE PHONE` · `409 PAYOUT_ACCOUNT_IN_USE` *(chỉ khi còn hóa đơn `pending` — xem `database-design.md` §2.9)*
- **UI:** `31._h_s_c_nh_n_profile/code.html` · `50._h_s_c_nh_n_profile_1/code.html` · `50._h_s_c_nh_n_profile_2/code.html`

> Ba trường `payoutAccount` phải gửi đủ cả ba cùng lúc; gửi `null` để xoá cũng phải xác nhận lại. `bank_code` là dữ liệu tra cứu danh mục ngân hàng, không tự do gõ. Cập nhật tài khoản nhận tiền **bị chặn** khi chủ nhà còn hóa đơn `pending` chưa phát hành, vì mã QR đã đưa cho người thuê sẽ không khớp tài khoản mới; hóa đơn `issued` giữ nguyên `code` nên đối soát vẫn tra được.

#### 9 · `PUT /me/password` — Đổi mật khẩu hiện tại

- **Quyền:** `tenant`, `landlord`, `admin`
- **Body:** `{ "currentPassword":"...", "newPassword":"...", "confirmPassword":"..." }`
- **Success:** `204`
- **Lỗi:** `401 INVALID CREDENTIALS` · `422 PASSWORD MISMATCH` · `422 WEAK PASSWORD`
- **UI:** `31._h_s_c_nh_n_profile/code.html`

#### 10 · `GET /users` — Liệt kê và tìm kiếm người dùng

- **Quyền:** `admin`
- **Query:** `filter[role]=tenant` · `filter[status]=active` · `pageNo=1` · `pageSize=20`
- **Success:** `200` `{ "statusCode":200, "code":"USERS_FETCHED", "data":[{"id":"<uuid>","name":"Lê Văn An","role":"tenant","status":"active"}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`
- **Lỗi:** `422 VALIDATION FAILED`
- **UI:** `7._danh_s_ch_ng_i_d_ng_user_list/code.html`

#### 11 · `GET /users/{userId}` — Đọc một người dùng

- **Quyền:** `admin`
- **Success:** `200` `{ "statusCode":200, "code":"USER_FETCHED", "data":{"id":"<uuid>","name":"Lê Văn An","role":"tenant","status":"active","buildingCount":0,"activeContractCount":1} }`
- **Lỗi:** `404 NOT FOUND`
- **UI:** `8._chi_ti_t_ng_i_d_ng_user_detail/code.html`

#### 12 · `PATCH /users/{userId}` — Cập nhật thông tin tài khoản

- **Quyền:** `admin`
- **Body:** `{ "name":"Nguyễn Văn An", "phone":"0901234567" }`
- **Success:** `200` `{ "statusCode":200, "code":"USER_UPDATED", "data":{"userId":"<uuid>","name":"Nguyễn Văn An","phone":"0901234567","status":"active"} }`
- **Lỗi:** `404 NOT FOUND` · `422 VALIDATION FAILED`
- **UI:** `7._danh_s_ch_ng_i_d_ng_user_list/code.html`

> > `status` không nằm trong body của endpoint này. Khoá và mở khoá là action vòng đời riêng, xem D48.

#### 13 · `POST /users/{userId}/lock` — Khoá tài khoản

- **Quyền:** `admin`
- **Body:** `{ "lockReason":"Spam listing" }`
- **Success:** `200` `{ "statusCode":200, "code":"USER_LOCKED", "data":{"userId":"<uuid>","status":"locked","lockReason":"Spam listing","lockedAt":"2026-09-23T11:55:00.000Z"} }`
- **Lỗi:** `404 NOT FOUND` · `409 USER ALREADY LOCKED` · `422 LOCK REASON REQUIRED`
- **UI:** `9a._kh_a_t_i_kho_n_lock_account/code.html`

> > Endpoint này thay thế route cũ `lock-user`. Tài khoản `locked` không đăng nhập được; phiên đang mở bị thu hồi.

#### 14 · `POST /users/{userId}/unlock` — Mở khoá tài khoản

- **Quyền:** `admin`
- **Body:** không có
- **Success:** `200` `{ "statusCode":200, "code":"USER_UNLOCKED", "data":{"userId":"<uuid>","status":"active","lockedAt":null} }`
- **Lỗi:** `404 NOT FOUND` · `409 USER NOT LOCKED`
- **UI:** `9b._m_kh_a_t_i_kho_n_unlock_account/code.html`

> > Endpoint này thay thế route cũ `unlock-user`.

#### 15 · `DELETE /users/{userId}` — Xóa mềm người dùng

- **Quyền:** `admin`
- **Body:** không có
- **Success:** `204`
- **Lỗi:** `404 NOT FOUND` · `409 USER ALREADY DELETED`
- **UI:** `7._danh_s_ch_ng_i_d_ng_user_list/code.html`

> Xóa mềm: đặt cờ `is_deleted = true`, cascade mềm sang bảng con theo mục 28.4. Hợp đồng, hóa đơn, thanh toán và audit log **không** bị xóa. Cột `is_deleted` đã có sẵn trong Base Entity nên không cần migration cột mới.

### 27.3 PushDevice

#### 16 · `POST /me/push-devices` — Đăng ký device token

- **Quyền:** `tenant`, `landlord`, `admin`
- **Body:** `{ "platform":"android", "token":"<fcm-token>" }`
- **Success:** `201` `{ "statusCode":201, "code":"PUSH_DEVICE_REGISTERED", "data":{"id":"<uuid>","platform":"android"} }`; `Location: /api/v1/me/push-devices`
- **Lỗi:** `422 VALIDATION FAILED` · `409 DUPLICATE DEVICE`
- **UI:** `32._c_i_t_th_ng_b_o_notification_settings/code.html` · `51._c_i_t_th_ng_b_o_notification_settings_1/code.html` · `51._c_i_t_th_ng_b_o_notification_settings_3/code.html`

#### 17 · `DELETE /me/push-devices/{deviceId}` — Gỡ device token

- **Quyền:** `tenant`, `landlord`, `admin`
- **Success:** `204`
- **Lỗi:** `404 NOT FOUND`
- **UI:** `32._c_i_t_th_ng_b_o_notification_settings/code.html` · `51._c_i_t_th_ng_b_o_notification_settings_1/code.html` · `51._c_i_t_th_ng_b_o_notification_settings_3/code.html`

### 27.4 Media

#### 18 · `POST /media/presign-upload` — Xin URL upload đã ký

- **Quyền:** `tenant`, `landlord`, `admin`
- **Body:** `{ "ownerType":"room", "ownerId":"<uuid>", "purpose":"cover_photo", "fileName":"p201.jpg", "contentType":"image/jpeg", "size":248120 }`
- **Success:** `201` `{ "statusCode":201, "code":"MEDIA_UPLOAD_TICKET_ISSUED", "data":{"id":"<uuid>","ownerType":"room","ownerId":"<uuid>","purpose":"cover_photo","uploadUrl":"<signed-url>","requiredHeaders":{"Content-Type":"image/jpeg"},"expiresIn":900} }`; `Location: /api/v1/media/{mediaId}`
- **Lỗi:** `422 MEDIA TYPE NOT ALLOWED` · `422 INVALID PURPOSE` · `403 FORBIDDEN`
- **UI:** `11._t_i_gi_y_t_s_h_u_b_c_2_3_upload_documents_step_2_3/code.html` · `22._t_i_l_n_h_p_ng_k_upload_signed_lease/code.html` · `30._b_o_c_o_s_c_m_i_report_an_issue/code.html` · `30._ch_p_nh_c_ng_t_qua_webcam_webcam_meter_photo/code.html`

> Bước 1/2. Backend không nhận tệp. Client phải `PUT` tệp thẳng lên `uploadUrl` với đúng `requiredHeaders`, rồi gọi API 19.

#### 19 · `POST /media/{mediaId}/complete-upload` — Chốt upload

- **Quyền:** `tenant`, `landlord`, `admin`
- **Body:** không có
- **Success:** `200` `{ "statusCode":200, "code":"MEDIA_READY", "data":{"id":"<uuid>","ownerType":"room","ownerId":"<uuid>","purpose":"cover_photo","fileType":"image","url":"<signed-url>"} }`
- **Lỗi:** `404 NOT FOUND` · `403 FORBIDDEN` · `409 UPLOAD NOT COMPLETED` · `410 TICKET EXPIRED`
- **UI:** `11._t_i_gi_y_t_s_h_u_b_c_2_3_upload_documents_step_2_3/code.html` · `22._t_i_l_n_h_p_ng_k_upload_signed_lease/code.html` · `30._b_o_c_o_s_c_m_i_report_an_issue/code.html` · `30._ch_p_nh_c_ng_t_qua_webcam_webcam_meter_photo/code.html`

> Bước 2/2. Backend xác minh tệp đã nằm trên storage với kích thước và content type khớp vé đã cấp, rồi mới cho phép đọc qua API 20.

#### 20 · `GET /media/{mediaId}` — Đọc hoặc stream một tệp

- **Quyền:** *(để trống — kế thừa từ tài nguyên cha)*
- **Success:** `200` luồng tệp hoặc chuyển hướng đã ký; có `Content-Type` và `Content-Disposition`
- **Lỗi:** `404 NOT FOUND` · `403 FORBIDDEN` · `410 MEDIA DELETED`
- **UI:** `23._xem_h_p_ng_thu_view_lease/code.html` · `29._chi_ti_t_s_c_issue_detail_popup/code.html`

> Không so sánh vai trò. Server nạp `ownerType`/`ownerId` rồi áp quyền của tài nguyên cha. Chỉ cho `public` khi media thuộc building/room đã duyệt.

#### 21 · `DELETE /media/{mediaId}` — Xóa mềm tệp

- **Quyền:** `tenant`, `landlord`, `admin`
- **Success:** `204`
- **Lỗi:** `403 FORBIDDEN` · `409 CAN'T DELETE`
- **UI:** `16._th_m_ph_ng_m_i_add_new_room/code.html` · `30._b_o_c_o_s_c_m_i_report_an_issue/code.html`

### 27.5 Building

#### 22 · `GET /buildings` — Tìm tòa nhà trên sàn công khai

- **Quyền:** `public`
- **Query:** `filter[province]=Thành phố Hồ Chí Minh` · `filter[ward]=Phường Bến Nghé` · `sort=createdAt` · `order=desc`
- **Success:** `200` `{ "statusCode":200, "code":"BUILDINGS_FETCHED", "data":[{"id":"<uuid>","name":"Nhà trọ Thanh Xuân","province":"Thành phố Hồ Chí Minh","ward":"Phường Bến Nghé","address":"12 Nguyễn Trãi"}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`
- **Lỗi:** `422 VALIDATION FAILED` · `429 RATE LIMIT EXCEEDED`
- **UI:** `9._danh_s_ch_t_a_nh_building_list/code.html`

> > Route stateless, không cần token. Danh sách tòa nhà của chủ nhà và hàng đợi duyệt của admin nằm ở `GET /me/buildings` và `GET /admin/buildings`, không phải ở đây.

#### 23 · `GET /me/buildings` — Liệt kê tòa nhà của tôi

- **Quyền:** `landlord`
- **Query:** `filter[status]=approved` · `sort=createdAt` · `order=desc`
- **Success:** `200` `{ "statusCode":200, "code":"MY_BUILDINGS_FETCHED", "data":[{"id":"<uuid>","name":"Tòa nhà Rentify Central Park","status":"approved","totalRooms":12,"occupancyRate":"75.0"}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`
- **Lỗi:** `403 FORBIDDEN` · `422 VALIDATION FAILED`
- **UI:** `8b._b_ng_i_u_khi_n_v_n_h_nh_y_dashboard_full_state/code.html`

> > `/me` ở đây nghĩa là **tài nguyên do tôi sở hữu**, khác với `/me` kiểu tự dịch vụ ở API 7–9. Xem D48.

#### 24 · `GET /admin/buildings` — Hàng đợi duyệt và quản lý toàn bộ tòa nhà

- **Quyền:** `admin`
- **Query:** `filter[status]=pending` · `filter[q]=central` · `sort=createdAt` · `order=asc`
- **Success:** `200` `{ "statusCode":200, "code":"ADMIN_BUILDINGS_FETCHED", "data":[{"id":"<uuid>","name":"Tòa nhà Rentify Central Park","landlordId":"<uuid>","status":"pending","createdAt":"2026-09-20T08:00:00.000Z"}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`
- **Lỗi:** `403 FORBIDDEN` · `422 VALIDATION FAILED`
- **UI:** `10._h_ng_i_ph_duy_t_b_t_ng_s_n_property_approval_queue/code.html`

> > Route đầu tiên dùng namespace `/admin`. Xem D48.

#### 25 · `POST /buildings` — Gửi tòa nhà để duyệt

- **Quyền:** `landlord`
- **Body:** `{ "name":"Nhà trọ Thanh Xuân", "province":"Thành phố Hồ Chí Minh", "ward":"Phường Bến Nghé", "address":"12 Nguyễn Trãi" }`
- **Success:** `201` `{ "statusCode":201, "code":"BUILDING_CREATED", "data":{"id":"<uuid>","status":"pending","latitude":"20.995100","longitude":"105.816649"} }`; `Location: /api/v1/buildings/{buildingId}`
- **Lỗi:** `422 VALIDATION FAILED` · `403 FORBIDDEN`
- **UI:** `10._th_m_t_a_nh_b_c_1_3_add_building_step_1_3/code.html` · `11._t_i_gi_y_t_s_h_u_b_c_2_3_upload_documents_step_2_3/code.html`

#### 26 · `GET /buildings/{buildingId}` — Đọc tòa nhà (chế độ công khai)

- **Quyền:** `public`
- **Success:** `200` `{ "statusCode":200, "code":"BUILDING_FETCHED", "data":{"id":"<uuid>","name":"Nhà trọ Thanh Xuân","province":"Thành phố Hồ Chí Minh","ward":"Phường Bến Nghé","address":"12 Nguyễn Trãi","status":"approved"} }`
- **Lỗi:** `404 NOT FOUND`
- **UI:** `13._chi_ti_t_t_a_nh_building_detail/code.html`

> > Không có quyền `tenant`. Tenant tiếp cận tòa nhà qua hợp đồng và phòng, không đọc tài nguyên tòa nhà trực tiếp.

#### 27 · `GET /me/buildings/{buildingId}` — Đọc tòa nhà của tôi (chế độ quản trị)

- **Quyền:** `landlord`
- **Success:** `200` `{ "statusCode":200, "code":"MY_BUILDING_FETCHED", "data":{"id":"<uuid>","name":"Tòa nhà Rentify Central Park","status":"pending","totalRooms":12,"occupancyRate":"75.0","reviewNote":null} }`
- **Lỗi:** `404 NOT FOUND` · `403 FORBIDDEN`
- **UI:** `13._chi_ti_t_t_a_nh_building_detail/code.html`

> > `404` chứ không phải `403` khi tòa nhà không thuộc sở hữu của người gọi, để không suy tận id tồn tại.

#### 28 · `PATCH /buildings/{buildingId}` — Cập nhật thông tin tòa nhà

- **Quyền:** `landlord`
- **Body:** `{ "name":"Tòa nhà Rentify Central Park", "address":"123 Nguyễn Thị Minh Khai" }`
- **Success:** `200` `{ "statusCode":200, "code":"BUILDING_UPDATED", "data":{"id":"<uuid>","name":"Tòa nhà Rentify Central Park","address":"123 Nguyễn Thị Minh Khai","status":"approved"} }`
- **Lỗi:** `404 NOT FOUND` · `403 FORBIDDEN` · `409 APPROVED BUILDING LOCKED` · `422 VALIDATION FAILED`
- **UI:** `13._chi_ti_t_t_a_nh_building_detail/code.html`

> > Landlord không gửi được `status` hay trường review. Duyệt và từ chối là action riêng: `POST /buildings/{buildingId}/approve` và `POST /buildings/{buildingId}/reject`.

#### 29 · `POST /buildings/{buildingId}/approve` — Duyệt tòa nhà

- **Quyền:** `admin`
- **Body:** `{ "note":"Ownership proof verified" }`
- **Success:** `200` `{ "statusCode":200, "code":"BUILDING_APPROVED", "data":{"id":"<uuid>","status":"approved","reviewedAt":"2026-09-23T12:00:00.000Z"} }`
- **Lỗi:** `404 NOT FOUND` · `409 BUILDING NOT PENDING`
- **UI:** `11._chi_ti_t_ph_duy_t_b_t_ng_s_n_property_approval_detail/code.html`

> > Tòa nhà đã `approved` trả `409`, không phải `200` idempotent, để phát hiện việc duyệt trùng.

#### 30 · `POST /buildings/{buildingId}/reject` — Từ chối tòa nhà

- **Quyền:** `admin`
- **Body:** `{ "note":"Ownership proof is unreadable" }`
- **Success:** `200` `{ "statusCode":200, "code":"BUILDING_REJECTED", "data":{"id":"<uuid>","status":"rejected","reviewNote":"Ownership proof is unreadable","reviewedAt":"2026-09-23T12:00:00.000Z"} }`
- **Lỗi:** `404 NOT FOUND` · `409 BUILDING NOT PENDING` · `422 NOTE REQUIRED`
- **UI:** `12._t_ch_i_ph_duy_t_reject_property/code.html`

> > `note` bắt buộc để chủ nhà biết cần bổ sung giấy tờ gì.

#### 31 · `DELETE /buildings/{buildingId}` — Xóa mềm tòa nhà

- **Quyền:** `landlord`
- **Success:** `204`
- **Lỗi:** `404 NOT FOUND` · `409 BUILDING HAS ACTIVE CONTRACT`
- **UI:** `13._chi_ti_t_t_a_nh_building_detail/code.html`

> Xóa mềm theo mục 28.4: cascade sang phòng, chính sách giá và cài đặt hóa đơn; giữ nguyên hợp đồng, hóa đơn, thanh toán và audit log. Không có cấu hình QR cấp tòa nhà (D39).

#### 108 · `GET /admin/buildings/{buildingId}` — Chi tiết tòa nhà trong hàng đợi duyệt

- **Quyền:** `admin`
- **Success:** `200` `{ "statusCode":200, "code":"ADMIN_BUILDING_FETCHED", "data":{"id":"<uuid>","name":"Tòa nhà Rentify Central Park","address":"123 Nguyễn Thị Minh Khai","landlordId":"<uuid>","status":"pending","totalRooms":12,"occupancyRate":"75.0","reviewNote":null,"createdAt":"2026-09-20T08:00:00.000Z"} }`
- **Lỗi:** `404 NOT FOUND` · `403 FORBIDDEN`
- **UI:** `10._h_ng_i_ph_duy_t_b_t_ng_s_n_property_approval_queue/code.html`

> > Trả về mọi trạng thái, kể cả `pending` và `rejected`. `GET /buildings/{buildingId}` (mã 26) cố ý trả `404` cho hai trạng thái đó, nên trước D50 admin không đọc được tòa nhà đang chờ và chỉ duyệt được mù. Không có quyền `landlord`, `tenant`.

### 27.6 Room

#### 33 · `GET /rooms` — Tìm phòng trên sàn công khai

- **Quyền:** `public`
- **Query:** `filter[minPrice]=2000000` · `filter[maxPrice]=5000000` · `sort=rentPrice` · `order=asc`
- **Success:** `200` `{ "statusCode":200, "code":"ROOMS_FETCHED", "data":[{"id":"<uuid>","buildingId":"<uuid>","name":"P.201","area":"18.5","rentPrice":3500000,"genderPolicy":"any"}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`
- **Lỗi:** `422 VALIDATION FAILED` · `429 RATE LIMIT EXCEEDED`
- **UI:** `8._trang_ch_danh_s_ch_ph_ng_home_room_list/code.html` · `15._s_danh_s_ch_ph_ng_room_list_room_map/code.html`

> > Route stateless, không cần token. Không trả `status` vì mọi phòng trả về đều đang `available`.

#### 34 · `GET /me/rooms` — Liệt kê phòng của tôi

- **Quyền:** `landlord`
- **Query:** `filter[buildingId]=<uuid>` · `filter[status]=available` · `sort=rentPrice` · `order=asc`
- **Success:** `200` `{ "statusCode":200, "code":"MY_ROOMS_FETCHED", "data":[{"id":"<uuid>","buildingId":"<uuid>","name":"P.201","rentPrice":3500000,"status":"cleaning"}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`
- **Lỗi:** `403 FORBIDDEN` · `422 VALIDATION FAILED`
- **UI:** `17._chi_ti_t_ph_ng_room_detail_1/code.html`

> > Đây là màn hình quản lý phòng của chủ nhà, khác hoàn toàn với sàn tìm kiếm công khai.

#### 35 · `POST /rooms` — Tạo phòng trong một tòa nhà

- **Quyền:** `landlord`
- **Body:** `{ "buildingId":"<uuid>", "name":"P.201", "floorNumber":2, "area":"18.5", "amenities":{"aircon":true}, "maxOccupancy":3, "genderPolicy":"any", "rentPrice":3500000 }`
- **Success:** `201` `{ "statusCode":201, "code":"ROOM_CREATED", "data":{"id":"<uuid>","buildingId":"<uuid>","name":"P.201","status":"available","rentPrice":3500000} }`; `Location: /api/v1/rooms/{roomId}`
- **Lỗi:** `403 FORBIDDEN` · `409 DUPLICATE ROOM` · `422 BUILDING NOT APPROVED`
- **UI:** `16._th_m_ph_ng_m_i_add_new_room/code.html`

#### 36 · `GET /rooms/{roomId}` — Đọc một phòng

- **Quyền:** `public`, `landlord`, `tenant`, `admin`
- **Success:** `200` `{ "statusCode":200, "code":"ROOM_FETCHED", "data":{"id":"<uuid>","buildingId":"<uuid>","name":"P.201","description":"Phòng trọ hiện đại","area":"18.5","rentPrice":3500000,"status":"available","effectiveRatePolicySummary":{"electricity":"flat","water":"flat"}} }`
- **Lỗi:** `404 NOT FOUND` · `403 FORBIDDEN`
- **UI:** `11._chi_ti_t_ph_ng_room_detail/code.html` · `17._chi_ti_t_ph_ng_room_detail_1/code.html` · `22._trung_t_m_ph_ng_c_a_t_i_my_room_hub/code.html`

#### 37 · `PATCH /rooms/{roomId}` — Cập nhật thông tin phòng

- **Quyền:** `landlord`
- **Body:** `{ "name":"P.201", "rentPrice":3600000, "area":"19.0" }`
- **Success:** `200` `{ "statusCode":200, "code":"ROOM_UPDATED", "data":{"id":"<uuid>","name":"P.201","rentPrice":3600000,"area":"19.0"} }`
- **Lỗi:** `404 NOT FOUND` · `403 FORBIDDEN` · `422 VALIDATION FAILED`
- **UI:** `17._chi_ti_t_ph_ng_room_detail_1/code.html`

> > `status` không nằm trong body của endpoint này; chuyển trạng thái phòng là action riêng: `POST /rooms/{roomId}/mark-ready`.

#### 38 · `POST /rooms/{roomId}/mark-ready` — Đánh dấu phòng sẵn sàng cho thuê

- **Quyền:** `landlord`
- **Body:** không có
- **Success:** `200` `{ "statusCode":200, "code":"ROOM_MARKED_READY", "data":{"id":"<uuid>","status":"available"} }`
- **Lỗi:** `404 NOT FOUND` · `403 FORBIDDEN` · `409 INVALID ROOM TRANSITION`
- **UI:** `47._tr_ng_th_i_ch_d_n_v_sinh_nghi_m_thu_pending_cleanup_status/code.html`

> > Chỉ `cleaning` → `available` là hợp lệ. Phòng `occupied` trả `409 INVALID ROOM TRANSITION`.

#### 109 · `DELETE /rooms/{roomId}` — Xóa mềm phòng

- **Quyền:** `landlord`
- **Success:** `204`
- **Lỗi:** `404 NOT FOUND` · `409 ROOM HAS ACTIVE CONTRACT` · `403 FORBIDDEN`
- **UI:** `17._chi_ti_t_ph_ng_room_detail_1/code.html`

> Xóa mềm theo mục 28.4: đặt `is_deleted = true`. Hợp đồng, hóa đơn, thanh toán, chỉ số đồng hồ và kiểm toán được giữ nguyên. Phòng đang có hợp đồng hiệu lực trả `409 ROOM HAS ACTIVE CONTRACT`. Trước D50 chủ nhà chỉ gỡ được cả tòa nhà chứ không gỡ được một phòng đăng nhầm. Xem D50.

### 27.7 FavoriteRoom

#### 39 · `GET /me/favorite-rooms` — Liệt kê phòng đã lưu

- **Quyền:** `tenant`
- **Query:** `pageNo=1` · `pageSize=20`
- **Success:** `200` `{ "statusCode":200, "code":"FAVORITE_ROOMS_FETCHED", "data":[{"roomId":"<uuid>","name":"P.201","rentPrice":3500000}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`
- **Lỗi:** `401 INVALID TOKEN`
- **UI:** `10._ph_ng_l_u_saved_rooms/code.html` · `12._ph_ng_l_u_saved_rooms/code.html`

#### 40 · `POST /me/favorite-rooms` — Lưu một phòng

- **Quyền:** `tenant`
- **Body:** `{ "roomId":"<uuid>" }`
- **Success:** `201` `{ "statusCode":201, "code":"ROOM_FAVORITED", "data":{"roomId":"<uuid>","roomName":"P.201"} }`; `Location: /api/v1/me/favorite-rooms/{roomId}`
- **Lỗi:** `404 NOT FOUND` · `409 ALREADY FAVORITED`
- **UI:** `8._trang_ch_danh_s_ch_ph_ng_home_room_list/code.html` · `11._chi_ti_t_ph_ng_room_detail/code.html`

#### 41 · `DELETE /me/favorite-rooms/{roomId}` — Bỏ lưu một phòng

- **Quyền:** `tenant`
- **Success:** `204`
- **Lỗi:** `404 NOT FOUND`
- **UI:** `10._ph_ng_l_u_saved_rooms/code.html` · `12._ph_ng_l_u_saved_rooms/code.html`

### 27.8 RoommateProfile

#### 42 · `GET /roommate-profiles` — Duyệt feed hồ sơ tìm bạn ở

- **Quyền:** `tenant`
- **Query:** `filter[preferredArea]=Hòa Khánh` · `pageNo=1` · `pageSize=20`
- **Success:** `200` `{ "statusCode":200, "code":"ROOMMATE_PROFILES_FETCHED", "data":[{"tenantId":"<uuid>","bio":"Hiền lành, sạch sẽ","budgetMin":2000000,"budgetMax":3500000,"isVisible":true}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`
- **Lỗi:** `422 VALIDATION FAILED`
- **UI:** `11._gh_p_b_n_c_ng_ph_ng_match_feed/code.html`

#### 43 · `GET /roommate-profiles/{roommateProfileId}` — Đọc một hồ sơ theo định danh

- **Quyền:** `tenant`
- **Success:** `200` `{ "statusCode":200, "code":"ROOMMATE_PROFILE_FETCHED", "data":{"tenantId":"<uuid>","bio":"Hiền lành, sạch sẽ","budgetMin":2000000,"budgetMax":3500000,"preferredArea":"Hòa Khánh, Liên Chiểu","isVisible":true} }`
- **Lỗi:** `404 NOT FOUND` · `403 PROFILE NOT VISIBLE`
- **UI:** `12._chi_ti_t_h_s_b_n_c_ng_ph_ng_profile_detail/code.html` · `13._t_o_ch_nh_s_a_h_s_gh_p_ph_ng_create_edit_profile/code.html`

> Đây là route xem hồ sơ **người khác**. Xem hồ sơ của chính mình dùng API 44.

#### 44 · `GET /me/roommate-profile` — Đọc profile của chính mình

- **Quyền:** `tenant`
- **Success:** `200` `{ "statusCode":200, "code":"ROOMMATE_PROFILE_FETCHED", "data":{"tenantId":"<uuid>","lifestyle":{"sleep":"23h-6h"},"personality":{"introvert":true},"isVisible":true} }`
- **Lỗi:** `404 NOT FOUND`
- **UI:** `12._chi_ti_t_h_s_b_n_c_ng_ph_ng_profile_detail/code.html` · `13._t_o_ch_nh_s_a_h_s_gh_p_ph_ng_create_edit_profile/code.html`

> Trả cả hồ sơ `isVisible=false` vì đây là hồ sơ của chính người gọi.

#### 45 · `PUT /me/roommate-profile` — Tạo hoặc cập nhật profile của chính mình

- **Quyền:** `tenant`
- **Body:** `{ "bio":"Hiền lành, sạch sẽ", "lifestyle":{"sleep":"23h-6h"}, "personality":{"introvert":true}, "budgetMin":2000000, "budgetMax":3500000, "preferredArea":"Hòa Khánh, Liên Chiểu", "moveInOn":"2026-10-01", "isVisible":true }`
- **Success:** `200` `{ "statusCode":200, "code":"ROOMMATE_PROFILE_SAVED", "data":{"tenantId":"<uuid>","isVisible":true} }`
- **Lỗi:** `422 BUDGET RANGE INVALID` · `422 VALIDATION FAILED`
- **UI:** `13._t_o_ch_nh_s_a_h_s_gh_p_ph_ng_create_edit_profile/code.html`

### 27.9 MatchRequest

#### 46 · `GET /match-requests` — Liệt kê yêu cầu đến hoặc đi

- **Quyền:** `tenant`
- **Query:** `filter[direction]=incoming` · `filter[status]=pending`
- **Success:** `200` `{ "statusCode":200, "code":"MATCH_REQUESTS_FETCHED", "data":[{"id":"<uuid>","requesterId":"<uuid>","targetId":"<uuid>","status":"pending","createdAt":"2026-09-23T10:00:00.000Z"}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`
- **Lỗi:** `422 VALIDATION FAILED`
- **UI:** `14._danh_s_ch_y_u_c_u_gh_p_ph_ng_requests/code.html`

#### 47 · `POST /match-requests` — Gửi yêu cầu tìm bạn ở

- **Quyền:** `tenant`
- **Body:** `{ "targetId":"<uuid>" }`
- **Success:** `201` `{ "statusCode":201, "code":"MATCH_REQUEST_CREATED", "data":{"id":"<uuid>","status":"pending","respondedAt":null} }`; `Location: /api/v1/match-requests`
- **Lỗi:** `409 DUPLICATE MATCH REQUEST` · `422 SELF MATCHING NOT ALLOWED` · `404 NOT FOUND`
- **UI:** `11._gh_p_b_n_c_ng_ph_ng_match_feed/code.html` · `12._chi_ti_t_h_s_b_n_c_ng_ph_ng_profile_detail/code.html`

#### 48 · `POST /match-requests/{matchRequestId}/accept-request` — Chấp nhận yêu cầu

- **Quyền:** `tenant`
- **Body:** không có
- **Success:** `200` `{ "statusCode":200, "code":"MATCH_REQUEST_ACCEPTED", "data":{"id":"<uuid>","status":"accepted","conversationId":"<uuid>"} }`
- **Lỗi:** `403 FORBIDDEN` · `409 MATCH REQUEST NOT PENDING` · `404 NOT FOUND`
- **UI:** `14._danh_s_ch_y_u_c_u_gh_p_ph_ng_requests/code.html` · `15._gh_p_i_th_nh_c_ng_match_success/code.html`

#### 49 · `POST /match-requests/{matchRequestId}/reject-request` — Từ chối yêu cầu

- **Quyền:** `tenant`
- **Body:** không có
- **Success:** `200` `{ "statusCode":200, "code":"MATCH_REQUEST_REJECTED", "data":{"id":"<uuid>","status":"rejected"} }`
- **Lỗi:** `403 FORBIDDEN` · `409 MATCH REQUEST NOT PENDING`
- **UI:** `14._danh_s_ch_y_u_c_u_gh_p_ph_ng_requests/code.html`

> Bên nhận không rút được yêu cầu; chỉ `requester` mới dùng được `POST /match-requests/{matchRequestId}/withdraw-request` (mã 110). Xem mục 28.9.

#### 110 · `POST /match-requests/{matchRequestId}/withdraw-request` — Người gửi rút yêu cầu

- **Quyền:** `tenant`
- **Body:** không có
- **Success:** `200` `{ "statusCode":200, "code":"MATCH_REQUEST_WITHDRAWN", "data":{"id":"<uuid>","status":"withdrawn","respondedAt":"2026-09-27T03:10:00.000Z"} }`
- **Lỗi:** `403 FORBIDDEN` · `404 NOT FOUND` · `409 NOT REQUESTER` · `409 MATCH REQUEST NOT PENDING`
- **UI:** `14._danh_s_ch_y_u_c_u_gh_p_ph_ng_requests/code.html`

> > Chỉ `requester` mới rút được, bên nhận gặp `409 NOT REQUESTER` và phải dùng `reject-request`. Chỉ yêu cầu `pending` mới rút được. Rút là chuyển trạng thái, bản ghi được giữ. Vì UNIQUE `(requester_id, target_id)`, một cặp đã rút không gửi lại được nếu không đổi index — xem D50.

### 27.10 RatePolicy

#### 50 · `GET /rate-policies` — Liệt kê chính sách đơn giá và phí định kỳ

- **Quyền:** `landlord`
- **Query:** `filter[scope]=room` · `filter[roomId]=<uuid>` · `filter[type]=electricity`
- **Success:** `200` `{ "statusCode":200, "code":"RATE_POLICIES_FETCHED", "data":[{"id":"<uuid>","landlordId":"<uuid>","scope":"room","roomId":"<uuid>","type":"electricity","rateKind":"tiered","isActive":true}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`
- **Lỗi:** `422 VALIDATION FAILED` · `403 FORBIDDEN`
- **UI:** `12._ch_n_lo_i_n_gi_d_ch_v_b_c_3_3_choose_utility_rate_type/code.html` · `18._b_ng_ti_n_ch_v_n_h_nh_ph_ng_room_utility_menu_1/code.html`

#### 51 · `POST /rate-policies` — Tạo một chính sách đơn giá hoặc phí

- **Quyền:** `landlord`
- **Body:** `{ "scope":"room", "roomId":"<uuid>", "name":"Điện EVN", "type":"electricity", "rateKind":"tiered", "steps":[{"from":0,"to":50,"price":1806}] }`
- **Success:** `201` `{ "statusCode":201, "code":"RATE_POLICY_CREATED", "data":{"id":"<uuid>","scope":"room","type":"electricity","rateKind":"tiered","isActive":true} }`; `Location: /api/v1/rate-policies`
- **Lỗi:** `409 ACTIVE POLICY EXISTS` · `422 INVALID RATE KIND` · `403 FORBIDDEN`
- **UI:** `12a._c_u_h_nh_n_gi_c_nh_configure_fixed_rate/code.html` · `12b._c_u_h_nh_bi_u_l_y_ti_n_evn_configure_evn_tiered_rate/code.html` · `12c._c_u_h_nh_kho_n_tr_n_g_i_theo_u_ng_i_configure_per_person_flat_rate/code.html`

#### 52 · `PATCH /rate-policies/{ratePolicyId}` — Đổi tên chính sách

- **Quyền:** `landlord`
- **Body:** `{ "name":"Điện EVN 2026" }`
- **Success:** `200` `{ "statusCode":200, "code":"RATE_POLICY_UPDATED", "data":{"id":"<uuid>","name":"Điện EVN 2026"} }`
- **Lỗi:** `403 FORBIDDEN` · `409 RATE POLICY LOCKED` · `422 VALIDATION FAILED`
- **UI:** `18._b_ng_ti_n_ch_v_n_h_nh_ph_ng_room_utility_menu_1/code.html`

#### 53 · `POST /rate-policies/{ratePolicyId}/deactivate-policy` — Vô hiệu hoá chính sách

- **Quyền:** `landlord`
- **Body:** không có
- **Success:** `200` `{ "statusCode":200, "code":"RATE_POLICY_DEACTIVATED", "data":{"id":"<uuid>","isActive":false} }`
- **Lỗi:** `403 FORBIDDEN` · `409 POLICY NOT ACTIVE`
- **UI:** `18._b_ng_ti_n_ch_v_n_h_nh_ph_ng_room_utility_menu_1/code.html`

### 27.11 BillingSetting

#### 54 · `GET /billing-settings` — Liệt kê cài đặt thanh toán và nhắc hóa đơn

- **Quyền:** `landlord`
- **Query:** `filter[scope]=room` · `filter[roomId]=<uuid>`
- **Success:** `200` `{ "statusCode":200, "code":"BILLING_SETTINGS_FETCHED", "data":[{"id":"<uuid>","scope":"room","roomId":"<uuid>","dueDays":5,"remindDays":3,"botEnabled":true,"isActive":true}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`
- **Lỗi:** `403 FORBIDDEN` · `422 VALIDATION FAILED`
- **UI:** `37._c_i_t_chu_k_thanh_to_n_qu_t_n_billing_cycle_debt_scan_settings/code.html` · `38._thi_t_l_p_ng_y_ch_t_h_n_thanh_to_n_due_date_settings/code.html`

#### 55 · `POST /billing-settings` — Tạo một cài đặt hóa đơn

- **Quyền:** `landlord`
- **Body:** `{ "scope":"room", "roomId":"<uuid>", "dueDays":5, "remindDays":3, "botEnabled":true }`
- **Success:** `201` `{ "statusCode":201, "code":"BILLING_SETTING_CREATED", "data":{"id":"<uuid>","dueDays":5,"remindDays":3,"botEnabled":true} }`; `Location: /api/v1/billing-settings`
- **Lỗi:** `409 ACTIVE SETTING EXISTS` · `422 DUE DAYS INVALID` · `403 FORBIDDEN`
- **UI:** `37._c_i_t_chu_k_thanh_to_n_qu_t_n_billing_cycle_debt_scan_settings/code.html`

#### 56 · `PATCH /billing-settings/{billingSettingId}` — Cập nhật cài đặt hóa đơn

- **Quyền:** `landlord`
- **Body:** `{ "dueDays":7, "remindDays":3, "botEnabled":false }`
- **Success:** `200` `{ "statusCode":200, "code":"BILLING_SETTING_UPDATED", "data":{"id":"<uuid>","dueDays":7,"remindDays":3,"botEnabled":false} }`
- **Lỗi:** `403 FORBIDDEN` · `422 DUE DAYS INVALID`
- **UI:** `38._thi_t_l_p_ng_y_ch_t_h_n_thanh_to_n_due_date_settings/code.html`

### 27.12 ContractTemplate

#### 57 · `GET /contract-templates` — Liệt kê mẫu khả dụng

- **Quyền:** `landlord`
- **Query:** `pageNo` · `pageSize` — offset pagination, không có filter vì bộ mẫu là seed cố định
- **Success:** `200` `{ "statusCode":200, "code":"CONTRACT_TEMPLATES_FETCHED", "data":[{"templateKey":"standard_residential_v1","title":"Residential lease","version":"1.0"}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`
- **Lỗi:** `403 FORBIDDEN`
- **UI:** `20._ch_n_m_u_h_p_ng_choose_lease_template/code.html`

#### 58 · `GET /contract-templates/{templateKey}` — Đọc một mẫu

- **Quyền:** `landlord`
- **Success:** `200` `{ "statusCode":200, "code":"CONTRACT_TEMPLATE_FETCHED", "data":{"templateKey":"standard_residential_v1","title":"Residential lease","version":"1.0","requiredVariables":["landlordName","tenantName","rentPrice"]} }`
- **Lỗi:** `404 NOT FOUND`
- **UI:** `20._ch_n_m_u_h_p_ng_choose_lease_template/code.html`

### 27.13 Contract

#### 59 · `GET /me/contracts` — Hợp đồng của tôi

- **Quyền:** `tenant`
- **Query:** `filter[status]=active` · `pageNo=1` · `pageSize=20`
- **Success:** `200` `{ "statusCode":200, "code":"MY_CONTRACTS_FETCHED", "data":[{"id":"<uuid>","roomId":"<uuid>","status":"active","rentPrice":3500000,"depositAmount":7000000}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`
- **Lỗi:** `403 FORBIDDEN` · `422 VALIDATION FAILED`
- **UI:** `21._danh_s_ch_h_p_ng_thu_lease_list/code.html`

> > Không có quyền `admin`, `landlord`.

#### 60 · `GET /contracts` — Quản lý hợp đồng của tôi

- **Quyền:** `landlord`
- **Query:** `filter[roomId]=<uuid>` · `filter[status]=draft` · `pageNo=1` · `pageSize=20`
- **Success:** `200` `{ "statusCode":200, "code":"CONTRACTS_FETCHED", "data":[{"id":"<uuid>","roomId":"<uuid>","status":"draft","rentPrice":3500000,"depositAmount":7000000}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`
- **Lỗi:** `403 FORBIDDEN` · `422 VALIDATION FAILED`
- **UI:** `21._danh_s_ch_h_p_ng_thu_lease_list/code.html`

> > Không có quyền `admin`, `tenant`.

#### 61 · `POST /contracts` — Tạo hợp đồng nháp

- **Quyền:** `landlord`
- **Body:** `{ "roomId":"<uuid>", "tenantId":null, "tenantName":"Trần Văn B", "tenantPhone":"0912345678", "depositAmount":7000000, "rentPrice":3500000, "startDate":"2026-09-01", "endDate":"2027-08-31", "vehicleCount":1 }`
- **Success:** `201` `{ "statusCode":201, "code":"CONTRACT_CREATED", "data":{"id":"<uuid>","status":"draft","tenantId":null,"rentPrice":3500000} }`; `Location: /api/v1/contracts/{contractId}`
- **Lỗi:** `409 ACTIVE CONTRACT EXISTS` · `422 TENANT IDENTITY INVALID` · `403 FORBIDDEN`
- **UI:** `19._t_o_h_p_ng_m_i_create_lease/code.html`

#### 62 · `GET /contracts/{contractId}` — Đọc một hợp đồng

- **Quyền:** `landlord`, `tenant`
- **Success:** `200` `{ "statusCode":200, "code":"CONTRACT_FETCHED", "data":{"id":"<uuid>","roomId":"<uuid>","status":"active","tenantId":"<uuid>","tenantName":"Trần Văn B","tenantPhone":"0912345678","rentPrice":3500000,"depositAmount":7000000,"startDate":"2026-09-01","endDate":"2027-08-31","signedContractMediaId":"<uuid>"} }`
- **Lỗi:** `403 FORBIDDEN` · `404 NOT FOUND`
- **UI:** `23._xem_h_p_ng_thu_view_lease/code.html`

> Không có quyền `admin`. Chỉ hợp đồng liên kết với `tenantId` của người gọi hoặc có `ContractMember` đang hoạt động mới hiển thị.

#### 63 · `PATCH /contracts/{contractId}` — Sửa hợp đồng nháp

- **Quyền:** `landlord`
- **Body:** `{ "description":"Đóng tiền trước ngày 5 hàng tháng" }`
- **Success:** `200` `{ "statusCode":200, "code":"CONTRACT_UPDATED", "data":{"id":"<uuid>","status":"draft","description":"Đóng tiền trước ngày 5 hàng tháng"} }`
- **Lỗi:** `409 CONTRACT NOT DRAFT` · `403 FORBIDDEN` · `422 VALIDATION FAILED`
- **UI:** `19._t_o_h_p_ng_m_i_create_lease/code.html`

#### 64 · `PUT /contracts/{contractId}/apply-template` — Áp mẫu vào hợp đồng nháp

- **Quyền:** `landlord`
- **Body:** `{ "templateKey":"standard_residential_v1" }`
- **Success:** `200` `{ "statusCode":200, "code":"CONTRACT_TEMPLATE_APPLIED", "data":{"id":"<uuid>","templateKey":"standard_residential_v1","status":"draft"} }`
- **Lỗi:** `404 TEMPLATE NOT FOUND` · `409 CONTRACT NOT DRAFT` · `403 FORBIDDEN`
- **UI:** `20._ch_n_m_u_h_p_ng_choose_lease_template/code.html`

#### 65 · `POST /contracts/{contractId}/generate-draft-document` — Sinh tài liệu nháp

- **Quyền:** `landlord`
- **Body:** `{ "templateKey":"standard_residential_v1" }`
- **Success:** `201` `{ "statusCode":201, "code":"CONTRACT_DRAFT_GENERATED", "data":{"contractId":"<uuid>","mediaId":"<uuid>","purpose":"contract_template"} }`; `Location: /api/v1/media/{mediaId}`
- **Lỗi:** `403 FORBIDDEN` · `409 CONTRACT NOT DRAFT` · `422 TEMPLATE DATA INVALID`
- **UI:** `21._xu_t_file_pdf_export_lease_pdf/code.html`

#### 66 · `POST /contracts/{contractId}/activate-contract` — Kích hoạt hợp đồng đã ký

- **Quyền:** `landlord`
- **Body:** `{ "signedContractMediaId":"<uuid>" }`
- **Success:** `200` `{ "statusCode":200, "code":"CONTRACT_ACTIVATED", "data":{"id":"<uuid>","status":"active","activatedAt":"2026-09-23T11:10:00.000Z"} }`
- **Lỗi:** `409 CONTRACT NOT READY` · `409 SIGNED FILE MISSING` · `403 FORBIDDEN`
- **UI:** `22._t_i_l_n_h_p_ng_k_upload_signed_lease/code.html`

> Vì sao không dùng PATCH: kích hoạt là bước vòng đời có điều kiện, không phải chỉ sửa một field. Nó đòi tệp đã ký hợp lệ và chuyển trạng thái. Gộp vào PATCH sẽ làm mất ranh giới này.

#### 67 · `POST /contracts/{contractId}/complete-checkout` — Hoàn tất trả phòng

- **Quyền:** `landlord`
- **Body:** `{ "completedOn":"2026-09-30" }`
- **Success:** `200` `{ "statusCode":200, "code":"CONTRACT_CHECKOUT_COMPLETED", "data":{"id":"<uuid>","status":"expired","completedOn":"2026-09-30"} }`
- **Lỗi:** `409 CONTRACT NOT ACTIVE` · `403 FORBIDDEN` · `422 SETTLEMENT NOT READY`
- **UI:** `46._x_c_nh_n_ho_n_t_t_tr_ph_ng_confirm_move_out_complete/code.html`

> Vì sao không dùng PATCH: bước này phát sinh hóa đơn quyết toán, tức là có side effect ngoài bản ghi hợp đồng. Cấu trúc hóa đơn quyết toán đang pending, xem mục 28.2.

### 27.14 ContractMember

#### 68 · `POST /contract-members` — Thêm một thành viên vào hợp đồng

- **Quyền:** `landlord`
- **Body:** `{ "contractId":"<uuid>", "tenantId":"<uuid>", "tenantName":"Nguyễn Thị C", "tenantPhone":"0921234567", "joinedAt":"2026-09-01" }`
- **Success:** `201` `{ "statusCode":201, "code":"CONTRACT_MEMBER_ADDED", "data":{"id":"<uuid>","contractId":"<uuid>","tenantId":"<uuid>","joinedAt":"2026-09-01","leftAt":null} }`; `Location: /api/v1/contract-members/{contractMemberId}`
- **Lỗi:** `409 MEMBER ALREADY EXISTS` · `403 FORBIDDEN` · `422 TENANT IDENTITY INVALID`
- **UI:** `24._th_m_th_nh_vi_n_m_i_add_new_member/code.html`

#### 69 · `PATCH /contract-members/{contractMemberId}` — Cập nhật thành viên

- **Quyền:** `landlord`
- **Body:** `{ "tenantPhone":"0921234567" }`
- **Success:** `200` `{ "statusCode":200, "code":"CONTRACT_MEMBER_UPDATED", "data":{"id":"<uuid>","tenantPhone":"0921234567"} }`
- **Lỗi:** `403 FORBIDDEN` · `409 MEMBER LEFT` · `422 VALIDATION FAILED`
- **UI:** `23._danh_s_ch_th_nh_vi_n_member_list/code.html` · `24._danh_s_ch_th_nh_vi_n_member_list/code.html`

> Chỉ landlord được sửa. Path param là `contractMemberId`, khớp tên bảng `ContractMember`.

#### 70 · `POST /contract-members/{contractMemberId}/leave-contract` — Ghi nhận thành viên rời đi

- **Quyền:** `landlord`
- **Body:** `{ "leftOn":"2026-10-01" }`
- **Success:** `200` `{ "statusCode":200, "code":"CONTRACT_MEMBER_LEFT", "data":{"id":"<uuid>","leftAt":"2026-10-01"} }`
- **Lỗi:** `403 FORBIDDEN` · `409 MEMBER ALREADY LEFT` · `422 LEFT DATE INVALID`
- **UI:** `25._x_c_nh_n_x_a_th_nh_vi_n_confirm_remove_member/code.html`

> Vì sao không dùng DELETE: cần giữ `leftAt` và lịch sử thành viên để đối soát tiền cọc. DELETE sẽ xóa mất bằng chứng đó.

#### 71 · `GET /contract-members` — Liệt kê thành viên hoặc xuất dữ liệu

- **Quyền:** `landlord`, `tenant`
- **Query:** `filter[contractId]=<uuid>` **(bắt buộc)** · `format=csv`
- **Success:** `200` `{ "statusCode":200, "code":"CONTRACT_MEMBERS_FETCHED", "data":[{"id":"<uuid>","contractId":"<uuid>","tenantName":"Trần Văn B","joinedAt":"2026-09-01","leftAt":null}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`; `format` khác JSON trả luồng tệp không có wrapper
- **Lỗi:** `403 FORBIDDEN` · `422 CONTRACT ID REQUIRED` · `404 NOT FOUND`
- **UI:** `23._danh_s_ch_th_nh_vi_n_member_list/code.html` · `24._danh_s_ch_th_nh_vi_n_member_list/code.html`

> Tenant chỉ xem được thành viên của hợp đồng mình tham gia, nên `filter[contractId]` là bắt buộc chứ không phải tuỳ chọn.

### 27.15 MeterReading

#### 72 · `GET /meter-readings` — Liệt kê chỉ số đồng hồ

- **Quyền:** `landlord`
- **Query:** `filter[roomId]=<uuid>` · `filter[type]=electricity` · `filter[period]=2026-09`
- **Success:** `200` `{ "statusCode":200, "code":"METER_READINGS_FETCHED", "data":[{"id":"<uuid>","roomId":"<uuid>","type":"electricity","period":"2026-09","previousReading":"1200","currentReading":"1380","readingDate":"2026-09-30","isBaseline":false}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`
- **Lỗi:** `403 FORBIDDEN` · `422 VALIDATION FAILED`
- **UI:** `26._ghi_ch_s_ph_ng_l_single_meter_reading/code.html`

> Tenant không đọc được tập chỉ số thô. Tenant nhận số liệu đã tính qua hóa đơn.

#### 73 · `POST /meter-readings/preview-ocr-result` — Xem trước kết quả chuẩn hoá OCR

- **Quyền:** `landlord`
- **Body:** `{ "roomId":"<uuid>", "mediaId":"<uuid>", "type":"electricity" }`
- **Success:** `200` `{ "statusCode":200, "code":"OCR_RESULT_PREVIEWED", "data":{"type":"electricity","previousReading":"12680.5","currentReading":"12850.5","requiresConfirmation":true} }`
- **Lỗi:** `422 OCR RESULT INVALID` · `422 EVIDENCE REQUIRED` · `403 FORBIDDEN`
- **UI:** `30._ch_p_nh_c_ng_t_qua_webcam_webcam_meter_photo/code.html` · `31._k_t_qu_nh_n_di_n_s_c_ocr_ocr_result/code.html`

#### 74 · `POST /meter-readings` — Tạo một chỉ số đã xác nhận

- **Quyền:** `landlord`
- **Body:** `{ "roomId":"<uuid>", "type":"electricity", "period":"2026-09", "previousReading":"12680.5", "currentReading":"12850.5", "readingDate":"2026-09-30", "isBaseline":false, "evidenceMediaId":"<uuid>" }`
- **Success:** `201` `{ "statusCode":201, "code":"METER_READING_CREATED", "data":{"id":"<uuid>","roomId":"<uuid>","type":"electricity","period":"2026-09","currentReading":"12850.5"} }`; `Location: /api/v1/meter-readings`
- **Lỗi:** `409 DUPLICATE METER READING` · `422 CURRENT READING INVALID` · `422 EVIDENCE REQUIRED` · `403 FORBIDDEN`
- **UI:** `26._ghi_ch_s_ph_ng_l_single_meter_reading/code.html` · `31._k_t_qu_nh_n_di_n_s_c_ocr_ocr_result/code.html` · `43._ch_t_ch_s_tr_ph_ng_final_meter_reading/code.html`

### 27.16 Invoice

#### 75 · `GET /invoices/tenant` — Hóa đơn của tôi

- **Quyền:** `tenant`
- **Query:** `filter[status]=issued` · `pageNo=1` · `pageSize=20`
- **Success:** `200` `{ "statusCode":200, "code":"MY_INVOICES_FETCHED", "data":[{"id":"<uuid>","code":"INV-202609-8F2K","contractId":"<uuid>","period":"2026-09","totalAmount":4610000,"invoiceStatus":"issued","issuedAt":"2026-09-30T20:15:00.000Z"}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`
- **Lỗi:** `403 FORBIDDEN` · `422 VALIDATION FAILED`
- **UI:** `25._danh_s_ch_h_a_n_invoice_list/code.html`

> > Tenant tải PDF hóa đơn của mình qua chính route này với `?format=pdf`. Xem D45, D46.

#### 76 · `GET /invoices` — Theo dõi hóa đơn và công nợ

- **Quyền:** `landlord`
- **Query:** `filter[status]=issued` · `filter[buildingId]=<uuid>` · `format=json`
- **Success:** `200` `{ "statusCode":200, "code":"INVOICES_FETCHED", "data":[{"id":"<uuid>","code":"INV-202609-8F2K","contractId":"<uuid>","period":"2026-09","totalAmount":4610000,"invoiceStatus":"issued","issuedAt":"2026-09-30T20:15:00.000Z"}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`
- **Lỗi:** `403 FORBIDDEN` · `422 VALIDATION FAILED`
- **UI:** `33._danh_s_ch_h_a_n_ph_t_h_nh_issued_invoice_list/code.html` · `39._danh_s_ch_c_ng_n_qu_h_n_debt_list/code.html`

> > Không có quyền `admin`, `tenant`. Đây là route dùng để tải PDF hóa đơn, xem D45.

#### 77 · `POST /invoices` — Tạo hóa đơn quyết toán trả phòng

- **Quyền:** `landlord`
- **Body:** `{ "contractId":"<uuid>", "period":"2026-09", "otherFees":[{"name":"Phí vệ sinh","amount":50000},{"name":"Hư hỏng nội thất","amount":-150000}], "note":"Thanh ly hợp đồng, prorate theo ngày ở thực tế" }`
- **Success:** `201` `{ "statusCode":201, "code":"SETTLEMENT_INVOICE_CREATED", "data":{"id":"<uuid>","code":"INV-202609-8F2K","contractId":"<uuid>","period":"2026-09","rentAmount":1750000,"breakdown":[{"type":"electricity","name":"Điện EVN","qtyKwh":180,"amount":720000}],"otherFees":[{"name":"Phí vệ sinh","amount":50000},{"name":"Hư hỏng nội thất","amount":-150000}],"totalAmount":2370000,"invoiceStatus":"pending","issuedAt":null} }`; `Location: /api/v1/invoices/{invoiceId}`
- **Lỗi:** `409 ACTIVE SETTLEMENT INVOICE EXISTS` · `422 TOTAL NEGATIVE` · `422 BREAKDOWN MISMATCH` · `403 FORBIDDEN`
- **UI:** `32._xem_tr_c_h_a_n_invoice_preview/code.html` · `44._h_a_n_quy_t_to_n_ti_n_ph_ng_final_settlement_invoice/code.html` · `45._quy_t_to_n_ti_n_c_c_ho_n_tr_deposit_settlement/code.html`

#### 78 · `GET /invoices/{invoiceId}` — Đọc hóa đơn kèm tổng hợp thanh toán

- **Quyền:** `landlord`, `tenant`
- **Success:** `200` `{ "statusCode":200, "code":"INVOICE_FETCHED", "data":{"id":"<uuid>","code":"INV-202609-8F2K","period":"2026-09","rentAmount":3500000,"breakdown":[{"type":"electricity","name":"Điện EVN","amount":720000}],"otherFees":[],"totalAmount":4220000,"invoiceStatus":"pending","issuedAt":null,"paidAmount":0,"remainingAmount":4220000} }`
- **Lỗi:** `403 FORBIDDEN` · `404 NOT FOUND`
- **UI:** `26._chi_ti_t_h_a_n_invoice_detail/code.html`

> Không có quyền `admin`. Đây cũng là route tải tệp hóa đơn; endpoint `invoice-document` riêng đã bị bỏ.

#### 79 · `PATCH /invoices/{invoiceId}` — Sửa hóa đơn đang chờ

- **Quyền:** `landlord`
- **Body:** `{ "otherFees":[{"name":"Giảm trừ","amount":-100000}], "note":"Adjustment approved" }`
- **Success:** `200` `{ "statusCode":200, "code":"INVOICE_UPDATED", "data":{"id":"<uuid>","otherFees":[{"name":"Giảm trừ","amount":-100000}],"totalAmount":4120000} }`
- **Lỗi:** `409 INVOICE ALREADY ISSUED` · `422 TOTAL AMOUNT INVALID` · `403 FORBIDDEN`
- **UI:** `34._ch_nh_s_a_ho_c_h_y_h_a_n_edit_cancel_invoice/code.html`

#### 80 · `POST /invoices/issue-invoice` — Phát hành nhiều hóa đơn theo lô

- **Quyền:** `landlord`
- **Header:** `Idempotency-Key: <uuid>` (bắt buộc)
- **Body:** `{ "invoiceIds":["<uuid>","<uuid>"], "sendNotification":true }`
- **Success:** `200` `{ "statusCode":200, "code":"INVOICES_ISSUE_REQUESTED", "data":{"requested":2,"succeeded":[{"id":"<uuid>","invoiceStatus":"pending","issuedAt":"2026-09-30T20:15:00.000Z","vietQrContent":"INV-202609-8F2K"}],"failed":[{"invoiceId":"<uuid>","code":"INVOICE_NOT_PENDING"}]} }`
- **Lỗi:** `422 INVOICE IDS REQUIRED` · `422 INVOICE IDS TOO LARGE` · `409 IDEMPOTENCY KEY REUSED` · `403 FORBIDDEN`
- **UI:** `35._ph_t_h_nh_h_a_n_th_nh_c_ng_issue_invoice/code.html`

> **Bulk action có tên nghiệp vụ**, thay cho biến thể `/invoices/{invoiceId}/issue-invoice`. Kết quả tách `succeeded` và `failed` để một hóa đơn lỗi không chặn cả lô. Lỗi nghiệp vụ của từng hóa đơn nằm trong `failed`, không phải ở tầng HTTP.

#### 81 · `POST /invoices/{invoiceId}/cancel-invoice` — Huỷ một hóa đơn sai

- **Quyền:** `landlord`
- **Body:** `{ "reason":"Wrong meter reading" }`
- **Success:** `200` `{ "statusCode":200, "code":"INVOICE_CANCELLED", "data":{"id":"<uuid>","invoiceStatus":"void","cancelReason":"Wrong meter reading"} }`
- **Lỗi:** `409 INVOICE ALREADY PAID` · `409 CAN'T DELETE` · `403 FORBIDDEN`
- **UI:** `34._ch_nh_s_a_ho_c_h_y_h_a_n_edit_cancel_invoice/code.html`

> Vẫn là thao tác một hóa đơn vì mỗi lần huỷ đều cần lý do riêng để ghi audit.

#### 82 · `POST /invoices/send-reminder` — Nhắc ngày thu dự kiến theo lô

- **Quyền:** `landlord`
- **Header:** `Idempotency-Key: <uuid>` (bắt buộc)
- **Body:** `{ "invoiceIds":["<uuid>","<uuid>"], "channel":"push" }`
- **Success:** `202` `{ "statusCode":202, "code":"INVOICE_REMINDERS_QUEUED", "data":{"requested":2,"queued":[{"invoiceId":"<uuid>","sentCount":1}],"failed":[{"invoiceId":"<uuid>","code":"INVOICE_NOT_OVERDUE"}]} }`
- **Lỗi:** `422 INVOICE IDS REQUIRED` · `422 INVOICE IDS TOO LARGE` · `409 IDEMPOTENCY KEY REUSED` · `403 FORBIDDEN`
- **UI:** `39._danh_s_ch_c_ng_n_qu_h_n_debt_list/code.html`

> **Bulk action có tên nghiệp vụ**, thay cho biến thể `/invoices/{invoiceId}/send-reminder`.

### 27.17 Payment

#### 83 · `GET /me/payments` — Lịch sử thanh toán của tôi

- **Quyền:** `tenant`
- **Query:** `filter[paymentStatus]=success` · `pageNo=1` · `pageSize=20`
- **Success:** `200` `{ "statusCode":200, "code":"MY_PAYMENTS_FETCHED", "data":[{"id":"<uuid>","invoiceId":"<uuid>","method":"vietqr","paymentStatus":"success","amount":4220000,"transactionId":"VQR20260923112001"}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`
- **Lỗi:** `403 FORBIDDEN` · `422 VALIDATION FAILED`
- **UI:** `26._chi_ti_t_h_a_n_invoice_detail/code.html`

> > Không có quyền `admin`, `landlord`.

#### 84 · `GET /payments` — Đối soát dòng tiền

- **Quyền:** `landlord`
- **Query:** `filter[invoiceId]=<uuid>` · `filter[paymentStatus]=success`
- **Success:** `200` `{ "statusCode":200, "code":"PAYMENTS_FETCHED", "data":[{"id":"<uuid>","invoiceId":"<uuid>","method":"vietqr","paymentStatus":"success","amount":4220000,"transactionId":"VQR20260923112001"}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`
- **Lỗi:** `403 FORBIDDEN` · `422 VALIDATION FAILED`
- **UI:** `26._chi_ti_t_h_a_n_invoice_detail/code.html`

> > Không có quyền `admin`, `tenant`.

#### 85 · `POST /payments/create-intent` — Tạo ý định thanh toán

- **Quyền:** `tenant`
- **Header:** `Idempotency-Key: <uuid>` (bắt buộc)
- **Body:** `{ "invoiceId":"<uuid>", "method":"vietqr" }`
- **Success:** `201` `{ "statusCode":201, "code":"PAYMENT_INTENT_CREATED", "data":{"paymentId":"<uuid>","invoiceCode":"INV-202609-8F2K","method":"vietqr","amount":4220000,"qrContent":"000201010212..."} }`; `Location: /api/v1/payments`
- **Lỗi:** `409 IDEMPOTENCY KEY REUSED` · `409 INVOICE NOT PAYABLE` · `403 FORBIDDEN`
- **UI:** `27._thanh_to_n_payment/code.html`

#### 86 · `POST /payments/record-cash-payment` — Ghi nhận thanh toán tiền mặt

- **Quyền:** `landlord`
- **Header:** `Idempotency-Key: <uuid>` (bắt buộc)
- **Body:** `{ "invoiceId":"<uuid>", "amount":4220000, "transactionId":"CASH-20260923", "receiptMediaId":"<uuid>" }`
- **Success:** `201` `{ "statusCode":201, "code":"CASH_PAYMENT_RECORDED", "data":{"paymentId":"<uuid>","invoiceId":"<uuid>","paymentStatus":"success","amount":4220000,"invoiceStatus":"issued","paidAmount":4220000,"remainingAmount":0,"paymentState":"paid"} }`; `Location: /api/v1/payments`
- **Lỗi:** `409 IDEMPOTENCY KEY REUSED` · `409 INVOICE NOT PAYABLE` · `422 AMOUNT INVALID` · `403 FORBIDDEN`
- **UI:** `36._x_c_nh_n_thanh_to_n_ti_n_m_t_confirm_cash_payment/code.html`

#### 87 · `POST /payments/webhooks/{provider}` — Nhận callback đã ký từ provider

- **Quyền:** `system`
- **Body:** payload đã ký gồm `transactionId`, `orderId`, `amount`, `signature`
- **Success:** phản hồi xác nhận của provider (`200` hoặc `204`); không có JSON wrapper; gọi lặp bị loại theo event/transaction ID của provider
- **Lỗi:** `401 INVALID SIGNATURE` · `409 DUPLICATE WEBHOOK` · `422 WEBHOOK INVALID`
- **UI:** không có màn hình — webhook do cổng thanh toán gọi vào, không phải thao tác người dùng

### 27.18 IssueReport

#### 88 · `GET /me/issues` — Sự cố của tôi

- **Quyền:** `tenant`
- **Query:** `filter[status]=open` · `pageNo=1` · `pageSize=20`
- **Success:** `200` `{ "statusCode":200, "code":"MY_ISSUES_FETCHED", "data":[{"id":"<uuid>","roomId":"<uuid>","title":"Vòi xịt bồn cầu bị rò rỉ","status":"open","description":"Nước rò rỉ liên tục"}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`
- **Lỗi:** `403 FORBIDDEN` · `422 VALIDATION FAILED`
- **UI:** `28._danh_s_ch_s_c_room_issue_list/code.html`

> > Không có quyền `admin`, `landlord`.

#### 89 · `GET /issues` — Hàng đợi sự cố bảo trì

- **Quyền:** `landlord`
- **Query:** `filter[status]=open` · `filter[buildingId]=<uuid>` · `pageNo=1` · `pageSize=20`
- **Success:** `200` `{ "statusCode":200, "code":"ISSUES_FETCHED", "data":[{"id":"<uuid>","roomId":"<uuid>","title":"Vòi xịt bồn cầu bị rò rỉ","status":"open","description":"Nước rò rỉ liên tục"}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`
- **Lỗi:** `403 FORBIDDEN` · `422 VALIDATION FAILED`
- **UI:** `40._danh_s_ch_s_c_issues_tab/code.html`

> > Không có quyền `admin`, `tenant`. Sự cố là vận hành giữa chủ nhà và người thuê.

#### 90 · `POST /issues` — Báo cáo sự cố

- **Quyền:** `tenant`, `landlord`
- **Body:** `{ "roomId":"<uuid>", "title":"Vòi xịt bồn cầu bị rò rỉ", "description":"Nước rò rỉ liên tục", "issuePhotoMediaIds":["<uuid>"] }`
- **Success:** `201` `{ "statusCode":201, "code":"ISSUE_CREATED", "data":{"id":"<uuid>","status":"open","title":"Vòi xịt bồn cầu bị rò rỉ"} }`; `Location: /api/v1/issues/{issueId}`
- **Lỗi:** `403 FORBIDDEN` · `422 ISSUE PHOTO INVALID` · `404 ROOM NOT FOUND`
- **UI:** `30._b_o_c_o_s_c_m_i_report_an_issue/code.html` · `42._t_o_phi_u_y_u_c_u_s_c_m_i_landlord_creates_an_issue/code.html`

#### 91 · `GET /issues/{issueId}` — Đọc chi tiết sự cố

- **Quyền:** `landlord`, `tenant`
- **Success:** `200` `{ "statusCode":200, "code":"ISSUE_FETCHED", "data":{"id":"<uuid>","roomId":"<uuid>","reporterId":"<uuid>","title":"Vòi xịt bồn cầu bị rò rỉ","description":"Nước rò rỉ liên tục","status":"in_progress","note":null,"closedAt":null,"issuePhotoMediaIds":["<uuid>"]} }`
- **Lỗi:** `403 FORBIDDEN` · `404 NOT FOUND`
- **UI:** `29._chi_ti_t_s_c_issue_detail_popup/code.html` · `41._chi_ti_t_s_c_issue_detail_popup/code.html`

#### 92 · `PATCH /issues/{issueId}` — Cập nhật tiến trình sự cố

- **Quyền:** `landlord`
- **Body:** `{ "status":"resolved", "note":"Đã thay dây vòi" }`
- **Success:** `200` `{ "statusCode":200, "code":"ISSUE_UPDATED", "data":{"id":"<uuid>","status":"resolved","closedAt":"2026-09-23T11:35:00.000Z"} }`
- **Lỗi:** `404 NOT FOUND` · `403 FORBIDDEN` · `409 INVALID ISSUE TRANSITION`
- **UI:** `41._chi_ti_t_s_c_issue_detail_popup/code.html`

> > Không có endpoint DELETE vì cần giữ lịch sử xử lý.

#### 93 · `POST /issues/{issueId}/cancel` — Huỷ báo cáo sự cố

- **Quyền:** `tenant`
- **Body:** không có
- **Success:** `200` `{ "statusCode":200, "code":"ISSUE_CANCELLED", "data":{"id":"<uuid>","status":"cancel"} }`
- **Lỗi:** `404 NOT FOUND` · `403 FORBIDDEN` · `422 CANNOT CANCEL RESOLVED ISSUE`
- **UI:** `29._chi_ti_t_s_c_issue_detail_popup/code.html`

> > Sự cố đã `resolved` hoặc `closed` không huỷ được, trả `422`.

### 27.19 Conversation

#### 94 · `GET /conversations` — Liệt kê các hội thoại của người gọi

- **Quyền:** `tenant`, `landlord`
- **Query:** `filter[type]=room` · `pageNo=1` · `pageSize=20`
- **Success:** `200` `{ "statusCode":200, "code":"CONVERSATIONS_FETCHED", "data":[{"id":"<uuid>","type":"room","title":"Phòng P.302","unreadCount":2}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`
- **Lỗi:** `403 FORBIDDEN` · `422 VALIDATION FAILED`
- **UI:** `16._h_p_th_inbox/code.html` · `48._h_p_th_inbox_1/code.html` · `48._h_p_th_inbox_5/code.html`

> Không có quyền `admin`. Admin không tham gia hội thoại.

#### 95 · `GET /conversations/{conversationId}` — Đọc chi tiết hội thoại

- **Quyền:** `tenant`, `landlord`
- **Success:** `200` `{ "statusCode":200, "code":"CONVERSATION_FETCHED", "data":{"id":"<uuid>","type":"room","roomId":"<uuid>","contractId":"<uuid>","title":"Phòng P.302","unreadCount":2} }`
- **Lỗi:** `403 FORBIDDEN` · `404 NOT FOUND`
- **UI:** `49._chi_ti_t_cu_c_tr_chuy_n_chat_thread_detail_1/code.html` · `49._chi_ti_t_cu_c_tr_chuy_n_chat_thread_detail_5/code.html`

#### 96 · `POST /conversations/resolve-conversation` — Lấy hội thoại của phòng hoặc tòa nhà

- **Quyền:** `tenant`, `landlord`
- **Body:** `{ "contractId":"<uuid>" }` hoặc `{ "buildingId":"<uuid>" }`
- **Success:** `200` `{ "statusCode":200, "code":"CONVERSATION_RESOLVED", "data":{"id":"<uuid>","type":"room","contractId":"<uuid>"} }`
- **Lỗi:** `422 EXACTLY ONE CONTEXT REQUIRED` · `403 FORBIDDEN` · `404 CONTEXT NOT FOUND`
- **UI:** `18._tr_chuy_n_nh_m_ph_ng_tr_property_group_chat_room/code.html` · `19._tr_chuy_n_nh_m_t_a_nh_property_group_chat_building/code.html` · `23._xem_h_p_ng_thu_view_lease/code.html`

### 27.20 Message

#### 97 · `GET /messages` — Liệt kê tin nhắn trong một hội thoại

- **Quyền:** `tenant`, `landlord`
- **Query:** `filter[conversationId]=<uuid>` · `pageSize=30` · `cursor=<opaque>`
- **Success:** `200` `{ "statusCode":200, "code":"MESSAGES_FETCHED", "data":[{"id":"<uuid>","conversationId":"<uuid>","senderId":"<uuid>","type":"text","content":"Dạ em gửi ảnh vòi xịt ạ","createdAt":"2026-09-23T11:30:00.000Z"}], "pagination":{"type":"cursor","pageSize":30,"nextCursor":null,"hasNextPage":false} }`
- **Lỗi:** `403 FORBIDDEN` · `422 INVALID CURSOR` · `404 CONVERSATION NOT FOUND`
- **UI:** `49._chi_ti_t_cu_c_tr_chuy_n_chat_thread_detail_1/code.html`

#### 98 · `POST /messages` — Gửi tin nhắn

- **Quyền:** `tenant`, `landlord`
- **Body:** `{ "conversationId":"<uuid>", "type":"text", "content":"Dạ thợ mấy giờ qua kiểm được ạ", "mediaId":null }`
- **Success:** `201` `{ "statusCode":201, "code":"MESSAGE_SENT", "data":{"id":"<uuid>","conversationId":"<uuid>","type":"text","content":"Dạ thợ mấy giờ qua kiểm được ạ","createdAt":"2026-09-23T11:38:00.000Z"} }`; `Location: /api/v1/messages`
- **Lỗi:** `403 FORBIDDEN` · `409 CONVERSATION ARCHIVED` · `422 MESSAGE CONTENT INVALID`
- **UI:** `49._chi_ti_t_cu_c_tr_chuy_n_chat_thread_detail_1/code.html`

#### 99 · `POST /messages/mark-read` — Đánh dấu đã đọc một hội thoại

- **Quyền:** `tenant`, `landlord`
- **Body:** `{ "conversationId":"<uuid>", "lastReadMessageId":"<uuid>" }`
- **Success:** `200` `{ "statusCode":200, "code":"MESSAGES_MARKED_READ", "data":{"conversationId":"<uuid>","unreadCount":0} }`
- **Lỗi:** `403 FORBIDDEN` · `404 MESSAGE NOT FOUND` · `422 READ CURSOR INVALID` · điều kiện migration cho con trỏ
- **UI:** `48._h_p_th_inbox_1/code.html`

### 27.21 Notification

#### 100 · `GET /notifications` — Liệt kê thông báo

- **Quyền:** `tenant`, `landlord`, `admin`
- **Query:** `filter[unreadOnly]=true` · `pageSize=20`
- **Success:** `200` `{ "statusCode":200, "code":"NOTIFICATIONS_FETCHED", "data":[{"id":"<uuid>","type":"invoice_due","data":{"invoiceId":"<uuid>"},"readAt":null}], "pagination":{"type":"cursor","pageSize":20,"nextCursor":null,"hasNextPage":false} }`
- **Lỗi:** `401 INVALID TOKEN` · `422 VALIDATION FAILED`
- **UI:** `16._h_p_th_inbox/code.html` · `48._h_p_th_inbox_1/code.html` · `48._h_p_th_inbox_5/code.html`

#### 101 · `POST /notifications/{notificationId}/mark-read` — Đánh dấu đã đọc một thông báo

- **Quyền:** `tenant`, `landlord`, `admin`
- **Body:** không có
- **Success:** `200` `{ "statusCode":200, "code":"NOTIFICATION_MARKED_READ", "data":{"id":"<uuid>","readAt":"2026-09-23T11:40:00.000Z"} }`
- **Lỗi:** `403 FORBIDDEN` · `404 NOT FOUND`
- **UI:** `16._h_p_th_inbox/code.html` · `48._h_p_th_inbox_1/code.html` · `48._h_p_th_inbox_5/code.html`

#### 102 · `POST /notifications/mark-all-read` — Đánh dấu đã đọc toàn bộ thông báo chưa đọc

- **Quyền:** `tenant`, `landlord`, `admin`
- **Body:** không có
- **Success:** `200` `{ "statusCode":200, "code":"ALL_NOTIFICATIONS_MARKED_READ", "data":{"markedCount":3} }`
- **Lỗi:** `401 INVALID TOKEN`
- **UI:** `16._h_p_th_inbox/code.html` · `48._h_p_th_inbox_1/code.html` · `48._h_p_th_inbox_5/code.html`

### 27.22 NotificationPreference

#### 103 · `GET /me/notification-preference` — Đọc tuỳ biến thông báo

- **Quyền:** `tenant`, `landlord`, `admin`
- **Success:** `200` `{ "statusCode":200, "code":"NOTIFICATION_PREFERENCES_FETCHED", "data":[{"type":"invoice","enabled":true},{"type":"chat","enabled":true},{"type":"issue","enabled":true},{"type":"match","enabled":true},{"type":"account","enabled":true}] }`; tối đa năm bản ghi nên response này không phân trang
- **Lỗi:** `401 INVALID TOKEN`
- **UI:** `32._c_i_t_th_ng_b_o_notification_settings/code.html` · `51._c_i_t_th_ng_b_o_notification_settings_1/code.html` · `51._c_i_t_th_ng_b_o_notification_settings_3/code.html`

#### 104 · `PUT /me/notification-preference` — Thay toàn bộ tuỳ biến thông báo

- **Quyền:** `tenant`, `landlord`, `admin`
- **Body:** `{ "preferences":[{"type":"invoice","enabled":true},{"type":"chat","enabled":false}] }`
- **Success:** `200` `{ "statusCode":200, "code":"NOTIFICATION_PREFERENCES_UPDATED", "data":{"updatedAt":"2026-09-23T11:45:00.000Z"} }`
- **Lỗi:** `422 INVALID NOTIFICATION TYPE` · `422 VALIDATION FAILED`
- **UI:** `32._c_i_t_th_ng_b_o_notification_settings/code.html`

### 27.23 AuditLog

#### 105 · `GET /audit-logs` — Tìm kiếm nhật ký chỉ ghi thêm

- **Quyền:** `admin`
- **Query:** `filter[entityType]=user` · `from=2026-09-01T00:00:00.000Z` · `pageNo=1` · `pageSize=20`
- **Success:** `200` `{ "statusCode":200, "code":"AUDIT_LOGS_FETCHED", "data":[{"id":"<uuid>","actorId":"<uuid>","action":"user.lock","entityType":"user","entityId":"<uuid>","createdAt":"2026-09-23T11:55:00.000Z"}], "pagination":{"type":"offset","pageNo":1,"pageSize":20,"totalItems":1,"totalPages":1,"hasNextPage":false,"hasPreviousPage":false} }`
- **Lỗi:** `403 FORBIDDEN` · `422 VALIDATION FAILED`
- **UI:** `13._nh_t_k_ki_m_to_n_audit_logs/code.html`

#### 106 · `GET /audit-logs/{auditLogId}` — Đọc hoặc xuất một bản ghi kiểm toán

- **Quyền:** `admin`
- **Success:** `200` `{ "statusCode":200, "code":"AUDIT_LOG_FETCHED", "data":{"id":"<uuid>","action":"user.lock","entityType":"user","entityId":"<uuid>","beforeData":{"status":"active"},"afterData":{"status":"locked"}} }`
- **Lỗi:** `403 FORBIDDEN` · `404 NOT FOUND`
- **UI:** `14._chi_ti_t_nh_t_k_ki_m_to_n_audit_log_detail_popup/code.html`

### 27.24 Dashboard

#### 107 · `GET /dashboard` — Đọc số liệu tổng hợp hệ thống

- **Quyền:** `admin`
- **Query:** `from=2026-09-01` · `to=2026-09-30`
- **Success:** `200` `{ "statusCode":200, "code":"DASHBOARD_FETCHED", "data":{"totalUsers":1250,"totalLandlords":320,"totalTenants":930,"totalBuildings":145,"pendingApprovalBuildings":8,"totalRooms":1580,"occupancyRate":"89.2","systemTransactionVolume":3450000000} }`
- **Lỗi:** `403 FORBIDDEN` · `422 INVALID DATE RANGE`
- **UI:** `6._b_ng_i_u_khi_n_qu_n_tr_vi_n_admin_dashboard/code.html`

---

## 28. Ghi chú đối chiếu database

1. `RatePolicy` và `BillingSetting` dùng phạm vi database `building` và `room`. Mặc định của chủ nhà được kế thừa khi cả hai định danh cha đều null. Nếu UI cần phạm vi tường minh `scope=landlord`, phải thêm giá trị enum bằng migration database trước. **Trạng thái: pending, chưa chốt.**
2. **Tài khoản nhận tiền đã chuyển sang hồ sơ chủ nhà (D39, 2026-09-26).** Bảng `VietQrReceiverConfig` và hai endpoint `PUT`/`GET /vietqr-configs` (mã cũ 32–33) **đã bị gỡ khỏi hợp đồng**. Ba cột `bank_code`, `account_number`, `account_name` nằm trên `LandlordProfile`, phục vụ ở cấp **chủ nhà**, không cấp tòa nhà: đọc qua `GET /me` và sửa qua `PATCH /me` (mục 27.2). Hệ quả bắt buộc:
   - `GET /me/buildings` và `GET /me/buildings/{buildingId}` **không** còn trường `vietQrConfigured`; trạng thái cấu hình QR không còn là thuộc tính của tòa nhà.
   - `DELETE /buildings/{buildingId}` **không** cascade sang cấu hình QR nữa. Khi chủ nhà đổi ngân hàng hoặc số tài khoản, mọi tòa nhà của chủ nhà đó dùng chung tài khoản mới.
   - Không cần migration cột mới: `LandlordProfile` đã có sẵn ba cột này. Ngược lại, nếu bản rà soát `f96888b` đã tạo `VietQrReceiverConfig` thì phải **xoá bảng** bằng migration, không chỉ bỏ endpoint.
   - Cấu trúc hóa đơn quyết toán mà API 67 phụ thuộc vẫn nằm trong nhóm pending này.
3. `IssueReport` chỉ dùng các field có trong database. Category, priority, thợ kỹ thuật, thời gian dự kiến và chi phí sửa nằm ngoài hợp đồng cho tới khi có migration và quyết định PM riêng. Ảnh sự cố là các bản ghi `Media` với `ownerType=issue_report` và `purpose=issue_photo`, không phải một cột trên `IssueReport`.
4. **Phạm vi cascade của xóa mềm.** `DELETE /users/{userId}` đặt cờ `is_deleted = true` trên `User` và cascade mềm sang `LandlordProfile`, `PushDevice`, `NotificationPreference`, `RoommateProfile`, `FavoriteRoom`, `MatchRequest`, các bản ghi thành viên hội thoại và các thông báo thuộc sở hữu. `DELETE /buildings/{buildingId}` cascade mềm sang `Room`, `RatePolicy` và `BillingSetting` của tòa nhà đó (không có bảng cấu hình QR nữa theo D39). Cả hai trường hợp đều **không** cascade sang `Contract`, `ContractMember`, `Invoice`, `Payment`, `MeterReading`, `IssueReport`, `Message`, `Conversation` và `AuditLog`: các bảng này giữ nguyên dữ liệu để tra cứu tài chính, pháp lý và kiểm toán, và chỉ bị ẩn khỏi danh sách theo tài nguyên cha đã xóa. Cột `is_deleted` đã có sẵn trong Base Entity nên **không** cần migration cột mới; phần còn phải migration chỉ là các partial unique index phải được rà lại cho khớp với cascade.
5. `RatePolicy.type` bị database ràng buộc ở `electricity`, `water`, `wifi`, `cleaning`, `parking`, `maintenance`. Kiểu TypeScript trong tài liệu thiết kế còn liệt kê `other`; ràng buộc database là chuẩn, và thêm `other` cần migration cùng quyết định PM.
6. `Contract` lưu snapshot liên hệ tenant thụ động, tiền thuê, tiền cọc, ngày và số phương tiện. Thời điểm thanh toán thuộc `BillingSetting`; `paymentDayOfMonth` không phải field của Contract.
7. `Invoice` chỉ có `contract_id` làm cha và không có cột `room_id`, `due_date` hay `is_final`. Hóa đơn hằng tháng được sinh tự động theo phòng khi có hai chỉ số và một chính sách giá, nên `POST /invoices` dành riêng cho hóa đơn quyết toán do chủ nhà tạo. `rentAmount` và `breakdown` luôn được server tính từ chỉ số và chính sách giá đang hiệu lực, không bao giờ nhận từ client.
8. `Invoice.otherFees[].amount` được phép âm cho khoản giảm trừ đã duyệt. `totalAmount` phải lớn hơn hoặc bằng 0; client không bao giờ tự tính tổng hóa đơn.
9. `MatchRequest.status` có `pending`, `accepted`, `rejected`, `withdrawn`. Không có `cancelled`: người gửi rút bằng `POST /match-requests/{matchRequestId}/withdraw-request` (mã 110) chuyển sang `withdrawn`, bên nhận dùng `reject-request` chuyển sang `rejected`. Không có endpoint xoá bản ghi. `requester_id` và `target_id` là duy nhất theo cặp, nên yêu cầu đã `rejected` hoặc `withdrawn` không gửi lại được nếu không đổi index — cần quyết định migration, xem D50.
10. `MeterReading` không có cột `contract_id`. Liên kết chỉ số với hợp đồng thông qua `Room` khi báo cáo cần.
11. `GET /invoices`, `GET /issues`, `GET /users`, `GET /contract-members` và `GET /audit-logs` thay thế các endpoint xuất file đã bị bỏ. Response chỉ là luồng tệp khi `format` yêu cầu định dạng khác JSON. `format` chỉ được khai báo trên route collection `GET`; route đọc một tài nguyên (`GET /invoices/{invoiceId}`, `GET /audit-logs/{auditLogId}`) luôn trả JSON.
12. Không có route `/admin/*`, `/debts`, `*/export`, `*/batch`, route lồng tài nguyên cha, hay route bulk generic nào trong v1. Các thao tác nhiều bản ghi duy nhất là các action có tên nghiệp vụ: `mark-all-read` của thông báo, `issue-invoice` và `send-reminder` của hóa đơn.
13. Vai trò trong cột `Quyền` chỉ gồm `public`, `tenant`, `landlord`, `admin` và `system`. Cột trống chỉ dùng cho API 20, nơi quyền kế thừa từ tài nguyên cha. `role` không thay thế kiểm tra quan hệ: tenant không thể đọc tài nguyên của tenant khác dù cùng vai trò.
14. **Ghi chỉ số hàng loạt chưa có endpoint.** Bản rà soát có `POST /buildings/{buildingId}/meter-reading-batches` cùng ba màn hình `27._b_t_u_ghi_ch_s_h_ng_lo_t_bulk_reading_entry/code.html`, `28._ti_n_tr_nh_ghi_ch_s_h_ng_lo_t_bulk_reading_flow/code.html` và `29._b_o_c_o_t_ng_k_t_ghi_ch_s_h_ng_lo_t_bulk_reading_summary/code.html`. Ba màn hình này mới xuất hiện ở `Rentify_UI_Screen_Outline_v0.1.md` với nhãn **[MỚI]** và mức ưu tiên thấp nhất, chưa được `requirement.md` xác nhận, trong khi `api-conventions.md` mục 14 cấm bulk cho chốt chỉ số và OCR. Vì vậy v1 chỉ có `POST /meter-readings` cho từng phòng và **không** có endpoint lô. **Trạng thái: pending, PM đã quyết định giữ nguyên pending tại D47 (chưa chốt).** Nếu PM chốt giữ, cần bổ sung endpoint có tên nghiệp vụ và bảng `MeterReadingBatch` qua migration.

---

## 29. Nhật ký thay đổi so với bản rà soát

Bản rà soát là commit `f96888b` với 109 route. Bảng dưới đây đối chiếu từng route của bản đó với hợp đồng **109 endpoint** hiện tại, nên reviewer tra ngược được bằng số mã cũ.

**Hai hệ số khác nhau, đừng đọc lẫn:** cột *Mã cũ* là số route của bản rà soát (1–109). Cột *Mã mới* là số endpoint của hợp đồng hiện tại (1–110, thiếu 32), khớp đúng với mục 27.

**Cân đối số lượng:** trong 109 route của bản rà soát, 7 route bị bỏ hẳn (mã cũ 19, 20, 36, 39, 71, 99, 64) và 102 route còn lại được giữ. 102 route đó ánh xạ thành 103 endpoint hiện tại; 6 endpoint còn lại là endpoint thuần mới, **không có route nguồn** ở bản rà soát (mã mới 15 `DELETE /users/{userId}`, 31 `DELETE /buildings/{buildingId}`, 43 `GET /roommate-profiles/{roommateProfileId}`, 108 `GET /admin/buildings/{buildingId}`, 109 `DELETE /rooms/{roomId}`, 110 `POST /match-requests/{matchRequestId}/withdraw-request` — xem các dòng có *Mã cũ* = `—` ở dưới). Ba endpoint D50 (108, 109, 110) không có route nguồn vì không tồn tại trong `f96888b`. Trong 102 route được giữ, có 11 route bị tách thêm theo vai trò hoặc theo business action, sinh ra 14 endpoint mới.

| Mã cũ | Thay đổi | Mã mới |
|---|---|---|
| 1–11, 13–18, 21, 23–24, 26–33, 37–38, 40, 42–50, 65, 67–68, 79–83, 85–86, 92, 95–96 | Giữ nguyên method và path; chỉ dịch mô tả sang tiếng Việt và đánh số lại theo thứ tự mới. Một số route trong nhóm này sau đó được tách tiếp theo vai trò (thêm biến thể `/me` cho chủ nhà hoặc tenant), nên một route cũ có thể ánh xạ tới nhiều endpoint; xem D48. | 1–9, 16–17, 20–21, 25–27, 33–34, 36, 39–42, 44–47, 50–52, 54–63, 78–79, 87, 90–95, 100, 103–104 |
| 12 | `POST /media` nhận `multipart/form-data` thay bằng luồng 2 bước `presign-upload` rồi `complete-upload` | 18–19 |
| 19, 20 | **Bỏ hẳn theo D39 (2026-09-26).** Cấu hình QR nhận tiền cấp tòa nhà bị loại: tài khoản nhận tiền nay thuộc `LandlordProfile` và đọc/sửa qua `GET /me` + `PATCH /me` (mã mới 7–8). Bảng `VietQrReceiverConfig` phải được xoá bằng migration nếu đã tạo; mọi endpoint cấu hình QR riêng đều không tồn tại trong v1 | — |
| 22 | `POST /buildings/{buildingId}/rooms` thành `POST /rooms`, `buildingId` nằm trong body | 35 |
| 15, 104 | Hoàn tác phép gộp: `GET /admin/buildings` trở lại thành route riêng cho hàng đợi duyệt. `GET /buildings` giờ chỉ là marketplace công khai, thêm `GET /me/buildings` cho danh sách của chủ nhà — tách theo vai trò, xem D48 | 22–24 |
| 18, 105, 106 | Hoàn tác phép gộp: tách `PATCH /buildings/{buildingId}` (chủ nhà tự sửa) khỏi hai action vòng đời `approve` và `reject` của admin. `status` không nằm trong body của PATCH, xem D48 | 28–30 |
| 24, 25 | Hoàn tác phép gộp: tách `mark-room-ready` khỏi `PATCH /rooms/{roomId}`. Chuyển trạng thái phòng là action vòng đời riêng, xem D48 | 37–38 |
| 34, 35 | `accept` và `reject` đổi tên thành `accept-request` và `reject-request` | 48–49 |
| 41 | `deactivate` đổi tên thành `deactivate-policy` | 53 |
| 51 | `PUT /contracts/{contractId}/template` thành `PUT /contracts/{contractId}/apply-template` | 64 |
| 52 | `POST /contracts/{contractId}/documents/draft` thành `POST /contracts/{contractId}/generate-draft-document` | 65 |
| 53 | `activate` thành `activate-contract` | 66 |
| 54, 63 | Bỏ tiền tố `/rooms/{roomId}`; chỉ số quyết toán tạo bằng `POST /meter-readings` với `isBaseline=true` | 74 |
| 55, 66 | `POST /rooms/{roomId}/invoices` và `checkout/final-invoice` gộp thành `POST /invoices` | 77 |
| 56 | `checkout/complete` thành `complete-checkout` | 67 |
| 57, 58, 59 | Bỏ route lồng `/contracts/{contractId}/members`; `contractId` nằm trong body, `memberId` thành `contractMemberId`, `leave` thành `leave-contract` | 68–70 |
| 60 | `GET /contracts/{contractId}/members/export` thành `GET /contract-members` bắt buộc `filter[contractId]`, xuất tệp bằng `?format=` | 71 |
| 61, 62 | Bỏ tiền tố `/rooms/{roomId}`; `roomId` nằm trong query, `ocr-preview` thành `preview-ocr-result` | 72–73 |
| 65, 72, 74, 75 | `GET /invoices`, `GET /debts`, `GET /debts/export` và `GET /invoices/export` gộp thành `GET /invoices` với `filter[...]` và `?format=` cho chủ nhà; thêm `GET /me/invoices` cho tenant, xem D48 | 75–76 |
| 69 | `POST /invoices/{invoiceId}/issue` thành bulk `POST /invoices/issue-invoice` nhận `invoiceIds[]` | 80 |
| 70 | `POST /invoices/{invoiceId}/cancel` thành `cancel-invoice` | 81 |
| 73 | `POST /debts/reminders` thành bulk `POST /invoices/send-reminder` nhận `invoiceIds[]` | 82 |
| 76, 77, 78 | Bỏ route lồng `/invoices/{invoiceId}`; `invoiceId` nằm trong body, action thành `create-intent` và `record-cash-payment` | 83–86 |
| 80, 84 | `GET /issues/export` gộp vào collection `GET /issues` bằng `?format=` cho chủ nhà; thêm `GET /me/issues` cho tenant, xem D48 | 88–89 |
| 87, 88, 89 | Bỏ route lồng `/conversations/{conversationId}`; `conversationId` nằm trong query hoặc body, `read` thành `mark-read` | 97–99 |
| 90, 91 | `GET /contracts/{contractId}/conversation` và `GET /buildings/{buildingId}/conversation` gộp thành `POST /conversations/resolve-conversation` | 96 |
| 93, 94 | `read` thành `mark-read`, `read-all` thành `mark-all-read` | 101–102 |
| 97 | `GET /admin/dashboard` thành `GET /dashboard` | 107 |
| 98, 100 | `GET /admin/users` và `GET /admin/users/export` gộp thành `GET /users` với `?format=` | 10 |
| 101 | `GET /admin/users/{userId}` thành `GET /users/{userId}` | 11 |
| 102, 103 | Hoàn tác phép gộp: `lock-user` và `unlock-user` trở lại thành hai action `POST /users/{userId}/lock` và `POST /users/{userId}/unlock`. `status` không nằm trong body của PATCH, xem D48 | 12–14 |
| 107, 108 | `GET /admin/audit-logs` và `GET /admin/audit-logs/export` gộp thành `GET /audit-logs` với `?format=` | 105 |
| 109 | `GET /admin/audit-logs/{auditLogId}/export` thành `GET /audit-logs/{auditLogId}` chỉ trả JSON | 106 |
| — | Thêm `DELETE /users/{userId}` (xóa mềm) | 15 |
| — | Thêm `DELETE /buildings/{buildingId}` (xóa mềm) | 31 |
| — | Thêm `GET /roommate-profiles/{roommateProfileId}` | 43 |
| — | Thêm `GET /admin/buildings/{buildingId}`: chi tiết tòa nhà cho hàng đợi duyệt, xem D50 | 108 |
| — | Thêm `DELETE /rooms/{roomId}` (xóa mềm), xem D50 | 109 |
| — | Thêm `POST /match-requests/{matchRequestId}/withdraw-request`: người gửi rút yêu cầu, xem D50 | 110 |
| 36 | Bỏ `DELETE /match-requests/{matchRequestId}`: rút yêu cầu là chuyển trạng thái `withdrawn`, không phải xoá bản ghi; dùng action mã 110, xem D50 | — |
| 39 | Bỏ `POST /rate-policies/batch`: bulk generic không được phép, xem mục 1 | — |
| 71 | Bỏ `GET /invoices/{invoiceId}/document`: xuất tệp qua collection `GET /invoices` kèm `?format=pdf` | — |
| 99 | Bỏ `POST /admin/users`: tài khoản chỉ tạo qua tự đăng ký, admin dùng `PATCH /users/{userId}` | — |
| 64 | `POST /buildings/{buildingId}/meter-reading-batches` **đang chờ quyết định PM**, xem mục 28.14 và D47 | — |
