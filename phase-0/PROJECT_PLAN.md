# PBL6 — Project Plan (13–14 weeks)

> Canonical plan owned by the PM. Update this file whenever scope, schedule, or ownership changes.
> Tooling: Linear (tasks) · GitHub (code) · Notion (wiki/decisions) · Google Drive (official submissions).
> Note: tools/repos are provisioned **after** boss approves resources (targeted for Phase 1). Until then, Phase 0 runs docs-only.

## 1. Vision & scope

A two-sided long-term rental-management platform (landlord ops + tenant portal) with AI-assisted roommate matching; **Property Chat platform (D24′) thay thế no-messenger**: integration-first via FCM, chat riêng phòng + chung toà, bot auto-remind, `@issue`, `@mention`, realtime Socket.io khi app mở + DB persistence (no built-in social feed — F2). Tenant portal is optional/passive under D29 resilience — the system must run end-to-end with zero tenant logins (landlord operates solo via QR/cash).

- **Web (React)** — Primary: landlord ops console (room/building, e-contracts+signing, OCR utility closing, invoice/payment tracking, statistics). Secondary: tenant responsive portal (D13).
- **Mobile (Kotlin/Android)** — Primary: tenant portal (map search, invoices, payment, roommate, issue reporting). Secondary: landlord lite — FCM push, duyệt sự cố, dashboard/hóa đơn (D13).
- **AI (Python/FastAPI, provider-agnostic adapter — OpenAI/Gemini via env, D3)** — (1) Auto-Description (MVP), (2) Matchmaking score + advice (Stretch, D28).

**MVP cut:** full utility-closing (OCR) + contract (template_upload wet-sign signing — no OTP/PIN) + invoice/payment (incl. dynamic-QR reconciliation) flow end-to-end; 2 AI features — Auto-Description (MVP), Matchmaking (Stretch, D28). Anything beyond `feature-list.md` MVP is stretch.

## 2. Team & ownership

| Member | Role | Repo | Main deliverables |
|--------|------|------|-------------------|
| (PM)   | Project manager | `PBL6` (docs hub) | Requirements, plan, tracking, diagrams, reports |
| FE     | Frontend | `pbl6-web` | Web UI (landlord/admin) |
| Mobile | Android | `pbl6-mobile` | Tenant app |
| BE     | Backend | `pbl6-backend` | NestJS API, DB, Swagger/Apidog |
| AI     | AI engineer | `pbl6-ai` | FastAPI service, prompts, OpenAI integration |

## 3. Tooling & conventions (summary)

| Concern | Tool | Role |
|---------|------|------|
| Tasks | **Linear** | Single source of truth for backlog/sprint/issues |
| PR & CI state | **GitHub Projects** | Per-repo board mirroring PR ↔ issue |
| Wiki, notes, decisions | **Notion** | Meeting notes, decision log, research |
| Official submissions | **Google Drive** | Teacher-facing reports, PPT, final docs |
| API contract | **Swagger (OpenAPI) + Apidog** | Canonical spec lives in `pbl6-backend`; sync to Apidog |
| Code hosting | **GitHub** | 4 repos (see table above) |

**Git flow (light GitFlow):** `main` (deployable) → `develop` (integration) → `feature/<linear-id>-<slug>`, plus `fix/`, `hotfix/`. Merge via squash PR, ≥1 reviewer, never push directly to `main`/`develop`.

**Language:** English for code, commits, PRs, API, and docs. Vietnamese allowed in teacher-facing reports only.

**Testing:** minimal by design (demo-grade). No mandatory CI gates.

## 4. Required process steps (per course requirement)

1. Analyze requirements → freeze business rules
2. Structure-level UI design (sitemap/wireframes)
3. Database design (ERD)
4. Process diagrams (use case, sequence, activity)
5. Code

## 5. Roadmap (odd weeks = on-campus checkpoints)

### Phase 0 — Market & customer discovery

**Dates: Tue 18/08 → Thu 27/08 (presentation deadline)**
- Core sprint: Tue 18/08 → Tue 25/08 (6 working days)
- Feature draft polish: Wed 26/08 → Thu 27/08
- **Presentation: Thu 27/08 (hard deadline)**

Goal: by **Thu 27/08**, deliver **market analysis + feature draft + P0-03 discovery** (vision, constraints, risks — pulled forward) for presentation. Customer discussion + exit criteria deferred to P0-07 (Phase 1).

**Key constraint:** 27/08 is a hard deadline for teacher presentation. Output scope = market analysis + feature draft + P0-03 discovery docs (vision.md, assumptions-risks.md, decisions.md); P0-07 customer meeting/exit deferred to Phase 1.

See `issues/README.md` for the issue list and coverage map.

| Date | PM | FE | Mobile | BE | AI | EOD sync |
|------|----|----|--------|----|----|----------|
| **Wed 19/08 (D1)** | P0-01: start competitor research (long-term rental + roommate apps) | P0-02: UX review — walk landlord web apps | P0-02: UX review — walk tenant mobile apps | — (deferred to Phase 1) | — (deferred to Phase 1) | 15-min sync |
| **Thu 20/08 (D2)** | P0-01: extract pain points, personas, extend `market-analysis.md` | P0-02: finish → `ux-web.md` | P0-02: finish → `discovery-ux-mobile.md` | — | — | 15-min sync; FE + Mobile hand deliverables to PM |
| **Fri 21/08 (D3)** | P0-01: finalize `market-analysis.md` + draft `feature-list.md` | Review feature draft | Review feature draft | — | — | Feature draft v0.1 team review (15 min) |
| **Sat 22/08 (D4)** | Polish feature-list.md (1-2 people) | — | — | — | — | — |
| **Sun 23/08 (D5)** | Polish feature-list.md (1-2 people) | — | — | — | — | — |
| **Mon 24/08 (D6)** | Team review feature draft → finalize `feature-list.md` + `product-sketch.md` | Sign off | Sign off | — | — | **Feature Draft Ready ✓** |
| **Tue 25/08** | Phase 0 exit checklist (formal) | — | — | — | — | Phase 0 done ✓ |
| **Wed 26/08** | Prepare presentation materials | — | — | — | — | — |
| **Thu 27/08** | **PRESENTATION** | — | — | — | — | — |

**Task tracking:** Markdown issues in `pm/phase-0/issues/` until Linear or GitHub Projects is chosen (target Phase 1). Key deliverables: `market-analysis.md` + `feature-list.md` + `product-sketch.md` + P0-03 discovery docs (`discovery/vision.md`, `discovery/assumptions-risks.md`, `discovery/decisions.md` — D1–D29).

**Task assignment (focused for 27/08 presentation):**
- **PM (owner):** P0-01 competitive analysis + market research, P0-06 simplified → feature draft.
- **FE:** P0-02 UX review — web (landlord side).
- **Mobile:** P0-02 UX review — mobile (tenant side).
- **BE:** Deferred to Phase 1 (P0-04 technical feasibility).
- **AI:** Deferred to Phase 1 (P0-05 AI feasibility).

**Deferred to Phase 1 (post-presentation):**
- P0-04: Technical feasibility (BE)
- P0-05: AI feature feasibility (AI)
- P0-07: Product sketch + customer discussion + exit criteria

**Done / pulled forward in Phase 0:**
- P0-03: Product vision, constraints & risks — delivered as `discovery/vision.md` + `discovery/assumptions-risks.md` + `discovery/decisions.md` (D1–D29).

**DoD for 27/08:** `market-analysis.md` updated with long-term rental + roommate competitors; `feature-list.md` complete with priorities/rationale/complexity; `product-sketch.md` updated; presentation ready.

### Phase 1 — Setup + requirements freeze (W3–4)

- **Setup (resources approved):** create 4 repos + this docs hub; seed each with `README.md` + `AGENTS.md` + branch protection; set up Linear board, Notion wiki, Drive structure; invite members.
- Backlog into Linear with priorities; user stories + use cases.
- Freeze business rules: room/contract/invoice/payment/roommate/issue/AI flows.
- **Checkpoint W5 (M1):** present requirement + business rules; collect teacher feedback; update `requirement.md`.

### Phase 2 — Design (W5–6)
- Sitemap + wireframes (FE + Mobile) — structure-level, not pixel-perfect.
- API draft (OpenAPI/Swagger) — BE.
- ERD v1 — BE, reviewed by PM.
- Process diagrams: use case, sequence, activity — PM with team.
- **Checkpoint W7 (M2):** design frozen; specs committed to docs hub & backend repo.

### Phase 3 — Scaffolding & first vertical slice (W7–8)
- Backend: NestJS scaffold, DB schema + migrations, auth module.
- Web/Mobile: scaffold + navigation + login screens.
- AI: FastAPI service, secure OpenAI key handling, `/health`.
- End-to-end slice: login → list rooms (BE + Web + Mobile + AI minimal).
- Deploy backend + web (Railway/Fly.io + Vercel).
- **Checkpoint W9 (M3):** demo skeleton slice.

### Phase 4 — Core features (W9–12)
- **BE:** room, contract, utility closing, invoice, payment modules.
- **Web:** landlord dashboard, room map, contract, invoice, statistics.
- **Mobile:** map search + filters, invoice view, roommate profile, issue report, payment (VNPay/Momo).
- **AI:** auto-description v1, matchmaking v1 integrated via BE.
- Sync API spec in Apidog; run end-to-end contract tests.
- **Checkpoint W11 (M4):** feature-complete demo on staging.

### Phase 5 — Hardening, demo & submission (W12–14)
- Bug-fix pass, seed realistic demo data, final deploy.
- Demo script + rehearsal; record demo video.
- Final report + PPT (Vietnamese, in Google Drive); update all docs.
- **W14:** buffer / final submission & defense.

## 6. Risks

| Risk | Mitigation |
|------|-----------|
| Resource/tool approval delayed | Full list in `product-sketch.md` §7. Phase 0 docs-only/tool-free; hầu hết free-tier tự lo được, nhưng **LLM API key/ngân sách** (#10) và **VNPay sandbox** (#11) cần tài khoản pháp nhân → ưu tiên xin thầy bảo trợ; fallback: key cá nhân + mock payment (R1) |
| Payment gateway (VNPay/Momo) approval slow | Use sandbox; mock payment as fallback |
| OpenAI API cost/limits | Cache prompts, limit calls, use cheap model |
| 3rd-party API drift | Apidog snapshot + contract tests |
| Scope creep by AI/UX features | PM enforces MVP cut; backlog-only for rest |
| Bi-weekly class cadence | Milestones aligned to odd-week checkpoints (W3,5,7,9,11) |
