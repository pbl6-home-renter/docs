# Phase 12 — Nhật ký quyết định

> Tiếp nối ID toàn cục từ Phase 11 (P11-D94). Luôn ghi tiền tố phase khi trích dẫn, ví dụ `P12-D95`. Không đánh lại hay tái sử dụng ID.

| ID | Ngày | Quyết định | Trạng thái |
|---|---|---|---|
| D95 | 2026-11-23 | Quy ước payload thông báo nghiệp vụ: `messageKey` + tham số chụp sẵn, `title`/`body` tiếng Việt đọc được | ✅ Accepted |
| D96 | 2026-11-23 | Web tự tính trang mở từ `messageKey`; `deepLink` chỉ là dự phòng; community chỉ log warning khi thiếu `messageKey` | ✅ Accepted |
| D97 | 2026-11-23 | Phạm vi thông báo Phase 12 và các mục loại khỏi phạm vi | ✅ Accepted |
| D98 | 2026-11-23 | Mỗi task thông báo do một BE member làm end-to-end: service nguồn → community → fe | ✅ Accepted |

## D95 — Quy ước payload thông báo nghiệp vụ

Chi tiết kỹ thuật: [`community-service/docs/notifications.md`](https://github.com/pbl6-home-renter/community-service/blob/main/docs/notifications.md).

- Mọi thông báo nghiệp vụ đi qua event `notification.requested`, ghi **outbox cùng transaction** với thay đổi nghiệp vụ.
- `data.messageKey` dạng `<aggregate>.<hành động>` (vd `building.approved`), kèm **đủ tham số để hiển thị lại** (tên tòa, tên phòng, kỳ hóa đơn, lý do…). Lịch sử thông báo được giữ vĩnh viễn nên không được dựa vào việc tra lại dữ liệu lúc hiển thị.
- `title`/`body` là **câu tiếng Việt đọc được**, dùng làm dự phòng cho mobile và client chưa dịch. Không dùng mã kiểu `USER_ACCOUNT_LOCKED_TITLE`.
- Giữ nguyên các `type`: `invoice`, `issue`, `system` (và `chat` ở cài đặt). Không thêm type mới trong phase này.
- Không gửi thông báo cho chính người thực hiện thao tác.

## D96 — Hiển thị và điều hướng phía Web

- Web dùng registry `messageKey → { i18n, tham số, route theo vai trò }` (`fe/src/features/notifications/utils/notification-registry.ts`). Backend không cần biết route của Web.
- Thứ tự chọn trang khi bấm: route của registry → `deepLink` cùng origin → ở lại (trang `/notifications`) hoặc mở `/notifications` (toast).
- Bản ghi cũ lưu mã thô trong `title` được dịch qua bảng `LEGACY_NOTIFICATION_CODES` của registry.
- community-service **không chặn** event thiếu `messageKey`, chỉ log warning, để producer cũ vẫn chạy cho tới khi P12-02/P12-03 xong.

## D97 — Phạm vi thông báo Phase 12

**Trong phạm vi:** khóa/mở tài khoản; luồng khóa landlord (tạm ngưng, cần quyết định, khôi phục, chấm dứt); hóa đơn phát hành/hủy; admin duyệt/từ chối tòa; tòa mới chờ duyệt (báo admin); hợp đồng kích hoạt/trả phòng; thành viên được thêm/liên kết/rời hợp đồng.

**Đã có, không làm lại:** sự cố (`issue.*`), ghép bạn (`match_request.*`), chat (chỉ push, có lịch sử riêng).

**Ngoài phạm vi:**

- Thông báo đổi trạng thái phòng: landlord chỉ chuyển `maintenance → available` khi phòng trống, không có người nhận; các chuyển trạng thái khác trùng sự kiện hợp đồng.
- Báo "phòng yêu thích đã trống", lọc lịch sử theo `type`, lưu kết quả gửi push/socket.
- Mobile dịch `messageKey` (mobile tiếp tục hiển thị `title`/`body`).

## D98 — Cách giao task

- Mỗi task do **một BE member** làm trọn: sửa service nguồn, kiểm tra bản ghi trong community, thêm mục registry + i18n `vi`/`en` ở fe, cập nhật bảng `messageKey` trong `docs/notifications.md`. PR riêng cho từng repo, ghi chung một issue.
- FE Lead review phần fe; owner community review nếu task đụng community.
