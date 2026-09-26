# Thiết kế Cơ sở dữ liệu & Phân quyền theo Role

## 2. Danh sách Entity

> **Quy ước cột `Validation`:** chỉ ghi validate có giá trị xác định như `Min length`, `Max length`, `Regex` hoặc điều kiện số; không có thì để trống.

### 2.0 Base Entity (quy ước áp dụng cho mọi bảng bên dưới)

| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| id | uuid | PK, default `gen_random_uuid()` | | | |
| created_at | timestamptz | NOT NULL, default `now()` | | | `2026-09-05T10:00:00Z` |
| updated_at | timestamptz | NOT NULL, default `now()` | tự cập nhật bằng trigger `set_updated_at()` mỗi lần `UPDATE` | | `2026-09-05T10:00:00Z` |
| is_deleted | boolean | NOT NULL, default false | Soft-delete: `false` = existing record; default queries use `WHERE is_deleted = false`. Financial/audit records are retained; voiding an invoice changes its status, not this flag. | | `false` |

### 2.1 User
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| phone | varchar(12) | UNIQUE, NOT NULL | định danh chính (VN) | Min length: 10; Max length: 12; Regex: `^0[0-9]{9}$` hoặc `^\+84[0-9]{9}$` | `0901234567` |
| email | varchar | UNIQUE, NOT NULL | | Min length: 5; Max length: 254; Regex: `^[^\s@]+@[^\s@]+\.[^\s@]+$` | `lan@example.com` |
| password | varchar | NOT NULL | | Min length: 60; Max length: 255 | `$2a$10$N9qo8uLOickgx2ZMRZoMye…` |
| name | varchar | NOT NULL | | Min length: 1; Max length: 254 | `Lê Văn An` |
| role | enum (`landlord`,`tenant`,`admin`) | NOT NULL | User flow SoT: một tài khoản có đúng một role bất biến; role khác dùng tài khoản riêng | | `landlord` |
| status | enum (`active`,`locked`) | NOT NULL default `active` | Tenant bị khóa vẫn được xem/thanh toán HĐ hiện tại ở tầng quyền; landlord bị khóa không đăng nhập được portal | | `active` |
| lock_reason | varchar | nullable | lý do admin khóa tài khoản | Min length: 1; Max length: 500 | `Spam listing` |
| locked_at | timestamptz | nullable | | | `NULL` |

### 2.2 FavoriteRoom (phòng đã lưu)
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| tenant_id | uuid | FK→User, NOT NULL | tenant lưu phòng cần đăng nhập | | |
| room_id | uuid | FK→Room, NOT NULL | | | |

**Index:** UNIQUE `(tenant_id, room_id)` WHERE `is_deleted = false`.

### 2.3 LandlordProfile
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| user_id | uuid | FK→User, UNIQUE, NOT NULL | 1-1, chỉ tồn tại nếu user có role landlord | | |
| bank_code | varchar | nullable | mã ngân hàng theo danh mục VietQR — dùng sinh QR nhận tiền | Min length: 4; Max length: 20 | `970436` |
| account_number | varchar | nullable | số tài khoản nhận tiền. **D39 — MVP chỉ chạy sandbox: đây là số liệu giả lập** | Regex: `^[0-9]{6,20}$` | `1234567890` |
| account_name | varchar | nullable | tên chủ tài khoản, viết không dấu (yêu cầu VietQR) | Min length: 1; Max length: 254 | `LEVANAN` |

> **Tài khoản nhận tiền (D39):** landlord khai 3 trường trên một lần; hệ thống dùng để sinh **QR động** nhúng `amount` + `Invoice.code` vào nội dung chuyển khoản. App **không** làm cổng thu tiền — chỉ phát QR rồi đối soát.
> Ngày thu dự kiến & nhắc nộp không lưu ở đây: dùng `BillingSetting` (§2.10), kế thừa `room → building`.

### 2.4 Building
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| landlord_id | uuid | FK→User, NOT NULL | landlord sở hữu | | |
| name | varchar | NOT NULL | | Min length: 1; Max length: 254 | `Nhà trọ Thanh Xuân` |
| province | varchar | NOT NULL | tên Tỉnh/TP từ dropdown VN | Min length: 1; Max length: 100 | `Thành phố Hồ Chí Minh` |
| ward | varchar | NOT NULL | tên Phường/Xã từ dropdown VN | Min length: 1; Max length: 100 | `Phường Bến Nghé` |
| address | varchar | NOT NULL | địa chỉ chi tiết (số nhà, đường) | Min length: 1; Max length: 254 | `12 Nguyễn Trãi` |
| latitude | decimal(9,6) | NOT NULL | tự geocode từ address khi tạo building | `>= -90; <= 90` | `20.995100` |
| longitude | decimal(9,6) | NOT NULL | tự geocode từ address khi tạo building | `>= -180; <= 180` | `105.816649` |
| status | enum (`pending`,`approved`,`rejected`) | NOT NULL default `pending` | chỉ BĐS `approved` mới tạo phòng, phát hành HĐ và hiển thị công khai | | `pending` |
| reviewed_by | uuid | FK→User, nullable | admin duyệt/từ chối | | |
| reviewed_at | timestamptz | nullable | | | |
| note | text | nullable | bắt buộc khi `status='rejected'` | Min length: 1; Max length: 500 | `Ảnh giấy tờ mờ` |

> Ảnh tòa nhà (bìa + gallery) và giấy tờ sở hữu bắt buộc: `Media(owner_type='building', purpose='cover_photo'|'gallery_photo'|'ownership_proof')`.

### 2.5 Room
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| landlord_id | uuid | FK→User, **NOT NULL** | **D25 — bắt buộc, 1 chủ/phòng** | | |
| building_id | uuid | FK→Building, NOT NULL | | | |
| floor_number | int | nullable | tầng (1-based) | `> 0` | `2` |
| name | varchar | NOT NULL | | Min length: 1; Max length: 254 | `P.201` |
| description | text | nullable | **D21** | Min length: 1; Max length: 500 | `Phòng trọ hiện đại, tiện nghi đầy đủ` |
| area | decimal | nullable | Area in m²; used by `per_area_m2` fees | `>0` | `18.5` |
| amenities | jsonb | NOT NULL | | {} | `{"aircon":true,"fridge":false,"wc_inside":true}` |
| max_occupancy | int | nullable | **D21** hard filter ghép bạn | `> 0`| `3` |
| gender_policy | enum (`any`,`male`,`female`) | default `any` | **D21** — `male` = male tenants only; `female` = female tenants only; `any` = no gender restriction | | `any` |
| rent_price | decimal | NOT NULL | | `>=0`| `3500000` |
| status | enum (`available`,`occupied`,`maintenance`) | cached/derived | `occupied` khi có HĐ active; | | `occupied` |

> **D39 — bỏ 2 con trỏ `electricity_policy_id`/`water_policy_id`:** `RatePolicy` nay tự khai scope/đích nên không cần trỏ ngược. Chuỗi kế thừa `room → building` suy ra từ chính bảng `RatePolicy` (`scope` + `room_id`/`building_id` + `is_active`).

> Ảnh phòng (bìa + gallery): `Media(owner_type='room', purpose='cover_photo'|'gallery_photo')`.

### 2.7 Contract
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| room_id | uuid | FK→Room, NOT NULL | | | |
| landlord_id | uuid | FK→User, NOT NULL | | | |
| tenant_id | uuid | FK→User, **nullable** | nullable để hỗ trợ tenant chưa có account (**D29**); nếu null thì lưu tên/SĐT trực tiếp trên contract | | `NULL` |
| tenant_name | varchar | nullable | dùng khi tenant không có account | Min length: 1; Max length: 254 | `Trần Văn B` |
| tenant_phone | varchar | nullable | dùng khi tenant không có account | Min length: 10; Max length: 12; Regex: `^0[0-9]{9}$` hoặc `^\+84[0-9]{9}$` | `0912345678` |
| status | enum (`draft`,`signed`,`active`,`suspended`,`expired`,`terminated`) | NOT NULL default `draft` | `suspended` khi landlord bị khóa trong grace period; `terminated` khi quá hạn hoặc admin/landlord hủy | | `active` |
| deposit_amount | decimal | NOT NULL | số cọc khi ký HĐ; lịch sử trả cọc/điều chỉnh lưu trong Payment | `>=0` | `7000000` |
| rent_price | decimal | NOT NULL | | `>=0`| `3500000` |
| start_date | date | NOT NULL | | `< end_date` | `2026-09-01` |
| end_date | date | NOT NULL | | `> start_date` | `2027-08-31` |
| description | text | nullable | | Min length: 1; Max length: 500 | `Đóng tiền trước ngày 5 hàng tháng…` |
| vehicle_count | int | **nullable** | **D32** — số xe gửi tại nhà trọ, kê khai lúc tạo/cập nhật HĐ; `NULL` = chưa khai → block phí `per_vehicle` (EC8); `0` = không gửi xe | `>= 0` | `1` |

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

**Index quan trọng:** partial unique index `(room_id) WHERE contract_status = 'active'` — chỉ 1 hợp đồng active/phòng.

### 2.8 ContractMember (thành viên ở ghép + CCCD)
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| contract_id | uuid | FK→Contract, NOT NULL | | | |
| tenant_id | uuid | FK→User, **nullable** | nullable nếu tenant không có account (**D29**) | | `NULL` |
| tenant_name | varchar | nullable | | Min length: 1; Max length: 254 | `Nguyễn Thị C` |
| tenant_phone | varchar | nullable | | Min length: 10; Max length: 12; Regex: `^0[0-9]{9}$` hoặc `^\+84[0-9]{9}$` | `0921234567` |
| joined_at | date | NOT NULL default `current_date` | ngày vào ở; phục vụ số người có hiệu lực theo kỳ | `< left_at` khi `left_at` có giá trị | `2026-09-01` |
| left_at | date | nullable | không xóa bản ghi khi rời phòng; ngừng quyền chat/tenant portal từ ngày này | `> joined_at` | `NULL` |

> Ảnh CCCD mặt trước/sau: `Media(owner_type='contract_member', purpose='cccd_front'|'cccd_back')` — **D17**, chụp 1 lần. **`ContractMember` là nguồn đếm `head_count`** cho `rate_kind='per_head'` trong `RatePolicy.rates[]`; chỉ tính thành viên có `joined_at ≤ period_end` và (`left_at IS NULL` hoặc `left_at ≥ period_start`).

### 2.9 RatePolicy — bộ đơn giá & phí định kỳ (1 bộ / scope)

> **D39 — mỗi scope chỉ có MỘT bộ, chỉ UPDATE tại chỗ:** gộp UtilityRatePolicy + RecurringFee vào `rates` jsonb. Không tạo bản sao, không xoá mền, **không có `effective_from`/`effective_to`**.
> Kế thừa: `room → building`; phòng không có bộ riêng thì dùng bộ của building. **Bật/tắt = `is_active`** (tắt → kế thừa cấp trên).
> **Cách tính → `utility-billing-calculations.md` §4–§7.**

| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| landlord_id | uuid | FK→User, NOT NULL | landlord sở hữu bộ rate | | |
| scope | enum (`building`,`room`) | NOT NULL | cấp áp dụng. **D39 bỏ cấp `landlord`** — bộ mặc định của landlord nằm ở từng building | | `room` |
| room_id | uuid | FK→Room, nullable | bắt buộc nếu `scope='room'` | | |
| building_id | uuid | FK→Building, nullable | bắt buộc nếu `scope='building'` | | `NULL` |
| rates | jsonb | NOT NULL default `[]` | **mảng các mục đơn giá** — shape bên dưới | | `[{...}]` |
| is_active | boolean | NOT NULL default true | `true` = áp dụng bộ này; `false` = tắt → kế thừa bộ cấp trên | | `true` |

**Shape `rates[]`** (mỗi phần tử):
| Key | Bắt buộc | Mô tả |
|---|---|---|
| `type` | ✔ | `electricity`\|`water`\|`wifi`\|`cleaning`\|`parking`\|`maintenance`\|`other` |
| `name` | ✔ | nhãn hiển thị, vd `"Điện EVN"` — copy sang snapshot hóa đơn |
| `rate_kind` | ✔ | `flat`\|`tiered`\|`fixed_per_period`\|`per_head`\|`per_area_m2`\|`per_vehicle` |
| `unit_price` | ✔ trừ `tiered` | đơn giá / đơn vị tính; `tiered` dùng `steps` |
| `steps` | chỉ `tiered` | `[{from,to,price}]`, `to=null` = mở ∞ (EVN 6 bậc, bậc 3 TT 25/2018) |
| `billing_unit` | ✔ | `kwh`\|`m3`\|`room`\|`person`\|`m2`\|`vehicle`\|`day`\|`occurrence` — đơn vị tính để hiển thị |

### 2.10 BillingSetting (ngày thu dự kiến & nhắc nộp)

> **D39 — app KHÔNG cưỡng chế thu tiền.** `payment_due_day` chỉ là *gợi ý hiển thị* ("thường thu ngày 5"), **không** sinh trạng thái `overdue`, không chặn thao tác nào. Resolve `room → building`; thiếu ở cấp dưới thì kế thừa cấp trên (không có cấp `landlord` — giống `RatePolicy`).

| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| landlord_id | uuid | FK→User, NOT NULL | landlord sở hữu cấu hình | | |
| scope | enum (`building`,`room`) | NOT NULL | | | `room` |
| building_id | uuid | FK→Building, nullable | bắt buộc khi `scope='building'` | | |
| room_id | uuid | FK→Room, nullable | bắt buộc khi `scope='room'` | | |
| payment_due_day | smallint | NOT NULL default 5 | ngày trong tháng **dự kiến thu tiền** (chỉ để hiển thị) | `>= 1; <= 28` | `5` |
| remind_day | smallint | nullable | ngày trong tháng gợi ý nhắc nộp (bỏ trống = không nhắc) | `>= 1; <= 28` | `3` |
| bot_enabled | boolean | NOT NULL default true | cho bot gửi card nhắc nộp vào room chat | | `true` |
| is_active | boolean | NOT NULL default true | `false` = tắt → kế thừa cấp trên | | `true` |

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
| code | varchar(32) | UNIQUE, NOT NULL | mã nhận diện nhúng trong VietQR (`addInfo`) để webhook đối soát **theo mã, không theo amount** | Min length: 1; Max length: 32 | `INV-202609-8F2K` |
| period | varchar(7) | NOT NULL | kỳ tính tiền (tháng dịch vụ) | Min length: 7; Max length: 7; Regex: `^[0-9]{4}-(0[1-9]\|1[0-2])$` | `2026-09` |
| rent_amount | decimal | NOT NULL | tiền phòng **prorated** theo §8 (`monthly_rent × ratio`); denormalized cho Dashboard (D20) | `>=0` | `3500000` |
| breakdown | jsonb | nullable | snapshot bất biến của điện/nước/phí định kỳ. **D39 bắt buộc mỗi item có:** `type`, `name`, `rate_kind`, `unit_price`, `quantity`, `unit`, `service_start`, `service_end`, `prorate_ratio`, `amount` (kèm `tier_detail` nếu `tiered`) | | `[{"type":"electricity","name":"Điện EVN","rate_kind":"flat","unit_price":4000,"quantity":180,"unit":"kwh","service_start":"2026-09-01","service_end":"2026-09-30","prorate_ratio":1,"amount":720000}]` |
| other_fees | jsonb | nullable | phí 1 lần / ngoài lệ (không trong cấu hình). **D33 — cho phép `amount` ÂM = giảm trừ/miễn giảm** (snapshot giữ dấu âm) | | `[{"name":"Vệ sinh lễ","amount":50000}]` |
| total_amount | decimal | NOT NULL | | `>=0` | `4610000` |
| status | enum (`pending`,`issued`,`void`) | NOT NULL default `pending` | **D39 — bỏ `overdue`; `cancel` → `void`.** `pending` = auto-sinh chưa phát hành; `issued` = đã gửi chủ trọ; `void` = hủy (giữ audit, không sửa/xoá). **Trạng thái thu tiền KHÔNG lưu** — suy ra từ Σ `Payment` success (D33③) | | `pending` |
| issued_at | timestamp | nullable | thời điểm **Phát hành** (rời `pending`) — audit D18/D20; `NULL` khi còn pending | | `2026-09-30T20:15:00Z` |
| voided_invoice_id | uuid | FK→Invoice, nullable | **D37 — bản thay thế trỏ về bản đã void**, giữ vòng đời hóa đơn | | `NULL` |
| note | text | nullable | | | `Tháng nhập cư, prorate từ 15/09` |

> **Cách tính toàn bộ (điện/nước/phí/prorate/làm tròn/block lỗi) → `utility-billing-calculations.md` §2–§11.** UNIQUE **partial** `(contract_id, period) WHERE invoice_status IN ('pending','issued') AND is_deleted = false` — cho phép tạo hóa đơn thay thế sau khi void bản sai (bản cũ giữ audit). **D33② — Invoice pending auto-sinh theo TỪNG PHÒNG** khi phòng đủ 2 MeterReading + policy OK (không batch toàn kỳ). **D39 — không lưu `due_date`:** app không cưỡng chế thu tiền nên không có mốc hạn/`overdue`; ngày thu dự kiến nằm ở `BillingSetting.payment_due_day`, chỉ để hiển thị.

### 2.13 Payment
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| invoice_id | uuid | FK→Invoice, **nullable** | nullable khi trả cọc hoặc hoàn tiền (không liên quan HĐ) | | |
| contract_id | uuid | FK→Contract, nullable | bắt buộc khi `invoice_id` null (trả cọc/hoàn tiền theo HĐ) | | |
| method | enum (`vietqr`,`vnpay`,`momo`,`cash`,`mock`) | NOT NULL | **D39 — MVP chỉ chạy sandbox:** `mock` (QR giả lập) + `cash` là kênh chính; `vietqr` = QR thật tầng 1 (sandbox); `vnpay`/`momo` = Stretch | | `mock` |
| status | enum (`pending`,`success`,`failed`) | NOT NULL | | | `success` |
| amount | decimal | NOT NULL | **số tiền THỰC NHẬN** (có thể ≠ total khi trả một phần; thu dư vẫn ghi đủ số nhận) | `>=0`| `2000000` |
| transaction_id | varchar | nullable | null cho cash | Min length: 1; Max length: 255 | `VNPAY-20260930183021` |
| raw_gateway_response | jsonb | nullable | bằng chứng đối soát (sandbox: payload giả lập) | | `{"bank":"VCB","amount":4610000}` |

> **D33③ — trả một phần / thu dư-đủ:** đối soát theo **mã định danh hóa đơn** (không theo amount — khách trả thiếu/dư vẫn khớp). **D39 — KHÔNG ghi trạng thái thu vào `Invoice.invoice_status`:** UI suy ra `chưa thu / thu một phần / thu đủ / thu dư` từ Σ `Payment` success so với `Invoice.total_amount`. Thu dư: KHÔNG hoàn tiền/bù trừ tự động — tab History hiển thị nhắc "thu dư X / còn thiếu Y". **D33⑤ — Payment success tới Invoice `void`:** đánh cờ `needs_review` để chủ trọ đối soát.
>
> **Trả cọc (checkout):** landlord tạo Payment với `invoice_id = NULL`, `contract_id = ?`, `method = 'cash'|'vnpay'`, `amount = số tiền trả lại`. `created_at` = thời điểm thanh lý. Không cần field riêng trên Contract. **D39 — không thêm `collected_at`: `Payment.created_at` đã là mốc thời gian ghi nhận khoản thu.**

### 2.14 IssueReport
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
### 2.15 Conversation (Chat)
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| type | enum (`room`,`building`,`direct`) | NOT NULL | | | `room` |
| room_id | uuid | FK→Room, nullable | bắt buộc nếu kind=room | | |
| building_id | uuid | FK→Building, nullable | bắt buộc nếu kind=building | | `NULL` |
| contract_id | uuid | FK→Contract, nullable | bắt buộc nếu kind=room; mỗi HĐ có một room chat mới | | |
| title | varchar | nullable | tên group chat (optional, cho building chat hoặc future use) | Min length: 1; Max length: 255 | `Chat tòa nhà` |

**Constraint:**
- `kind='room'` → có `room_id` + `contract_id`, không có `building_id`
- `kind='building'` → chỉ có `building_id`
- `kind='direct'` → không có `room_id`, `building_id`, `contract_id` (chat tự do, 2 người hoặc nhiều người)
- UNIQUE `contract_id` khi room chat
- Chat cũ vẫn giữ history sau checkout, không archive/read-only

### 2.16 ConversationMember
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| conversation_id | uuid | FK→Conversation, NOT NULL | | | |
| user_id | uuid | FK→User, NOT NULL | | | |
| joined_at | timestamp | | | `< left_at` khi `left_at` có giá trị | `2026-09-01T10:05:00Z` |
| left_at | timestamptz | nullable | rời phòng thì không gửi mới, nhưng vẫn đọc được history cũ theo flow P2-01 | `> joined_at` | `NULL` |

**Index:** UNIQUE `(conversation_id, user_id)`.

### 2.17 Message
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| conversation_id | uuid | FK→Conversation, NOT NULL | | | |
| sender_id | uuid | FK→User, **nullable** | null = bot | | `NULL` |
| type | enum (`text`,`image`,`file`,`bot`) | NOT NULL | | | `bot` |
| content | text | nullable | | | `Đã chốt số điện tháng 09: 180 kWh` |

> File/ảnh đính kèm (khi `type = image|file`): `Media(owner_type='message', purpose='chat_attachment')`.

### 2.18 MessageMention
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| message_id | uuid | FK→Message, NOT NULL | | | |
| user_id | uuid | FK→User, NOT NULL | người được `@mention` | | |

**Index:** UNIQUE `(message_id, user_id)`.

### 2.19 RoommateProfile
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| tenant_id | uuid | FK→User, UNIQUE, NOT NULL | chỉ tenant có account | | |
| lifestyle | jsonb | nullable | | | `{"sleep":"23h-6h","pets":false,"smoking":false}` |
| personality | jsonb | nullable | | | `{"introvert":true,"noisy_level":2}` |
| budget_min | decimal | nullable | | `>= 0; < budget_max` khi `budget_max` có giá trị | `2000000` |
| budget_max | decimal | nullable | | `>= 0; > budget_min` khi `budget_min` có giá trị | `3500000` |
| bio | text | nullable | | | `Hiền lành, sạch sẽ, dậy sớm` |
| preferred_area | varchar | nullable | khu vực mong muốn trong feed | Min length: 1; Max length: 255 | `Hòa Khánh, Liên Chiểu` |
| move_in_on | date | nullable | thời điểm muốn dọn vào | | `2026-10-01` |
| is_visible | boolean | NOT NULL default true | ẩn/hiện bài trong feed, không xóa profile | | `true` |
| id_verified | boolean | default false | badge xác minh tự nguyện (**D26**) | | `true` |

### 2.20 MatchRequest
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| requester_id | uuid | FK→User, NOT NULL | | | |
| target_id | uuid | FK→User, NOT NULL | Matching độc lập với phòng; ràng buộc phòng chỉ xét lúc tạo HĐ | | |
| status | enum (`pending`,`accepted`,`rejected`,`withdrawn`) | NOT NULL default `pending` | `withdrawn` = người gửi rút yêu cầu, **D50** | | `accepted` |
| responded_at | timestamptz | nullable | thời điểm target chấp nhận/từ chối | | |
| ai_score | decimal | nullable | **D28**, Stretch | `>= 0.0; <= 100.0` | `87.5` |
| ai_advice | text | nullable | **D28** | | `Hai người cùng giờ ngủ, ít rủi ro xung đột` |

**Index:** UNIQUE `(requester_id, target_id)` — cache mỗi cặp 1 lần (**D28**). Service chặn request đảo chiều trùng cặp.

### 2.21 Notification (MVP inbox + FCM)
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| user_id | uuid | FK→User, NOT NULL | | | |
| type | varchar | NOT NULL | invoice_due, contract_expiry,... | Min length: 1; Max length: 50 | `invoice_due` |
| data | jsonb | nullable | deep-link payload | | `{"invoice_id":"<uuid>","amount":4610000}` |
| read_at | timestamp | nullable | | | `NULL` |
| sent_at | timestamptz | nullable | thời điểm gửi FCM | | |

### 2.22 NotificationPreference
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| user_id | uuid | FK→User, NOT NULL | | | |
| type | enum (`invoice`,`chat`,`issue`,`match`,`account`) | NOT NULL | nhóm notification bật/tắt | | `invoice` |
| enabled | boolean | NOT NULL default true | | | `true` |

**Index:** UNIQUE `(user_id, type)`.

### 2.23 PushDevice
| Field | Type | Ràng buộc | Ghi chú | Validation | Ví dụ |
|---|---|---|---|---|---|
| user_id | uuid | FK→User, NOT NULL | một user có thể nhiều thiết bị | | |
| token | varchar | UNIQUE, NOT NULL | FCM registration token | Min length: 1; Max length: 512 | |
| platform | enum (`android`,`web`) | NOT NULL | | | `android` |
| last_seen_at | timestamptz | nullable | dùng dọn token hết hạn | | |

### 2.24 AuditLog
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

### 2.25 Media (polymorphic — gom mọi file/ảnh của hệ thống)

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