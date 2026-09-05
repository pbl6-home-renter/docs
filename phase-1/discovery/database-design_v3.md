# Thiết kế Cơ sở dữ liệu & Phân quyền theo Role
**Dự án:** Nền tảng quản lý thuê trọ dài hạn (Landlord Web + Tenant Mobile + AI)
**Nguồn:** decisions.md (D1–D29), feature-list.md, user-behavior-workflow.md
**Phạm vi:** MVP theo D9 (dài hạn only), D25 (ownership), D29 (landlord-solo resilience)

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
9. **Không rải cột `*_url` trên nhiều bảng.** Toàn bộ ảnh/file (avatar, ảnh phòng, ảnh tòa, CCCD, hợp đồng ký, ảnh công tơ, ảnh sự cố, file chat) đi qua **1 bảng `Media` polymorphic duy nhất** — xem mục 2.19.

---

## 2. Danh sách Entity

### 2.0 Base Entity (quy ước áp dụng cho mọi bảng bên dưới)

| Field | Type | Ràng buộc | Ghi chú |
|---|---|---|---|
| id | uuid | PK, default `gen_random_uuid()` | |
| created_at | timestamptz | NOT NULL, default `now()` | |
| updated_at | timestamptz | NOT NULL, default `now()` | tự cập nhật bằng trigger `set_updated_at()` mỗi lần `UPDATE` |
| deleted_at | timestamptz | nullable | quy ước soft-delete: `NULL` = còn tồn tại. Query mặc định luôn thêm `WHERE deleted_at IS NULL`. Với bảng mang tính chứng từ/audit (`invoice`, `payment`, `meter_reading`...) cột này gần như không dùng tới trong nghiệp vụ (không "xoá" hoá đơn) nhưng vẫn giữ để đồng nhất schema. |

Mọi entity ở mục 2.1 → 2.19 dưới đây được hiểu là **kế thừa 4 field trên** (không lặp lại trong từng bảng để bảng gọn). Các unique/partial index có điều kiện trạng thái (vd 1 hợp đồng active/phòng) đều kèm thêm `AND deleted_at IS NULL`.

### 2.1 User
| Field | Type | Ràng buộc | Ghi chú |
|---|---|---|---|
| id | uuid | PK | |
| phone | varchar(15) | UNIQUE, NOT NULL | định danh chính (VN) |
| email | varchar | UNIQUE, nullable | |
| password_hash | varchar | NOT NULL | |
| full_name | varchar | NOT NULL | |
| roles | enum[] (`landlord`,`tenant`,`admin`) | NOT NULL, default `{}` | **D13** — mảng, không phải 1 giá trị |

> Ảnh đại diện: **không có cột `avatar_url`** — lấy qua `Media(owner_type='user', owner_id=User.id, purpose='avatar')`.

### 2.2 LandlordProfile
| Field | Type | Ràng buộc | Ghi chú |
|---|---|---|---|
| id | uuid | PK | |
| user_id | uuid | FK→User, UNIQUE, NOT NULL | 1-1, chỉ tồn tại nếu user có role landlord |
| default_electricity_rate | decimal | NOT NULL | **D16** — set 1 lần, áp mọi tòa |
| default_water_rate | decimal | NOT NULL | **D16** |
| default_settings | jsonb | nullable | cấu hình invoice/contract mặc định |

### 2.3 Building
| Field | Type | Ràng buộc | Ghi chú |
|---|---|---|---|
| id | uuid | PK | |
| landlord_owner_id | uuid | FK→User, **nullable** | building **không bắt buộc** có chủ (**D25**) |
| name | varchar | NOT NULL | |
| address | varchar | NOT NULL | |
| latitude | decimal(9,6) | nullable, CHECK `[-90,90]` | định vị trên bản đồ |
| longitude | decimal(9,6) | nullable, CHECK `[-180,180]` | định vị trên bản đồ; index `(latitude, longitude)` phục vụ tìm theo khu vực (bounding-box). Nếu cần tìm bán kính chính xác, cân nhắc bật PostGIS ở Phase 1+ |
| electricity_rate_override | decimal | nullable | **D16** override cấp tòa |
| water_rate_override | decimal | nullable | **D16** |
| property_type | varchar | NOT NULL, default `'long_term'` | **D9** — field mở cho Phase 1+ |

> Ảnh tòa nhà (bìa + gallery): `Media(owner_type='building', purpose='cover_photo'|'gallery_photo')`.

### 2.4 Floor (optional)
| Field | Type | Ràng buộc | Ghi chú |
|---|---|---|---|
| id | uuid | PK | |
| building_id | uuid | FK→Building, NOT NULL | |
| name | varchar | NOT NULL | vd "Tầng 2" |
| owner_id_hint | uuid | FK→User, **nullable** | chỉ gợi ý, **không phải nguồn chân lý** (**D25** — Room.owner_id luôn thắng) |

### 2.5 Room
| Field | Type | Ràng buộc | Ghi chú |
|---|---|---|---|
| id | uuid | PK | |
| building_id | uuid | FK→Building, NOT NULL | |
| floor_id | uuid | FK→Floor, nullable | |
| owner_id | uuid | FK→User, **NOT NULL** | **D25 — bắt buộc, 1 chủ/phòng** |
| name | varchar | NOT NULL | |
| area_m2 | decimal | nullable | |
| amenities | jsonb | nullable | |
| max_occupancy | int | NOT NULL | **D21** hard filter ghép bạn |
| gender_policy | enum (`any`,`male_only`,`female_only`) | default `any` | **D21** |
| house_rules | text | nullable | **D21** |
| base_rent_price | decimal | NOT NULL | |
| electricity_rate_override | decimal | nullable | **D16** — thứ tự đọc: room → building → landlord default |
| water_rate_override | decimal | nullable | **D16** |
| status | enum (`available`,`occupied`,`maintenance`) | cached/derived | nguồn chân lý = Contract active; cache để query nhanh cho dashboard (**D20**) |

> Ảnh phòng (bìa + gallery): `Media(owner_type='room', purpose='cover_photo'|'gallery_photo')`.

### 2.6 Contract
| Field | Type | Ràng buộc | Ghi chú |
|---|---|---|---|
| id | uuid | PK | |
| room_id | uuid | FK→Room, NOT NULL | |
| issued_by_user_id | uuid | FK→User, NOT NULL | = Room.owner_id (**D25**) |
| lead_tenant_user_id | uuid | FK→User, **nullable** | nullable để hỗ trợ tenant chưa có account (**D29**); nếu null thì lưu tên/SĐT trực tiếp trên contract |
| lead_tenant_name / lead_tenant_phone | varchar | nullable | dùng khi tenant không có account |
| status | enum (`draft`,`signed`,`active`,`expired`,`terminated`) | NOT NULL default `draft` | |
| signature_mode | enum (`template_upload`) | NOT NULL | **D18** — chỉ 1 giá trị, không còn e_sign/e_ack |
| signed_at | timestamp | nullable | |
| parsed_fields | jsonb | nullable | field OCR/parse từ PDF ký — chỉ hỗ trợ, không phải nguồn chuẩn (**D18**) |
| deposit_amount | decimal | NOT NULL | |
| monthly_rent | decimal | NOT NULL | |
| start_date / end_date | date | NOT NULL | |
| terms | text | nullable | |
| payment_config | enum (`representative`,`shared_tracking`) | NOT NULL default `representative` | **D22** — chỉ áp dụng khi ở ghép |
| deposit_settled | boolean | default false | cờ "đã thanh lý cọc" (đề xuất trong audit GĐ6) |

> Mẫu HĐ / file ký: `Media(owner_type='contract', purpose='contract_template'|'contract_signed')` — file ký (`contract_signed`) vẫn là **nguồn chuẩn pháp lý**, `parsed_fields` chỉ hỗ trợ tra cứu.

**Index quan trọng:** partial unique index `(room_id) WHERE status = 'active'` — chỉ 1 hợp đồng active/phòng.

### 2.7 ContractMember (thành viên ở ghép + CCCD)
| Field | Type | Ràng buộc | Ghi chú |
|---|---|---|---|
| id | uuid | PK | |
| contract_id | uuid | FK→Contract, NOT NULL | |
| user_id | uuid | FK→User, **nullable** | nullable nếu tenant không có account (**D29**) |
| full_name | varchar | NOT NULL | |
| phone | varchar | nullable | |
| is_lead | boolean | NOT NULL default false | |
| cccd_ocr_data | jsonb | nullable | **D17/5.6** — số, họ tên, ngày sinh, địa chỉ (OCR MVP; dữ liệu có cấu trúc, không phải file) |
| share_amount | decimal | nullable | dùng khi `payment_config = shared_tracking` (**D22**) |
| share_paid_status | enum (`unpaid`,`paid`) | nullable | chỉ dùng khi shared_tracking |

> Ảnh CCCD mặt trước/sau: `Media(owner_type='contract_member', purpose='cccd_front'|'cccd_back')` — **D17**, chụp 1 lần.

### 2.8 MeterReading
| Field | Type | Ràng buộc | Ghi chú |
|---|---|---|---|
| id | uuid | PK | |
| room_id | uuid | FK→Room, NOT NULL | |
| period | varchar(7) (`YYYY-MM`) | NOT NULL | |
| previous_reading | decimal | NOT NULL | baseline kỳ đầu nhập tay |
| current_reading | decimal | NOT NULL | |
| consumption | decimal | GENERATED (current − previous) | |
| is_baseline | boolean | default false | |
| confirmed_at | timestamp | NOT NULL | |

> Ảnh đối chứng công tơ: `Media(owner_type='meter_reading', purpose='meter_reading_evidence')` — nghiệp vụ yêu cầu tối thiểu 1 ảnh trước khi xác nhận (ràng buộc ở service, không phải DB).

**Index:** UNIQUE `(room_id, period)`.

### 2.9 Invoice
| Field | Type | Ràng buộc | Ghi chú |
|---|---|---|---|
| id | uuid | PK | |
| contract_id | uuid | FK→Contract, NOT NULL | |
| period | varchar(7) | NOT NULL | |
| rent_amount / electricity_amount / water_amount | decimal | NOT NULL | |
| other_fees | jsonb | nullable | |
| total_amount | decimal | NOT NULL | |
| status | enum (`pending`,`paid`,`overdue`,`void`) | NOT NULL default `pending` | **không sửa sau khi gửi** — void + tạo mới (audit trail, **D18/D20**) |
| voided_invoice_id | uuid | FK→Invoice, nullable, self-ref | trỏ tới hóa đơn bị thay thế (nếu có) |
| issued_at / due_date | timestamp / date | NOT NULL | |
| note | text | nullable | |

**Index:** UNIQUE `(contract_id, period)`.

### 2.10 Payment
| Field | Type | Ràng buộc | Ghi chú |
|---|---|---|---|
| id | uuid | PK | |
| invoice_id | uuid | FK→Invoice, NOT NULL | 1 Invoice — N Payment (retry) |
| method | enum (`vnpay`,`momo`,`cash`,`mock`) | NOT NULL | |
| status | enum (`pending`,`success`,`failed`) | NOT NULL | |
| amount | decimal | NOT NULL | |
| transaction_id | varchar | nullable | null cho cash |
| raw_gateway_response | jsonb | nullable | bằng chứng đối soát QR |
| paid_by_contract_member_id | uuid | FK→ContractMember, nullable | dùng khi shared_tracking |
| created_at | timestamp | | |

### 2.11 IssueReport
| Field | Type | Ràng buộc | Ghi chú |
|---|---|---|---|
| id | uuid | PK | |
| room_id | uuid | FK→Room, NOT NULL | |
| conversation_id | uuid | FK→Conversation, nullable | |
| reported_by_user_id | uuid | FK→User, **nullable** | null nếu landlord tự tạo thay tenant passive (**D29**) |
| status | enum (`open`,`in_progress`,`resolved`) | NOT NULL default `open` | |
| title / description | varchar / text | NOT NULL | |
| resolved_at | timestamp | nullable | |
| resolution_note | text | nullable | |

> Ảnh sự cố: `Media(owner_type='issue_report', purpose='issue_photo')`.

### 2.12 Conversation (Property Chat — D24′)
| Field | Type | Ràng buộc | Ghi chú |
|---|---|---|---|
| id | uuid | PK | |
| kind | enum (`room`,`building`) | NOT NULL | |
| room_id | uuid | FK→Room, nullable | bắt buộc nếu kind=room |
| building_id | uuid | FK→Building, nullable | bắt buộc nếu kind=building |

### 2.13 ConversationMember
| Field | Type | Ràng buộc | Ghi chú |
|---|---|---|---|
| id | uuid | PK | |
| conversation_id | uuid | FK→Conversation, NOT NULL | |
| user_id | uuid | FK→User, NOT NULL | |
| joined_at | timestamp | | |

**Index:** UNIQUE `(conversation_id, user_id)`.

### 2.14 Message
| Field | Type | Ràng buộc | Ghi chú |
|---|---|---|---|
| id | uuid | PK | |
| conversation_id | uuid | FK→Conversation, NOT NULL | |
| sender_user_id | uuid | FK→User, **nullable** | null = bot |
| type | enum (`text`,`image`,`file`,`bot`) | NOT NULL | |
| content | text | nullable | |
| metadata | jsonb | nullable | card payload: `{invoice_id}`, `{issue_id}`, `{meter_reading_id}`,... + mention list |

> File/ảnh đính kèm (khi `type = image|file`): `Media(owner_type='message', purpose='chat_attachment')`.

### 2.15 RoommateProfile
| Field | Type | Ràng buộc | Ghi chú |
|---|---|---|---|
| id | uuid | PK | |
| user_id | uuid | FK→User, UNIQUE, NOT NULL | chỉ tenant có account |
| lifestyle | jsonb | nullable | |
| personality | jsonb | nullable | |
| budget_min / budget_max | decimal | nullable | |
| bio | text | nullable | |
| id_verified | boolean | default false | badge xác minh tự nguyện (**D26**) |

### 2.16 MatchRequest
| Field | Type | Ràng buộc | Ghi chú |
|---|---|---|---|
| id | uuid | PK | |
| requester_user_id | uuid | FK→User, NOT NULL | |
| target_user_id | uuid | FK→User, NOT NULL | |
| room_id | uuid | FK→Room, nullable | ngữ cảnh áp constraint hard-filter (**D21**) |
| status | enum (`pending`,`accepted`,`rejected`) | NOT NULL default `pending` | |
| ai_score | decimal | nullable | **D28**, Stretch |
| ai_advice | text | nullable | **D28** |

**Index:** UNIQUE `(requester_user_id, target_user_id)` — cache mỗi cặp 1 lần (**D28**).

### 2.17 TenantHistory (Stretch — D26, consent-based)
| Field | Type | Ràng buộc | Ghi chú |
|---|---|---|---|
| id | uuid | PK | |
| tenant_user_id | uuid | FK→User, NOT NULL | |
| contract_id | uuid | FK→Contract, NOT NULL | |
| on_time_payment_score | decimal | nullable | |
| review_text | text | nullable | |
| consent_given | boolean | NOT NULL default false | **bắt buộc true mới hiển thị** (PDPD Art.11) |
| visible | boolean | default false | |

### 2.18 Notification (Stretch)
| Field | Type | Ràng buộc | Ghi chú |
|---|---|---|---|
| id | uuid | PK | |
| user_id | uuid | FK→User, NOT NULL | |
| type | varchar | NOT NULL | invoice_due, contract_expiry,... |
| payload | jsonb | nullable | |
| read_at | timestamp | nullable | |

### 2.19 Media (polymorphic — gom mọi file/ảnh của hệ thống)

**Nghiên cứu 2 hướng thiết kế** cho bài toán "8 loại entity đều có ảnh/file, tránh rải cột `*_url`":

| Hướng | Ưu điểm | Nhược điểm |
|---|---|---|
| **A. 1 bảng polymorphic** `media(owner_type, owner_id, purpose, ...)` — mô hình dùng bởi Rails Active Storage, Django `GenericForeignKey`, kiểu Instagram/Airbnb | 1 chỗ duy nhất quản lý file (upload, xoá, CDN, resize); thêm loại entity mới không cần bảng mới; dễ làm gallery + ảnh bìa (`is_cover`) + audit ai upload | `owner_id` **không có FK thật** (1 cột không FK được nhiều bảng) → toàn vẹn tham chiếu phải kiểm tra ở tầng service |
| **B. Bảng join riêng từng entity** (`RoomPhoto`, `BuildingPhoto`, `ContractDocument`, `IssuePhoto`, `ChatAttachment`,...) | FK thật, DB tự đảm bảo toàn vẹn tham chiếu | 6-8 bảng gần như trùng cấu trúc (id, url, order, uploaded_by, timestamps); thêm entity mới lại phải thêm bảng + migration mới |

**Chọn hướng A** cho MVP: quy mô đồ án không cần multi-tenant phức tạp, và số lượng entity có file (8 loại: user, room, building, contract, contract_member, meter_reading, issue_report, message) đủ lớn để hướng B gây trùng lặp đáng kể. Rủi ro mất toàn vẹn tham chiếu được giảm bằng cách:
- `owner_type` là enum cố định (không phải string tự do)
- `purpose` enum ràng buộc rõ vai trò file trong từng loại owner (vd `purpose='avatar'` chỉ hợp lệ khi `owner_type='user'`) — kiểm tra ở service layer khi insert
- 1 index `(owner_type, owner_id)` để query nhanh toàn bộ media của 1 entity

| Field | Type | Ràng buộc | Ghi chú |
|---|---|---|---|
| id | uuid | PK | |
| owner_type | enum (`user`,`room`,`building`,`contract`,`contract_member`,`meter_reading`,`issue_report`,`message`) | NOT NULL | |
| owner_id | uuid | NOT NULL | **không có FK thật** — xem giải thích trên |
| purpose | enum (`avatar`,`cover_photo`,`gallery_photo`,`cccd_front`,`cccd_back`,`contract_template`,`contract_signed`,`meter_reading_evidence`,`issue_photo`,`chat_attachment`) | NOT NULL | vai trò của file trong owner đó |
| file_type | enum (`image`,`document`,`video`,`other`) | NOT NULL default `image` | |
| url | varchar | NOT NULL | |
| thumbnail_url | varchar | nullable | |
| mime_type | varchar | nullable | |
| size_bytes | bigint | nullable | |
| width / height | int | nullable | chỉ dùng khi `file_type='image'` |
| display_order | int | NOT NULL default 0 | thứ tự trong gallery (room/building) |
| is_cover | boolean | NOT NULL default false | UNIQUE partial `(owner_type, owner_id) WHERE is_cover=true` — mỗi entity chỉ 1 ảnh bìa |
| uploaded_by_user_id | uuid | FK→User, nullable | |

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
Contract 1--N MeterReading (qua room_id, không trực tiếp)
Room 1--N MeterReading
Contract 1--N Invoice
Invoice 1--N Payment
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

---

## 4. Traceability theo quyết định (D-number)

| Bảng | D áp dụng |
|---|---|
| Room.owner_id NOT NULL, Building không bắt buộc owner, bỏ Manager | D25 |
| Building/Room rate override, thứ tự đọc room→building→landlord | D16 |
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
| LandlordProfile (rate mặc định) | CRUD | ✅ (của mình) | ❌ | ✅ | |
| User | Đọc/sửa profile | ✅/✅ (chính mình) | ✅/✅ (chính mình) | ✅ (mọi user) | |
| Media | Upload/Delete | ✅ (nếu có quyền sửa entity cha) | ✅ (nếu có quyền sửa entity cha, vd ảnh issue của mình) | ✅ | không check qua role, check qua quyền của owner_type tương ứng |
| Media | Đọc | ✅ (theo quyền đọc entity cha) | ✅ (theo quyền đọc entity cha) | ✅ | vd ảnh phòng available = public, ảnh CCCD = riêng tư |

### 5.3 Vì sao không cần RBAC đầy đủ

- Tập hành động và tài nguyên **cố định**, không có nhu cầu cấu hình quyền động theo tổ chức (không multi-tenant SaaS phân quyền tùy biến).
- Chỉ 3 role, không có phân cấp phức tạp hay custom permission theo khách hàng → bảng `Role`/`Permission`/`RolePermission` sẽ over-engineer cho MVP 13–14 tuần (đúng tinh thần D9/D19 — ưu tiên đơn giản, tránh phức tạp không cần thiết).
- Ownership check (row-level) quan trọng hơn role check trong hệ thống này (D25) — RBAC thuần theo role sẽ không đủ, vẫn cần thêm lớp ownership dù có RBAC hay không, nên giữ đơn giản: role (coarse-grained) + ownership (fine-grained) là đủ.
- Nếu sau này cần permission tùy biến (vd. landlord có nhân viên phụ, multi-org), có thể mở rộng thêm bảng `Role`/`Permission` ở Phase 1+ mà không phá vỡ `User.roles` hiện tại (roles array vẫn dùng làm coarse filter đầu tiên).
