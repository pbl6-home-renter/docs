# P1-13 — AI/roommate Matching: Full Lifecycle Flow Spec (search → ký → ẩn profile)

- **Assignee:** AI
- **Participants:** PM (scope D21/D22/D26/D28/D29), BE (API contract + DB design P1-18), Mobile (matching UX)
- **Priority:** Medium
- **Status:** 🟡 Open
- **Timebox:** Fri 04/09 → Mon 07/09
- **Sprint:** W4
- **Depends on:** P1-06 (AI feasibility finalized), D21 (landlord constraints-only), D22 (representative contract + payment config), D26 (tenant history consent), D28 (Stretch + spec), D29 (landlord-solo resilience)
- **Blocks:** AI module implementation (Phase 4), OpenAPI `/ai/matchmaking`, `discovery/ai-matching-spec.md`, provides DB fields to P1-18 (roommate/match tables)
- **Decision ref:** D28 (keep Stretch + write this spec), D29 (matching only for opted-in tenants)

> **Source of truth for the flow:** `pm/phase-0/user-behavior-workflow.md` (full rental lifecycle) + `discovery/decisions.md` (D21/D22/D26/D28/D29) + `feature-list.md` Module 2 + Module 4.
>
> **Note:** This flow covers the **tenant-with-account** journey end-to-end (search trọ → thấy ràng buộc chủ trọ → contact → tìm bạn → accept → ký → ẩn profile). Under **D29** the matching/pairing sub-parts only run for tenants who have an account; a passive tenant never appears in the pool and the landlord-solo lifecycle is unaffected (all matching parts are tenant-optional).

---

## 0. Overview — lifecycle stages

```
A. Tìm trọ (Map Search)
   │  (2.1 map / 2.2 filters / 2.3 detail)
B. Thấy ràng buộc của chủ trọ (D21 hard-filter) ──┐
   │                                              │
   └─ Quyết định: contact chủ trọ? ───────────────┘
         │ YES → liên hệ chủ trọ (in-app Property Chat D24′ / mở khóa SĐT·Zalo kênh ngoài) — quay lại A bất kỳ lúc nào
         │ NO  → vẫn cần phòng để ở ghép ↓
C. Tìm bạn cùng phòng (Roommate search 4.2 / match 4.3)
D. AI Matching pipeline (D28: rule-filter → LLM score + advice)
E. Accept / Kết nối (P2P, mở khóa liên hệ, SĐT/Zalo)
F. Ký hợp đồng (D18 template+wet-sign / D22 1 đại diện)
G. Ẩn profile cá nhân khi đã match + ký (privacy)
```

---

## A. Tìm trọ trên map (search)

**User behavior (Mobile — tenant active):**
1. Mở map (2.1) → thấy phòng trọ quanh vị trí.
2. Lọc nâng cao (2.2): giá, diện tích, tiện nghi, khoảng cách.
3. Mở chi tiết phòng (2.3): ảnh, giá, vị trí, thông tin chủ trọ; trạng thái phòng.

**Artifact:** một `Room` (`owner_id` NOT NULL — D25) đủ điều kiện `available` (không có HĐ active).

**D29 gate:** map search là điểm chạm landlord-side (web) hoặc tenant active (mobile); tenant passive bỏ qua trục này — landlord tự quản phòng như thường.

---

## B. Thấy ràng buộc của chủ trọ (D21 hard-filter) → quyết định contact

**User behavior:**
1. Trong detail room (2.3), hệ thống hiển thị **ràng buộc của chủ trọ** (`Room` constraints — D21):
   - `maxOccupancy` (max người/phòng)
   - `genderPolicy` (policy giới tính)
   - `houseRules` (nội quy)
   - `budgetRange` (mức giá khả năng chi trả)
2. Đây là **hard filter**: nếu tenant vi phạm bất kỳ ràng buộc nào → hệ thống **loại** khỏi pool match của phòng đó. Chủ trọ **không** duyệt/veto từng cặp cá nhân (PDPD-safe).
3. Tenant quyết định **contact chủ trọ hay không**:
   - **Contact:** liên hệ qua **Property Chat (D24′)** trong app, hoặc qua **SĐT/Zalo kênh ngoài** khi liên hệ được mở khóa (contact privacy gate).
   - **Không contact hoặc đang xem xét:** vẫn có thể đi tiếp tới tìm bạn ở ghép (nếu khả năng chi trả + ràng buộc phù hợp).

**Artifact:** tenant đã hiểu ràng buộc phòng; quyết định contact (Property Chat / kênh ngoài) và/hoặc vào pool match.

**Edge case — trượt ràng buộc:** tenant không đủ điều kiện hard-filter → UI báo rõ lý do (PDPD-safe, không loại người theo đánh giá chủ quan; chỉ áp constraint khai báo).

---

## C. Tìm bạn cùng phòng (roommate search)

**User behavior:**
1. Tenant tạo/hoàn thiện `RoommateProfile` (4.1): lifestyle, sleep schedule, pets, smoking, budget, gender pref. (Trường bắt buộc tối thiểu: gender, budget, smoking, pets, sleep schedule — D28.)
2. Browse profile đồng hương/khu vực (4.2), lọc theo phòng/quận.
3. Tạo `MatchRequest` → target là **room** hoặc **tenant B** (4.3).

**Artifact:** `RoommateProfile` + `MatchRequest`.

---

## D. AI Matching pipeline (D28)

1. **Rule-filter (hard) TRƯỚC:** loại ứng viên vi phạm ràng buộc của A (gender, budget range, smoking/pets incompatibility) — chạy trước, không gọi LLM → giảm số call.
2. **LLM scoring:** với mỗi cặp qua filter → `Matching Score %` + advice về thói quen (ngủ muộn, nuôi mèo…).
3. **Caching:** unique `(requester, target)` → tính 1 lần, tái dùng (~$0.02–0.03/cặp ở quy mô demo). Moderation **text-only** (MVP); OCR image-moderation = stretch.
4. **Surface:** list kết quả sắp theo score + explanation card trên Mobile.

**No candidates / conflicting hard rules:** xử lý như edge case — gợi ý lỏng constraint hoặc hiển thị rỗng có hướng dẫn.

---

## E. Accept / Kết nối (P2P)

**User behavior:**
1. Tenant A chọn 1 kết quả → **gửi match request** tới tenant B (P2P, 4.3).
2. Tenant B nhận + **accept** (hoặc reject).
3. Khi cả 2 đồng ý → mở khóa liên hệ (SĐT/Zalo) giữa 2 bên → trao đổi qua **kênh ngoài (SĐT/Zalo)** hoặc **Property Chat (D24′)**.

**Artifact:** cặp match accepted; liên hệ mở khóa.

---

## F. Ký hợp đồng (D18 / D22)

1. **1 hợp đồng đại diện** (lead tenant ký với landlord — D22).
2. Ký theo **D18**: app sinh mẫu HĐ (Word/PDF) → 2 bên **ký tay trên giấy** → landlord upload file đã ký làm artifact pháp lý. **Không** OTP/PIN/e-sign.
3. Landlord cấu hình payment: rep-payer (chia offline) hoặc shared-invoice tracking (D22).

---

## G. Ẩn profile cá nhân khi đã match + ký

**Quy tắc privacy (mới — viết rõ trong spec):**
- Khi một tenant **đã ký HĐ active** cho phòng (F hoàn tất), hệ thống **ẩn `RoommateProfile` của họ khỏi kết quả tìm kiếm bạn ở ghép** của người khác — họ không còn "đang tìm bạn".
- Nếu họ **chưa** ký (chỉ accept E) → profile vẫn hiển thị (họ vẫn đang tìm bạn).
- Ẩn theo chính chủ: có thể `hidden` flag hoặc derive từ trạng thái `Contract.status = active` + tham gia phòng đó.
- **D26 (consent):** lịch sử uy tín/credibility chỉ hiển thị khi tenant đồng ý; không cross-platform credit.
- **D29:** profile chỉ tồn tại cho tenant có account; passive tenant không xuất hiện.

**Edge case — bỏ giữa chừng:** nếu HĐ không ký, pool giữ nguyên; nếu stop match, tenant tự set profile hidden/tạm ẩn.

---

## 3. Decision Chain

`D1` (two-sided) → `D3` (provider-agnostic adapter) → `P1-06`/`D28` (AI feasibility + Stretch spec này, cold-start risk) → `D21` (landlord constraints-only, không veto) → `D22` (representative contract + payment config) → `D26` (tenant history consent) → `D29` (resilience: matching chỉ cho tenant opted-in; profile ẩn khi ký). Liên kết giao tiếp: `D24′` (Property Chat — realtime Socket.io + kênh ngoài mở khóa liên hệ).

## 4. Tasks (AI member)

- [ ] Enumerate `RoommateProfile` fields (required vs optional).
- [ ] Define rule-filter logic + LLM prompt (score % + advice), caching `(requester,target)`.
- [ ] Define **profile-visibility rule** (ẩn khi ký HĐ active + consent D26) in the pipeline.
- [ ] Define API request/response `/ai/matchmaking`.
- [ ] Edge cases: cold-start, no candidates, conflicting hard rules, profile-post-sign hide.
- [ ] Hand DB fields (RoommateProfile, MatchRequest, match result, visibility) to P1-18.
- [ ] Write `discovery/ai-matching-spec.md`.

## Deliverable

`discovery/ai-matching-spec.md` — full lifecycle flow (A→G), inputs, pipeline, caching, moderation, profile-visibility rule, API contract, edge cases, feasibility verdict.

## Definition of Done

- [ ] Full lifecycle A→G documented (search → constraints → contact → find roommate → accept → sign → hide profile).
- [ ] Pipeline + profile-visibility rule documented; API contract handed to BE.
- [ ] Feasibility verdict (Stretch) recorded; D28 + D29 satisfied.
- [ ] DB fields handed to P1-18 for schema design.
