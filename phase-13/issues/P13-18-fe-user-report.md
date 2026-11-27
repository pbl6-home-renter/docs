# P13-18 — FE: Gửi báo cáo vi phạm và hàng chờ báo cáo

**Trạng thái:** 🔵 In review (PR: fe #72)
**Người phụ trách (đề xuất):** `ThaiBao11125`
**Người review:** PM/leader
**Ước lượng:** 2 points
**Phụ thuộc:** P13-16, P13-09 (dùng lại chip lý do khóa)
**Repo / branch:** `fe` · `feature/p13-18-user-report`
**Issue tổng:** [P13-11](P13-11-report-and-appeal-deferred.md) · Quyết định: P13-D109

## Mục tiêu

Landlord báo cáo được tenant hoặc người đang chat. Admin xem hàng chờ báo cáo và xử lý: bỏ qua, hoặc khóa tài khoản với lý do điền sẵn.

## Hiện trạng

- Chưa có UI báo cáo.
- Header chat: `features/chat/components/chat-window-header.tsx`. Danh sách và chi tiết tenant: `features/tenants`.
- Lock dialog có chip gợi ý lý do (P13-09) trong `features/users/components/admin/user-lock-dialog.tsx`.

## Phạm vi

### Dialog "Báo cáo vi phạm" (landlord)
- Component dùng chung `features/users/components/user-report-dialog.tsx`, nhận vào `reportedUserId` và context tùy chọn (`conversation` + id).
- Mở từ đâu:
  - menu của header chat **1-1** (không hiện ở chat nhóm hoặc bot);
  - trang hoặc menu hành động của tenant trong `features/tenants`.
- Form gồm:
  - Loại vi phạm: radio, 7 loại (6 loại của P13-09 + "Khác").
  - Mô tả: bắt buộc, 10–1000 ký tự.
  - Ảnh bằng chứng: tối đa 3, purpose `REPORT_EVIDENCE`.
- Thành công → toast "Đã gửi báo cáo. Admin sẽ xem xét." Lỗi `REPORT_ALREADY_PENDING` → "Bạn đã báo cáo người này, đang chờ xử lý."

### Hàng chờ báo cáo (admin)
- Thêm menu "Báo cáo vi phạm" và trang `DataTable`, lọc theo trạng thái (mặc định `pending`) và loại vi phạm.
- Dialog chi tiết gồm: người báo cáo, người bị báo cáo (link sang chi tiết user), loại, mô tả, ảnh, context.
- Hai hành động:
  - **Bỏ qua**: ghi chú không bắt buộc.
  - **Khóa tài khoản**: ô lý do điền sẵn theo loại vi phạm (dùng lại chuỗi i18n và chip của P13-09), admin sửa được, bắt buộc. Gọi `resolve` với `action: 'lock'`.
- Nếu người bị báo cáo đã bị khóa: ẩn nút khóa, thay bằng "Đóng báo cáo".
- Trang chi tiết user của admin: hiện số báo cáo đang chờ về user đó (`GET /reports?reportedUserId=&status=pending`), bấm vào thì mở hàng chờ lọc theo user đó. (BE không trả `pendingReportCount` trên danh sách user, xem P13-16.)

### i18n
- Chuỗi mới trong `vi`/`en`. Tên loại vi phạm đặt cạnh các chip của P13-09 để dùng chung.

## Acceptance

- [ ] Landlord mở chat 1-1 → menu có "Báo cáo vi phạm". Chat nhóm thì không có.
- [ ] Gửi báo cáo kèm ảnh → toast thành công. Gửi lại → báo đang chờ xử lý.
- [ ] Admin thấy báo cáo, "Bỏ qua" → báo cáo biến khỏi tab `pending`.
- [ ] Admin "Khóa tài khoản" → lý do đã điền sẵn, user bị khóa, mọi báo cáo về user đó đóng lại.
- [ ] Trang chi tiết user hiện số báo cáo đang chờ và link sang hàng chờ đã lọc.

## Definition of Done

- [ ] `npm run build`, `npm run lint`, `npm run i18n:check` pass. Không viết file test.
- [ ] Ảnh chụp dialog báo cáo và hàng chờ admin trong PR.
