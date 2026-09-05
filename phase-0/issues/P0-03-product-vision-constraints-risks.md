# P0-03 — Product Vision, Constraints & Risks

- **Assignee:** PM
- **Participants:** team review (15 min Mon 24/08 EOD)
- **Priority:** High
- **Status:** 🔵 In progress
- **Timebox:** revised — Sat 22/08 PM writes; team reviews Mon 24/08 EOD (pulled from Deferred; original slot Thu 20/08)
- **Depends on:** P0-01 (research + market)
- **Blocks:** P0-06, P0-07
- **Sprint day:** D3 (Thu 20/08)

## Goal

By EOD Thu 20/08, PM has written: vision statement, value proposition, success criteria, constraints, risks, and open questions — all in two short documents ready for team review.

## Context

P0-01 hands over research by Wed 19/08 EOD. PM must turn evidence into strategy overnight. This is the "why we exist and how we know we succeeded" issue. Keep it tight — no lengthy strategy decks, just the essentials that anchor scope decisions tomorrow (D4, P0-06).

## Tasks

### D3 (Thu 20/08) — write + review

**AM — Vision & strategy:**
- [x] Draft vision statement (who / what / why / for whom / differentiator), max 3–4 sentences.
- [x] Value proposition: map jobs-to-be-done × pains × gains per persona → which features address them.
- [x] Stakeholders: teacher (grading criteria), customer (landlords/tenants), admin — note influence + needs.
- [x] Success criteria: course success (demo works, report quality) + product success (measurable: e.g., "landlord closes monthly cycle in <10 min", "≥80% invoices paid online").
- [x] Write `discovery/vision.md`.

**PM — Constraints & risks (can overlap with above):**
- [x] Assumption log: ≥8 implicit assumptions (e.g., "chủ trọ quản lý >10 phòng", "khách thuê có smartphone"), mark each validated/unvalidated.
- [x] Constraints: 5-person team, 1 week left in Phase 0, 13–14 weeks total, OpenAI budget, VNPay/MoMo sandbox, demo-grade testing.
- [x] Risk register: ≥6 risks (likelihood/impact/mitigation) — payment delay, OpenAI cost, scope creep, member availability, Apidog drift, deployment cost.
- [x] Open questions for customer/teacher (consolidated from P0-01 interviews + market analysis).
- [x] Write `discovery/assumptions-risks.md`.

**EOD — Team review (15 min):**
- [ ] Walk vision + risks with the team; resolve disagreements; record decisions in `discovery/decisions.md`.

## Deliverables

- `pm/phase-0/discovery/vision.md` — vision, value prop, stakeholders, success criteria.
- `pm/phase-0/discovery/assumptions-risks.md` — assumptions, constraints, risks, open questions.
- `pm/phase-0/discovery/decisions.md` — any decisions made during review.

## Definition of Done

- [ ] Vision ≤4 sentences.
- [ ] Value prop canvas filled per persona.
- [ ] Success criteria measurable (numbers, not adjectives).
- [ ] Assumption log + risk register written.
- [ ] Team review done; decisions logged.
