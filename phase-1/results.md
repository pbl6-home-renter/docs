## 1. Log note các buổi họp

### 1.1 Ngày 7 tháng 9

* **Phương thức xác thực tài khoản và gửi mã xác thực:**
  * Đối với trường hợp người dùng đăng ký bằng số điện thoại và không cung cấp email: nhóm cân nhắc phương án tạm thời miễn gửi mã OTP hoặc hỏi ý kiến giảng viên hướng dẫn về giải pháp cung cấp cổng SMS.
  * Đối với trường hợp người dùng đăng ký có đầy đủ số điện thoại và email: sử dụng mã OTP gửi qua email nhằm tối ưu hóa chi phí vận hành. Khi hệ thống tích hợp thành công cổng tin nhắn SMS trong tương lai sẽ bỏ bước đăng nhập bằng email.
  * Về quy trình cập nhật trong hợp đồng: chủ trọ giữ quyền cập nhật danh sách thành viên thực tế và khách thuê có tính năng gửi nhắc nhở khi có phát sinh thêm hay bớt người ở cùng.
  * Trường hợp khách thuê không cài đặt ứng dụng: chủ trọ vẫn tự tạo hợp đồng và quản lý độc lập, khi đó kênh trò chuyện ban đầu chỉ có một mình chủ trọ. -> sau sẽ thêm khách sau
  * Trường hợp khách thuê tạo tài khoản sau ngày ký hợp đồng: hệ thống sẽ tự động đối soát dựa trên số điện thoại hoặc userID để liên kết khách thuê với hợp đồng phòng đang hiệu lực

* **Định hướng đăng nhập qua Google OAuth:**
  * Đang có định hướng lược bỏ email trong tương lai và đang đánh giá là có ảnh hưởng gì ko.
  * Quy trình đăng nhập lần đầu qua Google OAuth sẽ yêu cầu bổ sung số điện thoại và lựa chọn vai trò định danh. Chỉ note lại sau dư thời gian thì làm.

* **Cơ chế Admin khóa tài khoản người dùng:**
  * Cần khảo sát thực tế các nền tảng quản lý hiện hành để xác định phạm vi ảnh hưởng khi khóa tài khoản, đặc biệt là quyền lợi và tiến trình sinh hoạt của khách thuê khi tài khoản chủ trọ hoặc bạn cùng phòng bị tạm ngưng. -> Hỏi thầy thử

* **Tái cấu trúc chat và menu tiện ích:**
  * Dưới góc nhìn của chủ trọ: loại bỏ menu tiện ích ra khỏi khung trò chuyện, chuyển toàn bộ công cụ quản lý vào chi tiết phòng trọ. Bổ sung nút điều hướng nhanh sang khung trò chuyện phòng. Tách phân hệ quản lý sự cố thành một tab riêng biệt trên thanh điều hướng chính. Khi thêm thành viên vào hợp đồng thì hệ thống tự động đưa thành viên đó vào kênh trò chuyện chung của phòng. Chuyển các thiết lập đơn giá điện nước, phí sinh hoạt và chu kỳ nhắc nợ vào tiện ích từng phòng.
  * Dưới góc nhìn của khách thuê: Bỏ cú pháp dòng lệnh @issue khi báo sự cố. Quy hoạch mục quản lý hợp đồng, tra cứu hóa đơn và gửi sự cố vào tiện ích phòng. Kênh trò chuyện vận hành độc lập. -> chuyển qua tag tên luôn

* **Cơ chế chia sẻ hóa đơn:**
  * Tính năng chia sẻ hóa đơn chưa bao quát được bài toán nợ cộng dồn của từng cá nhân khi có người chậm nộp. Nhóm cân nhắc bỏ và xin ý kiến từ giảng viên hướng dẫn.

* **Tọa độ địa lý của bất động sản:**
  * Đánh giá việc bỏ thao tác lưu tọa độ thủ công do dịch vụ bản đồ đã hỗ trợ định vị chính xác dựa theo địa chỉ hành chính.

* **Quản lý biểu giá điện bậc thang và chi phí sinh hoạt:**
  * Admin cập nhật biểu giá điện bậc thang của nhà nước lên hệ thống, chủ trọ sẽ lựa chọn áp dụng khi thiết lập phòng.
  * Tiếp tục khảo sát thực tế về việc điều chỉnh đơn giá chi phí sinh hoạt chung và riêng giữa các phòng.

* **Xác thực tính chính danh của cơ sở lưu trú:**
  * Việc thiếu hồ sơ pháp lý chứng minh quyền sở hữu dễ dẫn đến tranh chấp thông tin phòng và tòa nhà. Nhóm thống nhất cần xây dựng cơ chế xác minh tính xác thực và đưa vào nội dung hỏi giảng viên hướng dẫn.

---

### 1.2 Ngày 8 tháng 9

* **Quy trình tiếp nhận căn cước công dân và cập nhật thành viên:**
  * Đề xuất chuyển luồng quét căn cước công dân qua phân hệ quản lý thành viên để tránh trùng lặp thao tác vừa sửa hợp đồng vừa sửa cư dân khi có biến động người ở.
  * Thảo luận về phạm vi thông tin pháp lý: hợp đồng chỉ cần thông tin của người đại diện ký kết hay bắt buộc phải lưu trữ đầy đủ toàn bộ người ở ghép.
  * Thống nhất quy trình: sau khi tạo lập hợp đồng thành công thì hệ thống sẽ mở khóa chức năng quản lý cư dân, các thành viên phát sinh sau sẽ được thêm vào danh sách quản lý phòng.
  * Trường hợp người đứng tên đại diện rời đi: tiến hành thanh lý hợp đồng cũ và lập hợp đồng mới cho người kế thừa.
  * Căn cứ xác định hợp đồng hợp lệ của tài khoản dựa trên trạng thái hợp đồng đang kích hoạt.
  * Bảo đảm tính riêng tư: khi thành viên rời phòng sẽ không được tiếp tục truy cập hồ sơ của phòng đó.

* **Phương thức số hóa hợp đồng thuê trọ:**
  * Thống nhất phương án sử dụng hợp đồng giấy ký sống truyền thống thay vì giải pháp chữ ký số điện tử. Hệ thống cung cấp mẫu văn bản để hai bên in ra ký tay, sau đó chủ trọ chụp ảnh hoặc tải tệp scan lên hệ thống để kích hoạt phòng.

* **Thiết lập thông tin phòng trọ và quy tắc ở ghép:**
  * Chủ trọ mong muốn cấu hình nhanh các quy định chung của phòng một lần duy nhất, tránh nhập liệu lặp lại.
  * Bỏ quy định cứng về số lượng người ở tối đa. Nếu chủ trọ không chủ động giới hạn thì phòng có thể tiếp nhận số lượng người ở ghép tùy theo thỏa thuận thực tế.
  * Mọi thành viên trong phòng đều có quyền thực hiện nghĩa vụ thanh toán hóa đơn, không giới hạn riêng người đại diện hợp đồng.

* **Vận hành hóa đơn và chỉ số tiêu thụ:**
  * Lưu trữ trạng thái bản nháp của hóa đơn trong cơ sở dữ liệu. Không cho phép chỉnh sửa hóa đơn sau khi đã phát hành chính thức, trường hợp sai sót bắt buộc phải tạo bản thay thế.
  * Tham khảo ý kiến giảng viên hướng dẫn về tính khả thi của việc cho phép khách thuê hỗ trợ gửi ảnh công tơ điện nước lên hệ thống.
  * Ghi nhận đầy đủ lịch sử thanh toán gồm hình thức chuyển khoản và tiền mặt, theo dõi công nợ chi tiết và gửi thông báo nhắc nợ định kỳ.

---

### 1.3 Ngày 9 tháng 9

* **Tối giản hóa luồng nghiệp vụ hợp đồng và phòng trọ:**
  * Lược bỏ bước cấu hình thanh toán linh hoạt ra khỏi quy trình tạo hợp đồng để đơn giản hóa giao diện.
  * Lược bỏ việc tự động tính lại tỷ lệ tiền chia sẻ trong phòng, xem trách nhiệm thanh toán là của tập thể phòng và ai cũng có thể nộp tiền.
  * Gộp nghiệp vụ ghi nhận chỉ số điện nước thành một nhánh hỗ trợ trong quy trình lập hóa đơn.
  * Đặt ra bài toán thực tế: tiền thuê phòng thu theo chu kỳ nhiều tháng nhưng tiền điện nước phát sinh theo từng tháng thì cần cơ chế quản lý như thế nào.

* **Tối ưu hóa giao diện và trải nghiệm:**
  * Đánh giá lại mức độ cần thiết của màn hình bản đồ tìm kiếm nhằm tập trung nguồn lực vào danh sách hiển thị chi tiết.
  * Màn hình chi tiết phòng bổ sung nút liên hệ trực tiếp với chủ trọ và nút lưu tin quan tâm.
  * Bỏ giao diện hóa đơn chia sẻ phức tạp, không hiển thị căn cước công dân của các thành viên khác nhằm bảo vệ dữ liệu cá nhân.

* **Short-term vs long-term:**
  * Nhận diện các bài toán thực tế gồm tích hợp cổng thanh toán bên ngoài, quy trình bàn giao dọn dẹp vệ sinh phòng, tần suất tương tác quản lý định kỳ của chủ trọ, sự biến động của giá thị trường và sự khác biệt về hạ tầng của từng khu nhà trọ.

  * 1. Hệ thống bên ngoài
  * 2. Dọn phòng, phân bổ người
  * 3. Tuần suất quản lý dày đặc
  * 4. giá không đồng bộ (ổn định)
  * 5. Hạ tang khác biệt

---

## 2. Những Vấn Đề Đã Giải Quyết Được Trong Tuần

Nhóm đã đối soát toàn bộ các thảo luận và hoàn thiện đồng bộ vào tài liệu quy trình nghiệp vụ và thiết kế wireframe:

1. **Chuẩn hóa mô hình quản trị hệ thống:**
   * Thống nhất toàn hệ thống chỉ vận hành duy nhất một tài khoản Admin, bỏ hoàn toàn phân cấp Super Admin và Admin bình thường, xóa bỏ màn hình quản lý đội ngũ Admin.

2. **Áp dụng nguyên tắc vai trò bất biến:**
   * Quy định vai trò người dùng là enum vĩnh viễn, tuyệt đối không cho phép chuyển đổi vai trò qua lại nhằm bảo vệ tính toàn vẹn của dữ liệu bất động sản và lịch sử giao dịch.

3. **Trải nghiệm quản trị của Chủ trọ:**
   * Chuyển toàn bộ menu tiện ích từ khung trò chuyện sang màn hình Quản lý phòng trọ.
   * Tích hợp tính năng điều hướng nhanh sang kênh trò chuyện từ tiện ích phòng.
   * Tách phân hệ Quản lý sự cố thành một tab riêng biệt độc lập trên thanh điều hướng chính của chủ trọ.

4. **Linh hoạt quyền hạn thanh toán hóa đơn:**
   * Cập nhật quy tắc cho phép bất kỳ thành viên nào trong phòng trọ đều có quyền quét mã QR động hoặc nộp tiền mặt cho chủ trọ để hoàn tất hóa đơn của phòng.

5. **Loại bỏ giới hạn cứng về số lượng người ở ghép:**
   * Bỏ ràng buộc kiểm tra số lượng người ở tối đa trong trường hợp chủ trọ không cài đặt giới hạn số người thì phòng trọ được phép tiếp nhận thành viên ở ghép không giới hạn tùy thuộc vào thương lượng giữa chủ trọ và mấy đứa thuê.

6. **Bỏ cú pháp dòng lệnh báo sự cố:**
   * Loại bỏ hoàn toàn việc gõ lệnh trong khung chat, thay thế bằng hình thức trao đổi tự nhiên kèm tag tên thành viên hoặc tag phòng và gửi ảnh hiện trường.

7. **Chuyển quyền quản lý lịch quét nợ về phía Chủ trọ:**
   * Xóa bỏ cấu hình tự động quét nợ bên phía Admin hệ thống. Từng chủ trọ toàn quyền cài đặt ngày chốt công tơ, thời hạn nộp tiền và kích hoạt lịch trình bot tự động nhắc nợ vào phòng chat.

---

## 3. Những Vấn Đề Cần Xin Ý Kiến Giảng Viên Hướng Dẫn

Nhóm đã tổng hợp danh sách các câu hỏi trọng tâm để trao đổi trực tiếp với giảng viên hướng dẫn trong buổi duyệt tiến độ:

1. **Phương án xác thực tài khoản qua số điện thoại:**
   * Đồ án có bắt buộc phải tích hợp cổng tin nhắn SMS thực tế để gửi mã xác thực hay được phép sử dụng giải pháp gửi mã qua email hoặc cơ chế giả lập xác thực để tiết kiệm chi phí vận hành.

2. **Tính khả thi của tính năng chia sẻ hóa đơn:**
   * Đối với bài toán chia nhỏ hóa đơn cho từng thành viên và nguy cơ phát sinh nợ xấu tồn đọng của cá nhân trong phòng, nhóm xin ý kiến thầy về việc có nên tinh giản tính năng này, chỉ quản lý hóa đơn theo đầu phòng để bảo đảm tính khả thi khi bảo vệ đồ án.

3. **Pháp lý về sổ đỏ, nhà đất, giấy tờ đất, quyền sở hữu các phòng hay các tầng:**
   * Có cần cơ chế xác thực về quyền sở hữu của chủ trọ các thứ ko ? -> không thì dễ xảy ra tranh chấp còn có thì sẽ liên quan đến pháp lý nên cần sự xác nhận của thầy về vấn đề ni

4. **Nghiệp vụ thu tiền phòng và tiền dịch vụ lệch chu kỳ:**
   * Trong thực tế nhiều chủ trọ thu tiền phòng theo chu kỳ ba tháng hoặc sáu tháng một lần, nhưng tiền điện nước bắt buộc phải chốt theo từng tháng. Thầy có khuyến nghị gì về mô hình xử lý hóa đơn cho kịch bản này để vừa bảo đảm luồng dữ liệu chuẩn vừa không gây phức tạp cho người dùng.

5. **Phân quyền chụp ảnh công tơ điện nước:**
   * Hệ thống có nên cho phép khách thuê tự chụp ảnh đồng hồ điện nước gửi lên hệ thống để thuật toán nhận diện chữ số hỗ trợ chủ trọ, hay chỉ cho phép duy nhất chủ trọ thực hiện thao tác này để bảo đảm tính pháp lý.

6. **Cơ chế và phạm vi ảnh hưởng khi Admin khóa tài khoản:**
   * Khi Admin khóa tài khoản của Chủ trọ (do vi phạm, tranh chấp) hoặc tài khoản của một khách thuê trong phòng, hệ thống nên xử lý quyền truy cập, tiến trình sinh hoạt, dữ liệu phòng và tính hiệu lực của hợp đồng đối với các khách thuê còn lại như thế nào để không làm gián đoạn quyền lợi của họ?

7. **Phạm vi lưu trữ thông tin pháp lý (CCCD) trong hợp đồng**
   * Về mặt pháp lý của đồ án, hệ thống chỉ cần lưu thông tin/CCCD của người đại diện đứng tên ký hợp đồng, hay bắt buộc phải số hóa và ràng buộc CCCD của toàn bộ thành viên ở ghép trong hợp đồng?

---

## 4. Kế Hoạch Triển Khai Tiếp Theo

Dựa trên kết quả rà soát nghiệp vụ, nhóm đề ra các đầu việc cụ thể cần thực hiện trong giai đoạn kế tiếp:

1. **Cập nhật Thiết kế Cơ sở Dữ liệu:**
   * Rà soát lại bảng hợp đồng, hóa đơn và thành viên để loại bỏ các trường phục vụ chia sẻ hóa đơn cá nhân, bổ sung trạng thái lưu trữ hồ sơ hợp đồng scan và cấu hình chu kỳ nhắc nợ của từng chủ trọ.

2. **Nghiên cứu cơ chế khóa tài khoản an toàn:**
   * Khảo sát giải pháp kỹ thuật từ các hệ thống quản lý bất động sản thực tế để xây dựng luồng khóa tài khoản vi phạm mà không làm gián đoạn quyền lợi sinh hoạt và lịch sử hợp đồng của các bên liên quan.

3. **Chuẩn bị tích hợp Google OAuth:**
   * Xây dựng luồng đăng nhập một chạm qua tài khoản Google, thiết kế biểu mẫu bổ sung thông tin số điện thoại và lựa chọn vai trò đối với người dùng truy cập lần đầu.

4. **Triển khai thiết kế giao diện cho Khách thuê:**
   * Hoàn thiện sơ đồ màn hình và xây dựng wireframe chi tiết cho web và ứng dụng di động của khách thuê, bám sát kiến trúc độc lập giữa tiện ích phòng trọ và kênh trò chuyện cộng đồng.

->>> Sau khi hoàn thành các công việc này sẽ triển khai các việc xây dụng usecase, các diagrams quan trọng, lập trình hệ thống

