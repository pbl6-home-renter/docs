# Phase 11 — Nhật ký quyết định

> Tiếp nối ID toàn cục từ Phase 10 (P10-D91). Luôn ghi tiền tố phase khi trích dẫn, ví dụ `P11-D92`. Không đánh lại hay tái sử dụng ID.

| ID | Ngày | Quyết định | Trạng thái |
|---|---|---|---|
| D92 | 2026-11-21 | Admin dashboard tách 2 endpoint snapshot; audit log ghi thao tác admin, lưu ở Identity, giữ vĩnh viễn | ✅ Accepted |
| D93 | 2026-11-21 | VietQR: chỉ làm spike nghiên cứu các dịch vụ có sandbox, chưa triển khai | ✅ Accepted |
| D94 | 2026-11-21 | Không tạo task seed demo riêng: các thành viên đã tự seed dữ liệu | ✅ Accepted |

## D92 — Admin dashboard và audit log

**Thay thế:** blocker trong P10-10; phạm vi của P10-19, P10-20, P10-21, P10-22 chuyển sang P11-01 → P11-08.

### Dashboard

- **Tách 2 endpoint, mỗi service tự đếm dữ liệu của mình.** Không gọi chéo service, không có distributed query.
  - Identity: `GET /users/stats`, chỉ cho role `admin`. Đi qua prefix `/users` mà gateway đã route sẵn về Identity.
  - Tenancy: `GET /dashboard`, chỉ cho role `admin`. Gateway đã route `/dashboard` về Tenancy.
- **Snapshot tại thời điểm gọi:** bỏ query `from`/`to`, bỏ field `systemTransactionVolume` (Payment vẫn deferred theo P6-D61).
- FE gọi 2 endpoint song song. Một endpoint lỗi thì chỉ nhóm thẻ của endpoint đó hiện trạng thái lỗi kèm nút thử lại, nhóm còn lại vẫn hiển thị.

**Định nghĩa số liệu:**

| Field | Service | Cách tính |
|---|---|---|
| `totalUsers` | Identity | Tất cả bản ghi trong bảng `users`, mọi role |
| `byRole.admin` / `byRole.landlord` / `byRole.tenant` | Identity | Đếm theo `role` |
| `byStatus.active` / `byStatus.locked` / `byStatus.pendingVerification` | Identity | Đếm theo `status` |
| `totalBuildings` | Tenancy | Tòa `approved`, chưa xóa mềm (`is_deleted = false`) |
| `pendingApprovalBuildings` | Tenancy | Tòa `pending`, chưa xóa mềm |
| `rejectedBuildings` | Tenancy | Tòa `rejected`, chưa xóa mềm |
| `totalRooms` | Tenancy | Phòng chưa xóa mềm, thuộc tòa `approved` chưa xóa mềm |
| `roomsByStatus.available` / `.occupied` / `.maintenance` | Tenancy | Tách `totalRooms` theo `status` |
| `occupancyRate` | Tenancy | `occupied / totalRooms × 100`, kiểu **number**, làm tròn 1 chữ số thập phân; `totalRooms = 0` → `0` |
| `generatedAt` | Cả hai | Thời điểm server tính (ISO 8601) |

### Audit log

- **Nơi lưu:** Identity, bảng `audit_logs`. Gateway đã route `/audit-logs` về Identity.
- **Chỉ thêm mới (append-only):** không có API sửa hay xóa. **Giữ vĩnh viễn**, không có job dọn dẹp.
- **Chỉ ghi thao tác của admin:**

| `action` | `entityType` | Nguồn ghi | `actorId` |
|---|---|---|---|
| `user.locked` | `user` | Identity, `@Audited` trên lệnh khóa | admin gọi API |
| `user.unlocked` | `user` | Identity, `@Audited` trên lệnh mở khóa | admin gọi API |
| `user.updated` | `user` | Identity, `@Audited` trên `PATCH /users/{userId}` | admin gọi API |
| `user.deleted` | `user` | Identity, `@Audited` trên `DELETE /users/{userId}` | admin gọi API |
| `building.approved` | `building` | Identity consume event `building.approved` từ Tenancy | `reviewedBy` trong event |
| `building.rejected` | `building` | Identity consume event `building.rejected` từ Tenancy | `reviewedBy` trong event |

- **Không lưu:** mật khẩu, hash, token, OTP, số điện thoại, CCCD, số tài khoản ngân hàng, hay giá trị cũ/mới của field.
- **`metadata` là danh sách field được phép (allowlist):**
  - `user.updated`: chỉ tên các field đã đổi (`changedFields: ["role", "fullName"]`), không lưu giá trị.
  - `user.locked`: `lockReason` (lý do khóa admin nhập, API khóa đã có field này).
  - `user.unlocked`, `user.deleted`: không có metadata.
  - `building.approved` / `building.rejected`: `note` (ghi chú duyệt/từ chối của admin).
- **Event consume phải idempotent:** lưu `source_event_id` (unique), dùng inbox `processed_events` như các subscriber khác. Nhận lại cùng event không tạo bản ghi thứ hai.
- **Ngoài phạm vi:** đăng nhập thất bại, đổi/reset mật khẩu, thao tác của landlord/tenant, export file (`format` khác `json`).

### Cơ chế ghi (bổ sung 2026-11-21)

- **Decorator generic `@Audited` + port `AuditRecorder` đặt trong `boilerplate/src/shared`** (P11-10), copy sang các service. Decorator không biết bảng lưu trữ; mỗi service tự bind adapter. Identity bind `DbAuditRecorder` ghi vào `audit_logs` (P11-04).
- **Thao tác qua API (command handler): ghi sau khi lệnh commit.** Unit of Work truyền transaction context tường minh nên decorator không tham gia được transaction của lệnh. Chấp nhận đánh đổi: lệnh lỗi thì không ghi; riêng bước ghi audit lỗi thì lệnh vẫn thành công, có `logger.error`, và có thể mất log (hiếm gặp). Không sửa Unit of Work trong Phase 11.
- **Ghi từ event (consumer): gọi port trực tiếp kèm transaction của inbox**, không dùng decorator, để audit và `processed_events` cùng commit hoặc cùng rollback (P11-05).
- **Mở rộng sau này:** thêm hành động trong Identity thì thêm action + allowlist và gắn `@Audited`; service khác cần audit thì bind adapter gửi event `audit.recorded` qua outbox, Identity consume và lưu. Chưa làm trong Phase 11.
- **Lưu ý đồng bộ shared:** `src/shared` của các service đã lệch boilerplate; chỉ copy file trong thư mục `audit/`, không chép đè cả `src/shared`.

## D93 — VietQR chỉ làm spike sandbox

- `PUT /buildings/{buildingId}/vietqr-config` giữ trạng thái `designing`; **chưa triển khai** trong Phase 11.
- `leminhkhai345` làm spike P11-09: so sánh các dịch vụ **có sandbox/test mode** để đề xuất cho nhóm, phân tích flow, công nghệ, rủi ro và biện pháp.
- Spike không merge code vào `main`. Nếu muốn thử thì làm PoC trên branch riêng, dùng key sandbox.
- Kết quả spike là đầu vào để PM quyết định có mở lại P6-05 (ghi nhận thanh toán) hay retire API VietQR. Quyết định đó sẽ là một D-ID mới.

## D94 — Không tạo task seed demo

Các thành viên đã tự seed dữ liệu trên môi trường của mình. Không mở lại P6-07 dưới dạng task riêng trong Phase 11.
