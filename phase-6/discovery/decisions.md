# Phase 6 decisions

> Published decision P6-D60 is preserved below. Subsequent decisions D61–D75 are maintained in [../decisions.md](../decisions.md).

## D60 — Meter reading baseline and bulk behavior (2026-11-01)

The following clarifies P6-02e/P6-02f, supersedes the replacement-baseline value in D34, and resolves the pending bulk scope from D47.

- For any baseline, the landlord may provide `previousReading` as `0` or the actual starting meter value and confirms `currentReading`. If omitted on the first baseline, `previousReading` defaults to `0`; a later baseline requires the landlord to provide it. Subsequent non-baseline readings derive `previousReading` from the latest `currentReading` on the server.
- Bulk records non-baseline readings only. A missing baseline in any submitted entry fails the whole request.
- Bulk accepts any subset of rooms in one building, with electricity, water, or both for each room. The request is atomic. `totalRoomsRecorded` counts distinct room IDs recorded by that request; an invoice still needs both meter types.
- A successful bulk response has only `SUCCESS` results. Invalid entries return an HTTP error and roll back the request. `WARNING` is deferred until a rule is defined.
- Bulk accepts no more than 200 reading entries. `readingMethod` is removed because it is not used by the recording flow.

The error code for a missing baseline in bulk and the permitted decimal scale remain open contract details. This decision does not change the separate OCR/media work.
