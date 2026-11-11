# P9-03 — Vòng đời Building → building chat và thông báo duyệt

**Epic:** Tích hợp event Phase 9  
**Trạng thái:** 🟡 Open  
**Coder:** `huynhtiennhat0403`  
**Người review:** PM  
**Ước lượng:** 3 points · 12 giờ (mục tiêu ≤15 file mỗi PR)  
**Phụ thuộc:** P8-06; P7-03/04/05; P9-05  
**Repo:** `Tenancy-Service/`, `community-service/`, `fe/`  
**Issue:** `docs#TBD`

## Mục tiêu

Tạo đúng một building conversation khi tạo building và gửi thông báo duyệt/từ chối tới landlord.

## Contract event và topology

| Producer | Routing key | Queue | Payload | Consumer xử lý |
|---|---|---|---|---|
| Tenancy | `building.created` | `community.building-context` | `buildingId`, `landlordId` | Tạo building conversation duy nhất, thêm landlord với role admin. |
| Tenancy | `notification.requested` sau approve/reject | Queue hiện có `community.notification` | `sourceService=tenancy-service`, `recipientUserIds=[landlordId]`, type `system`, title/body, deep link `/buildings/{buildingId}`, data gồm `buildingId` và decision | Community lưu một inbox item và gửi realtime/push theo preference `system`. |

Dùng lại outbox event `building.created` hiện có. `building.approved/rejected` vẫn là domain event của Tenancy; cùng transaction trạng thái append thêm notification request.

## Triển khai

1. Tạo subscriber Community cho `building.created`, upsert conversation và owner idempotent.
2. Append `notification.requested` từ approve/reject command trong cùng transaction với thay đổi trạng thái.
3. Thêm hỗ trợ type `system` theo P9-05 và cập nhật Web realtime guard/category hiển thị.
4. Xác nhận create → conversation và approve/reject → notification landlord.

## Acceptance

- Replay `building.created` vẫn chỉ có một building conversation và một owner membership.
- Approve và reject mỗi thao tác tạo đúng một notification tới landlord, có decision và deep link tương ứng.
- Rollback transaction không để lại trạng thái duyệt hoặc notification outbox message.
- Tắt preference chỉ ảnh hưởng push/toast; inbox và Socket sync vẫn hoạt động.

## Ngoài phạm vi

- Notification cho building update/delete, HTTP API mới hoặc đổi rule duyệt Building.

## Checklist review

- [ ] Bằng chứng happy path gồm create và một decision qua broker tới Community.
- [ ] Không tạo publisher `building.created` thứ hai.
- [ ] PM review trước khi merge.
