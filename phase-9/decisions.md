# Quyết định Phase 9

## P9-D83 — Topology event, notification và Saga choreography (2026-11-08)

**Trạng thái:** PM đã chốt.

- Các service dùng RabbitMQ topic exchange hiện có, transactional outbox/inbox local. Delivery at-least-once; consumer phải idempotent. Không dùng distributed transaction hoặc 2PC.
- Mỗi consumer có một durable queue:
  - `tenancy.identity-lifecycle` bind `user.registered`, `user.updated`, `user.locked`, `user.unlocked`, `user.deleted`.
  - `community.building-context` bind `building.created`.
  - `community.contract-context` bind `contract.activated`, `contract_member.added`, `contract_member.left`, `contract_member.linked`.
  - Queue `community.notification` hiện có bind `notification.requested`.
- Tenancy chỉ liên kết Contract/ContractMember có `tenantId=NULL` khi phone khớp chính xác sau chuẩn hóa. Phone chỉ đi qua Identity→Tenancy, không đưa vào event cho Community.
- Community context events tạo/đồng bộ conversation và membership; không tự tạo business inbox notification. Member lifecycle có thể ghi system message theo rule chat hiện có.
- Business notification dùng envelope `notification.requested`. Recipients: landlord khi building được duyệt/từ chối; user bị hạn chế/khôi phục; landlord và tenant đã link khi contract tạm ngưng/khôi phục/chấm dứt; ContractMember đang hoạt động và đã link khi Invoice được phát hành.
- Thêm notification type/category `system` cho Building/account/contract; mặc định bật push. Giữ `invoice` và `issue`. Preference tắt push/toast không được ẩn inbox hoặc chặn Socket sync.
- Landlord lock dùng Saga choreography: Identity phát `user.locked`; Tenancy consume, tạm ngưng các contract đang hiệu lực, lưu grace deadline và phát notification request. Nếu `user.unlocked` trước hạn, Tenancy dừng auto-termination và yêu cầu landlord chọn khôi phục hoặc chấm dứt. Scheduled job của Tenancy xử lý grace deadline, không tạo service scheduler riêng. Chấm dứt không bao gồm hoàn cọc trong Phase 9.
- Luồng register/link, tạo context chat và Invoice notification là event integration một chiều, không phải Saga. Saga Invoice/Payment orchestration trong P3-D57 không thuộc phạm vi; Payment vẫn Stretch theo P6-D61.
- IssueReport/Issue notification tiếp tục ngoài phạm vi cùng Issue feature theo P6-D61; code hiện chưa có Issue producer module.

**Tham chiếu:** `phase-1/discovery/user_flow/`, P6-D61, P6-D74, P7-D82, `phase-6/discovery/community-service-design.md`, `boilerplate/docs/transactional-outbox-design.md`.
