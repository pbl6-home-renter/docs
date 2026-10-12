# P4-10 — Hoàn thiện Boilerplate Frontend Web, Chuẩn hóa Network, Base UI & Đồng bộ Design System với Mobile (Rentify Core-UI)

**Status:** 🟡 Open  
**Assignee:** FE Dev / FE Lead  
**Stakeholders / Reviewers:** PM, Mobile Lead, BE Lead  
**Created:** 2026-10-11  
**Due date:** 2026-10-14  
**Priority:** 🔴 High / Blocker (Hoàn thiện nền móng Frontend Web trước khi ghép tính năng nghiệp vụ)  

**Input:**
- Repo Frontend hiện tại: `fe/` (đã khởi tạo khung Vite + React + TypeScript từ task P4-07)
- Repo Mobile chuẩn tham chiếu: `mobile/core-ui/` (Design System tokens, Format helpers, State & Feedback UI)
- `pm/phase-2/discovery/api-conventions.md` (§1 Response Wrapper, §4 Token Cookies, §10 Error Handling)
- `pm/phase-2/discovery/api-spec.md` (§2 Auth, §3 User)
- `pm/phase-4/issues/P4-07-fe-web-boilerplate-setup.md`

**Deliverables:**
- Toàn bộ các file trắng (0 byte) trong `fe/src/` được triển khai hoàn chỉnh mã nguồn thực tế.
- Đồng bộ bảng màu thương hiệu Rentify (`rentify-primary`, `rentify-surface`,...) từ `mobile/core-ui` sang Tailwind CSS v4 của Web.
- Bộ tiện ích định dạng dữ liệu (`formatVnd`, `formatDate`, `formatDateTime`, `cn`) đồng nhất với Mobile (`FormatExt.kt`).
- Bộ component Feedback tái sử dụng (`LoadingSpinner`, `LoadingOverlay`, `EmptyState`, `ErrorState`) tương thích `core-ui`.
- Tầng HTTP Client (`lib/axios.ts`) hoàn chỉnh: Request Interceptor (Bearer token), Response Interceptor (unwrap wrapper), Refresh Token Interceptor (bắt 401 tự gọi `/auth/refresh` và retry).
- Cấu hình `QueryClient` cho TanStack Query v5 tối ưu hóa cache và error handling.
- Hệ thống Layouts (`AuthLayout`, `DashboardLayout` kèm Sidebar động phân quyền theo Role Landlord/Admin), Trang lỗi `403`, `404`.
- Hoàn thiện luồng Navigation Router (`ProtectedRoute`, `PublicRoute`, Cây Route tại `App.tsx` và `app/routes/index.tsx`).
- Hệ thống i18n instance khởi tạo hoạt động thực tế với fallback và type-safe keys.
- Hook quản lý phiên xác thực `useAuth` kết nối với `auth-store`.
- Khắc phục triệt để lỗi TypeScript build, cấu hình Husky pre-commit hook chạy `lint-staged` và `npm run build`.

---

## 1. Bối cảnh & Vấn đề cần giải quyết

1. **Thực trạng sau task setup ban đầu (P4-07):**
   - Repo `fe` đã tạo cấu trúc thư mục và một số file cơ bản nhưng còn **hơn 14 files cốt lõi đang rỗng (0 bytes)**: `utils.ts`, `api.ts`, `use-auth.ts`, `i18n.ts`, `provider.tsx`, toàn bộ thư mục `routes/`, `layout/`, `pages/` (403/404), `feedback/`, `ui/button.tsx`.
   - File `lib/axios.ts` chỉ mới tạo instance đơn thuần, thiếu hoàn toàn các interceptor quan trọng (đặc biệt là cơ chế refresh token khi 401 và unwrap API response).
   - Dự án chưa build được bằng TypeScript (`npm run build` gặp lỗi thiếu type definitions).
   - Hook Git pre-commit trong `.husky/pre-commit` chưa cấu hình đúng theo tiêu chuẩn DoD.

2. **Yêu cầu đồng bộ chặt chẽ với Mobile (`mobile/core-ui`):**
   - Phía Mobile đã xây dựng hoàn chỉnh module `core-ui` với:
     - Hệ màu Rentify chuẩn (`rentify_primary: #1E6FD9`, `rentify_on_primary_container: #142A4C`, `rentify_background: #F8FBFE`,...).
     - Tiện ích định dạng tiền Việt Nam `toVnd()` (`1.500.000 đ`) và ngày tháng `dd/MM/yyyy`, `dd/MM/yyyy HH:mm`.
     - Bộ trạng thái và feedback chuẩn: `LoadingDialog`, `view_empty_state`, `view_error_state` (có retry button).
   - Frontend Web phục vụ phân hệ **Landlord Web & Admin Console** nên cần sử dụng chung ngôn ngữ thiết kế, chuẩn hóa hiển thị và hành vi phản hồi lỗi/tải dữ liệu để đảm bảo trải nghiệm người dùng nhất quán xuyên suốt hệ sinh thái Rentify.

---

## 2. Chi tiết công việc cần triển khai (Checklist)

### 1. Bổ sung Dependencies & Khắc phục môi trường Build
- [ ] Cài đặt các package cần thiết còn thiếu trong `fe/package.json`:
  ```bash
  npm install clsx tailwind-merge lucide-react sonner
  ```
  *(Hoặc `pnpm`/`npm` tùy theo quy ước package manager)*
- [ ] Kiểm tra và sửa cấu hình `tsconfig.json` / `tsconfig.app.json` để lệnh `npm run build` (`tsc -b && vite build`) vượt qua sạch sẽ không còn lỗi TS2688.

---

### 2. Đồng bộ Design System Tokens sang Tailwind CSS v4
Đồng bộ các mã màu từ `mobile/core-ui/src/main/res/values/colors.xml` vào `fe/src/index.css`:
- [ ] Cấu hình theme tokens trong `src/index.css`:
  ```css
  @import "tailwindcss";

  @theme {
    --color-rentify-primary: #1E6FD9;
    --color-rentify-primary-hover: #175bb3;
    --color-rentify-on-primary: #FFFFFF;
    --color-rentify-primary-container: #E8F1FC;
    --color-rentify-on-primary-container: #142A4C;
    --color-rentify-background: #F8FBFE;
    --color-rentify-surface: #FFFFFF;
    --color-rentify-text-primary: #142A4C;
    --color-rentify-text-secondary: #5C7290;
    --color-rentify-divider: #D7E3F2;
    --color-rentify-success: #16A34A;
    --color-rentify-warning: #F59E0B;
    --color-rentify-error: #DC2626;
    --color-rentify-neutral: #94A3B8;

    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
  }
  ```

---

### 3. Bộ tiện ích dùng chung (Utilities & Formatters)
*File: `src/lib/utils.ts`*
- [ ] Cài đặt hàm tiện ích ghép class `cn(...)` sử dụng `clsx` và `tailwind-merge`.
- [ ] Xây dựng các hàm định dạng dữ liệu đồng bộ chuẩn định dạng với Mobile (`mobile/core-ui/src/main/java/com/rentify/app/core/ui/extension/FormatExt.kt`):
  - `formatVnd(amount)`: Định dạng tiền tệ phân cách dấu chấm theo chuẩn Việt Nam (ví dụ: `1.500.000 đ`).
  - `formatDate(isoString)`: Chuẩn hóa hiển thị ngày `dd/MM/yyyy`.
  - `formatDateTime(isoString)`: Chuẩn hóa hiển thị ngày giờ `dd/MM/yyyy HH:mm`.
  - `formatMonth(isoString)`: Chuẩn hóa hiển thị tháng năm `MM/yyyy`.

---

### 4. Chuẩn hóa Tầng Network & API Client
*File: `src/types/api.ts`*
- [ ] Định nghĩa các Type / Interface tương thích quy ước response wrapper của dự án (`pm/phase-2/discovery/api-conventions.md` §1):
  - `ApiResponse<T>`: Wrapper chứa `statusCode`, `code`, `data`, `message`.
  - `ApiError`: Cấu trúc lỗi chuẩn gồm `statusCode`, `code`, `message`, `errors`.
  - `PaginationMeta` & `PaginatedResponse<T>`: Hỗ trợ các thuộc tính phân trang offset `page`, `limit`, `total`, `totalPages`.

*File: `src/lib/axios.ts`*
- [ ] **Request Interceptor:** Tự động lấy `accessToken` từ `useAuthStore` gắn vào `Authorization: Bearer <token>`.
- [ ] **Response Interceptor (Thành công):** Unwrap vỏ JSON `{ statusCode, code, data }`, trả về trực tiếp `response.data.data`.
- [ ] **Response Interceptor (Xử lý 401 & Auto Refresh):**
  - Khi API trả về HTTP 401 `UNAUTHORIZED` (và không phải endpoint `/auth/login` hay `/auth/refresh`):
  - Tạm giữ các request trong hàng đợi (request queue).
  - Tự động gọi `POST /auth/refresh` (với `withCredentials: true` để browser gửi cookie refreshToken).
  - Cập nhật lại `accessToken` trong store và retry lại request gốc.
  - Nếu refresh thất bại: gọi `clearAuth()` trong store và điều hướng về trang `/login`.

*File: `src/lib/react-query.ts`*
- [ ] Khởi tạo `QueryClient` với cấu hình chuẩn:
  - `staleTime: 1000 * 60 * 5` (5 phút).
  - `retry: 1` cho queries thông thường.
  - Global error handler hiển thị toast thông báo lỗi (sử dụng Sonner toast).

---

### 5. Bộ thành phần giao diện cơ sở (Base UI & Feedback Components)
Đồng bộ các thành phần feedback như bên Mobile `core-ui`:
- [ ] **Feedback Components (`src/components/feedback/`):**
  - `LoadingSpinner`: Spinner tròn hiển thị khi đang tải nội dung con.
  - `LoadingOverlay`: Màn chắn trong suốt kèm spinner chặn thao tác khi đang submit/mutation.
  - `EmptyState`: Giao diện trạng thái rỗng (icon, tiêu đề, mô tả phụ, action button tùy chọn).
  - `ErrorState`: Giao diện trạng thái lỗi kèm nút "Thử lại" (`onRetry`).
- [ ] **Base UI Components (`src/components/ui/`):**
  - `Button`: Hỗ trợ các variant (`primary`, `outline`, `ghost`, `danger`), các size (`sm`, `md`, `lg`), trạng thái `loading` có spinner tích hợp chống double-click spam.
  - `Input`: Ô nhập liệu chuẩn Tailwind bo góc, hiển thị nhãn (label), icon, và thông báo lỗi validation.
  - `Card`: Khung bao ngoài chuẩn `bg-white`, border divider, bo góc `rounded-xl`.

---

### 6. Cấu hình i18n & Hook xác thực
- [ ] **`src/i18n/i18n.ts`:**
  - Khởi tạo `i18next.use(initReactI18next).init({...})`.
  - Khai báo namespaces `common`, `auth`.
  - Thiết lập ngôn ngữ mặc định `vi`, fallback `vi`, hỗ trợ chuyển đổi giữa `vi` và `en`.
- [ ] **`src/hooks/use-auth.ts`:**
  - Hook cung cấp các helper tiện ích: `user`, `role`, `isAuthenticated`, `login(tokens, user)`, `logout()`.

---

### 7. Hệ thống Layouts, Trang lỗi & Navigation Router
- [ ] **`src/app/layouts/auth-layout.tsx`:**
  - Layout 2 cột (hoặc card chính giữa) dành riêng cho các trang xác thực (Login, Register), nền thương hiệu Rentify (`bg-rentify-background`).
- [ ] **`src/app/layouts/dashboard-layout.tsx`:**
  - Khung giao diện chính cho người dùng đã đăng nhập:
    - **Sidebar:** Danh sách menu điều hướng thay đổi linh hoạt theo vai trò:
      - Role `landlord`: Quản lý toà nhà, phòng trọ, hợp đồng, hoá đơn, báo cáo sự cố.
      - Role `admin`: Quản lý tài khoản, kiểm duyệt chủ trọ, cài đặt hệ thống.
    - **Header/Navbar:** Hiển thị breadcrumbs, nút chuyển đổi ngôn ngữ (VI/EN), thông báo, User Profile dropdown và nút Đăng xuất.
    - **Main Content:** Vùng hiển thị nội dung các trang qua `<Outlet />`.
- [ ] **Trang lỗi hệ thống:**
  - `src/app/pages/forbidden-page.tsx` (Mã 403: Không có quyền truy cập + Nút quay về trang chủ).
  - `src/app/pages/not-found-page.tsx` (Mã 404: Không tìm thấy trang + Nút quay về).
- [ ] **Hệ thống Route Guards (`src/app/routes/`):**
  - `protected-route.tsx`: Kiểm tra `isAuthenticated`. Nếu chưa đăng nhập thì redirect về `/login`. Nếu có truyền prop `roles` mà user không khớp thì redirect về `/403`.
  - `public-route.tsx`: Dành cho các trang như `/login`, nếu user đã đăng nhập thì tự động redirect vào dashboard phù hợp.
  - `src/app/routes/index.tsx`: Định nghĩa cây `createBrowserRouter` hoàn chỉnh.
- [ ] **Tích hợp tầng cao nhất (`src/app/provider.tsx` & `src/App.tsx`):**
  - Bọc ứng dụng trong `QueryClientProvider`, `Toaster` (Sonner), `RouterProvider`.

---

### 8. Hoàn thiện Git Hooks (Husky & Lint-staged)
- [ ] Cập nhật file `.husky/pre-commit`:
  ```bash
  npx lint-staged
  npm run build
  ```
  *(Đảm bảo tự động chặn commit nếu code có lỗi TypeScript hoặc vi phạm quy tắc ESLint/Prettier).*

---

## 3. Tiêu chí nghiệm thu (Definition of Done - DoD)

1. **Build & Type-check thành công 100%:**
   - Chạy `npm run build` không phát sinh bất kỳ lỗi cú pháp hoặc cảnh báo TypeScript nào.
2. **Khởi chạy Dev Server mượt mà:**
   - Chạy `npm run dev` mở được ứng dụng tại `http://localhost:5173`.
   - Các trang `/login`, `/dashboard`, `/403`, `/404` hiển thị đúng layout và phong cách thiết kế Rentify.
3. **Đồng bộ Design System & Formatter:**
   - Bảng màu Rentify áp dụng đúng từ token `rentify-primary` (#1E6FD9).
   - Hàm `formatVnd(1500000)` trả về chính xác `"1.500.000 đ"` đồng nhất với Mobile.
4. **Kiểm thử Route Guard & Phân quyền:**
   - Chưa đăng nhập truy cập `/dashboard` -> Tự động chuyển hướng về `/login`.
   - Đăng nhập với role `tenant` (hoặc mock sai role) truy cập trang Admin -> Chuyển hướng sang `/403`.
   - Truy cập URL không tồn tại -> Hiển thị trang `/404`.
5. **Kiểm thử Interceptor & Xử lý lỗi:**
   - Request API tự động đính kèm `Authorization: Bearer <token>` nếu store có token.
   - Thử mock lỗi 401: Client kích hoạt luồng gọi làm mới token và tự động logout nếu refresh thất bại.
6. **Kiểm thử Pre-commit Hook:**
   - Thử cố tình tạo 1 lỗi TypeScript (ví dụ gán sai kiểu biến) rồi chạy `git commit`: Husky phải chặn không cho commit.
