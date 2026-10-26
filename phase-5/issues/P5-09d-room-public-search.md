# P5-09d — Tìm kiếm và xem chi tiết Room

**Epic:** [P5-09](P5-09-tenancy-room-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** huynhtiennhat0403  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 3 points · 6–8 giờ  
**Phụ thuộc:** P5-09b, P5-08e  
**Repo / branch:** `Tenancy-Service` · `feature/p5-09d-room-public-search`

## Mục tiêu

Tenant/khách (không cần token) tìm phòng trên sàn công khai qua `GET /api/v1/rooms`, và các role xem chi tiết một phòng qua `GET /api/v1/rooms/{roomId}`. Chỉ đọc — không ghi outbox.

## Contract

| Endpoint | operationId | File | Success |
|---|---|---|---|
| `GET /rooms` | `getRooms` | `api-doc/src/paths/rooms/rooms.yaml` (`get`) | `200 ROOMS_FETCHED` + `pagination` |
| `GET /rooms/{roomId}` | `getRoomsRoomid` | `api-doc/src/paths/rooms/rooms-roomId.yaml` (`get`) | `200 ROOM_FETCHED` |

- `GET /rooms`: `security: []` (public). Filter `filter[province]`, `filter[ward]`, `filter[minPrice]`, `filter[maxPrice]` (int ≥ 0), `filter[genderPolicy]` (`any|male|female`); `sort` mặc định `rentPrice`, `order` mặc định `asc`; `pageSize` 1–100 (mặc định 20), `pageNo`.
- Response list: `api-doc/src/responses/dtos/rooms/public-room-list-response-dto.yaml` (required `id, buildingId, name, area, rentPrice, genderPolicy, address, district, province, isFavorited`) — **không** có `status`.
- Response detail: `room-detail-response-dto.yaml` (có `landlord`, `photoUrls`, `currentContract`, `currentMembers`, `latestMeterReadings`, `effectiveRatePolicySummary`).
- Lỗi: `404 RESOURCE_NOT_FOUND`, `403 FORBIDDEN`, `422 VALIDATION_FAILED`.

## Tham chiếu code (đã có trong repo)

| Cần | Copy pattern từ |
|---|---|
| Public endpoint | `@Public()` trong `src/shared/presentation/decorators/auth/access-control.decorators.ts` (xem `getById` trong `sample.controller.ts`) |
| Query handler | `src/modules/sample/application/queries/sample-get-by-id/` |
| Offset pagination | `OffsetPaginationQueryRequestDto`, `PaginatedResponseDto`, `TypeOrmOffsetPaginator`, `applySortingToQueryBuilder` (`src/shared/.../pagination/`) — cùng cách dùng ở P5-09c Bước 3 |
| Public search Building (join + filter province/ward) | query của P5-08e (`GET /buildings`) |
| Typeorm entity để join | `RoomTypeormEntity`, `BuildingTypeormEntity` |

## Các bước triển khai

### Bước 1 — Pull P5-09b + P5-08e, chuẩn bị dữ liệu

- **Cách làm:** `npm run migration:run && npm run start:dev`; tạo dữ liệu: Building A `approved` (2 phòng `available`, 1 phòng `maintenance`), Building B `pending` (1 phòng), 1 phòng đã xóa mềm.
- **Kiểm tra bước:** SQL đếm đúng 2 phòng thỏa điều kiện public (available + building approved + chưa xóa).

### Bước 2 — Read model và repository query

- **File tạo:** `src/modules/room/application/queries/read-models/public-room.read-model.ts` (interface: `id, buildingId, name, area, rentPrice, genderPolicy, address, province, ward`).
- **File sửa:** `src/modules/room/domain/repositories/room.repository.ts` → **không** thêm vào domain repo; tạo port riêng `src/modules/room/application/ports/room-read.repository.ts` với `searchPublic(query: OffsetPageQuery<PublicRoomFilter>): Promise<PaginatedResult<PublicRoomReadModel>>` và `findDetailById(id: Uuid)`; implement ở `src/modules/room/infrastructure/persistence/room-read.repository.ts`, đăng ký token `ROOM_DI_TOKEN.READ_REPOSITORY` trong `room.di-token.ts`.
- **Cách làm (`searchPublic`):** QueryBuilder `rooms r INNER JOIN buildings b ON b.id = r.building_id` với điều kiện cố định `r.is_deleted = false AND b.is_deleted = false AND b.status = 'approved' AND r.status = 'available'`; filter `b.province`, `b.ward`, `r.rent_price BETWEEN`, `r.gender_policy`; whitelist sort `rentPrice`, `createdAt`, `area`; phân trang bằng `TypeOrmOffsetPaginator`.
- **Kiểm tra bước:** viết tạm script hoặc gọi qua Bước 4 ⇒ chỉ ra 2 phòng của Building A.

### Bước 3 — Query `GET /rooms`

- **File tạo:**
  - `application/queries/room-public-search/room-public-search.query.ts` + `.query.handler.ts`.
  - `presentation/http/requests/public-rooms-query.request.ts` (extends `OffsetPaginationQueryRequestDto`; validate `minPrice <= maxPrice` ⇒ `422`).
  - `presentation/http/responses/room-public-list.response.dto.ts` theo `public-room-list-response-dto.yaml` (sau khi bỏ `district`); `area` trả dạng string; `isFavorited = false` (`TODO(favorite)`).
  - `constants/room-response-code.constant.ts` thêm `ROOMS_FETCHED`, `ROOM_FETCHED`.
- **File sửa:** `room.controller.ts`: `@Get() @Public() @ResponseCode('ROOMS_FETCHED')`, `operationId: 'getRooms'`.
- **Kiểm tra bước:** gọi không token ⇒ `200`, 2 phòng; `filter[genderPolicy]=other` ⇒ `422`; response không có `status`, không có `district`.

### Bước 4 — Query `GET /rooms/{roomId}` theo quyền

- **File tạo:** `application/queries/room-get-detail/` (query nhận `roomId` + `viewer?: AuthenticatedUser`), `responses/room-detail.response.dto.ts`.
- **Cách làm (rule quyền):**
  - Room không tồn tại/đã xóa ⇒ `404`.
  - Không token hoặc tenant: chỉ xem được nếu Building `approved` **và** Room không bị xóa; nếu Building chưa approved ⇒ `404` (không lộ sự tồn tại).
  - Landlord chủ phòng và admin: xem được mọi trạng thái.
  - Landlord khác với Room chưa public ⇒ `404`; Room public ⇒ `200` như khách.
  - Controller dùng `@Public()` nhưng vẫn đọc user nếu có token: kiểm tra `JwtAuthGuard` có gắn `request.user` khi route public và token hợp lệ không; nếu không, hỏi BE Lead trước khi sửa guard (không tự sửa `shared/`).
- **Field phụ thuộc module khác:** `landlord` (name/phone nằm ở identity) — dùng `InternalHttpClient` (`src/shared/infrastructure/http/internal-http-client.service.ts`, đã có cho Identity) nếu Identity đã có endpoint internal lookup user; nếu chưa thì trả `null` và ghi blocker. `photoUrls = []`, `currentContract = null`, `currentMembers = []`, `latestMeterReadings = null`, `effectiveRatePolicySummary = null` kèm `TODO(module)` tương ứng.
- **Kiểm tra bước:** đủ 4 case quyền ở trên trả đúng mã.

### Bước 5 — Hoàn thiện module, Swagger

- **File sửa:** `room.module.ts` đăng ký 2 query handler + read repository provider.
- **Kiểm tra bước:** `npm run build` + `npm run lint` pass; Swagger hiện `getRooms`, `getRoomsRoomid` không có khóa auth.

## Quyết định tạm thời / Ngoài phạm vi

- **`district`:** lỗi contract đã chốt bỏ (VN bỏ cấp Quận/Huyện) — không trả, xóa khỏi `api-doc`.
- **`isFavorited`:** module favorite chưa có ⇒ `false`.
- **Field Media/Contract/Billing trong detail:** trả giá trị rỗng/`null` theo contract (`nullable`), ghi `TODO`; **không** tự định nghĩa field mới.
- **`format=xlsx|csv|pdf`:** chỉ hỗ trợ `json`; giá trị khác ⇒ `422` và ghi blocker cho API owner.
- Không ghi outbox (chỉ đọc).

## Cập nhật `api-doc` (bắt buộc trước khi đóng issue)

- [ ] **Xóa `district`**: `src/responses/dtos/rooms/public-room-list-response-dto.yaml` (property + `required`) và example trong `src/paths/rooms/rooms.yaml`.
- [ ] Sequence diagram cho `getRooms` (Gateway → Tenancy → DB join buildings) và `getRoomsRoomid` (rule quyền + gọi Identity nếu có) khớp implementation. Tham khảo `src/paths/auth/register.yaml`.
- [ ] `x-apidog-status: designing` → `released`; sync Apidog; link PR `api-doc` vào issue.

## Manual verification (Apidog)

1. `GET /rooms` không token → chỉ Room `available` của Building `approved`, chưa xóa; không có `status`/`district`.
2. Filter `province`, `minPrice`/`maxPrice`, `genderPolicy` và pagination đúng; `minPrice > maxPrice` → `422`.
3. `GET /rooms/{id}` phòng public không token → `200`; phòng thuộc Building `pending` → `404` với khách, `200` với chủ phòng và admin.
4. `roomId` không tồn tại → `404`; `roomId` sai định dạng → `422`/`400` theo contract.

## Definition of Done

- [ ] Bước 1–5 đã qua phần Kiểm tra bước.
- [ ] `npm run build` + `npm run lint` pass.
- [ ] PR vào `main` ghi `Closes pbl6-home-renter/docs#59` + link file `api-doc` đã dùng.
- [ ] baoduong17 approve; PR `api-doc` merge cùng lúc.
