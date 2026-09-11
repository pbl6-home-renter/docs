# User Flow — Admin

Tài liệu User Flow hoàn chỉnh cho vai trò **Quản trị viên (Admin)** trong hệ thống Rentify (PBL6). Hệ thống vận hành với **duy nhất 1 tài khoản Admin** chịu trách nhiệm giám sát toàn sàn, quản lý người dùng, kiểm tra tay và phê duyệt tài sản (Sổ đỏ / Giấy tờ đất), cấu hình kỹ thuật và theo dõi nhật ký kiểm toán.

---

## 1. Nguyên Tắc Quản Trị Cốt Lõi

1. **Một Admin Duy Nhất (Single Admin System):**
   * Hệ thống chỉ có **duy nhất 1 tài khoản Admin** quản trị toàn bộ nền tảng.
   * Hoàn toàn không có phân cấp Super Admin hay Sub-Admin, không có chức năng tạo thêm hoặc quản lý đội ngũ Admin khác.
2. **Vai Trò Bất Biến (Immutable Role) — KHÔNG CHO PHÉP ĐỔI ROLE:**
   * `User.role` là Enum đơn lẻ: `ADMIN` | `LANDLORD` | `TENANT`.
   * **Quy tắc bất biến:** Một tài khoản sau khi đăng ký hoặc khởi tạo **TUYỆT ĐỐI KHÔNG THỂ ĐỔI ROLE** dưới bất kỳ hình thức nào.
   * Admin không có chức năng đổi role cho người dùng. Nếu người dùng muốn tham gia vai trò khác (ví dụ: Khách thuê muốn làm Chủ trọ), bắt buộc phải đăng ký tài khoản mới riêng biệt.
3. **Kiểm Tra Tay & Phê Duyệt Tài Sản / Dãy Trọ (Sổ Đỏ / Giấy Tờ Đất):**
   * Khi Chủ trọ (Landlord) tạo mới một tài sản (Tòa nhà / Dãy trọ), hệ thống bắt buộc Chủ trọ phải tải lên ảnh bằng chứng sở hữu (Sổ đỏ, Giấy chứng nhận quyền sử dụng đất hoặc Hợp đồng ủy quyền hợp pháp).
   * Tài sản mới tạo sẽ ở trạng thái chờ duyệt (`PENDING_APPROVAL`).
   * **Admin trực tiếp kiểm tra tay (manual review)** đối soát tính xác thực của giấy tờ và thông tin địa chỉ trước khi ra quyết định Phê duyệt (`APPROVED`) để kích hoạt hoạt động cho thuê hoặc Từ chối (`REJECTED`) kèm lý do rõ ràng.
4. **Phạm Vi Cấu Hình Của Admin (Chỉ Cấp Hệ Thống):**
   * Admin chỉ cấu hình các tham số kỹ thuật tầng nền tảng:
     - **Mock Payment Gateway (R1):** Bật/tắt chế độ thanh toán giả lập phục vụ kiểm thử và demo.
     - **AI Provider Adapter (D3):** Lựa chọn nhà cung cấp AI (`OpenAI` hoặc `Gemini`) và hạn mức API.
   * *Lưu ý:* Cấu hình ngày chốt tiền, chu kỳ hóa đơn và **quét nợ tiền trọ thuộc toàn quyền của từng Chủ trọ (Landlord)**, Admin tuyệt đối không can thiệp.

---

## 2. Tổng Quan Điều Hướng (Admin Navigation Hub)

```mermaid
flowchart TD
    StartAdmin([Bắt đầu: Admin truy cập Portal]) --> InputAuth[Nhập Email & Mật khẩu Admin]
    InputAuth --> CheckAdminAuth{Xác thực thông tin & User.role == ADMIN?}
    
    CheckAdminAuth -->|Thất bại| AuthErr[Báo lỗi sai thông tin đăng nhập] --> InputAuth
    CheckAdminAuth -->|Đúng nhưng bị khóa| LockedErr[Báo lỗi: Tài khoản Admin bị vô hiệu hóa] --> EndAdminFail([Dừng])
    CheckAdminAuth -->|Thành công| AdminDash[Admin Dashboard Tổng quan]
    
    AdminDash --> NavChoice{Chọn phân hệ quản trị}
    
    NavChoice -->|1. Quản lý Người dùng & eKYC| SubUser[Danh sách Người dùng: Landlord / Tenant]
    NavChoice -->|2. Phê duyệt Bất động sản| SubProperty[Kiểm tra Sổ đỏ / Giấy tờ đất Dãy trọ]
    NavChoice -->|3. Cấu hình Tham số Kỹ thuật| SubConfig[Cấu hình: Mock Payment & AI Provider]
    NavChoice -->|4. Giám sát & Audit Logs| SubLogs[Nhật ký hệ thống & Cảnh báo bất thường]
    NavChoice -->|5. Đăng xuất| AdminLogout[Đăng xuất an toàn]
    
    SubUser --> RetDash1[Quay về Dashboard] --> AdminDash
    SubProperty --> RetDash2[Quay về Dashboard] --> AdminDash
    SubConfig --> RetDash3[Quay về Dashboard] --> AdminDash
    SubLogs --> RetDash4[Quay về Dashboard] --> AdminDash
    
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
    
    SubmitLogin --> VerifyDB{Kiểm tra CSDL User}
    VerifyDB -->|Không khớp thông tin| FailAuth[Báo lỗi: Sai tài khoản hoặc mật khẩu] --> InputCreds
    
    VerifyDB -->|Khớp thông tin| CheckRole{Kiểm tra User.role == 'ADMIN'?}
    CheckRole -->|role != ADMIN| Deny403[Báo lỗi 403: Không có quyền quản trị] --> EndDeny([Dừng])
    
    CheckRole -->|role == ADMIN| IssueToken[Cấp JWT Token Quản trị viên]
    IssueToken --> EnterDash[Vào Admin Dashboard] --> EndAuthSuccess([Đăng nhập Admin thành công])
```

---

### Sub-Flow 2: Quản Lý Người Dùng & Phê Duyệt eKYC

Admin theo dõi danh sách toàn bộ người dùng trong hệ thống (đồng nhất vai trò Chủ trọ — Landlord, không phân tách chủ phòng hay chủ tòa nhà, và Khách thuê — Tenant). Admin có quyền xem chi tiết hồ sơ, duyệt CCCD (eKYC), hoặc khóa/mở khóa tài khoản vi phạm. **Tuyệt đối không có chức năng đổi role.**

```mermaid
flowchart TD
    StartUserMgmt([Vào Quản lý Người dùng]) --> ViewList[Xem danh sách: Lọc theo Role, KYC, Trạng thái hoạt động]
    ViewList --> SearchUser[Tìm kiếm theo Tên, Email, SĐT, Role]
    SearchUser --> SelectUser[Chọn xem chi tiết hồ sơ người dùng]
    
    SelectUser --> UserAction{Thao tác quản trị}
    
    %% Nhánh 1: Khóa tài khoản vi phạm
    UserAction -->|Khóa tài khoản vi phạm| CheckLockRole{Đối tượng bị khóa?}
    
    CheckLockRole -->|Khóa Chủ trọ Landlord| LockLL[Vô hiệu hóa tài khoản Chủ trọ: Ẩn toàn bộ BĐS/Phòng khỏi hệ thống]
    LockLL --> FreezeContracts[Hợp đồng đang hiệu lực chuyển trạng thái: 'Tạm thời kết thúc' - suspended]
    FreezeContracts --> AutoExpireCheck[Nếu đến ngày hết hạn HĐ mà chưa được mở khóa: HĐ tự động hủy]
    AutoExpireCheck --> AuditLockLL[Ghi Audit Log: Khóa Chủ trọ & Đóng băng tài sản] --> ViewList
    
    CheckLockRole -->|Khóa Khách thuê Tenant| LockTenant[Vô hiệu hóa quyền hạn Khách thuê]
    LockTenant --> RestrictTenant[Vẫn cho phép thanh toán HĐ/Hóa đơn hiện tại - Chặn gia hạn & Chặn thuê phòng mới]
    RestrictTenant --> AuditLockTT[Ghi Audit Log: Khóa Khách thuê với quyền thanh toán hạn chế] --> ViewList
    
    %% Nhánh 2: Mở khóa tài khoản
    UserAction -->|Mở khóa tài khoản| UnlockAccount[Cập nhật User.isActive = true]
    UnlockAccount --> CheckUnlockRole{Đối tượng được mở khóa?}
    CheckUnlockRole -->|Mở khóa Chủ trọ| RestoreLL[Khôi phục hiển thị BĐS & HĐ còn hạn - Chủ trọ tự bổ sung dữ liệu trong thời gian khóa]
    CheckUnlockRole -->|Mở khóa Khách thuê| RestoreTT[Khôi phục toàn bộ quyền gia hạn và tìm phòng mới]
    RestoreLL --> AuditUnlock[Ghi nhận Audit Log: Mở khóa tài khoản] --> ViewList
    RestoreTT --> AuditUnlock
    
    %% Nhánh 3: Đối soát & Phê duyệt eKYC (CCCD)
    UserAction -->|Xử lý hồ sơ eKYC| ReviewCCCD[Đối soát ảnh 2 mặt CCCD và thông tin cá nhân]
    ReviewCCCD --> DecisionKYC{Quyết định phê duyệt?}
    
    DecisionKYC -->|Thông tin chuẩn xác| ApproveKYC[Cập nhật trạng thái KYC: 'APPROVED']
    DecisionKYC -->|Ảnh mờ hoặc sai lệch| RejectKYC[Cập nhật trạng thái KYC: 'REJECTED' kèm lý do]
    
    ApproveKYC --> AuditKYC1[Ghi nhận Audit Log & Gửi thông báo đến người dùng] --> ViewList
    RejectKYC --> AuditKYC2[Ghi nhận Audit Log & Gửi thông báo đến người dùng] --> ViewList
```

* **Quy tắc khóa và mở khóa tài khoản:**
  - **Khóa tài khoản Chủ trọ (Landlord):** Toàn bộ thông tin dãy trọ và phòng trọ của chủ trọ sẽ bị vô hiệu hóa (ẩn hoàn toàn khỏi hệ thống tìm kiếm công khai). Các hợp đồng thuê đang có hiệu lực chuyển sang trạng thái tạm thời kết thúc (`suspended`). Đến ngày hết hạn hợp đồng mà chủ trọ chưa được mở khóa thì hợp đồng sẽ tự động bị hủy. Khi chủ trọ khắc phục vi phạm và được Admin mở khóa, bất động sản sẽ hiển thị lại trên hệ thống và các thông tin phát sinh trong thời gian bị khóa sẽ do chủ trọ tự bổ sung lại.
  - **Khóa tài khoản Khách thuê (Tenant):** Khách thuê vẫn được phép đăng nhập để xem và thanh toán tiền hợp đồng/hóa đơn hiện tại nhằm đảm bảo nghĩa vụ tài chính, nhưng tuyệt đối không thể gia hạn hợp đồng hiện tại và không thể thuê trọ mới hay tạo hợp đồng mới trên sàn.
  - **Đồng nhất vai trò:** Không phân biệt chủ phòng hay chủ tòa nhà, toàn bộ thống nhất thành một vai trò duy nhất là **Chủ trọ (Landlord)**.


---

### Sub-Flow 3: Phê Duyệt Bất Động Sản & Xác Minh Sổ Đỏ / Giấy Tờ Đất

Admin thực hiện kiểm tra tay hồ sơ pháp lý bất động sản (Tòa nhà / Dãy trọ) do Chủ trọ đăng ký để phòng tránh rủi ro gian lận, tranh chấp và bảo vệ quyền lợi người thuê.

```mermaid
flowchart TD
    StartPropAudit([Vào Phê duyệt Bất động sản]) --> LoadPendingProps[Tải danh sách BĐS chờ duyệt: status = 'PENDING_APPROVAL']
    LoadPendingProps --> SelectProp[Chọn xem chi tiết một Tòa nhà / Dãy trọ]
    
    SelectProp --> ViewPropDetails[Xem thông tin: Tên BĐS, Địa chỉ, Số tầng, Thông tin Chủ trọ sở hữu]
    ViewPropDetails --> InspectLegalDoc[Mở xem ảnh tài liệu pháp lý: Sổ đỏ / Giấy tờ đất / HĐ ủy quyền]
    
    InspectLegalDoc --> ManualDecision{Admin kiểm tra tay kết quả?}
    
    %% Phê duyệt thành công
    ManualDecision -->|Giấy tờ hợp lệ & Địa chỉ chuẩn xác| ApproveBuilding[Cập nhật trạng thái BĐS: 'APPROVED' / 'ACTIVE']
    ApproveBuilding --> WritePropAudit1[Ghi Audit Log: Admin đã phê duyệt tài sản]
    WritePropAudit1 --> NotifyLandlordPass[Gửi thông báo thành công cho Chủ trọ: Mở khóa vận hành cho thuê]
    NotifyLandlordPass --> LoadPendingProps
    
    %% Từ chối phê duyệt
    ManualDecision -->|Giấy tờ giả mạo / Không rõ ràng / Sai địa chỉ| RejectBuilding[Cập nhật trạng thái BĐS: 'REJECTED']
    RejectBuilding --> InputRejectReason[Admin nhập lý do từ chối cụ thể: vd ảnh sổ đỏ mờ, địa chỉ không khớp]
    InputRejectReason --> WritePropAudit2[Ghi Audit Log: Admin đã từ chối tài sản]
    WritePropAudit2 --> NotifyLandlordFail[Gửi thông báo kèm lý do cho Chủ trọ yêu cầu bổ sung giấy tờ]
    NotifyLandlordFail --> LoadPendingProps
```

* **Quy tắc kiểm tra bất động sản:**
  - Mọi bất động sản mới tạo bắt buộc phải có ít nhất 1 ảnh chụp giấy tờ pháp lý (Sổ đỏ / Sổ hồng / Giấy chứng nhận quyền sử dụng đất hoặc Giấy ủy quyền quản lý).
  - Khi chưa được Admin phê duyệt (`status != 'APPROVED'`), các phòng trong dãy trọ không thể phát hành hợp đồng chính thức và không được hiển thị công khai trên bản đồ tìm kiếm của khách thuê.

---

### Sub-Flow 4: Cấu Hình Tham Số Kỹ Thuật Hệ Thống

Quản lý các tham số vận hành tầng nền tảng dành riêng cho Quản trị viên (Toggle Mock Payment và AI Provider Adapter).

```mermaid
flowchart TD
    StartConfig([Vào Cấu hình Kỹ thuật]) --> ViewSettings[Xem danh sách tham số hệ thống hiện tại]
    ViewSettings --> ChooseSetting{Chọn tham số điều chỉnh}
    
    ChooseSetting -->|Toggle Mock Payment R1| ToggleMock[Bật / Tắt chế độ Mock cổng thanh toán]
    ChooseSetting -->|AI Provider Adapter D3| SwitchAI[Chọn nhà cung cấp AI: OpenAI hoặc Gemini]
    
    ToggleMock --> SaveConfig[Lưu cấu hình hệ thống]
    SwitchAI --> SaveConfig
    
    SaveConfig --> WriteConfigAudit[Ghi Audit Log: Admin cập nhật cấu hình kỹ thuật]
    WriteConfigAudit --> EndConfig([Áp dụng tham số mới thành công])
```

---

### Sub-Flow 5: Giám Sát Hoạt Động & Nhật Ký Kiểm Toán (Audit Logs)

Admin theo dõi mọi sự kiện quan trọng trong hệ thống nhằm bảo đảm tính minh bạch, truy vết trách nhiệm và an toàn thông tin.

```mermaid
flowchart TD
    StartAudit([Vào Nhật ký Kiểm toán]) --> LoadLogs[Tải danh sách Audit Logs thời gian thực]
    LoadLogs --> ApplyFilter[Lọc theo: Loại sự kiện, Thời gian, Đối tượng thao tác]
    
    ApplyFilter --> LogAction{Thao tác xem}
    LogAction -->|Xem chi tiết sự kiện| ViewPayload[Xem chi tiết payload thay đổi trước và sau]
    LogAction -->|Xuất báo cáo| ExportData[Xuất file báo cáo audit dạng CSV/Excel]
    
    ViewPayload --> LoadLogs
    ExportData --> EndAudit([Hoàn tất phiên giám sát])
```

* **Các sự kiện ghi nhận bắt buộc:**
  - Admin khóa hoặc mở khóa tài khoản người dùng.
  - Admin phê duyệt hoặc từ chối hồ sơ eKYC.
  - Admin phê duyệt hoặc từ chối tài sản / dãy trọ (Sổ đỏ / Giấy tờ đất).
  - Admin thay đổi tham số cấu hình hệ thống (Mock Payment, AI Adapter).
  - Lịch sử callback hoặc webhook giao dịch thanh toán từ cổng ngân hàng.
