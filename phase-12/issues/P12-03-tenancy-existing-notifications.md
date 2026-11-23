# P12-03 — Thông báo khóa hợp đồng và hóa đơn phát hành theo quy ước mới

**Trạng thái:** 🟡 Open
**Người phụ trách (đề xuất):** `leminhkhai345`
**Người review:** `baoduong17`, FE Lead
**Ước lượng:** 2 points
**Phụ thuộc:** P12-01
**Repo / branch:** `Tenancy-Service`, `fe` · `feature/p12-03-existing-notifications`

> **Đọc trước khi code:** [`community-service/docs/notifications.md`](https://github.com/pbl6-home-renter/community-service/blob/main/docs/notifications.md) (quy ước payload, checklist), `AGENTS.md` và skill trong `.agents/skills/` của từng repo. Nguồn mâu thuẫn: `decisions.md` > `docs/notifications.md` > issue.

## Mục tiêu

Các thông báo Tenancy đang gửi (luồng khóa landlord, hóa đơn phát hành) có `messageKey` để Web dịch thay vì hiện mã.

## Quyết định áp dụng

- `P12-D95`, `P12-D96`.

## Thông báo cần gửi

| `messageKey` | Khi nào gửi | Người nhận | `data` (ngoài `messageKey`) | Trang mở trên Web |
|---|---|---|---|---|
| `contract.suspended` | Landlord bị khóa, hợp đồng bị tạm ngưng | Như hiện tại | `contractId`, `contractCode`, `roomName` | `/contracts/{id}` |
| `contract.lock_decision_required` | Landlord được mở khóa, cần chọn khôi phục/chấm dứt | Landlord | `contractId`, `contractCode`, `lockCycleId` | `/contracts/{id}` |
| `contract.restored` | Landlord chọn khôi phục | Như hiện tại | `contractId`, `contractCode` | `/contracts/{id}` |
| `contract.terminated_by_lock` | Landlord chọn chấm dứt | Như hiện tại | `contractId`, `contractCode` | `/contracts/{id}` |
| `invoice.issued` | Phát hành hóa đơn (đã có) | Tenant | `invoiceId`, `contractId`, `period` | `/invoices/{id}` |

## Tham chiếu code

- `Tenancy-Service/src/modules/contract/domain/events/contract-suspension-notification-requested.event.ts`
- `Tenancy-Service/src/modules/contract/domain/events/contract-lock-resolution-notification-requested.event.ts`
- `Tenancy-Service/src/modules/contract/domain/constants/contract-notification-code.constant.ts`
- `Tenancy-Service/src/modules/invoice/domain/events/invoice-notification-requested.event.ts`

## Các bước

1. Tenancy: thêm `messageKey` + tham số; `invoice.issued` chuyển câu tiếng Việt đang viết cứng sang mã trong class constant; cập nhật unit test.
2. fe: thêm mục registry + i18n.
3. Kiểm tra lại luồng khóa landlord đầu-cuối (khóa → mở khóa → quyết định) và phát hành hóa đơn.

## Definition of Done

- [ ] Service nguồn: unit test payload (có `messageKey`, đủ tham số, `title`/`body` lấy từ class constant, đúng người nhận, không gửi cho người thao tác).
- [ ] Event ghi outbox trong cùng transaction với thay đổi nghiệp vụ; `npm test`, `npm run build`, `npm run lint` pass.
- [ ] fe: mục registry + key i18n `vi`/`en` trong `notifications.json`; `npm run build`, `npm run lint`, `npm run i18n:check` pass; không viết file test.
- [ ] Cập nhật bảng mục 5 trong `community-service/docs/notifications.md` (đổi trạng thái thành "Đã có").
- [ ] Chạy tay, đính kèm ảnh vào PR: thao tác → có bản ghi trong bảng `notifications` (community) → toast hiện trên web → bấm mở đúng trang → F5 lại `/notifications` vẫn hiển thị đúng cả `vi` và `en`.
- [ ] Mỗi repo một PR vào `main`, ghi chung issue này, ≥ 1 reviewer.
