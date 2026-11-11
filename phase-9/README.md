# Phase 9 — Tích hợp event xuyên service

**Mục tiêu:** triển khai end-to-end các luồng từ producer thuộc service nguồn, qua RabbitMQ, tới tác động cuối ở consumer. Mỗi issue có một coder phụ trách; PM review contract event và PR.

## Quyết định và ranh giới

- Mỗi service dùng transactional outbox local; consumer dùng inbox/dedup. Delivery là at-least-once; không dùng distributed transaction hay 2PC.
- Luồng landlord lock dùng Saga choreography. Identity phát event tài khoản; Tenancy phản ứng và giữ trạng thái contract cùng grace period trong DB của mình; Community xử lý notification request.
- Mỗi consumer có durable queue riêng. Queue và routing key được chốt trong [P9-D83](decisions.md).
- Tenancy liên kết `tenantId=NULL` bằng so khớp chính xác số điện thoại đã chuẩn hóa; chỉ dùng phone trong Identity→Tenancy, không chuyển phone sang Community.
- Thêm category notification `system` cho thông báo Building/account/contract; Invoice dùng category `invoice` hiện có.
- IssueReport/Issue notification, Payment và hoàn cọc không nằm trong Phase 9. Issue là Stretch theo P6-D61 và code hiện chưa có producer module.
- Chưa gán ngày triển khai Phase 9. Xem [tracker issue](issues/README.md).

## Thứ tự issue

1. P9-01/P9-02: liên kết tenant và ContractMember (Minh Khai).
2. P9-05: bổ sung category notification `system` (Tiến Nhật).
3. P9-03/P9-04: Building/Contract context chat (Tiến Nhật).
4. P9-06/P9-07: thông báo account và landlord lock theo choreography (Minh Khai).
5. P9-08: notification khi phát hành Invoice (Tiến Nhật).
6. P9-09: smoke xuyên service, lưu bằng chứng (cả hai coder; PM review).

Mỗi issue implementation ghi routing key, queue, payload, tác động consumer và happy path xuyên broker. Giữ mỗi PR trong 3 points và khoảng 15 file; nếu vượt thì tách PR con nhưng giữ nguyên issue.
