# P6-03 — Màn hình Building/Room cho Landlord và duyệt Building cho Admin (Epic)

**Trạng thái:** 🟡 Open  
**Người phụ trách:** ThaiBao11125  
**Người review:** baoduong17 (FE review + API owner)  
**Ước lượng:** 18 points tổng (P6-03a 5 · P6-03b 5 · P6-03c 5 · P6-03d 3)  
**Phụ thuộc:** `fe#6` (P5-01…P5-07) đã merge vào `main`; BE P5-08 (Building) và P5-09 (Room) đã deploy staging; P6-04 (media upload) cho P6-03b  
**Repo / branch:** `fe` · mỗi sub-issue một branch `feature/p6-03x-<slug>`  
**Issue:** `docs#79`

## Mục tiêu

Landlord quản lý được Tòa nhà và Phòng trên web console (list, tạo, sửa, xóa), Admin duyệt hoặc từ chối Tòa nhà chờ duyệt. Tất cả gọi API thật qua foundation của Phase 5, không còn placeholder `DashboardOverview`.

## Sub-issue

| ID | Nội dung | Màn hình (UI outline) | Ước lượng | Phụ thuộc |
|---|---|---|---|---|
| [P6-03a](P6-03a-fe-building-api-list-detail.md) | Building API layer, danh sách và chi tiết Building của tôi | LL-02, LL-06 | 5 pts · 10–14h | `fe#6`, P5-08c |
| [P6-03b](P6-03b-fe-building-create-edit-delete.md) | Wizard tạo Building (bước 1–2), sửa, xóa | LL-03, LL-04 | 5 pts · 10–14h | P6-03a, P5-08b, P5-08f, P6-04 |
| [P6-03c](P6-03c-fe-room-list-create-edit.md) | Danh sách, tạo, sửa, xóa, mark-ready Room trong 1 Building | LL-07, LL-08, LL-09 | 5 pts · 10–14h | P6-03a, P5-09b, P5-09c |
| [P6-03d](P6-03d-fe-admin-building-approval.md) | Admin: danh sách chờ duyệt, chi tiết, duyệt/từ chối | AD-06, AD-07, AD-08 | 3 pts · 6–8h | P6-03a, P5-08d |

Thứ tự: `P6-03a → (P6-03b ∥ P6-03c ∥ P6-03d)`. P6-03a dựng API layer dùng chung nên phải merge trước.

## Nguồn tham chiếu chung

- Contract: `api-doc/src/paths/buildings/*.yaml`, `api-doc/src/paths/rooms/*.yaml`; DTO trong `api-doc/src/requests/{buildings,rooms}/` và schema `Building*Dto`/`Room*Dto` trong `api-doc/src/openapi.yaml`.
- Nghiệp vụ: `pm/phase-1/discovery/user_flow/landlord_user_flow.md` (Sub-Flow 1), `pm/phase-1/discovery/user_flow/admin_user_flow.md` (Sub-Flow 3).
- Màn hình: `pm/phase-2/discovery/Rentify_UI_Screen_Outline_v0.1.md` (LL-02…LL-09, AD-06…AD-08).
- Foundation FE (từ `fe#6`, nhánh `feat/p5-auth-vertical-slice`):
  - API module mẫu: `src/features/auth/api/auth.api.ts` (`apiClient` + `ApiResponse<T>`).
  - Hook mẫu: `src/features/auth/hooks/auth/use-login-mutation.ts` (`useAppMutation`, `successCode`), `use-current-user-query.ts` (`useAppQuery`, `queryKeys`).
  - Form mẫu: `src/features/auth/hooks/login/use-login-form.ts` + `validations/login.validation.ts` (react-hook-form + zod, `setFormApiErrors`, `getFieldError`).
  - Response list: `src/lib/axios.ts` unwrap response có `pagination` thành `{ data, pagination }` (kiểu `OffsetPaginationMeta` trong `src/types/api.ts`).
  - Error/success code → i18n: `src/lib/api-code-i18n.ts`, `src/i18n/locales/{vi,en}/*.json`.
  - UI: `src/components/ui/*`, `src/components/feedback/*` (empty/error/skeleton).
  - Route: `src/app/routes/roles/landlord.routes.tsx`, `admin.routes.tsx`; menu: `src/config/navigation.config.ts`.

## Quy định chung cho cả epic

- Chỉ dùng field/route/code có trong contract. Gặp chỗ contract mâu thuẫn thì dừng và comment vào issue, không tự workaround.
- Toast dùng API `code` + i18n, không hiển thị raw `message`.
- Chỉ offset pagination (`pageNo`, `pageSize`), không cursor.
- Không làm LL-05 (đơn giá điện nước của Building, thuộc Billing) và LL-10 (Menu tiện ích phòng, cần Contract).
- PR ghi `Closes pbl6-home-renter/docs#<số sub-issue>` và đính kèm ảnh màn hình.

## Điểm cần chốt trước khi bắt đầu

1. **Menu và route lệch nhau:** `LANDLORD_NAVIGATION` có `/rooms`, còn route thật là `/buildings` và `/buildings/:id`. Đề xuất: đổi menu item `landlord-rooms` sang `path: '/buildings'` (giữ nhãn "Quản lý Phòng & BĐS"); Room nằm dưới `/buildings/:id/rooms/...`. Làm trong P6-03a.
2. **Geocoding:** BE tự geocode `latitude`/`longitude` bằng TrackAsia trong Tenancy-Service (P5-08f), khi tạo và khi đổi `address`. FE không gửi tọa độ, không làm map picker/autocomplete; chỉ xử lý `422 GEOCODING_FAILED` / `503 GEOCODING_UNAVAILABLE` và dùng tọa độ trong response nếu cần.
3. **Media cho giấy tờ sở hữu:** `BuildingCreateRequestDto.ownershipCertificateMediaIds` yêu cầu ≥ 1 media id, nhưng `POST /media/presign-upload` lại đòi `ownerId` của Building, mà Building chưa tồn tại lúc này. Vướng ở P6-03b và P6-04; API owner phải chốt cách làm trước It5 (xem P6-04 §Điểm cần chốt).

## Definition of Done (epic)

- [ ] 4 sub-issue Done; route `/buildings`, `/buildings/:id`, `/buildings/:id/rooms/*`, `/admin/approvals` không còn dùng `DashboardOverview` placeholder.
- [ ] Demo trên staging: landlord tạo Building (tọa độ được geocode thật, không phải `0`) → admin duyệt → landlord tạo Room → mark ready.
