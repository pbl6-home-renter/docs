# Discovery — Doc Index

> Danh mục 17 file trong `discovery/`. **Canonical (source of truth) = 4 file đầu.** Còn lại là research artifacts nuôi các decision. Khi nghi ngờ đọc gì → tra bảng này; chi tiết quyết định luôn ở `decisions.md`.

## Canonical (đọc khi cần quyết định / báo cáo)

| File | Nội dung | Liên quan |
|------|----------|-----------|
| `decisions.md` | **D1–D29 (22 active + 6 retired/merged)** — log quyết định duy nhất + Phụ lục A–E (spine, stress-test, talking points) | P0-03, D1–D29 |
| `vision.md` | Vision ≤4 câu, lifecycle break, personas (Chú Hùng, Chị Mai, Minh) | P0-03 |
| `assumptions-risks.md` | Assumptions A1–A10 + risks | P0-03 |
| `exit-criteria.md` | Checklist thoát Phase 0 (Go with conditions C1–C4) | P0-07 |

## User research (P0-01)

| File | Nội dung |
|------|----------|
| `P0-01-user_research.md` | Pain points top-5 ranked F×S |
| `P0-01-report.md` | Interview transcript thô |
| `P0-01-landlor_report.md` | Workflow người cho thuê |
| `P0-01-tenant_report.md` | Workflow người thuê |

## Competitive UX (P0-02)

| File | Nội dung |
|------|----------|
| `p0-02/ux-web.md` | Landlord web competitor notes |
| `p0-02/discovery-ux-mobile.md` | Tenant mobile competitor (Chợ Tốt, NhaTro VN, Rencity) |

## Feasibility (draft → finalize tại P1-05 / P1-06)

| File | Nội dung | Trạng thái |
|------|----------|------------|
| `tech-feasibility.md` | Hạ tầng, 10 entities, VNPay/MoMo, Render+Neon+Vercel ~$0 | 🟡 Draft (P0-04 → P1-05) |
| `ai-feasibility.md` | 3 luồng AI feasibility + adapter provider (D3) | 🟡 Draft (P0-05 → P1-06) |

## Decision-support research (mỗi file 1 topic — quyết định đã chốt ở `decisions.md`)

| File | Topic | Decision | Issue |
|------|-------|----------|-------|
| `market-roommate-models.md` | Landlord intervention / HĐ&payment ở ghép / lịch sử uy tín | D21, D22, D26 | P1-16 ✅ |
| `short-vs-long-term-analysis.md` | Kết hợp thuê ngắn+dài hạn? | D9 | P1-17 ✅ |
| `ownership-model.md` | Ownership DB (nhiều chủ / 1 chủ-phòng) | D25 ⏳ | P1-12 |
| `ai-matching-spec.md` | AI roommate matching spec (Stretch) | D28 | P1-13 |
| `tam-tru-api-research.md` | Census tạm trú public API | D17 | P1-15 |
| `realtime-feasibility.md` | WebSocket/Property Chat feasibility (options, kiến trúc, bot/command, effort, docs) | D24′ | **P1-14** |

## Verification & workflow audit (Decision cross-check)

| File | Nội dung | Liên quan |
|------|----------|-----------|
| `user-behavior-workflow.md` | End-to-end User Behavior Story (A→Z rental lifecycle) verifying D16/D17/D18/D22/D25/D29 interlock + failure-mode audit | D16–D29 cross-check |

## Ghi chú

- Canonic scope: `pm/phase-0/requirement.md` (scope) + `pm/phase-0/PROJECT_PLAN.md` (schedule). Business rules sẽ freeze tại `pm/phase-1/business-rules.md` (P1-07).
- Decision flow: research artifact → quyết định ở `decisions.md` → phản ánh vào `feature-list.md` + `business-rules.md`.