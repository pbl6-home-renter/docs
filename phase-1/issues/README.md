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
| [P1-05](P1-05-ui-design.md) | UI Design (sitemap / wireframe / design system / thống nhất) | FE + Mobile · PM (duyệt) | 🟡 Open | P1-01, P1-02, P1-03, P1-04 | `discovery/ui-fe-design.md`, `ui-mobile-design.md`, `ui-design-review.md` |

## Trật tự

```
P1-01 (feature map) → P1-02 FE + P1-03 Mobile (song song) → P1-04 (quy ước chung) → P1-05 (UI design)
```

## PM tự nhắc (không có issue)

- Tạo 4 repo GitHub + seed README/AGENTS + branch protection.
- Setup Linear + mirror GitHub Projects + Notion wiki.
- Đồng bộ OpenAPI/Swagger ↔ Apidog.
- FCM Firebase project + VNPay sandbox + LLM API key (theo `product-sketch.md` §7).
