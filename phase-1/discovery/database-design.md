# Thiết kế Cơ sở dữ liệu & Phân quyền theo Role
**Dự án:** Nền tảng quản lý thuê trọ dài hạn (Landlord Web + Tenant Mobile + AI)
**Nguồn:** decisions.md (D1–D29), feature-list.md, user-behavior-workflow.md
**Phạm vi:** MVP theo D9 (dài hạn only), D25 (ownership), D29 (landlord-solo resilience)

---

## 1. Nguyên tắc thiết kế

1. **Role không dùng RBAC (không có bảng Role/Permission riêng).** `User.role` là enum đơn: `landlord | tenant | admin`. Mỗi user chỉ thuộc 1 role — landlord và tenant là 2 user tách biệt (D13). Kiểm tra quyền = so khớp role trong JWT + kiểm tra sở hữu (ownership check) ở tầng service, không cần bảng trung gian.
2. **Ownership là nguồn chân lý phụ, không phải role.** Có role `landlord` chưa đủ — phải là đúng `Room.owner_id` / `Contract.issued_by_user_id` mới được thao tác (D25).
3. **Trạng thái phòng là derived/cached**, nguồn chân lý là `Contract.status` đang active cho phòng đó, không phải bảng riêng (ghi chú trong decisions.md).
4. **Không có bảng Manager/Delegation** — bỏ hoàn toàn khỏi MVP (D25).
5. **Không có bảng liên quan chữ ký điện tử** (e_sign, e_ack, OTP, PIN) — chỉ còn `signature_mode = template_upload` (D18).
6. **Schema giữ mở cho short-term (Phase 1+)** qua field `Building.property_type`, không redesign (D9).
7. **Mọi luồng nghiệp vụ phải chạy được với `tenant_user_id = NULL`** trên các bản ghi liên quan tenant thụ động (D29) — xem mục 5.

---

## 2. Danh sách Entity

### 2.1 User
| Field | Type | Ràng buộc | Ghi chú |
|---|---|---|---|
| id | uuid | PK | |
| phone | varchar(15) | UNIQUE, NOT NULL | định danh chính (VN) |
| email | varchar | UNIQUE, NOT NULL | Phương thức verify chính |
| password | varchar | NOT NULL | |
| full_name | varchar | NOT NULL | |
| avatar_url | varchar | nullable | |
| role | enum (`landlord`,`tenant`,`admin`) | NOT NULL | **D13** — enum đơn, mỗi user 1 role |

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
| electricity_rate_override | decimal | nullable | **D16** override cấp tòa |
| water_rate_override | decimal | nullable | **D16** |
| property_type | varchar | NOT NULL, default `'long_term'` | **D9** — field mở cho Phase 1+ |

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
| generated_template_file_url | varchar | nullable | mẫu HĐ sinh ra |
| uploaded_signed_file_url | varchar | nullable | file ký tay upload — **nguồn chuẩn pháp lý** |
| signed_at | timestamp | nullable | |
| parsed_fields | jsonb | nullable | field OCR/parse từ PDF ký — chỉ hỗ trợ, không phải nguồn chuẩn (**D18**) |
| deposit_amount | decimal | NOT NULL | |
| monthly_rent | decimal | NOT NULL | |
| start_date / end_date | date | NOT NULL | |
| terms | text | nullable | |
| payment_config | enum (`representative`,`shared_tracking`) | NOT NULL default `representative` | **D22** — chỉ áp dụng khi ở ghép |
| deposit_settled | boolean | default false | cờ "đã thanh lý cọc" (đề xuất trong audit GĐ6) |
| created_at | timestamp | | |

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
| cccd_image_url | varchar | nullable | **D17** — chụp 1 lần |
| cccd_ocr_data | jsonb | nullable | **D17/5.6** — số, họ tên, ngày sinh, địa chỉ (OCR MVP) |
| share_amount | decimal | nullable | dùng khi `payment_config = shared_tracking` (**D22**) |
| share_paid_status | enum (`unpaid`,`paid`) | nullable | chỉ dùng khi shared_tracking |

### 2.8 MeterReading
| Field | Type | Ràng buộc | Ghi chú |
|---|---|---|---|
| id | uuid | PK | |
| room_id | uuid | FK→Room, NOT NULL | |
| period | varchar(7) (`YYYY-MM`) | NOT NULL | |
| previous_reading | decimal | NOT NULL | baseline kỳ đầu nhập tay |
| current_reading | decimal | NOT NULL | |
| consumption | decimal | GENERATED (current − previous) | |
| photo_url | varchar | NOT NULL | ảnh đối chứng |
| is_baseline | boolean | default false | |
| confirmed_at | timestamp | NOT NULL | |

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
| photos | jsonb | nullable | |
| resolved_at | timestamp | nullable | |
| resolution_note | text | nullable | |

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
| created_at | timestamp | | |

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
| User.role là enum đơn | D13 |
| Conversation/Message | D24′ |
| MatchRequest unique(requester,target), ai_score/ai_advice | D28 |
| Room.max_occupancy/gender_policy/house_rules dùng làm hard filter | D21 |
| TenantHistory.consent_given bắt buộc | D26 |
| Contract.lead_tenant_user_id nullable, ContractMember.user_id nullable, IssueReport.reported_by_user_id nullable | D29 (zero tenant login) |
| Building.property_type mở rộng | D9 |

---

## 5. Thiết kế phân quyền theo Role (không RBAC)

### 5.1 Mô hình role

- **Không có bảng `Role` hay `Permission` riêng.** Quyền được suy ra trực tiếp từ 2 lớp kiểm tra ở tầng application (service/guard), không phải từ dữ liệu quan hệ:
  1. **Role check** — user có role cần thiết không (`landlord` / `tenant` / `admin`), lấy từ `User.role` (enum đơn) — đã đúng theo **D13**.
  2. **Ownership check** — nếu resource có `owner_id`/`issued_by_user_id`/`lead_tenant_user_id`/`user_id` thì phải khớp với `request.user.id`, trừ khi role = `admin`.
- JWT payload: `{ sub: user_id, role: "landlord" }` — không nhúng permission chi tiết.
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

### 5.3 Vì sao không cần RBAC đầy đủ

- Tập hành động và tài nguyên **cố định**, không có nhu cầu cấu hình quyền động theo tổ chức (không multi-tenant SaaS phân quyền tùy biến).
- Chỉ 3 role, không có phân cấp phức tạp hay custom permission theo khách hàng → bảng `Role`/`Permission`/`RolePermission` sẽ over-engineer cho MVP 13–14 tuần (đúng tinh thần D9/D19 — ưu tiên đơn giản, tránh phức tạp không cần thiết).
- Ownership check (row-level) quan trọng hơn role check trong hệ thống này (D25) — RBAC thuần theo role sẽ không đủ, vẫn cần thêm lớp ownership dù có RBAC hay không, nên giữ đơn giản: role (coarse-grained) + ownership (fine-grained) là đủ.
- Nếu sau này cần permission tùy biến (vd. landlord có nhân viên phụ, multi-org), có thể mở rộng thêm bảng `Role`/`Permission` ở Phase 1+ mà không phá vỡ `User.role` hiện tại (enum đơn vẫn dùng làm coarse filter đầu tiên).
