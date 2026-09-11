# User Flow — Admin

## 1. Nguyên Tắc Quản Trị Cốt Lõi

1. **Một Admin Duy Nhất (Single Admin System):**
   * Hệ thống chỉ có **duy nhất 1 tài khoản Admin** quản trị toàn bộ nền tảng.
   * Hoàn toàn không có phân cấp Super Admin hay Sub-Admin, không có chức năng tạo thêm hoặc quản lý đội ngũ Admin khác.
2. **Vai Trò Bất Biến (Immutable Role) — KHÔNG CHO PHÉP ĐỔI ROLE:**
   * Hệ thống có 3 vai trò: Admin, Chủ trọ, Khách thuê.
   * **Quy tắc bất biến:** Một tài khoản sau khi đăng ký hoặc khởi tạo **TUYỆT ĐỐI KHÔNG THỂ ĐỔI ROLE** dưới bất kỳ hình thức nào.
   * Admin không có chức năng đổi role cho người dùng. Nếu người dùng muốn tham gia vai trò khác (ví dụ: Khách thuê muốn làm Chủ trọ), bắt buộc phải đăng ký tài khoản mới riêng biệt.
3. **Kiểm Tra Tay & Phê Duyệt Tài Sản / Dãy Trọ (Sổ Đỏ / Giấy Tờ Đất):**
   * Khi Chủ trọ (Landlord) tạo mới một tài sản (Tòa nhà / Dãy trọ), hệ thống bắt buộc Chủ trọ phải tải lên ảnh bằng chứng sở hữu (Sổ đỏ, Giấy chứng nhận quyền sử dụng đất hoặc Hợp đồng ủy quyền hợp pháp).
   * Tài sản mới tạo sẽ ở trạng thái chờ Admin duyệt.
   * **Admin trực tiếp kiểm tra tay (manual review)** đối soát tính xác thực của giấy tờ và thông tin địa chỉ trước khi ra quyết định Phê duyệt để kích hoạt hoạt động cho thuê hoặc Từ chối kèm lý do rõ ràng.

---

## 2. Tổng Quan Điều Hướng (Admin Navigation Hub)

```mermaid
flowchart TD
    StartAdmin([Bắt đầu: Admin truy cập Portal]) --> InputAuth[Nhập Email & Mật khẩu]
    InputAuth --> CheckAdminAuth{Xác thực thông tin & kiểm tra quyền Admin?}
    
    CheckAdminAuth -->|Thất bại| AuthErr[Báo lỗi sai thông tin đăng nhập] --> InputAuth
    CheckAdminAuth -->|Thành công| AdminDash[Admin Dashboard Tổng quan]
    
    AdminDash --> NavChoice{Chọn phân hệ quản trị}
    
    NavChoice -->|1. Quản lý Người dùng| SubUser[Danh sách Người dùng: Landlord / Tenant]
    NavChoice -->|2. Phê duyệt Bất động sản| SubProperty[Kiểm tra Sổ đỏ / Giấy tờ đất Dãy trọ]
    NavChoice -->|3. Giám sát & Audit Logs| SubLogs[Nhật ký hệ thống & Cảnh báo bất thường]
    NavChoice -->|4. Đăng xuất| AdminLogout[Đăng xuất an toàn]
    
    SubUser --> RetDash1[Quay về Dashboard] --> AdminDash
    SubProperty --> RetDash1
    SubLogs --> RetDash1
    
    AdminLogout --> ClearAdminJWT[Hủy Token & Phiên làm việc] --> EndAdminSuccess([Kết thúc phiên làm việc])
```

---

## 3. Các Luồng Nghiệp Vụ Chi Tiết (Sub-Flows)

### Sub-Flow 1: Xác Thực & Đăng Nhập Admin

Admin đăng nhập qua cổng quản trị Web bằng email và mật khẩu. Hệ thống xác thực danh tính duy nhất của tài khoản Admin và cấp quyền truy cập.

```mermaid
flowchart TD
    StartLogin([Truy cập Cổng Admin]) --> InputCreds[Nhập Email & Mật khẩu]
    InputCreds --> SubmitLogin[Gửi yêu cầu đăng nhập]
    
    SubmitLogin --> VerifyDB{Kiểm tra thông tin đăng nhập}
    VerifyDB -->|Không khớp| FailAuth[Báo lỗi: Sai tài khoản hoặc mật khẩu] --> InputCreds
    
    VerifyDB -->|Khớp thông tin| CheckRole{Kiểm tra quyền Admin?}
    CheckRole -->|Không phải Admin| Deny403[Báo lỗi 403: Không có quyền quản trị] --> EndDeny([Dừng])
    
    CheckRole -->|Là Admin| IssueToken[Cấp JWT Token Quản trị viên]
    IssueToken --> EnterDash[Vào Admin Dashboard] --> EndAuthSuccess([Đăng nhập Admin thành công])
```

---

### Sub-Flow 2: Quản Lý Người Dùng

Admin có quyền xem chi tiết hồ sơ, hoặc khóa/mở khóa tài khoản vi phạm.

```mermaid
flowchart TD
    StartUserMgmt([Vào Quản lý Người dùng]) --> ViewList[Xem danh sách: Lọc theo Role, Trạng thái hoạt động]
    ViewList --> SearchUser[Tìm kiếm theo Tên, Email, SĐT, Role]
    SearchUser --> SelectUser[Chọn xem chi tiết hồ sơ người dùng]
    
    SelectUser --> UserAction{Thao tác quản trị}
    
    %% Nhánh 1: Khóa tài khoản vi phạm
    UserAction -->|Khóa tài khoản vi phạm| CheckLockRole{Đối tượng bị khóa?}
    
    CheckLockRole -->|Khóa Chủ trọ Landlord| LockLL[Vô hiệu hóa tài khoản Chủ trọ: Ẩn toàn bộ BĐS/Phòng khỏi hệ thống]
    LockLL --> TriggerFreezeContracts[Xử lý vòng đời HĐ: Xem Sub-Flow 5]
    TriggerFreezeContracts --> AuditLockLL[Ghi Audit Log: Khóa Chủ trọ] --> ViewList
    
    CheckLockRole -->|Khóa Khách thuê Tenant| LockTenant[Vô hiệu hóa quyền hạn Khách thuê]
    LockTenant --> TriggerRestrictTenant[Xử lý quyền HĐ: Xem Sub-Flow 5]
    TriggerRestrictTenant --> AuditLockTT[Ghi Audit Log: Khóa Khách thuê] --> ViewList
    
    %% Nhánh 2: Mở khóa tài khoản
    UserAction -->|Mở khóa tài khoản| UnlockAccount[Cập nhật trạng thái tài khoản: Đang hoạt động]
    UnlockAccount --> CheckUnlockRole{Đối tượng được mở khóa?}
    CheckUnlockRole -->|Mở khóa Chủ trọ| TriggerRestoreLL[Xử lý khôi phục HĐ: Xem Sub-Flow 5]
    CheckUnlockRole -->|Mở khóa Khách thuê| TriggerRestoreTT[Xử lý khôi phục HĐ: Xem Sub-Flow 5]
    TriggerRestoreLL --> AuditUnlock[Ghi nhận Audit Log: Mở khóa tài khoản] --> ViewList
    TriggerRestoreTT --> AuditUnlock
```

* **Quy tắc khóa và mở khóa tài khoản:**
  - **Khóa tài khoản Chủ trọ (Landlord):** Toàn bộ thông tin dãy trọ và phòng trọ của chủ trọ sẽ bị vô hiệu hóa (ẩn hoàn toàn khỏi hệ thống tìm kiếm công khai). Chi tiết xử lý hợp đồng đang hiệu lực khi khóa tài khoản Chủ trọ xem **Sub-Flow 5**.
  - **Khóa tài khoản Khách thuê (Tenant):** Khách thuê vẫn được phép đăng nhập để xem và thanh toán tiền hợp đồng/hóa đơn hiện tại nhằm đảm bảo nghĩa vụ tài chính. Chi tiết xử lý quyền hạn hợp đồng khi khóa tài khoản Khách thuê xem **Sub-Flow 5**.

---

### Sub-Flow 3: Phê Duyệt Bất Động Sản & Xác Minh Sổ Đỏ / Giấy Tờ Đất

Admin thực hiện kiểm tra tay hồ sơ pháp lý bất động sản (Tòa nhà / Dãy trọ) do Chủ trọ đăng ký để phòng tránh rủi ro gian lận, tranh chấp và bảo vệ quyền lợi người thuê.

```mermaid
flowchart TD
    StartPropAudit([Vào Phê duyệt Bất động sản]) --> LoadPendingProps[Tải danh sách BĐS chờ Admin duyệt]
    LoadPendingProps --> SelectProp[Chọn xem chi tiết một Tòa nhà / Dãy trọ]
    
    SelectProp --> ViewPropDetails[Xem thông tin: Tên BĐS, Địa chỉ, Số tầng, Thông tin Chủ trọ sở hữu]
    ViewPropDetails --> InspectLegalDoc[Mở xem ảnh tài liệu pháp lý: Sổ đỏ / Giấy tờ đất / HĐ ủy quyền]
    
    InspectLegalDoc --> ManualDecision{Admin kiểm tra tay kết quả?}
    
    %% Phê duyệt thành công
    ManualDecision -->|Giấy tờ hợp lệ & Địa chỉ chuẩn xác| ApproveBuilding[Cập nhật trạng thái BĐS: Phê duyệt / Kích hoạt]
    ApproveBuilding --> WritePropAudit1[Ghi Audit Log: Admin đã phê duyệt tài sản]
    WritePropAudit1 --> NotifyLandlordPass[Gửi thông báo thành công cho Chủ trọ: Mở khóa vận hành cho thuê]
    NotifyLandlordPass --> LoadPendingProps
    
    %% Từ chối phê duyệt
    ManualDecision -->|Giấy tờ giả mạo / Không rõ ràng / Sai địa chỉ| RejectBuilding[Cập nhật trạng thái BĐS: Từ chối]
    RejectBuilding --> InputRejectReason[Admin nhập lý do từ chối cụ thể: vd ảnh sổ đỏ mờ, địa chỉ không khớp]
    InputRejectReason --> WritePropAudit2[Ghi Audit Log: Admin đã từ chối tài sản]
    WritePropAudit2 --> NotifyLandlordFail[Gửi thông báo kèm lý do cho Chủ trọ yêu cầu bổ sung giấy tờ]
    NotifyLandlordFail --> LoadPendingProps
```

* **Quy tắc kiểm tra bất động sản:**
  - Mọi bất động sản mới tạo bắt buộc phải có ít nhất 1 ảnh chụp giấy tờ pháp lý (Sổ đỏ / Sổ hồng / Giấy chứng nhận quyền sử dụng đất hoặc Giấy ủy quyền quản lý).
  - Khi chưa được Admin phê duyệt, các phòng trong dãy trọ không thể phát hành hợp đồng chính thức và không được hiển thị công khai trên bản đồ tìm kiếm của khách thuê.

---

### Sub-Flow 4: Giám Sát Hoạt Động & Nhật Ký Kiểm Toán (Audit Logs)

Admin theo dõi mọi sự kiện quan trọng trong hệ thống nhằm bảo đảm tính minh bạch, truy vết trách nhiệm và an toàn thông tin.

```mermaid
flowchart TD
    StartAudit([Vào Nhật ký Kiểm toán]) --> LoadLogs[Tải danh sách Audit Logs thời gian thực]
    LoadLogs --> ApplyFilter[Lọc theo: Loại sự kiện, Thời gian, Đối tượng thao tác]
    
    ApplyFilter --> LogAction{Thao tác xem}
    LogAction -->|Xem chi tiết sự kiện| ViewPayload[Xem chi tiết thay đổi trước và sau]
    
    ViewPayload --> LoadLogs
```

* **Các sự kiện ghi nhận bắt buộc:**
  - Admin khóa hoặc mở khóa tài khoản người dùng.
  - Admin phê duyệt hoặc từ chối tài sản / dãy trọ (Sổ đỏ / Giấy tờ đất).
  - Lịch sử callback hoặc webhook giao dịch thanh toán từ cổng ngân hàng.

---

### Sub-Flow 5: Xử Lý Vòng Đời Hợp Đồng Khi Tài Khoản Bị Khóa / Mở Khóa

Luồng xử lý tự động liên quan đến hợp đồng thuê khi Admin thực hiện khóa hoặc mở khóa tài khoản người dùng. Đảm bảo quyền lợi tài chính của cả Chủ trọ và Khách thuê trong quá trình xử lý vi phạm.

```mermaid
flowchart TD
    Trigger([Kích hoạt: Sub-Flow 2 gọi xử lý HĐ]) --> CheckTarget{Loại tài khoản bị xử lý?}

    %% ─── LANDLORD ───
    CheckTarget -->|Chủ trọ Landlord| CheckActionLL{Hành động?}

    CheckActionLL -->|Khóa tài khoản| FreezeLL[Đặt trạng thái tất cả HĐ đang hiệu lực: Tạm ngưng]
    FreezeLL --> NotifyHDFreeze[Gửi thông báo cho cả Chủ trọ & Khách thuê: HĐ bị tạm ngưng]
    NotifyHDFreeze --> StartCountdown[Bắt đầu đếm thời gian Grace Period]
    StartCountdown --> CountdownCheck{Đến hạn Grace Period?}

    CountdownCheck -->|Chưa hết hạn & Chủ trọ đã được mở khóa| RestoreLL[Hủy trạng thái Tạm ngưng, khôi phục HĐ về Đang hoạt động]
    RestoreLL --> NotifyHDRestore[Gửi thông báo: HĐ được khôi phục] --> EndTrigger([Kết thúc])

    CountdownCheck -->|Hết hạn & chưa được mở khóa| AutoCancelLL[Hủy tự động HĐ: Chuyển trạng thái Đã hủy]
    AutoCancelLL --> RefundDeposit[Tra cứu khoản đặt cọc: Xử lý hoàn tiền theo điều khoản HĐ]
    RefundDeposit --> NotifyHDCancel[Gửi thông báo hủy HĐ cho cả hai bên kèm lý do]
    NotifyHDCancel --> AuditHDCancel[Ghi Audit Log: HĐ tự động hủy do Chủ trọ bị khóa quá hạn] --> EndTrigger

    CheckActionLL -->|Mở khóa tài khoản| CheckHDFreeze{Có HĐ đang Tạm ngưng?}
    CheckHDFreeze -->|Không| EndTrigger
    CheckHDFreeze -->|Có| PromptRestoreLL{Chủ trọ muốn xử lý?}
    PromptRestoreLL -->|Khôi phục HĐ| RestoreLL
    PromptRestoreLL -->|Hủy HĐ| AutoCancelLL

    %% ─── TENANT ───
    CheckTarget -->|Khách thuê Tenant| CheckActionTT{Hành động?}

    CheckActionTT -->|Khóa tài khoản| RestrictTT[Chặn quyền: Gia hạn HĐ, Thuê phòng mới, Tạo HĐ mới]
    RestrictTT --> AllowPayTT[Giữ nguyên quyền: Đăng nhập xem & thanh toán HĐ/Hóa đơn hiện tại]
    AllowPayTT --> NotifyTTRestrict[Gửi thông báo cho Khách thuê: Phạm vi quyền hạn bị giới hạn] --> EndTrigger

    CheckActionTT -->|Mở khóa tài khoản| RestoreTT[Khôi phục toàn bộ quyền hạn gia hạn & thuê phòng mới]
    RestoreTT --> NotifyTTRestore[Gửi thông báo: Quyền hạn được khôi phục đầy đủ] --> EndTrigger
```

* **Quy tắc xử lý hợp đồng khi khóa/mở khóa:**
  - **Khóa Chủ trọ (Landlord):** Tất cả hợp đồng thuê đang hiệu lực chuyển sang trạng thái tạm ngưng. Khách thuê vẫn có thể đăng nhập để xem và thanh toán hóa đơn hiện tại nhằm đảm bảo nghĩa vụ tài chính. Nếu qua thời gian Grace Period mà chủ trọ chưa được mở khóa, hợp đồng tự động bị hủy và hệ thống thực hiện tra cứu khoản đặt cọc để xử lý hoàn tiền theo điều khoản hợp đồng.
  - **Khóa Khách thuê (Tenant):** Khách thuê bị chặn quyền gia hạn hợp đồng, thuê phòng mới và tạo hợp đồng mới. Vẫn được phép đăng nhập để xem và thanh toán hợp đồng/hóa đơn hiện tại.
  - **Mở khóa:** Khi tài khoản được khôi phục, quyền hạn hợp đồng liên quan cũng được khôi phục theo tương ứng. Chủ trọ tự bổ sung dữ liệu phát sinh trong thời gian bị khóa.
