# Identity — Sequence diagram theo API

Bản vẽ **thiết kế đích** cho 17 API của Identity (15 API đã build + refresh/logout đang làm), dùng để gắn vào `api-docs` sau khi review.

**Cơ sở:**
- Bảng API, dữ liệu ngoài và event đã chốt.
- Event dùng RabbitMQ, exchange `pbl6.events` (D54); catalogue ở `pm/phase-3/discovery/microservices-architecture.md` §5.7.
- Payload event dùng đúng tên field của entity/DTO.

## 0. Phần chung (không lặp lại trong từng diagram)

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant GW as API Gateway
    participant ID as Identity

    C->>GW: Request
    opt API cần đăng nhập
        GW->>GW: Verify JWT bằng JWKS đã cache
        alt JWT không hợp lệ / hết hạn
            GW-->>C: 401 UNAUTHORIZED
        end
    end
    GW->>ID: Chuyển tiếp + correlation-id (+ x-user-id, x-user-role, x-user-status lấy từ claim JWT nếu đã đăng nhập)
    ID->>ID: Validate body/query/param (DTO)
    alt Sai định dạng, thiếu field, body rỗng, giá trị ngoài enum
        ID-->>GW: 422 <mã lỗi validation>
    end
    opt API chỉ dành cho admin
        alt role khác admin
            ID-->>GW: 403 FORBIDDEN
        end
    end
    Note over ID: Xử lý nghiệp vụ, phần vẽ riêng cho từng API bên dưới
    ID-->>GW: Response {statusCode, code, data}
    GW-->>C: Response
```

Từng diagram bên dưới **bắt đầu từ lúc API Gateway chuyển request vào Identity**, sau khi đã qua các bước chung ở trên.
- **Không vẽ lại:** Client, verify JWT, validate DTO (422), kiểm tra role admin (403).
- **Chỉ vẽ:** các kiểm tra nghiệp vụ cần dữ liệu (DB hoặc service khác).

**Quy ước vẽ:**
- **Participant:** `API Gateway`, `Identity`, `Identity DB`, `RabbitMQ`, `Tenancy`, `Community`, `Payment`. Mỗi diagram chỉ có những participant thật sự tham gia.
- **Response:** mọi response, kể cả lỗi, vẽ `Identity → API Gateway`.
- **Publish event:** Identity ghi event vào outbox **cùng transaction** với thay đổi dữ liệu. Diagram không vẽ outbox relay, chỉ vẽ `Identity -) RabbitMQ` sau khi commit.
- **Mũi tên:** `-)` là bất đồng bộ (event), `->>` là đồng bộ (HTTP/DB).
- **Soft delete:** user bị xóa vẫn còn dòng trong bảng `users` với `is_deleted = true`. Mọi truy vấn "tìm user" chỉ lấy user **chưa bị xóa**, nên user đã xóa được xử lý như không tồn tại.
- **Khóa và xóa tài khoản:**
  - User bị **khóa** vẫn đăng nhập được. Access token mang claim `{sub, role, status}`, nên token cấp sau khi khóa có `status=locked`. API Gateway gắn header `x-user-status` cho mọi service. Tenancy và Community đọc header này để chặn chức năng theo `shared_user_flow.md` §1.3, không lưu bản sao `status` (`microservices-architecture.md` §6.2).
  - Event `user.locked` / `user.unlocked` chỉ dùng để Tenancy/Community đổi **dữ liệu của chính mình** (ẩn/hiện BĐS, tạm ngưng/khôi phục HĐ).
  - Token cấp trước khi khóa/mở khóa vẫn mang `status` cũ tới khi hết hạn (tối đa 15 phút).
  - User bị **xóa** thì không đăng nhập được.

---

## 1. Auth

### 1.1 `POST /auth/register` — Đăng ký

```mermaid
sequenceDiagram
    autonumber
    participant GW as API Gateway
    participant ID as Identity
    participant DB as Identity DB
    participant MQ as RabbitMQ
    participant TEN as Tenancy
    participant COM as Community

    GW->>ID: POST /auth/register {email, phone, password, name, role}
    ID->>DB: Kiểm tra email/phone đã được user chưa bị xóa sử dụng
    alt Trùng email hoặc phone
        ID-->>GW: 409 DUPLICATE_EMAIL / DUPLICATE_PHONE
    end
    ID->>DB: [Transaction] Insert users (password bcrypt, status=active)<br/>+ insert refresh_tokens (tokenHash)<br/>+ outbox user.registered
    ID->>ID: Ký access token RS256 {sub, role, status}
    ID-->>GW: 201 USER_REGISTERED {accessToken, refreshToken, user}
    ID-)MQ: user.registered {userId, name, email, phone, role, status}
    MQ-)TEN: Upsert user snapshot
    MQ-)COM: Tạo profile chat/notification
```

### 1.2 `POST /auth/login` — Đăng nhập

```mermaid
sequenceDiagram
    autonumber
    participant GW as API Gateway
    participant ID as Identity
    participant DB as Identity DB

    GW->>ID: POST /auth/login {identifier, password, rememberMe}
    ID->>DB: Tìm user chưa bị xóa theo email hoặc phone
    ID->>ID: bcrypt compare password
    alt Không tìm thấy hoặc sai mật khẩu
        ID-->>GW: 401 AUTH_LOGIN_INVALID_CREDENTIALS
    end
    Note over ID: status=locked vẫn được cấp token
    ID->>DB: Insert refresh_tokens (tokenHash, expiresAt 7 ngày nếu rememberMe, ngược lại 1 ngày)
    ID->>ID: Ký access token RS256 {sub, role, status} (15 phút)
    ID-->>GW: 200 SESSION_STARTED {accessToken, refreshToken, user}
```

### 1.3 `POST /auth/password-reset-requests` — Yêu cầu đặt lại mật khẩu

```mermaid
sequenceDiagram
    autonumber
    participant GW as API Gateway
    participant ID as Identity
    participant DB as Identity DB
    participant MQ as RabbitMQ
    participant COM as Community

    GW->>ID: POST /auth/password-reset-requests {email}
    ID->>DB: Tìm user chưa bị xóa theo email
    opt User tồn tại
        ID->>ID: Sinh token ngẫu nhiên + tokenHash (SHA-256), expiresAt = +15 phút
        ID->>DB: [Transaction] Insert password_reset_tokens (tokenHash, expiresAt)<br/>+ outbox user.password_reset_requested
    end
    ID-->>GW: 202 PASSWORD_RESET_REQUESTED {accepted: true}
    Note over ID: Luôn trả 202 giống nhau, không lộ email có tồn tại hay không
    ID-)MQ: user.password_reset_requested {userId, email, name, token, expiresAt}
    MQ-)COM: Gửi email chứa link đặt lại mật khẩu
```

### 1.4 `POST /auth/password-resets` — Đặt lại mật khẩu bằng token

```mermaid
sequenceDiagram
    autonumber
    participant GW as API Gateway
    participant ID as Identity
    participant DB as Identity DB

    GW->>ID: POST /auth/password-resets {token, newPassword}
    ID->>ID: Hash token (SHA-256)
    ID->>DB: Tìm password_reset_tokens theo tokenHash
    alt Token không tồn tại
        ID-->>GW: 422 INVALID_TOKEN
    else Token đã dùng / hết hạn
        ID-->>GW: 409 TOKEN_USED / TOKEN_EXPIRED
    end
    ID->>DB: [Transaction] Update users.password (bcrypt)<br/>+ đánh dấu token đã dùng<br/>+ revoke toàn bộ refresh_tokens của user
    ID-->>GW: 204
```

### 1.5 `POST /auth/refresh` — Làm mới access token *(P4-04, đang làm)*

```mermaid
sequenceDiagram
    autonumber
    participant GW as API Gateway
    participant ID as Identity
    participant DB as Identity DB

    GW->>ID: POST /auth/refresh {refreshToken}
    ID->>DB: Tìm refresh_tokens theo tokenHash
    alt Không tồn tại / hết hạn
        ID-->>GW: 401 INVALID_REFRESH_TOKEN
    else Token đã bị revoke (dùng lại token cũ)
        ID->>DB: Revoke toàn bộ token cùng family
        ID-->>GW: 401 TOKEN_REUSED
    end
    ID->>DB: Tìm user chưa bị xóa của token
    alt User đã bị xóa
        ID-->>GW: 401 INVALID_REFRESH_TOKEN
    end
    ID->>DB: [Transaction] Revoke token cũ + insert token mới (cùng family)
    ID->>ID: Ký access token RS256 mới {sub, role, status} (status đọc lại từ DB)
    ID-->>GW: 200 {accessToken, refreshToken}
```

### 1.6 `POST /auth/logout` — Đăng xuất *(P4-04, đang làm)*

```mermaid
sequenceDiagram
    autonumber
    participant GW as API Gateway
    participant ID as Identity
    participant DB as Identity DB

    GW->>ID: POST /auth/logout {refreshToken} + x-user-id
    ID->>DB: Revoke refresh token family của phiên hiện tại
    ID-->>GW: 204
```

### 1.7 `GET /.well-known/jwks.json` — Public key để verify JWT

```mermaid
sequenceDiagram
    autonumber
    participant GW as API Gateway
    participant ID as Identity

    Note over GW: Lúc khởi động, khi cache hết hạn<br/>hoặc gặp kid lạ
    GW->>ID: GET /.well-known/jwks.json
    ID-->>GW: 200 {keys: [{kty, n, e, use: sig, alg: RS256, kid}]}
    GW->>GW: Cache public key để verify JWT
```

### 1.8 `GET /identity/health` — Health check

```mermaid
sequenceDiagram
    autonumber
    participant GW as API Gateway
    participant ID as Identity

    GW->>ID: GET /identity/health
    ID-->>GW: 200 HEALTH_OK {status: ok}
```

---

## 2. Me (tài khoản của chính mình)

### 2.1 `GET /me` — Xem hồ sơ

```mermaid
sequenceDiagram
    autonumber
    participant GW as API Gateway
    participant ID as Identity
    participant DB as Identity DB

    GW->>ID: GET /me + x-user-id
    ID->>DB: Đọc users + landlord_profiles theo userId
    ID->>ID: Che accountNumber thành "**xxxxx"
    ID-->>GW: 200 CURRENT_USER_PROFILE_FETCHED {id, name, email, phone, role, status, payoutAccount}
```

### 2.2 `PATCH /me` — Cập nhật hồ sơ

```mermaid
sequenceDiagram
    autonumber
    participant GW as API Gateway
    participant ID as Identity
    participant DB as Identity DB
    participant MQ as RabbitMQ
    participant TEN as Tenancy
    participant COM as Community
    participant PAY as Payment

    GW->>ID: PATCH /me {name, phone, payoutAccount} + x-user-id, x-user-role
    alt payoutAccount khác null nhưng role không phải landlord
        ID-->>GW: 422 USER_UPDATE_PAYOUT_NOT_ALLOWED
    end
    ID->>DB: Kiểm tra phone trùng với user khác
    alt Trùng phone
        ID-->>GW: 409 DUPLICATE_PHONE
    end
    ID->>DB: [Transaction] Update users (name, phone)<br/>+ upsert landlord_profiles (bankCode, accountNumber, accountName)<br/>+ outbox user.updated (nếu name/phone đổi)<br/>+ outbox landlord.payout_account_updated (nếu payoutAccount đổi)
    ID-->>GW: 200 CURRENT_USER_PROFILE_UPDATED {id, name, phone, payoutAccount}
    opt name/phone đổi
        ID-)MQ: user.updated {userId, name, phone}
        MQ-)TEN: Cập nhật user snapshot
        MQ-)COM: Cập nhật user snapshot
    end
    opt payoutAccount đổi
        ID-)MQ: landlord.payout_account_updated {userId}
        MQ-)PAY: Xóa cache payout của landlord
    end
```

### 2.3 `PUT /me/password` — Đổi mật khẩu

```mermaid
sequenceDiagram
    autonumber
    participant GW as API Gateway
    participant ID as Identity
    participant DB as Identity DB

    GW->>ID: PUT /me/password {currentPassword, newPassword, confirmPassword} + x-user-id
    ID->>DB: Đọc users theo userId
    ID->>ID: bcrypt compare currentPassword
    alt Sai mật khẩu hiện tại
        ID-->>GW: 401 USER_CHANGE_PASSWORD_INVALID_CURRENT
    end
    ID->>DB: [Transaction] Update users.password (bcrypt)<br/>+ revoke toàn bộ refresh_tokens của user
    ID-->>GW: 204
```

---

## 3. Admin users

### 3.1 `GET /users` — Danh sách người dùng

```mermaid
sequenceDiagram
    autonumber
    participant GW as API Gateway
    participant ID as Identity
    participant DB as Identity DB

    GW->>ID: GET /users?pageNo&pageSize&sort&role&status&q
    ID->>DB: Query users chưa bị xóa (filter role/status, q theo name/email/phone, sort, offset)<br/>+ count tổng
    ID-->>GW: 200 USER_LIST_FETCHED [{id, name, email, phone, role, status}] + pagination
```

### 3.2 `GET /users/:userId` — Chi tiết người dùng

```mermaid
sequenceDiagram
    autonumber
    participant GW as API Gateway
    participant ID as Identity
    participant DB as Identity DB
    participant TEN as Tenancy

    GW->>ID: GET /users/{userId}
    ID->>DB: Đọc users + landlord_profiles theo userId
    alt Không tìm thấy
        ID-->>GW: 404 USER_NOT_FOUND
    end
    ID->>TEN: GET /internal/users/{userId}/stats (service token, timeout 3s)
    alt Tenancy trả kết quả
        TEN-->>ID: 200 {buildingCount, activeContractCount}
    else Tenancy lỗi / timeout
        ID->>ID: buildingCount = null, activeContractCount = null
    end
    ID-->>GW: 200 USER_DETAIL_FETCHED {..., lockReason, lockedAt, payoutAccount, buildingCount, activeContractCount}
```

### 3.3 `PATCH /users/:userId` — Admin sửa thông tin người dùng

```mermaid
sequenceDiagram
    autonumber
    participant GW as API Gateway
    participant ID as Identity
    participant DB as Identity DB
    participant MQ as RabbitMQ
    participant TEN as Tenancy
    participant COM as Community

    GW->>ID: PATCH /users/{userId} {name?, phone?}
    ID->>DB: Đọc user, kiểm tra phone trùng
    alt Không tìm thấy
        ID-->>GW: 404 USER_NOT_FOUND
    else Trùng phone
        ID-->>GW: 409 DUPLICATE_PHONE
    end
    ID->>DB: [Transaction] Update users (name, phone)<br/>+ outbox user.updated
    ID-->>GW: 200 USER_UPDATED {userId, name, phone, email, status}
    ID-)MQ: user.updated {userId, name, phone}
    MQ-)TEN: Cập nhật user snapshot
    MQ-)COM: Cập nhật user snapshot
```

### 3.4 `POST /users/:userId/lock` — Khóa tài khoản

```mermaid
sequenceDiagram
    autonumber
    participant GW as API Gateway
    participant ID as Identity
    participant DB as Identity DB
    participant MQ as RabbitMQ
    participant TEN as Tenancy
    participant COM as Community

    GW->>ID: POST /users/{userId}/lock {lockReason} + x-user-id (admin)
    alt Admin tự khóa chính mình
        ID-->>GW: 400 USER_LOCK_CANNOT_SELF
    end
    ID->>DB: Đọc user
    alt Không tìm thấy
        ID-->>GW: 404 USER_NOT_FOUND
    else Đã bị khóa
        ID-->>GW: 409 USER_LOCK_ALREADY_LOCKED
    end
    ID->>DB: [Transaction] Update users (status=locked, lockReason, lockedAt)<br/>+ outbox user.locked
    Note over ID: Không revoke refresh token:<br/>user bị khóa vẫn đăng nhập được
    ID-->>GW: 200 USER_ACCOUNT_LOCKED {userId, status, lockReason, lockedAt}
    ID-)MQ: user.locked {userId, role, status, lockReason, lockedAt}
    MQ-)TEN: Nếu role=landlord: ẩn BĐS khỏi tìm kiếm, tạm ngưng HĐ
    MQ-)COM: Xử lý dữ liệu liên quan (nếu có)
    Note over TEN,COM: Chặn thao tác của user bị khóa dựa vào header x-user-status,<br/>không dựa vào event này
```

### 3.5 `POST /users/:userId/unlock` — Mở khóa tài khoản

```mermaid
sequenceDiagram
    autonumber
    participant GW as API Gateway
    participant ID as Identity
    participant DB as Identity DB
    participant MQ as RabbitMQ
    participant TEN as Tenancy
    participant COM as Community

    GW->>ID: POST /users/{userId}/unlock
    ID->>DB: Đọc user
    alt Không tìm thấy
        ID-->>GW: 404 USER_NOT_FOUND
    else Chưa bị khóa
        ID-->>GW: 409 USER_UNLOCK_NOT_LOCKED
    end
    ID->>DB: [Transaction] Update users (status=active, lockReason=null, lockedAt=null)<br/>+ outbox user.unlocked
    ID-->>GW: 200 USER_ACCOUNT_UNLOCKED {userId, status, lockedAt: null}
    ID-)MQ: user.unlocked {userId, status}
    MQ-)TEN: Nếu role=landlord: hiện lại BĐS, khôi phục HĐ đang tạm ngưng
    MQ-)COM: Xử lý dữ liệu liên quan (nếu có)
```

### 3.6 `DELETE /users/:userId` — Xóa mềm tài khoản

```mermaid
sequenceDiagram
    autonumber
    participant GW as API Gateway
    participant ID as Identity
    participant DB as Identity DB
    participant MQ as RabbitMQ
    participant TEN as Tenancy
    participant COM as Community

    GW->>ID: DELETE /users/{userId} + x-user-id (admin)
    alt Admin tự xóa chính mình
        ID-->>GW: 400 USER_DELETE_CANNOT_SELF
    end
    ID->>DB: Đọc user
    alt Không tìm thấy
        ID-->>GW: 404 USER_NOT_FOUND
    else Đã bị xóa
        ID-->>GW: 409 USER_DELETE_ALREADY_DELETED
    end
    ID->>TEN: GET /internal/users/{userId}/stats (service token, timeout 3s)
    alt Tenancy lỗi / timeout (fail-closed)
        ID-->>GW: 503 SERVICE_UNAVAILABLE
    end
    TEN-->>ID: 200 {buildingCount, activeContractCount}
    alt activeContractCount > 0
        ID-->>GW: 409 USER_DELETE_HAS_ACTIVE_CONTRACT
    end
    ID->>DB: [Transaction] Soft delete users (is_deleted=true) + landlord_profiles<br/>+ revoke toàn bộ refresh_tokens<br/>+ outbox user.deleted
    ID-->>GW: 204
    ID-)MQ: user.deleted {userId, role}
    MQ-)TEN: Ẩn user, không cho gán vào HĐ mới
    MQ-)COM: Ngắt socket, xóa push devices
```

---

## 4. Chỗ diagram lệch so với code hiện tại

Diagram vẽ theo thiết kế đã chốt. Những điểm dưới đây cần sửa code để khớp.

| # | Chỗ lệch | Vị trí | Cần làm |
|---|----------|--------|---------|
| 1 | ✅ Đã sửa: 7 event được ghi outbox cùng transaction (register, reset request, update me/admin, lock, unlock, delete). Tạm đặt `RABBITMQ_PUBLISH_MANDATORY=false` vì chưa có consumer bind `user.*`; bật lại khi Tenancy/Community subscribe | Các command handler trong `Identity-Service/src/modules/{auth,users}` | — |
| 2 | ✅ Đã sửa: lock không còn revoke refresh token | `auth-revoke-tokens-on-user-events.event.handler.ts` | — |
| 3 | ✅ Đã sửa: user bị khóa được yêu cầu reset mật khẩu | `password-reset-request.command.handler.ts` | — |
| 4 | ✅ Đã sửa: thay TODO bằng event `user.password_reset_requested` | `password-reset-request.command.handler.ts` | Community cần consumer gửi email |
| 5 | `buildingCount`, `activeContractCount` hard-code 0. Xóa user chưa kiểm tra HĐ hiệu lực | `user-get-detail-admin.query.handler.ts`, `user-delete.command.handler.ts` | Gọi `GET /internal/users/{userId}/stats` của Tenancy (Tenancy cần build endpoint này) |
| 6 | Access token chỉ có `{sub, role}`, Gateway chưa gắn `x-user-status` | `Identity-Service/src/modules/auth` (ký token), `api-gateway` (forward header) | Thêm claim `status`, Gateway gắn header `x-user-status` |
| 7 | Delete chưa có mã `409 USER_DELETE_HAS_ACTIVE_CONTRACT`, `503 SERVICE_UNAVAILABLE` | `user-delete.command.handler.ts`, `api-docs/src/paths/users/user-by-id.yaml` | Bổ sung mã lỗi vào code và api-docs |
