# P11-06 — Identity: API đọc audit log

**Trạng thái:** 🟡 Open  
**Người phụ trách (đề xuất):** `baoduong17`  
**Người review:** BE Lead  
**Ước lượng:** 2 points · khoảng 6 giờ  
**Phụ thuộc:** P11-04 (bảng `audit_logs`)  
**Repo / branch:** `Identity-Service` · `feature/p11-06-audit-log-read`  
**Quyết định áp dụng:** [P11-D92](../decisions.md#d92--admin-dashboard-và-audit-log)

## User story

> Là **admin**, tôi muốn **tìm nhật ký theo loại thao tác, đối tượng, người thực hiện và khoảng thời gian**, để **nhanh chóng tìm được ai đã khóa một tài khoản hay từ chối một tòa vào ngày nào**.

## Mô tả

- 2 query CQRS trong module `audit-log`: `audit-log-list` và `audit-log-detail`.
- Controller `audit-log.controller.ts`, `@Roles(UserRole.ADMIN)`:
  - `GET /audit-logs`: tham số theo contract P11-01 (`action`, `entityType`, `actorId`, `entityId`, `from`, `to`, `pageNo`, `pageSize ≤ 100`), sắp xếp `created_at DESC`, phân trang offset theo envelope chuẩn.
  - `GET /audit-logs/{auditLogId}`: trả thêm `metadata`.
- `actorName`: LEFT JOIN bảng `users` (cùng DB Identity). Actor đã bị xóa → `null`.
- Gateway đã route `/audit-logs` về Identity, không cần sửa gateway.

## Acceptance criteria

- [ ] **Given** có 30 dòng audit, **when** gọi `GET /audit-logs?pageSize=10&pageNo=2`, **then** trả 10 dòng thứ 11–20 theo thứ tự mới nhất trước, `pagination.totalItems = 30`, `totalPages = 3`.
- [ ] **Given** filter `action=user.locked`, **then** chỉ trả các dòng khóa user.
- [ ] **Given** filter `entityType=building&entityId=<id tòa>`, **then** trả lịch sử duyệt/từ chối của đúng tòa đó.
- [ ] **Given** `from` lớn hơn `to`, **then** `422 VALIDATION_FAILED`.
- [ ] **Given** `action` không thuộc enum, **then** `422 VALIDATION_FAILED`.
- [ ] **Given** actor đã bị xóa, **then** item vẫn trả về với `actorName = null`.
- [ ] **Given** id không tồn tại, **when** gọi chi tiết, **then** `404 AUDIT_LOG_NOT_FOUND`.
- [ ] **Given** token landlord/tenant, **then** `403`. Không có token → `401`.
- [ ] Response không chứa field nào ngoài contract (không lộ `source_event_id`).

## Definition of Done

- [ ] Unit test validation (`from > to`, enum sai, pageSize > 100).
- [ ] `npm run build`, `npm run lint`, `npm test` pass.
- [ ] `x-apidog-status` của 2 operation đổi sang `released` sau khi verify qua gateway.
- [ ] Export Apidog các case trên đính kèm PR.
