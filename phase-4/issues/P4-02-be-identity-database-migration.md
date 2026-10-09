# P4-02 — Thiết kế TypeORM Entities & Migration CSDL `identity_db`

**Status:** 🟡 Open  
**Assignee:** BE Dev  
**Stakeholders / Reviewers:** BE Lead, PM  
**Created:** 2026-10-09  
**Due date:** 2026-10-11  
**Priority:** 🔴 High / Blocker (Cần thiết trước khi viết nghiệp vụ Auth)  

**Input:**
- `pm/phase-1/discovery/database-design.md` (§2.0 Base Entity, §2.1 User, §2.3 LandlordProfile)
- `pm/phase-3/discovery/database-per-service.md` (§1 Bốn database, §2.2 Bảng mới `refresh_tokens`)
- `pm/phase-3/discovery/decisions.md` (D53: Database-per-service, role riêng cho `identity_db`)

**Deliverables:**
- Cấu hình kết nối Data Source tới database `identity_db`.
- TypeORM Entities cho 3 bảng: `UserTypeormEntity`, `LandlordProfileTypeormEntity`, `RefreshTokenTypeormEntity`.
- File Migration TypeORM tạo 3 bảng chuẩn.
- Migration chạy thành công và tạo đúng schema trong PostgreSQL.

---

## 1. Chi tiết bảng dữ liệu cần tạo

### 1. Bảng `users` (Entity 2.1)
* `id`: uuid, PK, default `gen_random_uuid()`
* `phone`: varchar(12), UNIQUE, NOT NULL (Regex: `^0[0-9]{9}$` hoặc `^\+84[0-9]{9}$`)
* `email`: varchar(254), UNIQUE, NOT NULL
* `password`: varchar(255), NOT NULL (lưu hash bcrypt)
* `name`: varchar(254), NOT NULL
* `role`: enum (`landlord`, `tenant`, `admin`), NOT NULL
* `status`: enum (`active`, `locked`), NOT NULL, default `active`
* `lock_reason`: varchar(500), nullable
* `locked_at`: timestamptz, nullable
* `created_at`: timestamptz, NOT NULL, default `now()`
* `updated_at`: timestamptz, NOT NULL, default `now()`
* `is_deleted`: boolean, NOT NULL, default `false`

### 2. Bảng `landlord_profiles` (Entity 2.3)
* `user_id`: uuid, PK & FK trỏ `users(id)`, ON DELETE CASCADE
* `bank_code`: varchar(20), nullable (mã VietQR)
* `account_number`: varchar(20), nullable
* `account_name`: varchar(254), nullable (tên chủ tài khoản không dấu)
* `created_at`: timestamptz, default `now()`
* `updated_at`: timestamptz, default `now()`
* `is_deleted`: boolean, default `false`

### 3. Bảng `refresh_tokens` (Do D53/D55 sinh ra)
* `id`: uuid, PK, default `gen_random_uuid()`
* `user_id`: uuid, NOT NULL, FK trỏ `users(id)`, ON DELETE CASCADE
* `token_hash`: varchar(255), NOT NULL (chỉ lưu hash của refresh token)
* `family_id`: uuid, NOT NULL (dùng để gom nhóm các token trong cùng một chuỗi xoay vòng — Token Rotation Family)
* `expires_at`: timestamptz, NOT NULL
* `revoked_at`: timestamptz, nullable (nếu khác null nghĩa là token đã bị thu hồi)
* `created_at`: timestamptz, default `now()`

---

## 2. Chi tiết công việc (Checklist)

- [ ] Cấu hình biến môi trường kết nối PostgreSQL tới DB `identity_db` (trong `docker-compose.yml` đảm bảo script init tạo DB `identity_db`).
- [ ] Tạo các TypeORM Entity trong thư mục persistence tương ứng (`src/modules/users/infra/persistence/`, `src/modules/auth/infra/persistence/`).
- [ ] Chạy lệnh `npm run migration:generate -- name=InitialIdentitySchema`.
- [ ] Kiểm tra file migration sinh ra trong thư mục migrations: kiểu dữ liệu đúng `timestamptz`, enum khớp `database-design.md`, ràng buộc UNIQUE cho `email` và `phone`.
- [ ] Chạy lệnh `npm run migration:run` để áp dụng vào DB.

---

## 3. Tiêu chí nghiệm thu (Definition of Done)
1. Kết nối vào PostgreSQL (DBeaver / pgAdmin / psql) thấy database `identity_db` có 3 bảng: `users`, `landlord_profiles`, `refresh_tokens`.
2. Bảng `users` có các index UNIQUE trên `email` và `phone`.
3. Lệnh `npm run migration:revert` và `npm run migration:run` hoạt động mượt mà không có lỗi cú pháp.
