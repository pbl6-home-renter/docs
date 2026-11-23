# P12-08 — Thông báo thành viên được thêm, liên kết và rời hợp đồng

**Trạng thái:** 🟡 Open
**Người phụ trách (đề xuất):** BE Tenancy (PM giao)
**Người review:** `leminhkhai345`, FE Lead
**Ước lượng:** 2 points
**Phụ thuộc:** P12-01
**Repo / branch:** `Tenancy-Service`, `fe` · `feature/p12-08-contract-member-notification`

> **Đọc trước khi code:** [`community-service/docs/notifications.md`](https://github.com/pbl6-home-renter/community-service/blob/main/docs/notifications.md) (quy ước payload, checklist), `AGENTS.md` và skill trong `.agents/skills/` của từng repo. Nguồn mâu thuẫn: `decisions.md` > `docs/notifications.md` > issue.

## Mục tiêu

Các bên của hợp đồng biết khi có người vào hoặc rời phòng.

## Quyết định áp dụng

- `P12-D95`.

## Thông báo cần gửi

| `messageKey` | Khi nào gửi | Người nhận | `data` (ngoài `messageKey`) | Trang mở trên Web |
|---|---|---|---|---|
| `contract.member_added` | Landlord thêm thành viên đã có tài khoản | Người được thêm | `contractId`, `contractCode`, `roomName`, `buildingName` | `/contracts/{id}` |
| `contract.member_linked` | Thành viên đăng ký/xác thực và được liên kết tự động theo số điện thoại | Landlord | `contractId`, `contractCode`, `memberName` | `/contracts/{id}` |
| `contract.member_left` | Thành viên rời hợp đồng | Landlord + thành viên còn lại đã liên kết (trừ người rời) | `contractId`, `contractCode`, `memberName` | `/contracts/{id}` |

## Tham chiếu code

- `Tenancy-Service/src/modules/contract/application/commands/contract-member-add/`, `contract-member-leave/`.
- Liên kết tự động: `Tenancy-Service/src/modules/contract/presentation/messaging/identity-lifecycle.subscriber.ts` → `contract-member.entity.ts#linkTenant`.

## Các bước

1. Tenancy: event cho từng use case + unit test.
2. fe: 3 mục registry + i18n.

## Definition of Done

- [ ] Service nguồn: unit test payload (có `messageKey`, đủ tham số, `title`/`body` là câu tiếng Việt, đúng người nhận, không gửi cho người thao tác).
- [ ] Event ghi outbox trong cùng transaction với thay đổi nghiệp vụ; `npm test`, `npm run build`, `npm run lint` pass.
- [ ] fe: mục registry + key i18n `vi`/`en` trong `notifications.json`; `npm run build`, `npm run lint`, `npm run i18n:check` pass; không viết file test.
- [ ] Cập nhật bảng mục 5 trong `community-service/docs/notifications.md` (đổi trạng thái thành "Đã có").
- [ ] Chạy tay, đính kèm ảnh vào PR: thao tác → có bản ghi trong bảng `notifications` (community) → toast hiện trên web → bấm mở đúng trang → F5 lại `/notifications` vẫn hiển thị đúng cả `vi` và `en`.
- [ ] Mỗi repo một PR vào `main`, ghi chung issue này, ≥ 1 reviewer.
