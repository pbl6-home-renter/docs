# P5-04 — Chuẩn hóa error/success code và i18n

**Assignee:** FE Intern  
**Priority:** High  
**Estimate:** 3 pts · 6–8h  
**Phụ thuộc:** P5-01, P5-02  
**Trạng thái:** Open

## Bối cảnh

Backend contract dùng `code` ổn định để client rẽ nhánh và hiển thị. FE không được lấy raw `message` làm text UI vì message không phải contract hiển thị và có thể không tồn tại.

## Mục tiêu

Xây dựng một cách duy nhất để hiển thị success/error bằng API code và bản dịch.

## Phạm vi

- Helper lấy `code` từ error response.
- Helper lấy validation code để form hiển thị inline.
- Fallback translation cho code chưa biết.
- Auth success/error translations trong `en/auth.json` và `vi/auth.json`.
- Common error translations trong `common.json` nếu code dùng chung.
- Cơ chế tắt global error toast cho form cần hiển thị inline.
- Success toast theo success code.

## Quy tắc bắt buộc

- Không hiển thị raw backend `message`.
- Không tự đổi `INVALID_CREDENTIALS` thành code khác.
- Không map một HTTP status thành một message nếu OpenAPI đã khai báo error code cụ thể.
- Chỉ thêm code đã đọc từ Auth contract; module khác để task sau.

## Deliverables

- Error/success translation keys cho toàn bộ Auth code được dùng.
- Helper dùng được từ Query/Mutation layer và Auth form.
- Bằng chứng kiểm tra cả locale `en` và `vi`.

## Definition of Done

- Toast và inline error đều lấy text qua i18n.
- Code không có bản dịch dùng fallback đã dịch, không lộ raw code/message.
- Không làm tăng lỗi i18n ngoài các dynamic-key warning đã được ghi nhận.
