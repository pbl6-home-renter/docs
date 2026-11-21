# P11-01 — Cập nhật contract dashboard, users/stats và audit-logs

**Trạng thái:** 🟡 Open  
**Người phụ trách (đề xuất):** `baoduong17` (API owner)  
**Người review:** PM, BE Lead  
**Ước lượng:** 2 points · khoảng 6 giờ  
**Phụ thuộc:** —  
**Repo / branch:** `api-docs` · `docs/p11-01-admin-contract`  
**Quyết định áp dụng:** [P11-D92](../decisions.md#d92--admin-dashboard-và-audit-log)

## User story

> Là **dev BE và FE của khu vực admin**, tôi muốn **contract của dashboard và audit log được chốt theo P11-D92**, để **hai bên làm song song mà không phải đoán field**.

## Hiện trạng

- `api-docs/src/paths/operations/dashboard.yaml`: có `from`/`to`, có `systemTransactionVolume`, `occupancyRate` kiểu string, gộp số liệu user và tòa vào một endpoint.
- `api-docs/src/paths/operations/audit-logs.yaml`: dùng tham số chung `filter` và `format`; response không có `metadata`, không có tên người thực hiện.
- Chưa có `GET /users/stats`.

## Phạm vi thay đổi

1. **`GET /dashboard` (Tenancy)**
   - Bỏ `from`, `to`, `systemTransactionVolume`, `totalUsers`, `totalLandlords`, `totalTenants`.
   - Response `data`: `totalBuildings`, `pendingApprovalBuildings`, `rejectedBuildings`, `totalRooms`, `roomsByStatus { available, occupied, maintenance }`, `occupancyRate` (number), `generatedAt`.
   - Lỗi: `401`, `403 FORBIDDEN` (không phải admin). Bỏ `422 INVALID DATE RANGE`.
2. **`GET /users/stats` (Identity, mới)** — file mới trong `api-docs/src/paths/users/`.
   - Response `data`: `totalUsers`, `byRole { admin, landlord, tenant }`, `byStatus { active, locked, pendingVerification }`, `generatedAt`.
   - Success code đề xuất: `USER_STATS_FETCHED`.
3. **`GET /audit-logs` (Identity)**
   - Thay `filter`, `format` bằng tham số rõ ràng: `action` (enum 6 giá trị trong P11-D92), `entityType` (`user` | `building`), `actorId` (uuid), `entityId` (uuid), `from`, `to` (date-time), `pageNo`, `pageSize` (tối đa 100).
   - Sắp xếp mặc định `createdAt` giảm dần.
   - Mỗi item thêm `actorName` (nullable — actor đã bị xóa thì null) và `sourceService` (`identity` | `tenancy`).
   - `422 VALIDATION_FAILED` khi `from > to` hoặc enum sai.
4. **`GET /audit-logs/{auditLogId}`**: response chi tiết thêm `metadata` (object, theo allowlist trong P11-D92). Không tìm thấy → `404 AUDIT_LOG_NOT_FOUND`.
5. Cả 4 operation: `x-apidog-status: developing`, có ví dụ response hợp lệ.

## Acceptance criteria

- [ ] **Given** spec đã sửa, **when** chạy `npm run lint` và `npm run bundle`, **then** cả hai pass và `reference/rentify.json` được cập nhật.
- [ ] **Given** spec `/dashboard`, **then** không còn `from`, `to`, `systemTransactionVolume` hay field user nào.
- [ ] **Given** spec `/users/stats`, **then** chỉ role `admin` được gọi, có ví dụ response với đủ field ở trên.
- [ ] **Given** spec `/audit-logs`, **then** không còn tham số `filter`/`format`; `action` là enum đúng 6 giá trị của P11-D92.
- [ ] Ví dụ `metadata` không chứa mật khẩu, token, SĐT, CCCD hay giá trị cũ/mới của field.
- [ ] Mock Apidog trả được dữ liệu cho cả 4 operation để FE dùng tạm.

## Ngoài phạm vi

- Code BE/FE (P11-02 → P11-08).
- Export audit log ra file.

## Definition of Done

- [ ] PR `api-docs` được BE Lead và FE Lead approve trước khi merge.
- [ ] Link PR được dán vào P11-02 → P11-08.
