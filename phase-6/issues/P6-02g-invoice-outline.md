# P6-02g — Invoice: sinh theo tòa + kỳ, phát hành, hủy, tenant xem (issue cha)

**Epic:** [P6-02](P6-02-tenancy-billing-vertical-slice.md)  
**Trạng thái:** 🔵 Split — làm qua 4 sub-issue bên dưới, issue này đóng khi cả 4 Done  
**Người phụ trách:** leminhkhai345  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 11 points (tổng sub-issue)  
**Phụ thuộc:** P6-02c, P6-02e, P6-02h (migration `meter_readings`), P6-01e1/P6-01e2 (`contract_members`, quy tắc "HĐ của tôi")
**Repo:** `Tenancy-Service` (+ 1 dòng ở `api-gateway` trong g4)  
**Iteration:** It6 (09/11–15/11)  
**Issue:** `docs#77`

## Mục tiêu

Landlord chọn Tòa + Kỳ → sinh/tính lại hóa đơn `pending` cho mọi HĐ đủ dữ kiện, xem danh sách phòng bị chặn kèm mã lỗi, thêm phí khác/giảm trừ, phát hành hàng loạt; hủy (`void`) rồi sinh lại khi sai. Tenant xem hóa đơn đã phát hành của mình.

## Quyết định áp dụng

- `P6-D64` — vòng đời: sinh theo yêu cầu, `pending` tính lại giữ `other_fees`/`note`, `issued` bất biến, `void` + generate lại có `voided_invoice_id`, `/me/invoices`.
- `P6-D65` — quy tắc tính: `headCount`, xe, prorate, làm tròn tổng (EC14), mã hóa đơn, decimal.
- `P6-D66` — khóa sửa reading khi kỳ đã phát hành (làm ở P6-02h).
- `P6-D61` — không Payment, demo dừng ở `issued`.
- `P1-D39`, `P1-D37`, `P1-D33`, `P2-D43`, `P2-D48`.

## Sub-issue

| ID | Task | Endpoint | Estimate | Phụ thuộc |
|---|---|---|---|---|
| [P6-02g1](P6-02g1-invoice-domain-calculator.md) | Aggregate, bảng `invoices`, calculator thuần + bảng Ví dụ số | — | 3 pts |  |
| [P6-02g2](P6-02g2-invoice-generate.md) | Sinh / tính lại `pending` theo tòa + kỳ, `blocked[]` | `POST /invoices/generate` | 3 pts | g1, P6-02h, P6-01e1 |
| [P6-02g3](P6-02g3-invoice-landlord-manage.md) | Landlord list/detail/PATCH, phát hành hàng loạt (`Idempotency-Key`), hủy | `GET /invoices`, `GET/PATCH /invoices/{id}`, `POST /invoices/issue-invoice`, `POST /invoices/{id}/cancel-invoice` | 3 pts | g2 |
| [P6-02g4](P6-02g4-invoice-tenant-view.md) | Tenant xem hóa đơn `issued` | `GET /me/invoices`, `GET /invoices/{id}` | 2 pts | g3, P6-01e2 |

Thứ tự: `g1 → P6-02h → g2 → g3 → g4`. API contract được cập nhật trong PR implementation của từng issue backend, không có dependency P6-09 riêng.

## Đã gỡ khỏi phạm vi (so với outline cũ)

| Mục cũ | Lý do |
|---|---|
| Sinh `pending` tự động bằng consumer `meter_reading.recorded` (`P1-D33②`) | `P6-D64`: sinh theo yêu cầu `POST /invoices/generate` |
| `POST /invoices` — `createSettlementInvoice` (hóa đơn quyết toán khi checkout) | `P6-D64`: không có hóa đơn quyết toán, không cột `type`; chênh lệch ghi bằng `other_fees` |
| `GET /invoices/overdue-debts`, `POST /invoices/send-reminder` | `P1-D39` + `P6-D64`: không `overdue`, không nhắc nợ |
| `GET /invoices/tenant` | `P6-D64`: thay bằng `GET /me/invoices` |
| `paidAmount`, `remainingAmount`, `dueDate`, `INVOICE_ALREADY_PAID`, tổng thanh toán từ payment-service | `P6-D61`: Payment ra Stretch |
| Unit test calculator | Quy ước team không viết test; xác minh bằng bảng Ví dụ số trong g1 |

## Câu hỏi mở

The former business questions are resolved by P6-D61/D64/D70/D72. Remaining work is ordered by the explicit dependencies of g1–g4 and P6-02h; no new rule is delegated to an implementer.

## Definition of Done

- [ ] 4 sub-issue Done; luồng demo `generate → PATCH → issue-invoice → /me/invoices` chạy qua gateway.
- [ ] `api-docs` của nhóm Invoice `released`, không còn path đã gỡ ở bảng trên.
