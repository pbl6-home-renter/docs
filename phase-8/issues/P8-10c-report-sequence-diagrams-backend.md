# P8-10c — Toàn bộ sơ đồ tuần tự hệ thống và tài liệu vận hành backend

**Epic:** [P8-10](P8-10-final-report-package.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** `huynhtiennhat0403` (Huỳnh Tiến Nhật)  
**Người review:** `baoduong17` / `ThaiBao11125` (Lead Report Author)  
**Ước lượng:** 2 points · 8 giờ (**tối đa 3 points và khoảng 15 file mỗi PR**)  
**Phụ thuộc:** P8-01, P8-06  
**Repo / branch:** `docs/` · `docs/p8-10c-report-sequence-diagrams-be`  
**Issue:** `docs#TBD`

> **Đọc trước khi thực hiện:** Đọc `Report/AGENTS.md`, `Report/khungbaocao.md` và `Report/phancong.md`. Mọi sơ đồ tuần tự phải thể hiện chuẩn xác các đường đời (lifelines), lời gọi API đồng bộ, xử lý bất đồng bộ qua RabbitMQ Outbox/Inbox và tương tác cơ sở dữ liệu.

## Mục tiêu

Xây dựng và bàn giao đầy đủ 7 sơ đồ tuần tự (Sequence Diagram) chuẩn UML thể hiện toàn diện các luồng nghiệp vụ cốt lõi của hệ thống Rentify, cùng tài liệu hướng dẫn cài đặt và vận hành các dịch vụ máy chủ NestJS để người phụ trách chính báo cáo (`ThaiBao11125`) tích hợp vào mục 1.5 và mục 5.4 của báo cáo đồ án.

## Quyết định áp dụng

- 7 sơ đồ tuần tự phải đồng nhất phong cách thiết kế, quy ước đặt tên actor, service, gateway, queue và database.
- Mô tả chính xác cơ chế xác thực JWT, tương tác giữa API Gateway và các vi dịch vụ, việc phát sinh sự kiện qua Transactional Outbox và tiêu thụ sự kiện ở Transactional Inbox.
- Tài liệu vận hành backend hướng dẫn đầy đủ từ việc chuẩn bị môi trường, cài đặt node_modules, biến môi trường cục bộ và lệnh chạy dev.
- Bàn giao dưới dạng sơ đồ nét cao (mermaid / PNG) kèm mô tả ngắn gọn từng bước cho mỗi sơ đồ.

## Chi tiết các nội dung cần bàn giao

| Mã mục | Tên mục trong khung báo cáo | Nội dung kỹ thuật và sơ đồ cần bàn giao |
|---|---|---|
| 1.5.1 | Quy trình đăng ký, xác thực và phân quyền tài khoản | Vẽ sơ đồ tuần tự luồng cấp phát mã truy cập (access token), mã làm mới (refresh token), xác thực thư điện tử và kiểm tra quyền tại API Gateway |
| 1.5.2 | Quy trình tạo bất động sản, tải lên giấy tờ sở hữu và phê duyệt | Vẽ sơ đồ tuần tự luồng chủ trọ tải lên giấy tờ chứng minh sở hữu và quản trị viên kiểm tra phê duyệt |
| 1.5.3 | Quy trình lập hợp đồng thuê và tải lên hợp đồng ký tay | Vẽ sơ đồ tuần tự quy trình lập hợp đồng nháp, xuất bản mẫu, tải ảnh hợp đồng ký tay làm căn cứ pháp lý và kích hoạt hợp đồng |
| 1.5.4 | Quy trình chốt chỉ số điện nước và tự động sinh hóa đơn định kỳ | Vẽ sơ đồ tuần tự luồng ghi nhận chỉ số điện nước định kỳ kèm ảnh công tơ, áp dụng biểu giá và thuật toán tự động sinh hóa đơn |
| 1.5.5 | Quy trình thanh toán hóa đơn qua VietQR và xác nhận thanh toán | Vẽ sơ đồ tuần tự luồng sinh mã thanh toán VietQR động, người thuê quét mã chuyển khoản và đối soát xác nhận giao dịch |
| 1.5.6 | Quy trình trò chuyện trực tuyến và tiếp nhận báo cáo sự cố | Vẽ sơ đồ tuần tự luồng truyền nhận tin nhắn qua Socket.io và luồng tiếp nhận báo cáo xử lý sự cố phòng trọ |
| 1.5.7 | Quy trình tìm kiếm và kết nối bạn ở ghép | Vẽ sơ đồ tuần tự luồng tạo hồ sơ tìm bạn ở ghép, tìm kiếm, gửi yêu cầu ghép đôi và tự động mở phòng trò chuyện trực tiếp khi được đồng ý |
| 5.4 | Cài đặt và vận hành các dịch vụ phía máy chủ | Cung cấp tài liệu chi tiết các bước cài đặt gói phụ thuộc, thiết lập kết nối và khởi chạy mã nguồn dịch vụ định danh, thuê trọ và cộng đồng |

## Tham chiếu mã nguồn và luồng nghiệp vụ

- Controller, Service, Guard trong `api-gateway/`, `Identity-Service/`, `Tenancy-Service/`, `community-service/`.
- Module hóa đơn và chỉ số: `Tenancy-Service/src/modules/billing/`, `invoice/`, `meter-reading/`.
- Tài liệu quy trình trong `docs/`.

## Các bước triển khai

### Bước 1 — Thiết kế các sơ đồ tuần tự xác thực, bất động sản và hợp đồng (Mục 1.5.1, 1.5.2, 1.5.3)
- **Cách làm:** Vẽ sơ đồ tuần tự luồng đăng ký/đăng nhập JWT, luồng duyệt giấy tờ bất động sản và luồng kích hoạt hợp đồng kèm ảnh chữ ký tay.
- **Kiểm tra bước:** Thể hiện rõ Client, API Gateway, Identity-Service, Tenancy-Service, DB và tệp lưu trữ.

### Bước 2 — Thiết kế các sơ đồ tuần tự chỉ số, hóa đơn và VietQR (Mục 1.5.4, 1.5.5)
- **Cách làm:** Vẽ sơ đồ ghi nhận chỉ số điện nước kèm ảnh, tính toán hóa đơn theo biểu giá (cố định, bậc thang, khoán đầu người) và luồng sinh mã VietQR động cùng đối soát.
- **Kiểm tra bước:** Luồng tính toán và sinh hóa đơn khớp với implementation trong Tenancy-Service.

### Bước 3 — Thiết kế các sơ đồ tuần tự trò chuyện, sự cố và tìm bạn ở ghép (Mục 1.5.6, 1.5.7)
- **Cách làm:** Vẽ luồng Socket.io gửi nhận tin nhắn thời gian thực, luồng tạo sự cố kèm ảnh, và luồng kết nối hồ sơ ghép đôi bạn ở ghép.
- **Kiểm tra bước:** Thể hiện rõ các sự kiện Socket.io và luồng tự động tạo cuộc trò chuyện khi ghép đôi thành công.

### Bước 4 — Soạn thảo tài liệu cài đặt vận hành Backend (Mục 5.4)
- **Cách làm:** Hướng dẫn cụ thể từng bước từ `npm ci`, cấu hình `.env`, chạy script khởi tạo đến `npm run start:dev` cho từng vi dịch vụ.
- **Kiểm tra bước:** Các lệnh chạy đã được kiểm chứng chạy thông suốt trên máy local.

### Bước 5 — Bàn giao cho Lead Author (`ThaiBao11125`)
- **Cách làm:** Bàn giao 7 tệp sơ đồ tuần tự và tài liệu markdown hướng dẫn vận hành backend.
- **Kiểm tra bước:** `ThaiBao11125` xác nhận nhận đủ 7 sơ đồ tuần tự và nội dung mục 5.4.

## Ngoài phạm vi

- Viết các phần mô tả chức năng chi tiết hoặc kịch bản kiểm thử.
- Sơ đồ kiến trúc (P8-10a), sơ đồ lớp (P8-10b), sơ đồ use case (P8-10d).

## Blocker

- Không có. Nếu cần làm rõ luồng Socket.io hay duyệt bất động sản thì trao đổi với `baoduong17` và `leminhkhai345`.

## Acceptance

- [ ] Đủ 7 sơ đồ tuần tự (1.5.1 đến 1.5.7) chuẩn UML, đúng thông điệp, rõ ràng và không chồng chéo.
- [ ] Mục 5.4 hướng dẫn đầy đủ cách chạy cả 3 vi dịch vụ phía máy chủ trên môi trường phát triển.
- [ ] Bàn giao toàn bộ tư liệu đúng hạn cho `ThaiBao11125`.

## Definition of Done

- [ ] `baoduong17` và `ThaiBao11125` duyệt chất lượng 7 sơ đồ tuần tự.
- [ ] Toàn bộ nội dung được tích hợp vào tài liệu báo cáo của dự án.
