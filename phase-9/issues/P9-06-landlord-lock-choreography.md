# P9-06 — Landlord bị khóa → tạm ngưng contract và bắt đầu grace period

**Epic:** Tích hợp event Phase 9  
**Trạng thái:** 🟡 Open  
**Coder:** `leminhkhai345`  
**Người review:** PM  
**Ước lượng:** 3 points · 12 giờ (mục tiêu ≤15 file mỗi PR)  
**Phụ thuộc:** Identity producer `user.locked`; P9-05  
**Repo:** `Identity-Service/`, `Tenancy-Service/`, `community-service/`  
**Issue:** `docs#TBD`

## Mục tiêu

Dùng Saga choreography cho landlord lock. Identity phát event account; Tenancy phản ứng với vai trò participant, tạm ngưng các contract đang hiệu lực, lưu grace deadline và yêu cầu gửi notification. Identity cũng yêu cầu thông báo hạn chế/khôi phục tới chính user. Không thêm service điều phối trung tâm.

## Contract event và topology

| Producer | Routing key | Queue | Payload sử dụng | Consumer xử lý |
|---|---|---|---|---|
| Identity | `user.locked` | `tenancy.identity-lifecycle` | `userId`, `role`, `status`, `lockedAt` | Với role landlord, Tenancy tạm ngưng contract đang hiệu lực của landlord, lưu lock cycle/deadline và phát notification request. Tenant lock không tạm ngưng contract landlord. |
| Identity | `notification.requested` cùng transaction `user.locked/unlocked` | `community.notification` | `recipientUserIds=[userId]`, type `system`, snapshot hạn chế/khôi phục | Community lưu account notice cho user bị ảnh hưởng. |
| Tenancy | `notification.requested` sau khi tạm ngưng landlord contract | `community.notification` | Type `system`; recipients gồm landlord và tenant đã link ở contract bị tạm ngưng; data gồm contract IDs/grace deadline | Community lưu inbox từng recipient và gửi Socket/FCM theo preference. |

## Triển khai

1. Consume `user.locked` bằng inbox dedup; Identity append account notification request trong transaction khóa user.
2. Trong một transaction Tenancy, chuyển các contract bị ảnh hưởng sang suspended, lưu lock-cycle/grace deadline bền vững và append notification requests.
3. Dùng scheduled job nhẹ trong process Tenancy để tìm lock cycle đến hạn; không thêm scheduler service hoặc delayed-queue infrastructure.
4. Dùng lock-cycle ID/deadline để xử lý idempotent duplicate lock event và timer cũ.

## Acceptance

- Khóa landlord tạm ngưng mọi contract đang hiệu lực của landlord và thông báo landlord cùng tenant đã link.
- Khóa tenant gửi notice tới tenant nhưng không tạm ngưng contract của landlord.
- Duplicate `user.locked` không tạo lock cycle hay notice trùng.
- Contract state, grace record và notification outbox cùng commit/rollback.
- Grace deadline còn sau khi restart Tenancy và được scheduled job tìm thấy.

## Ngoài phạm vi

- Payment/hoàn cọc, service mới, distributed transaction hoặc kick user khỏi contract chat.

## Checklist review

- [ ] Happy path Identity lock → Tenancy suspend → Community notice.
- [ ] Grace state lưu bền vững; event dùng outbox/inbox hiện có.
- [ ] PM review trước khi merge.
