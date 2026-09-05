# Thiết kế Cơ sở dữ liệu & Phân quyền theo Role
**Dự án:** Nền tảng quản lý thuê trọ dài hạn (Landlord Web + Tenant Mobile + AI)
**Nguồn:** decisions.md (D1–D33), feature-list.md
**Phạm vi:** MVP theo D9 (dài hạn only), D25 (ownership), D29 (landlord-solo resilience)
**Tính toán điện/nước/phí:** xem file **`utility-billing-calculations.md`** — tham chiếu đầy đủ 100% case + hướng dẫn code (liên kết chi tiết tại §2.8, §2.9, §2.10, §2.11).

---

## 1. Nguyên tắc thiết kế

1. **Role không dùng RBAC (không có bảng Role/Permission riêng).** `User.roles` là một tập hợp (array/set) enum tĩnh: `landlord | tenant | admin`. Một user có thể vừa là landlord vừa là tenant (D13). Kiểm tra quyền = so khớp role trong JWT + kiểm tra sở hữu (ownership check) ở tầng service, không cần bảng trung gian.
2. **Ownership là nguồn chân lý phụ, không phải role.** Có role `landlord` chưa đủ — phải là đúng `Room.owner_id` / `Contract.issued_by_user_id` mới được thao tác (D25).
3. **Trạng thái phòng là derived/cached**, nguồn chân lý là `Contract.status` đang active cho phòng đó, không phải bảng riêng (ghi chú trong decisions.md).
4. **Không có bảng Manager/Delegation** — bỏ hoàn toàn khỏi MVP (D25).
5. **Không có bảng liên quan chữ ký điện tử** (e_sign, e_ack, OTP, PIN) — chỉ còn `signature_mode = template_upload` (D18).
6. **Schema giữ mở cho short-term (Phase 1+)** qua field `Building.property_type`, không redesign (D9).
7. **Mọi luồng nghiệp vụ phải chạy được với `tenant_user_id = NULL`** trên các bản ghi liên quan tenant thụ động (D29) — xem mục 5.
8. **Base Entity thống nhất** — mọi bảng đều có `id`, `created_at`, `updated_at`, `deleted_at` (soft-delete), cập nhật `updated_at` tự động bằng trigger — xem mục 2.0.
9. **Không rải cột `*_url` trên nhiều bảng.** Toàn bộ ảnh/file (avatar, ảnh phòng, ảnh tòa, CCCD, hợp đồng ký, ảnh công tơ, ảnh sự cố, file chat) đi qua **1 bảng `Media` polymorphic duy nhất** — xem mục 2.21.
10. **Đơn giá & phí định kỳ là cấu hình versioned theo ngày hiệu lực (`UtilityRatePolicy`, `RecurringFee`)** — không phải số cứng trên bảng phòng; hóa đơn **snapshot** cấu hình đã dùng (`utility_breakdown`, `fees_breakdown`) và bất biến sau khi phát hành (xem `utility-billing-calculations.md`). Đóng open question #6 (flat hay bậc thang EVN) theo **D30**.

---

## 2. Danh sách Entity

> **Quy ước cột "Ví dụ":** các cột PK (`id`) và FK (`*_id`) **không kèm example value** (uuid do DB sinh; tham chiếu thấy rõ ở tên cột + ràng buộc FK). Ví dụ chỉ minh hoạ dữ liệu nghiệp vụ thật (tên, số, enum, jsonb…). Trong ví dụ jsonb, `<uuid>` = placeholder cho id thật.

### 2.0 Base Entity (quy ước áp dụng cho mọi bảng bên dưới)

| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK, default `gen_random_uuid()` | | |
| created_at | timestamptz | NOT NULL, default `now()` | | `2026-09-05T10:00:00Z` |
| updated_at | timestamptz | NOT NULL, default `now()` | tự cập nhật bằng trigger `set_updated_at()` mỗi lần `UPDATE` | `2026-09-05T10:00:00Z` |
| deleted_at | timestamptz | nullable | quy ước soft-delete: `NULL` = còn tồn tại. Query mặc định luôn thêm `WHERE deleted_at IS NULL`. Với bảng mang tính chứng từ/audit (`invoice`, `payment`, `meter_reading`...) cột này gần như không dùng tới trong nghiệp vụ (không "xoá" hoá đơn) nhưng vẫn giữ để đồng nhất schema. | `NULL` |

Mọi entity ở mục 2.1 → 2.21 dưới đây được hiểu là **kế thừa 4 field trên** (không lặp lại trong từng bảng để bảng gọn). Các unique/partial index có điều kiện trạng thái (vd 1 hợp đồng active/phòng) đều kèm thêm `AND deleted_at IS NULL`.

### 2.1 User
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| phone | varchar(15) | UNIQUE, NOT NULL | định danh chính (VN) | `0901234567` |
| email | varchar | UNIQUE, nullable | | `lan@example.com` |
| password_hash | varchar | NOT NULL | | `$2a$10$N9qo8uLOickgx2ZMRZoMye…` |
| full_name | varchar | NOT NULL | | `Lê Văn An` |
| roles | enum[] (`landlord`,`tenant`,`admin`) | NOT NULL, default `{}` | **D13** — mảng, không phải 1 giá trị | `['landlord']` |

> Ảnh đại diện: **không có cột `avatar_url`** — lấy qua `Media(owner_type='user', owner_id=User.id, purpose='avatar')`.

### 2.2 LandlordProfile
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | 1-1 | |
| user_id | uuid | FK→User, UNIQUE, NOT NULL | 1-1, chỉ tồn tại nếu user có role landlord | |
| elec_policy_id | uuid | FK→UtilityRatePolicy, **nullable** | **D30** — đơn giá điện mặc định (đáy chuỗi kế thừa); **D32** — NULL = chưa cấu hình, block khi lập hóa đơn (EC3 `RATE_MISSING`), không block ở login | `NULL` |
| water_policy_id | uuid | FK→UtilityRatePolicy, **nullable** | **D30**, **D32** | `NULL` |
| default_settings | jsonb | nullable | cấu hình invoice/contract mặc định | `{"invoice_due_day":5, "remind_after_due_days":3}` |

### 2.3 Building
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| landlord_owner_id | uuid | FK→User, **nullable** | building **không bắt buộc** có chủ (**D25**) | |
| name | varchar | NOT NULL | | `Nhà trọ Thanh Xuân` |
| address | varchar | NOT NULL | | `12 Nguyễn Trãi, Thanh Xuân, HN` |
| latitude | decimal(9,6) | nullable, CHECK `[-90,90]` | định vị trên bản đồ | `20.995100` |
| longitude | decimal(9,6) | nullable, CHECK `[-180,180]` | định vị trên bản đồ; index `(latitude, longitude)` phục vụ tìm theo khu vực (bounding-box). Nếu cần tìm bán kính chính xác, cân nhắc bật PostGIS ở Phase 1+ | `105.816649` |
| elec_policy_id | uuid | FK→UtilityRatePolicy, nullable | **D30** — policy cấp tòa thắng; NULL = kế thừa LandlordProfile | `NULL` (kế thừa landlord) |
| water_policy_id | uuid | FK→UtilityRatePolicy, nullable | **D30** | `NULL` (kế thừa landlord) |
| property_type | varchar | NOT NULL, default `'long_term'` | **D9** — field mở cho Phase 1+ | `'long_term'` |

> Ảnh tòa nhà (bìa + gallery): `Media(owner_type='building', purpose='cover_photo'|'gallery_photo')`.

### 2.4 Floor (optional)
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| building_id | uuid | FK→Building, NOT NULL | | |
| name | varchar | NOT NULL | vd "Tầng 2" | `Tầng 2` |
| owner_id_hint | uuid | FK→User, **nullable** | chỉ gợi ý, **không phải nguồn chân lý** (**D25** — Room.owner_id luôn thắng) | |

### 2.5 Room
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| building_id | uuid | FK→Building, NOT NULL | | |
| floor_id | uuid | FK→Floor, nullable | | |
| owner_id | uuid | FK→User, **NOT NULL** | **D25 — bắt buộc, 1 chủ/phòng** | |
| name | varchar | NOT NULL | | `P.201` |
| area_m2 | decimal | nullable | | `18.5` |
| amenities | jsonb | nullable | | `{"aircon":true,"fridge":false,"wc_inside":true}` |
| max_occupancy | int | NOT NULL | **D21** hard filter ghép bạn | `3` |
| gender_policy | enum (`any`,`male_only`,`female_only`) | default `any` | **D21** | `any` |
| house_rules | text | nullable | **D21** | `Không hút thuốc trong phòng` |
| base_rent_price | decimal | NOT NULL | | `3500000` |
| elec_policy_id | uuid | FK→UtilityRatePolicy, nullable | **D30** — NULL = kế thừa tòa → landlord | `NULL` |
| water_policy_id | uuid | FK→UtilityRatePolicy, nullable | **D30** | `override riêng phòng` |
| status | enum (`available`,`occupied`,`maintenance`) | cached/derived | nguồn chân lý = Contract active; cache để query nhanh cho dashboard (**D20**) | `occupied` |

> Ảnh phòng (bìa + gallery): `Media(owner_type='room', purpose='cover_photo'|'gallery_photo')`.

### 2.6 Contract
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| room_id | uuid | FK→Room, NOT NULL | | |
| issued_by_user_id | uuid | FK→User, NOT NULL | = Room.owner_id (**D25**) | |
| lead_tenant_user_id | uuid | FK→User, **nullable** | nullable để hỗ trợ tenant chưa có account (**D29**); nếu null thì lưu tên/SĐT trực tiếp trên contract | `NULL` |
| lead_tenant_name / lead_tenant_phone | varchar | nullable | dùng khi tenant không có account | `Trần Văn B` / `0912345678` |
| status | enum (`draft`,`signed`,`active`,`expired`,`terminated`) | NOT NULL default `draft` | | `active` |
| signature_mode | enum (`template_upload`) | NOT NULL | **D18** — chỉ 1 giá trị, không còn e_sign/e_ack | `template_upload` |
| signed_at | timestamp | nullable | | `2026-09-01T10:00:00Z` |
| parsed_fields | jsonb | nullable | field OCR/parse từ PDF ký — chỉ hỗ trợ, không phải nguồn chuẩn (**D18**) | `{"start_date":"2026-09-01","deposit_amount":7000000}` |
| deposit_amount | decimal | NOT NULL | | `7000000` |
| monthly_rent | decimal | NOT NULL | | `3500000` |
| start_date / end_date | date | NOT NULL | | `2026-09-01` / `2027-08-31` |
| terms | text | nullable | | `Đóng tiền trước ngày 5 hàng tháng…` |
| payment_config | enum (`representative`,`shared_tracking`) | NOT NULL default `representative` | **D22** — chỉ áp dụng khi ở ghép | `representative` |
| vehicle_count | int | **nullable** | **D32** — số xe gửi tại nhà trọ, kê khai lúc tạo/cập nhật HĐ; `NULL` = chưa khai → block phí `per_vehicle` (EC8); `0` = không gửi xe | `1` |
| deposit_settled | boolean | default false | cờ "đã thanh lý cọc" (đề xuất trong audit GĐ6) | `false` |

> Mẫu HĐ / file ký: `Media(owner_type='contract', purpose='contract_template'|'contract_signed')` — file ký (`contract_signed`) vẫn là **nguồn chuẩn pháp lý**, `parsed_fields` chỉ hỗ trợ tra cứu.

**Index quan trọng:** partial unique index `(room_id) WHERE status = 'active'` — chỉ 1 hợp đồng active/phòng.

### 2.7 ContractMember (thành viên ở ghép + CCCD)
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| contract_id | uuid | FK→Contract, NOT NULL | | |
| user_id | uuid | FK→User, **nullable** | nullable nếu tenant không có account (**D29**) | `NULL` |
| full_name | varchar | NOT NULL | | `Nguyễn Thị C` |
| phone | varchar | nullable | | `0921234567` |
| is_lead | boolean | NOT NULL default false | | `true` |
| cccd_ocr_data | jsonb | nullable | **D17/5.6** — số, họ tên, ngày sinh, địa chỉ (OCR MVP; dữ liệu có cấu trúc, không phải file) | `{"number":"0792…","full_name":"Nguyễn Thị C"}` |
| share_amount | decimal | nullable | dùng khi `payment_config = shared_tracking` (**D22**) | `NULL` |
| share_paid_status | enum (`unpaid`,`paid`) | nullable | chỉ dùng khi shared_tracking | `NULL` |

> Ảnh CCCD mặt trước/sau: `Media(owner_type='contract_member', purpose='cccd_front'|'cccd_back')` — **D17**, chụp 1 lần. **`ContractMember` là nguồn đếm `head_count`** cho `rate_kind='per_head'` và `fee_kind='per_head'` (xem `utility-billing-calculations.md` §3).

### 2.8 UtilityRatePolicy — cấu hình đơn giá điện/nước (ĐƠN GIÁ VERSIONED)

> **Bảng mới theo D30** (đóng open question #6: flat vs bậc thang EVN). Giữ nguyên thứ tự ưu tiên D16: `Room.elec_policy_id → Building.elec_policy_id → LandlordProfile.elec_policy_id`.
> **Cách tính → `utility-billing-calculations.md` §4–§6.**

| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| landlord_owner_id | uuid | FK→User, NOT NULL | quyền sở hữu (**D25**) | |
| scope | enum (`landlord`,`building`,`room`) | NOT NULL | cấp áp dụng; `landlord` = mặc định cả nhà (trỏ từ `LandlordProfile.elec/water_policy_id`); scope thực tế thể hiện ở cột ID trên bảng chủ (profile/tòa/phòng) | `room` |
| room_id | uuid | FK→Room, nullable | bắt buộc nếu `scope='room'` | |
| building_id | uuid | FK→Building, nullable | bắt buộc nếu `scope='building'` | `NULL` |
| utility_type | enum (`electricity`,`water`) | NOT NULL | | `water` |
| rate_kind | enum (`flat`,`tiered`,`per_head`) | NOT NULL | `flat`: đồng giá / `tiered`: bậc thang / `per_head`: khoán đầu người. **D33 — điện chỉ `flat`\|`tiered`** (vd `electricity` + `per_head` bị service reject); `per_head` chỉ áp nước + phí định kỳ F2 | `per_head` |
| unit_price | decimal | nullable | `flat`: đ/kWh hoặc đ/m³; `per_head`: đ/người/tháng; `tiered`: NULL | `80000` |
| steps | jsonb | nullable | `tiered`: `[{from,to,price}]`, `to=null` = mở ∞ (vd EVN 6 bậc, bậc 3 TT 25/2018, nước định mức) | `NULL` |
| name | varchar | NOT NULL | nhãn hiển thị | `Nước khoán đầu người` |
| effective_from | date | NOT NULL | bắt đầu hiệu lực | `2026-09-01` |
| effective_to | date | nullable | NULL = còn hiệu lực | `NULL` |
| is_active | boolean | default true | bản mới tạo **mặc định đang chạy**; `false` = tắt → resolve bỏ qua, kế thừa cấp trên | `true` |

> **Index:** `(utility_type, landlord_owner_id)` + `(room_id)`/`(building_id)` khi có. Ràng buộc `rate_kind` ↔ `unit_price`/`steps` kiểm tra ở service; preset EVN/TT25 = seed config, không phải bảng riêng.
> **D31 — bậc thang `steps` chỉ đến từ preset seed, không nhập tay trong UI thường** (EVN 6 bậc / Bậc 3 TT 25/2018 / nước địa phương). Landlord nhập tay tối đa `unit_price` cho `flat`/`per_head`. Đổi giá = tạo policy mới `effective_from`, không sửa policy cũ. Chi tiết UX → `landlord_user_flow.md` §3 (onboarding) + §10 (Module 6 — đổi giá/override).

### 2.9 RecurringFee — phí định kỳ ngoài điện/nước (Wifi, vệ sinh, gửi xe, QLVH…)

> **Bảng mới theo D30.** Tính theo `fee_kind` (cách tính) + `effective_from/to` (versioned).
> **Cách tính → `utility-billing-calculations.md` §7.**
> **D32 — preset phí = seed, không phải bảng riêng** (Wifi/QLVH/Gửi xe/Vệ sinh rác): chọn preset auto điền `fee_kind` + `unit_price` mẫu, chủ trọ xác nhận/chỉnh. `per_vehicle` lấy `contract.vehicle_count` (kê khai ở HĐ), không nhập mỗi kỳ.

| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| landlord_owner_id | uuid | FK→User, NOT NULL | quyền sở hữu (**D25**) | |
| scope | enum (`landlord`,`building`,`room`) | NOT NULL | `landlord`: mặc định áp **mọi phòng mọi tòa** của chủ trọ; `building`: mỗi phòng trong tòa đều phát sinh; `room`: chỉ phòng đó | `room` |
| room_id | uuid | FK→Room, nullable | bắt buộc nếu `scope='room'` | |
| building_id | uuid | FK→Building, nullable | bắt buộc nếu `scope='building'` | `NULL` |
| name | varchar | NOT NULL | | `Wifi` |
| fee_kind | enum (`fixed_per_period`,`per_head`,`per_area_m2`,`per_vehicle`) | NOT NULL | cố định/phóng / theo người / theo m² / theo xe | `fixed_per_period` |
| unit_price | decimal | NOT NULL | VD: wifi 100.000đ/phòng; xe máy 150.000đ/xe; QLVH 10.000đ/m² | `100000` |
| effective_from | date | NOT NULL | | `2026-09-01` |
| effective_to | date | nullable | | `NULL` |
| is_active | boolean | default true | bản mới tạo **mặc định đang chạy**; `false` = tắt cấp này → **bỏ qua và kế thừa cấp trên** (cùng loại phí, thứ tự room > building > landlord) | `true` |

### 2.10 MeterReading
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| room_id | uuid | FK→Room, NOT NULL | | |
| utility_type | enum (`electricity`,`water`) | NOT NULL | **thực tế mỗi phòng 2 công tơ riêng (điện + nước)** — 1 bản ghi/loại/kỳ | `electricity` |
| period | varchar(7) (`YYYY-MM`) | NOT NULL | | `2026-09` |
| previous_reading | decimal | NOT NULL | kỳ đầu = baseline chỉ số lúc bàn giao §5 do **OCR tự đọc + hiệu chỉnh tay nếu sai/mờ (D34/D35)**; kỳ sau = current_reading kỳ trước | `1200` |
| current_reading | decimal | NOT NULL | | `1380` |
| consumption | decimal | GENERATED (current − previous) | | `180` |
| reading_date | date | nullable | ngày chốt thực tế (dọn vào/ra giữa tháng) | `2026-09-30` |
| is_baseline | boolean | default false | kỳ đầu hoặc sau khi thay đồng hồ — OCR + hiệu chỉnh tay nếu sai (D34/D35) | `false` |

> Ảnh đối chứng công tơ theo **từng loại**: `Media(owner_type='meter_reading', purpose='meter_reading_evidence')` — nghiệp vụ yêu cầu tối thiểu 1 ảnh trước khi xác nhận (ràng buộc ở service, không phải DB). **Cách tính consumption & xử lý đồng hồ reset → `utility-billing-calculations.md` §3/EC1.** `created_at` (chuẩn mọi bảng) = thời điểm chốt/xác nhận — bản ghi chỉ được insert lúc chủ trọ bấm Xác nhận (§6, không có draft), nên không cần cột `confirmed_at` riêng.

**Index:** UNIQUE `(room_id, utility_type, period)`.

### 2.11 Invoice
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| contract_id | uuid | FK→Contract, NOT NULL | | |
| period | varchar(7) | NOT NULL | | `2026-09` |
| rent_amount | decimal | NOT NULL | tiền phòng **prorated** theo §8 (`monthly_rent × ratio`); denormalized cho Dashboard (D20). Điện/nước/phí **đọc từ `utility_breakdown`/`fees_breakdown`** (snapshot = nguồn duy nhất, không cột kép — D37) | `3500000` |
| utility_breakdown | jsonb | nullable | **D30 — snapshot bất biến** cấu hình đã dùng: policy, chỉ số cũ/mới, lượng, tier_result, head_count | `{"electricity":{"qty_kwh":180,"amount":720000}, "water":{"head_count":3,"amount":240000}}` |
| fees_breakdown | jsonb | nullable | **D30 — snapshot phí định kỳ** `[{fee_id,name,fee_kind,quantity,unit_price,prorate_ratio,amount}]` | `[{"fee_id":"<uuid>","name":"Wifi","fee_kind":"fixed_per_period","quantity":1,"unit_price":100000,"amount":100000}]` |
| other_fees | jsonb | nullable | phí 1 lần / ngoài lệ (không trong cấu hình). **D33 — cho phép `amount` ÂM = giảm trừ/miễn giảm** (snapshot giữ dấu âm) | `[{"name":"Vệ sinh lễ","amount":50000}, {"name":"Giảm trừ hỗ trợ","amount":-700000}]` |
| total_amount | decimal | NOT NULL | **= làm tròn tổng** (round-half-up → hàng nghìn), kiểm tra khớp dòng; **≥ 0** (`TOTAL_NEGATIVE` — D33⑥) | `4610000` |
| status | enum (`pending`,`partially_paid`,`paid`,`overdue`,`void`) | NOT NULL default `pending` | **D33③ — `partially_paid`** = đã thu được tiền nhưng chưa đủ (Σ success < total); `paid` khi Σ ≥ total; `overdue` khi quá hạn còn thiếu; **không sửa sau khi gửi** — void + tạo mới (audit trail, **D18/D20**) | `pending` |
| voided_invoice_id | uuid | FK→Invoice, nullable, self-ref | hóa đơn **MỚI** trỏ tới bản cũ **đã bị void** mà nó thay thế (new → old); bản cũ giữ `status='void'`, **không xóa** (audit D18/D20); webhook trễ tới bản void → cờ cảnh báo D33⑤ | `NULL` |
| issued_at | timestamp | nullable | thời điểm **Phát hành** (rời `pending`) — audit D18/D20; `NULL` khi còn pending (D33② auto-sinh chưa phát hành) | `2026-09-30T20:15:00Z` |
| due_date | date | nullable | **= `issued_at + N ngày`** (N cấu hình, mặc định 5 — D37); gốc quét định kỳ → `overdue` (landlord §7) | `2026-10-05` |
| note | text | nullable | | `Tháng nhập cư, prorate từ 15/09` |

> **Cách tính toàn bộ (điện/nước/phí/prorate/làm tròn/block lỗi) → `utility-billing-calculations.md` §2–§11.** UNIQUE **partial** `(contract_id, period) WHERE status != 'void'` — **D33①** cho phép tạo hóa đơn thay thế sau khi void bản sai (bản cũ giữ audit). **D33② — Invoice pending auto-sinh theo TỪNG PHÒNG** khi phòng đủ 2 MeterReading + policy OK (không batch toàn kỳ). **`issued_at`/`due_date` set khi Phát hành (D37); `due_date = issued_at + N ngày` (N cấu hình, mặc định 5) — quét định kỳ quá `due_date` còn nợ → `overdue`.**

### 2.12 Payment
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| invoice_id | uuid | FK→Invoice, NOT NULL | 1 Invoice — N Payment (retry) | |
| method | enum (`vnpay`,`momo`,`cash`,`mock`) | NOT NULL | | `vnpay` |
| status | enum (`pending`,`success`,`failed`) | NOT NULL | | `success` |
| amount | decimal | NOT NULL | **số tiền THỰC NHẬN** (có thể ≠ total khi trả một phần; thu dư vẫn ghi đủ số nhận) | `2000000` |
| transaction_id | varchar | nullable | null cho cash | `VNPAY-20260930183021` |
| raw_gateway_response | jsonb | nullable | bằng chứng đối soát QR | `{"bank":"VCB","amount":4610000}` |
| paid_by_contract_member_id | uuid | FK→ContractMember, nullable | dùng khi shared_tracking (D22) | `NULL` |

> **D33③ — trả một phần / thu dư-đủ:** đối soát theo **mã định danh hóa đơn** (không theo amount — khách trả thiếu/dư vẫn khớp). Invoice → `partially_paid` khi Σ success ∈ (0, total); `paid` khi Σ ≥ total. Thu dư: KHÔNG hoàn tiền/bù trừ tự động — tab History hiển thị nhắc "thu dư X / còn thiếu Y" (D33). **D33⑤ — Payment success tới Invoice `void`:** không set `paid`, đánh cờ cảnh báo chủ trọ đối soát.
| created_at | timestamp | | | `2026-09-30T18:30:21Z` |

### 2.13 IssueReport
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| room_id | uuid | FK→Room, NOT NULL | | |
| conversation_id | uuid | FK→Conversation, nullable | | |
| reported_by_user_id | uuid | FK→User, **nullable** | null nếu landlord tự tạo thay tenant passive (**D29**) | `NULL` |
| status | enum (`open`,`in_progress`,`resolved`) | NOT NULL default `open` | | `open` |
| title / description | varchar / text | NOT NULL | | `Đèn cháy` / `Bóng đèn phòng ngủ cháy 2 bóng` |
| resolved_at | timestamp | nullable | | `NULL` |
| resolution_note | text | nullable | | `NULL` |

> Ảnh sự cố: `Media(owner_type='issue_report', purpose='issue_photo')`.

### 2.14 Conversation (Property Chat — D24′)
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| kind | enum (`room`,`building`) | NOT NULL | | `room` |
| room_id | uuid | FK→Room, nullable | bắt buộc nếu kind=room | |
| building_id | uuid | FK→Building, nullable | bắt buộc nếu kind=building | `NULL` |

### 2.15 ConversationMember
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| conversation_id | uuid | FK→Conversation, NOT NULL | | |
| user_id | uuid | FK→User, NOT NULL | | |
| joined_at | timestamp | | | `2026-09-01T10:05:00Z` |

**Index:** UNIQUE `(conversation_id, user_id)`.

### 2.16 Message
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| conversation_id | uuid | FK→Conversation, NOT NULL | | |
| sender_user_id | uuid | FK→User, **nullable** | null = bot | `NULL` |
| type | enum (`text`,`image`,`file`,`bot`) | NOT NULL | | `bot` |
| content | text | nullable | | `Đã chốt số điện tháng 09: 180 kWh` |
| metadata | jsonb | nullable | card payload: `{invoice_id}`, `{issue_id}`, `{meter_reading_id}`,... + mention list | `{"meter_reading_id":"<uuid>"}` |

> File/ảnh đính kèm (khi `type = image|file`): `Media(owner_type='message', purpose='chat_attachment')`.

### 2.17 RoommateProfile
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| user_id | uuid | FK→User, UNIQUE, NOT NULL | chỉ tenant có account | |
| lifestyle | jsonb | nullable | | `{"sleep":"23h-6h","pets":false,"smoking":false}` |
| personality | jsonb | nullable | | `{"introvert":true,"noisy_level":2}` |
| budget_min / budget_max | decimal | nullable | | `2000000` / `3500000` |
| bio | text | nullable | | `Hiền lành, sạch sẽ, dậy sớm` |
| id_verified | boolean | default false | badge xác minh tự nguyện (**D26**) | `true` |

### 2.18 MatchRequest
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| requester_user_id | uuid | FK→User, NOT NULL | | |
| target_user_id | uuid | FK→User, NOT NULL | | |
| room_id | uuid | FK→Room, nullable | ngữ cảnh áp constraint hard-filter (**D21**) | |
| status | enum (`pending`,`accepted`,`rejected`) | NOT NULL default `pending` | | `accepted` |
| ai_score | decimal | nullable | **D28**, Stretch | `87.5` |
| ai_advice | text | nullable | **D28** | `Hai người cùng giờ ngủ, ít rủi ro xung đột` |

**Index:** UNIQUE `(requester_user_id, target_user_id)` — cache mỗi cặp 1 lần (**D28**).

### 2.19 TenantHistory (Stretch — D26, consent-based)
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| tenant_user_id | uuid | FK→User, NOT NULL | | |
| contract_id | uuid | FK→Contract, NOT NULL | | |
| on_time_payment_score | decimal | nullable | | `95` |
| review_text | text | nullable | | `Đóng tiền đúng hạn, phòng sạch` |
| consent_given | boolean | NOT NULL default false | **bắt buộc true mới hiển thị** (PDPD Art.11) | `true` |
| visible | boolean | default false | | `true` |

### 2.20 Notification (Stretch)
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| user_id | uuid | FK→User, NOT NULL | | |
| type | varchar | NOT NULL | invoice_due, contract_expiry,... | `invoice_due` |
| payload | jsonb | nullable | | `{"invoice_id":"<uuid>","amount":4610000}` |
| read_at | timestamp | nullable | | `NULL` |

### 2.21 Media (polymorphic — gom mọi file/ảnh của hệ thống)

**Nghiên cứu 2 hướng thiết kế** cho bài toán "8 loại entity đều có ảnh/file, tránh rải cột `*_url`":

| Hướng | Ưu điểm | Nhược điểm |
|---|---|---|
| **A. 1 bảng polymorphic** `media(owner_type, owner_id, purpose, ...)` — mô hình dùng bởi Rails Active Storage, Django `GenericForeignKey`, kiểu Instagram/Airbnb | 1 chỗ duy nhất quản lý file (upload, xoá, CDN, resize); thêm loại entity mới không cần bảng mới; dễ làm gallery + ảnh bìa (`is_cover`) + audit ai upload | `owner_id` **không có FK thật** (1 cột không FK được nhiều bảng) → toàn vẹn tham chiếu phải kiểm tra ở tầng service |
| **B. Bảng join riêng từng entity** (`RoomPhoto`, `BuildingPhoto`, `ContractDocument`, `IssuePhoto`, `ChatAttachment`,...) | FK thật, DB tự đảm bảo toàn vẹn tham chiếu | 6-8 bảng gần như trùng cấu trúc (id, url, order, uploaded_by, timestamps); thêm entity mới lại phải thêm bảng + migration mới |

**Chọn hướng A** cho MVP: quy mô đồ án không cần multi-tenant phức tạp, và số lượng entity có file (8 loại: user, room, building, contract, contract_member, meter_reading, issue_report, message) đủ lớn để hướng B gây trùng lặp đáng kể. Rủi ro mất toàn vẹn tham chiếu được giảm bằng cách:
- `owner_type` là enum cố định (không phải string tự do)
- `purpose` enum ràng buộc rõ vai trò file trong từng loại owner (vd `purpose='avatar'` chỉ hợp lệ khi `owner_type='user'`) — kiểm tra ở service layer khi insert
- 1 index `(owner_type, owner_id)` để query nhanh toàn bộ media của 1 entity

| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| owner_type | enum (`user`,`room`,`building`,`contract`,`contract_member`,`meter_reading`,`issue_report`,`message`) | NOT NULL | | `room` |
| owner_id | uuid | NOT NULL | **không có FK thật** — xem giải thích trên | |
| purpose | enum (`avatar`,`cover_photo`,`gallery_photo`,`cccd_front`,`cccd_back`,`contract_template`,`contract_signed`,`meter_reading_evidence`,`issue_photo`,`chat_attachment`) | NOT NULL | vai trò của file trong owner đó | `cover_photo` |
| file_type | enum (`image`,`document`,`video`,`other`) | NOT NULL default `image` | | `image` |
| url | varchar | NOT NULL | | `https://cdn.pbl6.dev/room/<room_id>/cover.webp` |
| thumbnail_url | varchar | nullable | | `https://cdn.pbl6.dev/room/<room_id>/cover_thumb.webp` |
| mime_type | varchar | nullable | | `image/webp` |
| size_bytes | bigint | nullable | | `245000` |
| width / height | int | nullable | chỉ dùng khi `file_type='image'` | `1200` / `800` |
| display_order | int | NOT NULL default 0 | thứ tự trong gallery (room/building) | `1` |
| is_cover | boolean | NOT NULL default false | UNIQUE partial `(owner_type, owner_id) WHERE is_cover=true` — mỗi entity chỉ 1 ảnh bìa | `true` |
| uploaded_by_user_id | uuid | FK→User, nullable | | |

**Phân quyền Media** (bổ sung vào ma trận mục 5.2): quyền upload/xoá = quyền sửa entity cha tương ứng (vd landlord chỉ upload được ảnh cho `Room` mình sở hữu — check qua `Room.owner_id`, không phải role suông); quyền đọc = quyền đọc entity cha (ảnh phòng `available` là public, ảnh CCCD chỉ landlord sở hữu HĐ + chính chủ CCCD + admin).

---

## 3. Sơ đồ quan hệ (ERD)

Xem file đính kèm `erd.mermaid` để render trực quan. Tóm tắt quan hệ chính:

```
User 1--1 LandlordProfile
User 1--0..1 RoommateProfile
User 1--N Building (landlord_owner_id, nullable)
Building 1--N Floor
Building 1--N Room
Floor 1--N Room
User 1--N Room (owner_id, NOT NULL)
Room 1--N Contract
Contract 1--N ContractMember
Contract 1--N Invoice
Invoice 1--N Payment
Room 1--N MeterReading            (điện + nước: 2 bản ghi/kỳ qua utility_type)
Building 1--N UtilityRatePolicy   (policy cấp tòa; còn: room, landlord)
Room 1--N UtilityRatePolicy       (policy cấp phòng)
LandlordProfile 1--0..1 UtilityRatePolicy  (2 con trỏ: elec_policy_id, water_policy_id)
User 1--N RecurringFee            (landlord_owner_id; fee cấp landlord = mặc định cả nhà)
Building 1--N RecurringFee        (fee áp mọi phòng trong tòa)
Room 1--N RecurringFee            (fee riêng phòng)
Room 1--N IssueReport
Room 1--0..1 Conversation (kind=room)
Building 1--0..1 Conversation (kind=building)
Conversation 1--N ConversationMember
Conversation 1--N Message
User 1--N MatchRequest (requester / target)
User 1--N TenantHistory
User 1--N Notification
User/Room/Building/Contract/ContractMember/MeterReading/IssueReport/Message
    1--N Media (polymorphic qua owner_type + owner_id, không FK thật)
```

> Lưu ý: `UtilityRatePolicy` được link **2 chiều** — bảng cấu hình giữ `elec_policy_id`/`water_policy_id` (con trỏ từ phòng/tòa/profile) đồng thời policy tự khai `scope`/`room_id`/`building_id`. Con trỏ trên Room/Building/LandlordProfile là nguồn chân lý cho chain resolution (D16/D30); trường `scope`/`*_id` trong policy phục vụ quản lý/gũi gọn (vd hiển thị danh sách, export).

---

## 4. Traceability theo quyết định (D-number)

| Bảng | D áp dụng |
|---|---|
| Room.owner_id NOT NULL, Building không bắt buộc owner, bỏ Manager | D25 |
| **UtilityRatePolicy, RecurringFee, Invoice.utility_breakdown/fees_breakdown, MeterReading.utility_type** | **D30** — đơn giá điện/nước versioned (flat/bậc thang/khoán đầu người) + phí định kỳ; đóng open question #6; mở rộng D16 (giữ thứ tự room→building→landlord) |
| **UtilityRatePolicy.steps bậc thang chỉ từ preset seed (EVN/TT25/nước địa phương), không nhập tay trong UI; đổi giá = policy mới `effective_from`** | **D31** — preset thân thiện landlord lớn tuổi; thuật toán `calcTiered` là code, giá là config |
| **LandlordProfile.elec_policy_id/water_policy_id nullable (NULL = chưa cấu hình), Contract.vehicle_count kê khai ở HĐ, phí 1 lần `other_fees`, preset phí seed** | **D32** — onboarding không chặn (banner + block tại hóa đơn), xe theo HĐ, preset phí |
| **Invoice status `partially_paid`, UNIQUE partial `(contract_id, period) WHERE status != 'void'`, Payment đối soát theo invoice_id + thu dư/thiếu nhắc ở History, Invoice auto-sinh theo phòng, `other_fees` âm (total ≥ 0), `rate_kind` điện chỉ flat/tiered** | **D33** — thanh toán một phần + thu dư/thiếu nhắc, hóa đơn theo phòng, điện bỏ khoán đầu người |
| Building/Room `elec_policy_id`/`water_policy_id` (con trỏ policy) thay field decimal | D16 (nâng cấp), D30 |
| Contract.signature_mode chỉ có template_upload | D18 |
| ContractMember.share_amount, Contract.payment_config | D22 |
| ContractMember.cccd_image_url, cccd_ocr_data | D17 |
| User.roles là mảng | D13 |
| Conversation/Message | D24′ |
| MatchRequest unique(requester,target), ai_score/ai_advice | D28 |
| Room.max_occupancy/gender_policy/house_rules dùng làm hard filter | D21 |
| TenantHistory.consent_given bắt buộc | D26 |
| Contract.lead_tenant_user_id nullable, ContractMember.user_id nullable, IssueReport.reported_by_user_id nullable | D29 (zero tenant login) |
| Building.property_type mở rộng | D9 |
| Building.latitude/longitude | yêu cầu định vị bản đồ |
| Bảng Media polymorphic (thay mọi cột `*_url`/`photos`) | yêu cầu tránh rải url file |
| Base Entity (id/created_at/updated_at/deleted_at) trên mọi bảng | yêu cầu chuẩn hoá audit/soft-delete |

---

## 5. Thiết kế phân quyền theo Role (không RBAC)

### 5.1 Mô hình role

- **Không có bảng `Role` hay `Permission` riêng.** Quyền được suy ra trực tiếp từ 2 lớp kiểm tra ở tầng application (service/guard), không phải từ dữ liệu quan hệ:
  1. **Role check** — user có role cần thiết không (`landlord` / `tenant` / `admin`), lấy từ `User.roles` (mảng) — đã đúng theo **D13**.
  2. **Ownership check** — nếu resource có `owner_id`/`issued_by_user_id`/`lead_tenant_user_id`/`user_id` thì phải khớp với `request.user.id`, trừ khi role = `admin`.
- JWT payload: `{ sub: user_id, roles: ["landlord","tenant"] }` — không nhúng permission chi tiết.
- Backend dùng decorator kiểu `@Roles('landlord')` trên từng endpoint + 1 hàm `assertOwnership(resource, user)` gọi thêm trong service layer khi cần. Không cần bảng ánh xạ role↔permission vì tập hành động cố định, không thay đổi runtime.

### 5.2 Ma trận quyền theo Resource × Action × Role

| Resource | Action | landlord | tenant | admin | Ghi chú |
|---|---|---|---|---|---|
| Building/Floor/Room | Create/Update/Delete | ✅ (chỉ resource mình sở hữu) | ❌ | ✅ | ownership check qua `Room.owner_id` |
| Room | Đọc (tìm phòng available) | ✅ (mọi phòng, phục vụ ops) | ✅ (public, chỉ field public) | ✅ | tenant chỉ thấy field public khi tìm kiếm |
| UtilityRatePolicy | Create/update/deactivate | ✅ (chỉ của mình, `landlord_owner_id`) | ❌ | ✅ | đổi giá ảnh hưởng kỳ sau (D30) |
| UtilityRatePolicy | Đọc | ✅ | ✅ (qua hóa đơn/hiển thị) | ✅ | tenant đọc qua snapshot hóa đơn, không sửa |
| RecurringFee | Create/update/deactivate | ✅ (chỉ của mình) | ❌ | ✅ | |
| RecurringFee | Đọc | ✅ | ✅ (qua hóa đơn) | ✅ | |
| Contract | Create/sinh mẫu/upload file ký | ✅ (chỉ phòng mình, `issued_by_user_id`) | ❌ | ✅ | |
| Contract | Đọc | ✅ (owner) | ✅ (chỉ HĐ mình là `lead_tenant_user_id`/`ContractMember`) | ✅ | |
| MeterReading | Create/confirm | ✅ (owner phòng) | ❌ | ✅ | D29: tenant không có vai trò tạo |
| MeterReading | Đọc | ✅ | ✅ (chỉ phòng mình đang thuê) | ✅ | |
| Invoice | Create (auto)/void | ✅ (owner) | ❌ | ✅ | |
| Invoice | Đọc | ✅ (owner) | ✅ (contract của mình) | ✅ | |
| Payment | Ghi nhận cash | ✅ (owner) | ❌ | ✅ | |
| Payment | Webhook callback (VNPay/MoMo) | hệ thống (service account) | — | — | không qua user JWT |
| Payment | Đọc | ✅ (owner) | ✅ (của mình) | ✅ | |
| IssueReport | Create | ✅ (owner, tạo thay tenant passive) | ✅ (tenant tự tạo qua @issue) | ✅ | |
| IssueReport | Update status | ✅ (owner) | ❌ | ✅ | |
| Conversation/Message | Đọc/Gửi | ✅ (nếu là `ConversationMember`) | ✅ (nếu là `ConversationMember`) | ✅ | check qua bảng ConversationMember, không phải role |
| RoommateProfile | CRUD | ❌ | ✅ (của chính mình) | ✅ | landlord không tham gia (**D21** — chỉ set constraint trên Room) |
| MatchRequest | Create/Accept/Reject | ❌ | ✅ (chỉ với tư cách requester/target) | ✅ | |
| Dashboard (D20) | Đọc | ✅ (chỉ số liệu của mình) | ❌ | ✅ (toàn hệ thống) | |
| TenantHistory | Đọc | ❌ (trừ khi `visible=true` và là landlord đang xét HĐ) | ✅ (của chính mình, toggle consent) | ✅ | consent-gate ở tầng service, không phải role |
| LandlordProfile (rate policy mặc định) | CRUD | ✅ (của mình) | ❌ | ✅ | |
| User | Đọc/sửa profile | ✅/✅ (chính mình) | ✅/✅ (chính mình) | ✅ (mọi user) | |
| Media | Upload/Delete | ✅ (nếu có quyền sửa entity cha) | ✅ (nếu có quyền sửa entity cha, vd ảnh issue của mình) | ✅ | không check qua role, check qua quyền của owner_type tương ứng |
| Media | Đọc | ✅ (theo quyền đọc entity cha) | ✅ (theo quyền đọc entity cha) | ✅ | vd ảnh phòng available = public, ảnh CCCD = riêng tư |

### 5.3 Vì sao không cần RBAC đầy đủ

- Tập hành động và tài nguyên **cố định**, không có nhu cầu cấu hình quyền động theo tổ chức (không multi-tenant SaaS phân quyền tùy biến).
- Chỉ 3 role, không có phân cấp phức tạp hay custom permission theo khách hàng → bảng `Role`/`Permission`/`RolePermission` sẽ over-engineer cho MVP 13–14 tuần (đúng tinh thần D9 — ưu tiên đơn giản, tránh phức tạp không cần thiết).
- Ownership check (row-level) quan trọng hơn role check trong hệ thống này (D25) — RBAC thuần theo role sẽ không đủ, vẫn cần thêm lớp ownership dù có RBAC hay không, nên giữ đơn giản: role (coarse-grained) + ownership (fine-grained) là đủ.
- Nếu sau này cần permission tùy biến (vd. landlord có nhân viên phụ, multi-org), có thể mở rộng thêm bảng `Role`/`Permission` ở Phase 1+ mà không phá vỡ `User.roles` hiện tại (roles array vẫn dùng làm coarse filter đầu tiên).