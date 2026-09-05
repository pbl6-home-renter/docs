# P1-19 — User Flow: Verify & Finalize (tenant / landlord / admin / shared)

- **Assignee:** FE + Mobile (verify theo platform) · **BE** (data hand-off & schema) · **AI** (OCR/CCCD + match) · **PM** (chốt SoT)
- **Participants:** PM (scope D18/D21/D22/D25/D26/D29), FE (web-primary flows), Mobile (tenant + landlord-lite), BE (P1-18 alignment), AI (OCR/CCCD + AI match)
- **Priority:** High
- **Status:** 🟡 Open
- **Timebox:** Fri 04/09 → Mon 07/09
- **Sprint:** W4
- **Depends on:** P1-07 (business-rules freeze), P1-18 (DB schema), P1-01 (feature map)
- **Blocks:** P1-05 (UI design sitemap/wireframe input), Phase 2 (sitemap finalize)
- **Inputs:** `pm/phase-1/discovery/user_flow/{tenant-user-flow,landlord_user_flow,admin_user_flow,shared_user_flow}.md`

> **Source of truth (SoT):** `business-rules.md` (frozen P1-07) · `feature-list.md` (Modules 1–6) · `discovery/decisions.md` (D13/D16/D17/D18/D21/D22/D25/D26/D29).
>
> **Quan hệ với bản kiểm chứng A→Z cũ:** doc `phase-0/user-behavior-workflow.md` đã **bị xóa** (lệch nhiều so với quyết định hiện hành, 2026-09-06). `user_flow/` ở phase-1 là bản **duy nhất còn lại, chi tiết theo vai trò (per-role)** — dùng làm **navigation/UI SoT** cho P1-05. Mọi verify luồng giờ đối chiếu trực tiếp bản per-role này với `business-rules.md` + `decisions.md`.

---

## Goal

Xác nhận & hoàn thiện 4 user-flow (tenant / landlord / admin / shared) đối chiếu từng luồng với **business-rules đã frozen** — đóng bản **chi tiết theo vai trò** thành source of truth cho navigation/UI (P1-05) và tham chiếu chuẩn cho DB (P1-18) / realtime (P1-14) / AI (P1-13).

## Context

`user_flow/` vừa được thêm vào `pm/phase-1/discovery/` nhưng chưa được verify, chưa được trỏ tới từ bất kỳ navigation/index nào. Các luồng phải khớp 100% với business rules — đặc biệt:

- **D29 (landlord-solo):** mỗi flow tenant phải có nhánh passive/ngoài-app, không điểm chạm nào hard-depend vào tenant login.
- **D18:** HĐ chỉ `draft → active` khi upload file ký tay 2 bên; **không** OTP/PIN/e-sign.
- **D21:** chủ trọ set hard-filter (maxOccupancy/gender/houseRules/budgetRange), **không** veto từng cặp.
- **D22:** 1 HĐ đại diện + payment config linh hoạt (rep-payer / shared-invoice).
- **D25:** `Room.owner_id` NOT NULL; không manager/delegation.
- **D17/5.6:** CCCD OCR = MVP trong luồng e-contract.
- **D24′:** Property Chat (riêng phòng + chung tòa), bot, `@issue`, `@mention`, realtime + FCM offline.

## Tasks

### Rà & verify từng file
- [ ] **Tenant** (`tenant-user-flow.md`): BATCH 1–4 vs Module 2 (search/invoice/pay/chat/issue) + Module 4 (roommate) — Mobile verify + FE (web-secondary tenant).
- [ ] **Landlord** (`landlord_user_flow.md`): 7 phân hệ (BĐS/HĐ/chốt số/hóa đơn&QR/sự cố&chat/đơn giá) vs Modules 1,3,5,6 — FE verify (web-primary) + Mobile (landlord-lite).
- [ ] **Admin** (`admin_user_flow.md`): quản trị user + cấu hình hệ thống (mock payment, AI provider) vs D13 roles array — FE verify.
- [ ] **Shared** (`shared_user_flow.md`): auth/roles routing (admin/landlord/tenant) vs D13 — FE verify.

### Đối chiếu & chỉnh sửa
- [ ] Từng luồng đối chiếu `business-rules.md` §1–8; sửa điểm lệch; đánh dấu điểm lệch cần PM.
- [ ] **BE:** kiểm tra data hand-off & state trong từng flow khớp schema P1-18 (entity/status/enum).
- [ ] **AI:** verify luồng OCR công tơ (3.3) + CCCD (5.6) + AI match (D28) trong các flow liên quan.
- [ ] Ghi chú bất kỳ thay đổi scope/rule → chuyển PM qua change-control (không sửa business-rules khi chưa chốt).

### Chốt & đăng ký
- [ ] PM tổng hợp → đánh dấu 4 file **verified/finalized** (gắn status header) + ghi nhận là SoT cho P1-05.
- [ ] Đảm bảo phase-1 README + issues README + pm/README đều trỏ tới `discovery/user_flow/`.

## Deliverable

`pm/phase-1/discovery/user_flow/*.md` — 4 file đã review/hoàn thiện; mỗi file gắn status (🟡 draft → 🟢 verified/finalized) + ghi chú verify/tác giả/ngày.

## Definition of Done

- [ ] Mọi luồng trong 4 file khớp 100% `business-rules.md` (đặc biệt D29, D18, D21, D22, D25, D24′).
- [ ] Không còn điểm gãy/mâu thuẫn giữa các vai trò (cross-check shared ↔ landlord ↔ tenant ↔ admin).
- [ ] BE/AI/Mobile/FE xác nhận phần liên quan mình phụ trách.
- [ ] User-flow được trỏ tới từ phase-1 README + issues README + pm/README (+ phase-0 như tham chiếu).
- [ ] Ghi rõ đây là **SoT cho P1-05 / Phase 2 navigation**.

---

*Không làm Linear/GitHub/Apidog — PM tự nhắc.*
