# P8-03 — FE: hồ sơ cá nhân và media

**Epic:** Phase 8  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** `ThaiBao11125`  
**Người review:** FE reviewer / PM  
**Ước lượng:** 2 points · 8 giờ (**tối đa 3 points và khoảng 15 file mỗi PR**)  
**Phụ thuộc:** P4-05 (`/me`); P6-04 cho luồng media nếu chưa hoàn tất  
**Repo / branch:** `fe/` · `feature/p8-03-profile-media`  
**Issue:** `docs#TBD`

> **Đọc trước khi code:** `fe/AGENTS.md`, `fe/.agents/skills/fe-feature-workflow/SKILL.md`, `fe-structure/SKILL.md`, `fe-code-style/SKILL.md`, `fe-ui-ux/SKILL.md`. Dùng auth/session, API client, upload component và design system hiện có.

## Mục tiêu

Người dùng xem và cập nhật hồ sơ của chính mình, tải/chọn ảnh hồ sơ qua media API đã có. Sau khi lưu hoặc tải ảnh thành công, thông tin vẫn đúng khi refresh và đăng nhập lại.

## Quyết định áp dụng

- P4-05 cung cấp API hồ sơ `/me`; P6-04 là nguồn API media. Xác minh OpenAPI và implementation hiện có, không tạo endpoint mới.
- User chỉ sửa field mà Identity cho phép; role, account status và dữ liệu định danh read-only nếu contract không cho sửa.
- Media URL tạm không phải nguồn dữ liệu bền vững; lưu media reference theo response/API hiện có.
- Không log token, email/phone đầy đủ hoặc nội dung file nhạy cảm.

## Contract

- `/me`: dùng method, body, response/error schema trong OpenAPI P4-05. Media: dùng presign → upload → complete hoặc API được P6-04 chốt; không tự thay flow.
- Dùng auth interceptor và xử lý session hết hạn theo pattern hiện hành.

### Mapping field

| API field | UI | Quy tắc |
|---|---|---|
| display/profile fields | form hồ sơ | chỉ gửi field được phép update |
| email/phone | thông tin tài khoản | read-only/mask theo contract |
| role/account status | nhãn hồ sơ | chỉ đọc, không gửi trong PATCH |
| media ID/reference | ảnh đại diện | chỉ cập nhật sau khi server hoàn tất upload/link |
| upload URL/token | không render ra giao diện/log | dùng một lần theo media flow, không persist |

## Tham chiếu code

- Tìm auth/session store, màn Settings/Profile và API hooks hiện có trong `fe/src/` trước khi tạo page mới.
- Tái sử dụng upload flow của P6-04 và component avatar/image trong UI library; không viết uploader thứ hai.

## Các bước triển khai

### Bước 1 — Đọc contract và dựng trạng thái hồ sơ

- **Cách làm:** xác định route phù hợp, gọi `/me`, tạo skeleton/loading/error và ánh xạ response vào form.
- **Kiểm tra bước:** đổi account trong session không hiển thị nháy dữ liệu user trước; 401 đi theo auth flow chuẩn.

### Bước 2 — Cập nhật hồ sơ

- **Cách làm:** form dirty state tách khỏi server state; submit chỉ gửi allowlist; giữ nội dung khi API trả 422; invalidate/refetch sau thành công.
- **Kiểm tra bước:** sửa một field hợp lệ rồi refresh thấy giá trị mới; field read-only không xuất hiện trong body.

### Bước 3 — Upload/thay ảnh

- **Cách làm:** validate file theo giới hạn API, dùng presign/upload/complete của P6-04; gắn media reference sau khi complete thành công.
- **Kiểm tra bước:** file hợp lệ hiển thị sau refresh; sai loại/kích thước không gọi API; timeout không làm form báo thành công giả.

### Bước 4 — Case biên

- **Cách làm:** xử lý upload hỏng, URL hết hạn, ảnh không tải, xung đột hai tab và bỏ form đang dirty.
- **Kiểm tra bước:** ảnh lỗi dùng fallback avatar; conflict refetch/báo người dùng thay vì âm thầm ghi đè.

## Ngoài phạm vi

- Sửa profile người khác, đổi role, khóa user, reset password hoặc thay đổi Identity API.
- Upload media nghiệp vụ khác hồ sơ cá nhân.

## Blocker

- Nếu P6-04 media API chưa sẵn sàng, hoàn thiện phần profile độc lập và ghi rõ media blocker; không tạo mock upload.

## Acceptance

- [ ] Profile luôn thuộc user đăng nhập; cập nhật thành công tồn tại sau refresh.
- [ ] Chỉ field được API cho phép mới sửa được; file sai bị chặn và lỗi API được trình bày rõ.
- [ ] Upload hoàn tất theo media API hiện có; không lưu URL tạm làm dữ liệu bền vững.
- [ ] Loading/empty/error/success, auth hết phiên và unsaved changes được xử lý.

## Definition of Done

- [ ] Có bằng chứng UI và request/response đã che dữ liệu nhạy cảm.
- [ ] Tuân thủ skill FE; lint/build/i18n check theo lệnh repo pass.
- [ ] PR ≤ 2 points/~15 file, reviewer FE approve, liên kết issue GitHub sau khi tạo.
