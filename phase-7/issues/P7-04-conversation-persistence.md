# P7-04 — Tạo Conversation generic và persistence

**Assignee:** `baoduong17` · **Iteration:** It5 · **Ước lượng:** 3 points
**Repo:** `community-service` · **Phụ thuộc:** P7-01, P7-03 · **Trạng thái:** 🟢 Done

## Context chuyển cho agent

Đọc `community-service/AGENTS.md`, skill `.agents/skills/be-feature-workflow/SKILL.md`, `.agents/skills/be-structure/SKILL.md`, module mẫu `src/modules/sample/`, `pm/phase-6/decisions.md` (D75), [Community design — ERD v1](../../phase-6/discovery/community-service-design.md) (§3), và OpenAPI `Conversation` schema sau P7-01.

## Quy tắc đã chốt

Conversation generic có `kind=direct|group`, context tùy chọn (`contract|building` + ID), tên/avatar tùy chọn và người tạo. Không tạo FK sang database service khác. Chat direct có khóa cặp user chuẩn hóa duy nhất; contextual conversation có tối đa một conversation cho một context; group tự do không có context.

## Phạm vi

- Tạo domain aggregate/entity, TypeORM mapping, repository và migration cho Conversation.
- Lưu các trường tối thiểu theo ERD v1; unique constraint cho direct pair và context theo design.
- Migration phải được sinh bằng TypeORM CLI, rà và bỏ thay đổi ngoài issue.

## Acceptance

- [ ] Domain không import NestJS/TypeORM; persistence adapter map đầy đủ hai chiều.
- [ ] DB ngăn được direct pair/context trùng khi có request đồng thời.
- [ ] Không có foreign key tới User/Tenancy DB.
- [ ] Migration run/revert/run theo backend workflow; build/lint pass.

## Không làm

- Không tạo endpoint, membership/message tables, context event consumer, hoặc thêm loại context ngoài `contract|building`.
- Nếu chọn cách biểu diễn unique/partial index cần quyết định kỹ thuật, ghi rõ trong PR; không thay đổi business rule.
