# P10-13 — Chủ nhà gửi reminder từ Web Chat

**Loại:** Frontend · **Trạng thái:** 🔵 In progress — PR code chờ review/merge, phụ thuộc P10-12

**Owner đề xuất:** `ThaiBao11125` · **Reviewer:** FE Lead / Community owner · **Repo:** `fe`

**Phụ thuộc:** P10-12, CB-15 · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## User story và bối cảnh

Là chủ nhà đang ở hội thoại liên quan, tôi muốn chọn một mẫu nhắc và xác nhận gửi để không nhập lại nội dung thủ công. Backend contract chưa hoàn tất; FE chỉ cung cấp thao tác cho template và resource đã được PM/API owner duyệt.

## Rà soát triển khai 14/11/2026

Chat đã có `contextType`/`contextId`, lịch sử message và đồng bộ Socket. FE có client hợp đồng và hóa đơn thật; danh sách hóa đơn hỗ trợ filter theo hợp đồng. Theo xác nhận của người yêu cầu ngày 14/11/2026, triển khai hai mẫu `invoice` và `contract_expiring` cho hội thoại hợp đồng, phụ thuộc API P10-12; không diễn giải hóa đơn `issued` là chưa thanh toán.

[FE #46](https://github.com/pbl6-home-renter/fe/pull/46) đang chờ review/merge và phụ thuộc [Community #36](https://github.com/pbl6-home-renter/community-service/pull/36). FE build/lint/i18n và kiểm tra trình duyệt bằng API giả lập đạt; chưa nghiệm thu Gateway và Socket/FCM thật.

## Triển khai

1. Đọc P10-12, contract response/error và rule quyền; xác định điểm mở action và danh sách resource thực từ API hiện có. **Kiểm tra:** chỉ user/context có quyền được đề nghị thao tác; chặn UI không thay thế kiểm tra backend.
2. Tạo API mutation, query key/invalidation và dialog chọn mẫu/resource theo FE conventions; dùng `clientMessageId` ổn định khi retry cùng yêu cầu, không dùng lại key sau khi đổi nội dung/resource. Không dựng danh sách resource giả. **Kiểm tra:** thay resource tạo yêu cầu mới; retry sau lỗi mạng không nhân bản message.
3. Xử lý loading, lỗi server bằng toast hiện có, empty resource và xác nhận gửi; khi thành công đồng bộ message history qua contract Socket/REST. Thêm text `vi/en`. **Kiểm tra:** hai client thấy một bot message; đóng/mở dialog không gửi ngoài ý muốn.
4. Chạy build/lint/i18n và kiểm tra 360px/desktop, keyboard, resource không có quyền, retry cùng key qua Gateway.

## Acceptance

- Landlord gửi được reminder được duyệt và nhìn thấy kết quả thật; member thường hoặc resource sai bị backend từ chối.
- Không hiển thị lựa chọn OCR/payment chưa được duyệt; request lỗi không báo thành công và retry không tạo message trùng.
- Có bằng chứng thao tác hai client, lỗi/empty và kết quả kiểm tra; không triển khai scheduler.
