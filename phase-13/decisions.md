# Phase 13 — Quyết định

Nguồn: tài liệu "Nghiệp vụ khóa tài khoản" (Thu Phương, 25/11/2026) và buổi review với PM ngày 26/11/2026. ID tiếp nối Phase 12 (D100).

## D101 — Khóa landlord không thay đổi hợp đồng

- **Bối cảnh:** Saga P9-06/P9-07 chuyển mọi hợp đồng `active` của landlord bị khóa sang `suspended`, quá 7 ngày tự `terminated`. Hợp đồng ký trên giấy ngoài đời nên app không có quyền chấm dứt; khóa nhầm mà xử lý quá 7 ngày thì người thuê mất hợp đồng trên app dù vẫn đang ở. Room hub của tenant cũng mất phòng vì chỉ lấy hợp đồng `active`.
- **Quyết định:**
  - Khi landlord bị khóa, Tenancy **không đổi trạng thái hợp đồng**. Không còn trạng thái `suspended`, lock cycle, hạn 7 ngày, scheduler, API chọn khôi phục/chấm dứt và các mã lỗi đi kèm.
  - Sau khi mở khóa, landlord tự cập nhật bằng các thao tác đã có (cập nhật hợp đồng, kết thúc hợp đồng, sinh hóa đơn, hủy hóa đơn, đánh dấu đã thu).
  - Hợp đồng đang `suspended` trong DB được đưa về `active` bằng migration. Không xử lý lại các hợp đồng đã bị chấm dứt trước đây.
- **Thay thế:** saga khóa landlord của P9-06/P9-07, màn chọn khôi phục/chấm dứt của P11-13, phần thông báo tạm ngưng/cần quyết định/khôi phục/chấm dứt do khóa của P12-03 và P12-D97.
- **Issues:** P13-01, P13-02.

## D102 — Tài khoản bị khóa không thanh toán qua app

- **Bối cảnh:** P12-D100 cho phép tài khoản bị khóa thanh toán hóa đơn, nhưng Rentify chưa có luồng thanh toán online (P6, D39) và VNPAY mới là bản thiết kế.
- **Quyết định:**
  - Giữ phần **chỉ đọc** của P12-D100 (hồ sơ, phòng, hợp đồng, hóa đơn của chính mình).
  - Bỏ phần **thanh toán** của P12-D100: tài khoản bị khóa không có thao tác thanh toán nào trên app. Khi có Payment Service sẽ chốt lại riêng.
  - Giữ nguyên cơ chế hiện tại: khóa có hiệu lực trễ tối đa 15 phút (TTL access token), không thu hồi phiên khi khóa.
- **Issues:** P13-03.

## D103 — Hiển thị khi một bên bị khóa

- Tòa nhà của landlord bị khóa **ẩn khỏi tìm kiếm công khai**; mở khóa thì tự hiện lại. Không đổi `BuildingStatus`.
- Mã QR / thông tin chuyển khoản của landlord bị khóa **ẩn** trên mọi hóa đơn. App **không hiển thị thêm hướng dẫn thanh toán** nào: hai bên đã có thông tin liên lạc trên hợp đồng và tự liên hệ ngoài app nếu cần.
- Trong chat, người bị khóa hiện nhãn **"Tài khoản đã bị khóa"**; người khác vẫn xem lịch sử, người bị khóa không gửi tin mới. Không gửi thông báo cho bên còn lại khi một người bị khóa hoặc mở khóa.
- **Issues:** P13-04, P13-05, P13-06.

## D104 — Hóa đơn có trạng thái "Đã thu"

- **Bối cảnh:** `InvoiceStatus` hiện chỉ có `pending`, `issued`, `void`; landlord không ghi nhận được tiền đã thu. Kênh `cash`/thu ngoài app là kênh chính theo D39.
- **Quyết định:** thêm trạng thái `paid`. Landlord **đánh dấu tay** hóa đơn `issued` là đã thu. Không có thanh toán online, không có `due_date`/quá hạn, không chia tiền theo từng người (D4/D22, D39 giữ nguyên).
- **Thay đổi phạm vi** so với P6-D64/MVP hóa đơn: PM đã duyệt ngày 26/11/2026.
- **Issues:** P13-07.

## D105 — Hợp đồng quá ngày kết thúc

- Không thêm cron, không thêm trạng thái "Hết hạn, chờ cập nhật", không tự chuyển `EXPIRED`. Hợp đồng quá ngày kết thúc vẫn `active` cho tới khi landlord kết thúc hoặc cập nhật.
- Áp dụng chung cho mọi hợp đồng, không riêng trường hợp bị khóa.

## D106 — Tenant bị khóa

- Hợp đồng, hóa đơn của phòng chạy bình thường; landlord vẫn quản lý như cũ.
- Tenant bị khóa không tự liên kết với hợp đồng mới; mở khóa thì hệ thống tự liên kết lại (hành vi hiện có của Tenancy, giữ nguyên).
- Ghép bạn: hồ sơ bị ẩn khỏi tìm kiếm; lời mời ghép đôi **không bị hủy**, nhưng không gửi mới, không chấp nhận/từ chối được khi một bên đang bị khóa.
- Không thông báo cho landlord; nhãn khóa trong chat (D103) là đủ.
- **Issues:** P13-08.

## D108 — Điện/nước khoán theo đầu người

- Chỉ bắt buộc chỉ số với điện/nước tính theo đồng hồ. Loại cấu hình `per_head` không cần chỉ số.
- Điện/nước `per_head` tính theo tỉ lệ ngày ở như các phí `per_head` khác. Điện/nước theo đồng hồ giữ nguyên cách tính theo số tiêu thụ.
- **Issues:** P13-12.

## D107 — Để sau / ngoài phạm vi Phase 13

- **Báo cáo vi phạm và khiếu nại** (hàng chờ báo cáo, form khiếu nại, xử lý của admin): ghi thành issue Deferred P13-11, cần PM duyệt phạm vi trước khi làm. Trong lúc chờ, người bị khóa liên hệ admin ngoài app.
- Email báo khóa/mở khóa (community đã có module email, làm sau nếu cần).
- Đổi người đại diện phòng khi người đại diện bị khóa.
- Bot nhắc và sự cố (issue report) khi landlord bị khóa: giữ nguyên.
- Các mục trong tài liệu gốc không tồn tại trong hệ thống: hóa đơn định kỳ tự sinh, quá hạn/nhắc hạn, trả từng phần theo người, yêu cầu thuê, hẹn xem phòng, "chế độ khóa".
