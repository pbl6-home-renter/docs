# Product Sketch — PBL6

> **Purpose:** customer-ready sketch consolidated from P0-03 discovery (`discovery/vision.md`, `discovery/assumptions-risks.md`, `discovery/decisions.md` D1–D29) + `feature-list.md`.
> Walk through in ~30 min with the customer; incorporate feedback into `../requirement.md` (scope SoT).

## 1. Problem & target users

- **Landlords (web):** manage contracts, utility (electricity/water) closing, invoices, payments — today done on paper/Excel, error-prone.
- **Tenants (mobile):** find rooms on a map, receive monthly invoices, pay online, find a compatible roommate, report issues.
- **Pain points (evidence from P0-01 interviews, quoted in `discovery/vision.md` §2):**
  - *Landlord — Chú Hùng (25 rooms):* "Đối soát chuyển khoản thủ công, gạch nhầm/bỏ sót (pain #1 — F5×S4=20)"; "Leo thang soi đèn pin, chép tay nhầm số 3 thành 8 (pain #2 — F5×S3=15)"; "Ngại nhắn tin đòi nợ trực tiếp"; "Đã xóa app vì 'danh mục tài sản, khấu hao... nhức hết cả đầu'".
  - *Landlord — Chị Mai (45 service apartments):* "Quên hạn hợp đồng trên Google Sheets → phòng trống 2–3 tuần"; "Trả phòng cãi nhau vì thiếu bằng chứng hiện trạng ban đầu"; "Khách nhắn liên tục giờ hành chính/lúc nửa đêm".
  - *Tenant — Minh (student):* "Bạn bùng nợ, phải gánh thay (F3×S5)"; "Thu 4.500đ/số, công tơ 'nhảy vọt' không giải trình được"; "Bị soi vết tróc sơn để trừ cọc oan".
  - *Lifecycle break (vision §1):* "Sau ngày ký hợp đồng, mọi việc quay về thao tác tay: soi đèn pin chép số công tơ, dò từng dòng sao kê gạch nợ, cọc bị giam oan khi trả phòng — vòng đời thuê đứt gãy ngay giai đoạn 'Ở'."

## 2. Product positioning

**One-line value proposition (from `discovery/vision.md` §1):** [Tên app] là nền tảng quản lý cho thuê hai chiều, tự động hóa trọn vòng tháng (OCR chốt số, sinh hóa đơn, nhắc nợ, đối soát QR động) dưới 10 phút cho 10 phòng; kết quả đẩy về đúng nơi user ở (kênh ngoài/Excel), trên dữ liệu minh bạch hai chiều để hết tranh chấp.

**How we differ (from `discovery/vision.md` §1 Unlike + `market-analysis.md` gap #3):** Khác với Mona House hay KiotViet vốn chỉ phục vụ một chiều chủ nhà, [Tên app] dành cho người thuê một cổng riêng: nhận hóa đơn minh bạch, báo sự cố kèm ảnh, tìm bạn ở ghép tương thích — cùng cơ chế **VietQR động định danh + gạch nợ tự động** mà chưa nền tảng nội địa nào có (gap #3).

## 3. Scope — MVP

- **Web (React — D13: Primary landlord ops console; Secondary tenant responsive portal):**
  - **Dashboard chủ trọ:** lịch phòng trống/đang thuê trực quan + biểu đồ doanh thu/công nợ realtime (D20); room/building list + room-map status (empty/occupied)
  - E-contract creation & management — app **sinh mẫu HĐ (Word/PDF)**, 2 bên **ký tay trên giấy**, user **up file đã ký (wet-sign 2 bên)** làm chứng cứ pháp lý; **bỏ OTP/PIN** (D18)
  - Monthly **OCR utility closing + 1-tap confirm** → auto invoice → payment status tracking (F5: OCR not utility-API)
  - **Dynamic named-QR + auto-reconciliation** (core differentiator, vision §1)
  - Revenue/cost statistics
  - Tenant secondary: view invoices, pay, report issues, find roommate
- **Mobile (Kotlin/Android — D13: Primary tenant portal; Secondary landlord lite: FCM push, duyệt sự cố, xem dashboard/hóa đơn):**
  - Map-based search + advanced filters
  - Monthly invoice + payment (VNPay/Momo) + dynamic-QR pay
  - "Find a roommate" profile & match request (D28)
  - Issue reporting + **Property Chat riêng phòng** (D24′: realtime Socket.io + bot auto-remind + `@issue` + `@mention`; FCM offline; loại Zalo khỏi kênh)
- **AI (FastAPI, provider-agnostic adapter — OpenAI/Gemini via env, D3):**
  - *Auto-Description* (MVP): keywords → PR text; rule-based fallback
  - *Matchmaking* (Stretch, D28): hybrid rule-filter → LLM score + advice; text-only moderation; seed ≥10 profiles

## 4. Key flows (sketch level)

1. Landlord creates room → tenant finds it on map → applies → e-contract signed (keyword: wet-sign upload của file ký tay 2 bên, D18) → move in. *(Under D29 these tenant steps are optional — landlord can run the whole flow solo; tenant reached via kênh ngoài/QR/cash.)*
2. Monthly: landlord OCR-closes utility meters (+1-tap confirm) → system auto-generates invoice → tenant pays via VNPay/Momo or dynamic named-QR → auto-reconciliation.
3. Tenant builds roommate profile → gets AI match score + advice → contacts candidate via external channels (SĐT/Zalo khi 2 bên đồng ý).

## 5. Non-goals / out of scope for MVP

  - Short-term / homestay (Airbnb-style) — D9: long-term-only; phân tích `short-vs-long-term-analysis.md` chứng minh bất khả thi kết hợp (schema keeps `property_type` open cho Phase 1+)
- Social / ranking feed — F2: tin-giả risk + empty-feed death on small supply
  - Full realtime messenger ngoài Property Chat — D24′: chỉ chat phòng + chung toà + bot/command; voice/sticker/poll/read-receipt out-of-scope MVP
  - **Landlord-can-operate-solo resilience (D29, mandatory):** hệ thống chạy được khi tenant không login; landlord làm toàn bộ vòng đời một mình, tenant app optional/passive (payment = cash / dynamic-QR quét bằng app ngân hàng bất kỳ)
- Bill splitting among roommates — D4 → Phase 1+
- ZNS / Zalo OA auto messaging — D7 → Phase 1+ (FCM primary)
- Google Sheets 2-way API — D7: import/export CSV/XLSX only
- EVN/water utility API pull — F5: OCR + manual confirm instead
- Full-text RAG contract chatbot (pgvector) — D15 bỏ; thêm lại Phase 1+ nếu có nhu cầu
- Profile photo image-moderation — D28: text-only moderation (OCR image-moderation = stretch)
- Multi-currency · HĐĐT legal · smart recs · price suggestion — nice-to-have / Phase 1+

## 6. Open questions for the customer

  - **For teacher:** (1) AI provider có bị ràng buộc không (OpenAI/Gemini đều chấp nhận — D3)? (2) ~~Hợp đồng điện tử ký PIN có cần phân tích pháp lý~~ **ĐÃ CHỐT (D18, 31/08):** chữ ký số/OTP/PIN KHÔNG có giá trị pháp lý → app sinh mẫu HĐ + 2 bên ký tay giấy + user up file đã ký; **bỏ OTP/PIN/soft-ack hoàn toàn**. (3) Trọng số chấm giữa SE artifacts vs demo vs AI? (4) **Hạ tầng & công cụ cần thiết** → xem **§7** bên dưới (xin thầy bảo trợ; nếu không, nhóm tự lo free-tier).
   - **For customer (P0-07):** (4) WTP bao nhiêu nghìn đồng/tháng? (5) Nhắc nợ qua kênh ngoài app 1 chạm đã đủ, hay cần ZNS? (6) Tính tiền điện nước: flat-rate đủ, hay bắt buộc bậc thang EVN? (7) **Khai báo tạm trú/tạm vắng:** MVP lưu ảnh CCCD tại e-contract (3.1) + research API dịch vụ công (D17/P1-15); implement Phase 1+. (8) **Lịch vệ sinh:** đã chốt skip MVP (Phase 1+ nếu có nhu cầu).
- **Internal:** (7) Ai làm spike OCR + matchmaking? (8) Tên sản phẩm? (9) **Quy mô & nguồn seed data demo?** — hiện tại chưa có user thật, nên cần **seed sẵn dữ liệu trọ (phòng/tòa nhà có toạ độ) trên map** để phục vụ demo môn học (luồng map-search của tenant + dashboard landlord). Quyết định quy mô (ví dụ ≥10 phòng, ≥N tòa nhà quanh 1 khu vực) và cách生成 (script seed / Faker / crawl公开). (10) **Nguồn dữ liệu landlord đầu vào ở đâu?** — phòng/tòa nhà/hợp đồng/công tơ lấy từ đâu (nhập thủ công trên web, import CSV/Excel từ Excel hiện tại của Chú Hùng/Chị Mai, hay hệ thống nguồn)? Ảnh hưởng schema seed + luồng onboarding landlord (P1-07 + Phase 3 scaffold).

## 7. Hạ tầng & công cụ cần thiết (trình thầy)

> Mục đích: xin thầy **bảo trợ/cung cấp** các tài khoản & hạ tầng dưới. Nếu không được, nhóm sẽ **tự triển khai bản free-tier** (đánh dấu "Tự lo"). Đây là câu hỏi mở (4) dành cho thầy ở §6.
> Hai mục nên ưu tiên xin thầy: **(10) LLM API key/ngân sách** và **(11) VNPay sandbox** — cần tài khoản pháp nhân / khó tự lo.

| # | Hạng mục | Công cụ đề xuất (free-tier) | Mục đích trong dự án | Xin thầy / Tự lo |
|---|----------|------------------------------|----------------------|------------------|
| 1 | Source control | GitHub — 4 repos (web/mobile/backend/ai) + branch protection | Lưu code, PR review | Xin thầy / tự tạo |
| 2 | Database | PostgreSQL — Neon (serverless free); dev local: Docker Postgres | Lưu room/contract/invoice/user… | Tự lo (Neon free, supabase) |
| 3 | Server BE | Render Web Service (free) hoặc Railway/Fly.io | Chạy NestJS API | Xin thầy |
| 4 | Server AI | Render Web Service (hoặc chung BE) | Chạy FastAPI (adapter D3) | Xin thầy |
| 5 | Hosting FE | Vercel | Deploy React web (landlord) | Xin thầy |
| 6 | Mobile distro | APK qua Google Drive / Firebase App Distribution | Cài app tenant demo | Tự lo |
| 7 | Domain + DNS | Cloudflare (DNS+SSL free) + domain tuỳ chọn (hoặc `*.vercel.app`/`*.onrender.com`) | Web + API (`api.`/`ai.`) | Tự lo |
| 8 | Object Storage | Cloudflare R2 / Supabase Storage / Firebase Storage | Ảnh phòng, ảnh công tơ (OCR), scan hợp đồng, avatar | Tự lo (free-tier) |
| 9 | Push Notification | Firebase Cloud Messaging (FCM) — cần Firebase project + server key | Thông báo hóa đơn/hợp đồng/sự cố (D7) | Tự lo (miễn phí) |
| 10 | AI / LLM | OpenAI **hoặc** Gemini API key + ngân sách (adapter D3) | Auto-Description, Matchmaking | **Xin thầy** / tự (cá nhân) |
| 11 | Payment sandbox | VNPay sandbox (bắt buộc); MoMo sandbox (stretch) | Demo thanh toán + dynamic-QR | **Xin thầy** / tự đăng ký sandbox |
| 12 | Maps / Geo | Google Maps SDK / Mapbox / OSM (tile + geocoding) | Tìm phòng trên bản đồ (2.1) | Tự lo (API key free) |
| 13 | API contract | Swagger/OpenAPI (trong NestJS) + Apidog (sync) | Chuẩn hoá API, demo SE | Tự lo |
| 14 | CI/CD | GitHub Actions (build/test/deploy) | Tự động hoá deploy | Tự lo |
| 15 | PM / Wiki / Submit | Linear (hoặc GitHub Projects) · Notion · Google Drive | Task, quyết định, nộp bài | Xin thầy / tự lo |
| 16 | Monitoring | Render/Vercel logs · UptimeRobot/Better Stack (free) | Theo dõi demo | Tự lo |
| 17 | Team comms | Zalo (free) + FCM | Giao tiếp team & người dùng | Tự lo |
