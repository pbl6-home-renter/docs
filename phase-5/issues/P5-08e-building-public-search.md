# P5-08e — Tìm kiếm và xem Building public

**Epic:** [P5-08](P5-08-tenancy-building-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** BE member  
**Người review:** BE Lead, API owner  
**Ước lượng:** 3 points · 6–8 giờ  
**Phụ thuộc:** P5-08d

## Mục tiêu

Cho tenant/khách tìm kiếm và xem chi tiết Building đã được duyệt.

## Contract

| Endpoint | File |
|---|---|
| `GET /buildings` | `api-docs/src/paths/buildings/buildings.yaml` (`getBuildings`) |
| `GET /buildings/{buildingId}` | `api-docs/src/paths/buildings/buildings-buildingId.yaml` (`getBuildingsBuildingid`) |

## Việc cần làm

- [ ] Chỉ trả Building `status = approved` và chưa bị xóa.
- [ ] Query param, filter, pagination và response schema theo đúng contract; không tự thêm field.
- [ ] Building không tồn tại hoặc chưa approved → `404`.
- [ ] Nếu contract có field phụ thuộc Room/Media chưa có dữ liệu, ghi blocker cho API owner thay vì tự định nghĩa.

## Cập nhật `api-docs` (bắt buộc trước khi đóng issue)

- [ ] Không thêm `district` vào response (field đã chốt bỏ khỏi contract).
- [ ] Viết/cập nhật **sequence diagram** cho `getBuildings` và `getBuildingsBuildingid` khớp implementation. Tham khảo `src/paths/auth/register.yaml`.
- [ ] Đổi tag `x-apidog-status: designing` → `released` cho endpoint đã chạy và verify xong.
- [ ] Sync lên Apidog và link PR `api-docs` vào issue.

## Manual verification

1. Building `pending`/`rejected` không xuất hiện trong kết quả tìm kiếm.
2. Xem chi tiết Building chưa approved → `404`.
3. Filter/pagination trả đúng kết quả theo contract.
