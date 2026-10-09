# P4-03 — Triển khai Auth Use-cases: Register & Login (CQRS)

**Status:** 🟡 Open  
**Assignee:** BE Dev  
**Stakeholders / Reviewers:** BE Lead, Mobile Lead  
**Created:** 2026-10-09  
**Due date:** 2026-10-12  
**Priority:** 🔴 High / Blocker (Mở khóa chức năng Login cho Mobile)  

**Input:**
- P4-01 (Boilerplate & conventions) & P4-02 (Schema `identity_db`)
- `pm/phase-2/discovery/api-spec.md` (§2 Auth: API 1 `POST /auth/register`, API 2 `POST /auth/login`)
- `pm/phase-2/discovery/api-conventions.md` (§1 Response Wrapper, §4 Token Cookies)

**Deliverables:**
- Domain Entities & Repository Interfaces: `UserEntity`, `UserRepository`.
- Use-case CQRS:
  - `RegisterCommand` + `RegisterCommandHandler`
  - `LoginCommand` + `LoginCommandHandler`
- Presentation:
  - `RegisterRequest`, `LoginRequest` (validation DTOs)
  - `AuthController` với các route:
    - `POST /api/v1/auth/register`
    - `POST /api/v1/auth/login`
- Cookie HttpOnly chứa Refresh Token được set vào response.

---

## 1. Chi tiết nghiệp vụ

### 1. Luồng `POST /api/v1/auth/register` (API 1)
* **Quyền:** `public`
* **Request Body:**
  ```json
  {
    "name": "Lê Văn An",
    "email": "lan@example.com",
    "phone": "0901234567",
    "password": "Password123!",
    "role": "tenant" // hoặc "landlord"
  }
  ```
* **Validation:**
  - `name`: 1-254 ký tự.
  - `email`: đúng định dạng RFC 5322.
  - `phone`: regex VN (`^0[0-9]{9}$` hoặc `^\+84[0-9]{9}$`).
  - `password`: tối thiểu 8 ký tự, gồm chữ hoa, chữ thường, số.
  - `role`: chỉ cho phép `tenant` hoặc `landlord`. **Nghiêm cấm** đăng ký role `admin` (trả lỗi `422 VALIDATION FAILED`).
* **Xử lý:**
  - Kiểm tra `email` hoặc `phone` đã tồn tại chưa (nếu trùng trả `409 EMAIL_ALREADY_EXISTS` hoặc `409 PHONE_ALREADY_EXISTS`).
  - Hash password bằng `bcrypt` (salt rounds: 10).
  - Tạo `UserEntity`. Nếu role là `landlord`, khởi tạo luôn `LandlordProfile` rỗng kèm theo.
  - Tạo JWT `accessToken` (hạn 15 phút, payload: `{ sub: user.id, role: user.role }`).
  - Sinh Refresh Token ngẫu nhiên (UUID cryptographically secure), lưu SHA-256 hash của token vào bảng `refresh_tokens`.
  - Set `refreshToken` vào Cookie (`HttpOnly`, `SameSite=Lax`, `Secure` trên production, maxAge: 7 ngày).
* **Response:** Status `201 Created`, header `Location: /api/v1/me`.
  ```json
  {
    "statusCode": 201,
    "code": "USER_REGISTERED",
    "data": {
      "accessToken": "eyJhbGciOi...",
      "user": {
        "id": "uuid",
        "name": "Lê Văn An",
        "email": "lan@example.com",
        "phone": "0901234567",
        "role": "tenant"
      }
    }
  }
  ```

---

### 2. Luồng `POST /api/v1/auth/login` (API 2)
* **Quyền:** `public`
* **Request Body:**
  ```json
  {
    "identifier": "lan@example.com", // hoặc "0901234567"
    "password": "Password123!",
    "rememberMe": true
  }
  ```
* **Xử lý:**
  - Tìm user theo `email` hoặc `phone` với điều kiện `is_deleted = false`.
  - Nếu không tìm thấy hoặc sai password: trả `401 INVALID_CREDENTIALS`.
  - Nếu tài khoản có `status === 'locked'`: trả `403 ACCOUNT_LOCKED`.
  - Sinh cặp `accessToken` và `refreshToken`, lưu hash của `refreshToken` vào DB.
  - Set Cookie `refreshToken`.
* **Response:** Status `200 OK`.
  ```json
  {
    "statusCode": 200,
    "code": "LOGIN_SUCCESS",
    "data": {
      "accessToken": "eyJhbGciOi...",
      "user": {
        "id": "uuid",
        "name": "Lê Văn An",
        "email": "lan@example.com",
        "phone": "0901234567",
        "role": "tenant"
      }
    }
  }
  ```

---

## 2. Tiêu chí nghiệm thu (Definition of Done)
1. Dùng Swagger UI (`/swagger`) hoặc Postman/Apidog gọi `POST /api/v1/auth/register` tạo tài khoản thành công.
2. Kiểm tra database thấy mật khẩu được mã hóa dạng hash (`$2b$10$...`), không lưu raw text.
3. Header response trả về `Set-Cookie: refreshToken=...; HttpOnly`.
4. Đăng nhập sai mật khẩu trả về đúng `401` với `code: "INVALID_CREDENTIALS"`.
5. Đăng ký trùng email hoặc SĐT trả về `409`.
