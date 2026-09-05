# User Flow — Admin

## 1. Admin Overview
Mục đích của Admin Flow là cung cấp quy trình quản trị người dùng tập trung đa vai trò (`roles` array theo D13), giám sát hoạt động hệ thống và cấu hình tham số vận hành chung (như mock payment gateway R1, provider AI adapter D3). Admin không can thiệp vào các nghiệp vụ riêng tư của chủ trọ/người thuê (không duyệt hợp đồng, không can thiệp đối soát tài chính hay duyệt từng người thuê).

---

## 2. Admin Main User Flow
```mermaid
flowchart TD
    Start([Bắt đầu: Truy cập Admin Portal]) --> Login[Nhập thông tin đăng nhập]
    Login --> AuthCheck{Xác thực tài khoản & Quyền Admin?}
    
    AuthCheck -->|Thất bại / Sai mật khẩu| LoginError[Hiển thị lỗi xác thực]
    LoginError --> Login
    AuthCheck -->|Không có role Admin| AccessDenied[Báo lỗi: Từ chối truy cập 403]
    AccessDenied --> Login
    
    AuthCheck -->|Thành công| AdminDash[Trang Tổng quan Admin Dashboard]
    
    AdminDash --> SelectNav{Chọn phân hệ quản trị}
    
    SelectNav -->|Quản lý người dùng| UserMod[Module Quản lý Người dùng]
    SelectNav -->|Cấu hình hệ thống| ConfigMod[Module Cấu hình Hệ thống]
    SelectNav -->|Giám sát & Logs| LogMod[Module Giám sát Hoạt động]
    SelectNav -->|Đăng xuất| LogoutAct[Thực hiện Đăng xuất]
    
    UserMod --> Ret1[Quay lại Dashboard] --> AdminDash
    ConfigMod --> Ret2[Quay lại Dashboard] --> AdminDash
    LogMod --> Ret3[Quay lại Dashboard] --> AdminDash
    
    LogoutAct --> ClearSession[Hủy JWT Session] --> EndAdmin([Kết thúc phiên làm việc])
```

---

## 3. Admin Authentication Flow
```mermaid
flowchart TD
    StartAuth([Bắt đầu đăng nhập Admin]) --> EnterCreds[Nhập Email và Mật khẩu]
    EnterCreds --> SubmitCreds[Gửi yêu cầu đăng nhập]
    
    SubmitCreds --> ValidateCreds{Kiểm tra thông tin hợp lệ?}
    ValidateCreds -->|Sai định dạng / Để trống| ShowValidError[Báo lỗi dữ liệu không hợp lệ]
    ShowValidError --> EnterCreds
    
    ValidateCreds -->|Hợp lệ| QueryUser{Kiểm tra tài khoản trong CSDL}
    QueryUser -->|Không tồn tại / Sai mật khẩu| ShowAuthFail[Báo lỗi: Sai email hoặc mật khẩu]
    ShowAuthFail --> EnterCreds
    
    QueryUser -->|Tài khoản bị khóa| ShowLocked[Báo lỗi: Tài khoản đã bị vô hiệu hóa]
    ShowLocked --> EndAuthFail([Dừng đăng nhập])
    
    QueryUser -->|Xác thực thành công| CheckAdminRole{roles array có chứa 'admin'?}
    CheckAdminRole -->|Không| DenyForbidden[Báo lỗi: 403 Forbidden - Không có quyền Admin]
    DenyForbidden --> EndAuthFail
    
    CheckAdminRole -->|Có quyền Admin| IssueJWT[Cấp JWT token chứa roles admin]
    IssueJWT --> SaveSession[Lưu token phiên làm việc]
    SaveSession --> RedirectDash[Chuyển hướng vào Admin Dashboard]
    RedirectDash --> EndAuthSuccess([Đăng nhập Admin thành công])
```

---

## 4. Admin Management Flow (User Management & System Config)
```mermaid
flowchart TD
    StartMgmt([Vào Quản lý Người dùng & Cấu hình]) --> ViewUsers[Xem danh sách Người dùng toàn hệ thống]
    
    ViewUsers --> FilterUser[Lọc theo vai trò: Landlord / Tenant / Admin]
    FilterUser --> SelectUser[Chọn một người dùng cụ thể]
    SelectUser --> ViewUserDetail[Xem thông tin chi tiết tài khoản]
    
    ViewUserDetail --> ActionDecision{Chọn thao tác tài khoản}
    
    ActionDecision -->|Khóa tài khoản vi phạm| ConfirmLock{Xác nhận khóa tài khoản?}
    ConfirmLock -->|Hủy| ViewUserDetail
    ConfirmLock -->|Đồng ý| LockAcc[Cập nhật trạng thái User: isActive = false]
    LockAcc --> NotifyLocked[Thông báo: Đã khóa tài khoản thành công]
    NotifyLocked --> ViewUsers
    
    ActionDecision -->|Mở khóa tài khoản| ConfirmUnlock{Xác nhận mở khóa?}
    ConfirmUnlock -->|Hủy| ViewUserDetail
    ConfirmUnlock -->|Đồng ý| UnlockAcc[Cập nhật trạng thái User: isActive = true]
    UnlockAcc --> NotifyUnlocked[Thông báo: Đã kích hoạt lại tài khoản]
    NotifyUnlocked --> ViewUsers
    
    ActionDecision -->|Đổi phân quyền role D13| UpdateRoles[Thêm / Bớt role trong mảng roles]
    UpdateRoles --> SaveRoles[Lưu phân quyền mới]
    SaveRoles --> ViewUserDetail
    
    ViewUsers --> SwitchConfig[Chuyển sang Cấu hình Hệ thống]
    SwitchConfig --> ViewSysConfig[Xem tham số: Toggle Mock Payment / AI Provider Env]
    ViewSysConfig --> EditSysConfig[Thay đổi tham số cấu hình]
    EditSysConfig --> SaveSysConfig[Lưu cấu hình hệ thống]
    SaveSysConfig --> EndMgmt([Hoàn tất tác vụ quản trị])
```
