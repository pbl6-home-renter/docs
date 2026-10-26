# P5-08e — Tìm kiếm và xem Building public

**Epic:** [P5-08](P5-08-tenancy-building-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** leminhkhai345  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 3 points · 6–8 giờ  
**Phụ thuộc:** P5-08d  
**Repo / branch:** `Tenancy-Service` · `feature/p5-08e-building-public-search`

## Mục tiêu

Khách (không cần đăng nhập) và tenant tìm kiếm Building đã duyệt theo tỉnh/phường/từ khóa và xem chi tiết. Building `pending`/`rejected`/đã xóa không bao giờ lộ ra ở endpoint public.

## Contract

| Endpoint | operationId | File `api-doc` | Success |
|---|---|---|---|
| `GET /buildings` | `getBuildings` | `src/paths/buildings/buildings.yaml` (`get`) | `200 BUILDINGS_FETCHED` + `pagination` |
| `GET /buildings/{buildingId}` | `getBuildingsBuildingid` | `src/paths/buildings/buildings-buildingId.yaml` (`get`) | `200 BUILDING_FETCHED` |

- `security: []` ⇒ public, không cần token.
- List: `filter[province|ward|q]`, `sort` (mặc định `createdAt`), `order` (mặc định `desc`), `pageNo`, `pageSize` (1–100).
- DTO: `src/responses/dtos/buildings/public-building-list-response-dto.yaml` (`id, name, province, ward, address`), `public-building-detail-response-dto.yaml` (thêm `status` chỉ có giá trị `approved`).
- Lỗi: `404 RESOURCE_NOT_FOUND`, `422 VALIDATION_FAILED`, `400` path không phải UUID.

## Tham chiếu code (đã có trong repo)

| Cần | Copy pattern từ |
|---|---|
| Route public | decorator `@Public()` trong `src/shared/presentation/decorators/auth/access-control.decorators.ts` (ví dụ dùng: `sample.controller.ts` `getById`) |
| Query service + filter/sort/pagination | `BuildingQueryService` (P5-08c/P5-08d) → thêm method mới; mẫu filter: `Identity-Service/src/modules/users/infrastructure/services/user-query.service.ts` |
| Query request DTO list | `building-list-admin.query.request.dto.ts` (P5-08d) |
| Controller `buildings` | `src/modules/building/presentation/http/controllers/building.controller.ts` (P5-08b) |
| Index sẵn có | `IDX_buildings_status` (`status`, partial `is_deleted = false`) trong migration `1792981146173-CreateBuildingsTable.ts` |

## Các bước triển khai

### Bước 1 — Pull code và chuẩn bị dữ liệu

- **Cách làm:**
  - Pull `main` (đã có P5-08d), tạo branch `feature/p5-08e-building-public-search`.
  - Tạo 4 Building: 2 `approved` (2 tỉnh khác nhau), 1 `pending`, 1 `rejected` (approve/reject bằng API admin của P5-08d); xóa mềm 1 Building `approved` khác.
- **Kiểm tra bước:** `SELECT status, is_deleted, count(*) FROM buildings GROUP BY 1,2;` khớp dữ liệu vừa tạo.

### Bước 2 — Query service public

- **File tạo:** `src/modules/building/application/queries/models/public-building-filter.model.ts`: `{ province?, ward?, q? }`.
- **File sửa:** `IBuildingQueryService` + `BuildingQueryService`: thêm
  - `findPublicBuildings(q)`: `where building.isDeleted = false AND building.status = 'approved'`; `province`/`ward` so khớp chính xác; `q` = `LOWER(building.name) LIKE :q OR LOWER(building.address) LIKE :q`; `withSort({ whitelist: ['createdAt', 'name'], defaultSort: 'createdAt', defaultOrder: 'desc', alias: 'building' })`.
  - `findPublicBuildingById(id)`: cùng điều kiện `approved` + chưa xóa, trả `null` nếu không thỏa.
- **Cách làm:** điều kiện `status = approved` nằm **trong query**, không lọc sau khi lấy ra (tránh sai `totalItems`).
- **Kiểm tra bước:** `npm run build` pass.

### Bước 3 — Query handler, request/response DTO

- **File tạo:**
  - `src/modules/building/application/queries/building-search-public/` và `building-get-public/` (query + handler); detail `null` → `BuildingNotFoundException`.
  - `src/modules/building/presentation/http/requests/building-search-public.query.request.dto.ts` (`extends OffsetPaginationQueryRequestDto<PublicBuildingFilter>`, `@IsOptional() @IsString() @MaxLength(100)` cho từng filter).
  - `src/modules/building/presentation/http/responses/public-building-list.response.dto.ts`, `public-building-detail.response.dto.ts` — **chỉ** các field trong schema (không trả `landlordId`, `note`, lat/long).
- **Kiểm tra bước:** `npm run build` pass.

### Bước 4 — Thêm route vào controller `buildings`

- **File sửa:** `building.controller.ts`:
  - `@Get() @Public()` `operationId: 'getBuildings'`, `@ResponseCode(BUILDINGS_FETCHED)` → `PaginatedResponseDto.create(...)`.
  - `@Get(':buildingId') @Public()` `operationId: 'getBuildingsBuildingid'`, `@ResponseCode(BUILDING_FETCHED)`.
  - Đặt 2 route GET này **trước** các route có segment cố định khác nếu bị trùng pattern (kiểm tra `POST :buildingId/approve` vẫn hoạt động).
- **File sửa:** `building-response-code.constant.ts` thêm `BUILDINGS_FETCHED`, `BUILDING_FETCHED`; `building.module.ts` đăng ký 2 query handler.
- **Kiểm tra bước:** gọi không token → `200`; Swagger không có ổ khóa ở 2 route này.

### Bước 5 — Kiểm tra qua Gateway

- **Cách làm:** chạy `api-gateway` local, gọi `GET http://localhost:<gateway>/api/v1/buildings` không token. Nếu gateway chặn `401` thì báo baoduong17 để mở route public trong gateway (không tự sửa gateway trong PR này).
- **Kiểm tra bước:** qua gateway trả cùng kết quả như gọi thẳng Tenancy, hoặc đã ghi blocker vào issue.

### Bước 6 — Build, lint

- **Kiểm tra bước:** `npm run build` + `npm run lint` pass.

## Quyết định tạm thời / Ngoài phạm vi

- **`format` (xlsx/csv/pdf):** chỉ làm `json`; ghi blocker cho API owner (đề xuất bỏ `format` khỏi endpoint public).
- **`429 RATE_LIMIT_EXCEEDED`:** service chưa có rate limiter; không làm trong task này (nếu cần sẽ làm ở gateway).
- **Không trả số phòng trống / giá** trong Building public — tìm phòng theo bản đồ thuộc P5-09d (`GET /rooms`).
- Không thêm `district` (đã chốt bỏ).

## Cập nhật `api-doc` (bắt buộc trước khi đóng issue)

- [ ] Kiểm tra không còn `district` trong 2 DTO public và example.
- [ ] Sequence diagram cho `getBuildings` và `getBuildingsBuildingid` (Gateway → Tenancy → DB, không auth). Tham khảo `src/paths/auth/register.yaml`.
- [ ] `x-apidog-status: designing` → `released`; sync Apidog; link PR `api-doc` vào issue.

## Manual verification (Apidog)

1. Không token, `GET /buildings` → chỉ 2 Building `approved` chưa xóa; `totalItems = 2`.
2. `filter[province]=<tỉnh A>` → 1 kết quả; `filter[q]=<một phần tên>` → khớp không phân biệt hoa thường.
3. `sort=name&order=asc` đúng thứ tự; `sort=landlordId` → `422 VALIDATION_FAILED`; `pageSize=101` → `422`.
4. `GET /buildings/{id pending|rejected|đã xóa}` → `404 RESOURCE_NOT_FOUND`; `GET /buildings/abc` → `400`.
5. Response không chứa `landlordId`, `note`, `latitude`, `longitude`.

## Definition of Done

- [ ] Bước 1–6 đã qua phần Kiểm tra bước.
- [ ] `npm run build` + `npm run lint` pass.
- [ ] PR vào `main` ghi `Closes pbl6-home-renter/docs#55` + link các file `api-doc` đã dùng.
- [ ] baoduong17 approve; PR `api-doc` merge cùng lúc.
