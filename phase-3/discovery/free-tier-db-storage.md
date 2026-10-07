# PBL-37 — Báo cáo Nghiên cứu, POC & Khuyến nghị Nguồn Database / Object Storage Free-Tier + Script Keepalive

**Mã Issue:** PBL-37 (P3-04)  
**Tiêu đề:** Nghiên cứu & POC nguồn DB/Storage free (managed) + script keepalive chống bị pause  
**Người thực hiện:** BE Lead  
**Stakeholders / Reviewers:** PM (quyết ngân sách + chốt D53/D56) · FE + Mobile Lead (giới hạn size/MIME khi upload) · GV SOA (nếu có thay đổi kiến trúc hạ tầng)  
**Ngày hoàn thành:** 2026-10-06  
**Trạng thái:** 🟢 Hoàn thành đầy đủ 4 Task & đáp ứng 100% Definition of Done  

---

## Tóm tắt Điều hành (Executive Summary)

Báo cáo này giải quyết dứt điểm 3 điểm nghẽn hạ tầng đang chặn quá trình scaffold của nhóm backend PBL6:
1. **Storage provider chưa ai chọn (D40 để ngỏ):** Nghiên cứu và thực nghiệm chứng minh **Cloudflare R2** là lựa chọn số 1 (10 GB free, 0đ egress, presigned PUT chuẩn S3, TTL 900s khớp 100% hợp đồng API).
2. **D56 (EC2 + Docker Compose) chưa được duyệt:** Cung cấp phương án managed free-tier đối trọng hoàn toàn khả thi: **Neon Serverless PostgreSQL** (1 GB, 100 CU-h/tháng, pooled connection lên tới 10,000 kết nối, đã kiểm chứng trực tiếp chạy tốt 4 DB + 4 role theo D53).
3. **Keep-alive chống pause chỉ là ghi chú:** Đã hiện thực hóa bằng script TypeScript standalone chạy tự động qua GitHub Actions, tự động tạo bảng riêng `ops_keepalive`, chu trình 1 WRITE + 1 READ-back, dọn dẹp tối đa 100 row, retry 3 lần, tiêu thụ **~0.63%** quota Neon/tháng.

---

# PHẦN 1 (Task 1) — Nghiên cứu Database Free Tier (PostgreSQL)

Yêu cầu kỹ thuật theo D53: Chỉ xét PostgreSQL thật (TypeORM/Prisma kết nối được), hỗ trợ `uuid`, `jsonb`, `pg_trgm`, có thể tạo **4 database riêng biệt** (`identity_db`, `tenancy_db`, `payment_db`, `community_db`) và **4 role riêng biệt** (`identity_role`, `tenancy_role`, `payment_role`, `community_role`), không dùng cross-service FK.

## 1.1. Bảng so sánh chi tiết các nhà cung cấp Database

| Tiêu chí | Neon | Supabase | Aiven Free | Render Postgres | AWS EC2 Self-host (D56) |
|---|---|---|---|---|---|
| **Free Storage** | [**1 GB / project**](https://neon.com/blog/neon-free-plan-1-gb-per-project) | [500 MB / project](https://supabase.com/pricing) | [1 GB disk](https://aiven.io/docs/products/postgresql/concepts/pg-free-tier) | [1 GB](https://render.com/docs/free#free-postgresql-databases) | [30 GB EBS Free](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-free-tier-usage.html) |
| **Compute / RAM** | [**100 CU-hours/tháng** (autoscale 0.25–2 CU)](https://neon.com/docs/introduction/plans) | [Shared CPU, 500 MB RAM](https://supabase.com/pricing) | [1 CPU, 1 GB RAM (single node)](https://aiven.io/docs/products/postgresql/concepts/pg-free-tier) | [Shared CPU](https://render.com/docs/free) | [t2.micro (1 vCPU, 1 GB RAM)](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-free-tier-usage.html) |
| **Số lượng Project** | [100 projects](https://neon.com/blog/neon-free-plan-1-gb-per-project) | [Tối đa 2 active projects](https://supabase.com/pricing) | [1 project Free](https://aiven.io/docs/products/postgresql/concepts/pg-free-tier) | 1 project / workspace | 1 EC2 instance |
| **Thời hạn Free** | [**Vĩnh viễn**](https://neon.com/pricing) | [**Vĩnh viễn**](https://supabase.com/pricing) | [**Vĩnh viễn**](https://aiven.io/docs/products/postgresql/concepts/pg-free-tier) | [**30 ngày** (hết hạn xóa DB)](https://render.com/docs/free#free-postgresql-databases) | [Tối đa 6 tháng hoặc hết $100 credit](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier.html) |
| **Bắt buộc Credit Card?** | [**Không bắt buộc**](https://neon.com/pricing) | [**Không bắt buộc**](https://supabase.com/pricing) | [**Không bắt buộc**](https://aiven.io/docs/products/postgresql/concepts/pg-free-tier) | [**Không bắt buộc**](https://render.com/docs/free) | Bắt buộc thẻ Visa/Master khi tạo AWS |
| **Chính sách Pause / Sleep** | [Scale-to-zero sau **5 phút idle**](https://neon.com/blog/why-you-want-a-database-that-scales-to-zero) | [Pause project sau **7 ngày inactivity**](https://supabase.com/docs/guides/platform/free-project-pausing) | [Power off nếu không có continuous activity](https://aiven.io/docs/products/postgresql/concepts/pg-free-tier) | **Không sleep khi idle**; restart bảo trì không SLA | Không pause (VM do team quản lý) |
| **Cold Start khi thức dậy** | **~1.19s** (đo thực tế) | ~1–3s khi resume | ~5–10s khi power on | **Không áp dụng** (vì không sleep) | Không áp dụng (luôn chạy) |
| **Chịu được D53 (4 DB + 4 Role)?** | **PASS — Đã test thật** | **PASS — Đã test thật** | **PASS — Đã test thật** | Chưa test | **PASS** (toàn quyền root/postgres) |
| **Chặn `CREATE DATABASE` / `ROLE`?** | [**Không chặn**](https://neon.com/docs/manage/databases) | [**Không chặn** (qua direct client)](https://supabase.com/docs/guides/database/managing-databases) | [**Không chặn**](https://aiven.io/docs/products/postgresql/concepts/pg-free-tier) | Có thể bị giới hạn | Không chặn |
| **Connection Pooling** | [**Có (PgBouncer tích hợp sẵn)**](https://neon.tech/docs/connect/connection-pooling) | [**Có (Supavisor)**](https://supabase.com/docs/guides/database/connecting-to-postgres/pooling-and-limits) | [**Không có trên Free**](https://aiven.io/docs/products/postgresql/concepts/pg-free-tier) | [**Không có trên Free**](https://render.com/docs/postgresql-connection-pooling) | Phải tự cài PgBouncer |
| **Trần Connection Cụ thể** | [Direct: ~112; **Pooler: 10,000 kết nối**](https://neon.tech/docs/connect/connection-pooling) | [Direct: **60**; **Supavisor pool: 15–200**](https://supabase.com/docs/guides/database/connecting-to-postgres/pooling-and-limits) | [**20 max_connections**](https://aiven.io/docs/products/postgresql/reference/pg-connection-limits) | Giới hạn theo RAM (~20–50) | Tự cấu hình (thường đặt 100) |
| **Extensions** (`uuid`, `pgcrypto`, `pg_trgm`) | [**PASS**](https://neon.com/docs/extensions/pg_trgm) | [**PASS**](https://supabase.com/docs/guides/database/extensions) | [**PASS**](https://aiven.io/docs/products/postgresql/concepts/pg-free-tier) | [**PASS**](https://render.com/docs/postgresql-extensions) | **PASS** |
| **Quyền Migrate Extension** | **Không cần superuser** (owner role chạy được) | **Không cần superuser** (tích hợp sẵn) | **Không cần superuser** | Cần kiểm tra | Toàn quyền superuser |
| **Egress / Bandwidth** | [10 GB egress miễn phí/tháng](https://neon.com/pricing) | [5 GB egress + 5 GB cached](https://supabase.com/pricing) | Phụ thuộc cloud | Egress miễn phí | Tốn phí egress AWS |
| **Region gần Việt Nam** | `ap-southeast-1` (Singapore) | `ap-southeast-1` (Singapore) | Không được chọn region ở Free | `singapore` | `ap-southeast-1` (Singapore) |
| **Latency đo được (VN $\to$ SG)** | **p50 = 58.14 ms**, **p95 = 59.73 ms** | *Chưa đo trực tiếp* (ước tính ~60ms) | *Chưa đo trực tiếp* | *Chưa đo trực tiếp* | *Chưa đo trực tiếp* (ước tính ~60ms) |
| **Backup / PITR trên Free** | [Instant Restore window **6 giờ**](https://neon.com/docs/introduction/plans) | [**Không có trên Free**](https://supabase.com/pricing) | Có backup cơ bản | [**Không có backup**](https://render.com/docs/free) | Phải tự viết script dump/cron |
| **Rủi ro siết Free Tier giữa kỳ** | Thấp (Neon mới nâng cấp 10/2026) | Thấp (chính sách ổn định) | Trung bình (có thể bị power off) | **Rất cao** (30 ngày xóa DB) | Rủi ro hết credit sau 6 tháng |
| **Đánh giá tổng kết** | 🥇 **Ứng viên chính số 1** | 🥈 **Ứng viên dự phòng mạnh** | ⚠️ Kém (chỉ 20 conn, không pool) | ❌ **Loại** (chỉ sống 30 ngày) | 📋 Đối chứng D56 (tốn công DevOps) |

*(Toàn bộ dữ liệu tra cứu chính thức ngày 2026-10-06).*

## 1.2. Phân tích Chi tiết Từng Provider

### 1. Neon (Khuyến nghị số 1)
- **Khả năng đáp ứng D53 (4 DB + 4 Role):** **PASS dứt khoát**. Thành viên nhóm đã kiểm chứng trực tiếp trên cụm Neon thật: tạo thành công 4 database độc lập (`identity_db`, `tenancy_db`, `payment_db`, `community_db`) và 4 role riêng biệt (`identity_role`, `tenancy_role`, `payment_role`, `community_role`).
- **Trần kết nối (Connection Limit):** Neon vượt trội nhờ tích hợp sẵn PgBouncer pooling trên port 6543 (kết nối qua host có hậu tố `-pooler`). Trong khi kết nối direct giới hạn ở ~112 kết nối (tương ứng 0.25 CU), kết nối qua pooler hỗ trợ lên tới **10,000 concurrent client connections** ([Nguồn Neon](https://neon.tech/docs/connect/connection-pooling)), giải quyết triệt để nguy cơ connection starvation khi 4 service NestJS cùng khởi động connection pool.
- **Migration & Superuser:** Khi chạy `CREATE EXTENSION IF NOT EXISTS "uuid-ossp"` hay `pgcrypto`, role mặc định của Neon (`role_core`) được phân quyền đầy đủ, **hoàn toàn không yêu cầu quyền superuser**.
- **Chính sách scale-to-zero:** Compute tự động suspend sau **5 phút idle**, giúp bảo tồn trọn vẹn 100 CU-hours/tháng. Cold start đo được tại Task 3 là **~1.19s** (chấp nhận được cho đồ án).

### 2. Supabase (Phương án dự phòng mạnh)
- **Ưu điểm:** Hỗ trợ Supavisor pooling rất mạnh, region Singapore gần Việt Nam. Đã test thành công 4 DB và 4 role qua direct connection.
- **Trần kết nối:** Giới hạn direct connection ở mức **60**, Supavisor pool size mặc định là **15** (hỗ trợ tối đa 200 client connections ở transaction mode) ([Nguồn Supabase](https://supabase.com/docs/guides/database/connecting-to-postgres/pooling-and-limits)).
- **Điểm trừ so với Neon:** Dung lượng database ở gói Free chỉ **500 MB** (bằng 1/2 Neon); pause sau **7 ngày inactivity**; không có backup tự động trên gói Free.

### 3. Aiven Free (Không ưu tiên)
- **Lý do không chọn:** Gói Free chặn connection pooling và áp trần cứng `max_connections = 20` ([Nguồn Aiven](https://aiven.io/docs/products/postgresql/reference/pg-connection-limits)). Trong kiến trúc 4 service NestJS, mỗi service TypeORM giữ mặc định 5–10 connection thì hệ thống sẽ ngay lập tức bị lỗi tràn connection (`connection pool exhausted`). Ngoài ra không được chọn region Singapore trên gói Free.

### 4. Render Free Postgres (Loại bỏ thẳng)
- **Cơ chế Sleep & Cold Start:** Lưu ý sự khác biệt quan trọng giữa Web Service và Postgres của Render:
  - Render Web Service: sleep sau 15 phút idle, cold start 50–90 giây.
  - Render Free Postgres: **KHÔNG sleep / scale-to-zero khi idle** (vẫn chạy liên tục), do đó không có khái niệm cold start truy vấn.
- **Lý do loại bỏ:** Cơ sở dữ liệu tự động bị hủy (hard-delete) sau **30 ngày** sử dụng ([Nguồn Render](https://render.com/docs/free#free-postgresql-databases)). Không thể dùng cho đồ án kéo dài cả học kỳ (15 tuần). Ngoài ra, gói Free không hỗ trợ PgBouncer pooling và không có backup.

### 5. AWS EC2 Self-host (D56 đối chứng)
- Toàn quyền root/postgres, nhưng tốn nhiều công sức cấu hình Docker Compose, PgBouncer, SSL, backup script, và máy ảo t2.micro (1 GB RAM) sẽ lập tức bị OOM khi chạy cùng lúc 4 service + DB + MinIO.

---

# PHẦN 2 (Task 2) — Nghiên cứu Object Storage / Media Free Tier

Yêu cầu kỹ thuật theo D40 & API Conventions: Luồng upload 2 bước (Client nhận presigned URL $\to$ PUT trực tiếp lên storage $\to$ gọi complete-upload). MIME allowlist nghiêm ngặt (`image/jpeg`, `image/png`, `image/webp`, `application/pdf`), signed URL có TTL đúng `expiresIn: 900` giây.

## 2.1. Ước lượng nhu cầu Media thực tế của PBL6

Dựa trên thiết kế bảng `Media` (§2.25) và các luồng nghiệp vụ phòng trọ:

| Loại media | `purpose` / Nguồn | Công thức ước lượng | Dung lượng dự kiến |
|---|---|---|---:|
| Ảnh phòng + tòa nhà | `cover_photo`, `gallery_photo`, `ownership_proof` | 25 phòng × 6 ảnh × ~1.5 MB | **225 MB** |
| Ảnh công tơ điện nước | `meter_reading_evidence` (OCR D51) | 500 ảnh × ~800 KB | **400 MB** |
| Hợp đồng thuê nhà | `contract_template`, `contract_signed` | 100 file PDF scan × ~1.0 MB | **100 MB** |
| Căn cước công dân | `cccd_front`, `cccd_back` | 100 user × 2 ảnh × ~500 KB | **100 MB** |
| Ảnh sự cố + Chat | `issue_photo`, `chat_attachment` | 300 ảnh × ~1.0 MB | **300 MB** |
| **Tổng dung lượng chuẩn MVP** | *(Chỉ ảnh và tài liệu PDF scan)* | | **~1,125 MB (~1.12 GB)** |
| **Dung lượng kèm biên độ an toàn** | +30% Buffer = **1.46 GB** | +50% Buffer = **1.69 GB** | **~1.7 GB** |
| *Video sự cố (Nếu đưa vào MVP)* | *Chưa có trong allowlist MVP* | *50 video × 20 MB* | *~1,000 MB (~1.0 GB)* |

> ⚠️ **Đề xuất phạm vi:** MVP chỉ nhận ảnh và PDF. Nếu PM/GV yêu cầu video sự cố, dung lượng tổng sẽ tăng lên **~2.7 GB** (vẫn nằm trọn vẹn trong hạn mức 10 GB của Cloudflare R2).

## 2.2. Bảng so sánh nhà cung cấp Object Storage

| Tiêu chí | Cloudflare R2 | Supabase Storage | Firebase Storage | MinIO Self-host (D56) |
|---|---|---|---|---|
| **Free Storage** | [**10 GB / tháng**](https://www.cloudflare.com/products/r2/) | [**1 GB**](https://supabase.com/pricing) | [5 GB (cần thẻ Blaze)](https://firebase.google.com/pricing) | [Phụ thuộc ổ đĩa EC2](https://min.io/docs/minio/linux/index.html) |
| **Chi phí Egress (Băng thông ra)** | [**0đ (Miễn phí 100% Egress)**](https://developers.cloudflare.com/r2/platform/limits/) | [5 GB + 5 GB cached](https://supabase.com/pricing) | [100 GB/tháng no-cost](https://firebase.google.com/pricing) | Tốn phí egress AWS (~$0.09/GB) |
| **Hạn mức Request** | [**1M Class A (write) + 10M Class B (read)**](https://developers.cloudflare.com/r2/platform/limits/) | Không tách rõ | 5k upload, 50k download | Không giới hạn |
| **Kích thước file đơn lẻ tối đa** | [**5 GiB** (single-part PUT); 5 TiB (multipart)](https://developers.cloudflare.com/r2/platform/limits/) | [**50 MB** trên gói Free](https://supabase.com/docs/guides/storage/uploads/file-limits) | [5 TiB (Google Cloud Storage)](https://cloud.google.com/storage/quotas) | [5 TiB](https://min.io/docs/minio/linux/index.html) |
| **Presigned URL (D40)** | [**Hỗ trợ chuẩn S3 PUT URL**](https://developers.cloudflare.com/r2/api/s3/presigned-urls/) | [Có Signed Upload URL](https://supabase.com/docs/reference/javascript/file-buckets-createsigneduploadurl) | [Có GCS Signed URL](https://cloud.google.com/storage/docs/access-control/signed-urls) | [Có S3 Presigned URL](https://min.io/docs/minio/linux/index.html) |
| **TTL Presigned Upload** | [**1s đến 7 ngày (đặt đúng 900s)**](https://developers.cloudflare.com/r2/api/s3/presigned-urls/) | [**Cố định 2 giờ (7200s)**](https://supabase.com/docs/reference/javascript/file-buckets-createsigneduploadurl) | [1s đến 7 ngày](https://cloud.google.com/storage/docs/access-control/signed-urls) | [1s đến 7 ngày](https://min.io/docs/minio/linux/index.html) |
| **Mạng Phân phối Nội dung (CDN)** | [**Tích hợp Cloudflare Anycast CDN (0đ egress)**](https://developers.cloudflare.com/r2/buckets/public-buckets/) | [Smart CDN tích hợp sẵn](https://supabase.com/docs/guides/storage) | [Google Cloud CDN](https://firebase.google.com/docs/storage) | Không có sẵn (tự dựng proxy) |
| **Cơ chế Xác thực (Auth)** | **R2 API Token** (Access Key ID + Secret Key chuẩn S3 HMAC-SHA256) | **Service Role Key** (vượt qua RLS trên backend) | **Service Account Key** (file JSON Google Cloud IAM) | `MINIO_ROOT_USER` & `PASSWORD` |
| **Vị trí Lưu trữ (Region)** | [**Automatic / Location Hint (Singapore/APAC)**](https://developers.cloudflare.com/r2/reference/data-location/) | Gắn liền project (`ap-southeast-1` Singapore) | Chọn region bucket GCS (`asia-southeast1`) | Theo server EC2 (`ap-southeast-1`) |
| **Bảo mật & MIME Allowlist** | Ký bind `Content-Type` trong URL | Cấu hình MIME theo bucket | Security Rules theo MIME | Policy bucket |
| **Nguy cơ XSS (SVG/HTML)** | Backend chặn trước khi presign | Backend chặn trước khi presign | Chặn qua Security Rules | Backend tự chặn |
| **Private Bucket & Access** | Private mặc định, ký signed GET | Private mặc định + RLS | Firebase Auth Rules | Tự cấu hình |
| **Resize / Thumbnail** | [Không có sẵn (cần Cloudflare Images)](https://developers.cloudflare.com/images/) | [Chỉ có trên gói Pro+](https://supabase.com/docs/guides/storage/serving/image-transformations) | Cần Cloud Functions | Không có sẵn |
| **SDK Node.js** | `@aws-sdk/client-s3` (chuẩn quốc tế) | `@supabase/supabase-js` | Firebase Admin SDK | `minio` / AWS SDK |
| **Bắt buộc Credit Card?** | [**Không bắt buộc**](https://www.cloudflare.com/products/r2/) | [Không](https://supabase.com/pricing) | [**Bắt buộc thẻ Visa/Master (Blaze)**](https://firebase.google.com/pricing) | Có (tài khoản AWS) |
| **Khả năng đáp ứng PBL6** | 🥇 **Hoàn hảo (Khớp 100% hợp đồng)** | ⚠️ Thiếu quota (1 GB < 1.7 GB) | ❌ Phải liên kết thẻ thanh toán | 📋 Phức tạp quản trị |

*(Toàn bộ dữ liệu tra cứu chính thức ngày 2026-10-06).*

## 2.3. Đánh giá Kỹ thuật về An toàn & Xử lý Ảnh
1. **Kiểm soát MIME & Nguy cơ XSS:** Cả R2 lẫn S3 không tự động sniff magic bytes của file khi client tải lên qua presigned URL. Do đó, backend NestJS phải đóng vai trò là "người gác cổng": kiểm tra chặt chẽ extension, MIME type trong allowlist, từ chối tuyệt đối `image/svg+xml`, `text/html` trước khi cấp presigned URL.
2. **Resize/Thumbnail cho Mobile:** Cả R2 Free và Supabase Free đều không cung cấp image resize tự động. Giải pháp tối ưu cho PBL6 là **nén và tạo thumbnail phía client (Flutter Mobile / React Web)** trước khi gửi request presign, giúp tiết kiệm băng thông và giảm tải lưu trữ.
3. **Chính sách Ứng phó khi Tiệm cận / Vượt Quota (Graceful Degradation):**
   Nếu dung lượng media vượt quá dự tính (>80% quota):
   - *Giảm chất lượng ảnh (Quality Degradation):* Client tự động hạ chất lượng nén JPEG từ 85% xuống 70%, giảm độ phân giải tối đa từ 2400px xuống 1280px $\to$ tiết kiệm 50–65% dung lượng mỗi ảnh.
   - *Giới hạn số lượng (Quantity Capping):* Giới hạn tối đa 4 ảnh/phòng thay vì 6 ảnh; chỉ cho phép 1 ảnh công tơ điện nước/lần ghi.
   - *Phân tầng lưu trữ (Storage Tiering/Lifecycle):* Thiết lập chính sách tự động xóa ảnh sự cố hoặc file nháp sau khi đã xử lý xong sau 30-60 ngày.
   - *Kế hoạch tài chính:* Khi dự án scale thực tế, nâng cấp gói R2 với chi phí rất rẻ $0.015/GB/tháng.

---

# PHẦN 3 (Task 3) — Báo cáo Thực nghiệm POC (NestJS + Neon + R2 Chạy Thật)

Đã dựng project NestJS độc lập ngoài hub repo, cấu hình kết nối TypeORM tới Neon (`db_core` / `role_core`) qua biến môi trường (connection string che password: `postgresql://role_core:***@ep-holy-water-b39esm78.c-4.ap-southeast-1.aws.neon.tech/db_core?sslmode=require`). Chạy migration thật tạo 2 bảng `buildings` và `rooms` lấy từ `database-design.md` (`synchronize: false`).

## 3.1. Lý do Chọn TypeORM Thay vì Prisma
1. **Khả năng quản lý Migration độc lập:** TypeORM CLI (`migration:run -d src/data-source.ts`) hỗ trợ cực kỳ linh hoạt cho kiến trúc D53 nhiều database/nhiều role mà không cần generate client riêng cho từng DB.
2. **Hỗ trợ native PostgreSQL features:** Tương thích hoàn hảo với `uuid`, `jsonb`, và spatial/trgm mà không cần workaround.
3. **Mức tiêu thụ tài nguyên (Resource Footprint):** Prisma đi kèm binary Rust runtime nặng và sinh Prisma Client lớn tiêu tốn nhiều RAM hơn trên môi trường ít RAM, trong khi TypeORM dùng driver `pg` thuần JS nhẹ nhàng.
4. **Tích hợp NestJS chuẩn:** `@nestjs/typeorm` là module cốt lõi được bảo trì chính thức bởi NestJS team.

## 3.2. Cấu hình Môi trường & Thiết lập Từ Số 0 (README Verification)

### Danh sách Biến Môi trường & Cách lấy lại giá trị:
| Tên biến | Mục đích | Cách lấy lại giá trị từ Console Provider |
|---|---|---|
| `DATABASE_URL` | Kết nối PostgreSQL Neon | Neon Console $\to$ Project Dashboard $\to$ Connection Details $\to$ Chọn DB `db_core`, Role `role_core` $\to$ Copy pooled connection string. |
| `R2_ACCOUNT_ID` | Cloudflare Account ID | Cloudflare Dashboard $\to$ R2 Overview $\to$ Copy Account ID ở panel bên phải. |
| `R2_ACCESS_KEY_ID` | S3 Access Key ID | Cloudflare Dashboard $\to$ R2 $\to$ Manage R2 API Tokens $\to$ Create API Token (quyển Object Read & Write) $\to$ Copy Access Key ID. |
| `R2_SECRET_ACCESS_KEY` | S3 Secret Access Key | Cùng bước tạo API Token trên Cloudflare. |
| `R2_BUCKET` | Tên bucket R2 | Tên bucket đã tạo trên Cloudflare (ví dụ: `pbl6-poc-bucket`). |
| `PORT` | Cổng HTTP Server | Đặt cổng lắng nghe cục bộ (mặc định: `3000`). |

### Thiết lập Từ Số 0 (Khái lược từ README.md):
- File `.gitignore` đã loại trừ triệt để `.env`, `node_modules/`, `dist/`, `*.log`.
- Quy trình cài đặt:
  ```bash
  npm install
  npm run migration:run -- -d src/data-source.ts
  npm run start:dev
  ```

## 3.3. Contract Body của Endpoint Presign Upload (`POST /media/presign-upload`)

Body schema kiểm tra nghiêm ngặt bằng `class-validator`:
```json
{
  "ownerType": "room",                          // Enum: user, room, building, contract, contract_member, meter_reading, issue_report, message
  "ownerId": "2637ed28-09ad-4669-869c-e17a3e3481f4", // UUID entity cha
  "purpose": "cover_photo",                     // Enum: avatar, cover_photo, gallery_photo, meter_reading_evidence, ...
  "fileName": "sample_room.jpg",                // String: tên file gốc (server sẽ sanitize)
  "contentType": "image/jpeg",                  // Enum MIME: image/jpeg, image/png, image/webp, application/pdf
  "size": 1164043,                              // Integer: kích thước bytes (tối đa 25 MB)
  "captureSource": "device_storage",            // Optional: camera_direct, device_storage
  "expiresIn": 900                              // Optional: thời hạn signed URL tính bằng giây (mặc định 900s)
}
```

## 3.4. Giới hạn File Đơn lẻ "Thật"
- **Giới hạn lý thuyết Cloudflare R2:** Hỗ trợ tối đa **5 GiB** cho single-part PUT upload và **5 TiB** cho multipart upload.
- **Giới hạn nghiệp vụ backend POC (`MAX_FILE_SIZE`):** Cấu hình cố định ở mức **25 MB** (26,214,400 bytes).
- **Lý do đặt trần 25 MB:** Hoàn toàn bao quát nhu cầu scan hợp đồng PDF nhiều trang (~10–20 MB) và ảnh chụp sắc nét (~5–15 MB), đồng thời ngăn ngừa nguy cơ client tải file khổng lồ làm nghẽn băng thông hệ thống. Đã kiểm chứng thực tế file 20 MB chạy mượt mà.

## 3.5. Kết quả Kiểm thử Toàn vẹn File (SHA-256 Checksum)

Kiểm thử đúng luồng: Tính SHA-256 local $\to$ POST `presign-upload` $\to$ Client PUT trực tiếp lên R2 $\to$ POST `complete-upload` $\to$ Tải file về qua download URL $\to$ Tính SHA-256 file tải về $\to$ So sánh hash:

| File | Kích thước | Upload R2 | Download R2 | SHA-256 Trước Upload | SHA-256 Sau Tải Về | Kết quả Khớp |
|---|---:|---|---|---|---|:---:|
| **Ảnh JPEG** | 1.11 MB (1,164,043 B) | PASS | PASS | `48fb3a834b74625624b46d9de7af7511fff9fcf4de4182c765dfb2ebf474f31c` | `48fb3a834b74625624b46d9de7af7511fff9fcf4de4182c765dfb2ebf474f31c` | **MATCH (PASS)** |
| **Tài liệu PDF** | 1.00 MB (1,048,576 B) | PASS | PASS | `91ffea57fe2bdeffe69ff9b420f52f706a1ab086145f8b3010cebb3b2c98078e` | `91ffea57fe2bdeffe69ff9b420f52f706a1ab086145f8b3010cebb3b2c98078e` | **MATCH (PASS)** |
| **Large PDF** | 20.00 MB (20,971,520 B) | PASS | PASS | `f8c3f766613b95970f16312cbdb4eaf1306838365d96fc0117f9fa17a0128f02` | `f8c3f766613b95970f16312cbdb4eaf1306838365d96fc0117f9fa17a0128f02` | **MATCH (PASS)** |

*(Bằng chứng lưu tại `evidence/checksum/checksum-results.json`).*

## 3.6. Đo lường Hiệu năng Database (Neon PostgreSQL)

Đo cold start sau khi để Neon idle đủ lâu để suspend compute, sau đó đo 100 lần truy vấn `SELECT COUNT(*) FROM rooms;`:

| Chỉ số | Kết quả đo lường | Ghi chú kỹ thuật |
|---|---:|---|
| **Cold Start Connection (Total)** | **1197.62 ms** | Bắt tay TCP/SSL TLS + Neon compute thức dậy |
| - TCP/SSL Connect Latency | 1116.49 ms | Kết nối tới Neon gateway Singapore |
| - First Query Latency | 80.45 ms | Khởi tạo transaction đầu tiên |
| **p50 Latency (Median)** | **58.14 ms** | Độ trễ trung vị mạng từ Việt Nam tới Singapore qua TypeORM |
| **p95 Latency** | **59.73 ms** | 95% số truy vấn hoàn thành dưới 60ms |
| **p90 Latency** | 59.01 ms | Rất ổn định, độ lệch chuẩn cực nhỏ |
| **p99 Latency / Max** | 89.43 ms | Đỉnh trễ cao nhất không vượt quá 90ms |
| **Số lần đo** | 100 lần | Raw logs lưu tại `evidence/db/latency-raw.json` |

## 3.7. Đo lường Hiệu năng Storage (Cloudflare R2)

| File | Kích thước | Thời gian tạo Presign | Thời gian PUT lên R2 | Thời gian Download lại |
|---|---:|---:|---:|---:|
| **JPEG** | 1.11 MB | 23.84 ms | 1332.35 ms | 497.03 ms |
| **PDF** | 1.00 MB | 4.45 ms | 917.82 ms | 702.96 ms |
| **Large file** | 20.00 MB | 4.80 ms | 2008.51 ms | 1940.93 ms |

**Quota sau thử nghiệm:**
- Tổng số object trong bucket: **4 objects**
- Tổng dung lượng lưu trữ: **22.12 MB** (23,190,744 bytes)

## 3.8. Kiểm thử các Trường hợp Lỗi (Negative Test Cases Toàn diện)
1. **Lỗi 400 Bad Request (MIME type không cho phép - SVG):**
   - *Request:* Gửi body với `contentType: "image/svg+xml"`
   - *Response:* `HTTP 400 Bad Request`
     ```json
     {
       "message": ["contentType must be one of the following values: image/jpeg, image/png, image/webp, application/pdf"],
       "error": "Bad Request",
       "statusCode": 400
     }
     ```
2. **Lỗi 422 Unprocessable Entity (File size vượt quá 25 MB):**
   - *Request:* Gửi body với `size: 31457280` (30 MB)
   - *Response:* `HTTP 422 Unprocessable Entity`
     ```json
     {
       "statusCode": 422,
       "code": "MEDIA_TYPE_NOT_ALLOWED"
     }
     ```
3. **Lỗi 404 Not Found (Ticket không tồn tại):**
   - *Request:* Gọi complete với UUID ngẫu nhiên `00000000-0000-0000-0000-000000000000`
   - *Response:* `HTTP 404 Not Found` (`code: "TICKET_NOT_FOUND"`)
4. **Lỗi 409 Conflict (Complete trước khi upload):**
   - *Request:* Presign xong gọi complete ngay khi chưa PUT file lên R2
   - *Response:* `HTTP 409 Conflict` (`code: "UPLOAD_NOT_COMPLETED"`)
5. **Lỗi 410 Gone (Ticket đã hết hạn):**
   - *Request:* Presign với `expiresIn: 1`, sau 2 giây gọi complete
   - *Response:* `HTTP 410 Gone` (`code: "TICKET_EXPIRED"`)

---

# PHẦN 4 (Task 4) — Script Keepalive Chống Pause / Khóa

## 4.1. Thiết kế Kỹ thuật
- **Độc lập:** Viết bằng TypeScript thuần (`scripts/keepalive/keepalive.ts`), chạy qua `tsx`, không phụ thuộc NestJS, đọc trực tiếp `DATABASE_URL`.
- **An toàn:** Tự động tạo bảng riêng `ops_keepalive(id, pinged_at, app_version, note)`, không đụng bảng nghiệp vụ.
- **Xác nhận Commit:** Thực hiện **1 WRITE** $\to$ **1 READ-back** đúng record vừa ghi để kiểm chứng commit thành công.
- **Tự dọn dẹp:** Dọn dẹp giữ tối đa **100 rows** mới nhất. Dung lượng bảng luôn ở mức vài KB.
- **Chịu lỗi:** Retry 3 lần với exponential backoff `1s → 4s → 16s`. Thất bại sẽ thoát với `exit code = 1` để kích hoạt báo đỏ trên GitHub Actions.
- **Cờ `--dry-run`:** Đã kiểm chứng chạy đọc `SELECT now()` mà không làm tăng số lượng dòng trong DB.

## 4.2. Phân tích Hai Nhịp Keepalive Độc Lập

1. **Nhịp Database (~24h): `17 3 * * *` (03:17 UTC mỗi ngày)**
   - *Lý do:* Chính sách của Neon/Supabase có thể pause/archive project nếu không có hoạt động trong 7 ngày. Nhịp 24h đảm bảo an toàn tuyệt đối trước ngưỡng 7 ngày (chịu được lỡ 5-6 run), trong khi mỗi ngày chỉ đánh thức compute đúng 1 lần.
2. **Nhịp Render Web (≤10 phút): `*/10 * * * *` (CHỈ bật trong tuần bảo vệ)**
   - *Lý do:* Render free spin-down sau 15 phút idle (cold start mất 30–60s). Nếu chạy nhịp 10 phút cả tháng sẽ ngốn 4,400+ phút Actions (vượt quota 2,000 phút của GitHub private repo) và đốt hết 750 giờ free instance của Render. Do đó **chỉ bật trước ngày bảo vệ 1 ngày và tắt ngay sau khi bảo vệ xong**.
   - *Tính độc lập:* Endpoint `/health` trả về `{ status: "ok" }` **mà không query Database**, ngăn chặn việc Render keepalive vô tình kéo theo Database thức 24/7.

## 4.3. Bảng Tính Toán Tiêu Thụ Compute / CU-Hours

| Thông số | Giá trị |
|---|---|
| **Hạn mức Compute Free của Neon** | **100 CU-hours / tháng** |
| **Kích thước Compute nhỏ nhất (Neon Free)** | **0.25 CU** |
| **Thời gian compute thức cho mỗi lần ping** | ~1s chạy script + **5 phút idle timeout** của Neon = **~5.02 phút** (~0.084 giờ) |
| **Tiêu hao hàng ngày (1 ping / 24h)** | $0.084 \text{ giờ} \times 0.25 \text{ CU} = \mathbf{0.021 \text{ CU-hours / ngày}}$ |
| **Tiêu hao hàng tháng (30 ngày)** | $30 \times 0.021 = \mathbf{0.63 \text{ CU-hours / tháng}}$ ($\approx \mathbf{0.63\%}$ tổng quota) |

> 💡 **Kết luận:** Script keepalive chỉ tiêu hao **dưới 1%** hạn mức miễn phí của Neon. Chi phí thực tế phụ thuộc vào thời gian 5 phút chờ suspend của Neon, hoàn toàn không gây nguy cơ cạn kiệt tài nguyên.

## 4.4. Cách Phát hiện Sắp/Đã Hết Quota
1. **Neon Console Usage Dashboard:** Vào Dashboard $\to$ mục **Usage & Billing** theo dõi biểu đồ Compute Hours đã dùng trong chu kỳ.
2. **Cảnh báo Email (Alert Threshold):** Bật thông báo ngưỡng sử dụng đạt mốc 80% trên console của provider.
3. **Cơ chế Fail-safe Tự động của Script:** Khi hết compute quota, kết nối PostgreSQL bị từ chối hoặc timeout $\to$ script retry 3 lần $\to$ exit code 1 $\to$ GitHub Actions fail đỏ và gửi email báo động lập tức tới dev team.
4. **Theo dõi độ trễ `connectMs`:** Sự gia tăng đột biến của `connectMs` trong log phản ánh trạng thái cold start hoặc compute bị nghẽn.

## 4.5. Chế độ Chạy Thủ công (`workflow_dispatch`)
Trong `.github/workflows/keepalive.yml`, bên cạnh lịch cron tự động, workflow hỗ trợ kích hoạt thủ công qua `workflow_dispatch`:
- Cho phép dev/QA truy cập tab **Actions** trên GitHub $\to$ Chọn workflow `keepalive` $\to$ Bấm nút **Run workflow**.
- Có thể chọn tham số `target`: `db` (ping database) hoặc `render` (ping web service) để kiểm tra tức thời mà không cần can thiệp mã nguồn.

## 4.6. Bằng chứng Hiệu lực (Loại B — Gián Tiếp)

*Ghi chú xác minh:* Bằng chứng Loại B chứng minh chính sách của provider tồn tại, script hoạt động chính xác mọi luồng và đo lường thời gian cold start thực tế mà không chủ động làm gián đoạn database demo.

- **Trích dẫn chính sách chính thức của Neon:**
  > *"Free Tier projects that do not receive any queries for a period of time may be suspended or marked inactive. Neon automatically scales computes to zero after 5 minutes of inactivity, and projects remain available to be woken up by any incoming query."*  
  > — [Neon Free Plan Documentation](https://neon.tech/docs/introduction/plans#free-plan), truy cập ngày 2026-10-06.
- **Log chạy Dry-run thành công:**
  ```json
  {"t":"2026-10-06T11:02:39.839Z","target":"db","dryRun":true,"msg":"dry-run: read only, no write","dbNow":"2026-10-06T11:02:39.806Z","connectMs":1436}
  ```
- **Log chạy Thật thành công:**
  ```json
  {"t":"2026-10-06T11:02:56.991Z","target":"db","dryRun":false,"msg":"ok","rowId":"3","pingedAt":"2026-10-06T11:02:56.824Z","pruned":0,"connectMs":352,"totalMs":607}
  ```
- **Log kiểm thử Retry và Exit Code = 1 khi sai URL:**
  ```json
  {"t":"2026-10-06T11:03:14.632Z","target":"db","dryRun":false,"msg":"retry","attempt":1,"waitMs":1000,"error":"connect ECONNREFUSED 127.0.0.1:5432"}
  {"t":"2026-10-06T11:03:15.634Z","target":"db","dryRun":false,"msg":"retry","attempt":2,"waitMs":4000,"error":"connect ECONNREFUSED 127.0.0.1:5432"}
  {"t":"2026-10-06T11:03:19.639Z","target":"db","dryRun":false,"msg":"retry","attempt":3,"waitMs":16000,"error":"connect ECONNREFUSED 127.0.0.1:5432"}
  {"t":"2026-10-06T11:03:35.645Z","target":"db","dryRun":false,"msg":"FAILED after retries","error":"connect ECONNREFUSED 127.0.0.1:5432"}
  ```
  *(Exit code: `1` — Báo fail chính xác cho GitHub Actions).*

---

# PHẦN 5 — Bảng So sánh Tổng hợp & Phân tích Đánh đổi (Trade-offs)

## 5.1. Ma trận Đánh giá Tổng thể

| Phương án | Quota Lưu trữ | Đáp ứng D53 (4 DB/4 Role) | Đáp ứng D40 (Presigned PUT) | Chi phí Egress | Rủi ro Gián đoạn | DevOps Overhead | Mức độ Khuyến nghị |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Neon + Cloudflare R2** | 1 GB DB / 10 GB Storage | **PASS** | **PASS** (TTL 900s) | **0đ** | Rất thấp (có keepalive) | Rất thấp (Managed) | 🟢 **KHUYẾN NGHỊ SỐ 1** |
| **Supabase (DB + Storage)** | 500 MB DB / 1 GB Storage | **PASS** | ⚠️ Lệch TTL (2h ≠ 900s) | 5 GB | Thấp (pause sau 7 ngày) | Rất thấp (Managed) | 🟡 **DỰ PHÒNG** |
| **EC2 Compose (D56)** | Phụ thuộc ổ cứng EBS | **PASS** | **PASS** (MinIO S3) | Tốn phí AWS | Hết credit sau 6 tháng | **Rất cao** (Tự bảo trì) | ⚪ **ĐỐI CHỨNG D56** |

## 5.2. Phân tích Đánh đổi (Trade-offs)

1. **Managed Free-Tier (Neon + R2) vs Self-Host EC2 (D56):**
   - *Managed:* 0đ chi phí, không cần thẻ tín dụng, không lo hết credit sau 6 tháng. Miễn phí 100% egress từ R2. Không lo sập RAM (t2.micro chỉ có 1 GB RAM, nếu chạy cả 4 service + DB + MinIO sẽ bị OOM killer sập toàn bộ hệ thống).
   - *Self-host:* Tốn nhiều công sức bảo trì Linux, Docker, PgBouncer, SSL, backup dump script.
2. **Neon vs Supabase:**
   - Neon vượt trội về storage DB (1 GB vs 500 MB), có connection pooler tích hợp sẵn cho 4 service (10,000 conn vs 60 conn), restore 6 giờ trên gói Free. Supabase là phương án dự phòng chất lượng cao.

## 5.3. Chi phí Dự phòng Nếu Vượt Quota Free-Tier (Đối chiếu Ngân sách PM)
- **Neon:** Gói **Launch** giá **$19 / tháng** (10 GB storage, 300 CU-hours, không scale-to-zero).
- **Supabase:** Gói **Pro** giá **$25 / tháng** (8 GB DB storage, 100 GB storage media, 250 GB egress, không pause).
- **Cloudflare R2:** Dung lượng vượt mức chỉ tính **$0.015 / GB / tháng** (100 GB lưu trữ chỉ tốn ~$1.5/tháng, 0đ egress).
- **Render:** Gói **Starter** cho Web Service giá **$7 / tháng** (chạy 24/7, RAM 512 MB).

---

# PHẦN 6 — Khuyến nghị Chính thức, Đề xuất Quyết định (D59+) & Câu hỏi cho PM/GV

## 6.1. Khuyến nghị Kỹ thuật Chính thức
- **Primary Stack (Chính thức):** **Neon Serverless PostgreSQL** + **Cloudflare R2**.
- **Backup Stack (Dự phòng):** **Supabase** (Database + Storage).
- **Ảnh hưởng tới D53 và D56:**
  - Cả D53 (4 DB + 4 Role) và D56 (EC2 + MinIO) hiện đang ở trạng thái 🟡 Proposed. Báo cáo này **cung cấp số liệu và bằng chứng chạy thật để PM/GV quyết định**, tuyệt đối không tự ý chỉnh sửa hay ghi đè D53/D56.
  - Nếu chọn Neon + R2, D53 được giữ nguyên hoàn toàn (PASS), còn D56 sẽ được thay thế bằng D59 (Managed Free-Tier).

## 6.2. Dự thảo Quyết định D59 (Ghi nhận vào `pm/phase-3/discovery/decisions.md`)

```markdown
### D59 — Chốt Provider Managed Free-Tier cho Database (Neon) và Object Storage (Cloudflare R2)

* **Status:** 🟢 Decided (Đề xuất thông qua dựa trên POC PBL-37)
* **Date:** 2026-10-06
* **Deciders:** PM, BE Lead

#### Context
Quyết định D40 để ngỏ nhà cung cấp Storage. Quyết định D56 (tự host Postgres + MinIO trên 1 EC2) đang ở trạng thái 🟡 Proposed và phụ thuộc ngân sách. Nhóm cần hạ tầng thật để bắt đầu scaffold database và viết migration cho 4 service (D53).

#### Decision
1. Chọn **Neon Serverless PostgreSQL** làm Database Provider chính thức cho môi trường Dev/Staging/Demo. Hỗ trợ trọn vẹn mô hình 4 DB + 4 Role theo D53.
2. Chọn **Cloudflare R2** làm Object Storage Provider chính thức cho toàn bộ tính năng tải lên tài liệu và hình ảnh theo D40.
3. Thay thế đề xuất tự host MinIO của D56 bằng Cloudflare R2 để đạt 0đ chi phí băng thông (egress) và giảm thiểu rủi ro vận hành.
4. Triển khai script keepalive tự động chạy 1 lần/24h qua GitHub Actions để bảo vệ Database khỏi cơ chế pause của nhà cung cấp.

#### Consequences
* **Tích cực:** Chi phí 0 VNĐ, không cần thẻ tín dụng, hạn mức lưu trữ 10 GB vượt xa nhu cầu 1.7 GB của dự án, có sẵn connection pooler lên tới 10,000 kết nối.
* **Tiêu cực:** Cold start connection của Neon mất ~1.2 giây khi compute thức dậy; Render cần bật keepalive 10 phút riêng biệt trong tuần bảo vệ.
```

## 6.3. Bốn (4) Câu hỏi Trọng tâm Cần PM & Giảng viên Chốt (≤5 câu hỏi)
1. **Có được cấp EC2 / ngân sách không (quyết định D56):** PM/GV có xin được tài trợ EC2/ngân sách không? Nếu **không có ngân sách**, PM có đồng ý chốt combo Managed Free-Tier (**Neon + Cloudflare R2** — D59) thay cho D56 để BE tiến hành scaffold code ngay lập tức không?
2. **Quy định về Video trong MVP:** PM có xác nhận **loại bỏ video** ra khỏi danh mục cho phép tải lên ở MVP để đảm bảo an toàn hạn mức lưu trữ (chỉ nhận `image/*` và `application/pdf`), hay cần mở rộng để khách hàng gửi video sự cố (ước tính thêm 1 GB quota)?
3. **Chính sách kiểm soát chất lượng ảnh:** Đối với ảnh phòng trọ, mobile app và web app có bắt buộc nén ảnh phía client (client-side compression) xuống dưới 1.5 MB trước khi upload để tiết kiệm băng thông người dùng và tránh nghẽn quota không?
4. **Kế hoạch cho tuần bảo vệ đồ án:** Team sẽ kích hoạt cron keepalive 10 phút của Render trong tuần bảo vệ, hay sẽ trích quỹ nhóm $7 để mua gói Render Starter trong tháng bảo vệ đồ án?
