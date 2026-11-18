# P8-10a — Sơ đồ kiến trúc vi dịch vụ và tài liệu hạ tầng triển khai

**Epic:** [P8-10](P8-10-final-report-package.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** `baoduong17` (Dương Văn Chí Bảo)  
**Người review:** `ThaiBao11125` (Lead Report Author) / PM  
**Ước lượng:** 2 points · 8 giờ (**tối đa 3 points và khoảng 15 file mỗi PR**)  
**Phụ thuộc:** P8-01, P8-09  
**Repo / branch:** `docs/` · `docs/p8-10a-report-architecture-infra`  
**Issue:** `docs#TBD`

> **Đọc trước khi thực hiện:** `Report/AGENTS.md`, `Report/khungbaocao.md` và `Report/phancong.md` chưa có trong checkout `docs/` hiện tại; đối chiếu trực tiếp mã nguồn và cấu hình `infra/`. Mọi sơ đồ kỹ thuật và thông số hạ tầng phải khớp với trạng thái thực tế; phân biệt thiết kế với thành phần đã triển khai.

**Tư liệu đã soạn:** [Report/P8-10a-architecture-infrastructure.md](../../Report/P8-10a-architecture-infrastructure.md) và hai tệp Mermaid độc lập trong `Report/diagrams/`. Chưa có kết quả chạy Compose trên EC2 hoặc xác nhận của Lead Author/PM.

## Mục tiêu

Xây dựng và bàn giao sơ đồ kiến trúc vi dịch vụ tổng thể, mô hình hướng sự kiện qua RabbitMQ, cấu hình mạng Caddy, mô hình PostgreSQL theo service, bảng biến môi trường và hai tệp Docker Compose để người phụ trách chính báo cáo (`ThaiBao11125`) tích hợp vào mục 1.2, các mục từ 4.1 đến 4.5 của Chương 4, mục 5.2 và mục 5.7 của báo cáo đồ án.

## Quyết định áp dụng

- Sơ đồ có 3 service đã có mã nguồn (`Identity-Service`, `Tenancy-Service`, `community-service`) và thêm `Payment Service` ở trạng thái **thiết kế** theo yêu cầu ngày 16/11/2026. Gateway có route Payment; chưa có mã nguồn Payment và cấu hình Compose của Payment đang bị comment.
- Mô hình hướng sự kiện hiện có dùng RabbitMQ và mẫu Transactional Outbox/Inbox ở các service đã có mã nguồn. Payment chưa có event contract, queue hay database để xác nhận.
- Caddy đang làm reverse proxy HTTP theo cổng; Caddyfile hiện không có domain/TLS, nên chưa thể ghi là đã cấp chứng chỉ SSL tự động.
- Bàn giao dưới dạng sơ đồ chuẩn nét cao (mermaid / PNG) kèm tài liệu thuyết minh kỹ thuật ngắn gọn, đúng các đề mục trong khung báo cáo.

## Chi tiết các nội dung cần bàn giao

| Mã mục | Tên mục trong khung báo cáo | Nội dung kỹ thuật và sơ đồ cần bàn giao |
|---|---|---|
| 1.2 | Sơ đồ thiết kế kiến trúc hệ thống | Vẽ và phân tích sơ đồ kiến trúc vi dịch vụ tổng thể từ 1.2.1 đến 1.2.4: cổng điều phối API Gateway, kiến trúc hướng sự kiện với RabbitMQ áp dụng mẫu hộp thư đi và hộp thư đến, mô hình cơ sở dữ liệu riêng biệt PostgreSQL, kiến trúc ứng dụng web React và ứng dụng di động Android |
| 4.1 | Hạ tầng máy chủ và phần cứng | Thông số cấu hình phần cứng máy chủ, tài nguyên CPU và bộ nhớ phân bổ cho các dịch vụ |
| 4.2 | Môi trường mạng và cổng điều phối API Gateway với Caddy | Sơ đồ mạng biên/nội bộ, reverse proxy và trạng thái TLS thực tế; Caddyfile hiện chỉ có HTTP |
| 4.3 | Hệ quản trị cơ sở dữ liệu PostgreSQL theo từng dịch vụ | Các kết nối PostgreSQL theo service, giới hạn bằng chứng về instance/role thực tế; Payment chỉ là thiết kế |
| 4.4 | Hệ thống hàng đợi thông điệp RabbitMQ | Cấu hình máy chủ RabbitMQ, các sàn giao dịch (exchanges), danh sách hàng đợi (queues), khóa định tuyến (routing keys) và cơ chế xử lý thông điệp bền bỉ |
| 4.5 | Dịch vụ lưu trữ tệp tin và đa phương tiện | Giải pháp lưu trữ hình ảnh hợp đồng ký tay, ảnh công tơ điện nước và giấy tờ pháp lý bất động sản |
| 5.2 | Cấu hình biến môi trường của hệ thống | Bảng tổng hợp đầy đủ các biến môi trường cấu hình cho API Gateway, các vi dịch vụ và ứng dụng khách |
| 5.7 | Đóng gói ứng dụng và tự động hóa triển khai bằng Docker Compose | Hai tệp Compose edge/internal, script kéo image và hướng dẫn khởi chạy các service hiện có; Payment chưa khởi chạy được |

## Tham chiếu mã nguồn và hạ tầng

- `infra/docker-compose.edge.yml` và `infra/docker-compose.internal.yml` (không có `docker-compose.yml` ở thư mục gốc workspace).
- Cấu hình Caddyfile trong hạ tầng mạng.
- Cấu hình RabbitMQ module, Outbox/Inbox relay trong `Tenancy-Service/` và `community-service/`.
- Cấu hình định tuyến và guard trong `api-gateway/`.

## Các bước triển khai

### Bước 1 — Thiết kế sơ đồ kiến trúc vi dịch vụ (Mục 1.2)
- **Cách làm:** Vẽ sơ đồ kiến trúc tổng thể bằng Mermaid thể hiện rõ Client (React, Android), Caddy, API Gateway, 3 service có mã nguồn, Payment ở trạng thái thiết kế, RabbitMQ, PostgreSQL và R2.
- **Kiểm tra bước:** Sơ đồ thể hiện đúng 4 tầng, phân định rõ ranh giới service và cơ sở dữ liệu riêng biệt.

### Bước 2 — Tổng hợp tài liệu hạ tầng Chương 4 (Mục 4.1 đến 4.5)
- **Cách làm:** Soạn thảo nội dung kỹ thuật từ 4.1 đến 4.5, ghi rõ thông số máy chủ, thiết lập Caddy, cấu hình RabbitMQ (tên exchange, queue) và cơ chế lưu trữ tệp tin.
- **Kiểm tra bước:** Các thông số trùng khớp với cấu hình thực tế đang chạy trên môi trường phát triển và máy chủ thử nghiệm.

### Bước 3 — Cung cấp cấu hình biến môi trường và Docker Compose (Mục 5.2, 5.7)
- **Cách làm:** Lập bảng tra cứu biến môi trường theo từng service; kiểm tra lại câu lệnh khởi chạy `docker compose up -d` và quy trình build image.
- **Kiểm tra bước:** Lệnh khởi chạy Docker Compose hoạt động ổn định từ trạng thái môi trường sạch.

### Bước 4 — Bàn giao cho Lead Author (`ThaiBao11125`)
- **Cách làm:** Bàn giao tài liệu markdown và tệp sơ đồ để tích hợp vào `Report/01_chuong1.md`, `Report/04_chuong4.md` và `Report/05_chuong5.md`.
- **Kiểm tra bước:** `ThaiBao11125` xác nhận nhận đủ sơ đồ và thông số, không còn vướng mắc kỹ thuật.

## Ngoài phạm vi

- Viết các phần mô tả chức năng chi tiết hoặc kịch bản kiểm thử (thuộc trách nhiệm của Lead Author).
- Sơ đồ use case, sơ đồ lớp, sơ đồ tuần tự và mục 4.6 về Firebase Cloud Messaging (thuộc các sub-issue P8-10b, P8-10c, P8-10d).

## Blocker

- Không có. Nếu thiếu thông số môi trường của service nào thì trao đổi trực tiếp với owner service đó.

## Acceptance

- [x] Tư liệu sơ đồ thể hiện Gateway, 3 service có mã nguồn, Payment ở trạng thái thiết kế, RabbitMQ, database theo service và 2 nền tảng ứng dụng khách.
- [ ] Các mục hạ tầng phụ trách (4.1 đến 4.5) có thông số cấu hình cụ thể và chuẩn xác.
- [ ] Bảng biến môi trường (5.2) và tệp hướng dẫn Docker Compose (5.7) chạy thử thành công.
- [ ] Toàn bộ tư liệu được bàn giao đúng hạn cho `ThaiBao11125`.

## Definition of Done

- [ ] `ThaiBao11125` và PM phê duyệt chất lượng sơ đồ và nội dung kỹ thuật.
- [ ] Tệp sơ đồ và nội dung được lưu trữ trong thư mục tài liệu báo cáo của dự án.
