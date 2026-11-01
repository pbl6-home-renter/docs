# Phase 7 — Community Service: Chat và Notification

> **Trạng thái:** Đã xếp lịch, bắt đầu trong It5; chạy song song với các task Phase 6 đã giao.
> **Phạm vi lịch:** It5 khởi động ngày 02/11/2026. Các iteration sau giữ theo thứ tự phụ thuộc; ngày It8 sẽ chốt khi gần lập lịch.
> **Thiết kế đã duyệt:** [Community Service design](../phase-6/discovery/community-service-design.md).
> **Backlog chi tiết:** [Community implementation backlog](../phase-6/discovery/community-service-implementation-backlog.md).

## Mục tiêu

Triển khai một Community Service dùng chung cho chat generic và business notification trên Web/Android. Chat hỗ trợ direct, group, contextual conversation, lịch sử, ảnh, realtime và unread. Inbox chỉ lưu thông báo nghiệp vụ; service nguồn quyết định recipient và nội dung. Community lưu rồi phân phối qua Socket/FCM theo preference.

## Phân công

| Người phụ trách | Vai trò trong Phase 7 | Phạm vi |
|---|---|---|
| `baoduong17` | Backend/Community owner | Community API, persistence, Socket, Media authorization, Notification, PushDevice, event consumer, bot reminder và tích hợp Gateway |
| `ThaiBao11125` | Web | Chat, quản trị nhóm, ảnh, notification inbox và cài đặt push trên Web |
| `tphuongin` | Android | Chat, đăng ký FCM token, notification inbox/push và deep link |

Các task Phase 6 hiện tại không bị đổi người hoặc dời iteration. Phase 7 là phần việc bổ sung; backend được giao trực tiếp cho `baoduong17` theo xác nhận của PM. Các PR cần reviewer khác theo quy trình repo.

## Lộ trình

| Iteration | Phạm vi | Người phụ trách | Mục tiêu kết thúc |
|---|---|---|---|
| **It5 · 02/11–08/11** | P7-01–06: đồng bộ contract, route/runtime, schema Conversation/Member/Message | `baoduong17` | Nền Community và schema Chat sẵn sàng; chưa phụ thuộc domain event publisher |
| **It6** | P7-07–12: tạo/list conversation, membership lifecycle, role và metadata; phối hợp CB-06–08 cho Socket/Media/Notification API | `baoduong17` | Chat REST conversation/group hoàn chỉnh |
| **It7** | P7-13–14: gửi/đọc history, mark-read/unread; CB-09–10 và CB-13–14: event delivery, Web/Android | Backend: `baoduong17`; Web: `ThaiBao11125`; Android: `tphuongin` | Chat và inbox cơ bản dùng được trên hai client; event delivery có thể kiểm chứng |
| **It8 · ngày chốt sau** | P7-CB-11–12, P7-CB-15–16: contextual sync, invoice/issue integration, bot reminder, staging/rollout | Backend: `baoduong17`; client support: `ThaiBao11125`, `tphuongin` | Tích hợp domain và phát hành sau khi producer/event payload đã sẵn sàng |

It5 là iteration bắt đầu Community, không phải cam kết hoàn tất toàn bộ service trong một iteration. It6–It8 là thứ tự dự kiến để giữ dependency; ngày chính thức sẽ được thêm vào `PROJECT_PLAN.md` khi lịch các iteration đó được chốt.

## Cổng review

- **A — Chat REST:** kiểm tra membership, group admin, history boundary, idempotency và read cursor trước khi nối Socket.
- **B — Backend chat/notification:** kiểm tra media authorization, inbox dedup, multi-device Socket/FCM và PushDevice.
- **C — Client:** kiểm tra Web/Android, reconnect, read sync, deep link và preference.
- **D — Tích hợp/phát hành:** chỉ nối domain publisher và bật production sau khi source event contract/recipient được duyệt.

## Ngoài phạm vi

IssueReport creation, `@issue`, Issue panel, mention, sửa/xóa message, file ngoài ảnh, email business notification, web push qua FCM và cron tự gửi bot reminder.

## Theo dõi

Danh sách task, owner, iteration, trạng thái và dependency nằm ở [issues/README.md](issues/README.md). Các task chi tiết đang được quản lý qua mã P7-CB-01–16 và backlog thiết kế ở Phase 6; issue code nhỏ hơn sẽ được tách theo template trước khi bắt đầu từng PR.
