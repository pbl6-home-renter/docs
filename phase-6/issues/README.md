# Phase 6 — Bảng task

Viết task mới theo [`_TEMPLATE.md`](_TEMPLATE.md). Task It5 đã viết step-by-step đầy đủ; task ⚪ Outline (It6) sẽ viết chi tiết trong tuần It5.

## Chốt trước khi bắt đầu It5 (baoduong17 — API owner)

| # | Vấn đề | Task bị chặn |
|---|---|---|
| 1 | Media cho Building: presign đòi `ownerId` nhưng Building chưa tồn tại → đề xuất presign không cần owner, rồi internal attach | P6-04, P5-08b (media), P6-03b |
| 2 | Contract Billing lệch D39 (RatePolicy create/batch/PATCH, BillingSetting có field overdue, `previousReading` bắt buộc, `overdue-debts`/`send-reminder`) | P6-02a → toàn bộ P6-02 |
| 3 | Contract HĐ: `rentalType: DAILY` trái D9, `tenantCccd` chưa có cột, `paymentDueDay` nằm ở Contract hay BillingSetting | P6-01a/b |
| 4 | Room status: response có `cleaning`/`pending_cleanup` nhưng domain không có; checkout cần trạng thái "chờ dọn" | P5-09c (mark-ready), P6-01e |
| 5 | Payment đặt ở `payment-service` riêng hay tạm trong tenancy | P6-05, P6-02g |
| 6 | Phương án OCR (Tesseract trong tenancy / dịch vụ ngoài / bỏ) | P6-02h |

## Iteration 5 (02/11–08/11)

| ID | Task | Assignee | Pts | Phụ thuộc |
|---|---|---|---|---|
| [P6-01](P6-01-tenancy-contract-vertical-slice.md) | Contract vertical slice (Epic) | leminhkhai345 | 18 (It5) + 8 (It6) | P5-08, P5-09, P6-04 |
| ↳ [P6-01a](P6-01a-contract-domain-persistence.md) | Contract domain, persistence, migration | leminhkhai345 | 3 | P5-09b (migration `rooms`) |
| ↳ [P6-01b](P6-01b-contract-create-and-manage-draft.md) | Tạo và quản lý hợp đồng nháp | leminhkhai345 | 5 | P6-01a, P5-09b |
| ↳ [P6-01c](P6-01c-contract-template-and-draft-document.md) | Mẫu HĐ, áp mẫu, sinh tài liệu nháp | leminhkhai345 | 5 | P6-01b, P6-04 |
| ↳ [P6-01d](P6-01d-contract-activate-signed-file.md) | Upload bản ký và kích hoạt HĐ | leminhkhai345 | 5 | P6-01b, P6-04 |
| [P6-02](P6-02-tenancy-billing-vertical-slice.md) | Billing vertical slice (Epic) | huynhtiennhat0403 | 20 (It5) | P5-09, P5-08b |
| ↳ [P6-02a](P6-02a-billing-contract-alignment.md) | Chốt contract Billing theo D39 | huynhtiennhat0403 | 2 | — |
| ↳ [P6-02b](P6-02b-rate-policy-domain-persistence.md) | RatePolicy domain và persistence | huynhtiennhat0403 | 3 | P6-02a |
| ↳ [P6-02c](P6-02c-rate-policy-api.md) | API RatePolicy | huynhtiennhat0403 | 5 | P6-02b, P5-09b |
| ↳ [P6-02d](P6-02d-billing-setting.md) | BillingSetting domain + API | huynhtiennhat0403 | 3 | P6-02a, P6-02c |
| ↳ [P6-02e](P6-02e-meter-reading-create-list.md) | MeterReading nhập tay + liệt kê | huynhtiennhat0403 | 5 | P6-02a, P5-09b |
| ↳ [P6-02f](P6-02f-meter-reading-bulk.md) | Chốt chỉ số hàng loạt theo tòa | huynhtiennhat0403 | 2 | P6-02e |
| [P6-03](P6-03-fe-landlord-building-room-screens.md) | Màn Building/Room landlord + admin duyệt (Epic) | ThaiBao11125 | 18 | `fe#6`, P5-08, P5-09 |
| ↳ [P6-03a](P6-03a-fe-building-api-list-detail.md) | Building API layer, list, detail | ThaiBao11125 | 5 | `fe#6`, P5-08c |
| ↳ [P6-03b](P6-03b-fe-building-create-edit-delete.md) | Wizard tạo, sửa, xóa Building | ThaiBao11125 | 5 | P6-03a, P5-08b/c, P6-04 |
| ↳ [P6-03c](P6-03c-fe-room-list-create-edit.md) | List, tạo, sửa, xóa Room | ThaiBao11125 | 5 | P6-03a, P5-09b/c |
| ↳ [P6-03d](P6-03d-fe-admin-building-approval.md) | Admin duyệt/từ chối Building | ThaiBao11125 | 3 | P6-03a, P5-08d |
| [P6-04](P6-04-identity-media-presign-upload.md) | Media upload 2 bước (Identity) | baoduong17 | 8 | — |

## Iteration 6 (09/11–15/11) — outline

| ID | Task | Assignee | Pts (sơ bộ) | Phụ thuộc |
|---|---|---|---|---|
| ↳ [P6-01e](P6-01e-contract-members-and-checkout.md) | Thành viên HĐ, HĐ của tenant, checkout, quyết toán cọc | leminhkhai345 | 8 | P6-01d, P6-05 |
| ↳ [P6-02g](P6-02g-invoice-outline.md) | Invoice: sinh, phát hành, xem, hủy | huynhtiennhat0403 | ~13 | P6-02c, P6-02e, P6-01 |
| ↳ [P6-02h](P6-02h-meter-reading-ocr-preview.md) | OCR preview chỉ số công tơ | huynhtiennhat0403 | ~5 | P6-02e, P6-04, quyết định OCR |
| [P6-05](P6-05-payment-cash-mock.md) | Thanh toán tiền mặt / mock | baoduong17 | ~8 | P6-02g |
| [P6-06](P6-06-fe-contract-invoice-screens.md) | Màn Contract, Meter reading, Invoice (Web) | ThaiBao11125 | ~13 | P6-03, P6-01, P6-02 |
| [P6-07](P6-07-demo-seed-and-staging.md) | Seed demo + chốt staging + demo script | baoduong17 | ~5 | P6-01, P6-02, P6-05 |

## Thứ tự

- Contract: `P6-01a → P6-01b → (P6-01c ∥ P6-01d) → P6-01e`.
- Billing: `P6-02a → P6-02b → P6-02c → P6-02d`; `P6-02e → P6-02f` song song sau `P6-02a`; It6: `P6-02g`, `P6-02h`.
- FE: `P6-03a → (P6-03b ∥ P6-03c ∥ P6-03d)` → It6 `P6-06`.
- `P6-04` làm sớm nhất trong It5 vì chặn `P6-01c/d` và `P6-03b`.

## Quy định chung

Giữ nguyên quy định trong [Phase 5](../phase-5/issues/README.md#quy-định-chung-cho-tất-cả-task). PR code ghi `Closes pbl6-home-renter/docs#<số>`; số issue được điền sau khi tạo issue trên GitHub.
