# P7-15 — Notification inbox và cài đặt push trên Web

**Assignee:** `ThaiBao11125` · **Iteration:** Chưa gán · **Ước lượng:** 3 points
**Repo:** `fe` · **Phụ thuộc:** Community API list/mark-read/preferences và Socket notification events · **Trạng thái:** 🟢 Done

## Context agent

Đọc `fe/AGENTS.md` và các skill bắt buộc của repo. Nguồn sản phẩm là [Phase 6 Community design](../../phase-6/discovery/community-service-design.md), [Phase 7 decisions](../discovery/decisions.md) và [Web Chat decisions](../discovery/web-chat-v1-decisions.md). Community là owner của inbox; service nguồn đã chọn recipient và nội dung trước khi publish event.

## Quy tắc đã chốt

- Inbox chỉ lưu business notification, ví dụ Invoice/Issue; không tạo inbox item cho chat message.
- User chỉ mark-read một item hoặc mark-all-read; bản đầu không xóa notification.
- Read state thuộc user và đồng bộ giữa thiết bị.
- Preference theo `chat`, `invoice`, `issue`; mặc định bật. Tắt category sẽ chặn push thiết bị và toast nổi Web, nhưng inbox vẫn lưu/hiển thị.
- Chuông Web hiển thị chấm khi có unread; chưa có tổng unread endpoint nên không hiển thị số lượng.
- Community phát `notification:created` và `notification:read-state-updated`; FE lọc toast theo category preference nhưng luôn đồng bộ inbox.

## Phạm vi

- Thay route `/notifications` placeholder bằng cursor inbox; tất cả/chưa đọc, mark-one, mark-all, tải tiếp và deep link nội bộ.
- Thay chấm đỏ hardcode trên header bằng unread state thật.
- Cài đặt ba nhóm qua GET/PUT `/me/notification-preference`; cùng preference điều khiển push thiết bị và toast Web.
- Đồng bộ query cache khi Socket notification events đến.
- Vi-only/English i18n theo chuẩn FE.

## Acceptance

- [ ] Query cursor dùng helper FE; bộ lọc được gửi dưới `filter[unreadOnly]` theo API.
- [ ] Mark-read/all cập nhật UI và đồng bộ giữa thiết bị; không có delete action.
- [ ] Toggle preference gửi đủ ba category và không ảnh hưởng inbox.
- [ ] Chuông chỉ hiện dot khi có unread và bỏ dot sau khi tất cả được đọc.
- [ ] Deep link chỉ điều hướng nội bộ; dữ liệu sai/URL ngoài không gây điều hướng ngoài ứng dụng.
- [ ] Có loading/empty/error/load-more states và bản dịch Việt/Anh.
- [ ] `npm run build`, `npm run lint`, `npm run i18n:check` pass.

## Không làm

Không thêm tổng unread endpoint, business email, FCM/web push integration mới, event publisher Invoice/Issue hoặc lưu chat message vào inbox.
