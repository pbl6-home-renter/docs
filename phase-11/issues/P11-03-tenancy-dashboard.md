# P11-03 — Tenancy: thống kê tòa và phòng `GET /dashboard`

**Trạng thái:** 🟡 Open  
**Người phụ trách (đề xuất):** `leminhkhai345`  
**Người review:** BE Lead  
**Ước lượng:** 2 points · khoảng 6 giờ  
**Phụ thuộc:** P11-01 (contract)  
**Repo / branch:** `Tenancy-Service` · `feature/p11-03-admin-dashboard`  
**Quyết định áp dụng:** [P11-D92](../decisions.md#d92--admin-dashboard-và-audit-log)

## User story

> Là **admin hệ thống**, tôi muốn **xem tổng số tòa, số tòa đang chờ duyệt, số phòng theo trạng thái và tỉ lệ lấp đầy toàn hệ thống**, để **biết có việc duyệt nào đang tồn đọng và nền tảng đang được sử dụng ra sao**.

## Mô tả

- Thêm query `admin-dashboard` (CQRS). Có thể đặt trong module `building` hoặc một module đọc riêng, theo skill `be-feature-workflow`.
- Đọc bằng câu lệnh đếm trên `buildings` và `rooms`, luôn lọc `is_deleted = false`.
- Cách tính theo bảng "Định nghĩa số liệu" trong P11-D92:
  - `totalBuildings` chỉ đếm tòa `approved`.
  - `totalRooms` và `roomsByStatus` chỉ đếm phòng thuộc tòa `approved`, chưa xóa.
  - `occupancyRate = occupied / totalRooms × 100`, làm tròn 1 chữ số thập phân; `totalRooms = 0` → `0`.
- Route `GET /dashboard`, `@Roles(UserRole.ADMIN)`. Gateway đã route `/dashboard` về Tenancy.

## Ví dụ số

| Dữ liệu | Kết quả |
|---|---|
| 3 tòa `approved` (1 trong đó đã xóa mềm), 2 `pending`, 1 `rejected` | `totalBuildings = 2`, `pendingApprovalBuildings = 2`, `rejectedBuildings = 1` |
| 2 tòa approved còn lại có 8 phòng: 5 `occupied`, 2 `available`, 1 `maintenance`; tòa `pending` có 4 phòng | `totalRooms = 8`, `roomsByStatus = {available: 2, occupied: 5, maintenance: 1}`, `occupancyRate = 62.5` |
| 3 phòng: 1 `occupied` | `occupancyRate = 33.3` |
| Chưa có phòng nào | `totalRooms = 0`, `occupancyRate = 0` |

## Acceptance criteria

- [ ] **Given** admin đăng nhập, **when** gọi `GET /dashboard`, **then** `200` với đúng các field trong contract P11-01, không còn field user hay `systemTransactionVolume`.
- [ ] **Given** dữ liệu như bảng ví dụ, **then** kết quả khớp từng dòng.
- [ ] Phòng/tòa đã xóa mềm và phòng thuộc tòa `pending`/`rejected` **không** được tính vào `totalRooms`.
- [ ] **Given** token landlord/tenant, **then** `403 FORBIDDEN`. Không có token → `401`.
- [ ] Gọi qua gateway thành công.

## Definition of Done

- [ ] Unit test cho phần tính `occupancyRate` (làm tròn, chia cho 0).
- [ ] `npm run build`, `npm run lint`, `npm test` pass; check dependency rule không in gì.
- [ ] `x-apidog-status` của `/dashboard` đổi sang `released` sau khi verify trên staging.
- [ ] Ảnh chụp/export Apidog đính kèm PR.
