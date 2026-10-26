# P6-08 — Local administrative geography API (Tenancy)

## Mục tiêu

Triển khai API chỉ đọc cho địa giới hành chính Việt Nam để web/mobile dùng làm danh mục chọn tỉnh/thành phố và phường/xã. Không triển khai geocoding, không tạo bảng database, không gọi provider runtime và không thêm cache.

## Quyết định triển khai

- Owner: `baoduong17` (BE/API lead).
- Service: `Tenancy-Service`, vì dữ liệu phục vụ trực tiếp cho Building address flow.
- Gateway: route `/api/v1/administrative-units/**` tới Tenancy-Service.
- Source snapshot: `https://provinces.open-api.vn/api/v2`.
- Local map: commit JSON snapshot gồm 34 provinces và 3,321 wards; mã tỉnh chuẩn hóa 2 chữ số, mã phường/xã 5 chữ số.
- API là public read-only vì đây là reference data không phụ thuộc user.

## API contract

### `GET /api/v1/administrative-units/provinces`

Trả danh sách `{ code, name, divisionType }` trong `data`.

### `GET /api/v1/administrative-units/provinces/{provinceCode}/wards`

Trả danh sách `{ code, provinceCode, name, divisionType }` trong `data`. Input chấp nhận một hoặc hai chữ số; backend chuẩn hóa về hai chữ số. Mã không hợp lệ trả `422 INVALID_PROVINCE_CODE`, mã không tồn tại trả `404 PROVINCE_NOT_FOUND`.

## Phạm vi file

- `Tenancy-Service/src/modules/administrative-unit/`: module, local catalog, service, controller, DTO.
- `Tenancy-Service/src/modules/administrative-unit/infrastructure/data/vietnam-administrative-units.v2.json`: snapshot runtime.
- `Tenancy-Service/scripts/generate-administrative-map.mjs`: tool cập nhật snapshot có chủ đích.
- `api-gateway/src/constants/route-paths.constants.ts`: route và public rules.
- `api-docs/src/openapi.yaml`, `api-docs/src/paths/administrative-units/`, `api-docs/src/schemas/administrative-units/`: canonical contract.

## Acceptance criteria

- [ ] `GET /api/v1/administrative-units/provinces` trả HTTP 200 và đủ 34 tỉnh/thành.
- [ ] `GET /api/v1/administrative-units/provinces/01/wards` trả HTTP 200 và các ward có `provinceCode = "01"`.
- [ ] `GET /api/v1/administrative-units/provinces/1/wards` cho kết quả tương đương `/01/wards`.
- [ ] Input `abc` trả `422 INVALID_PROVINCE_CODE`; input `99` trả `404 PROVINCE_NOT_FOUND`.
- [ ] Gateway cho phép hai GET public và forward đúng tới Tenancy-Service.
- [ ] OpenAPI, API docs note và PM issue phản ánh cùng path/response/error codes.
- [ ] `npm run build` và `npm run lint` của Tenancy-Service pass.

## Không thuộc phạm vi

- Geocoding/reverse geocoding và tọa độ.
- Đồng bộ runtime với TrackAsia hoặc bất kỳ provider nào.
- Database/cache/CRUD admin cho danh mục.
- Thay đổi schema Building đang lưu `province`, `ward`, `address` dạng text.

## Rollout / refresh snapshot

Khi cần cập nhật dữ liệu, chạy `npm run administrative-map:generate`, review diff JSON, build/lint, rồi commit snapshot cùng API docs nếu shape thay đổi. Không tự động fetch khi service chạy.
