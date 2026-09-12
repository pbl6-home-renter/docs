# Thiết kế Cơ sở dữ liệu & Phân quyền theo Role

## 1. Nguyên tắc thiết kế

1. **Ownership là nguồn chân lý phụ, không phải role.** Có role `landlord` chưa đủ — phải là đúng `Room.owner_id` / `Contract.issuer_id` mới được thao tác (D25).
2. **Trạng thái phòng là derived/cached**, nguồn chân lý là `Contract.status` đang active cho phòng đó, không phải bảng riêng (ghi chú trong decisions.md).
3. **Mọi luồng nghiệp vụ phải chạy được khi `lead_user_id` / `ContractMember.user_id` là `NULL`** cho tenant thụ động (D29) — xem mục 5.
4. **Tên khóa ngoại theo ngữ cảnh.** Dùng hậu tố `_id` ngắn, rõ (`owner_id`, `issuer_id`, `reporter_id`), không lặp lại tên bảng `User` khi ngữ cảnh đã thể hiện.
---

### 1.1 Cập nhật theo P2-01 và user flow Phase 1

Schema được rà lại theo `phase-2/discovery/product-platform-map.md` và bốn user flow Phase 1. Các tên dài được thay nhất quán như sau:

| Trước | Sau |
|---|---|
| `roles` | `role` |
| `issued_by_user_id` | `issuer_id` |
| `lead_tenant_user_id` | `lead_user_id` |
| `lead_tenant_name` / `lead_tenant_phone` | `lead_name` / `lead_phone` |
| `landlord_owner_id` | `owner_id` |
| `reported_by_user_id` | `reporter_id` |
| `sender_user_id` | `sender_id` |
| `paid_by_contract_member_id` | `payer_id` |
| `requester_user_id` / `target_user_id` | `requester_id` / `target_id` |
| `tenant_user_id` | `tenant_id` |

Ngoài các tên trên, bản này bổ sung dữ liệu còn thiếu cho P2-01: lưu phòng, duyệt BĐS, khóa tài khoản/audit, cấu hình nhắc nợ 3 cấp, notification/FCM, VietQR, mention và vòng đời checkout.

---

**Revision basis:** the supplied schema changes are applied here while retaining D30–D37 billing behavior (versioned policies, snapshots, partial payments, OCR confirmation, and issue-time due dates). The supplied removal of the invoice replacement pointer supersedes that schema detail in D37: voided invoices remain available and replacements are looked up by `contract_id`, `period`, and `issued_at`; this lookup does not encode an exact predecessor link. Older companion documents may still use previous field names.

**Naming:** fields and enum values use `snake_case`; entity labels use `PascalCase`. Use `owner_id` consistently for ownership, `electricity_policy_id`/`water_policy_id` for policy references, and explicit actor names where needed (`issued_by_user_id`, `report_by_user_id`, `sender_user_id`). `Media.owner_id` is polymorphic; `Media.user_id` identifies the uploader. Each table row defines one field. `MeterReading.utility_type` matches `UtilityRatePolicy.utility_type`; the supplied generic `name` is not used for utility classification. `ContractMember.is_lead` retains its separate representative-member meaning (D22).

## 2. Danh sách Entity

### 2.0 Base Entity (quy ước áp dụng cho mọi bảng bên dưới)

| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK, default `gen_random_uuid()` | | |
| created_at | timestamptz | NOT NULL, default `now()` | | `2026-09-05T10:00:00Z` |
| updated_at | timestamptz | NOT NULL, default `now()` | tự cập nhật bằng trigger `set_updated_at()` mỗi lần `UPDATE` | `2026-09-05T10:00:00Z` |
| is_deleted | boolean | NOT NULL, default false | Soft-delete: `false` = existing record; default queries use `WHERE is_deleted = false`. Financial/audit records are retained; voiding an invoice changes its status, not this flag. | `false` |

Mọi entity ở mục 2.1 → 2.27 dưới đây được hiểu là **kế thừa 4 field trên** (không lặp lại trong từng bảng để bảng gọn). Các unique/partial index có điều kiện trạng thái (vd 1 hợp đồng active/phòng) đều kèm thêm `AND deleted_at IS NULL`.

### 2.1 User
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| phone | varchar(15) | UNIQUE, NOT NULL | định danh chính (VN) | `0901234567` |
| email | varchar | UNIQUE, nullable | | `lan@example.com` |
| password_hash | varchar | NOT NULL | | `$2a$10$N9qo8uLOickgx2ZMRZoMye…` |
| full_name | varchar | NOT NULL | | `Lê Văn An` |
| role | enum (`landlord`,`tenant`,`admin`) | NOT NULL | User flow SoT: một tài khoản có đúng một role bất biến; role khác dùng tài khoản riêng | `landlord` |
| status | enum (`active`,`locked`) | NOT NULL default `active` | Tenant bị khóa vẫn được xem/thanh toán HĐ hiện tại ở tầng quyền; landlord bị khóa không đăng nhập được portal | `active` |
| lock_reason | varchar | nullable | lý do admin khóa tài khoản | `Spam listing` |
| locked_at | timestamptz | nullable | | `NULL` |

> Ảnh đại diện: **không có cột `avatar_url`** — lấy qua `Media(owner_type='user', owner_id=User.id, purpose='avatar')`. Tạo partial unique index trên `(role) WHERE role='admin' AND deleted_at IS NULL` để bảo đảm một admin duy nhất.

### 2.2 FavoriteRoom (phòng đã lưu)
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| user_id | uuid | FK→User, NOT NULL | tenant lưu phòng cần đăng nhập | |
| room_id | uuid | FK→Room, NOT NULL | | |

**Index:** UNIQUE `(user_id, room_id)` khi `deleted_at IS NULL`.

### 2.3 LandlordProfile
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | 1-1 | |
| user_id | uuid | FK→User, UNIQUE, NOT NULL | 1-1, chỉ tồn tại nếu user có role landlord | |
| electricity_policy_id | uuid | FK→UtilityRatePolicy, **nullable** | **D30** — đơn giá điện mặc định (đáy chuỗi kế thừa); **D32** — NULL = chưa cấu hình, block khi lập hóa đơn (EC3 `RATE_MISSING`), không block ở login | `NULL` |
| water_policy_id | uuid | FK→UtilityRatePolicy, **nullable** | **D30**, **D32** | `NULL` |
> Cấu hình hạn thanh toán/nhắc nợ không lưu trong JSON: dùng `BillingSetting` (§2.11) để kế thừa theo profile → building → room.

### 2.4 Building
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| submitted_by | uuid | FK→User, NOT NULL | landlord tạo và nộp hồ sơ BĐS; **không** là nguồn ownership (D25) | |
| name | varchar | NOT NULL | | `Nhà trọ Thanh Xuân` |
| address | varchar | NOT NULL | | `12 Nguyễn Trãi, Thanh Xuân, HN` |
| latitude | decimal(9,6) | nullable, CHECK `[-90,90]` | định vị trên bản đồ | `20.995100` |
| longitude | decimal(9,6) | nullable, CHECK `[-180,180]` | định vị trên bản đồ; index `(latitude, longitude)` phục vụ tìm theo khu vực (bounding-box). Nếu cần tìm bán kính chính xác, cân nhắc bật PostGIS ở Phase 1+ | `105.816649` |
| electricity_policy_id | uuid | FK→UtilityRatePolicy, nullable | **D30** — policy cấp tòa thắng; NULL = kế thừa LandlordProfile | `NULL` (kế thừa landlord) |
| water_policy_id | uuid | FK→UtilityRatePolicy, nullable | **D30** | `NULL` (kế thừa landlord) |
| property_type | varchar | NOT NULL, default `'long_term'` | **D9** — field mở cho Phase 1+ | `'long_term'` |
| approval_status | enum (`pending`,`approved`,`rejected`) | NOT NULL default `pending` | chỉ BĐS `approved` mới tạo phòng, phát hành HĐ và hiển thị công khai | `pending` |
| reviewed_by | uuid | FK→User, nullable | admin duyệt/từ chối | |
| reviewed_at | timestamptz | nullable | | |
| reject_reason | text | nullable | bắt buộc khi `approval_status='rejected'` | `Ảnh giấy tờ mờ` |

> Ảnh tòa nhà (bìa + gallery) và giấy tờ sở hữu bắt buộc: `Media(owner_type='building', purpose='cover_photo'|'gallery_photo'|'ownership_proof')`. Trước khi gửi duyệt phải có ít nhất một `ownership_proof` (service check).

### 2.5 Floor (optional)
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| building_id | uuid | FK→Building, NOT NULL | | |
| name | varchar | NOT NULL | vd "Tầng 2" | `Tầng 2` |
| owner_hint | uuid | FK→User, **nullable** | chỉ gợi ý, **không phải nguồn chân lý** (**D25** — Room.owner_id luôn thắng) | |

### 2.6 Room
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| building_id | uuid | FK→Building, NOT NULL | | |
| floor_id | uuid | FK→Floor, nullable | | |
| owner_id | uuid | FK→User, **NOT NULL** | **D25 — bắt buộc, 1 chủ/phòng** | |
| name | varchar | NOT NULL | | `P.201` |
| area | decimal | nullable | Area in m²; used by `per_area_m2` fees | `18.5` |
| amenities | jsonb | nullable | | `{"aircon":true,"fridge":false,"wc_inside":true}` |
| max_occupancy | int | NOT NULL | **D21** hard filter ghép bạn | `3` |
| gender_policy | enum (`any`,`male`,`female`) | default `any` | **D21** — `male` = male tenants only; `female` = female tenants only; `any` = no gender restriction | `any` |
| house_rules | text | nullable | **D21** | `Không hút thuốc trong phòng` |
| base_rent_price | decimal | NOT NULL | | `3500000` |
| electricity_policy_id | uuid | FK→UtilityRatePolicy, nullable | **D30** — NULL = kế thừa tòa → landlord | `NULL` |
| water_policy_id | uuid | FK→UtilityRatePolicy, nullable | **D30** | `override riêng phòng` |
| status | enum (`available`,`occupied`,`cleaning`,`maintenance`) | cached/derived | `occupied` khi có HĐ active; `cleaning` sau checkout đến khi landlord xác nhận sẵn sàng; cache phục vụ dashboard (**D20**) | `occupied` |

> Ảnh phòng (bìa + gallery): `Media(owner_type='room', purpose='cover_photo'|'gallery_photo')`.

### 2.7 Contract
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| room_id | uuid | FK→Room, NOT NULL | | |
| issuer_id | uuid | FK→User, NOT NULL | = Room.owner_id (**D25**) | |
| lead_user_id | uuid | FK→User, **nullable** | nullable để hỗ trợ tenant chưa có account (**D29**); nếu null thì lưu tên/SĐT trực tiếp trên contract | `NULL` |
| lead_name / lead_phone | varchar | nullable | dùng khi tenant không có account | `Trần Văn B` / `0912345678` |
| status | enum (`draft`,`signed`,`active`,`suspended`,`expired`,`terminated`,`cancelled`) | NOT NULL default `draft` | `suspended` khi landlord bị khóa trong grace period; `cancelled` khi quá hạn hoặc admin/landlord hủy | `active` |
| signature_mode | enum (`template_upload`) | NOT NULL | **D18** — chỉ 1 giá trị, không còn e_sign/e_ack | `template_upload` |
| signed_at | timestamp | nullable | | `2026-09-01T10:00:00Z` |
| parsed_fields | jsonb | nullable | field OCR/parse từ PDF ký — chỉ hỗ trợ, không phải nguồn chuẩn (**D18**) | `{"start_date":"2026-09-01","deposit_amount":7000000}` |
| deposit_amount | decimal | NOT NULL | | `7000000` |
| monthly_rent | decimal | NOT NULL | | `3500000` |
| start_date | date | NOT NULL | | `2026-09-01` |
| end_date | date | NOT NULL | | `2027-08-31` |
| terms | text | nullable | | `Đóng tiền trước ngày 5 hàng tháng…` |
| payment_config | enum (`representative`,`shared_tracking`) | NOT NULL default `representative` | **D22** — chỉ áp dụng khi ở ghép | `representative` |
| vehicle_count | int | **nullable** | **D32** — số xe gửi tại nhà trọ, kê khai lúc tạo/cập nhật HĐ; `NULL` = chưa khai → block phí `per_vehicle` (EC8); `0` = không gửi xe | `1` |
| deposit_settled | boolean | default false | cờ "đã thanh lý cọc" (đề xuất trong audit GĐ6) | `false` |
| deposit_deduction | decimal | NOT NULL default 0 | khoản khấu trừ cọc khi checkout | `500000` |
| deposit_returned | decimal | nullable | số cọc thực trả lại tenant | `6500000` |
| settled_at | timestamptz | nullable | hoàn tất checkout/thanh lý cọc | |

> Mẫu HĐ / file ký: `Media(owner_type='contract', purpose='contract_template'|'contract_signed')` — file ký (`contract_signed`) vẫn là **nguồn chuẩn pháp lý**, `parsed_fields` chỉ hỗ trợ tra cứu.

**Tenant identity constraint (DB CHECK, D29):** a linked account allows either contact field to be null; without an account, both fields must contain non-blank values. This is not an exclusive-or: linked tenants may retain contact snapshots.

```sql
CONSTRAINT contract_tenant_identity_check CHECK (
    tenant_user_id IS NOT NULL
    OR (
        NULLIF(BTRIM(tenant_name), '') IS NOT NULL
        AND NULLIF(BTRIM(tenant_phone), '') IS NOT NULL
    )
)
```

**Signing (D18):** no `signature_mode` field: there is only one workflow. Set `signed_at` and allow `signed` status only after a signed file exists in `Media` with `owner_type='contract'` and `purpose='contract_signed'` (service validation).

**Index quan trọng:** partial unique index `(room_id) WHERE status = 'active'` — chỉ 1 hợp đồng active/phòng.

### 2.8 ContractMember (thành viên ở ghép + CCCD)
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| contract_id | uuid | FK→Contract, NOT NULL | | |
| user_id | uuid | FK→User, **nullable** | nullable nếu tenant không có account (**D29**) | `NULL` |
| full_name | varchar | NOT NULL | | `Nguyễn Thị C` |
| phone | varchar | nullable | | `0921234567` |
| is_lead | boolean | NOT NULL default false | | `true` |
| joined_at | date | NOT NULL default `current_date` | ngày vào ở; phục vụ số người có hiệu lực theo kỳ | `2026-09-01` |
| left_at | date | nullable | không xóa bản ghi khi rời phòng; ngừng quyền chat/tenant portal từ ngày này | `NULL` |
| cccd_ocr_data | jsonb | nullable | **D17/5.6** — số, họ tên, ngày sinh, địa chỉ (OCR MVP; dữ liệu có cấu trúc, không phải file) | `{"number":"0792…","full_name":"Nguyễn Thị C"}` |
| share_amount | decimal | nullable | dùng khi `payment_config = shared_tracking` (**D22**) | `NULL` |
| share_paid_status | enum (`unpaid`,`paid`) | nullable | chỉ dùng khi shared_tracking | `NULL` |

> Ảnh CCCD mặt trước/sau: `Media(owner_type='contract_member', purpose='cccd_front'|'cccd_back')` — **D17**, chụp 1 lần. **`ContractMember` là nguồn đếm `head_count`** cho `rate_kind='per_head'` và `fee_kind='per_head'`; chỉ tính thành viên có `joined_at ≤ period_end` và (`left_at IS NULL` hoặc `left_at ≥ period_start`).

### 2.9 UtilityRatePolicy — cấu hình đơn giá điện/nước (ĐƠN GIÁ VERSIONED)

> **Bảng mới theo D30** (đóng open question #6: flat vs bậc thang EVN). Giữ nguyên thứ tự ưu tiên D16: `Room.electricity_policy_id → Building.electricity_policy_id → LandlordProfile.electricity_policy_id`.
> **Cách tính → `utility-billing-calculations.md` §4–§6.**

| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| owner_id | uuid | FK→User, NOT NULL | quyền sở hữu (**D25**) | |
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

> **Index:** `(utility_type, owner_id)` + `(room_id)`/`(building_id)` khi có. Ràng buộc `rate_kind` ↔ `unit_price`/`steps` kiểm tra ở service; preset EVN/TT25 = seed config, không phải bảng riêng.
> **D31 — bậc thang `steps` chỉ đến từ preset seed, không nhập tay trong UI thường** (EVN 6 bậc / Bậc 3 TT 25/2018 / nước địa phương). Landlord nhập tay tối đa `unit_price` cho `flat`/`per_head`. Đổi giá = tạo policy mới `effective_from`, không sửa policy cũ. Chi tiết UX → `landlord_user_flow.md` §3 (onboarding) + §10 (Module 6 — đổi giá/override).

### 2.10 RecurringFee — phí định kỳ ngoài điện/nước (Wifi, vệ sinh, gửi xe, QLVH…)

> **Bảng mới theo D30.** Tính theo `fee_kind` (cách tính) + `effective_from/to` (versioned).
> **Cách tính → `utility-billing-calculations.md` §7.**
> **D32 — preset phí = seed, không phải bảng riêng** (Wifi/QLVH/Gửi xe/Vệ sinh rác): chọn preset auto điền `fee_kind` + `unit_price` mẫu, chủ trọ xác nhận/chỉnh. `per_vehicle` lấy `contract.vehicle_count` (kê khai ở HĐ), không nhập mỗi kỳ.

| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| owner_id | uuid | FK→User, NOT NULL | quyền sở hữu (**D25**) | |
| scope | enum (`landlord`,`building`,`room`) | NOT NULL | `landlord`: mặc định áp **mọi phòng mọi tòa** của chủ trọ; `building`: mỗi phòng trong tòa đều phát sinh; `room`: chỉ phòng đó | `room` |
| room_id | uuid | FK→Room, nullable | bắt buộc nếu `scope='room'` | |
| building_id | uuid | FK→Building, nullable | bắt buộc nếu `scope='building'` | `NULL` |
| name | varchar | NOT NULL | | `Wifi` |
| fee_kind | enum (`fixed_per_period`,`per_head`,`per_area_m2`,`per_vehicle`) | NOT NULL | cố định/phóng / theo người / theo m² / theo xe | `fixed_per_period` |
| unit_price | decimal | NOT NULL | VD: wifi 100.000đ/phòng; xe máy 150.000đ/xe; QLVH 10.000đ/m² | `100000` |
| effective_from | date | NOT NULL | | `2026-09-01` |
| effective_to | date | nullable | | `NULL` |
| is_active | boolean | default true | bản mới tạo **mặc định đang chạy**; `false` = tắt cấp này → **bỏ qua và kế thừa cấp trên** (cùng loại phí, thứ tự room > building > landlord) | `true` |

### 2.11 BillingSetting (hạn thanh toán & nhắc nợ)

> Thay `LandlordProfile.default_settings`. Resolve theo `room → building → landlord`; thiếu ở cấp dưới thì kế thừa cấp trên.

| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| owner_id | uuid | FK→User, NOT NULL | landlord sở hữu cấu hình | |
| scope | enum (`landlord`,`building`,`room`) | NOT NULL | | `room` |
| building_id | uuid | FK→Building, nullable | bắt buộc khi `scope='building'` | |
| room_id | uuid | FK→Room, nullable | bắt buộc khi `scope='room'` | |
| due_days | smallint | NOT NULL default 5 | số ngày từ lúc phát hành đến hạn thanh toán | `5` |
| remind_days | smallint | NOT NULL default 0 | nhắc trước/sau hạn theo quy ước cron | `3` |
| bot_enabled | boolean | NOT NULL default true | cho bot gửi card nhắc nợ vào room chat | `true` |

**Constraint:** đúng một FK mục tiêu theo `scope`; UNIQUE `(scope, owner_id, building_id, room_id)` với bản chưa soft-delete.

### 2.12 MeterReading
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| room_id | uuid | FK→Room, NOT NULL | | |
| utility_type | enum (`electricity`,`water`) | NOT NULL | **thực tế mỗi phòng 2 công tơ riêng (điện + nước)** — 1 bản ghi/loại/kỳ | `electricity` |
| recorded_by | uuid | FK→User, NOT NULL | landlord xác nhận số đọc và chịu trách nhiệm evidence | |
| period | varchar(7) (`YYYY-MM`) | NOT NULL | | `2026-09` |
| previous_reading | decimal | NOT NULL | kỳ đầu = baseline chỉ số lúc bàn giao §5 do **OCR tự đọc + hiệu chỉnh tay nếu sai/mờ (D34/D35)**; kỳ sau = current_reading kỳ trước | `1200` |
| current_reading | decimal | NOT NULL | | `1380` |
| consumption | decimal | GENERATED (current_reading − previous_reading) | | `180` |
| reading_date | date | nullable | ngày chốt thực tế (dọn vào/ra giữa tháng) | `2026-09-30` |
| is_baseline | boolean | default false | kỳ đầu hoặc sau khi thay đồng hồ — OCR + hiệu chỉnh tay nếu sai (D34/D35) | `false` |

> Ảnh đối chứng công tơ theo **từng loại**: `Media(owner_type='meter_reading', purpose='meter_reading_evidence')` — nghiệp vụ yêu cầu tối thiểu 1 ảnh trước khi xác nhận (ràng buộc ở service, không phải DB). **Cách tính consumption & xử lý đồng hồ reset → `utility-billing-calculations.md` §3/EC1.** `created_at` (chuẩn mọi bảng) = thời điểm chốt/xác nhận — bản ghi chỉ được insert lúc chủ trọ bấm Xác nhận (§6, không có draft), nên không cần cột `confirmed_at` riêng.

**Index:** UNIQUE `(room_id, utility_type, period)`.

### 2.13 Invoice
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| contract_id | uuid | FK→Contract, NOT NULL | | |
| code | varchar(32) | UNIQUE, NOT NULL | mã nhận diện nhúng trong VietQR; webhook đối soát theo mã này, không theo amount | `INV-202609-8F2K` |
| period | varchar(7) | NOT NULL | | `2026-09` |
| rent_amount | decimal | NOT NULL | tiền phòng **prorated** theo §8 (`monthly_rent × ratio`); denormalized cho Dashboard (D20). Điện/nước/phí **đọc từ `utility_breakdown`/`fees_breakdown`** (snapshot = nguồn duy nhất, không cột kép — D37) | `3500000` |
| utility_breakdown | jsonb | nullable | **D30 — snapshot bất biến** cấu hình đã dùng: policy, chỉ số cũ/mới, lượng, tier_result, head_count | `{"electricity":{"qty_kwh":180,"amount":720000}, "water":{"head_count":3,"amount":240000}}` |
| fees_breakdown | jsonb | nullable | **D30 — snapshot phí định kỳ** `[{fee_id,name,fee_kind,quantity,unit_price,prorate_ratio,amount}]` | `[{"fee_id":"<uuid>","name":"Wifi","fee_kind":"fixed_per_period","quantity":1,"unit_price":100000,"amount":100000}]` |
| other_fees | jsonb | nullable | phí 1 lần / ngoài lệ (không trong cấu hình). **D33 — cho phép `amount` ÂM = giảm trừ/miễn giảm** (snapshot giữ dấu âm) | `[{"name":"Vệ sinh lễ","amount":50000}, {"name":"Giảm trừ hỗ trợ","amount":-700000}]` |
| total_amount | decimal | NOT NULL | **= làm tròn tổng** (round-half-up → hàng nghìn), kiểm tra khớp dòng; **≥ 0** (`TOTAL_NEGATIVE` — D33⑥) | `4610000` |
| status | enum (`pending`,`partially_paid`,`paid`,`overdue`,`void`) | NOT NULL default `pending` | **D33③ — `partially_paid`** = đã thu được tiền nhưng chưa đủ (Σ success < total); `paid` khi Σ ≥ total; `overdue` khi quá hạn còn thiếu; **không sửa sau khi gửi** — void + tạo mới (audit trail, **D18/D20**) | `pending` |
| issued_at | timestamp | nullable | thời điểm **Phát hành** (rời `pending`) — audit D18/D20; `NULL` khi còn pending (D33② auto-sinh chưa phát hành) | `2026-09-30T20:15:00Z` |
| due_date | date | nullable | **= `issued_at + N ngày`** (N cấu hình, mặc định 5 — D37); gốc quét định kỳ → `overdue` (landlord §7) | `2026-10-05` |
| note | text | nullable | | `Tháng nhập cư, prorate từ 15/09` |

> **Cách tính toàn bộ (điện/nước/phí/prorate/làm tròn/block lỗi) → `utility-billing-calculations.md` §2–§11.** UNIQUE **partial** `(contract_id, period) WHERE status != 'void'` — **D33①** cho phép tạo hóa đơn thay thế sau khi void bản sai (bản cũ giữ audit). **D33② — Invoice pending auto-sinh theo TỪNG PHÒNG** khi phòng đủ 2 MeterReading + policy OK (không batch toàn kỳ). **`issued_at`/`due_date` set khi Phát hành (D37); `due_date = issued_at + N ngày` (N cấu hình, mặc định 5) — quét định kỳ quá `due_date` còn nợ → `overdue`.**

### 2.14 Payment
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| invoice_id | uuid | FK→Invoice, NOT NULL | 1 Invoice — N Payment (retry) | |
| method | enum (`vietqr`,`vnpay`,`momo`,`cash`,`mock`) | NOT NULL | VietQR là kênh MVP; VNPay/MoMo là Stretch | `vietqr` |
| status | enum (`pending`,`success`,`failed`) | NOT NULL | | `success` |
| amount | decimal | NOT NULL | **số tiền THỰC NHẬN** (có thể ≠ total khi trả một phần; thu dư vẫn ghi đủ số nhận) | `2000000` |
| transaction_id | varchar | nullable | null cho cash | `VNPAY-20260930183021` |
| raw_gateway_response | jsonb | nullable | bằng chứng đối soát QR | `{"bank":"VCB","amount":4610000}` |
| payer_id | uuid | FK→ContractMember, nullable | dùng khi shared_tracking (D22) | `NULL` |
| needs_review | boolean | NOT NULL default false | true nếu webhook thành công tới Invoice `void` (D33⑤) | `false` |

> **D33③ — trả một phần / thu dư-đủ:** đối soát theo **mã định danh hóa đơn** (không theo amount — khách trả thiếu/dư vẫn khớp). Invoice → `partially_paid` khi Σ success ∈ (0, total); `paid` khi Σ ≥ total. Thu dư: KHÔNG hoàn tiền/bù trừ tự động — tab History hiển thị nhắc "thu dư X / còn thiếu Y" (D33). **D33⑤ — Payment success tới Invoice `void`:** không set `paid`, đánh cờ cảnh báo chủ trọ đối soát.

### 2.15 IssueReport
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| room_id | uuid | FK→Room, NOT NULL | | |
| conversation_id | uuid | FK→Conversation, nullable | | |
| reporter_id | uuid | FK→User, **nullable** | null nếu landlord tự tạo thay tenant passive (**D29**) | `NULL` |
| status | enum (`open`,`in_progress`,`resolved`,`cancelled`) | NOT NULL default `open` | `cancelled` là hủy sự cố, không hard-delete | `open` |
| title / description | varchar / text | NOT NULL | | `Đèn cháy` / `Bóng đèn phòng ngủ cháy 2 bóng` |
| resolved_at | timestamp | nullable | | `NULL` |
| resolution_note | text | nullable | | `NULL` |
| closed_at | timestamptz | nullable | set khi `resolved` hoặc `cancelled` | |

> Ảnh sự cố: `Media(owner_type='issue_report', purpose='issue_photo')`.

### 2.16 Conversation (Property Chat — D24′)
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| kind | enum (`room`,`building`) | NOT NULL | | `room` |
| room_id | uuid | FK→Room, nullable | bắt buộc nếu kind=room | |
| building_id | uuid | FK→Building, nullable | bắt buộc nếu kind=building | `NULL` |
| contract_id | uuid | FK→Contract, nullable | bắt buộc nếu kind=room; mỗi HĐ có một room chat mới, không lẫn tenant cũ/mới | |

**Constraint:** `kind='room'` → có `room_id` + `contract_id`, không có `building_id`; `kind='building'` → chỉ có `building_id`. UNIQUE `contract_id` khi room chat. Theo P2-01 §4.8, chat cũ vẫn giữ history bình thường sau checkout; không thêm cờ archive/read-only.

### 2.17 ConversationMember
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| conversation_id | uuid | FK→Conversation, NOT NULL | | |
| user_id | uuid | FK→User, NOT NULL | | |
| joined_at | timestamp | | | `2026-09-01T10:05:00Z` |
| left_at | timestamptz | nullable | rời phòng thì không gửi mới, nhưng vẫn đọc được history cũ theo flow P2-01 | `NULL` |

**Index:** UNIQUE `(conversation_id, user_id)`.

### 2.18 Message
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| conversation_id | uuid | FK→Conversation, NOT NULL | | |
| sender_id | uuid | FK→User, **nullable** | null = bot | `NULL` |
| type | enum (`text`,`image`,`file`,`bot`) | NOT NULL | | `bot` |
| content | text | nullable | | `Đã chốt số điện tháng 09: 180 kWh` |
| metadata | jsonb | nullable | card payload: `{invoice_id}`, `{issue_report_id}`, `{meter_reading_id}`,... + mention list | `{"meter_reading_id":"<uuid>"}` |

> File/ảnh đính kèm (khi `type = image|file`): `Media(owner_type='message', purpose='chat_attachment')`.

### 2.19 MessageMention
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| message_id | uuid | FK→Message, NOT NULL | | |
| user_id | uuid | FK→User, NOT NULL | người được `@mention` | |

**Index:** UNIQUE `(message_id, user_id)`.

### 2.20 RoommateProfile
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| user_id | uuid | FK→User, UNIQUE, NOT NULL | chỉ tenant có account | |
| lifestyle | jsonb | nullable | | `{"sleep":"23h-6h","pets":false,"smoking":false}` |
| personality | jsonb | nullable | | `{"introvert":true,"noisy_level":2}` |
| budget_min | decimal | nullable | | `2000000` |
| budget_max | decimal | nullable | | `3500000` |
| bio | text | nullable | | `Hiền lành, sạch sẽ, dậy sớm` |
| preferred_area | varchar | nullable | khu vực mong muốn trong feed | `Hòa Khánh, Liên Chiểu` |
| move_in_on | date | nullable | thời điểm muốn dọn vào | `2026-10-01` |
| is_visible | boolean | NOT NULL default true | ẩn/hiện bài trong feed, không xóa profile | `true` |
| id_verified | boolean | default false | badge xác minh tự nguyện (**D26**) | `true` |

### 2.21 MatchRequest
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| requester_id | uuid | FK→User, NOT NULL | | |
| target_id | uuid | FK→User, NOT NULL | Matching độc lập với phòng; ràng buộc phòng chỉ xét lúc tạo HĐ | |
| status | enum (`pending`,`accepted`,`rejected`) | NOT NULL default `pending` | | `accepted` |
| responded_at | timestamptz | nullable | thời điểm target chấp nhận/từ chối | |
| ai_score | decimal | nullable | **D28**, Stretch | `87.5` |
| ai_advice | text | nullable | **D28** | `Hai người cùng giờ ngủ, ít rủi ro xung đột` |

**Index:** UNIQUE `(requester_id, target_id)` — cache mỗi cặp 1 lần (**D28**). Service chặn request đảo chiều trùng cặp.

### 2.22 TenantHistory (Stretch — D26, consent-based)
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| tenant_id | uuid | FK→User, NOT NULL | | |
| contract_id | uuid | FK→Contract, NOT NULL | | |
| on_time_payment_score | decimal | nullable | | `95` |
| review_text | text | nullable | | `Đóng tiền đúng hạn, phòng sạch` |
| consent_given | boolean | NOT NULL default false | **bắt buộc true mới hiển thị** (PDPD Art.11) | `true` |
| visible | boolean | default false | | `true` |

### 2.23 Notification (MVP inbox + FCM)
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| user_id | uuid | FK→User, NOT NULL | | |
| type | varchar | NOT NULL | invoice_due, contract_expiry,... | `invoice_due` |
| data | jsonb | nullable | deep-link payload | `{"invoice_id":"<uuid>","amount":4610000}` |
| read_at | timestamp | nullable | | `NULL` |
| sent_at | timestamptz | nullable | thời điểm gửi FCM | |

### 2.24 NotificationPreference
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| user_id | uuid | FK→User, NOT NULL | | |
| type | enum (`invoice`,`chat`,`issue`,`match`,`account`) | NOT NULL | nhóm notification bật/tắt | `invoice` |
| enabled | boolean | NOT NULL default true | | `true` |

**Index:** UNIQUE `(user_id, type)`.

### 2.25 PushDevice
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| user_id | uuid | FK→User, NOT NULL | một user có thể nhiều thiết bị | |
| token | varchar | UNIQUE, NOT NULL | FCM registration token | |
| platform | enum (`android`,`web`) | NOT NULL | | `android` |
| last_seen_at | timestamptz | nullable | dùng dọn token hết hạn | |

### 2.26 AuditLog
| Field | Type | Ràng buộc | Ghi chú | Ví dụ |
|---|---|---|---|---|
| id | uuid | PK | | |
| actor_id | uuid | FK→User, nullable | null cho webhook/system | |
| action | varchar | NOT NULL | `user.lock`, `building.approve`, `payment.webhook` | `building.approve` |
| entity_type | varchar | NOT NULL | resource bị tác động | `building` |
| entity_id | uuid | nullable | | |
| before_data | jsonb | nullable | snapshot trước thay đổi | |
| after_data | jsonb | nullable | snapshot sau thay đổi | |
| created_at | timestamptz | NOT NULL default `now()` | Audit log append-only, không soft-delete | |

**Index:** `(entity_type, entity_id, created_at DESC)`, `(actor_id, created_at DESC)`.

### 2.27 Media (polymorphic — gom mọi file/ảnh của hệ thống)

**Nghiên cứu 2 hướng thiết kế** cho bài toán "8 loại entity đều có ảnh/file, tránh rải cột `*_url`":

| Hướng | Ưu điểm | Nhược điểm |
|---|---|---|
| **A. 1 bảng polymorphic** `media(owner_type, owner_id, purpose, ...)` — mô hình dùng bởi Rails Active Storage, Django `GenericForeignKey`, kiểu Instagram/Airbnb | 1 chỗ duy nhất quản lý file (upload, xoá, CDN, resize); thêm loại entity mới không cần bảng mới; gallery + cover photos via `purpose` + uploader audit | `owner_id` **không có FK thật** (1 cột không FK được nhiều bảng) → toàn vẹn tham chiếu phải kiểm tra ở tầng service |
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
| purpose | enum (`avatar`,`cover_photo`,`gallery_photo`,`ownership_proof`,`cccd_front`,`cccd_back`,`contract_template`,`contract_signed`,`meter_reading_evidence`,`issue_photo`,`chat_attachment`) | NOT NULL | vai trò của file trong owner đó | `cover_photo` |
| file_type | enum (`image`,`document`,`video`,`other`) | NOT NULL default `image` | | `image` |
| url | varchar | NOT NULL | | `https://cdn.pbl6.dev/room/<room_id>/cover.webp` |
| size_bytes | bigint | nullable | | `245000` |
| user_id | uuid | FK→User, nullable | Uploader | |

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
Building 1--N Floor
Building 1--N Room
Floor 1--N Room
User 1--N Room (owner_id, NOT NULL)
Room 1--N Contract
Contract 1--N ContractMember
Contract 1--N Invoice
Invoice 1--N Payment
Room 1--N MeterReading            (điện + nước: 2 bản ghi/kỳ qua utility_type)
Building/Room 1--N BillingSetting (cấu hình hạn/nhắc; còn: landlord)
User 1--N BillingSetting
Building 1--N UtilityRatePolicy   (policy cấp tòa; còn: room, landlord)
Room 1--N UtilityRatePolicy       (policy cấp phòng)
LandlordProfile 1--0..1 UtilityRatePolicy  (2 con trỏ: elec_policy_id, water_policy_id)
User 1--N RecurringFee            (owner_id; fee cấp landlord = mặc định cả nhà)
Building 1--N RecurringFee        (fee áp mọi phòng trong tòa)
Room 1--N RecurringFee            (fee riêng phòng)
Room 1--N IssueReport
Room 1--N Conversation (kind=room; một room chat mỗi hợp đồng)
Contract 1--0..1 Conversation (kind=room)
Building 1--0..1 Conversation (kind=building)
Conversation 1--N ConversationMember
Conversation 1--N Message
Message 1--N MessageMention
User 1--N MatchRequest (requester / target)
User 1--N TenantHistory
User 1--N Notification
User 1--N NotificationPreference
User 1--N PushDevice
User 1--N AuditLog
User/Room/Building/Contract/ContractMember/MeterReading/IssueReport/Message
    1--N Media (polymorphic qua owner_type + owner_id, không FK thật)
```

> Lưu ý: `UtilityRatePolicy` được link **2 chiều** — bảng cấu hình giữ `electricity_policy_id`/`water_policy_id` (con trỏ từ phòng/tòa/profile) đồng thời policy tự khai `scope`/`room_id`/`building_id`. Con trỏ trên Room/Building/LandlordProfile là nguồn chân lý cho chain resolution (D16/D30); trường `scope`/`*_id` trong policy phục vụ quản lý/gũi gọn (vd hiển thị danh sách, export).

---

## 4. Traceability theo quyết định (D-number)

| Bảng | D áp dụng |
|---|---|
| Room.owner_id NOT NULL, Building không bắt buộc owner, bỏ Manager | D25 |
| **UtilityRatePolicy, RecurringFee, Invoice.utility_breakdown/fees_breakdown, MeterReading.utility_type** | **D30** — đơn giá điện/nước versioned (flat/bậc thang/khoán đầu người) + phí định kỳ; đóng open question #6; mở rộng D16 (giữ thứ tự room→building→landlord) |
| **UtilityRatePolicy.steps bậc thang chỉ từ preset seed (EVN/TT25/nước địa phương), không nhập tay trong UI; đổi giá = policy mới `effective_from`** | **D31** — preset thân thiện landlord lớn tuổi; thuật toán `calcTiered` là code, giá là config |
| **LandlordProfile.electricity_policy_id/water_policy_id nullable (NULL = chưa cấu hình), Contract.vehicle_count kê khai ở HĐ, phí 1 lần `other_fees`, preset phí seed** | **D32** — onboarding không chặn (banner + block tại hóa đơn), xe theo HĐ, preset phí |
| **Invoice status `partially_paid`, UNIQUE partial `(contract_id, period) WHERE status != 'void'`, Payment đối soát theo invoice_id + thu dư/thiếu nhắc ở History, Invoice auto-sinh theo phòng, `other_fees` âm (total ≥ 0), `rate_kind` điện chỉ flat/tiered** | **D33** — thanh toán một phần + thu dư/thiếu nhắc, hóa đơn theo phòng, điện bỏ khoán đầu người |
| Building/Room `electricity_policy_id`/`water_policy_id` (con trỏ policy) thay field decimal | D16 (nâng cấp), D30 |
| Contract uses template generation + signed-file upload; `signed_at` + Media `contract_signed`, no signature-mode column | D18 |
| ContractMember.share_amount, Contract.payment_config | D22 |
| ContractMember `cccd_ocr_data` + Media CCCD | D17 |
| `User.role` bất biến; tài khoản role khác phải đăng ký riêng | User flows Phase 1 |
| Conversation/Message | D24′ |
| MatchRequest unique(requester_user_id,target_user_id), ai_score/ai_advice | D28 |
| Room.max_occupancy/gender_policy/house_rules dùng làm hard filter | D21 |
| TenantHistory.consent_given bắt buộc | D26 |
| Contract.lead_user_id nullable, ContractMember.user_id nullable, IssueReport.reporter_id nullable | D29 (zero tenant login) |
| Building.property_type mở rộng | D9 |
| Building.latitude/longitude | yêu cầu định vị bản đồ |
| Bảng Media polymorphic (thay mọi cột `*_url`/`photos`) | yêu cầu tránh rải url file |
| Base Entity (id/created_at/updated_at/deleted_at) trên mọi bảng | yêu cầu chuẩn hoá audit/soft-delete |
| FavoriteRoom, Building approval + ownership_proof Media, User lock, Contract suspended/cancelled, AuditLog | P2-01 M2–M8, C4, D1–D2; admin/landlord/shared flows |
| BillingSetting, NotificationPreference, PushDevice, Invoice.code, MessageMention | P2-01 I3, B2, H2/N1, J3–J5; landlord/tenant flows |
| ContractMember.joined_at/left_at, Room.cleaning, IssueReport.cancelled, RoommateProfile discovery fields | P2-01 E4, F1–F2, K1–K4, L1–L4; landlord/tenant flows |
| `LandlordGatewayCredential` / `GatewayConfig` | **Không thêm vào MVP:** D38 là thiết kế gateway/mock cho Phase 1+; P2-01 và scope SoT không có feature tạm trú |

---

## 5. Thiết kế phân quyền theo Role (không RBAC)

### 5.1 Mô hình role

- **Không có bảng `Role` hay `Permission` riêng.** Quyền được suy ra trực tiếp từ 2 lớp kiểm tra ở tầng application (service/guard), không phải từ dữ liệu quan hệ:
  1. **Role check** — user có role cần thiết không (`landlord` / `tenant` / `admin`), lấy từ `User.role` bất biến.
  2. **Ownership check** — nếu resource có `owner_id`/`issuer_id`/`lead_user_id`/`user_id` thì phải khớp với `request.user.id`, trừ khi role = `admin`.
- JWT payload: `{ sub: user_id, role: "landlord", status: "active" }` — không nhúng permission chi tiết.
- Backend dùng decorator kiểu `@Roles('landlord')` trên từng endpoint + 1 hàm `assertOwnership(resource, user)` gọi thêm trong service layer khi cần. Không cần bảng ánh xạ role↔permission vì tập hành động cố định, không thay đổi runtime.

### 5.2 Ma trận quyền theo Resource × Action × Role

| Resource | Action | landlord | tenant | admin | Ghi chú |
|---|---|---|---|---|---|
| Building/Floor/Room | Create/Update/Delete | ✅ (BĐS mình nộp / phòng mình sở hữu) | ❌ | ✅ | ownership check qua `Building.submitted_by` / `Room.owner_id` |
| Room | Đọc (tìm phòng available) | ✅ (mọi phòng, phục vụ ops) | ✅ (public, chỉ field public) | ✅ | tenant chỉ thấy field public khi tìm kiếm |
| UtilityRatePolicy | Create/update/deactivate | ✅ (chỉ của mình, `owner_id`) | ❌ | ✅ | đổi giá ảnh hưởng kỳ sau (D30) |
| UtilityRatePolicy | Đọc | ✅ | ✅ (qua hóa đơn/hiển thị) | ✅ | tenant đọc qua snapshot hóa đơn, không sửa |
| RecurringFee | Create/update/deactivate | ✅ (chỉ của mình) | ❌ | ✅ | |
| RecurringFee | Đọc | ✅ | ✅ (qua hóa đơn) | ✅ | |
| Contract | Create/sinh mẫu/upload file ký | ✅ (chỉ phòng mình, `issuer_id`) | ❌ | ✅ | |
| Contract | Đọc | ✅ (owner) | ✅ (chỉ HĐ mình là `lead_user_id`/`ContractMember`) | ✅ | |
| MeterReading | Create/confirm | ✅ (owner phòng) | ❌ | ✅ | P2-01: chỉ landlord thao tác trên mobile |
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
| FavoriteRoom / NotificationPreference / PushDevice | CRUD | ✅ (của chính mình) | ✅ (của chính mình) | ✅ | |
| AuditLog | Đọc | ❌ | ❌ | ✅ | append-only; webhook/system cũng ghi log |
| Media | Upload/Delete | ✅ (nếu có quyền sửa entity cha) | ✅ (nếu có quyền sửa entity cha, vd ảnh issue của mình) | ✅ | không check qua role, check qua quyền của owner_type tương ứng |
| Media | Đọc | ✅ (theo quyền đọc entity cha) | ✅ (theo quyền đọc entity cha) | ✅ | vd ảnh phòng available = public, ảnh CCCD = riêng tư |

### 5.3 Vì sao không cần RBAC đầy đủ

- Tập hành động và tài nguyên **cố định**, không có nhu cầu cấu hình quyền động theo tổ chức (không multi-tenant SaaS phân quyền tùy biến).
- Chỉ 3 role, không có phân cấp phức tạp hay custom permission theo khách hàng → bảng `Role`/`Permission`/`RolePermission` sẽ over-engineer cho MVP 13–14 tuần (đúng tinh thần D9 — ưu tiên đơn giản, tránh phức tạp không cần thiết).
- Ownership check (row-level) quan trọng hơn role check trong hệ thống này (D25) — RBAC thuần theo role sẽ không đủ, vẫn cần thêm lớp ownership dù có RBAC hay không, nên giữ đơn giản: role (coarse-grained) + ownership (fine-grained) là đủ.
- Nếu sau này cần permission tùy biến (vd. landlord có nhân viên phụ, multi-org), có thể mở rộng thêm bảng `Role`/`Permission` ở Phase 1+ mà không phá vỡ `User.role` hiện tại (role enum vẫn dùng làm coarse filter đầu tiên).
