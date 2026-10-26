# P6-01 — Contract vertical slice (Epic)

**Trạng thái:** 🟡 Open  
**Người phụ trách:** leminhkhai345  
**Người review:** baoduong17 (BE Lead, API owner), PM  
**Ước lượng:** 18 points cho Iteration 5 (P6-01a → P6-01d) + 8 points cho Iteration 6 (P6-01e)  
**Độ ưu tiên:** High  
**Phụ thuộc:** P5-08 (Building), P5-09 (Room), P6-04 (Media upload)  
**Issue:** `docs#TBD`

## Bối cảnh

Contract là bước tiếp theo trong vòng đời MVP: **Room trống → tạo HĐ nháp → in mẫu → hai bên ký tay → upload bản ký → kích hoạt HĐ → Room chuyển `occupied`**. Billing (meter reading, invoice) ở P6-02 cần một Contract `active` mới chạy được, nên epic này là đường găng của Iteration 5.

Quy tắc nghiệp vụ bắt buộc:

- **D18 (wet-sign, không OTP/PIN):** app sinh mẫu HĐ, hai bên ký tay trên giấy, landlord upload file đã ký. Chưa có file ký thì HĐ chưa được kích hoạt. Không có OTP, PIN hay `e_ack`.
- **D29 (landlord-solo):** tenant có thể chưa có tài khoản. `tenantId` được phép `null`; khi đó bắt buộc phải có `tenantName` và `tenantPhone` (DB CHECK `contract_tenant_identity_check`).
- **D9 (chỉ thuê dài hạn).**
- **Một HĐ `active` cho mỗi phòng:** partial unique index `(room_id) WHERE status = 'active'`.

Đây là issue cha, chỉ đóng khi mọi sub-issue Done. Pattern code theo slice mẫu [P5-08b](../../phase-5/issues/P5-08b-building-create-command.md).

## Sub-issue

| ID | Task | Endpoint | Iteration | Estimate | Phụ thuộc |
|---|---|---|---|---|---|
| [P6-01a](P6-01a-contract-domain-persistence.md) | Contract domain model, persistence và migration | — | It5 | 3 pts | P5-09a |
| [P6-01b](P6-01b-contract-create-and-manage-draft.md) | Tạo và quản lý HĐ nháp | `POST /contracts`, `GET /contracts`, `GET /contracts/{id}`, `PATCH /contracts/{id}` | It5 | 5 pts | P6-01a, P5-09b |
| [P6-01c](P6-01c-contract-template-and-draft-document.md) | Mẫu HĐ, áp mẫu và sinh tài liệu nháp | `GET /contract-templates`, `GET /contract-templates/{key}`, `PUT /contracts/{id}/apply-template`, `POST /contracts/{id}/generate-draft-document` | It5 | 5 pts | P6-01b, P6-04 |
| [P6-01d](P6-01d-contract-activate-signed-file.md) | Upload bản ký và kích hoạt HĐ | `POST /contracts/{id}/activate-contract` | It5 | 5 pts | P6-01b, P6-04 |
| [P6-01e](P6-01e-contract-members-and-checkout.md) | Thành viên HĐ, HĐ của tenant, checkout và quyết toán cọc (outline) | `GET /me/contracts`, `/contract-members*`, `complete-checkout`, `deposit-settlement` | It6 | 8 pts | P6-01d |

Thứ tự: `P6-01a → P6-01b → (P6-01c ∥ P6-01d) → P6-01e`.

P6-01c và P6-01d chỉ cần media ID từ P6-04 (`ownerType = contract`, `purpose = contract_template | contract_signed`). Nếu P6-04 trễ, làm trước phần domain/handler và test với media ID giả (UUID hợp lệ), ghi rõ blocker trong issue.

## Ngoài phạm vi epic này

- Tự động tạo kênh chat phòng sau khi kích hoạt (thuộc community-service, Stretch). Vẫn publish event `ContractActivated` qua outbox để sau này consumer dùng.
- Parse nội dung file ký (`parsed_fields`) và OCR hợp đồng.
- Thuê theo ngày (`rentalType = DAILY`) — mâu thuẫn với D9; xem mục "Sửa contract".
- Gia hạn, chấm dứt sớm, `suspended`/`expired` tự động (cron).

## Tiêu chí nghiệm thu chung (mọi sub-issue có write operation)

- Aggregate và outbox row được ghi trong cùng UoW transaction; khi rollback không còn row dở dang.
- Không publish RabbitMQ trực tiếp từ controller hay handler; relay publish sau commit.
- Route, schema và error code khớp `api-doc`. Mọi thay đổi contract đều có PR `api-doc` được API owner duyệt.
- Mỗi endpoint đã làm có sequence diagram trong `api-doc` và tag `x-apidog-status: released`.
- `landlord_id` luôn lấy từ JWT. Landlord chỉ thao tác được trên HĐ thuộc phòng của mình, nếu không trả `403 FORBIDDEN`.
- Manual verification (Apidog) ghi trong PR.

## Sửa contract cần API owner chốt trước khi bắt đầu P6-01b

| Vấn đề | Đề xuất |
|---|---|
| `rentalType` có `DAILY`, mâu thuẫn D9 (chỉ dài hạn) | Bỏ `DAILY`, giữ `MONTHLY` (hoặc bỏ hẳn field) |
| `tenantCccd` bắt buộc trong `ContractCreateRequestDto`, nhưng bảng `contracts` (`database-design.md` §2.7) không có cột CCCD | Thêm cột `tenant_cccd varchar(12)` (đề xuất, vì cần cho mẫu HĐ giấy) hoặc bỏ khỏi contract |
| `paymentDueDay` nằm trên Contract, trong khi D39 đặt `payment_due_day` ở `BillingSetting` | Giữ trên Contract làm snapshot hiển thị; Billing (P6-02) đọc từ BillingSetting |
| `templateKey`/`templateVariables` vừa có ở create, vừa có endpoint apply-template riêng | Create chỉ lưu `templateKey` (nullable); apply-template là cách chính để đổi mẫu |
| Chưa có endpoint upload bản ký; activate nhận thẳng `signedContractMediaId` | Giữ nguyên: FE upload qua P6-04 rồi gọi activate với media ID |

## Luồng xử lý chuẩn

```text
HTTP Request → Controller/DTO validation → Command Handler → UoW transaction
  → Contract (+ Room) aggregate → Repository save + Outbox append → Commit → Relay publish
```

## Nguồn tham chiếu

- `pm/phase-1/discovery/database-design.md` §2.7 (Contract), §2.8 (ContractMember), bảng `media`.
- `pm/phase-1/discovery/user_flow/landlord_user_flow.md` — Sub-Flow 2 "Tạo Hợp Đồng Thuê & Check-in".
- `api-doc/src/paths/contracts/*.yaml`, `src/requests/contracts/*`, `src/responses/dtos/contracts/*`.
- `pm/requirement.md` — D18, D29, D9.
