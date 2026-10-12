# Phase 4 — Issues

> Triển khai các dịch vụ cốt lõi (Core Services Implementation).  
> **Chặng 1:** Hoàn thiện `identity-service` (P4-01 đến P4-06, P4-11 đến P4-13) theo kiến trúc Clean Architecture, CQRS, Database-per-service (`identity_db`).

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
| [P4-11](P4-11-be-identity-password-reset-flow.md) | Triển khai Luồng Quên mật khẩu & Đặt lại mật khẩu (Password Reset Flow) | BE Dev | 🟡 Open | 2026-10-15 | `api-spec.md` §2 (API 5, 6), `api-conventions.md` | API `POST /auth/password-reset-requests`, `POST /auth/password-resets`, OTP/Token TTL 15m, MailService |
| [P4-12](P4-12-be-identity-admin-user-management.md) | Triển khai Phân hệ Quản trị Người dùng cho Admin (Admin User Management) | BE Dev | 🟡 Open | 2026-10-16 | `api-spec.md` §3 (API 10–15), P4-05 Guards | API `GET /users`, `GET /users/:id`, `PATCH /users/:id`, Action `lock`/`unlock`, `DELETE` soft-delete |
| [P4-13](P4-13-be-identity-admin-seeder.md) | Xây dựng Database Seeder & Khởi tạo Tài khoản Quản trị viên (Admin Initializer) | BE Dev | 🟡 Open | 2026-10-14 | `api-spec.md` §2 (D13), TypeORM DataSource | Script `npm run seed:admin`, cơ chế Idempotent, tài khoản Admin mặc định để test Web Console |

## Issue list — Frontend Web (pbl6-web)

| ID | Title | Owner | Status | Due Date | Input | Output |
|----|-------|-------|--------|----------|-------|--------|
| [P4-07](P4-07-fe-web-boilerplate-setup.md) | Setup Frontend Boilerplate (React + Vite + TypeScript) cho repo `pbl6-web` | FE Lead / Dev | 🟢 Done | 2026-10-11 | `api-conventions.md`, `Rentify_UI_Screen_Outline_v0.1.md`, D13 | Khởi tạo khung repo `pbl6-web`, packages, thư mục modular |
| [P4-10](P4-10-fe-web-boilerplate-refinement-and-mobile-alignment.md) | Hoàn thiện Boilerplate Frontend Web, Chuẩn hóa Network, Base UI & Đồng bộ Design System với Mobile (Rentify Core-UI) | FE Lead / Dev | 🟡 Open | 2026-10-14 | `fe/`, `mobile/core-ui/`, `api-conventions.md`, P4-07 | 100% files hoàn thiện mã nguồn, tokens đồng bộ Mobile, Interceptors + Auto Refresh, Layouts + Route Guards, Base UI & Feedback |

## Issue list — Backend Boilerplate & Cloud Database (Supabase)

| ID | Title | Owner | Status | Due Date | Input | Output |
|----|-------|-------|--------|----------|-------|--------|
| [P4-08](P4-08-be-boilerplate-supabase-setup-keepalive.md) | Setup kết nối Supabase PostgreSQL & Script Keepalive chống Pause cho Boilerplate | BE Dev / DevOps | 🟡 Open | 2026-10-14 | `boilerplate/backend/`, `free-tier-db-storage.md` §2/§4, D53/D56 | Cấu hình `DATABASE_URL` + SSL, script keepalive 1 WRITE / 1 READ + auto retention 100 rows, GitHub Actions cron 24h |

## Issue list — DevOps & Infrastructure (AWS EC2 & Deployment)

| ID | Title | Owner | Status | Due Date | Input | Output |
|----|-------|-------|--------|----------|-------|--------|
| [P4-09](P4-09-devops-aws-account-ec2-provisioning.md) | Chuẩn bị thẻ Credit, đăng ký AWS ($200 Credits), cấu hình Billing Alert & khởi tạo EC2 | DevOps / Infra | 🟡 Open | 2026-10-14 | Email `@dut.udn.vn`, D56 EC2, GitHub Pack | Tài khoản AWS nạp $100–$200 credit, Billing Alert qua email, EC2 Ubuntu chạy Docker & Swap RAM |

*(Các issue tiếp theo cho `tenancy-service` như Building, Room, Contract sẽ được mở nối tiếp sau khi hoàn thành Chặng 1)*
