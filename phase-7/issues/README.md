# Phase 7 — Community Service task tracker

Phase 7 bắt đầu song song trong It5 (02/11–08/11). Các task Phase 6 giữ nguyên. Mỗi issue dưới đây có đủ bối cảnh để giao độc lập cho agent; issue không thay thế `AGENTS.md`/skill của repo và không được tự tạo business rule.

## It5 — bắt đầu Chat REST

| ID | Issue | Repo | Assignee | Ước lượng | Phụ thuộc |
|---|---|---|---|---:|---|
| P7-01 | [Đồng bộ OpenAPI Chat v1](P7-01-chat-openapi-alignment.md) | api-docs | `baoduong17` | 2 | — |
| P7-02 | [Route API Community/PushDevice](P7-02-gateway-community-routes.md) | api-gateway | `baoduong17` | 1 | — |
| P7-03 | [Bật Community runtime nội bộ](P7-03-community-internal-runtime.md) | infra, community-service | `baoduong17` | 1 | — |
| P7-04 | [Conversation generic persistence](P7-04-conversation-persistence.md) | community-service | `baoduong17` | 3 | P7-01, P7-03 |
| P7-05 | [ConversationMember persistence](P7-05-conversation-member-persistence.md) | community-service | `baoduong17` | 3 | P7-04 |
| P7-06 | [Message persistence/sequence/idempotency](P7-06-message-persistence.md) | community-service | `baoduong17` | 3 | P7-04, P7-05 |

## It6 — tạo và quản lý conversation

| ID | Issue | Repo | Assignee | Ước lượng | Phụ thuộc |
|---|---|---|---|---:|---|
| P7-07 | [Tạo direct/group conversation](P7-07-create-direct-group.md) | community-service | `baoduong17` | 3 | P7-01, P7-04–06, CB-07 Media |
| P7-08 | [Liệt kê/đọc conversation](P7-08-list-conversations.md) | community-service | `baoduong17` | 3 | P7-04, P7-07 |
| P7-09 | [Xem/thêm thành viên](P7-09-list-add-members.md) | community-service | `baoduong17` | 3 | P7-05–07 |
| P7-10 | [Kick/leave và read-only boundary](P7-10-remove-leave-members.md) | community-service | `baoduong17` | 3 | P7-05–06, P7-09 |
| P7-11 | [Đổi role admin/member](P7-11-update-member-role.md) | community-service | `baoduong17` | 2 | P7-05–07 |
| P7-12 | [Sửa tên/ảnh group](P7-12-update-group-metadata.md) | community-service | `baoduong17` | 2 | P7-04, P7-06–07, CB-07 Media |

## It7 — message history và unread

| ID | Issue | Repo | Assignee | Ước lượng | Phụ thuộc |
|---|---|---|---|---:|---|
| P7-13 | [Gửi message/đọc history](P7-13-send-list-messages.md) | community-service | `baoduong17` | 3 | P7-05–07, CB-07 Media |
| P7-14 | [Mark-read/unread count](P7-14-mark-read-unread.md) | community-service | `baoduong17` | 2 | P7-05–08, P7-13 |

**Tổng dự kiến:** It5 13 points; It6 16 points; It7 5 points. Đây là estimate theo issue nhỏ, cần đối chiếu khả năng thực tế khi chốt iteration; không thay đổi task Phase 6 hiện có.

## Phân rã từ backlog cha

| Backlog cha | Issue con hiện tại |
|---|---|
| CB-01 Runtime/Gateway | P7-02, P7-03 |
| CB-02 Conversation/member schema | P7-04–05 |
| CB-03 Tạo/list direct/group | P7-07–08 |
| CB-04 Quản trị membership/group | P7-09–12 |
| CB-05 Message/history/unread | P7-06, P7-13–14 |

CB-06–16 được giữ ở backlog cấp cao và sẽ được tách tương tự trước khi đến iteration tương ứng. `baoduong17` phụ trách backend; `ThaiBao11125` Web và `tphuongin` Android theo [Phase 7 plan](../README.md). Chưa tạo issue bên ngoài trên GitHub Projects.

## Cách giao cho agent

Gửi nguyên file issue tương ứng cho agent. Issue nêu repo, nguồn chuẩn, rule đã chốt, phạm vi, acceptance và kiểm tra. Agent vẫn phải đọc `AGENTS.md` cùng skill bắt buộc trong repo đích; nếu tài liệu/code mâu thuẫn, theo D75 và ghi blocker, không tự bịa hướng xử lý.
