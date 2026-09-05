# P1-18 — Full MVP Database Design (parallel with business-rules freeze)

- **Assignee:** BE
- **Participants:** PM (scope D25/D18/D16/D22/D21/D26), AI (AI flows fields), FE/Mobile (review)
- **Priority:** High
- **Status:** 🟡 Open
- **Timebox:** Fri 04/09 → Mon 07/09 (runs **in parallel** with P1-07 to de-risk BE schedule)
- **Depends on:** D25 (`ownership-model.md` finalized), D18 (contract signing), D16 (utility rate config), D22 (payment config), D21 (landlord constraints), D26 (tenant history consent), P1-13 deliverable draft (AI matchmaking fields)
- **Blocks:** Phase 2 (BE implementation), ERD v1, OpenAPI schema
- **Sprint:** W4

## Goal

Design the **full MVP PostgreSQL schema** (ERD v1 + DDL sketch + indexes + constraints) covering Modules 1–6 of `feature-list.md`, derived from the **business-rules draft** (P1-07) and the finalized decisions.

> **Why parallel:** waiting for P1-07 freeze to finish before starting DB design would push all BE schema work past Phase 1 and guarantee a Phase 2 delay. This draft runs **concurrently** with the freeze and is explicitly **reversible/adjustable in Phase 2** if a rule changes before/at freeze. P1-07 remains source of truth for *rules*; this is the *schema rendering* and is a draft until freeze.

## Context & scope

- Absorbs the ownership model (formerly P1-12) — **D25 already finalized** via `discovery/ownership-model.md` (Building → optional Floor → Room, `Room.owner_id` NOT NULL, `Contract.issued_by_user_id` NOT NULL, no manager/delegation in MVP).
- Schema covers all **26 MVP features** (Modules 1–6).
- Stretch features (5.6 CCCD OCR now MVP, 2.10 history, 3.6 reminders, 4.4 AI match) included as tables/columns — see below.

## Key decisions baked in (do NOT relitigate)

| Decision | Schema impact |
|----------|---------------|
| **D25** | `rooms.owner_id` NOT NULL; `floors.building_id`, `floors.owner_id` nullable hint; `contracts.issued_by_user_id` NOT NULL; no `manager_id` |
| **D18** | `contracts.signature_mode` enum(1)=`template_upload`; `signed_at`, `uploaded_file`; parse fields; **no** `e_sign`/`e_ack`/`pin`/OTP fields |
| **D16** | `landlord_profiles.default_settings.electricityRate/waterRate` (global default); `buildings.*Rate` override optional; `rooms.*Override` optional; invoice resolves room→building→landlord |
| **D22** | 1 representative contract per active room (partial unique index); payment config = rep-payer OR shared-invoice tracking per room |
| **D21** | `rooms` hard-filter constraints: `maxOccupancy`, `genderPolicy`, `houseRules`, `budgetRange` — no per-pair vet |
| **D26** | consent-based tenant history tables, only shown on opt-in |
| **D29** | all tenant touchpoints optional; schema has no hard dependency on tenant account presence |

## Tasks

### Fri 04/09
- [ ] Draft entity inventory from feature-list Modules 1–6 (users, buildings, floors, rooms, contracts, meter_readings, invoices, payments, issue_reports, comments, roommate/match tables, AI fields).

### Sat 05/09 – Sun 06/09 — weekend (optional polish)
- [ ] Sketch ERD v1 + relationship cardinalities.

### Mon 07/09
- [ ] Write DDL sketch: tables, PK/constraints, indexes, partial unique indexes.
- [ ] Review against P1-07 freeze draft; flag any rule↔schema conflicts.
- [ ] Publish `discovery/db-design.md` (draft v0.x, Phase-2-adjustable).

## Deliverable

`pm/phase-1/discovery/db-design.md` — ERD v1 + DDL + index/constraint list (+ backfill/migration notes for NOT NULL columns).

## Definition of Done

- [ ] All 26 MVP features map to schema entities/columns.
- [ ] Ownership model (D25) reflected exactly; no manager/delegation fields.
- [ ] Contract model per D18 (template_upload only, no PIN/OTP).
- [ ] Reviewed against P1-07 freeze draft; conflicts flagged & resolved.
- [ ] Marked **draft; adjustable in Phase 2** (not frozen) — outcome communicated to BE planning.
