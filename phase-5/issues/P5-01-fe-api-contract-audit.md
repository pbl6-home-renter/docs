# P5-01 — Đọc và chốt contract FE cho Auth

**Assignee:** FE Intern, FE Lead review  
**Priority:** High / Blocker  
**Estimate:** 3 pts · 6–8h  
**Phụ thuộc:** Không có  
**Trạng thái:** Open

## Bối cảnh

FE hiện có application shell và một số Auth page dùng mock. Trước khi code API, member phải hiểu chính xác backend công bố gì. Không lấy UI hiện tại, database hoặc trí nhớ cá nhân làm nguồn định nghĩa API.

## Mục tiêu

Lập một bảng contract đủ rõ để người khác có thể viết type và API adapter mà không cần đoán.

## Nguồn bắt buộc

- `api-docs/src/openapi.yaml`
- `api-docs/src/paths/auth/register.yaml`
- `api-docs/src/paths/auth/login.yaml`
- `api-docs/src/paths/auth/refresh.yaml`
- `api-docs/src/paths/auth/logout.yaml`
- `api-docs/src/paths/auth/password-reset-requests.yaml`
- `api-docs/src/paths/auth/password-resets.yaml`
- `api-docs/src/paths/users/me.yaml`
- `api-docs/src/paths/users/me-password.yaml`
- Các request/response/schema được `$ref` từ các file trên

## Việc cần làm

Tạo bảng cho từng endpoint gồm:

- Method và path.
- Request body: field, kiểu, required/nullable, enum và validation.
- Success status, success `code`, response `data`.
- Error status và toàn bộ error `code` có thể trả về.
- Security scheme và header/body cần gửi.
- Quy tắc xử lý `204 No Content`.
- Ghi rõ field nào khác nhau giữa register/login/profile.

Đối chiếu thêm FE hiện tại để ghi mismatch, tối thiểu: mock token, login field, `/users/me` và các route Auth placeholder.

## Lưu ý blocker

`api-docs` hiện đang mô tả refresh/logout dùng `RefreshCookie`, trong khi định hướng FE là không dùng cookie. Không tự chọn body/header thay thế. Ghi mismatch và đánh dấu riêng hai flow này chờ API owner chốt.

## Ngoài phạm vi

- Không sửa code FE.
- Không sửa `api-docs`.
- Không thiết kế API mới.
- Không đọc và suy diễn model Building/Room/Contract.

## Deliverables

- Bảng contract trong PR description hoặc file discovery của task.
- Bảng mismatch FE–API.
- Danh sách blocker/câu hỏi cần FE Lead/API owner xác nhận.

## Definition of Done

- FE Lead có thể review và xác nhận từng dòng trong bảng bằng link tới `api-docs`.
- Không có field/route/error code nào được ghi theo phỏng đoán.
- Refresh/logout mismatch được ghi rõ, không có workaround.
