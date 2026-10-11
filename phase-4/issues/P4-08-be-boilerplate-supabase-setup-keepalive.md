# P4-08 — Setup kết nối Supabase PostgreSQL & Script Keepalive chống Pause cho Boilerplate

**Status:** 🟡 Open  
**Assignee:** BE Dev  
**Stakeholders / Reviewers:** BE Lead, PM  
**Created:** 2026-10-11  
**Due date:** 2026-10-14  
**Priority:** 🟠 Medium / High (Enabler cho môi trường Cloud Dev/Staging dùng chung)  

**Input:**
- Mã nguồn hiện có: `boilerplate/backend/`
- `pm/phase-3/discovery/free-tier-db-storage.md` (§2 So sánh Supabase, §4 Thiết kế Script Keepalive Chống Pause / Khóa)
- `pm/phase-3/discovery/decisions.md` (D53 Database-per-service, D56 Deployment)
- Tài liệu kỹ thuật: [Supabase Connecting with Pooler](https://supabase.com/docs/guides/database/connecting-to-postgres/pooling-and-limits), [Supabase Project Pausing Policy](https://supabase.com/docs/guides/platform/free-project-pausing)

**Deliverables:**
- Cấu hình kết nối linh hoạt hỗ trợ cả `DATABASE_URL` (tiêu chuẩn Supabase/Cloud) và các biến môi trường rời rạc (`DB_HOST`, `DB_PORT`,...), hỗ trợ cấu hình SSL an toàn.
- Cập nhật `data-source.ts` (cho TypeORM CLI Migration) và `TypeOrmConfigService` (NestJS runtime) hoạt động trơn tru với Supabase (hỗ trợ cả Direct Connection port 5432 và Supavisor Transaction Pooler port 6543).
- Cập nhật `boilerplate/backend/.env.example` với các biến môi trường và ghi chú cấu hình kết nối Supabase chi tiết.
- Script TypeScript độc lập `keepalive.ts` chạy bằng `tsx`/`ts-node` để ping DB (1 WRITE -> 1 READ), tự dọn dẹp (tối đa 100 rows), có cơ chế retry backoff và cờ `--dry-run`.
- Workflow GitHub Actions `.github/workflows/db-keepalive.yml` chạy định kỳ 24h và hỗ trợ trigger thủ công qua `workflow_dispatch`.
- Hướng dẫn sử dụng rõ ràng trong `boilerplate/README.md`.

---

## 1. Bối cảnh & Vấn đề cần giải quyết

1. **Nhu cầu kết nối Cloud DB:**
   - Trong quá trình phát triển Phase 4, các thành viên (BE Dev, FE Web, Mobile Dev) cần một môi trường CSDL PostgreSQL online dùng chung (Dev/Staging) để test API thực tế mà không bắt buộc tất cả phải tự bật Docker Postgres local.
   - Supabase Free Tier cung cấp 500 MB database PostgreSQL miễn phí, có connection pooler (Supavisor) tích hợp sẵn, là phương án cloud DB lý tưởng cho giai đoạn này.
2. **Hạn chế của Boilerplate hiện tại:**
   - `ApiConfigService` và `data-source.ts` hiện tại chỉ nhận các biến rời rạc (`DB_HOST`, `DB_PORT`, `DB_USERNAME`, `DB_PASSWORD`, `DB_DATABASE`).
   - Cấu hình SSL chỉ bật khi `NODE_ENV === 'production'`, trong khi Supabase yêu cầu SSL ngay cả ở môi trường Dev (`ssl: { rejectUnauthorized: false }`).
   - Chưa hỗ trợ parse trực tiếp chuỗi `DATABASE_URL` (định dạng kết nối phổ biến nhất trên Supabase Dashboard).
3. **Nguy cơ "Dead / Paused Database":**
   - Theo chính sách của Supabase Free Tier, project sẽ **tự động bị tạm dừng (paused/inactive)** nếu không có bất kỳ truy vấn nào trong vòng **7 ngày liên tục**.
   - Khi DB bị pause, ứng dụng backend sẽ mất kết nối hoàn toàn, làm gián đoạn việc phát triển và kiểm thử của cả nhóm.
   - Cần có script tự động "đánh thức" (keepalive ping) định kỳ để duy trì trạng thái active cho database mà không gây lãng phí tài nguyên hay ảnh hưởng đến bảng dữ liệu nghiệp vụ.

---

## 2. Chi tiết công việc (Checklist)

### 1. Nâng cấp cấu hình kết nối TypeORM hỗ trợ Supabase & Cloud DB
- [ ] Cập nhật `boilerplate/backend/src/shared/services/api-config.service.ts`:
  - Thêm logic hỗ trợ `DATABASE_URL`: Nếu có `DATABASE_URL`, ưu tiên parse thông tin kết nối (hoặc truyền trực tiếp dạng url cho driver postgres).
  - Thêm biến `DB_SSL` (boolean/string). Cho phép bật SSL độc lập với `NODE_ENV` (mặc định tự động bật nếu kết nối tới Supabase, ví dụ host chứa `supabase.co` hoặc `pooler.supabase.com`).
  - Cấu hình SSL: `ssl: isSsl ? { rejectUnauthorized: false } : false`.
- [ ] Cập nhật `boilerplate/backend/src/shared/infra/typeorm/data-source.ts`:
  - Đảm bảo TypeORM CLI (`npm run migration:run`, `npm run migration:generate`) có thể đọc được `DATABASE_URL` hoặc cấu hình SSL tương tự runtime.
  - Lưu ý kỹ thuật: TypeORM Migration yêu cầu Session Mode / Direct Connection (port 5432) vì migration thường chạy lệnh DDL/transaction lock, không nên chạy qua Transaction Pooler port 6543.
- [ ] Cập nhật `boilerplate/backend/.env.example`:
  - Bổ sung mẫu cấu hình:
    ```bash
    # Database Configuration (PostgreSQL / Supabase)
    # Cách 1: Dùng DATABASE_URL (Ưu tiên khi dùng Cloud / Supabase)
    # Session mode (Port 5432 - Dùng cho Migration & Dev):
    # DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
    # Transaction Pooler (Port 6543 - Dùng cho Backend high-traffic):
    # DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
    
    # Cách 2: Cấu hình biến rời rạc
    DB_HOST=localhost
    DB_PORT=5432
    DB_USERNAME=postgres
    DB_PASSWORD=postgres
    DB_DATABASE=app_db
    DB_SSL=false
    ```

### 2. Phát triển Script Keepalive chống Pause Database
- [ ] Tạo thư mục `boilerplate/backend/scripts/` (hoặc `scripts/keepalive/`).
- [ ] Viết script `keepalive.ts`:
  - Viết bằng TypeScript thuần sử dụng thư viện `pg` (hoặc TypeORM DataSource sẵn có), chạy độc lập qua `npx tsx scripts/keepalive.ts`.
  - **Tự khởi tạo bảng riêng:** Tự động tạo bảng `ops_keepalive` nếu chưa tồn tại (tách biệt 100% với bảng nghiệp vụ):
    ```sql
    CREATE TABLE IF NOT EXISTS ops_keepalive (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      pinged_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      app_version VARCHAR(50) DEFAULT '1.0.0',
      note VARCHAR(255) DEFAULT 'Keepalive health check'
    );
    ```
  - **Quy trình kiểm tra an toàn (Write + Read-back):**
    1. Thực hiện 1 lệnh `INSERT INTO ops_keepalive ...`
    2. Thực hiện 1 lệnh `SELECT * FROM ops_keepalive WHERE id = ...` để xác nhận commit thành công.
  - **Cơ chế tự dọn dẹp (Retention Management):**
    - Sau khi ghi, tự động chạy lệnh dọn dẹp chỉ giữ lại tối đa **100 records** mới nhất:
      ```sql
      DELETE FROM ops_keepalive
      WHERE id NOT IN (
        SELECT id FROM ops_keepalive ORDER BY pinged_at DESC LIMIT 100
      );
      ```
    - Đảm bảo dung lượng bảng luôn ở mức vài KB, không chiếm dụng quota 500 MB của Supabase.
  - **Cơ chế chịu lỗi (Fault-Tolerance):**
    - Thử lại tối đa 3 lần với exponential backoff (`1s -> 4s -> 16s`) nếu kết nối bị timeout hoặc gián đoạn.
    - Nếu thất bại sau 3 lần, log rõ lỗi và thoát với `process.exit(1)` (kích hoạt cảnh báo CI/CD).
  - **Cờ `--dry-run`:**
    - Cho phép chạy `npx tsx scripts/keepalive.ts --dry-run` chỉ thực hiện `SELECT now()` kiểm tra kết nối mà không ghi dữ liệu vào bảng.
- [ ] Thiết kế script chạy trực tiếp độc lập:
  - Script được gọi trực tiếp qua `npx tsx scripts/keepalive.ts` mà không bắt buộc phải khai báo vào `package.json` (giúp giữ file manifest của service backend gọn gàng, tách biệt nhiệm vụ Ops/CI).
  - *(Tùy chọn khi dev local)*: Dev có thể gõ trực tiếp `npx tsx scripts/keepalive.ts --dry-run` để test kết nối trước khi push lên repo.

### 3. Thiết lập Tự động hóa qua GitHub Actions (Keepalive Cron)
- [ ] Tạo file workflow `.github/workflows/db-keepalive.yml`:
  - **Thực thi trực tiếp qua `npx tsx`:** Workflow chạy độc lập `npx tsx scripts/keepalive.ts` mà không qua `npm run`:
    ```yaml
    - name: Run DB Keepalive
      env:
        DATABASE_URL: ${{ secrets.SUPABASE_DATABASE_URL }}
      run: npx tsx scripts/keepalive.ts
    ```
  - **Lịch chạy định kỳ (Cron):** Chạy 24 giờ một lần (ví dụ `17 3 * * *` - 03:17 UTC hàng ngày).
    *(Lý do: Supabase pause sau 7 ngày idle; nhịp 24h đảm bảo an toàn tuyệt đối, chịu được lỡ vài run mà không làm lãng phí thời gian chạy CI).*
  - **Kích hoạt thủ công (`workflow_dispatch`):** Cho phép dev/maintainer trigger thủ công trực tiếp từ tab Actions trên GitHub (có thể hỗ trợ option chạy với `--dry-run`).
  - **Biến môi trường bí mật:** Đọc `DATABASE_URL` từ GitHub Repository Secret (`SUPABASE_DATABASE_URL` hoặc `DATABASE_URL`).
  - Gửi thông báo / alert nếu workflow fail (thất bại kết nối).

### 4. Tài liệu hóa & Kiểm thử nghiệm thu
- [ ] Cập nhật `boilerplate/README.md`:
  - Bổ sung mục **"Hướng dẫn kết nối Supabase PostgreSQL"**: cách lấy connection string, phân biệt cổng 5432 (Session/Migration) và 6543 (Supavisor Transaction Pooler).
  - Bổ sung mục **"Cơ chế Keepalive chống Pause DB"**: giải thích vì sao cần keepalive, cách chạy test thủ công và cách cấu hình GitHub Actions.

---

## 3. Tiêu chí nghiệm thu (Definition of Done)

1. **Kết nối Supabase thành công:**
   - Điền thông tin Supabase vào `.env`, chạy `npm run start:dev` backend khởi động và kết nối thành công mà không gặp lỗi SSL (`self-signed certificate` hay `no pg_hba.conf entry`).
2. **Chạy Migration trên Supabase:**
   - Chạy `npm run migration:run` thành công trên instance Supabase thông qua Direct Connection (port 5432).
3. **Script Keepalive hoạt động chuẩn xác:**
   - Chạy test local bằng `npx tsx scripts/keepalive.ts --dry-run`: Trả về kết nối OK, thời gian phản hồi (latency ms), không ghi dữ liệu.
   - Chạy `npx tsx scripts/keepalive.ts`: Bảng `ops_keepalive` được tạo, bản ghi mới được insert và read-back thành công; kiểm tra tổng số dòng không vượt quá 100.
4. **GitHub Actions hoạt động:**
   - Workflow `.github/workflows/db-keepalive.yml` được kích hoạt bằng `workflow_dispatch` chạy thành công (green status) trên GitHub Actions gọi trực tiếp file script.
