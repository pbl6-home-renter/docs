# P4-15 — Cấu hình nền tảng Apidog và tự động hóa authentication flow

**Trạng thái:** 🟡 Open  
**Người phụ trách:** BE/API Lead phối hợp PM  
**Người review:** PM, FE Lead, các member phụ trách service  
**Ước lượng:** 8 points · 18–24 giờ  
**Độ ưu tiên:** High / Blocker cho việc tích hợp API giữa các member

## Bối cảnh

Các API contract hiện đã được tổ chức trong repository [`api-docs`](../../../api-docs/). Task này không yêu cầu viết lại OpenAPI, tạo lại request/response schema hoặc lập checklist để từng member sync API. `api-docs` là nguồn contract kỹ thuật hiện có; Apidog cần được cấu hình để team có thể sử dụng contract đó thuận tiện trong quá trình phát triển và demo.

Vấn đề cần giải quyết là sau khi gọi login, người dùng vẫn phải tự copy access token/refresh token vào từng request. Apidog cần tự nhận token từ response login, lưu vào environment và tự động dùng token cho các request tiếp theo.

## Mục tiêu

- Thiết lập environment chuẩn trên Apidog cho các môi trường của dự án.
- Tự động bắt access token và refresh token từ login response.
- Tự động gắn access token vào request cần authentication.
- Tự động refresh access token khi cần, trong phạm vi cơ chế Apidog hỗ trợ.
- Giúp member test API mà không phải nhập hoặc copy token thủ công.
- Giữ Apidog đồng bộ với contract đã có trong `api-docs`.

## Phạm vi công việc

### 1. Cấu hình environment trên Apidog

- [ ] Tạo environment cho local/development và các môi trường được PM xác nhận.
- [ ] Khai báo base URL cho `identity-service`, `tenancy-service`, `payment-service` và `community-service`.
- [ ] Khai báo biến `accessToken`.
- [ ] Khai báo `refreshToken` nếu backend trả refresh token qua body.
- [ ] Ghi rõ biến nào là local variable, environment variable hay secret variable.
- [ ] Không lưu secret production thật trong collection dùng chung.

### 2. Import và tổ chức API từ `api-docs`

- [ ] Import/bind collection từ OpenAPI bundle hiện có trong `api-docs`.
- [ ] Phân nhóm request theo service và domain.
- [ ] Kiểm tra request dùng đúng base URL của environment hiện tại.
- [ ] Không tạo schema khác với schema trong `api-docs` chỉ để tiện test.
- [ ] Nếu import conflict, xử lý bằng mapping/configuration và ghi chú nguyên nhân.

### 3. Tự động bắt token sau login

- [ ] Gắn post-response script cho request login.
- [ ] Đọc access token từ đúng path trong response thực tế.
- [ ] Đọc refresh token từ body nếu contract trả qua body.
- [ ] Nếu refresh token trả qua HttpOnly cookie, giữ cookie jar/session thay vì cố đọc token từ body.
- [ ] Lưu token vào đúng environment variable.
- [ ] Không log token ra console hoặc đưa token vào documentation/example.

Luồng mong muốn:

```text
POST /auth/login
  → nhận response thành công
  → lưu accessToken hoặc giữ cookie session
  → các request protected dùng token tự động
```

### 4. Tự động gắn access token

- [ ] Cấu hình Authorization ở collection/folder hoặc request level theo security scheme.
- [ ] Dùng biến environment thay vì hard-code Bearer token.
- [ ] Request public không bị gắn token bắt buộc nếu API không cần authentication.
- [ ] Kiểm tra request giữa các service không dùng nhầm token hoặc environment.

### 5. Tự động refresh token

- [ ] Tạo request refresh theo đúng route hiện có trong `api-docs`.
- [ ] Cấu hình refresh request dùng refresh token variable hoặc cookie jar.
- [ ] Sau refresh thành công, cập nhật access token mới vào environment.
- [ ] Kiểm tra request protected kế tiếp sử dụng access token mới.
- [ ] Ghi rõ giới hạn của Apidog nếu không hỗ trợ interceptor tự retry request gốc.
- [ ] Nếu không retry tự động được, cung cấp flow refresh một bước nhưng vẫn tự cập nhật token.

## Contract và nguồn sự thật

- `api-docs/` là nguồn OpenAPI hiện có.
- Apidog là nền tảng thực thi/test contract, không phải nơi định nghĩa contract khác.
- Task này không yêu cầu BE hoặc FE viết lại API contract.
- Khi implementation thay đổi route/response, API owner cập nhật `api-docs` theo quy trình hiện có; P4-15 chỉ cập nhật collection/environment cần thiết.

## Kết quả bàn giao

- Apidog project/collection được tổ chức theo service.
- Environment mẫu có base URL và biến token.
- Login tự lưu token hoặc duy trì cookie session.
- Request protected tự dùng token.
- Refresh flow được cấu hình và có hướng dẫn ngắn cho member.
- Có hướng dẫn reset environment/token khi đổi user hoặc môi trường.

## Manual verification

1. Chọn environment local/development.
2. Gọi login bằng tài khoản hợp lệ.
3. Xác nhận token được lưu tự động hoặc cookie session được giữ.
4. Gọi request protected mà không nhập Authorization thủ công.
5. Làm access token hết hạn hoặc thay bằng token không hợp lệ.
6. Gọi refresh và xác nhận token mới được lưu.
7. Gọi lại request protected bằng token mới.
8. Đổi environment và xác nhận không dùng nhầm base URL/token.

## Tiêu chí nghiệm thu

- Member test login và API protected trên Apidog mà không copy token thủ công.
- Các service được phân nhóm và dùng đúng environment base URL.
- Token không bị hard-code trong request hoặc commit vào repository.
- Apidog sử dụng contract từ `api-docs`, không tạo contract độc lập gây lệch.
- Có hướng dẫn ngắn để member khác sử dụng collection.
