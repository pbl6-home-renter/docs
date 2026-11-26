# P13-14 — Hóa đơn hiển thị minh bạch: giá thuê gốc, chỉ số cũ/mới, ảnh công tơ

**Trạng thái:** 🟡 Open
**Người phụ trách (đề xuất):** `baoduong17` (BE) + `ThaiBao11125` (Web)
**Người review:** `leminhkhai345`, PM/leader
**Ước lượng:** 3 points
**Phụ thuộc:** P13-12 (cùng sửa module invoice, làm sau để tránh xung đột)
**Repo / branch:** `Tenancy-Service`, `api-docs`, `fe` · `feature/p13-14-invoice-detail-transparency`

> **Đọc trước khi code:** P6-D78 (ảnh công tơ là bằng chứng chỉ số), `AGENTS.md` và skill của từng repo.

## Mục tiêu

Khi xem hóa đơn, landlord và tenant biết được tiền phòng tính bao nhiêu ngày và chỉ số điện nước lấy từ đâu, để tự đối chiếu mà không phải hỏi lại.

## Hiện trạng

- `GET /invoices/:id` (`invoice-detail.response.dto.ts`) và bản dành cho tenant (`invoice-tenant-detail.response.dto.ts`) chỉ trả `rentAmount`, tức số tiền đã nhân tỉ lệ ngày ở.
- Mỗi dòng `breakdown[]` chỉ có `quantity` (số tiêu thụ). Đầu vào của bộ tính tiền chỉ mang `consumption`, không có chỉ số cũ/mới.
- Sửa chỉ số (`PATCH /meter-readings/:id`) khi hóa đơn kỳ đó còn nháp: bấm "Sinh hóa đơn" lại thì hóa đơn nháp **được tính lại** (`invoice-generation.service.ts`, kết quả `RECALCULATED`). Chỉ thiếu lời nhắc trên UI.

## Phạm vi

### BE (snapshot lúc sinh hóa đơn)

Hóa đơn là bản chụp tại thời điểm sinh, nên các giá trị dưới đây lưu cùng hóa đơn, không tra lại khi đọc.

| Field | Vị trí | Ý nghĩa |
|---|---|---|
| `rentUnitPrice` | cấp hóa đơn | Giá thuê gốc của hợp đồng tại thời điểm sinh |
| `rentProrateRatio` | cấp hóa đơn | Tỉ lệ ngày ở (cùng định dạng `prorateRatio` của breakdown, ví dụ `0.500000`) |
| `previousReading`, `currentReading` | dòng breakdown điện/nước đồng hồ | Chỉ số cũ / mới; `null` với dòng `per_head` và phí khác |
| `evidenceMediaIds` | dòng breakdown điện/nước đồng hồ | Ảnh công tơ của lần chốt số; mảng rỗng nếu không có |

- Hóa đơn cũ chưa có dữ liệu → trả `null` / mảng rỗng. Không viết migration lấp dữ liệu cũ.
- Tenant chỉ mở được ảnh của hóa đơn thuộc hợp đồng của mình. Kiểm tra quyền đọc media hiện có trước khi trả ID.
- api-docs: thêm field vào schema chi tiết hóa đơn (landlord và tenant), bundle.

### FE (Web)

- Chi tiết hóa đơn: dòng tiền phòng hiển thị dạng "3.000.000đ × 15/30 ngày = 1.500.000đ" khi tỉ lệ khác 1.
- Dòng điện/nước: "Chỉ số 1200 → 1380 (180 kWh)" kèm nút xem ảnh công tơ.
- Sau khi sửa chỉ số thành công, nếu kỳ đó có hóa đơn nháp: hiện nhắc "Hóa đơn nháp kỳ này cần sinh lại để cập nhật".

## Acceptance

- [ ] Hợp đồng vào ở 15/30 ngày → chi tiết hóa đơn có `rentUnitPrice = 3000000`, `rentProrateRatio = 0.500000`, `rentAmount = 1500000`.
- [ ] Dòng điện có `previousReading`, `currentReading`, `quantity = current − previous`, `evidenceMediaIds` đúng ảnh của lần chốt.
- [ ] Hóa đơn sinh trước khi deploy vẫn mở được, các field mới là `null` / rỗng.
- [ ] Tenant xem được ảnh công tơ của hóa đơn mình; không xem được của phòng khác.
- [ ] Sửa chỉ số khi hóa đơn còn nháp → Web hiện nhắc sinh lại.

## Definition of Done

- [ ] BE: unit test bộ tính tiền và mapper; `npm test`, `npm run build`, `npm run lint` pass; migration (nếu đổi cột) chạy và revert được.
- [ ] fe: `npm run build`, `npm run lint`, `npm run i18n:check` pass; không viết file test.
- [ ] api-docs bundle; mỗi repo một PR, ghi chung issue này.

## Ngoài phạm vi

- Tự động tính lại hóa đơn nháp khi sửa chỉ số (đã có cách sinh lại thủ công).
- Mobile hiển thị các field mới (làm khi mobile có màn chi tiết hóa đơn).
