# P0-04 — Technical Feasibility

- **Assignee:** BE
- **Participants:** (consult AI for service contract, PM for scope questions)
- **Priority:** High
- **Status:** 🟡 Open
- **Timebox:** Tue 18/08 → Wed 19/08 — parallel track with FE/Mobile, deliver to PM by EOD Wed
- **Depends on:** — (uses existing `requirement.md` + `market-analysis.md`; does NOT block on P0-01)
- **Blocks:** P0-06 (scope decisions), Phase 3 (scaffolding)
- **Sprint day:** D1–D2 (Tue 18/08 – Wed 19/08, parallel)

## Goal

By EOD Tue, BE has a feasibility verdict (OK / Risk / Blocked) for every MVP candidate feature, plus a deployment plan. No code — analysis only.

## Context

Stack is fixed: NestJS + PostgreSQL, Swagger + Apidog. Unknowns: data model complexity, VNPay/MoMo integration, deployment cost. This issue answers "can we build it, and where will it hurt?" before scope freeze on Thu.

## Tasks

### D1 (Tue 18/08)
- [ ] Data-model sketch: User, Building, Room, Contract, MeterReading, Invoice, Payment, IssueReport, RoommateProfile, MatchRequest — validate relations, enums, uniqueness in NestJS+PostgreSQL.
- [ ] Auth: role model (landlord / tenant / admin), JWT + refresh, feasibility notes.
- [ ] Utility closing: monthly meter-read capture, bậc thang electricity calculation → invoice. Note edge cases.
- [ ] Payment: VNPay vs MoMo — sandbox availability, BE-side path, effort estimate, fallback (mock payment).

### D2 (Wed 19/08)
- [ ] API contract workflow: how Swagger spec is authored in NestJS, how Apidog sync works, how FE/Mobile consume it.
- [ ] Deployment: Railway/Fly.io for NestJS+Postgres, Vercel for web; free-tier limits, cost estimate.
- [ ] Feasibility matrix: for each MVP candidate feature → OK / Risk / Blocked + note.
- [ ] Deliver `discovery/tech-feasibility.md` to PM.

## Deliverable

`pm/phase-0/discovery/tech-feasibility.md` — data-model sketch, auth notes, feasibility matrix, payment decision, deployment plan.

## Definition of Done

- [ ] Feasibility matrix covering every MVP candidate feature.
- [ ] Payment decision recorded (sandbox vs mock).
- [ ] Deployment plan draft (platform, steps, cost).
- [ ] Reviewed with PM before P0-06 scope freeze (Thu).
