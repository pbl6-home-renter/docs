# Phase 2 — Issues

> Design phase (W5–6): feature map, wireframe, ERD, API spec, diagrams.
> Checkpoint W7 (M2): design frozen.

## Status legend

`🟡 Open` · `🔵 In progress` · `🟢 Done` · `⚪ Cancelled`

## Issue list

| ID | Title | Owner | Status | Input | Output |
|----|-------|-------|--------|-------|--------|
| [P2-01](P2-01-feature-platform-map.md) | Feature → Platform Map (chỉ từ user flow) | PM (draft) + FE + Mobile (verify) | 🔵 In progress | user_flow/*.md | `discovery/product-platform-map.md` |
| [P2-02](P2-02-screen-list-sitemap.md) | ~~Screen List + Sitemap~~ (gộp P2-03) | — | ⚪ Cancelled | — | — |
| [P2-03](P2-03-wireframe.md) | Screen List + Sitemap + Wireframe | FE + Mobile · PM review | 🟡 Open | P2-01 | `discovery/wire_frame/` |
| [P2-04](P2-04-erd.md) | ERD v1 finalized | BE · PM review | 🟡 Open | P2-01, database-design.md | `discovery/erd-v1.md` |
| [P2-05](P2-05-api-spec.md) | API Spec v1 (OpenAPI/Swagger) | BE | 🟡 Open | P2-04, user_flow | `openapi.yaml` trong `pbl6-backend` |
| [P2-06](P2-06-diagrams.md) | Process Diagrams (use case, sequence, activity) | PM + BE | 🟡 Open | P2-01, P2-04, P2-05 | `discovery/diagrams/` |
| [P2-07](P2-07-design-freeze.md) | Design Review → Freeze | All | 🟡 Open | P2-01–P2-06 | Design frozen ✓ |

## Dependency flow

```
P2-01 (Feature→Platform Map)
  │
  ├── P2-03 (Screen List + Sitemap + Wireframe)
  │
  ├── P2-04 (ERD) ──── P2-05 (API Spec)
  │
  └── P2-06 (Diagrams)
        │
    P2-07 (Freeze)
```

## Phân công

| Role | Tasks |
|------|-------|
| **PM** | P2-01 (draft), P2-06 (diagrams), P2-07 (review) |
| **FE** | P2-01 (verify), P2-03 (wireframe web) |
| **Mobile** | P2-01 (verify), P2-03 (wireframe mobile) |
| **BE** | P2-04 (ERD), P2-05 (API spec) |
| **AI** | — (Phase 3) |

## Flow

1. P2-01: List feature từ user flow → map platform → verify
2. P2-03: Screen list + sitemap + wireframe (gộp)
3. P2-04: ERD finalized
4. P2-05: API spec trên ERD
5. P2-06: Process diagrams
6. P2-07: Review → freeze
