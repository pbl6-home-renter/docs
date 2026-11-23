# P12-06 — Báo tenant khi hóa đơn đã phát hành bị hủy

**Trạng thái:** 🟡 Open
**Người phụ trách (đề xuất):** `leminhkhai345`
**Người review:** `baoduong17`, FE Lead
**Ước lượng:** 1 point
**Phụ thuộc:** P12-01, P12-03
**Repo / branch:** `Tenancy-Service`, `fe` · `feature/p12-06-invoice-voided-notification`

> **Đọc trước khi code:** [`community-service/docs/notifications.md`](https://github.com/pbl6-home-renter/community-service/blob/main/docs/notifications.md) (quy ước payload, checklist), `AGENTS.md` và skill trong `.agents/skills/` của từng repo. Nguồn mâu thuẫn: `decisions.md` > `docs/notifications.md` > issue.

## Mục tiêu

Tenant biết hóa đơn mình đã nhận bị hủy và lý do.

## Quyết định áp dụng

- `P12-D95`.

## Thông báo cần gửi

| `messageKey` | Khi nào gửi | Người nhận | `data` (ngoài `messageKey`) | Trang mở trên Web |
|---|---|---|---|---|
| `invoice.voided` | Landlord hủy hóa đơn **đã phát hành** (`ISSUED → VOID`); hủy hóa đơn chưa phát hành thì không báo | Tenant của hợp đồng (như `invoice.issued`) | `invoiceId`, `contractId`, `period`, `reason` | `/invoices/{id}` |

## Tham chiếu code

- `Tenancy-Service/src/modules/invoice/application/commands/invoice-cancel/`, `invoice.entity.ts` (`void(reason)`).
- Cách lấy người nhận: dùng lại logic của `invoice-issue-item.service.ts`.

## Các bước

1. Tenancy: chỉ gửi khi trạng thái trước đó là `ISSUED`; unit test cả hai nhánh.
2. fe: mục registry + i18n (body có `{{period}}`, `{{reason}}`).

## Definition of Done

- [ ] Service nguồn: unit test payload (có `messageKey`, đủ tham số, `title`/`body` lấy từ class constant, đúng người nhận, không gửi cho người thao tác).
- [ ] Event ghi outbox trong cùng transaction với thay đổi nghiệp vụ; `npm test`, `npm run build`, `npm run lint` pass.
- [ ] fe: mục registry + key i18n `vi`/`en` trong `notifications.json`; `npm run build`, `npm run lint`, `npm run i18n:check` pass; không viết file test.
- [ ] Cập nhật bảng mục 5 trong `community-service/docs/notifications.md` (đổi trạng thái thành "Đã có").
- [ ] Chạy tay, đính kèm ảnh vào PR: thao tác → có bản ghi trong bảng `notifications` (community) → toast hiện trên web → bấm mở đúng trang → F5 lại `/notifications` vẫn hiển thị đúng cả `vi` và `en`.
- [ ] Mỗi repo một PR vào `main`, ghi chung issue này, ≥ 1 reviewer.
