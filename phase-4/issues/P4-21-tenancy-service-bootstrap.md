# P4-21 — Bootstrap `tenancy-service` theo các domain đã được phê duyệt

**Trạng thái:** 🟡 Open  
**Người phụ trách:** BE member  
**Người review:** BE Lead, PM  
**Ước lượng:** 8 points · 18–24 giờ  
**Độ ưu tiên:** High / Blocker cho các task tenancy tiếp theo

## Bối cảnh

`tenancy-service` là service nghiệp vụ lớn, được thiết kế để gộp nhóm property và billing nhằm giữ các luồng liên quan đến phòng, hợp đồng, chốt số và hóa đơn trong cùng local transaction. Theo microservice architecture và `database-design.md`, service này không chỉ có một domain `tenancy` duy nhất chứa toàn bộ code.

Trong cùng một service, mỗi nhóm bảng/nghiệp vụ phải được tổ chức thành một module/domain riêng. Các module chia sẻ database và transaction boundary của `tenancy-service`, nhưng không được gom toàn bộ entity, handler và rule vào một thư mục domain chung khó bảo trì.

## Mục tiêu

- Fork repository `boilerplate` làm nền tảng service mới.
- Giữ capability nền tảng đã có, bao gồm Clean Architecture, UoW và Transactional Outbox.
- Tạo cấu trúc module/domain tương ứng với database design đã được phê duyệt.
- Thiết lập service chạy độc lập trên port/database của `tenancy-service`.
- Chuẩn bị boundary rõ để các member triển khai từng domain mà không chồng chéo code.

## Danh sách domain/module

Theo tài liệu hiện tại, các module chính gồm:

- `building` — `buildings`;
- `room` — `rooms`;
- `favorite-room` — `favorite_rooms`;
- `roommate-profile` — `roommate_profiles`;
- `match-request` — `match_requests`;
- `rate-policy` — `rate_policies`;
- `billing-setting` — `billing_settings`;
- `contract-template` — `contract_templates`;
- `contract` — `contracts`;
- `contract-member` — `contract_members`;
- `meter-reading` — `meter_readings`;
- `invoice` — `invoices`;
- `dashboard`/read model — `billing_read_models` nếu cần.

`Payment`, `IssueReport`, `Conversation`, `Message` và bảng community không thuộc phạm vi bootstrap tenancy theo service boundary hiện tại.

## Phạm vi công việc

### 1. Fork boilerplate

- [ ] Fork/clone `boilerplate` thành repository mới cho `tenancy-service`.
- [ ] Đổi package name, service name, port và application metadata.
- [ ] Giữ cấu hình UoW, transaction context, outbox relay, publisher và inbox đã có.
- [ ] Loại bỏ sample module không thuộc tenancy sau khi xác định phần cần giữ làm reference.
- [ ] Không copy thủ công từng phần Outbox hoặc tạo implementation khác.

### 2. Cấu hình service

- [ ] Cấu hình `PORT=3002`.
- [ ] Cấu hình database riêng cho `tenancy_db`.
- [ ] Cấu hình RabbitMQ/exchange/queue theo convention của boilerplate.
- [ ] Cấu hình `.env.example` và validation cho biến bắt buộc.
- [ ] Cấu hình migration command và startup command.
- [ ] Cấu hình health check tối thiểu cho process và database.

### 3. Tạo module boundary

- [ ] Tạo module folder cho danh sách domain đã chốt.
- [ ] Mỗi module có domain model/aggregate, application handler, repository port, persistence adapter và controller riêng khi có HTTP API.
- [ ] Không để controller module A gọi thẳng repository module B.
- [ ] Liên kết giữa module dùng application port, domain event hoặc contract đã xác định.
- [ ] Read model/dashboard không làm ngược dependency vào write entity nếu không cần.

### 4. Kiểm tra dependency direction

- [ ] Domain không import NestJS, TypeORM hoặc RabbitMQ.
- [ ] Application chỉ phụ thuộc domain và port.
- [ ] Infrastructure implement port và chứa framework-specific code.
- [ ] Presentation gọi application handler, không truy cập database trực tiếp.
- [ ] Shared chỉ chứa abstraction dùng thật sự giữa nhiều module.

## Ngoài phạm vi

- Không triển khai nghiệp vụ đầy đủ của tất cả domain trong issue bootstrap.
- Không thiết kế lại database; schema đã có trong `database-design.md`.
- Không tạo task port Outbox riêng; fork boilerplate đã bao gồm nền tảng cần thiết.
- Không đưa logic tenancy vào `Identity-Service`.
- Không tạo distributed transaction hoặc foreign key sang Identity database.

## Kết quả bàn giao

- Repository `tenancy-service` được fork từ `boilerplate`.
- Service khởi động được với port 3002 và database riêng.
- Các module/domain có boundary nhất quán.
- Outbox/UoW/infrastructure nền tảng hoạt động từ boilerplate fork.
- Có README ngắn mô tả module ownership và command chạy service.
- P5-08/P5-09 (trước đây P4-24/P4-25) có thể bắt đầu mà không phải di chuyển lại cấu trúc thư mục.

## Tiêu chí nghiệm thu

1. Chạy service bằng environment mẫu thành công.
2. Migration command không trỏ nhầm sang `identity_db`.
3. Các module trong danh sách domain tồn tại đúng boundary.
4. Domain không import framework.
5. Relay/outbox từ boilerplate vẫn được đăng ký khi service khởi động.
6. Module ownership được BE Lead review trước khi code nghiệp vụ.
