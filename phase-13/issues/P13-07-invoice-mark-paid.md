# P13-07 — Hóa đơn: landlord đánh dấu "Đã thu"

**Trạng thái:** 🟡 Open
**Người phụ trách (đề xuất):** `leminhkhai345` (BE) + `ThaiBao11125` (Web) + Mobile (PM giao, chỉ hiển thị)
**Người review:** `baoduong17` (BE, API owner), PM/leader (Web)
**Ước lượng:** 3 points
**Phụ thuộc:** —
**Repo / branch:** `Tenancy-Service`, `api-docs`, `fe`, `mobile` · `feature/p13-07-invoice-mark-paid`

> **Đọc trước khi code:** [`decisions.md`](../decisions.md) (P13-D104; D39 vẫn áp dụng: không quá hạn, không phạt, không thanh toán online).

## Mục tiêu

Landlord bấm **"Đã thu"** trên hóa đơn đã phát hành để ghi nhận tiền đã nhận ngoài app (tiền mặt, chuyển khoản). Tenant thấy hóa đơn ở trạng thái "Đã thu".

## Quy tắc nghiệp vụ

| Trạng thái hiện tại | Đánh dấu "Đã thu" | Hủy hóa đơn |
|---|---|---|
| `pending` (nháp) | ❌ `409` | Như hiện tại |
| `issued` | ✅ → `paid` | Như hiện tại |
| `paid` | Gọi lại → trả kết quả cũ (idempotent) | ❌ `409` |
| `void` | ❌ `409` | — |

- Chỉ landlord sở hữu hóa đơn được đánh dấu; tài khoản bị khóa → `403 ACCOUNT_LOCKED`.
- Lưu `paidAt` (thời điểm đánh dấu) và `paidBy`. Đánh dấu cả hóa đơn, không theo từng người (D4/D22).
- Không có thao tác "bỏ đánh dấu" trong task này.

## Contract (đề xuất, API owner chốt trong `api-docs` trước khi code)

- `POST /invoices/{invoiceId}/mark-paid`, role `landlord`, không body. Thành công `200` kèm hóa đơn.
- Thêm `paid` vào enum `InvoiceStatus`; thêm `paidAt` (nullable) vào schema hóa đơn.
- Mã lỗi: hóa đơn không ở `issued` → `409` (tên mã do API owner đặt theo quy ước hiện có).
- Filter danh sách hóa đơn hỗ trợ `status=paid`.

## Phạm vi

1. **api-docs:** path, schema, enum, mã lỗi, sequence diagram; bundle.
2. **Tenancy:** `InvoiceStatus.PAID`, method domain `markPaid()`, command `invoice-mark-paid` (theo mẫu `invoice-cancel`), migration cột `paid_at`, `paid_by`; chặn `invoice-cancel` khi đã `paid`.
3. **fe (landlord):** nút "Đã thu" ở chi tiết và danh sách hóa đơn (có hộp xác nhận), badge trạng thái mới, filter "Đã thu".
4. **fe / mobile (tenant):** hiển thị badge "Đã thu".

## Acceptance

- [ ] Hóa đơn `issued` → đánh dấu → `paid`, có `paidAt`.
- [ ] Đánh dấu hóa đơn `pending` / `void` → `409`.
- [ ] Hủy hóa đơn `paid` → `409`.
- [ ] Landlord khác → `403`/`404` theo contract; tenant gọi → `403`.
- [ ] Gọi đánh dấu hai lần → lần hai trả cùng kết quả, không lỗi.
- [ ] Tenant thấy "Đã thu" trên Web (và mobile nếu có màn hóa đơn).

## Definition of Done

- [ ] BE: unit test domain + command; `npm test`, `npm run build`, `npm run lint` pass; migration chạy và revert được.
- [ ] fe: `npm run build`, `npm run lint`, `npm run i18n:check` pass; không viết file test.
- [ ] api-docs merge trước hoặc cùng lúc với BE; mỗi repo một PR, ghi chung issue này.

## Ngoài phạm vi

- Thanh toán online, đối soát tự động, quá hạn/nhắc hạn, thu theo từng người.
- Thông báo cho tenant khi hóa đơn được đánh dấu đã thu (có thể thêm sau theo quy ước P12-D95).
