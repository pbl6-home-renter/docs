# Phase 12 — Nhật ký quyết định

> Tiếp nối ID toàn cục từ Phase 11 (P11-D94). Luôn ghi tiền tố phase khi trích dẫn, ví dụ `P12-D95`. Không đánh lại hay tái sử dụng ID.

| ID | Ngày | Quyết định | Trạng thái |
|---|---|---|---|
| D95 | 2026-11-23 | Quy ước payload thông báo nghiệp vụ: `messageKey` + tham số chụp sẵn, `title`/`body` là mã trong class constant | ✅ Accepted |
| D96 | 2026-11-23 | Web tự tính trang mở từ `messageKey`; `deepLink` chỉ là dự phòng; community chỉ log warning khi thiếu `messageKey` | ✅ Accepted |
| D97 | 2026-11-23 | Phạm vi thông báo Phase 12 và các mục loại khỏi phạm vi | ✅ Accepted |
| D98 | 2026-11-23 | Mỗi task thông báo do một BE member làm end-to-end: service nguồn → community → fe | ✅ Accepted |
| D99 | 2026-11-24 | Locked users may read their own notifications and receive notification Socket events; other business access remains blocked | ✅ Accepted |
| D100 | 2026-11-25 | Tài khoản bị khóa được phép xem thông tin chỉ đọc (phòng, hợp đồng, hóa đơn, tòa nhà) và thực hiện thanh toán; thao tác ghi/chỉnh sửa khác vẫn bị chặn | ✅ Accepted |
| D109 | 2026-11-27 | P12-05: Tenancy được gọi Identity trước transaction tạo tòa để lấy admin active; lỗi Identity không chặn tạo tòa | ✅ Accepted (PM) |

## D95 — Quy ước payload thông báo nghiệp vụ

Chi tiết kỹ thuật: [`community-service/docs/notifications.md`](https://github.com/pbl6-home-renter/community-service/blob/main/docs/notifications.md).

- Mọi thông báo nghiệp vụ đi qua event `notification.requested`, ghi **outbox cùng transaction** với thay đổi nghiệp vụ.
- `data.messageKey` dạng `<aggregate>.<hành động>` (vd `building.approved`), kèm **đủ tham số để hiển thị lại** (tên tòa, tên phòng, kỳ hóa đơn, lý do…). Lịch sử thông báo được giữ vĩnh viễn nên không được dựa vào việc tra lại dữ liệu lúc hiển thị.
- `title`/`body` là **mã** khai báo trong class constant của service nguồn (mẫu: `UserNotificationCodeConstant`). BE không viết câu hiển thị; client dịch theo `messageKey`.
- Giữ nguyên các `type`: `invoice`, `issue`, `system` (và `chat` ở cài đặt). Không thêm type mới trong phase này.
- Không gửi thông báo cho chính người thực hiện thao tác.

## D96 — Hiển thị và điều hướng phía Web

- Web dùng registry `messageKey → { i18n, tham số, route theo vai trò }` (`fe/src/features/notifications/utils/notification-registry.ts`). Backend không cần biết route của Web.
- Thứ tự chọn trang khi bấm: route của registry → `deepLink` cùng origin → ở lại (trang `/notifications`) hoặc mở `/notifications` (toast).
- `messageKey` chưa có trong registry thì Web hiển thị `title`/`body` như server gửi. Không ánh xạ ngược các bản ghi cũ thiếu `messageKey`.
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

## D99 — Notification access for locked accounts

- A locked account may open `/notifications`, list its own notifications, mark its own notifications as read, and read its notification preferences so the Web can decide whether to show a toast. Updating preferences and other business operations remain blocked.
- Community accepts a Socket connection bearing a `status=locked` access token for notification events only. It does not join the regular user room or a conversation room, and the chat handlers cannot act without an active user identity. Access tokens issued before the lock may still carry `status=active` for up to 15 minutes, as already documented for account locking.
- The exception supports P12-02's acceptance flow: an account lock notification remains visible after reloading `/notifications`. Authentication and recipient scoping remain required.

## D100 — Quyền truy cập chỉ đọc và thanh toán cho tài khoản bị khóa

- **Bối cảnh:** Khi tài khoản bị Admin khóa (`status = 'locked'`), người dùng bị chặn toàn bộ màn hình khiến họ không thể xem thông tin phòng đang thuê, hợp đồng, hóa đơn và không thể thanh toán tiền thuê/chi phí sinh hoạt.
- **Quyết định:**
  - **Cho phép đăng nhập:** Tài khoản bị khóa vẫn đăng nhập được để lấy token xác thực (chứa claim `status: 'locked'`).
  - **Xem thông tin ở chế độ chỉ đọc (Read-only):** Mở quyền truy cập bằng `@AllowLocked()` trên Backend và cấu hình route guard trên Frontend cho các thông tin liên quan của bản thân:
    - Hồ sơ cá nhân (`GET /me`).
    - Phòng & Tòa nhà đang thuê (`GET /me/room-hub`, `GET /rooms/:id`, `GET /me/rooms`, `GET /buildings/:id`).
    - Hợp đồng thuê (`GET /me/contracts`, `GET /contracts/:id`, `GET /contract-members`).
    - Hóa đơn (`GET /me/invoices`, `GET /invoices/:id`).
  - **Cho phép thực hiện thanh toán:** Endpoint xử lý thanh toán hóa đơn cho phép tài khoản bị khóa thực hiện giao dịch thanh toán đối với các hóa đơn hợp lệ mang trạng thái `issued` của chính mình.
  - **Chặn nghiêm ngặt các thao tác ghi khác:** 
    - Không cho phép cập nhật thông tin cá nhân (`PATCH /me`) hoặc đổi mật khẩu (`PUT /me/password`).
    - Không cho phép tạo/sửa hợp đồng, thêm/xóa thành viên.
    - Không cho phép tạo phòng, sửa phòng, tạo/hủy hóa đơn.
    - Frontend hiển thị banner cảnh báo tài khoản bị khóa và ẩn/vô hiệu hóa các nút chỉnh sửa/tạo mới.
- **Issues liên quan:** P12-09 (BE), P12-10 (FE).

## D109 — Tra cứu admin để thông báo tòa mới chờ duyệt

- PM đồng ý cho Tenancy gọi endpoint nội bộ của Identity trước transaction tạo tòa để lấy ID của tất cả admin đang `active`. Hiện hệ thống có một admin; đây là hiện trạng, không phải giới hạn của contract hoặc lý do để hardcode ID.
- Khi lấy được người nhận, Tenancy ghi `notification.requested` vào outbox cùng transaction tạo tòa. Nếu Identity lỗi, Tenancy vẫn tạo tòa, ghi warning và bỏ qua thông báo của lần tạo đó; không retry hoặc tự gửi bù.
- `api-doc` đã mô tả hành vi của `POST /buildings` theo quyết định này. Identity và Tenancy chốt đường dẫn/schema endpoint nội bộ trước khi triển khai và bổ sung contract đó vào `api-doc`.
