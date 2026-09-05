# User Flow — Landlord

## 1. Landlord Overview
Chủ trọ (Landlord) là vai trò vận hành trung tâm trên nền tảng Web console (có hỗ trợ Mobile-lite nhận thông báo). Dựa trên nguyên tắc **D29 (Landlord-can-operate-solo)**, Chủ trọ có thể vận hành trọn vẹn toàn bộ vòng đời cho thuê (từ thiết lập tòa/phòng, lập hợp đồng ký tay, chốt số công tơ OCR, xuất hóa đơn QR động đối soát tự động, đến xử lý sự cố và thanh lý) ngay cả khi **người thuê không bao giờ đăng nhập ứng dụng**.

---

## 2. Landlord Main User Flow
```mermaid
flowchart TD
    StartLL([Bắt đầu: Truy cập Landlord Web Console]) --> LL_Login[Đăng nhập tài khoản Chủ trọ]
    LL_Login --> LL_AuthCheck{Xác thực & roles chứa 'landlord'?}
    
    LL_AuthCheck -->|Không hợp lệ| LL_AuthError[Báo lỗi đăng nhập]
    LL_AuthError --> LL_Login
    
    LL_AuthCheck -->|Hợp lệ| LL_Dashboard[Landlord Dashboard: Room-map & Doanh thu/Công nợ D20]
    
    LL_Dashboard --> LL_Nav{Chọn phân hệ vận hành}
    
    LL_Nav -->|1. Quản lý BĐS| Mod_Property[Phân hệ Quản lý Tòa nhà & Phòng trọ]
    LL_Nav -->|2. Hợp đồng thuê| Mod_Contract[Phân hệ Hợp đồng & Check-in]
    LL_Nav -->|3. Chốt số điện nước| Mod_Utility[Phân hệ Chốt số Công tơ OCR]
    LL_Nav -->|4. Hóa đơn & Thu tiền| Mod_Billing[Phân hệ Hóa đơn & Đối soát QR]
    LL_Nav -->|5. Báo sự cố & Chat| Mod_Issue[Phân hệ Sự cố & Property Chat D24']
    LL_Nav -->|6. Cài đặt đơn giá| Mod_Settings[Cấu hình Đơn giá mặc định D16]
    LL_Nav -->|7. Đăng xuất| LL_Logout[Đăng xuất hệ thống]
    
    Mod_Property --> RetDash1[Về Dashboard] --> LL_Dashboard
    Mod_Contract --> RetDash2[Về Dashboard] --> LL_Dashboard
    Mod_Utility --> RetDash3[Về Dashboard] --> LL_Dashboard
    Mod_Billing --> RetDash4[Về Dashboard] --> LL_Dashboard
    Mod_Issue --> RetDash5[Về Dashboard] --> LL_Dashboard
    Mod_Settings --> RetDash6[Về Dashboard] --> LL_Dashboard
    
    LL_Logout --> EndLL([Kết thúc phiên làm việc Chủ trọ])
```

---

## 3. Landlord Authentication & Global Config Flow
```mermaid
flowchart TD
    StartLLAuth([Bắt đầu]) --> EnterLogin[Nhập Email/SĐT và Mật khẩu]
    EnterLogin --> SubmitLogin[Gửi yêu cầu đăng nhập]
    
    SubmitLogin --> CheckCreds{Thông tin chính xác?}
    CheckCreds -->|Sai| ShowErr[Hiển thị lỗi đăng nhập] --> EnterLogin
    
    CheckCreds -->|Đúng| CheckLLRole{Mảng roles có chứa 'landlord'?}
    CheckLLRole -->|Không| ErrRole[Báo lỗi: Bạn không có quyền Chủ trọ] --> EnterLogin
    
    CheckLLRole -->|Có quyền| CreateSession[Khởi tạo JWT session]
    CreateSession --> CheckGlobalRate{Đã thiết lập đơn giá điện/nước mặc định chưa?}
    
    CheckGlobalRate -->|Chưa - Thiết lập lần đầu D16| FormGlobalRate[Nhập đơn giá mặc định: electricityRate, waterRate]
    FormGlobalRate --> SaveGlobalRate[Lưu vào LandlordProfile.default_settings]
    SaveGlobalRate --> GoLLDash[Vào Landlord Dashboard]
    
    CheckGlobalRate -->|Đã thiết lập| GoLLDash
    GoLLDash --> EndLLAuth([Hoàn thành đăng nhập])
```

---

## 4. Landlord Property Management Flow (Building, Room & Constraints)
```mermaid
flowchart TD
    StartProp([Vào Quản lý Bất động sản]) --> ViewPropList[Xem danh sách Tòa nhà & Sơ đồ phòng]
    
    ViewPropList --> ActionProp{Chọn tác vụ}
    
    ActionProp -->|Thêm Tòa nhà mới| FormBuilding[Nhập Tên, Địa chỉ, Số tầng]
    FormBuilding --> RateOverrideBld{Có ghi đè đơn giá điện nước cho Tòa? D16}
    RateOverrideBld -->|Có| SetBldRate[Nhập buildingElectricityRate / WaterRate]
    RateOverrideBld -->|Không| UseDefaultBld[Sử dụng đơn giá mặc định của Chủ trọ]
    SetBldRate --> SaveBld[Lưu Tòa nhà]
    UseDefaultBld --> SaveBld
    SaveBld --> ViewPropList
    
    ActionProp -->|Thêm Phòng trọ mới D25| SelectBldForRoom[Chọn Tòa nhà và Tầng]
    SelectBldForRoom --> InputRoomInfo[Nhập Số phòng, Diện tích, Giá thuê, Tiện nghi]
    InputRoomInfo --> SetOwner[Gán Room.owner_id = ID của mình NOT NULL]
    
    SetOwner --> SetupConstraints[Cấu hình ràng buộc phòng D21: maxOccupancy, genderPolicy, houseRules, budgetRange]
    
    SetupConstraints --> RateOverrideRoom{Có ghi đè đơn giá điện nước riêng phòng?}
    RateOverrideRoom -->|Có| SetRoomRate[Nhập electricityRateOverride / WaterOverride]
    RateOverrideRoom -->|Không| InheritRate[Kế thừa đơn giá Tòa nhà / Chủ trọ]
    
    SetRoomRate --> SaveRoom[Tạo Phòng - Trạng thái: available]
    InheritRate --> SaveRoom
    SaveRoom --> UpdateRoomMap[Cập nhật Phòng mới lên Room Map]
    UpdateRoomMap --> ViewPropList
    
    ActionProp -->|Xem/Sửa thông tin phòng| SelectRoom[Chọn phòng trên Room Map]
    SelectRoom --> ViewRoomDetail[Xem chi tiết phòng, HĐ hiện tại, lịch sử]
    ViewRoomDetail --> EndProp([Hoàn tất quản lý phòng])
```

---

## 5. Landlord Rental Contract & Check-in Flow (D18 Wet-Sign & D17 CCCD)
```mermaid
flowchart TD
    StartContract([Bắt đầu tạo Hợp đồng thuê]) --> SelectVacantRoom[Chọn phòng trạng thái 'available']
    SelectVacantRoom --> ClickNewContract[Bấm 'Tạo hợp đồng mới']
    
    ClickNewContract --> InputTenantInfo[Nhập thông tin Người thuê đại diện: Tên, SĐT]
    InputTenantInfo --> UploadCCCD[Chụp / Tải ảnh CCCD mặt trước D17]
    
    UploadCCCD --> AI_OCR_CCCD[AI OCR CCCD tự trích xuất thông tin F5.6]
    AI_OCR_CCCD --> ReviewCCCD{Thông tin OCR chính xác?}
    ReviewCCCD -->|Cần chỉnh sửa| EditTenantData[Chỉnh sửa thông tin tay]
    ReviewCCCD -->|Chính xác| FillContractTerms[Nhập tiền cọc, ngày bắt đầu, thời hạn]
    EditTenantData --> FillContractTerms
    
    FillContractTerms --> SharedConfigDecision{Phòng ở ghép nhiều người? D22}
    SharedConfigDecision -->|Một người thuê| SinglePayment[Cấu hình HĐ đơn lẻ]
    SharedConfigDecision -->|Nhiều người ở ghép| SelectD22Config{Chọn cấu hình thanh toán D22}
    
    SelectD22Config -->|Model a: Đại diện thanh toán| RepPayerConfig[1 HĐ đại diện - Lead trả, tự chia offline]
    SelectD22Config -->|Model b: Hóa đơn chia sẻ| SharedInvoiceConfig[1 HĐ đại diện - Hệ thống track phần tiền từng người]
    
    SinglePayment --> GenContractDraft[Khởi tạo Contract: trạng thái 'draft']
    RepPayerConfig --> GenContractDraft
    SharedInvoiceConfig --> GenContractDraft
    
    GenContractDraft --> ExportTemplate[Sinh file mẫu HĐ chuẩn Word/PDF điền sẵn D18]
    ExportTemplate --> PrintContract[In hợp đồng ra giấy]
    
    PrintContract --> PhysicalSign[Hai bên ký tay trên giấy thật wet-sign]
    
    PhysicalSign --> UploadSignedDoc[Chủ trọ chụp / scan tải file HĐ đã ký lên]
    
    UploadSignedDoc --> ValidateUpload{Đã có file ký tải lên?}
    ValidateUpload -->|Chưa tải file| KeepDraft[HĐ giữ nguyên trạng thái 'draft' - Phòng chưa bàn giao]
    KeepDraft --> EndContractIncomplete([Chờ tải file ký])
    
    ValidateUpload -->|Tải file thành công| ActivateContract[Lưu uploaded_file + signed_at - Contract chuyển 'active']
    ActivateContract --> UpdateRoomOcc[Phòng chuyển trạng thái: occupied]
    UpdateRoomOcc --> DashboardSync[Cập nhật Room Map & ghi nhận tiền cọc]
    DashboardSync --> EndContractSuccess([Hoàn tất bàn giao phòng & HĐ có hiệu lực])
```

---

## 6. Landlord Utility Meter Closing Flow (OCR & Bot Remind)
```mermaid
flowchart TD
    StartMeter([Đến kỳ chốt số điện nước hàng tháng]) --> SelectBldAndPeriod[Chọn Tòa nhà và Kỳ chốt số period]
    SelectBldAndPeriod --> OpenRoomList[Hiển thị danh sách phòng cần chốt số]
    
    OpenRoomList --> SelectTargetRoom[Chọn phòng cần ghi số]
    SelectTargetRoom --> CheckBaseline{Kỳ chốt số đầu tiên?}
    CheckBaseline -->|Đúng| InputBaseline[Nhập chỉ số công tơ ban đầu baseline bằng tay]
    CheckBaseline -->|Không| FetchPrevReading[Lấy chỉ số cũ từ kỳ trước]
    
    InputBaseline --> SnapMeterPhoto[Chụp ảnh đồng hồ điện và đồng hồ nước]
    FetchPrevReading --> SnapMeterPhoto
    
    SnapMeterPhoto --> AI_OCR_Meter[AI OCR tự động đọc chỉ số mới từ ảnh F3.3]
    AI_OCR_Meter --> DisplayReading[Hiển thị chỉ số cũ, số mới, lượng tiêu thụ]
    
    DisplayReading --> VerifyReading{Chủ trọ kiểm tra chỉ số đọc?}
    VerifyReading -->|Ảnh mờ / Sai số| ManualEditReading[Chỉnh sửa chỉ số đọc thủ công]
    VerifyReading -->|Chính xác| OneTapConfirm[Bấm 'Xác nhận' 1 chạm]
    ManualEditReading --> OneTapConfirm
    
    OneTapConfirm --> SaveMeterReading[Tạo bản ghi MeterReading - unique room_id, period]
    SaveMeterReading --> SendBotCard[Bot gửi Card kết quả chốt số vào Chat phòng D24']
    
    SendBotCard --> NextRoomCheck{Còn phòng nào chưa chốt trong kỳ?}
    NextRoomCheck -->|Còn| OpenRoomList
    NextRoomCheck -->|Đã chốt xong hết| ReadyForBilling[Sẵn sàng chuyển sang phân hệ Lập hóa đơn]
    ReadyForBilling --> EndMeter([Hoàn tất chốt số điện nước])
```

---

## 7. Landlord Invoice Generation & Auto-Reconciliation Flow (VietQR Động)
```mermaid
flowchart TD
    StartBill([Lập hóa đơn hàng tháng]) --> SelectActiveContract[Chọn HĐ đang 'active' & Kỳ thanh toán]
    SelectActiveContract --> CheckReadingDone{Đã có dữ liệu MeterReading của kỳ?}
    CheckReadingDone -->|Chưa có| BlockBill[Báo lỗi: Phải chốt số điện nước trước] --> EndBillFail([Dừng lập hóa đơn])
    
    CheckReadingDone -->|Đã có| ResolveRates[Phân giải đơn giá D16: Room Override -> Building -> Landlord Default]
    ResolveRates --> CalcBill[Tính tiền: Tiền phòng + Tiền điện + Tiền nước + Phụ phí]
    
    CalcBill --> CheckProrate{HĐ bắt đầu giữa tháng?}
    CheckProrate -->|Có| ProrateCalc[Tính toán tiền phòng prorate theo số ngày]
    CheckProrate -->|Không| FullCalc[Tính trọn vẹn tháng]
    
    ProrateCalc --> CreateInvoice[Khởi tạo Invoice: trạng thái 'pending']
    FullCalc --> CreateInvoice
    
    CreateInvoice --> ReviewInvoice{Chủ trọ duyệt hóa đơn?}
    ReviewInvoice -->|Hóa đơn sai sót| VoidInvoice[Đánh dấu 'void' - Tạo hóa đơn mới thay thế] --> EndBillFail
    ReviewInvoice -->|Hợp lệ| IssueInvoice[Phát hành hóa đơn]
    
    IssueInvoice --> GenDynamicQR[Sinh mã VietQR động định danh: tiền phòng lẻ + mã HĐ]
    GenDynamicQR --> PushToRoomChat[Bot gửi Card hóa đơn + QR vào Chat riêng phòng D24']
    
    PushToRoomChat --> TenantPaymentBranch{Hình thức khách thanh toán D29}
    
    TenantPaymentBranch -->|Quét VietQR qua App Ngân hàng bất kỳ| BankTransfer[Khách chuyển khoản ngân hàng]
    BankTransfer --> WebhookReceived[Hệ thống nhận Webhook thanh toán từ ngân hàng]
    WebhookReceived --> AutoRecon[Tự động đối soát khớp mã định danh]
    AutoRecon --> MarkPaidAuto[Cập nhật Invoice: 'paid' - Ghi nhận Payment: success]
    
    TenantPaymentBranch -->|Khách trả tiền mặt| PayCash[Khách đưa tiền mặt cho Chủ trọ]
    PayCash --> ManualCashEntry[Chủ trọ ghi nhận thủ công: method = cash]
    ManualCashEntry --> MarkPaidManual[Cập nhật Invoice: 'paid']
    
    TenantPaymentBranch -->|Quá hạn chưa trả| CheckOverdue[Hệ thống quét định kỳ]
    CheckOverdue --> MarkOverdue[Chuyển Invoice sang 'overdue']
    MarkOverdue --> BotRemind[Bot gửi tin nhắn nhắc nợ vào Chat phòng + FCM push]
    
    MarkPaidAuto --> UpdateRevenueDash[Cập nhật Doanh thu & Công nợ trên Dashboard D20]
    MarkPaidManual --> UpdateRevenueDash
    UpdateRevenueDash --> EndBillSuccess([Hoàn tất chu trình hóa đơn])
```

---

## 8. Landlord Issue Handling & Property Chat Flow (D24')
```mermaid
flowchart TD
    StartIssue([Tiếp nhận / Quản lý Sự cố]) --> IssueSource{Nguồn báo cáo sự cố D29}
    
    IssueSource -->|Người thuê gửi qua App| TenantMsg[Tenant gõ @issue trong Property Chat]
    TenantMsg --> BotCreateCard[Bot tạo IssueReport 'open' + gửi card vào chat]
    
    IssueSource -->|Tenant báo ngoài app: SĐT/Gặp mặt D29| LandlordManual[Chủ trọ tự tạo IssueReport trên Web]
    LandlordManual --> CreateIssueRec[Lưu IssueReport: trạng thái 'open']
    
    BotCreateCard --> LandlordNotified[Chủ trọ nhận FCM push & xem trong Property Chat]
    CreateIssueRec --> LandlordNotified
    
    LandlordNotified --> AssessIssue{Chủ trọ tiếp nhận xử lý?}
    AssessIssue -->|Chưa xử lý ngay| KeepOpen[Giữ trạng thái 'open' trong danh sách theo dõi]
    AssessIssue -->|Bắt đầu sửa chữa| ChangeInProgress[Cập nhật IssueReport: 'in_progress']
    
    ChangeInProgress --> RoomMaintCheck{Có cần tạm dừng sử dụng phòng?}
    RoomMaintCheck -->|Có| SetRoomMaint[Đánh dấu phòng trạng thái 'maintenance']
    RoomMaintCheck -->|Không| MaintainNormal[Phòng giữ nguyên 'occupied']
    
    SetRoomMaint --> DoRepair[Thực hiện sửa chữa & trao đổi tiến độ qua Chat/Kênh ngoài]
    MaintainNormal --> DoRepair
    
    DoRepair --> RepairFinished{Đã sửa chữa xong?}
    RepairFinished -->|Chưa xong| DoRepair
    RepairFinished -->|Hoàn thành| MarkResolved[Cập nhật IssueReport: 'resolved']
    
    MarkResolved --> RestoreRoom[Khôi phục trạng thái phòng về 'occupied']
    RestoreRoom --> NotifyChatDone[Hệ thống thông báo kết quả giải quyết sự cố]
    NotifyChatDone --> EndIssue([Hoàn tất quy trình xử lý sự cố])
```

---

## 9. Landlord Check-out & Contract Termination Flow
```mermaid
flowchart TD
    StartTerm([Bắt đầu trả phòng & thanh lý]) --> CheckTermType{Loại kết thúc hợp đồng}
    
    CheckTermType -->|Hết hạn tự nhiên| AutoExpire[Đến ngày end_date: Contract chuyển 'expired']
    CheckTermType -->|Chấm dứt trước hạn| ManualTerm[Chủ trọ bấm 'Chấm dứt hợp đồng sớm']
    ManualTerm --> SetTermStatus[Cập nhật Contract: 'terminated']
    
    AutoExpire --> FinalMeterClosing[Thực hiện chốt số điện nước lần cuối cùng]
    SetTermStatus --> FinalMeterClosing
    
    FinalMeterClosing --> FinalInvoiceGen[Tạo hóa đơn tháng cuối: Prorate tiền phòng theo ngày thực tế]
    FinalInvoiceGen --> FinalInvoicePay[Khách thanh toán hóa đơn cuối qua QR hoặc tiền mặt]
    
    FinalInvoicePay --> SettleDeposit{Xử lý thanh lý tiền cọc}
    SettleDeposit --> CalcDeduction[Tính toán các khoản cấn trừ nếu có hư hỏng/nợ cước]
    CalcDeduction --> ExternalDepositSettle[Hoàn trả tiền cọc còn lại thực tế ngoài hệ thống: Tiền mặt/Bank]
    
    ExternalDepositSettle --> MarkContractClosed[Chủ trọ đánh dấu 'Đã thanh lý cọc và bàn giao phòng']
    MarkContractClosed --> FreeRoomStatus[Hệ thống giải phóng phòng: chuyển về 'available']
    
    FreeRoomStatus --> RoomMapUpdate[Phòng hiển thị trống trên Room Map & sẵn sàng cho thuê mới]
    RoomMapUpdate --> EndTermSuccess([Kết thúc trọn vẹn vòng đời hợp đồng])
```
