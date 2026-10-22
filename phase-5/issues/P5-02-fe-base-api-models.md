# P5-02 — Xây dựng base API types đầy đủ

**Assignee:** FE Intern  
**Priority:** High  
**Estimate:** 5 pts · 10–14h  
**Phụ thuộc:** P5-01 đã được review  
**Trạng thái:** Open

## Bối cảnh

Các module sau sẽ dùng chung response envelope, error envelope và pagination. Nếu base type làm thiếu hoặc quá rộng, mỗi module sẽ tự xử lý một kiểu và khó match API.

## Mục tiêu

Triển khai base TypeScript types bám đúng schema thực tế trong `api-docs`, đủ dùng cho Auth và các module sau.

## Phạm vi

Trong `src/types/api.ts` hoặc cấu trúc tương đương, hoàn thiện:

- `ApiResponse<T>` cho success envelope.
- Error response theo đúng field contract công bố; không tự thêm `message`/`errors` nếu OpenAPI không có.
- HTTP status/code type nếu có lợi cho việc type-check.
- Offset pagination metadata đầy đủ theo schema thực tế.
- Offset pagination query params đúng tên field trong endpoint.
- Paginated response cho collection.
- Kiểu cho response `204 No Content`.
- Kiểu/utility cần thiết để phân biệt JSON response và file response nếu API client dùng chung cần đến.

## Quy tắc

- Chỉ offset pagination trong batch này.
- Không tạo `CursorPaginationMeta`, `cursor`, `nextCursor` hoặc cursor helper.
- Field required nhưng nullable phải được biểu diễn là required và nullable.
- Không biến tất cả DTO domain thành một `BaseEntity` client-side nếu contract endpoint không dùng cùng response.
- Không define Building/Room/Contract model ở task này.

## Deliverables

- Base types compile được.
- Comment/link tới schema OpenAPI tương ứng cho các type dễ nhầm.
- Cập nhật import hiện tại nếu type cũ không còn khớp.
- Test type/runtime nhỏ cho envelope và pagination nếu phù hợp.

## Definition of Done

- `npm run build` pass.
- Offset pagination có đủ field contract yêu cầu.
- Không còn cursor abstraction trong base types.
- FE Lead review xác nhận type không làm mất required/nullable field.
