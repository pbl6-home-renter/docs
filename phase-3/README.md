# Phase 3 — Scaffolding & First Vertical Slice (W7–8)

> **Checkpoint:** W9 (M3) — demo skeleton vertical slice (Login → List rooms → Room detail).  
> **Input từ Phase 2:** `product-platform-map.md`, `wire_frame/`, `erd-v1.md`, `api-conventions.md`, `api-spec.md` (109 endpoints), `diagrams/`, decisions D39–D50.

## Scope

1. **Backend:** NestJS scaffold, DB schema + migrations, auth module, OpenAPI Swagger setup.
2. **Web:** Scaffold React + Vite, navigation, auth/login screen, landlord room management skeleton.
3. **Mobile:** Scaffold Kotlin/Android, navigation, login screen, tenant room browse slice.
4. **AI:** FastAPI service scaffold, secure key configuration, `/health`, prompt adapter stub.
5. **API & Integration:** Apidog mock environment, contract sync, first vertical slice integration (Login → List rooms).
6. **Deployment:** Backend + Web staging deployment baseline (Railway/Fly.io + Vercel).

## Flow

```
Phase 2 Design Frozen (API Spec + Wireframes + ERD)
    ↓
P3-01: Research Mobile E2E via Apidog Mock (song song hóa FE/Mobile với BE)
    ↓
Scaffolding (Backend NestJS · Web React · Mobile Android · AI FastAPI)
    ↓
Auth Module & Token Flow (BE Auth + Web/Mobile Login)
    ↓
Vertical Slice: Public Room Browsing (BE /rooms + Mobile / Web UI)
    ↓
Deploy Staging & Checkpoint W9 (M3) Demo ✓
```

## Output

| Artifact | Location |
|----------|----------|
| Phase 3 Discovery & Research | `pm/phase-3/discovery/` |
| Microservice Architecture (P3-02) | `discovery/microservices-architecture.md` |
| Data Boundary per Service (P3-03, D53) | `discovery/database-per-service.md` |
| Free-tier DB/Storage research + POC + keepalive (P3-04) | `discovery/free-tier-db-storage.md`, `discovery/decisions.md` (D59+) |
| Backend Scaffold & API | Repo `pbl6-backend` |
| Web Scaffold & Console | Repo `pbl6-web` |
| Mobile Scaffold & Tenant App | Repo `pbl6-mobile` |
| AI Service Scaffold | Repo `pbl6-ai` |
| Decisions Log | `pm/phase-3/discovery/decisions.md` |

## Issues

Xem [issues/README.md](issues/README.md) cho danh sách task, phân công và tiến độ chi tiết.
