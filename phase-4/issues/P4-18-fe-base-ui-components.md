# P4-18 — Xây dựng base UI components từ kết quả Google Stitch

**Trạng thái:** 🟢 Done
**Người phụ trách:** FE member / FE Lead  
**Người review:** PM, FE team  
**Ước lượng:** 13 points · 24–48 giờ  
**Độ ưu tiên:** High

## Bối cảnh

P4-17 tạo ra danh sách component và design pattern cần dùng chung. Issue này chuyển kết quả khảo sát thành code có thể sử dụng trong các feature sau. Mục tiêu là nền tảng đủ ổn định để F1/F2 không phải tự định nghĩa lại style và behavior.

## Phạm vi công việc

- Đưa design token đã approve vào codebase.
- Chuẩn hóa typography, màu sắc, spacing, border, radius và shadow.
- Triển khai primitive component đã được chọn.
- Triển khai feedback component cho loading, empty, error và success.
- Hỗ trợ disabled, loading, focus, validation và responsive state khi phù hợp.
- Đảm bảo component dùng được ở Tenant, Landlord và Admin shell.
- Tách shared component khỏi business logic feature.
- Cập nhật import convention và hướng dẫn sử dụng ngắn gọn.

## Quy tắc triển khai

- Không tự bổ sung component ngoài phạm vi đã review ở P4-17.
- Không hard-code style lặp lại trong feature nếu style thuộc shared component.
- Nếu vượt quá 13 points, tách issue con trước khi tiếp tục.

## Tiêu chí nghiệm thu

- Component được export từ vị trí shared ổn định.
- Có route thực tế sử dụng mỗi nhóm component đã chốt.
- Các trạng thái chính hiển thị nhất quán.
- `npm run build` và `npm run lint` của `fe/` chạy thành công.
- F1/F2 có thể sử dụng foundation mà không copy component.

---

## 1. Checklist triển khai

### Design token và theme

- [ ] Tạo một nguồn token chính, không lặp màu trực tiếp trong từng component.
- [ ] Chuẩn hóa màu brand, surface, text, border, success, warning và error.
- [ ] Chuẩn hóa font, heading scale, body text và trạng thái disabled.
- [ ] Chuẩn hóa spacing, radius, shadow và breakpoint.
- [ ] Đối chiếu token với kết quả P4-17 trước khi merge.

### Primitive components

- [ ] Button có variant, size, loading, disabled và keyboard focus.
- [ ] Input có label, placeholder, helper text, error text và disabled state.
- [ ] Select/textarea hoặc component tương đương nếu inventory yêu cầu.
- [ ] Card, badge/tag, divider và icon wrapper theo design reference.
- [ ] Component nhận className/props mở rộng nhưng không phá style mặc định.

### Feedback components

- [ ] Loading state cho page, section và submit action.
- [ ] Empty state có title, description và action tùy chọn.
- [ ] Error state có message thân thiện và callback retry.
- [ ] Success/error notification dùng chung cơ chế của app.
- [ ] Không để từng feature tự tạo một kiểu loading/error khác nhau.

### Tài liệu sử dụng

- [ ] Tạo showcase hoặc route nội bộ để review component.
- [ ] Ghi ví dụ import và cách dùng variant chính.
- [ ] Ghi rõ component stable và component experimental.

## 2. Tiêu chí review giao diện

- Kiểm tra desktop và kích thước màn hình nhỏ.
- Kiểm tra focus bằng keyboard.
- Kiểm tra text dài, lỗi validation và trạng thái loading.
- Đảm bảo component không chứa API call hoặc business rule.
- Đảm bảo không phá route hiện có trong `fe/`.
