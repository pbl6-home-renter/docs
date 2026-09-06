# Shared / Cross-Role User Flow

Tài liệu này mô tả luồng điều hướng dùng chung, cơ chế phân quyền vai trò bất biến (`User.role`), luồng trải nghiệm công khai không cần đăng nhập (Guest Access), và luồng đăng xuất chuẩn hóa cho mọi đối tượng trong hệ thống Rentify (PBL6).

---

## 1. Nguyên Tắc Thiết Kế (Shared Business Rules)

1. **Mô hình Role Đơn lẻ & Bất Biến (Immutable Role) — KHÔNG CHO PHÉP ĐỔI ROLE:**
   * `User.role` là **Enum đơn lẻ**: `ADMIN` | `LANDLORD` | `TENANT`. Một tài khoản tại một thời điểm chỉ mang đúng một vai trò duy nhất.
   * **Quy tắc bất biến:** Một tài khoản sau khi được đăng ký/khởi tạo **TUYỆT ĐỐI KHÔNG THỂ ĐỔI ROLE** dưới bất kỳ hình thức nào.
   * Không có tính năng đổi vai trò trong ứng dụng hay hệ thống quản trị. Người dùng muốn chuyển đổi mục đích sử dụng (ví dụ: Khách thuê muốn chuyển sang làm Chủ trọ) bắt buộc phải đăng ký tài khoản mới bằng thông tin định danh riêng.
2. **Cấu trúc Quản trị:**
   * Hệ thống chỉ có **DUY NHẤT 1 tài khoản Admin** quản trị toàn bộ nền tảng (không phân cấp Super Admin / Sub-Admin).
3. **Trải nghiệm Không cần đăng nhập (Public / Guest-First Access):**
   * Người dùng chưa đăng nhập (khách vãng lai, sinh viên tìm trọ) được tự do truy cập các tính năng khám phá: **Bản đồ phòng trọ**, **Bộ lọc tìm kiếm**, **Xem chi tiết phòng**, **Xem feed tìm bạn ở ghép**.
   * Chỉ khi thực hiện các thao tác định danh (Lưu tin yêu thích, Gửi yêu cầu ghép bạn, Chat, Xem hóa đơn, Ký hợp đồng), hệ thống mới yêu cầu đăng nhập.
4. **Đăng xuất Đồng bộ (Logout Flow):**
   * Mọi vai trò đều có nút Đăng xuất rõ ràng để hủy JWT token, xóa local storage, ngắt kết nối WebSocket và đưa ứng dụng về trạng thái Khách vãng lai.

---

## 2. Cross-Role Authentication, Guest Access & Navigation Flow

```mermaid
flowchart TD
    AppStart([Khởi động Ứng dụng: Web / Mobile]) --> CheckPublicAction{Người dùng chọn thao tác?}
    
    %% Nhánh 1: Khám phá công khai (Guest)
    CheckPublicAction -->|Khám phá công khai không cần login| GuestBrowse[Xem Bản đồ / Danh sách phòng trọ & Chi tiết]
    GuestBrowse --> NeedProtectedAction{Thao tác yêu cầu tài khoản?<br>Lưu yêu thích, Ghép bạn, Chat, Hóa đơn}
    NeedProtectedAction -->|Chỉ xem thông tin| GuestBrowse
    NeedProtectedAction -->|Cần định danh| TriggerLogin[Chuyển đến màn hình Đăng nhập]
    
    %% Nhánh 2: Chủ động đăng nhập
    CheckPublicAction -->|Chủ động Đăng nhập| TriggerLogin
    
    TriggerLogin --> InputCreds[Nhập Tài khoản & Mật khẩu]
    InputCreds --> SubmitAuth[Gửi xác thực API]
    
    SubmitAuth --> ValidateAuth{Thông tin đăng nhập chính xác?}
    ValidateAuth -->|Sai thông tin| ShowAuthErr[Báo lỗi đăng nhập] --> InputCreds
    ValidateAuth -->|Tài khoản bị khóa isActive=false| ShowLockErr[Báo lỗi: Tài khoản đang bị tạm khóa] --> EndBlocked([Dừng])
    
    ValidateAuth -->|Hợp lệ| IssueJWT[Hệ thống cấp JWT token chứa User.role enum]
    
    %% Điều hướng theo Role bất biến
    IssueJWT --> RouteByRole{User.role enum}
    RouteByRole -->|role == ADMIN| GoAdmin[Vào Admin Dashboard Web]
    RouteByRole -->|role == LANDLORD| GoLandlord[Vào Landlord Console Web / Mobile App]
    RouteByRole -->|role == TENANT| GoTenant[Vào Tenant Portal Mobile / Responsive Web]
    
    %% Đăng xuất cho cả 3 vai trò
    GoAdmin --> DoLogout[Người dùng chọn Đăng xuất]
    GoLandlord --> DoLogout
    GoTenant --> DoLogout
    
    DoLogout --> ClearSession[Hủy Token / Xóa Storage / Ngắt Socket]
    ClearSession --> RedirectGuest[Đưa về Màn hình Đăng nhập hoặc Trang khám phá]
    RedirectGuest --> EndSession([Kết thúc phiên an toàn])
```
