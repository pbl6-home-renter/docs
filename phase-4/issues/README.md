# Phase 4 — Issues

> Triển khai các dịch vụ cốt lõi (Core Services Implementation).  
> **Chặng 1:** Hoàn thiện `identity-service` (P4-01 đến P4-06) theo kiến trúc Clean Architecture, CQRS, Database-per-service (`identity_db`).

## Status legend

`🟡 Open` · `🔵 In progress` · `🟢 Done` · `⚪ Blocked` · `⏪ Deferred`

## Issue list — Chặng 1: Identity Service

| ID | Title | Owner | Status | Due Date | Input | Output |
|----|-------|-------|--------|----------|-------|--------|
| [P4-01](P4-01-be-identity-boilerplate-setup.md) | Setup boilerplate, Base Entity & Conventions cho Identity Service | BE Lead / Dev | 🟡 Open | 2026-10-10 | `boilerplate/backend/`, `api-conventions.md`, `database-design.md` §2.0 | Base code port 3001, BaseEntity `is_deleted`, Response/Exception filter chuẩn |
| [P4-02](P4-02-be-identity-database-migration.md) | Thiết kế TypeORM Entities & Migration CSDL `identity_db` | BE Lead / Dev | 🟡 Open | 2026-10-11 | `database-design.md` §2.1/§2.3, `database-per-service.md`, D53 | Migration 3 bảng: `users`, `landlord_profiles`, `refresh_tokens` |
| [P4-03](P4-03-be-identity-core-auth-register-login.md) | Triển khai Auth Use-cases: Register & Login (CQRS) | BE Lead / Dev | 🟡 Open | 2026-10-12 | `api-spec.md` §2 (API 1, 2), `api-conventions.md` | API `POST /auth/register`, `POST /auth/login`, Bcrypt, HttpOnly cookie |
| [P4-04](P4-04-be-identity-token-rotation-logout.md) | Triển khai Token Rotation & Logout (Quản lý phiên) | BE Lead / Dev | 🟡 Open | 2026-10-13 | `api-spec.md` §2 (API 3, 4), D55 §5.4.1 | API `POST /auth/refresh`, `POST /auth/logout`, Token reuse detection |
| [P4-05](P4-05-be-identity-user-profile-and-guards.md) | Triển khai Guards, User Profile & Đổi mật khẩu | BE Lead / Dev | 🟡 Open | 2026-10-14 | `api-spec.md` §3 (API 7, 8, 9), D39 payoutAccount | `JwtAuthGuard`, `RolesGuard`, API `GET /me`, `PATCH /me`, `PUT /me/password` |
| [P4-06](P4-06-be-identity-jwks-stateless-verification.md) | Cấu hình RS256 JWT & Expose JWKS Endpoint cho Microservices | BE Lead / Dev | 🟡 Open | 2026-10-15 | D55, D58, RFC 7517 | Endpoint `GET /.well-known/jwks.json`, RS256 signing, public key doc |

## Issue list — Frontend Web (pbl6-web)

| ID | Title | Owner | Status | Due Date | Input | Output |
|----|-------|-------|--------|----------|-------|--------|
| [P4-07](P4-07-fe-web-boilerplate-setup.md) | Setup Frontend Boilerplate (React + Vite + TypeScript) cho repo `pbl6-web` | FE Lead / Dev | 🟡 Open | 2026-10-13 | `api-conventions.md`, `Rentify_UI_Screen_Outline_v0.1.md`, D13 | Repo `pbl6-web` chuẩn Vite/React/Tailwind (UI tự build/custom template), Axios Interceptors, Auth & Dashboard layout |

*(Các issue tiếp theo cho `tenancy-service` như Building, Room, Contract sẽ được mở nối tiếp sau khi hoàn thành Chặng 1)*
