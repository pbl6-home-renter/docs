# P0-05 — AI Feature Feasibility

- **Assignee:** AI
- **Participants:** (consult BE for service contract)
- **Priority:** High
- **Status:** 🟡 Open
- **Timebox:** Tue 18/08 → Wed 19/08 — parallel track, deliver to PM by EOD Wed
- **Depends on:** — (uses existing `requirement.md`; does NOT block on P0-01)
- **Blocks:** P0-06 (scope decisions), Phase 3/4 (integration)
- **Sprint day:** D1–D2 (Tue 18/08 – Wed 19/08, parallel)

## Goal

By EOD Wed 19/08, AI has validated both AI features are buildable within time/budget, with tested prompts, a cost estimate, and a service contract ready for BE.

## Context

AI is "light, encouraged" in the course. Features: (1) roommate matchmaking (habits → score % + advice via OpenAI), (2) auto room-description from keywords. This issue tests the prompts, costs, and integration — no full service build yet.

## Tasks

### D1 (Tue 18/08)
- [ ] Matchmaking: define input (personality traits, lifestyle habits: sleep, pets, smoking, noise), output (score % + 2–3 sentence advice). Draft 1 prompt; test with 3 sample pairs (API key if available, else mock outputs).
- [ ] Auto-description: draft prompt (keywords → Vietnamese room listing copy); test with 3 sample keyword sets.
- [ ] Cost estimate: tokens per call × expected monthly calls → USD/month; recommend model (gpt-4o-mini) + caching strategy.

### D2 (Wed 19/08)
- [ ] Fallback plan: if OpenAI unavailable/costly → rule-based scoring or open-source model; document trigger.
- [ ] Service contract: FastAPI endpoints, request/response payloads, auth between BE and AI service, error handling.
- [ ] Risks: hallucination, bias, privacy of habit data; note mitigations.
- [ ] Deliver `discovery/ai-feasibility.md` to PM.

## Deliverable

`pm/phase-0/discovery/ai-feasibility.md` — 2 prompt drafts + sample outputs, cost estimate, fallback plan, service API draft, risks.

## Definition of Done

- [ ] Both prompts tested on ≥3 samples (outputs attached).
- [ ] Cost estimate table (per-call, per-month, recommended model).
- [ ] Service API draft shared and understood by BE.
- [ ] Reviewed with PM before P0-06 scope freeze (Thu).
