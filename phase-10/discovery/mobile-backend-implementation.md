# Backend mobile fixes - implementation 18/11/2026

The user approved [the audited plan](../../tasks/plan.md), then requested removing fallback/repair scripts. P10-D91 supersedes the maintenance/bootstrap part of P10-D90. Changes are split into review branches below; nothing has been merged or deployed.

## Implemented

- P10-31: create resolves an absent tenant ID from the existing active Identity phone projection. Activate retries for an old NULL draft before representative creation and the activation snapshot. Phone locks precede contract/room locks; existing IDs are retained.
- P10-33: list returns ward/buildingName; detail returns address/ward/province directly from building. Room address schemas/examples no longer require district.
- P10-34/35: Identity contact lookup fills landlord id/name/phone without email. Missing/deleted/non-landlord owners yield 404; Identity errors yield 503. Room visibility checks run before lookup.
- P10-36: list/detail return photoUrls/photoMediaIds. Nullable deprecated thumbnailUrl supports older list clients. Only uploaded room cover/gallery display URLs are exposed; metadata paths are not image fallbacks.
- P10-24: tenant favorite GET/POST/DELETE, uniqueness and migration, viewer-specific flags and private caching. Only eligible public available rooms are listed; hidden rooms remain removable. Duplicate POST is 409; absent DELETE is 404; empty GET is 200 without requiring a tenant profile.
- OpenAPI source/bundle and normal unit/PostgreSQL regression tests remain. CI includes the PostgreSQL tests.

## Removed at the user's request

P10-32's maintenance CLI, bootstrap/snapshot endpoint, supporting application helper/types/queries, dedicated tests and documentation have been removed. The Identity lifecycle subscriber is restored to its original implementation; Identity Service no longer needs changes for this task. Existing outbox/inbox/retry behavior and pre-existing operational tools remain as before. No manual fallback/repair script is required for acceptance.

## Verification

After removal: Tenancy has 165 passing unit tests (10 existing skips) and 7 passing PostgreSQL tests. Tenancy and Identity build/lint pass; Identity source and the lifecycle subscriber match their original implementations. Diff whitespace checks pass. OpenAPI public source/bundle are unchanged by this removal; its earlier lint/bundle passed (18 existing unrelated warnings).

## Remaining environment checks

1. Review/merge/deploy Tenancy and API spec; run the favorite migration before traffic. This delivery includes feature branches for the user to open PRs, with no merge, deployment or live data change.
2. Verify existing lifecycle event delivery and tenant access in staging. Independent-connection races and RabbitMQ delivery are not simulated by the in-memory PostgreSQL tests.
3. Upload/complete/attach a real room photo with a landlord test account and render it in mobile.
4. P10-37 needs the actual Android source/build. Local mobile remains a scaffold; verify /me/contracts or /me/room-hub instead of public /rooms or landlord /me/rooms.

## PR branches and creation order

No PR is opened automatically. Use the exact base/head pairs below so each review contains only its slice. Backend PRs form a stack; API and PM PRs target their own repository's main independently. The repositories currently have no develop branch.

| PR | Repository | Base | Head | Files in slice |
|---|---|---|---|---|
| 1 | Tenancy-Service | main | fix/p10-31-contract-tenant-phone-link | 4 |
| 2 | Tenancy-Service | fix/p10-31-contract-tenant-phone-link | fix/p10-33-room-public-details | 14 |
| 3 | Tenancy-Service | fix/p10-33-room-public-details | feat/p10-24-tenant-favorite-rooms | 15 |
| 4 | Tenancy-Service | feat/p10-24-tenant-favorite-rooms | ci/p10-mobile-backend-postgres | 8 |
| 5 | api-doc | main | docs/p10-mobile-backend-contract | 10 |
| 6 | docs | main | docs/p10-mobile-backend-delivery | 15 |

Review the backend stack in order 1 to 4. Under the team's squash-merge convention, rebase each child onto the updated main and change its PR base to main after its parent is merged, before merging that child. Do not merge a child into a stale feature branch. Use the parent commit as the old rebase boundary (record it before updating the stack); no force-push or merge is performed as part of this branch delivery.

### PR 1 - Fix tenant linking when a contract is created or activated

When a tenant account already exists, entering its phone while creating a contract could leave tenantId NULL. Resolve absent IDs from the existing active-tenant phone projection at creation and retry before activation creates the representative and context snapshot. Preserve explicit IDs and the phone-before-contract/room lock order.

Validation: 8 focused contract tests, build and lint pass. This PR adds no maintenance/replay/bootstrap tooling.

### PR 2 - Return complete public room address, owner and photo data

Room lists now expose ward/buildingName and details expose address/ward/province plus landlord id/name/phone through the existing Identity internal API. Keep visibility checks, distinguish missing owners from Identity outages, and return only uploaded room-photo display URLs. A nullable deprecated thumbnailUrl alias supports existing list clients.

Validation: 5 focused response/photo tests, build and lint pass. The existing isFavorited response flag is modeled explicitly; persistence and viewer-specific lookup are added by PR 3.

### PR 3 - Implement tenant favorite-room APIs

Add caller-scoped GET/POST/DELETE favorite rooms, unique tenant/room persistence and the required migration. Available rooms in approved buildings may be saved/listed; hidden rooms remain removable. Empty lists return 200 without a tenant profile, duplicate saves return 409 and absent removals return 404. Populate viewer-specific isFavorited and vary authenticated search caching by Authorization.

Validation: 2 focused command tests, build and lint pass; the PostgreSQL regression suite is delivered by PR 4. Run the new migration before serving this feature.

### PR 4 - Run PostgreSQL regressions in CI without external database credentials

Add a PGlite-backed test harness that executes the production TypeORM SQL in memory, covers contract tenant linking/access and favorite uniqueness/filtering/pagination/migration up/down, and runs as a separate CI step. It needs no Docker, .env or remote database and does not add operational fallback scripts.

Validation: 165 unit tests and 7 PostgreSQL tests pass; 10 existing unit tests remain skipped. Build and lint pass. Independent-connection races and RabbitMQ/mobile integration still need staging checks.

### PR 5 - Align OpenAPI with tenant linking, room responses and favorites

Document phone-based linking on create/activate, complete building address/contact fields, photoUrls/photoMediaIds with the thumbnail compatibility alias, and implemented favorite behavior. Remove export formats not supported by these list routes and regenerate reference/rentify.json.

Validation: OpenAPI lint and bundle pass; 18 pre-existing unrelated warnings remain. Coordinate API release with backend PRs 1 to 3.

### PR 6 - Record approved mobile backend scope and verification

Update the plan, requirements amendment, decisions and task tracker with the implementation evidence, review branches and remaining environment checks. P10-D91 records the explicit removal of maintenance/bootstrap/fallback scripts; P10-32 is retired. Existing Identity code and the RabbitMQ lifecycle consumer are unchanged.

Validation: documentation link and whitespace checks. No code merge, production repair or mobile acceptance is claimed.
