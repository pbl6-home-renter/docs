# P9-04 — Vòng đời Contract → contract chat membership

**Epic:** Tích hợp event Phase 9  
**Trạng thái:** 🟡 Open  
**Coder:** `huynhtiennhat0403`  
**Người review:** PM  
**Ước lượng:** 3 points · 12 giờ (mục tiêu ≤15 file mỗi PR)  
**Phụ thuộc:** P8-06; P9-01/P9-02; P7-03/04/05  
**Repo:** `Tenancy-Service/`, `community-service/`  
**Issue:** `docs#TBD`

## Mục tiêu

Khi kích hoạt contract, tạo conversation riêng cho contract và đồng bộ các ContractMember đã link. Cùng consumer xử lý member được thêm hoặc rời.

## Contract event và topology

Bind các routing key dưới đây vào một durable queue `community.contract-context`, để một subscriber xử lý lifecycle context contract:

| Routing key | Payload bắt buộc | Consumer xử lý |
|---|---|---|
| `contract.activated` | `contractId`, `buildingId`, `roomId`, `landlordId`, `tenantUserIds[]` | Tạo contract conversation duy nhất; thêm landlord và tenant đã link. |
| `contract_member.added` | `contractId`, `contractMemberId`, `tenantUserId` nullable, `joinedAt` | Thêm member đã link; nếu ID NULL thì chờ event linked do P9-01/P9-02 xử lý. |
| `contract_member.left` | `contractId`, `contractMemberId`, `tenantUserId`, `leftAt` | Đổi member thành read-only trong contract conversation. |

`contract_member.linked` được xử lý trong P9-01/P9-02. Message dùng integration-event envelope hiện có với ID ổn định, event type, aggregate metadata, payload và occurredAt. Tenancy append outbox trong cùng transaction với contract/member mutation.

## Acceptance

- Kích hoạt contract tạo đúng một conversation riêng, thêm landlord và participant đã link.
- Member được thêm/link vào chat; member rời chuyển sang read-only.
- Checkout hoặc contract termination tự thân không kick member khỏi chat.
- Duplicate delivery idempotent. Nếu member event tới trước activation, consumer upsert conversation/context an toàn; activation sau không tạo bản trùng.

## Ngoài phạm vi

- Xóa member khỏi building chat, email notification hoặc thay đổi direct/group chat.

## Checklist review

- [ ] Happy path qua broker gồm activation, add và leave.
- [ ] Payload chỉ chứa ID/context, không có phone.
- [ ] PM review trước khi merge.
