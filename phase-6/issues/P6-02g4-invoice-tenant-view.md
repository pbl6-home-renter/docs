# P6-02g4 — Invoice: tenant xem hóa đơn của mình

**Epic:** [P6-02](P6-02-tenancy-billing-vertical-slice.md) · cha: [P6-02g](P6-02g-invoice-outline.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** huynhtiennhat0403  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 2 points · 4–6 giờ  
**Phụ thuộc:** P6-02g3 (có hóa đơn `issued`), P6-01e2 (quy tắc "HĐ của tôi" — `GET /me/contracts`), P6-01e1 (bảng `contract_members`), P6-09 (`GET /me/invoices`)  
**Repo / branch:** `Tenancy-Service` · `feature/p6-02g4-invoice-tenant-view`; `api-gateway` · `feature/p6-02g4-me-invoices-route`  
**Iteration:** It6 (09/11–15/11)  
**Issue:** `docs#101`

> **Đọc trước khi code:** `AGENTS.md` và skill trong `.agents/skills/` của repo (backend: `be-feature-workflow`). Issue **không** quy định cách đặt file, đặt tên hay style — nếu issue nói khác skill thì làm theo skill. Nguồn mâu thuẫn xử lý theo [`P6-D75`](../decisions.md#d75--thứ-tự-ưu-tiên-nguồn-và-cách-xử-lý-câu-hỏi-mở): `decisions.md` > `api-docs` > skill > issue.

## Mục tiêu

Tenant (người đại diện hoặc thành viên đang ở) gọi `GET /me/invoices` thấy các hóa đơn **đã phát hành** của HĐ mình, và mở `GET /invoices/{id}` xem chi tiết từng khoản. Hóa đơn `pending`/`void` và hóa đơn của phòng khác không bao giờ lộ ra.

## Quyết định áp dụng

- `P6-D64` — tenant xem qua `GET /me/invoices` + `GET /invoices/{id}` (`P2-D48`); gỡ `GET /invoices/tenant`; tenant **chỉ thấy `issued`**.
- `P6-D63` — "HĐ của tôi" = user là `contracts.tenant_id` **hoặc** `contract_members.tenant_id` chưa rời. Dùng lại đúng điều kiện P6-01e2 đã cài cho `GET /me/contracts`, không viết điều kiện thứ hai.
- `P2-D48` — `/me/*` = tài nguyên của tôi; tách theo role.
- `P6-D61` — không có số "đã thu/còn thiếu".
- `P6-D71` — member "chưa rời" = `left_at IS NULL` hoặc `left_at > hôm nay` (cùng định nghĩa `status=active` của member).
- `P6-D72` — response không có `vietQrContent`; không hiển thị QR.
- `P6-D74` — web không liên kết tài khoản tenant; `tenant_id` chỉ có từ seed demo → view này phục vụ mobile + dữ liệu seed.

## Contract (sau P6-09)

| Endpoint | operationId | Success | Lỗi riêng |
|---|---|---|---|
| `GET /me/invoices` | `getMeInvoices` | `200 INVOICES_MY_FETCHED` + `pagination` | `422 VALIDATION_FAILED` |
| `GET /invoices/{invoiceId}` (role tenant) | `getInvoicesInvoiceid` | `200 INVOICE_FETCHED` | `404 INVOICE_NOT_FOUND` |

- File: `api-docs/src/paths/invoices/me-invoices.yaml` (P6-09 tạo, cùng kiểu `paths/contracts/me-contracts.yaml`, mã theo mẫu `CONTRACTS_MY_FETCHED`); `api-docs/src/paths/invoices/invoices-invoiceId.yaml`. P6-09 gỡ `invoices-tenant.yaml`.
- Role: `GET /me/invoices` chỉ `tenant`. `GET /invoices/{id}`: `landlord` (P6-02g3) **và** `tenant`.
- Tenant mở hóa đơn không được xem (`pending`, `void`, HĐ khác, đã rời trước) → **`404 INVOICE_NOT_FOUND`** (không `403`, để không lộ hóa đơn tồn tại). P6-09 ghi rõ trong description.
- Gateway: `api-gateway/src/constants/route-paths.constants.ts` **chưa có** `/me/invoices` → request sẽ rơi vào prefix `/me` của Identity. Phải thêm `'/me/invoices'` vào danh sách Tenancy.

### Mapping field

| Request / Response field | Domain prop | Cột DB | Ghi chú / validation |
|---|---|---|---|
| `filter[period]` | — | `invoices.period` | regex `YYYY-MM` |
| `filter[contractId]` | — | `invoices.contract_id` | UUID, phải thuộc tập HĐ của tôi (khác → list rỗng) |
| — | — | `invoices.status = 'issued'` | luôn áp dụng |
| — | — | `contracts.tenant_id = :me` OR `EXISTS contract_members (tenant_id = :me, (left_at IS NULL OR left_at > current_date), is_deleted=false)` | quy tắc của P6-01e2 / `P6-D63` / `P6-D71` |
| list item | — | `id, code, period, totalAmount, status, issuedAt, roomName` | sort `period desc` |
| detail | — | như landlord (`breakdown`, `otherFees`, `rentAmount`, `note`) | bỏ `voidReason`; không có `vietQrContent` |

### Ví dụ số

Không có tính toán mới. Kịch bản dữ liệu:

| Input | Kết quả mong đợi |
|---|---|
| HĐ X: đại diện T1, member T2 (đang ở), T3 (`left_at` 30/09). Hóa đơn X `2026-09` issued, `2026-10` issued, `2026-11` pending | T1 và T2: `GET /me/invoices` → 2 item (`2026-10`, `2026-09`). T3: 0 item (đã rời, theo `P6-D63`) |
| T1 `GET /invoices/{2026-11 pending}` | `404 INVOICE_NOT_FOUND` |
| Landlord void hóa đơn `2026-10` | T1 chỉ còn thấy `2026-09` |
| T4 (HĐ Y khác phòng) `GET /invoices/{X 2026-09}` | `404 INVOICE_NOT_FOUND` |

## Tham chiếu code

- Module mẫu: `Tenancy-Service/src/modules/rate-policy/` (query list + port page query `rate-policy-page-query.port.ts`).
- Quy tắc truy cập tenant: method/điều kiện P6-01e2 thêm cho `GET /me/contracts` trong `src/modules/contract/` — import lại, không copy SQL.
- Controller "của tôi" mẫu: `src/modules/building/presentation/http/controllers/my-building.controller.ts`.
- Query detail landlord + `INVOICE_NOT_FOUND` từ P6-02g3.

## Các bước triển khai

### Bước 1 — Dữ liệu thử

- **Cách làm:** từ dữ liệu P6-02g3: liên kết HĐ X với `tenant_id = T1` bằng SQL/seed (web không có ô chọn tài khoản, `P6-D74`), thêm member T2, T3 (`left_at = 2026-09-30`) qua API P6-01e1 (body có `tenantId` — API vẫn nhận); phát hành 2 hóa đơn, để 1 `pending`. Lấy token T1–T4 từ Identity.
- **Kiểm tra bước:** `SELECT period, status FROM invoices WHERE contract_id = '<X>'` → 2 `issued`, 1 `pending`.

### Bước 2 — Gateway route `/me/invoices`

- **File sửa:** `api-gateway/src/constants/route-paths.constants.ts` — thêm `'/me/invoices'` vào mảng `GatewayService.Tenancy` (PR riêng ở repo `api-gateway`, reviewer baoduong17).
- **Kiểm tra bước:** chạy gateway local, `GET http://localhost:3000/api/v1/me/invoices` có log proxy tới Tenancy (port 3002), không phải Identity.

### Bước 3 — `GET /me/invoices`

- **Cách làm:** query handler + read port: điều kiện "HĐ của tôi" của P6-01e2 + `status='issued'` + filter + phân trang. Controller "của tôi" `@Roles(UserRole.TENANT)`.
- **Kiểm tra bước:** token T1 `GET /api/v1/me/invoices` → `200 INVOICES_MY_FETCHED`, 2 item; token T3 → 0 item; `filter[period]=2026-13` → `422 VALIDATION_FAILED`; token landlord → `403`.

### Bước 4 — `GET /invoices/{id}` cho tenant

- **Cách làm:** mở `@Roles` của route detail cho `TENANT`; trong query handler: role landlord → nhánh P6-02g3; role tenant → hóa đơn phải `issued` **và** HĐ thuộc tập của tôi, ngược lại `404 INVOICE_NOT_FOUND`. Kiểm quyền trong use case, không trong guard.
- **Kiểm tra bước:** 4 dòng bảng Ví dụ số; landlord vẫn xem được hóa đơn `pending` của mình (không hồi quy P6-02g3).

### Bước 5 — Swagger + api-docs

- **Kiểm tra bước:** Swagger hiện `getMeInvoices`; `npm run build` + `npm run lint` pass ở cả `Tenancy-Service` và `api-gateway`.

## Ngoài phạm vi

- Thanh toán, QR, trạng thái thu (`P6-D61`, `P6-D72`). Thông báo khi phát hành.
- Màn hình mobile/FE (P6-06 và task mobile).
- Member chưa liên kết tài khoản (`tenant_id` NULL) — không đăng nhập được nên không có view.

## Blocker

- Không có, nếu P6-01e2 merge trước. Chưa merge → không tự viết điều kiện truy cập riêng; chờ.

## Cập nhật `api-docs` (bắt buộc trước khi đóng issue)

- [ ] Sequence diagram `getMeInvoices`, nhánh tenant của `getInvoicesInvoiceid`.
- [ ] `x-apidog-status: released`; `npm run bundle`.

## Acceptance (Apidog)

- [ ] Tenant đại diện và member đang ở thấy đúng hóa đơn `issued` → `200 INVOICES_MY_FETCHED`.
- [ ] Member đã rời, tenant HĐ khác: list rỗng; detail → `404 INVOICE_NOT_FOUND`.
- [ ] Hóa đơn `pending`/`void` không xuất hiện với tenant.
- [ ] Landlord gọi `/me/invoices` → `403`; không token → `401`.
- [ ] Qua gateway `/api/v1/me/invoices` tới Tenancy.

## Definition of Done

- [ ] Mọi bước qua phần Kiểm tra bước; mọi ô Acceptance được **tick bởi người làm**, kèm export Apidog trong PR.
- [ ] `npm run build` + `npm run lint` pass; không có file test, không sửa `src/shared`.
- [ ] PR `Tenancy-Service` + PR `api-gateway` ghi `Closes pbl6-home-renter/docs#<số issue>`, baoduong17 approve.
