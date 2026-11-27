# P13-17 — FE: Trang tài khoản bị khóa, form khiếu nại, hàng chờ khiếu nại

**Trạng thái:** 🔵 In review (PR: fe #72)
**Người phụ trách (đề xuất):** `ThaiBao11125`
**Người review:** PM/leader
**Ước lượng:** 2 points
**Phụ thuộc:** P13-15
**Repo / branch:** `fe` · `feature/p13-17-account-appeal`
**Issue tổng:** [P13-11](P13-11-report-and-appeal-deferred.md) · Quyết định: P13-D109

## Mục tiêu

Người bị khóa thấy rõ vì sao bị khóa và gửi được khiếu nại ngay trên web. Admin có hàng chờ khiếu nại để chấp nhận hoặc từ chối.

## Hiện trạng

- `fe/src/app/routes/protected-route.tsx:40`: user `LOCKED` bị `Navigate` về `ROUTES.FORBIDDEN` (`app/pages/forbidden-page.tsx`), một trang chung không có lý do khóa.
- Admin có `features/users/components/admin/user-lock-dialog.tsx` và `user-unlock-dialog.tsx`, chưa có màn khiếu nại.
- `features/notifications/utils/notification-registry.ts` đã có `user.locked` và `user.unlocked`.

## Phạm vi

### Trang `/account-locked` (người dùng)
- `protected-route.tsx`: user `LOCKED` → `ROUTES.ACCOUNT_LOCKED`, không đưa về `FORBIDDEN` nữa. Giữ nguyên các route chỉ đọc mà P12-09/P12-10 đã mở cho tài khoản bị khóa (nếu có).
- Trang này hiển thị:
  - Lý do khóa và thời điểm khóa (`GET /me`, trường mới `lockReason`, `lockedAt`).
  - Trạng thái khiếu nại (`GET /me/appeals/current`):
    - Chưa gửi: hiện form.
    - `pending`: "Đang chờ xử lý — thường xử lý trong 3 ngày làm việc", kèm ngày gửi.
    - `rejected`: lý do từ chối. Nếu `canSubmit = false` thì hiện "Bạn có thể gửi lại từ ngày …" (`nextSubmitAt`); đến ngày thì hiện lại form.
  - Nút đăng xuất.
- Form khiếu nại (react-hook-form + zod):
  - Lý do khóa: chỉ đọc.
  - Nội dung giải trình: bắt buộc, 10–2000 ký tự.
  - Đính kèm: tối đa 3 ảnh/PDF, upload qua `features/media` với purpose `APPEAL_ATTACHMENT`.
  - Email và số điện thoại liên hệ: không bắt buộc.
- Map error code `APPEAL_ALREADY_PENDING`, `APPEAL_COOLDOWN`, `ACCOUNT_NOT_LOCKED` sang thông điệp i18n.
- Khi nhận thông báo `user.unlocked` (realtime) hoặc người dùng tải lại trang: refetch `/me`. Nếu đã `ACTIVE` thì refresh token rồi chuyển về dashboard. Lý do: claim `status` trong JWT trễ tối đa 15 phút.

### Hàng chờ khiếu nại (admin)
- Thêm menu "Khiếu nại" và trang danh sách, dùng `DataTable` như các trang admin hiện có. Lọc theo trạng thái, mặc định `pending`.
- Dialog chi tiết gồm:
  - người gửi, lý do khóa, thời điểm khóa;
  - nội dung, file đính kèm (xem qua download URL), thông tin liên hệ;
  - nút "Chấp nhận" (xác nhận → mở khóa) và "Từ chối" (bắt buộc nhập lý do, ≤500 ký tự).
- Sau khi xử lý: invalidate query danh sách khiếu nại và query user tương ứng.
- Trang chi tiết user của admin (`features/users/pages/admin/user-detail-page.tsx`): nếu user có khiếu nại `pending` thì hiện badge hoặc link sang khiếu nại.

### Thông báo
- `notification-registry.ts`: thêm `appeal.rejected`, đích đến là `/account-locked`.
- i18n `vi`/`en` cho mọi chuỗi mới.

## Acceptance

- [ ] Đăng nhập bằng tài khoản bị khóa → vào `/account-locked`, thấy lý do và thời điểm khóa.
- [ ] Gửi khiếu nại có file đính kèm → trang chuyển sang trạng thái "Đang chờ xử lý".
- [ ] Admin thấy khiếu nại trong hàng chờ. Từ chối khi chưa nhập lý do thì nút bị chặn.
- [ ] Sau khi bị từ chối, người dùng thấy lý do và ngày được gửi lại.
- [ ] Admin chấp nhận → người dùng tải lại trang thì vào được app bình thường.

## Definition of Done

- [ ] `npm run build`, `npm run lint`, `npm run i18n:check` pass. Không viết file test.
- [ ] Ảnh chụp trang bị khóa (3 trạng thái) và hàng chờ admin trong PR.
