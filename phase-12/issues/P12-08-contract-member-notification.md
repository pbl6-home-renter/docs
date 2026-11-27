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

- `P12-D95`, `P12-D110`.

## Thông báo cần gửi

| `messageKey` | Khi nào gửi | Người nhận | `data` (ngoài `messageKey`) | Trang mở trên Web |
|---|---|---|---|---|
| `contract.member_added` | Landlord thêm thành viên đã có tài khoản | Người được thêm | `contractId`, `contractCode`, `roomName`, `buildingName` | `/contracts/{id}` |
| `contract.member_linked` | Thành viên đăng ký/xác thực và được liên kết tự động theo số điện thoại | Landlord | `contractId`, `contractCode`, `memberName` | `/contracts/{id}` |
| `contract.member_left` | Landlord ghi nhận ngày rời thành viên, kể cả ngày trong tương lai | Thành viên còn lại đã liên kết; không gồm landlord thao tác hoặc người rời | `contractId`, `contractCode`, `memberName`, `leftOn` | `/contracts/{id}` |

`contract.member_left` được yêu cầu ngay khi ghi nhận ngày rời thành công, không hẹn đến `leftOn`. Nếu không có thành viên còn lại đã liên kết, chỉ ghi sự kiện nghiệp vụ `contract_member.left`, không tạo `notification.requested` với `recipientUserIds` rỗng. FE phải nói rõ **ngày rời đã được ghi nhận**; với ngày trong tương lai, không diễn đạt rằng thành viên đã rời hợp đồng.

## Tham chiếu code

- `Tenancy-Service/src/modules/contract/application/commands/contract-member-add/`, `contract-member-leave/`.
- Liên kết tự động: `Tenancy-Service/src/modules/contract/presentation/messaging/identity-lifecycle.subscriber.ts` → `contract-member.entity.ts#linkTenant`.

## Các bước

1. Tenancy: event cho từng use case + unit test.
2. fe: 3 mục registry + i18n.

## Definition of Done

- [ ] Service nguồn: unit test payload (có `messageKey`, đủ tham số, `title`/`body` lấy từ class constant, đúng người nhận, không gửi cho người thao tác).
- [ ] `contract.member_left`: kiểm tra danh sách người nhận không gồm landlord thao tác hoặc người rời; chỉ gồm thành viên còn lại đã liên kết. Khi không còn người nhận, không tạo `notification.requested` với danh sách rỗng.
- [ ] `contract.member_left`: kiểm tra `notification.data.leftOn` là ngày đã ghi nhận; thông báo được ghi outbox ngay cả khi `leftOn` ở tương lai, không đợi đến ngày đó.
- [ ] Event ghi outbox trong cùng transaction với thay đổi nghiệp vụ; `npm test`, `npm run build`, `npm run lint` pass.
- [ ] fe: mục registry + key i18n `vi`/`en` trong `notifications.json`; `npm run build`, `npm run lint`, `npm run i18n:check` pass; không viết file test.
- [ ] fe: nội dung `contract.member_left` trong cả `vi`/`en` nói ngày rời **đã được ghi nhận**, không nói thành viên đã rời khi ngày ở tương lai.
- [ ] Đối chiếu bảng mục 5 trong `community-service/docs/notifications.md`; chỉ đổi trạng thái `contract.member_*` thành "Đã có" sau khi code và kiểm tra thông báo hoạt động.
- [ ] Chạy tay, đính kèm ảnh vào PR: thao tác → có bản ghi trong bảng `notifications` (community) → toast hiện trên web → bấm mở đúng trang → F5 lại `/notifications` vẫn hiển thị đúng cả `vi` và `en`.
- [ ] Mỗi repo một PR vào `main`, ghi chung issue này, ≥ 1 reviewer.
