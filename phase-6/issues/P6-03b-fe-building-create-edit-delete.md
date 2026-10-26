# P6-03b — Wizard tạo Building, sửa và xóa Building

**Epic:** [P6-03](P6-03-fe-landlord-building-room-screens.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** ThaiBao11125  
**Người review:** baoduong17  
**Ước lượng:** 5 points · 10–14 giờ  
**Phụ thuộc:** P6-03a; BE P5-08b (`POST /buildings`), P5-08c (`PATCH`/`DELETE /buildings/{id}`); P6-04 (media presign/complete)  
**Repo / branch:** `fe` · `feature/p6-03b-building-create-edit`  
**Issue:** `docs#81`

## Mục tiêu

Landlord tạo Tòa nhà qua wizard 2 bước (LL-03 thông tin → LL-04 upload giấy tờ sở hữu), sau khi gửi thì Tòa nhà ở trạng thái **Chờ duyệt**. Landlord sửa được Building (trừ field bị khóa khi đã duyệt) và xóa được Building.

## Contract

- `api-doc/src/paths/buildings/buildings.yaml` → `postBuildings`: body `BuildingCreateRequestDto` (`api-doc/src/requests/buildings/building-create-request-dto.yaml`), `201 BUILDING_CREATED`.
  - **`district` đã bị PM loại** (xem P5-08b), không đưa vào form dù file contract còn field này.
  - `ownershipCertificateMediaIds`: mảng uuid, `minItems: 1`.
- `api-doc/src/paths/buildings/buildings-buildingId.yaml`:
  - `patchBuildingsBuildingid`: `BuildingUpdateRequestDto`, `200 BUILDING_UPDATED`, `409 APPROVED_BUILDING_LOCKED`.
  - `deleteBuildingsBuildingid`: `204`, `409` (đọc code cụ thể trong file).
- Media (để lấy id giấy tờ): `api-doc/src/paths/media/media-presign-upload.yaml` (`purpose: ownership_proof`, `ownerType: building`) → PUT file lên `uploadUrl` kèm `requiredHeaders` → `media-mediaId-complete-upload.yaml`.

## Tham chiếu code

| Cần | Copy pattern từ |
|---|---|
| Form + zod + lỗi API vào field | `src/features/auth/hooks/register/use-register-form.ts`, `src/features/auth/validations/register.validation.ts`, `setFormApiErrors` trong `validations/common.validation.ts` |
| Mutation có toast theo code | `src/features/auth/hooks/auth/use-login-mutation.ts` (`successCode`, `invalidateKeys`) |
| Input | `src/components/ui/input.tsx`, `number-input.tsx`, `textarea.tsx`, `checkbox.tsx` |
| Dialog xác nhận xóa | `src/components/ui/dialog.tsx`, `src/app/layouts/components/logout-modal.tsx` |
| API module/hook đã có | `src/features/buildings/*` (P6-03a) |

## Các bước triển khai

### Bước 1 — Chốt luồng media với API owner

- **Cách làm:** đọc P6-04 §Điểm cần chốt. Chỉ bắt đầu Bước 4 khi BE đã chốt cách presign cho Building chưa tồn tại (ví dụ: tạo Building trước rồi upload sau, hoặc presign với `ownerType: building` không cần `ownerId`). Ghi quyết định vào comment issue.
- **Kiểm tra bước:** quyết định có link comment của baoduong17.

### Bước 2 — Types, schema validate, API

- **File sửa:** `src/features/buildings/types/building.dto.ts`: thêm `BuildingCreateRequestDto`, `BuildingUpdateRequestDto`, `BuildingCreateResponseDto` theo contract.
- **File tạo:** `src/features/buildings/validations/building.validation.ts`: zod schema với `name` 1–254, `province`/`ward` 1–100, `address` 1–254, `totalFloors` int ≥ 1 optional, `description` ≤ 1000 optional, `amenities` object các boolean optional.
- **File sửa:** `src/features/buildings/api/building.api.ts`: `createBuilding`, `updateBuilding(id, body)`, `deleteBuilding(id)`.
- **Kiểm tra bước:** `npm run build` pass; rule zod khớp min/max của contract (liệt kê trong PR).

### Bước 3 — Wizard bước 1: thông tin Tòa nhà (LL-03)

- **File tạo:** `src/features/buildings/pages/building-create-page.tsx`, `src/features/buildings/components/building-info-form.tsx`, `src/features/buildings/hooks/use-building-form.ts`.
- **Cách làm:**
  - Form: Tên, Tỉnh/TP, Phường/Xã, Địa chỉ chi tiết, Số tầng, Mô tả, tiện ích chung (checkbox: thang máy, khóa vân tay, chỗ để xe, camera).
  - Lưu state wizard trong component cha (`useState`), chưa gọi API ở bước này.
  - Nút "Tiếp tục" chỉ bật khi form hợp lệ.
- **Kiểm tra bước:** để trống trường bắt buộc → hiện lỗi i18n dưới field, không chuyển bước.

### Bước 4 — Wizard bước 2: upload giấy tờ sở hữu (LL-04)

- **File tạo:** `src/features/buildings/components/ownership-proof-uploader.tsx` (dùng hook upload chung `src/features/media/hooks/use-media-upload.ts`, nếu P6-04 chưa có FE helper thì tạo tại đây theo đúng 3 bước presign → PUT → complete).
- **Cách làm:**
  - Cho chọn **nhiều** ảnh/PDF (`image/jpeg|png|webp`, `application/pdf`), kiểm tra MIME và kích thước trước khi presign.
  - Mỗi file: hiện tiến trình; lỗi `MEDIA_TYPE_NOT_ALLOWED`/`TICKET_EXPIRED` → toast i18n và cho thử lại.
  - Khi ≥ 1 file `complete` thì bật nút "Gửi duyệt" → gọi `createBuilding({...info, ownershipCertificateMediaIds})`.
  - `201` → toast `BUILDING_CREATED`, invalidate `queryKeys.buildings.all`, điều hướng `/buildings/:id`.
- **Kiểm tra bước:** tạo thành công → chi tiết hiện badge "Chờ duyệt"; `422` → lỗi về đúng field ở bước 1 (quay lại bước 1 nếu lỗi thuộc field ở đó).

### Bước 5 — Sửa Building

- **File tạo:** `src/features/buildings/pages/building-edit-page.tsx` (tái dùng `building-info-form.tsx` với `defaultValues` từ `useMyBuildingQuery`).
- **Cách làm:**
  - Chỉ gửi field thay đổi (`form.formState.dirtyFields`).
  - Với Building `approved`: disable các field bị khóa theo mô tả trong `buildings-buildingId.yaml`; nếu BE vẫn trả `409 APPROVED_BUILDING_LOCKED` thì hiện toast i18n.
  - Thành công → toast `BUILDING_UPDATED`, invalidate list + detail.
- **Kiểm tra bước:** sửa tên Building `pending` → cập nhật; sửa field khóa của Building `approved` → nhận 409 và toast đúng.

### Bước 6 — Xóa Building

- **File tạo:** `src/features/buildings/components/delete-building-dialog.tsx`.
- **Cách làm:** dialog xác nhận, gọi `deleteBuilding`; `204` → toast, điều hướng `/buildings`; `409` → toast theo code (ví dụ còn phòng/hợp đồng).
- **Kiểm tra bước:** xóa Building rỗng → biến mất khỏi list.

### Bước 7 — Route, i18n, nút trên trang chi tiết

- **File sửa:**
  - `src/app/routes/roles/landlord.routes.tsx`: thêm `/buildings/new`, `/buildings/:id/edit`.
  - `building-detail-page.tsx`, `building-list-page.tsx`: bật nút Thêm/Sửa/Xóa.
  - `src/i18n/locales/{vi,en}/buildings.json` + `common.json` (`apiSuccess.BUILDING_CREATED`, `BUILDING_UPDATED`, `apiErrors.APPROVED_BUILDING_LOCKED`…).
- **Kiểm tra bước:** `npm run build`, `npm run lint`, `npm run i18n:check` pass.

## Quyết định tạm thời / Ngoài phạm vi

- Không có bước 3/3 (LL-05 đơn giá điện nước), phần này thuộc Billing (Phase 6 It5 BE `rate-policies`).
- Không chụp camera trên web; chỉ chọn file từ máy.
- Không có geocoding/map picker (BE đang để lat/long mặc định).

## Manual verification

1. Tạo Building đủ thông tin + 2 ảnh giấy tờ → `201`, trạng thái Chờ duyệt.
2. Bỏ qua upload → nút "Gửi duyệt" bị khóa.
3. Upload file `.svg` → bị chặn ở client; ép gửi → BE `422 MEDIA_TYPE_NOT_ALLOWED` hiển thị đúng.
4. Sửa Building `approved` ở field bị khóa → 409 + toast.
5. Xóa Building → biến mất khỏi danh sách.

## Definition of Done

- [ ] Bước 1–7 qua phần Kiểm tra bước.
- [ ] `npm run build` + `npm run lint` + `npm run i18n:check` pass.
- [ ] PR có video/ảnh wizard và `Closes pbl6-home-renter/docs#81`.
