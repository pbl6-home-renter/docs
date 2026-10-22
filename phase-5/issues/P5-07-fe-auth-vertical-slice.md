# P5-07 — Tích hợp Auth vertical slice

**Assignee:** FE Lead + FE Intern  
**Priority:** Critical  
**Estimate:** 13 pts · 30–45h  
**Phụ thuộc:** P5-01 đến P5-06  
**Trạng thái:** Open

## Bối cảnh

Đây là task tích hợp cuối của batch. Intern thực hiện theo contract table của P5-01; FE Lead review payload/response/security trước khi merge. Không coi UI chạy được với mock là hoàn thành.

## Mục tiêu

Thay thế Auth mock bằng API integration thật cho các endpoint đã được contract xác nhận.

## Phạm vi endpoint

- `POST /auth/register`.
- `POST /auth/login`.
- `GET /me`.
- `POST /auth/password-reset-requests`.
- `POST /auth/password-resets`.
- `PUT /me/password` nếu nằm trong Auth contract đã chốt.
- `POST /auth/refresh` và `POST /auth/logout` chỉ triển khai khi transport không-cookie đã được `api-docs` công bố và API owner xác nhận.

## Việc cần làm

- Define Auth request/response types theo đúng file `$ref`.
- Tạo Auth API adapters.
- Tạo Auth query/mutation hooks dùng P5-05.
- Cập nhật login/register page từ mock sang mutation thật.
- Hoàn thiện forgot/reset password page thay cho placeholder.
- Dùng `/me`, không dùng `/users/me` nếu contract công bố `/me`.
- Cập nhật Zustand auth state với profile/access token đúng response.
- Hydrate profile khi app khởi động nếu session state hiện tại cho phép.
- Cập nhật route guard theo trạng thái loading/error/profile.
- Thêm toàn bộ Auth success/error code vào i18n.

## Refresh/logout blocker

Nếu `api-docs` vẫn yêu cầu `RefreshCookie`, member phải:

1. Ghi rõ endpoint và security scheme trong PR.
2. Đánh dấu refresh/logout là `Blocked`.
3. Không thêm `withCredentials`, cookie storage hoặc body/header tự nghĩ ra.
4. Hoàn thành phần Auth không bị block và báo FE Lead/API owner.

## Ngoài phạm vi

- Building, Room, Contract, Billing, Payment.
- Cursor pagination.
- Đổi API contract trong PR FE.
- Tự thiết kế refresh-token protocol mới.

## Definition of Done

- Login/register không còn mock user hoặc mock token.
- Request/response match `api-docs` và có link contract trong PR.
- Profile dùng đúng endpoint và giữ đủ required/nullable field.
- `202`/`204` được xử lý đúng, không giả định response luôn có JSON `data`.
- Toast/inline error dùng API code + i18n, không dùng raw message.
- Refresh/logout được ghi rõ Done hoặc Blocked, không im lặng bỏ qua.
- `npm run build`, `npm run lint`, `npm run test` pass.
- Có evidence manual cho login, register, profile, password reset và route guard.
