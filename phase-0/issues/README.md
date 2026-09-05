# Phase 0 — Issues & Backlog

> Task tracking is **markdown-based** until Linear or GitHub Projects is chosen (target Phase 1). One file per issue. Migrate 1:1 when the tracker is decided.
> **Sprint:** Wed 18/08 → Thu 27/08 (presentation deadline). See `PROJECT_PLAN.md` Phase 0 for the day-by-day breakdown.
> **27/08 focus:** Market analysis + feature draft + P0-03 discovery (pulled forward) + P0-07 exit (sketch done; external customer interview deferred to Phase 1).

## Status legend

`🟡 Open` · `🔵 In progress` · `🟢 Done` · `⚪ Blocked` · `⏪ Deferred`

## Issue list

| ID | Title | Assignee | Dates | Status | Depends on | Blocks | Deliverable |
|----|-------|----------|-------|--------|------------|--------|-------------|
| [P0-01](P0-01-user-research-competitive-analysis.md) | User research & competitive analysis | PM | Wed 19/08 – Fri 21/08 | 🟢 Done | — | P0-06 | `market-analysis.md` (updated) |
| [P0-02](P0-02-competitive-ux-review.md) | Competitive UX review (web + mobile) | FE + Mobile | Wed 19/08 – Thu 20/08 | 🟢 Done | — (uses seed list) | P0-06 | `discovery/p0-02/ux-web.md` + `discovery/p0-02/discovery-ux-mobile.md` |
| [P0-03](P0-03-product-vision-constraints-risks.md) | Product vision, constraints & risks | PM | Sat 22/08 – Mon 24/08 | 🟢 Done | P0-01 | P0-07 | `discovery/vision.md` + `discovery/assumptions-risks.md` + `discovery/decisions.md` (D1–D29) |
| [P0-04](P0-04-technical-feasibility.md) | Technical feasibility | BE | ⏪ Deferred to Phase 1 | ⏪ Deferred | — | P0-06 | `discovery/tech-feasibility.md` |
| [P0-05](P0-05-ai-feasibility.md) | AI feature feasibility | AI | ⏪ Deferred to Phase 1 | ⏪ Deferred | — | P0-06 | `discovery/ai-feasibility.md` |
| [P0-06](P0-06-use-cases-mvp-scope.md) | Use cases, MVP scope & feature list (derived from P0-03) | PM | Mon 24/08 | 🟢 Done | P0-01, P0-02, P0-03 | P0-07 | `feature-list.md` (updated) + use-case list in issue |
| [P0-07](P0-07-product-sketch-exit.md) | Product sketch, exit criteria & phase review | PM | Mon 24/08 | 🟢 Done | P0-06 | Phase 1 | `product-sketch.md` + `discovery/exit-criteria.md` |

## Discovery items → coverage map (30 items → 3 active issues for 27/08)

> **Note:** For 27/08 presentation: P0-01 ✅ Done · P0-02 ✅ Done · P0-03 ✅ Done (pulled forward) · P0-06 ✅ Done · P0-07 ✅ Done (sketch + exit; external customer interview waived to Phase 1, C3). Feasibility drafts for P0-04/P0-05 exist under `discovery/` (finalized in Phase 1). Decisions D1–D29 logged in `discovery/decisions.md`.

Core = must deliver for 27/08. Deferred = Phase 1.

| Discovery item | Priority | Covered by |
|----------------|----------|------------|
| Product Vision | Core | P0-03 |
| Problem Statement | Core | P0-01 (input) → P0-06 |
| Target Users | Core | P0-01 |
| User Personas | Core | P0-01 |
| User Context | Supporting | P0-01 (merged into personas) |
| Current Workflow | Core | P0-01 |
| Pain Points | Core | P0-01 |
| Root Causes | Supporting | P0-01 (merged into Pain Points) |
| User Needs | Core | P0-01 |
| Existing Solutions | Core | P0-01 |
| Competitor Analysis | Core | P0-01 (+ P0-02 UX dimension) |
| Market Context | Supporting | P0-01 (merged into Competitor Analysis) |
| Business Opportunity | Core | P0-03 |
| Value Proposition | Core | P0-03 |
| Core Use Cases | Core | P0-06 → use-case list + feature list |
| User Journey | Core | P0-06 → use-case list + feature list |
| Stakeholders | Core | P0-03 |
| Business Goals | Core | P0-03 |
| Success Criteria | Core | P0-03 |
| Key Assumptions | Core | P0-03 |
| Risks & Unknowns | Core | P0-03 |
| Product Constraints | Core | P0-03 |
| MVP Candidate Scope | Core | P0-06 → `feature-list.md` |
| Out of Scope | Core | P0-06 → `feature-list.md` |
| Open Questions | Core | P0-03 + P0-07 |
| Research Findings | Supporting | P0-01 → consolidated in P0-06 |
| Problem Prioritization | Core | P0-06 → `feature-list.md` |
| Problem–Solution Fit Hypothesis | Deferred | P0-06 (Phase 1) |
| MVP Hypothesis | Deferred | P0-06 (Phase 1) |
| Discovery Exit Criteria | Deferred | P0-07 (Phase 1) |

## Workflow

- Edit the status in the issue header; keep the table above in sync.
- Deliverables land in `pm/phase-0/discovery/` (or `market-analysis.md` / `feature-list.md` / `product-sketch.md`).
- Decisions go in `discovery/decisions.md` (moves to Notion decision log when available).
- Daily EOD sync (15 min): each person states what they finished, what's blocked, what's next.
- **27/08 presentation prep:** PM owns `feature-list.md` + `product-sketch.md` finalization. FE/Mobile provide UX review inputs by Thu 20/08.
