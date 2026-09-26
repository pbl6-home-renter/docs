# P2-06 — API Spec v1 (OpenAPI/Swagger)

**Status:** 🟡 Open
**Owner:** BE
**Input:** P2-04 (ERD v1 — chưa có file), P2-05 (API Conventions), `phase-1/discovery/database-design.md`, user_flow/*.md
**Output:** `openapi.yaml` trong `pbl6-backend` (handoff được generate ở repo `pbl6-backend`, ngoài workspace này) · design input: `discovery/api-spec.md` (106 endpoints, 24 groups)

---

## Background

ERD v1 (P2-04) **chưa có deliverable `discovery/erd-v1.md`** — P2-04 vẫn `🟡 Open`. Endpoint design dùng `phase-1/discovery/database-design.md` làm nguồn schema thay thế. Cần đối chiếu lại khi P2-04 chốt, trước khi freeze P2-08.

## Mục đích

Tạo OpenAPI spec v1 cho toàn bộ API → dùng làm contract giữa BE và FE/Mobile.

## Endpoint inventory (final)

106 endpoints trong 24 nhóm domain. Số liệu này đã đối chiếu trực tiếp với 24 bảng domain và 106 endpoint block trong `api-spec.md` §27:

1. Auth (6)
2. User (9) — gồm 2 action `lock`, `unlock` tách khỏi PATCH
3. PushDevice (2)
4. Media (4)
5. Building (10) — tách theo vai trò: public `/buildings`, chủ nhà `/me/buildings`, admin `/admin/buildings`
6. Room (6) — gồm action `mark-ready` tách khỏi PATCH
7. FavoriteRoom (3)
8. RoommateProfile (4)
9. MatchRequest (4)
10. RatePolicy (4) — *scope `landlord` pending migration*
11. BillingSetting (3) — *scope `landlord` pending migration*
12. ContractTemplate (2)
13. Contract (9) — gồm `GET /me/contracts` cho tenant
14. ContractMember (4)
15. MeterReading (3)
16. Invoice (8) — 2 bulk action (`issue-invoice`, `send-reminder`) + `GET /me/invoices`
17. Payment (5) — gồm `GET /me/payments`
18. IssueReport (6) — gồm action `cancel` tách khỏi PATCH + `GET /me/issues`
19. Conversation (3)
20. Message (3) — *read cursor migration dependency*
21. Notification (3)
22. NotificationPreference (2)
23. AuditLog (2)
24. Dashboard (1)

Total: 106 endpoints.

> **D39 (2026-09-26):** nhóm `VietQrReceiverConfig` (2 endpoint) đã bị gỡ khỏi hợp đồng. Tài khoản nhận tiền nay là 3 trường trên `LandlordProfile`, đọc/sửa qua `GET /me` và `PATCH /me` — **không tính thành nhóm endpoint riêng**. Vì vậy nhóm domain đi từ 25 xuống 24, và tổng endpoint từ 108 xuống 106.

**Vì sao 94 → 106 (xem `decisions.md` D48):** các endpoint gộp nhiều vai trò hoặc gộp hành động vòng đời vào một `PATCH` đã được tách lại. Tách theo vai trò thêm 7 route `/me/*` cho chủ nhà và tenant; tách theo business action thêm `lock`, `unlock`, `approve`, `reject`, `mark-ready`, `cancel`. Baseline commit `f96888b` vốn đã mô tả riêng các action này nên đây là khôi phục ranh giới cũ, không phải thêm scope mới.

## Chi tiết thực hiện

### Bước 1: List endpoints từ feature map + user flow

Với mỗi feature có label `PRIMARY` hoặc `co-PRIMARY` trên Web/Mobile:
- Xác định CRUD operations cần thiết
- Xác định auth requirement (public, tenant, landlord, admin)
- Xác định relationship (nested resource hay top-level) — **flat namespace, parent IDs in body/query only**

### Bước 2: Design request/response schema

- Request body theo entity fields từ P2-04
- Response wrap theo format chuẩn ở P2-05: success `{ statusCode, code, data }`, list thêm `pagination`; error `{ statusCode, code }`
- Pagination format theo convention ở P2-05
- Error `code` theo convention ở P2-05 (không dùng `message`)

### Bước 3: Write OpenAPI YAML

- Version: 3.0+
- Path organization: `/api/v1/...`
- Consistent naming (kebab-case cho paths, camelCase cho fields)
- Include auth schemes (JWT Bearer)
- Include common response codes
- **Export YAML → generate trong repo `pbl6-backend`** (không nằm trong workspace này)

### Bước 4: Sync Apidog

- Export YAML → import Apidog
- Verify rendering correct

## Definition of Done

- [ ] File `openapi.yaml` tồn tại trong `pbl6-backend`
- [ ] Mỗi feature từ P2-01 đều có endpoint(s) tương ứng
- [x] Mỗi endpoint có: method, path, request schema, response schema, auth
- [x] Error response format theo P2-05 conventions
- [ ] YAML syntax valid (dùng swagger-cli validate hoặc tương đương)
- [ ] Sync sang Apidog thành công
- [ ] PM đã review (optional nhưng recommended)

## Open dependencies (blocking freeze)

- ~~`VietQrReceiverConfig` table — building-level QR receiver data~~ **Đã gỡ theo D39 (2026-09-26):** bỏ bảng và 2 endpoint; tài khoản nhận tiền nằm ở `LandlordProfile`, đọc/sửa qua `GET /me` + `PATCH /me`. Nếu baseline `f96888b` đã tạo bảng thì phải **xoá bằng migration**.
- `ConversationMember` read cursor column — required by `POST /messages/mark-read`
- `RatePolicy` explicit `landlord` scope + `type` value `other` — database enum currently does not allow it
- `BillingSetting` explicit `landlord` scope
- P2-04 ERD finalized (`discovery/erd-v1.md`) — reconciliation before P2-06 freeze
- **Bulk meter-reading (`MeterReadingBatch`) — pending PM decision, D47.** PM đã quyết định giữ nguyên pending tại session hiện tại, chưa đưa vào v1. Baseline có `POST /buildings/{buildingId}/meter-reading-batches` cùng 3 màn hình draft đánh dấu `[MỚI]`, nhưng `requirement.md` chưa xác nhận và `api-conventions.md` §14 cấm bulk cho chốt chỉ số. v1 giữ nguyên 108 endpoint, chỉ có `POST /meter-readings` từng phòng; xem `api-spec.md` §29.14, §30 và `decisions.md` D47. Đây là lý do chính khiến spec chưa thể freeze.
