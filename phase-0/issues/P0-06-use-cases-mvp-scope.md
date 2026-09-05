# P0-06 — Use Cases, MVP Scope & Feature List

- **Assignee:** PM
- **Participants:** all members (15-min scope sign-off)
- **Priority:** High
- **Status:** 🔵 In progress
- **Timebox:** Mon 24/08 (D5) — PM writes; team sign-off EOD
- **Depends on:** P0-01 (research), P0-02 (journeys), P0-03 (vision/constraints/risks — ✅ Done), P0-04/05 (feasibility drafts)
- **Blocks:** P0-07
- **Sprint day:** D5 (Mon 24/08)
- **Note:** Phase 0 simplified to a *feature draft* for the 27/08 presentation. Use-case list + prioritized feature list are the deliverables; the two measurable hypotheses are seeded here but full validation is deferred to Phase 1.

## Goal

By EOD Mon 24/08, the team has approved the MVP use-case set and feature scope. This is the single most important output of Phase 0 — it decides workload for the 13–14 weeks. Everything is derived directly from P0-03 (`discovery/vision.md` + `discovery/assumptions-risks.md`, decisions D1–D29, D12 skipped) and consolidated with `feature-list.md`.

## Context

P0-03 is complete: it defines the **why** (vision, value prop for 3 personas) and the **guardrails** (integration-first D7, long-term-only D9, Property Chat realtime D24′ (thay thế approach "no messenger"), matchmaking Stretch boundary D28, OCR-chosen-over-API F5, e-contract $0 F7, Explainer-not-RAG F8). P0-06 turns those into the concrete **what**: a use-case list mapped to the 3 personas, and a prioritized feature list (canonical & maintained in `feature-list.md`). Personas from `vision.md` §2 drive the actors below.

> **Platform model (D13):** web + mobile both serve both roles. Primary: landlord-web (ops console) + tenant-mobile (portal). Secondary: landlord-mobile-lite (FCM, duyệt sự cố, xem dashboard/hóa đơn) + tenant-web (responsive). Backend `User.role` enum → `roles` array. Use-case actors below show the **primary** platform.

## Use-case list (derived from P0-03 personas & value prop)

Each use case: **Actor · Precondition · Happy path · Postcondition · 1 Failure case**. Persona mapping: L = landlord (Chú Hùng / Chị Mai), T = tenant (Minh), A = admin/system.

### Landlord (web)

**UC-L1 — Manage buildings & rooms**
- Actor: Landlord · Pre: authenticated, role=landlord
- Happy: create building → add rooms (CRUD) → view room-map status (empty/occupied/maintenance)
- Post: room data persists; map reflects status · Fail: invalid room number → validation error, nothing saved

**UC-L2 — OCR meter closing + manual confirm**
- Actor: Landlord · Pre: room has active contract; month-end
- Happy: upload meter photo → OCR reads value → landlord 1-tap confirms → value + photo evidence saved
- Post: reading recorded with timestamp + photo · Fail: OCR unreadable → manual input fallback; photo still attached (F5)

**UC-L3 — Generate & send monthly invoice**
- Actor: Landlord · Pre: meter readings closed (UC-L2)
- Happy: system auto-generates invoice from meter + rent → **reads unit price from room override → building override → landlord default (D16)** → landlord reviews → sends to tenant (in-app notification + kênh ngoài app)
- Post: invoice status=pending; tenant notified (FCM) · Fail: missing rate config (no default at any level) → invoice blocked, prompt to set rate (UC-L1 / 3.11)

**UC-L4 — Reconcile payment (dynamic named-QR / webhook)**
- Actor: Landlord (system) · Pre: invoice sent (UC-L3)
- Happy: tenant pays via dynamic named-QR → bank/webhook callback → auto gạch nợ → invoice=paid
- Post: payment recorded, e-receipt issued · Fail: webhook timeout → `ENABLE_MOCK_PAYMENT` + landlord "mark paid" (R1)

**UC-L5 — Contract lifecycle & expiry alert**
- Actor: Landlord · Pre: e-contract created (UC-T2)
- Happy: list contracts with status → system warns 30–45 days before expiry
- Post: alert logged; landlord can prepare next tenant · Fail: contract missing dates → alert skipped, flagged

**UC-L6 — Incident ticket handling (@issue in Property Chat, D24′)**
- Actor: Landlord · Pre: tenant submitted issue (UC-T4)
- Happy: `@issue` tạo IssueReport → card vào chat riêng phòng (realtime Socket.io khi app mở + FCM offline) → in_progress → resolved
- Post: ticket state machine recorded; SLA measurable · Fail: no response → stays open, escalates in report (D24′)

**UC-L7 — AI auto room description**
- Actor: Landlord · Pre: room created with keywords/attributes
- Happy: call AI service → returns description → landlord edits/saves
- Post: description stored · Fail: API down → rule-based template fallback (D3, A7)

### Tenant (mobile)

**UC-T1 — Map-based room search**
- Actor: Tenant · Pre: authenticated
- Happy: open map → apply filters (price/area/amenities/distance) → view room detail (photos, price, landlord)
- Post: results listed; can favorite · Fail: GPS off → default city center; no crash

**UC-T2 — Apply & e-contract**
- Actor: Tenant · Pre: found room
- Happy: request → landlord creates e-contract (template) → **landlord captures & stores tenant CCCD image once (D17)** → both parties sign via in-app **transaction PIN** (`e_sign`) — or fall back to **paper_scan** (landlord scans signed paper, tenant confirms receipt); `signature_mode` recorded
- Post: contract active; move-in enabled · Fail: PIN mismatch / B-party refuses e-sign → retry or drop to `template_upload` (wet-sign); draft saved (D18, A8)

**UC-T3 — View & pay invoice**
- Actor: Tenant · Pre: invoice sent (UC-L3)
- Happy: view invoice + meter photo evidence → pay VNPay/MoMo → status updated
- Post: payment recorded; receipt shown · Fail: sandbox down → mock payment + landlord confirm (R1)

**UC-T4 — Report issue with photo (@issue, D24′)**
- Actor: Tenant · Pre: authenticated, has contract/room
- Happy: create issue (photo + description) → `@issue` tạo IssueReport → card vào chat phòng → theo dõi status
- Post: ticket open; landlord notified · Fail: upload fails → retry; draft saved locally (D24′)

**UC-T5 — Roommate profile & match**
- Actor: Tenant · Pre: profile created
- Happy: fill roommate profile (lifestyle/budget) → browse → send match request
- Post: request logged; AI score + advice returned (<15s on seed pool) · Fail: <10 seed profiles → limited matches; cold-start noted (D28, F1)

### Admin / cross-cutting

**UC-A1 — Auth & roles**
- Actor: all · Pre: none
  - Happy: register/login (JWT) → role-based views (landlord/tenant/admin). *(D29: tenant login optional — landlord-only happy path is valid; tenant engages via kênh ngoài app/QR/cash when not logged in.)*
- Post: session issued; profile manageable · Fail: wrong role → access denied (6.2)

**UC-A2 — Notifications (FCM)**
- Actor: system · Pre: event (invoice/contract/expiry)
- Happy: push notification → deep-link to object
- Post: user informed · Fail: token invalid → dropped, retry on next event (D7)

## Problem prioritization (frequency × severity × team ability)

Ranked from P0-01 pain points & `vision.md` value prop:

1. **Manual payment reconciliation** (landlord pain #1, F5×S4) — highest leverage
2. **Manual meter reading** (pain #2, F5×S3)
3. **Paper contracts / deposit disputes** (Chị Mai, Minh)
4. **Finding compatible roommate** (Minh, F3×S5)
5. **Incident-response gap** (Chị Mai)
6. **Room discovery on map** (tenant baseline expectation)

## MVP scope & feature list

Canonical, maintained version: **`feature-list.md`** (updated to reflect decisions D1–D29, D12 skipped). Compact summary by module & priority:

| Module | MVP (must) | Stretch (should) | Out / Phase 1+ |
|--------|-----------|------------------|----------------|
| 1 Property (web) | 1.1 Room CRUD · 1.2 Building · 1.3 Room-map | 1.4 Status · 1.5 Photo · 1.6 Bulk | — |
| 2 Tenant (mobile) | 2.1 Map search · 2.2 Filters · 2.3 Detail · 2.4 Invoice view · 2.5 Pay · 2.7 Issue (@issue) · 2.8 Property Chat (D24′) | 2.6 History · 2.9 Favorite | — |
| 3 Contract/Billing | 3.1 E-contract (+CCCD capture D17) · 3.2 Listing · 3.3 OCR closing+confirm · 3.4 Auto-invoice · 3.5 Invoice status · 3.10 Dynamic-QR recon · 3.11 Utility rate config (D16) | 3.6 Reminders · 3.7 Revenue+cost ledger | 3.8 Multi-currency · 3.9 HĐĐT |
| 4 Roommate | 4.1 Profile · 4.2 Browse · 4.3 Match request | 4.4 AI score (Stretch D28) | 4.5 Chat · 4.6 Quiz |
| 5 AI | 5.1 Auto-description · 5.5 Contract Explainer | 5.2 Matchmaking score · 5.6 CCCD OCR (D17) | 5.3 Recs · 5.4 Price |
| 6 Admin | 6.1 Auth · 6.2 RBAC · 6.3 Profile · 6.6 Issue/chat panel (D24′) | 6.4 Notifications | 6.5 Multi-lang |

Full rationale + complexity per feature → `feature-list.md`.

## Out-of-scope (explicit, from decisions)

- **Short-term / homestay (Airbnb-style)** — D9 (long-term only)
- **Social / ranking feed** — F2 (tin giả risk, empty-feed risk)
- **Built-in realtime messenger (full)** — D24′ (chỉ Property Chat: chat phòng + chung toà, bot, `@issue`, `@mention`; voice/sticker/poll ngoài MVP)
- **Bill splitting among roommates** — D4 (Phase 1+)
- **ZNS / Zalo OA auto messaging** — D7 (Phase 1+)
- **Google Sheets 2-way API** — D7 (import/export only)
- **EVN/water utility API pull** — F5 (OCR instead)
- **Real RAG contract chatbot (full-text PDF, pgvector)** — D15 (MVP uses Explainer from structured fields; real RAG → Phase 1+ stretch)
- **Profile photo image-moderation** — D28 (text-only moderation in MVP; OCR image-moderation = stretch)
- **Cleaning schedule (lịch vệ sinh)** — discussed 27/08: skip MVP; could reuse Property Chat `@issue` (UC-L6) if revived in Phase 1+
- **Full tạm trú/tạm vắng e-declaration** — D17: MVP only captures CCCD image at e-contract (3.1) + CCCD OCR (5.6 Stretch); full declaration (tờ khai/in/xuất, nộp cơ quan) → Phase 1+, pending C3 interview
- **Multi-currency · HĐĐT legal · smart recs · price suggestion** — data/legal dependent

## Hypotheses (seeded; full validation deferred to Phase 1)

- **Problem–Solution Fit:** "We believe landlords (Chú Hùng / Chị Mai) with manual reconciliation & meter pain will use OCR closing + dynamic-QR auto-reconcile because it cuts the monthly close to <10 min / 10 rooms."
- **MVP Hypothesis (measurable, from `vision.md` §4.2):** landlord closes monthly cycle ≤10 min/10 rooms · ≥80% invoices paid online E2E · OCR ≥90% on clear photos (always manual confirm) · match result <15s on seed pool ≥10 · AI auto-desc p95 <10s.

## Deliverables

- `pm/phase-0/feature-list.md` — updated, decision-aligned feature list (canonical).
- This issue — use-case list + MVP scope + out-of-scope (team sign-off artifact).

## Definition of Done

- [x] ≥8 use cases documented with all fields (14 above).
- [ ] MVP scope + out-of-scope approved by team (sign-off in `decisions.md`).
- [x] Feature list synced with P0-03 decisions D1–D29 (D12 skipped).
- [x] 2 hypotheses seeded & measurable.
