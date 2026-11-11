# P9-09 — Smoke event xuyên service và lưu bằng chứng

**Epic:** Tích hợp event Phase 9  
**Trạng thái:** 🟡 Open  
**Coders:** `leminhkhai345`, `huynhtiennhat0403`  
**Người review:** PM  
**Ước lượng:** 2 points · 8 giờ  
**Phụ thuộc:** P9-01–P9-08  
**Repo:** `Identity-Service/`, `Tenancy-Service/`, `community-service/`  
**Issue:** `docs#TBD`

## Mục tiêu

Ghi lại smoke xuyên RabbitMQ có thể lặp lại cho các nhóm event Phase 9 và lưu bằng chứng để PM review.

## Happy path bắt buộc

- Tenant đăng ký sau khi ContractMember NULL tồn tại → Tenancy link → Community contract conversation có user.
- Tenant đã đăng ký trước landlord thêm member → Tenancy resolve từ projection → Community có membership.
- Tạo Building → building chat duy nhất; approve/reject → landlord nhận system notification.
- Kích hoạt contract/member changes → contract chat có đúng membership.
- Tenant lock/unlock → account notice; landlord lock → contract suspend/grace flow; unlock choice hoặc hết hạn → kết quả/notice đúng.
- Invoice phát hành → Community lưu inbox item cho từng tenant active đã link.

## Kiểm tra lỗi/replay

- Replay message cùng ID và xác nhận không có membership, lock transition hoặc notification trùng.
- Tắt RabbitMQ, thực hiện mutation producer, xác nhận business/outbox commit; bật broker lại và xác nhận consumer nhận bù.
- Gây lỗi transaction consumer, xác nhận inbox/business rollback, retry và DLQ.

## Acceptance

- Bằng chứng ghi event ID, routing key, queue, producer DB/outbox state và consumer state cuối; không chứa secret hoặc phone PII trong Community payload/log.
- Có artifact cho toàn bộ happy path bắt buộc và link từ PR.
- PM duyệt evidence trước khi đóng issue event Phase 9.

## Ngoài phạm vi

- Load/performance test đầy đủ, Payment, IssueReport, auto-refund hoặc production rollout.
