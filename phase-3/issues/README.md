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
| [P3-03](P3-03-database-per-service-design.md) | Hiện thực hoá D53: ranh giới dữ liệu theo service (database-per-service) | BE Lead · PM review | 🔵 In progress | 2026-10-09 | `phase-1/discovery/database-design.md`, `discovery/decisions.md` D52–D58, `discovery/microservices-architecture.md` §3, §6 | `discovery/database-per-service.md`, cập nhật `database-design.md` (§1 + 24 marker `Service`) |
| [P3-04](P3-04-free-tier-db-storage-poc.md) | Nghiên cứu & POC nguồn DB/Storage free (Supabase/Neon/R2…) + script keepalive chống bị pause | BE Lead · PM (ngân sách) + FE/Mobile review | 🟡 Open | 2026-10-09 | `phase-2/discovery/decisions.md` D40, `discovery/decisions.md` D53/D56, `phase-0/discovery/tech-feasibility.md` §6, `assumptions-risks.md` R5, `phase-1/discovery/database-design.md` §2.25 | `discovery/free-tier-db-storage.md`, `discovery/decisions.md` (D59+), POC + script keepalive (ngoài hub repo) |

## Phân công (dự kiến Phase 3)

| Role | Responsibility |
|------|----------------|
| **PM** | Task tracking, review deliverables, điều phối tích hợp slice, chuẩn bị demo M3, **chốt các câu hỏi mở của P3-02** (`discovery/microservices-architecture.md` §12) và **duyệt D52–D58** để P3-03 dùng được làm schema, **quyết ngân sách + chọn provider** cho P3-04 |
| **Mobile** | P3-01 (Apidog research), Android scaffold, auth screen, room browse slice |
| **FE** | Web scaffold, auth flow, landlord room management skeleton; hỗ trợ P3-04 (giới hạn size/MIME khi upload) |
| **BE** | NestJS scaffold, PostgreSQL setup + migrations, Auth module, Apidog mock sync, **P3-02 (kiến trúc 4 service)**, **P3-03 (ranh giới dữ liệu, register 24 cột FK chéo)**, **P3-04 (research + POC provider free + keepalive script)** |
| **AI** | ⏸ Tạm dừng — chờ PM + GV chốt D51 (bỏ AI khỏi scope MVP) |

> **Lưu ý:** P3-02 đề xuất tách backend thành 4 service thay cho modular monolith. Trạng thái hiện tại là **🟡 Proposed** (D52–D58) và **⏸ Pending** (D51) — chưa được chấp thuận, nên phần scaffold Phase 3 bên dưới vẫn mô tả kế hoạch cũ. Cập nhật `README.md` của phase khi PM chốt.
>
> **P3-03 đi trước P3-02 một bước về mặt tài liệu:** nó hiện thực hoá hệ quả của D53 (ranh giới dữ liệu, register FK chéo, 4 ERD, ma trận role/grant) để BE không phải đoán khi scaffold. Nhưng nó **không** đi trước về mặt quyết định — toàn bộ nội dung đánh dấu 🟡 Draft và chỉ dùng được làm schema sau khi PM duyệt D52 + D53. 4 câu hỏi chặn nằm ở `discovery/database-per-service.md` §9.
>
> **P3-04 chạy song song P3-03, cùng hạn 09/10.** Nó cấp dữ liệu để PM chốt **D56** (tự host EC2 vs managed free tier) và trả lời câu hỏi chặn của D53: free tier nào chịu được **4 database + 4 Postgres role**? Câu hỏi cần PM: có được cấp EC2 / ngân sách không.
