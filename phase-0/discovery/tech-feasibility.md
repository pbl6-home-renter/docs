# Tech Feasibility Report — P0-04

**Assignee:** BE | **Sprint day:** D1–D2 (Tue 18/08 – Wed 19/08) | **Status:** Draft cho review PM
**Input:** `requirement.md`, `market-analysis.md` | **Stack:** NestJS + PostgreSQL, Swagger + Apidog

---

## 0. Tóm tắt nhanh (TL;DR)

| Hạng mục | Verdict | Ghi chú |
|---|---|---|
| Data model (10 entities) | ✅ OK | Quan hệ chuẩn, TypeORM/Prisma xử lý tốt |
| Auth (role-based, JWT+refresh) | ✅ OK | Pattern chuẩn NestJS, có sẵn nhiều boilerplate |
| Chốt số điện nước + bậc thang | ⚠️ Risk | Không phức tạp về code, nhưng nhiều edge case nghiệp vụ cần chốt sớm |
| Payment (VNPay/MoMo) | ⚠️ Risk (có fallback) | Sandbox có sẵn, miễn phí, nhưng effort + độ ổn định phụ thuộc bên thứ 3 |
| API contract (Swagger + Apidog) | ✅ OK | `@nestjs/swagger` generate OpenAPI, Apidog import qua URL |
| Deployment (Railway/Fly.io + Vercel) | ⚠️ Risk | Free tier 2026 đã siết chặt ở cả 2 nền tảng, cần chọn combo tối ưu chi phí (chi tiết mục 6) |

Không có hạng mục nào ở mức **Blocked**. Đề tài khả thi để triển khai trong phạm vi đồ án PBL6.

---

## 1. Data Model Sketch

### 1.1 Danh sách entity & field chính

**User**
- `id` (uuid, PK), `email` (unique), `phone` (unique), `password_hash`
- `roles` (array: `landlord` \| `tenant` \| `admin`) — D13: một user có thể mang nhiều vai trò
- `full_name`, `avatar_url`, `is_active`, `created_at`, `updated_at`
- Feasibility: ✅ OK — bảng gốc, không có gì đặc biệt.

**Building**
- `id` (uuid, PK), `owner_id` (FK → User, role phải là `landlord`)
- `name`, `address`, `lat`, `lng`, `created_at`
- Feasibility: ✅ OK.

**Room**
- `id` (uuid, PK), `building_id` (FK → Building)
- `code` (mã phòng, ví dụ "P101"), `area`, `price`, `max_occupants`
- `status` (enum: `vacant` \| `occupied` \| `maintenance`)
- Unique constraint: `(building_id, code)` — mỗi tòa nhà không được trùng mã phòng.
- Feasibility: ✅ OK.

**Contract**
- `id` (uuid, PK), `room_id` (FK), `tenant_id` (FK → User)
- `start_date`, `end_date`, `deposit`, `monthly_rent`
- `status` (enum: `draft` \| `active` \| `terminated` \| `expired`)
- `signature_mode` (always `template_upload`) — D18 (bỏ OTP/PIN/`e_ack` 31/08); file HĐ wet-sign 2 bên + `signed_at`, `contract_file_url`
- `signed_at`
- Ràng buộc nghiệp vụ cần enforce ở tầng service (không chỉ DB): **1 phòng chỉ có tối đa 1 hợp đồng `active` tại một thời điểm** — dùng partial unique index kiểu `CREATE UNIQUE INDEX ON contract (room_id) WHERE status = 'active'` (Postgres hỗ trợ tốt).
- Feasibility: ✅ OK, nhưng cần lưu ý điểm partial-unique-index ở trên khi viết migration.

**MeterReading**
- `id` (uuid, PK), `room_id` (FK), `period` (kiểu `date`, chuẩn hóa về ngày đầu tháng, ví dụ `2026-08-01`)
- `electricity_old`, `electricity_new`, `water_old`, `water_new`
- `image_url` (ảnh chốt số), `recorded_by` (FK → User), `created_at`
- Unique constraint: `(room_id, period)` — mỗi phòng chỉ chốt số 1 lần/kỳ.
- Feasibility: ✅ OK. Xem thêm edge case ở mục 3.

**Invoice**
- `id` (uuid, PK), `contract_id` (FK), `period`
- `rent_amount` (prorated), `other_fees` (jsonb — mảng `{label, amount}` cho phí phát sinh: giặt ủi, gửi xe...); điện/nước/phí định kỳ đọc từ snapshot `utility_breakdown`/`fees_breakdown` (D30/D37)
- `total_amount`, `status` (enum: `pending` \| `paid` \| `overdue` \| `void`)
- `issued_at` (nullable — set khi phát hành), `due_date = issued_at + N ngày` (N cấu hình, mặc định 5), `paid_at`
- Unique constraint: `(contract_id, period)`.
- Feasibility: ✅ OK.

**Payment**
- `id` (uuid, PK), `invoice_id` (FK)
- `amount`, `method` (enum: `vnpay` \| `momo` \| `cash` \| `mock`)
- `transaction_id` (mã giao dịch phía cổng thanh toán, nullable với `cash`)
- `status` (enum: `pending` \| `success` \| `failed`)
- `paid_at`, `raw_gateway_response` (jsonb — lưu nguyên payload IPN để debug/đối soát)
- Quan hệ 1 Invoice - N Payment (cho phép retry khi thanh toán thất bại).
- Feasibility: ✅ OK.

**IssueReport**
- `id` (uuid, PK), `room_id` (FK), `tenant_id` (FK)
- `category` (enum: `electricity` \| `water` \| `structural` \| `other`)
- `description`, `images` (jsonb array URL)
- `status` (enum: `open` \| `in_progress` \| `resolved`)
- `created_at`, `resolved_at`
- Feasibility: ✅ OK.

**RoommateProfile**
- `id` (uuid, PK), `user_id` (FK, unique — 1 user chỉ có 1 hồ sơ)
- `habits` (jsonb: `{sleep_time, smoking, pets, cleanliness, noise_tolerance,...}`)
- `bio`, `budget_min`, `budget_max`, `preferred_area`
- Feasibility: ✅ OK — dùng jsonb cho `habits` để linh hoạt thêm tiêu chí mà không cần migration liên tục.

**MatchRequest**
- `id` (uuid, PK), `requester_id` (FK → User), `target_id` (FK → User)
- `status` (enum: `pending` \| `accepted` \| `rejected`)
- `compatibility_score` (int 0-100, do AI trả về), `ai_notes` (text, lời khuyên ngắn từ LLM)
- `created_at`
- Unique constraint: `(requester_id, target_id)` để tránh gửi trùng request.
- Feasibility: ✅ OK.

### 1.2 Sơ đồ quan hệ (rút gọn)

```
User (landlord) 1---N Building 1---N Room
Room 1---N Contract (chỉ 1 "active" tại 1 thời điểm)
Contract 1---N Invoice 1---N Payment
Room 1---N MeterReading
Room 1---N IssueReport
User (tenant) 1---1 RoommateProfile
User 1---N MatchRequest (as requester / as target)
```

### 1.3 Feasibility notes chung
- NestJS + TypeORM hoặc Prisma đều support đầy đủ enum, jsonb, partial unique index (TypeORM cần viết migration tay cho partial index; Prisma hiện chưa hỗ trợ partial index native → nếu chọn Prisma thì phải viết raw SQL migration cho riêng index này).
- **Khuyến nghị:** dùng Prisma cho tốc độ phát triển (schema-first, migrate nhanh, đồ án timebox ngắn), chấp nhận 1-2 chỗ raw SQL cho constraint đặc thù.

---

## 2. Auth & Role Model

- 3 role: `landlord`, `tenant`, `admin` — lưu dạng **array/set `roles` trên User** thay vì enum đơn: D13 yêu cầu một user có thể vừa landlord vừa tenant (chủ trọ cũng phải ở chỗ khác). Guard `@Roles()` kiểm tra membership (pass nếu token chứa role cần thiết). Vẫn không cần bảng Role riêng — không có phân quyền động trong scope MVP (RBAC/membership đầy đủ → Phase 1+, tham chiếu `decisions.md` D12).
- **Access token:** JWT, thời hạn ngắn (15 phút), payload gồm `sub`, `roles[]`.
- **Refresh token:** thời hạn dài (7-30 ngày), lưu dạng hash (bcrypt/sha256) trong bảng `refresh_token` (hoặc Redis nếu muốn revoke nhanh + hỗ trợ logout-all-devices). Rotate refresh token mỗi lần dùng (phát hiện reuse → revoke toàn bộ session, chống đánh cắp token).
- **Authorization:** dùng `@UseGuards(JwtAuthGuard, RolesGuard)` + custom decorator `@Roles('landlord')` ở NestJS — pattern chuẩn, có nhiều ví dụ chính thức từ tài liệu NestJS.
- Mobile app (Kotlin) lưu token trong `EncryptedSharedPreferences`, không lưu plaintext.
- Feasibility: ✅ OK — không có rủi ro kỹ thuật, đây là pattern rất phổ biến.

---

## 3. Chốt số điện nước & Bậc thang (Utility Closing)

### 3.1 Luồng nghiệp vụ đề xuất
1. Cuối kỳ (hàng tháng), landlord chụp ảnh đồng hồ điện/nước → tạo `MeterReading` (số cũ tự động lấy từ kỳ trước / baseline bàn giao OCR, số mới do **OCR điền; sai/mờ → chủ trọ sửa tay đúng số thực tế** rồi xác nhận — D35).
2. Hệ thống tính `consumption = new - old`, áp bậc thang → ra `electricity_amount`.
3. Job (cron NestJS `@nestjs/schedule`) tự sinh `Invoice` từ `Contract` đang active + `MeterReading` của kỳ + `monthly_rent` + `other_fees`.

### 3.2 Công thức bậc thang
Bậc thang điện sinh hoạt (theo biểu giá EVN) được thiết kế cho **1 hộ dùng riêng 1 đồng hồ tổng**. Trong mô hình nhà trọ, chủ nhà thường:
- (a) mỗi phòng có đồng hồ riêng nhưng chủ nhà tính giá **cao hơn giá bậc 1 của EVN** (phổ biến 3.500–4.000đ/kWh đồng giá, không bậc thang) — đây là thực tế phổ biến và **đơn giản hóa được bài toán tính toán**; hoặc
- (b) nhiều phòng dùng chung 1 đồng hồ tổng của tòa nhà, bậc thang áp cho tổng rồi phân bổ lại theo tỷ lệ tiêu thụ từng phòng — **phức tạp hơn nhiều** và dễ gây tranh cãi với tenant.

**Khuyến nghị MVP:** cho `Building` một field cấu hình `pricing_mode` (enum: `flat_rate` \| `tiered`) + bảng `rate_tier` (nếu `tiered`: `min_kwh`, `max_kwh`, `unit_price`) để landlord tự cấu hình. Mặc định seed sẵn `flat_rate` (ví dụ 3.800đ/kWh) — đáp ứng đúng nhu cầu 90% chủ trọ như mô tả trong `market-analysis.md` (Mona House, KiotViet đều cho tùy biến đơn giá). Bậc thang thật (option b) để dạng **stretch goal**, không phải core MVP.

### 3.3 Edge case cần chốt trước khi code
| Edge case | Đề xuất xử lý |
|---|---|
| Kỳ đầu tiên chưa có số cũ | Bắt buộc nhập `electricity_old`/`water_old` thủ công khi tạo `Contract`, dùng làm baseline |
| Tenant chuyển đi giữa tháng | Tính tiền phòng theo tỷ lệ số ngày ở thực tế (prorate); điện nước vẫn theo số thực đo tại ngày chốt hợp đồng |
| Thay đồng hồ mới (số reset về 0) | Thêm field `is_meter_reset` (boolean) trên `MeterReading`; nếu true thì `consumption = new` (bỏ qua trừ số cũ) |
| Landlord quên chốt số | Cho phép chốt trễ (grace period cấu hình, ví dụ 5 ngày đầu tháng sau); nếu quá hạn, hệ thống cảnh báo qua notification, không tự bịa số |
| Phát hiện sai số sau khi đã gửi hóa đơn | Invoice có status `void`; tạo Invoice mới thay thế, giữ lịch sử — **không sửa trực tiếp Invoice đã gửi** (tránh mất audit trail) |
| Nhiều phòng dùng chung 1 đồng hồ | Đánh dấu Risk, xử lý ở mức Building (đồng hồ tổng) + hệ số phân bổ thủ công do landlord nhập — không tự động 100% |

Feasibility: ⚠️ **Risk ở mức nghiệp vụ, không phải kỹ thuật.** Code không khó, nhưng nhóm phải chốt rõ `flat_rate` là default cho MVP để tránh scope creep sang bài toán phân bổ điện nước dùng chung — nên đưa câu hỏi này vào cuộc họp scope freeze (P0-06).

---

## 4. Payment: VNPay vs MoMo

| Tiêu chí | VNPay | MoMo |
|---|---|---|
| Sandbox miễn phí | Có (VNPay Merchant Sandbox, đăng ký merchant test qua email, cấp `TMN Code` + `Hash Secret`) | Có (MoMo Developer Portal, cấp `Partner Code`, `Access Key`, `Secret Key`) |
| Luồng tích hợp BE | Tạo URL thanh toán (redirect) → user thanh toán trên trang VNPay → redirect về `return_url` + verify checksum (HMAC SHA512) → nhận thêm IPN (server-to-server) để xác nhận cuối cùng | Tương tự: tạo request ký HMAC SHA256 → redirect hoặc trả QR code → nhận callback (IPN) xác nhận |
| Tài liệu & cộng đồng | Rất phổ biến ở VN, nhiều mẫu code NestJS trên GitHub | Tài liệu tốt, nhưng ví dụ NestJS ít hơn VNPay |
| Effort ước tính (BE) | ~2–3 ngày làm việc: tạo URL, xử lý return URL, verify chữ ký, xử lý IPN, viết test | ~2–3 ngày làm việc, tương đương |
| Rủi ro cho đồ án | Sandbox có thể chậm duyệt merchant, hoặc phía thầy/cô chấm bài không có tài khoản test thật → nên có phương án dự phòng | Tương tự |

### 4.1 Quyết định (Payment decision)
- **MVP:** Tích hợp **VNPay sandbox** làm phương thức chính (tài liệu & ví dụ nhiều hơn, dễ debug trong thời gian ngắn).
- **MoMo:** để dạng stretch goal nếu còn thời gian sau khi VNPay chạy ổn — kiến trúc code nên tách interface `PaymentGateway` (strategy pattern) để thêm MoMo sau này không phải sửa core logic.
- **Fallback bắt buộc:** luôn có `method = mock` — một endpoint giả lập thanh toán thành công ngay lập tức (bật/tắt qua biến môi trường `ENABLE_MOCK_PAYMENT`). Đây là lưới an toàn khi demo/bảo vệ đồ án mà sandbox của bên thứ 3 gặp sự cố (hết hạn merchant, rate limit, sập server test...).

Feasibility: ⚠️ **Risk có kiểm soát** — rủi ro nằm ở việc phụ thuộc dịch vụ bên thứ 3 (thời gian duyệt merchant, uptime sandbox), không nằm ở độ khó kỹ thuật. Có fallback nên không Blocked.

---

## 5. API Contract Workflow (Swagger + Apidog)

1. **Viết trong NestJS:** dùng decorator `@nestjs/swagger` — `@ApiTags`, `@ApiOperation`, `@ApiProperty` trên DTO class. NestJS tự sinh spec OpenAPI 3.0 tại runtime, expose UI tại `/api-docs` và JSON raw tại `/api-docs-json`.
2. **Đồng bộ sang Apidog:** Apidog hỗ trợ import trực tiếp từ URL OpenAPI JSON (import 1 lần hoặc cấu hình "scheduled sync" để tự cập nhật định kỳ) — không cần thao tác thủ công lặp lại mỗi khi BE đổi API.
3. **FE (React) & Mobile (Kotlin) tiêu thụ:**
   - Trong giai đoạn BE chưa xong, FE/Mobile dùng **Apidog Mock Server** (tự sinh từ spec) để code song song, không bị block.
   - Khi BE deploy, đổi base URL sang server thật — Apidog cho phép cấu hình nhiều environment (mock / dev / staging).
4. **Quy trình khuyến nghị:** BE cập nhật DTO → CI/CD (hoặc thủ công) chạy `npm run start` → Apidog pull spec mới → BE thông báo trong task tracker khi có breaking change (đổi field, đổi status code) để FE/Mobile cập nhật kịp.

Feasibility: ✅ OK — đây là workflow tiêu chuẩn, không có rủi ro kỹ thuật, chỉ cần kỷ luật quy trình (thông báo breaking change).

---

## 6. Deployment Plan

> Ghi chú quan trọng: free tier của Railway và Fly.io đã bị **siết chặt đáng kể** so với vài năm trước, cần cập nhật lại giả định trước khi chốt platform.

### 6.1 Tình trạng free tier hiện tại (2026)
- **Railway:** không còn free tier "xài mãi" — chỉ có **Trial $5 credit** (không cần thẻ, dùng 1 lần khi mới tạo tài khoản) và sau đó **Free plan chỉ $1 tín dụng/tháng**, gần như không đủ chạy app + Postgres liên tục. Muốn chạy ổn định (24/7) cần **Hobby plan $5/tháng**.
- **Fly.io:** free tier cho tài khoản mới đã bị **gỡ bỏ hoàn toàn từ tháng 10/2024** — tài khoản mới chỉ có trial ngắn (khoảng 2 giờ hoặc 7 ngày), sau đó bắt buộc gắn thẻ, tính phí theo giây. Một app nhỏ + Postgres roi vào khoảng $8–12/tháng.
- **Render:** vẫn có free tier thật cho **web service** (750 giờ/tháng, sleep sau 15 phút không hoạt động, cold start 30-60s) và **static site free vô hạn**. Riêng **Postgres free của Render chỉ tồn tại 30 ngày rồi bị xoá** — không phù hợp để chạy suốt kỳ đồ án.
- **Neon:** Postgres serverless có **free tier thật, không giới hạn thời gian** (100 CU-giờ/tháng, 0.5GB storage/project, scale-to-zero khi rảnh) — phù hợp làm database miễn phí lâu dài cho đồ án.
- **Vercel:** free tier (Hobby) cho frontend/Next.js vẫn tốt như trước, phù hợp deploy web React (dù React thuần SPA build tĩnh cũng deploy ngon trên Vercel).

### 6.2 Khuyến nghị combo triển khai
| Thành phần | Platform | Lý do |
|---|---|---|
| NestJS BE (Docker/Node) | **Render Web Service (free)**, nâng cấp **Starter $7/tháng** nếu cần always-on (không cold start) khi demo | Free tier thật, không cần thẻ để bắt đầu; cold start 30-60s chấp nhận được cho đồ án, chỉ cần ping/keep-alive nếu demo trực tiếp |
| PostgreSQL | **Neon (free, vĩnh viễn)** thay vì Postgres free của Render (hết hạn 30 ngày) | Tránh mất dữ liệu giữa kỳ đồ án; Neon là Postgres chuẩn, NestJS/TypeORM/Prisma kết nối bình thường qua connection string |
| FE Web (React) | **Vercel (free/Hobby)** | Free tier ổn định, tối ưu cho SPA/Next.js, CDN tốt |
| Mobile App | Build APK thủ công / Firebase App Distribution (không cần hosting server) | Không phát sinh chi phí |

### 6.3 Chi phí ước tính
- **Phương án free hoàn toàn:** $0/tháng — chấp nhận cold start ở BE khi không có traffic (phù hợp cho đồ án, chỉ trả tiền nếu cần always-on lúc bảo vệ).
- **Phương án ổn định khi demo:** ~$7/tháng (Render Starter cho BE) + $0 (Neon free + Vercel free) = **~$7/tháng**, chỉ cần bật trong tuần bảo vệ đồ án rồi hạ về free.
- Railway/Fly.io **không còn là lựa chọn tối ưu chi phí** so với 1-2 năm trước — có thể dùng như phương án dự phòng nếu team quen thao tác CLI của Railway, nhưng ngân sách sẽ từ $5/tháng (Railway Hobby) trở lên ngay từ đầu.

### 6.4 Deployment steps (rút gọn)
1. Dockerize NestJS app (Dockerfile chuẩn multi-stage build).
2. Tạo project trên Render, connect GitHub repo, cấu hình build command (`npm run build`) + start command (`npm run start:prod`), set biến môi trường (DB connection string từ Neon, JWT secret, VNPay keys...).
3. Tạo project Neon, lấy connection string, chạy migration (`prisma migrate deploy` hoặc TypeORM migration) lên Neon.
4. Deploy FE React lên Vercel, connect GitHub repo, set `VITE_API_URL`/`NEXT_PUBLIC_API_URL` trỏ về Render URL.
5. Cấu hình CORS ở NestJS cho domain Vercel.
6. (Optional) Set up UptimeRobot/cron-job.org ping BE mỗi 10 phút để giảm cold start khi cần demo ổn định mà chưa muốn trả phí Starter.

Feasibility: ⚠️ **Risk (đã có phương án xử lý)** — rủi ro chính là cold start miễn phí gây trải nghiệm demo không mượt, đã có giải pháp (ping keep-alive hoặc nâng cấp $7/tháng tạm thời tuần bảo vệ).

---

## 7. Feasibility Matrix (đầy đủ theo MVP candidate features)

| # | Feature | Verdict | Ghi chú |
|---|---|---|---|
| 1 | Quản lý danh sách phòng, sơ đồ tòa nhà | ✅ OK | CRUD chuẩn |
| 2 | Hợp đồng điện tử (tạo, quản lý trạng thái) | ✅ OK | Cần partial unique index cho "1 phòng 1 hợp đồng active" |
| 3 | Chốt số điện nước hàng tháng | ⚠️ Risk | Nghiệp vụ cần chốt rõ flat-rate vs bậc thang trước khi code (mục 3) |
| 4 | Tự động sinh hóa đơn | ✅ OK | Cron job NestJS `@nestjs/schedule` |
| 5 | Theo dõi trạng thái thanh toán | ✅ OK | Phụ thuộc kết quả mục 6 |
| 6 | Thống kê doanh thu/chi phí | ✅ OK | Query aggregate trên Invoice/Payment, không cần lib ngoài |
| 7 | Tìm phòng theo bản đồ, filter nâng cao (Mobile) | ✅ OK | Dùng PostGIS hoặc filter đơn giản bằng lat/lng + bounding box (không cần PostGIS nếu MVP không cần tìm kiếm bán kính chính xác) |
| 8 | Nhận hóa đơn, thanh toán VNPay/MoMo (Mobile) | ⚠️ Risk | Xem mục 4, có fallback mock |
| 9 | Tìm người ở ghép (hồ sơ tính cách) | ✅ OK | CRUD RoommateProfile + MatchRequest |
| 10 | Báo cáo sự cố | ✅ OK | CRUD đơn giản |
| 11 | AI Matchmaking (compatibility score qua LLM API) | ✅ OK | Gọi API bên ngoài (OpenAI/Gemini...), lưu kết quả vào `MatchRequest.compatibility_score` + `ai_notes`; cần xử lý timeout/rate-limit của LLM API |
| 12 | AI Auto-Description (sinh mô tả phòng từ keyword) | ✅ OK | Tương tự #11, prompt đơn giản hơn |
| 13 | Hợp đồng điện tử (template + wet-sign upload) | ✅ OK | App sinh mẫu HĐ → 2 bên ký tay giấy → up file đã ký (artifact pháp lý); **bỏ OTP/PIN/`e_ack`** (31/08); parse/OCR PDF → field (D18) |
| 14 | Contract Q&A bot — **ĐÃ BỎ (D15, 31/08)** | — | Không còn trong scope; full-text RAG chatbot chỉ còn là Phase 1+ nếu có nhu cầu |
| 15 | Cross-platform: cả 2 role trên cả web lẫn mobile | ✅ OK backend / ⚠️ Effort FE | Backend đã role-agnostic; chi phí nằm ở UX 2 role × 2 platform — staging primary→secondary (D13) |

**Không có feature nào bị đánh giá Blocked.**

---

## 8. Kết luận & Kiến nghị cho P0-06 (scope freeze)

1. Chốt **`pricing_mode = flat_rate`** là default cho tính năng điện nước ở MVP; bậc thang thật + phân bổ đồng hồ tổng để dạng stretch goal.
2. Chốt **VNPay sandbox** là phương thức thanh toán chính, luôn giữ **mock payment** làm phương án demo an toàn.
3. Chốt **Prisma** làm ORM (tốc độ phát triển nhanh trong timebox ngắn), chấp nhận viết raw SQL cho constraint đặc thù (partial unique index).
4. Chốt combo deployment: **Render (BE) + Neon (DB) + Vercel (FE)** — chi phí $0/tháng bình thường, ~$7/tháng khi cần always-on lúc demo/bảo vệ. Không dùng Fly.io do free tier đã bị gỡ hoàn toàn.
5. Quy trình API contract: BE viết decorator Swagger đầy đủ ngay từ đầu, đồng bộ Apidog qua URL sync, thông báo breaking change chủ động cho FE/Mobile.

Deliverable này sẵn sàng để review với PM trước khi scope freeze (Thu).
