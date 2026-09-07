# Discovery: API khai báo tạm trú/tạm vắng — từ "chặn" sang "mock gateway thay được API thật" (Research spike)

- **Task:** Tạm trú API Research
- **Assignee:** BE · **Participants:** PM (scope D17/D38), AI (hỗ trợ OCR nếu cần)
- **Loại:** Research spike + **thiết kế demo (phương án trình bày)** — không triển khai MVP
- **Trạng thái:** Draft v2 — chờ PM log quyết định **D38** (thêm mock gateway vào hướng Phase 1+)
- **Liên quan:** D17 (MVP chỉ lưu ảnh CCCD tại e-contract 3.1 + OCR trích info 5.6 MVP; khai báo tạm trú đầy đủ → Phase 1+), **D38** (mock gateway, swap API thật)

---

## 1. Bối cảnh

Buổi 27/08, giảng viên yêu cầu nghiên cứu khả năng tích hợp API dịch vụ công để hỗ trợ khai báo tạm trú/tạm vắng ngay trong app, thay vì để chủ trọ/người thuê tự làm thủ tục ngoài hệ thống. Quyết định **D17** đã chốt rằng khai báo tạm trú đầy đủ (in tờ khai, nộp cơ quan) nằm ở **Phase 1+**; **MVP chỉ dừng ở việc lưu ảnh CCCD lúc ký hợp đồng điện tử + OCR trích thông tin** (feature 5.6).

Research v1 kết luận "🔴 Không có public API, blocked". Sau đó nhóm tìm được **tài liệu kỹ thuật chính thức về API Khai báo tạm trú (KBTT) cho Cơ sở lưu trú (CSLT)** của Cục Quản lý Xuất nhập cảnh – Bộ Công an. Tài liệu này không cho phép gọi thật từ app sinh viên, **nhưng mở ra cơ hội**: dựng một **mock gateway** theo đúng chuẩn kết nối thật, được thiết kế sao cho khi có quyền truy cập thật chỉ cần đổi cấu hình là vận hành được — tạo phương án trình bày thể hiện tư duy thiết kế phần mềm chuyên nghiệp trước hội đồng. Đây là nội dung quyết định **D38**.

---

## 2. API chính thức cho Cơ sở lưu trú (CSLT) — bản chất & khả năng gọi thật

### 2.1 API này dành cho ai, làm gì?

Tài liệu `api-kbtt.xuatnhapcanh.gov.vn` phục vụ **phần mềm bên thứ ba (PMS) của khách sạn / nhà nghỉ / cơ sở lưu trú chuyên nghiệp**:

- **Khai báo tạm trú cho Người nước ngoài (NNN)** — do Cục Xuất nhập cảnh quản lý.
- **Thông báo lưu trú cho người Việt Nam** (khách ở ngắn ngày, qua đêm tại khách sạn/nhà trọ).

**Cơ chế xác thực:**
- Chuẩn **OAuth 2.0 (Bearer Token)** qua `POST /authorization-service/oauth/token`.
- Có các API: Get Token / Refresh Token / Revoke Token; khai báo người Việt Nam / người nước ngoài; tra cứu danh mục hành chính (tỉnh/phường/xã, quốc tịch).

### 2.2 Có gọi thật từ app sinh viên được không?

**Không.** Vì:
- Endpoint yêu cầu **tài khoản CSLT thật** (`username`, `password`, `CsltId`) do cơ quan Công an địa phương cấp cho từng cơ sở.
- Cần **`Client ID` + Basic Auth** do Cục Quản lý Xuất nhập cảnh cấp phép cho đơn vị phần mềm thứ ba (nhóm sinh viên không có kênh xin phép này).

### 2.3 Phân biệt nghiệp vụ pháp lý (quan trọng)

- **Thông báo lưu trú ngắn hạn** (khách sạn/nhà trọ có khách qua đêm): có API như tài liệu trên.
- **Đăng ký tạm trú dài hạn** (hợp đồng thuê trọ 6 tháng – 1 năm, đúng phân khúc của sản phẩm): là thủ tục cư trú cá nhân của công dân, cần hợp đồng thuê + xác nhận chủ nhà + phê duyệt Công an xã/phường — hiện xử lý qua **Cổng Dịch vụ công / VNeID**, **không có API công khai** cho bên thứ ba tự động duyệt (rào cản giữ nguyên ở §5).

> **Hệ quả cho hệ thống:** sản phẩm hiện tại (D9 — cho thuê dài hạn theo hợp đồng tháng) KHÔNG khớp loại hình "thông báo lưu trú ngắn hạn qua API CSLT". Do đó tích hợp API thật vẫn nằm ngoài phạm vi; mock gateway là **minh họa kiến trúc**, không phải cam kết nghiệp vụ thật.

---

## 3. Kiến trúc tích hợp: Gateway Adapter (mock ⇄ real đổi bằng config)

Thay vì để các module nghiệp vụ gọi thẳng endpoint, ta định nghĩa một **interface gateway** duy nhất + 2 cài đặt (implementation) có thể đổi qua cấu hình:

```
                 ┌─────────────────────────────┐
  Backend  ◄────►│    ResidencyGateway (interface) │
 (NestJS)   gọi   │  getToken() / declare() /        │
  Module          │  getStatus() / refresh()          │
  Tạm trú         └──────────────┬──────────────┘
                                 │ (chọn qua cấu hình `gateway.env`)
                ┌────────────────┴────────────────┐
                ▼                                 ▼
       ┌─────────────────┐              ┌─────────────────┐
       │  MockGateway     │              │  RealBcaGateway  │
       │  (NestJS/mock)   │              │  (gọi API thật)  │
       │  admin duyệt tay │              │  Cục XNC          │
       └─────────────────┘              └─────────────────┘
```

**Nguyên tắc:** phần nghiệp vụ (contract data, payload, luồng trạng thái) viết 1 lần theo interface; chỉ **cài đặt gateway** đổi theo môi trường. Đổi API thật = đổi `gateway.env` + nguồn credential + tắt duyệt tay — **không đổi logic nghiệp vụ, không đổi payload contract**.

---

## 4. Mock Gateway (phương án demo)

### 4.1 Mục đích
- Minh họa đúng **chuẩn kết nối** và **data contract** của hệ thống quản lý lưu trú quốc gia.
- Cho hội đồng thấy: hệ thống đã thiết kế sẵn tầng tích hợp tuân thủ OAuth 2.0 + data contract; khi có quyền thật chỉ cần thay cấu hình là vận hành.

### 4.2 Cấu trúc (kiến trúc)
- **Backend (NestJS, `pbl6-backend`)** chứa `ResidencyGateway` interface + `MockGateway` implementation, chạy cùng backend (hoặc gọi tới một mock service tách riêng — để BE chốt ở Phase 2).
- Mock endpoint bám sát format tài liệu chính thức (dạng `POST /authorization-service/oauth/token`, `POST /api/v1/khai-bao-luu-tru…`) để dễ trình bày đối chiếu với chuẩn thật.

### 4.3 Per-landlord credential
- Mỗi **CSLT = 1 bộ credential riêng** (`CsltId`, username, password) — đúng mô hình thật.
- Ở mock: mỗi landlord tự khai báo credential trong tài khoản của mình (thiết kế — chi tiết mã hóa lưu trữ để BE quyết định ở Phase 2; dùng `GATEWAY_MOCK` khi chưa có thật).
- Model gợi ý: `LandlordGatewayCredential` (`landlord_id`, `cslt_id`, `username`, `password_encrypted`, `gateway_env`, `is_active`).

### 4.4 Admin toggle mock/real
- Trong Admin Portal (Cấu hình hệ thống) có **switch mock / real**:
  - **Mock mode:** bật **duyệt tay** — admin xem danh sách hồ sơ và **trigger duyệt / từ chối** thủ công (mô phỏng phản hồi của cơ quan).
  - **Real mode:** **tắt duyệt tay** (cơ quan đảm nhận), chỉ cập nhật trạng thái từ response thật.
- Lý do: duyệt tay là hành vi *mô phỏng* của mock, không tồn tại khi qua API thật → tự động ẩn khi real.

---

## 5. Rào cản pháp lý/kỹ thuật (giữ nguyên từ v1, cập nhật)

- **Xác thực:** quy trình hiện tại bắt buộc xác thực qua tài khoản VNeID của chính công dân (mức độ 2, sinh trắc học) — app thứ ba không thể "đăng nhập hộ" mà không vi phạm cơ chế định danh điện tử quốc gia.
- **Loại hình không khớp:** sản phẩm cho thuê **dài hạn** (D9) — API CSLT ở §2 dành cho **thông báo lưu trú ngắn hạn** của khách sạn. Đăng ký tạm trú dài hạn vẫn qua Cổng DVC/VNeID (không API).
- **Nghị định 13/2023/NĐ-CP:** số CCCD, ngày sinh, địa chỉ là dữ liệu cá nhân — cần đồng ý người thuê + đánh giá tác động (DPIA) nếu đóng vai trò trung gian truyền tới cơ quan nhà nước.
- **Ai được phép nộp hồ sơ:** "khai hộ" phải qua tài khoản định danh của chủ nhà trên kênh nhà nước, không phải app thứ ba.
- **Không có SLA/hợp đồng dịch vụ công khai** cho bên thứ ba (khác VNPay/Momo có API doc + sandbox + điều khoản đối tác).

---

## 6. Kết luận khả thi (Feasibility verdict)

**🔴 Vẫn Blocked** cho **việc gọi API thật trực tiếp** trong bất kỳ phase gần nào (không có quyền, loại hình không khớp, xác thực VNeID).

**Nhưng** — có thể thực hiện một **phương án demo minh họa kiến trúc** (✅ khả thi):

1. **Giữ nguyên D17 cho MVP:** chỉ lưu ảnh CCCD tại e-contract, OCR trích thông tin để điền sẵn form/tra cứu nội bộ — không tự động nộp hồ sơ.
2. **Phase 1+ (đề xuất D38):** dựng **mock gateway** theo chuẩn API thật + interface adapter để đổi API thật bằng cấu hình + per-landlord credential + admin toggle mock/real (duyệt tay chỉ ở mock). Đây là **thiết kế/demo artifact**, không ràng buộc pháp lý.
3. **Song song UX** (không phụ thuộc mock): sinh sẵn **PDF tờ khai CT01/CT04** với dữ liệu đã có + gắn **deep-link/hướng dẫn** tới Cổng DVC Quốc gia / VNeID để chủ nhà/người thuê tự nộp.

---

## 7. Việc còn mở

- **Chi tiết payload/OpenAPI** của gateway (endpoint + body JSON) — để riêng cho Phase 2 khi BE implement; doc này chỉ nêu kiến trúc & phương án.
- **Cách mã hóa/encrypt credential** per-landlord — BE quyết định ở Phase 2 (thiết kế, chưa chốt kỹ thuật).
- **Khả năng tích hợp phân khúc homestay/lưu trú ngắn hạn** (đã note ở Phase 1+ feature 1.2) — nếu mở rộng sang đó phải nghiên cứu lại riêng nhánh (loại hình khớp với API CSLT).

---

## Definition of Done — đối chiếu

- [x] Phân biệt rõ nghiệp vụ pháp lý: thông báo lưu trú ngắn hạn (có API CSLT) vs đăng ký tạm trú dài hạn (DVC/VNeID, không API).
- [x] Khả năng gọi thật từ app sinh viên: **Không** — chưa có quyền, loại hình không khớp.
- [x] Kiến trúc **gateway adapter** (mock ⇄ real đổi bằng config) + mock gateway + per-landlord credential + admin toggle — **D38**.
- [x] Rào cản pháp lý/kỹ thuật ghi nhận (§5).
- [x] Verdict: **Blocked** cho API thật; đề xuất mock gateway demo + hỗ trợ điền hộ/deep-link cho Phase 1+ (§6) — chờ PM log **D38**.
