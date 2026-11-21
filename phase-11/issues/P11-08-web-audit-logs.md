# P11-08 — Web: màn Audit logs

**Trạng thái:** 🟡 Open  
**Người phụ trách (đề xuất):** `ThaiBao11125`  
**Người review:** FE Lead  
**Ước lượng:** 2 points · khoảng 8 giờ  
**Phụ thuộc:** P11-01 (contract, dùng mock Apidog để dựng UI); nối API thật sau P11-06  
**Repo / branch:** `fe` · `feature/p11-08-admin-audit-logs`  
**Quyết định áp dụng:** [P11-D92](../decisions.md#d92--admin-dashboard-và-audit-log)

## User story

> Là **admin**, tôi muốn **xem danh sách thao tác quản trị, lọc theo loại thao tác, đối tượng và thời gian, rồi mở chi tiết từng dòng**, để **tra được ai đã khóa một tài khoản hoặc từ chối một tòa, và với ghi chú gì**.

## Hiện trạng

`ROUTES.ADMIN.AUDIT_LOGS` đang render placeholder `DashboardOverview`.

## Mô tả

- **Bảng danh sách** (dùng `data-table` có sẵn): cột Thời gian, Người thực hiện (`actorName`, null → "Tài khoản đã xóa"), Thao tác (nhãn tiếng Việt cho 6 `action`), Đối tượng (loại + liên kết), Nguồn (`identity`/`tenancy`).
- **Bộ lọc:** Thao tác (select 6 giá trị), Loại đối tượng (`user` / `building`), Khoảng thời gian (từ – đến). Lưu filter + trang vào URL query để reload/chia sẻ link giữ nguyên.
- **Phân trang** theo `pagination` của API, mặc định 20 dòng/trang.
- **Liên kết đối tượng:** `entityType = user` → `ROUTES.ADMIN.USER_DETAIL(entityId)`; `building` → `ROUTES.ADMIN.BUILDING_DETAIL(entityId)`. Đối tượng đã bị xóa (trang chi tiết trả 404) thì trang đích tự hiện thông báo không tìm thấy, không crash.
- **Chi tiết:** bấm một dòng mở drawer/dialog gọi `GET /audit-logs/{id}`, hiển thị `metadata` dạng dễ đọc:
  - `changedFields` → "Đã sửa: Họ tên, Vai trò" (dịch tên field).
  - `note` → "Ghi chú: …".
  - Không hiển thị JSON thô.
- Chuỗi qua i18n (vi + en).

## Nhãn thao tác (vi)

| `action` | Nhãn |
|---|---|
| `user.locked` | Khóa tài khoản |
| `user.unlocked` | Mở khóa tài khoản |
| `user.updated` | Sửa thông tin tài khoản |
| `user.deleted` | Xóa tài khoản |
| `building.approved` | Duyệt tòa nhà |
| `building.rejected` | Từ chối tòa nhà |

## Acceptance criteria

- [ ] **Given** admin mở `/admin/audit-logs`, **then** thấy bảng mới nhất trước, 20 dòng/trang.
- [ ] **Given** chọn filter "Khóa tài khoản" + khoảng ngày, **then** URL cập nhật query, bảng chỉ còn dòng phù hợp; reload trang vẫn giữ filter.
- [ ] **Given** chọn ngày "từ" sau ngày "đến", **then** form báo lỗi ngay, không gọi API.
- [ ] **Given** bấm dòng `building.rejected`, **then** drawer hiện "Ghi chú: …" đúng `metadata.note`.
- [ ] **Given** bấm dòng `user.updated`, **then** drawer hiện danh sách field đã sửa bằng tiếng Việt.
- [ ] **Given** không có kết quả, **then** hiện trạng thái rỗng kèm nút xóa bộ lọc.
- [ ] **Given** API lỗi, **then** hiện thông báo lỗi + nút Thử lại.
- [ ] Bấm liên kết đối tượng mở đúng trang chi tiết user/tòa.
- [ ] Đọc được ở chiều rộng điện thoại (bảng cuộn trong khung, trang không cuộn ngang).

## Definition of Done

- [ ] Không viết file test. `npm run build`, `npm run lint`, `npm run i18n:check` pass.
- [ ] Ảnh chụp: danh sách, filter, drawer chi tiết, trạng thái rỗng, đính kèm PR.
- [ ] Đã nối API thật trước khi đóng issue.
