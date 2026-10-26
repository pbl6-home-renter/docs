# P6-02g — Invoice: sinh pending, phát hành, xem, hủy, tenant xem *(outline — It6)*

**Epic:** [P6-02](P6-02-tenancy-billing-vertical-slice.md)  
**Trạng thái:** ⚪ Outline (viết chi tiết step-by-step khi It5 chạy được P6-02c/e)  
**Người phụ trách:** huynhtiennhat0403  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** ~13 points (sẽ tách sub-issue `P6-02g1…` khi viết chi tiết)  
**Phụ thuộc:** P6-02c (RatePolicy), P6-02e (MeterReading), P6-01 Contract (`contracts`, `contract_members`, `vehicle_count`)  
**Repo:** `Tenancy-Service`  
**Issue:** `docs#TBD`

## Mục tiêu

Khi phòng có đủ chỉ số điện + nước của kỳ và có bộ đơn giá, hệ thống sinh **Invoice `pending`** cho hợp đồng đang hiệu lực (D33② — từng phòng, không batch toàn kỳ); landlord xem/sửa phí phụ, phát hành (`issued`), hủy (`void`); tenant xem hóa đơn của mình.

## Contract dự kiến dùng

| Endpoint | File `api-doc` | MVP? |
|---|---|---|
| `GET /invoices` | `src/paths/invoices/invoices.yaml` (`getInvoices`) | ✅ |
| `GET /invoices/{invoiceId}`, `PATCH /invoices/{invoiceId}` | `invoices-invoiceId.yaml` | ✅ |
| `POST /invoices/issue-invoice` | `invoices-issue-invoice.yaml` (batch phát hành, `Idempotency-Key`) | ✅ |
| `POST /invoices/{invoiceId}/cancel-invoice` | `invoices-invoiceId-cancel-invoice.yaml` | ✅ |
| `GET /invoices/tenant` | `invoices-tenant.yaml` | ✅ |
| `POST /invoices` (`createSettlementInvoice` — hóa đơn quyết toán khi checkout) | `invoices.yaml` | Phụ thuộc Contract checkout — có thể Stretch |
| `GET /invoices/overdue-debts`, `POST /invoices/send-reminder` | — | ❌ Trái D39 (không `overdue`) — đề xuất gỡ khỏi contract |

## Các bước chính (sẽ chi tiết hóa)

1. **Rà contract Invoice theo D39** (giống P6-02a): bỏ `overdue`/`due_date`; status chỉ `pending|issued|void`; `cancel` → `void`; kiểm tra `409 INVOICE_ALREADY_PAID` có hợp lệ khi chưa có Payment (payment-service) không.
2. **Domain + persistence `invoices`** (`database-design.md` §2.12): `code` unique (`INV-YYYYMM-XXXX`), `breakdown`/`other_fees` jsonb, partial unique `(contract_id, period) WHERE status IN ('pending','issued') AND is_deleted=false`, `voided_invoice_id`.
3. **Calculator thuần (không I/O)** theo `utility-billing-calculations.md` §3–§10: resolve rate `room → building` (§4), điện E1/E2, nước W1–W3, phí F1–F4, prorate §8, snapshot §9, block lỗi EC2/EC3/EC6/EC7/EC8/EC13/EC17. Viết unit test cho calculator (bộ ví dụ trong tài liệu) — đây là phần dễ sai nhất.
4. **Sinh pending tự động**: consumer `meter_reading.recorded` (Inbox dedup — pattern `src/modules/sample/presentation/messaging/sample.subscriber.ts`) → nếu phòng đủ 2 chỉ số kỳ đó + có HĐ active → tạo invoice `pending`; thiếu dữ kiện thì bỏ qua và log lý do.
5. **API landlord**: list/detail/patch (chỉ khi `pending`, `422 TOTAL_AMOUNT_INVALID`/`TOTAL_NEGATIVE`), issue batch (idempotency), cancel → `void`.
6. **API tenant**: `GET /invoices/tenant` lọc theo `contract_members` của user.
7. Sequence diagram + `released` cho từng endpoint.

## Câu hỏi mở (chốt trước khi viết chi tiết)

- Tổng thanh toán (D33③ suy ra từ Σ Payment) lấy từ payment-service bằng event hay internal HTTP (`src/shared/infrastructure/http/internal-http-client.service.ts`)?
- Có giữ `createSettlementInvoice` trong MVP không (phụ thuộc phạm vi Contract checkout).
