# P9-02 — Tenant đã đăng ký → thêm member → contract chat

**Epic:** Tích hợp event Phase 9  
**Trạng thái:** 🟡 Open  
**Coder:** `leminhkhai345`  
**Người review:** PM  
**Ước lượng:** 3 points · 12 giờ (mục tiêu ≤15 file mỗi PR)  
**Phụ thuộc:** P9-01  
**Repo:** `Identity-Service/`, `Tenancy-Service/`, `community-service/`  
**Issue:** `docs#TBD`

## Mục tiêu

Khi account tenant tồn tại trước lúc landlord tạo hoặc sửa ContractMember, Tenancy link member bằng projection; Community thêm user vào contract conversation.

## Contract event

| Producer | Routing key | Queue | Field payload sử dụng | Consumer xử lý |
|---|---|---|---|---|
| Identity | `user.registered`, `user.updated`, `user.deleted` | `tenancy.identity-lifecycle` | `userId`, `role`, `phone`, `status`; event delete dùng `userId` | Cập nhật projection userId-phone; khi xóa user thì xóa mapping tra cứu, không unlink ContractMember cũ. |
| Tenancy | `contract_member.added`, `contract_member.linked` | `community.contract-context` | `contractId`, `contractMemberId`, `tenantUserId`, `joinedAt` | Thêm user đã link vào contract conversation tương ứng. |

`contract_member.added` gửi `tenantId` đã resolve nếu tìm thấy. `contract_member.linked` dành cho member NULL được link sau đó. Không event nào gửi phone sang Community.

## Triển khai

1. Tái sử dụng projection/consumer từ P9-01; cập nhật phone khi `user.updated`, bỏ mapping tra cứu khi `user.deleted` nhưng giữ liên kết lịch sử.
2. Trong transaction add/update ContractMember, tra phone đã chuẩn hóa trong projection. Không khớp thì giữ `tenantId = NULL`.
3. Lưu member change và outbox event trong cùng transaction.
4. Tái sử dụng handler `community.contract-context` từ P9-01/P9-04 để thêm user idempotent.

## Acceptance

- Account đã đăng ký và member có phone khớp thì `tenantId` được gán và user vào contract chat.
- Phone chưa có account thì `tenantId` vẫn NULL; lần đăng ký sau được P9-01 reconcile.
- Thay đổi phone cập nhật projection; không tự chuyển các link cũ sang account khác.
- Gửi lại member command/event không tạo membership trùng.

## Ngoài phạm vi

- Gọi Identity đồng bộ qua HTTP, fuzzy phone match, hoặc đưa phone vào event Community.

## Checklist review

- [ ] Happy path landlord add/update → Tenancy link → Community membership.
- [ ] Member mutation và outbox append nằm trong cùng transaction local.
- [ ] PM review trước khi merge.
