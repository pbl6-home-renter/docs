# P10-26 — API yêu cầu và phản hồi tìm bạn ở ghép

**Loại:** Backend · **Trạng thái:** ⏪ Deferred — matching là Stretch  
**Owner đề xuất:** BE Lead / người được giao · **Reviewer:** PM / API owner · **Repo:** service owner sau khi chốt, `api-docs`  
**Phụ thuộc:** P10-25, P10-11, P1-13 · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## Bối cảnh và contract

OpenAPI đang designing cho `GET/POST /match-requests` và `POST /match-requests/{id}/accept-request`, `reject-request`, `withdraw-request`; chưa thấy controller tương ứng trong các service đã rà. Là tenant tham gia matching, tôi muốn gửi và phản hồi lời mời theo quyền của mình. Không thể coi tên endpoint là đủ để chốt state machine hoặc notification.

## Triển khai sau khi được duyệt

1. Đối chiếu P1-13, P1-D28/D29 và OpenAPI; PM chốt state machine, ai gửi/nhận/rút, lặp request, account bị khóa, privacy và notification dependency. **Kiểm tra:** bảng state/action gồm happy path, action sai actor và retry.
2. Đồng bộ schema/API, áp dụng aggregate và persistence trong service owner; kiểm tra authorization và invariant trong transaction. **Kiểm tra:** requester không accept thay recipient, duplicate hoặc chuyển trạng thái sai được xử lý theo contract đã chốt.
3. Nếu notification được duyệt, dùng outbox/inbox hiện có với recipient do service nguồn xác định; không thêm notification trước khi contract được chốt. **Kiểm tra:** replay event không tạo tác động trùng.
4. Test các chuyển trạng thái, race, idempotency, privacy và pagination; build/lint/test, API docs lint/bundle, smoke qua Gateway.

## Acceptance

- Chỉ actor được phép gửi, chấp nhận, từ chối hoặc rút theo state machine được phê duyệt; trường hợp đồng thời và retry không làm trạng thái mâu thuẫn.
- Không phụ thuộc tenant thụ động phải tạo account; notification/AI ngoài phần được duyệt không được giả lập.
