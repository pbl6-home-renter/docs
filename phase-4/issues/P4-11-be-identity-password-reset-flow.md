# P4-11 — Triển khai Luồng Quên mật khẩu & Đặt lại mật khẩu (Password Reset Flow)

**Status:** 🟡 Open  
**Assignee:** BE Dev  
**Stakeholders / Reviewers:** BE Lead, PM, FE Lead, Mobile Lead  
**Created:** 2026-10-11  
**Due date:** 2026-10-15  
**Priority:** 🔴 High (Nghiệp vụ xác thực thiết yếu trước khi phát hành)  

**Input:**
- Đặc tả API: `pm/phase-2/discovery/api-spec.md` (§2 Auth: API 5 `POST /auth/password-reset-requests`, API 6 `POST /auth/password-resets`)
- Quy ước API: `pm/phase-2/discovery/api-conventions.md` (§1 Response Wrapper, §4 Token Security, §10 Error Handling)
- Request & Response DTOs chuẩn từ `api-docs`:
  - `api-docs/src/requests/auth/request-password-reset-request-dto.yaml`
  - `api-docs/src/requests/auth/password-reset-request-dto.yaml`
  - `api-docs/src/responses/dtos/auth/request-password-reset-response-dto.yaml`
  - `api-docs/note.md` §Auth

**Deliverables:**
- Cập nhật Schema / Migration trong `identity_db` phục vụ lưu trữ token đặt lại mật khẩu và thời hạn hết hạn.
- CQRS Use-cases:
  - `RequestPasswordResetCommand` + `RequestPasswordResetCommandHandler`
  - `ResetPasswordCommand` + `ResetPasswordCommandHandler`
- Presentation:
  - Controller routing cho 2 endpoint `POST /auth/password-reset-requests` và `POST /auth/password-resets`
  - Validation DTOs mapping 1:1 theo contract trong `api-docs`
- Tích hợp dịch vụ MailService (hoặc console logger khi chạy local dev) phục vụ gửi đường dẫn đặt lại mật khẩu.

---

## 1. Chi tiết nghiệp vụ & Quy tắc kỹ thuật

### 1. Luồng yêu cầu đặt lại mật khẩu (`POST /auth/password-reset-requests` — API 5)
* **Quyền:** `public`
* **Contract DTO:** Xem `api-docs/src/requests/auth/request-password-reset-request-dto.yaml` và `api-docs/src/responses/dtos/auth/request-password-reset-response-dto.yaml`.
* **Quy tắc bảo mật Anti-Account-Enumeration:**
  - Để ngăn chặn việc dò quét tài khoản đang hoạt động, hệ thống **luôn trả về HTTP 200 OK cùng thông điệp phản hồi trung tính**, bất kể email người dùng có tồn tại trong hệ thống hay không.
* **Xử lý nghiệp vụ:**
  - Kiểm tra email trong hệ thống (chỉ áp dụng cho tài khoản chưa bị xóa `is_deleted = false` và không ở trạng thái khóa `status !== 'locked'`).
  - Nếu tìm thấy tài khoản:
    - Sinh mã token ngẫu nhiên bảo mật cao kèm thời gian hết hạn (TTL 15 phút).
    - Lưu thông tin token vào cơ sở dữ liệu (khuyến nghị lưu dạng băm an toàn).
    - Soạn nội dung email chứa đường dẫn đặt lại mật khẩu và gửi thông qua `MailService`.

### 2. Luồng đặt lại mật khẩu bằng token (`POST /auth/password-resets` — API 6)
* **Quyền:** `public`
* **Contract DTO:** Xem `api-docs/src/requests/auth/password-reset-request-dto.yaml`.
* **Xử lý nghiệp vụ:**
  - Xác thực tính hợp lệ của token:
    - Nếu token không tồn tại: trả về lỗi `400 INVALID_RESET_TOKEN`.
    - Nếu token đã quá hạn sử dụng: trả về lỗi `400 RESET_TOKEN_EXPIRED`.
  - Validate mật khẩu mới theo chuẩn bảo mật hệ thống.
  - Mã hóa mật khẩu mới bằng bcrypt và cập nhật vào cơ sở dữ liệu.
  - **Bảo mật token:** Vô hiệu hóa hoặc xóa token ngay sau khi đổi mật khẩu để đảm bảo token chỉ được sử dụng duy nhất một lần.
  - **Bảo mật phiên làm việc:** Thu hồi (revoke) toàn bộ các `refresh_tokens` đang hoạt động của người dùng để cưỡng chế đăng xuất khỏi mọi thiết bị đã đăng nhập trước đó.
* **Response:** Trả về `204 No Content` theo đúng đặc tả contract (không chứa JSON body).

---

## 2. Tiêu chí nghiệm thu (Definition of Done)

1. **Kiểm thử API 5 (Yêu cầu đặt lại):**
   - Gửi email không tồn tại trong hệ thống -> Trả về `200 OK` với thông điệp trung tính, không lộ thông tin lỗi 404.
   - Gửi email tồn tại -> Sinh token thành công, ghi nhận URL đặt lại mật khẩu trong log / mail service.
2. **Kiểm thử API 6 (Đặt lại mật khẩu):**
   - Gửi token sai hoặc token đã hết hạn -> Trả về mã lỗi 400 tương ứng.
   - Gửi token hợp lệ cùng mật khẩu mới -> Đổi mật khẩu thành công, trả về đúng mã HTTP `204 No Content`.
   - Sử dụng lại token vừa đổi thành công -> Trả về mã lỗi 400 do token đã bị vô hiệu hóa.
3. **Kiểm thử phiên làm việc sau khi đổi mật khẩu:**
   - Dùng mật khẩu cũ đăng nhập -> Bị từ chối với mã lỗi `401 INVALID_CREDENTIALS`.
   - Dùng mật khẩu mới đăng nhập -> Đăng nhập thành công, nhận token mới.
   - Toàn bộ refresh token cũ bị thu hồi, không thể dùng để xoay vòng token mới.
