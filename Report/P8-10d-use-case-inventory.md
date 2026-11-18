# P8-10d — Bảng kiểm kê use case (bản nháp chờ duyệt)

Nguồn: `rentify-api-spec/reference/rentify.json` (133 endpoint, 10 tag). Dùng làm cơ sở vẽ 5 sơ đồ mục 1.3.1–1.3.5 và làm phụ lục cho Lead Author.

**Quy ước**
- Mức use case là "mục tiêu của tác nhân", CRUD gộp thành một use case "Quản lý X".
- Web và mobile gộp chung một use case. Chưa có cột nền tảng vì chưa có mã nguồn web để đối chiếu; sẽ thêm khi có.
- `«include»` chỉ dùng khi bước con bắt buộc, `«extend»` khi tùy chọn.
- Chức năng spec ghi chưa triển khai hoặc hoãn được đánh dấu **[chưa có]** và không vẽ vào sơ đồ.

## Quyết định đã chốt khi lập bảng

| # | Nội dung | Lý do |
|---|---|---|
| 1 | Khách vãng lai **không** có use case xem hồ sơ tìm bạn ở ghép | `GET /roommate-profiles` yêu cầu `BearerAuth` và chỉ cho tenant. Issue 1.3.5 ghi ngược lại nên cần báo Lead |
| 2 | Thanh toán bằng QR vẽ ở mức "Thanh toán hóa đơn" (tạo ý định thanh toán), không vẽ đối soát tự động | `requirement.md` xếp auto-reconciliation vào Stretch, webhook là tác nhân hệ thống |
| 3 | Cấu hình QR theo tòa nhà và quyết toán tiền cọc không vẽ | Spec ghi chưa triển khai (`PUT /buildings/{id}/vietqr-config`) và hoãn sau MVP (`POST /contracts/{id}/deposit-settlement`) |
| 4 | Chỉ số điện nước là use case của chủ trọ; người thuê xem qua chi tiết hóa đơn | `/meter-readings` là landlord-only. Mục 2.4 "theo dõi điện nước" cần đối chiếu với màn hình app |

## 1.3.1 Sơ đồ tổng quát — 4 tác nhân, 10 gói

| Gói | Tag nguồn | Khách | Người thuê | Chủ trọ | Quản trị viên |
|---|---|:-:|:-:|:-:|:-:|
| 1. Tài khoản và xác thực | Auth, User | x | x | x | x |
| 2. Trò chuyện và thông báo | Chat, Notification | | x | x | x |
| 3. Quản trị hệ thống (duyệt bất động sản, tài khoản, nhật ký, thống kê) | Property, User, Operation | | | | x |
| 4. Khám phá phòng trọ | Property, Administrative Units | x | x | | |
| 5. Quản lý tòa nhà và phòng | Property | | | x | |
| 6. Hợp đồng và thành viên | Contract | | x | x | |
| 7. Biểu giá và chỉ số điện nước | Billing | | | x | |
| 8. Hóa đơn và thanh toán | Billing | | x | x | |
| 9. Sự cố và tệp đính kèm | Operation | | x | x | |
| 10. Tìm bạn ở ghép | Matching | | x | | |

## 1.3.5 Khách vãng lai (7)

| Mã | Use case | Quan hệ | Endpoint nguồn |
|---|---|---|---|
| G1 | Tìm kiếm phòng trọ | «include» Chọn khu vực (tỉnh, phường) | `GET /rooms`, `/administrative-units/...` |
| G2 | Xem chi tiết phòng | | `GET /rooms/{roomId}` |
| G3 | Tìm kiếm tòa nhà | «include» Chọn khu vực | `GET /buildings` |
| G4 | Xem chi tiết tòa nhà | | `GET /buildings/{buildingId}` |
| G5 | Đăng ký tài khoản | «include» Xác thực email; «extend» Gửi lại email xác thực | `POST /auth/register`, `/auth/email-verifications`, `/auth/email-verification-requests` |
| G6 | Đăng nhập | | `POST /auth/login` |
| G7 | Quên và đặt lại mật khẩu | «include» Yêu cầu đặt lại mật khẩu | `POST /auth/password-reset-requests`, `/auth/password-resets` |

## 1.3.4 Người thuê trọ (14)

| Mã | Use case | Quan hệ | Endpoint nguồn |
|---|---|---|---|
| T1 | Đăng nhập, đăng xuất | | `/auth/login`, `/auth/logout`, `/auth/refresh` |
| T2 | Quản lý hồ sơ cá nhân | «extend» Đổi mật khẩu | `GET/PATCH /me`, `PUT /me/password` |
| T3 | Tìm phòng và lưu phòng yêu thích | «include» Tìm kiếm phòng (kế thừa từ khách) | `GET /rooms`, `/me/favorite-rooms` |
| T4 | Xem phòng đang thuê | | `GET /me/room-hub` |
| T5 | Xem hợp đồng | | `GET /me/contracts`, `GET /contracts/{id}` |
| T6 | Xem hóa đơn (kèm tiền điện nước) | | `GET /me/invoices`, `GET /invoices/{id}` |
| T7 | Thanh toán hóa đơn bằng QR | «include» Xem hóa đơn | `POST /payments/create-intent` |
| T8 | Xem lịch sử thanh toán | | `GET /me/payments` |
| T9 | Báo cáo sự cố | «extend» Đính kèm ảnh | `POST /issues`, `/media/presign-upload` |
| T10 | Theo dõi và hủy sự cố | | `GET /me/issues`, `POST /issues/{id}/cancel` |
| T11 | Trò chuyện | «extend» Đính kèm tệp; «extend» Tìm tin nhắn | `/conversations`, `/messages` |
| T12 | Nhận và quản lý thông báo | «include» Đăng ký thiết bị nhận thông báo đẩy | `/notifications`, `/me/push-devices`, `/me/notification-preference` |
| T13 | Quản lý hồ sơ ở ghép | | `GET/PUT /me/roommate-profile` |
| T14 | Tìm bạn ở ghép và gửi yêu cầu ghép | «include» Tìm hồ sơ; «extend» Chấp nhận, từ chối, rút yêu cầu | `/roommate-profiles`, `/match-requests` |

## 1.3.3 Chủ trọ (16)

| Mã | Use case | Quan hệ | Endpoint nguồn |
|---|---|---|---|
| L1 | Đăng nhập và quản lý hồ sơ | | `/auth/*`, `/me` |
| L2 | Quản lý tòa nhà (gửi duyệt, sửa, xóa) | «include» Tải ảnh minh chứng sở hữu | `/buildings`, `/me/buildings` |
| L3 | Thiết lập biểu giá (điện, nước, dịch vụ) | | `/rate-policies`, `/buildings/{id}/rate-policies/batch` |
| L4 | Cấu hình kỳ lập hóa đơn | | `/billing-settings` |
| L5 | Quản lý phòng | «extend» Đánh dấu phòng sẵn sàng cho thuê | `/rooms`, `/me/rooms`, `POST /rooms/{id}/mark-ready` |
| L6 | Lập hợp đồng | «include» Chọn mẫu hợp đồng; «include» Sinh bản nháp PDF | `/contracts`, `/contract-templates`, `.../apply-template`, `.../generate-draft-document` |
| L7 | Kích hoạt hợp đồng (tải bản đã ký) | «include» Lập hợp đồng | `POST /contracts/{id}/activate-contract` |
| L8 | Quản lý người thuê và thành viên hợp đồng | | `/contracts/tenants`, `/contract-members` |
| L9 | Xử lý trả phòng và hợp đồng bị khóa | | `.../complete-checkout`, `.../lock-cycles/{id}/decision` |
| L10 | Ghi chỉ số điện nước | «extend» Đính kèm ảnh bằng chứng | `/meter-readings`, `.../evidence` |
| L11 | Lập và phát hành hóa đơn | «include» Ghi chỉ số điện nước; «extend» Chỉnh sửa, hủy hóa đơn | `/invoices`, `.../generate`, `.../issue-invoice`, `.../cancel-invoice` |
| L12 | Ghi nhận thanh toán tiền mặt | «include» Xem hóa đơn | `POST /payments/record-cash-payment` |
| L13 | Đối soát giao dịch thanh toán | | `GET /payments` |
| L14 | Xử lý sự cố | | `/issues`, `PATCH /issues/{id}` |
| L15 | Trò chuyện và gửi nhắc nhở tự động | «extend» Gửi bot reminder | `/conversations`, `/messages`, `.../bot-reminders` |
| L16 | Nhận và quản lý thông báo | «include» Đăng ký thiết bị | `/notifications`, `/me/push-devices` |

## 1.3.2 Quản trị viên (6)

| Mã | Use case | Quan hệ | Endpoint nguồn |
|---|---|---|---|
| A1 | Đăng nhập, đổi mật khẩu | | `/auth/login`, `PUT /me/password` |
| A2 | Duyệt bất động sản | «include» Xem hàng đợi, xem chi tiết; «extend» Phê duyệt; «extend» Từ chối (bắt buộc ghi chú) | `/admin/buildings`, `.../approve`, `.../reject` |
| A3 | Quản lý tài khoản | «extend» Khóa, mở khóa; «extend» Xóa mềm | `/users`, `.../lock`, `.../unlock` |
| A4 | Xem nhật ký kiểm toán | | `/audit-logs` |
| A5 | Xem thống kê hệ thống | | `GET /dashboard` |
| A6 | Nhận thông báo hệ thống | | `/notifications` |
