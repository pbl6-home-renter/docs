# Phase 1 — Discovery / Deliverables

Các deliverable của Phase 1 (cho tới khi PM chốt, các file proposal là **draft của member**; file chính thức là bản đã PM duyệt).

| File | Trạng thái | Mô tả |
|------|-----------|-------|
| `product-platform-map.md` | 🟡 Chờ verify (P1-01) | Bảng feature → nền tảng (**bản tham khảo**, chờ FE+Mobile chỉnh) |
| `fe-proposal.md` | 🟡 Chờ FE tạo (P1-02) | Đề xuất tech stack/library/convention của FE + lý do + feature-map verify |
| `mobile-proposal.md` | 🟡 Chờ Mobile tạo (P1-03) | Đề xuất tech stack/library/convention của Mobile + lý do + feature-map verify |
| `shared-conventions.md` | 🟡 Chờ PM chốt (P1-04) | Quy ước chung: validation/error/format/image/API + **translation/i18n** + design token |
| `ui-fe-design.md` | 🟡 Chờ FE tạo (P1-05) | Sitemap + wireframe **sơ bộ** + design system hướng (web) — Phase 2 hoàn thiện |
| `ui-mobile-design.md` | 🟡 Chờ Mobile tạo (P1-05) | Sitemap + wireframe **sơ bộ** + design system hướng (mobile) — Phase 2 hoàn thiện |
| `ui-design-review.md` | 🟡 Chờ PM duyệt (P1-05) | Kết luận: duyệt hướng chung / list fix |

Ghi chú cấu trúc dự kiến cho thư mục translation:
- `i18n/` (file nguồn chuỗi dịch chung, ví dụ `source/vi.xlsx|json`) + script sinh `en/vi.json` (React) và `strings.xml` (Android) + script kiểm tra key thiếu/thừa. *(Địa điểm/định dạng cụ thể do P1-04 chốt.)*
