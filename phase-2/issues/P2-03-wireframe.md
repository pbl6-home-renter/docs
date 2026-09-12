# P2-03 — Screen List + Sitemap + Wireframe

**Status:** 🟡 Open
**Owner:** FE + Mobile · PM review
**Input:** P2-01 (feature-platform-map.md), user_flow/*.md
**Output:** `discovery/wire_frame/`

---

## Background

Sau khi có feature-platform map (P2-01), cần chuyển thành **danh sách màn hình** + **điều hướng** + **wireframe** cho từng platform. Gộp chung 1 task cho gọn.

## Chi tiết thực hiện

### Bước 1: List screen từ feature map

Với mỗi feature trong P2-01, xác định screen cần thiết:

| Cột | Ý nghĩa |
|-----|---------|
| Screen ID | Mã (VD: `LL-01`, `T-01`, `ADM-01`) |
| Screen Name | Tên |
| Purpose | Mô tả 1 dòng |
| Feature Ref | Feature # từ P2-01 |
| Platform | Web / Mobile / Both |

### Bước 3: Wireframe từng screen

Với mỗi screen:
1. Layout skeleton (boxes)
2. Component labels (table, form, card, map, chat...)
3. Navigation links (screen nào → screen nào)

### Bước 4: Review

- FE review wireframe web
- Mobile review wireframe mobile
- PM approve

## Platform cần wireframe

| Platform | Owner | Folder |
|----------|-------|--------|
| Landlord Web | FE | `wire_frame/landlord/` |
| Admin Web | FE | `wire_frame/admin/` |
| Tenant Web (responsive) | FE | `wire_frame/tenant-web/` |
| Tenant Mobile | Mobile | `wire_frame/tenant-mobile/` |

## Definition of Done

- [ ] Screen list đầy đủ cho mỗi platform
- [ ] Sitemap mermaid cho mỗi platform — syntax valid
- [ ] Wireframe tồn tại cho: landlord web, admin web, tenant mobile
- [ ] Tenant web responsive có wireframe (nếu P2-01 cần)
- [ ] Mỗi screen có: layout skeleton, component labels, navigation
- [ ] FE đã review wireframe web
- [ ] Mobile đã review wireframe mobile
- [ ] PM đã approve
