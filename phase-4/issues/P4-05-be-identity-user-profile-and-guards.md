# P4-05 — Triển khai Guards, User Profile & Đổi mật khẩu

**Status:** 🟡 Open  
**Assignee:** BE Dev  
**Stakeholders / Reviewers:** BE Lead, Mobile Lead, FE Lead  
**Created:** 2026-10-09  
**Due date:** 2026-10-14  
**Priority:** 🔴 High (Mobile/FE cần ngay để hiển thị User Profile & check quyền)  

**Input:**
- P4-03 (Core Auth & JWT generation)
- `pm/phase-2/discovery/api-spec.md` (§3 User: API 7 `GET /me`, API 8 `PATCH /me`, API 9 `PUT /me/password`)
- `pm/phase-2/discovery/decisions.md` (D39: payoutAccount cho Landlord VietQR)

**Deliverables:**
- Infrastructure & Security Guards:
  - `JwtAuthGuard` & `JwtStrategy`
  - `RolesGuard` & Decorator `@Roles('landlord', 'tenant', 'admin')`
  - Decorator `@CurrentUser()` trích xuất user profile từ request
- Use-cases CQRS:
  - `GetMeQuery` + Handler
  - `UpdateMeCommand` + Handler
  - `ChangePasswordCommand` + Handler
- Presentation (`UserController`):
  - `GET /api/v1/me`
  - `PATCH /api/v1/me`
  - `PUT /api/v1/me/password`

---

## 1. Chi tiết nghiệp vụ

### 1. Guards & Decorators
- [ ] `JwtStrategy`: Giải mã Bearer token từ header `Authorization: Bearer <token>`. Verify chữ ký và hạn dùng. Gán user info vào `request.user`.
- [ ] `@CurrentUser()`: Custom parameter decorator để controller lấy thông tin:
  ```typescript
  @Get('me')
  @UseGuards(JwtAuthGuard)
  async getMe(@CurrentUser() user: AuthenticatedUser) { ... }
  ```
- [ ] `RolesGuard`: So sánh `user.role` với role được khai báo tại `@Roles(...)`. Nếu không khớp trả `403 FORBIDDEN`.

---

### 2. Luồng `GET /api/v1/me` (API 7)
* **Quyền:** `tenant`, `landlord`, `admin`
* **Xử lý:**
  - Lấy thông tin user hiện tại từ DB theo `request.user.id`.
  - Nếu `role === 'landlord'`: JOIN với bảng `landlord_profiles` để lấy thông tin `payoutAccount` (gồm 3 trường: `bankCode`, `accountNumber`, `accountName`).
* **Response:** Status `200 OK`.
  ```json
  {
    "statusCode": 200,
    "code": "USER_PROFILE_FETCHED",
    "data": {
      "id": "uuid",
      "name": "Lê Văn An",
      "email": "lan@example.com",
      "phone": "0901234567",
      "role": "landlord",
      "status": "active",
      "payoutAccount": {
        "bankCode": "970436",
        "accountNumber": "1234567890",
        "accountName": "LEVANAN"
      }
    }
  }
  ```

---

### 3. Luồng `PATCH /api/v1/me` (API 8)
* **Quyền:** `tenant`, `landlord`, `admin`
* **Request Body:**
  ```json
  {
    "name": "Lê Văn An Mới",
    "phone": "0909999888",
    "payoutAccount": { // Bắt buộc gửi đủ 3 trường nếu là landlord muốn cập nhật tài khoản nhận tiền
      "bankCode": "970422",
      "accountNumber": "9876543210",
      "accountName": "LEVANAN"
    }
  }
  ```
* **Lưu ý nghiệp vụ:**
  - `email` và `role` là **bất biến**, KHÔNG được phép sửa qua endpoint này.
  - Nếu sửa `phone`: kiểm tra số mới không bị trùng với user khác (`409 PHONE_ALREADY_EXISTS`).
  - Nếu là landlord gửi `payoutAccount`: phải gửi đủ cả 3 trường `bankCode`, `accountNumber`, `accountName`. Cập nhật vào bảng `landlord_profiles`.

---

### 4. Luồng `PUT /api/v1/me/password` (API 9)
* **Quyền:** `tenant`, `landlord`, `admin`
* **Request Body:**
  ```json
  {
    "currentPassword": "OldPassword123!",
    "newPassword": "NewPassword456!",
    "confirmPassword": "NewPassword456!"
  }
  ```
* **Xử lý:**
  - Kiểm tra `newPassword === confirmPassword`.
  - So khớp `currentPassword` với hash hiện tại trong DB. Nếu sai trả `400 INVALID_CURRENT_PASSWORD`.
  - Hash `newPassword` và lưu vào DB.
  - Thu hồi (revoke) toàn bộ các refresh token đang active của user này trong bảng `refresh_tokens` để bắt đăng nhập lại trên các thiết bị khác.
* **Response:** Status `200 OK`, `code: "PASSWORD_CHANGED"`.

---

## 2. Tiêu chí nghiệm thu (Definition of Done)
1. Gọi `GET /me` không có token trả về `401 UNAUTHORIZED`.
2. Gọi `GET /me` với token hợp lệ:
   - Tenant: Nhận profile, `payoutAccount` là `null` hoặc không có.
   - Landlord: Nhận đủ profile và `payoutAccount`.
3. Sửa thông tin thành công bằng `PATCH /me`.
4. Đổi mật khẩu thành công bằng `PUT /me/password`, dùng mật khẩu mới đăng nhập lại thành công.
