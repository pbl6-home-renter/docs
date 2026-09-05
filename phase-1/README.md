# Phase 1 — Setup + Requirements Freeze (W3–4)

> Scope của Phase 1 theo `PROJECT_PLAN.md` §5: setup 4 repos + docs hub, chuẩn hoá quy ước, đóng băng nghiệp vụ.
> **Lưu ý:** Các việc vận hành/ngoài code (Linear board, tạo repo GitHub + branch protection, đồng bộ Apidog) do **PM tự xử lý & nhắc** — không nằm trong các issue ở đây. Các issue trong `issues/` tập trung vào **quyết định kỹ thuật của FE & Mobile** (feature map → setup tech stack → quy ước chung → thiết kế UI).

## Nội dung Phase 1

| Bước | Issue | Chủ đề | Trạng thái |
|------|-------|--------|-----------|
| 1 | [P1-01](issues/P1-01-feature-platform-map.md) | Mapping feature → nền tảng (web / mobile / cả 2) — **làm trước** | 🟡 Open |
| 2 | [P1-02](issues/P1-02-fe-setup.md) | FE Web setup — chọn tech stack, library, quy ước, agent skill | 🟡 Open |
| 3 | [P1-03](issues/P1-03-mobile-setup.md) | Mobile setup — chọn tech stack, library, quy ước, agent skill | 🟡 Open |
| 4 | [P1-04](issues/P1-04-shared-conventions.md) | Quy ước chung (validation, error, currency/date, image, API contract) | 🟡 Open |
| 5 | [P1-05](issues/P1-05-ui-design.md) | Thiết kế UI (sitemap/wireframe/design) cho web + mobile — thống nhất | 🟡 Open |

## Trật tự phụ thuộc

```
P1-01 Feature map  ──► (input cho) P1-02 FE, P1-03 Mobile   (biết mình build gì trước)
                              │
                              ▼
                     P1-04 Quy ước chung (sau khi chốt tech stack)
                              │
                              ▼
                     P1-05 UI design (dùng feature map + tech stack)
```

## Các việc PM tự nhắc (không tạo issue)

- Tạo 4 repo GitHub + seed `README.md` / `AGENTS.md` / branch protection.
- Setup Linear board (backlog/sprints) + mirror GitHub Projects + Notion wiki.
- Đồng bộ API contract Swagger ↔ Apidog.
- Xin tài nguyên (LLM API key, VNPay sandbox) theo `product-sketch.md` §7.
