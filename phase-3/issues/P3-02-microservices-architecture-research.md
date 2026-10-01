# P3-02 — Research: Thiết kế kiến trúc Microservice cho PBL6 (tách 4 service)

**Status:** 🟡 Open  
**Assignee:** BE Lead  
**Stakeholders / Reviewers:** PM, toàn bộ team (thảo luận tại buổi sync)  
**Created:** 2026-09-29  
**Due date:** 2026-10-02 (EOD)  
**Priority:** 🔴 High / Blocker (chặn NestJS scaffold — quyết định cấu trúc thư mục, DB, repo cho cả Phase 3 & 4)  
**Input:**

- `pm/requirement.md` (scope, D9 long-term-only, D29 landlord-solo resilience)
- `pm/PROJECT_PLAN.md` §2 (phân công), §5 Phase 3, §6 (rủi ro)
- `pm/phase-2/discovery/api-spec.md` (109 endpoint, 24 nhóm module)
- `pm/phase-2/discovery/api-conventions.md` (response wrapper §1, Idempotency-Key §13)
- `pm/phase-1/discovery/database-design.md` (25 entity)
- `pm/phase-0/discovery/tech-feasibility.md` §6 (deployment, `PaymentGateway` strategy pattern)
- `pm/phase-2/discovery/decisions.md` (D39–D50; đặc biệt D40 media 2 bước, D43 bulk + `Idempotency-Key`, D49 payout config)

**Deliverable:** Báo cáo kỹ thuật tại `pm/phase-3/discovery/microservices-architecture.md` + đề xuất decision D51 trở đi trong `pm/phase-3/discovery/decisions.md`.

---

## 1. Background & Bối cảnh

Phase 3 (W7–W8) chuẩn bị scaffold NestJS. Hiện tại thiết kế của team là **modular monolith**: một NestJS app chứa toàn bộ 24 nhóm module, cộng thêm FastAPI service cho AI.

Hai sự kiện mới làm thay đổi tiền đề:

1. **Yêu cầu của môn Kiến trúc hướng dịch vụ (SOA)** — đồ án phải có **tối thiểu 4 service** mới đạt yêu cầu môn học.
2. **Team tự bỏ AI khỏi scope MVP** vì chưa thống nhất được feature cụ thể. `PROJECT_PLAN.md` §1 vẫn đang xếp Auto-Description là MVP → cần sửa scope cho khớp.

Đây là thời điểm **rẻ nhất** để tách: `phase-3` chưa scaffold dòng code nào, nên chưa có gì phải viết lại hay migrate.

Tuy nhiên việc tách microservice lên 1 dự án 13 tuần với **1 BE engineer** là rủi ro thật, không phải chuyện hình thức. BE Lead cần một thiết kế vừa thoả yêu cầu môn học vừa **không giết chết tiến độ Phase 3/4**.

---

## 2. Mục tiêu nghiên cứu (Core Research Questions)

### Q1. Ranh giới service — tách ở đâu?

24 nhóm module trong `api-spec.md` cần gom về **4 service**. Câu hỏi then chốt:

- **Tiêu chí nào** để vẽ đường ranh giới giữa các service? (hợp đồng bên thứ ba · tách protocol · profile tài nguyên · liên kết transaction · chi phí team)
- Vì sao `payment` **phải** tách ra, trong khi `media` và `notification` **không nên** tách?
- Có phương án nào tốt hơn 4 service không? Nêu bằng chứng bác bỏ từng phương án.

### Q2. Cơ chế giao tiếp — sync, async và hạ tầng đi kèm

- Với từng luồng nghiệp vụ, chọn **request-reply đồng bộ** hay **pub/sub bất đồng bộ**? Tiêu chí chọn là gì?
- **Message broker:** RabbitMQ hay MQTT hay Kafka hay Redis Streams? So sánh theo yêu cầu thật của dự án (DLQ, retry, consumer group, độ trễ, vận hành trên 1 EC2).
- **Có cần API Gateway không?** Nếu có thì nó làm **client-side hay server-side discovery**? Trả lời trực tiếp câu hỏi lý thuyết trong `lab_5.docx` và nêu rõ áp dụng thế nào cho PBL6.
- **Có cần service registry, heartbeat, load balancing không?** Trên Docker Compose thì service name đã là định chỉ tĩnh — vậy registry để làm gì, và demo được điều gì?

### Q3. Saga, Idempotency và nhất quán cuối cùng

- Luồng nghiệp vụ nào của PBL6 **bắt buộc** phải có compensating transaction? Vẽ saga orchestration hoặc choreography cho luồng đó.
- `Idempotency-Key` đã bắt buộc ở `create-intent` và `record-cash-payment` — lưu ở đâu, sống bao lâu, xử lý race thế nào?
- Nếu payment provider timeout, làm sao phân biệt "chưa xử lý" với "đã xử lý xong nhưng mất gói phản hồi"?
- Ràng buộc **D29** (hệ thống phải chạy được khi tenant không login, chủ trọ làm một mình) ảnh hưởng thế nào đến thiết kế? Nếu provider chết, đường nào vẫn phải sống?

### Q4. Kiến trúc dữ liệu

- Mức độ "database-per-service" nào là khả thi trên **1 Postgres instance**? 4 database + 4 Postgres role riêng có đủ để chứng minh *Service Autonomy* không?
- Bảng nào thuộc service nào? Dữ liệu nào phải rời khỏi service để service khác dùng (và đi bằng gì — API hay event)?
- Ảnh hưởng lên `database-design.md` và ERD v1 (P2-04) ra sao?

### Q5. Triển khai và khả năng tái sử dụng

- Triển khai 4 service + hạ tầng trên **1 EC2** bằng Docker Compose: topology, cỡ máy tối thiểu, cổng, health check.
- Làm gì để một service **mang sang đồ án khác** dùng được? (cấu trúc repo, cấm thư viện dùng chung, cấu hình qua env var, thuần hoá hợp đồng)
- `payment-service` có đang rò ngôn ngữ nghiệp vụ PBL6 vào trong hợp đồng không? Nếu có thì sửa thế nào?

---

## 3. Các hạng mục công việc cụ thể (Tasks)

### Task 1: Lập ma trận mapping 24 nhóm module → 4 service

- [ ] Đọc `api-spec.md`, đánh số đủ 24 nhóm (§2 Auth → §25 Dashboard)
- [ ] Gán mỗi nhóm vào đúng 1 service, ghi rõ lý do
- [ ] Xuất bảng mapping đầy đủ 24 dòng (không được gộp vòng)

### Task 2: Áp dụng 5 tiêu chí và bác bỏ phương án

- [ ] Trình bày 5 tiêu chí vẽ ranh giới
- [ ] Phân tích riêng 4 quyết định khó nhất: tách `payment` · **không** tách `media` · gộp `notification` · gộp `property`+`billing`
- [ ] Mỗi quyết định phải **dẫn chứng dòng cụ thể** từ `api-spec.md` / `api-conventions.md` / `database-design.md`, không nói chung chung
- [ ] Bảng liệt kê các phương án bị loại (ví dụ: 6 service, 5 service, giữ monolith) kèm lý do loại

### Task 3: Chọn message broker

- [ ] So sánh RabbitMQ / MQTT / Kafka / Redis Streams theo tiêu chí dự án cần: DLQ, retry, consumer group, thứ tự message, độ trễ, tài nguyên, độ dễ vận hành trên 1 EC2
- [ ] Chốt 1 broker, nêu rõ lý do loại từng loại còn lại
- [ ] Vẽ sơ đồ exchange → queue → consumer cho ít nhất 1 event thật của dự án

### Task 4: Thiết kế luồng đồng bộ

- [ ] Vẽ sequence diagram cho: (a) Login → nhận JWT, (b) Tenant xem danh sách phòng, (c) Tạo ý định thanh toán
- [ ] Với mỗi lời gọi service-to-service: giao thức, timeout, retry, cách xác thực, cách bỏ qua service không liên quan

### Task 5: Thiết kế Saga & luồng bù trừ

- [ ] Chọn **Orchestration hay Choreography** — nêu lý theo tiêu chí trong `lab_4.docx` §3.3
- [ ] Vẽ saga phát hành hoá đơn theo kỳ: các bước local transaction và bước bù trừ khi fail
- [ ] Vẽ kịch bản provider timeout → retry → idempotency → trả đúng 1 kết quả
- [ ] Chỉ ra đường nào vẫn hoạt động khi provider chết (ràng buộc D29)

### Task 6: Catalogue event

- [ ] Liệt kê event thật cần có: tên · producer · consumer · nội dung payload · ngữ nghĩa delivery (at-most-once / at-least-once) · xử lý trùng lặp
- [ ] Ưu tiên event bắt nguồn từ `D24′` (Property Chat, `@issue`, bot auto-remind) và luồng hoá đơn

### Task 7: Cross-cutting concerns

- [ ] Xác thực: JWKS để service verify token cục bộ, không gọi network mỗi request
- [ ] Truy vết: `correlation-id` xuyên qua gateway → service → event
- [ ] Độ bền: outbox pattern để không mất event, DLQ + retry có backoff, circuit breaker cho provider
- [ ] Nêu rõ ứng dụng cụ thể của từng cơ chế này vào PBL6 (không liệt kê chung chung)

### Task 8: Kiến trúc dữ liệu & triển khai

- [ ] Bảng bảng-dữ-liệu → service; đánh dấu bảng nào **không** được FK chéo
- [ ] Docker Compose topology trên 1 EC2 + sizing tối thiểu (nêu rõ vì sao t3.micro không đủ)
- [ ] Cơ chế health check + heartbeat, kèm câu trả lời câu hỏi lý thuyết "vì sao heartbeat 6s > TTL 2s" trong `lab_5.docx`

### Task 9: Portability guardrails

- [ ] Cấu trúc repo đề xuất cho từng service (không dùng `libs/` dùng chung)
- [ ] Danh sách cấu hình bắt buộc phải qua env var
- [ ] Bảng sửa hợp đồng `payment-service` để không còn phụ thuộc khái niệm `invoice` / `media` của PBL6

---

## 4. Yêu cầu báo cáo kết quả (Deliverable Requirements)

Sản phẩm bàn giao: `pm/phase-3/discovery/microservices-architecture.md`

| # | Phần | Nội dung bắt buộc |
|---|------|-------------------|
| 1 | Executive Summary & Verdict | Kết luận rõ: bao nhiêu service, thoả điều kiện gì |
| 2 | Bối cảnh & ràng buộc | Môn SOA min 4 service · 13 tuần · 1 BE · 1 EC2 · D29 · AI đã bỏ |
| 3 | 4 service đã chốt | Bảng service / module / bảng dữ liệu / port / repo + mapping đủ 24 nhóm module |
| 4 | **Lý do cách tách** | 5 tiêu chí + phân tích 4 quyết định khó nhất + bảng phương án bị loại |
| 5 | **Sơ đồ giao tiếp** | Kiểm kê hạ tầng · sơ đồ container · ma trận giao tiếp · luồng sync · luồng async & Saga · chọn broker · catalogue event · cross-cutting |
| 6 | Kiến trúc dữ liệu | 4 DB + 4 role, cấm FK chéo, dữ liệu đi qua ranh giới bằng gì |
| 7 | Triển khai 1 EC2 | Docker Compose, sizing, health check + heartbeat |
| 8 | Portability | Repo, cấm thư viện chung, env var, sửa hợp đồng `payment` |
| 9 | Ảnh hưởng artifacts | Tách `api-docs/`, Apidog, `PROJECT_PLAN.md:118`, `tech-feasibility.md:257` |
| 10 | Rủi ro & biện pháp | Bảng risk / mitigation |
| 11 | Decision đề xuất | D51 trở đi, nêu rõ cái nào cần GV hoặc PM duyệt |
| 12 | Câu hỏi mở | Những gì chưa chốt được và cần ai trả lời |

Toàn bộ sơ đồ dùng **Mermaid** để render được trực tiếp trên GitHub/VS Code.

---

## 5. Definition of Done (DoD)

- [ ] `pm/phase-3/discovery/microservices-architecture.md` tồn tại, đủ 12 phần nêu trên
- [ ] Ma trận mapping đủ **24/24** nhóm module, mỗi dòng có lý do
- [ ] Có **ít nhất 3 sequence diagram** cho luồng sync và **2** cho luồng async/Saga, tất cả render được
- [ ] Bảng so sánh broker có **cả RabbitMQ và MQTT** (kể cả khi chốt RabbitMQ — cần nêu vì sao loại MQTT)
- [ ] Sơ đồ có đủ: API Gateway, Service Registry, Message Broker, Redis, PostgreSQL (nhiều DB), Object Storage, FCM, Payment Provider
- [ ] Mọi kết luận về phân tách service đều **có dẫn chứng dòng cụ thể** từ `api-spec.md` / `api-conventions.md` / `database-design.md`
- [ ] Có mục riêng nêu ảnh hưởng lên scope AI (D51) và cách sửa `requirement.md` + `PROJECT_PLAN.md`
- [ ] Đề xuất decision D51+ đã ghi vào `pm/phase-3/discovery/decisions.md`
- [ ] Báo cáo được review bởi PM; các mục **cần GV xác nhận** được đánh dấu rõ, không tự quyết
