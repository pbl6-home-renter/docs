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
| T7 | Thanh toán hóa đơn bằng QR | «include» Xem chi tiết hóa đơn | `POST /payments/create-intent` |
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
| L7 | Kích hoạt hợp đồng | «include» Tải hợp đồng đã ký | `POST /contracts/{id}/activate-contract` |
| L8 | Quản lý người thuê và thành viên hợp đồng | | `/contracts/tenants`, `/contract-members` |
| L9 | Xử lý trả phòng và hợp đồng bị khóa | | `.../complete-checkout`, `.../lock-cycles/{id}/decision` |
| L10 | Ghi chỉ số điện nước | «extend» Đính kèm ảnh bằng chứng | `/meter-readings`, `.../evidence` |
| L11 | Lập và phát hành hóa đơn | «extend» Chỉnh sửa hóa đơn; «extend» Hủy hóa đơn | `/invoices`, `.../generate`, `.../issue-invoice`, `.../cancel-invoice` |
| L12 | Ghi nhận thanh toán tiền mặt | | `POST /payments/record-cash-payment` |
| L13 | Đối soát giao dịch thanh toán | | `GET /payments` |
| L14 | Xử lý sự cố | | `/issues`, `PATCH /issues/{id}` |
| L15 | Trò chuyện và gửi nhắc nhở tự động | «extend» Gửi bot reminder | `/conversations`, `/messages`, `.../bot-reminders` |
| L16 | Nhận và quản lý thông báo | «include» Đăng ký thiết bị nhận thông báo đẩy | `/notifications`, `/me/push-devices` |

## 1.3.2 Quản trị viên (6)

| Mã | Use case | Quan hệ | Endpoint nguồn |
|---|---|---|---|
| A1 | Đăng nhập, đổi mật khẩu | | `/auth/login`, `PUT /me/password` |
| A2 | Duyệt bất động sản | «include» Xem hàng đợi, xem chi tiết; «extend» Phê duyệt; «extend» Từ chối (bắt buộc ghi chú) | `/admin/buildings`, `.../approve`, `.../reject` |
| A3 | Quản lý tài khoản | «extend» Khóa, mở khóa; «extend» Xóa mềm | `/users`, `.../lock`, `.../unlock` |
| A4 | Xem nhật ký kiểm toán | | `/audit-logs` |
| A5 | Xem thống kê hệ thống | | `GET /dashboard` |
| A6 | Nhận thông báo hệ thống | | `/notifications` |

## Mô tả use case

### Khách vãng lai (1.3.5)

| Mã | Use case | Mô tả |
|---|---|---|
| G1 | Tìm kiếm phòng trọ | Khách tìm các phòng còn trống thuộc tòa nhà đã được duyệt, lọc theo từ khóa, tỉnh/thành và phường/xã. |
| G2 | Xem chi tiết phòng | Khách xem thông tin phòng gồm giá, diện tích, ảnh, địa chỉ tòa nhà và thông tin liên hệ chủ trọ. |
| G3 | Tìm kiếm tòa nhà | Khách tìm các tòa nhà đã được quản trị viên phê duyệt theo từ khóa và khu vực. |
| G4 | Xem chi tiết tòa nhà | Khách xem thông tin công khai của tòa nhà và các phòng thuộc tòa nhà đó. |
| G5 | Đăng ký tài khoản | Khách tạo tài khoản người thuê hoặc chủ trọ bằng email, sau đó xác thực email bằng liên kết gửi về; có thể yêu cầu gửi lại email xác thực. |
| G6 | Đăng nhập | Người dùng đăng nhập bằng email và mật khẩu để nhận phiên làm việc theo vai trò. |
| G7 | Quên và đặt lại mật khẩu | Người dùng yêu cầu đặt lại mật khẩu qua email, sau đó nhập mật khẩu mới bằng mã đặt lại có thời hạn ngắn. |

### Người thuê trọ (1.3.4)

| Mã | Use case | Mô tả |
|---|---|---|
| T1 | Đăng nhập, đăng xuất | Người thuê đăng nhập vào ứng dụng, tự động làm mới phiên và đăng xuất khi cần. |
| T2 | Quản lý hồ sơ cá nhân | Người thuê xem và cập nhật thông tin cá nhân, đổi mật khẩu khi cần. |
| T3 | Tìm phòng và lưu phòng yêu thích | Người thuê tìm phòng trọ và lưu các phòng quan tâm để xem lại sau. |
| T4 | Xem phòng đang thuê | Người thuê xem danh sách phòng mình đang thuê hoặc ở cùng theo hợp đồng còn hiệu lực. |
| T5 | Xem hợp đồng | Người thuê xem các hợp đồng liên quan đến mình, gồm thời hạn, giá thuê, tiền cọc và thành viên. |
| T6 | Xem hóa đơn và tiền điện nước | Người thuê xem các hóa đơn đã phát hành, gồm tiền phòng, điện, nước và các khoản phụ thu. |
| T7 | Thanh toán hóa đơn bằng QR | Người thuê chọn hóa đơn cần trả, hệ thống tạo mã QR để quét và chuyển khoản. |
| T8 | Xem lịch sử thanh toán | Người thuê theo dõi các giao dịch thanh toán đã thực hiện. |
| T9 | Báo cáo sự cố | Người thuê gửi báo cáo sự cố trong phòng (điện, nước, hư hỏng), có thể đính kèm ảnh minh họa. |
| T10 | Theo dõi và hủy sự cố | Người thuê xem tiến độ xử lý sự cố và hủy báo cáo chưa được giải quyết. |
| T11 | Trò chuyện | Người thuê nhắn tin trực tiếp hoặc theo nhóm với chủ trọ và người ở cùng, có thể gửi tệp và tìm lại tin nhắn. |
| T12 | Nhận và quản lý thông báo | Người thuê nhận thông báo đẩy trên điện thoại, xem danh sách thông báo, đánh dấu đã đọc và tùy chỉnh loại thông báo; ứng dụng đăng ký mã thiết bị với máy chủ để nhận thông báo. |
| T13 | Quản lý hồ sơ ở ghép | Người thuê tạo và cập nhật hồ sơ tìm bạn ở ghép gồm ngân sách, thói quen sinh hoạt và chế độ hiển thị. |
| T14 | Tìm bạn ở ghép và gửi yêu cầu ghép | Người thuê tìm hồ sơ phù hợp, gửi yêu cầu ghép đôi; bên nhận có thể chấp nhận hoặc từ chối, bên gửi có thể rút yêu cầu. |

### Chủ trọ (1.3.3)

| Mã | Use case | Mô tả |
|---|---|---|
| L1 | Đăng nhập và quản lý hồ sơ | Chủ trọ đăng nhập và cập nhật thông tin cá nhân, tài khoản nhận thanh toán. |
| L2 | Quản lý tòa nhà | Chủ trọ đăng ký tòa nhà kèm ảnh minh chứng sở hữu để quản trị viên duyệt, sau đó sửa hoặc xóa tòa nhà của mình. |
| L3 | Thiết lập biểu giá | Chủ trọ cấu hình đơn giá điện, nước và dịch vụ cho từng tòa nhà. |
| L4 | Cấu hình kỳ lập hóa đơn | Chủ trọ thiết lập quy tắc lập hóa đơn hằng kỳ cho tòa nhà. |
| L5 | Quản lý phòng | Chủ trọ thêm, sửa, xóa phòng và đánh dấu phòng sẵn sàng cho thuê. |
| L6 | Lập hợp đồng | Chủ trọ tạo hợp đồng nháp cho phòng, chọn mẫu hợp đồng và sinh bản nháp PDF để in ký. |
| L7 | Kích hoạt hợp đồng | Sau khi hai bên ký trên giấy, chủ trọ tải bản hợp đồng đã ký lên hệ thống để hợp đồng có hiệu lực. |
| L8 | Quản lý người thuê và thành viên hợp đồng | Chủ trọ xem danh sách người thuê, thêm hoặc cập nhật thành viên và ghi nhận thành viên rời đi. |
| L9 | Xử lý trả phòng và hợp đồng bị khóa | Chủ trọ hoàn tất thủ tục trả phòng và quyết định khôi phục hoặc chấm dứt hợp đồng đang bị tạm ngưng. |
| L10 | Ghi chỉ số điện nước | Chủ trọ nhập chỉ số điện nước hằng kỳ cho từng phòng, có thể đính kèm ảnh làm bằng chứng. |
| L11 | Lập và phát hành hóa đơn | Chủ trọ tạo hóa đơn theo tòa nhà và kỳ, chỉnh sửa khoản phụ thu, phát hành hàng loạt hoặc hủy hóa đơn khi cần. |
| L12 | Ghi nhận thanh toán tiền mặt | Chủ trọ ghi nhận khoản người thuê trả bằng tiền mặt cho hóa đơn. |
| L13 | Đối soát giao dịch thanh toán | Chủ trọ xem các giao dịch thanh toán để đối chiếu dòng tiền. |
| L14 | Xử lý sự cố | Chủ trọ xem hàng đợi sự cố và cập nhật trạng thái từ đang chờ, đang xử lý đến đã giải quyết. |
| L15 | Trò chuyện với người thuê | Chủ trọ nhắn tin với người thuê và gửi nhắc nhở tự động theo mẫu trong hội thoại. |
| L16 | Nhận và quản lý thông báo | Chủ trọ nhận thông báo đẩy và quản lý thông báo; ứng dụng đăng ký mã thiết bị với máy chủ. |

### Quản trị viên (1.3.2)

| Mã | Use case | Mô tả |
|---|---|---|
| A1 | Đăng nhập và đổi mật khẩu | Quản trị viên (tài khoản được cấp sẵn) đăng nhập và đổi mật khẩu. |
| A2 | Duyệt bất động sản | Quản trị viên xem hàng đợi tòa nhà chờ duyệt, xem chi tiết rồi phê duyệt, hoặc từ chối kèm ghi chú bắt buộc. |
| A3 | Quản lý tài khoản | Quản trị viên xem danh sách người dùng, cập nhật thông tin, khóa hoặc mở khóa, xóa mềm tài khoản. |
| A4 | Xem nhật ký kiểm toán | Quản trị viên tra cứu nhật ký thao tác của hệ thống để kiểm tra và truy vết. |
| A5 | Xem thống kê hệ thống | Quản trị viên xem số liệu tổng hợp của toàn hệ thống trong một khoảng thời gian. |
| A6 | Nhận thông báo hệ thống | Quản trị viên nhận và xem các thông báo liên quan đến hoạt động hệ thống. |
