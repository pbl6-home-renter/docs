# User Flow — Admin

## 1. Nguyên Tắc Quản Trị Cốt Lõi

1. **Một Admin duy nhất (Single Admin):**
   * Hệ thống chỉ có **duy nhất 1 tài khoản Admin** quản trị toàn bộ nền tảng (không phân cấp Super Admin / Sub-Admin, không có chức năng tạo thêm hoặc phân quyền Admin khác).
2. **Vai trò Bất Biến (Immutable Role) — KHÔNG CHO PHÉP ĐỔI ROLE:**
   * `User.role` là Enum đơn lẻ: `ADMIN` | `LANDLORD` | `TENANT`.
   * **Quy tắc bất biến:** Một tài khoản sau khi đăng ký/khởi tạo **TUYỆT ĐỐI KHÔNG THỂ ĐỔI ROLE** dưới bất kỳ hình thức nào.
   * Admin **không có** chức năng đổi role cho người dùng, người dùng cũng không thể tự đổi vai trò của mình. Nếu một người muốn tham gia với vai trò khác (ví dụ: Khách thuê muốn đăng tin làm Chủ trọ), họ bắt buộc phải đăng ký tài khoản mới.
3. **Phạm vi Cấu hình của Admin (System-level Only):**
   * Admin chỉ cấu hình các tham số kỹ thuật cấp hệ thống:
     - **Mock Payment Gateway (R1):** Bật/tắt chế độ thanh toán giả lập phục vụ kiểm thử/demo.
     - **AI Provider Adapter (D3):** Lựa chọn adapter AI (`OpenAI` hoặc `Gemini`) và hạn mức API.
   * *Lưu ý:* Mọi cấu hình liên quan đến ngày chốt tiền, chu kỳ hóa đơn và **quét nợ tiền trọ thuộc toàn quyền của từng Chủ trọ (Landlord)**, Admin không can thiệp.

---

## 2. Tổng Quan Điều Hướng (Admin Navigation Hub)

```mermaid
flowchart TD
    StartAdmin([Bắt đầu: Admin truy cập Portal]) --> InputAuth[Nhập Email & Mật khẩu Admin]
    InputAuth --> CheckAdminAuth{Xác thực thông tin & User.role == ADMIN?}
    AdminStart([Admin Đăng Nhập]) --> AdminDash[Admin Dashboard Tổng Quan]
    AdminDash --> NavChoice{Chọn phân hệ quản trị}
    
    CheckAdminAuth -->|Thất bại| AuthErr[Báo lỗi sai thông tin đăng nhập] --> InputAuth
    CheckAdminAuth -->|Đúng nhưng bị khóa| LockedErr[Báo lỗi: Tài khoản Admin bị vô hiệu hóa] --> EndAdminFail([Dừng])
    NavChoice -->|1. Người dùng| SubUser[Quản lý Người Dùng & Duyệt KYC]
    NavChoice -->|2. Kỹ thuật| SubConfig[Cấu hình Tham số Kỹ thuật]
    NavChoice -->|3. Giám sát| SubLogs[Nhật ký Kiểm toán & Audit Logs]
    NavChoice -->|4. Đăng xuất| AdminLogout[Đăng xuất an toàn]
```

---

## 3. Các Luồng Nghiệp Vụ Chi Tiết (Sub-Flows)

### Sub-Flow 1: Xác Thực & Đăng Nhập Admin

Admin đăng nhập qua cổng quản trị Web bằng email và mật khẩu. Hệ thống xác thực danh tính và kiểm tra quyền quản trị.

```mermaid
flowchart TD
    StartLogin([Truy cập Cổng Admin]) --> InputCreds[Nhập Email & Mật khẩu]
    InputCreds --> SubmitLogin[Gửi yêu cầu đăng nhập]
    SubmitLogin --> CheckCreds{Kiểm tra thông tin?}
    
    CheckAdminAuth -->|Thành công| AdminDash[Admin Dashboard Tổng quan]
    CheckCreds -->|Sai tài khoản/mật khẩu| FailAuth[Báo lỗi đăng nhập] --> InputCreds
    CheckCreds -->|Đúng thông tin| CheckRole{User.role == 'ADMIN'?}
    
    AdminDash --> ChooseNav{Chọn phân hệ chức năng}
    
    ChooseNav -->|1. Quản lý Người dùng| ModUsers[Danh sách Người dùng: Landlord / Tenant]
    ChooseNav -->|2. Quản lý Đội ngũ Admin| ModAdminTeam[Phân hệ Super Admin: Quản lý Admin]
    ChooseNav -->|3. Cấu hình Tham số Kỹ thuật| ModConfig[Cấu hình: Mock Payment, AI Provider, Cron]
    ChooseNav -->|4. Giám sát & Audit Logs| ModLogs[Nhật ký hệ thống & Cảnh báo bất thường]
    ChooseNav -->|5. Đăng xuất| AdminLogout[Đăng xuất khỏi hệ thống]
    
    ModUsers --> RetDash1[Quay về Dashboard] --> AdminDash
    ModAdminTeam --> RetDash2[Quay về Dashboard] --> AdminDash
    ModConfig --> RetDash3[Quay về Dashboard] --> AdminDash
    ModLogs --> RetDash4[Quay về Dashboard] --> AdminDash
    
    AdminLogout --> ClearAdminJWT[Hủy Token & Phiên làm việc] --> EndAdminSuccess([Kết thúc phiên làm việc])
    CheckRole -->|Không phải Admin| Deny403[Báo lỗi 403: Không có quyền truy cập] --> EndDeny([Dừng])
    CheckRole -->|Đúng Admin| IssueToken[Cấp JWT Token Admin] --> EnterDash[Vào Admin Dashboard] --> EndAuthSuccess([Đăng nhập thành công])
```

---

## 3. Admin Authentication & Role Delegation Flow
### Sub-Flow 2: Quản Lý Người Dùng & Phê Duyệt eKYC

Admin theo dõi danh sách toàn bộ người dùng (Landlord, Tenant). Admin có quyền xem chi tiết hồ sơ, duyệt CCCD (eKYC), hoặc khóa/mở khóa tài khoản khi có vi phạm. **Tuyệt đối không có chức năng đổi role.**

```mermaid
flowchart TD
    StartAuth([Bắt đầu xác thực]) --> EnterAdminCreds[Nhập Email & Mật khẩu]
    EnterAdminCreds --> SubmitAdminLogin[Gửi yêu cầu đăng nhập]
    StartUserMgmt([Vào Quản lý Người dùng]) --> ViewList[Xem danh sách: Lọc theo Role, KYC, Trạng thái]
    ViewList --> SelectUser[Chọn xem chi tiết một Người dùng]
    SelectUser --> UserAction{Thao tác quản trị}
    
    SubmitAdminLogin --> VerifyDB{Kiểm tra CSDL User}
    VerifyDB -->|Không khớp| ShowFail[Thông báo: Sai tài khoản hoặc mật khẩu] --> EnterAdminCreds
    %% Nhánh 1: Khóa / Mở khóa tài khoản
    UserAction -->|Khóa tài khoản vi phạm| ConfirmLock{Xác nhận khóa?}
    ConfirmLock -->|Đồng ý| LockAccount[Cập nhật User.isActive = false]
    LockAccount --> AuditLock[Ghi nhận Audit Log: Khóa tài khoản] --> ViewList
    ConfirmLock -->|Hủy| SelectUser
    
    VerifyDB -->|Khớp thông tin| CheckAdminEnum{Kiểm tra User.role == 'ADMIN'?}
    CheckAdminEnum -->|role != ADMIN| Deny403[Báo lỗi 403: Bạn không có quyền quản trị] --> EndAuthDeny([Dừng])
    UserAction -->|Mở khóa tài khoản| UnlockAccount[Cập nhật User.isActive = true]
    UnlockAccount --> AuditUnlock[Ghi nhận Audit Log: Mở khóa tài khoản] --> ViewList
    
    CheckAdminEnum -->|role == ADMIN| CheckIsSuper{Là Super Admin hay Sub-Admin?}
    CheckIsSuper -->|Super Admin| FullAccess[Cấp Token toàn quyền: Có quyền thêm/xóa Sub-Admin]
    CheckIsSuper -->|Sub-Admin| RestrictedAccess[Cấp Token hạn chế: Không có quyền xóa Admin khác]
    %% Nhánh 2: Đối soát & Phê duyệt eKYC (CCCD)
    UserAction -->|Xử lý yêu cầu eKYC| ReviewCCCD[Đối soát ảnh 2 mặt CCCD và thông tin cá nhân]
    ReviewCCCD --> DecisionKYC{Quyết định duyệt?}
    DecisionKYC -->|Thông tin chuẩn xác| ApproveKYC[Chuyển KYC: 'APPROVED']
    DecisionKYC -->|Ảnh mờ / Sai thông tin| RejectKYC[Chuyển KYC: 'REJECTED' + Nhập lý do từ chối]
    
    FullAccess --> EnterAdminDashboard[Vào Trang Chủ Quản Trị]
    RestrictedAccess --> EnterAdminDashboard
    EnterAdminDashboard --> EndAuthSuccess([Đăng nhập Admin thành công])
    ApproveKYC --> NotifyKYC[Gửi thông báo kết quả cho người dùng] --> ViewList
    RejectKYC --> NotifyKYC
```

* **Quy tắc an toàn:**
  - Không có nút đổi role. Vai trò của tài khoản hiển thị dạng nhãn tĩnh (Static Tag: `LANDLORD` hoặc `TENANT`).
  - Khi tài khoản bị khóa (`isActive = false`), mọi phiên đăng nhập của người dùng đó bị hủy ngay lập tức và chặn truy cập API.

---

## 4. Admin Management Flow (User, Config & Audit Logs)
### Sub-Flow 3: Cấu Hình Tham Số Kỹ Thuật Hệ Thống

Quản lý các tham số vận hành tầng nền tảng (Toggle Mock Payment và AI Provider Adapter).

```mermaid
flowchart TD
    StartMgmt([Vào Phân hệ Quản Trị]) --> SelectTab{Chọn nghiệp vụ quản trị}
    StartConfig([Vào Cấu hình Kỹ thuật]) --> ViewSettings[Xem danh sách tham số hệ thống hiện tại]
    ViewSettings --> ChooseSetting{Chọn tham số điều chỉnh}
    
    %% Nhánh 1: Quản lý User (Khóa / Mở khóa an toàn)
    SelectTab -->|Quản lý Người dùng| ListUsers[Xem danh sách User toàn hệ thống]
    ListUsers --> SearchUser[Tìm kiếm theo Tên, Email, SĐT, Role]
    SearchUser --> ViewDetail[Xem chi tiết hồ sơ người dùng]
    ChooseSetting -->|Toggle Mock Payment R1| ToggleMock[Bật / Tắt chế độ Mock cổng thanh toán]
    ChooseSetting -->|AI Provider Adapter D3| SwitchAI[Chọn nhà cung cấp AI: OpenAI hoặc Gemini]
    
    ViewDetail --> UserAction{Thao tác quản trị}
    UserAction -->|Khóa tài khoản vi phạm| ConfirmLock{Xác nhận khóa người dùng?}
    ConfirmLock -->|Hủy| ViewDetail
    ConfirmLock -->|Đồng ý| SetInactive[Cập nhật User.isActive = false]
    SetInactive --> RecordAudit1[Ghi log: Admin X đã khóa User Y] --> ListUsers
    ToggleMock --> SaveConfig[Lưu cấu hình hệ thống]
    SwitchAI --> SaveConfig
    
    UserAction -->|Mở khóa tài khoản| SetActive[Cập nhật User.isActive = true]
    SetActive --> RecordAudit2[Ghi log: Admin X đã mở khóa User Y] --> ListUsers
    
    UserAction -->|Yêu cầu đổi vai trò Role| CheckDataIntegrity{Kiểm tra tài khoản có dữ liệu liên kết?<br>Nhà, Phòng, HĐ, Tiền}
    CheckDataIntegrity -->|Đang có phòng/HĐ hoạt động| RejectRoleChange[Từ chối: Không được đổi role vì đang vận hành BĐS] --> ViewDetail
    CheckDataIntegrity -->|Tài khoản trắng hoàn toàn| AllowChange[Cho phép cập nhật User.role enum mới] --> RecordAudit3[Ghi log đổi role] --> ListUsers
    SaveConfig --> WriteConfigAudit[Ghi Audit Log: Admin cập nhật cấu hình]
    WriteConfigAudit --> EndConfig([Áp dụng tham số mới thành công])
```

    %% Nhánh 2: Quản lý Admin Team (Chỉ Super Admin)
    SelectTab -->|Quản lý Admin Team| CheckSuperPerm{Người thực hiện là Super Admin?}
    CheckSuperPerm -->|Không| BlockSuper[Báo lỗi: Chỉ Super Admin mới được quản trị Admin] --> StartMgmt
    CheckSuperPerm -->|Phải| ManageAdminList[Xem danh sách các Admin]
    ManageAdminList --> CreateSubAdmin[Tạo tài khoản Sub-Admin mới]
    ManageAdminList --> RemoveSubAdmin{Xóa Sub-Admin cấp dưới?}
    RemoveSubAdmin -->|Xóa Sub-Admin| DeleteAdmin[Thu hồi quyền / Xóa tài khoản Sub-Admin] --> StartMgmt
    RemoveSubAdmin -->|Cố tình xóa Super Admin| ProtectSuper[Hệ thống từ chối: Không thể xóa tài khoản Root] --> StartMgmt
* **Lưu ý nghiệp vụ:**
  - Mock Payment: Dùng khi kiểm thử nghiệm thu hoặc chấm đồ án demo mà không cần quét tiền tài khoản thật.
  - Cấu hình này áp dụng chung cho toàn sàn, không can thiệp vào nghiệp vụ tiền tệ phòng trọ của Chủ trọ.

    %% Nhánh 3: Cấu hình Tham số Kỹ thuật
    SelectTab -->|Cấu hình Tham số| ShowConfigs[Hiển thị bảng thông số cấu hình]
    ShowConfigs --> ConfigItem{Chọn tham số thay đổi}
    ConfigItem -->|Toggle Mock Payment R1| SwitchMock[Bật / Tắt chế độ Mock cổng thanh toán]
    ConfigItem -->|Chọn AI Provider D3| SelectAI[Chuyển đổi Adapter: OpenAI <-> Gemini]
    ConfigItem -->|Cấu hình Lịch Bot Quét Nợ| EditCron[Cài đặt tần suất quét hóa đơn quá hạn]
    SwitchMock --> SaveConfig[Lưu cấu hình hệ thống & Ghi Audit Log]
    SelectAI --> SaveConfig
    EditCron --> SaveConfig
    SaveConfig --> StartMgmt
---

    %% Nhánh 4: Giám sát Hoạt động & Logs
    SelectTab -->|Giám sát & Logs| ViewAuditLog[Xem danh sách Audit Log thời gian thực]
    ViewAuditLog --> FilterAudit[Lọc theo: Lỗi thanh toán, Webhook ngân hàng, Hành vi Admin]
    FilterAudit --> ExportLog[Xuất báo cáo log kiểm toán khi cần] --> EndMgmt([Hoàn tất phiên quản trị])
### Sub-Flow 4: Giám Sát Hoạt Động & Nhật Ký Kiểm Toán (Audit Logs)

Admin theo dõi mọi sự kiện quan trọng trong hệ thống nhằm bảo đảm tính minh bạch và an toàn thông tin.

```mermaid
flowchart TD
    StartAudit([Vào Nhật ký Kiểm toán]) --> LoadLogs[Tải danh sách Audit Logs thời gian thực]
    LoadLogs --> ApplyFilter[Lọc theo: Loại sự kiện, Thời gian, Người thực hiện]
    ApplyFilter --> LogAction{Thao tác xem}
    
    LogAction -->|Xem chi tiết sự kiện| ViewPayload[Xem chi tiết payload thay đổi trước / sau]
    LogAction -->|Xuất báo cáo| ExportData[Xuất file báo cáo audit dạng CSV/Excel]
    
    ViewPayload --> LoadLogs
    ExportData --> EndAudit([Hoàn tất giám sát])
```

* **Các sự kiện ghi nhận bắt buộc:**
  - Admin khóa / mở khóa tài khoản người dùng.
  - Admin phê duyệt / từ chối hồ sơ eKYC.
  - Admin thay đổi tham số cấu hình hệ thống (Mock Payment, AI Adapter).
  - Lịch sử callback/webhook giao dịch thanh toán từ cổng ngân hàng.
