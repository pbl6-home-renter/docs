# P12-01 — Nền tảng thông báo: quy ước payload và registry trên Web

**Trạng thái:** 🔵 In review
**Người phụ trách (đề xuất):** PM/leader
**Người review:** `baoduong17`, FE Lead
**Ước lượng:** 2 points
**Phụ thuộc:** —
**Repo / branch:** `community-service` · `feature/p12-01-notification-conventions`; `fe` · `feature/p12-01-notification-registry`

> **Đọc trước khi code:** [`community-service/docs/notifications.md`](https://github.com/pbl6-home-renter/community-service/blob/main/docs/notifications.md) (quy ước payload, checklist), `AGENTS.md` và skill trong `.agents/skills/` của từng repo. Nguồn mâu thuẫn: `decisions.md` > `docs/notifications.md` > issue.

## Mục tiêu

Có quy ước chung để mọi task P12-02 → P12-08 chỉ cần sửa service nguồn, thêm một mục registry và i18n.

## Quyết định áp dụng

- `P12-D95` — quy ước payload.
- `P12-D96` — registry Web, `deepLink` dự phòng, community chỉ log warning.

## Đã làm

- community-service:
  - `docs/notifications.md`: luồng, payload, quy tắc cho service nguồn, danh sách `messageKey`, checklist.
  - `NotificationRequestedSubscriber` log warning khi thiếu `data.messageKey` (vẫn lưu bình thường), kèm unit test.
- fe:
  - `src/features/notifications/utils/notification-registry.ts` thay cho `notification-content.ts`: `NOTIFICATION_REGISTRY`, `getNotificationContent`, `getNotificationDestination`.
  - Toast và trang `/notifications` dùng chung registry để chọn nội dung và trang mở.

## Ngoài phạm vi

- Thêm `messageKey` cho các thông báo đang có (P12-02, P12-03).
