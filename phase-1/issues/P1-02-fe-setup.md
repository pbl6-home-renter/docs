# P1-02 — FE Web Setup

**Status:** 🟡 Open
**Assignee:** FE
**Depends on:** P1-01 (feature map — để biết build gì)
**Deliverable:** Proposal file của FE (tự nghiên cứu + chọn + giải thích lý do) → `pm/phase-1/discovery/fe-proposal.md`

---

## Mục đích

Thiết lập repo `pbl6-web` (React): chọn tech stack, library, bộ component UI, coding convention, và agent skill. Mục tiêu là **repo có thể code ngay**, mọi người tuân theo 1 chuẩn thống nhất.

> **Cách làm:** **Tự nghiên cứu** (web/cú pháp 2026), **nêu rõ lựa chọn + lý do** cho từng mục. Không có đáp án đúng tuyệt đối — PM chỉ cần bạn căn cứ nhu cầu dự án này (ops dashboard + tenant portal, demo 13 tuần, 1 dev, cần bản đồ/biểu đồ/form) mà chọn hợp lý và **giải thích được**.
>
> Bối cảnh dự án: Web = **landlord ops console (chính)** + **tenant responsive portal (phụ)**. Cần: dashboard biểu đồ (1.3/3.7), CRUD phòng/tòa (1.1/1.2), e-contract (3.1), chốt số OCR (3.3), hóa đơn + QR động (3.4/3.5/3.10), cấu hình giá (3.11), tìm phòng bản đồ (2.1, web-secondary), Property Chat issue/chat panel (6.6), 2 role (landlord/tenant).

---

## Câu hỏi cần quyết định

### A. Scaffold & ngôn ngữ
- A1. Build tool: **Vite** / **Next.js** / khác? (gợi ý cân nhắc: đây là app behind-login, không cần SEO/SSR) — vì sao?
- A2. TypeScript: có dùng **strict mode** không? Bật toàn bộ `noUnusedLocals`, `noImplicitAny`...?
- A3. Path alias `@/` hay import tương đối? Cấu hình ở đâu (`tsconfig` + bundler)?

### B. Cấu trúc folder
- B1. **Feature-based** hay **layer-based**? Đưa cây thư mục cụ thể (app/ features/ shared/...).
- B2. Quy ước đặt tên file/component/hook/util (PascalCase component? `useX` hooks? `.types.ts`?).
- B3. Có dùng barrel export (`index.ts`) ở feature boundary không?

### C. Code quality
- C1. **ESLint** bản nào + flat config hay dạng cũ? Plugin nào (react, hooks, import, prettier)? Có `@typescript-eslint` không?
- C2. **Prettier**: cấu hình (semi, quote, trailing comma, printWidth)?
- C3. **Husky + lint-staged** pre-commit cho cả lint + format?
- C4. Có cần **commitlint** (conventional commits) không, hay bỏ qua?

### D. State management
- D1. Client state (UI): **Zustand** / **Redux Toolkit** / **Jotai** / khác? Vì sao?
- D2. Server cache (dữ liệu từ API: room, invoice, contract): có dùng **TanStack Query** không, hay tự quản lý?
- D3. Nguyên tắc: data từ server dùng gì, data UI-local dùng gì (tránh 2 nguồn sự thật)?

### E. Routing
- E1. **React Router v7** hay khác? Config-based hay file-based?
- E2. Pattern cho **protected route** (cần login) + **role guard** (landlord vs tenant)?
- E3. Cấu trúc layout (DashboardLayout/Sidebar/Outlet)? Deep link nào cần?

### F. Forms & validation
- F1. **React Hook Form + Zod** / **Formik + Yup** / khác? Vì sao?
- F2. Pattern schema-based validation (resolver)? 
- F3. **Multi-step form** (e-contract 3.1, onboarding có nhiều bước) xử lý thế nào?
- F4. **File upload** (PDF HĐ, ảnh CCCD, ảnh phòng) — validate size/type, kéo thả hay nút chọn?

### G. UI Component Library & Styling
- G1. Chọn 1: **shadcn/ui + Tailwind** / **Ant Design** / **MUI** / **Chakra** / khác? Vì sao phù hợp ops-dashboard?
- G2. Tailwind version nào (nếu chọn)? Setup config (CSS vars, design tokens)?
- G3. Có cần **dark mode** không? Cơ chế toggle?

### H. Charts (cho dashboard 3.7)
- H1. **Recharts** / **Nivo** / **Chart.js** / **Tremor** / khác? Vì sao?
- H2. Cần chart nào (line, bar, area, donut...)? Chọn lib cover đủ?

### I. Maps (cho tìm phòng 2.1, web-secondary)
- I1. **Leaflet+react-leaflet** / **Google Maps** / **Mapbox**? Xét chi phí free-tier + mức cần dùng trên web.
- I2. Có cần marker clustering không?

### J. HTTP Client & API
- J1. **Axios** / fetch wrapper / **ky**? Vì sao?
- J2. Pattern **JWT refresh token interceptor** (đấu vào queue khi hết hạn)?
- J3. Có generate type-safe từ **OpenAPI** (backend spec) không? Dùng tool nào (`@hey-api/openapi-ts`...)?

### K. Error / Loading / Toast
- K1. **Error boundary** (react-error-boundary?) — mức nào (route-level)?
- K2. Loading: **skeleton** hay spinner cho từng trường hợp?
- K3. Toast: chọn lib nào (sonner/hot-toast/notistack...)?

### L. Auth flow
- L1. Token lưu ở đâu: **memory + httpOnly cookie** / **localStorage** / khác? Cân nhắc XSS (MVP có thể chấp nhận đơn giản).
- L2. Role-based UI rendering (landlord vs tenant view) thế nào?

### M. Env & Build
- M1. Cấu trúc `.env` (bao nhiêu file: dev/prod? `VITE_` prefix?).
- M2. Có cần **lazy loading / code splitting** route không? Manual chunks?

### N. Agent skill (repo `pbl6-web`)
- N1. Viết `AGENTS.md` cho repo (trỏ về `pm/phase-1/` + quy ước team: ngôn ngữ, git flow, task tracking).
- N2. (Nếu dùng opencode) tạo config agent/skill `.opencode/` hay `opencode.json` cho repo. Trình bày bạn định setup gì.

---

## Yêu cầu output

1. Tạo file `pm/phase-1/discovery/fe-proposal.md` trả lời **từng câu A1→N2** + lý do ngắn gọn.
2. Bổ sung: **mục "Feature map verify"** — ghi kết quả verify P1-01 từ phía FE (đồng ý/sửa/thêm/bớt feature, lý do).
3. Bổ sung: **danh sách dependencies** (package name + version) sẽ thêm vào `package.json`.
4. Nêu rõ bất kỳ tradeoff nào bạn cân nhắc (vd chọn AntD vì...) để PM + Mobile biết.
5. Đánh dấu mục nào là **quyết định nhạy cảm chung** (ảnh hưởng 2 platform: màu chủ đạo, validation, format, translation) → sẽ đưa sang P1-04/P1-05 để thống nhất.

## Định nghĩa "Done"

- [ ] Proposal FE đầy đủ A1→N2 + lý do.
- [ ] Feature map verify (P1-01) đã ghi trong proposal.
- [ ] Danh sách dependencies + version.
- [ ] Các quyết định ảnh hưởng cross-platform được highlight cho PM (P1-04/P1-05).
- [ ] Sẵn sàng demo scaffold `npm create vite` + chạy được trang trống khi PM duyệt tech stack.

---

*Không tạo issue riêng cho Linear/GitHub/Apidog — PM tự nhắc.*
