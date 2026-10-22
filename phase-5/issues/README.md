# Phase 5 — Task FE Foundation và Auth

## Cách giao việc

Mỗi task phải được assign cho một FE member với link tới task này và các file contract liên quan trong `api-docs`. Member không tự đoán API từ UI, database hoặc `api-conventions.md`.

## Bảng task

| ID | Task | Assignee gợi ý | Trạng thái | Estimate | Phụ thuộc |
|---|---|---|---|---|---|
| [P5-01](P5-01-fe-api-contract-audit.md) | Đọc và chốt contract FE cho Auth | FE Lead review + FE Intern | Open | 3 pts · 6–8h | — |
| [P5-02](P5-02-fe-base-api-models.md) | Xây dựng base API types đầy đủ | FE Intern | Open | 5 pts · 10–14h | P5-01 |
| [P5-03](P5-03-fe-api-client.md) | Chuẩn hóa Axios API client | FE Intern | Open | 5 pts · 10–14h | P5-01, P5-02 |
| [P5-04](P5-04-fe-api-code-i18n.md) | Chuẩn hóa error/success code và i18n | FE Intern | Open | 3 pts · 6–8h | P5-01, P5-02 |
| [P5-05](P5-05-fe-query-mutation-foundation.md) | Xây dựng query/mutation foundation | FE Intern | Open | 5 pts · 10–14h | P5-02, P5-03, P5-04 |
| [P5-06](P5-06-fe-auth-form-foundation.md) | Chuẩn hóa Auth form và validation | FE Intern | Open | 5 pts · 10–14h | P5-04, P5-05 |
| [P5-07](P5-07-fe-auth-vertical-slice.md) | Tích hợp Auth end-to-end | FE Lead + FE Intern | Open | 13 pts · 30–45h | P5-01 đến P5-06 |

## Thứ tự thực hiện

`P5-01 → P5-02 → (P5-03 và P5-04) → P5-05 → P5-06 → P5-07`

P5-03 và P5-04 có thể làm song song sau khi P5-02 được review. P5-07 chỉ bắt đầu khi foundation đã được FE Lead review.

## Quy định chung cho tất cả task

- PR phải dẫn link tới file endpoint/schema trong `api-docs` đã sử dụng.
- Không thêm field, route, enum, error code hoặc security behavior không có trong contract.
- Nếu phát hiện contract mâu thuẫn, dừng phần bị ảnh hưởng và ghi issue/blocker; không tự workaround.
- Mỗi task phải có test hoặc bằng chứng manual verification phù hợp.
- Commit/PR dùng tiếng Anh; nội dung task này dùng tiếng Việt để intern dễ thực hiện.
