# P6-01e3 — Checkout: kết thúc hợp đồng, member rời, phòng chuyển `maintenance` (+ sửa số xe khi HĐ `active`)

**Epic:** [P6-01](P6-01-tenancy-contract-vertical-slice.md) · tách từ [P6-01e](P6-01e-contract-members-and-checkout.md)  
**Trạng thái:** 🟡 Open (ước lượng 2 → 3 points: thêm bước sửa `vehicleCount`/`description` khi `active` theo `P6-D71`)  
**Người phụ trách:** leminhkhai345  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 3 points · 7–9 giờ  
**Phụ thuộc:** P6-01e1 (member + `leave()`), P6-01d (`Room.releaseByContract()`), P6-02g1 (bảng `invoices`), P6-09 (`api-docs` checkout theo `P6-D62`)  
**Repo / branch:** `Tenancy-Service` · `feature/p6-01e3-contract-checkout`  
**Iteration:** It6 (09/11–15/11)  
**Issue:** `docs#97`

> **Đọc trước khi code:** `AGENTS.md` và skill trong `.agents/skills/` của repo (backend: `be-feature-workflow`). Issue **không** quy định cách đặt file, đặt tên hay style — nếu issue nói khác skill thì làm theo skill. Nguồn mâu thuẫn xử lý theo [`P6-D75`](../decisions.md#d75--thứ-tự-ưu-tiên-nguồn-và-cách-xử-lý-câu-hỏi-mở): `decisions.md` > `api-docs` > skill > issue.

## Mục tiêu

Landlord gọi `POST /contracts/{id}/complete-checkout { completedOn }` khi hóa đơn kỳ trả phòng đã phát hành: HĐ → `terminated`, mọi member còn ở có `left_at = completedOn`, phòng → `maintenance` — trong **một transaction** cùng outbox. Sau đó landlord bấm `mark-ready` để phòng về `available`. Kèm theo: `PATCH /contracts/{id}` cho HĐ `active` sửa được `vehicleCount` và `description` (gỡ `VEHICLE_COUNT_MISSING` của Billing).

## Quyết định áp dụng

- `P6-D62` — điều kiện: HĐ `active` **và** hóa đơn của kỳ chứa `completedOn` đã `issued`, không còn bản `pending` của kỳ đó; không đạt → `409 SETTLEMENT_NOT_READY`. Kết quả: HĐ `terminated`, member còn ở `left_at = completedOn`, phòng `maintenance`, về `available` bằng `POST /rooms/{id}/mark-ready`. Không phí chấm dứt sớm, không prorate theo ngày trả.
- `P6-D61` — **không** quyết toán cọc, **không** thêm cột vào `contracts` (không lưu `completed_on`/`terminated_at`; ngày trả phòng nằm ở `contract_members.left_at` và payload event).
- `P6-D64` — không có hóa đơn quyết toán riêng; chênh lệch/đền bù ghi `other_fees` của hóa đơn kỳ cuối **trước** khi phát hành.
- `P6-D63` — rời = set `left_at`, không xóa member.
- `P6-D71` — `completedOn` ≥ `start_date` và ≤ hôm nay (không trả phòng ngày tương lai), sai → `422 VALIDATION_FAILED`; CHECK member là `left_at ≥ joined_at`; HĐ `active` chỉ sửa được `vehicleCount` và `description`, field khác vẫn `409 CONTRACT_NOT_DRAFT`; hóa đơn `pending` dùng số xe mới khi generate lại, `issued` giữ snapshot.

## Contract

| Endpoint | operationId | Role | Thành công | Lỗi nghiệp vụ |
|---|---|---|---|---|
| `POST /contracts/{contractId}/complete-checkout` | `postContractsContractidCompleteCheckout` | landlord | `200 CONTRACT_CHECKOUT_COMPLETED` | `404`, `403 FORBIDDEN`, `409 CONTRACT_NOT_ACTIVE`, `409 SETTLEMENT_NOT_READY`, `422 VALIDATION_FAILED` |
| `PATCH /contracts/{contractId}` (đã có, P6-01b) — mở rộng cho `active` | `patchContractsContractid` | landlord | `200 CONTRACT_UPDATED` | `409 CONTRACT_NOT_DRAFT` (HĐ `active` gửi field khác `vehicleCount`/`description`; HĐ `terminated`) |

- Path: `api-docs/src/paths/contracts/contracts-contractId-complete-checkout.yaml`; request `api-docs/src/requests/contracts/contract-checkout-complete-request-dto.yaml` (`completedOn: date`); response `api-docs/src/responses/dtos/contracts/contract-checkout-complete-response-dto.yaml`.
- Làm theo `api-docs` **sau P6-09**: response `status = terminated` (bản trên `main` còn `expired`), không còn `pending_cleanup`, `SETTLEMENT_NOT_READY` là **409** (bản trên `main` ghi 422 — `decisions.md` thắng theo `P6-D75`).

### Mapping field

| Field | Domain | DB | Ghi chú |
|---|---|---|---|
| `completedOn` (request) | tham số `terminate(completedOn)` / `member.leave(completedOn)` | `contract_members.left_at` | `YYYY-MM-DD`; `start_date ≤ completedOn ≤ hôm nay` và `≥ joined_at` của mọi member còn ở (CHECK `left_at ≥ joined_at`, `P6-D71`); sai → `422 VALIDATION_FAILED` |
| kỳ kiểm tra | `period = completedOn.slice(0, 7)` | `invoices.period` | `2026-11-20` → `2026-11` |
| `status` (response) | `ContractStatus.TERMINATED` | `contracts.status` | |
| `completedOn` (response) | echo request | — | không lưu cột riêng (`P6-D61`) |
| — | `Room.releaseByContract()` | `rooms.status = maintenance` | |

### Ví dụ điều kiện `SETTLEMENT_NOT_READY` (HĐ X, `completedOn = 2026-11-20`)

| Hóa đơn của X kỳ `2026-11` | Kết quả |
|---|---|
| Không có bản nào | `409 SETTLEMENT_NOT_READY` |
| 1 bản `pending` | `409 SETTLEMENT_NOT_READY` |
| 1 bản `void` + 1 bản `pending` (đang làm lại) | `409 SETTLEMENT_NOT_READY` |
| 1 bản `void` + 1 bản `issued` | `200` |
| 1 bản `issued` | `200` |

## Đọc hóa đơn từ module `contract` (cách làm cross-module)

- Module `invoice` (P6-02g1) sẽ phụ thuộc `contract` (đọc HĐ, `countHeadsInPeriod`). Nếu `ContractModule` import ngược `InvoiceModule` sẽ thành vòng lặp và application `contract` dính entity của module khác.
- Vì vậy: `contract` **tự khai báo port** ở `application/ports/` (cùng chỗ `contract-document-renderer.port.ts` đang có), ví dụ `isPeriodSettled(contractId, period, context): Promise<boolean>`. Adapter đặt ở `contract/infrastructure/`, chạy SQL thẳng trên bảng `invoices` qua `EntityManager` của `TransactionContext` (cùng DB, cùng transaction), **không import** TypeORM entity/repository của module `invoice`:

  ```sql
  SELECT bool_or(status = 'issued') AND NOT bool_or(status = 'pending') AS settled
  FROM invoices WHERE contract_id = $1 AND period = $2 AND is_deleted = false;
  -- không có dòng → NULL → coi như false
  ```
- Bind port → adapter trong `contract.module.ts`. Khi P6-02g1 đổi tên cột/bảng thì chỉ sửa adapter này.

## Tham chiếu code

- Command UoW + nhiều aggregate + outbox: handler activate của P6-01d; pattern `src/modules/rate-policy/application/commands/`.
- `ContractEntity` (thêm `terminate`): `src/modules/contract/domain/entities/contract.entity.ts`; enum `src/modules/contract/domain/enums/contract-status.enum.ts` (đã có `TERMINATED`); event constants `src/modules/contract/domain/constants/contract-event.constants.ts`.
- Room: `src/modules/room/domain/entities/room.entity.ts` (`releaseByContract()` do P6-01d thêm; `markReady()` đã có), `RoomRepository.findByIdForUpdate`.
- Port mẫu: `src/modules/contract/application/ports/contract-document-renderer.port.ts`; context transaction: `src/shared/infrastructure/database/transaction/typeorm-transaction-context.ts`.
- Member: `findActiveByContract`, `ContractMember.leave()` (P6-01e1), exception `CONTRACT_NOT_ACTIVE` (P6-01e1).

## Các bước triển khai

### Bước 1 — Dữ liệu thử

- **Cách làm:** sau khi P6-02g1 merge: HĐ X `active` (2 member còn ở), sinh + phát hành hóa đơn kỳ `2026-11` qua `POST /invoices/generate` và `POST /invoices/issue-invoice`; HĐ W `active` chỉ có hóa đơn `pending` kỳ `2026-11`.
- **Kiểm tra bước:** `SELECT contract_id, period, status FROM invoices WHERE period = '2026-11'` → X `issued`, W `pending`.

### Bước 2 — Domain

- **Cách làm:**
  - `ContractEntity.terminate(completedOn)`: không `active` → `ContractNotActiveException`; set `TERMINATED`, phát `ContractTerminatedEvent` (`contract.terminated`, payload `id, roomId, landlordId, completedOn`).
  - `SettlementNotReadyException` (409, `SETTLEMENT_NOT_READY`).
  - Nếu P6-01d chưa viết `Room.releaseByContract()`: thêm — `OCCUPIED → MAINTENANCE` + `RoomStatusChangedEvent`; đã `MAINTENANCE` thì không làm gì.
- **Kiểm tra bước:** `npm run build` pass.

### Bước 3 — Port + adapter đọc hóa đơn

- **Cách làm:** theo mục "Đọc hóa đơn từ module `contract`".
- **Kiểm tra bước:** chạy SQL adapter trong DB local: X/`2026-11` → `true`, W/`2026-11` → `false`, X/`2026-12` → `NULL`. Ghi kết quả vào PR.

### Bước 4 — Command checkout

- **Cách làm (một `unitOfWork.run`):**
  1. `contract = findByIdForUpdate` → `404`; khác landlord → `403`; `status ≠ active` → `409 CONTRACT_NOT_ACTIVE`; `completedOn < start_date` hoặc `> hôm nay` → `422 VALIDATION_FAILED` (`P6-D71`).
  2. `isPeriodSettled(contract.id, period, ctx)` = false → `409 SETTLEMENT_NOT_READY` (kiểm **sau** khi khóa HĐ).
  3. `members = findActiveByContract(contract.id, ctx)`; mỗi member `leave(completedOn)` — `LEFT_DATE_INVALID` map sang `422 VALIDATION_FAILED`.
  4. `contract.terminate(completedOn)`; `room = roomRepository.findByIdForUpdate(contract.roomId, ctx)`; `room.releaseByContract()`.
  5. Save HĐ, member, room; append outbox event của cả ba loại aggregate.
- **Kiểm tra bước:** `npm run build` pass.

### Bước 5 — Request/response, route

- **Cách làm:** `@Post(':contractId/complete-checkout')` trong `contract.controller.ts`, `@Roles(UserRole.LANDLORD)`, `@HttpCode(200)`, response code `CONTRACT_CHECKOUT_COMPLETED`.
- **Kiểm tra bước:**
  - `POST /api/v1/contracts/<X>/complete-checkout` `{ "completedOn": "2026-11-20" }` → `200`, `data = { id, status: "terminated", completedOn: "2026-11-20" }`.
  - SQL: `contracts.status = 'terminated'`; `SELECT count(*) FROM contract_members WHERE contract_id = :x AND left_at IS NULL` = 0; `rooms.status = 'maintenance'`.
  - `POST /api/v1/rooms/<roomX>/mark-ready` → `200`, phòng `available`.
  - Gọi checkout lại X → `409 CONTRACT_NOT_ACTIVE`; W → `409 SETTLEMENT_NOT_READY`; `completedOn` = ngày trước `start_date` hoặc ngày mai → `422 VALIDATION_FAILED`; `completedOn` < `joined_at` của một member → `422 VALIDATION_FAILED`; body rỗng → `422`.

### Bước 6 — `PATCH /contracts/{id}` khi HĐ `active` (`P6-D71`)

- **Cách làm:** trong `ContractEntity` thêm hành vi cho HĐ `active` chỉ đổi `vehicleCount` (≥ 0 hoặc `null`) và `description`; handler `contract-update` (P6-01b): HĐ `draft` giữ nguyên luồng cũ; HĐ `active` mà body có field khác hai field này → `409 CONTRACT_NOT_DRAFT`; HĐ `terminated` → `409 CONTRACT_NOT_DRAFT`. Event `contract.updated` như cũ.
- **Kiểm tra bước:** HĐ X `active`: `PATCH /api/v1/contracts/<X>` `{ "vehicleCount": 2 }` → `200 CONTRACT_UPDATED`, `SELECT vehicle_count` = 2; `{ "rentPrice": "4000000" }` → `409 CONTRACT_NOT_DRAFT`; HĐ `draft` sửa `rentPrice` vẫn `200` (không hồi quy). Nếu đã có P6-02g2: phòng có phí `per_vehicle` đang `blocked VEHICLE_COUNT_MISSING` → sau PATCH generate lại thì `generated`.

### Bước 7 — Transaction và outbox

- **Cách làm:** checkout thành công: `SELECT event_type FROM outbox_messages ORDER BY sequence DESC LIMIT 5` có `contract.terminated`, `room.status_changed`, `contract_member.left`. Tạm `throw` sau khi save room → `500`; HĐ vẫn `active`, member `left_at` NULL, phòng `occupied`, không có outbox mới. Xóa dòng throw.
- **Kiểm tra bước:** ghi query + kết quả vào PR.

## Ngoài phạm vi

- Quyết toán/hoàn cọc (`POST /contracts/{id}/deposit-settlement`) — Stretch (`P6-D61`).
- Hóa đơn quyết toán, prorate theo ngày trả, phí chấm dứt sớm (`P6-D62`, `P6-D64`).
- Chặn HĐ mới bắt đầu trong cùng kỳ với checkout — ngoài MVP (`P6-D62`), không kiểm tra ở đây.
- Lưu trữ kênh chat của HĐ cũ (community, Stretch) — chỉ cần event `contract.terminated` trong outbox.

## Blocker

- `completedOn` > `end_date` (HĐ quá hạn nhưng chưa checkout): `P6-D71` cho checkout tới hôm nay, nhưng rule `leftOn ≤ end_date` của leave-contract sẽ chặn `member.leave`. Task này áp rule `≤ end_date` ở handler leave-contract (P6-01e1), **không** ở domain `leave()`, để checkout vẫn set được `left_at = completedOn`. Confirmed by the D71 addendum: apply the end-date limit in leave-contract, not in the shared domain leave method.
- P6-02g1 (bảng `invoices`) chưa merge thì không làm được Bước 1, 3 — làm trước Bước 2, 4 với adapter trả `true` cố định trên branch, **không merge** khi chưa thay adapter thật.

## Cập nhật `api-docs` (bắt buộc trước khi đóng issue)

- [ ] `contracts-contractId.yaml` (PATCH): mô tả HĐ `active` chỉ sửa `vehicleCount`/`description` (`P6-D71`).
- [ ] Sequence diagram: Gateway → Tenancy → DB transaction (lock contract → đọc `invoices` → members `left_at` → contract → room → outbox) → Relay.
- [ ] `x-apidog-status: released`; sync Apidog.

## Acceptance (Apidog)

- [ ] HĐ `active` + hóa đơn kỳ `issued` → `200 CONTRACT_CHECKOUT_COMPLETED`, `status = terminated`; member còn ở có `leftAt = completedOn`; phòng `maintenance`.
- [ ] `mark-ready` sau checkout → phòng `available`.
- [ ] Kỳ chưa có hóa đơn / còn `pending` → `409 SETTLEMENT_NOT_READY`.
- [ ] HĐ `draft`/`terminated` → `409 CONTRACT_NOT_ACTIVE`.
- [ ] `completedOn` < `start_date`, > hôm nay, hoặc < `joinedAt` của một member → `422 VALIDATION_FAILED`, không đổi dữ liệu.
- [ ] HĐ `active`: `PATCH` `vehicleCount`/`description` → `200 CONTRACT_UPDATED`; field khác → `409 CONTRACT_NOT_DRAFT`.
- [ ] Landlord khác → `403 FORBIDDEN`; HĐ không tồn tại → `404`; token tenant → `403`; không token → `401`.

## Definition of Done

- [ ] Mọi bước qua phần Kiểm tra bước; mọi ô Acceptance được **tick bởi người làm**, kèm export Apidog hoặc ảnh chụp trong PR.
- [ ] `npm run build` + `npm run lint` pass; không có file test, không sửa `src/shared`; không import code của module `invoice`.
- [ ] Không có migration mới.
- [ ] PR vào `main` ghi `Closes pbl6-home-renter/docs#<số issue>`, ≥ 1 reviewer approve.
