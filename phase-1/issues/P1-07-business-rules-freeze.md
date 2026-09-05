# P1-07 — Business-Rules Freeze

- **Assignee:** PM + BE
- **Participants:** AI (AI flows), FE/Mobile (review)
- **Priority:** High
- **Status:** 🟡 Open
- **Timebox:** Fri 04/09 → Mon 07/09
- **Depends on:** P1-05, P1-06 (feasibility finalized)
- **Blocks:** P1-11 (M1), Phase 2 (design)
- **Sprint:** W4

## Goal

Author `business-rules.md` freezing the rules for room/building, contract, utility closing, invoice/payment, roommate/match, issue reporting, and AI flows — derived from `feature-list.md` Modules 1–6 and the finalized feasibility docs.

> **Parallel note:** DB design (P1-18) runs **in parallel** with this freeze (same timebox 04–07/09) because BE had a schedule risk waiting for freeze to finish. P1-18 drafts the schema from the business-rules **draft** + D25/D18/D16/D21/D22/D26; it is **reversible/adjustable in Phase 2** after this freeze lands. Keep the draft rule changes in sync here (P1-07 is source of truth).

## Context

`PROJECT_PLAN.md` Phase 1: "Freeze business rules." This is the contract PM/BE agree on before design (Phase 2). Changes after freeze require change-control (Notion decision log).

## Tasks

### Fri 04/09
- [ ] Draft room/building + contract rules (e-sign, PIN/paper_scan).
- [ ] Draft utility closing rules (meter capture, bậc thang, invoice generation).

### Sat 05/09 – Sun 06/09 — weekend (optional polish)

### Mon 07/09
- [ ] Draft invoice/payment (dynamic-QR reconciliation) + roommate/match + issue reporting rules.
- [ ] Draft AI flows (3 features) with BE/AI review.
- [ ] Publish `business-rules.md`; tag as frozen (v1.0).

## Deliverable

`pm/phase-1/business-rules.md` (frozen v1.0).

## Definition of Done

- [ ] All 7 business areas covered with explicit rules.
- [ ] Reviewed and signed off by BE (and AI for AI flows).
- [ ] Marked frozen; change-control process documented.
