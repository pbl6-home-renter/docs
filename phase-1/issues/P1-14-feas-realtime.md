# P1-14 — Realtime (WebSocket) Feasibility for Ticket-Thread

- **Assignee:** BE
- **Participants:** PM (scope Property Chat), Mobile (Android socket client), FE (web socket client)
- **Priority:** High
- **Status:** 🟡 Open — deliverable drafted → chờ member điền effort + PM trình teacher duyệt chi tiết, rồi close
- **Depends on:** teacher feedback 27/08 (wants socket for message flow)
- **Blocks:** business-rules.md §6 (done), feature-list 2.7/6.6 scope (done)
- **Decision ref:** D24′ (Property Chat — final, chờ teacher duyệt chi tiết)

## Goal

Analyze the **effort and feasibility** of implementing realtime (WebSocket) for the object-attached comment/message thread (issue reports, invoices), per the teacher's request, and recommend whether to adopt a realtime **Property Chat** over the former no-socket approach.

## Context

Approach trước P1-14 (đã thay bằng D24′): issue/thread qua FCM push + pull-to-refresh, **no socket, no presence, no read receipt** — justified by WebSocket not documenting cleanly in Swagger/Apidog (course requirement), Android background-kill risk during live demo, and ~10–16 person-days effort for the least-specific need. Teacher (27/08) wants a realtime socket to reduce app re-entry and increase lifecycle. Need a concrete verdict + plan.

## Tasks

### T1 — Option analysis
- [ ] Option A: **WebSocket for ticket-thread only** (no full messenger) — realtime comments on issue/invoice threads.
- [ ] Option B: **Full realtime chat** (Zalo-like) — out of original scope, large.
- [ ] Option C: **Keep FCM push + polling/pull-to-refresh** (no socket) — explain to teacher.

### T2 — Effort & risk
- [ ] Estimate person-days for Option A (gateway, auth on socket, room/sub-channel per thread, reconnect, mobile background handling).
- [ ] Note Swagger/Apidog limitation: how to document WS (asyncapi? separate doc?) so course requirement is still met.
- [ ] Demo risk: Android killing socket in background; mitigation (FCM wake + reconnect).
- [ ] Compare against Option C effort.

### T3 — Recommendation
- [ ] Recommend A, B, or C with rationale; if A, provide a minimal implementation plan + API/socket contract draft.

### T4 — Deliverable
- [ ] Write `pm/phase-0/discovery/realtime-feasibility.md`.

## Deliverable

`pm/phase-0/discovery/realtime-feasibility.md` — options so sánh, effort estimate (TBD), risks (inkl. doc + demo), kiến trúc Property Chat (Socket.io + bot/`@issue`/`@mention`), recommendation **Option A′**; PM log D24′ (final).

> Lưu ý: scope tiến hóa từ "ticket-thread" sang **Property Chat Platform** do yêu cầu "hệ sinh thái" của thầy. Cần thầy duyệt chi tiết (conversation/bot/command) + 3 member điền effort trước khi close.

## Definition of Done
- [x] Tất cả options so sánh với con số effort (A′ ~3 tuần, B ~10–16 p-d, C ~3–4 p-d) — **con số A′ đang TBD, cần member xác nhận**
- [x] Documentation approach cho WS dưới yêu cầu môn học (REST→Swagger, WS events→markdown)
- [x] Recommendation rõ ràng (Option A′ Property Chat); PM đã log D24′
- [ ] Teacher duyệt chi tiết scope + effort 3 member xác nhận → close
