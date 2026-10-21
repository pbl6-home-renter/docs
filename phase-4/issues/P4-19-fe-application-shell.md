# P4-19 — Xây dựng application shell cho Tenant, Landlord và Admin

**Trạng thái:** 🟢 Done
**Người phụ trách:** FE member / FE Lead  
**Người review:** PM, API owner  
**Ước lượng:** 8 points · 18–24 giờ  
**Độ ưu tiên:** High / Blocker cho F1 và F2

## Bối cảnh

Frontend hiện dùng một repository nhưng phục vụ nhiều nhóm người dùng. Cần một application shell có thể thay đổi menu, layout và quyền truy cập theo role mà không nhân bản toàn bộ source code.

## Phạm vi công việc

- Giữ mô hình một FE repository trong giai đoạn hiện tại.
- Xây layout authenticated dùng chung.
- Xây header, sidebar, content area, breadcrumb và navigation state.
- Tạo shell variant cho Tenant, Landlord và Admin bằng cấu hình role/route.
- Kết nối public route và protected route với auth store.
- Redirect khi chưa đăng nhập hoặc không đủ quyền.
- Chuẩn hóa trang 403, 404 và trạng thái session hết hạn.
- Thay placeholder cấp shell bằng cấu trúc dùng được cho feature screen.

## Ngoài phạm vi

- Không triển khai đầy đủ nghiệp vụ F1/F2.
- Không tách thành ba repository/app riêng.
- Không tự thay đổi authentication contract ngoài P4-15.

## Tiêu chí nghiệm thu

- User chưa đăng nhập bị chuyển về login khi truy cập route bảo vệ.
- Role khác nhau thấy menu và shell phù hợp.
- Route không có quyền được chuyển đến 403.
- Route không tồn tại hiển thị 404.
- F1/F2 có thể xây page trên content area mà không sửa lại shell.
- `npm run build` và `npm run lint` của `fe/` chạy thành công.

---

## 1. Checklist triển khai

### Cấu trúc layout

- [ ] Tạo authenticated layout có vùng navigation và vùng content riêng.
- [ ] Header hiển thị breadcrumb, user menu, logout và trạng thái session.
- [ ] Sidebar có menu theo role và trạng thái active rõ ràng.
- [ ] Có responsive behavior cho màn hình nhỏ theo design reference.
- [ ] Không nhúng business API call trực tiếp vào layout nếu có thể tách qua hook/store.

### Route và quyền truy cập

- [ ] Public route dành cho login/register không yêu cầu token.
- [ ] Protected route kiểm tra `isAuthenticated`.
- [ ] Role route kiểm tra role trước khi render page.
- [ ] Chưa đăng nhập redirect về login và giữ return URL nếu phù hợp.
- [ ] Không đủ quyền redirect về 403.
- [ ] Route không tồn tại hiển thị 404.

### Shell theo role

- [ ] Tenant shell có thể mở rộng cho màn hình tenant.
- [ ] Landlord shell có navigation quản lý tài sản và nghiệp vụ liên quan.
- [ ] Admin shell có navigation quản trị.
- [ ] Menu không duplicate toàn bộ giữa các role.
- [ ] Thêm menu mới bằng configuration/route definition thay vì sửa nhiều nơi.

## 2. Manual verification

1. Truy cập dashboard khi chưa đăng nhập.
2. Đăng nhập với từng role mẫu.
3. Kiểm tra menu, route và redirect của từng role.
4. Truy cập trực tiếp URL không có quyền.
5. Refresh browser ở route protected để xác nhận session được khôi phục.
6. Truy cập URL không tồn tại để kiểm tra 404.
