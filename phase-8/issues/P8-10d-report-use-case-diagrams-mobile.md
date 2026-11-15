# P8-10d — Toàn bộ sơ đồ use case hệ thống, dịch vụ thông báo đẩy và vận hành di động

**Epic:** [P8-10](P8-10-final-report-package.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** `tphuongin` (Nguyễn Thị Thu Phương)  
**Người review:** `ThaiBao11125` (Lead Report Author) / PM  
**Ước lượng:** 2 points · 8 giờ (**tối đa 3 points và khoảng 15 file mỗi PR**)  
**Phụ thuộc:** P8-01, P8-09  
**Repo / branch:** `docs/` · `docs/p8-10d-report-use-case-mobile`  
**Issue:** `docs#TBD`

> **Đọc trước khi thực hiện:** Đọc `Report/AGENTS.md`, `Report/khungbaocao.md` và `Report/phancong.md`. Mọi sơ đồ ca sử dụng use case phải bám sát 4 tác nhân chính (khách vãng lai, người thuê, chủ trọ, quản trị viên) và các chức năng thực tế của hệ thống. Ảnh chụp màn hình ứng dụng di động phải rõ nét, đúng tỷ lệ và che thông tin nhạy cảm.

## Mục tiêu

Xây dựng và bàn giao đầy đủ 5 sơ đồ ca sử dụng (Use Case Diagram) cho toàn bộ hệ thống Rentify, soạn thảo nội dung kỹ thuật mục 4.6 về dịch vụ thông báo đẩy thời gian thực với Firebase Cloud Messaging, cung cấp trọn bộ ảnh chụp thực tế màn hình ứng dụng di động Android cho phân hệ người thuê trọ (mục 2.4), cùng tài liệu hướng dẫn cài đặt và vận hành ứng dụng di động bằng Kotlin Jetpack Compose để người phụ trách chính báo cáo (`ThaiBao11125`) tích hợp vào mục 1.3, mục 2.4, mục 4.6 và mục 5.6 của báo cáo đồ án.

## Quyết định áp dụng

- 5 sơ đồ use case phải đồng nhất quy ước ký hiệu: actor, ca sử dụng hình oval, quan hệ include, extend và generalization theo chuẩn UML.
- Phân định rõ phạm vi quyền hạn của từng tác nhân theo đúng thiết kế hệ thống đã thống nhất.
- Trình bày chi tiết cơ chế tích hợp Firebase Cloud Messaging (FCM), lưu trữ token thiết bị và quy trình bắn thông báo đẩy đến ứng dụng di động.
- Chụp ảnh màn hình ứng dụng di động Android thật từ bản build mới nhất của repo mobile, thể hiện đầy đủ các chức năng dành cho người thuê trọ.
- Bàn giao dưới dạng sơ đồ nét cao (mermaid / PNG), tệp ảnh chụp màn hình chất lượng cao và tài liệu hướng dẫn biên dịch rõ ràng.

## Chi tiết các nội dung cần bàn giao

| Mã mục | Tên mục trong khung báo cáo | Nội dung kỹ thuật và sơ đồ cần bàn giao |
|---|---|---|
| 1.3.1 | Sơ đồ use case tổng quát | Vẽ sơ đồ use case tổng quát toàn bộ hệ thống Rentify thể hiện mối quan hệ giữa 4 tác nhân: khách vãng lai, người thuê, chủ trọ và quản trị viên |
| 1.3.2 | Sơ đồ use case phân hệ quản trị viên | Vẽ sơ đồ use case chi tiết toàn bộ các chức năng của quản trị viên hệ thống (duyệt bất động sản, quản lý tài khoản, nhật ký) |
| 1.3.3 | Sơ đồ use case phân hệ chủ trọ | Vẽ sơ đồ use case chi tiết toàn bộ các chức năng vận hành của chủ trọ trên hệ thống (tòa nhà, phòng, hợp đồng, biểu giá, chỉ số, hóa đơn, sự cố, thông báo) |
| 1.3.4 | Sơ đồ use case phân hệ người thuê trọ | Vẽ sơ đồ use case chi tiết toàn bộ các chức năng của người thuê trọ trên ứng dụng di động (hợp đồng, hóa đơn, thanh toán VietQR, báo cáo sự cố, trò chuyện, tìm bạn ở ghép) |
| 1.3.5 | Sơ đồ use case phân hệ khách vãng lai | Vẽ sơ đồ use case chi tiết các tính năng khám phá, tìm kiếm phòng trọ và xem bài đăng tìm bạn ở ghép dành cho khách vãng lai |
| 2.4 | Ảnh minh họa phân hệ người thuê trọ | Cung cấp đầy đủ các ảnh chụp màn hình ứng dụng di động Android từ mục 2.4.1 đến 2.4.11: xem phòng, tra cứu hợp đồng, theo dõi điện nước, hóa đơn, mã VietQR, báo cáo sự cố, trò chuyện, tạo hồ sơ và ghép đôi ở ghép |
| 4.6 | Dịch vụ thông báo đẩy thời gian thực với Firebase Cloud Messaging | Trình bày tích hợp dịch vụ Firebase Cloud Messaging, lưu trữ mã thiết bị và quy trình gửi thông báo đẩy đến di động |
| 5.6 | Cài đặt và vận hành ứng dụng di động Android | Cung cấp tài liệu hướng dẫn đồng bộ thư viện Gradle, cấu hình biến kết nối API, cấu hình google-services.json cho Firebase và các bước xuất gói cài đặt APK cho Android |

## Tham chiếu mã nguồn và thiết kế

- Dự án ứng dụng di động Android: repo mobile bằng Kotlin Jetpack Compose (`app-tenant`, `app-landlord`, `core-ui`).
- Bản thiết kế giao diện Figma của hệ thống Rentify.
- Cấu hình Firebase Cloud Messaging trong app Android và tích hợp backend trong `community-service`.

## Các bước triển khai

### Bước 1 — Thiết kế sơ đồ use case tổng quát và các tác nhân (Mục 1.3.1)
- **Cách làm:** Vẽ sơ đồ ca sử dụng tổng quát thể hiện 4 tác nhân chính và các gói chức năng tương ứng.
- **Kiểm tra bước:** Phân định rõ ràng phạm vi, không bỏ sót tác nhân nào.

### Bước 2 — Thiết kế 4 sơ đồ use case chi tiết từng phân hệ (Mục 1.3.2 đến 1.3.5)
- **Cách làm:** Vẽ chi tiết ca sử dụng cho Quản trị viên (1.3.2), Chủ trọ (1.3.3), Người thuê trọ (1.3.4) và Khách vãng lai (1.3.5).
- **Kiểm tra bước:** Mỗi sơ đồ thể hiện đúng các mối quan hệ `<<include>>`, `<<extend>>` và phân quyền.

### Bước 3 — Chụp ảnh màn hình giao diện ứng dụng di động Android (Mục 2.4)
- **Cách làm:** Khởi chạy ứng dụng Android trên máy ảo hoặc thiết bị thật, chụp các màn hình chính theo danh mục từ 2.4.1 đến 2.4.11; đặt tên tệp ảnh rõ ràng theo mã mục.
- **Kiểm tra bước:** Hình ảnh sắc nét, giao diện hiển thị dữ liệu mẫu hợp lý, không bị vỡ giao diện.

### Bước 4 — Soạn thảo nội dung dịch vụ thông báo đẩy FCM (Mục 4.6)
- **Cách làm:** Trình bày kiến trúc nhận diện mã thiết bị token, cách đăng ký token lên máy chủ và quy trình tiếp nhận thông báo đẩy nền/tiền cảnh trên Android.
- **Kiểm tra bước:** Thông số cấu hình khớp với tệp google-services.json và logic xử lý thông báo của ứng dụng di động.

### Bước 5 — Soạn thảo hướng dẫn cài đặt và biên dịch Android (Mục 5.6)
- **Cách làm:** Hướng dẫn phiên bản Android Studio, JDK, Gradle, cách thêm tệp cấu hình Firebase và cách xuất file APK.
- **Kiểm tra bước:** Hướng dẫn có thể tái hiện để build ra file APK thành công.

### Bước 6 — Bàn giao cho Lead Author (`ThaiBao11125`)
- **Cách làm:** Bàn giao 5 tệp sơ đồ use case, bộ ảnh chụp màn hình Android, tài liệu mục 4.6 và tài liệu hướng dẫn cài đặt mục 5.6.
- **Kiểm tra bước:** `ThaiBao11125` xác nhận nhận đủ 5 sơ đồ, đủ ảnh màn hình mục 2.4 và nội dung các mục 4.6, 5.6.

## Ngoài phạm vi

- Viết các phần mô tả chức năng chi tiết dạng văn bản (thuộc trách nhiệm của Lead Author).
- Sơ đồ kiến trúc (P8-10a), sơ đồ lớp (P8-10b), sơ đồ tuần tự (P8-10c).

## Blocker

- Không có. Nếu cần dữ liệu mẫu cho ứng dụng di động để chụp ảnh thì phối hợp cùng backend để seed dữ liệu.

## Acceptance

- [ ] Đủ 5 sơ đồ use case (1.3.1 đến 1.3.5) chuẩn UML, ký hiệu và đường nét sắc sảo, nhất quán.
- [ ] Đủ bộ ảnh chụp màn hình ứng dụng di động Android cho các chức năng phân hệ người thuê trọ (2.4.1 đến 2.4.11).
- [ ] Soạn thảo đầy đủ nội dung kỹ thuật mục 4.6 về dịch vụ thông báo đẩy Firebase Cloud Messaging.
- [ ] Mục 5.6 hướng dẫn biên dịch và cài đặt ứng dụng Android đầy đủ, dễ thực hiện.
- [ ] Bàn giao toàn bộ sản phẩm đúng hạn cho `ThaiBao11125`.

## Definition of Done

- [ ] `ThaiBao11125` và PM duyệt chất lượng 5 sơ đồ use case, nội dung mục 4.6 và bộ ảnh giao diện di động.
- [ ] Toàn bộ nội dung được tích hợp vào tài liệu báo cáo của dự án.
