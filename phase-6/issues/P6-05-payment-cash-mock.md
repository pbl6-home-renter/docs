# P6-05 — Ghi nhận thanh toán tiền mặt / mock cho hóa đơn

**Trạng thái:** ⚪ Outline (viết chi tiết trong It5)  
**Người phụ trách:** baoduong17  
**Người review:** leminhkhai345  
**Ước lượng:** ~8 points · 18–24 giờ (ước tính sơ bộ)  
**Phụ thuộc:** P6-02 (Invoice — phần It6)  
**Iteration:** It6 (09/11–15/11)

## Mục tiêu

Landlord đánh dấu hóa đơn đã thu tiền mặt (`POST /payments/record-cash-payment`) và xem lịch sử thanh toán (`GET /payments`, `GET /me/payments`). Kênh `mock`/`cash` là kênh chính theo D39; VietQR auto-reconciliation để Stretch.

## Contract

- `api-doc/src/paths/payments/payments-record-cash-payment.yaml` (`postPaymentsRecordCashPayment`): header `Idempotency-Key`; lỗi `IDEMPOTENCY_KEY_REUSED`, `INVOICE_NOT_PAYABLE`, `AMOUNT_INVALID`, `VALIDATION_FAILED`.
- `api-doc/src/paths/payments/payments.yaml`, `me-payments.yaml`.
- Ngoài phạm vi: `payments-create-intent.yaml`, `payments-webhooks-provider.yaml` (Stretch).

## Cần chốt trước khi viết chi tiết

- [ ] **Đặt payment ở đâu:** kiến trúc (`phase-3/discovery/microservices-architecture.md` §3.1, §4.2) tách `payment-service` riêng (port 3003), nhưng repo này chưa tồn tại. Có hai lựa chọn:
  - (a) fork `boilerplate` thành `Payment-Service`, invoice cập nhật trạng thái qua event `PaymentRecorded` (Outbox → RabbitMQ → Inbox ở tenancy);
  - (b) tạm ghi nhận trong `tenancy-service` để kịp demo.

  Đề xuất **(a)** nếu It5 đúng tiến độ, ngược lại thì **(b)** và ghi decision.
- [ ] Bảng `payments` + `idempotency_keys` theo `phase-1/discovery/database-design.md`.

## Các bước (outline)

1. Chốt vị trí service, tạo repo/module, migration `payments`, `idempotency_keys`.
2. `record-cash-payment`: kiểm tra idempotency, kiểm tra invoice payable (gọi nội bộ tenancy qua `InternalHttpClient` hoặc read model), ghi payment, publish `PaymentRecorded` qua outbox.
3. Tenancy consume `PaymentRecorded` → cập nhật trạng thái invoice (Inbox chống trùng, theo `sample.subscriber.ts`).
4. `GET /payments` (landlord) và `GET /me/payments` (tenant), offset pagination.
5. Route trên `api-gateway`, sequence diagram, `x-apidog-status: released`.

## Definition of Done

- Cash payment chuyển invoice sang trạng thái đã thanh toán; gọi lại với cùng `Idempotency-Key` không tạo payment thứ hai.
- PR ghi `Closes pbl6-home-renter/docs#TBD`.
