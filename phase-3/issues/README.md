# Phase 3 — Issues

> Scaffolding & first vertical slice (W7–8): NestJS scaffold, React web, Kotlin mobile, FastAPI AI, E2E vertical slice.  
> Checkpoint W9 (M3): demo skeleton vertical slice (Login → List rooms).

## Status legend

`🟡 Open` · `🔵 In progress` · `🟢 Done` · `⚪ Blocked` · `⏪ Deferred`

## Issue list

| ID | Title | Owner | Status | Due Date | Input | Output |
|----|-------|-------|--------|----------|-------|--------|
| [P3-01](P3-01-mobile-apidog-e2e-research.md) | Research: Triển khai Mobile End-to-End với Apidog Mock trước khi BE hoàn thiện | Mobile Lead · PM + BE review | 🟡 Open | 2026-09-29 | `phase-2/discovery/api-spec.md`, `api-conventions.md` | `discovery/mobile-apidog-e2e-research.md` |
| [P3-02](P3-02-microservices-architecture-research.md) | Research: Thiết kế kiến trúc Microservice cho PBL6 (tách 4 service) | BE Lead · PM + team review | 🔵 In progress | 2026-10-02 | `phase-2/discovery/api-spec.md`, `api-conventions.md`, `phase-1/discovery/database-design.md`, `phase-0/discovery/tech-feasibility.md` | `discovery/microservices-architecture.md`, `discovery/decisions.md` (D51–D58) |

## Phân công (dự kiến Phase 3)

| Role | Responsibility |
|------|----------------|
| **PM** | Task tracking, review deliverables, điều phối tích hợp slice, chuẩn bị demo M3, **chốt các câu hỏi mở của P3-02** (`discovery/microservices-architecture.md` §12) |
| **Mobile** | P3-01 (Apidog research), Android scaffold, auth screen, room browse slice |
| **FE** | Web scaffold, auth flow, landlord room management skeleton |
| **BE** | NestJS scaffold, PostgreSQL setup + migrations, Auth module, Apidog mock sync, **P3-02 (kiến trúc 4 service)** |
| **AI** | ⏸ Tạm dừng — chờ PM + GV chốt D51 (bỏ AI khỏi scope MVP) |

> **Lưu ý:** P3-02 đề xuất tách backend thành 4 service thay cho modular monolith. Trạng thái hiện tại là **🟡 Proposed** (D52–D58) và **⏸ Pending** (D51) — chưa được chấp thuận, nên phần scaffold Phase 3 bên dưới vẫn mô tả kế hoạch cũ. Cập nhật `README.md` của phase khi PM chốt.
