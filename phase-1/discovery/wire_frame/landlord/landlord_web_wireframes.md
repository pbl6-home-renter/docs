# LANDLORD WEB WIREFRAMES SPECIFICATION (LOW-FIDELITY)
**Hệ thống:** Rentify Property Rental Management
**Nền tảng:** Responsive Desktop Web (Viewport 1440 × 1024 px)
**Vai trò:** Landlord (Chủ trọ vận hành)
**Kiến trúc:** All-in-One Hub (Zalo-style) kết hợp Menu Tiện Ích "Ba Chấm (...)" trượt Drawer
**Nguồn căn cứ:** Phase 1 Approved Plan, `updated_landlord_user_flow.md`, Linear Comments `PBL-29`, Decisions `D1–D29`

---

## 1. MẪU BỐ CỤC CHUẨN (APPLICATION SHELL - 1440 × 1024 px)

```
+---------------------------------------------------------------------------------------------------------------+
| LOGO: RENTIFY CHỦ TRỌ  |  [1. DASHBOARD]  [2. BẤT ĐỘNG SẢN]  [3. TIN NHẮN (HUB)]*  [4. CÀI ĐẶT] | [Avatar v]   |
+---------------------------------------------------------------------------------------------------------------+
|                                                                                                               |
|                                       KHU VỰC NỘI DUNG CHÍNH CỦA TAB ĐƯỢC CHỌN                                |
|                                                                                                               |
+---------------------------------------------------------------------------------------------------------------+
```

---

## 2. CHI TIẾT CÁC MÀN HÌNH CHỦ TRỌ (LANDLORD SCREENS)

### SCR-LL-01: Landlord Dashboard (`/dashboard`)
* **Mục đích:** Sơ đồ phòng trực quan (Room Map D20) phân màu trạng thái kết hợp biểu đồ doanh thu và công nợ.
* **Wireframe:**
```
+---------------------------------------------------------------------------------------------------------------+
| RENTIFY CHỦ TRỌ  |  [DASHBOARD]*  [BẤT ĐỘNG SẢN]  [TIN NHẮN]  [CÀI ĐẶT]        | [Cơ sở: Tất cả tòa nhà v]   |
+---------------------------------------------------------------------------------------------------------------+
| BÁO CÁO TÀI CHÍNH & VẬN HÀNH THÁNG 08/2026                                                                    |
| +-------------------------+-------------------------+-------------------------+-----------------------------+ |
| | THỰC THU THÁNG NÀY      | CÔNG NỢ ĐẾN HẠN         | TỶ LỆ LẤP ĐẦY PHÒNG     | SỰ CỐ ĐANG XỬ LÝ            | |
| | 48,500,000 đ            | 12,350,000 đ            | 91.6% (22/24 Phòng)     | 2 Sự cố                     | |
| | (Đã thu 18/22 phòng)    | (4 phòng chưa thanh toán| [|||||||||||||||||||--] | (1 điện nước, 1 điều hòa)   | |
| +-------------------------+-------------------------+-------------------------+-----------------------------+ |
|                                                                                                               |
| SƠ ĐỒ PHÒNG TRỰC QUAN (ROOM MAP - D20)                                [ Lọc: [X] Tất cả  [ ] Trống  [ ] Nợ ]  |
| Chuẩn màu: [Xanh lá: Available (Trống)]   [Xám: Occupied (Đang thuê)]   [Vàng: Maintenance (Bảo trì)]         |
|                                                                                                               |
| TÒA A - 123 NGUYỄN LƯƠNG BẰNG (12 PHÒNG)                                                                      |
| +--------------------+ +--------------------+ +--------------------+ +--------------------+                   |
| | P.101 (XÁM)        | | P.102 (XÁM)        | | P.103 (XANH LÁ)    | | P.104 (VÀNG)       |                   |
| | Thuê: Thái Bảo     | | Thuê: Thu Phương   | | [ TRỐNG - SẴN SÀNG]| | [ ĐANG BẢO TRÌ ]   |                   |
| | HĐ: 3,5tr [Đã thu] | | HĐ: 3,8tr [NỢ TIỀN]| | Giá: 3,5tr/tháng   | | Đang sửa điều hòa  |                   |
| +--------------------+ +--------------------+ +--------------------+ +--------------------+                   |
| +--------------------+ +--------------------+ +--------------------+ +--------------------+                   |
| | P.201 (XÁM)        | | P.202 (XÁM)        | | P.203 (XÁM)        | | P.204 (XANH LÁ)    |                   |
| | Thuê: Hoàng Long   | | Thuê: Minh Tuấn    | | Thuê: Quỳnh Nga    | | [ TRỐNG - SẴN SÀNG]|                   |
| | HĐ: 4,0tr [Đã thu] | | HĐ: 4,2tr [Đã thu] | | HĐ: 4,0tr [NỢ TIỀN]| | Giá: 4,0tr/tháng   |                   |
| +--------------------+ +--------------------+ +--------------------+ +--------------------+                   |
+---------------------------------------------------------------------------------------------------------------+
```

---

### SCR-LL-02: Property Directory & Room Structure (`/properties`)
* **Mục đích:** Quản lý cấu trúc Tòa nhà - Tầng - Phòng; cung cấp lối tắt thêm mới.
* **Wireframe:**
```
+---------------------------------------------------------------------------------------------------------------+
| RENTIFY CHỦ TRỌ  |  [DASHBOARD]  [BẤT ĐỘNG SẢN]*  [TIN NHẮN]  [CÀI ĐẶT]                                       |
+---------------------------------------------------------------------------------------------------------------+
| QUẢN LÝ DANH MỤC BẤT ĐỘNG SẢN                           [ + Thêm Tòa Nhà ]  [ + Thêm Phòng Mới ]              |
|                                                                                                               |
| [DANH SÁCH TÒA NHÀ]               | CHI TIẾT CÁC PHÒNG THEO TẦNG: TÒA A (12 PHÒNG)                            |
| * Tòa A - 123 Nguyễn Lương Bằng   |                                                                           |
|   (12 phòng - Đầy: 10/12) (Active)| TẦNG 1:                                                                   |
| * Tòa B - 45 Cẩm Lệ               | | Phòng | Diện tích | Giá thuê   | Người thuê đại diện | Trạng thái | Action| |
|   (12 phòng - Đầy: 12/12)         | |-------|-----------|------------|---------------------|------------|-------| |
|                                   | | P.101 | 25 m2     | 3,500,000 đ| Thái Bảo (0905xxx)  | [Occupied] | [...] | |
|                                   | | P.102 | 28 m2     | 3,800,000 đ| Thu Phương (0912xxx)| [Occupied] | [...] | |
|                                   | | P.103 | 25 m2     | 3,500,000 đ| (Chưa có)           | [Available]| [Thuê]| |
|                                   | | P.104 | 25 m2     | 3,500,000 đ| (Đang sửa chữa)     | [Maint]    | [...] | |
|                                   |                                                                           |
|                                   | TẦNG 2:                                                                   |
|                                   | | P.201 | 30 m2     | 4,000,000 đ| Hoàng Long (0988xxx)| [Occupied] | [...] | |
|                                   | | P.202 | 32 m2     | 4,200,000 đ| Minh Tuấn (0977xxx) | [Occupied] | [...] | |
+---------------------------------------------------------------------------------------------------------------+
```

---

### SCR-LL-03: Building Form Modal with Map Location Picker
* **Mục đích:** Tạo/sửa tòa nhà kèm kéo thả ghim vị trí địa lý (Pin Drag & Drop / GPS) và override giá tòa (D16).
* **Wireframe (Modal căn giữa):**
```
+-------------------------------------------------------------------------------+
| THÊM TÒA NHÀ MỚI                                                          [X] |
+-------------------------------------------------------------------------------+
| Tên tòa nhà (*):    [ Tòa A - Khu Ký Túc Xá                                 ] |
| Địa chỉ (*):        [ 123 Nguyễn Lương Bằng, Phường Hòa Khánh Bắc, Đà Nẵng  ] |
| Số tầng:            [ 4 ] tầng                                                |
|                                                                               |
| ĐỊNH VỊ VỊ TRÍ TRÊN BẢN ĐỒ (MAP PICKER)             [ Bấm: Lấy GPS hiện tại ] |
| +---------------------------------------------------------------------------+ |
| | [BẢN ĐỒ TƯƠNG TÁC GOOGLE MAPS / LEAFLET]                                  | |
| |                                                                           | |
| |                             [ (PIN ĐỊNH VỊ) ]                             | |
| |                     <- Kéo thả ghim để chọn vị trí chính xác ->           | |
| |                                                                           | |
| +---------------------------------------------------------------------------+ |
| Tọa độ đã chọn:   Vĩ độ (Lat): [ 16.074812 ]   Kinh độ (Long): [ 108.152345 ] |
|                                                                               |
| CẤU HÌNH ĐƠN GIÁ ĐIỆN NƯỚC CẤP TÒA (TÙY CHỌN - D16)                          |
| [ ] Ghi đè đơn giá riêng cho tòa nhà này (Nếu không chọn, kế thừa giá chung)  |
|                                                                               |
| [ HỦY BỎ ]                                            [ LƯU VÀ TẠO TÒA NHÀ ]  |
+-------------------------------------------------------------------------------+
```

---

### SCR-LL-04: Room Form Modal with D21 Constraints Setup
* **Mục đích:** Tạo phòng mới, gán `owner_id = Landlord` (D25) và cài đặt bộ lọc cứng ghép bạn (D21).
* **Wireframe (Modal căn giữa):**
```
+-------------------------------------------------------------------------------+
| THÊM PHÒNG TRỌ MỚI                                                        [X] |
+-------------------------------------------------------------------------------+
| Thuộc Tòa nhà (*): [ Tòa A - 123 Nguyễn Lương Bằng v]   Tầng: [ Tầng 2 v]     |
| Số phòng / Tên (*):[ P.204                         ]   Diện tích: [ 28 ] m2   |
| Giá thuê tháng (*):[ 4,000,000                     ] đ/tháng                  |
| Tiện nghi có sẵn:  [X] Điều hòa   [X] Nóng lạnh   [X] Tủ lạnh   [ ] Ban công  |
|                                                                               |
| THIẾT LẬP RÀNG BUỘC CỨNG GHÉP BẠN (HARD FILTERS - D21)                        |
| * Số người tối đa trong phòng:   [ 2 ] người (Chặn thêm người khi đủ)        |
| * Chính sách giới tính:          ( ) Tất cả   ( ) Chỉ Nam   (*) Chỉ Nữ        |
| * Nội quy phòng trọ:             [ Không nuôi chó mèo, không gây ồn sau 23h ] |
|                                                                               |
| QUYỀN SỞ HỮU & ĐƠN GIÁ (D25 & D16)                                            |
| * Chủ sở hữu phòng (owner_id):   [ Thái Bảo (Chính mình) - BẮT BUỘC D25 ]     |
| [ ] Ghi đè đơn giá điện nước riêng cho phòng này                              |
|                                                                               |
| [ HỦY ]                                                     [ TẠO PHÒNG MỚI ] |
+-------------------------------------------------------------------------------+
```

---

### SCR-LL-05: Check-in & Create Contract Drawer
* **Mục đích:** Ký hợp đồng check-in, AI OCR CCCD (5.6), sinh mẫu Word/PDF, tải file ký tay wet-sign (D18).
* **Wireframe (Drawer trượt từ phải sang):**
```
+-----------------------------------------------------------------------+=======================================+
|                                                                       | TẠO HỢP ĐỒNG & CHECK-IN PHÒNG 103 [X] |
|                                                                       +---------------------------------------+
|                                                                       | 1. THÔNG TIN NGƯỜI ĐẠI DIỆN KÝ (LEAD) |
|                                                                       | Họ và tên (*):  [ Lê Văn Hoàng      ] |
|                                                                       | Số điện thoại(*):[ 0905888999       ] |
|                                                                       | Ảnh chụp CCCD (Mặt trước) (D17/5.6):  |
|                                                                       | [ (ẢNH CCCD ĐÃ TẢI) - OCR THÀNH CÔNG] |
|                                                                       | * Số CCCD:      048201009999          |
|                                                                       | * Ngày sinh:    12/05/2002            |
|                                                                       | * Địa chỉ:      Hải Châu, Đà Nẵng     |
|                                                                       +---------------------------------------+
|                                                                       | 2. CẤU HÌNH THANH TOÁN Ở GHÉP (D22)   |
|                                                                       | (*) Đại diện đóng 100% (chia offline) |
|                                                                       | ( ) Hóa đơn chia sẻ (App theo dõi góp)|
|                                                                       +---------------------------------------+
|                                                                       | 3. ĐIỀU KHOẢN & TIỀN CỌC              |
|                                                                       | Tiền cọc:       [ 3,500,000         ]đ|
|                                                                       | Giá thuê tháng: [ 3,500,000         ]đ|
|                                                                       | Ngày bắt đầu:   [ 01/09/2026        ] |
|                                                                       | Thời hạn:       [ 6 ] tháng           |
|                                                                       +---------------------------------------+
|                                                                       | 4. KÝ TAY WET-SIGN VẬT LÝ (D18)       |
|                                                                       | [ NÚT: SINH MẪU HĐ ĐỂ IN (WORD/PDF) ] |
|                                                                       |                                       |
|                                                                       | Tải lên File/Ảnh HĐ ĐÃ KÝ TAY 2 BÊN:  |
|                                                                       | [ Kéo thả file hop_dong_p103_signed ] |
|                                                                       | File: hop_dong_p103_signed.pdf (1.2MB)|
|                                                                       +---------------------------------------+
|                                                                       | [  KÍCH HOẠT HỢP ĐỒNG & BÀN GIAO  ]   |
+-----------------------------------------------------------------------+=======================================+
```

---

### SCR-LL-06 & SCR-LL-07: Property Chat Hub & Room Message Stream (All-in-One Central)
* **Mục đích:** Trung tâm hội thoại all-in-one, tích hợp bot cards, lệnh `@issue`, và nút `...` mở Utility Drawer.
* **Wireframe:**
```
+---------------------------------------------------------------------------------------------------------------+
| RENTIFY CHỦ TRỌ  |  [DASHBOARD]  [BẤT ĐỘNG SẢN]  [TIN NHẮN (HUB)]*  [CÀI ĐẶT]                 | [Avatar v]    |
+-----------------------------------+---------------------------------------------------------------------------+
| DANH SÁCH HỘI THOẠI               | PHÒNG 101 - TÒA A (HĐ: Đang hoạt động)        [Thành viên: 2]   [ ... ]*  |
| [Chat Riêng Phòng]* [Chat Chung Tòa] +---------------------------------------------------------------------------+
|                                   | [Hôm nay]                                                                 |
| [P.101 - Tòa A] (Đang chọn)       | Tenant Thái Bảo: Dạ chú ơi, cho con hỏi tiền điện tháng này với ạ!        |
| Thái Bảo: Dạ con gửi tiền mặt...  | Chủ trọ (Bạn): Chú vừa chốt số công tơ xong nhé, để chú gửi hóa đơn.      |
| 09:30 - [Đã thu tiền]             |                                                                           |
|                                   | [BOT HỆ THỐNG] ---------------------------------------------------------+ |
| [P.102 - Tòa A]                   | | THẺ HÓA ĐƠN TIỀN NHÀ THÁNG 08/2026                                    | |
| Bot: Hóa đơn T08 đã quá hạn 2 ngày| | Tiền phòng: 3,500,000 đ  | Điện: 350,000 đ  | Nước: 80,000 đ          | |
| Hôm qua - [CẢNH BÁO NỢ]           | | TỔNG THANH TOÁN: 3,930,000 VNĐ                                        | |
|                                   | | [ MÃ VIETQR ĐỘNG ĐỊNH DANH ] (Quét bằng mọi App Ngân Hàng)            | |
| [P.201 - Tòa A]                   | | Trạng thái: [ CHƯA THANH TOÁN ]                                       | |
| Hoàng Long: Điều hòa chảy nước... | | [ Xem chi tiết ]   [ Xác nhận đã thu tiền mặt (D29) ]                 | |
| 04/09                             | +-----------------------------------------------------------------------+ |
|                                   |                                                                           |
| [P.202 - Tòa A]                   | Tenant Thái Bảo: @issue Vòi sen trong nhà tắm bị rò rỉ nước nhờ chú sửa   |
| Minh Tuấn: Đã nhận phòng chú nhé  |                                                                           |
| 01/09                             | [BOT HỆ THỐNG] ---------------------------------------------------------+ |
|                                   | | [THẺ SỰ CỐ #042] Vòi sen bị rò rỉ nước       Trạng thái: [TIẾP NHẬN]  | |
|                                   | | Người báo: Thái Bảo | Đã tự động cập nhật vào Tab Quản lý sự cố       | |
|                                   | +-----------------------------------------------------------------------+ |
|                                   +---------------------------------------------------------------------------+
|                                   | [ Nhập tin nhắn... (Gõ @mention hoặc @issue <mô tả>)           ] [GỬI]    |
+-----------------------------------+---------------------------------------------------------------------------+
```
*(Ghi chú: Khi chủ trọ click vào nút `[ ... ]` ở góc trên bên phải thanh chat, Drawer All-in-One Utility sẽ trượt ra chiếm 480px bên phải).*

---

### SCR-LL-08: Utility Drawer — Quản Lý Hợp Đồng & Thành Viên Ở Ghép
* **Mục đích:** Xem hợp đồng, thêm/xóa thành viên; Lead tenant không thể bị xóa; check giới hạn `maxOccupancy`.
* **Wireframe:**
```
+-----------------------------------------------------------------------+=======================================+
|                                                                       | TIỆN ÍCH: THÀNH VIÊN & HỢP ĐỒNG   [X] |
|                                                                       +---------------------------------------+
|                                                                       | HỢP ĐỒNG HIỆN TẠI: HĐ-2026-0812       |
|                                                                       | * Thời hạn: 01/08/2026 -> 01/02/2027  |
|                                                                       | * Giá thuê: 3,500,000 đ | Cọc: 3,5tr  |
|                                                                       | [ NÚT: XEM FILE HĐ ĐÃ KÝ (WET-SIGN) ] |
|                                                                       +---------------------------------------+
|                                                                       | DANH SÁCH THÀNH VIÊN (2 / Max 2 người)|
|                                                                       |                                       |
|                                                                       | 1. THÁI BẢO [CHỦ HỢP ĐỒNG / LEAD]     |
|                                                                       |    SĐT: 0905111222 - CCCD: 04820100xx |
|                                                                       |    [ Khóa - Không thể xóa Lead ]      |
|                                                                       |                                       |
|                                                                       | 2. NGUYỄN VĂN ANH [THÀNH VIÊN Ở CÙNG] |
|                                                                       |    SĐT: 0905999888 - Đã nộp CCCD      |
|                                                                       |    Phần đóng: 50% (1,750,000 đ)       |
|                                                                       |    [ X XÓA KHỎI PHÒNG ]               |
|                                                                       +---------------------------------------+
|                                                                       | [!] ĐÃ ĐẠT GIỚI HẠN SỐ NGƯỜI (MAX 2)  |
|                                                                       | [ + Thêm Thành Viên (Bị Disable) ]    |
|                                                                       |                                       |
|                                                                       | [!] Hộp thoại khi bấm Xóa thành viên: |
|                                                                       | "Xác nhận xóa Nguyễn Văn Anh? Chủ trọ |
|                                                                       |  đã quyết toán tiền cước ngoài app?"  |
+-----------------------------------------------------------------------+=======================================+
```

---

### SCR-LL-09: Utility Drawer — Chốt Số Điện / Nước (OCR)
* **Mục đích:** Chụp ảnh đồng hồ, AI OCR đọc số mới tự động, tính mức tiêu thụ, xác nhận 1 chạm (F3.3).
* **Wireframe:**
```
+-----------------------------------------------------------------------+=======================================+
|                                                                       | TIỆN ÍCH: CHỐT SỐ ĐIỆN NƯỚC (OCR) [X] |
|                                                                       +---------------------------------------+
|                                                                       | KỲ CHỐT: THÁNG 08/2026                |
|                                                                       +---------------------------------------+
|                                                                       | 1. CÔNG TƠ ĐIỆN                       |
|                                                                       | Chỉ số cũ:   [ 1240 ] kWh (Kỳ trước)  |
|                                                                       | Ảnh công tơ: [ (ẢNH CHỤP ĐỒNG HỒ ĐIỆN)]|
|                                                                       | AI OCR đọc:  [ 1340 ] kWh [Chính xác] |
|                                                                       | -> TIÊU THỤ: [ 100 ] kWh              |
|                                                                       +---------------------------------------+
|                                                                       | 2. ĐỒNG HỒ NƯỚC                       |
|                                                                       | Chỉ số cũ:   [ 45 ] m3                |
|                                                                       | Ảnh công tơ: [ (ẢNH CHỤP ĐỒNG HỒ NƯỚC)]|
|                                                                       | AI OCR đọc:  [ 53 ] m3 [Chính xác]    |
|                                                                       | -> TIÊU THỤ: [ 8 ] m3                 |
|                                                                       +---------------------------------------+
|                                                                       | [  XÁC NHẬN CHỐT SỐ (1 CHẠM)  ]       |
|                                                                       |                                       |
|                                                                       | * Ghi chú: Sau khi xác nhận, bot sẽ   |
|                                                                       |   tự động gửi kết quả đối chiếu vào   |
|                                                                       |   khung Chat riêng phòng.             |
+-----------------------------------------------------------------------+=======================================+
```

---

### SCR-LL-10: Utility Drawer — Hóa Đơn & VietQR Động Đối Soát Tự Động
* **Mục đích:** Tính toán chi phí (D16), phát hành VietQR động định danh (F3.10), hỗ trợ gạch nợ tiền mặt (D29).
* **Wireframe:**
```
+-----------------------------------------------------------------------+=======================================+
|                                                                       | TIỆN ÍCH: HÓA ĐƠN & VIETQR        [X] |
|                                                                       +---------------------------------------+
|                                                                       | HÓA ĐƠN KỲ THÁNG 08/2026              |
|                                                                       | Trạng thái: [ CHƯA THANH TOÁN (UNPAID)]|
|                                                                       +---------------------------------------+
|                                                                       | BẢNG KÊ CHI PHÍ CHI TIẾT:             |
|                                                                       | 1. Tiền phòng:           3,500,000 đ  |
|                                                                       | 2. Tiền điện (100 kWh):    350,000 đ  |
|                                                                       |    (Đơn giá 3,500đ - Theo giá Tòa)    |
|                                                                       | 3. Tiền nước (8 m3):        80,000 đ  |
|                                                                       |    (Đơn giá 10,000đ - Theo mặc định)  |
|                                                                       | 4. Rác & Internet:         100,000 đ  |
|                                                                       | ------------------------------------- |
|                                                                       | TỔNG CỘNG:               4,030,000 đ  |
|                                                                       +---------------------------------------+
|                                                                       | THANH TOÁN VIETQR ĐỘNG ĐỊNH DANH:     |
|                                                                       | +-----------------------------------+ |
|                                                                       | |      [ HÌNH ẢNH MÃ VIETQR ]       | |
|                                                                       | | Nội dung: RENTIFY P101 T08        | |
|                                                                       | | Số tiền:  4,030,000 VNĐ           | |
|                                                                       | +-----------------------------------+ |
|                                                                       | (Tự động gạch nợ khi nhận Webhook)    |
|                                                                       +---------------------------------------+
|                                                                       | THAO TÁC CỦA CHỦ TRỌ:                 |
|                                                                       | [ V XÁC NHẬN ĐÃ THU TIỀN MẶT (D29) ]  |
|                                                                       |                                       |
|                                                                       | [ ! HỦY HÓA ĐƠN ĐỂ LẬP LẠI (VOID) ]   |
+-----------------------------------------------------------------------+=======================================+
```

---

### SCR-LL-11: Utility Drawer — Quản Lý Báo Cáo Sự Cố
* **Mục đích:** Theo dõi sự cố của phòng, cập nhật trạng thái đồng bộ hai chiều với Thẻ sự cố trong Chat.
* **Wireframe:**
```
+-----------------------------------------------------------------------+=======================================+
|                                                                       | TIỆN ÍCH: SỰ CỐ KỸ THUẬT PHÒNG    [X] |
|                                                                       +---------------------------------------+
|                                                                       | [ + Tự tạo sự cố thay khách (D29) ]   |
|                                                                       +---------------------------------------+
|                                                                       | SỰ CỐ #042: VÒI SEN BỊ RÒ RỈ NƯỚC     |
|                                                                       | * Người báo: Thái Bảo (06/09 09:30)   |
|                                                                       | * Nguồn tạo: Lệnh @issue trong chat   |
|                                                                       | * Trạng thái hiện tại: [ ĐANG SỬA v ] |
|                                                                       |   - Đã liên hệ thợ điện nước chiều ghé|
|                                                                       | [ V Bấm: ĐÃ HOÀN THÀNH SỬA CHỮA ]     |
|                                                                       | [ X Hủy bỏ sự cố này ]                |
|                                                                       +---------------------------------------+
|                                                                       | SỰ CỐ #015: BÓNG ĐÈN BAN CÔNG CHÁY    |
|                                                                       | * Trạng thái: [ ĐÃ HOÀN THÀNH (XANH) ]|
|                                                                       | * Đã xử lý ngày: 20/08/2026           |
|                                                                       +---------------------------------------+
|                                                                       | * Khi đổi trạng thái tại đây, Thẻ sự  |
|                                                                       |   cố trong Chat tự động đổi màu tương |
|                                                                       |   ứng thời gian thực.                 |
+-----------------------------------------------------------------------+=======================================+
```

---

### SCR-LL-12: Utility Drawer — Thanh Lý Trả Phòng & Hoàn Cọc
* **Mục đích:** Chốt số cuối, prorate hóa đơn, hoàn cọc ngoài app, archive chat cũ sang read-only, mở lại phòng trống.
* **Wireframe:**
```
+-----------------------------------------------------------------------+=======================================+
|                                                                       | TIỆN ÍCH: THANH LÝ & TRẢ PHÒNG    [X] |
|                                                                       +---------------------------------------+
|                                                                       | BƯỚC 1: CHỐT SỐ ĐIỆN NƯỚC CUỐI CÙNG   |
|                                                                       | * Điện cuối: 1450 kWh (Tiêu thụ: 50kwh|
|                                                                       | * Nước cuối: 60 m3 (Tiêu thụ: 4m3)    |
|                                                                       +---------------------------------------+
|                                                                       | BƯỚC 2: HÓA ĐƠN QUYẾT TOÁN CUỐI KỲ    |
|                                                                       | * Tiền phòng (ở 15 ngày prorate): 1,75|
|                                                                       | * Tiền điện nước cuối kỳ:         215k|
|                                                                       | -> TỔNG CÔNG NỢ CUỐI CÙNG: 1,965,000 đ|
|                                                                       +---------------------------------------+
|                                                                       | BƯỚC 3: QUYẾT TOÁN TIỀN ĐẶT CỌC       |
|                                                                       | * Tiền cọc gốc ban đầu:    3,500,000 đ|
|                                                                       | * Cấn trừ nợ hóa đơn cuối: -1,965,000 |
|                                                                       | * Khấu trừ hư hỏng sơn tường: -200,000|
|                                                                       | ------------------------------------- |
|                                                                       | THỰC TẾ HOÀN LẠI CHO KHÁCH:1,335,000 đ|
|                                                                       +---------------------------------------+
|                                                                       | [X] Đã hoàn tiền mặt/chuyển khoản cọc |
|                                                                       |     và đã nhận bàn giao chìa khóa.    |
|                                                                       |                                       |
|                                                                       | [ ! XÁC NHẬN THANH LÝ & ĐÓNG PHÒNG ]  |
|                                                                       |                                       |
|                                                                       | (Sau khi bấm: Chat cũ chuyển Archive  |
|                                                                       |  Read-only; Phòng đổi thành Xanh lá   |
|                                                                       |  Available trên Room Map).            |
+-----------------------------------------------------------------------+=======================================+
```

---

### SCR-LL-13: Global Settings Page (`/settings`)
* **Mục đích:** Cấu hình đơn giá mặc định toàn cục của chủ trọ (D16) và tài khoản nhận tiền VietQR.
* **Wireframe:**
```
+---------------------------------------------------------------------------------------------------------------+
| RENTIFY CHỦ TRỌ  |  [DASHBOARD]  [BẤT ĐỘNG SẢN]  [TIN NHẮN]  [CÀI ĐẶT]*                                       |
+---------------------------------------------------------------------------------------------------------------+
| CÀI ĐẶT THÔNG TIN VẬN HÀNH TOÀN CỤC                                                                           |
|                                                                                                               |
| 1. HỒ SƠ CHỦ TRỌ                                                                                              |
| Họ và tên:         [ Thái Bảo                      ]   Số điện thoại:   [ 0905111222        ]                 |
| Email nhận tin:    [ baocules@gmail.com            ]                                                          |
|                                                                                                               |
| 2. ĐƠN GIÁ ĐIỆN NƯỚC MẶC ĐỊNH TOÀN CỤC (GLOBAL RATE DEFAULT - D16)                                            |
| * Đơn giá Điện mặc định (*):   [ 3,500   ] VNĐ / kWh                                                          |
| * Đơn giá Nước mặc định (*):   [ 10,000  ] VNĐ / m3                                                           |
| (Ghi chú: Đơn giá này được tự động áp dụng cho tất cả tòa nhà và phòng trọ trừ khi có cấu hình ghi đè riêng). |
|                                                                                                               |
| 3. TÀI KHOẢN NGÂN HÀNG THU TIỀN VIETQR ĐỘNG                                                                   |
| Ngân hàng thụ hưởng (*):       [ MB Bank (Ngân hàng Quân Đội) v]                                              |
| Số tài khoản thụ hưởng (*):    [ 0905111222                  ]                                                |
| Tên chủ tài khoản:             [ THAI BAO                    ]                                                |
|                                                                                                               |
|                                                                                 [  LƯU CÀI ĐẶT TOÀN CỤC  ]    |
+---------------------------------------------------------------------------------------------------------------+
```

