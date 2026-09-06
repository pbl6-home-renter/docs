# Assumptions, Constraints & Risks — Giả định, Ràng buộc & Rủi ro (P0-03)

> **Status:** Draft for team review — Mon 24/08 EOD
> **Inputs:** interviews P0-01, `tech-feasibility.md`, `ai-feasibility.md`, thảo luận PM Sat 22/08

---

## 1. Assumption Log — Nhật ký giả định

| # | Giả định | Trạng thái | Bằng chứng / Hành động cần |
|---|---|---|---|
| A1 | Chủ trọ mục tiêu quản lý ≥10 phòng | ✅ Validated | Chú Hùng 25 phòng (Q12), Chị Mai 45 căn (Hà Nội) — P0-01 |
| A2 | Cả hai phía dùng smartphone + app ngân hàng/Zalo hằng ngày | ✅ Validated | 4/4 interviews |
| A3 | Chủ trọ sẵn sàng trả phí SaaS nhỏ (~100–150k/tháng) | ⚠️ Unvalidated | Chưa hỏi WTP trực tiếp → đưa vào customer interview (P0-07) |
| A4 | Người thuê chịu cài thêm app mới (app fatigue) | ⚠️ Unvalidated | Mitigation: giá trị hàng tháng (hóa đơn/báo sự cố) làm retention hook |
| A5 | OCR đọc số công tơ điện EVN/nước từ ảnh smartphone tầm trung đạt ≥90% | ⚠️ Unvalidated | Cần spike trước khi cam kết chỉ tiêu; degrade an toàn (D35): OCR tự điền → người dùng hiệu chỉnh tay nếu sai + lưu ảnh chứng cứ |
| A6 | VNPay sandbox ổn định đủ cho demo | 🔶 Partially | Sandbox miễn phí, đăng ký được; chưa test E2E → mock payment là lưới an toàn bắt buộc |
| A7 | Chi phí LLM nằm trong ngân sách sinh viên (<$30/tháng mức demo) | 🔶 Partially | Auto-Description validated ($24/tháng @1k calls đo thật); Matchmaking unvalidated (~$0.02–0.03/cặp có cache, suy từ analogy) |
| A8 | Hợp đồng điện tử: `template_upload` (up file wet-sign 2 bên = artifact pháp lý) + `e_ack` (PIN soft-acknowledgment, disclaimer "không giá trị pháp lý") chấp nhận được trong phạm vi đồ án | 🔶 Partially | Cơ chế chốt tại D18; vẫn open question cho thầy về mức chấp nhận của `e_ack` và quy trình upload |
| A9 | Dữ liệu demo do nhóm tự seed (không crawl tin đăng thật) | 📌 Internal | Confirm tại team review Mon 24/08 |
| A10 | Team 5 người available theo kế hoạch 13–14 tuần | ⚠️ Risky | Buffer week cuối + daily sync 15 phút |

---

## 2. Constraints — Ràng buộc

- Team 5 người cố định role: PM / FE / Mobile / BE / AI.
- Phase 0 kết thúc Thu **27/08** (presentation); tổng dự án 13–14 tuần.
- Payment sandbox-only: VNPay chính · MoMo stretch · mock payment bắt buộc cho demo.
- Testing demo-grade, không CI gates bắt buộc.
- LLM provider-agnostic (adapter OpenAI/Gemini, cấu hình env); ngân sách sinh viên.
- Deployment free-tier: Render (BE) + Neon (DB) + Vercel (FE) ≈ $0/tháng; ~$7 chỉ tuần demo nếu cần always-on.

---

## 3. Risk & Feasibility Register — Sổ rủi ro & phân tích tính khả thi

### 3.1 Các câu hỏi tính khả thi trọng yếu (F1–F8)

#### F1 — Matchmaking: triển khai có khả thi không?
- **Phân tích:** Kiến trúc y hệt Auto-Description đã test PASS (2 hồ sơ jsonb → LLM → `{score, advice}`), tái dùng FastAPI service + adapter provider-agnostic. Chi phí ~$0.02–0.03/cặp; unique constraint `(requester, target)` cho phép **cache mỗi cặp chỉ tính 1 lần** → quy mô demo gần như miễn phí. Rủi ro thật nằm ở marketplace cold-start (ít hồ sơ thật cùng khu vực/thời điểm), không phải code.
- **Verdict:** ✅ Khả thi — spike khuyến nghị trước khi code nhưng không blocker.
- **Mitigation:** hybrid rule-filter ràng buộc cứng trước → LLM chấm điểm; moderation **text-only** ở MVP (kiểm duyệt ảnh OCR = stretch); seed ≥10 profile/khu vực; success criteria chỉ đo trên pool seed (<15s), không đo growth.

#### F2 — Có nên xây "feed" trọ/căn hộ?
- **Phân tích:** Feed kiểu xã hội đòi hỏi ranking + kiểm duyệt nội dung liên tục — chi phí vận hành lớn. Bằng chứng đối thủ: tin đăng dạng feed bị nhiễu cò mồi/quảng cáo (Chợ Tốt, feed bạn-ở-ghép của Rencity/Ohana — `p0-02/discovery-ux-mobile.md` §1.1/§2.2); pain #5 của tenant chính là **tin giả**. Supply ban đầu nhỏ → feed trống làm app chết ngay lần mở đầu tiên.
- **Verdict:** ❌ Không làm feed social trong MVP.
- **Hướng thay thế:** danh sách tìm kiếm có cấu trúc (list + filter + map + wishlist) cho phòng; tăng discovery bằng **verified review gắn lịch sử ở thật** + badge "phòng từ chủ trọ dùng app" thay vì thuật toán feed.

#### F3 — Tích hợp cổng thanh toán: khả năng tương thích?
- **Phân tích:** VNPay sandbox (redirect + IPN, HMAC SHA512, ví dụ NestJS nhiều) và MoMo (SHA256, ít ví dụ hơn) tương đương nhau ~2–3 ngày BE effort — tách interface `PaymentGateway` (strategy pattern) để hoán đổi không đụng core. Điểm rủi ro thật là **auto-reconciliation qua chuyển khoản ngân hàng**: ngân hàng không cấp webhook trực tiếp cho sinh viên → phải đi qua aggregator (PayOS/SePay/VietQR Pro) — phụ thuộc bên thứ ba, free tier có thể thay đổi bất kỳ lúc nào.
- **Verdict:** ⚠️ Khả thi có kiểm soát.
- **Mitigation:** VNPay chính + MoMo stretch + mock payment bắt buộc; luồng dự phòng luôn sống: tenant bấm "Đã thanh toán" → landlord xác nhận thủ công; aggregator để stretch goal.

#### F4 — Tích hợp API Zalo?
- **Phân tích theo 3 tầng:**
  1. *Share-intent / deep-link* sang Zalo — miễn phí, không cần duyệt, hoạt động ngay trên Android/Web Share API.
  2. *Zalo Login SDK* (đăng nhập bằng Zalo) — khả thi, giảm rào cản onboarding cho chủ trọ low-tech.
  3. *ZNS / Zalo OA* (nhắn template tự động) — cần đăng ký OA + duyệt template + phí ~400–800đ/tin; rủi ro trễ duyệt và xác minh doanh nghiệp.
- **Verdict (đã cập nhật):** Share-intent/deep-link sang Zalo **không còn là kênh sản phẩm** (D24′ loại Zalo khỏi app); Zalo Login SDK 🔶 stretch; **ZNS / Zalo OA** (nhắn template tự động) ❌ out-of-scope MVP → Phase 1+ (chỉ như kênh ngoài app, không tích hợp trong app — D7).
- **Mitigation:** FCM push là kênh thông báo chính của app; liên hệ ngoài app qua SĐT/Zalo chỉ khi người dùng tự mở khóa (contact privacy gate, D24′).

#### F5 — Tích hợp API điện/nước để lấy số công tơ theo mã hợp đồng/khách hàng?
- **Phân tích:** EVN **không có public API chính thức** cho bên thứ ba (mỗi miền một portal/app CSKH riêng, endpoint không ổn định, scrape vi phạm ToS); nước do từng công ty địa phương quản lý, hầu như không có API; đồng hồ thông minh chỉ phổ biến ở chung cư mới — không phải đối tượng nhà trọ/sinh viên. Mã khách hàng/mã điểm đo hiện không truy vấn được từ hệ thống ngoài.
- **Verdict:** ❌ Không khả thi cho MVP → xác nhận **OCR ảnh công tơ + bước xác nhận tay là lựa chọn đúng** (và chính là điểm kế thừa-tăng-cược so với Mona House).
- **Mitigation:** thêm field rẻ `evn_customer_code` per room để tenant/chủ tự link-out tra cứu trên app EVN; revisit dịch vụ aggregator ở Phase 1+ nếu xuất hiện.

#### F6 — Built-in chat hay tận dụng Zalo?
- **Phân tích:** Chat đầy đủ (socket gateway + sync đa thiết bị + cache mobile + moderation) tốn ~10–16 người-ngày (~5–8% effort dự án), WebSocket không tài liệu hóa gọn trong Swagger/Apidog, rủi ro demo cao (Android kill background, reconnect). Trong khi đó chỉ 1/3 nhu cầu giao tiếp thực sự cần hội thoại tự do — phần Zalo đã đáp ứng sẵn.
- **Verdict (đã chốt D24′ — Property Chat, ngày 29/08):** thầy muốn hệ sinh thái socket → chọn **Property Chat** (không full messenger): chat riêng phòng + chung toà, Socket.io realtime khi app mở, **bot auto-remind + `@issue` + `@mention`**, message text/image/file/bot; **FCM + DB persistence làm baseline chống chịu** (D29); **loại Zalo khỏi kênh**. Voice/sticker/poll/read-receipt ngoài MVP. Effort ~3 tuần/team (TBD member xác nhận — `realtime-feasibility.md`).

#### F7 — E-contract PDF + upload file đã ký (template_upload) + PIN soft-ack (e_ack)?
- **Phân tích:** PDF text-based parse được bằng pdf-parse/pdfjs; PDF scan ảnh cần OCR (tái dùng pipeline chốt số công tơ). **Artifact pháp lý = `template_upload`**: app sinh mẫu HĐ → 2 bên ký giấy → landlord upload file đã ký → hệ thống lưu làm chứng cứ (D18). **`e_ack`**: PIN in-app chỉ là xác nhận đọc/đồng ý, disclaimer rõ "không có giá trị pháp lý". Case "bên từ chối ký" không dead-end → rơi về template_upload. Chi phí $0.
- **Verdict:** ✅ Khả thi với chi phí $0 (quyết định D18).
- **Mitigation:** mật khẩu ký lưu bcrypt hash + rate-limit thử sai; ưu tiên text-based PDF, scan-ảnh degrade sang OCR + bước xác nhận tay field; luôn lưu file gốc làm chứng cứ tranh chấp.

#### F8 — Chatbot hỏi đáp hợp đồng: RAG hay Explainer?
- **Phân tích:** RAG thật (chunking + pgvector + embeddings API) tốn ~1.5–2.5 tuần + dependency mới + rủi ro ảo giác trên văn bản pháp lý. Trong khi nhu cầu thực tế ("tiền cọc bao nhiêu", "giá điện thế nào", "hạn chấm dứt khi nào") nằm trọn trong field có cấu trúc đã trích từ PDF (F7/D18).
- **Verdict:** ✅ MVP = **Contract Explainer** từ field (LLM diễn đạt lại, grounding tuyệt đối, ~2–3 ngày, tái dùng adapter D3); ❌ RAG thật → Phase 1+ stretch (pgvector tái dùng Postgres) — quyết định D15.

### 3.2 Rủi ro vận hành còn lại (nén gọn — mitigation đã chốt sẵn)

| # | Rủi ro | L×I | Mitigation |
|---|---|---|---|
| R1 | Sandbox thanh toán sập/hết hạn lúc demo | M×H | Mock toggle (`ENABLE_MOCK_PAYMENT`) + kịch bản offline |
| R2 | Chi phí token / rate-limit LLM | M×M | Cache, giới hạn calls, rule-based fallback |
| R3 | Scope creep (feed, homestay, chia tiền, RAG thật...) | H×H | MVP freeze tại P0-06; D9 chặn homestay; D4/D28/D15 chặn biên giới |
| R4 | OpenAPI/Apidog drift giữa BE ↔ FE/Mobile (phình thêm khi 1 endpoint phục vụ 2 client × 2 platform theo D13) | M×M | URL sync tự động + protocol breaking change |
| R5 | Cold start Render lúc demo / DB free 30 ngày | M×M | Keep-alive ping hoặc $7 Starter tuần bảo vệ; DB đã chuyển Neon |
| R6 | Availability thành viên (thi cọc, lịch học) | M×H | Buffer week cuối + daily EOD sync 15' |
| R7 | Effort FE tăng ~40–60% theo D13 (2 role × 2 platform) + QA matrix phình | M×H | Staging primary → secondary; secondary chỉ bắt đầu khi primary chạy E2E |
| R8 | Tenant không login → matching pool trống — D29 landlord-solo là chính | L×H | Landlord solo ops (D29); seed ≥10 profiles demo (D28); cold-start = accepted edge case, không blocker |
| R9 | Kỳ vọng/thầy muốn socket "realtime" → **D24′ Property Chat** (Socket.io) được chọn theo yêu cầu thầy; nhưng realtime chỉ khi app mở, **FCM + DB persistence là baseline chống chịu** (D29) — giảm rủi ro phụ thuộc socket | L×M | Chốt D24′; giữ FCM offline + DB persistence; fallback nếu socket lỗi demo = load history từ DB; explain cho thầy rằng realtime = socket chỉ khi mở app, còn offline vẫn đủ qua FCM |
| R10 | Ownership DB model chưa chốt (P1-12 D25) → business-rules §1 Room/Building blocked | M×M | D25 direction đã đồng ý; BE finalize ERD trước P1-07 freeze |
| R11 | PDPD consent flows chưa build: CCCD (D17), consent banner cho history/matching (D26/D21), right to delete | M×H | Tất cả data features đều consent-based (D17/D21/D26); implement consent banner + delete flow trước khi collect data |

---

## 4. Open Questions — Câu hỏi mở

**Cho thầy:**
1. AI provider có bị ràng buộc không (OpenAI API hay Gemini/provider khác đều chấp nhận)?
2. Hợp đồng điện tử ký OTP có cần phân tích pháp lý, hay demo-grade là đủ?
3. Trọng số chấm giữa SE artifacts vs demo vs AI?
4. **Hạ tầng & công cụ triển khai:** xem danh sách đầy đủ 17 mục tại `product-sketch.md` §7 (repo GitHub, Linear, Notion, Drive, Apidog, deploy free-tier, LLM key/ngân sách, VNPay sandbox…). Nhờ thầy **cung cấp/bảo trợ**; nếu không, nhóm **tự lo free-tier** (risk tương ứng ở `PROJECT_PLAN.md` §6).

**Cho khách/chủ trọ (customer interview tiếp):**
4. WTP bao nhiêu nghìn đồng/tháng cho gói quản lý?
5. Nhắc nợ qua app + kênh ngoài 1 chạm đã đủ, hay cần kênh template tự động (vd ZNS/Zalo OA ngoài app)?
6. Tính tiền điện nước: flat-rate đủ dùng, hay bắt buộc bậc thang EVN?

**Nội bộ:**
7. Ai làm spike OCR + matchmaking, trước ngày nào?
8. Tên sản phẩm ([Tên app] đang placeholder)?
9. Quy mô seed data demo (số phòng/profile) để demo đẹp?
