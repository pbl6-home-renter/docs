# P0-02 — Competitive UX Review (Web + Mobile)

- **Assignee:** FE (web side), Mobile (mobile side)
- **Participants:** — (independent work, results handed to PM)
- **Priority:** High
- **Status:** 🟢 Done
- **Timebox:** Tue 18/08 → Wed 19/08 — must finish by EOD Wed so PM can write use cases Thu
- **Depends on:** — (uses existing `market-analysis.md` seed; does NOT block on P0-01)
- **Blocks:** P0-06 (journeys), Phase 2 design
- **Sprint day:** D1 (Tue 18/08) start, D2 (Wed 19/08) finish

## Goal

By EOD Tue, PM has structure-level journey sketches + UX pros/cons for both web (landlord) and mobile (tenant) sides, ready to feed use cases and design.

## Context

We build `pbl6-web` (React) and `pbl6-mobile` (Kotlin/Android). Before designing screens, we need to know what works and what breaks in existing tools. This is a quick, focused competitive UX audit — register free trials, walk flows, screenshot, annotate, sketch.

**Seed product list** (from existing `market-analysis.md`; FE/Mobile may substitute if a better option is found):
- Web (landlord): Mona House, KiotViet, iNest
- Mobile (tenant): Phòng Trọ 123, NhaTroTot, Chợ Tốt

## Tasks

### FE — Web (landlord side)

**D1 (Tue 18/08):**
- [ ] Pick 3 landlord web products from the seed list above (or substitute).
- [ ] Walk the flow: create/manage room → contract → monthly utility close → invoice → payment tracking → stats.
- [ ] Screenshot key screens; note structure, navigation, what's confusing or slow.

**D2 (Wed 19/08):**
- [ ] Write pros/cons table per product.
- [ ] Sketch 3–4 landlord user-journey drafts (structure-level, not pixel-perfect) for our product.
- [ ] Deliver `discovery/ux-web.md` to PM.

### Mobile — Tenant side

**D1 (Tue 18/08):**
- [ ] Pick 3 tenant apps: 2 room-search (Phòng Trọ 123, NhaTroTot, Chợ Tốt) + 1 with payment flow (any app using VNPay/MoMo).
- [ ] Walk the flow: search on map → filter → view room → contact → pay; also: create issue report, roommate profile.
- [ ] Screenshot key screens; note gestures, filter UX, friction points.

**D2 (Wed 19/08):**
- [ ] Write pros/cons table per product.
- [ ] Sketch 3–4 tenant user-journey drafts (structure-level).
- [x] Deliver `discovery/p0-02/discovery-ux-mobile.md` to PM.

## Deliverables

- `pm/phase-0/discovery/p0-02/ux-web.md` — 3 products reviewed + pros/cons + journey sketches. *(actual location)*
- `pm/phase-0/discovery/p0-02/discovery-ux-mobile.md` — 3 products reviewed + pros/cons + journey sketches. *(actual location)*

## Definition of Done

- [ ] 3 products per side reviewed with screenshots.
- [ ] Pros/cons table per product.
- [ ] 3–4 journey sketches per side, handed to PM.
- [ ] Cross-checked against P0-01 personas (journeys match persona behavior).
