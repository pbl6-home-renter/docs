# Phase 1 — Issues & Backlog

> Task tracking là **markdown** cho tới khi Linear/GitHub Projects được chốt (migrate khi đã setup, PM tự lo).
> Phase 1 theo `PROJECT_PLAN.md` §5 Phase 1: setup repos + freeze requirements.
> **Phạm vi issue:** tập trung quyết định kỹ thuật FE & Mobile. Các việc vận hành (Linear, tạo repo, Apidog, FCM-project, xin tài nguyên) do PM tự nhắc — không có issue.

## Status legend

`🟡 Open` · `🔵 In progress` · `🟢 Done`

## Issue list

| ID | Title | Assignee | Status | Depends on | Deliverable |
|----|-------|----------|--------|------------|-------------|
| [P1-01](P1-01-feature-platform-map.md) | Feature → Platform Map | PM (draft) + FE + Mobile (verify) | 🟡 Open | `feature-list.md`, `user-behavior-workflow.md`, `decisions.md` | `discovery/product-platform-map.md` (đã verify) |
| [P1-02](P1-02-fe-setup.md) | FE Web setup (tech / library / convention / agent skill) | FE | 🟡 Open | P1-01 | `discovery/fe-proposal.md` |
| [P1-03](P1-03-mobile-setup.md) | Mobile setup (tech / library / convention / agent skill) | Mobile | 🟡 Open | P1-01 | `discovery/mobile-proposal.md` |
| [P1-04](P1-04-shared-conventions.md) | Shared conventions (validation / error / format / image / API) | FE + Mobile (propose) · PM (chốt) | 🟡 Open | P1-02, P1-03 | `discovery/shared-conventions.md` |
| [P1-05](P1-05-ui-design.md) | UI Design (sitemap / wireframe / design system / thống nhất) | FE + Mobile · PM (duyệt) | 🟡 Open | P1-01, P1-02, P1-03, P1-04, P1-19 | `discovery/ui-fe-design.md`, `ui-mobile-design.md`, `ui-design-review.md` |
| [P1-07](P1-07-business-rules-freeze.md) | Business-Rules Freeze (7 areas → frozen v1.0) | PM + BE · AI (AI flows) · FE/Mobile (review) | 🟡 Open | P1-05, P1-06 | `business-rules.md` (frozen v1.0); cũng là input P1-19 |
| [P1-08](P1-08-update-requirement.md) | Update `requirement.md` (lock MVP + fix C4) | PM · BE/AI (review) | 🟡 Open | P1-07 | `requirement.md` (root SoT, locked MVP), C4 resolved |
| [P1-13](P1-13-ai-match-spec.md) | AI roommate Matching full-lifecycle spec (search → ký → ẩn profile) | AI · PM/BE/Mobile | 🟡 Open | P1-06 (feasibility), D21/D22/D26/D28/D29 | `discovery/ai-matching-spec.md` + DB fields cho P1-18 |
| [P1-14](P1-14-feas-realtime.md) | Realtime (WebSocket) feasibility → Property Chat (D24′) | BE · PM/Mobile/FE | 🟡 Open | Teacher feedback 27/08 | `phase-0/discovery/realtime-feasibility.md` (D24′ final) |
| [P1-18](P1-18-db-design-be.md) | Full MVP Database Design (ERD v1 + DDL, parallel với P1-07) | BE · PM/AI/FE/Mobile | 🟡 Open | D25/D18/D16/D22/D21/D26, P1-13 draft | `discovery/db-design.md` (draft, Phase-2-adjustable) |
| [P1-19](P1-19-user-flow-verify.md) | User Flow verify/finalize (tenant / landlord / admin / shared) | FE + Mobile · BE · AI · PM (chốt) | 🟡 Open | P1-07 (rules), P1-18 (DB) | `discovery/user_flow/*.md` (finalized, SoT cho P1-05) |

## Trật tự

```
P1-01 (feature map) → P1-02 FE + P1-03 Mobile (song song) → P1-04 (quy ước chung) → P1-19 (user-flow, dùng P1-07 rules) → P1-05 (UI design)
```

## PM tự nhắc (không có issue)

- Tạo 4 repo GitHub + seed README/AGENTS + branch protection.
- Setup Linear + mirror GitHub Projects + Notion wiki.
- Đồng bộ OpenAPI/Swagger ↔ Apidog.
- FCM Firebase project + VNPay sandbox + LLM API key (theo `product-sketch.md` §7).
