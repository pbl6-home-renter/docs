# Landlord User Research

## 1. Research Objective

Mục tiêu nghiên cứu nhằm xác định quy trình vận hành thực tế, thói quen sử dụng công cụ, và các điểm nghẽn (pain points) cốt lõi của chủ nhà trọ/căn hộ cho thuê tại Việt Nam; từ đó thiết lập cơ sở dữ liệu định tính và định lượng phục vụ phát triển giải pháp phần mềm quản lý vận hành tự động.

---

## 2. Research Sources

### Secondary Research

* **News articles:** Tổng hợp các bài viết thực tế từ VnExpress, Dân Trí, Lao Động, Thanh Niên, Tuổi Trẻ, Tiền Phong, VietNamNet, Tạp chí Tài chính phản ánh rủi ro bùng nợ, áp lực kiểm tra PCCC, tranh cãi điện nước và chi phí bảo trì.
* **Market reports:** Báo cáo thị trường bất động sản cho thuê phân khúc căn hộ mini, nhà trọ đô thị tại Hà Nội và TP.HCM.
* **Existing products:** Đánh giá các giải pháp hiện hành (như Mona House, iTro, App KiotViet BĐS) nhằm xác định khoảng cách giữa tính năng sản phẩm và hành vi thực tế của người dùng.
* **Public discussions:** Thảo luận trên các hội nhóm chủ nhà trọ tại Facebook, diễn đàn Zalo cộng đồng BĐS cho thuê.

### Primary Research

* Dữ liệu mô phỏng sâu từ 2 persona chủ cho thuê điển hình:
* **Persona A (Chủ trọ truyền thống - Anh Hùng, 48 tuổi):** Quản lý dãy trọ 25 phòng tại TP.HCM, tự vận hành, dùng sổ tay và Zalo.
* **Persona B (Chủ căn hộ dịch vụ/Chung cư mini - Chị Mai, 35 tuổi):** Quản lý 3 tòa nhà (tổng 45 căn hộ) tại Hà Nội, dùng Google Sheets, có thuê nhân công dọn dẹp theo giờ.



---

## 3. Current Landlord Workflow

### Daily

* Giám sát an ninh qua camera, kiểm tra khu vực để xe và cửa ra vào.
* Tiếp nhận tin nhắn, cuộc gọi phản ánh sự cố phát sinh (mất nước, hỏng điều hòa, nghẹt bồn cầu, phòng bên cạnh làm ồn).
* Dẫn khách xem phòng, trả lời tin nhắn trên hội nhóm mạng xã hội khi có phòng trống.

### Weekly

* Rà soát vệ sinh khu vực sinh hoạt chung, hành lang, sân phơi và thu gom rác.
* Kiểm tra vật tư tiêu hao, mua linh kiện cơ bản (bóng đèn, aptomat, vòi xịt).
* Đăng bài marketing lại các phòng sắp trống trên Facebook/Chợ Tốt.

### Monthly

* **Ngày 25 - 28:** Đi từng tầng chụp ảnh chỉ số công tơ điện và đồng hồ nước.
* **Ngày 28 - 30:** Nhập số liệu vào bảng tính/sổ, tính toán tiền phòng + dịch vụ + điện nước phát sinh.
* **Ngày 01 - 05:** Xuất hóa đơn/phiếu thu, gửi ảnh hoặc bảng kê qua Zalo cho từng phòng.
* **Ngày 05 - 10:** Đối soát lịch sử tài khoản ngân hàng, khớp lệnh người trả, lập danh sách người trễ nợ để nhắn tin/gọi điện đòi tiền.
* Khai báo biến động cư trú cho cơ quan chức năng (đăng ký tạm trú/tạm vắng).

### Move-in

* Ký hợp đồng giấy (2 bản) và thu tiền cọc + tiền phòng tháng đầu.
* Chụp ảnh CCCD/VNeID để lưu trữ thông tin nhân khẩu.
* Bàn giao phòng sơ bộ: Giao chìa khóa/thẻ từ, kiểm tra nhanh bóng đèn, máy lạnh và ghi lại chỉ số điện nước ban đầu.

### Move-out

* Kiểm tra hiện trạng phòng và thiết bị nội thất so với lúc mới vào.
* Chốt chỉ số điện nước cuối cùng và tính toán tiền trừ phát sinh.
* Khấu trừ hư hao (nếu có), hoàn trả tiền cọc còn lại và thu hồi chìa khóa/thẻ từ.

---

## 4. Current Tools & Workarounds

### Zalo

* **Cách dùng:** Tạo nhóm riêng với từng phòng để gửi ảnh hóa đơn; đổi tên gợi nhớ (VD: `P201 - Nam - 0987xxx`) để tra cứu nhanh.
* **Hạn chế:** Trôi tin nhắn, mất ảnh công tơ điện nước sau 30 ngày do cơ chế dọn cache của Zalo, không có tính năng nhắc nợ tự động.

### Excel / Google Sheets

* **Cách dùng:** Thiết lập bảng tính chứa công thức nhân đơn giá điện nước và quản lý trạng thái đóng tiền.
* **Hạn chế:** Nhập liệu thủ công dễ sai sót công thức, thao tác trên điện thoại bất tiện khi đang đi kiểm tra thực địa.

### Banking apps

* **Cách dùng:** Dán mã QR cá nhân trước phòng trọ hoặc gửi qua chat để khách quét chuyển khoản.
* **Hạn chế:** Khách chuyển sai cú pháp hoặc người khác chuyển hộ, buộc chủ nhà phải kéo sao kê từng dòng để đối soát thủ công.

### Paper documents

* **Cách dùng:** Ký hợp đồng bản cứng, lưu cuống hóa đơn giấy và ghi chép chi phí phát sinh vào sổ tay.
* **Hạn chế:** Dễ thất lạc, rách nát, không tra cứu lịch sử nhanh được khi có tranh chấp sau nhiều năm.

### Camera systems

* **Cách dùng:** Cài đặt ứng dụng xem camera giám sát (Ezviz, Imou, Yoosee) để theo dõi an ninh nhà xe và cửa chính.
* **Hạn chế:** Chỉ phục vụ xem thụ động, không liên kết được với dữ liệu cư dân hay kiểm soát ra vào tự động.

---

## 5. Problem Map

```
               ┌───────────────────────────────┐
               │    VẬN HÀNH QUẢN LÝ CHO THUÊ   │
               └───────────────┬───────────────┘
         ┌─────────────────────┼─────────────────────┐
         ▼                     ▼                     ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│     TÀI CHÍNH   │   │     HÀNG NGÀY   │   │  PHÁP LÝ & CSVC │
├─────────────────┤   ├─────────────────┤   ├─────────────────┤
│• Chốt điện nước │   │• Nhắc nợ trễ hạn│   │• Quản lý tạm trú│
│• Sai lệch bill  │   │• Sự cố đêm khuya│   │• Hỏng hóc đồ đạc│
│• Lệch sao kê    │   │• Tiếng ồn nội bộ│   │• Tranh chấp cọc │
└─────────────────┘   └─────────────────┘   └─────────────────┘

```

---

## 6. Pain Point Clusters

### Billing & Payment

* Chốt chỉ số điện nước thủ công tốn nhiều giờ, dễ nhầm lẫn số đo.
* Khách thanh toán trễ, sai cú pháp khiến việc tra soát sao kê ngân hàng kéo dài.
* Tâm lý e ngại khi phải nhắn tin đòi tiền trực tiếp từng khách thuê.

### Tenant & Contract Lifecycle

* Khách thuê dọn đi bất ngờ mà không báo trước đủ thời gian cam kết.
* Bỏ quên thời điểm hết hạn hợp đồng, không kịp điều chỉnh giá hoặc tìm khách mới.
* Mất liên lạc, rủi ro khách bỏ trốn khi tiền nợ vượt quá số tiền cọc.

### Property & Asset

* Khách sử dụng thiết bị cẩu thả gây hư hại nhưng từ chối bồi thường vì thiếu ảnh hiện trạng lúc nhận phòng.
* Khó quản lý tình trạng hao mòn tự nhiên so với hư hại do người dùng gây ra.

### Incident & Maintenance

* Nhận cuộc gọi xử lý sự cố đột xuất vào khung giờ nghỉ ngơi (ban đêm/sáng sớm).
* Không có danh bạ thợ sửa chữa uy tín, chi phí sửa chữa lặt vặt tốn kém.

### Occupancy & Compliance

* Số lượng người ở thực tế vượt quá hợp đồng (dắt thêm người về ở chui).
* Rắc rối khi đăng ký tạm trú trực tuyến và rủi ro bị xử phạt hành chính về PCCC/cư trú.

---

## 7. Preliminary Pain Points

Hệ thống chấm điểm sử dụng thang điểm từ 1 đến 5 cho 3 tiêu chí cốt lõi:Tần suất (Frequency - F): Độ lặp lại của vấn đề trong chu kỳ vận hành (1: Hiếm khi $\rightarrow$ 5: Hằng tháng/Hằng ngày).Thiệt hại tài chính & Rủi ro (Impact - I): Mức độ ảnh hưởng trực tiếp đến dòng tiền, mất vốn hoặc rủi ro pháp lý (1: Nhẹ $\rightarrow$ 5: Mất trắng dòng tiền/Bị phạt nặng).Ức chế vận hành (Operational Friction - OF): Mức độ tốn thời gian, hao tổn tâm lý, ngại va chạm của chủ nhà (1: Dễ xử lý $\rightarrow$ 5: Căng thẳng, tốn nhiều giờ thao tác thủ công).Tổng điểm (Total Score): $\text{Total} = F + I + OF$ (Tối đa 15 điểm).

| Thứ hạng | Vấn đề (Problem) | F | I | OF | Tổng điểm | Bằng chứng (Evidence) | Tác động cốt lõi (Core Impact) | Nguyên nhân gốc rễ (Root Cause) | Độ tin cậy (Confidence) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **#1** | **Tắc nghẽn đối soát ngân hàng & Thu hồi nợ** | 5 | 4 | 5 | **14/15** | Đối soát thủ công từng dòng sao kê từ ngày 1-5 hằng tháng; ngại nhắn tin đòi nợ trực tiếp | Tốn 2–4h/kỳ tính tiền, dễ bỏ sót nợ cũ, dòng tiền về chậm | Khách chuyển khoản sai cú pháp; không có hệ thống tự động gạch nợ và tự động gửi nhắc nhở | High |
| **#2** | **Chốt chỉ số điện nước thủ công & Tranh chấp hóa đơn** | 5 | 3 | 5 | **13/15** | Báo chí phản ánh nhiều vụ tranh cãi số điện tăng vọt; chủ trọ phải leo từng tầng chụp ảnh | Tốn thời gian đo đạc, khách nghi ngờ thiếu minh bạch, giữ tiền không chịu đóng bill | Đọc số cơ thủ công, chép tay qua nhiều khâu trung gian (sổ $\rightarrow$ Excel $\rightarrow$ Zalo) | High |
| **#3** | **Khách bùng nợ dọn đi trong đêm (vượt tiền cọc)** | 2 | 5 | 4 | **11/15** | Nhiều bài báo ghi nhận khách nợ 2-3 tháng rồi biến mất, khóa phòng để lại đồ cũ | Thất thoát 100% doanh thu kỳ nợ + gánh thêm tiền điện nước phát sinh | Không có ngưỡng chặn cảnh báo khi nợ chạm mốc tiền cọc; kiểm soát ra vào lỏng lẻo | High |
| **#4** | **Tranh chấp khấu trừ cọc & Bàn giao tài sản** | 3 | 3 | 4 | **10/15** | Mâu thuẫn khi trả phòng; tranh cãi về đồ đạc hư hỏng cũ/mới, tiền dọn vệ sinh | Chủ nhà chịu thiệt chi phí sửa chữa hoặc bị khách bóc phốt, khiếu nại gay gắt | Biên bản bàn giao sơ sài, thiếu kho lưu trữ hình ảnh hiện trạng có mốc thời gian (timestamp) | High |
| **#5** | **Chậm trễ đăng ký tạm trú & Rủi ro kiểm tra pháp lý** | 2 | 4 | 3 | **9/15** | Các đợt kiểm tra liên ngành xử phạt hành chính về PCCC và đăng ký cư trú | Bị phạt hành chính từ vài triệu đến hàng chục triệu đồng, đình chỉ hoạt động | Khách thuê thay đổi liên tục nhưng ngại nộp CCCD; cổng dịch vụ công thao tác phức tạp | Medium |

---

## 8. Problem Chains

### Utility $\rightarrow$ Billing $\rightarrow$ Dispute

* **Cơ chế:** Ghi chép chỉ số thủ công $\rightarrow$ Nhập sai số vào file tính tiền $\rightarrow$ Hóa đơn tăng bất thường $\rightarrow$ Khách khiếu nại, giữ tiền không đóng $\rightarrow$ Tranh cãi kéo dài làm chậm dòng tiền.

### Payment $\rightarrow$ Reconciliation $\rightarrow$ Debt

* **Cơ chế:** Khách chuyển khoản không ghi phòng $\rightarrow$ Chủ nhà không gạch nợ trên sổ $\rightarrow$ Chủ nhà đòi nhầm hoặc bỏ quên người chưa trả $\rightarrow$ Tích tụ công nợ lớn khó thu hồi.

### Contract $\rightarrow$ Reminder $\rightarrow$ Missed deadline

* **Cơ chế:** Lưu hợp đồng giấy trong ngăn kéo $\rightarrow$ Không có lịch thông báo tự động $\rightarrow$ Quên thông báo gia hạn trước 30 ngày $\rightarrow$ Khách trả phòng đột ngột khiến phòng bị trống dài ngày.

### Handover $\rightarrow$ Evidence $\rightarrow$ Deposit dispute

* **Cơ chế:** Bàn giao bằng miệng/ký giấy qua loa $\rightarrow$ Khách làm hỏng thiết bị khi dọn đi $\rightarrow$ Không có ảnh đối chiếu ngày nhận $\rightarrow$ Khách không chịu trừ cọc, xảy ra xích mích.

---

## 9. Preliminary Insights

* **Tâm lý phòng thủ với phần mềm mới:** Chủ nhà trọ thường ngại các phần mềm quá nhiều tính năng kế toán phức tạp; họ cần sự tiện lợi tương đương bảng tính nhưng có tính năng tự động nhắc nợ và xuất bill sang Zalo.
* **Cổ chai nằm ở khâu giao tiếp tiền nong:** Nỗi đau lớn nhất không phải là tính toán, mà là việc **đối soát giao dịch** và **nhắc nợ**. Chủ trọ cần một công cụ trung gian đóng vai trò thông báo khách quan để tránh làm sứt mẻ mối quan hệ với người thuê.
* **Hình ảnh là tài sản xác thực cốt lõi:** Mọi tranh chấp (điện nước, hỏng hóc đồ đạc) đều xuất phát từ việc thiếu bằng chứng hình ảnh có dấu mốc thời gian rõ ràng.

---

## 10. Research Gaps & Hypotheses

### Research Gaps

* Mức độ sẵn sàng trả phí (Willingness to Pay) chính xác của từng nhóm quy mô phòng (dưới 10 phòng, 10-30 phòng, trên 50 phòng).
* Tỷ lệ chủ trọ sẵn sàng chuyển đổi sang các giải pháp phần cứng kết nối mạng (công tơ điện thông minh, khóa cửa vân tay quản lý từ xa).

### Hypotheses

* **H1:** Nếu tự động hóa quy trình đọc số điện nước qua hình ảnh (OCR) và xuất hóa đơn gửi thẳng qua Zalo, chủ trọ sẽ tiết kiệm được ít nhất 70% thời gian vận hành cuối tháng.
* **H2:** Chủ nhà trọ sẵn sàng trả phí dịch vụ từ 5.000 - 10.000 VNĐ/phòng/tháng nếu hệ thống giải quyết triệt để bài toán đối soát tài khoản và nhắc nợ tự động.