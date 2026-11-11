# P9-08 — Invoice phát hành → notification cho tenant

**Epic:** Tích hợp event Phase 9  
**Trạng thái:** 🟡 Open  
**Coder:** `huynhtiennhat0403`  
**Người review:** PM  
**Ước lượng:** 3 points · 12 giờ (mục tiêu ≤15 file mỗi PR)  
**Phụ thuộc:** P6-02g phát hành invoice; P9-05; P7-15  
**Repo:** `Tenancy-Service/`, `community-service/`  
**Issue:** `docs#TBD`

## Mục tiêu

Sau khi Tenancy phát hành invoice, Community lưu notification inbox cho từng tenant đã link và đủ điều kiện, rồi delivery qua realtime/push hiện có.

## Contract event và topology

Tenancy append `notification.requested` trong cùng transaction với thao tác phát hành Invoice. Event publish vào queue hiện có `community.notification` theo envelope hiện tại:

- `sourceService`: `tenancy-service`.
- `recipientUserIds`: các `tenantId` duy nhất của ContractMember đang active tại thời điểm phát hành; bỏ ID NULL/chưa link, không gửi landlord.
- `notification.type`: `invoice`.
- `title`/`body`: thông báo invoice được phát hành và kỳ hóa đơn.
- `deepLink`: `/invoices/{invoiceId}`.
- `data`: `invoiceId`, `contractId`, `period`.

Source domain event là `invoice.issued`; Community nhận integration request chung `notification.requested`, không tạo consumer `invoice.issued` thứ hai.

## Acceptance

- Phát hành invoice tạo một outbox notification request có đúng recipients đã link và snapshot.
- Community lưu một inbox item cho mỗi recipient, dedup theo event ID và phát notification Socket hiện có.
- Push tuân theo preference invoice; tắt push không ẩn inbox hoặc chặn Socket sync.
- Invoice và notification request atomic tại Tenancy; broker outage không làm mất request.
- Không có recipient đã link thì không phát request có recipient list rỗng; invoice vẫn được phát hành.

## Ngoài phạm vi

- Payment, settlement, overdue/reminder, notification hủy invoice hoặc Issue notification.

## Checklist review

- [ ] Happy path invoice issue → outbox relay → Community inbox/realtime.
- [ ] Recipient do Tenancy chọn từ ContractMember; Community không lookup.
- [ ] PM review trước khi merge.
