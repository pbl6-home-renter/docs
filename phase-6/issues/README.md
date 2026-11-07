# Phase 6 â€” Task tracker

Use [`_TEMPLATE.md`](_TEMPLATE.md) v2. Each task links to its GitHub issue; assignees below follow the task documents. GitHub issue states were checked on 2026-11-01. A split parent remains open until its implementation sub-issues are complete.

## Decisions and prerequisites

- [Published P6-D60](../discovery/decisions.md): baseline inputs and **atomic bulk** (PR #94). One invalid reading rolls back the whole request; successful responses contain only `SUCCESS` results.
- [P6-D61â€“D75](../decisions.md): Payment/deposit settlement deferred; Contract, Invoice, MeterReading, OCR, media and tenant-linking decisions. P6-D75 defines source precedence.
- It5: 02/11â€“08/11. It6: 09/11â€“15/11. It7: 16/11â€“22/11.
- Project #3 field synchronization is pending: the current GitHub credentials do not grant Projects access. This table records the intended iterations; it does not claim those fields were applied remotely.

## Iteration 5 â€” core work and prerequisites

| ID / GitHub | Task | Assignee | Estimate | Status | Dependencies |
|---|---|---|---|---|---|
| [P6-01](P6-01-tenancy-contract-vertical-slice.md) Â· [#64](https://github.com/pbl6-home-renter/docs/issues/64) | Contract vertical slice (Epic) | leminhkhai345 | 18 It5 + 8 It6 | ðŸŸ¡ Open | P5-08, P5-09, P6-04 |
| [P6-01a](P6-01a-contract-domain-persistence.md) Â· [#65](https://github.com/pbl6-home-renter/docs/issues/65) | Contract domain model, persistence vÃ  migration | leminhkhai345 | 3 points | ðŸŸ¢ Done | P5-09a |
| [P6-01b](P6-01b-contract-create-and-manage-draft.md) Â· [#66](https://github.com/pbl6-home-renter/docs/issues/66) | Táº¡o vÃ  quáº£n lÃ½ há»£p Ä‘á»“ng nhÃ¡p | leminhkhai345 | 5 points | ðŸŸ¢ Done | P6-01a, P5-09b |
| [P6-01c](P6-01c-contract-template-and-draft-document.md) Â· [#67](https://github.com/pbl6-home-renter/docs/issues/67) | Máº«u há»£p Ä‘á»“ng, Ã¡p máº«u vÃ  sinh tÃ i liá»‡u nhÃ¡p | leminhkhai345 | 5 points | ðŸŸ¢ Done | P6-01b, P6-04 |
| [P6-01d](P6-01d-contract-activate-signed-file.md) Â· [#68](https://github.com/pbl6-home-renter/docs/issues/68) | Upload báº£n kÃ½ vÃ  kÃ­ch hoáº¡t há»£p Ä‘á»“ng | leminhkhai345 | 5 points | ðŸŸ¡ Open | P6-01b, P6-04 |
| [P6-02](P6-02-tenancy-billing-vertical-slice.md) Â· [#70](https://github.com/pbl6-home-renter/docs/issues/70) | Billing vertical slice (Epic) | huynhtiennhat0403 | 20 It5 + 14 It6 | ðŸŸ¡ Open | P5-09, P5-08b |
| [P6-02a](P6-02a-billing-contract-alignment.md) Â· [#71](https://github.com/pbl6-home-renter/docs/issues/71) | Chá»‘t contract Billing theo D39 | huynhtiennhat0403 | 2 points | ðŸŸ¡ Open | â€” |
| [P6-02b](P6-02b-rate-policy-domain-persistence.md) Â· [#72](https://github.com/pbl6-home-renter/docs/issues/72) | RatePolicy domain vÃ  persistence | huynhtiennhat0403 | 3 points | ðŸŸ¡ Open | P6-02a |
| [P6-02c](P6-02c-rate-policy-api.md) Â· [#73](https://github.com/pbl6-home-renter/docs/issues/73) | API RatePolicy (táº¡o, batch tÃ²a, sá»­a, táº¯t, liá»‡t kÃª) | huynhtiennhat0403 | 5 points | ðŸŸ¡ Open | P6-02b, P5-09b, P5-08b |
| [P6-02d](P6-02d-billing-setting.md) Â· [#74](https://github.com/pbl6-home-renter/docs/issues/74) | BillingSetting domain + API | huynhtiennhat0403 | 3 points | ðŸŸ¡ Open | P6-02a, P6-02c |
| [P6-02e](P6-02e-meter-reading-create-list.md) Â· [#75](https://github.com/pbl6-home-renter/docs/issues/75) | MeterReading: nháº­p tay tá»«ng chá»‰ sá»‘ vÃ  liá»‡t kÃª | huynhtiennhat0403 | 5 points | ðŸŸ¡ Open | P6-02a, P5-09b |
| [P6-02f](P6-02f-meter-reading-bulk.md) Â· [#76](https://github.com/pbl6-home-renter/docs/issues/76) | Chá»‘t chá»‰ sá»‘ hÃ ng loáº¡t theo tÃ²a | huynhtiennhat0403 | 2 points | ðŸŸ¡ Open | P6-02e |
| [P6-03](P6-03-fe-landlord-building-room-screens.md) Â· [#79](https://github.com/pbl6-home-renter/docs/issues/79) | MÃ n hÃ¬nh Building/Room cho Landlord vÃ  duyá»‡t Building cho Admin (Epic) | ThaiBao11125 | 18 points tá»•ng (P6-03a 5 | ðŸŸ¢ Done | P5-01, P5-07, P5-08, P5-09, P6-04, P6-03b |
| [P6-03a](P6-03a-fe-building-api-list-detail.md) Â· [#80](https://github.com/pbl6-home-renter/docs/issues/80) | Building API layer, danh sÃ¡ch vÃ  chi tiáº¿t Building cá»§a tÃ´i | ThaiBao11125 | 5 points | ðŸŸ¢ Done | P5-08c |
| [P6-03b](P6-03b-fe-building-create-edit-delete.md) Â· [#81](https://github.com/pbl6-home-renter/docs/issues/81) | Wizard táº¡o Building, sá»­a vÃ  xÃ³a Building | ThaiBao11125 | 5 points | ðŸŸ¢ Done | P6-03a, P5-08b, P5-08c, P5-08f, P6-04 |
| [P6-03c](P6-03c-fe-room-list-create-edit.md) Â· [#82](https://github.com/pbl6-home-renter/docs/issues/82) | Danh sÃ¡ch, táº¡o, sá»­a, xÃ³a Room trong má»™t Building | ThaiBao11125 | 5 points | ðŸŸ¢ Done | P6-03a, P5-09b, P5-09c |
| [P6-03d](P6-03d-fe-admin-building-approval.md) Â· [#83](https://github.com/pbl6-home-renter/docs/issues/83) | Admin duyá»‡t/tá»« chá»‘i Building | ThaiBao11125 | 3 points | ðŸŸ¢ Done | P6-03a, P5-08d |
| [P6-04](P6-04-identity-media-presign-upload.md) Â· [#84](https://github.com/pbl6-home-renter/docs/issues/84) | Media upload 2 bÆ°á»›c (presign â†’ PUT â†’ complete) vÃ  Ä‘á»c/xÃ³a media | baoduong17 | 8 points | ðŸŸ¡ Open | P6-03b, P6-03d |
| [P6-08](P6-08-tenancy-administrative-units.md) Â· [#89](https://github.com/pbl6-home-renter/docs/issues/89) | Local administrative geography API (Tenancy) | baoduong17 | 3 points | ðŸŸ¢ Done | â€” |

| [P6-11](P6-11-tenancy-internal-ownership.md) · [#110](https://github.com/pbl6-home-renter/docs/issues/110) | Tenancy: `GET /internal/ownership/{ownerType}/{ownerId}` cho Media | baoduong17 | 2 points | 🟢 Done | P6-01e1, P6-02h |
| [P6-12](P6-12-identity-internal-media-lookup.md) · [#111](https://github.com/pbl6-home-renter/docs/issues/111) | Identity: `GET /internal/media/{mediaId}` cho service nội bộ | baoduong17 | 1 point | 🟢 Done | P6-04 |

## Iteration 6 â€” implementation backlog

| ID / GitHub | Task | Assignee | Estimate | Status | Dependencies |
|---|---|---|---|---|---|
| [P6-01e](P6-01e-contract-members-and-checkout.md) Â· [#69](https://github.com/pbl6-home-renter/docs/issues/69) | ThÃ nh viÃªn HÄ, HÄ cá»§a tenant, checkout (Ä‘Ã£ tÃ¡ch) | leminhkhai345 | 8 points (tá»•ng e1â€“e3) | ðŸŸ¡ Open Â· split | P6-01d |
| [P6-01e1](P6-01e1-contract-members.md) Â· [#95](https://github.com/pbl6-home-renter/docs/issues/95) | ThÃ nh viÃªn há»£p Ä‘á»“ng: báº£ng, tá»± thÃªm Ä‘áº¡i diá»‡n khi activate, API thÃªm/xem/sá»­a/rá»i | leminhkhai345 | 3 points | ðŸŸ¡ Open | P6-01d |
| [P6-01e2](P6-01e2-tenant-my-contracts.md) Â· [#96](https://github.com/pbl6-home-renter/docs/issues/96) | Tenant xem há»£p Ä‘á»“ng cá»§a mÃ¬nh (`GET /me/contracts`) | leminhkhai345 | 2 points | ðŸŸ¡ Open | P6-01e1 |
| [P6-01e3](P6-01e3-contract-checkout.md) Â· [#97](https://github.com/pbl6-home-renter/docs/issues/97) | Checkout: káº¿t thÃºc há»£p Ä‘á»“ng, member rá»i, phÃ²ng chuyá»ƒn `maintenance` (+ sá»­a sá»‘ xe khi HÄ `active`) | leminhkhai345 | 3 points | ðŸŸ¡ Open | P6-01e1, P6-01d, P6-02g1 |
| [P6-02g](P6-02g-invoice-outline.md) Â· [#77](https://github.com/pbl6-home-renter/docs/issues/77) | Invoice: sinh theo tÃ²a + ká»³, phÃ¡t hÃ nh, há»§y, tenant xem (issue cha) | huynhtiennhat0403 | 11 points (tá»•ng sub-issue) | ðŸŸ¡ Open Â· split | P6-02c, P6-02e, P6-02h, P6-01e1, P6-01e2 |
| [P6-02g1](P6-02g1-invoice-domain-calculator.md) Â· [#98](https://github.com/pbl6-home-renter/docs/issues/98) | Invoice: aggregate, báº£ng `invoices` vÃ  calculator tÃ­nh tiá»n thuáº§n | huynhtiennhat0403 | 3 points | ðŸŸ¡ Open | P6-02c, P6-02e |
| [P6-02g2](P6-02g2-invoice-generate.md) Â· [#99](https://github.com/pbl6-home-renter/docs/issues/99) | Invoice: sinh / tÃ­nh láº¡i hÃ³a Ä‘Æ¡n `pending` theo tÃ²a + ká»³ | huynhtiennhat0403 | 3 points | ðŸŸ¡ Open | P6-02g1, P6-02h, P6-01e1, P6-09 |
| [P6-02g3](P6-02g3-invoice-landlord-manage.md) Â· [#100](https://github.com/pbl6-home-renter/docs/issues/100) | Invoice: landlord xem, sá»­a phÃ­ khÃ¡c, phÃ¡t hÃ nh hÃ ng loáº¡t, há»§y | huynhtiennhat0403 | 3 points | ðŸŸ¡ Open | P6-02g2, P6-09 |
| [P6-02g4](P6-02g4-invoice-tenant-view.md) Â· [#101](https://github.com/pbl6-home-renter/docs/issues/101) | Invoice: tenant xem hÃ³a Ä‘Æ¡n cá»§a mÃ¬nh | huynhtiennhat0403 | 2 points | ðŸŸ¡ Open | P6-02g3, P6-01e2, P6-01e1, P6-09 |
| [P6-02h](P6-02h-meter-reading-ocr-preview.md) Â· [#78](https://github.com/pbl6-home-renter/docs/issues/78) | MeterReading: migration, baseline ká»³ Ä‘áº§u, `source`/`ocrValue`, `PATCH` cÃ³ khÃ³a ká»³ | huynhtiennhat0403 | 3 points | ðŸŸ¡ Open | P6-02g1, P6-02g2 |
| [P6-06](P6-06-fe-contract-invoice-screens.md) Â· [#86](https://github.com/pbl6-home-renter/docs/issues/86) | MÃ n Há»£p Ä‘á»“ng, Chá»‰ sá»‘ Ä‘iá»‡n nÆ°á»›c vÃ  HÃ³a Ä‘Æ¡n cho landlord (Web) â€” Epic | ThaiBao11125 | 12 points | ðŸŸ¡ Open Â· split | P6-03c, P6-01b, P6-02e, P6-02g1 |
| [P6-06a](P6-06a-fe-contract-list-create-activate.md) Â· [#102](https://github.com/pbl6-home-renter/docs/issues/102) | Danh sÃ¡ch, táº¡o há»£p Ä‘á»“ng nhÃ¡p, Ã¡p máº«u vÃ  kÃ­ch hoáº¡t há»£p Ä‘á»“ng (Web) | ThaiBao11125 | 3 points | ðŸŸ¡ Open | P6-01b, P6-01c, P6-01d, P6-03c |
| [P6-06b](P6-06b-fe-meter-reading-entry.md) Â· [#103](https://github.com/pbl6-home-renter/docs/issues/103) | Nháº­p chá»‰ sá»‘ Ä‘iá»‡n nÆ°á»›c theo tÃ²a vÃ  ká»³, cÃ³ OCR gá»£i Ã½ (Web) | ThaiBao11125 | 3 points | ðŸŸ¡ Open | P6-02e, P6-02f, P6-02h, P6-03c |
| [P6-06c](P6-06c-fe-invoice-screens.md) Â· [#104](https://github.com/pbl6-home-renter/docs/issues/104) | Sinh, xem, sá»­a phÃ­ khÃ¡c, phÃ¡t hÃ nh vÃ  há»§y hÃ³a Ä‘Æ¡n (Web) | ThaiBao11125 | 3 points | ðŸŸ¡ Open | P6-02g1, P6-06b, P6-06a, P6-01e3 |
| [P6-06d](P6-06d-fe-contract-members-checkout.md) Â· [#105](https://github.com/pbl6-home-renter/docs/issues/105) | ThÃ nh viÃªn há»£p Ä‘á»“ng vÃ  tráº£ phÃ²ng (Web) | ThaiBao11125 | 3 points | ðŸŸ¡ Open | P6-06a, P6-01e1, P6-01e3, P6-03c |
| [P6-07](P6-07-demo-seed-and-staging.md) Â· [#87](https://github.com/pbl6-home-renter/docs/issues/87) | Seed dá»¯ liá»‡u demo, chá»‘t staging, ká»‹ch báº£n demo | baoduong17 | 3 points | ðŸŸ¡ Open | P6-01e1, P6-02g1 |

## Stretch â€” outside Phase 6 MVP

| ID / GitHub | Task | Assignee | Estimate | Status | Dependencies |
|---|---|---|---|---|---|
| [P6-05](P6-05-payment-cash-mock.md) Â· [#85](https://github.com/pbl6-home-renter/docs/issues/85) | Ghi nháº­n thanh toÃ¡n tiá»n máº·t / mock cho hÃ³a Ä‘Æ¡n | baoduong17 | ~8 points | âª Deferred | P6-02 |

## Dependency order

- Contract: `P6-01a â†’ P6-01b â†’ (P6-01c âˆ¥ P6-01d) â†’ P6-01e1 â†’ (P6-01e2 âˆ¥ P6-01e3)`. Checkout also requires P6-02g1.
- Billing It5: `P6-02a â†’ P6-02b â†’ P6-02c â†’ P6-02d`; readings e/f follow the aligned contract and Room API.
- Invoice It6: `P6-02g1 â†’ P6-02h â†’ P6-02g2 â†’ P6-02g3 â†’ P6-02g4`. Generation also requires P6-01e1; tenant views require P6-01e2.
- Web: `P6-06a â†’ P6-06d`; meter entry b and contract a can proceed independently; invoice c follows b and the active-contract update in e3.
- Demo P6-07 follows the core integrations. Payment is not a demo dependency.

## Tracking convention

Keep task documents, this table and GitHub issues consistent. Implementation PRs use `Closes pbl6-home-renter/docs#<number>`. A documentation PR references implementation issues without closing them. Community Service remains a design proposal; implementation issues require design gates Aâ€“C to be approved first.

