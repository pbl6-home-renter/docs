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
| `contract_member.left` | `contractId`, `contractMemberId`, `tenantUserId` nullable, `leftAt` | Change an existing member to read-only; no membership is created for an unknown user. |

`contract_member.linked` được xử lý trong P9-01/P9-02. Message dùng integration-event envelope hiện có với ID ổn định, event type, aggregate metadata, payload và occurredAt. Tenancy append outbox trong cùng transaction với contract/member mutation.

The producer retains its existing event fields: `contract.activated` also carries `id`, `tenantId`, `activatedAt`, and `status`; `contract_member.added` also carries `id`, `tenantId`, and date-only `joinedAt`; `contract_member.left` also carries `id` and date-only `leftAt`. `contract_member.linked` carries `contractId`, `contractMemberId`, and `tenantUserId`. Community consumes resolved IDs only, never phone. See P9-D85 for lifecycle and ordering.

## Acceptance

- Kích hoạt contract tạo đúng một conversation riêng, thêm landlord và participant đã link.
- Member được thêm/link vào chat; member rời chuyển sang read-only.
- Checkout marks remaining members as left and emits `contract_member.left`; it does not delete or kick them from the conversation. A member who leaves individually follows the same chat rule. After Community applies the event, the member is `read_only`: sending is forbidden and REST history ends at `leftSequence`, computed using envelope `occurredAt`, not the date-only `leftAt` or broker delivery time. Contract termination itself does not close the conversation or invent a leave event.
- Only activation creates the conversation and landlord admin. Earlier member events are stored in Community's durable `contract_context_events` table and acknowledged after commit. Activation creates one conversation, adds linked users from its snapshot, then applies pending events in `occurredAt`/event-ID order. Events older than activation time are covered by the snapshot. Event ID deduplicates redelivery; stale add/link events cannot reactivate a member after a later leave. Pending events remain stored if activation never arrives.
- Revocation takes effect when the leave event reaches Community, so broker delay can briefly leave the old access active. P9-04 has no scheduler for future-dated departures.

## Ngoài phạm vi

- Xóa member khỏi building chat, email notification hoặc thay đổi direct/group chat.

## Checklist review

- [ ] Happy path qua broker gồm activation, add và leave.
- [ ] Payload chỉ chứa ID/context, không có phone.
- [ ] PM review trước khi merge.
