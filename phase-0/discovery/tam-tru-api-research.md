# Discovery: API dịch vụ công cho khai báo tạm trú/tạm vắng (Research spike)

- **Task:** Tạm trú API Research
- **Assignee:** BE · **Participants:** PM (scope D17), AI (hỗ trợ OCR nếu cần)
- **Loại:** Research-only spike — **không triển khai** trong MVP
- **Trạng thái:** Draft v1 — chờ PM log quyết định **D17**
- **Liên quan:** D17 (MVP chỉ lưu ảnh CCCD tại e-contract 3.1 + OCR trích info 5.6 MVP; khai báo tạm trú đầy đủ → Phase 1+)

---

## 1. Bối cảnh

Buổi 27/08, giảng viên yêu cầu nghiên cứu khả năng tích hợp API dịch vụ công để hỗ trợ khai báo tạm trú/tạm vắng ngay trong app, thay vì để chủ trọ/người thuê tự làm thủ tục ngoài hệ thống. Đây **chỉ là spike tìm hiểu khả thi** — quyết định D17 đã chốt rằng khai báo tạm trú đầy đủ (in tờ khai, nộp cơ quan) nằm ở Phase 1+, MVP chỉ dừng ở việc lưu ảnh CCCD lúc ký hợp đồng điện tử.

## 2. Có API công khai cho bên thứ ba (như app của mình) không?

**Câu trả lời ngắn: Không có API mở, machine-callable, dành cho ứng dụng tư nhân/bên thứ ba tại thời điểm nghiên cứu.**

### 2.1 Các kênh chính thức hiện có (chỉ có giao diện web/app cho công dân, không phải API)

| Kênh | Bản chất | Ghi chú |
|---|---|---|
| **Cổng Dịch vụ công Quốc gia** (`dichvucong.gov.vn`) | Web portal cho công dân tự nộp hồ sơ | Không công bố REST/SOAP API public cho lập trình bên ngoài |
| **Ứng dụng VNeID** (Bộ Công an) | App di động, đăng ký tạm trú "mức độ 2" qua tài khoản định danh điện tử | Chỉ dùng qua app chính chủ Bộ Công an, không có SDK/API để nhúng vào app thứ ba |
| **Cổng DVC Bộ Công an** (`dichvucong.bocongan.gov.vn`) | Web portal chuyên ngành cư trú | Tương tự Cổng DVC Quốc gia — giao diện người dùng, không phải API |

Cả 3 kênh trên đều yêu cầu công dân **tự đăng nhập bằng tài khoản VNeID hoặc tài khoản Cổng DVC Quốc gia của chính họ**, không có cơ chế "app thứ ba gọi API thay mặt người dùng" kiểu OAuth như các nền tảng thanh toán (VNPay/Momo) mà hệ thống đang dùng.

Điểm đáng chú ý: hệ thống cho phép **"khai hộ"** — chủ nhà trọ có thể đăng nhập bằng tài khoản VNeID của chính chủ nhà và nhập hộ thông tin người thuê vào form. Đây vẫn là thao tác thủ công trên giao diện web/app của nhà nước, không phải tích hợp API.

### 2.2 Hạ tầng tích hợp cấp quốc gia (NDXP/LGSP) — có nhưng không dành cho SaaS tư nhân

Việt Nam có hạ tầng **NDXP** (Nền tảng tích hợp, chia sẻ dữ liệu quốc gia) và **LGSP** (cấp tỉnh) để các *cơ quan nhà nước, bộ ngành, địa phương* kết nối dữ liệu với nhau (vd. CSDL quốc gia về dân cư, đăng ký doanh nghiệp, bảo hiểm xã hội). Tính đến các báo cáo gần nhất, NDXP đã kết nối hơn 200 hệ thống của các bộ/ngành/địa phương với hàng triệu giao dịch/ngày.

Tuy nhiên, đối tượng kết nối vào NDXP/LGSP là **cơ quan nhà nước và một số ít doanh nghiệp được cấp phép/đối tác chiến lược** (như ngân hàng cho thanh toán, các bên vận hành CSDL chuyên ngành) — **không phải mô hình "đăng ký API key rồi gọi endpoint"** kiểu mở cho mọi lập trình viên. Một startup/team sinh viên **không có kênh chính thức nào** để xin quyền gọi API tạm trú qua NDXP/LGSP ở giai đoạn hiện tại.

### 2.3 Cập nhật quy trình gần đây

Bộ Công an đã ban hành Quyết định 1523/QĐ-BCA-C06 (26/03/2026) công bố thủ tục hành chính mới/sửa đổi cho lĩnh vực quản lý cư trú, tiếp tục đơn giản hóa quy trình đăng ký tạm trú online qua Cổng DVC/VNeID cho công dân — nhưng đây là cải tiến **trải nghiệm người dùng cuối**, không mở thêm cổng API cho bên thứ ba.

## 3. Hình dạng tích hợp (nếu giả định có API trong tương lai)

Dù hiện chưa có API, để chuẩn bị sẵn thiết kế cho Phase 1+ nếu chính sách thay đổi, dữ liệu cần trao đổi sẽ gồm:

**Chiều gửi đi (app → cơ quan quản lý cư trú):**
- Thông tin định danh người thuê: họ tên, số CCCD/CMND, ngày sinh, quê quán (đã có sẵn từ ảnh CCCD lưu ở feature 3.1 + OCR ở feature 5.6)
- Địa chỉ chỗ ở tạm trú (Room/Building address)
- Thời gian bắt đầu/kết thúc lưu trú (map từ `Contract.startDate`/`endDate`)
- Thông tin người khai báo hộ (chủ nhà) + xác nhận "chỗ ở hợp pháp" (giấy tờ sở hữu hoặc hợp đồng thuê — đã có trong `Contract`)

**Chiều nhận về (cơ quan → app):**
- Trạng thái hồ sơ (tiếp nhận / yêu cầu bổ sung / đã duyệt)
- Phiếu tiếp nhận hồ sơ (mẫu CT04) hoặc mã hồ sơ để tra cứu
- Thời gian xử lý: theo quy định hiện hành, hồ sơ tạm trú online được xử lý trong khoảng 3 ngày làm việc

### 3.1 Rào cản pháp lý/kỹ thuật nếu triển khai

- **Xác thực:** quy trình hiện tại bắt buộc công dân xác thực qua tài khoản VNeID *của chính họ* (mức độ 2, sinh trắc học) — một app thứ ba không thể "đăng nhập hộ" mà không vi phạm cơ chế định danh điện tử quốc gia.
- **Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân:** số CCCD, ngày sinh, địa chỉ là dữ liệu cá nhân (có thể thuộc nhóm nhạy cảm tùy ngữ cảnh) — nếu app đóng vai trò trung gian truyền dữ liệu này tới cơ quan nhà nước, cần đánh giá tác động xử lý dữ liệu cá nhân (DPIA) và có sự đồng ý rõ ràng của người thuê, vượt ngoài phạm vi kỹ thuật của spike này.
- **Ai được phép nộp hồ sơ:** hệ thống có hỗ trợ "khai hộ" (chủ nhà khai hộ người thuê) nhưng vẫn qua tài khoản định danh của chủ nhà trên chính kênh nhà nước — không phải qua app thứ ba.
- **Không có SLA/hợp đồng dịch vụ công khai** cho bên thứ ba muốn tích hợp — khác hẳn VNPay/Momo là các cổng thanh toán thương mại có API doc, sandbox, và điều khoản đối tác rõ ràng.

## 4. Kết luận khả thi (Feasibility verdict)

**🔴 Blocked** cho việc tích hợp API trực tiếp trong bất kỳ phase gần nào.

Lý do: không tồn tại API công khai, không có kênh chính thức để đăng ký làm đối tác tích hợp, và cơ chế xác thực (VNeID mức 2) về bản chất được thiết kế để công dân tự thao tác, không phải cho ứng dụng trung gian gọi thay.

**Khuyến nghị:**
1. **Giữ nguyên hướng D17** cho MVP: chỉ lưu ảnh CCCD tại e-contract, OCR trích thông tin để tái sử dụng nội bộ (điền sẵn form, tra cứu nhanh) — không tự động nộp hồ sơ tạm trú.
2. **Phase 1+ (nếu muốn cải thiện UX)**, thay vì gọi API (không khả thi), có thể làm ở mức "hỗ trợ điền hộ":
   - Sinh sẵn PDF tờ khai thông tin cư trú (mẫu CT01/CT04) với dữ liệu đã có trong hệ thống (tên, CCCD, địa chỉ, ngày thuê) để chủ nhà/người thuê tải về và tự nộp qua Cổng DVC/VNeID.
   - Gắn deep-link/hướng dẫn từng bước tới Cổng DVC Quốc gia hoặc VNeID (tương tự cách hệ thống dùng deep-link/hướng dẫn ngoài cho các điểm chạm bên ngoài app) thay vì cố xây tích hợp API không tồn tại.
3. **Theo dõi định kỳ (mỗi 6 tháng)** thông báo từ Bộ Công an/Cổng DVC Quốc gia — nếu trong tương lai họ mở chương trình đối tác API (như đã làm với ngành ngân hàng, bảo hiểm xã hội), có thể revisit quyết định này.

## 5. Việc còn mở

- Chưa xác minh liệu có API dành riêng cho *doanh nghiệp lưu trú* (khách sạn/nhà nghỉ có nghĩa vụ báo cáo lưu trú theo Luật Cư trú, khác với hộ gia đình cho thuê trọ dân sự) — nhóm khách sạn có nghĩa vụ báo cáo khác và có thể có kênh riêng qua công an địa phương; nếu app mở rộng sang phân khúc homestay/lưu trú ngắn hạn (đã note ở Phase 1+ trong feature 1.2), nên nghiên cứu lại riêng nhánh này.
- Chưa liên hệ trực tiếp công an phường/xã địa phương để hỏi khả năng tích hợp thí điểm cấp cơ sở — nằm ngoài phạm vi spike kỹ thuật này, để PM cân nhắc nếu cần.

## Definition of Done — đối chiếu

- [x] Câu trả lời cụ thể về sự tồn tại của API: **Không** — chỉ có giao diện web/app cho công dân tự thao tác qua Cổng DVC Quốc gia và VNeID; hạ tầng NDXP/LGSP tồn tại nhưng chỉ dành cho cơ quan nhà nước/đối tác được cấp phép.
- [x] Sketch tích hợp (nếu có trong tương lai) + rào cản pháp lý đã ghi nhận (§3).
- [x] Verdict: **🔴 Blocked** cho tích hợp API; khuyến nghị hướng thay thế "hỗ trợ điền hộ + deep-link" cho Phase 1+ (§4) — chờ PM log **D17**.
