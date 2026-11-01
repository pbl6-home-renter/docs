# P6-01e2 — Tenant xem hợp đồng của mình (`GET /me/contracts`)

**Epic:** [P6-01](P6-01-tenancy-contract-vertical-slice.md) · tách từ [P6-01e](P6-01e-contract-members-and-checkout.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** leminhkhai345  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 2 points · 4–6 giờ  
**Phụ thuộc:** P6-01e1 (bảng `contract_members`), P6-09 (`api-docs` bỏ `rentalType`)  
**Repo / branch:** `Tenancy-Service` · `feature/p6-01e2-me-contracts`  
**Iteration:** It6 (09/11–15/11)  
**Issue:** `docs#96`

> **Đọc trước khi code:** `AGENTS.md` và skill trong `.agents/skills/` của repo (backend: `be-feature-workflow`). Issue **không** quy định cách đặt file, đặt tên hay style — nếu issue nói khác skill thì làm theo skill. Nguồn mâu thuẫn xử lý theo [`P6-D75`](../decisions.md#d75--thứ-tự-ưu-tiên-nguồn-và-cách-xử-lý-câu-hỏi-mở): `decisions.md` > `api-docs` > skill > issue.

## Mục tiêu

Tenant gọi `GET /me/contracts` nhận danh sách HĐ mà mình đứng tên **hoặc** đang là member (`200 CONTRACTS_MY_FETCHED`), kèm tên phòng và tên tòa. Tenant thấy HĐ trong danh sách thì mở được chi tiết `GET /contracts/{id}`.

## Quyết định áp dụng

- `P6-D63` — `GET /me/contracts` trả HĐ mà user là `contracts.tenant_id` **hoặc** là `contract_members.tenant_id` chưa rời.
- `P6-D68` — không có `rentalType` trên Contract.
- `P6-D71` — "chưa rời" = `left_at IS NULL` hoặc `left_at > hôm nay` (cùng định nghĩa `status=active` của member, P6-01e1).
- `P6-D73` — participants của `contract` trong `GET /internal/ownership` (P6-11) dùng cùng tập người "đại diện + member chưa rời" → giữ một định nghĩa.
- `P6-D74` — web không liên kết tài khoản; `tenant_id` chỉ có từ seed demo. Endpoint vẫn làm cho mobile + dữ liệu seed.
- `P2-D44` — HĐ đã soft-delete (`is_deleted = true`) không trả.

## Contract

| Endpoint | operationId | Role | Thành công | Lỗi |
|---|---|---|---|---|
| `GET /me/contracts` | `getMeContracts` | tenant | `200 CONTRACTS_MY_FETCHED` + `pagination` offset | `403` (role khác), `422 VALIDATION_FAILED` |
| `GET /contracts/{contractId}` (sửa quyền) | `getContractsContractid` | landlord, tenant | `200 CONTRACT_FETCHED` | `403`, `404` |

- Path: `api-docs/src/paths/contracts/me-contracts.yaml`; response item `api-docs/src/responses/dtos/contracts/my-contract-list-response-dto.yaml` (**sau P6-09**: không có `rentalType`).
- Query: `filter[status]` (giá trị của `ContractStatus`), `filter[roomId]` (uuid), `pageNo`, `pageSize ≤ 100`; chỉ `format=json` (khác → `422`).
- Gateway đã route `/me/contracts` → Tenancy (`api-gateway/src/constants/route-paths.constants.ts`), không cần sửa gateway.

### Mapping field

| Response field | Nguồn | Ghi chú |
|---|---|---|
| `id`, `roomId`, `status`, `rentPrice`, `depositAmount`, `startDate`, `endDate` | `contracts` (§2.7) | tiền giữ đúng kiểu như `GET /contracts` hiện tại |
| `contractCode` | sinh `HD-<6 ký tự đầu id>` | dùng lại cách của `contract-list-item.response.dto.ts` (P6-01b), không thêm cột |
| `roomName` | `rooms.name` | join như `contract-read.repository.ts` |
| `buildingName` | `buildings.name` | join `rooms.building_id` |

### Điều kiện lọc (SQL tương đương)

```sql
SELECT c.*, r.name AS room_name, b.name AS building_name
FROM contracts c JOIN rooms r ON r.id = c.room_id JOIN buildings b ON b.id = r.building_id
WHERE c.is_deleted = false
  AND (c.tenant_id = :userId
       OR EXISTS (SELECT 1 FROM contract_members m
                  WHERE m.contract_id = c.id AND m.tenant_id = :userId
                    AND (m.left_at IS NULL OR m.left_at > current_date)
                    AND m.is_deleted = false))
ORDER BY c.start_date DESC, c.id;
```

## Tham chiếu code

- Read repository + join `rooms`: `Tenancy-Service/src/modules/contract/infrastructure/persistence/contract-read.repository.ts`, port `src/modules/contract/domain/repositories/contract-read.repository.ts`.
- List query + DTO phân trang: `src/modules/contract/application/queries/contract-list/`, `src/modules/contract/presentation/http/requests/list-contracts.query.request.dto.ts`.
- Route `/me/...` trong Tenancy: `src/modules/room/presentation/http/controllers/room.controller.ts` (`@Controller()` không prefix, path đầy đủ trên từng route).
- Quyền chi tiết: `src/modules/contract/application/queries/contract-get-by-id/contract-get-by-id.query.handler.ts`.
- Member chưa rời: `findActiveByContract` của member repository (P6-01e1, định nghĩa `P6-D71`).

## Các bước triển khai

### Bước 1 — Dữ liệu thử

- **Cách làm:** chạy service; gán `tenant_id` bằng SQL/seed (web không có ô chọn tài khoản, `P6-D74`); chuẩn bị tenant T1 là đại diện HĐ X (`active`), T1 là member chưa rời của HĐ Y (HĐ của người khác), T1 là member **đã rời** HĐ Z (`left_at` hôm qua), T1 là member HĐ V với `left_at` = ngày mai (vẫn chưa rời), tenant T2 không liên quan.
- **Kiểm tra bước:** `SELECT contract_id, tenant_id, left_at FROM contract_members WHERE tenant_id = :t1` ra Y (left_at NULL), Z (left_at quá khứ), V (left_at tương lai).

### Bước 2 — Query đọc HĐ của tenant

- **Cách làm:** thêm method đọc vào read repository (port + adapter) theo SQL ở trên, nhận `userId` + filter + phân trang; query handler gọi method này.
- **Kiểm tra bước:** chạy SQL trên với `:userId = T1` trong DB local → ra X, Y, V, không có Z; ghi kết quả vào PR.

### Bước 3 — Request/response DTO, route

- **Cách làm:** `GET /me/contracts`, `@Roles(UserRole.TENANT)`, response code `CONTRACTS_MY_FETCHED`, `operationId: getMeContracts`; item đúng bảng Mapping.
- **Kiểm tra bước:**
  - Token T1: `GET /api/v1/me/contracts` → `200`, `data` có 3 HĐ (X, Y, V), mỗi item có `roomName`, `buildingName`, `contractCode`, **không** có `rentalType`; `pagination.type = offset`.
  - `GET /api/v1/me/contracts?filter[status]=active&pageSize=1` → `200`, 1 item, `hasNextPage` đúng.
  - `filter[status]=abc` → `422 VALIDATION_FAILED`; `format=pdf` → `422`.
  - Token T2 → `200`, `data = []`; token landlord → `403`.

### Bước 4 — Cho member xem chi tiết HĐ

- **File sửa:** `contract-get-by-id.query.handler.ts`.
- **Cách làm:** điều kiện tenant đọc được = `contract.tenantId === user.id` **hoặc** user là member chưa rời của HĐ (cùng định nghĩa `P6-D63` với danh sách) — để không có HĐ hiện trong `/me/contracts` mà mở chi tiết bị `403`.
- **Kiểm tra bước:** T1 `GET /api/v1/contracts/<Y>` → `200 CONTRACT_FETCHED`; T1 `GET /api/v1/contracts/<Z>` → `403`; T2 → `403`.

### Bước 5 — Hoàn thiện

- **Kiểm tra bước:** Swagger có `getMeContracts`; `npm run build` + `npm run lint` pass.

## Ngoài phạm vi

- Tenant tự liên kết HĐ theo SĐT (scan danh sách member) — Stretch (`P6-D63`, `P6-D74`).
- "Phòng của tôi" hub (`/me/room-hub`), hóa đơn của tenant (`/me/invoices` — P6-02g).
- Xuất `xlsx/csv/pdf`.

## Blocker

- Không có.

## Cập nhật `api-docs` (bắt buộc trước khi đóng issue)

- [ ] Sequence diagram `getMeContracts` (Gateway → Tenancy → DB: contracts ⋈ rooms ⋈ buildings, EXISTS contract_members).
- [ ] Mô tả `getContractsContractid`: tenant đọc được khi là đại diện hoặc member chưa rời.
- [ ] `x-apidog-status: released`; sync Apidog.

## Acceptance (Apidog)

- [ ] Tenant đại diện → thấy HĐ của mình; tenant là member chưa rời → thấy HĐ đó; member có `left_at` tương lai vẫn thấy; member đã rời → không thấy.
- [ ] `filter[status]`, `filter[roomId]`, phân trang hoạt động; filter sai → `422 VALIDATION_FAILED`.
- [ ] Token landlord → `403 FORBIDDEN`; không token → `401`.
- [ ] Member chưa rời `GET /contracts/{id}` → `200`; member đã rời / người ngoài → `403`.

## Definition of Done

- [ ] Mọi bước qua phần Kiểm tra bước; mọi ô Acceptance được **tick bởi người làm**, kèm export Apidog hoặc ảnh chụp trong PR.
- [ ] `npm run build` + `npm run lint` pass; không có file test, không sửa `src/shared`.
- [ ] Không có migration mới (nếu cần index thì dùng index `tenant_id` đã tạo ở P6-01e1).
- [ ] PR vào `main` ghi `Closes pbl6-home-renter/docs#<số issue>`, ≥ 1 reviewer approve.
