# API Contract Change Tracking — Research & POC

**Task:** P4-27  
**Status:** Draft for team review  
**Scope:** Contract change tracking; not runtime business audit logging

## Problem statement

`api-docs/src/` is the canonical OpenAPI source used by backend, web and mobile handoff. `reference/rentify.json` is generated for Apidog with `npm run bundle`. Without an automated diff and change report, a client developer must inspect commits or Apidog manually to discover whether a route, request, response, schema, enum, required field or security contract changed.

The desired record answers five questions:

1. What changed?
2. Is the change breaking, non-breaking or informational?
3. Which client-facing contract element is affected?
4. When and in which commit/PR did it change?
5. What action is expected from FE/Mobile?

## Options evaluated

| Approach | Accuracy | Automation | Breaking-change detection | Cost | Maintenance | Polyrepo fit | Assessment |
|---|---|---|---|---|---|---|---|
| Git/PR template and manual changelog | Depends on author; misses unmentioned changes | Low | None unless manually assessed | Low | Low initially, high over time | Good | Useful as context, insufficient as the source of truth |
| CI diff of canonical OpenAPI source | High when source is valid and bundled consistently | High | High for structural OpenAPI changes | Low | Medium | Good | Recommended foundation |
| Hosted API registry/documentation platform | Depends on provider import/version model | High after setup | Varies by product and plan | Medium–high | Medium | Varies | Useful later, but introduces account/vendor dependency |
| Apidog-only history | Tracks imported/synced artifacts, not necessarily the PR source | Medium | Varies by sync workflow | Existing cost | Medium | Weak for independent service repos | Keep as a consumer of the report, not the canonical tracker |

## Recommendation

Use a source-first, CI-generated OpenAPI diff:

- The pull request changes canonical YAML under `api-docs/src/` or a service-owned OpenAPI source.
- CI lints and bundles the source into a temporary artifact.
- CI compares the base and head bundles, not the committed generated file, to avoid duplicate changes caused by `reference/rentify.json`.
- The diff tool classifies structural changes. The POC adds project metadata (commit, PR, timestamp and source repository) and writes a Markdown report.
- The report is attached to the PR and, after merge, appended to a durable API changelog or published as a release artifact.
- Apidog remains a consumer for testing/documentation; it is not a second contract authority.

The repository POC is intentionally dependency-light: it uses Redocly's existing bundle command and a Node script to generate a readable report. A production follow-up should replace or extend the classifier with a maintained OpenAPI diff tool after the team reviews its classification semantics against the project contract.

## POC workflow

```text
canonical YAML source
        │
        ├── lint
        ├── bundle base + head to temporary JSON
        ├── compare structural OpenAPI contract
        └── publish Markdown report with commit/PR/timestamp metadata
                         │
                         ├── PR reviewer checks breaking changes
                         └── FE/Mobile reads impact and required action
```

Run locally from `api-docs/`:

```bash
npm run lint
npm run bundle
npm run contract:report -- --base scripts/fixtures/base.yaml --head scripts/fixtures/non-breaking.yaml --output reports/poc-non-breaking.md --commit local-poc --pr 27
npm run contract:report -- --base scripts/fixtures/base.yaml --head scripts/fixtures/breaking.yaml --output reports/poc-breaking.md --commit local-poc --pr 27
```

The POC only accepts source specifications as comparison inputs. It bundles each input into a temporary file and never compares `reference/rentify.json` as an independent change. A production CI job should fail or require review when a breaking change is detected, while allowing an explicit override with a migration note.

## Change-log format

Each entry should contain:

| Field | Purpose |
|---|---|
| `timestamp` | When the report was generated, in UTC/ISO-8601 |
| `repository` | Repository containing the canonical source |
| `commit` | Exact commit introducing the change |
| `pull_request` | Review context and discussion link |
| `source` | OpenAPI source and service/spec identity |
| `classification` | `breaking`, `non-breaking` or `informational` |
| `location` | Path/method, schema, parameter or security scheme |
| `change` | Human-readable before/after summary |
| `client_impact` | Required action for FE/Mobile |
| `migration_note` | Compatibility or rollout instructions |

Sensitive values, tokens and production payloads must never be copied into the report.

## Classification baseline

- Removed path, operation, parameter, response, property or enum value: breaking.
- Newly required request field or newly required parameter: breaking.
- Added path, operation, optional field, optional parameter or enum value: non-breaking.
- Description, example or documentation-only change: informational/non-breaking.
- Security scheme or operation security requirement changes require explicit review; the implementation must not silently label them safe.

These are initial project rules. The production implementation must validate them against the selected diff tool and document exceptions for gateway/service splits under D58.

## Rollout proposal

1. Run the POC and review its two fixture reports with BE, FE, Mobile and PM.
2. Select and pin the production diff tool/version in CI.
3. Add PR validation to the canonical contract repository and require a migration note for breaking changes.
4. Publish merged reports as a versioned changelog/release artifact discoverable from Apidog and the team docs.
5. Extend the same workflow to each service-owned spec after the D58 split is implemented; keep the gateway/client-facing contract report separate from internal service contracts.

## Open decisions for the follow-up implementation task

- Whether the durable log is a Markdown file in Git, PR artifacts plus releases, or a hosted registry.
- Whether breaking changes block merge or only require a designated reviewer override.
- The final diff engine and its version-pinning/update policy.
- Notification channel for FE/Mobile after merge.
