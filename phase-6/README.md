# Phase 6 — MVP lõi: Contract, Billing, Web landlord (W11–W14)

> Lập ngày 2026-10-26 (đầu Iteration 4). Thay thế lộ trình "Phase 4 core features → Phase 5 hardening" trong `PROJECT_PLAN.md` §5, vì tại W11 mới xong Identity và đang làm Building/Room.

## Mục tiêu

Demo được vòng đời **landlord-solo** (D29) trên staging:

`Building/Room → Hợp đồng (mẫu + upload bản ký tay) → Chốt số điện nước (OCR/nhập tay/bulk) → Hóa đơn (sinh → phát hành) → Checkout`

Quyết định làm rõ MeterReading baseline và bulk của phase này: [D60](discovery/decisions.md).

## Cắt phạm vi (MVP lõi)

| Nhóm | Quyết định |
|---|---|
| Building, Room, Contract (+ thành viên, checkout), Rate policy/Billing setting, Meter reading, Invoice (`pending → issued → void`) | **MVP** — làm trong phase này |
| OCR chốt số qua `ai-service` (Claude vision) | **MVP** It6 — `P6-D67`; fallback nhập tay luôn có |
| Payment tiền mặt/mock, quyết toán cọc | **Stretch** — `P6-D61` (demo dừng ở phát hành hóa đơn) |
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
| **It6** 09/11–15/11 | P6-01e1–e3 (members, `/me/contracts`, checkout) | P6-02g1–g4 Invoice, P6-02h | P6-06a–d màn Contract/Meter/Invoice | P6-10b OCR, P6-07 seed demo |
| **It7** 16/11–22/11 | Bug fix | Bug fix | Bug fix + polish | Demo script, báo cáo, slide |

Task It5 và It6 đều đã viết step-by-step theo `_TEMPLATE.md` v2. Mọi quyết định nghiệp vụ của phase nằm ở [`decisions.md`](decisions.md) (D61–D75; published D60 remains in `discovery/decisions.md`); trước It6 lead làm thêm P6-09 (đồng bộ `api-docs`), P6-10a (scaffold `ai-service`), P6-11 (endpoint ownership nội bộ), P6-12 (internal media lookup).

P6-08 (administrative geography) is assigned to `baoduong17` in Iteration 5 and is intentionally kept separate from geocoding.

## Cách viết và giao task

- Mỗi task dùng [`issues/_TEMPLATE.md`](issues/_TEMPLATE.md). Mẫu tham chiếu: [P5-08b](../phase-5/issues/P5-08b-building-create-command.md).
- Đường dẫn file trong task phải lấy từ code thật của repo; bước nào cũng có phần **Kiểm tra bước**.
- Mỗi file task ↔ một issue trong repo `docs`, thêm vào Project #3 với Assignee, Priority, Iteration. Sub-issue được link vào epic.
- PR code ghi `Closes pbl6-home-renter/docs#<số>` để hiện ở cột *Linked pull requests*.
- Thứ tự ưu tiên khi nguồn mâu thuẫn ([`P6-D75`](decisions.md)): `decisions.md` > `api-docs` > skill của repo (`.agents/skills/`) > nội dung issue. Câu hỏi nghiệp vụ phải có D-ID trước khi giao task.
- Quy ước code nằm trong `AGENTS.md` + `.agents/skills/` của từng repo (FE: `fe`; backend: nguồn ở `boilerplate`, copy sang các service); issue không mô tả lại.

## Danh sách task

Xem [issues/README.md](issues/README.md).

## Community Service

Chat và Notification đã được chuyển sang track Phase 7, bắt đầu It5 song song với Phase 6. Xem [Phase 7 plan](../phase-7/README.md) và [task tracker](../phase-7/issues/README.md). Thiết kế ERD/business/API cùng dependency backlog được giữ tại [thiết kế Community Service](discovery/community-service-design.md) và [implementation backlog](discovery/community-service-implementation-backlog.md).
