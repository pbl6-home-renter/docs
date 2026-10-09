# P4-07 — Setup Frontend Boilerplate (React + Vite + TypeScript) cho repo `pbl6-web`

**Status:** 🟡 Open  
**Assignee:** FE Dev / FE Lead  
**Stakeholders / Reviewers:** PM, BE Lead  
**Created:** 2026-10-09  
**Due date:** 2026-10-13  
**Priority:** 🔴 High / Blocker (Nền móng vững chắc cho toàn bộ ứng dụng Web)  

**Input:**
- Tech stack định hướng: React (TypeScript) + Vite
- `pm/phase-2/discovery/api-conventions.md` (§1 Response Wrapper, §4 Token Cookies, §10 Error Handling)
- `pm/phase-2/discovery/api-spec.md` (§2 Auth, §3 User)
- `pm/phase-2/discovery/Rentify_UI_Screen_Outline_v0.1.md` (Danh sách màn hình Web)
- Quyết định D13 (Web hỗ trợ Landlord Ops Console & Admin)

**Deliverables:**
- Repository `pbl6-web` khởi tạo hoàn chỉnh với React + Vite + TypeScript.
- Cấu trúc thư mục chuẩn Modular / Feature-based Clean Architecture.
- Cấu hình Tailwind CSS (chưa chốt bộ component cố định, linh hoạt tự build base UI hoặc custom template sau).
- **Phân quyền UI linh hoạt:** Component `<Can>` và hook `useCan()` để ẩn/hiện thành phần UI linh hoạt theo Role.
- **Base Query & Mutation wrapper:** Chuẩn hóa TanStack Query (Query Key Factory, auto error toast, unwrap response).
- **Hệ thống Core Hooks:** `useDebounce`, `useDisclosure` (dialog/drawer), `useAuth`.
- **Hệ sinh thái i18n Type-safe:** Autocomplete translation keys, kèm script tự động audit key thiếu / thừa.
- **Git Hooks:** Cấu hình Husky + lint-staged (tự động format, lint, type-check trước khi commit).
- **Khung giao diện & Trang lỗi:** `DashboardLayout` dùng chung đa role, `AuthLayout`, trang `403 Forbidden` và `404 Not Found`.
- **Axios Client chuẩn PBL6:** Tự động gắn Bearer Token, gửi HttpOnly Cookie `withCredentials`, auto refresh token khi 401.

---

## 1. Công nghệ đề xuất (Tech Stack Khuyến nghị)

| Mục | Công nghệ | Vai trò & Lý do chọn |
|---|---|---|
| **Build Tool & Framework** | **Vite + React (TypeScript)** | Khởi động siêu nhanh, HMR tức thì, strict type-safe |
| **Styling** | **Tailwind CSS (Core)** | Linh hoạt tối đa, dễ tuỳ biến, không phụ thuộc cứng vào bất kỳ UI framework nào |
| **Component UI Kit** | *(Chưa cố định)* | Base component (`Button`, `Input`, `Card`, `Modal`) tự build hoặc lấy template về custom |
| **Routing** | **React Router DOM (v6/v7)** | Nested routes, Layouts, Route Guards (Protected / Public) |
| **Server State & Cache** | **TanStack Query (React Query) v5** | Caching, deduplication, auto refetch, quản lý trạng thái query/mutation chuẩn |
| **Client State** | **Zustand** | Quản lý auth state, token, user profile siêu nhẹ |
| **HTTP Client** | **Axios** | Interceptors xử lý HttpOnly cookie, unwrap response wrapper, auto refresh token khi 401 |
| **Forms & Validation** | **React Hook Form + Zod** | Form handling hiệu năng cao, validate schema chuẩn |
| **Đa ngôn ngữ (i18n)** | **i18next + react-i18next** | Hỗ trợ Type-safe key, kèm tool audit phát hiện key thừa / thiếu trong code |
| **Git Automation** | **Husky + lint-staged** | Đảm bảo code sạch (pre-commit: check lint, format, `tsc --noEmit`) |
| **Icons & Toast** | *(Thống nhất sau)* | Sẽ cài bổ sung sau khi chốt đồng bộ với team Mobile |

---

## 2. Cấu trúc thư mục chuẩn (Feature-based Directory Structure)

Khởi tạo cấu trúc source code trong `pbl6-web/src/` như sau:

```text
pbl6-web/
├── .husky/                       # Git hook pre-commit
├── public/
├── src/
│   ├── app/                      # Cấu hình tầng ứng dụng cao nhất
│   │   ├── routes/               # Routing & Navigation
│   │   │   ├── index.tsx         # Định nghĩa toàn bộ cây Route
│   │   │   ├── protected-route.tsx # Chặn truy cập nếu chưa login hoặc sai role
│   │   │   └── public-route.tsx  # Chặn nếu đã login (redirect về dashboard)
│   │   ├── layouts/              # Khung giao diện dùng chung
│   │   │   ├── auth-layout.tsx   # Layout màn hình Auth (Login, Register)
│   │   │   └── dashboard-layout.tsx # Layout chung (Sidebar động theo role + Header + Content)
│   │   ├── pages/                # Các trang tĩnh / hệ thống
│   │   │   ├── not-found-page.tsx # Trang 404
│   │   │   └── forbidden-page.tsx # Trang 403
│   │   └── providers.tsx         # Gom các Provider (QueryClient, Theme, i18n)
│   │
│   ├── components/               # UI components dùng chung toàn dự án
│   │   ├── auth/                 # Component bảo vệ & phân quyền UI
│   │   │   └── can.tsx           # <Can roles={['landlord']}>...</Can>
│   │   ├── ui/                   # Base components tự build (button, input, modal, card...)
│   │   ├── feedback/             # LoadingSpinner, EmptyState, ErrorBoundary
│   │   └── navigation/           # Sidebar, Navbar, UserDropdown
│   │
│   ├── features/                 # Chia module theo Domain Nghiệp vụ
│   │   ├── auth/                 # Module Xác thực (Login, Register)
│   │   │   ├── api/              # auth.api.ts (useLogin, useRegister, useGetMe)
│   │   │   ├── components/       # Form UI: login-form.tsx, register-form.tsx
│   │   │   ├── types/            # auth.types.ts
│   │   │   └── pages/            # login-page.tsx, register-page.tsx
│   │   ├── dashboard/            # Trang tổng quan
│   │   ├── buildings/            # Module Toà nhà (chuẩn bị sau)
│   │   ├── rooms/                # Module Phòng trọ
│   │   ├── contracts/            # Module Hợp đồng
│   │   └── invoices/             # Module Hoá đơn điện nước
│   │
│   ├── hooks/                    # Global Custom Hooks
│   │   ├── use-auth.ts           # Hook tiện ích lấy user, status, token
│   │   ├── use-can.ts            # Hook kiểm tra role/permission
│   │   ├── use-debounce.ts       # Hook debounce search input
│   │   └── use-disclosure.ts     # Hook điều khiển trạng thái mở/đóng Modal, Drawer
│   │
│   ├── i18n/                     # Cấu hình đa ngôn ngữ Type-safe
│   │   ├── locales/
│   │   │   ├── vi/               # Bản dịch tiếng Việt (auth.json, common.json...)
│   │   │   └── en/               # Bản dịch tiếng Anh
│   │   ├── i18n.ts               # Setup i18next instance
│   │   └── i18n.d.ts             # Type definition augmentation cho autocomplete
│   │
│   ├── lib/                      # Cấu hình thư viện bên thứ 3
│   │   ├── axios.ts              # Axios instance cấu hình interceptors chuẩn PBL6
│   │   ├── react-query.ts        # QueryClient, Base Query helper & QueryKey Factory
│   │   └── utils.ts              # Hàm tiện ích (hàm `cn` ghép class Tailwind)
│   │
│   ├── stores/                   # Global state với Zustand
│   │   └── auth-store.ts         # Lưu user info, accessToken, trạng thái isAuthenticated
│   │
│   ├── types/                    # Common Types toàn dự án
│   │   ├── api.ts                # ApiResponse<T>, ApiError, Pagination
│   │   └── user.ts               # User, Role ('landlord' | 'tenant' | 'admin'), Status
│   │
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css                 # Tailwind directives
│
├── .env.example                  # VITE_API_URL=http://localhost:3001/api/v1
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

---

## 3. Chi tiết kiến trúc kỹ thuật & Checklist

### 1. Phân quyền UI với Component `<Can>` và hook `useCan()`
Cho phép hiển thị/ẩn các button, menu item, card tùy theo Role của user:

*File: `src/components/auth/can.tsx`*
```tsx
import { ReactNode } from 'react';
import { useAuthStore } from '@/stores/auth-store';
import { Role } from '@/types/user';

interface CanProps {
  roles?: Role[];
  fallback?: ReactNode;
  children: ReactNode;
}

export const Can = ({ roles, fallback = null, children }: CanProps) => {
  const user = useAuthStore((state) => state.user);

  if (!user) return <>{fallback}</>;
  if (roles && !roles.includes(user.role)) return <>{fallback}</>;

  return <>{children}</>;
};
```
*Cách dùng:*
```tsx
<Can roles={['landlord', 'admin']}>
  <button>Thêm tòa nhà mới</button>
</Can>
```

*File: `src/hooks/use-can.ts`:*
```typescript
import { useAuthStore } from '@/stores/auth-store';
import { Role } from '@/types/user';

export const useCan = () => {
  const user = useAuthStore((state) => state.user);
  const hasRole = (...roles: Role[]) => !!user && roles.includes(user.role);
  return { hasRole, role: user?.role };
};
```

---

### 2. Base Query & Base Mutation Wrapper (TanStack Query)
Tránh viết lặp logic toast thông báo, parse lỗi và quản lý query key lộn xộn.

*File: `src/lib/react-query.ts`:*
- [ ] **Query Key Factory:** Gom các key truy vấn có cấu trúc để dễ invalidate:
  ```typescript
  export const queryKeys = {
    auth: {
      me: ['auth', 'me'] as const,
    },
    buildings: {
      all: ['buildings'] as const,
      detail: (id: string) => ['buildings', id] as const,
    },
  };
  ```
- [ ] **Base Mutation:** Viết wrapper cho `useMutation` tự động:
  - Bắt mã lỗi từ `api-conventions.md` (ví dụ `VALIDATION FAILED`, `INVALID_CREDENTIALS`).
  - Hỗ trợ custom onSuccess callback và tự động invalidate các query liên quan.

---

### 3. Hệ sinh thái Đa ngôn ngữ (i18n) Type-safe & Audit thừa/thiếu
Giải quyết triệt để vấn đề: gõ sai key không biết, không biết key nào đã dịch hay chưa dịch.

#### A. Type-safe Key Autocomplete
*File: `src/i18n/i18n.d.ts`:*
```typescript
import 'i18next';
import viCommon from './locales/vi/common.json';
import viAuth from './locales/vi/auth.json';

declare module 'i18next' {
  interface CustomTypeOptions {
    defaultNS: 'common';
    resources: {
      common: typeof viCommon;
      auth: typeof viAuth;
    };
  }
}
```
👉 Khi gõ `t('auth:login.title')`, IDE sẽ tự động gợi ý chính xác key, nếu gõ sai sẽ báo lỗi TypeScript ngay lúc code!

#### B. Kiểm tra key thiếu / dư (Translation Audit)
Cài đặt công cụ kiểm tra `i18n-unused` hoặc viết script kiểm tra:
```bash
npm install -D i18n-unused
```
Thêm script vào `package.json`:
```json
"scripts": {
  "i18n:check": "i18n-unused"
}
```
👉 Chạy `npm run i18n:check` sẽ quét toàn bộ code trong `src/` và báo cáo rõ:
- Key nào có trong JSON nhưng code **không còn dùng** (thừa → dọn rác).
- Key nào được gọi trong code nhưng file tiếng Anh/tiếng Việt **chưa có** (thiếu → cần dịch).

---

### 4. Global Custom Hooks cốt lõi
*File: `src/hooks/use-debounce.ts`*
- Trì hoãn xử lý khi gõ search box để tránh spam API:
  ```typescript
  export function useDebounce<T>(value: T, delay: number = 300): T { ... }
  ```
*File: `src/hooks/use-disclosure.ts`*
- Quản lý trạng thái mở/đóng Modal, Drawer, Popup gọn gàng:
  ```typescript
  export const useDisclosure = (initialState = false) => {
    const [isOpen, setIsOpen] = useState(initialState);
    const open = () => setIsOpen(true);
    const close = () => setIsOpen(false);
    const toggle = () => setIsOpen((prev) => !prev);
    return { isOpen, open, close, toggle };
  };
  ```

---

### 5. Cấu hình Git Hook với Husky & Lint-staged
Đảm bảo không ai có thể push code bẩn hoặc lỗi type lên GitHub.

- [ ] Cài đặt:
  ```bash
  npm install -D husky lint-staged
  npx husky init
  ```
- [ ] Cấu hình file `package.json`:
  ```json
  "lint-staged": {
    "src/**/*.{ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ]
  }
  ```
- [ ] Cấu hình `.husky/pre-commit`:
  ```bash
  npx lint-staged
  npm run build --noEmit # Kiểm tra toàn bộ type TypeScript
  ```

---

### 6. Cấu hình Axios Client chuẩn hóa theo Quy ước API PBL6
*File: `src/lib/axios.ts`*
- [ ] Cấu hình Base Instance:
  ```typescript
  export const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:3001/api/v1',
    withCredentials: true, // BẮT BUỘC: để trình duyệt tự gửi Refresh Token Cookie
    headers: {
      'Content-Type': 'application/json',
    },
  });
  ```
- [ ] **Request Interceptor:** Tự động lấy `accessToken` từ `useAuthStore` gắn vào Header `Authorization: Bearer <token>`.
- [ ] **Response Interceptor:**
  - *Thành công:* Tự động bóc tách vỏ JSON wrapper `{ statusCode, code, data }` để trả về trực tiếp `response.data.data`.
  - *Bắt lỗi 401 UNAUTHORIZED:* Tự động gọi `POST /auth/refresh` để xin token mới và retry request gốc. Nếu refresh thất bại thì logout và redirect về `/login`.

---

### 7. Hệ thống Layouts & Trang lỗi hệ thống (403, 404)
- [ ] **DashboardLayout (`src/app/layouts/dashboard-layout.tsx`):**
  - Layout chung có Sidebar & Header.
  - Sử dụng `<Can>` hoặc cấu hình menu động: Landlord nhìn thấy menu quản lý nhà trọ, Admin nhìn thấy menu duyệt tài khoản.
- [ ] **AuthLayout (`src/app/layouts/auth-layout.tsx`):**
  - Layout 2 cột cho Login / Register.
- [ ] **Trang 403 Forbidden (`src/app/pages/forbidden-page.tsx`):**
  - Giao diện báo lỗi "Bạn không có quyền truy cập trang này", nút bấm "Quay lại trang chính".
- [ ] **Trang 404 Not Found (`src/app/pages/not-found-page.tsx`):**
  - Bắt mọi route không tồn tại (`path="*"`) hiển thị trang 404 sinh động.

---

## 4. Tiêu chí nghiệm thu (Definition of Done - DoD)

1. **Khởi chạy & Build sạch:**
   - Chạy `npm run dev` mở được trang web trên `localhost:5173`.
   - Chạy `npm run build` không có bất kỳ lỗi cú pháp hoặc TypeScript nào.
2. **Kiểm thử Git Hook:**
   - Thử sửa một file TypeScript sai cú pháp rồi gõ `git commit`, Husky phải chặn lại và không cho commit.
3. **Kiểm thử i18n:**
   - Chạy `npm run i18n:check` báo cáo chính xác trạng thái các key dịch.
   - Thử gõ `t('auth:non_existing_key')` thì TypeScript gạch đỏ báo lỗi ngay lập tức.
4. **Kiểm thử Component `<Can>`:**
   - Đăng nhập tài khoản role `tenant` -> không nhìn thấy các nút bọc trong `<Can roles={['landlord']}>`.
   - Đăng nhập role `landlord` -> hiển thị đầy đủ các nút quyền chủ nhà.
5. **Kiểm thử Trang lỗi:**
   - Truy cập URL linh tinh (vd: `/abcxyz`) -> hiển thị trang **404 Not Found**.
   - User không đúng role truy cập route admin -> chuyển hướng sang trang **403 Forbidden**.
6. **Thông luồng E2E với Backend Identity Service (port 3001):**
   - Đăng ký và đăng nhập thành công, lưu session, F5 không bị mất đăng nhập, logout xóa cookie sạch sẽ.
