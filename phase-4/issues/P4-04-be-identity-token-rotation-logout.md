# P4-04 — Triển khai Token Rotation & Logout (Quản lý phiên)

**Status:** 🟡 Open  
**Assignee:** BE Dev  
**Stakeholders / Reviewers:** BE Lead, Mobile Lead  
**Created:** 2026-10-09  
**Due date:** 2026-10-13  
**Priority:** 🔴 High (Bảo đảm an toàn bảo mật và duy trì session)  

**Input:**
- P4-03 (Core Auth register/login & refresh token)
- `pm/phase-2/discovery/api-spec.md` (§2 Auth: API 3 `POST /auth/refresh`, API 4 `POST /auth/logout`)
- `pm/phase-3/discovery/decisions.md` (D55 §5.4.1: Lưu hash refresh token, Token reuse detection)

**Deliverables:**
- Use-case CQRS:
  - `RefreshTokenCommand` + `RefreshTokenCommandHandler`
  - `LogoutCommand` + `LogoutCommandHandler`
- Presentation:
  - `POST /api/v1/auth/refresh`
  - `POST /api/v1/auth/logout`
- Cơ chế Token Rotation & Token Reuse Detection hoàn chỉnh.

---

## 1. Chi tiết nghiệp vụ

### 1. Luồng `POST /api/v1/auth/refresh` (API 3)
* **Quyền:** `public` (Client gửi kèm cookie `refreshToken` hoặc body nếu là mobile client).
* **Nguyên tắc bảo mật:** Xoay vòng Refresh Token (Token Rotation): Mỗi lần xin access token mới, client PHẢI nhận một refresh token mới và refresh token cũ sẽ bị vô hiệu hóa ngay lập tức.
* **Xử lý:**
  1. Đọc `refreshToken` từ cookie (hoặc header/body).
  2. Băm chuỗi token này bằng SHA-256 để tìm trong bảng `refresh_tokens`.
  3. **Phát hiện tái sử dụng (Token Reuse Detection - Cực kỳ quan trọng):**
     - Nếu token tìm thấy có `revoked_at IS NOT NULL`: Cảnh báo rò rỉ token (kẻ tấn công hoặc client dùng lại token cũ đã xoay vòng).
     - **Hành động ngay:** Tìm toàn bộ các token có cùng `family_id` của user này và set `revoked_at = now()` (Force logout toàn bộ thiết bị trong chuỗi phiên này).
     - Trả về `401 TOKEN_REUSED`.
  4. **Happy path:**
     - Nếu token còn hạn (`expires_at > now()`) và chưa bị revoke (`revoked_at IS NULL`):
     - Đánh dấu token hiện tại `revoked_at = now()`.
     - Tạo một `refreshToken` mới với cùng `family_id`. Lưu hash của token mới vào DB.
     - Tạo `accessToken` mới (hạn 15 phút).
     - Cập nhật cookie `refreshToken` mới vào response.
* **Response:** Status `200 OK`.
  ```json
  {
    "statusCode": 200,
    "code": "TOKEN_REFRESHED",
    "data": {
      "accessToken": "eyJhbGciOi..."
    }
  }
  ```

---

### 2. Luồng `POST /api/v1/auth/logout` (API 4)
* **Quyền:** `public` (hoặc có kèm token).
* **Xử lý:**
  1. Đọc `refreshToken` từ request.
  2. Tìm bản ghi tương ứng trong `refresh_tokens` và cập nhật `revoked_at = now()`.
  3. Xóa cookie `refreshToken` ở client (`res.clearCookie('refreshToken')`).
* **Response:** Status `200 OK`.
  ```json
  {
    "statusCode": 200,
    "code": "LOGGED_OUT",
    "data": null
  }
  ```

---

## 2. Tiêu chí nghiệm thu (Definition of Done)
1. Gọi `POST /api/v1/auth/refresh` với cookie hợp lệ nhận được `accessToken` mới và `Set-Cookie` chứa `refreshToken` mới.
2. Kiểm tra DB thấy token cũ có `revoked_at != null`, và token mới có cùng `family_id`.
3. **Kiểm thử kịch bản Hack (Token Reuse):** Dùng lại token cũ vừa bị xoay vòng để gọi lại `refresh`:
   - Phải nhận mã lỗi `401 TOKEN_REUSED`.
   - Toàn bộ các token thuộc `family_id` đó trong DB đều bị set `revoked_at != null`.
4. Gọi `POST /api/v1/auth/logout` làm sạch cookie và revoke token thành công.
