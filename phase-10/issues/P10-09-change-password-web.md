# P10-09 — Cho người dùng đổi mật khẩu trong Web

**Loại:** Feature gap · **Ưu tiên đề xuất:** Medium · **Trạng thái:** 🟢 Done — code đã merge  
**Owner đề xuất:** `ThaiBao11125` · **Reviewer:** FE Lead / Identity owner · **Repo:** `fe`  
**Phụ thuộc:** `PUT /me/password` · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## Cập nhật triển khai 14/11/2026

[FE #37](https://github.com/pbl6-home-renter/fe/pull/37) đã merge. Còn kiểm tra thực tế mật khẩu hiện tại sai, 401 do hết phiên, đổi thành công, thu hồi phiên và đăng nhập lại qua Identity/Gateway.

## Bối cảnh và mục tiêu

Identity đã có `changeCurrentUserPassword` và OpenAPI đánh dấu released; FE đã có `authApi.changePassword`, schema và mutation hook nhưng chưa có component gọi hook, route settings là placeholder. Người dùng đã đăng nhập cần đổi mật khẩu và đăng nhập lại sau khi đổi thành công.

## Contract và xử lý session

`PUT /me/password` nhận `currentPassword`, `newPassword`, `confirmPassword`, trả 204. Sai mật khẩu hiện tại trả `401 USER_CHANGE_PASSWORD_INVALID_CURRENT`; API revoke toàn bộ refresh token kể cả phiên hiện tại sau khi đổi thành công. Phân biệt lỗi này với 401 do phiên hết hạn theo error code; không coi sai mật khẩu là thành công hoặc tự retry mutation.

## Các bước triển khai

1. Đối chiếu schema, DTO, mutation và interceptor 401 hiện có với `api-docs/src/paths/users/me-password.yaml`; xác định đường xử lý code sai mật khẩu không trigger refresh/logout nhầm. **Kiểm tra:** response 401 `USER_CHANGE_PASSWORD_INVALID_CURRENT` chỉ báo lỗi phù hợp, phiên vẫn có thể gọi API được phép.
2. Tạo form ở trang settings hoặc mục bảo mật có thể truy cập từ các role; dùng schema/hook hiện có, `PasswordInput`, i18n `vi/en`, kiểm tra mật khẩu xác nhận ở client. Không log hoặc lưu mật khẩu vào storage. **Kiểm tra:** thiếu field, format sai, xác nhận không khớp không gửi request.
3. Submit một lần, xử lý server error qua toast/interceptor theo quy ước. Sau 204 xóa form và session local theo flow auth hiện có, điều hướng login cùng thông báo đăng nhập lại; không phụ thuộc logout server còn refresh token. **Kiểm tra:** mật khẩu cũ không đăng nhập được, mật khẩu mới đăng nhập được, tab khác không refresh được.
4. Test 401/422/503, timeout, click liên tiếp, keyboard và mobile; chạy build/lint/i18n. Nếu interceptor cần sửa, kiểm tra hồi quy login/refresh và 401 thật.

## Acceptance

- User đăng nhập đổi được mật khẩu hợp lệ, được thông báo rõ và đưa về login sau 204; không còn giữ phiên client như thể refresh token còn hiệu lực.
- Sai mật khẩu hiện tại không tạo vòng refresh hoặc báo thành công; lỗi client inline và lỗi server qua toast đúng quy ước.
- Form truy cập được, có bản dịch hai ngôn ngữ và không ghi lộ password vào log, URL hoặc storage.
