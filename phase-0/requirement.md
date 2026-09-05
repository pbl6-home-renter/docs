# PBL6

Học theo tuần lẻ (2 tuần lên trường 1 lần)

## 1. Yêu cầu:
- Đầu ra gồm 1 Web + 1 App
- FE web: Reactjs
- FE app: Kotlin/Android Native
- BE: Nodejs + Nestjs + PostgreSQL
- Khuyến khích: thêm AI (gọi api / dùng open source rồi tự build)
- Công cụ quản lí task
- Sử dụng Swagger + Apidog
- Triển khai theo từng step:
    - phân tích yêu cầu → chốt nghiệp vụ
    - Thiết kế giao diện dạng cấu trúc
    - Xây dựng cơ sở dữ liệu
    - Biểu đồ các thứ tự vẽ trong các quá trình
    - Code

## 2. Đề tài draft: 
**Vấn đề:** Các chủ trọ đang quản lý hợp đồng, hóa đơn điện nước bằng sổ sách hoặc Excel rất dễ sai sót. Trong khi đó, người thuê trọ (đặc biệt là sinh viên) lại gặp khó khăn trong việc tìm người ở ghép hợp tính.
**Core Business (Nặng về Software Engineering):** Nền tảng quản lý cho thuê hai chiều (landlord ops + tenant portal cùng vòng đời): quản lý phòng/hợp đồng, chốt số điện nước bằng OCR, tự động sinh hóa đơn, đối soát QR động, và tìm bạn ở ghép có AI hỗ trợ — **Property Chat platform (D24′) thay thế no-messenger**: chat riêng phòng + chung toà, bot auto-remind, `@issue`, `@mention` (F2 no feed).

- **Web (React — Primary: Landlord ops console; Secondary: Tenant responsive portal) [D13]:**
    - Dashboard chủ trọ: theo dõi lịch phòng trống/đang thuê trực quan + biểu đồ doanh thu/công nợ realtime (D20); quản lý danh sách phòng, sơ đồ tòa nhà.
    - Tạo và quản lý hợp đồng điện tử — app **sinh mẫu HĐ (Word/PDF)**, 2 bên **ký tay trên giấy**, user **up file đã ký (wet-sign 2 bên)** làm chứng cứ pháp lý [D18]. **Bỏ OTP/PIN/`e_ack` hoàn toàn** (31/08): không OTP SMS/FCM, không soft-ack — chưa có file ký thì HĐ chưa signed.
    - Tự động chốt số điện nước hàng tháng bằng **OCR + xác nhận tay**, sinh hóa đơn và theo dõi trạng thái thanh toán (F5: OCR thay utility-API).
    - Thống kê doanh thu, chi phí.
- **Mobile (Kotlin/Android — Primary: Tenant portal; Secondary: Landlord lite: FCM push, duyệt sự cố, xem dashboard/hóa đơn) [D13]:**
    - Tìm kiếm phòng trọ theo bản đồ, filter nâng cao.
    - Nhận hóa đơn hàng tháng, thanh toán (tích hợp VNPay/Momo) + dynamic named-QR.
    - Tính năng "Tìm người ở ghép" (hồ sơ tính cách, thói quen sinh hoạt) + match request [D28].
    - Báo cáo sự cố (hỏng điện, nước) cho chủ trọ qua **Property Chat riêng phòng** (D24′: `@issue` tạo IssueReport, bot auto-remind, mention `@user`; realtime Socket.io khi app mở + FCM offline; loại Zalo khỏi kênh).
- **Chức năng AI (FastAPI + LLM provider-agnostic — OpenAI/Gemini qua adapter, cấu hình env) [D3]:**
    - *AI Auto-Description (MVP):* Chủ trọ nhập vài từ khóa (vd: "20m2, khép kín, có điều hòa, gần bách khoa"), LLM tự động sinh bài PR phòng trọ; fallback rule-based khi API lỗi.
    - *AI Matchmaking (Stretch, D28):* Lấy hồ sơ 2 người tìm bạn ở ghép → LLM tính "Độ tương thích (Matching Score) %" + lời khuyên theo thói quen (ngủ muộn, nuôi mèo, hút thuốc...); hybrid rule-filter → LLM score, moderation text-only, seed ≥10; spec tại P1-13 (D28).

- **Phạm vi sản phẩm (Scope Boundary) [D9]:**
    - Chỉ cho thuê **dài hạn** (phòng trọ / căn hộ mini, hợp đồng theo tháng, chốt số điện nước định kỳ). **Cho thuê ngắn hạn / homestay (kiểu Airbnb) nằm ngoài phạm vi** — phân tích `discovery/short-vs-long-term-analysis.md` (D9) chứng minh bất khả thi kết hợp; schema giữ `property_type` mở cho Phase 1+.
    - **Nguyên tắc chống chịu bắt buộc (D29):** hệ thống phải vận hành được khi tenant **KHÔNG login** — landlord làm toàn bộ vòng đời một mình (tạo HĐ, up CCCD, chốt số, xuất hóa đơn, đẩy qua QR/tiền mặt/giấy/kênh ngoài, đối soát); tenant app là optional/passive; roommate matching vẫn chạy cho tenant có account.
  - **Ngoài phạm vi MVP (Out-of-scope) [D1–D29, F2, F5, F7, F8]:**
    - Social/ranking feed (F2); full realtime messenger (D24′: chỉ Property Chat — voice/sticker/poll/read-receipt ngoài MVP); **tính năng import** (D19: user non-tech → bỏ); chia tiền ở ghép đầy đủ (D4/D22 → Phase 1+); ZNS/Zalo OA (D7 → Phase 1+); EVN/nước utility API pull (F5 → OCR); full-text RAG chatbot trên hợp đồng (D15 bỏ — thêm vào Phase 1+ nếu có nhu cầu); Google Sheets 2-way API (D7); multi-currency/HĐĐT legal (nice-to-have).
  - **Quyết định nền tảng:** xem `discovery/decisions.md` (D1–D29, D12 bỏ qua) — hai chiều (D1), integration-first (D7), long-term-only (D9), cross-platform roles (D13), e-contract template+upload wet-sign, no OTP/PIN (D18), ownership model chốt theo `ownership-model.md` (D25), landlord-solo resilience (D29).

**Lưu ý:** Mô tả mang tính tham khảo; phạm vi chính thức được chốt qua các quyết định D1–D29 trong `discovery/decisions.md`. Nhóm vẫn có thể sáng tạo (tên app, theme, cách triển khai) miễn là giữ core business và các quyết định đã chốt.