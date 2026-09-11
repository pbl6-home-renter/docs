# Tenant User Flow — PBL6
---
## 1. Tổng quan Tenant trong hệ thống

### 1.1 Tenant là ai trong vòng đời sản phẩm

Tenant là 1 trong 2 phía chính của nền tảng, nhưng khác với landlord, **tenant không bắt buộc phải dùng app** — landlord vẫn có thể vận hành toàn bộ vòng đời thuê phòng một mình nếu tenant không tham gia. Vì vậy toàn bộ user flow tenant phải được thiết kế với tinh thần:

> **App tenant là lớp trải nghiệm CỘNG THÊM, không phải điều kiện bắt buộc để vòng đời thuê phòng vận hành.**

Mỗi tenant thực tế rơi vào 1 hoặc nhiều trong các trạng thái sau tại bất kỳ thời điểm nào:

| Trạng thái | Mô tả | Có tài khoản? |
| -- | -- | -- |
| **Khách vãng lai (Guest)** | Chưa từng thuê, đang tìm phòng/tìm bạn ở ghép | Không |
| **Đang tìm bạn ở ghép** | Đã có hồ sơ, đang match, chưa chốt phòng nào | Có |
| **Tenant chính thức (Active)** | Đã là thành viên chính thức của ≥1 hợp đồng đang hiệu lực, dùng app | Có |
| **Tenant thụ động (Passive)** | Đã là thành viên hợp đồng nhưng không dùng app — mọi thứ landlord xử lý thay qua kênh ngoài | Có thể không |
| **Cựu tenant** | Hợp đồng đã kết thúc, còn lịch sử trong app | Có |

Một tài khoản có thể **đi qua nhiều trạng thái cùng lúc hoặc nối tiếp nhau** (ví dụ: vừa là cựu tenant ở phòng A, vừa đang match tìm bạn cho phòng B).

### 1.2 Nguyên tắc thiết kế bắt buộc (áp dụng cho MỌI flow bên dưới)

1. **Guest-first cho phần khám phá:** xem phòng, xem chi tiết, xem feed ghép bạn — không cần login. Chỉ hành động (lưu, gửi match, chat, thanh toán, đăng bài, quản lý) mới gate bằng popup đăng nhập tại chỗ — không có giao diện riêng cho guest/đã login.
2. **Tenant không tự tạo hoặc tự sửa hợp đồng/thành viên** — mọi thao tác pháp lý/hợp đồng đều do landlord thực hiện. App tenant ở các màn liên quan chỉ **hiển thị (read-only)**.
3. **Ghép bạn tách biệt hoàn toàn khỏi việc chọn phòng** — không áp ràng buộc landlord (giới tính, số người, ngân sách) trong giai đoạn tìm bạn; ràng buộc đó chỉ có tác dụng ở bước landlord tạo hợp đồng sau này.
4. **Property Chat chỉ tồn tại sau khi có hợp đồng active** — trước đó, mọi liên hệ với landlord là qua thông tin liên hệ tĩnh (SĐT).
5. **Mọi hóa đơn/thanh toán đều có song song 2 kênh:** online (QR/VNPay/MoMo) và tiền mặt (landlord xác nhận thủ công) — không có màn hình nào chỉ có 1 lựa chọn duy nhất.
6. **Thuê ngắn hạn tính theo ngày:** Hệ thống chỉ tính thời gian thuê theo ngày (mốc 00:00 nửa đêm làm chuẩn chuyển ngày, trước 0h tính là 1 ngày, qua sau 0h tính sang ngày kế tiếp), tuyệt đối không tính theo giờ.
7. **Bỏ qua khai báo lưu trú/tạm trú:** Ứng dụng không xử lý thủ tục khai báo tạm trú của người dùng.
8. **Quy tắc khi tài khoản Khách thuê bị khóa:** Khách thuê vẫn được phép đăng nhập để xem và thanh toán hợp đồng/hóa đơn hiện tại nhằm đảm bảo nghĩa vụ tài chính, nhưng bị khóa hoàn toàn chức năng gia hạn hợp đồng, không thể tìm thuê phòng mới hay tạo hợp đồng mới.
9. **Quy định Camera và tải ảnh công tơ điện nước:** Hệ thống tích hợp Camera chụp trực tiếp tại chỗ cho phép cả Chủ trọ và Khách thuê đều có thể dùng để chụp ảnh đồng hồ điện nước. Tuy nhiên, **Khách thuê KHÔNG ĐƯỢC PHÉP tải ảnh có sẵn từ bộ nhớ thiết bị (thư viện ảnh) lên**, quyền tải ảnh từ máy lên chỉ dành riêng cho Chủ trọ.
10. **Gộp chi phí vào danh mục Dịch vụ & Quy về từng tháng:** Hóa đơn trên hệ thống gồm Tiền phòng và Dịch vụ (gộp điện, nước, wifi, máy giặt, rác...). Toàn bộ hóa đơn được chuẩn hóa quy về theo từng tháng.
11. **Mọi thành viên trong phòng đều có quyền thanh toán:** Bất kỳ ai trong phòng đều có thể quét mã VietQR động hoặc nộp tiền mặt để hoàn tất thanh toán hóa đơn của phòng.
12. **Trạng thái phòng sau Checkout:** Sau khi thanh lý hợp đồng và bàn giao phòng, phòng trọ chuyển sang trạng thái chờ dọn dẹp, chỉ khi chủ trọ hoàn tất vệ sinh và bấm xác nhận thì phòng mới hiển thị lại sẵn sàng cho thuê.

### 1.3 Kiến trúc điều hướng tổng thể

```mermaid
flowchart LR
    Home(["Mở app"]) --> Nav["Bottom navigation"]
    Nav --> T1["Tìm phòng"]
    Nav --> T2["Ghép bạn"]
    Nav --> T3["Phòng của tôi"]
    Nav --> T4["Tài khoản"]
```

| Tab | Nội dung chính | Cần login? |
| -- | -- | -- |
| **Tìm phòng** | Bộ lọc, danh sách phòng, chi tiết phòng | Xem: không · Lưu/liên hệ: có |
| **Ghép bạn** | Feed hồ sơ roommate, quản lý match | Xem feed: không · Gửi match: có |
| **Phòng của tôi** | Hub hợp đồng / thành viên / hóa đơn / chat / sự cố — ẩn nếu chưa có hợp đồng nào | Có |
| **Tài khoản** | Hồ sơ, lịch sử uy tín + consent, cài đặt | Có |

---

## 2. BATCH 1 — Khám phá (Guest-first)

### Sub-Flow 1: Tìm phòng & xem chi tiết (Guest)

```mermaid
flowchart TD
    Start(["Mở app / tab Tìm phòng"]) --> Filter["Bộ lọc tìm phòng\n(giá, diện tích, tiện nghi, khoảng cách)"]
    Filter --> List["Danh sách kết quả dạng thẻ"]
    List --> Detail["Chi tiết phòng\n(ảnh, giá, tiện nghi, SĐT landlord)"]
    Detail --> Action{"Chạm hành động?"}
    Action -->|"Chỉ xem"| End1(["Kết thúc — không cần login"])
    Action -->|"Lưu phòng / Liên hệ"| Gate[["Kiểm tra đăng nhập — xem Sub-Flow 3"]]

    style Start fill:#e6f1fb,stroke:#378add
    style Filter fill:#e6f1fb,stroke:#378add
    style List fill:#e6f1fb,stroke:#378add
    style Detail fill:#e6f1fb,stroke:#378add
    style End1 fill:#eaf3de,stroke:#639922
    style Gate fill:#faeeda,stroke:#ba7517
```

| Màn hình | Nội dung | Ghi chú thiết kế |
| -- | -- | -- |
| Bộ lọc + Danh sách | Filter giá/diện tích/tiện nghi/khoảng cách; kết quả dạng card: ảnh, giá, khu vực, số phòng trống | Có thể thêm sort (gần nhất/giá thấp-cao) |
| Chi tiết phòng | Gallery ảnh, mô tả, tiện nghi, giá, ràng buộc phòng (nếu có, hiện dạng badge — ví dụ "Chỉ nhận nữ"), SĐT/liên hệ landlord tĩnh | Ràng buộc hiện ở đây chỉ mang tính **thông tin**, chưa liên quan matching |

### Sub-Flow 2: Lưu phòng (hành động cần login)

```mermaid
flowchart TD
    Detail["Chi tiết phòng"] --> Tap["Chạm icon Lưu"]
    Tap --> Check{"Đã đăng nhập?"}
    Check -->|"Có"| Saved["Phòng được lưu\nvào danh sách yêu thích"]
    Check -->|"Chưa"| Popup("Popup: Đăng nhập để lưu phòng")
    Popup --> Login[["Sub-Flow 3 — Đăng nhập"]]
    Login --> Saved

    style Detail fill:#e6f1fb,stroke:#378add
    style Tap fill:#e6f1fb,stroke:#378add
    style Popup fill:#faeeda,stroke:#ba7517
    style Saved fill:#eaf3de,stroke:#639922
```

### Sub-Flow 3: Đăng ký & Scan danh sách thành viên hợp đồng (Tenant)

```mermaid
flowchart TD
    Start(["Popup đăng nhập được trigger"]) --> Register["Đăng ký tài khoản mới:\nNhập Email, Mật khẩu, Họ tên, SĐT"]
    Register --> SubmitReg["Gửi yêu cầu đăng ký"]
    SubmitReg --> VerifyReg{"Đăng ký thành công?"}
    VerifyReg -->|"Thất bại"| ErrorReg["Báo lỗi: Email đã tồn tại hoặc thông tin không hợp lệ"] --> Register
    VerifyReg -->|"Thành công"| Home["Về lại thao tác đang dở"]

    Home --> Scan[["Hệ thống quét nền: đối chiếu SĐT tài khoản\nvới danh sách thành viên hợp đồng"]]

    style Start fill:#faeeda,stroke:#ba7517
    style Register fill:#faeeda,stroke:#ba7517
    style Home fill:#f1efe8,stroke:#5f5e5a
    style ShowContract fill:#eaf3de,stroke:#639922
    style Empty fill:#f1efe8,stroke:#5f5e5a
```

**Lưu ý thiết kế quan trọng:** bước scan **không chỉ chạy 1 lần lúc đăng ký** — chạy lại mỗi khi landlord thêm/sửa thông tin thành viên. Tab "Phòng của tôi" **luôn hiển thị** dù có hay không hợp đồng; khi chưa có thì hiện trống, khi có thì hiện danh sách hợp đồng đã liên kết.

---

## 3. BATCH 2 — Ghép bạn (Roommate matching)

> Nguyên tắc cốt lõi: đây là **feed độc lập, xảy ra TRƯỚC khi chọn phòng**. Không áp ràng buộc landlord ở giai đoạn này.

### Sub-Flow 4: Xem feed & tạo hồ sơ

```mermaid
flowchart TD
    Start(["Tab Ghép bạn"]) --> Feed["Feed cuộn dọc:\nảnh, mô tả, ngân sách, khu vực mong muốn"]
    Feed --> View["Xem chi tiết 1 hồ sơ"]
    View --> Act{"Chạm hành động?"}
    Act -->|"Chỉ xem"| End1(["Kết thúc — không cần login"])
    Act -->|"Đăng bài / Gửi match"| Check{"Đã đăng nhập?"}
    Check -->|"Chưa"| Gate("Popup đăng nhập")
    Gate --> Login[["Sub-Flow 3"]]
    Check -->|"Có, chưa có hồ sơ"| Create["Tạo hồ sơ cá nhân\n(ảnh, mô tả, ngân sách, khu vực)"]
    Create --> Post["Đăng bài vào feed"]
    Check -->|"Có, đã có hồ sơ"| Send[["Sub-Flow 5 — Gửi match request"]]

    style Start fill:#e6f1fb,stroke:#378add
    style Feed fill:#e6f1fb,stroke:#378add
    style View fill:#e6f1fb,stroke:#378add
    style End1 fill:#eaf3de,stroke:#639922
    style Gate fill:#faeeda,stroke:#ba7517
    style Create fill:#faeeda,stroke:#ba7517
    style Post fill:#faeeda,stroke:#ba7517
```

| Màn hình | Nội dung | Ghi chú |
| -- | -- | -- |
| Feed | Card cuộn dọc: ảnh, tên hiển thị, mô tả ngắn, ngân sách, khu vực mong muốn, badge tuổi/giới tính | Không có like/share/comment, không thuật toán ranking — chỉ list theo mới nhất/gần khu vực |
| Tạo hồ sơ | Ảnh đại diện, mô tả lối sống, ngân sách, khu vực mong muốn, thời điểm cần dọn vào | 1 tài khoản = 1 hồ sơ; có thể ẩn/hiện bài đăng bất kỳ lúc nào |

### Sub-Flow 5: Gửi/nhận match request (2 chiều)

```mermaid
flowchart TD
    Start(["Từ chi tiết hồ sơ, chạm Gửi yêu cầu"]) --> Send["Trạng thái: Đã gửi — chờ phản hồi"]
    Send --> Wait{"Bên kia phản hồi?"}
    Wait -->|"Chấp nhận"| Success["Match thành công"]
    Wait -->|"Từ chối"| Declined["Trạng thái: Đã từ chối"]
    Wait -->|"Chưa phản hồi"| Pending["Vẫn hiện trong danh sách\nYêu cầu đã gửi"]

    Received(["Nhận được 1 yêu cầu mới"]) --> Notif["Thông báo + hiện trong\ndanh sách Yêu cầu đã nhận"]
    Notif --> Decide{"Chấp nhận hay từ chối?"}
    Decide -->|"Chấp nhận"| Success
    Decide -->|"Từ chối"| Declined

    style Start fill:#faeeda,stroke:#ba7517
    style Send fill:#faeeda,stroke:#ba7517
    style Success fill:#eaf3de,stroke:#639922
    style Declined fill:#f1efe8,stroke:#5f5e5a
    style Pending fill:#f1efe8,stroke:#5f5e5a
    style Received fill:#faeeda,stroke:#ba7517
    style Notif fill:#faeeda,stroke:#ba7517
```

| Màn hình | Nội dung |
| -- | -- |
| Danh sách match | 2 tab: "Đã gửi" (chờ/từ chối) và "Đã nhận" (chờ mình phản hồi) |
| Match thành công | Card chúc mừng + nút "Xem thông tin liên hệ" |

### Sub-Flow 6: Sau match: lộ liên hệ → thành thành viên chính thức

```mermaid
flowchart TD
    Success(["Match thành công"]) --> Reveal["Hiện SĐT + Zalo (nếu có)\ncủa cả 2 bên"]
    Reveal --> Outside[/"Nhóm tự liên hệ, tìm phòng,\nthống nhất ngoài app"/]
    Outside --> Report[/"Nhóm báo landlord\n(gặp trực tiếp / SĐT)"/]
    Report --> LandlordAdd[["Landlord thêm nhóm vào\ndanh sách thành viên hợp đồng"]]
    LandlordAdd --> Appear["Tenant thấy phòng xuất hiện\nở tab Phòng của tôi"]

    style Success fill:#eaf3de,stroke:#639922
    style Reveal fill:#eaf3de,stroke:#639922
    style Outside fill:#f1efe8,stroke:#5f5e5a,stroke-dasharray: 5 5
    style Report fill:#f1efe8,stroke:#5f5e5a,stroke-dasharray: 5 5
    style Appear fill:#eaf3de,stroke:#639922
```

**Không có màn hình app nào cho bước "Outside" và "Report"** — đây là hành động ngoài hệ thống theo thiết kế. App chỉ cần đảm bảo bước cuối "Appear" hoạt động đúng (dựa vào Sub-Flow 3 — auto liên kết theo SĐT).

---

## 4. BATCH 3 — "Phòng của tôi" (Hub sau khi có hợp đồng active)

### Sub-Flow 7: Xem danh sách hợp đồng

```mermaid
flowchart TD
    Start(["Chạm tab Phòng của tôi"]) --> List["Danh sách hợp đồng đang hiệu lực\n(Phòng, Địa chỉ, Thời hạn, Trạng thái)"]
    List --> Select["Chọn 1 hợp đồng để vào Hub phòng"]

    style Start fill:#faeeda,stroke:#ba7517
    style List fill:#faeeda,stroke:#ba7517
    style Select fill:#faeeda,stroke:#ba7517
```

### Sub-Flow 8: Cấu trúc Hub (tổng quan các mục con)

```mermaid
flowchart TD
    Hub["Hub: Phòng của tôi"] --> M1["Xem hợp đồng"]
    Hub --> M2["Danh sách thành viên"]
    Hub --> M3["Hóa đơn"]
    Hub --> M4["Property Chat"]
    Hub --> M5["Báo & theo dõi sự cố"]

    style Hub fill:#faeeda,stroke:#ba7517
```

### Sub-Flow 9: Xem hợp đồng (read-only)

```mermaid
flowchart TD
    Start(["Chạm mục Hợp đồng"]) --> View["Thông tin HĐ: tiền thuê,\ncọc, ngày bắt đầu/kết thúc, điều khoản"]
    View --> Status{"Trạng thái file ký?"}
    Status -->|"Đã upload"| File["Xem file HĐ đã ký\n(ảnh/PDF)"]
    Status -->|"Chưa upload (draft)"| Info["Ghi chú: HĐ đang chờ\nlandlord upload file đã ký"]

    style Start fill:#faeeda,stroke:#ba7517
    style View fill:#faeeda,stroke:#ba7517
    style File fill:#eaf3de,stroke:#639922
    style Info fill:#f1efe8,stroke:#5f5e5a
```

**Không có nút ký nào ở đây** — hệ thống không có cơ chế ký điện tử, toàn bộ màn hình này chỉ để tenant tra cứu thông tin.

### Sub-Flow 10: Danh sách thành viên

```mermaid
flowchart TD
    Start(["Chạm mục Thành viên"]) --> List["Danh sách tên các thành viên trong phòng"]

    style Start fill:#faeeda,stroke:#ba7517
    style List fill:#faeeda,stroke:#ba7517
```

**Read-only tuyệt đối** — không có nút thêm/xóa thành viên ở đây.

### Sub-Flow 11: Hóa đơn (Thanh toán linh hoạt cho mọi thành viên)

Mọi hóa đơn trên hệ thống được **chuẩn hóa quy về từng tháng**. Mọi thành viên trong phòng đều có quyền xem chi tiết và trực tiếp thực hiện thanh toán.

```mermaid
flowchart TD
    Start(["Chạm mục Hóa đơn"]) --> LoadInvoice["Tải danh sách hóa đơn theo tháng của phòng"]
    LoadInvoice --> ViewInvoice["Mọi thành viên trong phòng đều xem được toàn bộ hóa đơn\n(Kỳ thanh toán, hạn nộp, Tiền phòng + Dịch vụ)"]
    ViewInvoice --> ActionPay["Nút 'Thanh toán' hiển thị cho mọi thành viên trong phòng"]
    ActionPay --> Pay1[["Sub-Flow 12 — Thanh toán"]]

    style Start fill:#faeeda,stroke:#ba7517
    style LoadInvoice fill:#faeeda,stroke:#ba7517
    style ViewInvoice fill:#faeeda,stroke:#ba7517
    style ActionPay fill:#faeeda,stroke:#ba7517
    style Pay1 fill:#eaf3de,stroke:#639922
```

**Lưu ý quan trọng:** **Bất kỳ thành viên nào trong phòng** cũng có thể thanh toán hóa đơn bằng cách quét mã VietQR động hoặc nộp tiền mặt cho chủ trọ.

### Sub-Flow 12: Thanh toán hóa đơn (online / tiền mặt)

```mermaid
flowchart TD
    Start(["Xem chi tiết 1 hóa đơn tháng"]) --> Detail["Số tiền tổng, kỳ tháng, hạn thanh toán,\nChi tiết: Tiền phòng + Danh mục Dịch vụ (Điện, Nước, Wifi, Rác, Máy giặt)"]
    Detail --> Status{"Trạng thái hóa đơn?"}
    Status -->|"Đã thu một phần"| PartialNote["Hiển thị 'Đã thu X / còn nợ Y'\nnút thanh toán phần còn lại"]
    Status -->|"Đã thanh toán / Thanh toán đủ"| HistoryTab["Khi mở tab History: ghi nhận 'Đã thanh toán đủ'"]
    Status -->|"Chưa thanh toán / Quá hạn"| Choose{"Chọn kênh thanh toán"}
    Choose -->|"Online VietQR"| QR["Quét mã VietQR động định danh phòng"]
    QR --> Webhook[["Webhook ngân hàng đối soát tự động"]]
    Webhook --> Paid1["Trạng thái: Đã thanh toán (Gạch nợ cho phòng)"]
    Choose -->|"Tiền mặt"| Cash[/"Nộp tiền mặt trực tiếp cho chủ trọ"/]
    Cash --> Confirm[["Chủ trọ xác nhận thu tiền mặt trên hệ thống"]]
    Confirm --> Paid2["Trạng thái: Đã thanh toán (Gạch nợ cho phòng)"]

    style Start fill:#faeeda,stroke:#ba7517
    style Detail fill:#faeeda,stroke:#ba7517
    style QR fill:#faeeda,stroke:#ba7517
    style Paid1 fill:#eaf3de,stroke:#639922
    style Paid2 fill:#eaf3de,stroke:#639922
    style Cash fill:#f1efe8,stroke:#5f5e5a,stroke-dasharray: 5 5
```

**Lưu ý minh bạch phí:** Màn chi tiết hóa đơn quy về theo từng tháng, hiển thị rõ ràng Tiền phòng và nhóm **Dịch vụ** (trong đó bóc tách chi tiết lượng điện, nước theo chỉ số công tơ do chủ trọ chốt hoặc khách thuê hỗ trợ chụp bằng Camera trong app, cùng các chi phí dịch vụ cố định như Wifi, rác, máy giặt...). Khách thuê chỉ được chụp trực tiếp qua Camera hệ thống, không được tải ảnh có sẵn từ máy lên.

**Nhắc quá hạn:** nếu hóa đơn quá hạn, bot tự động post card nhắc vào Property Chat riêng phòng (xem Sub-Flow 13) — không có màn hình riêng cho việc này, chỉ là 1 loại card trong chat.

### Sub-Flow 13: Property Chat riêng phòng

```mermaid
flowchart TD
    Start(["Chạm mục Chat"]) --> Room["Chat riêng phòng"]
    Room --> Type{"Loại nội dung?"}
    Type -->|"Tin nhắn thường"| Text["Text / ảnh / file"]
    Type -->|"Card bot tự động"| Bot["Card: kết quả chốt số,\nhóa đơn mới, nhắc quá hạn"]
    Type -->|"@mention"| Mention["Autocomplete gắn tên\nthành viên/landlord"]

    Room --> Switch["Chuyển sang Chat chung tòa\n(chỉ text/ảnh/file + mention)"]

    style Start fill:#faeeda,stroke:#ba7517
    style Room fill:#faeeda,stroke:#ba7517
    style Text fill:#faeeda,stroke:#ba7517
    style Bot fill:#eeedfe,stroke:#534ab7
    style Mention fill:#faeeda,stroke:#ba7517
    style Switch fill:#f1efe8,stroke:#5f5e5a
```

### Sub-Flow 14: Báo & theo dõi sự cố

```mermaid
flowchart TD
    Start(["Từ Hub Phòng của tôi, chọn 'Báo sự cố'"]) --> Form["Chọn phòng → Mô tả sự cố + đính kèm ảnh"]
    Form --> Create[["Tạo báo cáo sự cố: mở"]]
    Create --> Notify["Bot post card vào chat +\nFCM push tới landlord"]
    Notify --> Track["Theo dõi trạng thái"]
    Track --> Status{"Trạng thái hiện tại?"}
    Status -->|"Mở"| Wait["Chờ landlord xử lý"]
    Status -->|"Đang xử lý"| Progress["Đang sửa — có thể\ntrao đổi thêm qua chat"]
    Status -->|"Đã hoàn thành"| Done["Đã xử lý xong"]

    style Start fill:#faeeda,stroke:#ba7517
    style Form fill:#faeeda,stroke:#ba7517
    style Notify fill:#faeeda,stroke:#ba7517
    style Wait fill:#f1efe8,stroke:#5f5e5a
    style Progress fill:#faeeda,stroke:#ba7517
    style Done fill:#eaf3de,stroke:#639922
```

**Nhánh Passive:** nếu tenant không dùng app, sự cố vẫn tồn tại vì landlord có thể tự tạo báo cáo sự cố thay — flow này chỉ mô tả nhánh Active, không có bước nào bị chặn nếu tenant vắng mặt.

---

## 5. BATCH 4 — Phần còn lại

### Sub-Flow 15: Hồ sơ cá nhân & cài đặt

```mermaid
flowchart TD
    Start(["Tab Tài khoản"]) --> Profile["Thông tin cá nhân: tên,\nsố điện thoại, ảnh đại diện"]
    Profile --> Notif["Cài đặt thông báo\n(bật/tắt theo loại: hóa đơn, chat, sự cố)"]
    Notif --> Logout["Đăng xuất"]

    style Start fill:#faeeda,stroke:#ba7517
    style Profile fill:#faeeda,stroke:#ba7517
    style Notif fill:#faeeda,stroke:#ba7517
```

### Sub-Flow 16: Thông báo FCM → deep link

```mermaid
flowchart TD
    Push(["FCM push đến"]) --> Type{"Loại thông báo?"}
    Type -->|"Hóa đơn mới/quá hạn"| Deep1["Deep link → Chi tiết hóa đơn"]
    Type -->|"Tin nhắn mới trong Chat"| Deep2["Deep link → Property Chat"]
    Type -->|"Cập nhật sự cố"| Deep3["Deep link → Chi tiết báo cáo sự cố"]
    Type -->|"Match request mới"| Deep4["Deep link → Danh sách Yêu cầu đã nhận"]

    style Push fill:#eeedfe,stroke:#534ab7
    style Deep1 fill:#faeeda,stroke:#ba7517
    style Deep2 fill:#faeeda,stroke:#ba7517
    style Deep3 fill:#faeeda,stroke:#ba7517
    style Deep4 fill:#faeeda,stroke:#ba7517
```

---

## 6. Bảng tổng hợp toàn bộ màn hình (screen inventory)

| # | Màn hình | Batch | Cần login? |
| -- | -- | -- | -- |
| 1 | Bản đồ + Filter | 1 | Không |
| 2 | Danh sách kết quả phòng | 1 | Không |
| 3 | Chi tiết phòng | 1 | Không |
| 4 | Popup đăng nhập (Email + Mật khẩu) | 1 | — |
| 5 | Danh sách phòng đã lưu | 1 | Có |
| 6 | Feed ghép bạn | 2 | Không |
| 7 | Chi tiết 1 hồ sơ roommate | 2 | Không |
| 8 | Tạo/sửa hồ sơ cá nhân | 2 | Có |
| 9 | Danh sách Yêu cầu đã gửi/đã nhận | 2 | Có |
| 10 | Màn Match thành công | 2 | Có |
| 11 | Danh sách hợp đồng | 3 | Có |
| 12 | Hub Phòng của tôi | 3 | Có |
| 13 | Xem hợp đồng | 3 | Có |
| 14 | Danh sách thành viên | 3 | Có |
| 15 | Danh sách hóa đơn | 3 | Có |
| 16 | Chi tiết hóa đơn + breakdown (điện/nước/phí định kỳ) + thanh toán | 3 | Có |
| 17 | Property Chat riêng phòng | 3 | Có |
| 18 | Property Chat chung tòa | 3 | Có |
| 19 | Form tạo sự cố | 3 | Có |
| 20 | Chi tiết/theo dõi sự cố | 3 | Có |
| 21 | Hồ sơ cá nhân / cài đặt | 4 | Có |
| 22 | Cài đặt thông báo | 4 | Có |

---
