# P2-07 — Design Review → Freeze

**Status:** 🟡 Open
**Owner:** All
**Input:** P2-01–P2-06
**Output:** Design frozen ✓

---

## Background

Toàn bộ design artifacts đã hoàn thành (P2-01–P2-06). Cần team review chung → xác nhận không có issue → freeze design trước khi sang Phase 3 (scaffolding + code).

## Mục đích

Đảm bảo design artifacts nhất quán, không thiếu, không conflict → team đồng ý freeze.

## Chi tiết thực hiện

### Bước 1: Individual review

Mỗi member đọc artifacts theo role:

| Role | Review |
|------|--------|
| PM | P2-01 (map), P2-02 (sitemap), P2-06 (diagrams), overall consistency |
| FE | P2-02 (sitemap web), P2-03 (wireframe web), P2-05 (API cho web) |
| Mobile | P2-02 (sitemap mobile), P2-03 (wireframe mobile), P2-05 (API cho mobile) |
| BE | P2-04 (ERD), P2-05 (API spec), consistency giữa ERD ↔ API ↔ wireframe |

### Bước 2: Group review meeting

- Walk through từng artifact
- Flag issues (missing, conflict, unclear)
- Record decisions → `discovery/decisions.md`

### Bước 3: Fix & confirm

- Fix issues identified
- Everyone signs off

### Bước 4: Update status

- Update `issues/README.md`: P2-01–P2-06 → 🟢 Done
- Ghi design freeze vào `discovery/decisions.md`
- Update `PROJECT_PLAN.md` nếu cần

## Definition of Done

- [ ] P2-01–P2-06 tất cả đã 🟢 Done
- [ ] Group review meeting đã diễn ra
- [ ] Không có open issue nào chưa resolve
- [ ] Decision log ghi nhận "Design Frozen"
- [ ] Mọi member đã approve (PM, FE, Mobile, BE)
- [ ] `issues/README.md` updated với status mới
