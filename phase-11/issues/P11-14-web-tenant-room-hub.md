# P11-14 — Web: màn "Phòng của tôi" dùng API room-hub

**Trạng thái:** 🟡 Open  
**Người phụ trách (đề xuất):** `ThaiBao11125`  
**Người review:** FE Lead  
**Ước lượng:** 1 point · khoảng 4 giờ  
**Ưu tiên:** Thấp (màn hiện tại đã dùng được, task này làm dữ liệu đầy đủ hơn)  
**Phụ thuộc:** `GET /me/room-hub` đã có code trong Tenancy; API owner đổi `x-apidog-status` từ `designing` sang `developing` trước khi bắt đầu  
**Repo / branch:** `fe` · `feature/p11-14-tenant-room-hub`  
**Thay thế:** P10-15

## User story

> Là **người thuê**, tôi muốn **màn "Phòng của tôi" hiển thị tên tòa, địa chỉ đầy đủ, diện tích, giá thuê và thời hạn hợp đồng của từng phòng tôi đang ở**, để **biết ngay mình đang thuê gì mà không phải mở chi tiết hợp đồng**.

## Hiện trạng

- `fe/src/features/rooms/pages/tenant/tenant-rooms-page.tsx` đang lấy dữ liệu bằng `useTenantActiveContracts()` (bản "lite" theo P10-15/D7), nên thiếu tên tòa, địa chỉ, diện tích.
- `GET /me/room-hub` đã có controller nhưng FE chưa gọi.

## Contract

`GET /me/room-hub` (phân trang): mỗi phần tử là một hợp đồng đang hiệu lực của tenant (là người đứng tên hoặc thành viên đang ở), gồm `contractId`, `roomId`, `roomName`, `area`, `buildingId`, `buildingName`, `address`, `ward`, `province`, `rentPrice`, `startDate`, `endDate`. Sắp theo ngày bắt đầu mới nhất. Không có phòng → `200` với mảng rỗng.

## Mô tả

- Thêm API client + query hook cho `/me/room-hub`, thay `useTenantActiveContracts()` trong `tenant-rooms-page.tsx`. Giữ layout hiện có, chỉ bổ sung thông tin.
- Mỗi thẻ: tên phòng, tên tòa, địa chỉ ghép `address, ward, province`, diện tích (m²), giá thuê (định dạng VNĐ), thời hạn `startDate – endDate`. Nút "Xem hợp đồng" → `ROUTES.TENANT.CONTRACT_DETAIL(contractId)`, nút "Chat với chủ trọ" nếu màn hiện tại đã có.
- Phân trang nếu nhiều hơn 1 trang (thường tenant chỉ có 1–2 phòng).
- Giữ trạng thái rỗng, skeleton và lỗi như màn hiện tại.

## Acceptance criteria

- [ ] **Given** tenant có 1 hợp đồng đang hiệu lực, **when** mở "Phòng của tôi", **then** thấy 1 thẻ với đủ tên tòa, địa chỉ, diện tích, giá, thời hạn.
- [ ] **Given** tenant là thành viên đã rời phòng (ngày rời ≤ hôm nay), **then** phòng đó không còn hiện.
- [ ] **Given** tenant chưa có phòng, **then** hiện trạng thái rỗng kèm nút "Tìm phòng".
- [ ] Bấm "Xem hợp đồng" mở đúng hợp đồng.
- [ ] Không còn import `useTenantActiveContracts` trong màn này (nếu hook không còn nơi nào dùng thì xóa).

## Definition of Done

- [ ] Không viết file test. `npm run build`, `npm run lint`, `npm run i18n:check` pass.
- [ ] Ảnh chụp trước/sau đính kèm PR.
