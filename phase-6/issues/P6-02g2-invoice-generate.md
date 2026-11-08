# P6-02g2 — Invoice: sinh / tính lại hóa đơn `pending` theo tòa + kỳ

**Epic:** [P6-02](P6-02-tenancy-billing-vertical-slice.md) · cha: [P6-02g](P6-02g-invoice-outline.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** leminhkhai345  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 3 points · 8–12 giờ  
**Phụ thuộc:** P6-02g1 (aggregate + calculator), P6-02h (migration `meter_readings` + baseline kỳ đầu — phải merge trước, `P6-D70`), P6-01e1 (port đếm member theo kỳ) 
**Repo / branch:** `Tenancy-Service` · `feature/p6-02g2-invoice-generate`  
**Iteration:** It6 (09/11–15/11)  
**Issue:** `docs#99`

> **Đọc trước khi code:** `AGENTS.md` và skill trong `.agents/skills/` của repo (backend: `be-feature-workflow`). Issue **không** quy định cách đặt file, đặt tên hay style — nếu issue nói khác skill thì làm theo skill. Nguồn mâu thuẫn xử lý theo [`P6-D75`](../decisions.md#d75--thứ-tự-ưu-tiên-nguồn-và-cách-xử-lý-câu-hỏi-mở): `decisions.md` > `api-docs` > skill > issue.

## Mục tiêu

Landlord chọn **Tòa + Kỳ** rồi gọi `POST /invoices/generate { buildingId, period }`: mỗi HĐ `active` của tòa có hiệu lực trong kỳ được tạo mới hoặc tính lại bản `pending`; HĐ thiếu dữ kiện trả về trong `blocked[]` kèm mã lỗi. Gọi lại bao nhiêu lần cũng cho cùng kết quả.

## Quyết định áp dụng

- `P6-D64` — sinh theo yêu cầu (không event); đủ dữ kiện → tạo/tính lại `pending`; thiếu → `blocked[] { roomId, contractId, reasonCode }` (thay danh sách chờ sửa lỗi của `P1-D34`, không lưu bảng); tính lại **giữ `other_fees` và `note`**; `issued` không đụng tới; bản mới sau `void` có `voided_invoice_id`.
- `P6-D65` — `headCount` theo khoảng ở; số xe từ `contracts.vehicle_count`; mã `INV-YYYYMM-XXXX` sinh lại tối đa 5 lần khi trùng.
- `P6-D62` — phòng có 2 HĐ trong cùng kỳ là ngoài MVP (partial unique index `contracts (room_id) WHERE status='active'` đảm bảo tối đa 1 HĐ active/phòng).
- `P6-D70` — kỳ đầu: reading chốt tháng có `previous` = baseline cùng kỳ (P6-02h) → điện/nước kỳ đầu tính theo số thực; generate chỉ đọc reading **không phải baseline** của kỳ.
- `P6-D71` — HĐ `active` sửa được `vehicleCount` → landlord gỡ `VEHICLE_COUNT_MISSING` rồi generate lại; `pending` dùng số mới.
- `P6-D72` — bộ rate thiếu mục `electricity`/`water` → `blocked` `RATE_MISSING`; `totalAmount` = round half-up của Σ dòng (calculator g1).
- `P1-D39` (EC4) — tính bằng bộ rate **đang chạy lúc gọi**; bản `pending` cũ được tính lại với giá mới.

## Contract (đồng bộ cùng implementation theo quyết định đã duyệt)

| Endpoint | operationId | Success | Lỗi riêng |
|---|---|---|---|
| `POST /invoices/generate` | `postInvoicesGenerate` | `200 INVOICES_GENERATED` | `404 BUILDING_NOT_FOUND`, `403 FORBIDDEN`, `422 VALIDATION_FAILED` |

- File contract: `api-docs/src/paths/invoices/invoices-generate.yaml`; request `api-docs/src/requests/invoices/invoice-generate-request-dto.yaml`. Cập nhật operation/schema cùng PR implementation theo P6-D64/D72; bỏ `POST /invoices` settlement (`createSettlementInvoice`) khỏi spec.
- Role: `landlord`. Trả `200` (không phải `201`) vì một lần gọi có thể chỉ tính lại.
- Response `data`:

```json
{
  "buildingId": "…", "period": "2026-10",
  "generated":    [{ "invoiceId": "…", "code": "INV-202610-7KQ2", "contractId": "…", "roomId": "…", "totalAmount": "4875400" }],
  "recalculated": [{ "invoiceId": "…", "code": "INV-202610-A1B9", "contractId": "…", "roomId": "…", "totalAmount": "3593600" }],
  "blocked":      [{ "roomId": "…", "contractId": "…", "reasonCode": "READING_MISSING" }]
}
```

- `reasonCode` ∈ `READING_MISSING`, `RATE_MISSING`, `TIER_CONFIG_INVALID`, `AREA_MISSING`, `HEADCOUNT_ZERO`, `VEHICLE_COUNT_MISSING`, `TOTAL_NEGATIVE` (EC2/3/13/6/7/8/17). HĐ đã có bản `issued` của kỳ → **bỏ qua**, không nằm trong danh sách nào.

### Mapping field

| Request / Response field | Nguồn | Cột DB | Ghi chú / validation |
|---|---|---|---|
| `buildingId` | body | `rooms.building_id` | UUID; tòa của landlord khác → `403` |
| `period` | body | `invoices.period`, `meter_readings.period` | `^[0-9]{4}-(0[1-9]\|1[0-2])$` |
| HĐ được chọn | `ContractRepository` (method mới) | `contracts.status='active' AND start_date <= cuối kỳ AND end_date >= đầu kỳ`, join `rooms.building_id` | EC10: HĐ ngoài kỳ không được chọn |
| `headCount` | port từ P6-01e1 | `contract_members.joined_at/left_at` | `P6-D65` |
| reading điện/nước | `MeterReadingRepository` (method mới `findByRoomAndPeriod`) | `meter_readings (room_id, type, period) WHERE is_baseline = false` | consumption = `current - previous`; kỳ đầu `previous` = baseline (`P6-D70`) |
| `totalAmount` | calculator g1 + `otherFees` giữ lại | `invoices.total_amount` | string |

**Port invoice cần từ P6-01e1** (khai báo trong module invoice, adapter gọi repository `contract_members` của P6-01e1):

```ts
interface ContractHeadCountPort {
  countActiveMembers(contractId: Uuid, periodStart: string, periodEnd: string,
                     context?: TransactionContext): Promise<number>;
}
// SQL tương đương: count(*) FROM contract_members WHERE contract_id = $1 AND is_deleted = false
//   AND joined_at <= $periodEnd AND (left_at IS NULL OR left_at >= $periodStart)
```

### Ví dụ số

Dùng lại bảng của [P6-02g1](P6-02g1-invoice-domain-calculator.md). Kịch bản tích hợp riêng của task này:

| Input | Kết quả mong đợi |
|---|---|
| Tòa có 3 HĐ active: P101 đủ dữ kiện (#1 g1), P102 thiếu reading nước, P103 có phí QLVH mà `area` NULL | `generated` 1 (P101, `4875400`); `blocked` 2: P102 `READING_MISSING`, P103 `AREA_MISSING` |
| Gọi lại lần 2, không đổi gì | `generated` 0, `recalculated` 1 (P101, **cùng `invoiceId` + `code`**), `blocked` 2 |
| PATCH P101 thêm `otherFees [-700000]` (g3) rồi đổi giá wifi 100.000 → 150.000, generate lại | `recalculated` P101 = 4.875.400 + 50.000 − 700.000 = **4.225.400**; `other_fees` vẫn còn dòng −700.000 |
| P101 đã `issued`, generate lại | P101 không xuất hiện trong 3 danh sách; DB không đổi |
| HĐ P104 bắt đầu 01/09, baseline `2026-09` điện 1000 / nước 10, reading chốt `2026-09` điện 1060 / nước 13 | P104 `generated` kỳ `2026-09`, điện tính trên **60 kWh** (không phải 0), nước **3 m³** |
| P105 có phí gửi xe, `vehicle_count` NULL → `blocked` `VEHICLE_COUNT_MISSING`; `PATCH /contracts/{id} { vehicleCount: 1 }` (HĐ active, `P6-D71`) rồi generate lại | P105 `generated`, dòng gửi xe 1 × 80.000 |
| P101 `void` rồi generate lại | `generated` P101 với `code` **mới**, `voided_invoice_id` = id bản void |

## Tham chiếu code

- Module mẫu: `Tenancy-Service/src/modules/rate-policy/` (command UoW + outbox, controller `@Roles(UserRole.LANDLORD)`, `@ResponseCode`).
- Command handler mẫu có lock: `src/modules/meter-reading/application/commands/meter-reading-create/meter-reading-create.command.handler.ts` (`findByIdForUpdate` + `outbox.append`).
- Load tòa + check quyền: `BUILDING_DI_TOKEN.REPOSITORY` (`src/modules/building/building.module.ts`), exception `src/modules/rate-policy/domain/exceptions/rate-policy-building-not-found.exception.ts` làm mẫu cho `404 BUILDING_NOT_FOUND`.
- Contract: `ContractRepository.findByIdForUpdate` (`src/modules/contract/domain/repositories/contract.repository.ts`) — thêm method chọn HĐ theo tòa + kỳ.
- RatePolicy: `RatePolicyRepository.findByRoom/findByBuilding`.

## Các bước triển khai

### Bước 1 — Dữ liệu thử

- **Cách làm:** `npm run migration:run && npm run start:dev`. Landlord A: 1 tòa, 3 phòng (P101 `area` 18.5, P102, P103 `area` NULL). Bộ rate tòa: `POST /api/v1/buildings/{buildingId}/rate-policies/batch` với `rates` = EVN + nước khoán 80000 + wifi 100000 + QLVH 10000 (body theo P6-02c). Tạo 3 HĐ qua `POST /contracts` rồi `UPDATE contracts SET status='active' WHERE id IN (…)` nếu P6-01d chưa merge. Thêm member qua API P6-01e1 (P101: 3 người). Reading: baseline `2026-09` + kỳ `2026-10` (P101 điện 1200→1550, nước 50→56; P102 chỉ điện; P103 đủ cả hai).
- **Kiểm tra bước:** `SELECT room_id, type, period, current_reading FROM meter_readings WHERE period='2026-10'` → 5 row.

### Bước 2 — Method đọc dữ liệu đầu vào + adapter head count

- **Cách làm:** `ContractRepository`: chọn HĐ active theo `buildingId` + khoảng kỳ. `MeterReadingRepository`: `findByRoomAndPeriod(roomId, period)`. Adapter `ContractHeadCountPort` gọi method của P6-01e1 (không query bảng `contract_members` trực tiếp nếu P6-01e1 đã có).
- **Kiểm tra bước:** log tạm trong handler (xóa trước PR) in ra 3 HĐ, P101 `headCount=3`.

### Bước 3 — Command handler generate

- **Cách làm:** load Building → `404`/`403`. Với **từng HĐ, một `unitOfWork.run` riêng** (lỗi một HĐ không rollback HĐ khác): `contracts.findByIdForUpdate` (khóa tránh 2 request generate song song) → `findOpenByContractPeriod`: `issued` → bỏ qua; gom input → calculator g1. Có mã chặn → đẩy vào `blocked`, không ghi gì. Có bản `pending` → `recalculate` (kiểm `TOTAL_NEGATIVE` với `other_fees` cũ → nếu âm thì `blocked`, bản cũ giữ nguyên). Không có → tạo mới, `voidedInvoiceId` = `findLatestVoidByContractPeriod`; save, bắt unique `UQ_invoices_code` → sinh mã khác, tối đa 5 lần. Append outbox `invoice.generated` / `invoice.recalculated` trong cùng transaction.
- **Kiểm tra bước:** `POST /api/v1/invoices/generate` body `{ "buildingId": "<A>", "period": "2026-10" }` → `200 INVOICES_GENERATED`, `generated` 1, `blocked` 2 như bảng Ví dụ số. `SELECT code, total_amount, status FROM invoices` → 1 row `4875400`, `pending`.

### Bước 4 — Idempotent + tính lại

- **Kiểm tra bước:** thêm HĐ P104 (bắt đầu 01/09) theo dòng kỳ đầu của bảng Ví dụ số, generate `2026-09` → điện 60 kWh. Gọi lại y nguyên → `recalculated` chứa P101 cùng `invoiceId`; `SELECT count(*) FROM invoices` vẫn 1. `UPDATE invoices SET other_fees='[{"name":"Giảm trừ","amount":"-700000"}]'` rồi generate → `total_amount` = 4175400, `other_fees` không mất. `UPDATE invoices SET status='issued', issued_at=now()` rồi generate → P101 vắng mặt, `updated_at` không đổi.

### Bước 5 — Controller, Swagger

- **Cách làm:** route `POST /invoices/generate` trong controller `invoices` (`@Roles(UserRole.LANDLORD)`), request DTO validate `buildingId` UUID, `period` regex. Module invoice import `BuildingModule`, `RoomModule`, `ContractModule`, `RatePolicyModule`, `MeterReadingModule`, `OutboxModule`.
- **Kiểm tra bước:** `period: "2026-13"` → `422 VALIDATION_FAILED`; tòa landlord B → `403`; UUID không tồn tại → `404 BUILDING_NOT_FOUND`; token tenant → `403`. Swagger hiện `postInvoicesGenerate`. `outbox_messages` có `invoice.generated`.

## Ngoài phạm vi

- Sinh tự động theo event `meter_reading.recorded` (`P1-D33②` bị thay bởi `P6-D64`).
- Hóa đơn quyết toán khi checkout (`P6-D64`, `P6-D61`). Prorate theo ngày checkout (`P6-D65` dùng `end_date`).
- PATCH/phát hành/hủy (g3); tenant xem (g4); khóa sửa reading (P6-02h).

## Blocker

- Không có. (Kỳ đầu từ baseline đã chốt ở `P6-D70`, giao ở P6-02h.)

## Cập nhật `api-docs` (bắt buộc trước khi đóng issue)

- [ ] Sequence diagram `postInvoicesGenerate` (Gateway → Tenancy → load Building → lặp HĐ: lock → calculator → save + outbox).
- [ ] `x-apidog-status: released`; `npm run bundle`.

## Acceptance (Apidog)

- [ ] Happy path → `200 INVOICES_GENERATED`, đúng 3 danh sách.
- [ ] Gọi 2 lần → không tạo trùng; `other_fees`/`note` giữ nguyên khi tính lại.
- [ ] Kỳ đầu của HĐ tính tiêu thụ từ baseline (không ra 0).
- [ ] Bản `issued` không bị đụng; sau `void` sinh bản mới có `voidedInvoiceId`.
- [ ] Sai `period` → `422 VALIDATION_FAILED`; tòa landlord khác → `403`; không token → `401`; tòa không tồn tại → `404 BUILDING_NOT_FOUND`.

## Definition of Done

- [ ] Mọi bước qua phần Kiểm tra bước; mọi ô Acceptance được **tick bởi người làm**, kèm export Apidog trong PR.
- [ ] `npm run build` + `npm run lint` pass; không có file test, không sửa `src/shared`.
- [ ] PR vào `main` ghi `Closes pbl6-home-renter/docs#<số issue>`, baoduong17 approve.
