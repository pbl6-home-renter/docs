# Rentify — UI Screen Outline (Khung sườn v0.1)

> **Trạng thái tài liệu:** Bản NHÁP KHUNG SƯỜN (Draft #1) — mới liệt kê đầy đủ màn hình + vai trò/nền tảng/điều hướng ở mức tối thiểu, **CHƯA đào sâu nội dung/bố cục/component chi tiết**. Mục tiêu bước này: hai bên rà soát xem đã liệt kê **ĐỦ** và **ĐÚNG** màn hình chưa, tên gọi/nhóm batch có hợp lý không, trước khi đào sâu từng phần.
>
> **Nguồn:** `shared_user_flow.md`, `tenant-user-flow.md`, `landlord_user_flow.md`, `admin_user_flow.md`.
>
> **Quy ước nền tảng (theo yêu cầu):** Mobile và Web **tương đương về chức năng tuyệt đối** — không nền tảng nào có tính năng mà nền tảng kia thiếu. Khác biệt CHỈ ở trình bày/bố cục/tương tác (ví dụ: bottom nav trên mobile ↔ sidebar trên web; bottom-sheet trên mobile ↔ modal/dialog trên web; camera mobile ↔ camera qua webcam browser trên web). Ở bước đào sâu, mỗi màn sẽ có 2 mô tả bố cục song song (Mobile / Web) thay vì 2 bộ màn hình riêng.
>
> **Ký hiệu trạng thái từng dòng:** 🔲 outline only · sẽ chuyển ✅ khi được đào sâu ở vòng sau.

---

## PHẦN 0 — Kiến trúc điều hướng tổng thể

### 0.1 Điều hướng chính theo vai trò

| Vai trò | Mobile — điều hướng chính | Web — điều hướng chính |
| -- | -- | -- |
| Guest / Tenant | Bottom navigation (**5 tab**): **Tìm phòng · Ghép bạn · Tin nhắn (mới) · Phòng của tôi · Tài khoản** | Top nav / responsive tương đương (có thể thu gọn còn hamburger trên màn hẹp) |
| Landlord | Bottom navigation (hoặc drawer): **Dashboard · Quản lý Phòng & BĐS · Sự cố · Chat · Cài đặt** | Sidebar cố định bên trái: cùng 5 mục, dạng console quản trị |
| Admin | **Chỉ Web** (ngoại lệ đã chốt — xem 0.3) | Sidebar cố định: **Dashboard · Người dùng · Phê duyệt BĐS · Audit Logs · Đăng xuất** |

### 0.1b Kiến trúc phân luồng trước khi đăng nhập (đã chốt)

Do Tenant và Landlord có nhu cầu pre-login hoàn toàn khác nhau (Tenant cần browse công khai; Landlord không browse gì, chỉ cần Login/Đăng ký), hệ thống phân luồng **ngay từ trước khi có JWT/role**, theo nguyên tắc: tách biệt **trải nghiệm & UX**, nhưng **không tách hạ tầng** (1 codebase, 1 app, 1 web) để phù hợp phạm vi đồ án:

* **Web:** `rentify.vn` (domain gốc) = mặc định trải nghiệm Guest/Tenant (Guest Home + danh sách phòng). Có mục **"Kênh Chủ trọ"** trên header/footer dẫn tới path riêng `rentify.vn/chu-tro` — trang landing giới thiệu dịch vụ cho Chủ trọ + Login/Đăng ký Landlord riêng biệt. Admin dùng route ẩn, không xuất hiện ở menu công khai nào.
* **Mobile:** Dùng **chung 1 app**. Lần đầu mở app khi **chưa có tài khoản/token**, hiển thị màn hỏi vai trò: **"Tìm phòng trọ"** hoặc **"Tôi là Chủ trọ, muốn đăng tin"** → rẽ nhánh tương ứng (Guest Home browsing, hoặc thẳng Login/Register Landlord, bỏ qua Guest Home). Lựa chọn chỉ ảnh hưởng giai đoạn pre-login, được nhớ lại (persist local), chỉ hỏi lại khi logout về guest gốc. Sau khi đăng nhập, điều hướng luôn theo `User.role` từ JWT, không liên quan lựa chọn ban đầu.

### 0.3 Ngoại lệ nền tảng: Admin chỉ cần Web
Đã chốt: vì hệ thống chỉ có **duy nhất 1 tài khoản Admin**, back-office/admin portal theo thông lệ chuyên nghiệp luôn là web-only — không cần đầu tư bản Mobile tương đương cho Admin. Đây là ngoại lệ **duy nhất** đối với nguyên tắc "Mobile/Web tương đương 100% chức năng".

### 0.2 Nguyên tắc xuyên suốt cần nhớ khi đào sâu (rule engine)

* Guest-first cho khám phá (xem phòng, xem feed ghép bạn) — không login. Chỉ gate login khi có hành động định danh.
* Role bất biến — không có màn hình "đổi vai trò" ở bất kỳ đâu.
* Tài khoản Landlord bị khóa → toàn bộ BĐS ẩn khỏi tìm kiếm công khai + chặn cổng quản lý; Tenant bị khóa → vẫn xem/thanh toán HĐ hiện tại nhưng chặn gia hạn/thuê mới.
* Thuê ngắn hạn tính theo ngày (mốc 00:00), không tính giờ; không có màn khai báo tạm trú.
* Mọi hóa đơn = Tiền phòng + nhóm **Dịch vụ** (điện/nước/wifi/rác/máy giặt gộp chung); quy về theo tháng; 2 kênh thanh toán song song (VietQR online / tiền mặt xác nhận thủ công); **mọi thành viên trong phòng** đều thanh toán được.
* Camera công tơ: **Chỉ Landlord** thực hiện chốt số điện nước (chụp trực tiếp bằng Camera **hoặc** tải ảnh từ thư viện). **Tenant không có bất kỳ thao tác/màn hình nào liên quan đến việc chụp/chốt số công tơ** — đây là nghiệp vụ độc quyền của Landlord.
* Chat: **Property Chat (chat nhóm theo phòng, gồm mọi thành viên)** chỉ được tạo và tồn tại **sau khi hợp đồng chuyển trạng thái Active**. **Trước khi có hợp đồng active**, Tenant/Guest vẫn có thể liên hệ Landlord qua **Chat riêng 1-1 trong app** (không phải chỉ hiển thị SĐT tĩnh) — đây là kênh chat cá nhân giữa 1 người quan tâm và Landlord của BĐS đó, tách biệt hoàn toàn với Property Chat nhóm (sẽ được tạo mới, độc lập, khi HĐ kích hoạt). SĐT vẫn hiển thị ở Chi tiết phòng như một kênh liên hệ bổ sung, không phải kênh duy nhất.
* Không có tính năng ký điện tử — chỉ wet-sign giấy + upload file đã ký lưu trữ.
* BĐS mới tạo luôn ở trạng thái chờ Admin duyệt (cần ảnh sổ đỏ/giấy tờ đất); phòng chỉ được public/tạo HĐ sau khi BĐS được duyệt.

---

## PHẦN A — Shared / Auth / Guest (dùng chung mọi vai trò) ✅✅ TOÀN BỘ ĐÃ KHÓA

| ID | Tên màn hình | Vai trò áp dụng | Nền tảng | Login? | Trạng thái |
| -- | -- | -- | -- | -- | -- |
| SH-01 | Splash / App Start | Mọi người | Mobile only (Web bỏ qua) | Không | 🔲 |
| SH-01b | **[MỚI]** Màn chọn vai trò lúc chưa có tài khoản ("Tìm phòng trọ" / "Tôi là Chủ trọ") | Guest chưa từng chọn | Mobile only | Không | 🔲 |
| SH-02 | Trang khám phá công khai (Guest Home) — **gộp làm landing**, vào `rentify.vn` là thấy ngay thanh tìm kiếm + danh sách phòng, không có trang giới thiệu riêng đứng trước | Guest/Tenant | Mobile & Web | Không | 🔲 |
| SH-02b | Trang landing "Kênh Chủ trọ" (`rentify.vn/chu-tro`) — giới thiệu dịch vụ + Login/Đăng ký Landlord riêng *(giữ nguyên theo quyết định #6, KHÔNG bị ảnh hưởng bởi việc bỏ landing của SH-02 — 2 vấn đề khác nhau: SH-02 là landing chung cho Tenant, SH-02b là landing riêng chỉ dành cho Landlord)* | Guest → Landlord | Web (Mobile: đi thẳng từ SH-01b, không cần landing riêng) | Không | 🔲 |
| SH-03 | Đăng nhập (Email + Mật khẩu) — dùng chung form, khác điểm vào | Mọi vai trò | Mobile & Web | — | 🔲 |
| SH-03b | **[MỚI]** Quên mật khẩu — nhập Email → gửi link đặt lại mật khẩu | Mọi vai trò | Mobile & Web | — | 🔲 |
| SH-03c | **[MỚI]** Đặt lại mật khẩu mới (mở từ link email, nhập mật khẩu mới + xác nhận) | Mọi vai trò | Mobile & Web | — | 🔲 |
| SH-04a | **[MỚI]** Đăng ký tài khoản Tenant (Email, Mật khẩu, Họ tên, SĐT) | Guest → Tenant | Mobile & Web | — | 🔲 |
| SH-04b | **[MỚI]** Đăng ký tài khoản Landlord | Guest → Landlord | Mobile & Web (qua SH-02b) | — | 🔲 |
| SH-05 | Báo lỗi đăng nhập/đăng ký (trạng thái inline của SH-03/04, không phải màn riêng) | Mọi vai trò | Mobile & Web | — | 🔲 |
| SH-06 | Màn chặn: Tài khoản Landlord bị khóa (toàn bộ BĐS tạm ẩn) | Landlord | Mobile & Web | Có (bị chặn) | 🔲 |
| SH-07 | Màn giới hạn quyền: Tenant bị khóa (chỉ xem & thanh toán HĐ hiện tại; **khóa luôn tab Ghép bạn và tab Tìm phòng** — không thể tìm phòng mới dưới bất kỳ hình thức nào, kể cả qua ghép bạn) | Tenant | Mobile & Web | Có (hạn chế) | 🔲 |
| SH-08 | Xác nhận Đăng xuất + màn quay về Guest | Mọi vai trò | Mobile & Web | Có | 🔲 |
| SH-09 | Màn lỗi chung (network error / 403 / 404) | Mọi vai trò | Mobile & Web | — | 🔲 |

> **Ghi chú:** Admin không có SH-04 (không có đăng ký) — tài khoản Admin duy nhất được seed sẵn trong hệ thống, không qua UI đăng ký. Admin dùng chung màn SH-03 (Login) qua route ẩn riêng, không qua SH-01/SH-02.

---

## PHẦN B — Tenant (Khách thuê) ✅✅ TOÀN BỘ PHẦN B ĐÃ KHÓA

### B.1 Batch 1 — Khám phá (Guest-first) ✅ ĐÃ KHÓA

| ID | Tên màn hình | Login? | Trạng thái |
| -- | -- | -- | -- |
| TN-01 | Bộ lọc tìm phòng (giá/diện tích/tiện nghi/khoảng cách/**khu vực** — tìm theo khu vực là 1 tiêu chí lọc, KHÔNG phải bản đồ) | Không | 🔲 |
| TN-02 | Danh sách kết quả phòng (dạng thẻ/card) — **chỉ dạng List, chưa làm Bản đồ/Map view (kế hoạch tương lai, ngoài phạm vi hiện tại)** | Không | 🔲 |
| TN-03 | Chi tiết phòng (gallery, giá, tiện nghi, badge ràng buộc, **địa chỉ đầy đủ hiển thị ngay từ đầu**, SĐT landlord) | Không | 🔲 |
| TN-04 | Danh sách phòng đã lưu (yêu thích) | Có | 🔲 |

### B.1b — Tin nhắn (Tab mới, Inbox hợp nhất — quyết định #14) ✅ ĐÃ KHÓA

> **Thay đổi kiến trúc quan trọng:** Chat không còn nằm rải rác (1 phần dưới Chi tiết phòng, 1 phần dưới Hub "Phòng của tôi") mà **gộp thành 1 Inbox duy nhất**, sống ở **tab riêng cấp cao nhất**, ngang hàng Tìm phòng/Ghép bạn/Phòng của tôi/Tài khoản (→ nav Tenant nay là **5 tab**, xem 0.1). Inbox chứa **3 loại thread**: (1) Chat riêng 1-1 với Landlord (pre-contract, gắn theo Landlord), (2) Property Chat nhóm (post-contract, gắn theo phòng), (3) **Chat Match Roommate** (peer-to-peer giữa 2 tenant đã match — mới thêm, thay thế hoàn toàn việc lộ SĐT/Zalo) — phân biệt bằng nhãn/icon trong danh sách, không tách nhiều màn riêng ở cấp Inbox. Toàn bộ tab yêu cầu đăng nhập.

| ID | Tên màn hình | Login? | Trạng thái |
| -- | -- | -- | -- |
| TN-MSG-01 | **Inbox tổng** — danh sách toàn bộ thread chat (1-1 Landlord + Nhóm phòng + Match Roommate), sort theo tin nhắn mới nhất, badge phân loại | Có | 🔲 |
| TN-MSG-02 | Chi tiết Chat riêng 1-1 với Landlord — **gắn theo Landlord** (hỏi nhiều phòng của cùng 1 landlord vẫn chung 1 thread), khởi tạo từ nút "Liên hệ" ở TN-03 (gate login) | Có | 🔲 |
| TN-MSG-03 | Chi tiết Property Chat **nhóm** theo phòng — chỉ tồn tại sau khi HĐ Active, kênh mới hoàn toàn độc lập với TN-MSG-02 | Có | 🔲 |
| TN-MSG-04 | Property Chat chung tòa (multi-room, chỉ text/ảnh/file + mention) | Có | 🔲 |
| TN-MSG-05 | **[MỚI]** Chat Match Roommate (peer-to-peer, giữa 2 tenant đã match thành công) — khởi tạo tự động từ TN-09, **thay thế** bước lộ SĐT/Zalo trong flow gốc | Có | 🔲 |

> **Note vào/ra:** Từ Hub "Phòng của tôi" (TN-11), mục "Chat" sẽ **deep-link thẳng vào TN-MSG-03/04** tương ứng — Hub chỉ là lối tắt, không sở hữu màn chat.

### B.2 Batch 2 — Ghép bạn (Roommate matching) ✅ ĐÃ KHÓA

| ID | Tên màn hình | Login? | Trạng thái |
| -- | -- | -- | -- |
| TN-05 | Feed ghép bạn (cuộn dọc thường, **không phải swipe kiểu Tinder**) | Không (xem) | 🔲 |
| TN-06 | Chi tiết 1 hồ sơ roommate | Không (xem) | 🔲 |
| TN-07 | Tạo/Sửa hồ sơ cá nhân ghép bạn + **toggle "Tìm bạn ở ghép": Bật/Tắt** hiển thị hồ sơ trên Feed | Có | 🔲 |
| TN-08 | Danh sách Yêu cầu Đã gửi / Đã nhận (2 tab) — **Chấp nhận/Từ chối thao tác ngay trên item của list** (không cần vào chi tiết) | Có | 🔲 |
| TN-09 | Màn Match thành công — **KHÔNG còn lộ SĐT/Zalo**, thay bằng nút "Nhắn tin ngay" → mở thẳng thread chat trong app (xem TN-MSG-05) | Có | 🔲 |

### B.3 Batch 3 — "Phòng của tôi" (Hub sau khi có hợp đồng active) ✅ ĐÃ KHÓA

| ID | Tên màn hình | Login? | Trạng thái |
| -- | -- | -- | -- |
| TN-10 | **Danh sách hợp đồng** — cùng 1 màn, có **bộ lọc/tab: "Đang hiệu lực" / "Đã kết thúc"**. **Chỉ hiển thị màn này khi Tenant có ≥2 hợp đồng** (bất kể trạng thái); nếu chỉ có đúng 1 HĐ (dù active hay đã kết thúc) → **bỏ qua, vào thẳng TN-11 (Hub)** | Có | 🔲 |
| TN-11 | Hub "Phòng của tôi" — **nội dung Hub khác nhau theo trạng thái HĐ**: xem chi tiết bên dưới | Có | 🔲 |
| TN-12 | Xem hợp đồng (read-only; file đã ký hoặc ghi chú "chờ upload") | Có | 🔲 |
| TN-13 | Danh sách thành viên phòng (read-only, **chỉ hiện Họ tên + avatar, KHÔNG hiện SĐT** của thành viên khác) | Có | 🔲 |
| TN-14 | Danh sách hóa đơn theo tháng | Có | 🔲 |
| TN-15 | Chi tiết hóa đơn (breakdown Tiền phòng + Dịch vụ, trạng thái thu 1 phần/đủ) | Có | 🔲 |
| TN-16 | Màn thanh toán — chọn kênh (VietQR / Tiền mặt) | Có | 🔲 |
| — | ~~TN-17/18 Property Chat~~ → đã chuyển sang **TN-MSG-03/04** (xem B.1b). Hub chỉ chứa 1 nút "Chat" deep-link sang đó. | Có | ✅ đã gộp |
| TN-19 | Form tạo báo cáo sự cố (mô tả + ảnh — **Camera HOẶC thư viện, không giới hạn** như quy định ảnh công tơ, vì đó là quy định RIÊNG cho ảnh chốt số điện nước) | Có | 🔲 |
| TN-20a | **[MỚI]** Danh sách sự cố của phòng (list toàn bộ sự cố đã báo — cũ & mới, trạng thái từng cái) — **nằm bên trong Hub (TN-11) của phòng đang mở, KHÔNG phải tab riêng cấp cao nhất**; chỉ hiện sự cố của đúng phòng/HĐ đang xem Hub đó | Có | 🔲 |
| TN-20b | Chi tiết 1 sự cố — **hiển thị dạng Popup/Modal nổi lên khi bấm vào 1 item trong TN-20a** (không điều hướng sang trang/màn riêng biệt), theo dõi trạng thái (Mở → Đang xử lý → Hoàn thành) **+ khung trao đổi/bình luận tích hợp ngay trong popup** (self-contained, không bắt buộc phải nhảy qua Property Chat để bàn thêm) | Có | 🔲 |

> **Chi tiết Hub theo trạng thái HĐ (trả lời câu hỏi #1):**
> * **HĐ Đang hiệu lực (Active):** Hub đầy đủ — Xem HĐ, Thành viên, Hóa đơn (xem + thanh toán), Sự cố (xem + **tạo mới** được), Chat (deep-link tới thread đang hoạt động).
> * **HĐ Đã kết thúc (cựu tenant):** Hub rút gọn, toàn bộ **read-only** — Xem HĐ (lịch sử), Thành viên (danh sách cũ), Hóa đơn (lịch sử, đã thanh toán/thanh lý — **không có nút thanh toán** vì đã xong), Sự cố (chỉ xem lịch sử — **KHÔNG cho tạo mới**), Chat (thread cũ chuyển **read-only/archive**, theo đúng nghiệp vụ Landlord Sub-Flow 7 — khách mới không thấy, cựu tenant chỉ xem lại).

### B.4 Batch 4 — Tài khoản ✅ ĐÃ KHÓA

| ID | Tên màn hình | Login? | Trạng thái |
| -- | -- | -- | -- |
| TN-21 | Hồ sơ cá nhân (tên, ảnh đại diện — sửa được; **SĐT & Email: read-only, KHÔNG cho đổi** vì SĐT là cơ chế auto-link hợp đồng) + nút "Đổi mật khẩu" | Có | 🔲 |
| TN-22 | Cài đặt thông báo — **1 toggle Bật/Tắt duy nhất** (không tách nhỏ theo loại) | Có | 🔲 |

> **Đã bỏ khỏi phạm vi:** Màn "Lịch sử uy tín" (nhắc trong shared_user_flow 1.3 nhưng không có sub-flow chi tiết, không có cơ chế Landlord đánh giá Tenant ở đâu trong hệ thống) — **không triển khai**. Màn "Consent" (quản lý các đồng ý đã cấp) cũng tạm gộp bỏ theo cùng quyết định, vì không có mô tả nghiệp vụ cụ thể — nếu về sau cần, sẽ bổ sung riêng khi có yêu cầu rõ ràng.

---

## PHẦN C — Landlord (Chủ trọ) ✅✅ TOÀN BỘ PHẦN C ĐÃ KHÓA

### C.1 Dashboard ✅ ĐÃ KHÓA

| ID | Tên màn hình | Trạng thái |
| -- | -- | -- |
| LL-01 | Landlord Dashboard — Doanh thu (**có biểu đồ theo tháng**, dạng line/bar chart), Công nợ (số liệu), **Room Map tổng quan dạng sơ đồ trực quan** (mỗi ô = 1 phòng, màu theo trạng thái: Trống/Đang thuê/Chờ dọn), gộp mọi tòa nhà | 🔲 |

> **Empty state (lần đầu vào, chưa có tòa nhà nào — đã chốt):** Thay vì hiện Dashboard đầy đủ với số 0 mọi nơi, hiện **card CTA lớn nổi bật ở giữa màn hình**: *"Chào mừng đến Rentify! Bắt đầu bằng cách thêm Tòa nhà/Dãy trọ đầu tiên"* + nút "Thêm Tòa nhà" → LL-03 (bước 1/3 của wizard). Doanh thu/Công nợ/Room Map vẫn hiện phía dưới nhưng ở dạng nhạt màu "chưa có dữ liệu", không phải trọng tâm. Dashboard đầy đủ chỉ hiện sau khi có ≥1 tòa nhà được Admin duyệt.

### C.2 Quản lý BĐS & Phòng trọ ✅ ĐÃ KHÓA

| ID | Tên màn hình | Trạng thái |
| -- | -- | -- |
| LL-02 | Danh sách Tòa nhà/Dãy trọ | 🔲 |
| LL-03 | **[Bước 1/3]** Form Thêm Dãy trọ/Tòa nhà (tên, địa chỉ, số tầng) — **màn riêng biệt, KHÔNG gộp chung 1 form** với LL-04/LL-05 (đi theo dạng wizard nhiều bước, mỗi bước 1 màn) | 🔲 |
| LL-04 | **[Bước 2/3]** Upload bằng chứng sở hữu (sổ đỏ/giấy tờ đất/ủy quyền) — **cho phép upload NHIỀU ảnh** (vd sổ đỏ 2 mặt) và **cả 2 quyền: Camera chụp trực tiếp + Upload từ thư viện** | 🔲 |
| LL-05 | **[Bước 3/3]** Cấu hình đơn giá điện nước mặc định của Tòa nhà | 🔲 |
| LL-06 | Chi tiết Tòa nhà — trạng thái duyệt (Chờ duyệt / Đã duyệt / Bị từ chối + lý do) | 🔲 |
| LL-06b | **[MỚI]** Cấu hình Tài khoản nhận tiền / VietQR của Tòa nhà — STK, Tên ngân hàng, Chủ tài khoản; **chỉ khả dụng sau khi Tòa nhà đã được Admin duyệt**; dùng để sinh mã VietQR cho mọi hóa đơn của các phòng trong tòa này (LL-22) | 🔲 |
| LL-07 | Danh sách Phòng trong 1 Tòa nhà — **dùng chung 1 kiểu hiển thị Room Map trực quan như LL-01**, chỉ lọc riêng cho 1 tòa nhà này | 🔲 |
| LL-08 | Form Thêm Phòng mới (số phòng, diện tích, giá, quy tắc tùy chọn giới tính/tiện nghi) — **chỉ khả dụng sau khi Tòa nhà đã được Admin duyệt** (đúng nghiệp vụ gốc) | 🔲 |
| LL-09 | Chi tiết 1 Phòng (card tổng quan + trạng thái) | 🔲 |
| LL-10 | Menu Tiện ích Phòng (entry: Thành viên/Chốt số/Hóa đơn/Chat/Thanh lý) — chỉ hiện khi có HĐ active | 🔲 |

### C.3 Hợp đồng thuê & Check-in ✅ ĐÃ KHÓA

| ID | Tên màn hình | Trạng thái |
| -- | -- | -- |
| LL-11 | Form Tạo Hợp đồng — nhập thông tin **1 người đại diện đứng tên HĐ** (Họ tên, SĐT, CCCD, Địa chỉ, Cọc, Tiền thuê, Ngày bắt đầu & Thời hạn). **Các thành viên ở ghép khác được thêm SAU, qua LL-16** (kể cả nếu dọn vào cùng ngày) | 🔲 |
| LL-12 | Chọn mẫu hợp đồng — **chỉ chọn trong các mẫu do hệ thống dựng sẵn, cố định** (không có tính năng Landlord tự tạo/quản lý mẫu riêng) / hoặc "Bỏ qua, dùng mẫu chuẩn" | 🔲 |
| LL-13 | Xuất file mẫu HĐ PDF điền sẵn (để in ký tay) — *đây là 1 action/loading state, không phải màn hình độc lập* | 🔲 |
| LL-14 | Upload file HĐ đã ký (ảnh/doc/pdf) → kích hoạt HĐ | 🔲 |

### C.4 Quản lý thành viên phòng ✅ ĐÃ KHÓA

| ID | Tên màn hình | Trạng thái |
| -- | -- | -- |
| LL-15 | Danh sách thành viên phòng (từ Menu Tiện ích) | 🔲 |
| LL-16 | Form Thêm thành viên mới (họ tên, SĐT, CCCD) — dùng để bổ sung thành viên ở ghép, kể cả ngay lúc mới tạo HĐ lẫn về sau | 🔲 |
| LL-17 | Xác nhận Xóa thành viên rời phòng — **KHÔNG có khái niệm "người đại diện HĐ" đặc biệt, mọi thành viên ngang hàng**, xóa ai cũng xử lý giống nhau (không cần chỉ định lại đại diện mới) | 🔲 |

### C.5 Chốt số điện/nước & Lập hóa đơn ✅ ĐÃ KHÓA

| ID | Tên màn hình | Trạng thái |
| -- | -- | -- |
| LL-18 | Chốt số điện nước (**đơn lẻ**, entry từ Chi tiết Phòng LL-09/10) — chọn nguồn ảnh (Camera / Upload thư viện), xong thì dừng | 🔲 |
| LL-18b | **[MỚI]** Nút/Entry "Chốt số hàng loạt" — đặt ở LL-07 (Danh sách Phòng cấp Tòa nhà), khởi động luồng chốt liên tục nhiều phòng | 🔲 |
| LL-18c | **[MỚI]** Màn luồng Chốt hàng loạt — hiện tiến trình ("Phòng 3/20"), tái sử dụng LL-19/LL-20 cho từng phòng, có nút Next/Bỏ qua (skip phòng trống hoặc phòng lỗi), tự động chuyển phòng kế tiếp | 🔲 |
| LL-18d | **[MỚI]** Màn tổng kết sau khi Chốt hàng loạt — "Đã chốt xong 18/20 phòng, còn 2 phòng chưa chốt" + danh sách phòng còn thiếu để xử lý riêng | 🔲 |
| LL-19 | Camera chụp công tơ (live) — dùng chung cho cả 2 luồng (đơn lẻ & hàng loạt) | 🔲 |
| LL-20 | Kết quả OCR — xác nhận/sửa tay chỉ số — dùng chung cho cả 2 luồng. **Có trạng thái riêng khi OCR thất bại hoàn toàn:** "Không nhận diện được, vui lòng nhập tay" — hiện ô nhập số trống, không đưa số gợi ý sai | 🔲 |
| LL-21 | Xem trước & chỉnh sửa Hóa đơn tháng (Tiền phòng + Dịch vụ breakdown) — *trước khi phát hành lần đầu* | 🔲 |
| LL-21a | **[MỚI — bổ sung sau khi khóa]** Danh sách hóa đơn **đã phát hành** của 1 phòng (theo tháng) — vào từ Menu Tiện ích → Hóa đơn, hiện trạng thái từng hóa đơn (Chưa TT/Quá hạn/1 phần/Đã đủ/Đã hủy) | 🔲 |
| LL-21b | **[MỚI — bổ sung sau khi khóa]** Sửa hóa đơn đã phát hành (tái sử dụng UI LL-21) + nút Hủy hóa đơn (dialog xác nhận) — **CHỈ khả dụng khi hóa đơn CHƯA có bất kỳ khoản thanh toán nào**; nếu đã có Đã thu (1 phần/đủ) → chỉ xem, ẩn nút sửa/hủy. Sửa xong → tự sinh lại mã VietQR mới + gửi card "Hóa đơn đã cập nhật" vào Property Chat phòng | 🔲 |
| LL-22 | Phát hành Hóa đơn (sinh VietQR động, gửi card vào Chat phòng) | 🔲 |
| LL-23 | Xác nhận thu tiền mặt — hiện Tổng HĐ/Đã thu/Còn lại; **nút mặc định "Xác nhận đã thu ĐỦ"** (1-tap cho case phổ biến) + **tùy chọn phụ "Nhập số tiền vừa thu"** (input số → cộng dồn vào Đã thu, hệ thống tự tính lại Còn lại & tự đổi trạng thái Thanh toán 1 phần/Đã đủ) | 🔲 |

### C.6 Cấu hình chu kỳ & quét nợ ✅ ĐÃ KHÓA

| ID | Tên màn hình | Trạng thái |
| -- | -- | -- |
| LL-24 | Cài đặt Chu kỳ Hóa đơn & Quét nợ (chọn cấp: Profile/Building/Room) | 🔲 |
| LL-25 | Form cấu hình hạn thanh toán + ngày nhắc nhở | 🔲 |
| LL-25b | **[MỚI]** Danh sách công nợ (đơn giản) — list các hóa đơn Quá hạn: Phòng, Số tiền còn thiếu, Số ngày quá hạn. Truy cập từ mục "Công nợ" trên Dashboard (LL-01). Khi quá hạn: hệ thống **tự động đánh dấu "Quá hạn" + gửi thông báo nhắc** cho Tenant, đồng thời hiện vào list này cho Landlord theo dõi — **không làm thêm hành động phức tạp** (không tự động phạt/tính lãi...) | 🔲 |

### C.7 Sự cố (Tab riêng) ✅ ĐÃ KHÓA

| ID | Tên màn hình | Trạng thái |
| -- | -- | -- |
| LL-26 | Tab Sự cố — danh sách tập trung toàn bộ tòa nhà (filter theo trạng thái). **Mỗi item PHẢI hiển thị rõ nhãn "Tòa nhà — Số phòng"** ngay trên card (issue tự động gắn `room_id`/`building_id` từ ngữ cảnh Hub lúc Tenant tạo báo cáo — Tenant không tự chọn phòng) | 🔲 |
| LL-27 | Chi tiết sự cố — **giữ dạng Popup/Modal** (tái sử dụng pattern như TN-20b) nhưng **đầy đủ hành động cho Landlord**: header hiện "Tòa nhà — Phòng — Người báo cáo", cập nhật trạng thái (Đang xử lý/Hoàn thành/Hủy), và **nút "Xem trong Chat phòng"** deep-link thẳng tới LL-35 của đúng phòng đó (thay vì khung trao đổi nhúng sẵn như bên Tenant) | 🔲 |
| LL-28 | Landlord tự tạo sự cố (từ Chi tiết Phòng — `room_id` cũng tự động gắn theo ngữ cảnh phòng đang mở) | 🔲 |

### C.8 Checkout / Thanh lý phòng ✅ ĐÃ KHÓA

| ID | Tên màn hình | Trạng thái |
| -- | -- | -- |
| LL-29 | Menu Tiện ích: Thanh lý phòng — Chốt số điện nước lần cuối | 🔲 |
| LL-30 | Hóa đơn quyết toán cuối — **Landlord tự nhập số tiền phòng quyết toán** (không bắt buộc theo công thức chia ngày cứng nhắc, vì thực tế thường thỏa thuận riêng) — hệ thống có thể **gợi ý** con số tính theo ngày ở thực tế để tham khảo, nhưng Landlord toàn quyền sửa lại; điện nước vẫn tính tự động theo chỉ số lần cuối vừa chốt (LL-29) | 🔲 |
| LL-31 | Quyết toán tiền cọc — **1 ô nhập tổng số tiền khấu trừ + 1 ô lý do chung** (không tách nhiều hạng mục chi tiết) → tự tính tiền cọc hoàn lại = Cọc − Khấu trừ − (Hóa đơn quyết toán chưa thanh toán, nếu có) | 🔲 |
| LL-32 | Xác nhận hoàn tất thanh lý & nhận bàn giao | 🔲 |
| LL-33 | Trạng thái phòng "Chờ dọn dẹp" + nút "Xác nhận phòng sẵn sàng" | 🔲 |

### C.9 Chat ✅ ĐÃ KHÓA

> **Đã chốt: hợp nhất giống Tenant** — 1 tab "Chat" duy nhất (đã có sẵn trong nav Landlord) lưu trữ TOÀN BỘ thread, đồng thời mỗi phòng vẫn có Property Chat nhóm riêng (truy cập qua Menu Tiện ích Phòng, deep-link vào đúng thread trong Inbox này).

| ID | Tên màn hình | Trạng thái |
| -- | -- | -- |
| LL-CHAT-01 | **Inbox tổng (tab Chat)** — danh sách toàn bộ thread: Chat riêng 1-1 (khách tiềm năng, pre-contract) + Property Chat nhóm theo từng phòng (post-contract) + Chat chung toàn tòa — phân biệt bằng nhãn/icon, gộp thay cho LL-34/34b cũ | 🔲 |
| LL-CHAT-02 | Chi tiết 1 thread chat (dùng chung UI cho cả 3 loại, nội dung khác nhau theo loại) — gộp thay cho LL-35/35b cũ | 🔲 |

> **Lưu ý điều hướng:** Từ Menu Tiện ích Phòng (LL-10), mục "Chat" deep-link thẳng vào đúng Property Chat nhóm của phòng đó trong LL-CHAT-02 — không có màn chat riêng nằm trong cây điều hướng của Menu Tiện ích Phòng (giống pattern Hub bên Tenant).

### C.10 Cài đặt ✅ ĐÃ KHÓA

| ID | Tên màn hình | Trạng thái |
| -- | -- | -- |
| LL-36 | Hồ sơ cá nhân Landlord (tên, SĐT, ảnh đại diện — **KHÔNG chứa STK ngân hàng**, việc đó đã chuyển sang LL-06b cấp Tòa nhà) | 🔲 |
| LL-37 | Cài đặt thông báo — **1 toggle Bật/Tắt duy nhất** (giống Tenant, không tách nhỏ theo loại) | 🔲 |

> ✅ Đã giải quyết: LL-12 (mẫu HĐ hệ thống dựng sẵn — quyết định #38), Room Map (sơ đồ trực quan — quyết định #31).
>
> ❓ **Còn treo duy nhất:** Có cần màn "Báo cáo/Thống kê" chuyên sâu (doanh thu theo tháng/theo tòa, xuất Excel...) không, hay Dashboard tổng quan (đã có biểu đồ — quyết định #32) là đủ cho phạm vi đồ án?

---

## PHẦN D — Admin ✅✅ TOÀN BỘ ĐÃ KHÓA

| ID | Tên màn hình | Trạng thái |
| -- | -- | -- |
| AD-01 | Admin Dashboard — **chỉ số liệu/card tổng quan** (tổng Landlord/Tenant, số BĐS chờ duyệt, hoạt động gần đây), **KHÔNG cần biểu đồ** (khác Landlord Dashboard) | 🔲 |
| AD-02 | Danh sách Người dùng (filter theo Role/Trạng thái, tìm kiếm) | 🔲 |
| AD-03 | Chi tiết hồ sơ Người dùng | 🔲 |
| AD-04 | Hành động Khóa tài khoản (xác nhận) — **bắt buộc nhập lý do khóa** (lưu vào Audit Log) | 🔲 |
| AD-05 | Hành động Mở khóa tài khoản (xác nhận + chọn khôi phục/hủy HĐ nếu có) | 🔲 |
| AD-06 | Danh sách BĐS chờ duyệt (Phê duyệt Bất động sản) | 🔲 |
| AD-07 | Chi tiết BĐS chờ duyệt (xem thông tin + ảnh giấy tờ pháp lý) | 🔲 |
| AD-08 | Form Từ chối BĐS (nhập lý do cụ thể, bắt buộc) | 🔲 |
| AD-09 | Audit Logs — danh sách nhật ký hệ thống (filter loại sự kiện/thời gian/đối tượng) | 🔲 |
| AD-10 | Chi tiết 1 bản ghi Audit Log (before/after) — **hiển thị dạng Popup/Modal**, nhất quán với pattern đã dùng ở LL-27/TN-20b | 🔲 |

> ✅ Đã giải quyết: Admin chỉ cần Web, không cần bản Mobile (quyết định #7, Phần 0.3).

---

## PHẦN E — Bảng tổng hợp toàn bộ màn hình (Master Screen Count)

| Nhóm | Số màn hình (outline) |
| -- | -- |
| Shared / Auth / Guest | 13 |
| Tenant | 26 |
| Landlord | 44 |
| Admin | 10 |
| **Tổng** | **93** |

*(Số liệu cuối cùng sau khi đã hoàn tất thảo luận toàn bộ 4 Phần A–D — không còn thay đổi trừ khi phát sinh yêu cầu mới.)*

---

## PHẦN F — Đề xuất bổ sung (đã rà soát lại, cập nhật trạng thái cuối)

| # | Đề xuất | Trạng thái cuối |
| -- | -- | -- |
| 1 | Empty states cho từng danh sách | Xử lý inline trong từng màn khi cần (không cần màn riêng) |
| 2 | Trung tâm thông báo (xem lại lịch sử thông báo) | ❌ **Bỏ qua** — ngoài phạm vi |
| 3 | Onboarding lần đầu (giới thiệu tính năng) | ❌ Không làm — không có landing/onboarding riêng (quyết định #6, #10) |
| 4 | Tìm kiếm/lọc Admin | ✅ Giữ nguyên, đã có sẵn trong AD-02/AD-09 |
| 5 | Xuất báo cáo Excel/PDF cho Landlord | ❌ Không làm — quyết định #51 |
| 6 | Đa ngôn ngữ (VI/EN) | ❌ **Bỏ qua** — chỉ tiếng Việt |
| 7 | Trang landing/marketing riêng | ❌ Không làm — quyết định #6, #10 |

---

## ✅✅✅ TOÀN BỘ TÀI LIỆU ĐÃ HOÀN TẤT THẢO LUẬN (93 màn hình, 4 Phần A–D + Phần E/F đã chốt)

---

## PHẦN G — Nhật ký quyết định đã chốt (Decision Log)

> Mục này ghi lại các quyết định đã được bạn xác nhận, cập nhật liên tục trong suốt quá trình thảo luận. Phần nào đã "chốt" sẽ được đánh dấu ✅ và không thay đổi trừ khi bạn yêu cầu mở lại.

| # | Chủ đề | Quyết định đã chốt | Trạng thái |
| -- | -- | -- | -- |
| 1 | Chốt số điện nước | Chỉ Landlord thực hiện (Camera hoặc Upload thư viện). Tenant không có vai trò/màn hình nào trong việc chụp/chốt số công tơ. | ✅ |
| 2 | Property Chat vs Chat riêng | Property Chat **nhóm** theo phòng chỉ tạo mới sau khi HĐ Active. **Trước đó**, Tenant/Guest liên hệ Landlord qua **Chat riêng 1-1 trong app** (không chỉ qua SĐT tĩnh). 2 loại chat độc lập nhau, không liên thông dữ liệu. | ✅ |
| 3 | Tổ chức file | Gộp theo batch hợp lý trong 1 tài liệu duy nhất (không tách 4 file riêng) | ✅ |
| 4 | Phạm vi nháp đầu tiên | Làm khung sườn toàn bộ màn hình trước, đào sâu sau | ✅ |
| 5 | Mobile vs Web | Tương đương 100% chức năng, chỉ khác bố cục/trình bày theo từng nền tảng | ✅ |
| 6 | Phân luồng pre-login | Web: tách theo path (`/` = Tenant mặc định, `/chu-tro` = Landlord). Mobile: 1 app chung, có màn chọn vai trò lúc chưa có tài khoản (SH-01b), lựa chọn chỉ ảnh hưởng pre-login, persist local. | ✅ |
| 7 | Admin nền tảng | Ngoại lệ: Admin CHỈ Web, không cần bản Mobile | ✅ |
| 8 | Đăng ký tài khoản | Tách riêng SH-04a (Tenant) và SH-04b (Landlord); Admin không có màn đăng ký (seed sẵn) | ✅ |
| 9 | SH-01 Splash | Giữ trong phạm vi thiết kế (mobile only, Web bỏ qua) | ✅ |
| 10 | SH-02 Landing Tenant | KHÔNG cần trang giới thiệu riêng — gộp landing = thẳng danh sách phòng/bộ lọc | ✅ |
| 11 | Quên mật khẩu | CÓ — thêm SH-03b (nhập email) và SH-03c (đặt mật khẩu mới) | ✅ |
| 12 | SH-05 Báo lỗi login | Gộp thành trạng thái inline của SH-03, không tách màn riêng | ✅ |
| 13 | SH-07 Tenant bị khóa | Khóa luôn cả tab Ghép bạn (không chỉ tab Tìm phòng) — vì mục đích cuối của ghép bạn cũng là tìm phòng mới | ✅ |
| 14 | Bản đồ (Map view) | KHÔNG làm ở phạm vi hiện tại — chỉ List view. Map là kế hoạch tương lai, ghi chú lại nhưng không thiết kế UI | ✅ |
| 15 | Tìm theo khu vực | Là 1 tiêu chí trong Bộ lọc (TN-01), không phải bản đồ | ✅ |
| 16 | Địa chỉ phòng (TN-03) | Hiển thị đầy đủ ngay từ đầu, không ẩn bớt | ✅ |
| 17 | Chat riêng 1-1 | Gắn theo **Landlord** (không theo từng phòng); yêu cầu đăng nhập | ✅ |
| 18 | Kiến trúc Chat | Gộp toàn bộ (1-1 + nhóm phòng) vào **1 Inbox duy nhất**, đặt ở **tab mới cấp cao nhất "Tin nhắn"** (Tenant nay 5 tab). Landlord vốn đã có tab Chat riêng — sẽ rà soát lại tương tự khi tới Phần C. | ✅ |
| 19 | Feed Ghép bạn | Cuộn dọc thường, KHÔNG làm swipe kiểu Tinder | ✅ |
| 20 | Toggle hồ sơ Ghép bạn | Có — thêm toggle "Tìm bạn ở ghép: Bật/Tắt" ngay trong màn Tạo/Sửa hồ sơ (TN-07) | ✅ |
| 21 | Action Yêu cầu match | Chấp nhận/Từ chối thao tác **ngay trên item của list** (TN-08), không cần vào chi tiết | ✅ |
| 22 | Match thành công | **Bỏ hoàn toàn** việc lộ SĐT/Zalo — thay bằng mở thẳng Chat trong app. **Thêm loại thread thứ 3 vào Inbox: TN-MSG-05 (Chat Match Roommate, peer-to-peer)**. *(Lưu ý: quyết định này cập nhật ngược lại nội dung Batch 1b đã khóa trước đó — đã chỉnh trực tiếp trong file.)* | ✅ |
| 23 | TN-10 Danh sách HĐ | Cùng 1 màn, tách bằng tab/filter "Đang hiệu lực" / "Đã kết thúc". Hub (TN-11) có nội dung khác nhau rõ rệt theo trạng thái (xem bảng trong B.3) | ✅ |
| 24 | TN-10/TN-11 gộp | Nếu Tenant chỉ có 1 HĐ (bất kể trạng thái) → bỏ qua màn danh sách, vào thẳng Hub. Chỉ hiện list khi ≥2 HĐ | ✅ |
| 25 | TN-13 Thành viên | KHÔNG hiện SĐT thành viên khác, chỉ Họ tên + avatar | ✅ |
| 26 | TN-19 Ảnh sự cố | Camera HOẶC thư viện, tự do — quy định "chỉ Camera" chỉ áp dụng riêng cho ảnh công tơ điện nước | ✅ |
| 27 | Theo dõi sự cố | Tách 2 màn: TN-20a (danh sách sự cố của phòng) + TN-20b (chi tiết 1 sự cố, hiển thị dạng **Popup/Modal nổi lên** khi bấm vào item trong list — Mobile: bottom-sheet, Web: modal dialog — có khung trao đổi tích hợp sẵn, không bắt buộc qua Property Chat) | ✅ |
| 28 | TN-21 Đổi SĐT | KHÔNG cho phép đổi SĐT (và Email) — vì là cơ chế auto-link hợp đồng, chỉ sửa được tên/avatar | ✅ |
| 29 | TN-22 Thông báo | Chỉ 1 toggle Bật/Tắt tổng, không tách nhỏ theo loại | ✅ |
| 30 | Lịch sử uy tín & Consent | KHÔNG triển khai — bỏ khỏi phạm vi outline | ✅ |
| 31 | LL-01 Room Map | Sơ đồ trực quan (mỗi ô = 1 phòng, màu theo trạng thái), không phải bảng số | ✅ |
| 32 | LL-01 Dashboard | Cần biểu đồ doanh thu theo tháng (line/bar chart) | ✅ |
| 33 | LL-04 Upload giấy tờ | Cho phép nhiều ảnh + cả Camera lẫn Upload thư viện | ✅ |
| 34 | LL-03/04/05 | Giữ 3 màn riêng biệt (wizard 3 bước), không gộp 1 form | ✅ |
| 35 | LL-07 Room Map cấp tòa | Dùng chung kiểu hiển thị với LL-01, chỉ lọc theo 1 tòa | ✅ |
| 36 | Landlord Dashboard lần đầu | Empty state: card CTA lớn "Thêm Tòa nhà đầu tiên", số liệu nhạt màu phía dưới, đầy đủ chỉ sau khi có tòa được duyệt | ✅ |
| 37 | LL-11 Tạo HĐ | Chỉ nhập 1 người đại diện lúc tạo HĐ; các thành viên khác thêm sau qua LL-16 | ✅ |
| 38 | LL-12 Mẫu HĐ | Chỉ dùng mẫu hệ thống dựng sẵn, không có tính năng Landlord tự tạo mẫu riêng | ✅ |
| 39 | LL-17 Xóa thành viên | Không có khái niệm "người đại diện HĐ" đặc biệt — mọi thành viên ngang hàng | ✅ |
| 40 | Chốt số điện nước | Cho phép CẢ 2: Chốt đơn lẻ (từ Chi tiết Phòng) VÀ Chốt hàng loạt (từ Danh sách Phòng cấp Tòa, LL-18b/c/d) | ✅ |
| 41 | LL-20 OCR thất bại | Có trạng thái riêng "Không nhận diện được, vui lòng nhập tay" | ✅ |
| 42 | LL-23 Thanh toán 1 phần | Cho phép — nút mặc định "Xác nhận thu ĐỦ" + tùy chọn phụ nhập số tiền cụ thể, hệ thống tự tính & tự đổi trạng thái | ✅ |
| 43 | LL-25 Quét nợ | Tự động đánh dấu "Quá hạn" + gửi noti nhắc + hiện trong **Danh sách công nợ đơn giản** (LL-25b) trên Dashboard — không làm thêm logic phức tạp (không phạt/tính lãi) | ✅ |
| 44 | LL-27 Popup sự cố Landlord | Giữ dạng popup (tái sử dụng), đầy đủ hành động; issue tự động gắn `room_id` theo ngữ cảnh Hub lúc Tenant tạo (không tự chọn); list (LL-26/TN-20a) luôn hiện rõ nhãn Tòa nhà—Phòng; nút "Xem trong Chat phòng" deep-link thay vì khung trao đổi nhúng | ✅ |
| 45 | LL-30 Tiền phòng quyết toán | Landlord tự nhập số tiền (không ép theo công thức chia ngày cứng) — hệ thống chỉ gợi ý tham khảo | ✅ |
| 46 | LL-31 Khấu trừ cọc | 1 ô tổng số tiền + 1 ô lý do chung, không tách nhiều hạng mục | ✅ |
| 47 | Sửa/Hủy hóa đơn đã phát hành | **[Bổ sung ngược lại C.5 đã khóa]** Thêm LL-21a (danh sách hóa đơn đã phát hành) + LL-21b (sửa/hủy). Chỉ cho sửa/hủy khi hóa đơn CHƯA có thanh toán nào; đã có tiền vào (1 phần/đủ) → chỉ xem, không cho sửa. Sửa xong tự sinh lại VietQR mới + báo qua Property Chat | ✅ |
| 48 | C.9 Chat Landlord | Gộp thành 1 Inbox duy nhất (LL-CHAT-01/02), giống cấu trúc Tenant — mỗi phòng vẫn có Property Chat nhóm riêng, deep-link vào Inbox chung | ✅ |
| 49 | STK/VietQR nhận tiền | Cấu hình ở cấp **Tòa nhà** (LL-06b, mới thêm), khả dụng sau khi được duyệt — KHÔNG nằm trong Hồ sơ cá nhân Landlord | ✅ |
| 50 | LL-37 Thông báo Landlord | Chỉ 1 toggle Bật/Tắt tổng, giống Tenant, không tách nhỏ theo loại | ✅ |
| 51 | Báo cáo/Thống kê chuyên sâu | KHÔNG làm màn riêng ở giai đoạn này — trước mắt chỉ dùng Dashboard tổng quan (LL-01), nhưng đảm bảo Dashboard ở **mức đầy đủ** (biểu đồ doanh thu + công nợ + room map, không sơ sài) | ✅ |
| 52 | AD-01 Admin Dashboard | Chỉ số liệu/card tổng quan, KHÔNG cần biểu đồ (khác Landlord) | ✅ |
| 53 | AD-04 Khóa tài khoản | Bắt buộc nhập lý do khóa, lưu vào Audit Log | ✅ |
| 54 | AD-10 Chi tiết Audit Log | Hiển thị dạng Popup/Modal, nhất quán với LL-27/TN-20b | ✅ |

---

## Bước tiếp theo (đề xuất)

1. ✅ **Đã hoàn tất:** Khung sườn đầy đủ 93 màn hình, toàn bộ 4 Phần A–D đã được thảo luận và chốt chi tiết (nội dung, hành vi, điều hướng, các trường hợp đặc biệt).
2. **Bước kế tiếp:** Soạn **kế hoạch prompt chuẩn cho Stitch** — chia theo từng màn hình hoặc từng cụm màn liên quan, kèm mô tả bố cục Mobile & Web, dựa trên toàn bộ quyết định đã chốt trong tài liệu này.

---

## PHẦN H — Danh sách màn hình đánh số theo Stitch Project (Mobile / Web tách riêng)

> Mobile và Web là **2 Project riêng biệt trên Stitch**. Nội dung/nghiệp vụ giống hệt nhau (đã chốt ở Phần A–D), chỉ khác bố cục trình bày. Vì vậy 2 project sau đây liệt kê **cùng 1 tập nội dung**, chỉ khác: (1) Mobile có thêm Splash + màn chọn vai trò mà Web không có; (2) Web có thêm trang Landing Chủ trọ (SH-02b) và toàn bộ 10 màn Admin mà Mobile không có. Số thứ tự dùng để đặt tên frame trên Stitch (vd "01. Splash"); mã trong ngoặc là ID tham chiếu tới quyết định chi tiết ở Phần A–D.

### H.1 — PROJECT: "Rentify — Mobile" (81 màn)

**Cụm 1 — Auth & Onboarding (11 màn)**
01. Splash *(SH-01)* · 02. Chọn vai trò *(SH-01b)* · 03. Đăng nhập *(SH-03)* · 04. Quên mật khẩu — Nhập email *(SH-03b)* · 05. Đặt lại mật khẩu *(SH-03c)* · 06. Đăng ký — Tenant *(SH-04a)* · 07. Đăng ký — Landlord *(SH-04b)* · 08. Tài khoản Landlord bị khóa *(SH-06)* · 09. Tài khoản Tenant bị hạn chế *(SH-07)* · 10. Xác nhận đăng xuất *(SH-08)* · 11. Lỗi chung (network/403/404) *(SH-09)*

**Cụm 2 — Tìm phòng & Chi tiết (4 màn)**
12. Trang chủ / Danh sách phòng *(SH-02 + TN-02, gộp 1 màn)* · 13. Bộ lọc tìm phòng *(TN-01)* · 14. Chi tiết phòng *(TN-03)* · 15. Phòng đã lưu *(TN-04)*

**Cụm 3 — Ghép bạn (5 màn)**
16. Feed Ghép bạn *(TN-05)* · 17. Chi tiết hồ sơ Roommate *(TN-06)* · 18. Tạo/Sửa hồ sơ Ghép bạn *(TN-07)* · 19. Yêu cầu Đã gửi/Đã nhận *(TN-08)* · 20. Match thành công *(TN-09)*

**Cụm 4 — Inbox/Chat Tenant (5 màn)**
21. Inbox tổng *(TN-MSG-01)* · 22. Chat riêng với Landlord *(TN-MSG-02)* · 23. Property Chat nhóm phòng *(TN-MSG-03)* · 24. Property Chat chung tòa *(TN-MSG-04)* · 25. Chat Match Roommate *(TN-MSG-05)*

**Cụm 5 — Hub "Phòng của tôi" (7 màn)**
26. Danh sách hợp đồng *(TN-10)* · 27. Hub Phòng của tôi *(TN-11)* · 28. Xem hợp đồng *(TN-12)* · 29. Danh sách thành viên *(TN-13)* · 30. Danh sách hóa đơn *(TN-14)* · 31. Chi tiết hóa đơn *(TN-15)* · 32. Thanh toán *(TN-16)*

**Cụm 6 — Sự cố Tenant (3 màn)**
33. Danh sách sự cố của phòng *(TN-20a)* · 34. Popup chi tiết sự cố *(TN-20b)* · 35. Tạo báo cáo sự cố *(TN-19)*

**Cụm 7 — Tài khoản Tenant (2 màn)**
36. Hồ sơ cá nhân *(TN-21)* · 37. Cài đặt thông báo *(TN-22)*

**Cụm 8 — Dashboard Landlord (1 màn)**
38. Dashboard (kèm biến thể Empty state) *(LL-01)*

**Cụm 9 — Quản lý Tòa nhà & Phòng (10 màn)**
39. Danh sách Tòa nhà *(LL-02)* · 40. Thêm Tòa nhà B1/3 *(LL-03)* · 41. Upload giấy tờ B2/3 *(LL-04)* · 42. Cấu hình đơn giá B3/3 *(LL-05)* · 43. Chi tiết Tòa nhà *(LL-06)* · 44. Cấu hình VietQR Tòa nhà *(LL-06b)* · 45. Danh sách Phòng (Room Map) *(LL-07)* · 46. Thêm Phòng mới *(LL-08)* · 47. Chi tiết Phòng *(LL-09)* · 48. Menu Tiện ích Phòng *(LL-10)*

**Cụm 10 — Hợp đồng & Thành viên (7 màn)**
49. Tạo Hợp đồng *(LL-11)* · 50. Chọn mẫu HĐ *(LL-12)* · 51. Xuất PDF HĐ *(LL-13)* · 52. Upload HĐ đã ký *(LL-14)* · 53. Danh sách thành viên *(LL-15)* · 54. Thêm thành viên *(LL-16)* · 55. Xác nhận xóa thành viên *(LL-17)*

**Cụm 11 — Chốt số điện nước (6 màn)**
56. Chốt số đơn lẻ *(LL-18)* · 57. Entry Chốt hàng loạt *(LL-18b)* · 58. Luồng Chốt hàng loạt *(LL-18c)* · 59. Tổng kết hàng loạt *(LL-18d)* · 60. Camera chụp công tơ *(LL-19)* · 61. Kết quả OCR *(LL-20)*

**Cụm 12 — Hóa đơn (5 màn)**
62. Preview hóa đơn (trước phát hành) *(LL-21)* · 63. Danh sách hóa đơn đã phát hành *(LL-21a)* · 64. Sửa/Hủy hóa đơn *(LL-21b)* · 65. Phát hành hóa đơn *(LL-22)* · 66. Xác nhận thu tiền mặt *(LL-23)*

**Cụm 13 — Cấu hình chu kỳ & Công nợ (3 màn)**
67. Cấu hình chu kỳ & quét nợ *(LL-24)* · 68. Form hạn thanh toán *(LL-25)* · 69. Danh sách công nợ *(LL-25b)*

**Cụm 14 — Sự cố Landlord (3 màn)**
70. Tab Sự cố tổng *(LL-26)* · 71. Popup chi tiết sự cố *(LL-27)* · 72. Landlord tạo sự cố *(LL-28)*

**Cụm 15 — Checkout/Thanh lý (5 màn)**
73. Chốt số lần cuối *(LL-29)* · 74. Hóa đơn quyết toán *(LL-30)* · 75. Quyết toán cọc *(LL-31)* · 76. Xác nhận hoàn tất thanh lý *(LL-32)* · 77. Trạng thái chờ dọn dẹp *(LL-33)*

**Cụm 16 — Chat Inbox Landlord (2 màn)**
78. Inbox tổng *(LL-CHAT-01)* · 79. Chi tiết 1 thread chat *(LL-CHAT-02)*

**Cụm 17 — Cài đặt Landlord (2 màn)**
80. Hồ sơ cá nhân *(LL-36)* · 81. Cài đặt thông báo *(LL-37)*

---

### H.2 — PROJECT: "Rentify — Web" (90 màn)

**Cụm 1 — Auth & Onboarding (10 màn, KHÔNG có Splash/Chọn vai trò, CÓ thêm Landing Chủ trọ)**
01. Landing "Kênh Chủ trọ" *(SH-02b)* · 02. Đăng nhập *(SH-03)* · 03. Quên mật khẩu *(SH-03b)* · 04. Đặt lại mật khẩu *(SH-03c)* · 05. Đăng ký — Tenant *(SH-04a)* · 06. Đăng ký — Landlord *(SH-04b)* · 07. Tài khoản Landlord bị khóa *(SH-06)* · 08. Tài khoản Tenant bị hạn chế *(SH-07)* · 09. Xác nhận đăng xuất *(SH-08)* · 10. Lỗi chung *(SH-09)*

**Cụm 2–7 (Tenant, 22 màn):** giữ nguyên số thứ tự nội dung như bản Mobile (11→36), chỉ đổi bố cục Web (list/grid nhiều cột, sidebar filter, modal thay bottom-sheet...). *(SH-02+TN-02 → TN-22, tổng 22 màn)*

**Cụm 8–17 (Landlord, 44 màn):** giữ nguyên nội dung như bản Mobile, đổi bố cục Web (sidebar nav, table thay vì card cho danh sách...).

**Cụm 18 — Admin (10 màn, CHỈ CÓ trên Web)**
81. Admin Dashboard *(AD-01)* · 82. Danh sách Người dùng *(AD-02)* · 83. Chi tiết hồ sơ Người dùng *(AD-03)* · 84. Khóa tài khoản *(AD-04)* · 85. Mở khóa tài khoản *(AD-05)* · 86. Danh sách BĐS chờ duyệt *(AD-06)* · 87. Chi tiết BĐS chờ duyệt *(AD-07)* · 88. Từ chối BĐS *(AD-08)* · 89. Audit Logs *(AD-09)* · 90. Popup chi tiết Audit Log *(AD-10)*

> **Lưu ý số thứ tự Web:** Cụm 1 Web có 10 màn (thay vì 11 bên Mobile, do bỏ Splash+Chọn vai trò nhưng thêm Landing Chủ trọ). Vì vậy số thứ tự Cụm 2–17 bên Web = **số thứ tự Mobile tương ứng TRỪ 1** (vd "Chi tiết phòng" là #14 bên Mobile → là #13 bên Web). Cụm 2–17 kết thúc ở #80, Admin đánh số tiếp 81–90. Số thứ tự cụ thể từng màn được ghi rõ trong file prompt riêng.

---

## PHẦN I — Design System (Style Tokens cho Stitch — trích từ tài liệu style đã cung cấp)

> Khối này dán vào **đầu mỗi prompt Stitch** (cả Mobile lẫn Web) để đảm bảo nhất quán xuyên suốt toàn bộ 171 màn hình của 2 project.

**Grounding:** Lấy cảm hứng từ Stripe Dashboard, Linear, Mercury — KHÔNG theo default "AI UI kit". Màu gần như vắng mặt trừ khi mang ý nghĩa thật (trạng thái, dữ liệu, 1 hành động chính). Dữ liệu dày đặc hiển thị dạng bảng/list căn chỉnh thật, không nhồi mọi thứ vào card bo tròn riêng lẻ. Số liệu trông như dữ liệu thật (cụ thể, hơi lẻ), không phải số demo tròn trịa giả tạo. Phân cấp thông tin đến từ cỡ chữ/độ đậm/khoảng cách, không phải từ việc bọc khung/thêm nhãn trang trí. Icon nhỏ, chức năng, không phải minh họa trang trí.

**Cấm tuyệt đối:** chữ IN HOA toàn bộ; dấu chấm giữa (·)/gạch chéo (//)/em-dash trang trí trong heading; tên kiểu code hiển thị trên UI; font monospace; shadow trang trí trên mọi card; bọc mọi section trong khung viền giống hệt nhau; số liệu demo tròn giả; hero/gradient trang trí không có chức năng thật; **badge dạng pill tô màu nền** (dùng hệ thống dot-indicator/outlined-tag bắt buộc bên dưới thay thế).

**Design Tokens (dùng chính xác các giá trị sau):**
- Nền: `#F8FBFE` (xanh pastel rất nhạt, gần trắng)
- Chữ chính: `#142A4C` (navy đậm) · Chữ phụ: `#5C7290` · Viền/divider: `#D7E3F2`
- Accent chính (`#1E6FD9`) — dùng TIẾT KIỆM: chỉ cho 1 card nổi bật nhất/màn, nút CTA chính, progress bar, tab nav đang active. KHÔNG áp cho mọi nút/icon.
- Semantic: Thành công/Đã trả `#16A34A` · Quá hạn/Cảnh báo `#DC2626` (đỏ thật, không làm nhạt thành cam) · Trung tính/Chờ xử lý `#94A3B8`
- Typography: DUY NHẤT font **Inter** cho mọi thứ (heading semibold/bold, body regular/medium); số liệu dùng tabular figures
- Bo góc & độ nổi (theo ngữ cảnh): Card nổi bật/hero = bo góc 24px + shadow mềm màu xanh nhạt `rgba(30,111,217,0.10)`; Card list/nội dung thường = bo góc 14px, phẳng, KHÔNG shadow, chỉ viền 1px `#D7E3F2`; Button = bo góc 12px
- **Badges & tags (bắt buộc):** Trạng thái sống (phòng trống/đã xác minh/đã thanh toán/trạng thái sự cố) = chấm tròn 7px màu semantic + chữ navy thường, KHÔNG nền màu, KHÔNG pill. Thuộc tính cố định mô tả (Chỉ nữ/Tối đa 3 người/Không thú cưng) = tag chữ nhật viền 1px `#D7E3F2`, bo góc 7px, KHÔNG nền, chữ navy — dùng y hệt bất kể thuộc tính đó "tích cực" hay "tiêu cực" (đây là dữ kiện mô tả, không phải cảnh báo).
- Layout: Dashboard được phép có card xếp lớp/hơi lệch tạo chiều sâu; màn danh sách/dữ liệu (hóa đơn, thành viên, kết quả tìm kiếm) phải căn lưới chuẩn, không xếp lệch.

**Logo (placeholder):** Icon hình mái nhà cách điệu đơn giản (roofline monogram), màu Primary Accent `#1E6FD9`, nền trong suốt/nền app. Đây là placeholder tạm — có thể yêu cầu Stitch thay logo thật bằng 1 Edit prompt riêng sau này mà không ảnh hưởng các màn khác.
