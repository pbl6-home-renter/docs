# P6-10a — Tạo `ai-service` từ boilerplate và deploy

**Epic:** [P6-10](P6-10-ai-service-meter-ocr.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** baoduong17  
**Người review:** leminhkhai345  
**Ước lượng:** 3 points · 6 giờ  
**Phụ thuộc:** —  
**Repo / branch:** `ai-service` (repo mới trong org `pbl6-home-renter`) · `main` khởi tạo, sau đó `feature/p6-10a-scaffold`; `api-gateway` · `feature/p6-10a-ai-route`; `infra` · `feature/p6-10a-ai-service`  
**Iteration:** It5 prerequisite  
**Issue:** `docs#108`

> Đọc `AGENTS.md` + `.agents/skills/` của `boilerplate` trước. `src/shared/` **không được sửa** (copy nguyên từ boilerplate).

## Mục tiêu

`GET https://<domain>/api/v1/ai/health` qua gateway trên staging trả `200`; Swagger tại `/api/v1/ai/swagger`. Service không cần DB hay RabbitMQ.

## Quyết định áp dụng

- `P6-D67` — `ai-service` NestJS fork từ boilerplate, không DB, không outbox, cổng **3005**, host internal, prefix gateway `/ai`.
- `P6-D75` — không sửa `src/shared`.

## Tham chiếu code

- `boilerplate/src/app.module.ts` — đang import `SharedModule` (kéo theo `TypeormModule`, `RabbitmqModule`), `OutboxModule`, `SampleModule`.
- `boilerplate/src/shared/shared.module.ts` — `TypeormModule`, `RabbitmqModule`, `InternalHttpModule`, `ApiConfigService`, `UNIT_OF_WORK_DI_TOKEN`.
- `boilerplate/src/shared/security.module.ts` — guard toàn cục, không phụ thuộc DB.
- `boilerplate/src/config/service.constants.ts` — `PATH`, `TITLE`, `DEFAULT_DATABASE_NAME`.
- Deploy mẫu: `Identity-Service/.github/workflows/deploy.yml` (commit `7adc833` "deploy identity to the internal stack").
- Gateway: `api-gateway/docs/02-routing.md` mục "Thêm service mới"; `api-gateway/src/constants/gateway-service.enum.ts`, `route-paths.constants.ts`.
- Infra: `infra/docker-compose.internal.yml` (khối `payment`/`community` đang comment), `infra/README.md` mục Security Group.

## Các bước triển khai

### Bước 1 — Tạo repo

- **Cách làm:**
  - Tạo repo `pbl6-home-renter/ai-service`, copy toàn bộ `boilerplate` (trừ `.git`), xóa module `sample`, `outbox`, `inbox` và migration/seed.
  - `service.constants.ts`: `PATH = 'ai'`, `TITLE = 'Rentify AI Service'`. `.env.example`: `PORT=3005`.
- **Kiểm tra bước:** `npm ci && npm run build` pass.

### Bước 2 — Bỏ DB và RabbitMQ mà không sửa `src/shared`

- **File tạo:** `src/modules/core/ai-core.module.ts` (*mới*): `@Global()` module chỉ import `ConfigModule.forRoot({ isGlobal: true })`, `InternalHttpModule`, provide + export `ApiConfigService`.
- **File sửa:** `src/app.module.ts`: thay `SharedModule` bằng `AiCoreModule`; giữ `SecurityModule`, `HealthModule`, filter + interceptor toàn cục.
- **Cách làm:** nếu `ApiConfigService`/`SecurityModule`/`HealthModule` vẫn đòi biến DB hoặc RabbitMQ khi khởi động thì **dừng, comment vào issue** (không vá trong `src/shared`); phương án dự phòng là cấp một DB rỗng `ai_db` — lead chốt.
- **Kiểm tra bước:** `npm run start:dev` với `.env` **không có** `DATABASE_URL`/`RABBITMQ_URL` → khởi động thành công; `curl localhost:3005/api/v1/ai/health` → `200`.

### Bước 3 — Auth

- **Kiểm tra bước:**
  - `GET /api/v1/ai/health` không token → `200` (health là public theo boilerplate).
  - Tạo tạm controller test `GET /api/v1/ai/ping` (`@Roles('landlord')`): không token → `401`; token tenant → `403`; token landlord (lấy từ Identity local) → `200`. Xóa controller test trước khi tạo PR.

### Bước 4 — Docker + CI deploy

- **Cách làm:** copy `Dockerfile` + `.github/workflows/deploy.yml` từ Identity, đổi tên image `ai-service`, container `ai`. Secret: `ANTHROPIC_API_KEY` chỉ nằm trong `env/ai.env` trên server, không commit.
- **Kiểm tra bước:** workflow chạy xanh, image `linux/amd64` có trên Docker Hub.

### Bước 5 — Infra + gateway

- **File sửa:**
  - `infra/docker-compose.internal.yml`: service `ai` cổng `3005:3005`, `env_file: ./env/ai.env`, network `rentify-internal`.
  - `infra/README.md`: thêm dòng `ai` vào bảng service; Security Group nội bộ `3001-3005`; edge env `AI_SERVICE_URL=http://<INTERNAL_PRIVATE_HOST>:3005`.
  - `api-gateway/src/constants/gateway-service.enum.ts`: `Ai = 'AI'`, env `AI_SERVICE_URL`.
  - `api-gateway/src/constants/route-paths.constants.ts`: `SERVICE_PATHS[Ai] = 'ai'`, `ROUTE_PREFIXES[Ai] = ['/ai']`.
  - Rate limit riêng cho `/ai` (ví dụ 10 request/phút/user) nếu `api-gateway/src/rate-limit/rate-limit.middleware.ts` hỗ trợ cấu hình theo prefix; nếu không, ghi vào Ngoài phạm vi.
- **Kiểm tra bước:** trên staging `curl https://<domain>/api/v1/ai/health` → `200`; `curl https://<domain>/api/v1/ai/swagger/json` → JSON. Port 3005 **không** truy cập được từ Internet (`curl http://<internal-public-ip>:3005` timeout).

## Ngoài phạm vi

- Endpoint OCR (P6-10b).
- Healthcheck tự động của gateway.

## Acceptance

- [ ] Service chạy không cần DB/RabbitMQ; `src/shared` giống hệt boilerplate (`diff -r ai-service/src/shared boilerplate/src/shared` rỗng).
- [ ] Health + Swagger qua gateway staging.
- [ ] 401/403/200 đúng role ở Bước 3.
- [ ] Port 3005 không public.

## Definition of Done

- [ ] PR `ai-service`, `api-gateway`, `infra` merged; deploy staging xanh.
- [ ] `CLAUDE.md` gốc của workspace thêm dòng `ai-service` (cổng 3005).
