# Rà soát sau demo Web Chat v1

> **Ngày rà soát:** 07/11/2026. User xác nhận Web Chat hiện demo ổn; các lỗi gửi chậm, cache realtime và toast đã được xử lý/commit trước lượt rà soát này. Notification inbox và group management hiện đang được triển khai trong workspace FE; thay đổi chưa được commit/merge. Đây là trạng thái mã nguồn, không phải xác nhận tải production hay kiểm thử end-to-end mới.

## Trạng thái FE sau bước tiếp theo

- Đã có route `/chat` và `/chat/:id`, layout hai cột, danh sách/tìm kiếm hội thoại, mở direct/group, tạo nhóm.
- Đã có lịch sử cursor, gửi text với optimistic bubble/idempotent retry, unread/read cursor, Socket realtime và reconnect.
- Đã có toast tin chat với avatar người gửi, tên conversation, preview và điều hướng vào conversation khi click.
- Đã có hiển thị ảnh trong history và xem ảnh lớn; chưa có luồng gửi ảnh từ Web.
- Đang bổ sung trang `/notifications`: cursor inbox, all/unread filter, mark-one/all, deep link nội bộ, category preferences áp dụng cho push thiết bị và toast Web, unread dot và đồng bộ Socket.
- Đang bổ sung quản trị group: đổi tên/ảnh, thêm/xóa thành viên, đổi role và rời nhóm theo quyền Community.
- Các thay đổi Notification/group management chưa được build/lint/i18n kiểm tra trong trạng thái tài liệu này; cập nhật acceptance sau khi kiểm tra xong.

## Đối chiếu phạm vi đã chốt

| Quyết định | Hiện trạng | Việc còn lại |
|---|---|---|
| Inbox giữ business notification, đọc đồng bộ theo user, không xóa | Community có list, mark-one và mark-all; FE đang có inbox và Socket cache sync | Chạy build/lint/i18n và kiểm tra API qua Gateway |
| Preference theo `chat`, `invoice`, `issue`, mặc định bật; tắt category không gửi push/toast nhưng inbox vẫn lưu | Community GET/PUT và FE Socket bridge áp dụng preference đã có | Xác minh đủ 3 category và đồng bộ cache |
| Chuông web chỉ cần chấm unread; chưa có endpoint tổng unread notification | FE đang lấy trang unread đầu tiên để hiện dot | Kiểm tra dot sau mark-read/all và Socket sync |
| Group admin quản lý metadata/membership/role; system messages hiện trong history | Community endpoints đã có; FE đang có dialog quản lý group | Kiểm tra quyền, mutation, confirm, reload list/history và loading/error |
| Ảnh nhóm dùng `ownerType=conversation`, `purpose=conversation_avatar` | Identity, Community validator và FE policy/API đã được nối trong workspace | Kiểm tra upload → PATCH avatar và lỗi upload |
| Ảnh chat: upload trước với `ownerType=conversation`, message trỏ `mediaId`; mỗi message tối đa một ảnh | FE xem ảnh đã gửi được; chưa có composer upload/send image | Tách task P7-17 |
| Event nguồn quyết định recipients/nội dung; Community lưu và phân phối | Backend đã có inbox event consumer | Tích hợp publisher Invoice/Issue là backlog domain riêng, không thuộc Web inbox implementation |
| Forgot/reset password thuộc nghiệp vụ Identity; Community cung cấp SMTP transport dùng chung qua queue | Community mailer đã triển khai | Identity publisher/outbox integration nằm ngoài các task FE này |

## Trình tự đề xuất

1. **P7-15 — Notification inbox và preferences:** thay placeholder, mark-read/all-read, cursor load-more, cài đặt category cho push/toast và unread dot; nghe `notification:created` / `notification:read-state-updated`.
2. **P7-16 — Group management:** đổi tên/ảnh, thêm/xóa thành viên, đổi admin/member và rời nhóm; chỉ active admin thấy thao tác quản trị. System message hiện trong history như contract.
3. **P7-17 — Gửi ảnh từ Web:** presign upload theo conversation rồi gửi message ảnh, giữ một ảnh mỗi message.
4. **P7-18 — Kiểm chứng tích hợp:** hai user qua Gateway, tab/device khác, quyền thành viên, read sync, inbox và deep link.

P7-15/16 đang được triển khai trong workspace FE, chưa commit/merge. Sau khi build/lint/i18n pass, kiểm tra bằng tài khoản có quyền member/admin và xác minh API qua Gateway. P7-17/18 vẫn ở backlog; các task chưa có iteration không tự xếp vào It8.
