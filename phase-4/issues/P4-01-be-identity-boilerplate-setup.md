# P4-01 — Setup boilerplate, Base Entity & Conventions cho Identity Service

**Status:** 🟡 Open  
**Assignee:** BE Dev  
**Stakeholders / Reviewers:** BE Lead, PM  
**Created:** 2026-10-09  
**Due date:** 2026-10-10  
**Priority:** 🔴 High / Blocker (Nền móng cho toàn bộ các module sau)  

**Input:**
- Boilerplate hiện có: `boilerplate/backend/`
- `pm/phase-2/discovery/api-conventions.md` (§1 Response Wrapper Format, §10 Error Handling)
- `pm/phase-1/discovery/database-design.md` (§2.0 Base Entity)
- `pm/phase-3/discovery/decisions.md` (D52 port 3001)

**Deliverables:**
- Cập nhật `package.json` với các package xác thực & bảo mật.
- Cập nhật `AbstractEntity` (TypeORM) và `BaseEntity` (Domain) có trường `isDeleted` và kiểu `timestamptz`.
- Viết `TransformInterceptor` bọc success response `{ statusCode, code, data }`.
- Cập nhật `LoggingExceptionFilter` chỉ trả về `{ statusCode, code }`.
- Cấu hình port mặc định `3001` và middleware `cookieParser()`.

---

## 1. Chi tiết công việc (Checklist)

### 1. Cài đặt Dependencies cần thiết
Thêm vào `boilerplate/backend/package.json`:
- [ ] `@nestjs/jwt`, `@nestjs/passport`, `passport`, `passport-jwt`, `@types/passport-jwt`
- [ ] `bcrypt`, `@types/bcrypt` (hoặc `argon2`)
- [ ] `cookie-parser`, `@types/cookie-parser`
- [ ] Chạy `npm install` thành công, kiểm tra không bị conflict dependency.

### 2. Chuẩn hóa Base Entity
- [ ] `src/shared/infra/typeorm/persistence/type-orm.abstract.entity.ts`:
  - Đổi `createdAt`, `updatedAt` sang `type: 'timestamptz'`.
  - Thêm trường `isDeleted`:
    ```typescript
    @Column({ name: 'is_deleted', type: 'boolean', default: false })
    isDeleted: boolean;
    ```
- [ ] `src/shared/domain/entities/base.entity.ts`:
  - Thêm `readonly isDeleted: boolean = false` vào constructor.

### 3. Chuẩn hóa Response Wrapper & Exception Filter
- [ ] Tạo `src/shared/interceptors/transform-response.interceptor.ts`:
  - Tự động bọc kết quả từ Controller vào:
    ```json
    {
      "statusCode": 200,
      "code": "SUCCESS",
      "data": { ... }
    }
    ```
  - Cho phép Controller truyền custom `code` (ví dụ `USER_REGISTERED`, `LOGIN_SUCCESS`) qua Decorator hoặc Meta.
- [ ] Cập nhật `src/filter/error-handling-exception-filter.ts`:
  - Khớp với `api-conventions.md` §1: Response lỗi **chỉ trả** `{ "statusCode": <number>, "code": "<STRING>" }`.
  - Không để lộ `message`, `details`, stack trace ra response trả về client.

### 4. Cấu hình Port, Middleware & Health Check trong `main.ts`
- [ ] Đổi port chạy sang `3001` trong `api-config.service.ts` / `.env.example`.
- [ ] Thêm `app.use(cookieParser())` trong `main.ts`.
- [ ] Thêm `HealthController` với endpoint `GET /health` để test trạng thái service.

---

## 2. Tiêu chí nghiệm thu (Definition of Done)
1. Ứng dụng khởi động bình thường với `npm run start:dev`, lắng nghe tại cổng `http://localhost:3001`.
2. Truy cập Swagger UI tại `http://localhost:3001/swagger`.
3. Gọi thử endpoint `GET /health`:
   - Kết quả thành công trả về đúng bọc `{ statusCode: 200, code: "HEALTH_OK", data: { status: "ok" } }` (hoặc `{ status: "ok" }`).
   - Gọi endpoint không tồn tại trả về `{ statusCode: 404, code: "NOT_FOUND" }`.
