# Feature List — PBL6

> **Purpose:** canonical prioritized feature list — source of truth for P0-06 MVP scope. Aligned with P0-03 decisions D1–D29 (D12 skipped).
> Each feature includes: priority, rationale (why needed), and complexity estimate.
> **Priority levels:** MVP (must have) · Stretch (should have) · Nice-to-have (could have)
> **Platform model (D13):** web + mobile both serve both roles. Primary: landlord-web (ops console) + tenant-mobile (portal). Secondary: landlord-mobile-lite (FCM, duyệt sự cố, xem dashboard/hóa đơn) + tenant-web (responsive). Backend `User.role` enum → `roles` array.
> **Decisions reflected:** D1 two-sided · D4/D22 bill-splitting→Phase1+ (MVP: 1 HĐ đại diện + payment config: rep-payer hoặc shared-invoice tracking) · D7 integration-first (FCM, own data/compute) · D9 long-term-only (analysis doc, hợp nhất D23) · **D24′ Property Chat** · D13 cross-platform roles · D17 tạm trú research (spike P1-15) · D18 e-contract template+upload wet-sign ONLY (bỏ OTP/PIN, hợp nhất D14) · D19 drop import · D20 landlord dashboard MVP · D21 landlord CÓ quyền set yêu cầu (hard filter) matching · D25 ownership model finalized (`ownership-model.md`) · D26 tenant history Stretch (consent-based) · D28 AI match spec (hợp nhất D8) · D29 landlord-solo resilience (mandatory) · F2 no feed · F5 OCR not utility-API · F7 e-contract $0.

## Legend

| Priority | Meaning |
|----------|---------|
| **MVP** | Must ship for demo; core value proposition |
| **Stretch** | Important but can be demoed with mock/placeholder |
| **Nice-to-have** | Differentiator; only if time permits |

---

## Module 1: Property Management (Web primary — Landlord; Mobile-lite secondary)

| # | Feature | Priority | Rationale | Complexity |
|---|---------|----------|-----------|------------|
| 1.1 | Room CRUD (create/read/update/delete) | MVP | Core entity — everything depends on room data | Low |
| 1.2 | Building management (group rooms by building) | MVP | Landlords manage multiple buildings; competitor standard (Mona House, KiotViet) | Low |
| 1.3 | **Dashboard chủ trọ:** lịch phòng trống/đang thuê trực quan (room-map nâng cấp) + biểu đồ doanh thu/công nợ realtime (D20) | MVP | Key UX differentiator — visual overview + realtime metrics saves time vs spreadsheet | Medium |
| 1.4 | Room status tracking (available/occupied/maintenance) | Stretch | Useful but can be inferred from contract status initially | Medium |
| 1.5 | Photo gallery per room | Nice-to-have | Helps tenant decision; Mona House has this | Medium |
| 1.6 | Bulk room operations (export CSV/XLSX only) | Dropped | **Import bỏ hẳn** (D19: user non-tech); giữ export nếu cần | Medium |

## Module 2: Tenant Operations (Mobile primary — Tenant; Web responsive secondary)

| # | Feature | Priority | Rationale | Complexity |
|---|---------|----------|-----------|------------|
| 2.1 | Map-based room search | MVP | Core tenant feature; standard in all rental apps (Phong Tro 123, NhaTroTot, Cho Tot). Under D29 landlord có thể tự tìm/tạo thay tenant | High |
| 2.2 | Advanced filters (price, area, amenities, distance) | MVP | Users expect filtering; competitor standard | Medium |
| 2.3 | Room detail view (photos, price, location, landlord info) | MVP | Required for decision-making | Low |
| 2.4 | Monthly invoice view | MVP | Core billing flow — tenant xem qua app, hoặc landlord đẩy qua kênh ngoài app/QR/tiền mặt (D29) | Low |
| 2.5 | Online payment (VNPay/Momo) | MVP | Critical for digitizing payment; currently paper/cash | High |
| 2.6 | Payment history | Stretch | Useful for tenant records; low effort if invoice view exists | Low |
| 2.7 | Báo sự cố + Property Chat riêng phòng | MVP | Pain point (Chị Mai SLA); **D24′**: IssueReport (open→in_progress→resolved) qua `@issue` trong chat riêng phòng; bot auto-remind (OCR, hóa đơn, hợp đồng); mention `@user`; realtime Socket.io khi app mở, FCM offline | High |
| 2.8 | In-app messaging with landlord | Nice-to-have | Đã hợp nhất vào **Property Chat (D24′)** — chat riêng phòng + chung toà; không xây kênh riêng 1-1 ngoài phòng | High |
| 2.9 | Favorite/save rooms | Nice-to-have | Standard in search apps; low effort | Low |
| 2.10 | Tenant rental history / credibility (consent-based, platform-internal) | Stretch | D26: lịch sử kỳ thuê trước trong app + thanh toán đúng hạn, chỉ hiển thị khi tenant đồng ý; defer cross-platform credit (PDPD 2023) | Medium |

## Module 3: Contract & Billing (Web + Mobile)

| # | Feature | Priority | Rationale | Complexity |
|---|---------|----------|-----------|------------|
| 3.1 | E-contract creation + signing (template upload) | MVP | Core business flow; digitizes paper contracts. Signing (D18): app **sinh mẫu HĐ (Word/PDF)** → 2 bên **ký tay trên giấy** → user **up file đã ký (wet-sign 2 bên)** làm artifact pháp lý. **Bỏ OTP/PIN/`e_ack` hoàn toàn** (31/08): không OTP SMS/FCM, không soft-ack — chưa có file ký thì HĐ chưa signed. `signature_mode` = `template_upload` only (F7, $0). **Tại bước này: chủ trọ chụp & lưu ảnh CCCD 1 lần cho mỗi tenant** (D17) | Medium |
| 3.2 | E-contract listing & status tracking | MVP | Landlord needs overview of active/expired contracts | Low |
| 3.3 | OCR meter closing + manual confirm | MVP | Major pain point — manual Excel today (F5); OCR from photo + 1-tap confirm + photo evidence; manual fallback always | Medium |
| 3.4 | Auto-invoice generation from utility data | MVP | Reduces manual work; key value prop for landlords | Medium |
| 3.5 | Invoice listing & status (paid/unpaid) | MVP | Landlord needs payment overview | Low |
| 3.6 | Payment tracking & overdue reminders | Stretch | Reduces follow-up work; can be manual for MVP | Medium |
| 3.10 | Dynamic named-QR + auto-reconciliation | MVP | Core differentiator (vision §1 Unlike); webhook callback auto gạch nợ; mock toggle fallback (R1) | High |
| 3.11 | Utility rate config (landlord-default global + building/room override) | MVP | Hóa đơn phụ thuộc rate; UC-L3 fail case "missing rate → blocked". D16: `LandlordProfile` default 1 lần, `Building`/`Room` override tùy chọn; invoice đọc room→building→landlord; flat vs bậc thang EVN = open Q#6 | Low–Med |
| 3.7 | **Realtime revenue & debt dashboard** (doanh thu/công nợ theo thời gian thực, period grouping tháng/quý/năm) | MVP | Nâng từ ledger Stretch → MVP theo D20; biểu đồ realtime + công nợ đến hạn | Medium |
| 3.8 | Multi-currency support | Nice-to-have | Not needed for Vietnam market | High |
| 3.9 | E-invoice legal compliance (HĐĐT) | Nice-to-have | Legal requirement but can be post-MVP | High |

## Module 4: Roommate Social (Mobile primary — Tenant; Web secondary)

| # | Feature | Priority | Rationale | Complexity |
|---|---------|----------|-----------|------------|
| 4.1 | Roommate profile (lifestyle, personality, budget) | MVP | Foundation for matching; unique feature vs competitors | Medium |
| 4.2 | Browse roommate profiles | MVP | Users need to discover potential roommates | Medium |
| 4.3 | Match request / connect (P2P, constraints-only) | MVP | Core social interaction; D21: landlord **CÓ quyền set yêu cầu/ràng buộc** (hard filter 4.7) nhưng **không duyệt/veto từng cặp** | Medium |
| 4.4 | AI Matchmaking score + advice | Stretch | Differentiator (D28): hybrid rule-filter→LLM score, text-only moderation, cache per pair; seed ≥10 profiles | High |
| 4.5 | Chat between matched roommates | Nice-to-have | Deferred — liên hệ ngoài app sau mở khóa SĐT/Zalo khi 2 bên đồng ý; không build chat trong MVP | High |
| 4.6 | Personality quiz / assessment | Nice-to-have | Improves matching quality; can be manual profile fields first | Medium |
| 4.7 | Landlord room/tenant constraints (max occupancy, gender policy, house rules, budget) | MVP | D21: chủ trọ **CÓ quyền set yêu cầu** (hard filter — vi phạm bị loại khỏi pool); **không duyệt từng cặp**; matching P2P + ID-verify badge | Low |

## Module 5: AI Features (Python/FastAPI)

| # | Feature | Priority | Rationale | Complexity |
|---|---------|----------|-----------|------------|
| 5.1 | Auto room description from keywords | MVP | Landlord pain point — writing descriptions; quick win with OpenAI | Medium |
| 5.2 | Roommate matchmaking score | Stretch | Cool demo feature; depends on profile data quality (D28) | High |
| 5.3 | Smart room recommendations | Nice-to-have | Personalized search; needs data volume | High |
| 5.4 | Price suggestion based on market | Nice-to-have | Data-dependent; post-MVP | High |
| 5.6 | CCCD OCR extraction (supplementary) | MVP | D17 (nâng từ Stretch 31/08): trích số/họ tên/ngày sinh/địa chỉ từ ảnh CCCD đã lưu ở 3.1; tái dùng pipeline OCR công tơ; giảm nhập liệu thủ công | Medium |

## Module 6: Admin & System

| # | Feature | Priority | Rationale | Complexity |
|---|---------|----------|-----------|------------|
| 6.1 | User authentication (JWT) | MVP | Required for all users | Medium |
| 6.2 | Role-based access (`roles` array) | MVP | Different views per role; D13: one user may be both landlord & tenant → `roles` set not single enum | Medium |
| 6.3 | User profile management | MVP | Basic profile for all users | Low |
| 6.4 | Notification system (invoice, contract expiry) | Stretch | Reduces manual follow-up; FCM is primary channel (D7) | Medium |
| 6.5 | Multi-language support | Nice-to-have | Not critical for Vietnam MVP | Medium |
| 6.6 | Property Chat (riêng phòng + chung toà) + bot + command | MVP | **D24′** replaces "object-attached thread": chat phòng + chat chung toà; bot card (OCR/invoice/contract), `@issue` command, `@mention`; message text/image/file/bot; FCM offline + DB persistence; loại Zalo/Excel khỏi kênh | Medium |

---

## Out-of-Scope (explicit — from P0-03 decisions)

| Item | Reason | Decision |
|------|--------|----------|
| Short-term / homestay (Airbnb-style) | Different business logic; phân tích `short-vs-long-term-analysis.md` (D9) chứng minh bất khả thi kết hợp; schema keeps `property_type` open | Phase 1+ |
| Social / ranking feed | Tin-giả risk + empty-feed death on small supply (F2) | Use structured list + verified review instead |
| Built-in realtime messenger | Full messenger too costly (voice/sticker/poll/read-receipt); demo risk | **D24′ Property Chat** (Socket.io): chat riêng phòng + chung toà, bot auto-remind, `@issue`, `@mention` — KHÔNG full messenger (voice/sticker/poll/read-receipt outside MVP) |
| Bill splitting đầy đủ among roommates | Beyond MVP; D22: MVP = 1 HĐ đại diện (lead ký) + landlord config payment (rep-payer hoặc shared-invoice tracking phần góp); full split (D4) | Phase 1+ |
| Import feature (bulk room ops) | D19: user non-tech → drop; giữ export CSV/XLSX | Dropped (MVP) |
| ZNS / Zalo OA auto messaging | OA approval + fee + business verify risk (D7) | Phase 1+; FCM primary |
| Google Sheets 2-way API | Out of MVP scope (D7) | Import/export CSV/XLSX only |
| EVN/water utility API pull | No public API; ToS violation (F5) | OCR + manual confirm instead |
| Full-text RAG contract chatbot (pgvector) | Needs vector store + ingest pipeline | Phase 1+ stretch |
| Profile photo image-moderation | D28: text-only moderation in MVP; OCR image-moderation = stretch | Stretch goal |
| **Cleaning schedule (lịch vệ sinh)** | Thảo luận 27/08: skip MVP; có thể tái dùng Property Chat `@issue` (UC-L6) nếu revive ở Phase 1+ | Phase 1+ |
| **Full tạm trú/tạm vắng e-declaration** | D17: MVP chỉ lưu ảnh CCCD tại e-contract (3.1) + **OCR trích info (5.6, MVP)**; khai báo đầy đủ (tờ khai/in/xuất, nộp cơ quan) → Phase 1+, chờ C3 | Phase 1+ |
| CCCD OCR extraction | D17: **nâng thành MVP (31/08)** — tái dùng pipeline OCR công tơ | MVP (5.6) |
| Multi-currency · HĐĐT legal · smart recs · price suggestion | Data/legal dependent | Nice-to-have / Phase 1+ |

---

## Summary by priority

| Priority | Count | Features |
|----------|-------|----------|
| **MVP** | 27 | Core flows: room CRUD, **landlord realtime dashboard (1.3 + 3.7)**, OCR closing, auto-invoice, dynamic-QR recon, **utility rate config (3.11)**, search, pay, **Property Chat (D24′: `@issue` + issue card + `@mention`)**, e-contract (**template+upload wet-sign, no OTP/PIN (D18)** + CCCD capture), **CCCD OCR (5.6)**, roommate profile/match + **landlord constraints (4.7)**, AI auto-desc, auth |
| **Stretch** | 7 | Enhancements: room status, payment history, reminders, AI matchmaking score, notifications, profile photo-moderation, **tenant history/credibility (2.10, D26)** |
| **Nice-to-have** | 7 | Differentiators: photo gallery, messenger (deferred), chat, quiz, smart recs, price suggestion, multi-lang |

**MVP total complexity:** ~23 features, weighted average = Medium-High
**Recommended MVP scope:** Modules 1-3 (full MVP) + Module 4 (MVP only) + Module 5 (5.1 & 5.6 MVP) + Module 6 (incl. 6.6) — integration-first, long-term-only, cross-platform (D13).

---

## Source references

- `discovery/vision.md` — personas, value prop, success criteria (P0-03)
- `discovery/assumptions-risks.md` — constraints, risks, feasibility verdicts (P0-03)
- `discovery/decisions.md` — D1–D29 scope decisions (D12 skipped)
- `market-analysis.md` — competitor features & gaps
- `../requirement.md` — course requirements & proposed topic (scope SoT)
