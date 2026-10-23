# P5-08b — Create Building (slice mẫu UoW + Outbox)

**Epic:** [P5-08](P5-08-tenancy-building-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** BE member  
**Người review:** BE Lead, API owner  
**Ước lượng:** 5 points · 10–14 giờ  
**Phụ thuộc:** P5-08a

## Mục tiêu

Triển khai `POST /buildings` end-to-end. Đây là **slice mẫu** — các command khác của Building và Room làm theo đúng pattern này.

## Contract

- `api-docs/src/paths/buildings/buildings.yaml` (`postBuildings`).
- Role: landlord. Response `201`, code `BUILDING_CREATED`, header `Location`.
- Building mới luôn ở `status = pending`; `landlord_id` lấy từ JWT, không nhận từ body.

## Việc cần làm

- [ ] Controller + DTO validation theo `BuildingCreateRequestDto`; map DTO sang command, không truyền request object vào domain.
- [ ] Command handler: mở UoW → `Building.create(...)` → repository save → append outbox → commit → trả response.
- [ ] Map domain event `BuildingCreated` sang integration event (`message_id`, `event_type`, `aggregate_id`, timestamp).
- [ ] Map lỗi domain/application sang error code API (`VALIDATION_FAILED`, `FORBIDDEN`).
- [ ] Swagger/OpenAPI schema khớp `api-docs`.

## Quyết định tạm thời

- **Geocoding:** chưa triển khai. Gán `latitude`/`longitude` bằng **giá trị mặc định** (`0.000000`), đặt thành constant/config để thay bằng geocode thật sau. Ghi `TODO` ở chỗ gán.
- **`ownershipCertificateMediaIds`:** chưa có media flow — nhận theo contract nhưng không validate/không lưu liên kết media.
- **`district`:** đã được PM xác nhận là **lỗi trong `api-docs`** (Việt Nam đã bỏ cấp Quận/Huyện, địa chỉ chỉ còn Tỉnh/TP → Phường/Xã). **Xóa field `district`**, không thêm cột vào DB. Các file cần sửa:
  - `src/requests/buildings/building-create-request-dto.yaml` (property + `required`);
  - `src/paths/buildings/buildings.yaml` (request example).
  - Các response DTO/example còn lại xóa trong sub-issue tương ứng (P5-08c, P5-08d, P5-09d); `src/schemas/common/address-hierarchy.yaml` không còn được tham chiếu — xóa `district` luôn trong task này.

## Cập nhật `api-docs` (bắt buộc trước khi đóng issue)

- [ ] Xóa `district` như mục trên.
- [ ] Viết/cập nhật **sequence diagram** (block ` ```mermaid sequenceDiagram ``` ` trong `description`) của `postBuildings` khớp implementation thực tế: Gateway → Tenancy → DB (transaction + outbox) → RabbitMQ. Tham khảo `src/paths/auth/register.yaml`.
- [ ] Đổi tag `x-apidog-status: designing` → `released` cho endpoint đã chạy và verify xong.
- [ ] Sync lên Apidog và link PR `api-docs` vào issue.

## Manual verification

1. Tạo Building hợp lệ → `201`, `status = pending`, lat/long = giá trị mặc định.
2. Gửi dữ liệu thiếu/sai → `422 VALIDATION_FAILED`.
3. Gọi bằng role không phải landlord → `403`.
4. Buộc lỗi trước commit → không còn row `buildings` lẫn outbox dở dang.
5. Relay publish `BuildingCreated` sau khi commit.
