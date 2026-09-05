---
name: pm-context
description: Load the full context of the PBL6 PM/docs hub (pm/) so agents can make well-grounded decisions about scope, schedule, business rules, and issues. Use when opening work in this repo, before proposing scope/plan changes, or before answering questions that depend on requirements, phase status, or past decisions.
license: Apache-2.0
metadata:
  version: "1.0.0"
  category: context
  author: PBL6 PM
---

# PBL6 PM Context Loader

Orient an agent to the PBL6 management & docs hub (`pm/`) so every decision is grounded in the repo's single source of truth.

## When to Use

- Before starting any task in this repo that touches scope, schedule, business rules, or role/assignee questions.
- Before proposing a feature or change that may go beyond existing requirements.
- Before answering a teammate's question that depends on requirements, phase status, or past decisions.

## When NOT to Use

- The full context was already loaded earlier in this session and nothing changed.
- The task is a pure formatting/typo edit with no decision impact.

## Required Reading (in order)

1. `README.md` — index of phases, SoT locations, task-tracking scheme.
2. `requirement.md` — **scope SoT**. Never propose beyond it without PM approval.
3. `PROJECT_PLAN.md` — **schedule SoT** (13–14 weeks, milestones on odd-week checkpoints). Use it to determine the current phase + date window.
4. `<current-phase>/README.md` — phase scope and dependency order (e.g. `phase-1/README.md`).
5. `<current-phase>/issues/README.md` — issue/backlog status table (`🟡 Open` / `🔵 In progress` / `🟢 Done` / `⚪ Blocked` / `⏪ Deferred`).
6. Decision log(s): `phase-N/discovery/decisions.md` for all completed phases — the canonical record of accepted decisions (IDs D1…D29+). New decisions must append the next free ID, never renumber.
7. Role-relevant context (as applicable): `feature-list.md`, `business-rules.md`, `discovery/` outputs, `discovery/user_flow/`, `product-sketch.md`, `market-analysis.md`.

## Output — Context Brief

After reading the docs above, produce a concise brief:

- **Product & phase:** one-liner positioning + current phase and its date window.
- **Scope boundary:** what is MVP vs Phase 1+ / out-of-scope, with `requirement.md` section refs.
- **Key decisions:** the accepted decision IDs relevant to the task (cite `decisions.md`).
- **Issues:** relevant issue IDs + title + status + assignee + depends-on.
- **Uncertainty list:** explicit list of anything you could not determine. Do NOT guess.

## Rules

- Never invent features beyond `requirement.md`; flag to PM if scope seems unclear.
- When a new decision is needed, propose a new ID (next free number in the relevant `decisions.md`) on the correct date; record UTC.
- If docs conflict on a time-sensitive fact, flag the conflict — do not silently pick one.
- Language: English for docs/commits/API. Vietnamese only in teacher-facing reports.