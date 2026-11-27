# P13-15 — BE: Khiếu nại khóa tài khoản

**Trạng thái:** 🔵 In review (PR: Identity-Service #52, api-doc #83, api-gateway #12)
**Người phụ trách (đề xuất):** `huynhtiennhat0403`
**Người review:** `baoduong17`
**Ước lượng:** 3 points
**Phụ thuộc:** —
**Repo / branch:** `Identity-Service`, `api-docs` · `feature/p13-15-account-appeal`
**Issue tổng:** [P13-11](P13-11-report-and-appeal-deferred.md) · Quyết định: P13-D109

## Mục tiêu

Người bị khóa gửi được khiếu nại trong app. Admin chấp nhận (mở khóa ngay) hoặc từ chối (bắt buộc ghi lý do). Người dùng nhận kết quả qua thông báo trong app và email.

## Hiện trạng

- Khóa/mở khóa: `modules/users/application/commands/user-lock/` và `user-unlock/`. Cả hai đều chạy trong `unitOfWork.run`, ghi domain event vào outbox và audit bằng `@Audited`.
- `GET /users/me` có `@AllowLocked()` nhưng **không trả** `lockReason`/`lockedAt`. Các trường này chỉ có ở response admin (`user-get-detail-admin.response.dto.ts`).
- Thông báo trong app: mẫu `users/domain/events/user-account-notification-requested.event.ts` (có `messageKey`).
- Email: `auth/application/events/email-send-requested.event.ts`. Community đã consume event này.
- Media: `modules/media/domain/policies/media-purpose.policies.ts`. Route `presign-upload` và `complete-upload` chưa cho tài khoản bị khóa gọi.

## Phạm vi

### Domain + persistence
- Entity `AccountAppeal`:
  - `id`, `userId`
  - `lockedAt`, `lockReason`: snapshot lúc gửi; `lockedAt` dùng để xác định kỳ khóa
  - `content`: bắt buộc, 10–2000 ký tự
  - `attachmentMediaIds`: tối đa 3
  - `contactEmail`, `contactPhone`: không bắt buộc
  - `status`: `pending | accepted | rejected`
  - `rejectReason`, `reviewedBy`, `reviewedAt`, `createdAt`
- Bảng `account_appeals`, tạo bằng `npm run migration:generate -- name=CreateAccountAppeals`. Thêm index `(user_id, status)`.
- Đặt trong module mới `modules/moderation/` (dùng chung với P13-16), theo cấu trúc `boilerplate/src/modules/sample`.

### Quy tắc (domain/use case)
- Chỉ user đang `LOCKED` (đọc từ DB, không dựa vào claim JWT) mới gửi được. Nếu không → `ACCOUNT_NOT_LOCKED`.
- Đã có 1 khiếu nại `pending` → `APPEAL_ALREADY_PENDING`.
- Khiếu nại gần nhất có cùng `lockedAt` bị `rejected`, và `now < reviewedAt + 7 ngày` → `APPEAL_COOLDOWN`. Response lỗi kèm `nextSubmitAt`.
- Mọi file đính kèm phải là media của chính người gửi, đúng purpose `APPEAL_ATTACHMENT`, trạng thái đã upload xong.
- Từ chối mà thiếu `rejectReason` (1–500 ký tự) → lỗi validation.
- Chỉ xử lý được khiếu nại `pending` → `APPEAL_NOT_PENDING`.

### Mở khóa dùng chung
- Handler chấp nhận khiếu nại tự gọi `user.unlock()`, `recordUnlockPeriod` và ghi event vào outbox trong transaction của mình (UnitOfWork không lồng được transaction).
- **Chấp nhận khiếu nại**: trong 1 transaction, đổi khiếu nại sang `accepted` và gọi `UserUnlockService`.
- **Admin mở khóa trực tiếp** (`POST /users/:userId/unlock`): sau khi commit, `UserUnlockCommandHandler` phát event nội bộ `UserUnlockedByAdminEvent`; module moderation đóng khiếu nại `pending` thành `accepted` (best effort, transaction riêng). Nếu bước này lỗi, admin bấm chấp nhận sau cũng chỉ đóng khiếu nại mà không mở khóa lại.

### API
| Method | Path | Quyền |
|---|---|---|
| GET | `/api/v1/me/appeals/current` | `LANDLORD`, `TENANT`, `@AllowLocked()` |
| POST | `/api/v1/me/appeals` | `LANDLORD`, `TENANT`, `@AllowLocked()` |
| GET | `/api/v1/appeals?status=&userId=&pageNo=&pageSize=` | `ADMIN` |
| GET | `/api/v1/appeals/:appealId` | `ADMIN` |
| POST | `/api/v1/appeals/:appealId/accept` | `ADMIN` |
| POST | `/api/v1/appeals/:appealId/reject` | `ADMIN`, body `{ rejectReason }` |

- `GET .../current` trả `{ appeal | null, canSubmit, nextSubmitAt | null }`. Chỉ tính các khiếu nại thuộc kỳ khóa hiện tại.
- Danh sách cho admin trả kèm thông tin người gửi: `id`, `fullName`, `email`, `role`, `lockReason`, `lockedAt`. Sắp xếp `pending` cũ nhất lên đầu.
- Đường dẫn theo quy ước hiện có: route admin không có tiền tố `admin/` (giống `users`, `audit-logs`). Gateway thêm prefix `/appeals` cho Identity; `/me/appeals` đi theo prefix `/me` sẵn có.

### `GET /me`
- Thêm `lockReason` và `lockedAt` (null khi tài khoản không bị khóa).

### Media
- Thêm `MediaPurpose.APPEAL_ATTACHMENT`:
  - `ownerTypes: [USER]`, `PRIVATE`
  - định dạng: ảnh + PDF
  - `canUpload: isSelf`, `canRead`: chính chủ (admin đọc được nhờ `MediaAccessPolicy`)
- Thêm `@AllowLocked()` cho `POST /media/presign-upload` và `POST /media/:mediaId/complete-upload`. Trong use case presign: nếu actor đang bị khóa và purpose khác `APPEAL_ATTACHMENT` → `ACCOUNT_LOCKED` (giữ hành vi cũ cho mọi purpose khác).

### Audit, thông báo, email
- Audit bằng `@Audited`: `appeal.submitted`, `appeal.accepted`, `appeal.rejected`. Metadata gồm `appealId` và `rejectReason` (khi từ chối).
- **Thông báo trong app:**
  - Chấp nhận: thông báo `user.unlocked` có sẵn là đủ.
  - Từ chối: event mới với `messageKey: 'appeal.rejected'`, `data` gồm `appealId`, `rejectReason`, `nextSubmitAt`. Title/body dùng hằng số trong `UserNotificationCodeConstant` (theo `community-service/docs/notifications.md`).
- **Email**: dùng `EmailSendRequestedEvent` cho cả chấp nhận và từ chối. Nội dung tiếng Việt, kèm lý do từ chối và ngày được gửi lại.

### api-docs
- Thêm path, schema và error code: `ACCOUNT_NOT_LOCKED`, `APPEAL_ALREADY_PENDING`, `APPEAL_COOLDOWN`, `APPEAL_NOT_PENDING`.
- Thêm `lockReason`/`lockedAt` vào schema `GET /me`, thêm `APPEAL_ATTACHMENT` vào enum purpose.
- `npm run lint` và `npm run bundle`.

## Acceptance

- [ ] User bị khóa gửi được khiếu nại có 0–3 file đính kèm. Gửi lần 2 khi còn `pending` → `409 APPEAL_ALREADY_PENDING`.
- [ ] User đang hoạt động gửi khiếu nại → `ACCOUNT_NOT_LOCKED`.
- [ ] Admin từ chối không nhập lý do → `400`. Có lý do → user nhận thông báo `appeal.rejected` và email. Gửi lại trong 7 ngày → `APPEAL_COOLDOWN` kèm `nextSubmitAt`.
- [ ] Admin chấp nhận → user `ACTIVE`, có bản ghi kỳ khóa đã đóng, nhận thông báo `user.unlocked` và email.
- [ ] Admin mở khóa trực tiếp khi có khiếu nại `pending` → khiếu nại thành `accepted`.
- [ ] User bị khóa presign được `APPEAL_ATTACHMENT`, presign purpose khác vẫn `403 ACCOUNT_LOCKED`.
- [ ] `GET /me` của user bị khóa trả `lockReason`, `lockedAt`.
- [ ] Ba lệnh grep kiểm tra dependency rule (CLAUDE.md) không in ra gì.

## Definition of Done

- [ ] `npm run lint`, `npm run build`, `npm test` pass. Có unit test cho quy tắc của entity `AccountAppeal` (pending, cooldown, reject reason) trong `test/unit/account-appeals/`.
- [ ] Migration chạy được trên DB sạch, `migration:revert` hoạt động.
- [ ] `api-docs` đã bundle.
