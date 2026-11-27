# P13-16 — BE: Báo cáo vi phạm

**Trạng thái:** 🔵 In review (PR: Identity-Service #52, api-doc #83, api-gateway #12)
**Người phụ trách (đề xuất):** `huynhtiennhat0403`
**Người review:** `baoduong17`
**Ước lượng:** 2 points
**Phụ thuộc:** P13-15 (cùng chỗ sửa media purpose và luồng khóa/mở khóa; làm sau để tránh conflict)
**Repo / branch:** `Identity-Service`, `api-docs` · `feature/p13-16-user-report`
**Issue tổng:** [P13-11](P13-11-report-and-appeal-deferred.md) · Quyết định: P13-D109

## Mục tiêu

Người dùng báo cáo được một tài khoản khác. Admin có hàng chờ báo cáo để làm căn cứ, rồi chọn "Bỏ qua" hoặc "Khóa tài khoản".

## Hiện trạng

- Admin khóa qua `POST /users/:userId/lock` (`UserLockCommandHandler`), lý do là chuỗi tự do. P13-09 thêm 6 gợi ý lý do ở FE.
- Chưa có nơi nào lưu báo cáo từ người dùng.

## Phạm vi

### Domain + persistence
- Enum `ViolationCategory`, gồm 6 loại theo P13-09 và `other`:
  - `fraud`
  - `fake_listing`
  - `harassment`
  - `spam`
  - `impersonation`
  - `inappropriate_content`
  - `other`
- Entity `UserReport`:
  - `id`, `reporterId`, `reportedUserId`
  - `category`
  - `description`: bắt buộc, 10–1000 ký tự
  - `evidenceMediaIds`: tối đa 3
  - `contextType`: không bắt buộc, `conversation | contract | other`
  - `contextId`: không bắt buộc
  - `status`: `pending | dismissed | actioned`
  - `resolutionNote`, `resolvedBy`, `resolvedAt`, `createdAt`
- Bảng `user_reports`, index `(reported_user_id, status)` và `(reporter_id, reported_user_id, status)`. Có migration.
- Đặt trong module `modules/moderation/` cùng khiếu nại (P13-15).

### Quy tắc
- Không báo cáo chính mình → `REPORT_SELF`.
- Không báo cáo admin, không báo cáo user không tồn tại hoặc đã xóa → `404 USER_NOT_FOUND` (không lộ đó là admin).
- Người gửi đang bị khóa: bị `ActiveUserGuard` chặn sẵn, **không** thêm `@AllowLocked()`.
- Cùng người gửi và cùng người bị báo cáo đã có báo cáo `pending` → `REPORT_ALREADY_PENDING`.
- Ảnh bằng chứng phải là media của chính người gửi, purpose `REPORT_EVIDENCE`.
- Chỉ xử lý được báo cáo `pending` → `REPORT_NOT_PENDING`.

### Xử lý của admin
- `dismiss`: báo cáo thành `dismissed`, `resolutionNote` không bắt buộc.
- `lock`: bắt buộc có `lockReason`. Trong 1 transaction:
  - khóa user bằng đúng các bước của `UserLockCommandHandler` (`user.lock()`, `recordLockPeriod`, outbox) trong transaction của handler xử lý báo cáo;
  - chuyển **mọi** báo cáo `pending` về người đó sang `actioned`.
  - Nếu user đã bị khóa từ trước thì chỉ đóng các báo cáo, không khóa lại.
- Audit: `report.submitted`, `report.dismissed`, `report.actioned`. Khi khóa thì có thêm audit `user.locked` như cũ.
- Không gửi thông báo cho người báo cáo trong đợt này.

### API
| Method | Path | Quyền |
|---|---|---|
| POST | `/api/v1/reports` | user đang hoạt động (`LANDLORD`, `TENANT`) |
| GET | `/api/v1/reports?status=&reportedUserId=&category=&pageNo=&pageSize=` | `ADMIN` |
| GET | `/api/v1/reports/:reportId` | `ADMIN` |
| POST | `/api/v1/reports/:reportId/resolve` | `ADMIN`, body `{ action: 'dismiss' \| 'lock', note?, lockReason? }` |

- Danh sách và chi tiết trả kèm tóm tắt người gửi và người bị báo cáo (`id`, `fullName`, `email`, `role`, `status`).
- ~~`pendingReportCount` trên danh sách user~~: bỏ để không đụng query danh sách user. FE lấy số báo cáo đang chờ của một user bằng `GET /reports?reportedUserId=&status=pending`.
- Gateway thêm prefix `/reports` cho Identity.

### Media
- Thêm `MediaPurpose.REPORT_EVIDENCE`: `ownerTypes: [USER]`, `PRIVATE`, chỉ ảnh, `canUpload: isSelf`, `canRead`: chính chủ (admin đọc được nhờ `MediaAccessPolicy`).

### api-docs
- Thêm path, schema, enum `ViolationCategory`, error code (`REPORT_SELF`, `REPORT_ALREADY_PENDING`, `REPORT_NOT_PENDING`).
- `npm run lint` và `npm run bundle`.

## Acceptance

- [ ] Landlord báo cáo tenant thành công. Gửi lần 2 khi còn `pending` → `409 REPORT_ALREADY_PENDING`.
- [ ] Báo cáo chính mình → `REPORT_SELF`. Báo cáo admin → `404`.
- [ ] Admin `dismiss` → báo cáo thành `dismissed`, user không bị khóa.
- [ ] Admin `lock` → user `LOCKED` với `lockReason` đã nhập, mọi báo cáo `pending` về user đó thành `actioned`, có thông báo `user.locked` như khóa thường.
- [ ] `GET /reports?reportedUserId=&status=pending` trả đúng các báo cáo đang chờ về một user.

## Definition of Done

- [ ] `npm run lint`, `npm run build`, `npm test` pass. Có unit test cho quy tắc `UserReport` trong `test/unit/user-reports/`.
- [ ] Ba lệnh grep kiểm tra dependency rule không in ra gì. Migration chạy và revert được.
- [ ] `api-docs` đã bundle.
