# Landlord User Flow — PBL6

Tài liệu User Flow hoàn chỉnh cho vai trò **Chủ trọ (Landlord)** trong hệ thống Rentify (PBL6). Luồng thiết kế phản ánh góc nhìn quản trị thực tế của Chủ trọ: phân hệ **Quản lý Phòng** là trung tâm chứa **Menu Tiện ích**, **Sự cố được tách thành Tab riêng**, quy trình thanh toán linh hoạt cho **mọi thành viên trong phòng**.

---

## 1. Nguyên Tắc Nghiệp Vụ Cốt Lõi

1. **Góc Nhìn Quản Trị Của Chủ Trọ (Landlord Viewpoint):**
   * **Tiện ích nằm ở Quản lý Phòng:** Toàn bộ các công cụ vận hành (Quản lý thành viên, Chốt số điện nước, Xuất hóa đơn, Thanh lý phòng) được đặt trực tiếp trong **Menu Tiện ích** của từng Phòng trọ.
   * **Tab Sự Cố Riêng:** Phân hệ Sự cố được tách thành một **Tab độc lập** trên thanh điều hướng chính giúp Chủ trọ theo dõi, lọc trạng thái và điều phối sửa chữa tập trung cho toàn bộ các tòa nhà.
2. **Ai Trong Phòng Cũng Có Thể Thanh Toán:**
   * Hóa đơn và mã VietQR động được tạo cho phòng. **Bất kỳ thành viên nào** trong phòng đều có thể quét QR thanh toán hoặc nộp tiền mặt. Khi có khoản nộp được xác nhận, hệ thống tự động gạch nợ cho phòng.
3. **Linh Hoạt Thành Viên:**
   * Hệ thống không ép buộc giới hạn số người cứng. Chủ trọ có thể thêm bao nhiêu thành viên ở ghép tùy ý. Thành viên rời đi cần có sự phê duyệt của Chủ trọ (chủ trọ thực hiện thao tác xóa).
4. **Trao Đổi Tự Nhiên Trong Chat:**
   * Trong khung chat, cư dân và chủ trọ trao đổi tự nhiên bằng text, ảnh và file. Mọi báo cáo sự cố được đồng bộ và quản lý tập trung tại Tab Sự Cố riêng.
5. **Cấu Hình Quét Nợ & Chu Kỳ Quy Về Từng Tháng:**
   * Chủ trọ tự quyết định ngày chốt điện nước, hạn đóng tiền và bật/tắt lịch bot tự động quét nợ định kỳ để nhắc nhở phòng trọ. Cấu hình có thể设置 ở cấp profile, building hoặc room.
   * **Chu kỳ thanh toán chuẩn hóa theo từng tháng:** Mọi hóa đơn và khoản thu trên hệ thống đều được quy về từng tháng.
6. **Gộp Chi Phí Vào Danh Mục Dịch Vụ & Quy Định Chụp/Tải Ảnh Công Tơ:**
   * Gộp chung toàn bộ chi phí điện, nước, wifi, máy giặt chung, tiền rác... vào một danh mục duy nhất là **Dịch vụ**.
   * **Cả Chủ trọ và Khách thuê đều dùng được Camera trong hệ thống:** Hai bên đều có thể mở Camera trong app chụp trực tiếp tại chỗ ảnh đồng hồ điện nước.
   * **Chủ trọ có quyền chụp hoặc tải ảnh từ máy lên:** Chủ trọ có cả 2 quyền: chụp trực tiếp bằng Camera và tải ảnh có sẵn từ bộ nhớ thiết bị. Khách thuê chỉ được chụp trực tiếp qua Camera.
7. **Hợp Đồng Ký Tay Wet-Sign & Lưu Trữ (Archive):**
   * Hỗ trợ in mẫu hợp đồng giấy ký sống (wet-sign), sau đó tải file lên lưu trữ.
   * **Trạng thái chờ dọn dẹp sau Checkout:** Sau khi khách trả phòng, phòng trọ chuyển sang trạng thái chờ dọn dẹp. Chỉ khi chủ trọ hoàn tất và xác nhận sẵn sàng thì phòng mới chuyển sang sẵn sàng cho thuê.
   * Hội thoại cũ được lưu trữ (Archive) và khởi tạo kênh mới cho khách tiếp theo.
8. **Tải Lên Bằng Chứng Sở Hữu (Sổ Đỏ / Giấy Tờ Đất) Khi Tạo Dãy Trọ:**
   * Khi Chủ trọ tạo mới Tòa nhà / Dãy trọ, bắt buộc phải tải lên ảnh chụp giấy tờ pháp lý (Sổ đỏ, Giấy chứng nhận quyền sử dụng đất hoặc Hợp đồng ủy quyền hợp pháp).
   * Bất động sản mới tạo ở trạng thái chờ Admin duyệt và cần được Admin kiểm tra tay phê duyệt trước khi mở quyền đăng phòng cho thuê công khai.
9. **Đồng Nhất Vai Trò Quản Lý:**
   * Thống nhất toàn bộ thành một vai trò duy nhất là **Chủ trọ (Landlord)** sở hữu/quản lý Dãy trọ và các Phòng trọ bên trong, không phân tách phức tạp giữa chủ phòng hay chủ tòa nhà.

---

## 2. Tổng Quan Điều Hướng (Landlord Navigation Hub)

```mermaid
flowchart TD
    StartLL([Chủ trọ Đăng Nhập: Email & Mật khẩu]) --> HomeLL[Landlord Dashboard]
    HomeLL --> MainNav{Chọn phân hệ quản lý}
    
    MainNav -->|1. Dashboard| TabDash[Xem Doanh thu, Công nợ & Room Map]
    MainNav -->|2. Quản lý Phòng & BĐS| TabProp[Quản lý Tòa nhà, Phòng trọ & Menu Tiện Ích Phòng]
    MainNav -->|3. Sự cố riêng| TabIssues[Tab Sự Cố: Quản lý & Điều phối sửa chữa tập trung]
    MainNav -->|4. Chat Hub| TabChat[Property Chat Hub: Kênh trao đổi cư dân]
    MainNav -->|5. Cài đặt| TabSettings[Cấu hình Đơn giá & Quét Nợ]
    MainNav -->|6. Đăng xuất| LogoutLL[Đăng xuất an toàn]
```

---

## 3. Các Luồng Nghiệp Vụ Chi Tiết (Sub-Flows)

### Sub-Flow 1: Quản Lý Bất Động Sản & Phòng Trọ (Kèm Menu Tiện Ích)

Chủ trọ tạo mới Tòa nhà / Dãy trọ, tải lên bằng chứng quyền sở hữu (Sổ đỏ / Giấy tờ đất) gửi Admin kiểm tra tay, và quản lý danh sách phòng. Trong mỗi phòng tích hợp sẵn **Menu Tiện ích**.

```mermaid
flowchart TD
    StartProp([Vào Quản lý BĐS & Phòng]) --> ChoosePropAction{Chọn thao tác}
    
    %% Nhánh 1: Thêm Tòa nhà / Dãy trọ (Yêu cầu Sổ đỏ / Giấy tờ đất)
    ChoosePropAction -->|Thêm Dãy trọ / Tòa nhà| FormBld[Nhập Tên dãy trọ, Địa chỉ, Số tầng]
    FormBld --> UploadLandProof[Tải lên ảnh Sổ đỏ / Giấy chứng nhận QSDĐ / Giấy ủy quyền]
    UploadLandProof --> SetDefaultRates[Cấu hình đơn giá điện nước mặc định của Tòa nhà]
    SetDefaultRates --> SaveBld[Lưu BĐS: Trạng thái Chờ Admin duyệt]
    
    SaveBld --> WaitAdminAudit[Chờ Admin kiểm tra tay giấy tờ đất]
    WaitAdminAudit -->|Admin Phê duyệt| BldActive[BĐS kích hoạt: Mở khóa cho thuê]
    WaitAdminAudit -->|Admin Từ chối| BldReject[Báo lỗi kèm lý do từ chối: Yêu cầu bổ sung giấy tờ]
    
    %% Nhánh 2: Thêm Phòng trọ
    ChoosePropAction -->|Thêm Phòng mới| CheckBldActive{Dãy trọ đã được Admin duyệt?}
    CheckBldActive -->|Chưa duyệt / Bị từ chối| BlockRoomCreate[Báo lỗi: Cần chờ Admin duyệt dãy trọ trước khi thêm phòng]
    CheckBldActive -->|Đã được Admin duyệt| FormRoom[Chọn Tòa nhà & Tầng]
    FormRoom --> InputRoomSpecs[Nhập Số phòng, Diện tích, Giá thuê]
    InputRoomSpecs --> SetOptionalRules[Cài đặt quy tắc tùy chọn: Giới tính, Tiện nghi]
    SetOptionalRules --> SaveRoom[Tạo phòng: Trạng thái sẵn sàng cho thuê]
    
    %% Mở Tiện ích phòng
    ChoosePropAction -->|Chọn một Phòng cụ thể| RoomCard[Mở Chi tiết Phòng]
    RoomCard --> RoomMenu{Phòng có hợp đồng đang hoạt động?}
    RoomMenu -->|Có| ShowMenu[Menu Tiện Ích Phòng: Thành viên, Chốt số, Hóa đơn, Chat, Thanh lý]
    RoomMenu -->|Chưa có hợp đồng| ShowBasic[Chỉ hiển thị: Thêm hợp đồng]
```

---

### Sub-Flow 2: Tạo Hợp Đồng Thuê & Check-in

Đón khách mới: nhập thông tin người thuê, chọn mẫu hợp đồng (tùy chọn), in hợp đồng giấy ký sống, tải file lên lưu trữ, kích hoạt phòng.

```mermaid
flowchart TD
    StartContract([Chọn phòng trống sẵn sàng cho thuê]) --> FormContract[Mở Form Tạo Hợp Đồng]
    FormContract --> InputTenant[Nhập thông tin người thuê: Họ tên, SĐT, CCCD, Địa chỉ]
    InputTenant --> InputTerms[Nhập Tiền cọc, Tiền thuê, Ngày bắt đầu & Thời hạn HĐ]
    
    InputTerms --> ChooseTemplate{Chọn mẫu hợp đồng?}
    ChooseTemplate -->|Bỏ qua| PrintTemplate[Xuất file mẫu HĐ chuẩn PDF điền sẵn]
    ChooseTemplate -->|Chọn mẫu| SelectTemplate[Chọn mẫu HĐ có sẵn trong hệ thống] --> PrintTemplate
    
    PrintTemplate --> DownloadSign[Người dùng tải file xuống, in, ký tay trên giấy thật]
    DownloadSign --> UploadSigned[Tải file lên lưu trữ: chấp nhận ảnh, doc hoặc pdf]
    
    UploadSigned --> ActivateContract[HĐ chuyển trạng thái Đang hoạt động - Phòng sang Đang cho thuê]
    ActivateContract --> CreateRoomChat[Tự động tạo Kênh Chat riêng cho phòng & nạp thành viên]
    CreateRoomChat --> EndCheckin([Hoàn tất bàn giao phòng])
```

---

### Sub-Flow 3: Quản Lý Thành Viên Phòng & Biến Động Giữa Kỳ (Từ Tiện Ích Phòng)

Chủ trọ mở **Menu Tiện ích trong Quản lý Phòng** để thêm/bớt người ở ghép.

```mermaid
flowchart TD
    StartMember([Quản lý Phòng -> Chọn Menu Tiện ích: Thành viên]) --> ViewMembers[Xem danh sách thành viên hiện tại của phòng]
    ViewMembers --> MemberAction{Chọn thao tác}
    
    %% Thêm người ở ghép
    MemberAction -->|Thêm người ở ghép mới| InputNewMember[Nhập Họ tên, SĐT & CCCD người mới]
    InputNewMember --> AddToSystem[Thêm vào hệ thống & tự động add vào Chat phòng]
    AddToSystem --> BotMsgNew[Bot thông báo thành viên mới vào kênh Chat] --> ViewMembers
    
    %% Xóa thành viên rời đi
    MemberAction -->|Xóa thành viên rời đi| SelectRemove[Chọn thành viên cần xóa]
    SelectRemove --> ConfirmRemove{Chủ trọ xác nhận xóa?}
    ConfirmRemove -->|Hủy| ViewMembers
    ConfirmRemove -->|Xác nhận| RemoveMember[Xóa thành viên khỏi phòng & rút khỏi Chat]
    RemoveMember --> BotMsgLeave[Bot thông báo thành viên đã rời phòng] --> ViewMembers
```

---

### Sub-Flow 4: Chốt Số Điện/Nước & Lập Hóa Đơn (Từ Tiện Ích Phòng)

Hệ thống tích hợp Camera chụp trực tiếp cho cả Chủ trọ và Khách thuê. Chủ trọ có quyền chụp hoặc tải ảnh từ máy lên. Sau khi chốt số, chủ trọ lập hóa đơn và phát hành cho phòng.

```mermaid
flowchart TD
    %% Chốt số điện nước
    StartMeter([Tiện ích Chốt số điện nước]) --> SelectCaptureMethod{Nguồn cung cấp ảnh công tơ}
    
    SelectCaptureMethod -->|Chụp trực tiếp bằng Camera trong app| LiveCamera[Camera chụp tại chỗ]
    SelectCaptureMethod -->|Tải ảnh có sẵn từ máy| UploadFromStorage[Upload từ bộ nhớ/thư viện ảnh]
    
    LiveCamera --> RunOCR[AI OCR tự động nhận diện chỉ số từ ảnh công tơ]
    UploadFromStorage --> RunOCR
    
    RunOCR --> ReviewIndex{Chủ trọ kiểm tra kết quả?}
    ReviewIndex -->|Chưa chuẩn| EditManual[Sửa lại số bằng tay]
    ReviewIndex -->|Chính xác| ConfirmIndex[Bấm Xác nhận 1 chạm]
    EditManual --> ConfirmIndex
    
    ConfirmIndex --> SaveMeterDB[Lưu bản ghi chốt số kỳ hiện tại]
    
    %% Lập hóa đơn
    SaveMeterDB --> CalcAmount[Tính toán chuẩn hóa theo tháng: Tiền phòng + Danh mục Dịch vụ]
    CalcAmount --> ReviewBill{Chủ trọ xem trước hóa đơn?}
    
    ReviewBill -->|Cần chỉnh sửa| EditBill[Điều chỉnh số liệu] --> CalcAmount
    ReviewBill -->|Hợp lệ| PublishBill[Bấm Phát hành Hóa đơn Tháng]
    
    PublishBill --> GenQR[Sinh mã VietQR động: Gắn mã định danh phòng & đúng số tiền lẻ]
    GenQR --> BotSendBill[Bot gửi Thẻ Hóa Đơn kèm mã VietQR vào Chat phòng]
    
    BotSendBill --> PayMethod{Ai thanh toán & Hình thức nào?}
    
    %% Bất kỳ ai quét VietQR
    PayMethod -->|Bất kỳ thành viên nào trong phòng quét VietQR| BankTransfer[Chuyển khoản qua App Ngân hàng]
    BankTransfer --> WebhookReconcile[Hệ thống nhận Webhook ngân hàng: Khớp mã định danh]
    WebhookReconcile --> AutoGachNo[Hệ thống tự động Gạch Nợ phòng: Hóa đơn chuyển Đã thanh toán]
    
    %% Bất kỳ ai nộp tiền mặt
    PayMethod -->|Bất kỳ thành viên nào nộp Tiền mặt| CashPay[Chủ trọ nhận tiền mặt trực tiếp]
    CashPay --> ConfirmCashBtn[Chủ trọ bấm 'Xác nhận thu tiền mặt' trên hóa đơn]
    ConfirmCashBtn --> AutoGachNo
    
    AutoGachNo --> UpdateFinDash[Cập nhật Doanh thu & Giảm công nợ trên Dashboard]
```

* **Quy định bảo mật chỉ số:** 
  * Cả Chủ trọ và Khách thuê đều có thể dùng Camera trong app để chụp trực tiếp đồng hồ điện nước.
  * Khách thuê **không có quyền tải ảnh từ bộ nhớ máy lên**, chỉ Chủ trọ mới có tính năng này.

* **Nguyên tắc tài chính:**
  * Gộp chung toàn bộ điện, nước, internet/wifi, máy giặt, vệ sinh/rác vào một nhóm duy nhất là **Dịch vụ**.
  * Hóa đơn luôn chốt theo chu kỳ hàng tháng trên hệ thống.

---

### Sub-Flow 5: Cấu Hình Chu Kỳ Hóa Đơn & Quét Nợ Tự Động

Chủ trọ cài đặt hạn thanh toán và lịch nhắc nhở tự động. Cấu hình có thể设置 ở 3 cấp: profile (chung), building (theo tòa nhà) hoặc room (theo phòng cụ thể).

```mermaid
flowchart TD
    StartDebtConfig([Vào Cài đặt]) --> ChooseLevel{Chọn cấp cấu hình?}
    
    ChooseLevel -->|Profile| ProfileConfig[Cấu hình chung cho toàn bộ]
    ChooseLevel -->|Building| BuildingConfig[Chọn tòa nhà cần cấu hình]
    ChooseLevel -->|Room| RoomConfig[Chọn phòng cụ thể cần cấu hình]
    
    ProfileConfig --> SetDueDate[Cài đặt hạn chót thanh toán]
    BuildingConfig --> SetDueDate
    RoomConfig --> SetDueDate
    
    SetDueDate --> SetReminder[Cài đặt ngày nhắc nhở: Nhắc đúng hạn vào ngày đó]
    SetReminder --> SaveSettings[Lưu cấu hình]
    
    SaveSettings --> RunAutoCron[Hệ thống nền chạy quét nợ hàng ngày theo cấu hình]
    
    RunAutoCron --> CheckOverdueBills{Có hóa đơn đến hạn / quá hạn?}
    CheckOverdueBills -->|Không| SleepCron[Kết thúc lượt quét]
    CheckOverdueBills -->|Có| TriggerBotReminder[Bot tự động nhắc nợ vào Chat phòng + Gửi Push Noti]
```

---

### Sub-Flow 6: Quản Lý Sự Cố (Tab Sự Cố Riêng)

Sự cố được quản lý tập trung tại **Tab Sự Cố độc lập** trên thanh điều hướng chính. Cả Khách thuê và Chủ trọ đều có thể tạo sự cố từ Hub Phòng.

```mermaid
flowchart TD
    StartIssue([Phát sinh sự cố hỏng hóc]) --> ReportChannel{Ai tạo sự cố?}
    
    %% Khách thuê tạo từ Hub Phòng
    ReportChannel -->|Khách thuê| TenantReport[Khách thuê vào Hub Phòng -> Báo sự cố: Mô tả + đính kèm ảnh]
    TenantReport --> SyncToIssueTab[Xuất hiện tức thì trong Tab Sự Cố riêng]
    
    %% Chủ trọ tạo từ Hub Phòng
    ReportChannel -->|Chủ trọ| LandlordReport[Chủ trọ vào Chi tiết Phòng -> Tạo sự cố: Mô tả + đính kèm ảnh]
    LandlordReport --> SyncToIssueTab
    
    %% Xử lý tại Tab Sự Cố
    SyncToIssueTab --> ProcessIssue{Chủ trọ cập nhật tiến độ xử lý}
    ProcessIssue -->|Đang sửa chữa| SetProgress[Chuyển trạng thái: Đang xử lý]
    ProcessIssue -->|Đã sửa xong| SetResolved[Chuyển trạng thái: Đã hoàn thành]
    ProcessIssue -->|Hủy sự cố| SetCancelled[Hủy / Xóa bản ghi sự cố]
    
    SetProgress --> UpdateChatNoti[Bot cập nhật thông báo tiến độ vào Chat phòng tương ứng]
    SetResolved --> UpdateChatNoti
    SetCancelled --> UpdateChatNoti
```

---

### Sub-Flow 7: Check-out, Thanh Lý Cọc & Lưu Trữ Hội Thoại (Từ Tiện Ích Phòng)

Quy trình trả phòng khởi động từ **Menu Tiện ích trong Quản lý Phòng**: chốt số cuối, quyết toán cọc, lưu trữ hội thoại cũ (Archive) và chuyển trạng thái phòng sẵn sàng đón khách mới.

```mermaid
flowchart TD
    StartCheckout([Quản lý Phòng -> Chọn Menu Tiện ích: Thanh lý phòng]) --> FinalMeter[Chốt số điện nước lần cuối cùng bằng Camera OCR]
    
    FinalMeter --> FinalInvoice[Lập hóa đơn quyết toán: Tính tiền phòng theo số ngày ở thực tế]
    FinalInvoice --> PayFinalInvoice[Khách thanh toán hóa đơn cuối]
    
    PayFinalInvoice --> InspectDeposit{Khấu trừ tiền cọc?}
    InspectDeposit -->|Có khấu trừ| CalcDeduct[Tiền cọc hoàn lại = Cọc ban đầu - Khấu trừ]
    InspectDeposit -->|Không khấu trừ| FullDeposit[Hoàn trả 100% tiền cọc]
    
    CalcDeduct --> SettleDeposit[Hoàn tiền cọc cho khách]
    FullDeposit --> SettleDeposit
    
    SettleDeposit --> ConfirmRelease[Chủ trọ bấm 'Xác nhận hoàn tất thanh lý & nhận bàn giao']
    
    %% Lưu trữ & trạng thái phòng
    ConfirmRelease --> ArchiveOldChat[Lưu trữ cuộc trò chuyện của HĐ cũ sang trạng thái Read-only]
    ArchiveOldChat --> SetRoomPending[Phòng chuyển sang trạng thái: Chờ dọn dẹp & chuẩn bị]
    SetRoomPending --> CleanAndPrep[Chủ trọ dọn dẹp, kiểm tra cơ sở vật chất và chuẩn bị phòng cho thuê mới]
    CleanAndPrep --> ConfirmReady[Chủ trọ kiểm tra xong và bấm: 'Xác nhận phòng sẵn sàng đón khách']
    ConfirmReady --> ResetRoomAvail[Phòng chính thức chuyển về trạng thái: Sẵn sàng cho thuê trên Room Map]
    
    ResetRoomAvail --> NewTenantCheckin[Khi có khách mới dọn vào ký HĐ mới]
    NewTenantCheckin --> InitNewChat[Hệ thống tạo kênh chat hoàn toàn mới tinh - Khách mới không thấy dữ liệu khách cũ]
```
