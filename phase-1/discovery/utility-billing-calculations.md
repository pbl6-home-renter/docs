# Utility & Fee Billing Calculations — Hướng dẫn tính toán trong code

> **Status:** 🟢 REFERENCE (tham chiếu từ `database-design_v3.md` §2.8 → §2.11).
> **Nguồn:** `database-design_v3.md` (Schema), `business-rules.md` §3/§4 (D16, D22), `discovery/decisions.md` (D30, D31, D32, D33), thực tế thị trường VN.
> **Mục đích:** liệt kê **100% case** tính tiền điện/nước/phí định kỳ + hướng dẫn code từng bước. Backend (NestJS / `decimal`) dùng file này làm spec cho dịch vụ `InvoiceService`.

---

## 0. Quy ước chung (áp dụng MỌI case)

| Quy ước | Giá trị |
|---|---|
| Kiểu số | `decimal` (PostgreSQL numeric / BigDecimal trong code). **Cấm float/double** cho tiền và chỉ số. |
| Kỳ (`period`) | `YYYY-MM` theo tháng dương lịch. Đơn giá & phí áp dụng theo **ngày hiệu lực**, không theo thời điểm nhập. |
| Chuỗi ưu tiên | Đơn giá: `Room.elec_policy_id → Building.elec_policy_id → LandlordProfile.elec_policy_id` (nước tương tự). Phí định kỳ: scope room → building → landlord (fee landlord/tòa áp cho từng phòng). |
| Block khi thiếu dữ kiện | Nếu thiếu reading/policy/phí nền tảng → **không tạo hóa đơn**, trả lỗi cụ thể (mục 11). |

---

## 1. Ma trận toàn bộ case

### 1.1 Đơn giá điện/nước — `UtilityRatePolicy.rate_kind`

| # | rate_kind | Loại | Đầu vào | Công thức | Thực tế VN |
|---|---|---|---|---|---|
| E1 | `flat` | Electricity | consumption (kWh) | `consumption × unit_price` | Đồng giá 3.500–4.500đ/kWh |
| E2 | `tiered` | Electricity | consumption (kWh) | cộng dồn theo `steps` | EVN bậc thang 6 bậc; bậc 3 TT 25/2018 |
| W1 | `flat` | Water | consumption (m³) | `consumption × unit_price` | 20.000–35.000đ/m³ |
| W2 | `per_head` | Water | head_count | `head_count × unit_price` | **Phổ biến**: 70.000–120.000đ/người/tháng |
| W3 | `tiered` | Water | consumption (m³) | cộng dồn theo `steps` | Bậc thang theo định mức nhân khẩu (chung cư) |

> **D33 — điện KHÔNG có `per_head`:** `rate_kind` điện chỉ `flat` | `tiered` (thu theo công tơ/kWh); `per_head` (khoán đầu người) chỉ áp cho **nước** (W2) và **phí định kỳ** (F2). Validate ở service layer, không đổi enum DB.

### 1.2 Phí định kỳ — `RecurringFee.fee_kind`

| # | fee_kind | Loại đầu vào | Công thức | Thực tế VN |
|---|---|---|---|---|
| F1 | `fixed_per_period` | — (1) | `unit_price × prorate_ratio` | Wifi 50–150k/phòng, vệ sinh/rác 30–80k/phòng |
| F2 | `per_head` | head_count | `unit_price × head_count × prorate_ratio` | Phí DV chung 150–300k/người |
| F3 | `per_area_m2` | room.area_m2 | `unit_price × area_m2 × prorate_ratio` | Phí QLVH chung cư 5–20k/m² |
| F4 | `per_vehicle` | vehicle_count (từ `Contract.vehicle_count`, kê khai lúc tạo/cập nhật HĐ **D32**) | `unit_price × vehicle_count × prorate_ratio` | Gửi xe máy 70–200k/xe, ô tô 1–2,5tr/xe |

> `prorate_ratio = 1` cho tháng trọn; nếu HĐ bắt đầu/kết thúc giữa tháng → công thức mục 8.

---

## 2. Authentication

Mỗi hóa đơn chạy qua chuỗi **8 bước** (mục 2–9). Bản ghi hóa đơn luôn ghi nhận **đầu vào đã dùng** (snapshot) để không phụ thuộc cấu hình hiện hành về sau.

## 3. Bước 0 — Gom dữ liệu đầu vào (per contract × period)

```
inputs = {
  contractId, room, building, landlordProfile,
  period,                                 // YYYY-MM
  elecReading, waterReading,              // MeterReading theo utility_type (bắt buộc đủ 2)
  headCount,                              // số ContractMember active tại kỳ (kể cả tenant passive user_id=NULL, D29)
  areaM2 = room.area_m2,
  vehicleCount = contract.vehicle_count,  // kê khai lúc tạo/cập nhật HĐ (D32); NULL = chưa khai → block EC8
  contractDaysInPeriod                    // tính từ Contract.start_date/end_date vs đầu/cuối period
}
```

- `headCount = COUNT(contract_member WHERE contract_id=? AND deleted_at IS NULL)` — đếm **ngay tại kỳ lập hóa đơn** (không lọc theo thời điểm vào/ra từng người; việc chia nội bộ cho các thành viên trong phòng do tenant tự lo — D22). **D33:** `headCount` chỉ dùng cho **nước W2 `per_head`** và **phí F2 `per_head`** — điện không dùng (luôn theo kWh).
- Điện & nước phải **đủ cả 2** bản ghi `MeterReading` của kỳ. Thiếu 1 → **block** (mục 11.2).

## 4. Bước 1 — Resolve đơn giá (policy chain)

```
function resolvePolicy(elecOrWater, room, building, landlordProfile, period):
  candidates = [
    room[elecOrWater + "_policy_id"],
    building[elecOrWater + "_policy_id"],
    landlordProfile[elecOrWater + "_policy_id"],
  ]
  for policyId in candidates:
    if policyId == null: continue                      // kế thừa
    p = load(UtilityRatePolicy, policyId)
    if not (p.is_active): continue                     // bị tắt → kế thừa lên trên
    if period < p.effective_from: continue             // chưa có hiệu lực
    if p.effective_to != null and period > p.effective_to: continue // hết hạn
    return p
  return null                                          // → BLOCK (11.3)
```

- **1 policy/kỳ:** nếu landlord đổi giá giữa tháng → áp dụng từ **kỳ sau**, không chia đôi trong 1 kỳ (kéo dài hoặc cấu hình `effective_to` của policy cũ rồi tạo policy mới `effective_from` = kỳ sau).
- `effective_to` (date) = hạn cuối NGÀY, so với `period` theo tháng: `p.effective_to >= ngày cuối tháng period` thì coi còn hiệu lực cho cả kỳ.

## 5. Bước 2 — Tính điện (E1–E2)

```
function calcElectricity(policy, consumption):
  switch policy.rate_kind:
    case "flat":    return consumption * policy.unit_price
    case "tiered":  return calcTiered(policy.steps, consumption)
```

### 5.1 E1 `flat` — đồng giá
- VD: 180 kWh × 4.000đ = **720.000đ**.

### 5.2 E2 `tiered` — EVN bậc thang 6 bậc
`steps = [{from, to, price}]`, `to` nullable = mở ∞. Khoảng đóng-đóng bậc dưới, bậc sau bắt đầu `from = bậc trước.to + 1`.

```
function calcTiered(steps, consumption):
  remaining = consumption; total = 0
  for step in steps (order by from):
    if remaining <= 0: break
    qtyInStep = (step.to == null) ? remaining
              : min(remaining, step.to - step.from + 1)
    total += qtyInStep * step.price
    remaining -= qtyInStep
  if remaining > 0 and last step has to != null: throw "không đủ bậc"   // cấu hình sai
  return total
```

**VD: 350 kWh** (giá tham khảo QĐ 2941/QĐ-BCT, hiệu lực từ 11/10/2024 — **giá là config/seed, không hard-code**):

| Bậc | kWh | Đơn giá | Tiền |
|---|---|---|---|
| 1 (0–50) | 50 | 1.893 | 94.650 |
| 2 (51–100) | 50 | 1.956 | 97.800 |
| 3 (101–200) | 100 | 2.283 | 228.300 |
| 4 (201–300) | 100 | 2.833 | 283.300 |
| 5 (301–400) | 50 | 2.927 | 146.350 |
| **Tổng** | 350 | | **850.400đ** |

### 5.3 E2′ Bậc 3 TT 25/2018 (sub-meter, HĐ < 12 tháng / không kê khai đủ nhân khẩu)
- Luật: điện lực tính **toàn bộ sản lượng theo bậc 3** cho đối tượng cho thuê không kê khai. 
- **2 cách cấu hình (tương đương):**
  1. `rate_kind='flat'`, `unit_price = giá bậc 3 (2.283đ/kWh)`;
  2. `rate_kind='tiered'`, `steps = [{from:0, to:null, price:2283}]`.
- App cung cấp **preset** (seed) có tên "Bậc 3 TT25/2018" — chủ trọ chọn khỏi nhập tay. VD 180 kWh × 2.283 = **410.940đ**.
- Ghi chú pháp lý: 4 người = 1 hộ (mục 12) thường đi kèm công tơ tổng → ngoài MVP (Phase 1+); bản thân policy này đủ cho chủ trọ thu đúng.

## 6. Bước 3 — Tính nước (W1–W3)

### 6.1 W1 `flat` theo m³
- VD: 6 m³ × 25.000đ = **150.000đ**.

### 6.2 W2 `per_head` — khoán đầu người (PHỐ BIẾN)
- VD: 3 người × 80.000đ = **240.000đ**.
- headCount = mục 3 (snapshot tại kỳ, không prorate theo ngày vào/ra từng người).

### 6.3 W3 `tiered` theo m³
- Dùng khi bậc thang theo **tổng lượng m³** (hoặc theo khung định mức từng vùng cấp nước).
- Cùng hàm `calcTiered` mục 5.2. VD: `steps=[{0–10:12000},{11–20:16000},{21–30:20000},{31–null:25000}]`; 25 m³ = 10×12.000 + 10×16.000 + 5×20.000 = 120.000 + 160.000 + 100.000 = **380.000đ**.
- **Trường hợp định mức theo nhân khẩu (chung cư đã đăng ký tạm trú/nhân khẩu):** quota = `headCount × m³/người/tháng` → cấu hình `effective_from` theo tháng đăng ký; **chưa đăng ký** → policy giá cao (hoặc giá kinh doanh) thay thế policy ưu đãi. MVP không tự "đăng ký" — chủ trọ chọn đúng policy theo hiện trạng phòng.

## 7. Bước 4 — Tính phí định kỳ (F1–F4)

```
function calcFee(fee, inputs, prorateRatio):
  switch fee.fee_kind:
    case "fixed_per_period": return fee.unit_price * prorateRatio
    case "per_head":         return fee.unit_price * inputs.headCount * prorateRatio
    case "per_area_m2":      return fee.unit_price * inputs.areaM2 * prorateRatio
    case "per_vehicle":      return fee.unit_price * inputs.vehicleCount * prorateRatio
```

- **Fee scope `landlord` (D30, mặc định)** áp cho **từng phòng ở mọi tòa** của chủ trọ (trừ khi bị override ở tòa/phòng). VD "Wifi 100k mặc định cả nhà".
- **Fee scope `building`** áp cho **từng phòng trong tòa** (mỗi phòng trong tòa đều phát sinh 1 dòng). Ví dụ "Wifi chung tòa 100k/phòng" → mỗi phòng +100.000đ.
- **Fee scope `room`** chỉ áp cho phòng đó.
- Thứ tự ưu tiên khi trùng (một phòng có thể nhận từ 3 cấp): `room > building > landlord` — lấy cấp sâu nhất; `is_active=false` hoặc hết hiệu lực ở cấp nào thì bỏ qua cấp đó và kế thừa cấp trên.
- `is_active` mặc định `true` (bản mới tạo đang chạy); mọi `RecurringFee` **đều thu qua hóa đơn app** (bỏ `charged_in_invoice` — D36).
- Chỉ lấy fee có `is_active` và hiệu lực trong kỳ (giống mục 4).
- **Block (11.6):** `per_area_m2` mà `room.area_m2 IS NULL`; `per_vehicle` thiếu `vehicleCount`; `per_head` mà `headCount = 0`.

## 8. Bước 5 — Prorate tháng đầu / cuối (HĐ vào/ra giữa tháng)

```
function prorateRatio(contract, period):
  pStart = first day of period; pEnd = last day of period
  cStart = contract.start_date; cEnd = contract.end_date
  if cStart > pEnd or cEnd < pStart: return 0            // HĐ không nằm trong kỳ
  activeStart = max(pStart, cStart)
  activeEnd   = min(pEnd, cEnd)
  return (activeEnd - activeStart + 1) / daysInMonth(period)
```

- Áp cho **tiền phòng** (`monthly_rent × ratio`) và **phí định kỳ (F1–F4)**.
- **Điện/nước KHÔNG prorate theo công thức trên** — dùng lượng tiêu thụ thực từ `MeterReading` (kỳ đầu: baseline đọc tại ngày dọn vào; kỳ cuối: đọc tại ngày trả phòng → consumption thực). Tiền phòng prorate riêng, điện/nước theo số thực.
- **VD:** HĐ 15/09–14/10, `monthly_rent = 3.000.000`, phòng 20m², phí QLVH 10.000đ/m², wifi 100.000đ.
  - Tháng 09: ratio(15→30/09) = 16/30 = 0.5333. Phòng = 1.600.000đ; QLVH = 10.000×20×0.5333 = 106.660đ → làm tròn tổng sau.
  - Tháng 10: ratio(01→14/10) = 14/31 = 0.4516. Phòng = 1.354.839đ.
  - Điện/nước tháng 09: chốt từ baseline 15/09 → theo số thực.

## 9. Bước 6 — Gộp tiền & snapshot bất biến

```
elecAmount = calcElectricity(elecPolicy, elecConsumption, headCount)
waterAmount = calcWater(waterPolicy, waterConsumption, headCount)
feeLines   = fees.map(f => { feeId:f.id, name:f.name, kind:f.fee_kind,
                             quantity:qtyOf(f), unitPrice:f.unit_price, amount:calcFee(f), prorateRatio })
otherFees  = input("phí khác / giảm trừ", period, prompt="preset gợi ý + gõ tự do")   // D32: phí 1 lần (nệm mới, sửa thiết bị); D33: amount ÂM = giảm trừ/miễn giảm
rawTotal   = rentProrated + elecAmount + waterAmount + sum(feeLines.amount) + sum(otherFees.amount)
if rawTotal < 0: throw TOTAL_NEGATIVE (EC17)
totalAmount = roundMoney(rawTotal)
```

- **`utility_breakdown` (snapshot jsonb)**:
```json
{
  "electricity": {
    "policy_snapshot": {"id":"<uuid>", "name":"EVN bậc thang", "rate_kind":"tiered",
                        "unit_price":null, "steps":[{"from":1,"to":50,"price":1893}, ...]},
    "previous_reading":1200, "current_reading":1380, "qty_kwh":180,
    "tier_result":[{"from":1,"to":50,"qty":50,"price":1893,"amount":94650}, ...],
    "amount":850400, "head_count":null
  },
  "water": {
    "policy_snapshot": {"id":"<uuid>", "name":"Nước khoán", "rate_kind":"per_head", "unit_price":80000},
    "head_count":3, "amount":240000
  }
}
```
- **`fees_breakdown` (snapshot jsonb)**:
```json
[{"fee_id":"<uuid>","name":"Wifi","fee_kind":"fixed_per_period","quantity":1,
  "unit_price":100000,"prorate_ratio":1,"amount":100000},
 {"fee_id":"<uuid>","name":"QLVH","fee_kind":"per_area_m2","quantity":18.5,
  "unit_price":10000,"prorate_ratio":1,"amount":185000}]
```
- **`other_fees` (snapshot jsonb, phí 1 lần D32; **D33 — amount ÂM = giảm trừ/miễn giảm**)**:
```json
[{"name":"Nệm mới","amount":250000},
 {"name":"Sửa bật lửa bếp","amount":50000},
 {"name":"Giảm trừ hỗ trợ","amount":-700000}]
```
- **Bất biến D33:** `rent_amount + Σ(utility_breakdown.amount) + Σ(fees_breakdown.amount) + Σ(other_fees.amount) == total_amount` giữ nguyên với `other_fees` âm (snapshot giữ dấu âm); **block nếu `total_amount < 0`** (EC17). Sau khi `status != pending` (đã phát hành), không sửa. Sai → `void` + hóa đơn mới (`voided_invoice_id`), giữ bản cũ. Chỉ `rent_amount` + `total_amount` là cột denormalized cho dashboard D20 (D37); điện/nước/phí đọc từ snapshot jsonb (nguồn duy nhất, không cột kép).

## 10. Pseudocode luồng lập hóa đơn (TỪNG PHÒNG — D33②)

> **D33② Trigger:** hàm này được gọi **tự động cho từng phòng** ngay khi phòng đó đủ (a) 2 `MeterReading` kỳ hiện tại VÀ (b) policy/phí resolve không lỗi. Không batch toàn kỳ. Landlord không cần nhập tay — danh sách "phòng chốt số xong" hiển thị để rà soát trước khi phát hành.

```
def generateInvoice(contractId, period):
  contract = load(contractId); room = contract.room; building = room.building
  elecReading = MeterReading.find(room.id, "electricity", period)   # null → BLOCK (11.2)
  waterReading = MeterReading.find(room.id, "water", period)
  elecPolicy = resolvePolicy("elec", room, building, landlordProfile)      # null → BLOCK (11.3)
  waterPolicy = resolvePolicy("water", room, building, landlordProfile)
  if existing invoice (contractId, period, status != void): return duplicate error (11.7)   # D33① partial unique
headCount = countContractMembers(contract, period)
  vehicleCount = contract.vehicle_count                # D32: kê khai lúc tạo/cập nhật HĐ (EC8 nếu NULL)
  prorate = prorateRatio(contract, period)
  elec = calcElectricity(elecPolicy, elecReading.consumption)          # D33④ điện không dùng headCount
  water = calcWater(waterPolicy, waterReading.consumption, headCount)  # nước per_head dùng headCount
  fees = activeRecurringFees(room, building, landlordProfile, period).map(...)   # BLOCK nếu thiếu nền tảng (11.6) — room > building > landlord
  otherFees = promptOtherFees()                        # D32: phí 1 lần; D33: amount âm = giảm trừ
  rentProrated = roundMoney(contract.monthly_rent * prorate)
  total = roundMoney(rentProrated + elec.amount + water.amount + feesSum + otherFeesSum)
  if total < 0: throw TOTAL_NEGATIVE (EC17)
  invoice = Invoices.create({ ..., utility_breakdown, fees_breakdown, other_fees, total_amount: total })
  return invoice   # status=pending
```

## 11. Edge cases & blocking — toàn bộ

| # | Tình huống | Hành vi | Mã lỗi gợi ý |
|---|---|---|---|
| EC1 | `current_reading < previous_reading` (đồng hồ reset/thay) | **Block**, bắt sửa. Nếu thay đồng hồ thật → tạo `MeterReading` baseline mới (`is_baseline=true`, `previous_reading=0`) đọc lại qua **OCR; OCR sai/mờ → hiệu chỉnh tay số thực tế (D35)** rồi tính từ đó | `METER_REVERSED` |
| EC2 | Thiếu `MeterReading` điện HOẶC nước của kỳ | Block hóa đơn | `READING_MISSING` |
| EC3 | Không resolve được rate policy (3 cấp đều null/tắt/hết hạn) | Block, hiển thị "thiếu cấu hình đơn giá" | `RATE_MISSING` |
| EC4 | Policy chỉ hiệu lực nửa kỳ (đổi giá giữa tháng) | Áp dụng policy hiệu lực tại **đầu kỳ**; thay đổi có hiệu lực từ kỳ sau | — |
| EC5 | Consumption lẻ (vd 183.4 kWh) | Tính với decimal, không làm tròn lượng | — |
| EC6 | `per_area_m2` mà `area_m2` NULL | Block kỳ đó, yêu cầu nhập diện tích phòng | `AREA_MISSING` |
| EC7 | `per_head` mà `headCount = 0` | Block, yêu cầu thêm thành viên HĐ (D29: passive vẫn phải khai tên/SĐT) | `HEADCOUNT_ZERO` |
| EC8 | `per_vehicle` mà `contract.vehicle_count` NULL (chưa kê khai xe khi tạo/cập nhật HĐ) | Block, hiển thị ô nhập số xe trên HĐ | `VEHICLE_COUNT_MISSING` |
| EC9 | Hóa đơn đã tồn tại (contract, period, `status != 'void'`) | Chặn tạo trùng; **partial unique D33①** `(contract_id, period) WHERE status != 'void'` — chỉ tạo được hóa đơn thay thế sau khi void bản cũ | `INVOICE_DUPLICATE` |
| EC10 | Prorate tháng đầu/cuối, `ratio=0` (HĐ ngoài kỳ) | Không phát hành hóa đơn cho kỳ đó | — |
| EC11 | Fee `building` áp nhiều phòng | Tạo dòng fee riêng cho **từng phòng** | — |
| EC12 | `consumption` = 0 | Hợp lệ → amount = 0, vẫn lập hóa đơn (điện/nước bậc 1 tối thiểu nếu luật/phí duy trì không nằm trong app) | — |
| EC13 | Policy `steps` thiếu bậc ∞ ở cuối | Block khi tính (chê cấu hình sai), không tự bịa giá | `TIER_CONFIG_INVALID` |
| EC14 | Làm tròn mỗi dòng trước khi cộng | **Không** — chỉ làm tròn tổng; snapshot lưu số chính xác (VD 1.354.839đ vẫn đủ) | — |
| EC15 | Thanh toán một phần (Payment success < total_amount) | `Invoice.status = 'partially_paid'` (D33③) — hiển thị "đã thu X / còn nợ Y"; `paid` chỉ khi Σ success ≥ total; `overdue` khi quá hạn còn thiếu | — |
| EC16 | Webhook thanh toán tới hóa đơn đã `void` | KHÔNG set `paid`; ghi nhận Payment + cờ **cảnh báo chủ trọ đối soát** (D33⑤) | `INVOICE_VOIDED` |
| EC17 | `total_amount < 0` (do `other_fees` âm vượt tổng) | Block tạo hóa đơn (D33⑥) — giảm trừ không được làm hóa đơn âm | `TOTAL_NEGATIVE` |

## 12. Ghi chú luật pháp & preset gợi ý (tham khảo — giá là CONFIG, không hard-code)

| Preset | Chế độ | Giá |
|---|---|---|
| Đồng giá phòng trọ | `flat` | 3.500–4.500 đ/kWh (chủ trọ tự set) |
| EVN hộ gia đình 6 bậc | `tiered` | 1.893 / 1.956 / 2.283 / 2.833 / 2.927 / 3.451 (QĐ 2941/QĐ-BCT, 11/10/2024) |
| Bậc 3 TT 25/2018 | `flat` (2.283) hoặc `tiered` 1 bậc | áp khi HĐ < 12 tháng hoặc không kê khai đủ nhân khẩu |
| Nước khoán đầu người | `per_head` | 70.000–120.000 đ/người/tháng |
| Nước theo m³ | `flat` | 20.000–35.000 đ/m³ |
| Nước bậc theo định mức | `tiered` | tùy Công ty Cấp nước địa phương |

- **4 người = 1 hộ gia đình** (đăng ký tạm trú, HĐ ≥ 12 tháng): chủ trọ đăng ký định mức với Điện lực để tòa được tính bậc thang hộ; app **không** tự nộp/đăng ký (D17 — Phase 1+), chỉ hỗ trợ cấu hình policy đúng.
- **Nước chung cư:** đăng ký nhân khẩu với BQL/công ty cấp nước để dùng bậc ưu đãi; chưa đăng ký → giá bậc cao/kinh doanh. Chủ trọ/tenant chọn đúng policy theo hiện trạng.
- **D31 — bậc thang `steps` chỉ đến từ preset bảng trên, không bao giờ nhập tay trong UI thường** (EVN 6 bậc / Bậc 3 TT 25/2018 / nước địa phương). Landlord nhập tay tối đa 1 con số cho `flat`/`per_head`; đổi giá = tạo policy mới `effective_from`. Preset là seed config (đổi khi có QĐ mới chỉ thay seed, không deploy code).
- **D32 — preset phí định kỳ (seed, đồng hành D31):** Module 6 tab Phí định kỳ cho chọn preset mẫu **Wifi / Quản lý vận hành / Gửi xe / Vệ sinh rác / Phí tự nhập** — chọn preset = auto điền `fee_kind` + `unit_price` (vd Wifi: `fixed_per_period` 100.000đ, QLVH: `per_area_m2` 10.000đ/m², Gửi xe: `per_vehicle` 80.000đ, Vệ sinh: `fixed_per_period` 50.000đ), chủ trọ xác nhận hoặc chỉnh số rồi chọn phạm vi + `effective_from`. Không hard-code: preset là seed, vẫn cho nhập tay bất kỳ phí nào.
- **D32 — `vehicle_count` kê khai tại Hợp đồng** (không nhập mỗi kỳ): khai lúc tạo/cập nhật HĐ (xem `landlord_user_flow.md` §5), lấy `contract.vehicle_count` khi lập hóa đơn F4, snapshot vào `fees_breakdown`. Đổi số xe giữa kỳ → cập nhật HĐ, áp dụng từ kỳ sau.
- **D33 — Điện KHÔNG có preset/rate `per_head`** (chỉ `flat` EVN/1 số cố định + `tiered` EVN 6 bậc & Bậc 3 TT 25/2018); nước giữ cả `per_head` (khoán đầu người) / theo m³ / bậc. `other_fees` cho nhập **âm** (giảm trừ), block tổng âm (EC17). Thanh toán một phần dùng `Invoice.status='partially_paid'`; thu dư/thiếu → nhắc khi mở tab History (EC15–EC16).

---

## 13. Ranh giới MVP (không nằm trong file này ở Phase hiện tại)

- **Công tơ tổng / chia tỷ lệ** (master meter) → Phase 1+ (chủ trọ vẫn chốt sub-meter từng phòng, hao hụt gộp vào đơn giá flat).
- **Đăng ký xe / VehicleRegister** → số xe nhập tay mỗi kỳ (F4), snapshot vào `fees_breakdown`.
- **Bậc thang theo quota nhân khẩu tự tính** → chỉ hỗ trợ qua cấu hình `steps` + `effective_from`.
- **Nộp/tờ khai tạm trú điện tử** → D17, Phase 1+.