# P9-07 — Landlord mở khóa/hết hạn → khôi phục hoặc chấm dứt contract

**Epic:** Tích hợp event Phase 9  
**Trạng thái:** 🟡 Open  
**Coder:** `leminhkhai345`  
**Người review:** PM  
**Ước lượng:** 3 points · 12 giờ (mục tiêu ≤15 file mỗi PR)  
**Phụ thuộc:** P9-06; P9-05  
**Repo:** `Tenancy-Service/`, `community-service/`  
**Issue:** `docs#TBD`

## Mục tiêu

Hoàn tất choreography sau `user.unlocked` hoặc grace-period expiry. Mở khóa trước hạn dừng auto-termination và yêu cầu landlord chọn khôi phục/chấm dứt. Nếu hết hạn mà account vẫn khóa, Tenancy chấm dứt contract đang suspended và thông báo hai bên.

## Contract event và flow

| Trigger | Hành vi Tenancy | Event phát tiếp |
|---|---|---|
| Identity `user.unlocked` trước deadline | Chuyển lock cycle sang decision-pending; dừng auto-termination; giữ contract suspended đến khi landlord chọn | `notification.requested` type `system` tới landlord, yêu cầu khôi phục hoặc chấm dứt các contract bị ảnh hưởng |
| Landlord chọn khôi phục | Khôi phục contract phù hợp trong một transaction local | `notification.requested` type `system` tới landlord và tenant đã link |
| Landlord chọn chấm dứt | Chấm dứt contract phù hợp trong một transaction local | `notification.requested` type `system` tới landlord và tenant đã link |
| Grace deadline đến khi account vẫn khóa | Scheduled job chấm dứt contract phù hợp idempotent | `notification.requested` type `system` tới landlord và tenant đã link |

Routing `user.unlocked` → `tenancy.identity-lifecycle`; mọi notification dùng `notification.requested` → `community.notification`.

## Acceptance

- Unlock trước hạn ngăn auto-termination và báo landlord chọn; contract giữ suspended đến khi có lựa chọn.
- Restore/terminate chỉ áp dụng một lần và thông báo mọi bên đã link trong contract.
- Hết hạn chỉ chấm dứt contract còn suspended thuộc đúng lock cycle; timer cũ sau unlock/restore không làm thay đổi trạng thái.
- Duplicate unlock, lựa chọn hoặc scheduler delivery không tạo transition/notification trùng.
- Auto-termination không thực hiện hoặc hứa hoàn cọc trong Phase 9.

## Ngoài phạm vi

- Payment/hoàn cọc, mutation contract do tenant lock/unlock hoặc workflow orchestrator bên ngoài.

## Checklist review

- [ ] Happy path gồm unlock→restore và grace expiry→termination.
- [ ] Transition khóa theo lock-cycle ID và transaction locking.
- [ ] PM review trước khi merge.
