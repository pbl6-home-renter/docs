# P13-19 — Mobile: Khiếu nại khóa tài khoản và báo cáo vi phạm

**Trạng thái:** ⏸ Blocked — repo `mobile` hiện mới có khung (`core-ui` base classes, `MainActivity` trống), chưa có lớp mạng, đăng nhập, push hay chat. Làm khi các nền tảng đó có.
**Người phụ trách (đề xuất):** Mobile (PM giao)
**Người review:** PM/leader
**Ước lượng:** 3 points (nếu vượt 3 points thì tách thành 2 PR: khiếu nại / báo cáo)
**Phụ thuộc:** P13-15, P13-16
**Repo / branch:** `mobile` · `feature/p13-19-report-and-appeal`
**Issue tổng:** [P13-11](P13-11-report-and-appeal-deferred.md) · Quyết định: P13-D109

## Mục tiêu

Trên `app-tenant` và `app-landlord`, người dùng có cùng hai luồng như web (P13-17, P13-18): người bị khóa xem lý do và gửi khiếu nại; người dùng báo cáo vi phạm từ chat. Hàng chờ của admin chỉ có trên web.

## Phạm vi

### Màn tài khoản bị khóa (cả 2 app)
- Khi `GET /me` trả `status = LOCKED` hoặc API trả `403 ACCOUNT_LOCKED`: chuyển sang màn "Tài khoản bị khóa". Màn này hiển thị:
  - lý do và thời điểm khóa;
  - trạng thái khiếu nại (`GET /users/me/appeals/current`) với cùng 3 trạng thái như P13-17: chưa gửi, đang chờ (kèm "thường xử lý trong 3 ngày làm việc"), bị từ chối (kèm lý do và ngày được gửi lại);
  - nút "Gửi khiếu nại" và nút đăng xuất.
- Màn form khiếu nại:
  - Lý do khóa: chỉ đọc.
  - Nội dung: bắt buộc, 10–2000 ký tự.
  - Đính kèm: tối đa 3, chọn ảnh hoặc PDF, upload qua flow presign có sẵn với purpose `APPEAL_ATTACHMENT`.
  - Email và số điện thoại liên hệ.
- Giữ nguyên các màn chỉ đọc mà P12-10 đã cho phép (nếu có). Màn bị khóa là điểm vào, không thay thế các màn đó.
- Nhận push `appeal.rejected` → mở màn bị khóa. Nhận `user.unlocked` → refresh token, vào lại màn chính.

### Báo cáo vi phạm
- Menu của màn chat 1-1 (cả 2 app) có "Báo cáo vi phạm". `app-landlord` có thêm mục này ở chi tiết tenant.
- Form gồm: loại vi phạm (7 loại), mô tả (10–1000 ký tự), tối đa 3 ảnh (`REPORT_EVIDENCE`). Xử lý lỗi `REPORT_ALREADY_PENDING`.

### Kỹ thuật
- Theo MVVM, XML Views, component dùng chung đặt trong `core-ui` khi cả 2 app cùng dùng.
- Chuỗi tiếng Việt trong `strings.xml`. Tên loại vi phạm và trạng thái khớp với web.

## Acceptance

- [ ] Tài khoản bị khóa mở app → thấy màn bị khóa có lý do.
- [ ] Gửi khiếu nại có ảnh → hiện trạng thái "Đang chờ xử lý". Admin từ chối trên web → app nhận push, thấy lý do và ngày được gửi lại.
- [ ] Admin chấp nhận → app vào lại màn chính sau khi refresh token.
- [ ] Từ chat 1-1 gửi được báo cáo; admin thấy báo cáo trên web.

## Definition of Done

- [ ] `./gradlew :app-landlord:assembleDebug` và `./gradlew :app-tenant:assembleDebug` pass.
- [ ] Video hoặc ảnh chụp 2 luồng trong PR.
