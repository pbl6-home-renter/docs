# P7-05 — Lưu membership và read boundary

**Assignee:** `baoduong17` · **Iteration:** It5 · **Ước lượng:** 3 points
**Repo:** `community-service` · **Phụ thuộc:** P7-04 · **Trạng thái:** 🟡 Open

## Context agent

Đọc `community-service/AGENTS.md` và skills `be-feature-workflow`, `be-structure`, `be-naming`; mục ERD v1 (§3) trong [Community design](../../phase-6/discovery/community-service-design.md), business rules BL-02/03/08/10/11/12 và ERD-01/02/10/13 trong cùng tài liệu; `api-docs/src/schemas/chat/conversation-member.yaml`.

## Quy tắc đã chốt

Membership giữ lại sau leave/kick với status `active|read_only`, role `admin|member|system`, `joinedAt`, `leftAt`, `leftSequence` và `lastReadSequence`. Read-only chỉ đọc tới `leftSequence`; re-add kích hoạt row cũ, xem toàn bộ history và unread chỉ tính tin mới từ lúc thêm lại. Direct reopen kích hoạt cả hai member.

## Phạm vi và acceptance

- [ ] Tạo domain/persistence/migration cho ConversationMember, gồm participant user/system theo ERD.
- [ ] Membership liên kết Conversation bằng FK cùng database; `userId` chỉ là ID tham chiếu, không FK Identity.
- [ ] Có trạng thái, role, timestamps và sequence cursor cần cho các luồng sau.
- [ ] Migration không đụng bảng outbox/inbox đã tồn tại; chạy/revert/run được.
- [ ] Build/lint pass; ghi mapping và quyết định index trong PR.

## Không làm

- Không triển khai HTTP endpoint, đồng bộ ContractMember/building, Socket join/leave hoặc xử lý quyền trong Media.
- Không hard-delete membership hoặc tạo bảng Message trong issue này.
