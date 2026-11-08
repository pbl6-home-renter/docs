# P8-09 — Kiểm chứng smoke xuyên hệ thống và lưu bằng chứng

**Epic:** Phase 8  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** FE `ThaiBao11125`; BE `leminhkhai345`, `baoduong17`  
**Người review:** PM + FE/BE reviewer  
**Ước lượng:** 3 points · 12 giờ (**tối đa 3 points và khoảng 15 file mỗi PR**)  
**Phụ thuộc:** issue P5/P6 được dùng lại, P8-02–P8-06; P8-07/08 chỉ sau khi PM định nghĩa flow  
**Repo / branch:** `fe/`, `api-gateway/`, `Tenancy-Service/`, `community-service/` · `docs/p8-09-smoke-evidence`  
**Issue:** `docs#TBD`

> **Đọc trước khi chạy:** `fe/AGENTS.md`, skill FE; `community-service/AGENTS.md` và skill backend Community; skill Tenancy trong `boilerplate/.agents/skills/`. Chạy trên môi trường team chỉ định, không dùng production data.

## Mục tiêu

Chạy smoke qua Web → Gateway → services → DB/RabbitMQ bằng landlord, admin và tenant. Tái sử dụng kết quả P7-18 cho Web Chat; chỉ kiểm tra lại chat trong phạm vi regression/context integration Phase 8, không lặp toàn bộ P7.

## Quyết định áp dụng

- Chỉ kiểm luồng đã có acceptance và flow được PM duyệt; P8-07/08 chưa có flow nên chưa tự thêm expected behavior.
- Dùng tài khoản/seed demo reset được; che PII, token và secret trong ảnh/log.
- Mỗi fail phải có issue follow-up, severity, owner, expected/actual và bước tái hiện; không đánh dấu pass khi thiếu account/config.

## Ma trận kiểm chứng

| Vai trò | Luồng | Bằng chứng |
|---|---|---|
| Landlord | Building/Room và approval; Contract/Member; MeterReading; billing policy; invoice generate/edit/issue/void | UI route, API request ID, state DB tương ứng |
| Tenant | `/me/invoices` chỉ trả issued; invoice detail/deep link | token role, response status/IDs đã che dữ liệu |
| Admin | list/detail/update/lock/unlock/delete user theo quyền | thao tác UI, response Identity |
| Community | Building/Contract context, membership và invoice notification sau khi flow P8-07/08 được chốt | event ID, conversation/inbox dedupe, delivery preference |
| Broker | outage/retry/duplicate cho outbox/consumer đã triển khai | log correlation ID, outbox/inbox DB và kết quả sau recovery |

## Các bước triển khai

### Bước 1 — Chuẩn bị run

- **Cách làm:** ghi environment/commit, tài khoản từng role, seed/reset procedure và baseline issue carry-over đã merge.
- **Kiểm tra bước:** đăng nhập được đủ role qua Gateway; health route và dependency sẵn sàng.

### Bước 2 — Chạy role matrix

- **Cách làm:** chạy lần lượt landlord, admin, tenant; ghi case ID, thao tác, expected/actual, request/correlation ID.
- **Kiểm tra bước:** đối chiếu ownership, status invoice và permission với issue gốc tương ứng; không gọi thẳng service thay user flow.

### Bước 3 — Kiểm tra event/retry

- **Cách làm:** replay event và mô phỏng broker outage theo khả năng môi trường; dùng P8-07/08 acceptance sau khi PM chốt flow.
- **Kiểm tra bước:** event duplicate không nhân state; broker phục hồi thì outbox pending được xử lý.

### Bước 4 — Báo lỗi và lưu artifact

- **Cách làm:** lưu ảnh/log đã che dữ liệu vào `pm/phase-8/evidence/` hoặc Drive team folder; tạo issue cho fail.
- **Kiểm tra bước:** reviewer có thể tái hiện từng fail từ evidence; mọi blocker có owner.

## Ngoài phạm vi

- Thay đổi business logic/API trong smoke task; tạo flow thay PM; chạy destructive test trên production.
- Lặp lại toàn bộ P7-18 đã hoàn tất khi không có regression liên quan.

## Blocker

- Thiếu credential, seed, môi trường hoặc flow P8-07/08 thì ghi blocker và tiếp tục các case độc lập; không phỏng đoán hoặc tự assign flow.

## Acceptance

- [ ] Các luồng đã sẵn sàng chạy qua Gateway bằng đúng role; quyền/ownership/invoice visibility đúng.
- [ ] Context event, notification, duplicate và retry chỉ được đánh giá theo flow đã được PM chốt.
- [ ] Mọi fail có issue liên kết, owner, severity và evidence; secrets/PII đã che.
- [ ] P7-18 evidence được tham chiếu, không tạo lại issue chat integration.

## Definition of Done

- [ ] Có report smoke run gồm commit/environment, role matrix, expected/actual, request ID và kết quả.
- [ ] Mọi case chưa chạy có lý do/blocker; không tuyên bố pass toàn hệ thống khi còn blocker.
- [ ] FE/BE reviewer xác nhận evidence; PR tài liệu không vượt 3 points/~15 file.
