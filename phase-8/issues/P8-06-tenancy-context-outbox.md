# P8-06 — Tenancy: hoàn thiện context event qua transactional outbox

**Epic:** Phase 8  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** `leminhkhai345`  
**Người review:** `baoduong17` (BE Lead / API owner)  
**Ước lượng:** 3 points · 12 giờ (**tối đa 3 points và khoảng 15 file mỗi PR**)  
**Phụ thuộc:** P8-01; tái sử dụng outbox pattern ở P5-08b  
**Repo / branch:** `Tenancy-Service/` · `feature/p8-06-context-events`  
**Issue:** `docs#TBD`

> **Đọc trước khi code:** đọc `boilerplate/.agents/skills/be-feature-workflow/SKILL.md`, `be-structure/SKILL.md`, `be-naming/SKILL.md`, `be-code-style/SKILL.md`, `be-api-presentation/SKILL.md`, `be-cross-service/SKILL.md`. Tuân thủ AGENTS/CLAUDE của repo đang chạy; Tenancy checkout hiện không có `AGENTS.md` riêng.

## Mục tiêu

Tenancy phát context event bền vững để Community biết Building/Contract/ContractMember đã thay đổi. Dùng outbox trong cùng transaction; tái sử dụng `BuildingCreated` và hạ tầng Outbox đã có, chỉ bổ sung dữ liệu/producer còn thiếu theo CB-11/12.

## Quyết định áp dụng

- P5-08b đã tạo Building bằng UoW + Outbox và phát `BuildingCreated`; không tạo event/building publisher thứ hai.
- Dùng backlog `pm/phase-6/discovery/community-service-implementation-backlog.md` CB-11/12 và quyết định Phase 7 làm contract cho context.
- Event ghi cùng DB transaction với thay đổi nghiệp vụ; không publish trước commit.
- Không thêm PII nếu consumer không cần; không tìm tenant theo phone.
- P8-07/08 flows chưa được PM định nghĩa. Issue này không tự mở rộng consumer/notification behavior dựa trên flow chưa chốt.

## Contract sự kiện và dữ liệu

Rà outbox/event types hiện có trước khi quyết định thay đổi. Tên event, routing key, version và payload cuối cùng phải tương thích consumer và được `baoduong17` review.

| Nguồn | Dữ liệu tối thiểu cần đối chiếu | Hành vi |
|---|---|---|
| `BuildingCreated` hiện tại | building ID, owner/admin user ID, actor, event ID/version/time nếu contract yêu cầu | tái sử dụng event; chỉ bổ sung field thiếu sau khi consumer xác nhận |
| Contract create/activate | contract ID, building/room ID, landlord ID và linked member IDs cần thiết | append event đúng transaction transition đã chốt |
| ContractMember add/leave | contract ID, member user ID nếu đã linked, action, event ID/version/time | ghi event theo mutation đã commit; không phone lookup |

## Tham chiếu code

- `P5-08b-building-create-command.md`: Building slice mẫu có UoW + Outbox và `BuildingCreated`.
- Dùng `OutboxModule`, publisher/relay, transaction context và migration hiện hữu trong Tenancy; không tạo framework thứ hai.
- Dùng module Contract/ContractMember hiện tại để xác định transaction boundary và domain events.

## Các bước triển khai

### Bước 1 — Kiểm kê event/outbox

- **Cách làm:** tìm event BuildingCreated, contract/member domain events, outbox entity, relay, exchange/routing/queue và migration.
- **Kiểm tra bước:** lập bảng event đang có/thiếu, producer và consumer; xác nhận không đề xuất duplicate BuildingCreated.

### Bước 2 — Chốt payload với Community

- **Cách làm:** đối chiếu CB-11/12, chia sẻ payload dự kiến với Community reviewer; chỉ dùng ID/context cần thiết, giữ event ID ổn định.
- **Kiểm tra bước:** reviewer Community xác nhận schema/routing/version; thiếu quyết định thì dừng phần đó và ghi blocker.

### Bước 3 — Thêm producer còn thiếu

- **Cách làm:** ghi outbox event trong cùng UoW của Contract/ContractMember mutation; tái sử dụng BuildingCreated hiện có, không sửa ngoài payload đã thống nhất.
- **Kiểm tra bước:** commit mutation tạo đúng event; rollback mutation không để lại outbox record.

### Bước 4 — Retry và lỗi broker

- **Cách làm:** dùng retry/confirm/dead-letter pattern hiện hữu; không giữ DB transaction mở trong lúc chờ broker; log event/correlation ID không có secrets.
- **Kiểm tra bước:** tắt broker, tạo mutation, xác nhận DB/outbox commit; bật broker lại, xác nhận publish; giả lập retry không đổi event ID.

## Ngoài phạm vi

- Xây outbox framework mới, consumer Community, conversation creation hoặc notification inbox.
- Đặt business flow P8-07/08 chưa được PM gửi.
- Thay đổi BuildingCreated/event schema không được consumer/API owner chấp thuận.

## Blocker

- Nếu CB-11/12 không chốt tên event, version, recipient hoặc thứ tự, ghi câu hỏi cụ thể vào issue và không tự tạo contract mới.

## Cập nhật contract/tài liệu

- [ ] Cập nhật event schema/sequence trong tài liệu nguồn tương ứng cùng PR implementation.
- [ ] Không tạo issue OpenAPI độc lập; nếu thay đổi API HTTP thì đồng bộ `api-docs` cùng PR.
- [ ] Reviewer Community duyệt payload, retry và compatibility.

## Acceptance

- [ ] BuildingCreated được tái sử dụng, không có publisher/event duplicate.
- [ ] Contract/ContractMember event được ghi cùng transaction; rollback không phát event.
- [ ] Broker outage không mất event; retry dùng event ID ổn định và có thể truy vết.
- [ ] Payload/routing tương thích CB-11/12 và được consumer owner duyệt.

## Definition of Done

- [ ] Có bằng chứng DB/outbox, broker retry và rollback trong PR.
- [ ] Migration có rollback nếu thay đổi schema; config không chứa secret.
- [ ] PR ≤ 3 points/~15 file, `leminhkhai345` implement, `baoduong17` approve.
