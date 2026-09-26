# Decisions Log — Phase 2

> Quyết định phát sinh trong Phase 2 được ghi tại đây.
> Quyết định Phase 0 (D1–D29): `../../phase-0/discovery/decisions.md`
> Quyết định Phase 1 (D30–D39): `../../phase-1/discovery/decisions.md`

## Index

| ID | Date | Decision | Status |
|---|---|---|---|
| D39 | 2026-09-25 | User account lifecycle in v1: no admin create endpoint, lock/unlock merged into `PATCH /users/{userId}`, added admin soft delete | ✅ Accepted |
| D40 | 2026-09-25 | Two-step media upload (presign + complete) and inherited access for `Media` | ✅ Accepted |
| D41 | 2026-09-25 | Flat resource namespace: remove `/admin/*`, `/debts`, nested parent paths, and dedicated export routes; parent identifiers move to body/query | ✅ Accepted |
| D42 | 2026-09-25 | Role permission matrix correction: `tenant_contract` removed, `admin` scope narrowed, business actions kept only where there is a lifecycle precondition or a cross-entity side effect | ✅ Accepted |
| D43 | 2026-09-25 | Business-named bulk actions for invoice issue and reminder, with per-item results and `Idempotency-Key`; narrows the previous blanket no-bulk rule | ✅ Accepted |
| D44 | 2026-09-25 | Soft delete uses the existing `is_deleted` Base Entity flag, with an explicit cascade boundary that never touches financial/legal/audit records | ✅ Accepted |
| D45 | 2026-09-25 | Export is `format` on a collection `GET` only; no `*/export` and no single-document download route | ✅ Accepted |
| D46 | 2026-09-25 | Removed `GET /invoices/{invoiceId}/document` (superseded by collection export) | ✅ Accepted |
| D47 | 2026-09-25 | Bulk meter-reading deferred and out of API v1: no `MeterReadingBatch` route, only per-room `POST /meter-readings` | ⏸ Pending (PM giữ nguyên pending) |
| D48 | 2026-09-25 | Overloaded endpoints split by role and by business action → 108 endpoints in 25 groups; renumbered throughout | ✅ Accepted (số liệu 108/25 đã lỗi thời, xem D49) |
| D49 | 2026-09-26 | Payout account moved onto `LandlordProfile` (implements Phase 1 D39): `VietQrReceiverConfig` + `PUT/GET /vietqr-configs` removed → 106 endpoints in 24 groups | ✅ Accepted |

---

## D39 — User account lifecycle in v1

- **Context:** Bản thiết kế trước có `POST /users` (admin tạo tài khoản), `POST /users/{userId}/lock-user`, `POST /users/{userId}/unlock-user`. Review chốt: tài khoản chỉ được tạo qua đăng ký tự phục vụ (`POST /auth/register`); khóa/mở khóa gộp vào một endpoint duy nhất `PATCH /users/{userId}` dùng field `status` (`active`/`locked`); thêm `DELETE /users/{userId}` cho admin xóa mềm.
- **Decision:**
  - Bỏ `POST /users` hoàn toàn.
  - Gộp lock/unlock vào `PATCH /users/{userId}` với body `{ "status": "locked", "lockReason": "..." }` hoặc `{ "status": "active" }`.
  - Thêm `DELETE /users/{userId}` (admin) — xóa mềm đặt `is_deleted = true`, cascade mềm sang các con vận hành (xem D44).
- **Reason:** Đơn giản hóa API surface, nhất quán với pattern `status` dùng cho Building/Room, loại bỏ endpoint admin tạo tài khoản không phù hợp self-service registration (D29).
- **Not decided / left to migration:** Cần migration cột `is_deleted` (đã có trong Base Entity) và logic cascade mềm cho các bảng con; `deletedAt` không được dùng.
- **Cross-ref:** `api-spec.md` §3 (User endpoints 10–13), `api-conventions.md` §12, §14.

---

## D40 — Two-step media upload and inherited Media access

- **Context:** Bản trước dùng `POST /media` nhận `multipart/form-data`. Review chốt: upload 2 bước, backend không nhận file bytes; quyền đọc/xóa Media kế thừa từ tài nguyên cha.
- **Decision:**
  - Bước 1: `POST /media/presign-upload` — body `ownerType`, `ownerId`, `purpose`, `fileName`, `contentType`, `size`; response `mediaId`, `uploadUrl` (signed URL), `requiredHeaders`.
  - Bước 2: Client `PUT` file lên storage, rồi `POST /media/{mediaId}/complete-upload` để backend chốt bản ghi `Media`.
  - `GET /media/{mediaId}` có cột **Quyền để trống có chủ ý** — server nạp rule của tài nguyên cha qua `ownerType`/`ownerId` thay vì so sánh role. Đây là ngoại lệ hợp lệ duy nhất của cột quyền.
- **Reason:** Tách concerns (backend không lo storage bandwidth), bảo mật (signed URL ngắn hạn), quyền Media tự động đúng theo cha (building approved = public, CCCD = private).
- **Not decided / left to migration:** Cấu hình storage provider (S3-compatible), TTL signed URL, virus scan pipeline — BE quyết định ở implement.
- **Cross-ref:** `api-spec.md` §5 (Media endpoints 16–19), `api-conventions.md` §5, §4.

---

## D41 — Flat resource namespace

- **Context:** Bản trước có `/admin/*`, `/debts`, nested paths như `/buildings/{buildingId}/rooms`, `/contracts/{contractId}/invoices`, và endpoint export riêng.
- **Decision:**
  - Bỏ hẳn namespace `/admin/*` — admin dùng cùng resource paths (`GET /users`, `GET /buildings?filter[status]=pending`).
  - Bỏ `/debts` — công nợ là `GET /invoices?filter[invoiceStatus]=issued&filter[unpaid]=true` (**D39**: `paymentState` tính toán từ Σ `Payment` success, không có `overdue`).
  - Bỏ nested parent paths: `POST /rooms` nhận `buildingId` trong body; `POST /contract-members` nhận `contractId`; `GET /messages?filter[conversationId]=`; `POST /conversations/resolve-conversation` nhận `contractId` hoặc `buildingId`. Tài khoản nhận tiền không còn endpoint riêng: nó nằm trong `GET /me` + `PATCH /me` (**D39**, bỏ `VietQrReceiverConfig`).
  - Bỏ dedicated export endpoints (`*/export`) — export = collection `GET` kèm `?format=xlsx|csv|pdf|json`.
- **Reason:** API phẳng, dễ cache, dễ generate client, nhất quán với OpenAPI tooling. Định danh cha luôn ở body/query.
- **Not decided / left to migration:** Không có.
- **Cross-ref:** `api-spec.md` §1, §6, §7, §12, §15, §16, §18, §21, §22, `api-conventions.md` §6, §11, §14.

---

## D42 — Role permission matrix correction

- **Context:** Ma trận quyền cũ có role `tenant_contract` và `admin` trên nhiều resource (RatePolicy, BillingSetting, Contract, Invoice, IssueReport, Conversation, Message). Review chốt: `tenant_contract` không còn tồn tại đâu; `admin` bị thu hẹp (không quản lý giá/cài đặt hóa đơn của landlord, không đọc conversation/message); business action chỉ giữ khi có lifecycle precondition hoặc cross-entity side effect.
- **Decision:**
  - Xóa `tenant_contract` hoàn toàn khỏi ma trận.
  - `admin` bị bỏ khỏi: RatePolicy, BillingSetting, Contract, Invoice, IssueReport, Conversation, Message.
  - Giữ business action có tên riêng chỉ 2 trường hợp: `activate-contract` (lifecycle precondition: cần file ký hợp lệ) và `complete-checkout` (side effect: sinh hóa đơn quyết toán). Các action khác (`approve/reject building`, `mark-room-ready`) chuyển thành `PATCH` với `status`.
- **Reason:** Quyền đơn giản, ownership-based, tránh role explosion. Admin chỉ làm system-level (user, building approval, audit).
- **Not decided / left to migration:** Không có.
- **Cross-ref:** `api-spec.md` §12, §13, §15, §18, §20, §21, §22; `database-design.md` §4; `api-conventions.md` §4.

---

## D43 — Business-named bulk actions for invoice issue and reminder

- **Context:** Quy ước cũ (§14 `api-conventions.md` trước review) cấm hẳn bulk. Review chốt: cần 2 bulk action thực tế cho hóa đơn, nhưng phải mang tên nghiệp vụ, không generic.
- **Decision:**
  - `POST /invoices/issue-invoice` — nhận `invoiceIds[]`, optional `sendNotification`; trả `succeeded[]`/`failed[]` (mỗi item: `id`, `code`); bắt buộc `Idempotency-Key`.
  - `POST /invoices/send-reminder` — nhận `invoiceIds[]`, `channel`; trả `queued[]`/`failed[]`; bắt buộc `Idempotency-Key`.
  - Pattern: explicit id array, item cap trong OpenAPI, per-item ownership check, per-item result split, counts, **không atomic** (partial success allowed), idempotency required.
  - Cấm bulk cho: signed contract, meter/OCR commit, evidence, property status change, user lock/unlock.
- **Reason:** Cân bằng giữa DX (một request cho nhiều hóa đơn cùng kỳ) và auditability (kết quả từng record, idempotency, không atomic). Thu hẹp quy tắc cấm bulk cũ.
- **Not decided / left to migration:** Số item cap cụ thể (BE quyết định trước P2-06 freeze).
- **Cross-ref:** `api-spec.md` §18 (endpoints 70, 72), `api-conventions.md` §13, §14.

---

## D44 — Soft delete using existing `is_deleted` flag with cascade boundary

- **Context:** Schema Base Entity (`database-design.md` §2.0) đã có `is_deleted` boolean NOT NULL default false. Bản trước nhắc `deletedAt` timestamp. Review chốt: dùng cờ có sẵn, không thêm cột; cascade boundary tường minh.
- **Decision:**
  - `DELETE /users/{userId}` và `DELETE /buildings/{buildingId}` đặt `is_deleted = true`.
  - Cascade mềm **chỉ** sang con trực tiếp mang tính vận hành: `LandlordProfile`, `PushDevice`, `NotificationPreference`, `RoommateProfile`, `FavoriteRoom`, `MatchRequest`, `Room`, `RatePolicy`, `BillingSetting`. **D39:** không có `VietQrReceiverConfig` trong danh sách này vì bảng đã bị loại.
  - **Không bao giờ cascade** sang: `Contract`, `ContractMember`, `Invoice`, `Payment`, `MeterReading`, `IssueReport`, `Message`, `Conversation`, `AuditLog`. Các bảng này giữ nguyên để tra cứu tài chính/pháp lý/audit, chỉ ẩn khỏi list khi cha đã xóa.
  - `FavoriteRoom`, `PushDevice` có thể hard-delete (không giá trị audit).
- **Reason:** Dùng schema hiện có, bảo toàn bằng chứng tài chính/pháp lý, cascade đúng ngữ nghĩa vận hành.
- **Not decided / left to migration:** Logic cascade mềm trong service layer (BE implement); partial unique indexes cần re-check khi `is_deleted` cascade (xem `database-design.md` migration subsection).
- **Cross-ref:** `api-spec.md` §3 (endpoint 13), §6 (endpoint 24), §29.4; `api-conventions.md` §12; `database-design.md` §2.0, migration subsection.

---

## D45 — Export via `format` on collection GET only

- **Context:** Bản trước có endpoint export riêng và route tải tài liệu đơn lẻ. Review chốt: export = collection `GET` + `format`, không endpoint riêng, detail route luôn JSON.
- **Decision:**
  - `format` (`xlsx`/`csv`/`pdf`/`json`) **chỉ khai báo trên collection `GET`**.
  - Resource-detail `GET` (ví dụ `GET /invoices/{invoiceId}`, `GET /audit-logs/{auditLogId}`) **không bao giờ có `format`** — luôn trả JSON.
  - Cấm `*/export` endpoints. Tải một tài liệu đơn lẻ: filter collection (ví dụ `GET /invoices?filter[id]=<uuid>&format=pdf`).
- **Reason:** Giảm API surface, nhất quán filter+pagination+export trên một route, detail route ổn định cho client cache.
- **Not decided / left to migration:** Không có.
- **Cross-ref:** `api-spec.md` §11, §18, §25; `api-conventions.md` §11.

---

## D46 — Removed `GET /invoices/{invoiceId}/document`

- **Context:** Bản trước có endpoint `GET /invoices/{invoiceId}/document` để tải PDF hóa đơn. Review chốt: bỏ route detail có `format` theo quy tắc D45.
- **Decision:** Bỏ endpoint `GET /invoices/{invoiceId}/document`. Client tải PDF của một hóa đơn qua collection `GET /invoices?filter[id]=<uuid>&format=pdf`; `GET /invoices/{invoiceId}` không có `format` và luôn trả JSON.
- **Reason:** Tuân thủ D45, không có route tải tài liệu đơn lẻ riêng.
- **Not decided / left to migration:** Không có.
- **Cross-ref:** `api-spec.md` §18 (endpoint 68 note), `api-conventions.md` §11, D45.

---

## D47 — Bulk meter-reading deferred, out of API v1

- **Context:** Baseline (UI prototype `f96888b`) có `POST /buildings/{buildingId}/meter-reading-batches` cùng 3 màn hình draft đánh dấu `[MỚI]` (bulk-reading entry, bulk-reading flow, bulk-reading summary). Chưa rõ đây là scope đã được duyệt hay ý tưởng chưa chốt.
- **Decision:** **Giữ pending, chưa chốt.** Không thêm vào v1. Khi quyết định này được chốt, hợp đồng có 94 endpoint và chỉ có `POST /meter-readings` nhập từng phòng. Ba citation baseline cũ được giữ ở trạng thái pending, không xoá. *(Số 94 ở đây là số endpoint tại thời điểm chốt; hợp đồng sau đó đã lên 108 endpoint theo D48. Quyết định "không đưa bulk meter-reading vào v1" không thay đổi.)*
- **Reason:** `requirement.md` (SoT của scope) không nhắc tới bulk meter-reading, và `api-conventions.md` §14 cấm bulk cho chốt chỉ số — nhập chỉ số hàng loạt là thao tác ghi dữ liệu đo có hậu quả tính tiền, cần luồng review riêng. Ba màn hình chỉ tồn tại ở bản prototype, chưa có feature tương ứng trong feature map.
- **Not decided / left to migration:** Có. Cần PM chốt LL-18b/c/d ở session planning tiếp theo. Nếu duyệt, phải bổ sung: rule bulk trong `api-conventions.md` §14, bảng `MeterReadingBatch` + migration, và 3 endpoint block mới (tạo batch, phát hành batch, xác nhận batch) — 94 → 97. Nếu loại, xoá 3 ghi chú pending ở `api-spec.md` §29.14, §30, `P2-06-api-spec.md`.
- **Cross-ref:** `api-spec.md` §29.14, §30; `P2-06-api-spec.md` (Open dependencies); `api-conventions.md` §14; `Rentify_UI_Screen_Outline_v0.1.md` LL-18b/c/d.

## D48 — Overloaded endpoints split by role and by business action

- **Context:** The 94-endpoint contract collapsed several distinct use cases into single routes. `GET /buildings` and `GET /rooms` served the public marketplace, the landlord's own inventory and the admin review queue behind one `filter[status]`. `PATCH /users/{userId}`, `PATCH /buildings/{buildingId}`, `PATCH /rooms/{roomId}` and `PATCH /issues/{issueId}` each mixed ordinary field edits with a lifecycle transition carried in `status`. Baseline commit `f96888b` had already modelled these as separate routes (`GET /admin/buildings`, `approve-building`, `reject-building`, `mark-room-ready`, `lock-user`, `unlock-user`); the 94-endpoint pass merged them back.
- **Decision:** Split by **role** and by **business action**. Contract becomes **108 endpoints in 25 groups**.
  - *Role split on collections:* `GET /buildings` stays public marketplace; landlord gets `GET /me/buildings` and `GET /me/buildings/{buildingId}`; the review queue is restored to `GET /admin/buildings`. Same pattern for `GET /me/rooms`, `GET /me/contracts`, `GET /me/invoices`, `GET /me/payments`, `GET /me/issues`.
  - *Action split on mutations:* `status` is removed from the body of `PATCH /users/{userId}`, `PATCH /buildings/{buildingId}`, `PATCH /rooms/{roomId}` and `PATCH /issues/{issueId}`. Each lifecycle transition becomes its own `POST .../{business-action}`: `lock`, `unlock`, `approve`, `reject`, `mark-ready`, `cancel`.
- **Reason:** One route with a `status` field forces the server to decide, per body content, whether the caller is editing or transitioning — so authorization cannot be expressed in the OpenAPI operation and every client re-implements the same guess. Splitting by role also makes the public marketplace genuinely stateless: it needs no token at all, and landlord/admin data never leaks into an unauthenticated response. The baseline already drew these lines, so restoring them reduces rather than adds contract risk.
- **Naming rules applied:** action segments are verb phrases (`approve`, `reject`, `mark-ready`, `lock`, `unlock`, `cancel`), never bare verbs. The `/me` prefix means *a resource I own*, and is distinct from the self-service `GET /me` of the auth service. Bulk metering stays a separate pending decision (D47) and is not affected by this split.
- **Consequence:** `api-spec.md` §1 scope line, all 25 domain tables, all 108 endpoint blocks, every `API N` cross-reference and the whole §30 traceability table were renumbered. §30's *Mã cũ* column (baseline routes) is deliberately **not** renumbered — that column answers "which route of `f96888b`?", which is a different question from "which endpoint of the current contract?".
- **Cross-ref (số mục theo hợp đồng trước D49):** `api-spec.md` §1, §28, §30; `api-conventions.md` §5, §14; `P2-06-api-spec.md`. Sau D49 các mục này thành §1, §27, §29.
- **Superseded in part by D49:** con số 108/25 ở trên đã lỗi thời.

## D49 - Payout account moved onto the landlord profile (implements Phase 1 D39)

- **Date:** 2026-09-26
- **Status:** Accepted
- **Context:** Phase 1 `D39` (2026-09-26) settled the payment-receiving side of the model: there is no `VietQrReceiverConfig` table. Bank code, account number and account name live as three columns on `LandlordProfile`, configured once by the landlord, and are not building-level. This contract still carried the earlier Phase 2 shape: a `VietQrReceiverConfig` domain group with `PUT /vietqr-configs` and `GET /vietqr-configs`, a `vietQrConfigured` flag on the landlord building DTO, and `VietQrReceiverConfig` in the soft-delete cascade list. Those four things now contradict the schema, and the baseline commit `f96888b` has `PUT`/`GET /buildings/{buildingId}/vietqr-config`, so the mismatch would have surfaced as a migration surprise during handoff.
- **Decision:** Remove the building-level QR receiver surface and serve the payout account from the self-service profile.
  - Delete the `VietQrReceiverConfig` domain group and both `PUT`/`GET /vietqr-configs` endpoints (contract IDs 32-33).
  - `GET /me` returns `payoutAccount` (`bankCode`, masked `accountNumber`, `accountName`) when `role = landlord`, and `null` for every other role. `PATCH /me` accepts it, all three fields together, for landlords only.
  - Drop `vietQrConfigured` from `GET /me/buildings` and `GET /me/buildings/{buildingId}`: QR readiness is no longer a property of a building.
  - Drop `VietQrReceiverConfig` from the soft-delete cascade boundary in both `api-conventions.md` and `api-spec.md` §28.4. Switching banks now moves every building of that landlord at once.
  - `PATCH /me` rejects a payout change with `409 PAYOUT_ACCOUNT_IN_USE` while the landlord still has an `invoice_status = pending` invoice, because a QR already handed to a tenant would point at the old account. `issued` invoices keep their `code`, so reconciliation still resolves.
- **Reason:** One account per landlord is the actual business rule, and it makes the QR payload derive from a single source instead of a per-building table that two buildings of the same landlord could disagree about. Folding the three fields into `GET /me`/`PATCH /me` also means the landlord configures payment details in the same screen they already edit their name and phone, and it removes the last owner-scoped child of `Building` that only existed to hold payment data. Keeping the change on the existing profile endpoint is cheaper than adding a dedicated resource for three fields.
- **Consequence:** Contract shrinks to **106 endpoints in 24 groups**. IDs 34-108 were renumbered down by one to 33-107, so 32 is now unused. Domain sections `## 7`-`## 29` and the `API N` cross-references shifted with them; the `§30` *Mã cũ* column is left alone for the same reason as in D48. Baseline routes 19 and 20 move to the *removed* set, so the reconciliation count becomes 7 removed / 102 kept. `LandlordProfile` needs no new columns, but the migration must **drop** `VietQrReceiverConfig` if `f96888b` already created it — dropping endpoints alone would leave an orphan table.
- **Cross-ref:** `phase-1/discovery/database-design.md` §2.9 and the struck-through row in the ERD exclusion list; `api-spec.md` §1, §3, §6, §27.2, §28.2, §29; `api-conventions.md` cascade boundary; `Rentify_UI_Screen_Outline_v0.1.md` row 49; `P2-06-api-spec.md`; `P2-04-erd.md`.