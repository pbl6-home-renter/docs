# Business Rules (Frozen v1.0)

> **Status:** 🟡 DRAFT — being finalized in P1-07. Do not change without PM approval + change-control (Notion decision log).
> Source of truth inputs: `../requirement.md` (scope SoT), `../phase-0/feature-list.md` (Modules 1–6), `../phase-0/discovery/decisions.md` (D1–D29 + decision graph appendix), `../phase-0/discovery/market-roommate-models.md` (D21/D22/D26), `../phase-0/discovery/short-vs-long-term-analysis.md` (D23).

## 1. Room / Building

- Building → many Rooms (1:n).
- Room attributes: area, price, amenities, status (available / occupied / maintenance), `maxOccupancy`, `genderPolicy`, `houseRules`.
- **Ownership (D25, finalized 31/08 per `discovery/ownership-model.md`):** a building can be owned by **multiple people across different rooms**; each `Room` has **exactly one owner** (`Room.ownerId`, NOT NULL). `Floor` (optional grouping node) may carry a hint `ownerId` for validation/statistics only — `Room.ownerId` is the source of truth. **No manager/delegation concept in MVP** — the room owner is the operator. Covers the 59-room case: A owns 50 rooms, B/C/D own 3 each. Contract issuer = `Room.ownerId` (`Contract.issued_by_user_id`).
- Availability is derived from active Contract (no separate availability table unless short-term is added later, D9).

## 2. Contract

- Lifecycle: `draft` → `signed` (`template_upload`: landlord uploads wet-signed file by both parties) → `active` → `expired` / `terminated`.
- **Signing (D18):** legal artifact = app generates contract template (Word/PDF) → 2 bên **ký tay trên giấy** → user uploads the file **wet-signed by both parties**. **No OTP/PIN/`e_ack`** (31/08): no digital signature, no soft-acknowledgment — if no signed file is uploaded, the contract is not `signed`.
- **Shared room (D22):** 1 hợp đồng đại diện (lead tenant ký). Payment config linh hoạt: landlord chọn (1) đại diện thanh toán (lead trả, chia offline) HOẶC (2) hóa đơn chia sẻ (app track phần góp + trạng thái đã trả/chưa). Full bill-splitting (D4) → Phase 1+.
- At contract creation: landlord captures & stores CCCD photo once per tenant (D17).

## 3. Utility closing

- Monthly meter-read capture (OCR + manual confirm); OCR pipeline reused for CCCD (5.6).
- Electricity: flat-rate vs EVN bậc thang = open question #6 (decide in P1-07). Rate from `Building` default (D16) with optional per-`Room` override.
- Prorate when contract starts/ends mid-month.

## 4. Invoice / Payment

- Invoice = rent + utility (from closing) + optional fees.
- **HĐ ở ghép (D22):** 1 hợp đồng đại diện (lead tenant ký). **Payment config linh hoạt:** landlord chọn (1) đại diện thanh toán (lead trả, chia offline) HOẶC (2) hóa đơn chia sẻ (app track phần góp + trạng thái đã trả/chưa).
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

- (1) Auto-Description (MVP), (2) Matchmaking (Stretch D28). Provider-agnostic adapter (D3: OpenAI/Gemini via env).
- Tenant history / credibility (D26, **Stretch** feature 2.10): **platform-internal**, shown only with tenant consent; defer cross-platform credit (no VN rental bureau; PDPD 2023 risk). Không bắt buộc MVP.

## 8. Landlord-can-operate-solo resilience (D29 — MANDATORY)

- Hệ thống **PHẢI** vận hành được khi tenant **KHÔNG login**. Landlord quản lý toàn bộ vòng đời một mình; tenant app là optional/passive.
- Tenant touchpoints delegated: dynamic-QR (tenant quét bằng app ngân hàng bất kỳ), tiền mặt, giấy, kênh ngoài app (SĐT).
- Không feature nào hard-depend vào tenant login (stress-test: `discovery/decisions.md` Phụ lục B). Roommate matching chỉ chạy cho tenant có account (tenant không account = vắng mặt pool, không blocker).
