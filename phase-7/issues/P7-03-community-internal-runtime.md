# P7-03 — Bật Community trong runtime nội bộ

**Assignee:** `baoduong17` · **Iteration:** It5 · **Ước lượng:** 1 point
**Repo:** `infra` + `community-service` · **Phụ thuộc:** — · **Trạng thái:** 🟢 Done

## Bối cảnh agent cần đọc

Community NestJS đã có scaffold, health, outbox/inbox; không tạo service mới. Đọc `community-service/AGENTS.md`, `community-service/.env.example`, `community-service/src/app.module.ts`, `infra/docker-compose.internal.yml`, các service identity/tenancy trong compose, và `pm/phase-7/README.md`.

## Mục tiêu

Community chạy được trong profile môi trường nội bộ để Gateway gọi tới, dùng database/service config riêng nhất quán với scaffold. Service chỉ được truy cập qua Gateway trong môi trường tích hợp.

## Acceptance

- [ ] Kích hoạt cấu hình Community tương tự optional service hiện có; container nhận env file và tham gia network nội bộ.
- [ ] Đồng bộ port trong `community-service/.env.example` (hiện mặc định 3001), compose nội bộ (Community dự kiến 3004) và `COMMUNITY_SERVICE_URL`; service không xung đột với Identity.
- [ ] Gateway gọi được health endpoint theo cấu hình môi trường và service port chỉ được expose theo network/private deployment hiện tại.
- [ ] Không expose RabbitMQ hoặc Community trực tiếp ra Internet; không commit secret hay file env chứa secret.
- [ ] Không thay đổi migration/schema hoặc bật production rollout trong issue này.

## Kiểm tra

- Dùng compose profile nội bộ để khởi động Community và xác nhận health trả thành công từ network tích hợp.
- Kiểm tra `community-service` build/lint theo `AGENTS.md` nếu có thay đổi source.

## Không làm

- Không cấu hình FCM, Socket hoặc domain event publisher ở lát cắt runtime này.
