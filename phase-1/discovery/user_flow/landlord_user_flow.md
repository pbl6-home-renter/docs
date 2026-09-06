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
    LL_Nav -->|6. Cài đặt đơn giá & phí| Mod_Settings[Cấu hình UtilityRatePolicy + RecurringFee D30 - preset D31, đổi giá/override - xem §10]
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
    CreateSession --> CheckGlobalRate{Đã có Policy đơn giá điện/nước mặc định chưa? D30/D31}
    
    CheckGlobalRate -->|Chưa cấu hình| ShowBanner[Hiện banner nhắc nhẹ: Cấu hình đơn giá để lập hóa đơn - nút Cài đặt ngay / Để sau]
    ShowBanner -->|Cài đặt ngay| GotoRateSettings[Chuyển tới §10 - Tab Đơn giá mặc định - PickPreset → NewPolicy → DoneGlobal]
    GotoRateSettings --> DoneCfgGlobal[Lưu LandlordProfile.elec_policy_id / water_policy_id]
    DoneCfgGlobal --> HideBanner[Ẩn banner - Đã đủ cấu hình]
    HideBanner --> GoLLDash[Vào Landlord Dashboard]
    
    ShowBanner -->|Để sau| GoLLDash
    CheckGlobalRate -->|Đã thiết lập| GoLLDash
    GoLLDash --> EndLLAuth([Hoàn thành đăng nhập - banner còn hiển thị nếu chưa cấu hình])
```

---

## 4. Landlord Property Management Flow (Building, Room & Constraints)
```mermaid
flowchart TD
    StartProp([Vào Quản lý Bất động sản]) --> ViewPropList[Xem danh sách Tòa nhà & Sơ đồ phòng]
    
    ViewPropList --> ActionProp{Chọn tác vụ}
    
    ActionProp -->|Thêm Tòa nhà mới| FormBuilding[Nhập Tên, Địa chỉ, Số tầng - đơn giá để NULL kế thừa LandlordProfile]
    FormBuilding --> SaveBld[Lưu Tòa nhà]
    SaveBld --> ViewPropList
    
    ActionProp -->|Cấu hình phí định kỳ| ConfigFees[Đi vào §10 - Tab Phí định kỳ]
    ConfigFees --> GotoFeesSettings[Trong luồng §10: PickScopeFee → FillFee → SaveFee → DoneFees]
    GotoFeesSettings --> BackToProp[Quay lại danh sách Tòa & Sơ đồ phòng]
    BackToProp --> ViewPropList

    ActionProp -->|Thêm Phòng trọ mới D25| SelectBldForRoom[Chọn Tòa nhà và Tầng]
    SelectBldForRoom --> InputRoomInfo[Nhập Số phòng, Diện tích, Giá thuê, Tiện nghi]
    InputRoomInfo --> SetOwner[Gán Room.owner_id = ID của mình NOT NULL]
    
    SetOwner --> SetupConstraints[Cấu hình ràng buộc phòng D21: maxOccupancy, genderPolicy, houseRules, budgetRange - đơn giá để NULL kế thừa Tòa/Landlord]
    
    SetupConstraints --> SaveRoom[Tạo Phòng - Trạng thái: available]
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
    
    FillContractTerms --> DeclareVehicles[Nhập số xe gửi tại nhà trọ vehicle_count - dùng cho phí per_vehicle D32]
    
    DeclareVehicles --> SharedConfigDecision{Phòng ở ghép nhiều người? D22}
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
    ActivateContract --> CaptureMeterBaseline[Bàn giao phòng: chụp ảnh đồng hồ ĐIỆN và NƯỚC lúc dọn vào - OCR tự đọc; sai/mờ thì sửa tay số thực tế trước khi lưu D35 - MeterReading is_baseline=true previous=0 current=chỉ số OCR/đã sửa reading_date=ngày bàn giao - D34]
    CaptureMeterBaseline --> UpdateRoomOcc[Phòng chuyển trạng thái: occupied]
    UpdateRoomOcc --> DashboardSync[Cập nhật Room Map & ghi nhận tiền cọc]
    DashboardSync --> EndContractSuccess([Hoàn tất bàn giao phòng & HĐ có hiệu lực])
```

---

## 6. Landlord Utility Meter Closing Flow (OCR & Bot Remind)
```mermaid
flowchart TD
    StartMeter([Đến kỳ chốt số điện nước hàng tháng]) --> SelectBldAndPeriod[Chọn Tòa nhà và Kỳ chốt số period - mặc định kỳ hiện tại]
    SelectBldAndPeriod --> OpenRoomList[Hiển thị danh sách phòng cần chốt số - tiến độ X/Y]
    
    OpenRoomList --> SelectTargetRoom[Chọn phòng cần ghi số]
    SelectTargetRoom --> FetchPrevReading[Lấy chỉ số cũ theo từng loại: kỳ đầu = baseline OCR lúc bàn giao §5 is_baseline=true - hiệu chỉnh tay nếu OCR sai D35; kỳ sau = chỉ số kỳ trước; thay đồng hồ giữa kỳ = baseline mới qua OCR EC1]
    FetchPrevReading --> ConfirmOneType[Chốt lần lượt: ĐIỆN và NƯỚC - mỗi loại 1 bản ghi]

    ConfirmOneType --> SnapMeterPhoto[Chụp ảnh đồng hồ ĐIỆN hoặc NƯỚC tương ứng]
    SnapMeterPhoto --> AI_OCR_Meter[AI OCR tự động đọc chỉ số mới từ ảnh F3.3]
    AI_OCR_Meter --> DisplayReading[Hiển thị chỉ số cũ, số mới, lượng tiêu thụ]
    
    DisplayReading --> VerifyReading{Chủ trọ kiểm tra chỉ số đọc?}
    VerifyReading -->|Ảnh mờ / Sai số| FixMethod{Chọn cách xử lý}
    FixMethod -->|Chụp lại ảnh rõ hơn| RetakePhoto[Chụp lại ảnh đồng hồ]
    FixMethod -->|Sửa tay đúng số thực tế| ManualEditReading[Chỉnh sửa chỉ số đọc thủ công - lưu kèm ảnh evidence gốc - D35]
    RetakePhoto --> SnapMeterPhoto
    ManualEditReading --> OneTapConfirm
    VerifyReading -->|Chính xác| OneTapConfirm[Bấm 'Xác nhận' 1 chạm]
    
    OneTapConfirm --> SaveMeterReading[Tạo MeterReading room + utility_type + period - ảnh evidence riêng từng loại]
    SaveMeterReading --> BothTypesDone{Đã chốt xong cả ĐIỆN và NƯỚC cho phòng này?}
    BothTypesDone -->|Chưa| ConfirmOneType
    BothTypesDone -->|Xong| TriggerAutoInvoice[Auto-trigger D33②: thử tạo Invoice pending cho phòng này - chỉ tạo khi policy/phí resolve OK EC2-EC13 không lỗi]
    
    TriggerAutoInvoice --> BillableOk{Hệ thống tạo được hóa đơn?}
    BillableOk -->|Tạo được| AddToReadyList[Invoice pending được tạo - phòng vào bảng 'Phòng chốt số xong' của §7 để rà soát & phát hành]
    BillableOk -->|Không tạo được| BlockReason[Ghi lỗi block ECx cụ thể: EC3 thiếu đơn giá / EC6 thiếu diện tích / EC7 chưa khai thành viên / EC8 chưa kê khai xe / EC13 policy sai / EC17 tổng âm]
    BlockReason --> FlagFixList[Phòng vào danh sách 'Đã chốt số - chờ sửa lỗi' của §7 - bot nhắc chủ trọ 1 lần kèm lý do + nút hành động vào đúng màn sửa; sửa xong trigger chạy lại tự tạo hóa đơn]
    
    AddToReadyList --> BotCard[Bot gửi Card tổng kết cả 2 loại vào Chat phòng D24']
    FlagFixList --> BotCard
    BotCard --> NextRoomCheck{Còn phòng nào chưa chốt trong kỳ?}
    NextRoomCheck -->|Còn| OpenRoomList
    NextRoomCheck -->|Xong kỳ này| GotoBilling[Chuyển sang phân hệ Hóa đơn §7 - rà soát & phát hành]
    GotoBilling --> EndMeter([Hoàn tất chốt số điện nước])
```

---

## 7. Landlord Invoice Generation & Auto-Reconciliation Flow (VietQR Động) — D33② auto theo PHÒNG
```mermaid
flowchart TD
    StartBill([Vào phân hệ Hóa đơn - chọn Tòa nhà và Kỳ lập hóa đơn - mặc định kỳ hiện tại]) --> LoadRoomStates{Các phòng đang active trong kỳ thuộc trạng thái nào?}
    LoadRoomStates -->|Đủ chỉ số + policy/phí resolve OK| ReadyList[Danh sách 'Phòng chốt số xong' - mỗi dòng 1 phòng Invoice pending auto-tạo D33② - hiển thị tổng tiền, tính theo utility-billing-calculations.md §5–§7]
    LoadRoomStates -->|Chưa đủ chỉ số điện/nước| GotoMeter[Chuyển sang §6 chụp số công tơ trước]
    LoadRoomStates -->|Đủ chỉ số nhưng block ECx| FixBlockList[Danh sách 'Đã chốt số - chờ sửa lỗi' kèm mã lỗi - nút hành động: EC3 → §10 thiết lập đơn giá; EC6 → §4 nhập diện tích; EC7 → §5 khai thành viên; EC8 → §5 kê khai xe; EC13 → §10 sửa policy; EC17 → chỉnh giảm trừ]
    GotoMeter --> EndBillWait([Dừng - khi chốt số xong trigger auto tạo hóa đơn, quay lại danh sách này])
    FixBlockList -->|Sửa xong lỗi| ReTrigger[Trigger auto chạy lại - tạo Invoice pending nếu hết lỗi D33②]
    ReTrigger --> ReadyList
    ReadyList --> ReviewBill[Chủ trọ mở từng phòng để rà soát & điều chỉnh]
    ReviewBill --> AdjustLines["Điều chỉnh trước duyệt: other_fees dương (phí 1 lần D32) HOẶC ÂM (giảm trừ/miễn giảm D33) - block nếu tổng âm EC17"]
    AdjustLines --> ReviewInvoice{Chủ trọ duyệt hóa đơn?}
    ReviewInvoice -->|Hóa đơn sai sót| VoidInvoice[Đánh dấu 'void' - Tạo hóa đơn mới thay thế] --> EndBillFail([Dừng - chờ chủ trọ duyệt tiếp phòng khác])
    ReviewInvoice -->|Hợp lệ| IssueInvoice[Phát hành hóa đơn]

    IssueInvoice --> GenDynamicQR[Sinh mã VietQR động định danh: tiền phòng lẻ + mã HĐ]
    GenDynamicQR --> PushToRoomChat[Bot gửi Card hóa đơn + QR vào Chat riêng phòng D24']

    PushToRoomChat --> TenantPaymentBranch{Hình thức khách thanh toán D29}

    TenantPaymentBranch -->|Quét VietQR qua App Ngân hàng bất kỳ| BankTransfer[Khách chuyển khoản ngân hàng]
    BankTransfer --> WebhookReceived[Hệ thống nhận Webhook thanh toán từ ngân hàng]
    WebhookReceived --> ReconMatch[Tự động đối soát khớp mã định danh hóa đơn - KHÔNG khớp theo số tiền]
    ReconMatch --> CheckVoided{Invoice còn hiệu lực? status != 'void'}
    CheckVoided -->|Đã bị void| VoidWebhook[Ghi nhận Payment + Đánh cờ cảnh báo chủ trọ đối soát - KHÔNG set paid - D33⑤]
    CheckVoided -->|Hợp lệ| SumPaid[Σ Payment success]

    SumPaid -->|Σ == total| MarkPaidAuto[Invoice: 'paid' - Ghi nhận Payment: success]
    SumPaid -->|0 < Σ < total| MarkPartial[Invoice: 'partially_paid' - hiển thị 'đã thu X / còn nợ Y' - D33③]
    SumPaid -->|Σ > total| MarkOverpay[Invoice: 'paid' - ghi đủ số thực nhận, nhắc 'thu dư Z' khi mở tab History - D33]

    TenantPaymentBranch -->|Khách trả tiền mặt| PayCash[Khách đưa tiền mặt cho Chủ trọ]
    PayCash --> ManualCashEntry[Chủ trọ ghi nhận thủ công: method = cash]
    ManualCashEntry --> SumPaid

    TenantPaymentBranch -->|Quá hạn chưa trả đủ| CheckOverdue[Hệ thống quét định kỳ Invoice quá due_date còn nợ]
    CheckOverdue --> MarkOverdue[Chuyển Invoice sang 'overdue' - vẫn giữ số đã thu nếu đã trả một phần]
    MarkOverdue --> BotRemind[Bot gửi tin nhắn nhắc nợ vào Chat phòng + FCM push]

    MarkPaidAuto --> UpdateRevenueDash[Cập nhật Doanh thu & Công nợ trên Dashboard D20]
    MarkPartial --> UpdateRevenueDash
    MarkOverpay --> UpdateRevenueDash
    MarkOverdue --> UpdateRevenueDash
    VoidWebhook --> UpdateRevenueDash
    BotRemind --> UpdateRevenueDash
    UpdateRevenueDash --> EndBillSuccess([Hoàn tất chu trình - lặp lại cho phòng tiếp theo trong danh sách])
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
    
    AutoExpire --> FinalMeterClosing[Chốt số lần cuối — phải đủ cả ĐIỆN và NƯỚC]
    SetTermStatus --> FinalMeterClosing
    
    FinalMeterClosing --> FinalInvoiceGen[Tạo hóa đơn tháng cuối: tiền phòng prorate theo ngày ở thực tế, điện/nước theo lượng thực đọc — xem utility-billing-calculations.md §8]
    FinalInvoiceGen --> FinalInvoicePay[Khách thanh toán hóa đơn cuối qua QR hoặc tiền mặt]
    
    FinalInvoicePay --> SettleDeposit{Xử lý thanh lý tiền cọc}
    SettleDeposit --> CalcDeduction[Tính toán các khoản cấn trừ nếu có hư hỏng/nợ cước]
    CalcDeduction --> ExternalDepositSettle[Hoàn trả tiền cọc còn lại thực tế ngoài hệ thống: Tiền mặt/Bank]
    
    ExternalDepositSettle --> MarkContractClosed[Chủ trọ đánh dấu 'Đã thanh lý cọc và bàn giao phòng']
    MarkContractClosed --> FreeRoomStatus[Hệ thống giải phóng phòng: chuyển về 'available']
    
    FreeRoomStatus --> RoomMapUpdate[Phòng hiển thị trống trên Room Map & sẵn sàng cho thuê mới]
    RoomMapUpdate --> EndTermSuccess([Kết thúc trọn vẹn vòng đời hợp đồng])
```

---

## 10. Landlord Utility & Fee Settings Flow (Module 6 — Cài đặt đơn giá & phí)

```mermaid
flowchart TD
    StartSettings([Vào Cài đặt đơn giá & phí]) --> Settab{Chọn tab}

    Settab -->|Tab: Đơn giá mặc định| TabGlobal[Danh sách policy LandlordProfile: điện + nước hiện hiệu lực]
    Settab -->|Tab: Đơn giá theo Tòa/Phòng| TabScope[Chọn Tòa → thiết lập nâng cao override phòng]
    Settab -->|Tab: Phí định kỳ| TabFees[Danh sách RecurringFee theo tòa/phòng]

    TabGlobal --> ViewGlobal{Đổi giá mặc định?}
    ViewGlobal -->|Có| PickPreset[Chọn preset D31 cho loại cần đổi - ĐIỆN: Giá theo EVN / 1 số cố định - D33 bỏ khoán đầu người; NƯỚC: Khoán đầu người / Đồng giá theo m³ / Bậc theo vùng]
    PickPreset --> NewPolicy[App tạo UtilityRatePolicy MỚI có effective_from = kỳ sau - không sửa policy cũ]
    NewPolicy --> RepointGlobal[Trỏ LandlordProfile.elec_policy_id / water_policy_id sang policy mới]
    RepointGlobal --> DoneGlobal[Lưu - kỳ sau tính theo giá mới]
    ViewGlobal -->|Không| DoneGlobal

    TabScope --> PickBld[Chọn Tòa nhà]
    PickBld --> ScopeAction{Chọn tác vụ}
    ScopeAction -->|Override cho Tòa| PickPresetBld[Chọn preset cho điện/nước - App tạo policy scope building]
    PickPresetBld --> SetBldPolicy[Trỏ Building.elec_policy_id / water_policy_id]
    ScopeAction -->|Override cho từng Phòng| PickRoom[Chọn phòng]
    PickRoom --> PickPresetRoom[Chọn preset - App tạo policy scope room]
    PickPresetRoom --> SetRoomPolicy[Trỏ Room.elec_policy_id / water_policy_id]
    SetBldPolicy --> DoneScope[Áp dụng - NULL trước đó vẫn kế thừa cấp trên]
    SetRoomPolicy --> DoneScope

    TabFees --> FeeAction{Thao tác phí}
    FeeAction -->|Thêm phí mới| PickScopeFee[Chọn phạm vi: Áp cả nhà - mặc định mọi tòa/phòng, hoặc Tòa - mọi phòng trong tòa, hoặc Phòng riêng]
    PickScopeFee --> PickFeeKind[Chọn loại phí: preset mẫu Wifi/QLVH/Gửi xe/Vệ sinh rác/Phí tự nhập]
    PickFeeKind --> FillFee[Auto điền fee_kind + unit_price mẫu, chủ trọ xác nhận hoặc chỉnh số]
    FillFee --> FeeEffective[Xác lập effective_from/to]
    FeeEffective --> SaveFee[Lưu RecurringFee]
    FeeAction -->|Sửa/Ngưng phí hiện hữu| EditFee[Tạo bản mới hoặc đặt effective_to / is_active=false - không sửa bản đã phát sinh hóa đơn]
    EditFee --> SaveFee
    SaveFee --> DoneFees[Cập nhật tức thì cho kỳ chưa lập hóa đơn]

    DoneGlobal --> EndSettings([Hoàn tất cấu hình - áp dụng từ kỳ sau])
    DoneScope --> EndSettings
    DoneFees --> EndSettings
```
