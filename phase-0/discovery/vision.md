# Product Vision & Strategy — Tầm nhìn & Chiến lược sản phẩm (P0-03)

> **Status:** Draft for team review — Mon 24/08 EOD
> **Inputs:** `P0-01-user_research.md`, `market-analysis.md`, `p0-02/ux-web.md`, `p0-02/discovery-ux-mobile.md`, `tech-feasibility.md`, `ai-feasibility.md`
> **Ngôn ngữ:** thân tiếng Việt, tiêu đề song ngữ Việt–Anh (quyết định D5 trong `decisions.md`)

---

## 1. Vision Statement — Tuyên bố tầm nhìn

*(Geoffrey Moore template: For / Who / What+Why / Unlike — đã duyệt Sat 22/08)*

> **For:** Dành cho **sinh viên và người đi làm** đang thuê phòng trọ, căn hộ mini tại đô thị — cùng những **chủ trọ quản lý 10–100 phòng** (từ chú chủ dãy quen sổ tay và Zalo đến bà quản lý chuyên nghiệp) đang phục vụ họ.
>
> **Who:** Sau ngày ký hợp đồng, mọi việc quay về thao tác tay: soi đèn pin chép số công tơ, dò từng dòng sao kê gạch nợ, cọc bị giam oan khi trả phòng — những việc máy móc mà Zalo và Excel quen thuộc không tự làm thay được: vòng đời thuê đứt gãy ngay giai đoạn "Ở".
>
> **What + Why:** [Tên app] là **nền tảng quản lý cho thuê hai chiều**, tự động hóa trọn vòng tháng — chốt số bằng OCR ảnh công tơ, sinh hóa đơn, nhắc nợ, đối soát tự động qua QR định danh — dưới 10 phút cho 10 phòng; kết quả đẩy về đúng nơi người dùng đang ở (nhắc nợ qua app + kênh ngoài, báo cáo ra Excel), trên nền dữ liệu minh bạch hai chiều để hết tranh chấp tiền bạc.
>
> **Unlike:** Khác với Mona House hay KiotViet vốn chỉ phục vụ một chiều chủ nhà, [Tên app] dành cho người thuê một **cổng riêng**: nhận hóa đơn minh bạch, báo sự cố kèm ảnh, tìm bạn ở ghép tương thích — cùng cơ chế **VietQR động định danh + gạch nợ tự động** mà chưa nền tảng nội địa nào có.

**English rendering (for report):**
For urban students and young professionals renting rooms and mini-apartments in big cities — and for the landlords managing 10–100 units who serve them, from notebook-and-Zalo owners to professional service-apartment hosts. After the contract is signed, everything falls back to manual work: flashlight meter readings, bank-statement reconciliation by hand, unfairly withheld deposits — mechanical tasks that familiar tools like Zalo and Excel cannot automate: the rental lifecycle breaks at the "living" stage. [App name] is a two-sided rental management platform that automates the entire monthly cycle — OCR meter reading, invoicing, payment reminders, automatic reconciliation via personalized QR codes — in under 10 minutes per 10 rooms, delivering results where users already are (reminders through the app and external channels, reports exportable to Excel) on transparent two-sided data. Unlike one-sided landlord tools such as Mona House or KiotViet, [App name] gives tenants their own portal — transparent invoices, photo-based issue reporting, compatible roommate matching — plus dynamic named-QR auto-reconciliation no domestic platform offers. *(Under D29 resilience the tenant portal is optional/passive: the platform still runs end-to-end if tenants never log in — landlord operates solo via external channels/QR/cash.)*

**Traceability:** mỗi chi tiết đều trace về research — "đèn pin/soi sao kê" (phỏng vấn Chú Hùng), "cọc bị giam" (Linh/Mai), "<10 phút/10 phòng" (pain #1+#2 landlord = 35 điểm), "chưa nền tảng nội địa nào" (`market-analysis.md` gap #3).

---

## 2. Value Proposition — Bản đề xuất giá trị theo persona

### Persona 1 — Chú Hùng (chủ trọ truyền thống, 25 phòng, tech-comfort thấp)

| Jobs-to-be-done | Pains (bằng chứng P0-01) | Gains | Feature đáp ứng |
|---|---|---|---|
| Thu đủ tiền phòng + điện nước đúng hạn mỗi tháng | Đối soát chuyển khoản thủ công, gạch nhầm/bỏ sót (pain #1 — F5×S4=20) | Tiền về đúng hạn, hết cảnh "quê muốn chết" khi đòi nhầm | QR định danh từng phòng → webhook ngân hàng **gạch nợ tự động** |
| Chốt điện nước hàng tháng không sai | Leo thang soi đèn pin, chép tay nhầm số 3 thành 8 (pain #2 — F5×S3=15) | Không leo trèo, số liệu có ảnh đối chứng | **OCR chốt số bằng ảnh công tơ** + bước xác nhận 1 chạm |
| Nhắc nợ mà không ngại ngùng | Ngại nhắn tin đòi nợ trực tiếp | Nhắc nợ "máy móc", khách không mất mặt | Hóa đơn tự sinh → **nhắc tự động + QR định danh / kênh ngoài app 1 chạm** |
| Dùng được ngay, không rối | Đã xóa app vì "danh mục tài sản, khấu hao... nhức hết cả đầu" | Mở app là làm được việc | UI tiếng Việt tối giản, **import CSV/XLSX** từ dữ liệu sẵn có |

### Persona 2 — Chị Mai (quản lý căn hộ dịch vụ, 45 căn, tech-savvy)

| Jobs-to-be-done | Pains (bằng chứng P0-01) | Gains | Feature đáp ứng |
|---|---|---|---|
| Giữ occupancy >90% | Quên hạn hợp đồng trên Google Sheets → phòng trống 2–3 tuần | Chủ động gối đầu khách mới | **Cảnh báo hết hạn hợp đồng trước 30–45 ngày** |
| Bàn giao minh bạch, không tranh chấp cọc | Trả phòng cãi nhau vì thiếu bằng chứng hiện trạng ban đầu | Trừ cọc có căn cứ, giữ quan hệ khách | **Biên bản bàn giao kèm ảnh có timestamp** |
| Chuẩn hóa xử lý sự cố | Khách nhắn liên tục giờ hành chính/lúc nửa đêm | Ticket có trạng thái, xử lý theo thứ tự | **Tenant portal báo sự cố kèm ảnh + theo dõi tiến độ** |
| Vận hành chuyên nghiệp như SaaS | Quản lý phân mảnh nhiều công cụ | Dashboard doanh thu, báo cáo đẹp | **Dashboard thống kê + export Excel** |

### Persona 3 — Minh (sinh viên ở ghép, Gen Z tenant)

| Jobs-to-be-done | Pains (bằng chứng P0-01) | Gains | Feature đáp ứng |
|---|---|---|---|
| Tìm bạn ở ghép hợp tính | Bạn bùng nợ, phải gánh thay (F3×S5) | Sàng lọc trước khi dọn vào chung | **Hồ sơ tag-based + AI match score & lời khuyên** |
| Kiểm tra điện nước không bị kê khống | Thu 4.500đ/số, công tơ "nhảy vọt" không giải trình được | Tự đối chiếu được trước khi trả tiền | **Hóa đơn kèm ảnh công tơ cũ/mới đối chiếu** |
| Giữ tiền cọc khi chuyển đi | Bị soi vết tróc sơn để trừ cọc oan | Có bằng chứng hiện trạng lúc dọn vào | **Nhật ký hiện trạng + báo sự cố có timestamp** |

> **Lưu ý scope:** chia tiền ở ghép giữa các thành viên phòng → **Phase 1+** (quyết định D4). Tìm bạn ở ghép giữ Stretch với biên giới chốt tại D28.

---

## 3. Stakeholders — Các bên liên quan

| Bên liên quan | Influence | Needs |
|---|---|---|
| **Thầy cô (grading)** | Cao — định hình tiêu chí đạt môn | SE process artifacts (DB design, diagrams), Swagger/Apidog chuẩn, demo E2E chạy thật, AI integration nhẹ nhàng nhưng thật |
| **Chủ trọ (khách hàng trả tiền)** | Cao — quyết định "sản phẩm có đáng dùng" | Giảm thời gian vận hành, dòng tiền về đúng hạn, onboarding không cần đào tạo |
| **Người thuê (end user)** | Trung bình–cao — quyết định adoption phía mobile | Minh bạch điện nước/cọc, kênh phản ánh sự cố được hồi âm |
| **Admin (nhóm phát triển)** | Thấp–trung | Seed data demo, kiểm duyệt hồ sơ tìm bạn ở ghép |

---

## 4. Success Criteria — Tiêu chí thành công

### 4.1 Course success / Thành công học phần
- Demo E2E chạy live không lỗi: tạo tòa nhà → hợp đồng → chốt số (OCR) → sinh hóa đơn → thanh toán VNPay sandbox → biên nhận điện tử.
- Đủ SE artifacts theo rubric: DB schema, use case/diagrams, OpenAPI spec đồng bộ Apidog.
- 4 repos tích hợp chạy được end-to-end: web (landlord) + mobile (tenant) + BE (NestJS) + AI service (FastAPI).

### 4.2 Product success / Thành công sản phẩm (đo được, không dùng tính từ)
- Chủ trọ đóng vòng tháng ≤ **10 phút** cho 10 phòng (từ chốt số → bill gửi đi).
- ≥ **80%** hóa đơn trong demo được thanh toán online end-to-end.
- OCR đọc đúng ≥ **90%** trên ảnh công tơ rõ nét; **luôn có bước xác nhận tay** trước khi tính tiền.
- Match request trả kết quả < **15 giây** trên pool seed ≥ **10 profile**; **100%** cặp trong demo hiển thị score + lời khuyên.
- AI Auto-Description p95 < **10 giây**; fallback rule-based hoạt động khi API lỗi.

---

## 5. Product Principles — Nguyên tắc sản phẩm (Integration-first)

1. **Delegate the external communication layer, own the data & computation layer (D24′).** FCM push = kênh thông báo offline; app **own** phần máy móc: OCR chốt số, sinh hóa đơn, đối soát QR/webhook, vòng đời hợp đồng, biên bản timestamp. Hội thoại quanh nghiệp vụ (sự cố, hóa đơn) chạy qua **Property Chat** (realtime Socket.io khi app mở + bot auto-remind + `@issue` + `@mention`); không full messenger (voice/sticker/poll ngoài MVP) — quyết định D24′.
2. **Excel/Sheets là biên nhập/xuất, không phải đối thủ:** import CSV/XLSX dữ liệu sẵn có, export báo cáo .xlsx. Không build full messenger realtime (chat 1-1 với voice/sticker/…) — **Property Chat (D24′)** đảm nhiệm hội thoại nghiệp vụ + bot remind; ZNS/Zalo OA và Google Sheets API 2 chiều → out of scope MVP.
3. **Không bắt ai bỏ thói quen cũ — chỉ bỏ khâu gõ tay.**

---

## 6. AI Scope Note — Ghi chú phạm vi AI

- **Auto-Description:** khả thi — đã test PASS (3/3 case), ~$0.024/call đo thực tế, có fallback rule-based.
- **Matchmaking:** kiến trúc tương tự Auto-Description (2 hồ sơ jsonb → LLM → `{score, advice}`, cache theo cặp nhờ unique constraint). Spike khuyến nghị trước khi code nhưng **không blocker**. Biên giới MVP: hybrid rule-filter → LLM score; moderation text-only (kiểm duyệt ảnh bằng OCR → stretch goal).
- **Contract Explainer (D15) — ĐÃ BỎ (31/08):** tính năng AI thứ 3 bị loại khỏi scope để giảm effort; hết 2 feature AI là Auto-Description (MVP) + Matchmaking (Stretch). Ký hợp đồng thì dùng template+upload wet-sign, không OTP/PIN (D18). Full-text RAG chatbot → Phase 1+ nếu có nhu cầu.

---

## 7. Scope Boundary — Phạm vi sản phẩm

**Cho thuê dài hạn only.** Sản phẩm phục vụ cho thuê **phòng trọ / căn hộ mini dài hạn** (hợp đồng theo tháng, chu kỳ chốt số điện nước hàng tháng, đối soát QR). **Cho thuê ngắn hạn / homestay (kiểu Airbnb) nằm ngoài phạm vi**, kể cả khi được đề xuất bổ sung (quyết định D9):

- Business logic khác bản chất: giá theo đêm + lịch check-in/out + đồng bộ OTA ↔ hợp đồng tháng + chốt số định kỳ + đối soát chuyển khoản — hai vòng đời, không dùng chung một luồng nào.
- 13–14 tuần không đủ làm tốt CẢ HAI; chọn làm sâu một lifecycle thay vì làm hời hợt hai lifecycle.
- Schema vẫn để mở field `property_type` trên `Building` để Phase 1+ có thể mở rộng mà không phá vỡ mô hình dữ liệu hiện có.

---

## 8. Platform & Role Coverage — Phạm vi nền tảng theo vai trò

Cả **web** và **mobile** đều phục vụ cả hai vai trò (quyết định D13), staging primary → secondary:

| Vai trò | Web (React) | Mobile (Kotlin) |
|---|---|---|
| Landlord | ✅ Primary — ops console đầy đủ | 🔶 Secondary — lite: FCM push, duyệt sự cố, xem dashboard/hóa đơn |
| Tenant | 🔶 Secondary — responsive | ✅ Primary — portal đầy đủ |

Authorization platform-agnostic sẵn (JWT + guard ở tầng API) — phân vai không phụ thuộc nền tảng; chi phí thật nằm ở UX 2 role × 2 platform, kiểm soát bằng R7 (staging).

→ Chi tiết giả định/rủi ro: `assumptions-risks.md`. Quyết định liên quan: D1–D29 trong `decisions.md`.
