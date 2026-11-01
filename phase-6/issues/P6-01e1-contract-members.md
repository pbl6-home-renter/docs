# P6-01e1 — Thành viên hợp đồng: bảng, tự thêm đại diện khi activate, API thêm/xem/sửa/rời

**Epic:** [P6-01](P6-01-tenancy-contract-vertical-slice.md) · tách từ [P6-01e](P6-01e-contract-members-and-checkout.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** leminhkhai345  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 3 points · 8–10 giờ  
**Phụ thuộc:** P6-01d (handler activate — chưa có trên `main`), P6-09 (`api-docs` khớp `P6-D63`)  
**Repo / branch:** `Tenancy-Service` · `feature/p6-01e1-contract-members`  
**Iteration:** It6 (09/11–15/11)  
**Issue:** `docs#95`

> **Đọc trước khi code:** `AGENTS.md` và skill trong `.agents/skills/` của repo (backend: `be-feature-workflow`). Issue **không** quy định cách đặt file, đặt tên hay style — nếu issue nói khác skill thì làm theo skill. Nguồn mâu thuẫn xử lý theo [`P6-D75`](../decisions.md#d75--thứ-tự-ưu-tiên-nguồn-và-cách-xử-lý-câu-hỏi-mở): `decisions.md` > `api-docs` > skill > issue.

## Mục tiêu

Có bảng `contract_members`. Khi HĐ được activate, người đại diện tự thành member. Landlord thêm member, sửa SĐT và ghi nhận member rời phòng; landlord và tenant trong HĐ xem được danh sách member. Repository có sẵn hàm đếm `headCount` theo kỳ để Billing (P6-02g1) gọi.

## Quyết định áp dụng

- `P6-D63` — đại diện (`contracts.tenant_id/tenant_name/tenant_phone`) tự thành member khi activate, `joined_at = start_date`, không có cờ đại diện trong danh sách; thêm/rời chỉ khi HĐ `active` (`409 CONTRACT_NOT_ACTIVE`); rời = set `left_at`, không xóa; DTO thêm member chỉ có `contractId`, `tenantId?`, `tenantName`, `tenantPhone?`, `joinedAt`; liên kết tenant chỉ qua `tenantId`.
- `P6-D65` — `headCount` = member có `joined_at ≤ cuối kỳ` và (`left_at IS NULL` hoặc `left_at ≥ đầu kỳ`).
- `P2-D44` — không xóa cứng bản ghi.
- `P0-D29` — member có thể chưa có tài khoản (`tenant_id` null).
- `P6-D71` — `joinedAt` ∈ `[start_date, end_date]` (sai → `422 VALIDATION_FAILED`); `leftOn` ≥ `joinedAt` và ≤ `end_date` (sai → `422 LEFT_DATE_INVALID`); `MEMBER_ALREADY_EXISTS` khi HĐ đã có member **chưa rời** trùng `tenantId` (nếu có) hoặc trùng `tenantPhone` (nếu có); `status` suy ra `active` (`left_at IS NULL` hoặc `left_at > hôm nay`) / `left`; response bỏ `identityCardNumber`, `isRepresentative`, `TEMPORARY_ABSENT`. (Sửa `vehicleCount` khi `active` giao ở P6-01e3.)
- `P6-D74` — web không có ô chọn tài khoản → member tạo từ web có `tenantId = NULL`; API **vẫn nhận** `tenantId` (seed demo, mobile sau này).

## Contract

| Endpoint | operationId | Role | Thành công | Lỗi nghiệp vụ |
|---|---|---|---|---|
| `POST /contract-members` | `postContractMembers` | landlord | `201 CONTRACT_MEMBER_ADDED` + `Location` | `404`, `403 FORBIDDEN`, `409 CONTRACT_NOT_ACTIVE`, `409 MEMBER_ALREADY_EXISTS`, `422 TENANT_IDENTITY_INVALID`, `422 VALIDATION_FAILED` |
| `GET /contract-members?filter[contractId]=` | `getContractMembers` | landlord, tenant | `200 CONTRACT_MEMBERS_FETCHED` + `pagination` offset | `422 CONTRACT_ID_REQUIRED`, `404`, `403` |
| `PATCH /contract-members/{contractMemberId}` | `patchContractMembersContractmemberid` | landlord | `200 CONTRACT_MEMBER_UPDATED` | `404`, `403`, `409 MEMBER_LEFT`, `422` |
| `POST /contract-members/{contractMemberId}/leave-contract` | `postContractMembersContractmemberidLeaveContract` | landlord | `200 CONTRACT_MEMBER_LEFT` | `404`, `403`, `409 CONTRACT_NOT_ACTIVE`, `409 MEMBER_ALREADY_LEFT`, `422 LEFT_DATE_INVALID` |

- Path: `api-docs/src/paths/contracts/contract-members.yaml`, `contract-members-contractMemberId.yaml`, `contract-members-contractMemberId-leave-contract.yaml`.
- Request: `api-docs/src/requests/contracts/contract-member-add-request-dto.yaml`, `contract-member-update-request-dto.yaml` (`tenantPhone`), `contract-member-leave-request-dto.yaml` (`leftOn`).
- Response: `api-docs/src/responses/dtos/contracts/contract-member-add-response-dto.yaml`, `contract-member-list-response-dto.yaml`, `contract-member-update-response-dto.yaml`, `contract-member-leave-response-dto.yaml`.
- Làm theo `api-docs` **sau P6-09**: request thêm member không còn `identityCardNumber`, `dateOfBirth`, `gender`, `isRepresentative`. Bản hiện tại trên `main` còn các field này — không implement chúng.
- `GET`: chỉ `format=json` (khác → `422 VALIDATION_FAILED`, như P6-01b). Item: `id, contractId, tenantId, tenantName, tenantPhone, joinedAt, leftAt, status` (`active | left`, `P6-D71`).

### Mapping field

| Request / Response field | Domain prop | Cột DB (`database-design.md` §2.8) | Ghi chú / validation |
|---|---|---|---|
| `contractId` | `contractId` | `contract_id uuid NOT NULL` FK → `contracts` | HĐ phải thuộc landlord trong JWT |
| `tenantId` | `tenantId` | `tenant_id uuid NULL` | optional; không kiểm tra tồn tại bên Identity (giống P6-01b); web luôn gửi NULL (`P6-D74`) |
| `tenantName` | `tenantName` | `tenant_name varchar(254) NULL` | 1–254 ký tự; bắt buộc ở request |
| `tenantPhone` | `tenantPhone` | `tenant_phone varchar(12) NULL` | `^(0[0-9]{9}|\+84[0-9]{9})$`; `tenantId` null mà thiếu → `422 TENANT_IDENTITY_INVALID` (cùng rule `P0-D29` của `contracts`) |
| `joinedAt` | `joinedAt` | `joined_at date NOT NULL` | `YYYY-MM-DD`; ∈ `[start_date, end_date]` của HĐ, sai → `422 VALIDATION_FAILED` (`P6-D71`) |
| `leftOn` (request) / `leftAt` (response) | `leftAt` | `left_at date NULL` | `≥ joined_at` và `≤ end_date`, sai → `422 LEFT_DATE_INVALID`; CHECK `left_at IS NULL OR left_at >= joined_at` (`P6-D71`) |
| `status` (response) | getter suy ra | không có cột | `active` khi `left_at IS NULL` hoặc `left_at > hôm nay`, ngược lại `left` (`P6-D71`) |
| — | — | `id`, `created_at`, `updated_at`, `is_deleted` | base entity §2.0 |

- Chống trùng (`P6-D71`): kiểm trong use case **sau khi khóa HĐ** (`findByIdForUpdate`) — member chưa rời (định nghĩa như `status=active`) trùng `tenantId` hoặc trùng `tenantPhone` → `409 MEMBER_ALREADY_EXISTS`. Index phụ: partial unique `(contract_id, tenant_id) WHERE tenant_id IS NOT NULL AND left_at IS NULL AND is_deleted = false` (chặn race); index thường `(tenant_id)` cho P6-01e2.

### Ví dụ số — `headCount` kỳ `2026-11` (đầu kỳ `2026-11-01`, cuối kỳ `2026-11-30`)

| Member | `joined_at` | `left_at` | Đếm? |
|---|---|---|---|
| A (đại diện) | 2026-09-01 | NULL | ✅ |
| B | 2026-11-15 | NULL | ✅ |
| C | 2026-09-01 | 2026-10-31 | ❌ (rời trước đầu kỳ) |
| D | 2026-09-01 | 2026-11-01 | ✅ (`left_at ≥ đầu kỳ`) |
| E | 2026-12-01 | NULL | ❌ (vào sau cuối kỳ) |
| **Kết quả** | | | **3** |

## Tham chiếu code

- Module mẫu: `Tenancy-Service/src/modules/rate-policy/` (pattern mới nhất) và `Tenancy-Service/src/modules/contract/` (cùng module; member là aggregate riêng nằm trong module `contract`).
- Đọc HĐ + kiểm tra chủ: `CONTRACT_DI_TOKEN.REPOSITORY` → `ContractRepository.findById` / `findByIdForUpdate` (`src/modules/contract/domain/repositories/contract.repository.ts`).
- Quyền tenant đọc HĐ hiện có: `src/modules/contract/application/queries/contract-get-by-id/contract-get-by-id.query.handler.ts`.
- Lỗi unique Postgres: `src/shared/infrastructure/database/postgres-error-code.ts`; UoW + outbox: `src/modules/rate-policy/application/commands/`.
- Migration mẫu: `src/database/migrations/1793335626475-CreateContractsTable.ts`.

## Các bước triển khai

### Bước 1 — Đọc contract sau P6-09, chuẩn bị dữ liệu

- **Cách làm:** pull `main`; đọc PR P6-09 phần member; chuẩn bị 1 HĐ `active` của landlord A (activate qua P6-01d, hoặc `UPDATE contracts SET status='active'` nếu P6-01d chưa merge), 1 HĐ `draft`, 1 HĐ của landlord B.
- **Kiểm tra bước:** `GET /api/v1/tenancy/health` → `200`; `SELECT id, status, landlord_id FROM contracts` thấy đủ 3 HĐ.

### Bước 2 — Domain `ContractMember` + repository port

- **Cách làm:**
  - Aggregate `ContractMember`: `add(...)` (kiểm tra rule `P0-D29`, phát event `contract_member.added`), `updatePhone(phone)` (đã rời → `MEMBER_LEFT`), `leave(leftOn)` (đã rời → `MEMBER_ALREADY_LEFT`, `leftOn < joinedAt` → `LEFT_DATE_INVALID`, event `contract_member.left`); getter `status` (`active`/`left`, nhận `today`).
  - Exception mới: `CONTRACT_NOT_ACTIVE` (409 — P6-01e3 dùng lại), `MEMBER_ALREADY_EXISTS`, `MEMBER_LEFT`, `MEMBER_ALREADY_LEFT` (409), `LEFT_DATE_INVALID` (422).
  - Repository port, **chữ ký cố định** vì P6-01e3 và P6-02g1 gọi:

    ```ts
    findById(id: Uuid, context?: TransactionContext): Promise<ContractMember | null>;
    findByIdForUpdate(id: Uuid, context: TransactionContext): Promise<ContractMember | null>;
    /** Chưa rời (P6-D71): left_at IS NULL OR left_at > today. */
    findActiveByContract(contractId: Uuid, context?: TransactionContext): Promise<ContractMember[]>;
    /** P6-D71: member chưa rời trùng tenantId hoặc trùng tenantPhone (bỏ qua field null; excludeId cho PATCH). */
    existsActiveDuplicate(contractId: Uuid, match: { tenantId: Uuid | null; tenantPhone: string | null; excludeId?: Uuid }, context?: TransactionContext): Promise<boolean>;
    findPageByContract(contractId: Uuid, query: OffsetPageQuery): Promise<PaginatedResult<ContractMember>>;
    /** P6-D65: joined_at <= periodEnd AND (left_at IS NULL OR left_at >= periodStart). Dates 'YYYY-MM-DD'. */
    countHeadsInPeriod(contractId: Uuid, periodStart: string, periodEnd: string, context?: TransactionContext): Promise<number>;
    ```
  - Thêm DI token cho member repository và **export** khỏi `ContractModule` (P6-02g1 inject token này, giống cách `contract` đang dùng `ROOM_DI_TOKEN.REPOSITORY`).
- **Kiểm tra bước:** `npm run build` pass.

### Bước 3 — Persistence + migration (kèm backfill)

- **Cách làm:** TypeORM entity theo bảng Mapping; `npm run migration:generate -- name=CreateContractMembersTable`. Trong `up()` thêm câu backfill đại diện cho HĐ đã `active` trước task này:
  `INSERT INTO contract_members (contract_id, tenant_id, tenant_name, tenant_phone, joined_at) SELECT id, tenant_id, tenant_name, tenant_phone, start_date FROM contracts WHERE status = 'active' AND is_deleted = false;`
- **Kiểm tra bước:**
  - `migration:run` → `migration:revert` → `migration:run` pass.
  - `SELECT count(*) FROM contract_members` = số HĐ `active`.
  - Insert tay 2 dòng cùng `(contract_id, tenant_id)` còn ở → lỗi unique; `UPDATE ... SET left_at = joined_at - 1` → lỗi CHECK (`left_at = joined_at` hợp lệ).
  - Với dữ liệu bảng Ví dụ số: `countHeadsInPeriod(id, '2026-11-01', '2026-11-30')` trả `3` (gọi tạm qua script/REPL hoặc ghi SQL tương đương vào PR).

### Bước 4 — Tự thêm đại diện khi activate

- **File sửa:** handler activate do P6-01d tạo (`src/modules/contract/application/commands/contract-activate/` theo P6-01d).
- **Cách làm:** trong **cùng** `unitOfWork.run` sau `contract.activate(...)`: tạo `ContractMember` từ `contract.tenantId/tenantName/tenantPhone`, `joinedAt = contract.startDate`, save + append event vào outbox chung.
- **Kiểm tra bước:** activate HĐ draft → `200 CONTRACT_ACTIVATED`; `SELECT tenant_id, joined_at FROM contract_members WHERE contract_id = :id` ra đúng 1 dòng, `joined_at = start_date`. Tạm `throw` sau khi save member → `500`, HĐ vẫn `draft`, không có member. Xóa dòng throw.

### Bước 5 — `POST /contract-members` + `PATCH /contract-members/{id}`

- **Cách làm (thêm):** trong UoW: `findByIdForUpdate(contractId)` → `404`; khác landlord → `403`; `status ≠ active` → `409 CONTRACT_NOT_ACTIVE`; `joinedAt` ngoài `[start_date, end_date]` → `422 VALIDATION_FAILED`; `existsActiveDuplicate` → `409 MEMBER_ALREADY_EXISTS`; `ContractMember.add` → save → outbox. Bắt unique violation → `409 MEMBER_ALREADY_EXISTS`.
- **Cách làm (sửa SĐT):** load member + HĐ (khóa HĐ); khác landlord → `403`; SĐT mới trùng member chưa rời khác → `409 MEMBER_ALREADY_EXISTS`; `updatePhone`.
- **Kiểm tra bước:**
  - `POST /api/v1/contract-members` `{ "contractId": "<active>", "tenantName": "Lê Văn C", "tenantPhone": "0912345678", "joinedAt": "2026-11-05" }` → `201 CONTRACT_MEMBER_ADDED`, có `Location`.
  - Cùng body nhưng `contractId` = HĐ draft → `409 CONTRACT_NOT_ACTIVE`.
  - `tenantId` = tenant của đại diện → `409 MEMBER_ALREADY_EXISTS`; gửi lại body trên (trùng `tenantPhone` `0912345678`, không có `tenantId`) → `409 MEMBER_ALREADY_EXISTS`.
  - `joinedAt` trước `start_date` hoặc sau `end_date` → `422 VALIDATION_FAILED`.
  - Bỏ `tenantPhone`, `tenantId` null → `422 TENANT_IDENTITY_INVALID`; gửi `identityCardNumber` → `422` (field lạ).
  - `PATCH /api/v1/contract-members/<id>` `{ "tenantPhone": "0987654321" }` → `200 CONTRACT_MEMBER_UPDATED`.

### Bước 6 — `POST /contract-members/{id}/leave-contract`

- **Cách làm:** UoW, lock member + HĐ; HĐ không `active` → `409 CONTRACT_NOT_ACTIVE`; `leftOn > end_date` → `422 LEFT_DATE_INVALID` (kiểm ở handler, xem Blocker P6-01e3); `member.leave(leftOn)`.
- **Kiểm tra bước:** `{ "leftOn": "2026-11-20" }` → `200 CONTRACT_MEMBER_LEFT`, `leftAt = 2026-11-20`; gọi lại → `409 MEMBER_ALREADY_LEFT`; member khác với `leftOn` = `joinedAt − 1 ngày` hoặc `> end_date` → `422 LEFT_DATE_INVALID` (`leftOn = joinedAt` → `200`); `PATCH` member đã rời → `409 MEMBER_LEFT`. `SELECT is_deleted FROM contract_members WHERE id = :id` vẫn `false`.

### Bước 7 — `GET /contract-members`

- **Cách làm:** thiếu `filter[contractId]` → `422 CONTRACT_ID_REQUIRED`; HĐ không có → `404`. Quyền: landlord chủ HĐ, hoặc tenant là `contracts.tenant_id` / member chưa rời của HĐ đó (`P6-D63`); còn lại → `403`. Sắp xếp `joinedAt asc`. Không có cờ đại diện, CCCD trong item; `status` suy ra theo `P6-D71`.
- **Kiểm tra bước:** landlord A → `200`, có đại diện + member mới (`status: active`), member đã rời có `status: left`; token tenant đại diện → `200`; tenant khác → `403`; landlord B → `403`; không có filter → `422 CONTRACT_ID_REQUIRED`.

### Bước 8 — Swagger, outbox, `api-docs`

- **Kiểm tra bước:** Swagger `/api/v1/tenancy/swagger` có 4 operation đúng `operationId`; `SELECT event_type FROM outbox_messages ORDER BY sequence DESC LIMIT 3` có `contract_member.added`, `contract_member.left`; `npm run build` + `npm run lint` pass.

## Ngoài phạm vi

- Ảnh CCCD member (`cccd_front/back`), tự liên kết tenant theo SĐT — Stretch (`P6-D63`, `P6-D74`).
- `GET /me/contracts` → P6-01e2; checkout set `left_at` hàng loạt → P6-01e3.
- Kiểm tra `tenantId` có tồn tại/đúng role bên Identity; thêm member vào kênh chat (Stretch).
- Xuất `xlsx/csv/pdf` cho `GET /contract-members`.

## Blocker

- Không có. (`status` member, khoảng ngày, chống trùng đã chốt ở `P6-D71`; liên kết tài khoản ở `P6-D74`.)

## Cập nhật `api-docs` (bắt buộc trước khi đóng issue)

- [ ] Sequence diagram cho 4 endpoint + đoạn "activate thêm đại diện" trong `contracts-contractId-activate-contract.yaml`.
- [ ] `x-apidog-status: released` cho 4 endpoint; sync Apidog.

## Acceptance (Apidog)

- [ ] Activate HĐ → đại diện có trong `GET /contract-members`, `joinedAt = startDate`.
- [ ] Thêm member HĐ `active` → `201 CONTRACT_MEMBER_ADDED`; HĐ `draft` → `409 CONTRACT_NOT_ACTIVE`.
- [ ] Trùng `tenantId` hoặc `tenantPhone` với member chưa rời → `409 MEMBER_ALREADY_EXISTS`; `joinedAt` ngoài khoảng HĐ → `422 VALIDATION_FAILED`; thiếu SĐT khi không có `tenantId` → `422 TENANT_IDENTITY_INVALID`.
- [ ] Rời → `200 CONTRACT_MEMBER_LEFT`; rời lại → `409 MEMBER_ALREADY_LEFT`; `leftOn < joinedAt` hoặc `> end_date` → `422 LEFT_DATE_INVALID`; sửa member đã rời → `409 MEMBER_LEFT`.
- [ ] Item `GET` có `status` `active`/`left`, không có `identityCardNumber`/`isRepresentative`.
- [ ] `GET` thiếu `filter[contractId]` → `422 CONTRACT_ID_REQUIRED`; HĐ không tồn tại → `404`.
- [ ] Landlord khác / tenant ngoài HĐ → `403 FORBIDDEN`; token tenant gọi `POST` → `403`; không token → `401`.
- [ ] `countHeadsInPeriod` với dữ liệu Ví dụ số trả `3` (ghi kết quả vào PR).

## Definition of Done

- [ ] Mọi bước qua phần Kiểm tra bước; mọi ô Acceptance được **tick bởi người làm**, kèm export Apidog hoặc ảnh chụp trong PR.
- [ ] `npm run build` + `npm run lint` pass; không có file test, không sửa `src/shared`.
- [ ] Migration sinh bằng `migration:generate`, `migration:run` + `migration:revert` pass từ DB trống.
- [ ] PR vào `main` ghi `Closes pbl6-home-renter/docs#<số issue>`, ≥ 1 reviewer approve.
