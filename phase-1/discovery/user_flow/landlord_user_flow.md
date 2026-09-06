# Landlord User Flow — PBL6

Tài liệu User Flow hoàn chỉnh cho vai trò **Chủ trọ (Landlord)** trong hệ thống Rentify (PBL6). Luồng thiết kế phản ánh góc nhìn quản trị thực tế của Chủ trọ: phân hệ **Quản lý Phòng** là trung tâm chứa **Menu Tiện ích**, hỗ trợ **Chat redirect**, **Sự cố được tách thành Tab riêng**, quy trình thanh toán linh hoạt cho **mọi thành viên trong phòng**, và cơ chế **tag tên/tag phòng** trong hội thoại.

---

## 1. Nguyên Tắc Nghiệp Vụ Cốt Lõi

1. **Góc Nhìn Quản Trị Của Chủ Trọ (Landlord Viewpoint):**
   * **Tiện ích nằm ở Quản lý Phòng:** Toàn bộ các công cụ vận hành (Quản lý thành viên, Chốt số điện nước, Xuất hóa đơn, Thanh lý phòng) được đặt trực tiếp trong **Menu Tiện ích** của từng Phòng trọ.
   * **Chat độc lập & Chat redirect:** Kênh Chat là phân hệ liên lạc riêng. Trong Menu Tiện ích của mỗi phòng có nút **"Nhắn tin phòng" (Chat redirect)** để chuyển nhanh đến đúng luồng chat của phòng đó.
   * **Tab Sự Cố Riêng:** Phân hệ Sự cố được tách thành một **Tab độc lập** trên thanh điều hướng chính giúp Chủ trọ theo dõi, lọc trạng thái và điều phối sửa chữa tập trung cho toàn bộ các tòa nhà.
2. **Ai Trong Phòng Cũng Có Thể Thanh Toán (Không Chỉ Lead):**
   * Hóa đơn và mã VietQR động được tạo cho phòng. **Bất kỳ thành viên nào** trong phòng (người đại diện ký hợp đồng hoặc thành viên ở ghép) đều có thể quét QR thanh toán hoặc nộp tiền mặt. Khi có khoản nộp được xác nhận, hệ thống tự động gạch nợ cho phòng.
3. **Linh Hoạt Thành Viên & Bỏ Giới Hạn Max Occupancy Mặc Định:**
   * Hệ thống không ép buộc giới hạn số người cứng. Nếu Chủ trọ không chủ động cài đặt giới hạn số lượng người ở (`maxOccupancy` để trống/không giới hạn), phòng đó có thể thêm bao nhiêu người ở ghép tùy ý.
4. **Trao Đổi Tự Nhiên (Tag Tên, Tag Phòng — Bỏ Cú Pháp `@issue`):**
   * Bỏ cú pháp lệnh `@issue`. Trong khung chat, cư dân và chủ trọ trao đổi tự nhiên bằng cách **tag tên thành viên (`@tên`) hoặc tag phòng (`@phòng` / `#phòng`)** kèm ảnh hiện trường. Mọi báo cáo sự cố được đồng bộ và quản lý tập trung tại Tab Sự Cố riêng.
5. **Cấu Hình Quét Nợ Tiền Thuộc Về Chủ Trọ:**
   * Chủ trọ tự quyết định ngày chốt điện nước, hạn đóng tiền (Due date) và bật/tắt lịch bot tự động quét nợ định kỳ để nhắc nhở phòng trọ.
6. **Hợp Đồng Ký Tay Wet-Sign (D18) & Lưu Trữ Hội Thoại (Archive):**
   * Hỗ trợ in mẫu hợp đồng giấy ký sống (wet-sign), chụp ảnh tải lên kích hoạt phòng. Khi trả phòng, hội thoại cũ được lưu trữ (Archive) và khởi tạo kênh mới cho khách tiếp theo.

---

## 2. Tổng Quan Điều Hướng (Landlord Navigation Hub)

```mermaid
flowchart TD
    StartLL([Chủ trọ Đăng Nhập]) --> HomeLL[Landlord Dashboard]
    HomeLL --> MainNav{Chọn phân hệ quản lý}
    
    MainNav -->|1. Dashboard| TabDash[Xem Doanh thu, Công nợ & Room Map D20]
    MainNav -->|2. Quản lý Phòng & BĐS| TabProp[Quản lý Tòa nhà, Phòng trọ & Menu Tiện Ích Phòng]
    MainNav -->|3. Sự cố riêng| TabIssues[Tab Sự Cố: Quản lý & Điều phối sửa chữa tập trung]
    MainNav -->|4. Chat Hub| TabChat[Property Chat Hub: Kênh trao đổi cư dân]
    MainNav -->|5. Cài đặt & Quét nợ| TabSettings[Cấu hình Đơn giá & Lịch Quét Nợ Tự Động]
    MainNav -->|6. Đăng xuất| LogoutLL[Đăng xuất an toàn]
```

---

## 3. Các Luồng Nghiệp Vụ Chi Tiết (Sub-Flows)

### Sub-Flow 1: Quản Lý Bất Động Sản & Phòng Trọ (Kèm Menu Tiện Ích)

Chủ trọ tạo mới Tòa nhà bằng bản đồ định vị kéo thả pin (Map Picker) và quản lý danh sách phòng. Trong mỗi phòng tích hợp sẵn **Menu Tiện ích**.

```mermaid
flowchart TD
    StartProp([Vào Quản lý BĐS & Phòng]) --> ChoosePropAction{Chọn thao tác}
    
    %% Nhánh 1: Thêm Tòa nhà
    ChoosePropAction -->|Thêm Tòa nhà| FormBld[Nhập Tên tòa, Địa chỉ, Số tầng]
    FormBld --> PickMap[Kéo thả ghim vị trí trên Bản đồ Map Picker]
    PickMap --> SetDefaultRates[Cấu hình đơn giá điện nước mặc định của Tòa nhà D16]
    SetDefaultRates --> SaveBld[Lưu Tòa nhà vào hệ thống]
    
    %% Nhánh 2: Thêm Phòng trọ
    ChoosePropAction -->|Thêm Phòng mới D25| FormRoom[Chọn Tòa nhà & Tầng]
    FormRoom --> InputRoomSpecs[Nhập Số phòng, Diện tích, Giá thuê]
    InputRoomSpecs --> SetOptionalRules[Cài đặt quy tắc tùy chọn: Giới tính, Tiện nghi - maxOccupancy không bắt buộc]
    SetOptionalRules --> SaveRoom[Tạo phòng: Trạng thái 'available']
    
    %% Mở Tiện ích phòng
    ChoosePropAction -->|Chọn một Phòng cụ thể| RoomCard[Mở Chi tiết Phòng]
    RoomCard --> RoomMenu[Menu Tiện Ích Phòng: Thành viên, Chốt số, Hóa đơn, Chat redirect, Thanh lý]
    RoomMenu --> ChatRedirect[Bấm 'Nhắn tin phòng' -> Chuyển sang khung Chat của phòng]
```

---

### Sub-Flow 2: Tạo Hợp Đồng Thuê & Check-in (Mẫu HĐ & Wet-Sign D18)

Đón khách mới: nhập thông tin người ký, quét CCCD bằng AI OCR, in hợp đồng giấy ký sống, kích hoạt phòng và thiết lập để **bất kỳ ai trong phòng cũng có thể thanh toán**.

```mermaid
flowchart TD
    StartContract([Chọn phòng trống 'available']) --> FormContract[Mở Form Tạo Hợp Đồng]
    FormContract --> InputTenant[Nhập SĐT & Chụp ảnh CCCD người đại diện D17]
    InputTenant --> AI_OCR_CCCD[AI OCR tự động bóc tách Họ tên, Số CCCD, Địa chỉ]
    AI_OCR_CCCD --> InputTerms[Nhập Tiền cọc, Tiền thuê, Ngày bắt đầu & Thời hạn HĐ]
    
    InputTerms --> ConfigPay[Cấu hình thanh toán linh hoạt: Bất kỳ thành viên nào trong phòng cũng có thể quét QR thanh toán]
    
    ConfigPay --> PrintTemplate[Xuất file mẫu HĐ chuẩn PDF điền sẵn D18]
    PrintTemplate --> PhysicalSign[Hai bên ký tay trực tiếp trên giấy thật Wet-Sign]
    PhysicalSign --> UploadSigned[Chủ trọ chụp ảnh HĐ đã ký tải lên hệ thống]
    
    UploadSigned --> ActivateContract[HĐ chuyển trạng thái 'active' - Phòng sang 'occupied']
    ActivateContract --> CreateRoomChat[Tự động tạo Kênh Chat riêng cho phòng & nạp thành viên]
    CreateRoomChat --> EndCheckin([Hoàn tất bàn giao phòng])
```

---

### Sub-Flow 3: Quản Lý Thành Viên Phòng & Biến Động Giữa Kỳ (Từ Tiện Ích Phòng)

Chủ trọ mở **Menu Tiện ích trong Quản lý Phòng** để thêm/bớt người ở ghép. Nếu không cấu hình giới hạn, phòng có thể thêm thành viên thoải mái.

```mermaid
flowchart TD
    StartMember([Quản lý Phòng -> Chọn Menu Tiện ích: Thành viên]) --> ViewMembers[Xem danh sách thành viên hiện tại của phòng]
    ViewMembers --> MemberAction{Chọn thao tác}
    
    %% Thêm người ở ghép
    MemberAction -->|Thêm người ở ghép mới| InputNewMember[Nhập Họ tên, SĐT & CCCD người mới]
    InputNewMember --> AddToChat[Hệ thống tự động add tài khoản vào Chat phòng & tính lại tỷ lệ tiền]
    AddToChat --> BotMsgNew[Bot thông báo thành viên mới vào kênh Chat] --> ViewMembers
    
    %% Xóa thành viên rời đi
    MemberAction -->|Xóa thành viên rời đi| SelectRemove[Chọn thành viên chuyển đi]
    SelectRemove --> CheckLeadRole{Người này có phải Người đại diện ký HĐ?}
    CheckLeadRole -->|Phải là Lead| BlockRemove[Không thể xóa Lead - Cần đổi đại diện hoặc thanh lý HĐ] --> ViewMembers
    CheckLeadRole -->|Thành viên ở ghép| SettleDebt[Chủ trọ thu khoản tiền cấn trừ trực tiếp]
    SettleDebt --> RemoveMember[Xóa thành viên khỏi phòng & rút khỏi Chat]
    RemoveMember --> BotMsgLeave[Bot thông báo thành viên đã rời phòng] --> ViewMembers
```

* **Ghi chú về số lượng người ở:** Bỏ ràng buộc chặn cứng `maxOccupancy`. Nếu chủ trọ không thiết lập số người tối đa thì phòng có thể thêm bao nhiêu thành viên ở ghép tùy theo nhu cầu thực tế.

---

### Sub-Flow 4: Chốt Số Điện/Nước (Từ Tiện Ích Phòng)

Chủ trọ mở tiện ích chốt số từ màn hình Quản lý Phòng, chụp ảnh công tơ điện nước và AI OCR bóc tách số liệu.

```mermaid
flowchart TD
    StartMeter([Quản lý Phòng -> Chọn Menu Tiện ích: Chốt số điện nước]) --> LoadLastIndex[Hệ thống nạp chỉ số cũ kỳ trước]
    LoadLastIndex --> SnapPhoto[Dùng Camera chụp ảnh đồng hồ Điện & Nước]
    SnapPhoto --> RunOCR[AI OCR tự động đọc chỉ số mới từ ảnh chụp F3.3]
    RunOCR --> ReviewIndex{Chủ trọ kiểm tra kết quả?}
    
    ReviewIndex -->|Chưa chuẩn| EditManual[Sửa lại số bằng tay]
    ReviewIndex -->|Chính xác| ConfirmIndex[Bấm Xác nhận 1 chạm]
    EditManual --> ConfirmIndex
    
    ConfirmIndex --> SaveMeterDB[Lưu bản ghi chốt số kỳ hiện tại]
    SaveMeterDB --> BotPushMeter[Bot gửi Thẻ Chốt Số vào Chat phòng để cư dân cùng nắm]
    BotPushMeter --> EndMeter([Sẵn sàng xuất hóa đơn])
```

---

### Sub-Flow 5: Lập Hóa Đơn & Thanh Toán Linh Hoạt (Mọi Thành Viên Đều Trả Được)

Hóa đơn kèm mã VietQR động được phát hành cho phòng. Bất kỳ ai trong phòng (Lead hoặc thành viên ở ghép) đều có thể quét mã thanh toán hoặc nộp tiền mặt.

```mermaid
flowchart TD
    StartInvoice([Quản lý Phòng -> Chọn Menu Tiện ích: Lập hóa đơn]) --> CalcAmount[Tính toán: Tiền phòng + Điện + Nước + Dịch vụ]
    CalcAmount --> ReviewBill{Chủ trọ xem trước hóa đơn?}
    
    ReviewBill -->|Cần chỉnh sửa| EditBill[Điều chỉnh số liệu] --> CalcAmount
    ReviewBill -->|Hợp lệ| PublishBill[Bấm Phát hành Hóa đơn]
    
    PublishBill --> GenQR[Sinh mã VietQR động: Gắn mã định danh phòng & đúng số tiền lẻ]
    GenQR --> BotSendBill[Bot gửi Thẻ Hóa Đơn kèm mã VietQR vào Chat phòng]
    
    BotSendBill --> PayMethod{Ai thanh toán & Hình thức nào?}
    
    %% Bất kỳ ai quét VietQR
    PayMethod -->|Bất kỳ thành viên nào trong phòng quét VietQR| BankTransfer[Chuyển khoản qua App Ngân hàng]
    BankTransfer --> WebhookReconcile[Hệ thống nhận Webhook ngân hàng: Khớp mã định danh]
    WebhookReconcile --> AutoGachNo[Hệ thống tự động Gạch Nợ phòng: Hóa đơn chuyển 'paid']
    
    %% Bất kỳ ai nộp tiền mặt
    PayMethod -->|Bất kỳ thành viên nào nộp Tiền mặt| CashPay[Chủ trọ nhận tiền mặt trực tiếp]
    CashPay --> ConfirmCashBtn[Chủ trọ bấm 'Xác nhận thu tiền mặt' trên hóa đơn]
    ConfirmCashBtn --> AutoGachNo
    
    AutoGachNo --> BotReceipt[Bot bắn Thẻ Biên Nhận Đã Thanh Toán vào Chat phòng]
    BotReceipt --> UpdateFinDash[Cập nhật Doanh thu & Giảm công nợ trên Dashboard]
```

---

### Sub-Flow 6: Cấu Hình Chu Kỳ Hóa Đơn & Quét Nợ Tự Động (Landlord Debt Automation)

Chủ trọ toàn quyền cài đặt ngày chốt tiền, hạn thanh toán và cấu hình lịch trình tự động quét nợ cho các phòng trọ của mình.

```mermaid
flowchart TD
    StartDebtConfig([Vào Cài đặt Quản lý của Chủ trọ]) --> OpenBillingConfig[Màn hình Cấu hình Hóa đơn & Quét Nợ]
    
    OpenBillingConfig --> SetClosingDay[Cài đặt Ngày chốt số hàng tháng: vd ngày 25 hoặc 30]
    SetClosingDay --> SetDueDate[Cài đặt Hạn chót thanh toán: vd 5 ngày sau ngày phát hành]
    
    SetDueDate --> SetupReminderCron{Bật tính năng Bot quét nợ tự động?}
    
    SetupReminderCron -->|Tắt| ManualOnly[Chủ trọ sẽ tự bấm nút 'Nhắc nợ' thủ công khi cần]
    
    SetupReminderCron -->|Bật| ConfigCronRules[Cấu hình tần suất bot quét nợ:]
    ConfigCronRules --> Rule1[1. Nhắc trước hạn: T - 1 ngày]
    Rule1 --> Rule2[2. Nhắc đúng hạn: T - 0]
    Rule2 --> Rule3[3. Nhắc quá hạn định kỳ: Mỗi 2 ngày sau khi quá hạn]
    
    ManualOnly --> SaveDebtSettings[Lưu cấu hình quét nợ]
    Rule3 --> SaveDebtSettings
    
    SaveDebtSettings --> RunAutoCron[[Hệ thống nền chạy quét nợ hàng ngày theo giờ chủ trọ đặt]]
    
    RunAutoCron --> CheckOverdueBills{Có hóa đơn đến hạn / quá hạn?}
    CheckOverdueBills -->|Không| SleepCron[Kết thúc lượt quét]
    CheckOverdueBills -->|Có| TriggerBotReminder[Bot tự động bắn Thẻ Nhắc Nợ vào Chat phòng + Gửi Push Noti]
```

---

### Sub-Flow 7: Quản Lý Sự Cố (Tab Sự Cố Riêng & Trao Đổi Tag Tên, Tag Phòng)

Sự cố được quản lý tại **Tab Sự Cố độc lập**. Trong khung Chat, cư dân và chủ trọ trao đổi thông tin tự nhiên bằng cách **tag tên (`@tên`) hoặc tag phòng (`@phòng` / `#phòng`)** thay vì dùng cú pháp lệnh `@issue`.

```mermaid
flowchart TD
    StartIssue([Phát sinh sự cố hỏng hóc]) --> ReportChannel{Kênh tiếp nhận}
    
    %% Tiếp nhận qua Chat bằng Tag tên / Tag phòng
    ReportChannel -->|Nhắn trong Chat: Tag tên @chủ_trọ hoặc tag @phòng kèm ảnh| ChatMessage[Tin nhắn trao đổi kèm hình ảnh hiện trường hỏng hóc]
    ChatMessage --> CreateFromChat[Chủ trọ hoặc Bot tạo bản ghi sự cố gắn với phòng tương ứng]
    CreateFromChat --> SyncToIssueTab[Xuất hiện tức thì trong Tab Sự Cố riêng]
    
    %% Tiếp nhận trực tiếp tại Tab Sự Cố
    ReportChannel -->|Chủ trọ chủ động tạo tại Tab Sự Cố| FormIssue[Mở Form tạo sự cố tại Tab Sự Cố]
    FormIssue --> InputIssueData[Chọn Tòa nhà, Số phòng, Mô tả thiết bị hỏng]
    InputIssueData --> SyncToIssueTab
    
    %% Xử lý tại Tab Sự Cố
    SyncToIssueTab --> ProcessIssue{Chủ trọ cập nhật tiến độ xử lý}
    ProcessIssue -->|Đang sửa chữa| SetProgress[Chuyển trạng thái: 'Đang xử lý']
    ProcessIssue -->|Đã sửa xong| SetResolved[Chuyển trạng thái: 'Đã hoàn thành']
    ProcessIssue -->|Hủy sự cố| SetCancelled[Hủy / Xóa bản ghi sự cố]
    
    SetProgress --> UpdateChatNoti[Bot cập nhật thông báo tiến độ vào Chat phòng tương ứng]
    SetResolved --> UpdateChatNoti
    SetCancelled --> UpdateChatNoti
```

---

### Sub-Flow 8: Check-out, Thanh Lý Cọc & Lưu Trữ Hội Thoại (Từ Tiện Ích Phòng)

Quy trình trả phòng khởi động từ **Menu Tiện ích trong Quản lý Phòng**: chốt số cuối, quyết toán cọc, lưu trữ hội thoại cũ (Archive) và chuyển trạng thái phòng sẵn sàng đón khách mới.

```mermaid
flowchart TD
    StartCheckout([Quản lý Phòng -> Chọn Menu Tiện ích: Thanh lý phòng]) --> CheckTermReason{Hình thức trả phòng}
    
    CheckTermReason -->|Hết hạn HĐ tự nhiên| EndDateReach[HĐ chuyển trạng thái 'expired']
    CheckTermReason -->|Trả phòng sớm| EarlyTerm[Chủ trọ chọn 'Chấm dứt hợp đồng trước hạn']
    
    EndDateReach --> FinalMeter[Chốt số điện nước lần cuối cùng bằng Camera OCR]
    EarlyTerm --> FinalMeter
    
    FinalMeter --> FinalInvoice[Lập hóa đơn quyết toán: Tính tiền phòng theo số ngày ở thực tế]
    FinalInvoice --> PayFinalInvoice[Khách thanh toán hóa đơn cuối]
    
    PayFinalInvoice --> InspectDeposit{Khấu trừ tiền cọc?<br>Hư hỏng tài sản / Tiền phạt}
    InspectDeposit -->|Có khấu trừ| CalcDeduct[Tiền cọc hoàn lại = Cọc ban đầu - Khấu trừ]
    InspectDeposit -->|Không khấu trừ| FullDeposit[Hoàn trả 100% tiền cọc]
    
    CalcDeduct --> SettleDepositCash[Chuyển khoản hoặc trả tiền mặt cọc ngoài hệ thống]
    FullDeposit --> SettleDepositCash
    
    SettleDepositCash --> ConfirmRelease[Chủ trọ bấm 'Xác nhận hoàn tất thanh lý & nhận bàn giao']
    
    %% Archive Chat & Mở phòng mới
    ConfirmRelease --> ArchiveOldChat[Lưu trữ cuộc trò chuyện của HĐ cũ sang trạng thái Read-only]
    ArchiveOldChat --> ResetRoomAvail[Phòng chuyển về trạng thái 'available' trên Room Map]
    
    ResetRoomAvail --> NewTenantCheckin[Khi có khách mới dọn vào ký HĐ mới]
    NewTenantCheckin --> InitNewChat[Hệ thống tạo kênh chat hoàn toàn mới tinh - Khách mới không thấy dữ liệu khách cũ]
```
