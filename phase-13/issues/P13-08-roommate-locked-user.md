# P13-08 — BE: Ghép bạn với tài khoản bị khóa

**Trạng thái:** 🔵 In progress
**Người phụ trách (đề xuất):** BE Tenancy (PM giao)
**Người review:** `leminhkhai345`
**Ước lượng:** 1 point
**Phụ thuộc:** —
**Repo / branch:** `Tenancy-Service`, `api-doc`, `docs` · `feature/p13-08-roommate-locked-user`

> **Đọc trước khi code:** [`decisions.md`](../decisions.md) (P13-D106), P10-D88/P10-D89 (ghép bạn).

## Mục tiêu

Tenant bị khóa không xuất hiện trong tìm kiếm bạn ở ghép và không bị kéo vào giao dịch ghép đôi mới. Lời mời cũ **được giữ nguyên** để mở khóa xong là dùng tiếp, không cần khôi phục.

## Quy tắc

| Tình huống | Hành vi |
|---|---|
| Tìm kiếm hồ sơ (`roommate-profile-search`) | Loại hồ sơ của tenant đang bị khóa. **Không** đổi lựa chọn `isVisible` của họ |
| Xem hồ sơ theo id của người bị khóa | `404` |
| Gửi lời mời tới người đang bị khóa (`match-request-create`) | Chặn, `409 MATCH_REQUEST_COUNTERPART_UNAVAILABLE` |
| Chấp nhận / từ chối lời mời mà bên kia đang bị khóa (`match-request-transition`) | Chặn, `409 MATCH_REQUEST_COUNTERPART_UNAVAILABLE` |
| Người bị khóa tự thao tác | Đã bị chặn bởi `ActiveUserGuard` (`403 ACCOUNT_LOCKED`) |
| Lời mời đang chờ lúc khóa | Giữ nguyên trạng thái |
| Mở khóa | Hồ sơ tự hiện lại; lời mời dùng tiếp như bình thường |

## Thiết kế

- Dùng projection `tenant_user_projections` đã có: tenant bị khóa bị xóa khỏi projection khi nhận `user.locked`, thêm lại khi `user.unlocked`. Lọc theo projection này, không thêm bảng mới.

## Acceptance

- [ ] Khóa tenant A → A không còn trong kết quả tìm kiếm của người khác; xem hồ sơ A → `404`.
- [ ] B gửi lời mời cho A → `409`; B chấp nhận lời mời A gửi trước đó → `409`.
- [ ] Mở khóa A → A hiện lại trong tìm kiếm, B chấp nhận được lời mời cũ.

## Definition of Done

- [x] Unit test cho query search và hai command; `npm test`, `npm run build`, `npm run lint` pass (local; xem giới hạn bên dưới).
- [x] api-doc: thêm mã lỗi `409` và ghi chú quy tắc; bundle (local).
- [ ] PR vào `main`, ≥ 1 reviewer.

## Implementation / verification — 2026-11-28

- Local changes are on `feature/p13-08-roommate-locked-user` in `Tenancy-Service`, `api-doc` and `docs`. The user has authorized staging, commits and pushing these task branches. PR review and rollout acceptance remain open.
- Search/detail require an existing, non-deleted `tenant_user_projections` row in the shared discoverability SQL before pagination/count. The lifecycle consumer remains unchanged; reads never populate the projection or change `isVisible`.
- New requests retain Identity validation and require the target projection in the current transaction. A locked Identity tenant or an otherwise valid tenant without projection returns `409 MATCH_REQUEST_COUNTERPART_UNAVAILABLE`; other missing/inactive target accounts and missing/hidden/full profiles keep `404 ROOMMATE_PROFILE_NOT_FOUND`. Idempotent replay and duplicate-pair rules are unchanged.
- Accept/reject verify actor authorization and terminal/replay rules before reading the counterpart projection, then transition only if available. A blocked operation leaves the request pending with no save/outbox. Unlock allows retrying that request; visibility/capacity are not rechecked. Withdraw is unchanged.
- List behavior/schema is unchanged: missing active participant summaries can still return `404 MATCH_REQUEST_PARTICIPANT_UNAVAILABLE`. Data is preserved and listing works again once active summaries are available after unlock.
- Regression fixtures cover SQL pagination/count, detail 404, unchanged visibility, blocked create rollback, blocked accept/reject with unchanged pending rows/outbox, projection restore, hidden/full-room transitions, authorization, self-matching, duplicates, idempotency, terminal replay and withdraw. Existing tenant lock/unlock/contract auto-linking tests remain in the PostgreSQL suite.

### Local checks

- `npm test -- --runInBand`: **234 passed**, 10 previously skipped; 46 suites passed, one previously skipped. Initial sandbox run failed on the existing `contract-route.spec.ts` child-process spawn (`EPERM`); rerun with process permission passed without modifying/skipping tests.
- `npm run test:postgres`: **17 passed / 5 suites**, including the existing tenant lock/unlock and contract auto-linking regressions plus a complete matching acceptance test through actual lock/unlock consumers (with duplicate delivery). `npm run build`, `npm run lint` and changed-file Prettier checks passed.
- Compiled-controller smoke checks: all 9 matching routes reject locked tenant actors with `403 ACCOUNT_LOCKED`; the actual exception filter maps unavailable counterpart/profile exceptions to HTTP 409/404. Controller Swagger now includes the counterpart 409 for create/accept/reject while withdraw keeps its existing errors.
- API `npm run lint`: passed with 18 warnings; `npm run bundle`: passed, generated `reference/rentify.json` included. Bot-managed changelog reports are untouched.
- `git diff --check`: passed in all three repos. Architecture dependency checks retain the same **16 baseline findings** (six application imports from infrastructure in building/rate-policy/room, ten domain imports from application pagination in building/contract/room); no new violations. Unrelated modules were not refactored.

### Projection data / rollout condition

- Migration `1794395332044-CreateTenantUserProjectionsTable` creates the table without seeding historical accounts. The existing Identity lifecycle consumer populates active tenants from received events, deletes tenants on lock, and restores/reconciles on unlock when the event includes the tenant snapshot. P10-D91 excludes new bootstrap/replay/repair tools.
- Read-only audit of the database configured by the local Tenancy `.env`, using `BEGIN READ ONLY`, aggregate `SELECT`, then `ROLLBACK`: **6** non-deleted profile owners, **3** with a non-deleted projection row, **3** without one. No operational data/schema was written; no migrations or synchronization ran against this database.
- Absence alone does **not** prove a lock or a historical-data defect. `IDENTITY_SERVICE_URL` is not configured in this environment, so the three absent owners could not be classified against current Identity status. Historical active-tenant coverage is **not verified**; this is a rollout gate. Before rollout, classify these owners and verify every eligible active owner is projected and lifecycle events are drained. Any confirmed historical gap needs an approved resolution outside this task; no fallback or repair was added.
- Changes take effect after lifecycle processing; no claim of immediate cross-service updates or token-TTL changes. Local PGlite checks do not establish independent-connection race behavior, live RabbitMQ delivery or deployed acceptance.
