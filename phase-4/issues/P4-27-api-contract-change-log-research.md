# P4-27 — Research & POC: Automated API Contract Change Log

**Status:** 🟡 Open  
**Owner:** BE/API Lead + PM review  
**Reviewers:** FE Lead, Mobile Lead, service owners  
**Estimate:** 5 points · 10–16 hours  
**Priority:** High — protects the API handoff between BE, FE and Mobile

## Background

Web and Mobile implement against `api-docs/` independently from backend service implementation. A contract change currently depends on a developer noticing the change in Git history or Apidog. That makes it difficult to answer, after the fact, which endpoint, request/response field, schema, enum or security rule changed, when it changed, why it changed and whether clients are affected.

This task covers API contract change tracking only. It does not add or change the runtime business `AuditLog` API/entity.

## Objective

Research and validate an automated workflow that detects changes to the canonical OpenAPI source, classifies their client impact, and produces a readable change log/report linked to the commit or pull request that introduced the change.

## Scope

- Compare at least three approaches:
  - Git history/PR-based changelog.
  - CI-based OpenAPI diff and breaking-change checks.
  - OpenAPI diff/changelog tooling and its integration with GitHub, Apidog, `api-docs`, and service repositories.
- Evaluate accuracy, automation, breaking/non-breaking detection, cost, maintenance, polyrepo support and FE/Mobile discoverability.
- Build the POC in `api-docs/scripts/contract-change-report.mjs` with YAML fixtures for one breaking and one non-breaking change.
- Make the POC bundle source specifications before comparison and treat `reference/rentify.json` as generated output, so a generated-file-only change is not logged as a second contract change.
- Produce `pm/phase-4/discovery/api-contract-change-tracking.md` with the recommendation, report format, CI/PR workflow, ownership, generated-artifact rules and rollout proposal.

## Out of scope

- Runtime audit events, business activity history or changes to the `AuditLog` schema.
- Full CI rollout across all sister repositories.
- Client SDK generation or automatic client code migration.
- Changing the current OpenAPI contract as part of this research.

## Acceptance criteria

- [ ] The research identifies change categories covering endpoints, methods, parameters, request/response schemas, fields, enums, required fields and security contracts.
- [ ] At least three approaches are compared using accuracy, automation, breaking-change detection, cost, maintainability and polyrepo support.
- [ ] The POC runs against two YAML fixtures and produces a report that FE/Mobile can read without inspecting the diff manually.
- [ ] The report includes the changed path/schema/field, impact classification, timestamp, commit/PR metadata and client impact.
- [ ] The POC distinguishes canonical source from `npm run bundle` output and does not duplicate a source change because of `reference/rentify.json`.
- [ ] The documented workflow covers PR validation, diff generation, log publication and notification or artifact discovery for FE/Mobile.
- [ ] PM, BE, FE and Mobile review the recommendation before a follow-up implementation task is created.

## Verification

- [ ] `npm run lint` succeeds for the unchanged canonical contract.
- [ ] `npm run bundle` succeeds for the unchanged canonical contract.
- [ ] The POC classifies the breaking fixture as breaking and the optional-field fixture as non-breaking.
- [ ] The generated report names the correct path/schema/field and includes commit/PR/timestamp metadata.
- [ ] Re-running the workflow after changing only the generated bundle does not create a duplicate contract-change entry.
- [ ] FE and Mobile reviewers can identify what action is required from the report alone.

## Dependencies

- `api-docs/` OpenAPI source and existing `npm run lint` / `npm run bundle` scripts.
- P4-15 Apidog environment and authentication automation.
- D58 service/repository boundaries and D59 contract/event ownership decisions.

## Deliverables

- Runnable POC script and fixtures under `api-docs/scripts/`.
- POC report under `api-docs/reports/`.
- Research and recommendation at `pm/phase-4/discovery/api-contract-change-tracking.md`.
