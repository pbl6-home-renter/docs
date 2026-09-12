# Product → Platform Map

> P2-01 output: Liệt kê feature từ user flow → xác định quyền (tenant/landlord/anonymous) + nền tảng (Web/Mobile).
> Owner: PM (draft) · FE + Mobile (verify)

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
| D3 | Cấu hình đơn giá điện nước | — | — | ✅ | ✅ | — | ✅ | ✅ | Preset EVN/tiered/flat/khoán; override tòa/phòng ẩn nâng cao |
| D4 | Thêm Phòng trọ | — | — | ✅ | ✅ | — | ✅ | ✅ | Chỉ BĐS đã duyệt mới thêm được phòng |
| D5 | Xem danh sách Phòng trọ (Room Map) | ✅ | — | ✅ | — | ✅ | ✅ | ✅ | Tenant & Anonymous đều xem được. Sơ đồ tòa nhà, trạng thái phòng |
| D6 | Chỉnh sửa thông tin phòng | — | — | ✅ | ✅ | — | ✅ | ✅ | Sửa diện tích, giá, tiện nghi, ràng buộc |

### E. Hợp đồng & Check-in/out

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| E1 | Tạo Hợp đồng thuê (kèm kê khai số xe) | — | — | ✅ | ✅ | — | ✅ | ✅ | Nhập thông tin tenant, tiền cọc, thời hạn, vehicle_count |
| E2 | Chọn & Xuất mẫu HĐ (PDF) | — | — | ✅ | ✅ | — | ✅ | ✅ | Chọn mẫu có sẵn → xuất PDF điền sẵn |
| E3 | Tải lên file HĐ đã ký (wet-sign) | — | — | ✅ | ✅ | — | ✅ | ✅ | Upload ảnh/PDF hợp đồng giấy ký tay 2 bên |
| E4 | Check-out & Thanh lý phòng | — | — | ✅ | ✅ | — | ✅ | ✅ | Chốt số cuối, quyết toán cọc, lưu trữ chat |
| E5 | Xem hợp đồng (read-only) | ✅ | — | ✅ | — | — | ✅ | ✅ | Tiền thuê, cọc, thời hạn, file đã ký |

### F. Quản lý Thành viên

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| F1 | Thêm thành viên ở ghép | — | — | ✅ | ✅ | — | ✅ | ✅ | Nhập Họ tên, SĐT, CCCD → tự add vào Chat |
| F2 | Xóa thành viên rời đi | — | — | ✅ | ✅ | — | ✅ | ✅ | Xóa khỏi phòng + rút khỏi Chat (cần xác nhận) |
| F3 | Xem danh sách thành viên | ✅ | — | ✅ | — | — | ✅ | ✅ | Read-only: tên các thành viên trong phòng |

### G. Chốt số Điện/Nước (Mobile only — landlord thao tác trực tiếp tại phòng)

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| G1 | Chụp ảnh công tơ (Camera trong app) | — | — | ✅ | ✅ | — | — | ✅ | Chỉ landlord chụp trực tiếp tại phòng |
| G2 | Tải ảnh công tơ từ máy | — | — | ✅ | ✅ | — | — | ✅ | Chỉ landlord mới có quyền này |
| G3 | Hiệu chỉnh tay số đọc | — | — | ✅ | ✅ | — | — | ✅ | Sửa tay khi OCR sai + giữ ảnh evidence |

### H. Hóa đơn & Thanh toán (Mobile only — liên quan tiền bạc)

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| H1 | Lập Hóa đơn tháng (kèm phí 1 lần) | — | — | ✅ | ✅ | — | — | ✅ | Tiền phòng + dịch vụ + other_fees, phát hành |
| H2 | Tạo mã VietQR động | — | — | ✅ | ✅ | — | — | ✅ | Mã QR gắn mã định danh phòng |
| H3 | Xem chi tiết hóa đơn | ✅ | — | ✅ | — | — | — | ✅ | Tiền phòng + breakdown dịch vụ, trạng thái |
| H4 | Thanh toán qua VietQR | ✅ | ✅ | — | — | — | — | ✅ | Quét mã QR → chuyển khoản qua app ngân hàng |
| H5 | Xác nhận thu tiền mặt | — | — | ✅ | ✅ | — | — | ✅ | Landlord xác nhận khi tenant nộp tiền mặt |
| H6 | Theo dõi trạng thái thanh toán | ✅ | — | ✅ | — | — | — | ✅ | Đã thanh toán / Đã thu một phần / Quá hạn |

### I. Cài đặt Đơn giá & Phí định kỳ

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| I1 | Cấu hình đơn giá (UtilityRatePolicy) | — | — | ✅ | ✅ | — | ✅ | ✅ | Preset EVN/tiered/flat/khoán; override tòa/phòng |
| I2 | Cấu hình phí định kỳ (RecurringFee) | — | — | ✅ | ✅ | — | ✅ | ✅ | Preset Wifi/QLVH/Gửi xe/Vệ sinh + phí tự nhập |
| I3 | Cài đặt chu kỳ quét nợ tự động | — | — | ✅ | ✅ | — | ✅ | ✅ | Hạn thanh toán, ngày nhắc, bật/tắt bot. 3 cấp |

### J. Property Chat (Mobile only)

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| J1 | Chat riêng phòng | ✅ | ✅ | ✅ | ✅ | — | — | ✅ | Text, ảnh, file + bot card. Tự tạo khi HĐ active |
| J2 | Chat chung tòa | ✅ | ✅ | ✅ | ✅ | — | — | ✅ | Text, ảnh, file + @mention. KHÔNG có bot card |
| J3 | @mention thành viên/landlord | ✅ | ✅ | ✅ | ✅ | — | — | ✅ | Autocomplete gắn tên trong chat |
| J4 | Bot auto-remind nhắc nợ | ✅ | — | ✅ | — | — | — | ✅ | Bot post card nhắc vào chat khi hóa đơn quá hạn |
| J5 | Bot thông báo sự cố | ✅ | — | ✅ | — | — | — | ✅ | Bot post card + FCM push khi có sự cố mới |

### K. Sự cố (Mobile only)

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| K1 | Tạo báo cáo sự cố | ✅ | ✅ | ✅ | ✅ | — | — | ✅ | Mô tả + đính kèm ảnh. Cả 2 bên tạo được |
| K2 | Quản lý Sự cố (Tab riêng) | — | — | ✅ | ✅ | — | — | ✅ | Xem danh sách, lọc trạng thái, điều phối |
| K3 | Cập nhật trạng thái sự cố | — | — | ✅ | ✅ | — | — | ✅ | Đang xử lý / Đã hoàn thành / Hủy |
| K4 | Theo dõi sự cố | ✅ | — | ✅ | — | — | — | ✅ | Tenant xem tất cả sự cố phòng mình |

### L. Ghép bạn / Roommate Matching

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| L1 | Feed ghép bạn | ✅ | — | — | — | — | — | ✅ | Cần login để xem feed (guest chỉ find-room) |
| L2 | Tạo/sửa hồ sơ ghép bạn | ✅ | ✅ | — | — | — | — | ✅ | 1 tài khoản = 1 hồ sơ |
| L3 | Gửi/nhận match request | ✅ | ✅ | — | — | — | — | ✅ | 2 chiều: gửi → chờ → chấp nhận/từ chối |
| L4 | Match thành công → lộ liên hệ | ✅ | — | — | — | — | — | ✅ | Hiện SĐT + Zalo cả 2 bên |

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
| N1 | Webhook ngân hàng đối soát | — | — | ✅ | — | — | ✅ | — | Backend service: nhận kết quả CK, tự gạch nợ |
| N2 | Tích hợp VNPay/MoMo (Stretch) | ✅ | ✅ | — | — | — | — | ✅ | Nice-to-have, Phase 1+ |

### O. AI Features

| # | Feature | Tenant View | Tenant Edit | Landlord View | Landlord Edit | Anonymous | Web | Mobile | Ghi chú |
|---|---------|:-----------:|:-----------:|:-------------:|:-------------:|:---------:|:---:|:------:|---------|
| O1 | AI Auto-Description (MVP) | — | — | ✅ | ✅ | — | ✅ | ✅ | Landlord nhập keywords → LLM sinh bài PR phòng |
| O2 | AI Matchmaking (Stretch) | ✅ | — | — | — | — | — | ✅ | Matching Score % + lời khuyên. Cần login |

---

## 3. Tổng hợp theo nền tảng

### Web — Feature xuất hiện

| Nhóm | Features |
|------|----------|
| Auth | A1–A3 |
| Hồ sơ | B1–B3 |
| Tìm phòng | C1–C4 |
| BĐS & Phòng | D1–D6 |
| Hợp đồng | E1–E5 |
| Thành viên | F1–F3 |
| Cài đặt | I1–I3 |
| Quản trị | M1–M8 |
| Thanh toán | N1 |
| AI | O1 |
| **Total** | **~37 features** |

### Mobile — Feature xuất hiện

| Nhóm | Features |
|------|----------|
| Auth | A1–A3 |
| Hồ sơ | B1–B3 |
| Tìm phòng | C1–C4 |
| BĐS & Phòng | D1–D6 |
| Hợp đồng | E1–E5 |
| Thành viên | F1–F3 |
| Chốt số | G1–G3 |
| Hóa đơn | H1–H6 |
| Cài đặt | I1–I3 |
| Chat | J1–J5 |
| Sự cố | K1–K4 |
| Ghép bạn | L1–L4 |
| Thanh toán | N2 |
| AI | O2 |
| **Total** | **~51 features** |

---

## 4. Quy định đặc biệt (sau khi verify với team)

| # | Quy định |
|---|----------|
| 1 | Guest trên mobile KHÔNG xem feed ghép bạn — chỉ tìm phòng. Feed ghép bạn cần login. |
| 2 | Chat chung tòa CHỈ có text/ảnh/file + @mention, KHÔNG có bot card. Bot chỉ ở chat riêng phòng. |
| 3 | Admin có Dashboard tổng quan (số BĐS chờ duyệt, user hoạt động, thống kê cơ bản). |
| 4 | Landlord-lite xem hóa đơn với ĐẦY ĐỦ breakdown (tiền phòng, điện, nước, phí), không chỉ xem tổng. |
| 5 | Bộ lọc tìm phòng hiện tại chỉ có filter → danh sách, CHƯA có bản đồ. Landlord cũng xem được danh sách phòng. |
| 6 | Kê khai số xe tích hợp vào tạo/sửa hợp đồng, không tách riêng. |
| 7 | Chốt số điện/nước, hóa đơn, chat, sự cố = Mobile only. Web chỉ dùng cho quản trị BĐS/hợp đồng/thành viên/admin. |
| 8 | Chat history vẫn bình thường sau check-out, không có chế độ read-only/archive. |

---

## 5. Verification

- [ ] FE đọc bảng map → xác nhận / đề xuất sửa
- [ ] Mobile đọc bảng map → xác nhận / đề xuất sửa
- [ ] PM tổng hợp → chốt final
- [ ] Không có open question chưa resolve
