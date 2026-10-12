# P4-12 — Triển khai Phân hệ Quản trị Người dùng cho Admin (Admin User Management)

**Status:** 🟡 Open  
**Assignee:** BE Dev  
**Stakeholders / Reviewers:** BE Lead, PM, FE Lead  
**Created:** 2026-10-11  
**Due date:** 2026-10-16  
**Priority:** 🔴 High (Enabler cho Admin Web Console quản lý & duyệt tài khoản)  

**Input:**
- Quyền & Bảo vệ: P4-05 (Guards `JwtAuthGuard`, `RolesGuard`, Decorator `@Roles('admin')`)
- Đặc tả API: `pm/phase-2/discovery/api-spec.md` (§3 User: API 10 đến 15)
- Quy ước API: `pm/phase-2/discovery/api-conventions.md` (§1 Response Wrapper & Pagination, §2 Permissions, §5 Validation, §10 Error Handling)
- Request & Response DTOs chuẩn từ `api-docs`:
  - `api-docs/src/requests/users/user-update-request-dto.yaml`
  - `api-docs/src/requests/users/user-lock-request-dto.yaml`
  - `api-docs/src/responses/dtos/users/user-list-response-dto.yaml`
  - `api-docs/src/responses/dtos/users/user-detail-response-dto.yaml`
  - `api-docs/src/responses/dtos/users/user-lock-response-dto.yaml`
  - `api-docs/src/responses/dtos/users/user-unlock-response-dto.yaml`
  - `api-docs/note.md` §User

**Deliverables:**
- CQRS Use-cases:
  - `GetUsersAdminQuery` + Handler (Tìm kiếm, bộ lọc role/status/q, phân trang offset chuẩn).
  - `GetUserDetailAdminQuery` + Handler (Xem chi tiết hồ sơ người dùng theo `userId`).
  - `UpdateUserAdminCommand` + Handler (Cập nhật thông tin cơ bản của người dùng).
  - `LockUserCommand` + Handler (Khóa tài khoản kèm lý do bắt buộc).
  - `UnlockUserCommand` + Handler (Mở khóa tài khoản về trạng thái `active`).
  - `DeleteUserCommand` + Handler (Xóa mềm tài khoản `is_deleted = true`).
- Presentation:
  - Routing Controller cho các endpoint API 10 đến 15.
  - Áp dụng `JwtAuthGuard` và `RolesGuard` với vai trò `admin` trên toàn bộ controller.
  - Validation DTOs ánh xạ theo đặc tả trong `api-docs`.

---

## 1. Chi tiết nghiệp vụ & Quy tắc kỹ thuật

> **Quy định phân quyền:** Toàn bộ các endpoint trong nhóm này chỉ cho phép vai trò `admin` truy cập. Mọi yêu cầu không có token hoặc token thuộc các vai trò khác (`tenant`, `landlord`) phải bị từ chối với mã lỗi `403 FORBIDDEN`.

### 1. `GET /api/v1/users` (Liệt kê & Tìm kiếm người dùng — API 10)
* **Contract DTO:** Xem `api-docs/src/responses/dtos/users/user-list-response-dto.yaml` và `api-docs/src/schemas/common/pagination-query-params.yaml`.
* **Xử lý:**
  - Hỗ trợ các tham số lọc: `filter[role]`, `filter[status]`, tìm kiếm từ khóa `filter[q]` (áp dụng tìm kiếm không phân biệt hoa thường theo `name`, `email`, hoặc `phone`).
  - Hỗ trợ phân trang offset (`page`, `limit`) và sắp xếp (`sort`, `order`).
  - Danh sách trả về không được chứa thông tin nhạy cảm (mật khẩu, khóa phiên).

### 2. `GET /api/v1/users/{userId}` (Chi tiết người dùng — API 11)
* **Contract DTO:** Xem `api-docs/src/responses/dtos/users/user-detail-response-dto.yaml`.
* **Xử lý:**
  - Lấy đầy đủ thông tin hồ sơ theo `userId`. Trường hợp tài khoản là chủ nhà (`role === 'landlord'`), trả kèm thông tin cấu hình tài khoản nhận tiền `payoutAccount` từ `landlord_profiles`.
  - Trả về `404 USER_NOT_FOUND` nếu định danh người dùng không tồn tại.

### 3. `PATCH /api/v1/users/{userId}` (Admin sửa thông tin người dùng — API 12)
* **Contract DTO:** Xem `api-docs/src/requests/users/user-update-request-dto.yaml`.
* **Quy tắc nghiệp vụ:**
  - Chỉ cho phép chỉnh sửa các trường thông tin cơ bản (`name`, `phone`, `email`).
  - Không cho phép thay đổi `role` hoặc `status` thông qua endpoint này (trạng thái tài khoản được quản lý độc lập qua API 13/14).
  - Kiểm tra tính duy nhất của `email` và `phone` trước khi cập nhật.

### 4. `POST /api/v1/users/{userId}/lock` (Khóa tài khoản — API 13)
* **Contract DTO:** Xem `api-docs/src/requests/users/user-lock-request-dto.yaml` và `api-docs/src/responses/dtos/users/user-lock-response-dto.yaml`.
* **Quy tắc nghiệp vụ:**
  - Yêu cầu cung cấp lý do khóa tài khoản (`lockReason`) bắt buộc.
  - Ngăn chặn Admin tự khóa tài khoản của chính mình.
  - Chuyển `status` sang `locked`, ghi nhận thời gian `lockedAt` và lý do `lockReason`.
  - Thu hồi (revoke) toàn bộ phiên làm việc `refresh_tokens` hiện tại của tài khoản bị khóa để chấm dứt quyền truy cập ngay lập tức.

### 5. `POST /api/v1/users/{userId}/unlock` (Mở khóa tài khoản — API 14)
* **Contract DTO:** Xem `api-docs/src/responses/dtos/users/user-unlock-response-dto.yaml` (không có request body).
* **Quy tắc nghiệp vụ:**
  - Chuyển `status` về `active`, xóa trắng `lockedAt` và `lockReason`.

### 6. `DELETE /api/v1/users/{userId}` (Xóa mềm người dùng — API 15)
* **Quy tắc nghiệp vụ:**
  - Ngăn chặn Admin tự xóa tài khoản của chính mình.
  - Thực hiện xóa mềm (`is_deleted = true`, gán `deletedAt = now()`).
  - Trả về `204 No Content` theo chuẩn quy ước API (không chứa JSON body).

---

## 2. Tiêu chí nghiệm thu (Definition of Done)

1. **Kiểm tra phân quyền truy cập:**
   - Người dùng có vai trò `tenant` hoặc `landlord` gọi vào nhóm API này đều nhận mã lỗi `403 FORBIDDEN`.
2. **Kiểm tra nghiệp vụ tra cứu danh sách:**
   - Bộ lọc theo vai trò và trạng thái hoạt động chính xác.
   - Tìm kiếm từ khóa theo tên, email hoặc số điện thoại trả về đúng kết quả.
   - Siêu dữ liệu phân trang phản ánh đúng số trang và tổng số bản ghi.
3. **Kiểm tra trạng thái khóa và mở khóa tài khoản:**
   - Tài khoản sau khi bị khóa không thể đăng nhập hoặc sử dụng token cũ để truy cập hệ thống.
   - Tài khoản sau khi được mở khóa có thể đăng nhập lại bình thường.
   - Admin tự thao tác khóa hoặc xóa chính mình bị hệ thống từ chối.
4. **Kiểm tra xóa mềm:**
   - Người dùng bị xóa không còn xuất hiện trong các truy vấn danh sách thông thường.
