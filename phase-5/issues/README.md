# Phase 5 — Task FE Foundation và Auth

## Cách giao việc

Mỗi task phải được assign cho một FE member với link tới task này và các file contract liên quan trong `api-docs`. Member không tự đoán API từ UI, database hoặc `api-conventions.md`.

## Bảng task

| ID | Task | Assignee gợi ý | Trạng thái | Estimate | Phụ thuộc |
|---|---|---|---|---|---|
| [P5-01](P5-01-fe-api-contract-audit.md) | Đọc và chốt contract FE cho Auth | FE Lead review + FE Intern | In progress (`fe#6`) | 3 pts · 6–8h | — |
| [P5-02](P5-02-fe-base-api-models.md) | Xây dựng base API types đầy đủ | FE Intern | In progress (`fe#6`) | 5 pts · 10–14h | P5-01 |
| [P5-03](P5-03-fe-api-client.md) | Chuẩn hóa Axios API client | FE Intern | In progress (`fe#6`) | 5 pts · 10–14h | P5-01, P5-02 |
| [P5-04](P5-04-fe-api-code-i18n.md) | Chuẩn hóa error/success code và i18n | FE Intern | In progress (`fe#6`) | 3 pts · 6–8h | P5-01, P5-02 |
| [P5-05](P5-05-fe-query-mutation-foundation.md) | Xây dựng query/mutation foundation | FE Intern | In progress (`fe#6`) | 5 pts · 10–14h | P5-02, P5-03, P5-04 |
| [P5-06](P5-06-fe-auth-form-foundation.md) | Chuẩn hóa Auth form và validation | FE Intern | In progress (`fe#6`) | 5 pts · 10–14h | P5-04, P5-05 |
| [P5-07](P5-07-fe-auth-vertical-slice.md) | Tích hợp Auth end-to-end | FE Lead + FE Intern | In progress (`fe#6`) | 13 pts · 30–45h | P5-01 đến P5-06 |

## Thứ tự thực hiện

`P5-01 → P5-02 → (P5-03 và P5-04) → P5-05 → P5-06 → P5-07`

P5-03 và P5-04 có thể làm song song sau khi P5-02 được review. P5-07 chỉ bắt đầu khi foundation đã được FE Lead review.

## Bảng task — Backend Tenancy (Building/Room)

Chuyển từ Phase 4 (`P4-24`, `P4-25`). Building được tách thành sub-issue; issue cha `P5-08` chỉ đóng khi mọi sub-issue Done.

| ID | Task | Assignee gợi ý | Trạng thái | Estimate | Phụ thuộc |
|---|---|---|---|---|---|
| [P5-08](P5-08-tenancy-building-vertical-slice.md) | Building vertical slice (Epic) | BE Dev | In progress | 24 pts (tổng, gồm P5-08f) | P4-21 |
| ↳ [P5-08a](P5-08a-building-domain-persistence.md) | Building domain model và persistence | BE Dev | Done (migration lỗi chạy lại — sửa ở P5-08b) | 3 pts · 6–8h | P4-21 |
| ↳ [P5-08b](P5-08b-building-create-command.md) | Create Building — slice mẫu UoW + Outbox | BE Dev | Open | 5 pts · 10–14h | P5-08a |
| ↳ [P5-08c](P5-08c-building-landlord-management.md) | Landlord quản lý Building | BE Dev | Open | 5 pts · 10–14h | P5-08b |
| ↳ [P5-08d](P5-08d-building-admin-approval.md) | Admin duyệt/từ chối Building | BE Dev | Open | 5 pts · 10–14h | P5-08b |
| ↳ [P5-08e](P5-08e-building-public-search.md) | Tìm kiếm và xem Building public | BE Dev | Open | 3 pts · 6–8h | P5-08d |
| [P5-09](P5-09-tenancy-room-vertical-slice.md) | Room vertical slice (Epic) | BE Dev | In progress | 16 pts (tổng) | P5-08a, P5-08b, P5-08d |
| ↳ [P5-09a](P5-09a-room-domain-persistence.md) | Room domain model và persistence | BE Dev | Done (thiếu migration `rooms` — bổ sung ở P5-09b) | 3 pts · 6–8h | P5-08a |
| ↳ [P5-09b](P5-09b-room-create-command.md) | Create Room trong Building đã duyệt | BE Dev | Open | 5 pts · 10–14h | P5-09a, P5-08b, P5-08d |
| ↳ [P5-09c](P5-09c-room-landlord-management.md) | Landlord quản lý Room | BE Dev | Open | 5 pts · 10–14h | P5-09b |
| ↳ [P5-09d](P5-09d-room-public-search.md) | Tìm kiếm và xem chi tiết Room | BE Dev | Open | 3 pts · 6–8h | P5-09b, P5-08e |

Thứ tự:

- Building: `P5-08a → P5-08b → (P5-08c ∥ P5-08d) → P5-08e`.
- Room: `P5-09a` (song song sau `P5-08a`) → `P5-09b` (sau `P5-08d`) → (`P5-09c` ∥ `P5-09d`).

Quy định "FE member" và "Commit/PR" bên dưới áp dụng tương tự cho BE task: PR link tới file `api-docs` đã dùng, không tự thêm field/route/error code ngoài contract. Mọi BE task tạo API phải cập nhật sequence diagram và đổi tag `x-apidog-status` sang `released` khi xong.

## Quy định chung cho tất cả task

- PR phải dẫn link tới file endpoint/schema trong `api-docs` đã sử dụng.
- Không thêm field, route, enum, error code hoặc security behavior không có trong contract.
- Nếu phát hiện contract mâu thuẫn, dừng phần bị ảnh hưởng và ghi issue/blocker; không tự workaround.
- Mỗi task phải có test hoặc bằng chứng manual verification phù hợp.
- Commit/PR dùng tiếng Anh; nội dung task này dùng tiếng Việt để intern dễ thực hiện.
