# P6-03d — Admin duyệt/từ chối Building

**Epic:** [P6-03](P6-03-fe-landlord-building-room-screens.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** ThaiBao11125  
**Người review:** baoduong17  
**Ước lượng:** 3 points · 6–8 giờ  
**Phụ thuộc:** P6-03a; BE P5-08d (`/admin/buildings`, `approve`, `reject`)  
**Repo / branch:** `fe` · `feature/p6-03d-admin-building-approval`  
**Issue:** `docs#83`

## Mục tiêu

Admin vào `/admin/approvals` thấy danh sách Tòa nhà chờ duyệt (AD-06), mở chi tiết xem thông tin và ảnh giấy tờ (AD-07), rồi Phê duyệt hoặc Từ chối kèm lý do bắt buộc (AD-08).

## Contract

- `api-doc/src/paths/buildings/admin-buildings.yaml` → `getAdminBuildings`: `filter[status]`, `filter[landlordId]`, phân trang; `200 BUILDINGS_ADMIN_FETCHED`, item `BuildingAdminListResponseDto`.
- `api-doc/src/paths/buildings/admin-buildings-buildingId.yaml` → `getAdminBuildingsBuildingid`: `200 BUILDING_ADMIN_FETCHED`, `BuildingAdminDetailResponseDto`.
- `api-doc/src/paths/buildings/buildings-buildingId-approve.yaml` → `postBuildingsBuildingidApprove`: `BuildingApproveRequestDto` (note tùy chọn), `200 BUILDING_APPROVED`, `409 BUILDING_NOT_PENDING`.
- `api-doc/src/paths/buildings/buildings-buildingId-reject.yaml` → `postBuildingsBuildingidReject`: `BuildingRejectRequestDto` (note bắt buộc), `200 BUILDING_REJECTED`, `409 BUILDING_NOT_PENDING`, `422 NOTE_REQUIRED | VALIDATION_FAILED`.
- Ảnh giấy tờ: `GET /media/{mediaId}` (`api-doc/src/paths/media/media-mediaId.yaml`) trả file stream. Cần P6-04; nếu chưa có thì hiển thị danh sách media id.
- Role: `admin`.

## Tham chiếu code

| Cần | Copy pattern từ |
|---|---|
| API/hook/types Building | `src/features/buildings/*` (P6-03a) |
| Dialog nhập lý do | `src/components/ui/dialog.tsx` + `textarea.tsx` |
| Route admin | `src/app/routes/roles/admin.routes.tsx` (`/admin/approvals` đang là placeholder) |

## Các bước triển khai

### Bước 1 — Dữ liệu test

- **Cách làm:** tạo branch; trên staging dùng landlord test tạo 2–3 Building `pending` (Apidog hoặc màn P6-03b); login admin seed (`npm run seed:admin` của Identity, hỏi BE Lead tài khoản).
- **Kiểm tra bước:** Apidog `GET /admin/buildings?filter[status]=pending` bằng token admin trả danh sách.

### Bước 2 — API và hooks admin

- **File sửa:** `src/features/buildings/api/building.api.ts`: `getAdminBuildings(params)`, `getAdminBuilding(id)`, `approveBuilding(id, body)`, `rejectBuilding(id, body)`.
- **File sửa:** `src/features/buildings/types/building.dto.ts`: `BuildingAdminListItemDto`, `BuildingAdminDetailDto`, `BuildingApproveRequestDto`, `BuildingRejectRequestDto`.
- **File tạo:** `src/features/buildings/hooks/admin/use-admin-buildings-query.ts`, `use-admin-building-query.ts`, `use-approve-building-mutation.ts`, `use-reject-building-mutation.ts` (`invalidateKeys: [queryKeys.buildings.all]`).
- **Kiểm tra bước:** `npm run build` pass.

### Bước 3 — Danh sách chờ duyệt (AD-06)

- **File tạo:** `src/features/buildings/pages/admin/building-approval-list-page.tsx`.
- **Cách làm:** mặc định `filter[status]=pending`, có select đổi sang approved/rejected; cột Tên, Địa chỉ, Chủ trọ (theo field contract), Ngày tạo; click → `/admin/approvals/:id`.
- **Kiểm tra bước:** danh sách chỉ có Building `pending` ở lần mở đầu.

### Bước 4 — Chi tiết và hành động (AD-07, AD-08)

- **File tạo:** `src/features/buildings/pages/admin/building-approval-detail-page.tsx`, `src/features/buildings/components/admin/reject-building-dialog.tsx`.
- **Cách làm:**
  - Hiển thị thông tin Building + chủ trọ + ảnh giấy tờ (thumbnail mở lớn; PDF mở tab mới).
  - "Phê duyệt" → confirm → `approveBuilding` → toast `BUILDING_APPROVED`, quay về list.
  - "Từ chối" → dialog bắt buộc nhập lý do (zod: trim ≥ 1, ≤ 500 theo contract) → `rejectBuilding` → toast `BUILDING_REJECTED`.
  - `409 BUILDING_NOT_PENDING` → toast và refetch chi tiết.
  - Ẩn 2 nút khi status ≠ `pending`.
- **Kiểm tra bước:** từ chối với lý do rỗng → không gửi request; gửi lý do → landlord thấy lý do ở LL-06.

### Bước 5 — Route, i18n

- **File sửa:**
  - `src/app/routes/roles/admin.routes.tsx`: `/admin/approvals` → list page; thêm `/admin/approvals/:id`.
  - `src/i18n/locales/{vi,en}/buildings.json` (mục `admin.*`), `common.json` (`BUILDING_APPROVED`, `BUILDING_REJECTED`, `BUILDING_NOT_PENDING`, `NOTE_REQUIRED`).
- **Kiểm tra bước:** `npm run build`, `npm run lint`, `npm run i18n:check` pass.

## Quyết định tạm thời / Ngoài phạm vi

- Audit log và thông báo cho landlord do BE xử lý (không làm trên FE).
- Nếu `GET /media/{id}` chưa có: hiển thị text "Giấy tờ: N tệp (chưa xem được)" và ghi `TODO(media)`.

## Manual verification

1. Admin duyệt Building `pending` → landlord thấy "Đã duyệt" và thêm được phòng.
2. Admin từ chối kèm lý do → landlord thấy lý do.
3. Duyệt lại Building đã duyệt (2 tab) → `409 BUILDING_NOT_PENDING` hiển thị đúng.
4. Landlord truy cập `/admin/approvals` → trang 403.

## Definition of Done

- [ ] Bước 1–5 qua phần Kiểm tra bước.
- [ ] `npm run build` + `npm run lint` + `npm run i18n:check` pass.
- [ ] PR có ảnh AD-06/07/08 và `Closes pbl6-home-renter/docs#83`.
