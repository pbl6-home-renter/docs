# Shared / Cross-Role User Flow

## Cross-Role Authentication & Navigation Flow
Diagram dưới đây thể hiện luồng điều hướng dùng chung khi một tài khoản đăng nhập vào hệ thống, minh họa cách cơ chế mảng vai trò `roles` (D13) phân định quyền truy cập giữa **Admin** và **Landlord**.

```mermaid
flowchart TD
    UserStart([Người dùng truy cập Hệ thống]) --> InputCredentials[Nhập tài khoản và mật khẩu]
    InputCredentials --> AuthenticateUser{Xác thực thông tin người dùng}
    
    AuthenticateUser -->|Sai thông tin| AuthFailure[Thông báo lỗi đăng nhập] --> InputCredentials
    AuthenticateUser -->|Tài khoản bị khóa| AccountLocked[Thông báo: Tài khoản đang bị khóa bởi Admin] --> UserEndFail([Dừng truy cập])
    
    AuthenticateUser -->|Xác thực thành công| IssueToken[Hệ thống cấp JWT chứa mảng 'roles']
    
    IssueToken --> InspectRoles{Kiểm tra mảng roles}
    
    InspectRoles -->|Chứa role 'admin'| GoAdminPanel[Điều hướng đến Admin Dashboard]
    InspectRoles -->|Chứa role 'landlord'| GoLandlordConsole[Điều hướng đến Landlord Web Console]
    InspectRoles -->|Chỉ chứa role 'tenant'| GoTenantPortal[Điều hướng đến Tenant Portal]
    
    GoAdminPanel --> AdminSession[Admin thực hiện quản trị người dùng & hệ thống]
    GoLandlordConsole --> LandlordSession[Chủ trọ thực hiện vận hành bất động sản & hóa đơn]
    
    AdminSession --> TriggerLockAction{Admin khóa tài khoản Chủ trọ vi phạm?}
    TriggerLockAction -->|Có khóa| InvalidateLLSession[Hủy JWT của Chủ trọ & Chặn truy cập]
    InvalidateLLSession --> UserEndFail
    TriggerLockAction -->|Không| ContinueNormal[Hệ thống vận hành bình thường]
    
    LandlordSession --> LandlordLogout[Chủ trọ đăng xuất]
    AdminSession --> AdminLogout[Admin đăng xuất]
    
    LandlordLogout --> ClearUserToken[Xóa Session Token] --> UserEndSuccess([Đăng xuất an toàn])
    AdminLogout --> ClearUserToken
```
