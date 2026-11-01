# P6-11 — Tenancy: `GET /internal/ownership/{ownerType}/{ownerId}` cho Media

**Liên quan:** [P6-04](P6-04-identity-media-presign-upload.md) (Identity media — phía gọi). Không thuộc epic.  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** baoduong17  
**Người review:** leminhkhai345 (BE)  
**Ước lượng:** 2 points · 5–7 giờ  
**Phụ thuộc:** — (phần `contract_member` cần P6-01e1; phần `meter_reading` cần migration `meter_readings` của P6-02h — xem Bước 5)  
**Repo / branch:** `Tenancy-Service` · `feature/p6-11-internal-ownership`  
**Iteration:** It5 prerequisite  
**Issue:** `docs#110`

> **Đọc trước khi code:** `AGENTS.md` và skill trong `.agents/skills/` của repo (backend: `be-feature-workflow`). Issue **không** quy định cách đặt file, đặt tên hay style — nếu issue nói khác skill thì làm theo skill. Nguồn mâu thuẫn xử lý theo [`P6-D75`](../decisions.md#d75--thứ-tự-ưu-tiên-nguồn-và-cách-xử-lý-câu-hỏi-mở): `decisions.md` > `api-docs` > skill > issue.

## Mục tiêu

Identity hỏi được Tenancy "entity này của landlord nào, ai tham gia, trạng thái gì" để cấp quyền upload/đọc/xóa media. Xong task: landlord tạo Building rồi upload `ownership_proof` qua `POST /media/presign-upload` thành công (hiện tại trả `403` vì Tenancy chưa có endpoint → Identity coi owner là không tồn tại).

## Quyết định áp dụng

- `P6-D69` — tạo entity trước, upload sau với `ownerId` thật; Tenancy thêm `GET /internal/ownership/{ownerType}/{ownerId}` (`@InternalOnly()`), trả `{ landlordId, participantUserIds, status }` cho `building`, `room`, `contract`, `contract_member`, `meter_reading`; không tìm thấy → `404`.
- `P6-D73` — bảng `landlordId`/`participantUserIds`/`status` theo từng `ownerType` (dùng nguyên văn ở mục Mapping); `GET /internal/media/{id}` thuộc Identity, giao ở **P6-12**.
- `P6-D63` / `P6-D71` — người tham gia HĐ = `contracts.tenant_id` + `contract_members.tenant_id` chưa rời (`left_at IS NULL` hoặc `left_at > hôm nay`), bỏ `NULL`.
- `P6-D70` — migration `meter_readings` sinh ở P6-02h.
- `P6-D66` — ảnh minh chứng chỉ số: `owner_type = meter_reading`, `owner_id = <readingId>`.

## Contract (internal — không nằm trong `api-docs` public, theo P6-09)

- `GET /internal/ownership/{ownerType}/{ownerId}` — ngoài prefix `api/v1` (`src/main.ts` exclude `internal/(.*)`), gateway không route tới.
- Auth: header `X-Service-Token` = `SERVICE_TOKEN` (`ServiceTokenGuard`); sai/thiếu → `401`.
- Thành công `200`, envelope chuẩn `{ statusCode, code: "OWNERSHIP_FETCHED", data }`. Identity đọc `response.data.data` (`Identity-Service/src/shared/infrastructure/http/internal-http-client.service.ts`).
- `data` **phải khớp đúng** interface `TenancyOwnership` trong `Identity-Service/src/modules/media/infrastructure/owners/tenancy-owner.resolver.ts`:

  ```ts
  { landlordId: Uuid | null; participantUserIds: Uuid[]; status: string | null }
  ```
- Không có / `is_deleted = true` / `ownerType` ngoài 5 giá trị → `404` (Identity map `404` → `null` → `403 FORBIDDEN` cho client). `ownerId` không phải UUID → `422 VALIDATION_FAILED`.

### Mapping theo `ownerType` (`P6-D73`)

| `ownerType` | Bảng | `landlordId` | `participantUserIds` | `status` | Identity dùng `status` cho |
|---|---|---|---|---|---|
| `building` | `buildings` | `landlord_id` | `[]` | trạng thái duyệt `buildings.status` (`pending/approved/rejected`) | `ownership_proof` khóa xóa khi `approved` |
| `room` | `rooms` | `landlord_id` của tòa | `[]` | `rooms.status` | — (ảnh phòng: chỉ landlord upload, ai cũng đọc) |
| `contract` | `contracts` | `landlord_id` | `tenant_id` (nếu có) ∪ member chưa rời có `tenant_id` | `contracts.status` | `contract_signed` khóa xóa khi `signed/active/suspended/expired/terminated` |
| `contract_member` | `contract_members` ⋈ `contracts` | như dòng `contract` của HĐ chứa member | như dòng `contract` | `contracts.status` | — |
| `meter_reading` | `meter_readings` ⋈ HĐ `active` của `room_id` | `meter_readings.landlord_id` | người tham gia HĐ `active` của phòng (như dòng `contract`; không có HĐ `active` → `[]`) — để tenant tự chụp sau này | `null` | — |

- Code Identity dùng các field này ở: `Identity-Service/src/modules/media/domain/policies/media-purpose.policies.ts` (`lockedOwnerStatuses`, `isOwnerLandlord`, `isParticipant`), `.../domain/value-objects/owner-snapshot.ts`.
- `participantUserIds` không trùng lặp, không có `null`.

## Tham chiếu code

- Controller internal mẫu: `Identity-Service/src/modules/users/presentation/http/controllers/user-internal.controller.ts` (`@ApiExcludeController()`, `@InternalOnly()`, `@Controller('internal/...')`, `@ResponseCode`).
- Decorator: `Tenancy-Service/src/shared/presentation/decorators/auth/internal-only.decorator.ts`; guard `src/shared/presentation/guards/service-token.guard.ts`.
- Đọc nhiều bảng không qua aggregate: read repository kiểu `src/modules/contract/infrastructure/persistence/contract-read.repository.ts`; module mẫu `src/modules/rate-policy/`.
- Bảng: `src/modules/building/infrastructure/persistence/`, `src/modules/room/infrastructure/persistence/room.typeorm-entity.ts`, `src/modules/contract/infrastructure/persistence/contract.typeorm-entity.ts`, `src/modules/meter-reading/infrastructure/persistence/meter-reading.typeorm-entity.ts`.

## Các bước triển khai

### Bước 1 — Tái hiện lỗi hiện tại

- **Cách làm:** chạy Identity (3001) + Tenancy (3002) local, cùng `SERVICE_TOKEN`; Identity `TENANCY_SERVICE_URL=http://localhost:3002`. Landlord A tạo building (`POST /api/v1/buildings`, body như P5-08b).
- **Kiểm tra bước:** `POST http://localhost:3001/api/v1/media/presign-upload` `{ "ownerType": "building", "ownerId": "<buildingId>", "purpose": "ownership_proof", "fileName": "so-do.pdf", "contentType": "application/pdf", "size": 120000 }` → `403 FORBIDDEN`; log Tenancy có `GET /internal/ownership/building/<id> 404`.

### Bước 2 — Read port + query cho `building`, `room`, `contract`

- **Cách làm:** một read port `findOwnership(ownerType, ownerId): Promise<Ownership | null>`; adapter SQL theo bảng Mapping, lọc `is_deleted = false`. Phần member của `contract` chỉ bật khi bảng `contract_members` đã có (P6-01e1); trước đó participants = `[tenant_id]`.
- **Kiểm tra bước:** SQL tương đương chạy tay trên DB local cho 1 building, 1 room, 1 HĐ có `tenant_id` → kết quả khớp bảng Mapping; ghi vào PR.

### Bước 3 — Controller internal

- **Cách làm:** `GET internal/ownership/:ownerType/:ownerId`, `@InternalOnly()`, ẩn khỏi Swagger, response code `OWNERSHIP_FETCHED`; `ownerType` ngoài 5 giá trị → `404`.
- **Kiểm tra bước:**
  - `curl -H "X-Service-Token: $SERVICE_TOKEN" http://localhost:3002/internal/ownership/building/<id>` → `200`, `data = { "landlordId": "<A>", "participantUserIds": [], "status": "pending" }`.
  - Không header → `401`; UUID ngẫu nhiên → `404`; `/internal/ownership/user/<id>` → `404`; `ownerId=abc` → `422`.
  - `curl http://localhost:3000/internal/ownership/building/<id>` qua gateway → không tới Tenancy (`404` của gateway).
  - HĐ có tenant T: `/internal/ownership/contract/<id>` → `participantUserIds = ["<T>"]`, `status = "draft"`.

### Bước 4 — End-to-end với Identity

- **Kiểm tra bước:** lặp lại request Bước 1 → `201 MEDIA_UPLOAD_TICKET_ISSUED`; PUT file lên `uploadUrl`; `POST /api/v1/media/<mediaId>/complete-upload` → `200 MEDIA_UPLOAD_COMPLETED`. Landlord B presign cùng building → `403`. Admin duyệt building (`POST /api/v1/buildings/<id>/approve`) → landlord A `DELETE /api/v1/media/<mediaId>` → `409 CANNOT_DELETE`.

### Bước 5 — `contract_member` và `meter_reading` (có điều kiện)

- **Cách làm:**
  - `contract_member`: làm khi P6-01e1 đã merge (cần bảng `contract_members`).
  - `meter_reading`: entity `meter_readings` đã có trên `main` (`6251329`) nhưng **chưa có migration** → làm khi migration của [P6-02h](P6-02h-meter-reading-ocr-preview.md) (`P6-D70`) đã merge. Nếu chưa merge khi đóng task này: trả `404` cho `meter_reading`, mở follow-up `P6-11a` và ghi link vào issue.
- **Kiểm tra bước:** `/internal/ownership/contract_member/<id>` → giống hệt `/internal/ownership/contract/<contractId của member>` (`landlordId`, participants, `status` của HĐ); `/internal/ownership/meter_reading/<id>` → `landlordId` = landlord của reading, participants = người tham gia HĐ `active` của phòng; presign `meter_reading_evidence` cho reading đó bằng token landlord → `201`.

## Ngoài phạm vi

- `issue_report`, `message` (community-service, Stretch) — Identity đã route sang `UnavailableOwnerResolver`.
- Endpoint tra cứu media phía Identity (`GET /internal/media/{id}`) mà P6-01d cần — **P6-12** (`P6-D73`).
- Cache kết quả ownership; thêm field vào response ngoài 3 field trên.

## Blocker

- Không có. (Mapping theo owner type đã chốt ở `P6-D73`.) Phụ thuộc còn lại: migration `meter_readings` của P6-02h (xem Bước 5).

## Acceptance

- [ ] Đúng `X-Service-Token` → `200 OWNERSHIP_FETCHED`, `data` đúng 3 field `landlordId`, `participantUserIds`, `status` cho `building`, `room`, `contract`.
- [ ] Thiếu/sai token → `401`; không tồn tại / đã xóa / `ownerType` lạ → `404`; `ownerId` sai định dạng → `422 VALIDATION_FAILED`.
- [ ] Gateway không route được tới `/internal/...`.
- [ ] **E2E:** landlord tạo Building → presign `ownership_proof` (`ownerType=building`, `ownerId` thật) → `201 MEDIA_UPLOAD_TICKET_ISSUED` → PUT → complete → `200 MEDIA_UPLOAD_COMPLETED`; landlord khác → `403 FORBIDDEN`.
- [ ] Building `approved` → xóa `ownership_proof` → `409 CANNOT_DELETE`.
- [ ] `contract_member` (sau P6-01e1) và `meter_reading` (sau migration) trả đúng bảng Mapping, hoặc đã mở follow-up P6-11a.

## Definition of Done

- [ ] Mọi bước qua phần Kiểm tra bước; mọi ô Acceptance được **tick bởi người làm**, kèm log/ảnh chụp trong PR.
- [ ] `npm run build` + `npm run lint` pass; không có file test, không sửa `src/shared`; không có migration mới.
- [ ] PR vào `main` ghi `Closes pbl6-home-renter/docs#<số issue>`, ≥ 1 reviewer approve.
