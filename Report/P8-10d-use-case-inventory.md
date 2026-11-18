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
| G1 | Tìm kiếm phòng trọ | Khách vãng lai tìm các phòng còn trống thuộc những tòa nhà đã được quản trị viên phê duyệt mà không cần đăng nhập. Kết quả có thể lọc theo từ khóa, tỉnh/thành và phường/xã, kèm giá thuê, địa chỉ và ảnh phòng. Việc chọn khu vực dùng danh mục đơn vị hành chính của hệ thống. |
| G2 | Xem chi tiết phòng | Khách xem đầy đủ thông tin một phòng trọ gồm giá thuê, diện tích, ảnh, tiện nghi và địa chỉ tòa nhà. Trang chi tiết hiển thị thêm tên và số điện thoại của chủ trọ để khách chủ động liên hệ trước khi quyết định thuê. |
| G3 | Tìm kiếm tòa nhà | Khách tra cứu danh sách các tòa nhà đã được duyệt theo tên, địa chỉ hoặc khu vực. Tòa nhà đang chờ duyệt, bị từ chối hoặc đã xóa không xuất hiện trong kết quả. |
| G4 | Xem chi tiết tòa nhà | Khách xem thông tin công khai của một tòa nhà cùng các phòng thuộc tòa nhà đó. Nếu tòa nhà chưa được duyệt hoặc không tồn tại, hệ thống trả về thông báo không tìm thấy. |
| G5 | Đăng ký tài khoản | Khách tự đăng ký tài khoản với vai trò người thuê hoặc chủ trọ bằng email; tài khoản quản trị viên do hệ thống cấp sẵn. Sau khi đăng ký, hệ thống gửi email xác thực có thời hạn 24 giờ, khách phải bấm liên kết xác thực mới sử dụng được tài khoản. Nếu chưa nhận được email, khách có thể yêu cầu gửi lại. |
| G6 | Đăng nhập | Người dùng đăng nhập bằng email và mật khẩu để nhận phiên làm việc gắn với vai trò của mình. Hệ thống tự làm mới phiên bằng mã làm mới và thu hồi toàn bộ phiên khi người dùng đổi mật khẩu. Tài khoản bị khóa vẫn đăng nhập được nhưng các chức năng nghiệp vụ bị chặn. |
| G7 | Quên và đặt lại mật khẩu | Người dùng nhập email để yêu cầu đặt lại mật khẩu; hệ thống luôn phản hồi giống nhau để không tiết lộ email có tồn tại hay không. Mã đặt lại gửi qua email chỉ dùng một lần và hết hạn sau 15 phút. Khi đặt lại thành công, mọi phiên đăng nhập cũ đều bị thu hồi. |

### Người thuê trọ (1.3.4)

| Mã | Use case | Mô tả |
|---|---|---|
| T1 | Đăng nhập, đăng xuất | Người thuê đăng nhập vào ứng dụng di động bằng tài khoản đã xác thực. Ứng dụng tự làm mới phiên khi mã truy cập hết hạn, và người thuê có thể đăng xuất để thu hồi phiên hiện tại. |
| T2 | Quản lý hồ sơ cá nhân | Người thuê xem và cập nhật thông tin cá nhân như họ tên, số điện thoại và tài khoản nhận tiền; số tài khoản luôn được che một phần khi hiển thị. Người thuê cũng có thể đổi mật khẩu, và sau khi đổi, các phiên đăng nhập khác bị thu hồi. |
| T3 | Tìm phòng và lưu phòng yêu thích | Người thuê tìm kiếm phòng trọ giống khách vãng lai và có thể lưu các phòng quan tâm vào danh sách yêu thích. Danh sách này chỉ giữ những phòng còn trống thuộc tòa nhà đã duyệt; người thuê có thể bỏ lưu bất cứ lúc nào. |
| T4 | Xem phòng đang thuê | Người thuê xem danh sách các phòng mình đang thuê hoặc đang ở chung, mỗi hợp đồng còn hiệu lực cho một mục. Đây là điểm vào để mở nhanh hợp đồng, hóa đơn, sự cố và hội thoại của từng phòng. |
| T5 | Xem hợp đồng | Người thuê xem các hợp đồng mà mình là người đứng tên hoặc là thành viên, gồm thời hạn, giá thuê, tiền cọc và danh sách người ở cùng. Người thuê chỉ có quyền xem, việc chỉnh sửa hợp đồng do chủ trọ thực hiện. |
| T6 | Xem hóa đơn và tiền điện nước | Người thuê xem các hóa đơn đã được chủ trọ phát hành, gồm tiền phòng, tiền điện, nước theo chỉ số ghi nhận và các khoản phụ thu. Hóa đơn chưa phát hành hoặc đã hủy không hiển thị cho người thuê. |
| T7 | Thanh toán hóa đơn bằng QR | Người thuê chọn hóa đơn cần trả, hệ thống tạo ý định thanh toán và sinh mã QR để người thuê quét bằng ứng dụng ngân hàng. Mỗi yêu cầu có khóa chống trùng để tránh tạo hai lần cho cùng một hóa đơn. Trước khi thanh toán, người thuê xem lại chi tiết hóa đơn. |
| T8 | Xem lịch sử thanh toán | Người thuê tra cứu danh sách các giao dịch thanh toán của mình, gồm hóa đơn tương ứng, số tiền, hình thức và trạng thái. Chức năng giúp người thuê đối chiếu những khoản đã trả. |
| T9 | Báo cáo sự cố | Người thuê gửi báo cáo sự cố như hỏng điện, nước hoặc hư hỏng thiết bị, gắn với hợp đồng đang hiệu lực của phòng mình ở. Báo cáo có thể đính kèm ảnh minh họa, ảnh được tải lên riêng tư và chỉ chủ trọ cùng người thuê xem được. |
| T10 | Theo dõi và hủy sự cố | Người thuê xem danh sách sự cố của mình và theo dõi trạng thái xử lý do chủ trọ cập nhật. Người thuê có thể hủy báo cáo khi sự cố chưa được giải quyết. |
| T11 | Trò chuyện | Người thuê nhắn tin trực tiếp hoặc theo nhóm với chủ trọ và những người ở cùng trong phòng. Ngoài tin nhắn văn bản, người thuê có thể đính kèm tệp, tìm lại nội dung trong một hội thoại và xem số tin chưa đọc. Người đã rời hợp đồng chỉ còn quyền đọc lại hội thoại. |
| T12 | Nhận và quản lý thông báo | Ứng dụng đăng ký mã thiết bị Android với máy chủ để người thuê nhận thông báo đẩy khi có thông tin mới liên quan đến tài khoản. Người thuê xem danh sách thông báo, đánh dấu đã đọc từng thông báo hoặc tất cả, và tùy chỉnh loại thông báo muốn nhận. Khi không dùng nữa, mã thiết bị có thể được hủy đăng ký. |
| T13 | Quản lý hồ sơ ở ghép | Người thuê tạo và cập nhật hồ sơ tìm bạn ở ghép gồm khoảng ngân sách, thói quen sinh hoạt và lựa chọn hiển thị hồ sơ. Khi người thuê tắt hiển thị, hồ sơ không xuất hiện trong kết quả tìm kiếm của người khác. |
| T14 | Tìm bạn ở ghép và gửi yêu cầu ghép | Người thuê duyệt danh sách hồ sơ đang hiển thị, xem chi tiết một hồ sơ và gửi yêu cầu ghép đôi tới người phù hợp. Bên nhận có thể chấp nhận hoặc từ chối, còn bên gửi có thể rút yêu cầu khi chưa được phản hồi. |

### Chủ trọ (1.3.3)

| Mã | Use case | Mô tả |
|---|---|---|
| L1 | Đăng nhập và quản lý hồ sơ | Chủ trọ đăng nhập vào web hoặc ứng dụng để sử dụng các chức năng quản lý. Chủ trọ cập nhật thông tin cá nhân và tài khoản nhận thanh toán của mình, và có thể đổi mật khẩu. |
| L2 | Quản lý tòa nhà | Chủ trọ đăng ký tòa nhà mới kèm ảnh minh chứng quyền sở hữu; tòa nhà ở trạng thái chờ duyệt cho đến khi quản trị viên phê duyệt. Chủ trọ có thể sửa thông tin, xem danh sách tòa nhà của mình và xóa tòa nhà khi cần. Chủ trọ chỉ thao tác được trên tòa nhà do chính mình sở hữu. |
| L3 | Thiết lập biểu giá | Chủ trọ cấu hình đơn giá điện, nước và các dịch vụ cho từng tòa nhà, thường là bước cuối khi tạo tòa nhà. Có thể lưu cả bộ đơn giá cùng lúc, sửa từng đơn giá hoặc ngừng áp dụng một đơn giá. |
| L4 | Cấu hình kỳ lập hóa đơn | Chủ trọ tạo và cập nhật thiết lập lập hóa đơn cho tòa nhà. Các thiết lập này được hệ thống dùng làm cơ sở khi tạo hóa đơn theo kỳ. |
| L5 | Quản lý phòng | Chủ trọ thêm phòng mới vào tòa nhà, cập nhật thông tin phòng và xóa phòng khi không còn cho thuê. Sau khi hoàn thiện thông tin, chủ trọ đánh dấu phòng sẵn sàng cho thuê để phòng hiển thị cho khách tìm kiếm. Phòng đang có hợp đồng hiệu lực không thể xóa hoặc đánh dấu lại. |
| L6 | Lập hợp đồng | Chủ trọ tạo hợp đồng nháp cho một phòng, chọn mẫu hợp đồng có sẵn và để hệ thống sinh bản nháp PDF từ dữ liệu hợp đồng, phòng và tòa nhà. Hai bên in bản này để ký tay trên giấy. Hợp đồng ở trạng thái nháp vẫn có thể chỉnh sửa. |
| L7 | Kích hoạt hợp đồng | Sau khi hai bên ký trên giấy, chủ trọ tải bản hợp đồng đã ký lên hệ thống. Chỉ khi có tệp đã ký, hợp đồng mới chuyển sang trạng thái hiệu lực và phòng được giữ cho người thuê. |
| L8 | Quản lý người thuê và thành viên hợp đồng | Chủ trọ xem danh sách người thuê theo từng hợp đồng và thông tin chi tiết của từng người. Chủ trọ thêm thành viên ở cùng, cập nhật số điện thoại và ghi nhận khi một thành viên rời đi. Người chưa có tài khoản vẫn được ghi nhận bằng họ tên và số điện thoại. |
| L9 | Xử lý trả phòng và hợp đồng bị khóa | Khi người thuê trả phòng, chủ trọ hoàn tất thủ tục trả phòng để kết thúc hợp đồng. Với hợp đồng bị tạm ngưng do khóa tài khoản, chủ trọ quyết định khôi phục hoặc chấm dứt hợp đồng. |
| L10 | Ghi chỉ số điện nước | Chủ trọ nhập chỉ số điện, nước của từng phòng theo kỳ, có thể nhập hàng loạt tối đa 200 chỉ số trong một lần. Kỳ đầu tiên cần có chỉ số gốc làm cơ sở tính. Ảnh công tơ có thể đính kèm làm bằng chứng nhưng không bắt buộc. |
| L11 | Lập và phát hành hóa đơn | Chủ trọ tạo hoặc tính lại các hóa đơn nháp theo tòa nhà và kỳ, chỉnh sửa khoản phụ thu khi hóa đơn còn ở trạng thái chờ. Sau đó chủ trọ phát hành hàng loạt để người thuê nhìn thấy hóa đơn. Hóa đơn có thể bị hủy kèm lý do, và lý do được lưu lại. |
| L12 | Ghi nhận thanh toán tiền mặt | Khi người thuê trả tiền mặt, chủ trọ ghi nhận khoản thanh toán này cho hóa đơn tương ứng. Mỗi lần ghi nhận có khóa chống trùng để không tính hai lần. |
| L13 | Đối soát giao dịch thanh toán | Chủ trọ xem danh sách giao dịch thanh toán thuộc các tòa nhà của mình, gồm cả khoản trả bằng QR và tiền mặt. Chức năng giúp chủ trọ đối chiếu dòng tiền với hóa đơn đã phát hành. |
| L14 | Xử lý sự cố | Chủ trọ xem hàng đợi các sự cố do người thuê báo cáo cho phòng của mình và xem chi tiết kèm ảnh. Chủ trọ cập nhật tiến độ xử lý theo thứ tự từ đang chờ, đang xử lý đến đã giải quyết. |
| L15 | Trò chuyện với người thuê | Chủ trọ nhắn tin với người thuê trong hội thoại gắn với hợp đồng của từng phòng. Chủ trọ có thể gửi nhắc nhở tự động theo mẫu có sẵn ngay trong hội thoại đó. |
| L16 | Nhận và quản lý thông báo | Chủ trọ nhận thông báo đẩy trên ứng dụng khi có thông tin mới liên quan đến tòa nhà và người thuê của mình. Chủ trọ xem danh sách thông báo, đánh dấu đã đọc và tùy chỉnh loại thông báo. Ứng dụng đăng ký mã thiết bị với máy chủ để nhận thông báo. |

### Quản trị viên (1.3.2)

| Mã | Use case | Mô tả |
|---|---|---|
| A1 | Đăng nhập và đổi mật khẩu | Quản trị viên sử dụng tài khoản được cấp sẵn để đăng nhập, vì vai trò này không tự đăng ký được. Quản trị viên có thể đổi mật khẩu, và các phiên cũ sẽ bị thu hồi sau khi đổi. |
| A2 | Duyệt bất động sản | Quản trị viên xem hàng đợi các tòa nhà do chủ trọ gửi lên và mở chi tiết để kiểm tra thông tin, ảnh minh chứng sở hữu. Sau đó quản trị viên phê duyệt để tòa nhà hiển thị công khai, hoặc từ chối và bắt buộc ghi chú lý do để chủ trọ biết cần bổ sung gì. |
| A3 | Quản lý tài khoản | Quản trị viên xem danh sách và thông tin chi tiết người dùng, chỉnh sửa thông tin cơ bản của họ. Quản trị viên có thể khóa hoặc mở khóa tài khoản, hoặc xóa mềm tài khoản khi cần; tài khoản bị khóa vẫn đăng nhập được nhưng không dùng được các chức năng nghiệp vụ. |
| A4 | Xem nhật ký kiểm toán | Quản trị viên tra cứu nhật ký ghi lại các thao tác quan trọng trong hệ thống và xem chi tiết từng bản ghi. Nhật ký chỉ ghi thêm, không thể sửa hay xóa, nên đảm bảo khả năng truy vết khi có tranh chấp. |
| A5 | Xem thống kê hệ thống | Quản trị viên xem các số liệu tổng hợp của toàn hệ thống theo một khoảng thời gian chọn trước. Thông tin này giúp theo dõi tình hình vận hành chung. |
| A6 | Nhận thông báo hệ thống | Quản trị viên nhận và xem các thông báo hệ thống liên quan đến hoạt động quản trị, đánh dấu đã đọc từng thông báo hoặc tất cả. |
