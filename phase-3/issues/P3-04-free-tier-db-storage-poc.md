# P3-04 — Nghiên cứu & POC nguồn DB/Storage free (managed) + script keepalive chống bị pause

**Status:** 🟡 Open
**Assignee:** BE Lead
**Stakeholders / Reviewers:** PM (quyết ngân sách + chốt D53/D56) · FE + Mobile (giới hạn size/MIME khi upload) · GV SOA (nếu có thay đổi kiến trúc hạ tầng)
**Created:** 2026-10-05
**Due date:** 2026-10-09 (EOD) — chung hạn với P3-03, **trước** khi BE viết entity + migration đầu tiên
**Priority:** 🔴 High (chặn scaffold: connection string, migration, presign upload)

> **Không phải task "chọn provider".** Task này đưa ra **số liệu + bằng chứng chạy thật** để PM
> chọn. Không deploy production, không dùng tiền, không viết vào `pbl6-backend`.

**Input:**

- `pm/phase-2/discovery/decisions.md` **D40** — presign upload 2 bước, **storage provider để ngỏ** ("cấu hình storage provider (S3-compatible) … BE quyết định ở implement")
- `pm/phase-3/discovery/decisions.md` **D53** (4 database + 4 Postgres role, cấm cross-service FK) · **D56** (1 EC2 + Docker Compose: Postgres · MinIO, 🟡 Proposed, cần budget)
- `pm/phase-0/discovery/tech-feasibility.md` §6 — Render + Neon + Vercel, free tier 2026 (viết ở Phase 0, **D56 đã vô hiệu hoá** combo này)
- `pm/phase-0/product-sketch.md` §7 — #2 Database (Neon/Supabase), #8 Object Storage (R2/Supabase Storage/Firebase), đánh dấu "Tự lo free-tier"
- `pm/phase-0/discovery/assumptions-risks.md` **R5** — mitigation hiện tại là "Keep-alive ping", **chưa có gì cụ thể**
- `pm/phase-1/discovery/database-design.md` §2.25 `Media` — `size_bytes`, `owner_type`/`purpose` (9 purpose), polymorphic, quyền đọc kế thừa từ entity cha
- `pm/phase-2/discovery/api-conventions.md` §(media upload) — **không** `multipart`, chỉ nhận `image/jpeg|png|webp` + `application/pdf`, signed URL `expiresIn: 900`
- `pm/phase-3/discovery/microservices-architecture.md` §6.1, §7.3 — MinIO trong Compose

**Deliverable:**

| # | Artifact | Vị trí |
|---|----------|--------|
| 1 | Báo cáo research + POC + khuyến nghị provider | `pm/phase-3/discovery/free-tier-db-storage.md` |
| 2 | Quyết định mới (nếu có) | `pm/phase-3/discovery/decisions.md` — ID tiếp theo **D59** trở đi |
| 3 | POC + script keepalive (**code thật, không commit vào hub repo**) | Thư mục tạm ngoài `PBL6/`, ví dụ `C:\Users\ASUS\pbl6-fre-tier-poc` |

---

## 1. Vì sao cần task này

Ba việc đang treo, cùng chặn scaffold:

1. **Storage provider chưa ai chọn.** D40 tuyên bố để ngỏ; `product-sketch.md` §7 liệt kê 3 ứng
   viên nhưng chỉ ghi "tự lo free-tier" — không ai đã mở bảng giá để xác minh.
2. **D56 chưa duyệt.** Nó thay combo Render+Neon+Vercel bằng 1 EC2 + Compose (Postgres + MinIO),
   nhưng D56 tự ghi 🟡 Proposed **(needs budget)**. Nếu GV không cấp EC2 thì phương án còn lại
   là managed free tier — mà chưa ai biết managed free tier có chịu được kiến trúc hiện tại không.
3. **Keep-alive chỉ là ghi chú.** R5 ghi "Keep-alive ping hoặc $7 Starter tuần bảo vệ". Chưa có
   script, chưa có nhịp, chưa đo được free tier ăn bao nhiêu compute — nên không biết keep-alive
   có giữ được DB sống hay chỉ tốn quota.

**Vì sao phải làm bây giờ, không làm sau:** P3-03 sắp sinh ra **4 database + 4 Postgres role**
(D53). Có những free tier cấp đúng **1** Postgres và **không cho `CREATE DATABASE` / `CREATE ROLE`**.
Nếu chọn xong mới biết, thì hoặc phải đổi D53, hoặc phải bỏ free tier — cả hai đều là việc
tốn hơn nhiều so với hỏi trước.

## 2. Ranh giới

| Không làm | Vì sao |
|----------|--------|
| Không chốt provider cuối cùng | PM chốt sau khi đọc báo cáo; task này đưa khuyến nghị + điều kiện |
| Không deploy production, không nâng paid tier | Chỉ free tier, không cần thẻ tín dụng |
| Không viết code vào `pbl6-backend` | D52–D58 chưa duyệt; POC để hiểu, không phải code production |
| **Không commit code vào hub repo `PBL6`** | `pm/AGENTS.md`: repo này không chứa app code — POC để ngoài, chỉ chép kết quả vào báo cáo |
| Không sửa `api-spec.md` / `database-design.md` | Đổi giới hạn upload hoặc schema `Media` là thay đổi contract → task riêng sau khi PM chốt |
| Không tự thêm video vào MVP | Allowlist MVP **không có** video (xem Task 2) — nêu câu hỏi, không tự mở scope |

## 3. Hạng mục

### Task 1 — Research: DB free tier

Danh sách tối thiểu: **Supabase**, **Neon**, **Aiven Free (Postgres)**, **Render Postgres** (để
loại rõ ràng — chỉ 30 ngày), cộng phương án **tự host Postgres trên EC2** (D56) làm đối chứng.

> **Chỉ xét Postgres thật.** Cần TypeORM/Prisma kết nối được và cần `jsonb`, `uuid`, `pg_trgm`
> (D53 dùng role + grant). Firestore/SQLite/MySQL không thay thế được.

- [ ] Mỗi provider: storage size, compute hours/CU-hours, số project, **thời hạn** (vĩnh viễn
      hay 30/90 ngày), có bắt buộc thẻ tín dụng không
- [ ] **Chính sách pause / scale-to-zero, ghi con số cụ thể**: Neon scale-to-zero sau bao lâu,
      Supabase pause sau bao lâu không có query, Render sleep sau bao lâu + cold start mấy giây
- [ ] **Có chịu được D53 không**: 1 free project có tạo được **4 database + 4 Postgres role** không;
      có chặn `CREATE DATABASE` / `CREATE ROLE` không; connection pooler có ở free tier không,
      trần bao nhiêu connection
- [ ] Migration: extension nào phải bật (`uuid-ossp`, `pgcrypto`, `pg_trgm`), có cần `superuser`
      cho lúc migrate không
- [ ] Egress/bandwidth, region gần VN (`ap-southeast-1` Singapore nếu có), latency đo được
- [ ] Backup / PITR / restore thủ công trên free tier
- [ ] Rủi ro giữa kỳ: free tier có bị siết giữa lúc bảo vệ đồ án không (**ghi ngày tra + URL**)
- [ ] **Mọi con số ghi kèm URL nguồn + ngày tra** — free tier đổi theo tháng, không có nguồn thì
      coi như không có số

### Task 2 — Research: object storage / media free tier

Danh sách tối thiểu: **Supabase Storage**, **Cloudflare R2**, **Firebase Storage**, **MinIO tự
host** (D56).

- [ ] Quota: tổng dung lượng, **giới hạn file đơn lẻ** (quan trọng cho scan hợp đồng), số request/tháng, egress
- [ ] **Presigned URL** có không (D40 bắt buộc) + TTL tối đa (contract đang đặt `expiresIn: 900`)
- [ ] MIME/extension allowlist — có chặn `svg` / `html` không (nguy cơ XSS khi serve file user up);
      provider nào ép content-type theo file thật
- [ ] Public bucket vs private + signed URL; có CDN không
- [ ] Có resize/thumbnail không (ảnh phòng nhiều, mobile upload 4G)
- [ ] SDK chính thức phía JS (`@supabase/supabase-js`, `aws-sdk v3` cho R2) + cách auth
      (service role key vs R2 API token) — BE sẽ dùng cái này luôn
- [ ] Region gần VN + latency upload/download
- [ ] **Ước lượng nhu cầu thật của PBL6** (đưa số vào báo cáo — đây là bước quyết định, không
      dùng con số của người khác):

  | Loại media | `purpose` / nguồn | Ước lượng |
  |---|---|---|
  | Ảnh phòng + tòa nhà | `cover_photo`, `gallery_photo`, `ownership_proof` | 25 phòng × 6 ảnh × ~1.5MB ≈ **225MB** |
  | Ảnh công tơ (OCR, D51) | `meter_reading_evidence` | 500 ảnh × ~800KB ≈ **400MB** |
  | File HĐ template + đã ký | `contract_template`, `contract_signed` | 100 × ~1MB ≈ **100MB** |
  | Ảnh CCCD | `cccd_front`, `cccd_back` | 200 × ~500KB ≈ **100MB** |
  | Ảnh sự cố + chat attachment | `issue_photo`, `chat_attachment` | 300 × ~1MB ≈ **300MB** |
  | **Video sự cố** | ⚠️ **không có trong allowlist MVP** | chưa tính — xem câu hỏi bên dưới |

- [ ] **Câu hỏi cần PM/GV trả lời:** MVP có đưa **video** vào không? `api-conventions.md` chỉ cho
      phép `image/*` + `application/pdf`, nhưng UX web (`phase-0/discovery/p0-02/ux-web.md`) và
      `product-platform-map.md` có nói khách gửi "ảnh chụp/video". **Tính cả video vào quota**
      (50 × 20MB ≈ 1GB) để PM chọn, chứ không tự thêm vào MVP.

### Task 3 — POC: project NestJS tạm, chạy thật

- [ ] Tạo project NestJS **ngoài hub repo** (không được lẫn vào `PBL6/`), có `.gitignore`
- [ ] Cấu hình **chỉ qua env var**, không hardcode: `DATABASE_URL`, `SUPABASE_URL`,
      `SUPABASE_SERVICE_KEY`, `S3_*`/`R2_*`
- [ ] DB: kết nối provider thắng Task 1, chạy **2 bảng thật** lấy từ `database-design.md`
      (ví dụ `buildings` + `rooms` — đủ FK + index + `jsonb`), dùng TypeORM **hoặc** Prisma
      (chọn 1, ghi lý do)
- [ ] **`synchronize: false` + file migration thật** — không dùng `synchronize: true` trong bất kỳ
      trường hợp nào
- [ ] Storage: dựng 1 endpoint `POST /media/presign-upload` đúng flow D40 (body `ownerType`,
      `ownerId`, `purpose`, `fileName`, `contentType`, `size`) → `PUT` thẳng lên storage →
      `POST /media/{mediaId}/complete-upload`
- [ ] Upload **3 file thật** rồi tải lại và **đối chiếu checksum**: 1 JPEG ~1MB · 1 PDF ~1MB ·
      1 file ~20MB (để biết giới hạn file đơn lẻ thật là bao nhiêu, không đoán)
- [ ] Đo và ghi lại: thời gian cold start kết nối (sau khi để idle), latency p50/p95 của 1 query
      đơn giản, thời gian upload/download, quota đã dùng sau 1 lần chạy
- [ ] Connection string trong báo cáo phải **che password** (`postgres://user:***@host/db`)
- [ ] `README.md` trong POC: setup từ số 0 (clone → cài → env → migrate → chạy) để BE tái lập được
      mà không cần hỏi lại
- [ ] **Không** push `.env` lên GitHub; báo cáo chỉ ghi *tên biến* + cách lấy lại giá trị

### Task 4 — Script keepalive chống bị pause / khóa

Mục tiêu: **đo được**, không phải ping cảm tính.

- [ ] Script Node/TS **standalone**, không phụ thuộc NestJS, đọc `DATABASE_URL`
- [ ] Chạy **1 write + 1 read** vào bảng riêng `ops_keepalive` (`id`, `pinged_at`, `app_version`,
      `note`) — **không** ping vào bảng nghiệp vụ
- [ ] **2 nhịp khác nhau, nêu rõ lý do**: DB ~**24h** (an toàn với cả policy 7 ngày) ·
      Render ~**≤10 phút** nếu cần always-on trong tuần bảo vệ
- [ ] **Idempotent + tự dọn**: giữ tối đa N=100 row rồi xoá row cũ, hoặc upsert 1 dòng `current`
      (chọn 1, ghi lại)
- [ ] **Retry/backoff 3 lần (1s/4s/16s)**, exit code ≠ 0 khi thất bại để cron/GitHub Action báo fail
- [ ] **Không nuôi DB**: ghi rõ free compute/CU-hours mà 30s/ngày script này tiêu tốn, và cách phát
      hiện hết quota
- [ ] Chế độ chạy: cron máy **hoặc** GitHub Actions `schedule` (repo private + `workflow_dispatch`
      để bấm tay) — chọn 1, không làm cả hai
- [ ] Cờ `--dry-run` để test không ghi thật
- [ ] **Bằng chứng hiệu lực**: chạy thật 1 lần, dán log. Nếu test được pause thật thì làm trên
      **project riêng, không project demo** — tắt script, đợi pause, bật lại, ghi thời gian wake.
      Nếu không dám để mất dữ liệu demo thì ghi bằng chứng gián tiếp: trích nguyên văn chính sách
      pause trong docs provider + cold start đã đo ở Task 3. **Nêu rõ là bằng chứng loại nào**,
      không để hai loại lẫn vào nhau.

### Task 5 — Chốt & khuyến nghị

- [ ] Bảng so sánh cuối: provider × (đủ quota? chịu 4 DB/4 role? có presign? egress? có pause?
      cần thẻ?) → **khuyến nghị 1 phương án chính + 1 phương án dự phòng**
- [ ] Nêu ảnh hưởng tới **D53** và **D56**: đây là 2 quyết định đang 🟡 Proposed, task này cung cấp
      dữ liệu để PM chốt — không tự sửa D53/D56
- [ ] Chi phí nếu free tier không đủ (Render Starter, Supabase Pro…) để PM đối chiếu ngân sách
- [ ] Quyết định mới → ghi vào `discovery/decisions.md` với **ID kế tiếp (D59+)**, không đánh số lại
- [ ] **≤5 câu hỏi cần PM trả lời**, đứng đầu là: có được cấp EC2 / ngân sách không (quyết định D56)

## 4. Definition of Done

- [ ] `discovery/free-tier-db-storage.md` tồn tại, đủ 6 phần (DB · Storage · POC · Keepalive · So sánh · Khuyến nghị)
- [ ] ≥4 provider DB + ≥4 provider storage, mỗi cái có con số cụ thể + URL + ngày tra
- [ ] Câu hỏi D53 (4 DB/4 role) trả lời dứt khoát cho provider được khuyến nghị
- [ ] Bảng ước lượng nhu cầu media có con số của PBL6, không phải con số ước lượng chung
- [ ] POC chạy được từ số 0 theo `README.md`: 2 bảng + migration thật + upload/download checksum khớp
- [ ] Log đo: cold start, latency p50/p95, thời gian upload 3 file
- [ ] Keepalive chạy được: idempotent, retry + exit code, `--dry-run`, có 1 log chạy thật
- [ ] Ghi rõ bằng chứng pause là **trực tiếp** hay **gián tiếp**
- [ ] Không có secret nào trong báo cáo hoặc hub repo; connection string đã che
- [ ] Hub repo `PBL6/` **không** chứa app code của POC
- [ ] PM review + chốt provider; D59+ ghi vào `decisions.md` nếu có quyết định mới

## 5. Ước lượng & thứ tự

Tổng ~**5–6 ngày công**: Task 1 (2) · Task 2 (1) · Task 3 (2) · Task 4 (1) · Task 5 (0.5).

| Ngày | Việc |
|------|------|
| 05/10 (T2) | Task 1 — research DB, có bảng số liệu sơ bộ |
| 06/10 (T3) | Task 2 — research storage + ước lượng quota PBL6 |
| 07–08/10 (T4–T5) | Task 3 — POC NestJS tạm |
| 09/10 (T6) | Task 4 + Task 5 — keepalive, chốt, khuyến nghị |

**Nếu thiếu thời gian:** bỏ Task 2 (dùng luôn MinIO theo D56) và cắt POC xuống 1 bảng.
**Không được bỏ Task 4** — R5 phụ thuộc vào nó.

## 6. Rủi ro của chính task này

- **Free tier đổi không báo trước** → bắt buộc có ngày tra; đọc lại ngay trước buổi bảo vệ (W13–14).
- **Không test pause thật** vì sợ mất dữ liệu demo → nên test trên project phụ, không dùng project
  có dữ liệu thật.
- **Quota nhỏ hơn ước lượng** khi có nhiều ảnh chụp thật → ước lượng ở Task 2 phải có mức bù, và
  cần nói rõ chuyện gì xảy ra khi vượt quota (giảm chất lượng ảnh? giới hạn số ảnh/phòng?).
- **Có thể kết luận ngược với D56** → đó là kết quả hợp lệ, ghi vào báo cáo kèm điều kiện, đừng
  hiểu chỉnh báo cáo cho khớp quyết định sẵn có.

## 7. Cross-ref

- `discovery/decisions.md` — D51 · D53 · D56
- `phase-2/discovery/decisions.md` — **D40** (storage provider để ngỏ)
- `phase-0/discovery/tech-feasibility.md` §6 · `phase-0/product-sketch.md` §7 (#2, #8) ·
  `phase-0/discovery/assumptions-risks.md` R5 · `phase-0/discovery/exit-criteria.md`
- `phase-1/discovery/database-design.md` §2.25 (`Media`) + các `purpose` ở §2.x
- `phase-2/discovery/api-conventions.md` (presign upload, MIME allowlist, rate limit 20 req/phút)
- `phase-2/discovery/api-spec.md` API 18–19
- `discovery/microservices-architecture.md` §6.1, §7.3
- `P3-02-microservices-architecture-research.md` · `P3-03-database-per-service-design.md`