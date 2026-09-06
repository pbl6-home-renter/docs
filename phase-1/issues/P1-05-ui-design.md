# P1-05 — UI Design (Web + Mobile)

**Status:** 🟡 Open
**Assignee:** FE + Mobile (thiết kế) · **PM (review & duyệt hướng thống nhất)**
**Depends on:** P1-01 (feature map), P1-02/P1-03 (tech stack + component lib), P1-04 (design token / quy ước chung)
**Deliverable:** 
- FE: `pm/phase-1/discovery/ui-fe-design.md` (sitemap + wireframe + design system)
- Mobile: `pm/phase-1/discovery/ui-mobile-design.md` (sitemap + wireframe + design system)
- PM: review & duyệt 1 hướng chung, or yêu cầu fix → `pm/phase-1/discovery/ui-design-review.md`

---

## Mục đích

Thiết kế **định hướng giao diện (UI) sơ bộ** cho cả 2 nền tảng — **không chỉ chọn màu**, nhưng cũng **chưa phải bản hoàn thiện/chốt chính thức**. 

> **Về "chuẩn chưa?":** P1-05 (Phase 1) tạo **bản sơ bộ đủ dùng để scaffold + chốt tech stack trước** (biết mình cần lib chart/map/form gì, bố cục thế nào). Bản **wireframe hoàn thiện + lock chính thức** sẽ được làm chi tiết trong **Phase 2 — "Sitemap + wireframes (structure-level)"** theo `PROJECT_PLAN.md` (W5–6), nơi đây cung cấp input nền.
>
> **Phong cách:** Tự do sáng tạo. Không có nền tảng nào làm "chuẩn" — cả 2 tự do thiết kế, miễn là **giao để PM duyệt output thống nhất** về thương hiệu/look-and-feel (màu chủ đạo, hình thể nút/card, tone). Nếu Web và Mobile lệch nhau về hướng thị giác, PM sẽ bắt fix về 1 hướng chung.

---

## Yêu cầu thiết kế

### A. Sitemap / Navigation structure
- Dựa trên `product-platform-map.md` (P1-01), liệt kê **toàn bộ trang (FE)** / **màn hình + luồng (Mobile)** cần có.
- Web: **landlord side** (dashboard, rooms, buildings, contracts, invoices, issues...) + **tenant side** (search, my-invoices, roommate...).
- Mobile: **tenant primary** (search map, filters, room detail, invoice, payment, roommate profile/browse/request, issue report/Property Chat, profile) + **landlord-lite** (push, approve issue, view dashboard/invoice).
- Sắp xếp **navigation tree** + luồng điều hướng chính giữa các trang.

### B. Wireframe (structure-level, không cần pixel-perfect)
- Với **từng màn hình quan trọng** (MVP), vẽ wireframe thô: bố cục vùng (header/sidebar/nội dung), vị trí thành phần, luồng form multi-step (e-contract 3.1, cài đặt building, tạo phòng).
- Ưu tiên các luồng cốt lõi từ `../discovery/user_flow/` (per-role SoT — tenant / landlord / admin / shared):
  - Landlord: add building/room → tạo HĐ (đa bước) → chốt số OCR → xem hóa đơn/QR → dashboard.
  - Tenant: search map → filter → room detail → invoice/pay → report issue/chat → roommate.
- Không cần đúng tới từng pixel — **structure + flow** là đủ (đáp ứng yêu cầu môn học).

### C. Design System (component-level)
- **FE:** danh sách component UI dùng (từ thư viện đã chọn P1-02) — button, input, table/data-table, card, dialog, form field, toast, skeleton... + cách tổ chức.
- **Mobile:** component M3 dùng + bộ custom (nếu có) — top bar, card, text field, bottom sheet, snackbar...
- **Tokens chung:** màu primary, typography, spacing, border-radius (đã đề xuất ở P1-04) → triển khai cụ thể trong component.

### D. Thống nhất look-and-feel (để PM duyệt)
- Mỗi bên mô tả **design direction** ngắn: mood, màu sắc, hình thể nút/card, tone (hiện đại/thân thiện/chuyên nghiệp).
- PM so sánh 2 bên → **chốt 1 hướng chung** hoặc yêu cầu điều chỉnh để Web + Mobile trông thuộc cùng 1 sản phẩm.

---

## Công cụ gợi ý (không bắt buộc)
- Tự do: Figma / Excalidraw / draw.io / mermaid (markdown) / ảnh chụp wireframe. Vì repo là markdown hub, có thể dùng **mermaid** cho sitemap + mô tả wireframe bằng text/ascii, hoặc kèm ảnh.

## Định nghĩa "Done"

- [ ] FE: `ui-fe-design.md` gồm sitemap + wireframe *sơ bộ* các màn hình chính + design system hướng + design direction.
- [ ] Mobile: `ui-mobile-design.md` gồm sitemap + wireframe *sơ bộ* các màn hình chính + design system hướng + design direction.
- [ ] PM review → ra `ui-design-review.md` duyệt **hướng chung** (hoặc danh sách fix).
- [ ] Đánh dấu rõ: đây là **định hướng sơ bộ**; bản wireframe hoàn thiện + lock chính thức = **Phase 2** (sitemap + wireframes) theo `PROJECT_PLAN.md`.

---

*Không làm Linear/GitHub/Apidog — PM tự nhắc.*
