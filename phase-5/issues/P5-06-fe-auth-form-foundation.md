# P5-06 — Chuẩn hóa Auth form và validation

**Assignee:** FE Intern  
**Priority:** High  
**Estimate:** 5 pts · 10–14h  
**Phụ thuộc:** P5-04, P5-05  
**Trạng thái:** Open

## Bối cảnh

Form hiện tại còn mock và tự quản lý state. Trước khi nối API thật, request schema phải khớp DTO trong `api-docs`, đặc biệt là tên field và required/nullable semantics.

## Nguồn contract

- Auth request DTOs trong `api-docs/src/requests/auth/`.
- User password request DTO trong `api-docs/src/requests/users/`.
- Error codes được khai báo trên từng Auth path.

## Mục tiêu

Chuẩn hóa form layer để P5-07 chỉ cần gắn mutation, không phải sửa lại validation architecture.

## Phạm vi

- React Hook Form + Zod.
- Login: `identifier`, `password`, `rememberMe`.
- Register: `email`, `phone`, `password`, `name`, `role`.
- Password reset request/reset theo DTO thực tế.
- Change password nếu thuộc Auth scope hiện tại.
- Map API validation code vào form-level/field-level feedback phù hợp.
- Dùng `mutation.isPending` cho submit button.
- Chống submit trùng.

## Quy tắc

- Không gửi field ngoài DTO.
- Không đổi tên `identifier` thành `email` hoặc `phoneOrEmail` ở request adapter.
- Required, optional và nullable phải đọc từ OpenAPI; không suy ra từ UI.
- Không tạo mock token/mock user.

## Deliverables

- Form schemas và reusable form error mapping.
- Cập nhật Auth form component/page để nhận mutation state.
- Test validation tối thiểu cho required field, format và mismatch password.

## Definition of Done

- Form invalid không gọi API.
- Payload gửi lên khớp DTO OpenAPI.
- API error code được hiển thị bằng i18n.
- Không còn logic loading riêng bằng `useState` cho submit.
