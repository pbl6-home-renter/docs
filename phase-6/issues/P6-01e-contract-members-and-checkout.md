# P6-01e — Thành viên HĐ, HĐ của tenant, checkout và quyết toán cọc (outline)

**Epic:** [P6-01](P6-01-tenancy-contract-vertical-slice.md)  
**Trạng thái:** ⚪ Outline (viết chi tiết step-by-step theo `_TEMPLATE.md` khi bắt đầu Iteration 6)  
**Người phụ trách:** leminhkhai345  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 8 points · 16–22 giờ (tách nhỏ khi viết chi tiết)  
**Phụ thuộc:** P6-01d; phần quyết toán cọc phụ thuộc thêm Payment cash (lead, It6)  
**Repo:** `Tenancy-Service`  
**Iteration:** 6 (09/11)  
**Issue:** `docs#69`

## Mục tiêu

Hoàn thiện phần còn lại của vòng đời HĐ:

- tenant xem HĐ của mình;
- landlord quản lý thành viên ở ghép (nguồn đếm `head_count` cho phí `per_head` của Billing);
- landlord checkout trả phòng, phòng trở về trạng thái sẵn sàng cho thuê.

## Phạm vi dự kiến (tách thành sub-issue khi viết chi tiết)

| Nhóm | Endpoint (`api-doc/src/paths/contracts/`) | Ghi chú nghiệp vụ |
|---|---|---|
| HĐ của tenant | `GET /me/contracts` (`me-contracts.yaml`, `CONTRACTS_MY_FETCHED`) | Lọc theo `tenant_id = user.id`, cùng HĐ mà user là `contract_members.tenant_id` |
| Thành viên | `POST/GET /contract-members`, `PATCH /contract-members/{id}`, `POST /contract-members/{id}/leave-contract` | Bảng `contract_members` (`database-design.md` §2.8). Lỗi: `MEMBER_ALREADY_EXISTS`, `MEMBER_LEFT`, `MEMBER_ALREADY_LEFT`, `LEFT_DATE_INVALID`, `CONTRACT_ID_REQUIRED`. Không xóa bản ghi khi rời, chỉ set `left_at`. Người đại diện HĐ được tạo tự động thành member khi activate (cần chốt). |
| Checkout | `POST /contracts/{id}/complete-checkout` | `CONTRACT_NOT_ACTIVE`, `SETTLEMENT_NOT_READY`. HĐ chuyển `terminated`; phòng gọi `Room.releaseByContract()` (viết ở P6-01d), chuyển trạng thái chờ dọn theo mô tả contract |
| Quyết toán cọc | `POST /contracts/{id}/deposit-settlement` | Ghi Payment `invoice_id = NULL`, `contract_id`, `method = cash` (`database-design.md` dòng về "Trả cọc"); lỗi `REFUND_AMOUNT_MISMATCH`, `REFUND_PAYOUT_ACCOUNT_REQUIRED`, `SETTLEMENT_INVALID`, `CONTRACT_ID_MISMATCH`. Cần payment-service hoặc thay bằng mock ghi nhận trong tenancy: **chờ lead chốt** |

## Câu hỏi cần chốt trước khi viết chi tiết

- Khi activate, có tự tạo `contract_members` cho người đại diện không? (Ảnh hưởng `head_count`.)
- Mô tả checkout ghi phòng chuyển "chờ dọn dẹp", nhưng `RoomStatus` hiện chỉ có `available | occupied | maintenance`. Dùng `maintenance` hay thêm trạng thái mới (đổi contract Room)?
- Quyết toán cọc ghi Payment ở service nào trong MVP (payment-service chưa có repo)?
- Ảnh CCCD thành viên (`cccd_front`/`cccd_back`, D17) dùng media P6-04: có nằm trong MVP không?

## Definition of Done (khi viết chi tiết)

- Mỗi sub-issue theo `_TEMPLATE.md`, có đường dẫn file thật và phần Kiểm tra bước.
- Write operation tuân theo tiêu chí chung của epic P6-01 (UoW + outbox, sequence diagram, `released`).
