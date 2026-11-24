# P11-04 — Identity: bảng audit log và ghi thao tác admin trên user

**Trạng thái:** 🟡 Open  
**Người phụ trách (đề xuất):** `huynhtiennhat0403`  
**Người review:** BE Lead  
**Ước lượng:** 3 points · khoảng 10 giờ  
**Phụ thuộc:** P11-01 (contract), P11-10 (decorator `@Audited` + port `AuditRecorder`)  
**Repo / branch:** `Identity-Service` · `feature/p11-04-audit-log-user-actions`  
**Quyết định áp dụng:** [P11-D92](../decisions.md#d92--admin-dashboard-và-audit-log)

## User story

> Là **admin**, tôi muốn **mọi lần admin khóa, mở khóa, sửa hoặc xóa tài khoản đều được ghi lại kèm người thực hiện và thời điểm**, để **truy vết được khi có khiếu nại "tại sao tài khoản tôi bị khóa"**.

## Mô tả

1. **Module mới `audit-log`** trong Identity (domain → application → infrastructure), theo `boilerplate/src/modules/sample`.
2. **Bảng `audit_logs`** (sinh bằng `migration:generate`):

   | Cột | Kiểu | Ghi chú |
   |---|---|---|
   | `id` | uuid PK | |
   | `actor_id` | uuid, nullable | admin thực hiện. **Không** đặt FK cứng tới `users` để còn giữ log khi user bị xóa |
   | `action` | varchar(100) | 1 trong 6 giá trị của P11-D92 |
   | `entity_type` | varchar(50) | `user` / `building` |
   | `entity_id` | uuid, nullable | |
   | `metadata` | jsonb, default `{}` | chỉ field trong allowlist |
   | `source_service` | varchar(30) | `identity` / `tenancy` |
   | `source_event_id` | uuid, nullable, **unique** | dùng cho P11-05 |
   | `occurred_at` | timestamptz | Thời điểm thao tác thực sự xảy ra; P11-05 lấy từ `reviewedAt` trong event |
   | `created_at` | timestamptz | Thời điểm database tạo dòng audit khi Identity ghi nhận |

   Index: `(created_at DESC)`, `(action, created_at)`, `(entity_type, entity_id)`, `(actor_id)`.
3. **Adapter `DbAuditRecorder`** (infrastructure của module `audit-log`) implement port `AuditRecorder` từ P11-10 và bind vào `AUDIT_RECORDER_DI_TOKEN`:
   - Có `context` → ghi bằng transaction đó; không có → tự mở transaction riêng.
   - **Lọc metadata theo allowlist của từng action** (bảng trong P11-D92), bỏ mọi key ngoài danh sách. Action không có trong danh sách → ném lỗi.
   - Có `sourceEventId` → `INSERT ... ON CONFLICT (source_event_id) DO NOTHING`.
   - `source_service = identity` mặc định.
4. **Gắn `@Audited` lên `execute()` của 4 command handler** có sẵn trong `src/modules/users/application/commands/`. Không viết code ghi audit thủ công trong thân handler.

   | Handler | `action` | `actorId` | `entityId` | `metadata` | `skipIf` |
   |---|---|---|---|---|---|
   | `user-lock` | `user.locked` | `cmd.adminId` | `cmd.userId` | `{ lockReason: cmd.lockReason }` | — |
   | `user-unlock` | `user.unlocked` | admin trong command | `cmd.userId` | — | — |
   | `user-update-admin` | `user.updated` | admin trong command | `cmd.userId` | `{ changedFields }` | `changedFields.length === 0` |
   | `user-delete` | `user.deleted` | admin trong command | `cmd.userId` | — | — |

   - `user-update-admin` hiện trả `User`. Cần để handler **trả thêm danh sách field thực sự thay đổi** (so giá trị trước/sau, không phải field có mặt trong request) để resolver `metadata`/`skipIf` dùng; controller vẫn trả response như cũ.
   - Command nào chưa mang `adminId` thì bổ sung từ `@CurrentUser()` ở controller.
5. **Ghi sau khi lệnh commit** (theo P11-D92): lệnh lỗi thì không ghi; ghi audit lỗi thì lệnh vẫn thành công và có `logger.error`.

## Acceptance criteria

- [ ] **Given** admin A khóa user B với lý do "Spam", **when** lệnh thành công, **then** có đúng 1 dòng `audit_logs` với `action = user.locked`, `actor_id = A`, `entity_type = user`, `entity_id = B`, `source_service = identity`, `metadata = {"lockReason": "Spam"}`.
- [ ] Cả 4 handler dùng `@Audited`; trong thân handler không có lời gọi ghi audit thủ công.
- [ ] **Given** resolver trả thêm key ngoài allowlist (vd `phone`), **then** key đó bị loại trước khi lưu.
- [ ] **Given** admin khóa một user đã bị khóa (lệnh trả lỗi nghiệp vụ), **then** không có dòng audit mới.
- [ ] **Given** admin sửa `role` và `fullName` của user, **then** `metadata = {"changedFields": ["fullName", "role"]}` và không chứa giá trị cũ/mới.
- [ ] **Given** admin gửi PATCH nhưng không field nào đổi, **then** không ghi audit.
- [ ] **Given** admin xóa user B, **then** dòng audit `user.deleted` vẫn tồn tại sau khi B bị xóa.
- [ ] Mở khóa ghi `user.unlocked` tương tự.
- [ ] Không có cột hay giá trị `metadata` nào chứa mật khẩu, hash, token, SĐT.
- [ ] Không có API sửa/xóa audit log.

## Definition of Done

- [ ] `migration:run` và `migration:revert` pass từ DB trống.
- [ ] Unit test cho allowlist `metadata` trong `DbAuditRecorder` và cho cách tính `changedFields` (đổi 2 field, không đổi field nào).
- [ ] `npm run build`, `npm run lint`, `npm test` pass; check dependency rule không in gì.
- [ ] Ảnh chụp câu SQL `SELECT * FROM audit_logs ORDER BY created_at DESC` sau khi chạy 4 thao tác, đính kèm PR.
