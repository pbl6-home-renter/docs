# P6-12 — Identity: `GET /internal/media/{mediaId}` cho service nội bộ

**Trạng thái:** 🟡 Open  
**Người phụ trách:** baoduong17  
**Người review:** leminhkhai345 (dùng ở P6-01d)  
**Ước lượng:** 1 point · 2–3 giờ  
**Phụ thuộc:** P6-04 (đã merge)  
**Repo / branch:** `Identity-Service` · `feature/p6-12-internal-media-lookup`  
**Iteration:** It5 prerequisite  
**Issue:** `docs#111`

## Mục tiêu

Tenancy kiểm tra được `mediaId` client gửi (vd. `signedContractMediaId` khi activate) có thật, đã upload xong, đúng owner và purpose.

## Quyết định áp dụng

- `P6-D73` — `GET /internal/media/{mediaId}` (`@InternalOnly()`) trả `{ id, ownerType, ownerId, purpose, status }`.

## Tham chiếu code

- Mẫu controller nội bộ: `Identity-Service/src/modules/users/presentation/http/controllers/user-internal.controller.ts`.
- Domain media: `Identity-Service/src/modules/media/`.

## Các bước triển khai

### Bước 1 — Query + controller nội bộ

- **Kiểm tra bước:** có `X-Service-Token` + id đã upload → `200` đúng 5 field; thiếu token → bị chặn; UUID không tồn tại → `404`.

### Bước 2 — Không lộ qua gateway

- **Kiểm tra bước:** `curl https://<staging>/internal/media/<id>` → `404 ROUTE_NOT_FOUND`.

## Definition of Done

- [ ] `npm run build` + `npm run lint` pass; không sửa `src/shared`.
- [ ] Link PR vào issue P6-01d.
