# Product → Platform Map

> P2-01 output: Liệt kê feature từ user flow → xác định quyền (tenant/landlord/anonymous) + nền tảng (Web/Mobile).
> Owner: PM (draft) · FE + Mobile (verify)
>
> **v1.2 — Kiến trúc App:** Đã chuyển từ "1 app chung + chọn vai trò" sang **5 app/project độc lập theo vai trò**: Tenant Mobile, Landlord Mobile, Tenant Web, Landlord Web, Admin Web (Admin tách hẳn khỏi Landlord, không lồng vào nhau). Bỏ màn "Chọn vai trò" và "Landing Chủ trọ" — không còn cần thiết. Chi tiết đầy đủ ở `UI_Screen_Outline_v0_1.md` mục J.8 và 2 file prompt Stitch.

---

## 1. Cách đọc bảng

| Cột | Ý nghĩa |
|-----|---------|
| **Tenant View** | Tenant có thể xem feature này |
| **Tenant Edit** | Tenant có thể tạo/sửa/xóa dữ liệu |
| **Landlord View** | Chủ trọ có thể xem feature này |
| **Landlord Edit** | Chủ trọ có thể tạo/sửa/xóa dữ liệu |
| **Anonymous** | Khách vãng lai (chưa login) truy cập được |
| **Web** | Feature có trên nền tảng Web (React) |
| **Mobile** | Feature có trên nền tảng Mobile (Kotlin/Android) |

**Ghi chú:** ✅ = có · — = không

---

## 2. Feature → Platform Map

### A. Xác thực & Đăng xuất

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| A1 | Đăng nhập (Email + Mật khẩu) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Cổng riêng cho từng role |
| A2 | Đăng ký tài khoản | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Tenant & Landlord đều đăng ký được, cả web và mobile |
| A3 | Đăng xuất | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ | Hủy token, xóa storage, ngắt socket |

### B. Hồ sơ & Cài đặt cá nhân

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| B1 | Quản lý hồ sơ cá nhân | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ | Sửa tên, SĐT, ảnh đại diện |
| B2 | Cài đặt thông báo | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ | Bật/tắt theo loại: hóa đơn, chat, sự cố |
| B3 | Kiểm tra trạng thái tài khoản | ✅ | — | ✅ | — | — | ✅ | ✅ | Tenant khóa vẫn xem+thanh toán HĐ hiện tại |

### C. Tìm phòng (Guest-first)

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| C1 | Bộ lọc tìm phòng | ✅ | — | ✅ | — | ✅ | ✅ | ✅ | Filter giá, diện tích, tiện nghi. Hiện tại chỉ có filter → danh sách, chưa có bản đồ |
| C2 | Danh sách kết quả phòng | ✅ | — | ✅ | — | ✅ | ✅ | ✅ | Card: ảnh, giá, khu vực, số phòng trống |
| C3 | Chi tiết phòng | ✅ | — | ✅ | — | ✅ | ✅ | ✅ | Gallery ảnh, mô tả, tiện nghi, giá, SĐT landlord |
| C4 | Lưu phòng yêu thích | ✅ | ✅ | ✅ | — | — | ✅ | ✅ | Cần login |

### D. Quản lý Bất động sản & Phòng trọ

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| D1 | Tạo Dãy trọ / Tòa nhà | — | — | ✅ | ✅ | — | ✅ | ✅ | Bắt buộc upload Sổ đỏ/giấy tờ đất |
| D2 | Upload bằng chứng sở hữu (Sổ đỏ) | — | — | ✅ | ✅ | — | ✅ | ✅ | Ảnh Sổ đỏ / Giấy QSDĐ / HĐ ủy quyền |
| D3 | Cấu hình đơn giá điện nước (Bước 3/3 khi tạo Tòa) | — | — | ✅ | ✅ | — | ✅ | ✅ | Xem chi tiết ở nhóm I (I1a-d): chọn loại → cấu hình cụ thể |
| D4 | Thêm Phòng trọ | — | — | ✅ | ✅ | — | ✅ | ✅ | Chỉ BĐS đã duyệt mới thêm được phòng |
| D5 | Xem danh sách Phòng trọ (Room Map) | ✅ | — | ✅ | — | ✅ | ✅ | ✅ | Tenant & Anonymous đều xem được. Sơ đồ tòa nhà, trạng thái phòng |
| D6 | Chỉnh sửa thông tin phòng | — | — | ✅ | ✅ | — | ✅ | ✅ | Sửa diện tích, giá, tiện nghi, ràng buộc |

### E. Hợp đồng & Check-in/out

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| E1 | Tạo Hợp đồng thuê | — | — | ✅ | ✅ | — | ✅ | ✅ | Nhập thông tin người đại diện, tiền cọc, thời hạn. Thành viên (kèm khai báo xe) thêm SAU ở mục Thành viên |
| E2 | Chọn & Xuất mẫu HĐ (PDF) | — | — | ✅ | ✅ | — | ✅ | ✅ | Chọn mẫu có sẵn → xuất PDF điền sẵn |
| E3 | Tải lên file HĐ đã ký (wet-sign) | — | — | ✅ | ✅ | — | ✅ | ✅ | Upload ảnh/PDF hợp đồng giấy ký tay 2 bên |
| E4 | Check-out & Thanh lý phòng | — | — | ✅ | ✅ | — | ✅ | ✅ | Chốt số cuối, quyết toán cọc, lưu trữ chat |
| E5 | Xem hợp đồng (read-only) | ✅ | — | ✅ | — | — | ✅ | ✅ | Tiền thuê, cọc, thời hạn, file đã ký |

### F. Quản lý Thành viên

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| F1 | Thêm thành viên ở ghép | — | — | ✅ | ✅ | — | ✅ | ✅ | Nhập Họ tên, SĐT, CCCD, toggle "Có xe: Có/Không" → tự add vào Chat |
| F2 | Xóa thành viên rời đi | — | — | ✅ | ✅ | — | ✅ | ✅ | Xóa khỏi phòng + rút khỏi Chat (cần xác nhận) |
| F3 | Xem danh sách thành viên | ✅ | — | ✅ | — | — | ✅ | ✅ | Tenant: read-only chỉ thấy tên. Landlord: thấy thêm icon xe nếu "Có xe" |

### G. Chốt số Điện/Nước (Landlord thao tác — CẢ Web lẫn Mobile, tương đương chức năng)

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| G1 | Chụp ảnh công tơ (Camera/Webcam trong app) | — | — | ✅ | ✅ | — | ✅ | ✅ | Mobile: Camera app. Web: Webcam trình duyệt. Chỉ landlord thao tác |
| G2 | Tải ảnh công tơ từ máy | — | — | ✅ | ✅ | — | ✅ | ✅ | Chỉ landlord mới có quyền này |
| G3 | Hiệu chỉnh tay số đọc | — | — | ✅ | ✅ | — | ✅ | ✅ | Sửa tay khi OCR sai + giữ ảnh evidence |

### H. Hóa đơn & Thanh toán (CẢ Web lẫn Mobile, tương đương chức năng)

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| H1 | Lập Hóa đơn tháng (kèm phí 1 lần) | — | — | ✅ | ✅ | — | ✅ | ✅ | Tiền phòng + dịch vụ + other_fees, phát hành |
| H2 | Tạo mã VietQR động | — | — | ✅ | ✅ | — | ✅ | ✅ | Mã QR gắn `Invoice.code` + đúng số tiền (D39: đối soát theo mã, không theo amount) |
| H3 | Xem chi tiết hóa đơn | ✅ | — | ✅ | — | — | ✅ | ✅ | Tiền phòng + breakdown dịch vụ, trạng thái |
| H4 | Thanh toán qua VietQR | ✅ | ✅ | — | — | — | ✅ | ✅ | Quét mã QR → chuyển khoản qua app ngân hàng |
| H5 | Xác nhận thu tiền mặt | — | — | ✅ | ✅ | — | ✅ | ✅ | Landlord xác nhận khi tenant nộp tiền mặt (hỗ trợ thu 1 phần) |
| H6 | Theo dõi trạng thái thanh toán | ✅ | — | ✅ | — | — | ✅ | ✅ | Đã thanh toán / Đã thu một phần / Quá hạn |
| H7 | Sửa/Hủy hóa đơn đã phát hành | — | — | ✅ | ✅ | — | ✅ | ✅ | Chỉ khi hóa đơn CHƯA có thanh toán nào |

### I. Cài đặt Đơn giá & Phí định kỳ

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| I1a | Chọn loại biểu giá điện/nước | — | — | ✅ | ✅ | — | ✅ | ✅ | Bước 1: chọn 1 trong 3 loại — Cố định / EVN bậc thang / Khoán theo đầu người |
| I1b | Cấu hình biểu giá — Cố định | — | — | ✅ | ✅ | — | ✅ | ✅ | Bước 2 (nếu chọn Cố định): 1 ô đơn giá điện + 1 ô đơn giá nước |
| I1c | Cấu hình biểu giá — EVN bậc thang | — | — | ✅ | ✅ | — | ✅ | ✅ | Bước 2 (nếu chọn EVN): bảng nhiều bậc (từ-đến kWh + đơn giá), thêm/xóa bậc |
| I1d | Cấu hình biểu giá — Khoán đầu người | — | — | ✅ | ✅ | — | ✅ | ✅ | Bước 2 (nếu chọn Khoán): 1 ô đ/người/tháng |
| I1e | Sửa lại biểu giá đã cấu hình | — | — | ✅ | ✅ | — | ✅ | ✅ | Vào lại từ Chi tiết Tòa nhà, quay lại I1a để đổi loại/số liệu |
| I1f | Ghi đè biểu giá cấp Phòng (nâng cao) | — | — | ✅ | ✅ | — | ✅ | ✅ | Ẩn dưới mục "Nâng cao" ở Chi tiết Phòng — dùng lại luồng I1a-d nhưng phạm vi 1 phòng |
| I2 | Cấu hình phí định kỳ (trong `RatePolicy.rates[]`) | — | — | ✅ | ✅ | — | ✅ | ✅ | Preset Wifi/QLVH/Gửi xe/Vệ sinh + phí tự nhập (D39: gộp vào bộ đơn giá, bỏ bảng `RecurringFee` riêng) |
| I3 | Cài đặt chu kỳ quét nợ tự động | — | — | ✅ | ✅ | — | ✅ | ✅ | Hạn thanh toán, ngày nhắc, bật/tắt bot. 3 cấp |

### J. Property Chat & Inbox (CẢ Web lẫn Mobile — hợp nhất 1 Inbox: Chat riêng 1-1 + Chat nhóm phòng + Chat chung tòa + Chat Match)

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| J1 | Chat riêng 1-1 (trước khi có HĐ) | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ | Gắn theo Landlord (không theo phòng). Cần login |
| J2 | Chat nhóm phòng | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ | Text, ảnh, file + bot card. Tự tạo khi HĐ active. Chuyển read-only khi HĐ kết thúc |
| J3 | Chat chung tòa | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ | Text, ảnh, file + @mention. KHÔNG có bot card |
| J4 | @mention thành viên/landlord | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ | Autocomplete gắn tên trong chat |
| J5 | Bot auto-remind nhắc thu | ✅ | — | ✅ | — | — | ✅ | ✅ | Bot post card nhắc vào chat theo `BillingSetting.remind_day` (D39: nhắc ngày thu dự kiến, không phải nhắc quá hạn, không ghi trạng thái) |
| J6 | Bot thông báo sự cố | ✅ | — | ✅ | — | — | ✅ | ✅ | Bot post card + push khi có sự cố mới |
| J7 | Chat Match Roommate (peer-to-peer) | ✅ | ✅ | — | — | — | ✅ | ✅ | Mở tự động sau khi match thành công, thay cho việc lộ SĐT/Zalo |

### K. Sự cố (CẢ Web lẫn Mobile, tương đương chức năng)

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| K1 | Tạo báo cáo sự cố | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ | Mô tả + đính kèm ảnh (camera/thư viện tự do). Cả 2 bên tạo được |
| K2 | Quản lý Sự cố (Tab riêng) | — | — | ✅ | ✅ | — | ✅ | ✅ | Xem danh sách, lọc trạng thái, điều phối. Luôn hiện nhãn Tòa nhà—Phòng |
| K3 | Cập nhật trạng thái sự cố | — | — | ✅ | ✅ | — | ✅ | ✅ | Đang xử lý / Đã hoàn thành / Hủy. Popup có nút "Xem trong Chat phòng" |
| K4 | Theo dõi sự cố | ✅ | — | ✅ | — | — | ✅ | ✅ | Tenant xem tất cả sự cố phòng mình, popup có khung trao đổi tích hợp |

### L. Ghép bạn / Roommate Matching (CẢ Web lẫn Mobile — Guest xem Feed không cần login)

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| L1 | Feed ghép bạn | ✅ | — | — | — | ✅ | ✅ | ✅ | Guest/chưa login vẫn xem được feed (giống Tìm phòng) — chỉ gate login ở Gửi yêu cầu/Tạo hồ sơ/Chat |
| L2 | Tạo/sửa hồ sơ ghép bạn | ✅ | ✅ | — | — | — | ✅ | ✅ | 1 tài khoản = 1 hồ sơ. Có toggle "Tìm bạn ở ghép: Bật/Tắt" |
| L3 | Gửi/nhận match request | ✅ | ✅ | — | — | — | ✅ | ✅ | 2 chiều: gửi → chờ → chấp nhận/từ chối ngay trên item list |
| L4 | Match thành công → mở Chat trong app | ✅ | ✅ | — | — | — | ✅ | ✅ | Mở thẳng Chat Match Roommate trong app — KHÔNG lộ SĐT/Zalo |

### M. Quản trị Hệ thống (Admin)

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| M1 | Dashboard tổng quan | — | — | — | — | — | ✅ | — | Số BĐS chờ duyệt, user hoạt động, thống kê |
| M2 | Phê duyệt BĐS (Sổ đỏ/Giấy tờ đất) | — | — | — | — | — | ✅ | — | Kiểm tra tay giấy tờ → Phê duyệt / Từ chối |
| M3 | Quản lý Người dùng | — | — | — | — | — | ✅ | — | Xem danh sách, tìm kiếm, khóa/mở khóa |
| M4 | Khóa tài khoản Landlord | — | — | — | — | — | ✅ | — | Ẩn BĐS/Phòng, tạm ngưng HĐ |
| M5 | Khóa tài khoản Tenant | — | — | — | — | — | ✅ | — | Chặn gia hạn/thuê mới, giữ quyền xem+thanh toán |
| M6 | Mở khóa tài khoản | — | — | — | — | — | ✅ | — | Khôi phục quyền hạn + HĐ liên quan |
| M7 | Giám sát Audit Log | — | — | — | — | — | ✅ | — | Nhật ký: khóa/mở khóa, phê duyệt, webhook |
| M8 | Xử lý vòng đời HĐ khi khóa/mở khóa | — | — | — | — | — | ✅ | — | Tam ngung → Grace Period → auto-cancel + hoan coc |

### N. Thanh toán Online

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| N1 | Webhook ngân hàng đối soát | — | — | ✅ | — | — | — | — | **D39 → STRETCH.** MVP chỉ `mock`/`cash` + VietQR sandbox; nhận callback thật cần merchant/đối tác + idempotency + verify chữ ký. Đối soát MVP theo `Invoice.code` do chủ trọ xác nhận |
| N2 | Tích hợp VNPay/MoMo (Stretch) | ✅ | ✅ | — | — | — | ✅ | ✅ | Nice-to-have — thêm làm kênh thứ 3 bên cạnh VietQR/Tiền mặt ở màn Thanh toán |

### O. AI Features

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| O1 | AI Auto-Description (MVP) | — | — | ✅ | ✅ | — | ✅ | ✅ | Ở màn Thêm Phòng: nhập keyword → nút "✨ Tạo mô tả bằng AI" → tự điền ô Mô tả |
| O2 | AI Matchmaking (Stretch) | ✅ | — | — | — | — | ✅ | ✅ | Badge nhỏ "Độ phù hợp: 87%" trên Feed & Chi tiết hồ sơ Ghép bạn. Cần login |

---

## 3. Tổng hợp theo nền tảng

> **Nguyên tắc:** Bảng dưới đây thể hiện feature nào áp dụng cho nền tảng nào — về mặt CHỨC NĂNG, Web và Mobile tương đương 100% cho Tenant và Landlord. Tuy nhiên, kể từ **v1.2**, Tenant và Landlord chạy trên **app/project hoàn toàn tách biệt** (không còn 1 codebase chung + route theo vai trò): **Tenant Mobile, Landlord Mobile, Tenant Web, Landlord Web, Admin Web — 5 app độc lập**. Cột "Web"/"Mobile" trong bảng dưới nghĩa là "feature này có ở phiên bản Web/Mobile của app tương ứng vai trò đó", không ngụ ý dùng chung 1 app nữa. Admin luôn là app riêng biệt thứ 5, chỉ có Web.

| Nhóm | Features | Web | Mobile |
|------|----------|:---:|:------:|
| Auth | A1–A3 | ✅ | ✅ |
| Hồ sơ | B1–B3 | ✅ | ✅ |
| Tìm phòng | C1–C4 | ✅ | ✅ |
| BĐS & Phòng | D1–D6 | ✅ | ✅ |
| Hợp đồng | E1–E5 | ✅ | ✅ |
| Thành viên | F1–F3 | ✅ | ✅ |
| Chốt số | G1–G3 | ✅ | ✅ |
| Hóa đơn | H1–H7 | ✅ | ✅ |
| Cài đặt | I1a–I3 | ✅ | ✅ |
| Chat | J1–J7 | ✅ | ✅ |
| Sự cố | K1–K4 | ✅ | ✅ |
| Ghép bạn | L1–L4 | ✅ | ✅ |
| Thanh toán | N1–N2 | ✅ | ✅ |
| AI | O1–O2 | ✅ | ✅ |
| Quản trị | M1–M8 | ✅ | ❌ (Web only) |
| **Total** | | **~85 features** | **~81 features** |

---

## 4. Quy định đặc biệt (sau khi verify với team)

| # | Quy định |
|---|----------|
| 1 | Guest xem được Feed Ghép bạn KHÔNG cần login (giống Tìm phòng) — chỉ gate login ở hành động Gửi yêu cầu / Tạo hồ sơ / Chat. |
| 2 | Chat chung tòa CHỈ có text/ảnh/file + @mention, KHÔNG có bot card. Bot chỉ ở chat riêng phòng. |
| 3 | Admin có Dashboard tổng quan (số BĐS chờ duyệt, user hoạt động, thống kê cơ bản) — KHÔNG có biểu đồ (khác Landlord Dashboard). Admin là ngoại lệ duy nhất chỉ có Web, không có Mobile. |
| 4 | Landlord-lite xem hóa đơn với ĐẦY ĐỦ breakdown (tiền phòng, điện, nước, phí), không chỉ xem tổng. |
| 5 | Bộ lọc tìm phòng hiện tại chỉ có filter → danh sách, CHƯA có bản đồ (kế hoạch tương lai). Landlord cũng xem được danh sách phòng. |
| 6 | Khai báo xe KHÔNG nằm trong Hợp đồng — chuyển sang mục Thành viên, đơn giản hóa thành toggle "Có xe: Có/Không" cho từng thành viên. |
| 7 | Web và Mobile tương đương 100% chức năng cho Tenant/Landlord (chỉ khác bố cục trình bày). Admin là ngoại lệ duy nhất: chỉ có Web. |
| 8 | Sau khi HĐ kết thúc (check-out), Property Chat của phòng đó chuyển sang trạng thái read-only/archive — không xóa lịch sử, chỉ khóa gửi tin mới. |
| 9 | Biểu giá điện/nước + phí định kỳ nằm trong **một bộ `RatePolicy.rates[]`** theo scope `building`/`room`, kế thừa `room → building`; chỉ UPDATE tại chỗ, không versioning (D39). |
| 10 | AI Auto-Description (O1) và AI Matchmaking (O2) đều có trên cả Web & Mobile. VNPay/MoMo (N2) là kênh thanh toán thứ 3 bên cạnh VietQR/Tiền mặt — **Stretch**. |

---

## 5. Verification

- [ ] FE đọc bảng map → xác nhận / đề xuất sửa
- [ ] Mobile đọc bảng map → xác nhận / đề xuất sửa
- [ ] PM tổng hợp → chốt final
- [ ] Không có open question chưa resolve
