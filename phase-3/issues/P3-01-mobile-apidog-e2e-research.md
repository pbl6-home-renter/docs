# P3-01 — Research: Triển khai Mobile End-to-End với Apidog Mock trước khi BE hoàn thiện

**Status:** 🟡 Open  
**Assignee:** Mobile Lead  
**Stakeholders / Reviewers:** PM, BE Lead  
**Created:** 2026-09-28  
**Due date:** 2026-09-29 (Ngày mai — EOD)  
**Priority:** 🔴 High / Blocker (Định hình toàn bộ workflow phát triển Mobile trong Phase 3 & Phase 4)  
**Input:**

- `pm/phase-2/discovery/api-conventions.md` (chuẩn response wrapper, pagination, error code)
- `pm/phase-2/discovery/api-spec.md` (109 endpoints, 24 domain groups)
- `pm/phase-0/discovery/tech-feasibility.md` (§5 API Contract Workflow & Apidog Mock)
- Spec dự án trên Apidog (do BE lead quản lý và sync từ OpenAPI)  
  **Deliverable:** Báo cáo kỹ thuật chi tiết lưu tại `pm/phase-3/discovery/mobile-apidog-e2e-research.md` kèm kiến trúc đề xuất và PoC code.

---

## 1. Background & Bối cảnh

Tại Phase 3 (W7–W8), mục tiêu cốt lõi của team là xây dựng khung ứng dụng (Scaffolding) và hoàn thành **First Vertical Slice** (luồng Login → Xem danh sách phòng trọ → Xem chi tiết phòng) để chuẩn bị cho Milestone Checkpoint W9 (M3).

Hiện tại, team Backend (NestJS + PostgreSQL) đang bắt đầu khởi tạo dự án, thiết lập database schema. Tuy nhiên:

- Nếu team Mobile (Android / Kotlin) phải chờ BE deploy API thật mới bắt đầu viết tầng mạng (Network Layer), ViewModel và liên kết dữ liệu lên UI thì sẽ tạo ra **điểm nghẽn nghiêm trọng (bottleneck)**, đẩy toàn bộ rủi ro tích hợp vào sát ngày demo Checkpoint W9.
- Theo thỏa thuận thiết kế ở Phase 2, BE sẽ định nghĩa và hoàn thiện toàn bộ API contract trên **Swagger/OpenAPI** và đồng bộ sang **Apidog**.

Vì vậy, PM yêu cầu Mobile Lead nghiên cứu chuyên sâu về tính khả thi, giải pháp kiến trúc và quy trình thực hiện: **Liệu phía Mobile có thể triển khai code End-to-End hoàn chỉnh dựa trên Apidog Mock trước khi BE hoàn thiện hay không?**

---

## 2. Mục tiêu nghiên cứu (Core Research Questions)

Mobile Lead cần làm rõ và đưa ra kết luận dứt khoát cho 5 câu hỏi chiến lược sau:

### Q1. Tính khả thi tổng thể (End-to-End Feasibility)

- Mobile có thể viết code xuyên suốt từ **UI (Jetpack Compose / XML) → ViewModel → Repository / UseCase → Network DataSource (Retrofit) → Apidog Mock Server** và nhận data render đầy đủ lên màn hình hay không?
- Mức độ khả thi là bao nhiêu %? Có thể áp dụng cho toàn bộ 109 endpoints hay chỉ phù hợp cho một nhóm tính năng nhất định?

### Q2. Cơ chế Mock của Apidog & Mức độ tương thích với Android

- Apidog cung cấp những cơ chế mock nào (Cloud Mock URL công khai, Local Mock server qua desktop app, CLI)?
- Android Emulator và thiết bị thật (qua Wi-Fi) kết nối tới Apidog Mock có gặp trở ngại gì về SSL/TLS, CORS, hay cấu hình `network_security_config.xml` không?
- **Smart Mock / Faker Data:** Apidog tự động sinh dữ liệu giả lập (tên, số điện thoại, ảnh URL, giá phòng) chuẩn đến mức nào so với kiểu dữ liệu định nghĩa trong `api-spec.md`?

### Q3. Xử lý chuẩn API PBL6 (P2-05 Conventions) & Kịch bản Lỗi

- Dữ liệu mock từ Apidog có bọc được theo đúng Response Wrapper Format của dự án (`{ statusCode, code, data }` cho success và `{ statusCode, code }` cho error) hay không?
- Làm sao Mobile có thể chủ động kích hoạt và kiểm thử các **kịch bản lỗi (Negative Testing)** từ Apidog Mock (ví dụ: `401 UNAUTHORIZED`, `422 VALIDATION FAILED`, `409 ROOM HAS ACTIVE CONTRACT`, `500 INTERNAL_SERVER_ERROR`) để hoàn thiện luồng xử lý ngoại lệ trên UI?

### Q4. Quản lý trạng thái & Giới hạn của Mock (Stateful vs Stateless)

- Apidog Mock Server là stateless (không lưu trữ state giữa các request). Khi Mobile thực hiện các hành động ghi (POST/PATCH/DELETE) như tạo hợp đồng mới, cập nhật hồ sơ, gửi tin nhắn... thì request GET sau đó sẽ không phản ánh thay đổi đó.
- Mobile đề xuất giải pháp xử lý vấn đề này ra sao trong lúc phát triển để luồng trải nghiệm E2E không bị gãy (ví dụ: optimistic update ở Repository/Local DB Room, hay can thiệp Interceptor)?

### Q5. Chi phí chuyển đổi (Switching Cost) khi BE hoàn thiện

- Khi BE deploy xong API thật lên staging, Mobile cần thay đổi những gì để app chuyển sang chạy với BE thật?
- Có đảm bảo tiêu chí: **"Chỉ thay đổi `BASE_URL` trong file cấu hình (Build Variant / Flavor) mà không cần sửa bất kỳ một dòng code logic hay DTO nào"** hay không?
- Rủi ro lệch chuẩn (API Contract Drift) giữa Apidog Mock và NestJS implementation thật là gì, và cách phòng tránh?

---

## 3. Các hạng mục công việc cụ thể (Tasks & Experiments)

Mobile Lead cần thực hiện các bài thử nghiệm thực tế (Hands-on PoC) trên dự án Android:

### Task 1: Thực nghiệm kết nối Retrofit/OkHttp tới Apidog Cloud Mock

- [ ] Lấy URL Mock của một endpoint công khai (ví dụ: `GET /rooms` hoặc `GET /me`) từ project Apidog của dự án.
- [ ] Tạo một project Android sample / nhánh feature trên `pbl6-mobile`, cấu hình Retrofit + Moshi/Kotlinx Serialization.
- [ ] Thực hiện gọi request từ Android Emulator / thiết bị thật, kiểm tra log qua HttpLoggingInterceptor.
- [ ] Đánh giá độ trễ (latency), độ ổn định mạng và kiểm tra xem có cần bypass SSL hay thêm network security config không.

### Task 2: Kiểm thử tính tương thích với Response Wrapper P2-05

- [ ] Định nghĩa `ApiResponse<T>` wrapper class bằng Kotlin:
  ```kotlin
  data class ApiResponse<T>(
      val statusCode: Int,
      val code: String,
      val data: T? = null,
      val pagination: PaginationMetadata? = null
  )
  ```
- [ ] Thử nghiệm parse response trả về từ Apidog Mock khi có data và khi trả về mã lỗi (`statusCode: 422`, `code: "VALIDATION FAILED"`).
- [ ] Thử nghiệm kích hoạt các Custom Expectation hoặc Rule trên Apidog (bằng Header hoặc Query Param) để ép trả về kịch bản lỗi.

### Task 3: Đánh giá các luồng nghiệp vụ đặc thù (Edge Cases)

Nghiên cứu giải pháp cho 4 bài toán nhạy cảm sau:

1. **Authentication Flow (JWT Bearer Token):**
   - Endpoint `POST /auth/login` mock trả về `accessToken` và `refreshToken`.
   - Phía Mobile lưu token vào `EncryptedSharedPreferences` / DataStore.
   - `AuthInterceptor` tự động đính kèm `Authorization: Bearer <token>` vào các request tiếp theo.
   - Xác nhận xem Apidog Mock có kiểm tra token thật không hay chấp nhận mọi token.
2. **Quy trình Upload Media 2 bước (Theo quyết định D40):**
   - Bước 1: `POST /media/presign-upload` nhận `uploadUrl` (presigned URL).
   - Bước 2: Client PUT file trực tiếp lên S3/Storage.
   - Bước 3: `POST /media/{id}/complete-upload`.
   - _Vấn đề:_ Apidog Mock trả về `uploadUrl` giả thì bước PUT file lên URL giả sẽ thất bại nếu không xử lý. Mobile Lead đề xuất cách xử lý cho luồng này khi dùng Mock (bỏ qua PUT step qua Interceptor mock hay trỏ vào đâu?).
3. **Mã QR Động & Thanh toán (D29, D49):**
   - Mock endpoint lấy dữ liệu hóa đơn và chuỗi mã VietQR payload; kiểm tra khả năng render mã QR cục bộ bằng thư viện ZXing/QR trên Android.
4. **Realtime / Chat / FCM (D24′):**
   - Apidog mock có hỗ trợ Socket.io / WebSocket không? Nếu không, phương án giả lập tin nhắn/sự cố cho màn hình Chat/Issue trên mobile là gì?

### Task 4: Thiết kế kiến trúc Network Layer & Build Variants cho Android

- [ ] Đề xuất cấu hình Gradle `productFlavors` hoặc `buildTypes` chuẩn:
  - `mock`: `BASE_URL = "https://mock.apidog.com/..."` (dùng cho dev/test độc lập khi BE chưa có)
  - `dev`: `BASE_URL = "http://10.0.2.2:3000/api/v1/"` hoặc IP LAN của BE dev

### Task 5: Đánh giá Code Generation vs Manual DTOs

- [ ] Khảo sát công cụ: Có nên dùng OpenAPI Generator Gradle Plugin để sinh tự động Retrofit interfaces & Data models từ file `openapi.yaml` của BE không?
- [ ] So sánh ưu điểm vs nhược điểm: Viết DTO bằng tay (kiểm soát 100% naming, validation, annotation) vs Code Gen tự động (nhanh nhưng dễ phát sinh code thừa, phụ thuộc plugin).

---

## 4. Yêu cầu báo cáo kết quả (Deliverable Requirements)

Sản phẩm bàn giao là file tài liệu: `pm/phase-3/discovery/mobile-apidog-e2e-research.md`.  
Nội dung báo cáo phải được cấu trúc rõ ràng với các phần sau:

1. **Executive Summary & Verdict (Kết luận tóm tắt):**
   - Trả lời trực diện: _Có thể triển khai E2E trước khi BE hoàn thiện không?_ (Khẳng định: **CÓ / CÓ KÈM ĐIỀU KIỆN / KHÔNG**).
   - Tỷ lệ khả thi trên tổng thể các module của Mobile.
2. **Proposed End-to-End Workflow (Quy trình phối hợp đề xuất):**
   - Sơ đồ/luồng từng bước từ khi BE cập nhật API Spec trên Apidog → Mobile kích hoạt Mock → Code feature → Chuyển sang cắm API thật của BE.
3. **Android Architecture & Configuration Pattern:**
   - Cấu hình `build.gradle.kts` (Flavors, BuildConfig).
   - Setup Dependency Injection (Hilt/Koin) cho NetworkModule và Retrofit.
   - Code mẫu xử lý `ApiResponse<T>` wrapper và Error Handling.
4. **Feature Mockability & Edge-Case Matrix:**
   - Bảng phân tích chi tiết: Tính năng nào mock được 100% mượt mà, tính năng nào cần workaround (Auth, Media Upload, Realtime Chat, Thanh toán QR).
5. **Rủi ro & Biện pháp phòng ngừa (Risks & Mitigation):**
   - Nguy cơ Contract Drift (BE sửa API mà Mobile không biết).
   - Cách kiểm soát breaking changes.
6. **PoC Snippets / Proof:**
   - Đoạn code mẫu thực tế đã chạy thành công trên Android gọi vào Apidog Mock kèm ảnh chụp logcat/kết quả màn hình (nếu có).

---

## 5. Definition of Done (DoD)

- [ ] File tài liệu `pm/phase-3/discovery/mobile-apidog-e2e-research.md` được tạo và hoàn thiện đầy đủ 6 phần nội dung theo yêu cầu.
- [ ] Đã trả lời rõ ràng câu hỏi về tính khả thi của việc Mobile code End-to-End trước khi BE xong.
- [ ] Đã thực hiện ít nhất 01 PoC thực tế gọi API mock từ Android bằng Retrofit và parse thành công dữ liệu theo format chuẩn P2-05.
- [ ] Đã có phương án giải quyết cụ thể cho 3 luồng phức tạp: Authentication (JWT), 2-step Media Upload (D40) và Error Scenarios.
- [ ] Đã đề xuất cấu hình Build Variant/Flavor để việc chuyển đổi từ Mock sang BE thật chỉ tốn 0 dòng code logic.
- [ ] Báo cáo được gửi và review bởi PM và BE Lead trước khi kết thúc ngày **2026-09-29**.
