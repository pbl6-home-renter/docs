# P6-03a — Building API layer, danh sách và chi tiết Building của tôi

**Epic:** [P6-03](P6-03-fe-landlord-building-room-screens.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** ThaiBao11125  
**Người review:** baoduong17  
**Ước lượng:** 5 points · 10–14 giờ  
**Phụ thuộc:** `fe#6` merged; BE P5-08c (`GET /me/buildings`, `GET /me/buildings/{id}`) chạy trên staging  
**Repo / branch:** `fe` · `feature/p6-03a-building-list-detail`  
**Issue:** `docs#80`

## Mục tiêu

Landlord vào `/buildings` thấy danh sách Tòa nhà của mình (phân trang, lọc theo trạng thái), bấm vào một Tòa nhà để mở `/buildings/:id` xem chi tiết và trạng thái duyệt (Chờ duyệt / Đã duyệt / Bị từ chối kèm lý do). Task này cũng dựng feature `buildings` mà P6-03b/c/d sẽ dùng lại.

## Contract

- `api-doc/src/paths/buildings/me-buildings.yaml` → `getMeBuildings`: query `filter[...]`, `sort`, `order`, `pageNo`, `pageSize`; `200 BUILDINGS_MY_FETCHED`, item `BuildingMyListResponseDto`.
- `api-doc/src/paths/buildings/me-buildings-buildingId.yaml` → `getMeBuildingsBuildingid`: `200 BUILDING_MY_FETCHED`, `BuildingMyDetailResponseDto`; lỗi `403`, `404`.
- Schema: `BuildingMyListResponseDto`, `BuildingMyDetailResponseDto` trong `api-doc/src/openapi.yaml` (lần theo `$ref` tới file trong `src/responses/dtos/`).
- Role: `landlord`. Status enum: `pending | approved | rejected`.

## Tham chiếu code

| Cần | Copy pattern từ |
|---|---|
| API module | `src/features/auth/api/auth.api.ts` |
| Query hook | `src/features/auth/hooks/auth/use-current-user-query.ts` |
| Query key | `queryKeys` trong `src/lib/react-query.ts` |
| Kiểu phân trang | `OffsetPaginationMeta`, `OffsetPaginationParams` trong `src/types/api.ts` |
| Trạng thái rỗng/lỗi/loading | `src/components/feedback/empty-state.tsx`, `error-state.tsx`, `skeleton.tsx` |
| Badge trạng thái | `src/components/ui/badge.tsx` |

## Các bước triển khai

### Bước 1 — Chạy FE với API staging

- **Cách làm:**
  - Pull `main` (đã có `fe#6`), tạo branch `feature/p6-03a-building-list-detail`.
  - Đặt base URL trong `.env` trỏ tới gateway staging, đăng nhập bằng tài khoản landlord test.
  - Dùng Apidog gọi `GET /me/buildings` bằng token đó và lưu response mẫu vào comment của issue.
- **Kiểm tra bước:** `npm run dev` chạy được, login landlord vào `/dashboard`; Apidog trả `200 BUILDINGS_MY_FETCHED`.

### Bước 2 — Types và enum Building

- **File tạo:**
  - `src/features/buildings/types/building.dto.ts`: `BuildingMyListItemDto`, `BuildingMyDetailDto`, `BuildingListFilter` (`status?`, `q?` nếu contract có), field y hệt schema contract (camelCase).
  - `src/features/buildings/enums/building-status.enum.ts`: `BuildingStatus = { PENDING: 'pending', APPROVED: 'approved', REJECTED: 'rejected' } as const`.
- **Kiểm tra bước:** `npm run build` pass; so từng field với schema contract, ghi vào PR các field đã map.

### Bước 3 — API module

- **File tạo:** `src/features/buildings/api/building.api.ts`
  - `getMyBuildings(params: OffsetPaginationParams & { filter?: BuildingListFilter; sort?; order? })` → `apiClient.get('/me/buildings', { params })`, trả `{ data: BuildingMyListItemDto[]; pagination: OffsetPaginationMeta }`.
  - `getMyBuilding(id: string)` → `apiClient.get('/me/buildings/' + id)`.
  - Query `filter` dạng deepObject: truyền `params: { 'filter[status]': status }` (kiểm tra lại với contract `style: deepObject`).
- **Kiểm tra bước:** gọi tạm trong console dev → nhận đúng `{ data, pagination }`.

### Bước 4 — Query key và hooks

- **File sửa:** `src/lib/react-query.ts`: thêm `buildings: { all: ['buildings'], myList: (p) => ['buildings', 'my', p], myDetail: (id) => ['buildings', 'my', id] }` vào `queryKeys`.
- **File tạo:**
  - `src/features/buildings/hooks/use-my-buildings-query.ts` (`useAppQuery`, `placeholderData: keepPreviousData` khi đổi trang).
  - `src/features/buildings/hooks/use-my-building-query.ts`.
- **Kiểm tra bước:** React Query Devtools (nếu có) hoặc log thấy key đúng; đổi trang không nháy trắng.

### Bước 5 — i18n namespace `buildings`

- **File tạo:** `src/i18n/locales/vi/buildings.json`, `src/i18n/locales/en/buildings.json` (tiêu đề, cột bảng, nhãn trạng thái, empty state).
- **File sửa:**
  - `src/i18n/i18n.ts` và `src/types/i18next.d.ts`: đăng ký namespace `buildings`.
  - `src/i18n/locales/{vi,en}/common.json`: thêm `apiSuccess.BUILDINGS_MY_FETCHED`/`BUILDING_MY_FETCHED` nếu foundation cần.
- **Kiểm tra bước:** `npm run i18n:check` không báo key thiếu.

### Bước 6 — Trang danh sách `/buildings` (LL-02)

- **File tạo:** `src/features/buildings/pages/building-list-page.tsx`, `src/features/buildings/components/building-status-badge.tsx`.
- **Cách làm:**
  - Bảng hoặc card: Tên, Địa chỉ (`address, ward, province`), Trạng thái (badge), Ngày tạo; click dòng → `/buildings/:id`.
  - Bộ lọc trạng thái (`select-dropdown.tsx`) và phân trang theo `pagination`.
  - Nút "Thêm Tòa nhà" → `/buildings/new` (P6-03b làm trang này; tạm thời ẩn nếu route chưa có).
  - Empty state theo UI outline LL-01: CTA "Thêm Tòa nhà đầu tiên".
- **Kiểm tra bước:** có/không có dữ liệu đều hiển thị đúng; đổi filter thì gọi lại API với `filter[status]`.

### Bước 7 — Trang chi tiết `/buildings/:id` (LL-06)

- **File tạo:** `src/features/buildings/pages/building-detail-page.tsx`.
- **Cách làm:**
  - Hiển thị thông tin, trạng thái duyệt; nếu `rejected` thì hiện `note` (lý do) trong `alert-banner.tsx`.
  - Chừa vùng "Danh sách phòng" cho P6-03c và nút "Sửa/Xóa" cho P6-03b.
  - `404` → `error-state` + nút quay lại; `403` → điều hướng `forbidden-page`.
- **Kiểm tra bước:** mở id của landlord khác → hiện trang 403/404 đúng code.

### Bước 8 — Gắn route và menu

- **File sửa:**
  - `src/app/routes/roles/landlord.routes.tsx`: thay `DashboardOverview` ở `/buildings` và `/buildings/:id` bằng 2 page mới; `allowedRoles` chỉ còn `[Role.LANDLORD]` vì admin có màn riêng ở P6-03d (xác nhận với reviewer).
  - `src/config/navigation.config.ts`: đổi `landlord-rooms.path` từ `/rooms` → `/buildings`.
- **Kiểm tra bước:** bấm menu sidebar mở đúng trang; `npm run build` + `npm run lint` pass.

## Quyết định tạm thời / Ngoài phạm vi

- Không làm export `format=xlsx|csv|pdf` (contract có, nhưng không phải MVP).
- Room map trực quan của LL-01/LL-07 chưa làm, P6-03c dùng dạng danh sách.

## Manual verification

1. Landlord chưa có Building → empty state + CTA.
2. Có ≥ 21 Building → phân trang 2 trang, `pageSize=20`.
3. Lọc `rejected` → chỉ hiện Building bị từ chối; chi tiết hiện lý do.
4. Truy cập chi tiết Building của landlord khác → 403/404, không crash.

## Definition of Done

- [ ] Bước 1–8 qua phần Kiểm tra bước.
- [ ] `npm run build`, `npm run lint`, `npm run i18n:check` pass.
- [ ] PR có ảnh 3 trạng thái (rỗng, có dữ liệu, rejected) + `Closes pbl6-home-renter/docs#80`.
