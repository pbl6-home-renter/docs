# P12-02 — Thông báo khóa/mở tài khoản theo quy ước mới

**Trạng thái:** 🟡 Open
**Người phụ trách (đề xuất):** `huynhtiennhat0403`
**Người review:** `baoduong17`, FE Lead
**Ước lượng:** 1 point
**Phụ thuộc:** P12-01
**Repo / branch:** `Identity-Service`, `fe` · `feature/p12-02-account-lock-notification`

> **Đọc trước khi code:** [`community-service/docs/notifications.md`](https://github.com/pbl6-home-renter/community-service/blob/main/docs/notifications.md) (quy ước payload, checklist), `AGENTS.md` và skill trong `.agents/skills/` của từng repo. Nguồn mâu thuẫn: `decisions.md` > `docs/notifications.md` > issue.

## Mục tiêu

Người bị admin khóa/mở khóa thấy thông báo đã dịch trên Web thay vì mã `USER_ACCOUNT_LOCKED_TITLE`.

## Quyết định áp dụng

- `P12-D95`, `P12-D96`.

## Thông báo cần gửi

| `messageKey` | Khi nào gửi | Người nhận | `data` (ngoài `messageKey`) | Trang mở trên Web |
|---|---|---|---|---|
| `user.locked` | Admin khóa tài khoản | Người bị khóa | `userId`, `lockedAt` | Không có trang riêng |
| `user.unlocked` | Admin mở khóa | Người được mở khóa | `userId` | Không có trang riêng |

## Tham chiếu code

- `Identity-Service/src/modules/users/domain/events/user-account-notification-requested.event.ts`
- `Identity-Service/src/modules/users/domain/constants/user-notification-code.constant.ts` (giữ nguyên các mã `title`/`body`)

## Các bước

1. Identity: thêm `data.messageKey` (`user.locked` / `user.unlocked`); cập nhật unit test.
2. fe: thêm 2 mục registry + i18n.

## Definition of Done

- [ ] Service nguồn: unit test payload (có `messageKey`, đủ tham số, `title`/`body` lấy từ class constant, đúng người nhận, không gửi cho người thao tác).
- [ ] Event ghi outbox trong cùng transaction với thay đổi nghiệp vụ; `npm test`, `npm run build`, `npm run lint` pass.
- [ ] fe: mục registry + key i18n `vi`/`en` trong `notifications.json`; `npm run build`, `npm run lint`, `npm run i18n:check` pass; không viết file test.
- [ ] Cập nhật bảng mục 5 trong `community-service/docs/notifications.md` (đổi trạng thái thành "Đã có").
- [ ] Chạy tay, đính kèm ảnh vào PR: thao tác → có bản ghi trong bảng `notifications` (community) → toast hiện trên web → bấm mở đúng trang → F5 lại `/notifications` vẫn hiển thị đúng cả `vi` và `en`.
- [ ] Mỗi repo một PR vào `main`, ghi chung issue này, ≥ 1 reviewer.
