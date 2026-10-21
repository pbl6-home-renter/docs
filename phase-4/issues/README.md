# Phase 4 — Issues

> Triển khai các dịch vụ cốt lõi (Core Services Implementation).  
> P4-01 đến P4-06 và P4-11 đến P4-13 là các issue Identity hiện có. P4-15, P4-17 đến P4-19 và P4-21, P4-24 đến P4-25 là các task bổ sung cho Apidog, frontend foundation và `tenancy-service`.

## Status legend

`🟡 Open` · `🔵 In progress` · `🟢 Done` · `⚪ Blocked` · `⏪ Deferred`

## Issue list — Chặng 1: Identity Service

| ID | Title | Owner | Status | Due Date | Input | Output |
|----|-------|-------|--------|----------|-------|--------|
| [P4-01](P4-01-be-identity-boilerplate-setup.md) | Setup boilerplate, Base Entity & Conventions cho Identity Service | BE Lead / Dev | 🟢 Done | 2026-10-10 | `boilerplate/backend/`, `api-conventions.md`, `database-design.md` §2.0 | Base code port 3001, BaseEntity `is_deleted`, Response/Exception filter chuẩn |
| [P4-02](P4-02-be-identity-database-migration.md) | Thiết kế TypeORM Entities & Migration CSDL `identity_db` | BE Lead / Dev | 🟢 Done | 2026-10-11 | `database-design.md` §2.1/§2.3, `database-per-service.md`, D53 | Migration 3 bảng: `users`, `landlord_profiles`, `refresh_tokens` |
| [P4-03](P4-03-be-identity-core-auth-register-login.md) | Triển khai Auth Use-cases: Register & Login (CQRS) | BE Lead / Dev | 🟢 Done | 2026-10-12 | `api-spec.md` §2 (API 1, 2), `api-conventions.md` | API `POST /auth/register`, `POST /auth/login`, Bcrypt, HttpOnly cookie |
| [P4-04](P4-04-be-identity-token-rotation-logout.md) | Triển khai Token Rotation & Logout (Quản lý phiên) | BE Lead / Dev | 🔵 In progress | 2026-10-13 | `api-spec.md` §2 (API 3, 4), D55 §5.4.1 | API `POST /auth/refresh`, `POST /auth/logout`, Token reuse detection |
| [P4-05](P4-05-be-identity-user-profile-and-guards.md) | Triển khai Guards, User Profile & Đổi mật khẩu | BE Lead / Dev | 🟢 Done | 2026-10-14 | `api-spec.md` §3 (API 7, 8, 9), D39 payoutAccount | `JwtAuthGuard`, `RolesGuard`, API `GET /me`, `PATCH /me`, `PUT /me/password` |
| [P4-06](P4-06-be-identity-jwks-stateless-verification.md) | Cấu hình RS256 JWT & Expose JWKS Endpoint cho Microservices | BE Lead / Dev | 🟢 Done | 2026-10-15 | D55, D58, RFC 7517 | Endpoint `GET /.well-known/jwks.json`, RS256 signing, public key doc |
| [P4-11](P4-11-be-identity-password-reset-flow.md) | Triển khai Luồng Quên mật khẩu & Đặt lại mật khẩu (Password Reset Flow) | BE Dev | 🟢 Done | 2026-10-15 | `api-spec.md` §2 (API 5, 6), `api-conventions.md` | API `POST /auth/password-reset-requests`, `POST /auth/password-resets`, OTP/Token TTL 15m, MailService |
| [P4-12](P4-12-be-identity-admin-user-management.md) | Triển khai Phân hệ Quản trị Người dùng cho Admin (Admin User Management) | BE Dev | 🟢 Done | 2026-10-16 | `api-spec.md` §3 (API 10–15), P4-05 Guards | API `GET /users`, `GET /users/:id`, `PATCH /users/:id`, Action `lock`/`unlock`, `DELETE` soft-delete |
| [P4-13](P4-13-be-identity-admin-seeder.md) | Xây dựng Database Seeder & Khởi tạo Tài khoản Quản trị viên (Admin Initializer) | BE Dev | 🟢 Done | 2026-10-14 | `api-spec.md` §2 (D13), TypeORM DataSource | Script `npm run seed:admin`, cơ chế Idempotent, tài khoản Admin mặc định để test Web Console |

## Issue list — Frontend Web (pbl6-web)

| ID | Title | Owner | Status | Due Date | Input | Output |
|----|-------|-------|--------|----------|-------|--------|
| [P4-07](P4-07-fe-web-boilerplate-setup.md) | Setup Frontend Boilerplate (React + Vite + TypeScript) cho repo `pbl6-web` | FE Lead / Dev | 🟢 Done | 2026-10-11 | `api-conventions.md`, `Rentify_UI_Screen_Outline_v0.1.md`, D13 | Khởi tạo khung repo `pbl6-web`, packages, thư mục modular |
| [P4-10](P4-10-fe-web-boilerplate-refinement-and-mobile-alignment.md) | Hoàn thiện Boilerplate Frontend Web, Chuẩn hóa Network, Base UI & Đồng bộ Design System với Mobile (Rentify Core-UI) | FE Lead / Dev | 🟡 Open | 2026-10-14 | `fe/`, `mobile/core-ui/`, `api-conventions.md`, P4-07 | 100% files hoàn thiện mã nguồn, tokens đồng bộ Mobile, Interceptors + Auto Refresh, Layouts + Route Guards, Base UI & Feedback |

## Issue list — Backend Boilerplate & Cloud Database (Supabase)

| ID | Title | Owner | Status | Due Date | Input | Output |
|----|-------|-------|--------|----------|-------|--------|
| [P4-08](P4-08-be-boilerplate-supabase-setup-keepalive.md) | Setup kết nối Supabase PostgreSQL & Script Keepalive chống Pause cho Boilerplate | BE Dev / DevOps | 🟢 Done | 2026-10-14 | `boilerplate/backend/`, `free-tier-db-storage.md` §2/§4, D53/D56 | Cấu hình `DATABASE_URL` + SSL, script keepalive 1 WRITE / 1 READ + auto retention 100 rows, GitHub Actions cron 24h |

## Issue list — DevOps & Infrastructure (AWS EC2 & Deployment)

| ID | Title | Owner | Status | Due Date | Input | Output |
|----|-------|-------|--------|----------|-------|--------|
| [P4-09](P4-09-devops-aws-account-ec2-provisioning.md) | Chuẩn bị thẻ Credit, đăng ký AWS ($200 Credits), cấu hình Billing Alert & khởi tạo EC2 | DevOps / Infra | 🟢 Done | 2026-10-14 | Email `@dut.udn.vn`, D56 EC2, GitHub Pack | Tài khoản AWS nạp $100–$200 credit, Billing Alert qua email, EC2 Ubuntu chạy Docker & Swap RAM |

## Issue list — Apidog & Authentication Integration

| ID | Title | Owner | Status | Estimate | Output |
|----|-------|-------|--------|----------|--------|
| [P4-15](P4-15-apidog-environment-and-token-automation.md) | Cấu hình nền tảng Apidog và tự động hóa authentication flow | BE/API Lead + PM | 🟡 Open | 8 pts · 18–24h | Environment, token capture, Authorization và refresh flow trên Apidog |

## Issue list — API Contract Governance

| ID | Title | Owner | Status | Estimate | Output |
|----|-------|-------|--------|----------|--------|
| [P4-27](P4-27-api-contract-change-log-research.md) | Research & POC: Automated API Contract Change Log | BE/API Lead + PM review | 🟡 Open | 5 pts · 10–16h | OpenAPI change-tracking recommendation, runnable POC, readable change report and rollout proposal |

## Issue list — Frontend Foundation

| ID | Title | Owner | Status | Estimate | Output |
|----|-------|-------|--------|----------|--------|
| [P4-17](P4-17-fe-google-stitch-research.md) | Google Stitch Research & Base UI Proposal | FE Dev | 🟡 Open | 5 pts · 8–12h | Member tự inspect Stitch và đề xuất phạm vi component cần code |
| [P4-18](P4-18-fe-base-ui-components.md) | Implement Base UI Components từ kết quả Stitch | FE Dev / FE Lead | 🟢 Done | 13 pts · 24–48h | Design tokens và bộ base/feedback components dùng chung |
| [P4-19](P4-19-fe-application-shell.md) | Implement Tenant, Landlord & Admin Application Shell | FE Dev / FE Lead | 🟢 Done | 8 pts · 18–24h | Layout, navigation, route guard và shell theo role |

## Issue list — Tenancy Service

| ID | Title | Owner | Status | Estimate | Output |
|----|-------|-------|--------|----------|--------|
| [P4-21](P4-21-tenancy-service-bootstrap.md) | Bootstrap `tenancy-service` theo Clean Architecture & DDD | BE Dev | 🟡 Open | 8 pts · 18–24h | Service skeleton, config, database và module boundaries |
| [P4-24](P4-24-tenancy-building-vertical-slice.md) | Building Vertical Slice | BE Dev | 🟡 Open | 8 pts · 18–24h | Building aggregate, API, transaction và outbox flow chạy được |
| [P4-25](P4-25-tenancy-room-vertical-slice.md) | Room Vertical Slice | BE Dev | 🟡 Open | 13 pts · 30–45h | Room aggregate, Building relationship, API và event flow |

`boilerplate` là nền tảng reference đã có sẵn Transactional Outbox. `tenancy-service` được tạo bằng cách fork repository này; không tạo task port/approve/verify Outbox riêng trong Phase 4.

## Planning notes

- P4-01 đến P4-06 và P4-11 đến P4-13 không được tạo lại; P1 Identity tiếp tục theo implementation hiện tại.
- P4-10 có phạm vi frontend cũ và có mobile alignment; phạm vi frontend mới cần theo P4-17 đến P4-19. Không giao thêm task Mobile trong batch này.
- P4-14 bị loại khỏi batch vì các service hiện tại đã tuân thủ convention prefix/environment.
- P4-16 được gộp vào P4-15; `api-docs` đã là nguồn contract hiện có, P4-15 chỉ cấu hình Apidog và token automation.
- P4-27 bổ sung nghiên cứu và POC cho việc tự động phát hiện, phân loại và ghi log thay đổi API contract; không phải runtime business audit log.
- P4-20, P4-22, P4-23 và P4-26 được loại khỏi batch theo quyết định của PM.
- P4-23 được thay thế bằng việc sử dụng `pm/phase-1/discovery/database-design.md` trong P4-21/P4-24/P4-25.
- P4-08 và P4-09 không nằm trong batch task mới vì server/database đã được chuẩn bị. PM có thể đóng hoặc đánh dấu deferred các issue hạ tầng cũ theo trạng thái thực tế.
