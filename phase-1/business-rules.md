# Business Rules (Frozen v1.2)

> **Status:** 🟢 FROZEN v1.2 (updated 2026-09-06: D33 — partial payment/overpay, per-room invoice auto, electricity drops per_head). Changes only via PM approval + change-control (Notion decision log).
> Source of truth inputs: `../requirement.md` (scope SoT), `../phase-0/feature-list.md` (Modules 1–6), `../phase-0/discovery/decisions.md` (D1–D29 + decision graph appendix), `../phase-1/discovery/decisions.md` (D30–D33), `../phase-0/discovery/market-roommate-models.md` (D21/D22/D26), `../phase-0/discovery/short-vs-long-term-analysis.md` (D23).

## 1. Room / Building

- Building → many Rooms (1:n).
- Room attributes: area, price, amenities, status (available / occupied / maintenance), `maxOccupancy`, `genderPolicy`, `houseRules`.
- **Ownership (D25, finalized 31/08 per `discovery/ownership-model.md`):** a building can be owned by **multiple people across different rooms**; each `Room` has **exactly one owner** (`Room.ownerId`, NOT NULL). `Floor` (optional grouping node) may carry a hint `ownerId` for validation/statistics only — `Room.ownerId` is the source of truth. **No manager/delegation concept in MVP** — the room owner is the operator. Covers the 59-room case: A owns 50 rooms, B/C/D own 3 each. Contract issuer = `Room.ownerId` (`Contract.issued_by_user_id`).
- Availability is derived from active Contract (no separate availability table unless short-term is added later, D9).

## 2. Contract

- Lifecycle: `draft` → `signed` (`template_upload`: landlord uploads wet-signed file by both parties) → `active` → `expired` / `terminated`.
- **Signing (D18):** legal artifact = app generates contract template (Word/PDF) → 2 bên **ký tay trên giấy** → user uploads the file **wet-signed by both parties**. **No OTP/PIN/`e_ack`** (31/08): no digital signature, no soft-acknowledgment — if no signed file is uploaded, the contract is not `signed`.
- **Shared room (D22):** 1 hợp đồng đại diện (lead tenant ký). Payment config linh hoạt: landlord chọn (1) đại diện thanh toán (lead trả, chia offline) HOẶC (2) hóa đơn chia sẻ (app track phần góp + trạng thái đã trả/chưa). Full bill-splitting (D4) → Phase 1+. (Payment-config invoicing: §4.)
- At contract creation: landlord captures & stores CCCD photo once per tenant (D17).

## 3. Utility closing (D30 — flat / bậc thang / khoán đầu người)

- Monthly meter-read capture **per utility type** (`electricity` | `water`) — OCR + manual confirm; OCR pipeline reused for CCCD (5.6). 2 bản ghi/kỳ `/phòng/kỳ`, UNIQUE `(room_id, utility_type, period)`; **đủ cả 2 loại mới được lập hóa đơn**.
- **Baseline = OCR lúc bàn giao (D34 + D35):** chỉ số cũ kỳ đầu = baseline chụp/OCR khi **bàn giao phòng** (`is_baseline=true`, `reading_date` = ngày bàn giao); OCR sai/mờ → **hiệu chỉnh tay đúng số thực tế** hoặc chụp lại (D35), đồng thời lưu ảnh evidence. Thay đồng hồ giữa kỳ → baseline mới cũng qua OCR (EC1). OCR baseline ghi nhận trong `landlord_user_flow.md` §5 (bàn giao phòng).
- **Đơn giá = `UtilityRatePolicy` (D30):** `rate_kind` = `flat` | `tiered` | `per_head`. **D33 — điện KHÔNG có `per_head`**: điện chỉ `flat`/`tiered` (thu theo kWh); `per_head` (khoán đầu người) chỉ áp **nước** + **phí định kỳ F2**. Bậc thang EVN 6 bậc + bậc 3 TT 25/2018 = preset **seed config** (không hard-code). `per_head` đếm theo `ContractMember` active tại kỳ.
- **Chuỗi kế thừa (D30, giữ tinh thần D16):** `Room.elec_policy_id`/`water_policy_id` → `Building.*` → `LandlordProfile.*`; `NULL` = kế thừa cấp trên; không resolve được policy hiệu lực → **chặn hóa đơn** (`RATE_MISSING`). Đổi giá giữa kỳ → áp từ kỳ sau.
- **Onboarding không chặn (D32):** chưa cấu hình đơn giá không block login — hiện banner nhẹ; `LandlordProfile.elec_policy_id`/`water_policy_id` là **nullable** (NULL = chưa cấu hình); bắt buộc phải đủ policy chỉ xuất hiện **lúc lập hóa đơn** (block `RATE_MISSING`).
- **Phí định kỳ = `RecurringFee` (D30):** `fee_kind` = `fixed_per_period` | `per_head` | `per_area_m2` | `per_vehicle`; scope `landlord` | `building` | `room` (fee mặc định cấp landlord áp **mọi phòng/mọi tòa**; fee tòa áp cho **từng phòng**; override ở tòa/phòng); `is_active=false` ở cấp nào → bỏ qua, kế thừa cấp trên. Mọi phí **đều thu qua hóa đơn app** (bỏ `charged_in_invoice` — D36). **Preset phí seed (D32):** Wifi/QLVH/Gửi xe/Vệ sinh rác — chọn preset tự điền `fee_kind` + `unit_price` mẫu, chủ trọ xác nhận/chỉnh.
- **Cách tính / làm tròn / prorate / edge case / blocking: → `discovery/utility-billing-calculations.md`** (spec 100% case + pseudocode).

## 4. Invoice / Payment

- Invoice = tiền phòng (prorate nếu HĐ vào/ra giữa tháng) + điện/nước (theo lượng thực + `rate_kind`) + phí định kỳ (`RecurringFee`) + phí khác (1 lần, cho phép ÂM = giảm trừ).
- **Auto-sinh theo phòng (D33 + D34):** hệ thống tự sinh `Invoice pending` cho **từng phòng** khi phòng đủ cả 2 `MeterReading` kỳ + policy/phí resolve OK (không batch toàn kỳ); landlord rà soát → phát hành. Phòng **đủ chỉ số nhưng block** (EC3/EC6/EC7/EC8/EC13/EC17) → vào danh sách **"Đã chốt số - chờ sửa lỗi"** kèm mã lỗi + nút hành động vào đúng màn sửa; sửa xong trigger chạy lại tự tạo hóa đơn. UNIQUE partial `(contract_id, period) WHERE status != 'void'` (cho phép tạo thay thế sau void).
- **Kê khai xe (D32):** số xe gửi tại nhà trọ (`Contract.vehicle_count`) khai **khi tạo/cập nhật hợp đồng** (không nhập mỗi kỳ). Phí `per_vehicle` tính theo số này, snapshot vào `fees_breakdown`; đổi giữa kỳ → cập nhật HĐ, áp từ kỳ sau. `NULL` khi có phí `per_vehicle` → block (`VEHICLE_COUNT_MISSING`).
- **Phí khác 1 lần (`other_fees`, D32):** thêm trực tiếp lúc lập hóa đơn (preset gợi ý + nhập tự do: nệm mới, sửa thiết bị…), snapshot vào hóa đơn. **D33 — amount ÂM = giảm trừ/miễn giảm**; block nếu tổng hóa đơn < 0 (`TOTAL_NEGATIVE`).
- **Snapshot bất biến (D30):** `utility_breakdown` + `fees_breakdown` (jsonb) lưu cấu hình & đầu vào đã dùng; tổng = round-half-up → hàng nghìn, kiểm tra `rent_amount + Σ(utility_breakdown) + Σ(fees_breakdown) + Σ(other_fees) == total_amount` (giữ true cả khi `other_fees` âm). Chỉ `rent_amount`/`total_amount` là cột (D20); điện/nước/phí ở snapshot (D37). Sai sót → `void` + hóa đơn mới (`voided_invoice_id`), không sửa bản đã phát hành.
- **Trạng thái hóa đơn (D33):** `pending` → `partially_paid` (Σ success ∈ (0, total)) → `paid` (Σ ≥ total) | `overdue` (quá hạn còn nợ) | `void`.
- **Đối soát (D33):** khớp theo **mã định danh hóa đơn** (không theo số tiền — trả thiếu/dư vẫn nhận). Thu dư: ghi đủ số thực nhận, `paid`, chỉ **nhắc khi mở tab History** (không hoàn tiền/bù trừ tự động). Webhook tới hóa đơn `void`: không set `paid`, đánh cờ cảnh báo chủ trọ.
- **HĐ ở ghép (D22):** payment config theo §2 — (1) đại diện thanh toán HOẶC (2) hóa đơn chia sẻ (mỗi Payment ghi `paid_by_contract_member_id`, hóa đơn `paid` khi Σ tổng ≥ total).
- Dynamic-QR reconciliation; VNPay/MoMo sandbox vs mock (R1 fallback, decided in P1-05).

## 5. Roommate / Match

- `RoommateProfile`: lifestyle, sleep schedule, pets, smoking, budget, gender preference.
- **Landlord CÓ quyền set yêu cầu (D21):** landlord sets `maxOccupancy`, `genderPolicy`, `houseRules`, `budgetRange` for his room — these are **forced hard filters** (candidates violating them are excluded from that room's match pool BEFORE matching). Landlord does **NOT** approve/veto individual pairs — matching is P2P between tenants + optional consented ID-verification badge (PDPD 13/2023). If a landlord sets no constraints, the room is open to all eligible tenants.
- `MatchRequest` (requester → target); AI match score (Stretch, spec at D28 / P1-13).

## 6. Issue reporting & Property Chat (D24′)

- `IssueReport` lifecycle: `open` → `in_progress` → `resolved`. Tái dùng làm foundation cho `@issue` + issue panel.
- **Property Chat (D24′):** 2 loại Conversation — **chat riêng phòng** (landlord ↔ tenants phòng đó) + **chat chung toà** (giao lưu + landlord nhắc tổng).
  - Realtime (Socket.io) khi app mở; **FCM offline**; DB persistence load history (lazy-load, cursor-based).
  - **Bot engine** (identity riêng): auto-remind cron — OCR-result, hóa đơn, hợp đồng hết hạn → card vào chat phòng.
  - **`@issue <mô tả>` (+ ảnh):** tạo IssueReport → card → notify conversation. (Chỉ chat riêng phòng.)
  - **`@mention @user`:** notify user được mention, autocomplete gợi ý.
  - Message types MVP: `text`, `image`, `file`, `bot`/card. Voice/sticker/poll/etc = nice-to-have.
  - Loại Zalo / Excel khỏi kênh trong app (chỉ FCM nội bộ + thuộc app).
- **Bot fatigue guard:** bot chỉ ở chat riêng phòng; chat chung toà không có bot command phòng (tránh spam + nhiễu giao lưu).

## 7. AI flows

- (1) Auto-Description (MVP), (2) Matchmaking (Stretch D28). Provider-agnostic adapter (OpenAI/Gemini via env — xem `requirement.md`).
- Tenant history / credibility (D26, **Stretch** feature 2.10): **platform-internal**, shown only with tenant consent; defer cross-platform credit (no VN rental bureau; PDPD 2023 risk). Không bắt buộc MVP.

## 8. Landlord-can-operate-solo resilience (D29 — MANDATORY)

- Hệ thống **PHẢI** vận hành được khi tenant **KHÔNG login**. Landlord quản lý toàn bộ vòng đời một mình; tenant app là optional/passive.
- Tenant touchpoints delegated: dynamic-QR (tenant quét bằng app ngân hàng bất kỳ), tiền mặt, giấy, kênh ngoài app (SĐT).
- Không feature nào hard-depend vào tenant login (stress-test: `discovery/decisions.md` Phụ lục B). Roommate matching chỉ chạy cho tenant có account (tenant không account = vắng mặt pool, không blocker).
