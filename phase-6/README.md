# Phase 6 — MVP lõi: Contract, Billing, Web landlord (W11–W14)

> Lập ngày 2026-10-26 (đầu Iteration 4). Thay thế lộ trình "Phase 4 core features → Phase 5 hardening" trong `PROJECT_PLAN.md` §5, vì tại W11 mới xong Identity và đang làm Building/Room.

## Mục tiêu

Demo được vòng đời **landlord-solo** (D29) trên staging:

`Building/Room → Hợp đồng (mẫu + upload bản ký tay) → Chốt số điện nước (nhập tay/bulk) → Hóa đơn → Ghi nhận thanh toán tiền mặt/mock`

## Cắt phạm vi (MVP lõi)

| Nhóm | Quyết định |
|---|---|
| Building, Room, Contract, Rate policy/Billing setting, Meter reading, Invoice, Payment mock/cash | **MVP** — làm trong phase này |
| OCR chốt số (`preview-ocr-result`) | MVP nếu kịp It6; fallback nhập tay luôn có |
| Property Chat, Issue report, Notification (community-service) | **Stretch** |
| Roommate profile + match request | **Stretch** |
| VietQR auto-reconciliation | **Stretch** (D39) |
| AI Auto-Description / Matchmaking | **Chờ PM verify** — Phase 3 đã bỏ AI (`phase-3/discovery/microservices-architecture.md` §2.3) nhưng `requirement.md` vẫn ghi MVP |
| Mobile | Lên kế hoạch riêng, không nằm trong batch này |

## Lộ trình theo iteration

| Iteration | leminhkhai345 (BE) | huynhtiennhat0403 (BE) | ThaiBao11125 (FE) | baoduong17 (Lead) |
|---|---|---|---|---|
| **It4** 26/10–01/11 | P5-08b → P5-08c ∥ P5-08d → P5-08e | P5-09b → P5-09c ∥ P5-09d | Hoàn tất `fe#6` (P5-01…P5-07) | Review, route gateway cho tenancy, chốt OCR |
| **It5** 02/11–08/11 | P6-01 Contract (a–d) | P6-02 Billing (rate policy, billing setting, meter reading) | P6-03 màn Building/Room + admin duyệt | P6-04 Media upload, P6-08 administrative geography, deploy staging |
| **It6** 09/11–15/11 | P6-01 phần It6 (members, checkout) | P6-02 Invoice + OCR | P6-06 màn Contract/Invoice | P6-05 Payment mock/cash, P6-07 seed demo |
| **It7** 16/11–22/11 | Bug fix | Bug fix | Bug fix + polish | Demo script, báo cáo, slide |

Task It5 được viết đầy đủ step-by-step. Task It6 hiện ở mức outline, viết chi tiết trong tuần It5.

P6-08 (administrative geography) is assigned to `baoduong17` in Iteration 5 and is intentionally kept separate from geocoding.

## Cách viết và giao task

- Mỗi task dùng [`issues/_TEMPLATE.md`](issues/_TEMPLATE.md). Mẫu tham chiếu: [P5-08b](../phase-5/issues/P5-08b-building-create-command.md).
- Đường dẫn file trong task phải lấy từ code thật của repo; bước nào cũng có phần **Kiểm tra bước**.
- Mỗi file task ↔ một issue trong repo `docs`, thêm vào Project #3 với Assignee, Priority, Iteration. Sub-issue được link vào epic.
- PR code ghi `Closes pbl6-home-renter/docs#<số>` để hiện ở cột *Linked pull requests*.
- Nguyên tắc contract giữ như [Phase 5](../phase-5/README.md): `api-doc` là nguồn sự thật; gặp mâu thuẫn thì dừng và ghi blocker.

## Danh sách task

Xem [issues/README.md](issues/README.md).
