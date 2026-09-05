# AGENTS.md — PBL6 PM Workspace (`pm/`)

This is the **management & documentation hub** for PBL6 (university project, 5 members: PM · FE · Mobile · BE · AI). No application code lives here. Companion hubs/sub-repos: see the hub repo `AGENTS.md` at the repo root (one level up) for shared team conventions.

## What this repo is

- **Source of truth (SoT):** `requirement.md` (scope) and `PROJECT_PLAN.md` (schedule, 13–14 weeks, odd-week milestones). Anything beyond them requires PM approval; record the decision in the phase decision log.
- **Structure:** docs grouped by phase — `phase-0/` (market & discovery), `phase-1/` (setup + requirements freeze), … Each phase contains `README.md` (phase scope + dependency order), `issues/` (markdown task tracker with status table), `discovery/` (phase outputs incl. decision log `decisions.md`).
- **Task tracking:** markdown issues under `phase-N/issues/` (table in `README.md` is authoritative) until Linear/GitHub Projects is chosen. Keep statuses in sync.

## Skill: `pm-context` (read this first)

Before any decision-affecting work, load the skill **`pm-context`** (`.agents/skills/pm-context/SKILL.md`). It walks the required reading order — README index → `requirement.md` → `PROJECT_PLAN.md` → current phase docs/issues → `discovery/decisions.md` (D1–D29…) → role-relevant docs — and produces a context brief with scope boundary, key decisions, relevant issues, and an explicit uncertainty list.

Accepted convention: an agent that opens this repo should start by reading `pm-context`.

## Conventions

- **Language:** English for docs/commits. Vietnamese only in teacher-facing reports (some `discovery/` docs are intentionally bilingual per decision D5).
- **Scope discipline:** never propose features beyond `requirement.md` without PM approval. New scope/plan changes must update `PROJECT_PLAN.md` + decision log.
- **Decisions:** append new decisions to the relevant phase `discovery/decisions.md` with the next free ID (never renumber or reuse IDs; cross-references rely on stable IDs).
- **Teacher-facing reports** may be Vietnamese; everything else in English.
- This repo is a dependency (not the implementation) for the sister code repos (`pbl6-backend`, `pbl6-web`, `pbl6-mobile`, `pbl6-ai`) — reference docs here, don't duplicate.