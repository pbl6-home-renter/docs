# P2-05 — API Spec v1 (OpenAPI/Swagger)

**Status:** 🟡 Open
**Owner:** BE
**Input:** P2-04 (ERD v1), user_flow/*.md, business-rules
**Output:** `openapi.yaml` trong `pbl6-backend`

---

## Background

ERD v1 đã chốt (P2-04). Giờ cần thiết kế REST API endpoints trên cơ sở đó — mỗi endpoint map với entity/operation trong ERD.

## Mục đích

Tạo OpenAPI spec v1 cho toàn bộ API → dùng làm contract giữa BE và FE/Mobile.

## Chi tiết thực hiện

### Bước 1: List endpoints từ feature map + user flow

Với mỗi feature có label `PRIMARY` hoặc `co-PRIMARY` trên Web/Mobile:
- Xác định CRUD operations cần thiết
- Xác định auth requirement (public, tenant, landlord, admin)
- Xác định relationship (nested resource hay top-level)

### Bước 2: Design request/response schema

- Request body theo entity fields từ P2-04
- Response wrap theo format chuẩn (`{ data, meta, error }`)
- Pagination format (cursor-based hoặc offset)
- Error response code + message

### Bước 3: Write OpenAPI YAML

- Version: 3.0+
- Path organization: `/api/v1/...`
- Consistent naming (kebab-case cho paths, camelCase cho fields)
- Include auth schemes (JWT Bearer)
- Include common response codes

### Bước 4: Sync Apidog

- Export YAML → import Apidog
- Verify rendering correct

## Definition of Done

- [ ] File `openapi.yaml` tồn tại trong `pbl6-backend`
- [ ] Mỗi feature từ P2-01 đều có endpoint(s) tương ứng
- [ ] Mỗi endpoint có: method, path, request schema, response schema, auth
- [ ] Error response format chuẩn
- [ ] YAML syntax valid (dùng swagger-cli validate hoặc tương đương)
- [ ] Sync sang Apidog thành công
- [ ] PM đã review (optional nhưng recommended)
