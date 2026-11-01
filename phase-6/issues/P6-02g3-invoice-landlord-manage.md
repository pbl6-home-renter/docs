# P6-02g3 — Invoice: landlord xem, sửa phí khác, phát hành hàng loạt, hủy

**Epic:** [P6-02](P6-02-tenancy-billing-vertical-slice.md) · cha: [P6-02g](P6-02g-invoice-outline.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** huynhtiennhat0403  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 3 points · 8–12 giờ  
**Phụ thuộc:** P6-02g2 (có hóa đơn `pending` để thao tác), P6-09 (contract Invoice sau D64)  
**Repo / branch:** `Tenancy-Service` · `feature/p6-02g3-invoice-landlord`  
**Iteration:** It6 (09/11–15/11)  
**Issue:** `docs#100`

> **Đọc trước khi code:** `AGENTS.md` và skill trong `.agents/skills/` của repo (backend: `be-feature-workflow`). Issue **không** quy định cách đặt file, đặt tên hay style — nếu issue nói khác skill thì làm theo skill. Nguồn mâu thuẫn xử lý theo [`P6-D75`](../decisions.md#d75--thứ-tự-ưu-tiên-nguồn-và-cách-xử-lý-câu-hỏi-mở): `decisions.md` > `api-docs` > skill > issue.

## Mục tiêu

Landlord xem danh sách/chi tiết hóa đơn theo tòa + kỳ, thêm phí khác/giảm trừ và ghi chú cho bản `pending`, phát hành nhiều hóa đơn trong một request (kết quả từng hóa đơn, chống gửi trùng bằng `Idempotency-Key`), và hủy (`void`) hóa đơn sai.

## Quyết định áp dụng

- `P6-D64` — `pending` sửa được `other_fees`, `note`; `issued` bất biến (không có "sửa sau phát hành" của LL-21b); sai thì `void` rồi generate lại; phát hành hàng loạt theo `P2-D43`; gỡ `overdue-debts`, `send-reminder`.
- `P2-D43` — `POST /invoices/issue-invoice`: mảng id tường minh, có giới hạn số item, kiểm quyền **từng item**, kết quả tách `succeeded[]`/`failed[]`, **không atomic**, bắt buộc `Idempotency-Key`.
- `P1-D33⑥` / EC17 — `other_fees` âm được; tổng âm → `422 TOTAL_NEGATIVE`.
- `P1-D37` — void giữ bản ghi, không xóa.
- `P6-D72` — `cancel-invoice` bắt buộc `reason` 1–500 ký tự, lưu vào `void_reason`; `InvoiceIssueRequestDto` **không có** `sendNotification`; response **không có** `vietQrContent` (web không hiển thị QR); tổng = round half-up của Σ dòng.
- `P6-D61` — không có trạng thái "đã thu": bỏ `paidAmount`, `remainingAmount`, `dueDate`, `INVOICE_ALREADY_PAID`.

## Contract (sau P6-09)

| Endpoint | operationId | Success | Lỗi riêng |
|---|---|---|---|
| `GET /invoices` | `getInvoices` | `200 INVOICES_FETCHED` + `pagination` | `422 VALIDATION_FAILED` |
| `GET /invoices/{invoiceId}` | `getInvoicesInvoiceid` | `200 INVOICE_FETCHED` | `404 INVOICE_NOT_FOUND`, `403` |
| `PATCH /invoices/{invoiceId}` | `patchInvoicesInvoiceid` | `200 INVOICE_UPDATED` | `409 INVOICE_ALREADY_ISSUED`, `422 TOTAL_NEGATIVE`, `VALIDATION_FAILED` |
| `POST /invoices/issue-invoice` | `postInvoicesIssueInvoice` | `200 INVOICES_ISSUE_REQUESTED` | `409 IDEMPOTENCY_KEY_REUSED`, `422 INVOICE_IDS_REQUIRED`, `INVOICE_IDS_TOO_LARGE`; per-item `INVOICE_NOT_PENDING`, `INVOICE_NOT_FOUND` |
| `POST /invoices/{invoiceId}/cancel-invoice` | `postInvoicesInvoiceidCancelInvoice` | `200 INVOICE_CANCELLED` | `409 INVOICE_ALREADY_VOIDED`, `422 VALIDATION_FAILED` (thiếu/sai `reason`), `404`, `403` |

- File: `api-docs/src/paths/invoices/invoices.yaml`, `invoices-invoiceId.yaml`, `invoices-issue-invoice.yaml`, `invoices-invoiceId-cancel-invoice.yaml`; request `api-docs/src/requests/invoices/invoice-update-request-dto.yaml`, `invoices-issue-request-dto.yaml`, `invoice-cancel-request-dto.yaml`.
- P6-09 sửa so với hiện tại: PATCH `TOTAL_AMOUNT_INVALID` → `TOTAL_NEGATIVE`; `otherFees[].amount` integer → string; cancel bỏ `INVOICE_ALREADY_PAID`/`CANNOT_DELETE`, thêm `INVOICE_ALREADY_VOIDED`; ví dụ `succeeded[].invoiceStatus` phải là `issued`; `maxItems` cho `invoiceIds` (đề xuất **100**, `P2-D43` để BE chọn); list bỏ `format` xlsx/csv/pdf; bỏ `sendNotification` khỏi request issue và `vietQrContent` khỏi response (`P6-D72`).
- Role: `landlord` cho cả 5 endpoint (tenant xem ở P6-02g4). Hóa đơn của landlord khác → `403`.

### Mapping field

| Request / Response field | Domain prop | Cột DB | Ghi chú / validation |
|---|---|---|---|
| `filter[buildingId]`, `filter[roomId]`, `filter[contractId]`, `filter[period]`, `filter[status]` | — | `building_id`, `room_id`, `contract_id`, `period`, `status` | luôn thêm `landlord_id = user.id`, `is_deleted=false`; sort `period`, `createdAt` (default `period desc`) |
| list item `roomName`, `tenantName` | — | join `rooms.name`, `contracts.tenant_name` | chỉ đọc |
| `otherFees[] { name, amount }` | `otherFees` | `other_fees jsonb` | name 1–100 ký tự; amount `^-?(0\|[1-9]\d*)(\.\d{1,2})?$`; tối đa 20 dòng; gửi mảng = **thay toàn bộ** |
| `note` | `note` | `note` | ≤ 500 ký tự, `null` để xóa |
| `invoiceIds[]` | — | `invoices.id` | 1–100, unique |
| `reason` | `voidReason` | `void_reason text` NULL | bắt buộc, 1–500 ký tự (`P6-D72`); response detail trả `voidReason` |
| header `Idempotency-Key` | — | `idempotency_keys.key` | UUID, bắt buộc |

### Bảng `idempotency_keys` (mới, trong `tenancy_db`)

`src/shared` **không** có cơ chế idempotency (đã kiểm). Tạo bảng riêng trong module invoice theo mẫu `payment_db.idempotency_keys` của `pm/phase-3/discovery/database-per-service.md` §4.3:

| Cột | Kiểu | Ghi chú |
|---|---|---|
| `id` | uuid PK | |
| `key` | uuid NOT NULL | từ header |
| `user_id` | uuid NOT NULL | landlord gọi |
| `operation` | varchar(64) NOT NULL | `postInvoicesIssueInvoice` |
| `request_hash` | varchar(64) NOT NULL | sha256 của body đã chuẩn hóa (sort `invoiceIds`) |
| `response_body` | jsonb NOT NULL | `data` đã trả |
| `created_at` / `expires_at` | timestamptz | `expires_at = created_at + 24h` (contract: "lưu ít nhất 24 giờ") |

UNIQUE `(user_id, operation, key)`. Cùng key + cùng hash → trả lại `response_body` (không phát hành lại); cùng key + hash khác → `409 IDEMPOTENCY_KEY_REUSED`; bản ghi hết hạn coi như không có. Nếu muốn dùng chung cho service khác → đề xuất đưa vào `boilerplate`, không sửa `src/shared` ở đây.

### Ví dụ số

| Input | Kết quả mong đợi |
|---|---|
| Hóa đơn P101 `pending` 4.875.400 (g1 #1), PATCH `otherFees [{Nệm mới, "250000"}, {Giảm trừ hỗ trợ, "-700000"}]` | `200`, `totalAmount` **"4425400"**, `rentAmount`/`breakdown` không đổi |
| PATCH `otherFees [{Giảm trừ, "-5000000"}]` | `422 TOTAL_NEGATIVE`, DB giữ 4.425.400 |
| PATCH `otherFees []` | `totalAmount` về **"4875400"** |
| Issue `[P101 pending, P102 issued, id lạ]` | `requested 3`, `succeeded 1`, `failed 2` (`INVOICE_NOT_PENDING`, `INVOICE_NOT_FOUND`) |

## Tham chiếu code

- Module mẫu: `Tenancy-Service/src/modules/rate-policy/` (command UoW + outbox, query list với `OffsetPaginationQueryRequestDto`, port `rate-policy-page-query.port.ts`).
- Phân trang: `src/shared/presentation/pagination/offset-pagination.request.dto.ts`, `paginated.response.dto.ts`, `src/shared/infrastructure/database/pagination/offset.paginator.ts`.
- Aggregate + exception `Invoice` từ P6-02g1 (`updateExtras`, `issue`, `void`).
- Unique violation (race trên `idempotency_keys`) → `src/shared/infrastructure/database/postgres-error-code.ts`.

## Các bước triển khai

### Bước 1 — Dữ liệu thử

- **Cách làm:** chạy kịch bản bước 1–3 của P6-02g2 → có ít nhất 2 hóa đơn `pending` của landlord A; tạo thêm 1 tòa + hóa đơn cho landlord B.
- **Kiểm tra bước:** `SELECT id, code, status, landlord_id FROM invoices` có dữ liệu của A và B.

### Bước 2 — `GET /invoices`, `GET /invoices/{id}`

- **Cách làm:** query handler list (filter + sort whitelist + `landlord_id`), detail trả đủ `breakdown`, `otherFees`, `voidedInvoiceId`. Hóa đơn của landlord khác → `403`; không tồn tại → `404 INVOICE_NOT_FOUND`.
- **Kiểm tra bước:** `GET /api/v1/invoices?filter[buildingId]=<A>&filter[period]=2026-10&filter[status]=pending` → `200 INVOICES_FETCHED`, chỉ hóa đơn A; `pageSize=101` → `422`; token B gọi detail hóa đơn A → `403`.

### Bước 3 — `PATCH /invoices/{id}`

- **Cách làm:** UoW: `findByIdForUpdate` → check landlord → `invoice.updateExtras(otherFees, note)` (domain tính lại tổng, chặn âm) → save + outbox `invoice.updated`.
- **Kiểm tra bước:** 3 dòng PATCH đầu ở bảng Ví dụ số. `UPDATE invoices SET status='issued', issued_at=now() WHERE …` rồi PATCH → `409 INVOICE_ALREADY_ISSUED`.

### Bước 4 — Migration + adapter `idempotency_keys`

- **Cách làm:** typeorm entity + repository như bảng trên; `npm run migration:generate -- name=CreateIdempotencyKeysTable`.
- **Kiểm tra bước:** `migration:run`/`revert`/`run` pass; insert tay 2 row cùng `(user_id, operation, key)` → lỗi unique.

### Bước 5 — `POST /invoices/issue-invoice`

- **Cách làm:** handler: kiểm key (hit cùng hash → trả bản lưu; khác hash → `409`). Lặp từng id, **mỗi id một UoW**: không có → `failed {invoiceId, code: INVOICE_NOT_FOUND}`; landlord khác → `failed … FORBIDDEN`; `invoice.issue(now)` lỗi → `failed … INVOICE_NOT_PENDING`; thành công → `succeeded {id, code, status: "issued", issuedAt}` + outbox `invoice.issued`. Cuối cùng ghi `idempotency_keys` (bắt unique → đọc lại bản đã lưu).
- **Kiểm tra bước:**
  - `POST /api/v1/invoices/issue-invoice`, header `Idempotency-Key: 6f1c…`, body `{ "invoiceIds": [P101, P102, "<uuid lạ>"] }` → `200 INVOICES_ISSUE_REQUESTED`, kết quả như bảng Ví dụ số.
  - Gửi lại y nguyên → cùng response; `SELECT issued_at FROM invoices WHERE id=P101` không đổi.
  - Cùng key, body chỉ `[P102]` → `409 IDEMPOTENCY_KEY_REUSED`. Thiếu header → `422 VALIDATION_FAILED`; `invoiceIds: []` → `422 INVOICE_IDS_REQUIRED`; 101 id → `422 INVOICE_IDS_TOO_LARGE`.

### Bước 6 — `POST /invoices/{id}/cancel-invoice`

- **Cách làm:** UoW: lock → check landlord → `invoice.void(reason)` → save + outbox `invoice.voided`.
- **Kiểm tra bước:** `POST /api/v1/invoices/{P101}/cancel-invoice` `{ "reason": "Sai chỉ số điện" }` → `200 INVOICE_CANCELLED`, `status: void`, `SELECT void_reason` = `Sai chỉ số điện`; body `{}` hoặc `reason` 501 ký tự → `422 VALIDATION_FAILED`; lần 2 → `409 INVOICE_ALREADY_VOIDED`. Sau đó `POST /invoices/generate` (g2) → bản mới có `voidedInvoiceId` = P101.

### Bước 7 — Controller, Swagger

- **Cách làm:** route `issue-invoice` khai báo **trước** `:invoiceId`; tất cả `@Roles(UserRole.LANDLORD)`.
- **Kiểm tra bước:** Swagger hiện đủ 5 operation; token tenant gọi `PATCH` → `403`; không token → `401`.

## Ngoài phạm vi

- `GET /invoices/overdue-debts`, `POST /invoices/send-reminder`, `POST /invoices` settlement (`P6-D64`); export xlsx/csv/pdf.
- Gửi thông báo thật khi phát hành (chưa có community/notification service) — chỉ có event.
- Payment, QR/`vietQrContent`, `paidAmount`/`remainingAmount` (`P6-D61`, `P6-D72`).

## Blocker

- Không có. (`void_reason` đã chốt ở `P6-D72`, cột tạo ở P6-02g1.)

## Cập nhật `api-docs` (bắt buộc trước khi đóng issue)

- [ ] Sequence diagram cho PATCH, issue-invoice (vòng lặp per-item + idempotency), cancel-invoice.
- [ ] `x-apidog-status: released` cho 5 endpoint; `npm run bundle`.

## Acceptance (Apidog)

- [ ] List/detail → `200`; filter đúng; landlord khác → `403`; id lạ → `404 INVOICE_NOT_FOUND`.
- [ ] PATCH pending → `200 INVOICE_UPDATED` với tổng đúng bảng Ví dụ số; tổng âm → `422 TOTAL_NEGATIVE`; đã phát hành → `409 INVOICE_ALREADY_ISSUED`.
- [ ] Issue: partial success, replay cùng key không phát hành lại, key dùng lại với body khác → `409 IDEMPOTENCY_KEY_REUSED`.
- [ ] Cancel thiếu `reason` → `422`; cancel hợp lệ → `void`, `voidReason` lưu và trả về; hủy lần 2 → `409 INVOICE_ALREADY_VOIDED`; generate lại có `voidedInvoiceId`.
- [ ] Token tenant → `403`; không token → `401`.

## Definition of Done

- [ ] Mọi bước qua phần Kiểm tra bước; mọi ô Acceptance được **tick bởi người làm**, kèm export Apidog trong PR.
- [ ] `npm run build` + `npm run lint` pass; không có file test, không sửa `src/shared`.
- [ ] Migration sinh bằng `migration:generate`, `migration:run` + `migration:revert` pass từ DB trống.
- [ ] PR vào `main` ghi `Closes pbl6-home-renter/docs#<số issue>`, baoduong17 approve.
