# P12-07 — Báo tenant khi hợp đồng được kích hoạt hoặc trả phòng

**Trạng thái:** 🟡 Open
**Người phụ trách (đề xuất):** BE Tenancy (PM giao)
**Người review:** `leminhkhai345`, FE Lead
**Ước lượng:** 2 points
**Phụ thuộc:** P12-01
**Repo / branch:** `Tenancy-Service`, `fe` · `feature/p12-07-contract-lifecycle-notification`

> **Đọc trước khi code:** [`community-service/docs/notifications.md`](https://github.com/pbl6-home-renter/community-service/blob/main/docs/notifications.md) (quy ước payload, checklist), `AGENTS.md` và skill trong `.agents/skills/` của từng repo. Nguồn mâu thuẫn: `decisions.md` > `docs/notifications.md` > issue.

## Mục tiêu

Tenant và thành viên đã liên kết tài khoản nhận thông báo khi hợp đồng bắt đầu hiệu lực và khi hoàn tất trả phòng.

## Quyết định áp dụng

- `P12-D95`, `P12-D97` (không báo đổi trạng thái phòng).

## Thông báo cần gửi

| `messageKey` | Khi nào gửi | Người nhận | `data` (ngoài `messageKey`) | Trang mở trên Web |
|---|---|---|---|---|
| `contract.activated` | Landlord kích hoạt hợp đồng | Tenant đại diện + thành viên đã liên kết tài khoản | `contractId`, `contractCode`, `roomName`, `buildingName`, `startDate` | `/contracts/{id}` |
| `contract.checked_out` | Landlord hoàn tất trả phòng | Như trên | `contractId`, `contractCode`, `roomName`, `buildingName`, `endDate` | `/contracts/{id}` |

## Tham chiếu code

- `Tenancy-Service/src/modules/contract/application/commands/contract-activate/`, `contract-checkout-complete/`.
- Thành viên chưa có tài khoản (chưa liên kết) thì bỏ qua.

## Các bước

1. Tenancy: event + unit test (có/không có thành viên đã liên kết).
2. fe: 2 mục registry + i18n.

## Definition of Done

- [ ] Service nguồn: unit test payload (có `messageKey`, đủ tham số, `title`/`body` là câu tiếng Việt, đúng người nhận, không gửi cho người thao tác).
- [ ] Event ghi outbox trong cùng transaction với thay đổi nghiệp vụ; `npm test`, `npm run build`, `npm run lint` pass.
- [ ] fe: mục registry + key i18n `vi`/`en` trong `notifications.json`; `npm run build`, `npm run lint`, `npm run i18n:check` pass; không viết file test.
- [ ] Cập nhật bảng mục 5 trong `community-service/docs/notifications.md` (đổi trạng thái thành "Đã có").
- [ ] Chạy tay, đính kèm ảnh vào PR: thao tác → có bản ghi trong bảng `notifications` (community) → toast hiện trên web → bấm mở đúng trang → F5 lại `/notifications` vẫn hiển thị đúng cả `vi` và `en`.
- [ ] Mỗi repo một PR vào `main`, ghi chung issue này, ≥ 1 reviewer.
