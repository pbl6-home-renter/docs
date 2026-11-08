# P6-01e — Thành viên HĐ, HĐ của tenant, checkout (đã tách)

**Epic:** [P6-01](P6-01-tenancy-contract-vertical-slice.md)  
**Trạng thái:** 🔵 Split — làm theo các sub-issue bên dưới, issue này đóng khi cả ba Done  
**Người phụ trách:** leminhkhai345  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 8 points (tổng e1–e3)  
**Phụ thuộc:** P6-01d 
**Repo:** `Tenancy-Service`  
**Iteration:** 6 (09/11–15/11)  
**Issue:** `docs#69`

## Sub-issue

| ID | Task | Endpoint | Pts | Phụ thuộc |
|---|---|---|---|---|
| [P6-01e1](P6-01e1-contract-members.md) | Bảng `contract_members`, tự thêm đại diện khi activate, API member, hàm `headCount` | `POST/GET /contract-members`, `PATCH /contract-members/{id}`, `POST /contract-members/{id}/leave-contract` | 3 | P6-01d |
| [P6-01e2](P6-01e2-tenant-my-contracts.md) | Tenant xem HĐ của mình | `GET /me/contracts` (+ quyền member ở `GET /contracts/{id}`) | 2 | P6-01e1 |
| [P6-01e3](P6-01e3-contract-checkout.md) | Checkout: HĐ `terminated`, member rời, phòng `maintenance`; sửa `vehicleCount`/`description` khi HĐ `active` (`P6-D71`) | `POST /contracts/{id}/complete-checkout`, `PATCH /contracts/{id}` | 3 | P6-01e1, P6-01d, P6-02g1 |

Thứ tự: `P6-01e1 → (P6-01e2 ∥ P6-01e3)`. P6-01e3 chờ thêm bảng `invoices` của P6-02g1.

## Câu hỏi của outline cũ → đã chốt

| Câu hỏi | Quyết định |
|---|---|
| Activate có tự tạo member cho người đại diện? | Có — [`P6-D63`](../decisions.md#d63--thành-viên-hợp-đồng) |
| Checkout: phòng chuyển `pending_cleanup` hay `maintenance`? HĐ `expired` hay `terminated`? | `maintenance` rồi `mark-ready`; HĐ `terminated` — [`P6-D62`](../decisions.md#d62--checkout) |
| Quyết toán cọc ghi Payment ở đâu? | Không làm trong MVP — [`P6-D61`](../decisions.md#d61--payment-và-quyết-toán-cọc-ra-khỏi-mvp) |
| Ảnh CCCD member có trong MVP? | Không — Stretch, [`P6-D63`](../decisions.md#d63--thành-viên-hợp-đồng) |
| `status` member, khoảng ngày `joinedAt`/`leftOn`/`completedOn`, chống trùng member, sửa số xe khi `active`? | [`P6-D71`](../decisions.md#d71--contract-và-member-dữ-liệu-và-ràng-buộc) |
| Landlord chọn tài khoản tenant (`tenantId`) trên web? | Không — họ tên + SĐT, [`P6-D74`](../decisions.md#d74--liên-kết-tài-khoản-tenant) |

## Chuyển sang Stretch

- `POST /contracts/{id}/deposit-settlement` (quyết toán/hoàn cọc, lỗi `REFUND_*`, `SETTLEMENT_INVALID`, `CONTRACT_ID_MISMATCH`) — [`P6-D61`](../decisions.md#d61--payment-và-quyết-toán-cọc-ra-khỏi-mvp).
- Ảnh CCCD member (`cccd_front`/`cccd_back`) và tự liên kết tenant theo số điện thoại — [`P6-D63`](../decisions.md#d63--thành-viên-hợp-đồng), [`P6-D74`](../decisions.md#d74--liên-kết-tài-khoản-tenant).
- Field `identityCardNumber`, `dateOfBirth`, `gender`, `isRepresentative` của DTO thêm member — bỏ hẳn (`P6-D63`), không phải Stretch.
