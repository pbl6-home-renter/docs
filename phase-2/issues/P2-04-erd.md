# P2-04 — ERD v1 Finalized

**Status:** 🟡 Open
**Owner:** BE · PM review
**Input:** P2-01 (feature-platform-map.md), `phase-1/discovery/database-design.md`, business-rules
**Output:** `discovery/erd-v1.md`

---

## Background

Phase 1 đã thiết kế database v3 (`database-design.md`) với ~21 entity + DDL. Tuy nhiên cần review lại sau khi có feature-platform map để đảm bảo:
- Entity nào thực sự cần cho MVP
- Có entity nào thiếu cho feature mới trong P2-01 không
- Decisions D30–D38 đã được áp đúng vào schema chưa

## Mục đích

Finalized ERD v1 — đảm bảo schema nhất quán với feature map + business rules đã freeze.

## Chi tiết thực hiện

### Bước 1: Review schema hiện tại

- Đọc `phase-1/discovery/database-design.md` — list toàn bộ entity
- Với mỗi entity: kiểm tra field, type, constraint, relationship

### Bước 2: So với feature map (P2-01)

- Entity nào dùng cho feature nào? (traceability)
- Feature nào trong P2-01 mà chưa có entity hỗ trợ?
- Entity nào thừa (không có feature nào dùng)?

### Bước 3: Kiểm tra decisions D30–D39

> **D39 (2026-09-26) đã thu hẹp D30/D32/D33/D36/D37 — kiểm tra theo D39, các ID cũ chỉ để tham chiếu lịch sử.**

- **D39:** `RatePolicy` gộp `UtilityRatePolicy` + `RecurringFee` vào `rates` jsonb, scope `building`|`room`, chỉ UPDATE, không versioning → đã có trong schema?
- **D39:** bỏ 2 con trỏ `*_policy_id`, bỏ cấp `landlord` → đã xóa?
- **D39:** `Invoice.invoice_status` = `pending`|`issued`|`void`, bỏ `partially_paid`/`paid`/`overdue`/`cancel` + bỏ `due_date` → đã update?
- **D39:** `Invoice.breakdown` gộp `utility_breakdown` + `fees_breakdown` thành 1 mảng, đủ `service_start`/`service_end`/`prorate_ratio`/`unit` → đã update?
- **D39:** `BillingSetting` → `payment_due_day`/`remind_day` advisory, scope `building`|`room` → đã update?
- **D39:** tài khoản nhận tiền nằm ở `LandlordProfile`, **không** tạo bảng `VietQrReceiverConfig` → đã loại?
- D31: Preset steps chỉ từ seed — schema note đúng?
- D32: `Contract.vehicle_count` — đã update?
- D33: Partial unique `(contract_id, period) WHERE invoice_status IN ('pending','issued')`, `other_fees` âm — đã update?
- D34: Baseline OCR bắt buộc — schema note đúng?
- D35: Manual correction allowed — schema note đúng?
- D38: ResidencyGateway — entity cho Phase 2?

### Bước 4: Adjust & finalize

- Thêm/xóa/sửa field nếu cần
- Vẽ lại ERD diagram
- Ghi change log

## Definition of Done

- [ ] File `discovery/erd-v1.md` tồn tại
- [ ] Danh sách entity đầy đủ với field, type, constraint
- [ ] ERD diagram (mermaid erDiagram) —语法valid
- [ ] Traceability matrix: entity ↔ feature (từ P2-01)
- [ ] Decisions D30–D38 đã được verify trong schema
- [ ] Change log so với database-design.md (nếu có thay đổi)
- [ ] PM đã review và approve
