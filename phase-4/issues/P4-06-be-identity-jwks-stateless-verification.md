# P4-06 — Cấu hình RS256 JWT & Expose JWKS Endpoint cho Microservices

**Status:** 🟡 Open  
**Assignee:** BE Dev / BE Lead  
**Stakeholders / Reviewers:** PM, Toàn bộ BE team  
**Created:** 2026-10-09  
**Due date:** 2026-10-15  
**Priority:** 🟡 Medium (Quan trọng để phục vụ kiến trúc Microservices SOA)  

**Input:**
- P4-03, P4-04
- `pm/phase-3/discovery/decisions.md` (D55 API Gateway, D58 Statelessness & No shared libs)
- `pm/phase-3/discovery/microservices-architecture.md` (§5.4.1 JWKS + RS256)
- Chuẩn IETF RFC 7517 (JSON Web Key Set - JWKS)

**Deliverables:**
- Cặp khóa RSA (Private Key & Public Key, độ dài 2048-bit).
- Cấu hình ký token trong `identity-service` bằng thuật toán bất đối xứng `RS256` (dùng Private Key).
- Endpoint công khai: `GET /api/v1/.well-known/jwks.json`.
- Tài liệu/Code snippet mẫu hướng dẫn các service khác (`api-gateway`, `tenancy-service`) verify Access Token bằng Public Key/JWKS.

---

## 1. Chi tiết kiến trúc & Nghiệp vụ

### 1. Tại sao cần RS256 và JWKS?
- Theo nguyên lý SOA số 6 (Service Statelessness) và quyết định **D55 / D58**:
  - `identity-service` là nơi DUY NHẤT phát hành và ký JWT token.
  - Các service còn lại (`api-gateway`, `tenancy-service`, `payment-service`, `community-service`) **tuyệt đối không gọi HTTP sang identity-service** trên mỗi request chỉ để hỏi "token này hợp lệ không" (tránh tạo network hop làm nghẽn hệ thống).
  - Thay vào đó, các service tải Public Key từ `/.well-known/jwks.json` của `identity-service` về và cache lại (ví dụ trong 5-10 phút). Khi có request đến, chúng tự dùng Public Key để verify chữ ký của JWT cục bộ.

### 2. Tạo cặp khóa RSA
- Tạo cặp Private Key (`private.key` hoặc `private.pem`) và Public Key (`public.key` hoặc `public.pem`):
  - Khuyến khích cấu hình qua biến môi trường (Base64 encoded string) để tiện triển khai Docker:
    `JWT_PRIVATE_KEY` và `JWT_PUBLIC_KEY`.

### 3. Expose endpoint JWKS
- **Method & Path:** `GET /api/v1/.well-known/jwks.json`
- **Quyền:** `public` (không cần token)
- **Response format (chuẩn RFC 7517):**
  ```json
  {
    "keys": [
      {
        "kty": "RSA",
        "use": "sig",
        "alg": "RS256",
        "kid": "pbl6-identity-key-v1",
        "n": "...", // Modulus của RSA Public Key (Base64URL)
        "e": "AQAB"  // Exponent
      }
    ]
  }
  ```

---

## 2. Tiêu chí nghiệm thu (Definition of Done)
1. Token được ký bởi `identity-service` có header `alg: "RS256"` và `kid: "pbl6-identity-key-v1"`.
2. Gọi `GET /api/v1/.well-known/jwks.json` trả về đúng định dạng JWKS.
3. Kiểm thử với một service khác (hoặc script test độc lập): Lấy JWKS từ endpoint trên, dùng thư viện `jwks-rsa` hoặc `jose` để verify token phát hành từ `identity-service` thành công 100% mà không cần kết nối DB hay shared secret key.
