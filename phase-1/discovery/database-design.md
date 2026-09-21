# Thiết kế Cơ sở dữ liệu & Phân quyền theo Role

## 2. Danh sách Entity

> **Quy ước cột `Validation`:** chỉ ghi validate có giá trị xác định như `Min length`, `Max length`, `Regex` hoặc điều kiện số; không có thì để trống.

### 2.0 Base Entity (quy ước áp dụng cho mọi bảng bên dưới)

| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| id | uuid | PK, default `gen_random_uuid()` | | | |
| created_at | timestamptz | NOT NULL, default `now()` | | | `2026-09-05T10:00:00Z` |
| updated_at | timestamptz | NOT NULL, default `now()` | tự cập nhật bằng trigger `set_updated_at()` mỗi lần `UPDATE` | | `2026-09-05T10:00:00Z` |
| is_deleted | boolean | NOT NULL, default false | Soft-delete: `false` = existing record; default queries use `WHERE is_deleted = false`. Financial/audit records are retained; cancelling an invoice changes its status, not this flag. | | `false` |

### 2.1 User
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| phone | varchar(12) | UNIQUE, NOT NULL | định danh chính (VN) | Min length: 10; Max length: 12; Regex: `^0[0-9]{9}$` hoặc `^\+84[0-9]{9}$` | `0901234567` |
| email | varchar | UNIQUE, NOT NULL | | Min length: 5; Max length: 254; Regex: `^[^\s@]+@[^\s@]+\.[^\s@]+$` | `lan@example.com` |
| password_hash | varchar | NOT NULL | | Min length: 60; Max length: 255 | `$2a$10$N9qo8uLOickgx2ZMRZoMye…` |
| full_name | varchar | NOT NULL | | Min length: 1; Max length: 254 | `Lê Văn An` |
| role | enum (`landlord`,`tenant`,`admin`) | NOT NULL | User flow SoT: một tài khoản có đúng một role bất biến; role khác dùng tài khoản riêng | | `landlord` |
| user_status | enum (`active`,`locked`) | NOT NULL default `active` | Tenant bị khóa vẫn được xem/thanh toán HĐ hiện tại ở tầng quyền; landlord bị khóa không đăng nhập được portal | | `active` |
| lock_reason | varchar | nullable | lý do admin khóa tài khoản | Min length: 1; Max length: 500 | `Spam listing` |
| locked_at | timestamptz | nullable | | | `NULL` |

### 2.2 FavoriteRoom (phòng đã lưu)
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| user_id | uuid | FK→User, NOT NULL | tenant lưu phòng cần đăng nhập | | |
| room_id | uuid | FK→Room, NOT NULL | | | |

**Index:** UNIQUE `(user_id, room_id)` khi `deleted_at IS NULL`.

### 2.3 LandlordProfile
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| user_id | uuid | FK→User, UNIQUE, NOT NULL | 1-1, chỉ tồn tại nếu user có role landlord | | |
> Cấu hình hạn thanh toán/nhắc nợ không lưu trong JSON: dùng `BillingSetting` (§2.11) để kế thừa theo profile → building → room.

### 2.4 Building
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| landlord_id | uuid | FK→User, NOT NULL | landlord sở hữu | | |
| name | varchar | NOT NULL | | Min length: 1; Max length: 254 | `Nhà trọ Thanh Xuân` |
| province | varchar | NOT NULL | tên Tỉnh/TP từ dropdown VN | Min length: 1; Max length: 100 | `Thành phố Hồ Chí Minh` |
| ward | varchar | NOT NULL | tên Phường/Xã từ dropdown VN | Min length: 1; Max length: 100 | `Phường Bến Nghé` |
| address | varchar | NOT NULL | địa chỉ chi tiết (số nhà, đường) | Min length: 1; Max length: 254 | `12 Nguyễn Trãi` |
| latitude | decimal(9,6) | nullable | tự geocode từ address khi tạo building | `>= -90; <= 90` | `20.995100` |
| longitude | decimal(9,6) | nullable | tự geocode từ address khi tạo building | `>= -180; <= 180` | `105.816649` |
| electricity_policy_id | uuid | FK→RatePolicy, nullable | **D30** — policy cấp tòa thắng; NULL = kế thừa LandlordProfile | | `NULL` (kế thừa landlord) |
| water_policy_id | uuid | FK→RatePolicy, nullable | **D30** | | `NULL` (kế thừa landlord) |
| building_status | enum (`pending`,`approved`,`rejected`) | NOT NULL default `pending` | chỉ BĐS `approved` mới tạo phòng, phát hành HĐ và hiển thị công khai | | `pending` |
| reviewed_by | uuid | FK→User, nullable | admin duyệt/từ chối | | |
| reviewed_at | timestamptz | nullable | | | |
| note | text | nullable | bắt buộc khi `status='rejected'` | Min length: 1; Max length: 500 | `Ảnh giấy tờ mờ` |

> Ảnh tòa nhà (bìa + gallery) và giấy tờ sở hữu bắt buộc: `Media(owner_type='building', purpose='cover_photo'|'gallery_photo'|'ownership_proof')`.

### 2.5 Room
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| building_id | uuid | FK→Building, NOT NULL | | | |
| floor_number | int | nullable | tầng (1-based) | `> 0` | `2` |
| landlord_id | uuid | FK→User, **NOT NULL** | **D25 — bắt buộc, 1 chủ/phòng** | | |
| name | varchar | NOT NULL | | Min length: 1; Max length: 254 | `P.201` |
| description | text | nullable | **D21** | Min length: 1; Max length: 500 | `Phòng trọ hiện đại, tiện nghi đầy đủ` |
| area | decimal | nullable | Area in m²; used by `per_area_m2` fees | `>0` | `18.5` |
| amenities | jsonb | NOT NULL | | {} | `{"aircon":true,"fridge":false,"wc_inside":true}` |
| max_occupancy | int | nullable | **D21** hard filter ghép bạn | `> 0`| `3` |
| gender_policy | enum (`any`,`male`,`female`) | default `any` | **D21** — `male` = male tenants only; `female` = female tenants only; `any` = no gender restriction | | `any` |
| rent_price | decimal | NOT NULL | | `>=0`| `3500000` |
| electricity_policy_id | uuid | FK→RatePolicy, nullable | **D30** — NULL = kế thừa tòa → landlord | | `NULL` |
| water_policy_id | uuid | FK→RatePolicy, nullable | **D30** | | `override riêng phòng` |
| room_status | enum (`available`,`occupied`,`maintenance`) | cached/derived | `occupied` khi có HĐ active; | | `occupied` |

> Ảnh phòng (bìa + gallery): `Media(owner_type='room', purpose='cover_photo'|'gallery_photo')`.

### 2.7 Contract
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| room_id | uuid | FK→Room, NOT NULL | | | |
| landlord_id | uuid | FK→User, NOT NULL | | | |
| tenant_id | uuid | FK→User, **nullable** | nullable để hỗ trợ tenant chưa có account (**D29**); nếu null thì lưu tên/SĐT trực tiếp trên contract | | `NULL` |
| tenant_name | varchar | nullable | dùng khi tenant không có account | Min length: 1; Max length: 254 | `Trần Văn B` |
| tenant_phone | varchar | nullable | dùng khi tenant không có account | Min length: 10; Max length: 12; Regex: `^0[0-9]{9}$` hoặc `^\+84[0-9]{9}$` | `0912345678` |
| contract_status | enum (`draft`,`signed`,`active`,`suspended`,`expired`,`terminated`) | NOT NULL default `draft` | `suspended` khi landlord bị khóa trong grace period; `terminated` khi quá hạn hoặc admin/landlord hủy | | `active` |
| deposit_amount | decimal | NOT NULL | Agreed deposit; actual collections and refunds are recorded in Payment | `>=0` | `7000000` |
| deposit_deduction_amount | decimal | NOT NULL default 0 | Total deposit retained at checkout; this is not a new cash movement | `>=0` | `1000000` |
| deposit_deduction_reason | text | nullable | Required and non-blank when deposit_deduction_amount > 0 | Max length: 500 | `Repair damaged door` |
| deposit_settled_at | timestamptz | nullable | Set when checkout deposit reconciliation is complete, including full deduction with no refund | | |
| monthly_rent | decimal | NOT NULL | | `>=0`| `3500000` |
| start_date | date | NOT NULL | | `< end_date` | `2026-09-01` |
| end_date | date | NOT NULL | | `> start_date` | `2027-08-31` |
| description | text | nullable | | Min length: 1; Max length: 500 | `Đóng tiền trước ngày 5 hàng tháng…` |


> Mẫu HĐ / file ký: `Media(owner_type='contract', purpose='contract_template'|'contract_signed')` — file ký (`contract_signed`) vẫn là **nguồn chuẩn pháp lý**, `parsed_fields` chỉ hỗ trợ tra cứu.

**Tenant identity constraint (DB CHECK, D29):** a linked account allows either contact field to be null; without an account, both fields must contain non-blank values. This is not an exclusive-or: linked tenants may retain contact snapshots.

```sql
CONSTRAINT contract_tenant_identity_check CHECK (
    tenant_id IS NOT NULL
    OR (
        NULLIF(BTRIM(tenant_name), '') IS NOT NULL
        AND NULLIF(BTRIM(tenant_phone), '') IS NOT NULL
    )
)
```

**Index quan trọng:** partial unique index `(room_id) WHERE contract_status = 'active'` — chỉ 1 hợp đồng active/phòng.

**Deposit settlement:** use the three fields above on Contract and existing Payment rows; no separate settlement table. Remaining deposit = successful deposit collections − successful deposit refunds − `deposit_deduction_amount`. The service locks the contract when recording a refund or deduction, rejects a negative remaining deposit, and sets `deposit_settled_at` only when the remaining deposit is zero. Calculate from actual collections, not the agreed `deposit_amount`. AuditLog records changes and the actor; do not alter a completed settlement through normal checkout actions.

### 2.8 ContractMember (thành viên ở ghép + CCCD)
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| contract_id | uuid | FK→Contract, NOT NULL | | | |
| tenant_id | uuid | FK→User, **nullable** | nullable nếu tenant không có account (**D29**) | | `NULL` |
| tenant_name | varchar | nullable | | Min length: 1; Max length: 254 | `Nguyễn Thị C` |
| tenant_phone | varchar | nullable | | Min length: 10; Max length: 12; Regex: `^0[0-9]{9}$` hoặc `^\+84[0-9]{9}$` | `0921234567` |
| joined_at | date | NOT NULL default `current_date` | ngày vào ở; phục vụ số người có hiệu lực theo kỳ | `< left_at` khi `left_at` có giá trị | `2026-09-01` |
| left_at | date | nullable | không xóa bản ghi khi rời phòng; ngừng quyền chat/tenant portal từ ngày này | `> joined_at` | `NULL` |
| vehicle_count | int | **nullable** | **D32** — số xe gửi tại nhà trọ, kê khai lúc tạo/cập nhật HĐ; `NULL` = chưa khai → block phí `per_vehicle` (EC8); `0` = không gửi xe | `>= 0` | `1` |

> Ảnh CCCD mặt trước/sau: `Media(owner_type='contract_member', purpose='cccd_front'|'cccd_back')` — **D17**, chụp 1 lần. **`ContractMember` là nguồn đếm `head_count`** cho `rate_kind='per_head'` và `fee_kind='per_head'`; chỉ tính thành viên có `joined_at ≤ period_end` và (`left_at IS NULL` hoặc `left_at ≥ period_start`).

**Index:** UNIQUE `(id, contract_id)`. Composite key này được `Payment` tham chiếu để bảo đảm người trả (nếu xác định được) thuộc chính hợp đồng của khoản thu.

### 2.9 RatePolicy — đơn giá & phí định kỳ

> Gộp UtilityRatePolicy + RecurringFee vào 1 bảng. Giữ nguyên inheritance: `room → building → landlord`.
> **Cách tính → `utility-billing-calculations.md` §4–§7.**

| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| landlord_id | uuid | FK→User, NOT NULL | landlord sở hữu policy | | |
| scope | enum (`building`,`room`) | NOT NULL | cấp áp dụng | | `room` |
| room_id | uuid | FK→Room, nullable | bắt buộc nếu `scope='room'` | | |
| building_id | uuid | FK→Building, nullable | bắt buộc nếu `scope='building'` | | `NULL` |
| name | varchar | NOT NULL | nhãn hiển thị | Min length: 1; Max length: 254 | `Điện EVN`, `Wifi` |
| type | enum (`electricity`,`water`,`wifi`,`cleaning`,`parking`,`maintenance`) | NOT NULL | phân loại phí | | `electricity` |
| rate_kind | enum (`flat`,`tiered`,`per_head`,`per_area_m2`,`per_vehicle`) | NOT NULL | cách tính; service reject nếu `type` không hỗ trợ `rate_kind` (vd: `electricity` chỉ `flat`/`tiered`) | | `flat` |
| unit_price | decimal | nullable | `flat`/`per_head`/`per_area_m2`/`per_vehicle`: đ/unit; `tiered`: NULL (dùng steps) | `>=0`| `80000` |
| steps | jsonb | nullable | `tiered`: `[{from,to,price}]`, `to=null` = mở ∞ (EVN 6 bậc, bậc 3 TT 25/2018) | | `NULL` |
| is_active | boolean | default true | chỉ 1 record active/trùng index; tạo mới → deactivate record cũ; `false` = tắt → kế thừa cấp trên | | `true` |

> **Index:** `(type, landlord_id)` + `(room_id)`/`(building_id)` khi có. Partial UNIQUE `(type, scope, landlord_id, building_id, room_id) WHERE is_active = true` — mỗi index chỉ 1 record active. Ràng buộc `type` ↔ `rate_kind` kiểm tra ở service. Đổi giá = tạo record mới, deactivate record cũ (AuditLog ghi lịch sử).

### 2.10 BillingSetting (hạn thanh toán & nhắc nợ)

> Thay `LandlordProfile.default_settings`. Resolve theo `room → building → landlord`; thiếu ở cấp dưới thì kế thừa cấp trên.

| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| landlord_id | uuid | FK→User, NOT NULL | landlord sở hữu cấu hình | | |
| scope | enum (`landlord`,`building`,`room`) | NOT NULL | Default for the landlord, or an override for one building/room | | `room` |
| building_id | uuid | FK→Building, nullable | bắt buộc khi `scope='building'` | | |
| room_id | uuid | FK→Room, nullable | bắt buộc khi `scope='room'` | | |
| due_days | smallint | NOT NULL default 5 | Days allowed after invoice issuance; copied into the invoice due_date calculation (D37) | `>= 1; <= 28` | `5` |
| remind_days | smallint | NOT NULL default 3 | ngày trong tháng nhắc nộp tiền | `>= 1; <= 28` | `3` |
| bot_enabled | boolean | NOT NULL default true | cho bot gửi card nhắc nợ vào room chat | | `true` |
| is_active | boolean | NOT NULL default true | chỉ 1 record active/trùng index; `false` = tắt → kế thừa cấp trên | | `true` |

**Constraints:** `scope='landlord'` requires both target FKs to be NULL; `building` requires only `building_id`; `room` requires only `room_id`. Validate that the target belongs to the configuring landlord. Use three partial UNIQUE indexes, each filtered by its scope and `is_active = true AND is_deleted = false`: `(landlord_id)` for landlord defaults, `(landlord_id, building_id)` for building overrides, and `(landlord_id, room_id)` for room overrides. Resolution skips inactive/deleted settings. Changes affect newly issued invoices only.

### 2.11 MeterReading
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| room_id | uuid | FK→Room, NOT NULL | | | |
| type | enum (`electricity`,`water`) | NOT NULL | 1 bản ghi/loại/kỳ | | `electricity` |
| period | varchar(7) (`YYYY-MM`) | NOT NULL | | Min length: 7; Max length: 7; Regex: `^[0-9]{4}-(0[1-9]\|1[0-2])$` | `2026-09` |
| previous_reading | decimal | NOT NULL | kỳ đầu = baseline chỉ số lúc bàn giao §5; kỳ sau = current_reading kỳ trước | `>= 0` | `1200` |
| current_reading | decimal | NOT NULL | | `>= previous_reading` | `1380` |
| reading_date | date | nullable | ngày chốt thực tế (dọn vào/ra giữa tháng) | | `2026-09-30` |
| is_baseline | boolean | default false | kỳ đầu hoặc sau khi thay đồng hồ | | `false` |

> Ảnh đối chứng công tơ: `Media(owner_type='meter_reading', purpose='meter_reading_evidence')` — tối thiểu 1 ảnh trước khi xác nhận (service constraint). **Cách tính consumption & xử lý đồng hồ reset → `utility-billing-calculations.md` §3/EC1.**

**Index:** UNIQUE `(room_id, type, period)`.

### 2.12 Invoice
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| contract_id | uuid | FK→Contract, NOT NULL | | | |
| code | varchar(32) | UNIQUE, NOT NULL | mã nhận diện nhúng trong VietQR; webhook đối soát theo mã này, không theo amount | Min length: 1; Max length: 32 | `INV-202609-8F2K` |
| payment_account_id | uuid | FK→LandlordPaymentAccount, nullable | tài khoản/kênh nhận tiền đã chọn; bắt buộc khi phát hành hóa đơn có VietQR | | |
| payment_recipient_snapshot | jsonb | nullable | snapshot bất biến lúc phát hành: `account_type`, `bank_code`, `account_number_encrypted`, `account_number_masked`, `account_name`, `merchant_id`; API chỉ trả QR render + số TK đã che | | |
| period | varchar(7) | NOT NULL | | Min length: 7; Max length: 7; Regex: `^[0-9]{4}-(0[1-9]\|1[0-2])$` | `2026-09` |
| rent_amount | decimal | NOT NULL | tiền phòng **prorated** theo §8 (`monthly_rent × ratio`); denormalized cho Dashboard (D20) | `>=0` | `3500000` |
| breakdown | jsonb | nullable | snapshot bất biến: điện/nước/phí định kỳ từ RatePolicy;每个item có `type` để phân loại | | `[{"type":"electricity","name":"Điện EVN","qty_kwh":180,"amount":720000}]` |
| other_fees | jsonb | nullable | phí 1 lần / ngoài lệ (không trong cấu hình). **D33 — cho phép `amount` ÂM = giảm trừ/miễn giảm** (snapshot giữ dấu âm) | | `[{"name":"Vệ sinh lễ","amount":50000}]` |
| total_amount | decimal | NOT NULL | **= làm tròn tổng** (round-half-up → hàng nghìn), kiểm tra khớp dòng; **≥ 0** (`TOTAL_NEGATIVE` — D33⑥) | `>=0` | `4610000` |
| paid_amount | decimal | NOT NULL default 0 | Sum of successful invoice collections; updated with Payment in the same transaction | `>=0` | `3500000` |
| invoice_status | enum (`pending`,`unpaid`,`partially_paid`,`paid`,`overdue`,`cancel`) | NOT NULL default `pending` | pending = draft; unpaid = issued with no payment; partially_paid = some payment before the deadline; overdue = past the deadline with money still owed; paid = paid_amount >= total_amount; cancel = retained for audit | | `pending` |
| issued_at | timestamptz | nullable | Issuance time; NULL while pending. Issued financial details are immutable; corrections require cancellation and replacement | | `2026-09-30T20:15:00Z` |
| due_date | date | nullable | Set once at issuance: local issue date in Asia/Ho_Chi_Minh + resolved due_days (D37); subsequent setting changes do not alter it | | `2026-10-06` |
| voided_invoice_id | uuid | FK→Invoice, nullable | Replacement points to the cancelled invoice it replaces (new → old, D37); same contract and period, validated by the service | | |
| note | text | nullable | | | `Tháng nhập cư, prorate từ 15/09` |

> **Billing calculation:** see `utility-billing-calculations.md` §2–§11. Partial UNIQUE `(contract_id, period) WHERE invoice_status != 'cancel'` permits a replacement after cancellation (D33①). Auto-create a pending invoice per room when both readings and policies are ready (D33②). At issuance, select the landlord's payment account, freeze the recipient snapshot, and generate VietQR using `code`, `total_amount`, and that snapshot. Set `issued_at` and `due_date` together (D37); use `unpaid`, or `paid` immediately if the total is zero. Do not create a zero-value Payment for a zero-total invoice. An issued invoice is overdue when the current date in Asia/Ho_Chi_Minh is later than `due_date` and a balance remains; a partial payment after that date leaves it overdue. Never change `cancel` through payment processing. CHECK `(issued_at IS NULL) = (due_date IS NULL)`; pending requires both NULL, and unpaid/partially_paid/paid/overdue require both present. A cancelled draft may keep both NULL.

**Constraint:** UNIQUE `(id, contract_id)` để `Payment` có thể dùng foreign key kép xác nhận invoice thực sự thuộc contract đã ghi. `payment_account_id` phải thuộc `Contract.landlord_id`; đây là ràng buộc xuyên bảng, thực thi bằng trigger `validate_invoice_payment_account_owner()` khi tạo/cập nhật invoice. Trigger cũng buộc `payment_account_id` và snapshot cùng có mặt khi `issued_at IS NOT NULL`.

**DTO — Breakdown items:**

```typescript
// Base interface cho mọi item trong breakdown
interface BreakdownItem {
  type: string;         // RatePolicy.type: 'electricity' | 'water' | 'wifi' | 'cleaning' | 'parking' | 'maintenance' | 'other'
  name: string;         // nhãn hiển thị: "Điện EVN", "Wifi", "Gửi xe"
  amount: number;       // số tiền (đ)
}

// Item điện
interface ElectricityItem extends BreakdownItem {
  type: 'electricity';
  qty_kwh: number;      // số kWh tiêu thụ
  tier_detail?: {       // bậc thang (nếu rate_kind = 'tiered')
    step: number;
    from: number;
    to: number | null;
    price: number;
    amount: number;
  }[];
}

// Item nước
interface WaterItem extends BreakdownItem {
  type: 'water';
  qty_m3?: number;      // số m³ (nếu rate_kind = 'flat')
  head_count?: number;  // số người (nếu rate_kind = 'per_head')
}

// Item phí định kỳ (wifi, cleaning, parking, maintenance, other)
interface FeeItem extends BreakdownItem {
  type: 'wifi' | 'cleaning' | 'parking' | 'maintenance' | 'other';
  rate_kind: string;    // 'fixed_per_period' | 'per_head' | 'per_area_m2' | 'per_vehicle'
  quantity: number;
  unit_price: number;
}

type InvoiceBreakdownItem = ElectricityItem | WaterItem | FeeItem;
```

**Ví dụ snapshot trong Invoice.breakdown:**
```json
[
  {
    "type": "electricity",
    "name": "Điện EVN",
    "qty_kwh": 180,
    "amount": 720000,
    "tier_detail": [
      {"step":1,"from":0,"to":50,"price":1806,"amount":90300},
      {"step":2,"from":51,"to":100,"price":1866,"price":93300},
      {"step":3,"from":101,"to":null,"price":2012,"amount":160960}
    ]
  },
  {
    "type": "water",
    "name": "Nước",
    "head_count": 3,
    "amount": 240000
  },
  {
    "type": "wifi",
    "name": "Wifi",
    "rate_kind": "fixed_per_period",
    "quantity": 1,
    "unit_price": 100000,
    "amount": 100000
  },
  {
    "type": "parking",
    "name": "Gửi xe",
    "rate_kind": "per_vehicle",
    "quantity": 2,
    "unit_price": 150000,
    "amount": 300000
  }
]
```

### 2.13 LandlordPaymentAccount (tài khoản/kênh nhận tiền)
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| landlord_id | uuid | FK→User, NOT NULL | chủ sở hữu tài khoản/kênh nhận tiền | | |
| account_type | enum (`bank_account`,`vnpay_merchant`,`momo_merchant`) | NOT NULL | `bank_account` là nguồn sinh VietQR; hai loại merchant phục vụ gateway khi được bật | | `bank_account` |
| bank_code | varchar(32) | nullable | mã ngân hàng/VietQR; bắt buộc với `bank_account` | Min length: 1; Max length: 32 | `VCB` |
| account_number_encrypted | bytea | nullable | số tài khoản mã hóa ở tầng ứng dụng; không trả qua API | | |
| account_number_masked | varchar(32) | nullable | số TK đã che để hiển thị/audit; bắt buộc với `bank_account` | Min length: 4; Max length: 32 | `****1234` |
| account_name | varchar | nullable | tên chủ tài khoản; bắt buộc với `bank_account` | Min length: 1; Max length: 254 | `NGUYEN VAN A` |
| merchant_id | varchar | nullable | mã merchant của VNPay/MoMo; bắt buộc với loại merchant tương ứng | Min length: 1; Max length: 255 | `MOMO_MERCHANT_01` |
| credential_ref | varchar | nullable | khóa tham chiếu secret manager; không lưu API key/secret trong DB | Min length: 1; Max length: 255 | `secrets/payment/momo/01` |
| is_default | boolean | NOT NULL default false | gợi ý khi tạo invoice; invoice vẫn snapshot tài khoản thực được chọn | | `true` |
| is_active | boolean | NOT NULL default true | false = không được chọn cho hóa đơn mới, vẫn giữ để audit hóa đơn cũ | | `true` |
| verified_at | timestamptz | nullable | thời điểm xác minh ownership/gateway thành công | | |

**Constraints & indexes:**

- `account_type='bank_account'` bắt buộc có `bank_code`, `account_number_encrypted`, `account_number_masked`, `account_name`; loại merchant bắt buộc có `merchant_id` và `credential_ref`.
- Partial UNIQUE `(landlord_id) WHERE is_default = true AND is_active = true AND is_deleted = false` — mỗi landlord tối đa một tài khoản mặc định đang hoạt động.
- Không hard-delete tài khoản đã được `Invoice.payment_account_id` tham chiếu; chỉ `is_active=false`/soft-delete sau khi đã ngừng dùng.

### 2.14 Payment
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| invoice_id | uuid | FK→Invoice, nullable | bắt buộc chỉ với `payment_purpose='invoice_collection'` | | |
| contract_id | uuid | FK→Contract, **NOT NULL** | luôn giữ contract để đối soát cả thu hóa đơn, thu cọc và hoàn cọc | | |
| payment_purpose | enum (`invoice_collection`,`deposit_collection`,`deposit_refund`) | NOT NULL | phân biệt thu hóa đơn, nhận cọc và trả cọc; không suy luận bằng `invoice_id` | | `invoice_collection` |
| direction | enum (`inflow`,`outflow`) | NOT NULL | `inflow` là tiền vào landlord; `outflow` là tiền trả từ landlord | | `inflow` |
| channel | enum (`bank_transfer_qr`,`vnpay`,`momo`,`cash`,`mock`) | NOT NULL | kênh thanh toán; VietQR là `bank_transfer_qr` | | `bank_transfer_qr` |
| payment_status | enum (`pending`,`success`,`failed`) | NOT NULL | | | `success` |
| amount | decimal | NOT NULL | Actual money received or refunded; record the full amount even for underpayment/overpayment | `>0` | `2000000` |
| provider | varchar | nullable | nguồn đối soát/gateway: `sepay`, `casso`, `vnpay`, `momo`, `mock`, `manual` | Min length: 1; Max length: 50 | `sepay` |
| provider_event_id | varchar | nullable | event ID do provider gửi; dùng chống xử lý lặp webhook | Min length: 1; Max length: 255 | `evt_01J...` |
| transaction_id | varchar | nullable | mã giao dịch do ngân hàng/gateway trả về; null cho cash chưa có biên lai điện tử | Min length: 1; Max length: 255 | `VNPAY-20260930183021` |
| raw_gateway_response | jsonb | nullable | bằng chứng đối soát QR | | `{"bank":"VCB","amount":4610000}` |
| payer_contract_member_id | uuid | FK→ContractMember, nullable | người trả nếu xác định được; nullable khi webhook QR chỉ biết mã invoice hoặc tenant passive (D29) | | `NULL` |
| paid_at | timestamptz | nullable | thời điểm tiền thực sự được nhận/trả thành công; không dùng `created_at` cho báo cáo tài chính | | `2026-09-30T20:15:00Z` |
| needs_review | boolean | NOT NULL default false | true nếu webhook thành công tới Invoice `cancel` (D33⑤) | | `false` |

**Constraints & indexes:**

- CHECK `payment_purpose='invoice_collection'` ⟺ `invoice_id IS NOT NULL AND direction='inflow'`; `deposit_collection` yêu cầu `invoice_id IS NULL AND direction='inflow'`; `deposit_refund` yêu cầu `invoice_id IS NULL AND direction='outflow'`.
- CHECK `provider_event_id IS NOT NULL OR transaction_id IS NOT NULL` thì `provider IS NOT NULL`; khoản cash thu tay không có mã điện tử dùng `provider='manual'` khi cần lưu biên lai.
- UNIQUE `(provider, provider_event_id) WHERE provider_event_id IS NOT NULL` và UNIQUE `(provider, transaction_id) WHERE transaction_id IS NOT NULL` — callback/webhook gửi lại không tạo thêm Payment.
- FK `(invoice_id, contract_id)` → `Invoice(id, contract_id)` và FK `(payer_contract_member_id, contract_id)` → `ContractMember(id, contract_id)`. Vì `contract_id` luôn có, Payment không thể trỏ sang invoice hoặc member của hợp đồng khác.
- CHECK `payment_status != 'success' OR paid_at IS NOT NULL`.
- **Manual-entry retries:** reuse the existing Payment `id` as the request identifier. The client generates one UUID per collection/refund action and reuses it on retries. After owner authorization, an existing ID with the same payment details returns the existing result; different details are rejected. The primary key prevents double insertion, and retries must not increment `paid_amount` again. AuditLog records who confirmed the payment.

**Reconciliation (existing tables):** authenticate the provider callback, require a provider event/transaction ID, then validate invoice code, incoming direction, and the actual recipient bank account/merchant against the frozen invoice snapshot before recording an invoice collection. An amount mismatch is allowed under D33. Unmatched transfers do not create a Payment or change invoice balances: record the authenticated event in the existing AuditLog (`payment.unmatched`, system actor), retaining the provider ID and received data needed for manual reconciliation. The landlord checks the provider/bank history and confirms the correct invoice manually through the same recipient/direction checks; keep the original provider IDs and raw response so a later callback cannot record it twice. Do not expose a new unmatched-event screen or automatic matching workflow. Payments for draft invoices also require manual review after issuance; cancelled invoices keep the existing D33⑤ behavior.

> **D33③ — partial payment / overpayment:** after recipient/direction checks, match by invoice code, not exact amount. For an issued, non-cancelled invoice, use `paid` when the successful invoice-collection sum reaches the total; otherwise use `overdue` if the deadline has passed, `partially_paid` if any money was received, or `unpaid`. Keep the full amount received; show excess/remaining amounts in History without automatic refunds or carry-forward. Update Payment and `Invoice.paid_amount` atomically while holding the invoice row lock; cancellation uses the same lock. A duplicate callback must not add to the aggregate again or downgrade success. **D33⑤:** a successful payment to a cancelled invoice is retained with `needs_review=true`; never revive the invoice or automatically move the payment to its replacement.
>
> **Tiền cọc:** nhận cọc dùng `payment_purpose='deposit_collection'`, `direction='inflow'`; hoàn cọc lúc checkout dùng `payment_purpose='deposit_refund'`, `direction='outflow'`. Hai loại này không được cộng vào doanh thu hóa đơn. Báo cáo doanh thu chỉ lấy `invoice_collection` + `inflow` + `payment_status='success'`, theo `paid_at`.

### 2.15 IssueReport
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| room_id | uuid | FK→Room, NOT NULL | | | |
| conversation_id | uuid | FK→Conversation, nullable | | | |
| reporter_id | uuid | FK→User, **nullable** | null nếu landlord tự tạo thay tenant passive (**D29**) | | `NULL` |
| status | enum (`open`,`in_progress`,`resolved`,`cancelled`) | NOT NULL default `open` | `cancelled` là hủy sự cố, không hard-delete | | `open` |
| title | varchar | NOT NULL | | Min length: 1; Max length: 255 | `Đèn cháy` |
| description | text | nullable | | Min length: 1; Max length: 500 | `Bóng đèn phòng ngủ cháy 2 bóng` |
| note | text | nullable | | Min length: 1; Max length: 500 | `NULL` |
| closed_at | timestamptz | nullable | set khi `resolved` hoặc `cancelled` | | |

> Ảnh sự cố: `Media(owner_type='issue_report', purpose='issue_photo')`.
### 2.16 Conversation (Chat)
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| type | enum (`room`,`building`,`direct`) | NOT NULL | | | `room` |
| building_id | uuid | FK→Building, nullable | bắt buộc nếu kind=building | | `NULL` |
| contract_id | uuid | FK→Contract, nullable | bắt buộc nếu kind=room; mỗi HĐ có một room chat mới | | |
| title | varchar | nullable | tên group chat (optional, cho building chat hoặc future use) | Min length: 1; Max length: 255 | `Chat tòa nhà` |

**Constraint:**
- `kind='room'` → có `room_id` + `contract_id`, không có `building_id`
- `kind='building'` → chỉ có `building_id`
- `kind='direct'` → không có `room_id`, `building_id`, `contract_id` (chat tự do, 2 người hoặc nhiều người)
- UNIQUE `contract_id` khi room chat
- Chat cũ vẫn giữ history sau checkout, không archive/read-only

### 2.17 ConversationMember
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| conversation_id | uuid | FK→Conversation, NOT NULL | | | |
| user_id | uuid | FK→User, NOT NULL | | | |
| joined_at | timestamp | | | `< left_at` khi `left_at` có giá trị | `2026-09-01T10:05:00Z` |
| left_at | timestamptz | nullable | rời phòng thì không gửi mới, nhưng vẫn đọc được history cũ theo flow P2-01 | `> joined_at` | `NULL` |

**Index:** UNIQUE `(conversation_id, user_id)`.

### 2.18 Message
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| conversation_id | uuid | FK→Conversation, NOT NULL | | | |
| sender_id | uuid | FK→User, **nullable** | null = bot | | `NULL` |
| type | enum (`text`,`image`,`file`,`bot`) | NOT NULL | | | `bot` |
| content | text | nullable | | | `Đã chốt số điện tháng 09: 180 kWh` |

> File/ảnh đính kèm (khi `type = image|file`): `Media(owner_type='message', purpose='chat_attachment')`.

### 2.19 MessageMention
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| message_id | uuid | FK→Message, NOT NULL | | | |
| user_id | uuid | FK→User, NOT NULL | người được `@mention` | | |

**Index:** UNIQUE `(message_id, user_id)`.

### 2.20 RoommateProfile
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| user_id | uuid | FK→User, UNIQUE, NOT NULL | chỉ tenant có account | | |
| lifestyle | jsonb | nullable | | | `{"sleep":"23h-6h","pets":false,"smoking":false}` |
| personality | jsonb | nullable | | | `{"introvert":true,"noisy_level":2}` |
| budget_min | decimal | nullable | | `>= 0; < budget_max` khi `budget_max` có giá trị | `2000000` |
| budget_max | decimal | nullable | | `>= 0; > budget_min` khi `budget_min` có giá trị | `3500000` |
| bio | text | nullable | | | `Hiền lành, sạch sẽ, dậy sớm` |
| preferred_area | varchar | nullable | khu vực mong muốn trong feed | Min length: 1; Max length: 255 | `Hòa Khánh, Liên Chiểu` |
| move_in_on | date | nullable | thời điểm muốn dọn vào | | `2026-10-01` |
| is_visible | boolean | NOT NULL default true | ẩn/hiện bài trong feed, không xóa profile | | `true` |
| id_verified | boolean | default false | badge xác minh tự nguyện (**D26**) | | `true` |

### 2.21 MatchRequest
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| requester_id | uuid | FK→User, NOT NULL | | | |
| target_id | uuid | FK→User, NOT NULL | Matching độc lập với phòng; ràng buộc phòng chỉ xét lúc tạo HĐ | | |
| match_status | enum (`pending`,`accepted`,`rejected`) | NOT NULL default `pending` | | | `accepted` |
| responded_at | timestamptz | nullable | thời điểm target chấp nhận/từ chối | | |
| ai_score | decimal | nullable | **D28**, Stretch | `>= 0.0; <= 100.0` | `87.5` |
| ai_advice | text | nullable | **D28** | | `Hai người cùng giờ ngủ, ít rủi ro xung đột` |

**Index:** UNIQUE `(requester_id, target_id)` — cache mỗi cặp 1 lần (**D28**). Service chặn request đảo chiều trùng cặp.

### 2.22 Notification (MVP inbox + FCM)
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| user_id | uuid | FK→User, NOT NULL | | | |
| type | varchar | NOT NULL | invoice_due, contract_expiry,... | Min length: 1; Max length: 50 | `invoice_due` |
| data | jsonb | nullable | deep-link payload | | `{"invoice_id":"<uuid>","amount":4610000}` |
| read_at | timestamp | nullable | | | `NULL` |
| sent_at | timestamp | nullable | thời điểm gửi FCM | | |

### 2.23 NotificationPreference
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| user_id | uuid | FK→User, NOT NULL | | | |
| type | enum (`invoice`,`chat`,`issue`,`match`,`account`) | NOT NULL | nhóm notification bật/tắt | | `invoice` |
| enabled | boolean | NOT NULL default true | | | `true` |

**Index:** UNIQUE `(user_id, type)`.

### 2.24 PushDevice
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| user_id | uuid | FK→User, NOT NULL | một user có thể nhiều thiết bị | | |
| token | varchar | UNIQUE, NOT NULL | FCM registration token | Min length: 1; Max length: 512 | |
| platform | enum (`android`,`web`) | NOT NULL | | | `android` |
| last_seen_at | timestamptz | nullable | dùng dọn token hết hạn | | |

### 2.25 AuditLog
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| actor_id | uuid | FK→User, nullable | null cho webhook/system | | |
| action | varchar | NOT NULL | `user.lock`, `building.approve`, `payment.webhook` | Min length: 1; Max length: 100 | `building.approve` |
| entity_type | varchar | NOT NULL | resource bị tác động | Min length: 1; Max length: 50 | `building` |
| entity_id | uuid | nullable | | | |
| before_data | jsonb | nullable | snapshot trước thay đổi | | |
| after_data | jsonb | nullable | snapshot sau thay đổi | | |
| created_at | timestamptz | NOT NULL default `now()` | Audit log append-only, không soft-delete | | |

**Index:** `(entity_type, entity_id, created_at DESC)`, `(actor_id, created_at DESC)`.

### 2.26 Media (polymorphic — gom mọi file/ảnh của hệ thống)

**Thiết kế polymorphic** — 1 bảng `media` quản lý file/ảnh mọi entity (user, room, building, contract, contract_member, meter_reading, issue_report, message). `owner_type` enum cố định + `purpose` enum ràng buộc hợp lệ theo từng owner_type. Toàn vẹn tham chiếu kiểm tra ở service layer (không FK thật vì 1 cột `owner_id` reference nhiều bảng).

| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| owner_type | enum (`user`,`room`,`building`,`contract`,`contract_member`,`meter_reading`,`issue_report`,`message`) | NOT NULL | | | `room` |
| owner_id | uuid | NOT NULL | **không có FK thật** — xem giải thích trên | | |
| purpose | enum (`avatar`,`cover_photo`,`gallery_photo`,`ownership_proof`,`cccd_front`,`cccd_back`,`contract_template`,`contract_signed`,`meter_reading_evidence`,`issue_photo`,`chat_attachment`) | NOT NULL | vai trò của file trong owner đó | | `cover_photo` |
| file_type | enum (`image`,`document`,`video`,`other`) | NOT NULL default `image` | | | `image` |
| url | varchar | NOT NULL | | Min length: 1; Max length: 2048 | `https://cdn.pbl6.dev/room/<room_id>/cover.webp` |
| size_bytes | bigint | nullable | | | `245000` |
| user_id | uuid | FK→User, nullable | Uploader | | |

**Index:** `(owner_type, owner_id)`. Partial UNIQUE `(owner_type, owner_id, purpose) WHERE purpose = 'cover_photo' AND is_deleted = false` ensures one cover per entity. Gallery order: `created_at ASC, id ASC`.

**Phân quyền Media** (bổ sung vào ma trận mục 5.2): quyền upload/xoá = quyền sửa entity cha tương ứng (vd landlord chỉ upload được ảnh cho `Room` mình sở hữu — check qua `Room.owner_id`, không phải role suông); quyền đọc = quyền đọc entity cha (ảnh phòng `available` là public, ảnh CCCD chỉ landlord sở hữu HĐ + chính chủ CCCD + admin).

---

## 3. Sơ đồ quan hệ (ERD)

Xem file đính kèm `erd.mermaid` để render trực quan. Tóm tắt quan hệ chính:

```
User 1--1 LandlordProfile
User 1--N FavoriteRoom
Room 1--N FavoriteRoom
User 1--0..1 RoommateProfile
User 1--N Building (submitted_by; không phải ownership)
Building 1--N Room
User 1--N Room (owner_id, NOT NULL)
Room 1--N Contract
Contract 1--N ContractMember
Contract 1--N Invoice
Contract 1--N Payment              (cọc / hoàn cọc / đối soát)
User 1--N LandlordPaymentAccount
LandlordPaymentAccount 1--N Invoice (tài khoản đã snapshot khi phát hành)
Invoice 1--N Payment
ContractMember 1--N Payment        (payer_contract_member_id, optional)
Room 1--N MeterReading            (điện + nước: 2 bản ghi/kỳ qua type)
Building/Room 1--N BillingSetting (cấu hình hạn/nhắc; còn: landlord)
User 1--N BillingSetting
Building 1--N RatePolicy   (policy cấp tòa; còn: room, landlord)
Room 1--N RatePolicy       (policy cấp phòng)
LandlordProfile 1--0..1 RatePolicy  (2 con trỏ: elec_policy_id, water_policy_id)
Room 1--N IssueReport
Room 1--N Conversation (kind=room; một room chat mỗi hợp đồng)
Contract 1--0..1 Conversation (kind=room)
Building 1--0..1 Conversation (kind=building)
User N--N Conversation (kind=direct; chat tự do, không gắn room/building)
Conversation 1--N ConversationMember
Conversation 1--N Message
Message 1--N MessageMention
User 1--N MatchRequest (requester / target)
User 1--N Notification
User 1--N NotificationPreference
User 1--N PushDevice
User 1--N AuditLog
User/Room/Building/Contract/ContractMember/MeterReading/IssueReport/Message
    1--N Media (polymorphic qua owner_type + owner_id, không FK thật)
```

> Lưu ý: `RatePolicy` được link **2 chiều** — bảng cấu hình giữ `electricity_policy_id`/`water_policy_id` (con trỏ từ phòng/tòa/profile) đồng thời policy tự khai `scope`/`room_id`/`building_id`. Con trỏ trên Room/Building/LandlordProfile là nguồn chân lý cho chain resolution (D16/D30); trường `scope`/`*_id` trong policy phục vụ quản lý/gũi gọn (vd hiển thị danh sách, export).

---

| Bảng | D áp dụng |
|---|---|
| Room.owner_id NOT NULL, Building không bắt buộc owner, bỏ Manager | D25 |
| **RatePolicy (gộp UtilityRatePolicy + RecurringFee), Invoice.breakdown, MeterReading.type** | **D30** — đơn giá điện/nước versioned (flat/bậc thang/khoán đầu người) + phí định kỳ; đóng open question #6; mở rộng D16 (giữ thứ tự room→building→landlord) |
| **RatePolicy.steps bậc thang chỉ từ preset seed (EVN/TT25/nước địa phương), không nhập tay trong UI; đổi giá = policy mới `effective_from`** | **D31** — preset thân thiện landlord lớn tuổi; thuật toán `calcTiered` là code, giá là config |
| **LandlordProfile.electricity_policy_id/water_policy_id nullable (NULL = chưa cấu hình), Contract.vehicle_count kê khai ở HĐ, phí 1 lần `other_fees`, preset phí seed** | **D32** — onboarding không chặn (banner + block tại hóa đơn), xe theo HĐ, preset phí |
| **Invoice `invoice_status` `partially_paid`, UNIQUE partial `(contract_id, period) WHERE invoice_status != 'cancel'`, Payment đối soát theo invoice_id + thu dư/thiếu nhắc ở History, Invoice auto-sinh theo phòng, `other_fees` âm (total ≥ 0), `rate_kind` điện chỉ flat/tiered** | **D33** — thanh toán một phần + thu dư/thiếu nhắc, hóa đơn theo phòng, điện bỏ khoán đầu người |
| **LandlordPaymentAccount, Invoice payment-recipient snapshot, Payment purpose/direction + composite FKs + webhook idempotency** | Payment-design fix — VietQR đúng recipient, tách tiền cọc khỏi doanh thu, chặn Payment gắn sai hợp đồng/member |
| **Invoice unpaid/due_date, manual Payment retry via existing id, Contract deposit settlement fields, unmatched events in existing AuditLog** | Payment simplification using existing tables only; retain D33/D37 behavior |
| Building/Room `electricity_policy_id`/`water_policy_id` (con trỏ policy) thay field decimal | D16 (nâng cấp), D30 |
| Contract uses template generation + signed-file upload; `signed_at` + Media `contract_signed`, no signature-mode column | D18 |
| ContractMember.share_amount, Contract.payment_config | D22 |
| ContractMember `cccd_ocr_data` + Media CCCD | D17 |
| `User.role` bất biến; tài khoản role khác phải đăng ký riêng | User flows Phase 1 |
| Conversation/Message | D24′ |
| MatchRequest unique(requester_user_id,target_user_id), ai_score/ai_advice | D28 |
| Room.max_occupancy/gender_policy/house_rules dùng làm hard filter | D21 |
| Contract.tenant_id nullable, ContractMember.tenant_id nullable, IssueReport.reporter_id nullable | D29 (zero tenant login) |
| Building.property_type mở rộng | D9 |
| Building province/ward/address + latitude/longitude (geocoded tự động) | yêu cầu định vị bản đồ + dropdown VN |
| Bảng Media polymorphic (thay mọi cột `*_url`/`photos`) | yêu cầu tránh rải url file |
| Base Entity (id/created_at/updated_at/deleted_at) trên mọi bảng | yêu cầu chuẩn hoá audit/soft-delete |
| FavoriteRoom, Building approval + ownership_proof Media, User lock, Contract suspended/cancelled, AuditLog | P2-01 M2–M8, C4, D1–D2; admin/landlord/shared flows |
| BillingSetting, NotificationPreference, PushDevice, Invoice.code, MessageMention | P2-01 I3, B2, H2/N1, J3–J5; landlord/tenant flows |
| ContractMember.joined_at/left_at, Room.cleaning, IssueReport.cancelled, RoommateProfile discovery fields | P2-01 E4, F1–F2, K1–K4, L1–L4; landlord/tenant flows |
| `LandlordGatewayCredential` / `GatewayConfig` | **Không thêm vào MVP:** D38 là thiết kế gateway/mock cho Phase 1+; P2-01 và scope SoT không có feature tạm trú |

---

## 4. Thiết kế phân quyền theo Role (không RBAC)

| Resource | Action | landlord | tenant | admin | Ghi chú |
|---|---|---|---|---|---|
| Building/Room | Create/Update/Delete | ✅ (BĐS mình nộp / phòng mình sở hữu) | ❌ | ✅ | ownership check qua `Building.submitted_by` / `Room.owner_id` |
| Room | Đọc (tìm phòng available) | ✅ (mọi phòng, phục vụ ops) | ✅ (public, chỉ field public) | ✅ | tenant chỉ thấy field public khi tìm kiếm |
| RatePolicy | Create/update/deactivate | ✅ (chỉ của mình, `landlord_id`) | ❌ | ✅ | đổi giá ảnh hưởng kỳ sau (D30) |
| RatePolicy | Đọc | ✅ | ✅ (qua hóa đơn/hiển thị) | ✅ | tenant đọc qua snapshot hóa đơn, không sửa |
| Contract | Create/sinh mẫu/upload file ký | ✅ (chỉ phòng mình, qua `Room.owner_id`) | ❌ | ✅ | |
| Contract | Đọc | ✅ (owner) | ✅ (chỉ HĐ mình là `tenant_id`/`ContractMember`) | ✅ | |
| MeterReading | Create/confirm | ✅ (owner phòng) | ❌ | ✅ | P2-01: chỉ landlord thao tác trên mobile |
| MeterReading | Đọc | ✅ | ✅ (chỉ phòng mình đang thuê) | ✅ | |
| Invoice | Create (auto)/cancel | ✅ (owner) | ❌ | ✅ | |
| Invoice | Đọc | ✅ (owner) | ✅ (contract của mình) | ✅ | |
| LandlordPaymentAccount | CRUD | ✅ (chỉ của mình) | ❌ | ✅ | không trả `account_number_encrypted`/`credential_ref` ra API client |
| Payment | Record cash / confirm a verified bank transfer manually | ✅ (owner) | ❌ | ✅ | Retain provider IDs for bank transfers; use the existing Payment id for manual-entry retries |
| Payment | Webhook callback (bank/VNPay/MoMo) | hệ thống (service account) | — | — | xác minh chữ ký provider + idempotency, không qua user JWT |
| Payment | Đọc | ✅ (owner) | ✅ (của mình) | ✅ | |
| IssueReport | Create | ✅ (owner, tạo thay tenant passive) | ✅ (tenant tự tạo qua @issue) | ✅ | |
| IssueReport | Update status | ✅ (owner) | ❌ | ✅ | |
| Conversation/Message | Đọc/Gửi | ✅ (nếu là `ConversationMember`) | ✅ (nếu là `ConversationMember`) | ✅ | check qua bảng ConversationMember, không phải role |
| RoommateProfile | CRUD | ❌ | ✅ (của chính mình) | ✅ | landlord không tham gia (**D21** — chỉ set constraint trên Room) |
| MatchRequest | Create/Accept/Reject | ❌ | ✅ (chỉ với tư cách requester/target) | ✅ | |
| Dashboard (D20) | Đọc | ✅ (chỉ số liệu của mình) | ❌ | ✅ (toàn hệ thống) | |
| LandlordProfile (rate policy mặc định) | CRUD | ✅ (của mình) | ❌ | ✅ | |
| User | Đọc/sửa profile | ✅/✅ (chính mình) | ✅/✅ (chính mình) | ✅ (mọi user) | |
| FavoriteRoom / NotificationPreference / PushDevice | CRUD | ✅ (của chính mình) | ✅ (của chính mình) | ✅ | |
| AuditLog | Đọc | ❌ | ❌ | ✅ | append-only; webhook/system cũng ghi log |
| Media | Upload/Delete | ✅ (nếu có quyền sửa entity cha) | ✅ (nếu có quyền sửa entity cha, vd ảnh issue của mình) | ✅ | không check qua role, check qua quyền của owner_type tương ứng |
| Media | Đọc | ✅ (theo quyền đọc entity cha) | ✅ (theo quyền đọc entity cha) | ✅ | vd ảnh phòng available = public, ảnh CCCD = riêng tư |
