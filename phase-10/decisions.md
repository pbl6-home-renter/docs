# Phase 10 decisions

## P10-D87 — Tenant room hub (2026-11-15 UTC)

The user requested P10-14 and delegated the design. The endpoint returns a paginated list with one item per active contract, including room and building identifiers, names, address, room area, contract dates and contract rent. No matching contract returns an empty list. Multiple contracts are returned in descending start-date order with contract ID as a tie-breaker. The named tenant and currently linked members have the same access as `/me/contracts`; soft-deleted contracts, rooms and buildings are excluded. Payment, invoice payment state, issue counts and contact details are not inferred. This decision enables the API independently of the P10-15 lite web flow, which continues to use its existing endpoints. The response replaces the old unimplemented draft schema.

## P10-D86 — Issue reports and notifications (2026-11-14 UTC)

The user approved implementing P10-28 and P10-29 with Community Service owning issue reports. Each issue is associated with a room and its active contract at creation. The room's landlord and current contract tenants can create and view issues. A landlord can create a report for a tenant who does not use the application. Tenants lose access after leaving; other landlords and tenants outside the contract cannot access the report or its images. Authorization is enforced by the backend on every request.

The landlord can move an issue from `open` to `in_progress` and then `resolved`. Its creator can cancel it before resolution. Resolved and cancelled issues are terminal. Concurrent actions must preserve these transitions.

Images and notifications are in scope. Images use the existing private Media service and a real IssueReport ownership resolver. Since Media requires an existing owner, create the issue before uploading its images. Only completed images attached to that issue may be shown. Notifications use English event keys and data in the backend payload, translated by the frontend. Notification recipients must be authorized for the issue, with retry-safe delivery. The `@issue` chat command and tagging are out of scope.

This decision supersedes the IssueReport deferral in P6-D61 and P9-D83 for this work; it does not change the scope of payment, deposit settlement, OCR, or other deferred features. OpenAPI and the implementation must describe the implemented contract consistently.
