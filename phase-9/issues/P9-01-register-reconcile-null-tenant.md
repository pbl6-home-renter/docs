# P9-01 — Tenant đăng ký → reconcile membership NULL → contract chat

**Epic:** Tích hợp event Phase 9  
**Trạng thái:** 🟡 Open  
**Coder:** `leminhkhai345`  
**Người review:** PM  
**Ước lượng:** 3 points · 12 giờ (mục tiêu ≤15 file mỗi PR)  
**Phụ thuộc:** P8-06; P7-03/04/05  
**Repo:** `Identity-Service/`, `Tenancy-Service/`, `community-service/`  
**Issue:** `docs#TBD`

## Mục tiêu

Khi tenant đăng ký sau khi landlord đã khai báo số điện thoại trong Contract/ContractMember, Tenancy liên kết account và Community thêm user vào contract conversation. Hoàn thành happy path xuyên RabbitMQ.

## Contract event

| Producer | Routing key | Queue | Field payload sử dụng | Consumer xử lý |
|---|---|---|---|---|
| Identity | `user.registered` | `tenancy.identity-lifecycle` | Envelope hiện có; payload `userId`, `role`, `phone`, `status` | Tenancy dedup, so khớp phone tenant chính xác sau chuẩn hóa, cập nhật `tenantId=NULL`, lưu projection user-phone và ghi event linked vào outbox. |
| Tenancy | `contract_member.linked` | `community.contract-context` | `contractId`, `contractMemberId`, `tenantUserId` | Community thêm user vào contract conversation idempotent. Không gửi phone sang Community. |

Dùng lại producer `user.registered` và hạ tầng Building/outbox hiện có. Không tạo publisher trùng và không để Community tự tra Identity.

## Triển khai

1. Tạo consumer Tenancy trên queue `tenancy.identity-lifecycle`, dùng inbox/transaction pattern hiện có.
2. Trong một transaction Tenancy, tìm các Contract/ContractMember chưa xóa có `tenantId IS NULL` và phone khớp chính xác; gán `tenantId`, ghi/cập nhật projection user-phone và append `contract_member.linked` vào outbox.
3. Tạo subscriber Community trên `community.contract-context`; tìm conversation theo contract context và thêm/kích hoạt membership idempotent.
4. Dùng một tenant/member mẫu để xác nhận account xuất hiện trong contract chat.

## Acceptance

- Tenant đăng ký khớp Contract representative/member NULL thì được link ở Tenancy và có membership trong contract conversation.
- Gửi lại `user.registered` không tạo link hoặc membership trùng.
- Phone không khớp thì dữ liệu Tenancy không đổi; payload/log phía Community không có phone.
- Business update, projection và outbox commit/rollback cùng nhau; inbox consumer dedup side effect.

## Ngoài phạm vi

- Community phân quyền bằng phone, Community tìm kiếm phone, welcome email hoặc sửa record có `tenantId` đã được gán.

## Checklist review

- [ ] Bằng chứng happy path Identity → Tenancy → RabbitMQ → Community contract membership.
- [ ] Schema/routing khớp P9-D83.
- [ ] PM review trước khi merge.
