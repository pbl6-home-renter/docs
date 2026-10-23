# P5-08d — Admin duyệt/từ chối Building

**Epic:** [P5-08](P5-08-tenancy-building-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** BE member  
**Người review:** BE Lead, API owner  
**Ước lượng:** 5 points · 10–14 giờ  
**Phụ thuộc:** P5-08b

## Mục tiêu

Admin xem danh sách Building chờ duyệt và approve/reject. Chỉ Building `approved` mới được tạo phòng và hiển thị công khai.

## Contract

| Endpoint | File |
|---|---|
| `GET /admin/buildings` | `api-docs/src/paths/buildings/admin-buildings.yaml` |
| `GET /admin/buildings/{buildingId}` | `api-docs/src/paths/buildings/admin-buildings-buildingId.yaml` |
| `POST /buildings/{buildingId}/approve` | `api-docs/src/paths/buildings/buildings-buildingId-approve.yaml` |
| `POST /buildings/{buildingId}/reject` | `api-docs/src/paths/buildings/buildings-buildingId-reject.yaml` |

## Việc cần làm

- [ ] Tất cả endpoint chỉ cho role admin.
- [ ] List/detail cho admin với filter/sort/pagination theo contract.
- [ ] `approve`: `building.approve(adminId)` → set `reviewed_by`, `reviewed_at`; append `BuildingApproved` vào outbox.
- [ ] `reject`: `building.reject(adminId, note)`; thiếu note → `NOTE_REQUIRED`; append `BuildingRejected` vào outbox.
- [ ] Building không ở `pending` → `BUILDING_NOT_PENDING`.
- [ ] Command đi qua UoW như pattern P5-08b.

## Cập nhật `api-docs` (bắt buộc trước khi đóng issue)

- [ ] **Xóa field `district`** (lỗi contract, đã chốt bỏ): `src/responses/dtos/buildings/admin-building-detail-response-dto.yaml` (property + `required`) và example trong `src/paths/buildings/admin-buildings-buildingId.yaml`.
- [ ] Viết/cập nhật **sequence diagram** cho từng endpoint (`getAdminBuildings`, `getAdminBuildingsBuildingid`, `postBuildingsBuildingidApprove`, `postBuildingsBuildingidReject`) khớp implementation, gồm outbox event approved/rejected. Tham khảo `src/paths/auth/register.yaml`.
- [ ] Đổi tag `x-apidog-status: designing` → `released` cho endpoint đã chạy và verify xong.
- [ ] Sync lên Apidog và link PR `api-docs` vào issue.

## Manual verification

1. Landlord gọi endpoint admin → `403`.
2. Approve Building `pending` → `status = approved`, có `reviewed_by`/`reviewed_at`, outbox có `BuildingApproved`.
3. Reject không có note → `NOTE_REQUIRED`; có note → `status = rejected`.
4. Approve/reject Building đã xử lý → `BUILDING_NOT_PENDING`.
