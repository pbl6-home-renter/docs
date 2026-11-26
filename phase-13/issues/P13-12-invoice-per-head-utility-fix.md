# P13-12 — BE: Sửa tính tiền điện/nước khoán theo đầu người

**Trạng thái:** 🟡 Open · **Ưu tiên cao (bug tính tiền)**
**Người phụ trách (đề xuất):** `leminhkhai345`
**Người review:** `baoduong17`
**Ước lượng:** 1 point
**Phụ thuộc:** —
**Repo / branch:** `Tenancy-Service` · `fix/p13-12-per-head-utility`

> **Đọc trước khi code:** [`decisions.md`](../decisions.md) (P13-D108), `AGENTS.md` và skill của repo.

## Bối cảnh

Nguồn: feedback review FE ngày 26/11/2026, PM đã đối chiếu code.

File: `Tenancy-Service/src/modules/invoice/domain/services/invoice-calculator.service.ts`

| Lỗi | Vị trí | Hiện tại | Hậu quả |
|---|---|---|---|
| 1 | dòng 30–31 | Kiểm tra `!input.readings.electricity \|\| !input.readings.water` **trước** `resolveRates()` | Phòng cấu hình điện hoặc nước `per_head` (khoán, không có đồng hồ) vẫn bị chặn `READING_MISSING`, không sinh được hóa đơn |
| 2 | dòng 148–154 | Điện/nước `per_head` trả `prorate: false` | Người vào ở giữa tháng bị tính đủ tháng tiền điện/nước khoán, trong khi các phí `per_head` khác (dòng 169) được tính theo tỉ lệ ngày ở |

## Quy tắc (P13-D108)

- Chỉ bắt buộc chỉ số của loại (điện / nước) có `rateKind !== 'per_head'`. Thiếu chỉ số loại đó → `READING_MISSING`.
- Điện/nước `per_head` tính theo tỉ lệ ngày ở (`prorate: true`), giống các phí `per_head` khác. Điện/nước theo đồng hồ giữ `prorate: false` (tính theo số tiêu thụ thật).
- Giữ thứ tự ưu tiên lỗi hiện có: thiếu chỉ số (của loại cần đồng hồ) vẫn được báo trước lỗi cấu hình đơn giá khác.

## Các bước

1. Gọi `resolveRates()` trước; sau đó kiểm tra chỉ số theo từng loại dựa trên `rateKind`.
2. Đổi `prorate` của nhánh `per_head` điện/nước thành `true`.
3. Unit test (`test/unit/invoice/domain/`):

| Cấu hình | Chỉ số | Kết quả mong đợi |
|---|---|---|
| Điện đồng hồ, nước `per_head` | Có điện, không có nước | Sinh được; nước = đơn giá × số người |
| Điện đồng hồ, nước `per_head` | Không có điện | `READING_MISSING` |
| Điện và nước đều `per_head` | Không có chỉ số nào | Sinh được |
| Nước `per_head` 100.000đ/người, 2 người, ở 15/30 ngày | — | Nước = 100.000đ (2 × 100.000 × 0,5) |
| Điện, nước đều đồng hồ | Thiếu nước | `READING_MISSING` (không đổi) |

## Acceptance

- [ ] Tòa có nước khoán theo đầu người: bấm sinh hóa đơn khi chưa nhập chỉ số nước → hóa đơn được tạo, không bị chặn.
- [ ] Hợp đồng bắt đầu giữa kỳ: dòng nước `per_head` có `prorateRatio` khác `1.000000`, đúng tỉ lệ như các phí khoán khác.
- [ ] Hóa đơn đã phát hành trước đó không bị thay đổi.

## Definition of Done

- [ ] `npm test`, `npm run build`, `npm run lint` pass.
- [ ] Nếu api-docs có mô tả quy tắc `READING_MISSING` / prorate thì sửa cho khớp và bundle.
- [ ] PR vào `main`, ≥ 1 reviewer.
