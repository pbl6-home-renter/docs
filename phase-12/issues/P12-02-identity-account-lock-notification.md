# P12-02 — Thông báo khóa/mở tài khoản theo quy ước mới

**Trạng thái:** 🟡 Open
**Người phụ trách (đề xuất):** `huynhtiennhat0403`
**Người review:** `baoduong17`, FE Lead
**Ước lượng:** 1 point
**Phụ thuộc:** P12-01
**Repo / branch:** `Identity-Service`, `fe` · `feature/p12-02-account-lock-notification`

> **Đọc trước khi code:** [`community-service/docs/notifications.md`](https://github.com/pbl6-home-renter/community-service/blob/main/docs/notifications.md) (quy ước payload, checklist), `AGENTS.md` và skill trong `.agents/skills/` của từng repo. Nguồn mâu thuẫn: `decisions.md` > `docs/notifications.md` > issue.

## Mục tiêu

Người bị admin khóa/mở khóa thấy thông báo đọc được (không còn `USER_ACCOUNT_LOCKED_TITLE`), kể cả các bản ghi cũ trong lịch sử.

## Quyết định áp dụng

- `P12-D95`, `P12-D96` (bảng mã cũ).

## Thông báo cần gửi

| `messageKey` | Khi nào gửi | Người nhận | `data` (ngoài `messageKey`) | Trang mở trên Web |
|---|---|---|---|---|
| `user.locked` | Admin khóa tài khoản | Người bị khóa | `userId`, `lockedAt` | Không có trang riêng |
| `user.unlocked` | Admin mở khóa | Người được mở khóa | `userId` | Không có trang riêng |

## Tham chiếu code

- `Identity-Service/src/modules/users/domain/events/user-account-notification-requested.event.ts`
- `Identity-Service/src/modules/users/domain/constants/user-notification-code.constant.ts` (bỏ mã, thay bằng câu tiếng Việt)

## Các bước

1. Identity: thêm `data.messageKey`, đổi `title`/`body` sang câu tiếng Việt; cập nhật unit test.
2. fe: thêm 2 mục registry + i18n; thêm vào `LEGACY_NOTIFICATION_CODES`: `USER_ACCOUNT_LOCKED_TITLE → user.locked`, `USER_ACCOUNT_UNLOCKED_TITLE → user.unlocked`.
3. Kiểm tra bản ghi cũ (tạo trước khi deploy) trên `/notifications` hiển thị câu đã dịch.

## Definition of Done

- [ ] Service nguồn: unit test payload (có `messageKey`, đủ tham số, `title`/`body` là câu tiếng Việt, đúng người nhận, không gửi cho người thao tác).
- [ ] Event ghi outbox trong cùng transaction với thay đổi nghiệp vụ; `npm test`, `npm run build`, `npm run lint` pass.
- [ ] fe: mục registry + key i18n `vi`/`en` trong `notifications.json`; `npm run build`, `npm run lint`, `npm run i18n:check` pass; không viết file test.
- [ ] Cập nhật bảng mục 5 trong `community-service/docs/notifications.md` (đổi trạng thái thành "Đã có").
- [ ] Chạy tay, đính kèm ảnh vào PR: thao tác → có bản ghi trong bảng `notifications` (community) → toast hiện trên web → bấm mở đúng trang → F5 lại `/notifications` vẫn hiển thị đúng cả `vi` và `en`.
- [ ] Mỗi repo một PR vào `main`, ghi chung issue này, ≥ 1 reviewer.
