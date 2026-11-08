# P6-02g1 — Invoice: aggregate, bảng `invoices` và calculator tính tiền thuần

**Epic:** [P6-02](P6-02-tenancy-billing-vertical-slice.md) · cha: [P6-02g](P6-02g-invoice-outline.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** leminhkhai345  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 3 points · 8–12 giờ  
**Phụ thuộc:** P6-02c (RatePolicy — đã merge `65c4910`), P6-02e (MeterReading — đã merge `6251329`)
**Repo / branch:** `Tenancy-Service` · `feature/p6-02g1-invoice-domain`  
**Iteration:** It6 (09/11–15/11)  
**Issue:** `docs#98`

> **Đọc trước khi code:** `AGENTS.md` và skill trong `.agents/skills/` của repo (backend: `be-feature-workflow`). Issue **không** quy định cách đặt file, đặt tên hay style — nếu issue nói khác skill thì làm theo skill. Nguồn mâu thuẫn xử lý theo [`P6-D75`](../decisions.md#d75--thứ-tự-ưu-tiên-nguồn-và-cách-xử-lý-câu-hỏi-mở): `decisions.md` > `api-docs` > skill > issue.

## Mục tiêu

Có aggregate `Invoice` + bảng `invoices` (migration chạy được) và một **calculator thuần** (không I/O) nhận dữ liệu đầu vào của một HĐ × kỳ, trả về `rentAmount` + `breakdown[]` snapshot hoặc một `reasonCode` chặn. Mọi dòng trong bảng **Ví dụ số** chạy qua script ra đúng số. Task này **không** có endpoint — g2/g3/g4 dùng lại.

## Quyết định áp dụng

- `P6-D64` — trạng thái `pending | issued | void`; `pending` tính lại được nhưng giữ `other_fees`/`note`; `issued` bất biến; bản thay thế có `voided_invoice_id`; **không có cột `type`**, không có hóa đơn quyết toán.
- `P6-D65` — `headCount` theo khoảng ở; số xe = `contracts.vehicle_count`; tiền phòng = `rent_price × prorateRatio` (calc §8, dùng `start_date`/`end_date`); **chỉ làm tròn `total_amount`** half-up về đồng (EC14, chi tiết ở `P6-D72`); mã `INV-YYYYMM-XXXX`; tiền/chỉ số là `numeric` trong DB, string trong JSON, thư viện decimal trong code.
- `P6-D72` — số tiền từng dòng `numeric(14,4)`, làm tròn half-up tới 4 chữ số; `total_amount` = round half-up về đồng của Σ dòng; bất biến là `total_amount = round(Σ dòng)` (không phải `Σ dòng = total_amount`); bộ rate thiếu mục `electricity` hoặc `water` → `RATE_MISSING`; thêm cột `void_reason text NULL`.
- `P1-D39` — 1 bộ rate/scope, kế thừa `room → building`; `breakdown` là một mảng, mỗi dòng có đủ `type, name, rate_kind, unit_price, quantity, unit, service_start, service_end, prorate_ratio, amount` (+ `tier_detail` khi `tiered`).
- `P1-D33` ④⑥ — điện không `per_head`; `other_fees` âm được, tổng âm → `TOTAL_NEGATIVE` (EC17).
- `P1-D37` — void là soft (đổi status, không xóa); `voided_invoice_id` trỏ **mới → cũ**.

## Contract

Không có endpoint. Shape dữ liệu phải khớp schema `Invoice` và P6-D64/D72: `api-docs/src/schemas/billing/invoice.yaml` (`breakdown[].serviceStart/serviceEnd` là `date`, mọi số tiền là string). Nếu phát hiện schema chưa đúng, issue implementation có API công khai liên quan cập nhật `api-docs` cùng PR.

### Mapping field

| Response field | Domain prop | Cột DB (`database-design.md` §2.12) | Ghi chú / validation |
|---|---|---|---|
| `id` | `id` | `id` | base entity |
| `contractId` | `contractId` | `contract_id` FK `contracts` | NOT NULL |
| — (lọc/quyền) | `landlordId`, `buildingId`, `roomId` | `landlord_id`, `building_id`, `room_id` | **lệch §2.12** (giống `meter_readings` ở P6-02e): denormalize để lọc theo tòa/landlord không join — ghi chú trong PR |
| `code` | `code` | `code varchar(32)` UNIQUE | `^INV-\d{6}-[A-Z0-9]{4}$` (`P6-D65`) |
| `period` | `period` | `period varchar(7)` | CHECK regex `^[0-9]{4}-(0[1-9]\|1[0-2])$`; tái dùng `ReadingPeriod` |
| `rentAmount` | `rentAmount` | `rent_amount numeric(14,4)` | ≥ 0, half-up 4 chữ số (`P6-D72`) |
| `breakdown[]` | `breakdown` | `breakdown jsonb` | key snake_case trong DB (như `rate_policies.rates`), camelCase trong API; `amount` là string 4 chữ số half-up (`P6-D72`) |
| `otherFees[]` | `otherFees` | `other_fees jsonb` NOT NULL default `[]` | `{ name 1–100 ký tự, amount }`, amount được âm |
| `totalAmount` | `totalAmount` | `total_amount numeric` | CHECK `>= 0` và `= round(total_amount)`; domain bảo đảm `= round(rent + Σbreakdown + ΣotherFees)` half-up (`P6-D72`) |
| `status` | `status` | `status invoice_status_enum` default `pending` | `pending \| issued \| void` |
| `issuedAt` | `issuedAt` | `issued_at timestamptz` null | CHECK: `pending` ⇒ NULL, `issued` ⇒ NOT NULL |
| `voidedInvoiceId` | `voidedInvoiceId` | `voided_invoice_id uuid` FK `invoices` null | mới → cũ |
| `voidReason` | `voidReason` | `void_reason text` NULL | `P6-D72`; set khi `void(reason)` (g3 validate 1–500 ký tự) |
| `note` | `note` | `note text` null | ≤ 500 ký tự |

Index: `UQ_invoices_code` (unique), `UQ_invoices_contract_period` **partial unique** `(contract_id, period) WHERE status IN ('pending','issued') AND is_deleted = false`, `IDX_invoices_landlord_period (landlord_id, period)`, `IDX_invoices_building_period (building_id, period)`.

### Ví dụ số (bắt buộc — nguồn: `utility-billing-calculations.md` §5–§8, §11)

Bộ rate dùng chung: **EVN** = `tiered` steps `[0–50:1893, 51–100:1956, 101–200:2283, 201–300:2833, 301–400:2927, 401–∞:3451]` (§12); **nước khoán** `per_head` 80.000; **wifi** `fixed_per_period` 100.000; **QLVH** `per_area_m2` 10.000; **gửi xe** `per_vehicle` 80.000.

| # | Input | Kết quả mong đợi |
|---|---|---|
| 1 | Kỳ `2026-10`, HĐ 01/09/2026–31/08/2027, `rent_price` 3.500.000, 3 member, `area` 18.5. Rate: EVN + nước khoán + wifi + QLVH. Điện 1200→1550 (350 kWh) | ratio 1. Điện **850.400** (`tier_detail`: 94.650 / 97.800 / 228.300 / 283.300 / 146.350). Nước 3 × 80.000 = **240.000**. Wifi **100.000**. QLVH 18.5 × 10.000 = **185.000**. `rentAmount` **3.500.000**. `totalAmount` **4.875.400** |
| 2 | Như #1 nhưng điện 50.5 kWh | Điện = 50 × 1.893 + 0.5 × 1.956 = **95.628** (phần lẻ vượt ngưỡng sang bậc 2, §5.2) |
| 3 | Kỳ `2026-10`, `rent_price` 3.000.000, điện `flat` 4.000 × 183.4 kWh, nước `flat` 25.000 × 6 m³, gửi xe `per_vehicle`, `vehicle_count` 2 | Điện **733.600** (EC5 giữ lẻ). Nước **150.000**. Gửi xe 2 × 80.000 = **160.000**. Tổng **4.043.600** |
| 4 | §8: HĐ 15/09/2026–14/10/2026, `rent_price` 3.000.000, `area` 20, 2 member. Rate: điện `flat` 4.000, nước khoán, wifi, QLVH. Kỳ `2026-09`, điện 40 kWh | ratio 16/30 (`prorate_ratio` hiển thị `"0.533333"`, tính bằng phân số). Phòng **1.600.000**; QLVH 200.000 × 16/30 = **106.666,6667**; wifi **53.333,3333**; điện **160.000**; nước 2 × 80.000 = **160.000** (W2 không prorate, §6.2). `service_start` = `2026-09-15`, `service_end` = `2026-09-30`. Tổng **2.080.000** |
| 5 | Như #4, kỳ `2026-10` (01→14/10), điện 30 kWh | ratio 14/31 (`"0.451613"`). Phòng **1.354.838,7097** (không làm tròn dòng, EC14); QLVH **90.322,5806**; wifi **45.161,2903**; điện **120.000**; nước **160.000**. Σ = 1.770.322,5806 → `totalAmount` **1.770.323** |
| 6 | Điện `flat` 4.001 × 120.5 kWh, nước `flat` 25.000 × 0 m³, `rent_price` 3.000.000 | Điện **482.120,5**; nước **0** (EC12 hợp lệ). Σ = 3.482.120,5 → **3.482.121** (half-up) |
| 7 | #3 + `otherFees` `[{Nệm mới, 250000}, {Giảm trừ hỗ trợ, -700000}]` | Tổng **3.593.600**; `otherFees` giữ nguyên dấu âm |
| 8 | #3 + `otherFees` `[{Giảm trừ, -5000000}]` | Σ = −956.400 → **`TOTAL_NEGATIVE`** (EC17) |
| 9 | `headCount` kỳ `2026-10`: A vào 01/09 chưa rời; B vào 20/10; C rời 30/09; D vào 01/11 | **2** (A, B) — `P6-D65` |
| 10 | Phòng có bộ `room` active {điện `flat` 3.500, nước `flat` 20.000}, tòa có bộ EVN + wifi | Dùng **trọn bộ phòng**, không có dòng wifi (§4). Tắt bộ phòng (`is_active=false`) → dùng bộ tòa |
| 11 | Chặn | thiếu reading nước → `READING_MISSING`; phòng + tòa không có bộ active → `RATE_MISSING`; bộ phòng active chỉ có wifi + QLVH (thiếu mục `electricity`) → `RATE_MISSING` (`P6-D72`, không lấy điện từ bộ tòa); QLVH mà `area` NULL → `AREA_MISSING`; nước khoán mà `headCount` 0 → `HEADCOUNT_ZERO`; gửi xe mà `vehicle_count` NULL → `VEHICLE_COUNT_MISSING`; steps bậc cuối `to=400`, tiêu thụ 450 → `TIER_CONFIG_INVALID` |

> Dòng tiền lẻ vô hạn (16/30, 14/31) lưu ở **4 chữ số thập phân** half-up (`P6-D72`); chỉ `totalAmount` làm tròn về đồng. Vì vậy Σ dòng có thể khác `totalAmount` (#5: 1.770.322,5806 vs 1.770.323) — kiểm `totalAmount = round(Σ dòng)`.

## Tham chiếu code

- Module mẫu để copy pattern: `Tenancy-Service/src/modules/rate-policy/` (aggregate + VO + typeorm entity + mapper + jsonb transformer `ratesTransformer` trong `rate-policy.typeorm-entity.ts`).
- Dùng lại, không viết lại: `RateItem`, `RateKind`, `RateType`, `BillingUnit` (`src/modules/rate-policy/domain/`); `RatePolicyRepository.findByRoom/findByBuilding`; `ReadingPeriod` (`src/modules/meter-reading/domain/value-objects/reading-period.vo.ts`); `MeterReadingEntity.consumption`.
- Unique violation → `src/shared/infrastructure/database/postgres-error-code.ts`.
- **Lưu ý code hiện có:** `ContractEntity.rentPrice` và `Room.area` đang là `number` (`moneyTransformer`, `nullableDecimalTransformer`). Không refactor module contract/room trong task này; đổi sang decimal string ngay tại chỗ calculator nhận input.

## Các bước triển khai

### Bước 1 — Branch, đọc contract, thêm thư viện decimal

- **Cách làm:** tạo branch từ `main`; đối chiếu schema Invoice hiện có với P6-D64/D65/D72; `package.json` chưa có thư viện decimal → thêm `decimal.js` (`P6-D65` cho phép). Không dùng `number` cho tiền ở bất kỳ đâu trong module mới.
- **Kiểm tra bước:** `npm ls decimal.js` có 1 version; `GET http://localhost:3002/api/v1/tenancy/health` → `200`.

### Bước 2 — Domain `Invoice` (aggregate, VO, exception, event)

- **Cách làm:** aggregate với các hành vi: tạo `pending` từ kết quả calculator; `recalculate(result)` (chỉ `pending`, giữ `otherFees`/`note`); `updateExtras(otherFees, note)` (chỉ `pending`); `issue(now)` (`pending` → `issued`, set `issuedAt`); `void(reason)` (`pending`/`issued` → `void`, lưu `voidReason`). Mỗi dòng (`rentAmount`, `breakdown[].amount`) làm tròn half-up 4 chữ số; mọi thay đổi tính lại `totalAmount = roundHalfUp(rent + Σbreakdown + ΣotherFees)` về đồng; < 0 → `422 TOTAL_NEGATIVE`. VO mã hóa đơn sinh `INV-YYYYMM-` + 4 ký tự `[A-Z0-9]`. Exception: `404 INVOICE_NOT_FOUND`, `409 INVOICE_ALREADY_ISSUED` (sửa khi không pending), `409 INVOICE_NOT_PENDING` (phát hành), `409 INVOICE_ALREADY_VOIDED`, `422 TOTAL_NEGATIVE`. Event: `invoice.generated`, `invoice.recalculated`, `invoice.updated`, `invoice.issued`, `invoice.voided`. Repository interface: `save`, `findById`, `findByIdForUpdate`, `findOpenByContractPeriod` (pending/issued), `findLatestVoidByContractPeriod`.
- **Kiểm tra bước:** `npm run build` pass; chạy dependency-rule check trong `CLAUDE.md` → không in gì.

### Bước 3 — Calculator thuần

- **Cách làm:** một domain service **không inject gì, không I/O**. Input: `period`, contract `{ startDate, endDate, rentPrice, vehicleCount }`, room `{ area }`, `headCount`, `roomPolicy?`, `buildingPolicy?`, `readings { electricity?, water? }`. Thứ tự: thiếu reading (EC2) → resolve rate §4 (EC3; bộ được chọn thiếu mục `electricity`/`water` → `RATE_MISSING`) → điện E1/E2 → nước W1–W3 → phí F1–F4 (EC6/7/8) → prorate §8 cho tiền phòng + F1–F4 → snapshot `breakdown` §9. Trả **mã chặn đầu tiên** theo thứ tự trên. `tier_detail` mỗi bậc: `step, from, to, price, quantity, amount`. Hàm `headCount` không ở đây (port của g2).
- **Kiểm tra bước:** viết script tạm ngoài repo (không commit) gọi calculator với input dòng #1, #4, #5 → in đúng 4.875.400 / 2.080.000 / 1.770.323: `npx ts-node -r tsconfig-paths/register <scratch>/calc-check.ts`.

### Bước 4 — Persistence + migration

- **Cách làm:** typeorm entity + mapper + repository theo Mapping field; enum `invoice_status_enum`; FK `contract_id`, `room_id`, `building_id`, `voided_invoice_id`; cột `void_reason text NULL`; tiền dòng `numeric(14,4)`; index/CHECK như mục Contract. `npm run migration:generate -- name=CreateInvoicesTable`, chỉ giữ phần `invoices`.
- **Kiểm tra bước:** `migration:run` → `migration:revert` → `migration:run` pass. SQL: insert 2 row `pending` cùng `(contract_id, period)` → lỗi `UQ_invoices_contract_period`; đổi row 1 sang `void` rồi insert lại → thành công; `UPDATE invoices SET total_amount = 10.5` → vi phạm CHECK; `\d invoices` có `void_reason`.

### Bước 5 — Chạy đủ bảng Ví dụ số

- **Kiểm tra bước:** mở rộng script bước 3 cho cả 11 dòng; dán output vào PR. Dòng #8, #11 phải ra đúng `reasonCode`, không ném lỗi khác.

## Ngoài phạm vi

- Endpoint (g2 generate, g3 landlord, g4 tenant). Đếm `headCount` từ DB (g2, port từ P6-01e1).
- Payment / trạng thái "đã thu" (`P6-D61`); `due_date`, `overdue` (`P1-D39`).
- Unit test file (quy ước team: không viết test; xác minh bằng script + bảng Ví dụ số).

## Blocker

- Không có. (Độ chính xác dòng, thiếu mục điện/nước, `void_reason` đã chốt ở `P6-D72`.)

## Cập nhật `api-docs` (bắt buộc trước khi đóng issue)

- [ ] Schema `Invoice` khớp entity theo P6-D64/D72: tiền là string, `serviceStart/serviceEnd` là `date`, có `voidReason`, không có `vietQrContent`; mọi sai lệch được ghi để đồng bộ trong PR API liên quan.

## Acceptance

- [ ] 11 dòng Ví dụ số ra đúng kết quả (output script trong PR); mọi hóa đơn thỏa `totalAmount = round(Σ dòng)`.
- [ ] Bảng `invoices` có `void_reason`; tiền dòng lưu 4 chữ số thập phân.
- [ ] Partial unique cho phép tạo lại sau `void`; `code` trùng bị chặn.
- [ ] Calculator không import NestJS/TypeORM/repository (dependency-rule check sạch).

## Definition of Done

- [ ] Mọi bước qua phần Kiểm tra bước; mọi ô Acceptance được **tick bởi người làm**.
- [ ] `npm run build` + `npm run lint` pass; không có file test, không sửa `src/shared`.
- [ ] Migration sinh bằng `migration:generate`, `migration:run` + `migration:revert` pass từ DB trống.
- [ ] PR vào `main` ghi `Closes pbl6-home-renter/docs#<số issue>`, baoduong17 approve.
