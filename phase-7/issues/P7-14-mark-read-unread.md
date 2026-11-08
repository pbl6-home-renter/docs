# P7-14 — Mark-read và unread count theo conversation

**Assignee:** `baoduong17` · **Iteration:** It6 · **Ước lượng:** 2 points
**Repo:** `community-service` · **Phụ thuộc:** P7-05, P7-06, P7-08, P7-13 · **Trạng thái:** 🟢 Done

## Context agent

Đọc backend `AGENTS.md`, feature/API presentation skills; OpenAPI `POST /messages/mark-read` (`postMessagesMarkRead`) và `MessageMarkReadRequestDto/ResponseDto` sau P7-01; BL-15 và ERD-11/13.

## Hành vi đã chốt

Read state thuộc membership của user, không thuộc device. Body gồm `conversationId` và `lastReadSequence`; chỉ cho cursor tiến lên. Unread là số message mới trong conversation chưa đọc, không có receipt đã xem từng message. Khi rời/bị kick chỉ tính phần được quyền đọc; khi re-add cursor bắt đầu từ thời điểm được thêm lại.

## Acceptance

- [ ] Mark-read yêu cầu membership có quyền đọc; xác thực sequence thuộc conversation và không vượt message cuối.
- [ ] Cursor chỉ tăng; request lặp an toàn; unread count không âm.
- [ ] Response khớp schema/status/code OpenAPI; mọi session khác có thể nhận state update qua Socket ở task realtime.
- [ ] Apidog kiểm tra cursor tiến/lùi/lặp, sequence sai, read-only boundary và unread count; build/lint pass.

## Không làm

- Không per-message read receipt, notification inbox read state, Socket fan-out hoặc FCM.
