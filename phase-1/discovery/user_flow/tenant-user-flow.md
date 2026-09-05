# Tenant User Flow — PBL6

> **Mục đích:** tài liệu user flow đầy đủ, chi tiết cho phía **Tenant**, dùng để designer triển khai UI/UX.
>
> **Quy ước đọc sơ đồ:** xem Legend ở mục 0 trước khi đọc bất kỳ flow nào bên dưới.

---

## 0. Legend — quy tắc ký hiệu dùng xuyên suốt tài liệu

```mermaid
flowchart TD
    A(["Điểm bắt đầu / kết thúc"])
    B["Màn hình (Screen)"]
    C{"Điểm quyết định / rẽ nhánh"}
    D[["Hệ thống tự xử lý (background)"]]
    E("Popup / Modal")
    F[/"Hành động ngoài app (offline / kênh ngoài)"/]

    A --> B --> C
    C --> D
    C --> E
    C --> F
```

| Ký hiệu | Ý nghĩa |
| -- | -- |
| Stadium `(...)` | Điểm bắt đầu/kết thúc 1 flow |
| Rectangle `[...]` | 1 màn hình cụ thể trong app |
| Diamond `{...}` | Điểm rẽ nhánh — luôn có ≥2 nhánh output |
| Subroutine `[[...]]` | Hệ thống tự xử lý ngầm, không phải màn hình (vd: auto chia đều, matching filter) |
| Rounded `(...)` | Popup/Modal nổi lên trên màn hình hiện tại, không chuyển trang |
| Parallelogram `[/.../]` | Hành động xảy ra **ngoài app** (SĐT, giấy, tiền mặt, gặp trực tiếp) |
| Màu xanh dương | Guest xem được, không cần login |
| Màu cam | Cần đăng nhập mới thao tác được |
| Màu xanh lá | Trạng thái hoàn tất / thành công |
| Màu xám | Trung tính / hệ thống nền |

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
3. **Ghép bạn tách biệt hoàn toàn khỏi việc chọn phòng** — không áp ràng buộc landlord (max người/giới tính/ngân sách) trong giai đoạn tìm bạn; ràng buộc đó chỉ có tác dụng ở bước landlord tạo hợp đồng sau này.
4. **Property Chat chỉ tồn tại sau khi có hợp đồng active** — trước đó, mọi liên hệ với landlord là qua thông tin liên hệ tĩnh (SĐT).
5. **Mọi hóa đơn/thanh toán đều có song song 2 kênh:** online (QR/VNPay/MoMo) và tiền mặt (landlord xác nhận thủ công) — không có màn hình nào chỉ có 1 lựa chọn duy nhất.

### 1.3 Kiến trúc điều hướng tổng thể

```mermaid
flowchart LR
    Home(["Mở app"]) --> Nav["Bottom navigation"]
    Nav --> T1["Tìm phòng"]
    Nav --> T2["Ghép bạn"]
    Nav --> T3["Phòng của tôi"]
    Nav --> T4["Tài khoản"]

    T3 -.->|"Chỉ hiện khi có\nhợp đồng active"| T3
```

| Tab | Nội dung chính | Cần login? |
| -- | -- | -- |
| **Tìm phòng** | Bản đồ, filter, chi tiết phòng | Xem: không · Lưu/liên hệ: có |
| **Ghép bạn** | Feed hồ sơ roommate, quản lý match | Xem feed: không · Gửi match: có |
| **Phòng của tôi** | Hub hợp đồng / thành viên / hóa đơn / chat / sự cố — ẩn nếu chưa có hợp đồng nào | Có |
| **Tài khoản** | Hồ sơ, lịch sử uy tín + consent, cài đặt | Có |

---

## 2. BATCH 1 — Khám phá (Guest-first)

### Flow 1.1 — Tìm phòng & xem chi tiết (Guest)

```mermaid
flowchart TD
    Start(["Mở app / tab Tìm phòng"]) --> Map["Màn Bản đồ + Filter\n(giá, diện tích, tiện nghi, khoảng cách)"]
    Map --> List["Danh sách kết quả dạng thẻ"]
    List --> Detail["Chi tiết phòng\n(ảnh, giá, tiện nghi, SĐT landlord)"]
    Detail --> Action{"Chạm hành động?"}
    Action -->|"Chỉ xem"| End1(["Kết thúc — không cần login"])
    Action -->|"Lưu phòng / Liên hệ"| Gate[["Kiểm tra đăng nhập — xem Flow 1.3"]]

    style Start fill:#e6f1fb,stroke:#378add
    style Map fill:#e6f1fb,stroke:#378add
    style List fill:#e6f1fb,stroke:#378add
    style Detail fill:#e6f1fb,stroke:#378add
    style End1 fill:#eaf3de,stroke:#639922
    style Gate fill:#faeeda,stroke:#ba7517
```

| Màn hình | Nội dung | Ghi chú thiết kế |
| -- | -- | -- |
| Bản đồ + Filter | Pin trên bản đồ theo vị trí thật; filter giá/diện tích/tiện nghi/khoảng cách | Toggle giữa view bản đồ ↔ view danh sách |
| Danh sách kết quả | Card: ảnh đại diện, giá, khu vực, số phòng trống | Có thể thêm sort (gần nhất/giá thấp-cao) |
| Chi tiết phòng | Gallery ảnh, mô tả, tiện nghi, giá, ràng buộc phòng (nếu có, hiện dạng badge — ví dụ "Chỉ nhận nữ", "Tối đa 3 người"), SĐT/liên hệ landlord tĩnh | Ràng buộc landlord hiện ở đây chỉ mang tính **thông tin**, chưa liên quan matching |

### Flow 1.2 — Lưu phòng (hành động cần login)

```mermaid
flowchart TD
    Detail["Chi tiết phòng"] --> Tap["Chạm icon Lưu"]
    Tap --> Check{"Đã đăng nhập?"}
    Check -->|"Có"| Saved["Phòng được lưu\nvào danh sách yêu thích"]
    Check -->|"Chưa"| Popup("Popup: Đăng nhập để lưu phòng")
    Popup --> Login[["Flow 1.3 — Đăng nhập"]]
    Login --> Saved

    style Detail fill:#e6f1fb,stroke:#378add
    style Tap fill:#e6f1fb,stroke:#378add
    style Popup fill:#faeeda,stroke:#ba7517
    style Saved fill:#eaf3de,stroke:#639922
```

### Flow 1.3 — Đăng nhập & tự động liên kết hợp đồng

```mermaid
flowchart TD
    Start(["Popup đăng nhập được trigger"]) --> Phone["Nhập số điện thoại"]
    Phone --> OTP["Xác thực OTP"]
    OTP --> Scan[["Hệ thống quét danh sách thành viên hợp đồng\ntheo số điện thoại"]]
    Scan --> Match{"Có khớp?"}
    Match -->|"Có"| Home1["Về lại thao tác đang dở\n+ tab Phòng của tôi xuất hiện"]
    Match -->|"Không"| Home2["Về lại thao tác đang dở\nchưa có tab Phòng của tôi"]

    style Start fill:#faeeda,stroke:#ba7517
    style Phone fill:#faeeda,stroke:#ba7517
    style OTP fill:#faeeda,stroke:#ba7517
    style Home1 fill:#eaf3de,stroke:#639922
    style Home2 fill:#f1efe8,stroke:#5f5e5a
```

**Lưu ý thiết kế quan trọng:** bước "Quét danh sách thành viên" **không chỉ chạy 1 lần lúc đăng ký** — chạy lại mỗi khi landlord thêm/sửa số điện thoại của thành viên. App cần có cơ chế re-check nền (mở app / pull-to-refresh) để tự chuyển trạng thái "Không → Có" mà không bắt đăng nhập lại.

---

## 3. BATCH 2 — Ghép bạn (Roommate matching)

> Nguyên tắc cốt lõi: đây là **feed độc lập, xảy ra TRƯỚC khi chọn phòng**. Không áp ràng buộc landlord ở giai đoạn này.

### Flow 2.1 — Xem feed & tạo hồ sơ

```mermaid
flowchart TD
    Start(["Tab Ghép bạn"]) --> Feed["Feed cuộn dọc:\nảnh, mô tả, ngân sách, khu vực mong muốn"]
    Feed --> View["Xem chi tiết 1 hồ sơ"]
    View --> Act{"Chạm hành động?"}
    Act -->|"Chỉ xem"| End1(["Kết thúc — không cần login"])
    Act -->|"Đăng bài / Gửi match"| Check{"Đã đăng nhập?"}
    Check -->|"Chưa"| Gate("Popup đăng nhập")
    Gate --> Login[["Flow 1.3"]]
    Check -->|"Có, chưa có hồ sơ"| Create["Tạo hồ sơ cá nhân\n(ảnh, mô tả, ngân sách, khu vực)"]
    Create --> Post["Đăng bài vào feed"]
    Check -->|"Có, đã có hồ sơ"| Send[["Flow 2.2 — Gửi match request"]]

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

### Flow 2.2 — Gửi/nhận match request (2 chiều)

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

### Flow 2.3 — Sau match: lộ liên hệ → thành thành viên chính thức

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

**Không có màn hình app nào cho bước "Outside" và "Report"** — đây là hành động ngoài hệ thống theo thiết kế. App chỉ cần đảm bảo bước cuối "Appear" hoạt động đúng (dựa vào Flow 1.3 — auto liên kết theo SĐT).

---

## 4. BATCH 3 — "Phòng của tôi" (Hub sau khi có hợp đồng active)

### Flow 3.1 — Vào hub & chuyển đổi giữa nhiều hợp đồng (nếu có)

```mermaid
flowchart TD
    Start(["Chạm tab Phòng của tôi"]) --> Count{"Có bao nhiêu\nhợp đồng active?"}
    Count -->|"1"| Hub["Vào thẳng Hub phòng đó"]
    Count -->|">1"| Switcher["Danh sách chọn phòng\n(switcher)"]
    Switcher --> Hub

    style Start fill:#faeeda,stroke:#ba7517
    style Hub fill:#faeeda,stroke:#ba7517
    style Switcher fill:#faeeda,stroke:#ba7517
```

### Flow 3.2 — Cấu trúc Hub (tổng quan các mục con)

```mermaid
flowchart TD
    Hub["Hub: Phòng của tôi"] --> M1["Xem hợp đồng"]
    Hub --> M2["Danh sách thành viên"]
    Hub --> M3["Hóa đơn"]
    Hub --> M4["Property Chat"]
    Hub --> M5["Báo & theo dõi sự cố"]

    style Hub fill:#faeeda,stroke:#ba7517
```

### Flow 3.3 — Xem hợp đồng (read-only)

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

### Flow 3.4 — Danh sách thành viên & phần góp

```mermaid
flowchart TD
    Start(["Chạm mục Thành viên"]) --> Config{"Payment config?"}
    Config -->|"(a) Rep-payer"| ListA["Danh sách tên các thành viên\nkhông hiện số tiền (chia offline)"]
    Config -->|"(b) Shared-invoice"| ListB["Danh sách tên + phần góp\nmỗi người (auto chia đều)"]

    style Start fill:#faeeda,stroke:#ba7517
    style ListA fill:#faeeda,stroke:#ba7517
    style ListB fill:#faeeda,stroke:#ba7517
```

**Read-only tuyệt đối** — không có nút thêm/xóa thành viên ở đây, kể cả với lead tenant.

### Flow 3.5 — Hóa đơn (rẽ nhánh theo payment config)

```mermaid
flowchart TD
    Start(["Chạm mục Hóa đơn"]) --> Role{"Vai trò của tenant\ntrong hợp đồng?"}
    Role -->|"Config (a): không phải lead"| ViewOnly["Thấy toàn bộ hóa đơn\n(read-only, không có nút thanh toán)"]
    Role -->|"Config (a): là lead"| FullInvoice["Thấy toàn bộ hóa đơn,\ncó nút thanh toán"]
    Role -->|"Config (b): bất kỳ ai"| ShareInvoice["Thấy đúng phần của mình,\ncó nút thanh toán phần đó"]

    FullInvoice --> Pay1[["Flow 3.6 — Thanh toán"]]
    ShareInvoice --> Pay1
    ViewOnly --> NoPay["Chỉ để theo dõi minh bạch\n— không dẫn tới bước thanh toán"]

    style Start fill:#faeeda,stroke:#ba7517
    style ViewOnly fill:#f1efe8,stroke:#5f5e5a
    style NoPay fill:#f1efe8,stroke:#5f5e5a
    style FullInvoice fill:#faeeda,stroke:#ba7517
    style ShareInvoice fill:#faeeda,stroke:#ba7517
```

**Lưu ý quan trọng cho thiết kế:** ở config (a), **mọi thành viên đều nhìn thấy hóa đơn** (số tiền, kỳ, hạn thanh toán, chi tiết điện/nước) — chỉ khác ở chỗ **thành viên không phải lead không có nút thanh toán/chuyển khoản** trên màn hình đó (vì tiền vẫn chia offline giữa các thành viên, chỉ lead là người thực sự giao dịch với landlord). Đây là khác biệt về **quyền thao tác**, không phải khác biệt về **quyền xem**.

### Flow 3.6 — Thanh toán hóa đơn (online / tiền mặt)

```mermaid
flowchart TD
    Start(["Xem chi tiết 1 hóa đơn"]) --> Detail["Số tiền, kỳ, hạn thanh toán,\nchi tiết điện/nước"]
    Detail --> Choose{"Chọn kênh thanh toán"}
    Choose -->|"Online"| QR["Quét QR động /\nVNPay / MoMo"]
    QR --> Webhook[["Webhook đối soát tự động"]]
    Webhook --> Paid1["Trạng thái: Đã thanh toán"]
    Choose -->|"Tiền mặt"| Cash[/"Trả tiền mặt trực tiếp\ncho landlord"/]
    Cash --> Confirm[["Landlord xác nhận thủ công"]]
    Confirm --> Paid2["Trạng thái: Đã thanh toán"]

    style Start fill:#faeeda,stroke:#ba7517
    style Detail fill:#faeeda,stroke:#ba7517
    style QR fill:#faeeda,stroke:#ba7517
    style Paid1 fill:#eaf3de,stroke:#639922
    style Paid2 fill:#eaf3de,stroke:#639922
    style Cash fill:#f1efe8,stroke:#5f5e5a,stroke-dasharray: 5 5
```

**Nhắc quá hạn:** nếu hóa đơn quá hạn, bot tự động post card nhắc vào Property Chat riêng phòng (xem Flow 3.7) — không có màn hình riêng cho việc này, chỉ là 1 loại card trong chat.

### Flow 3.7 — Property Chat riêng phòng

```mermaid
flowchart TD
    Start(["Chạm mục Chat"]) --> Room["Chat riêng phòng"]
    Room --> Type{"Loại nội dung?"}
    Type -->|"Tin nhắn thường"| Text["Text / ảnh / file"]
    Type -->|"Card bot tự động"| Bot["Card: kết quả chốt số,\nhóa đơn mới, nhắc quá hạn"]
    Type -->|"Lệnh @issue"| IssueCmd[["Flow 3.8 — Tạo sự cố"]]
    Type -->|"@mention"| Mention["Autocomplete gắn tên\nthành viên/landlord"]

    Room --> Switch["Chuyển sang Chat chung tòa\n(chỉ text/ảnh/file + mention)"]

    style Start fill:#faeeda,stroke:#ba7517
    style Room fill:#faeeda,stroke:#ba7517
    style Text fill:#faeeda,stroke:#ba7517
    style Bot fill:#eeedfe,stroke:#534ab7
    style Mention fill:#faeeda,stroke:#ba7517
    style Switch fill:#f1efe8,stroke:#5f5e5a
```

### Flow 3.8 — Báo & theo dõi sự cố

```mermaid
flowchart TD
    Start(["Trong Chat riêng phòng, gõ @issue"]) --> Form["Mô tả sự cố + đính kèm ảnh"]
    Form --> Create[["Tạo báo cáo sự cố: mở"]]
    Create --> Notify["Bot post card vào chat +\nFCM push tới landlord"]
    Notify --> Track["Theo dõi trạng thái"]
    Track --> Status{"Trạng thái hiện tại?"}
    Status -->|"Mở"| Wait["Chờ landlord xử lý"]
    Status -->|"Đang xử lý"| Progress["Đang sửa — có thể\ntrao đổi thêm qua chat"]
    Status -->|"Đã xử lý"| Done["Đã xử lý xong"]

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

### Flow 4.1 — Lịch sử uy tín & consent toggle

```mermaid
flowchart TD
    Start(["Tab Tài khoản"]) --> History["Lịch sử các kỳ thuê trước:\nphòng, thời gian, thanh toán đúng hạn"]
    History --> Toggle{"Bật hiển thị công khai?"}
    Toggle -->|"Bật"| Public["Hiện trên hồ sơ Ghép bạn\ncho người khác xem"]
    Toggle -->|"Tắt"| Private["Chỉ mình tenant xem được"]
    Public --> Revoke["Có thể tắt lại/thu hồi\nbất kỳ lúc nào"]

    style Start fill:#faeeda,stroke:#ba7517
    style History fill:#faeeda,stroke:#ba7517
    style Public fill:#eaf3de,stroke:#639922
    style Private fill:#f1efe8,stroke:#5f5e5a
    style Revoke fill:#faeeda,stroke:#ba7517
```

**Nguyên tắc bắt buộc:** mặc định **Tắt** (opt-in, không phải opt-out) — im lặng không phải là đồng ý.

### Flow 4.2 — Hồ sơ cá nhân & cài đặt

```mermaid
flowchart TD
    Start(["Tab Tài khoản"]) --> Profile["Thông tin cá nhân: tên,\nsố điện thoại, ảnh đại diện"]
    Profile --> Notif["Cài đặt thông báo\n(bật/tắt theo loại: hóa đơn, chat, sự cố)"]
    Notif --> Logout["Đăng xuất"]

    style Start fill:#faeeda,stroke:#ba7517
    style Profile fill:#faeeda,stroke:#ba7517
    style Notif fill:#faeeda,stroke:#ba7517
```

### Flow 4.3 — Thông báo FCM → deep link

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
| 4 | Popup đăng nhập (SĐT + OTP) | 1 | — |
| 5 | Danh sách phòng đã lưu | 1 | Có |
| 6 | Feed ghép bạn | 2 | Không |
| 7 | Chi tiết 1 hồ sơ roommate | 2 | Không |
| 8 | Tạo/sửa hồ sơ cá nhân | 2 | Có |
| 9 | Danh sách Yêu cầu đã gửi/đã nhận | 2 | Có |
| 10 | Màn Match thành công | 2 | Có |
| 11 | Switcher chọn hợp đồng (nếu >1) | 3 | Có |
| 12 | Hub Phòng của tôi | 3 | Có |
| 13 | Xem hợp đồng | 3 | Có |
| 14 | Danh sách thành viên + phần góp | 3 | Có |
| 15 | Danh sách hóa đơn | 3 | Có |
| 16 | Chi tiết hóa đơn + thanh toán | 3 | Có |
| 17 | Property Chat riêng phòng | 3 | Có |
| 18 | Property Chat chung tòa | 3 | Có |
| 19 | Form tạo sự cố (@issue) | 3 | Có |
| 20 | Chi tiết/theo dõi sự cố | 3 | Có |
| 21 | Lịch sử uy tín + consent toggle | 4 | Có |
| 22 | Hồ sơ cá nhân / cài đặt | 4 | Có |
| 23 | Cài đặt thông báo | 4 | Có |

---
