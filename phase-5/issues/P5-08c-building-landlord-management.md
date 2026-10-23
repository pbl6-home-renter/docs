# P5-08c — Landlord quản lý Building

**Epic:** [P5-08](P5-08-tenancy-building-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** BE member  
**Người review:** BE Lead, API owner  
**Ước lượng:** 5 points · 10–14 giờ  
**Phụ thuộc:** P5-08b

## Mục tiêu

Cho landlord xem, sửa và xóa Building của chính mình.

## Contract

| Endpoint | File |
|---|---|
| `GET /me/buildings` | `api-docs/src/paths/buildings/me-buildings.yaml` |
| `GET /me/buildings/{buildingId}` | `api-docs/src/paths/buildings/me-buildings-buildingId.yaml` |
| `PATCH /buildings/{buildingId}` | `api-docs/src/paths/buildings/buildings-buildingId.yaml` |
| `DELETE /buildings/{buildingId}` | `api-docs/src/paths/buildings/buildings-buildingId.yaml` |

## Việc cần làm

### Query

- [ ] List có `filter`, `sort`, `order`, `pageNo`, `pageSize` theo contract (offset pagination).
- [ ] Chỉ trả Building có `landlord_id` = user hiện tại; Building của người khác trả `404`, không lộ sự tồn tại.
- [ ] Query đọc qua query/read repository, không đưa query logic vào entity.

### Command

- [ ] `PATCH`: gọi `building.update(...)`; Building đã `approved` không được sửa trường bị khóa → `409 APPROVED_BUILDING_LOCKED`. Append `BuildingUpdated` vào outbox.
- [ ] `DELETE`: soft-delete qua aggregate, append `BuildingDeleted` vào outbox.
- [ ] Cả hai command đi qua UoW như pattern P5-08b.

## Quyết định tạm thời

- **`BUILDING_HAS_ACTIVE_CONTRACT`:** domain Contract chưa tồn tại → **bỏ qua check này**. Ghi `TODO` tại handler delete; bổ sung khi có Contract.

## Cập nhật `api-docs` (bắt buộc trước khi đóng issue)

- [ ] **Xóa field `district`** (lỗi contract, đã chốt bỏ): `src/responses/dtos/buildings/my-building-detail-response-dto.yaml` (property + `required`) và example trong `src/paths/buildings/me-buildings-buildingId.yaml`.
- [ ] Viết/cập nhật **sequence diagram** cho từng endpoint (`getMeBuildings`, `getMeBuildingsBuildingid`, `patchBuildingsBuildingid`, `deleteBuildingsBuildingid`) khớp implementation. Tham khảo `src/paths/auth/register.yaml`.
- [ ] Đổi tag `x-apidog-status: designing` → `released` cho endpoint đã chạy và verify xong.
- [ ] Sync lên Apidog và link PR `api-docs` vào issue.

## Manual verification

1. List/detail chỉ trả Building của landlord đang đăng nhập; pagination đúng.
2. Truy cập Building của landlord khác → `404`.
3. Sửa Building `pending` → `200 BUILDING_UPDATED`.
4. Sửa trường bị khóa của Building `approved` → `409 APPROVED_BUILDING_LOCKED`.
5. Xóa → Building không còn xuất hiện trong list; outbox có `BuildingDeleted`.
