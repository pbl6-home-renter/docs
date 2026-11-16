# P10-25 — Basic roommate profile API

**Type:** Backend · **Status:** 🟡 Open — scope approved, implementation pending
**Suggested owner:** BE Lead / assignee TBD · **Reviewer:** PM / API owner
**Repos:** `Tenancy-Service`, `api-doc` · **Depends on:** P10-11, P1-13, [P10-D88](../decisions.md)
**Estimate:** TBD · **Issue:** `docs#TBD`

## Scope and source of truth

P10-D88 approves the profile portion of the older D28 Stretch feature for Phase 10. An account-holding tenant can save their own profile and browse basic profiles. Implement `GET /roommate-profiles`, `GET /roommate-profiles/{roommateProfileId}`, and `GET/PUT /me/roommate-profile`. These operations are currently `designing` in OpenAPI. P10-26 match requests, AI scoring/advice, and P10-27 Web UI remain deferred. The old P1-13 rule that an active contract always hides the profile is superseded here.

Tenancy Service owns profile storage and eligibility because it owns rooms, contracts and members. Identity supplies account role/status, name and public avatar through the existing internal lookup. Do not store or expose Identity email/phone in the public profile, infer contact information, or query another service's database.

## Fields and behavior

| Field | PUT | GET my profile | Public list/detail |
|---|---|---|---|
| `id`, `tenantId` | Server-owned | Returned | Returned |
| `isVisible` | Required | Returned as saved | Always `true` for eligible results |
| `bio` | Nonempty when visible | Returned | Returned |
| `gender`, `birthYear`, `occupation` | Optional | Returned | Returned if supplied |
| `preferredProvince`, `preferredDistrict`, `preferredArea` | Optional | Returned | Returned if supplied |
| `budgetMin`, `budgetMax`, `moveInOn` | Optional | Returned | Returned if supplied; min <= max when both exist |
| `lifestyle` | Optional typed flags | Returned | Returned if supplied |
| `tenantName`, `avatarUrl` | Not accepted | Not required for editing | Resolved from Identity; never fabricated |

Omit `personality`, `idVerified`, `matchScore`, `aiMatchScore`, `aiAdvice`, `isDiscoverable`, and `visibilityReason` from this slice. `GET /me/roommate-profile` must return all fields that can be saved, so a tenant can edit a previously saved profile. Do not require AI-specific hard-filter inputs merely to create a basic profile.

These omissions apply to P10-25 only. Later matching work may add approved profile inputs and a separate contract for viewer-dependent AI scores/advice; existing basic profiles must remain valid when those features are introduced. See P1-13 for the deferred matching design and P10-D88 for the decisions that supersede it.

`isVisible` is the tenant's persisted opt-in. An active contract does not automatically turn it off. Search and other-user detail require `isVisible=true`, an active tenant account, and capacity eligibility. No active contract means the tenant may appear. For active contracts, at least one current room must have a vacancy. `maxOccupancy=null` means no configured limit. Count the lead tenant plus distinct current contract members, including unlinked members without accounts; apply effective join/leave dates and do not double-count the lead. A full room hides the profile from others without changing `isVisible`; it can reappear when capacity changes. With several active contracts, one room with a vacancy suffices. Recompute eligibility for list and detail rather than trusting stale cached visibility.

Only active tenant accounts may use these operations. A tenant can read their own hidden profile. List excludes hidden/ineligible profiles; other-user detail returns 404 for a hidden/ineligible profile, including a previously visible ID. Never expose email, phone, contract or member records. If Identity cannot supply required public name/account state, fail closed rather than inventing data. List pagination and the `preferredArea` filter apply after eligibility filtering so counts reflect only visible results.

## Implementation and verification

1. Add Tenancy profile persistence, generated migration, owner-only PUT/GET, and list/detail queries. Use Identity internal lookup only for required user display/status data. Validate `bio` when visible, budget range, date and optional lifestyle shape.
2. Apply one eligibility rule to list and detail. Verify a tenant with no contract, a room with one open place, a full room, `maxOccupancy=null`, multiple active contracts, unlinked members, scheduled joins/leaves, and lead/member duplication. Check that changing capacity or membership affects search without overwriting `isVisible`.
3. Verify role and privacy: tenant cannot edit another profile; landlord/admin/locked account cannot access; hidden/full profile cannot be opened by ID; Identity failure does not reveal or fabricate data. Run build/lint/tests and smoke all four operations through Gateway with real data.
4. After the feature is complete and verified, align OpenAPI request/response DTOs, visibility/error behavior and examples with P10-D88. Lint and bundle `api-doc`; do not mark operations `released` before implementation and verification. Until then, leave the existing `api-doc` draft unchanged.

## Acceptance

- The four operations match the approved contract, ownership and pagination rules; public responses contain only approved fields.
- Saved fields round-trip through `GET /me/roommate-profile`; `birthYear` is optional, and no AI fields or match request behavior appear.
- A full room temporarily removes the profile from list/detail while preserving the tenant's `isVisible` choice; a room with a vacancy or no active contract follows the rules above.
- Authorization, privacy, empty/error cases and Gateway behavior have verification evidence. No status is marked `released` solely because YAML or code exists.
