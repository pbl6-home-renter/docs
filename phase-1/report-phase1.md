# Báo cáo Phase 1 — Quản lý thuê trọ hai chiều (PBL6)

> **Chuẩn bị:** Tritinh · **Checkpoint W5 (M1):** Thứ 5 tuần sau
> **Mục đích:** Báo cáo kết quả Phase 1 (Setup + Requirements Freeze) — nghiệp vụ cốt lõi đã chốt, mô hình dữ liệu, kế hoạch Phase 2.
> **Tài liệu gốc:** mỗi mục kèm link tới file nguồn trong repo để trình bày/dẫn chứng dễ dàng.

---

## 1. Tổng quan Phase 1 (W3–4: 28/08 – 09/09)

**Mục tiêu Phase 1** (theo [PROJECT_PLAN.md](../PROJECT_PLAN.md) §5):
- Setup 4 repository (`pbl6-backend`, `pbl6-web`, `pbl6-mobile`, `pbl6-ai`) + docs hub, chuẩn hoá quy ước.
- Soạn **user flow theo từng vai trò** → source of truth cho Navigation/UI.
- **Đóng băng nghiệp vụ (Business Rules FROZEN v1.2)**: hợp đồng, phòng/tòa, điện nước, hóa đơn – thanh toán, roommate, chat, AI flows ([business-rules.md](business-rules.md)).
- Checkpoint W5: trình bày requirement + business rules trước thầy → thu thập feedback → cập nhật `requirement.md`.

**Outputs chính đã hoàn thành trong Phase 1:**

| Output | File |
|---|---|
| User flow 4 vai (tenant / landlord / admin / shared) | [discovery/user_flow/](discovery/user_flow/) |
| Business rules **FROZEN v1.2** (7 lĩnh vực) | [business-rules.md](business-rules.md) |
| Thiết kế CSDL v3 (ERD + DDL chi tiết, snapshot hóa đơn) | [discovery/database-design_v3.md](discovery/database-design_v3.md) |
| Spec tính tiền điện/nước/phí — 100% case + pseudocode | [discovery/utility-billing-calculations.md](discovery/utility-billing-calculations.md) |
| Quyết định Phase 1 (D30–D37, cập nhật liên tục) | [discovery/decisions.md](discovery/decisions.md) |

---

## 2. Nghiệp vụ cốt lõi đã chốt

### 2.1 Quản lý Hợp đồng & Pháp lý

Nguồn: [business-rules.md](business-rules.md) §2 · [requirement.md](../requirement.md)

- **Đại diện ký kết:** 1 hợp đồng đại diện do lead tenant đứng tên ký (ở ghép); các thành viên khác khai báo thông tin + số người ở theo quy định.
- **Mẫu văn bản:** hệ thống sinh template hợp đồng (Word/PDF), chủ trọ tải về chỉnh sửa linh hoạt.
- **Tính pháp lý & lưu trữ:** mô hình **wet-sign** — 2 bên ký tay trên giấy → scan/tải lên bản đã ký làm chứng cứ (không dùng OTP/PIN/chữ ký điện tử — `template_upload`). Chưa upload file ký thì hợp đồng chưa `signed`.
- **Vòng đời hợp đồng:** `draft → signed → active → expired / terminated`; lúc tạo HĐ chủ trọ lưu ảnh CCCD của người thuê 1 lần.

### 2.2 Phân loại thuê — Ngắn hạn vs Dài hạn

Nguồn: [phase-0/discovery/short-vs-long-term-analysis.md](../phase-0/discovery/short-vs-long-term-analysis.md) (D9)

- **Kết luận:** luồng thanh toán & chi phí phát sinh không khác biệt đáng kể. Điểm khác duy nhất: ngắn hạn có thêm phí dịch vụ theo lượt/ngày.
- **Quyết định:** MVP chỉ cho thuê **dài hạn** (hợp đồng theo tháng, chốt số điện nước định kỳ). Ngắn hạn/homestay nằm ngoài phạm vi, gộp chung luồng thanh toán. Schema giữ `property_type` mở cho Phase 1+.

### 2.3 Điện nước & Tiện ích

Nguồn: [business-rules.md](business-rules.md) §3 · [discovery/utility-billing-calculations.md](discovery/utility-billing-calculations.md)

- **Cách tính:** theo quy định nhà nước (bậc thang EVN 6 bậc, bậc 3 TT 25/2018) **hoặc** giá thỏa thuận cố định (flat) — chủ trọ chọn preset.
- **Mô hình đơn giá versioned:** bảng `UtilityRatePolicy` (`flat` / `tiered` / `per_head`) — điện chỉ flat/tiered; nước thêm khoán đầu người. Giá theo `effective_from/to`, đổi giá giữa kỳ áp từ kỳ sau.
- **Nhập số công tơ bắt buộc bằng ảnh:** chụp công tơ trực tiếp qua app → OCR → xác nhận tay (OCR sai/mờ thì sửa tay đúng số thực tế, vẫn kèm ảnh nguồn). **Baseline = OCR lúc bàn giao phòng** (`is_baseline=true`).
- **Phí định kỳ** (`RecurringFee`): Wifi / QLVH / gửi xe / vệ sinh… chọn preset seed, không hard-code; đều thu qua hóa đơn app.
- **Spec tính tiền 100% case + pseudocode + edge case** tại [utility-billing-calculations.md](discovery/utility-billing-calculations.md) — dùng làm spec cho `InvoiceService` (BE).

### 2.4 Cơ chế Thông báo (thay kênh Zalo truyền thống)

Nguồn: [business-rules.md](business-rules.md) §6 · [phase-0/discovery/realtime-feasibility.md](../phase-0/discovery/realtime-feasibility.md) (D24′)

- **Property Chat in-app** giữa chủ nhà và người thuê: chat riêng phòng + chat chung toà.
- **Bot engine** (identity riêng): auto-remind cron — kết quả OCR, hóa đơn, hợp đồng hết hạn → gửi card vào chat phòng.
- **`@issue <mô tả>` (+ ảnh):** tạo sự cố → card → thông báo; **`@mention @user`:** nhắc thành viên cụ thể.
- Kỹ thuật: realtime Socket.io khi app mở + FCM khi offline; DB persistence, lazy-load theo cursor.
- Loại Zalo/Excel khỏi kênh trong app.

---

## 3. Mô hình dữ liệu & tổ chức căn hộ

Nguồn: [phase-0/discovery/ownership-model.md](../phase-0/discovery/ownership-model.md) (D25) · [database-design_v3.md](discovery/database-design_v3.md)

- **DB linh hoạt đa dạng hình thức sở hữu:**
  - 1 chủ → 1 khu/dãy trọ.
  - 1 chủ → nhiều khu trọ.
  - Chung cư/tòa nhà: chia lẻ theo tầng hoặc sở hữu vài phòng riêng trong cùng 1 tòa.
- **Thiết kế chốt:** Tòa chứa nhiều phòng (1:n); mỗi phòng có **đúng 1 chủ sở hữu** (`Room.ownerId`, nguồn chân lý), không có khái niệm quản lý/nhượng quyền trong MVP. Bao được case 59 phòng (A giữ 50, B/C/D mỗi người 3).
- **Luồng thao tác trực tiếp trên app** (chuyển phòng / quyền quản lý) được thể hiện trong [user_flow/landlord_user_flow.md](discovery/user_flow/landlord_user_flow.md).
- **Nguyên tắc DB:** không RBAC (roles là enum tĩnh + ownership check), trạng thái phòng là derived từ hợp đồng active, ảnh/file tập trung 1 bảng `Media`, hóa đơn **snapshot bất biến** cấu hình đã dùng.

---

## 4. Tính năng dành cho chủ nhà & người thuê

### 4.1 Dashboard chủ trọ

Nguồn: [user_flow/landlord_user_flow.md](discovery/user_flow/landlord_user_flow.md) §1

- Lịch phòng **đang thuê / phòng trống** trực quan.
- Biểu đồ & báo cáo **doanh thu / công nợ** realtime (đọc trực tiếp từ snapshot hóa đơn).

### 4.2 Lịch sử người thuê *(đang cân nhắc)*

Nguồn: [phase-0/discovery/decisions.md](../phase-0/discovery/decisions.md) (D26)

- Hiển thị lịch sử thuê trọ trước đó để chủ nhà đánh giá độ uy tín.
- **Đang xem xét chính sách quyền riêng tư** (PDPD 13/2023): dự kiến chỉ hiển thị dữ liệu **nội bộ nền tảng** khi có sự đồng ý của người thuê; tạm xếp vào **Stretch**, không bắt buộc MVP.

### 4.3 Khai báo tạm trú

Nguồn: [phase-0/discovery/tam-tru-api-research.md](../phase-0/discovery/tam-tru-api-research.md) (D17) · quyết định [D38](discovery/decisions.md)

- Đã nghiên cứu **API chính thức khai báo tạm trú cho Cơ sở lưu trú (CSLT)** của Cục Quản lý Xuất nhập cảnh – Bộ Công an: chuẩn **OAuth 2.0 (Bearer Token)**, per-CSLT credential (`CsltId`/username/password). Không gọi thật được từ app sinh viên (chưa có quyền; sản phẩm thuê **dài hạn** D9 không khớp loại hình "thông báo lưu trú ngắn hạn").
- **Phương án kiến trúc (D38):** thiết kế **gateway adapter** — định nghĩa interface `ResidencyGateway` (mock ⇄ API thật đổi bằng cấu hình), **per-landlord credential** (landlord tự khai báo, chi tiết mã hóa để BE chốt Phase 2), và **admin toggle mock/real** (duyệt tay chỉ ở mock mode, tự tắt khi real). Khi có quyền thật chỉ cần đổi `BASE_URL` + nguồn credential + tắt duyệt tay là vận hành — payload/contract không đổi.
- **Điểm chốt MVP (D17 bất biến):** chủ trọ lưu **CCCD photo** của người thuê ngay khi tạo hợp đồng + **OCR trích thông tin** (feature 5.6); không tự động nộp hồ sơ. Nộp hồ sơ đầy đủ → Phase 1+ (mock gateway demo + PDF tờ khai CT01/CT04 + deep-link Cổng DVC/VNeID).

### 4.4 Tìm bạn ở ghép (AI Matching)

Nguồn: [phase-0/discovery/ai-matching-spec.md](../phase-0/discovery/ai-matching-spec.md) (D28) · AI member phụ trách

- Hồ sơ roommate: lifestyle, giờ ngủ, thú cưng, hút thuốc, budget, giới tính…
- **Chủ trọ set yêu cầu cứng** (max người, giới tính, nội quy, khoảng giá) — ai vi phạm bị loại khỏi pool; không duyệt/veto từng cặp.
- **AI Matching score** (Stretch, D28): hybrid rule-filter → LLM tính độ tương thích % + lời khuyên; spec full lifecycle tại [ai-matching-spec.md](../phase-0/discovery/ai-matching-spec.md).

### 4.5 Chống chịu landlord-solo (D29 — bắt buộc)

Nguồn: [business-rules.md](business-rules.md) §8

- Hệ thống **phải vận hành được khi tenant KHÔNG đăng nhập** — chủ trọ tự làm toàn bộ vòng đời (HĐ, CCCD, chốt số, hóa đơn, QR/tiền mặt/giấy). App tenant là optional/passive.
- Thanh toán không phụ thuộc login tenant: dynamic-QR (quét bằng app ngân hàng bất kỳ), tiền mặt, chuyển khoản.

---

## 5. Tính năng hủy trong Phase 1 (ngoài scope MVP)

| Tính năng | Ghi chú |
|---|---|
| Chatbot tư vấn luật | Chi phí xây Knowledge Graph/Vector DB phức tạp, chưa khả thi giai đoạn này |
| Lịch vệ sinh nội bộ | Giảm tải phạm vi cho MVP |
| Đa tiền tệ | Chỉ xử lý VND |
| Đa ngôn ngữ (Tiếng Anh) | Chỉ phục vụ tiếng Việt trong giai đoạn 1 |

Nguồn scope chính thức: [requirement.md](../requirement.md) (Out-of-scope).

---

## 6. Kế hoạch tiếp theo (Phase 2 — Design, W5–6)

Nguồn: [PROJECT_PLAN.md](../PROJECT_PLAN.md) §5 Phase 2

- **Bước 1:** Hoàn thiện & chốt 100% tài liệu mô tả luồng nghiệp vụ (đang chốt tại [business-rules.md](business-rules.md) + [user_flow/](discovery/user_flow/)).
- **Bước 2:** Thiết kế **UI/UX (Wireframe & Prototype)** — danh sách màn hình, cấu trúc điều hướng, layout từng page tương ứng nghiệp vụ đã chốt.
- **Bước 3 (Kỹ thuật):** sau khi UI/UX + nghiệp vụ hoàn tất mới triển khai: Thiết kế CSDL hoàn chỉnh, khởi tạo Repository/base code, chốt Technical Stack.

**Checkpoint tiếp theo:** W7 (M2) — design frozen, spec commit vào docs hub & backend repo.

---

## 7. Tài nguyên trình bày

| Nội dung | File |
|---|---|
| Scope chính thức + quyết định nền tảng | [requirement.md](../requirement.md) |
| Kế hoạch & mốc thời gian | [PROJECT_PLAN.md](../PROJECT_PLAN.md) |
| Nghiệp vụ đóng băng v1.2 | [business-rules.md](business-rules.md) |
| User flow per-role (tenant / landlord / admin / shared) | [discovery/user_flow/](discovery/user_flow/) |
| Thiết kế CSDL v3 (ERD + DDL + phân quyền theo role) | [discovery/database-design_v3.md](discovery/database-design_v3.md) |
| Spec tính tiền điện nước phí (100% case) | [discovery/utility-billing-calculations.md](discovery/utility-billing-calculations.md) |
| Research: so sánh ngắn/dài hạn | [phase-0/discovery/short-vs-long-term-analysis.md](../phase-0/discovery/short-vs-long-term-analysis.md) |
| Research: mô hình sở hữu | [phase-0/discovery/ownership-model.md](../phase-0/discovery/ownership-model.md) |
| Research: AI matching spec | [phase-0/discovery/ai-matching-spec.md](../phase-0/discovery/ai-matching-spec.md) |
| Research: khai báo tạm trú | [phase-0/discovery/tam-tru-api-research.md](../phase-0/discovery/tam-tru-api-research.md) |
| Research: realtime Property Chat | [phase-0/discovery/realtime-feasibility.md](../phase-0/discovery/realtime-feasibility.md) |