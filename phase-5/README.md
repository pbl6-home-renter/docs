# Phase 5 — Nền tảng FE và tích hợp Auth

Phase này chuẩn bị nền tảng dữ liệu/API cho Web và hoàn thiện vertical slice Auth. Phạm vi chỉ dừng ở Auth; chưa triển khai Building, Room, Contract, Billing hoặc Payment.

## Nguyên tắc làm việc

- `api-docs/src/openapi.yaml` và các file `$ref` là nguồn sự thật kỹ thuật.
- `api-conventions.md` chỉ là tài liệu tham khảo. Khi có khác biệt, lấy endpoint-level contract trong `api-docs` làm chuẩn và ghi nhận vấn đề để API owner xác nhận.
- Làm tới đâu define model/API tới đó. Không dựng trước model nghiệp vụ của các module chưa bắt đầu.
- Giai đoạn này chỉ dùng offset pagination; không tạo cursor type, cursor query hoặc cursor hook.
- FE không tự triển khai cookie. Nếu Auth contract hiện tại yêu cầu `RefreshCookie`, phải ghi rõ blocker thay vì tự nghĩ transport khác.
- Toast và thông báo UI dùng API `code` + i18n, không dùng raw `message` từ backend.

## Danh sách task

Xem [bảng task Phase 5](issues/README.md).
