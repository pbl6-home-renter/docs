# P5-03 — Chuẩn hóa Axios API client theo contract

**Assignee:** FE Intern  
**Priority:** High  
**Estimate:** 5 pts · 10–14h  
**Phụ thuộc:** P5-01, P5-02  
**Trạng thái:** Open

## Bối cảnh

Axios hiện là điểm dùng chung của toàn FE. Đây là nơi dễ làm sai envelope, 204 hoặc security nếu member chỉ test một endpoint thành công.

## Mục tiêu

Đảm bảo API client xử lý đúng transport được công bố trong `api-docs`, không tự thêm behavior ngoài contract.

## Việc cần làm

- Giữ base URL theo environment và prefix `/api/v1`.
- Gắn Bearer access token cho protected request.
- Unwrap success JSON envelope theo response thực tế.
- Giữ nguyên `statusCode` và `code` khi request lỗi.
- Không cố đọc `data` với response `204`.
- Không xử lý file/binary như JSON envelope.
- Không thêm `withCredentials`, không đọc hoặc ghi cookie.
- Không tự gọi refresh khi contract refresh hiện tại chưa có transport không-cookie được chốt.
- Đảm bảo không có vòng lặp retry 401.

## Ngoài phạm vi

- Không quyết định lại refresh-token protocol.
- Không sửa backend/API contract.
- Không tạo API adapter cho Auth trong task này.

## Deliverables

- Axios client đã chuẩn hóa.
- Test hoặc manual verification cho success envelope, error envelope, 204, public request và protected request.
- Ghi rõ case refresh/logout bị block nếu contract chưa thay đổi.

## Definition of Done

- Public request không gửi Authorization khi chưa có access token.
- Protected request gửi đúng Bearer token.
- 401 được trả về cho Auth layer xử lý, không retry vô hạn.
- Không có cookie handling trong FE.
- `npm run build` và `npm run lint` pass.
