# Phase 0 — Exit Criteria & Review

> Status: ✅ **Go (with conditions)**
> Date: Mon 24/08 (D5) · Reviewed by: PM + team
> Source of truth: `discovery/decisions.md` (D1–D29), `feature-list.md`, `product-sketch.md`

## 1. Exit checklist

| # | Criterion | Status | Note |
|---|-----------|--------|------|
| 1 | User research & competitive analysis (P0-01) | ✅ Done | `market-analysis.md` updated (long-term + roommate competitors, gap #3) |
| 2 | Competitive UX review (P0-02) | ✅ Done | `discovery/p0-02/ux-web.md` + `discovery/p0-02/discovery-ux-mobile.md` |
| 3 | Vision, constraints & risks (P0-03) | ✅ Done | `discovery/vision.md` + `discovery/assumptions-risks.md` + `decisions.md` (D1–D29, D12 skipped) |
| 4 | Technical feasibility (P0-04) | ⏪ Deferred | Draft `discovery/tech-feasibility.md` exists; finalized in Phase 1 (BE) |
| 5 | AI feasibility (P0-05) | ⏪ Deferred | Draft `discovery/ai-feasibility.md` exists; finalized in Phase 1 (AI) |
| 6 | Use cases, MVP scope & feature list (P0-06) | ✅ Done | `feature-list.md` (MVP=24) + `issues/P0-06…` use-case list; team sign-off pending → logged as open item |
| 7 | Product sketch (P0-07) | ✅ Done | `product-sketch.md` consolidated from P0-03 + `feature-list.md`, customer-ready |
| 8 | Customer/teacher discussion | ⏸ Deferred (waived for 27/08) | Sketch is customer-ready; real interview not schedulable before 27/08 → moved to Phase 1; open questions carried in `product-sketch.md` §6 |
| 9 | Exit criteria + phase review | ✅ Done | This file |
| 10 | Hand-off brief (Phase 1) | ✅ Done | §3 below |

## 2. Phase review result

**Vote: Go (with conditions).** All Phase 0 discovery artifacts required for the 27/08 teacher presentation are complete and mutually consistent (requirement.md ↔ product-sketch.md ↔ feature-list.md ↔ discovery docs).

**Conditions / open items:**
- **C1 — Team sign-off on P0-06:** scope approved verbally; formal sign-off to be recorded in `decisions.md` (target: Phase 1 W5 teacher checkpoint).
- **C2 — Feasibility verdicts P0-04/P0-05:** drafts accepted as evidence; BE/AI to confirm in Phase 1 before code.
- **C3 — External customer interview:** deferred; when held, feedback may adjust `requirement.md` (scope SoT) — change-control via `decisions.md`. **Note 27/08:** 4 scope topics discussed pre-interview → recorded as **D16** (utility rate = landlord global default + building/room override), **D17** (CCCD-at-contract + tạm trú Phase 1+), `feature-list.md` 3.11/3.7/5.6 + out-of-scope (cleaning, full tạm trú), `product-sketch.md` §6 Q7–Q8. MVP count 24 → 25.
- **C4 — D10 persona name anomaly:** `decisions.md` D10 references "Linh" not present in `vision.md` §2 (only Minh) — fix in Phase 1 doc pass.

## 3. Hand-off brief — Phase 1 (Setup + requirements freeze)

**What carries over (approved, frozen unless re-decided):**
- Vision & value prop (two-sided, D1) — `discovery/vision.md`.
- Scope boundaries: long-term-only (D9), no feed (F2), **Full messenger ngoài Property Chat (D24′: chỉ chat phòng + chung toà, bot/`@issue`/`@mention`; voice/sticker/poll/read-receipt out-of-scope MVP)**, bill-splitting → Phase 1+ (D4).
- MVP feature set: Modules 1–6 per `feature-list.md` (26 MVP features).
- AI scope: 2 features (Auto-Description MVP, Matchmaking Stretch D28), provider-agnostic (D3).
- Cross-platform role model (D13): `roles` array; landlord-web + tenant-mobile primary.
- E-contract signing (D18): `template_upload` wet-sign only (bỏ OTP/PIN/`e_ack`).

**Tools to provision (Phase 1, after resource approval):**
- 4 repos: `pbl6-web` (React), `pbl6-mobile` (Kotlin), `pbl6-backend` (NestJS+PostgreSQL), `pbl6-ai` (FastAPI).
- Linear (backlog), Notion (wiki/decisions), Google Drive (submissions), Apidog (API spec sync from `pbl6-backend` Swagger).
- Free-tier deploy: Render + Neon + Vercel (~$0; ~$7 demo week buffer).

**What was approved vs deferred:**
- Approved: all Phase 0 discovery + MVP cut.
- Deferred to Phase 1+: P0-04/P0-05 finalization, customer interview, full-text RAG chatbot (D15 bỏ — nếu cần), ZNS/OA (D7), bill-splitting (D4), hybrid/short-term (D9).

**Next gate:** Phase 1 W5 (M1) — present frozen requirements + business rules to teacher; update `requirement.md` with any feedback.
