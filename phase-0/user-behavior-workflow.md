# User Behavior Story — Workflow vòng đời cho thuê trọn vẹn (A→Z)

> **Mục đích:** Kiểm chứng hành vi từ đầu đến cuối. Tài liệu này mô phỏng lại, từng bước, toàn bộ vòng đời cho thuê của 1 phòng — từ **chủ trọ thêm phòng trống** → **khách dọn vào ký HĐ** → **chốt số & tính tiền tháng đầu** → **phát sinh 1 sự cố sửa chữa** → **trả phòng thanh lý cọc** — và đối soát từng bước với các quyết định chuẩn để xác nhận **các luồng nghiệp vụ khớp 100% với nhau và không có điểm gãy/mâu thuẫn nào**.
>
> **Đối tượng kiểm chứng (source of truth):** `discovery/decisions.md` (D16, D17, D18, D22, D25, D29) · `feature-list.md` · `business-rules.md` (draft P1-07) · `product-sketch.md` · `tech-feasibility.md`.
>
> **Trạng thái:** 🟡 Bản kiểm chứng (draft) — sinh ra để soi lỗi luồng; mọi cập nhật cần PM duyệt (không đổi scope vượt `requirement.md` khi chưa có PM chấp thuận).
>
> **User-flow chi tiết theo vai trò:** bản per-role (tenant / landlord / admin / shared) sống tại `pm/phase-1/discovery/user_flow/` (verify qua P1-19) — là **source of truth cho navigation/UI**. Tài liệu này giữ vai trò **kiểm chứng A→Z 1 vòng đời** (soi lỗi luồng & đối soát quyết định); hai bản bổ trợ cho nhau, không trùng lặp.

---

## Phạm vi kiểm chứng (một vòng đời, theo đúng yêu cầu)

> Một vòng đời trọn vẹn của 1 phòng: **Chủ trọ thêm phòng trống** → **Khách dọn vào & ký HĐ** → **chốt số & hóa đơn tháng đầu** → **1 sự cố sửa chữa phát sinh** → **khách trả phòng & thanh lý cọc.**

Mỗi giai đoạn được viết theo 3 phần như yêu cầu:
1. **Step-by-Step User Behavior** — Ai làm gì, trên màn hình nào.
2. **Artifact & Data Handoff** — Dữ liệu nào sinh ra ở bước này làm input cho bước kế tiếp.
3. **Logic Gap & Failure Mode Audit** — Soi chỗ luồng có thể gãy, và có vi phạm quyết định nào không.

**Tenant Action** luôn được viết theo **2 nhánh song song**:
- **Nhánh 1 — Active Tenant:** người thuê dùng Mobile app.
- **Nhánh 2 — Passive/Solo Tenant (D29):** người thuê không bao giờ đăng nhập; toàn bộ điểm chạm được delegate (Kênh ngoài app / QR ngân hàng động, tiền mặt, giấy).

Mỗi bước phải giữ được **cả 2 nhánh đồng thời** — đây là ràng buộc lõi của D29.

---

## Giai đoạn 0 — Chuẩn bị: Tổng quan Entity & Trạng thái (bối cảnh, không phải bước)

Tái sử dụng ở mọi giai đoạn. Giá trị lấy từ `tech-feasibility.md` + `business-rules.md`.

| Entity | Trạng thái quan trọng / enum | Ghi chú |
|--------|------------------------------|---------|
| `LandlordProfile` | default settings jsonb: `electricityRate`, `waterRate`, invoice/contract config (**D16**) | đặt 1 lần, áp mọi tòa |
| `Building` | optional `electricityRate`, `waterRate` (building override, **D16**) | chỉ khai khi khác landlord default; chủ không bắt buộc (**D25**) |
| `Room` | `owner_id` NOT NULL (**D25**); optional `electricityRateOverride`, `waterRateOverride` (**D16**); status `available/occupied/maintenance` | tình trạng derive từ HĐ active (D9, không có bảng riêng) |
| `Contract` | `draft → signed → active → expired/terminated`; `signature_mode` luôn `template_upload` (**D18**); `issued_by_user_id` (**D25**); partial unique index: 1 `active` / phòng | chụp ảnh CCCD lúc tạo (**D17**) |
| `MeterReading` | unique `(room_id, period)`; kỳ đầu nhập baseline thủ công | OCR + xác nhận tay (F5) |
| `Invoice` | `pending → paid/overdue/void`; unique `(contract_id, period)`; không sửa sau khi gửi — void rồi tạo lại | tiền thuê + điện nước + phí |
| `Payment` | `method: vnpay / momo / cash / mock`; `status: pending → success/failed`; 1 Invoice − N Payment (retry) | đối soát QR động qua webhook; tiền mặt ghi tay |
| `IssueReport` | `open → in_progress → resolved`; tạo qua `@issue` trong Property Chat riêng phòng (**D24′**); FCM push; chủ trọ có thể tự tạo cho tenant solo (**D29**) |
| `Conversation` / `Message` (Property Chat) | `conversation.kind: room \| building`; `message.type: text \| image \| file \| bot` (card) | realtime Socket.io khi app mở + FCM offline + DB persistence khi mở lại (**D24′**); không phụ thuộc socket (**D29**) |
| `Deposit` (cọc) | lưu số tiền trên `Contract` | thanh lý giải quyết ngoài hệ thống (**giấy / 2 bên**) |

**Nguyên tắc chung D29:** mọi giai đoạn dưới đây phải hoàn thành với **zero tenant login**. Nếu bước nào có "Nhánh 1 (app)" là con đường *duy nhất* để đi tiếp → bước đó **vi phạm D29** và bị đánh dấu trong phần audit.

---

## Giai đoạn 1 — Onboarding: Chủ trọ thêm phòng trống

### 1.1 Step-by-Step User Behavior

**Hành vi Chủ trọ** (Web — primary ops console):
1. Đăng nhập → JWT với `roles: ["landlord"]` (**D13** roles array).
2. Đặt **đơn giá mặc định của landlord (global)** `electricityRate`, `waterRate` — set 1 lần, áp mọi tòa (**D16**). *(Landlord có nhiều tòa không cần set lại từng cái.)*
3. Tạo **Building** → chỉ override đơn giá ở cấp tòa (`electricityRate`, `waterRate`) khi tòa khác landlord default (**D16**). *(Chủ Building không bắt buộc theo D25.)*
4. (Tùy chọn) Tạo **Floor** (nhóm); có thể gán hint `owner_id` (**D25**, chỉ gợi ý).
5. Tạo **Room**: tên, diện tích, tiện nghi, `maxOccupancy`, `genderPolicy`, `houseRules`, giá thuê. Đặt **`owner_id` = chính mình (NOT NULL)** (**D25**). Tùy chọn override đơn giá `electricityRateOverride` / `waterRateOverride` (**D16**).
6. Trạng thái phòng hiển thị **`available`**.

**Hành vi Người thuê:** *Không có.* Chưa tồn tại tenant. (Lần tiếp xúc đầu tiên ở Giai đoạn 2.)

**Phản hồi của Hệ thống & Thay đổi trạng thái:** tạo `Room` → trạng thái derive `available` → hiện ô trống trên dashboard room-map (**D20**) → đưa vào tìm kiếm bản đồ (**2.1**) cho tenant active.

### 1.2 Artifact & Data Handoff

- Sinh ra: `Building` (rate mặc định), `Room` (`owner_id`, override rate tùy chọn, ràng buộc/occupancy).
- Cung cấp cho: **GĐ 2** tạo HĐ (room + rate + owner); **GĐ 4** tính hóa đơn (dùng nguồn rate nào); **GĐ 5** hard-filter ghép bạn (**D21** ràng buộc).

### 1.3 Logic Gap & Failure Mode Audit

- **Kiểm điểm gãy:** Nếu chủ trọ **không** đặt rate cấp Building **và** không có override phòng → auto-invoice **bị chặn** (đã ghi trong context D16: *"thiếu rate → hóa đơn bị chặn"*). **Đây là gap có sẵn**, không phải mới sinh ra. **Đề xuất:** buộc rate ở bước tạo Building HOẶC có hàng mặc định (fallback), nếu không GĐ 4.3 (auto-invoice) sẽ gãy.
- **Thứ tự:** Nếu chủ trọ tạo Room trước Building → web phải ép "tạo building trước" hoặc tự tạo building mặc định. Nếu không Room không có nguồn rate. Không phải quyết định nào quy định, nhưng không được crash.
- **Kiểm tra D25 ✅:** 1 `owner_id` / phòng, tự vận hành. Không có khái niệm manager — đúng; chủ trọ chính là operator. Không có `manager_id` ở đâu — khớp "Bỏ Manager/delegation hoàn toàn ở MVP".

---

## Giai đoạn 2 — Ký hợp đồng (dọn vào)

### 2.1 Step-by-Step User Behavior

**Hành vi Chủ trọ** (Web — e-contract **3.1**):
1. Mở phòng → bấm **"Tạo hợp đồng"**. Hệ thống tạo `Contract` status **`draft`**; `issued_by_user_id = Room.owner_id` (**D25**).
2. Nhập thông tin tenant. **Chụp & lưu ảnh CCCD** cho tenant (mặt trước; 1 lần / tenant) (**D17**). *(OCR tự điền tên/ngày sinh/địa chỉ — feature **5.6**, **MVP** (nâng từ Stretch 31/08), tái dùng pipeline OCR công tơ.)*
3. Với **phòng ở ghép** → cấu hình thanh toán theo **D22**: chọn hoặc
   - **(a) Đại diện thanh toán** (lead ký; người ở cùng chia offline), hoặc
   - **(b) Hóa đơn chia sẻ** (hệ thống track phần góp từng người + trạng thái đã trả/chưa).
   HĐ **luôn là 1 hợp đồng đại diện** (lead ký). Chủ trọ chỉ giao dịch 1 bên (D22).
4. Nhập tiền cọc, tiền thuê tháng, ngày bắt đầu/kết thúc, điều khoản.
5. Bấm **"Sinh mẫu HĐ"** → hệ thống sinh file **Word/PDF đã điền sẵn** thông tin phòng/tenant/rate/cọc (**D18**).
6. Tải về & **in** mẫu.

**Hành vi Người thuê:**
- **Nhánh 1 (Active):** tenant có thể đăng nhập xem HĐ draft / kiểm tra thông tin trên Mobile, **nhưng không có thao tác ký điện tử** (không OTP/PIN — **D18**). App chỉ mang tính thông tin tại bước này.
- **Nhánh 2 (Passive, D29):** tenant không đăng nhập. Chủ trọ truyền đạt điều khoản qua **kênh ngoài (SĐT/giấy)**. Tenant không cần app.

**Hai nhánh hội tụ — Ký tay (thật, có giá trị pháp lý):**
7. **Hai bên ký tay trên giấy đã in** (Chủ trọ + tenant đại diện). *(Hệ thống không tồn tại bất kỳ chữ ký điện tử nào — D18, 31/08.)*
8. **Chủ trọ upload file đã ký** (`template_upload`) → hệ thống lưu làm chứng cứ pháp lý, ghi `signed_at`, `uploaded_file`. Hệ thống parse/OCR PDF → các field có cấu trúc (deposit, monthly_rent, rates, dates, terms) **và giữ file gốc** (**D18** hấp thụ D14). File gốc = nguồn chuẩn nếu parse lệch.

**Phản hồi của Hệ thống & Thay đổi trạng thái:** `Contract.status: draft → signed` → rồi `active` (auto hoặc theo trigger; xem audit). Trạng thái phòng derive chuyển `available → occupied`. Dashboard (**D20**) hiện phòng occupied + bắt đầu ghi doanh thu.

### 2.2 Artifact & Data Handoff

- Sinh ra: `Contract` (active), `issued_by_user_id` = owner; ảnh CCCD + field OCR tùy chọn (**D17**); số tiền cọc; payment config (**D22**); file PDF ký tay upload + field có cấu trúc parse được (**D18**).
- Cung cấp cho: **GĐ 3** chốt số công tơ; **GĐ 4** hóa đơn (tiền thuê + rate + tham chiếu cọc); **GĐ 6** thanh lý cọc; tương lai khai báo tạm trú (Phase 1+) và lịch sử uy tín (**D26**, consent).

### 2.3 Logic Gap & Failure Mode Audit

- **Soát D18 ✅ (sạch):** **không** có `e_sign` / `e_ack` / `pin_verified` / `transaction_pin_hash` / OTP ở đâu. "Nếu chưa up file ký thì HĐ **chưa** signed" giữ nguyên. **Không có điểm gãy do từ chối ký điện tử** vì ký điện tử không tồn tại — con đường duy nhất là ký giấy + upload, tenant **không thể** né bằng cách từ chối ký số (không có gì để từ chối).
- **Lỗi — hai bên không ký:** HĐ ở nguyên `draft`. Phòng giữ `available` (không có HĐ active). **Không gãy** — không bị khóa tiền/nghĩa vụ; chủ trọ làm lại hoặc bỏ. Chấp nhận được.
- **Lỗi — chủ trọ chậm upload (đã ký giấy nhưng chưa scan):** HĐ vẫn `draft` trong hệ thống dù ràng buộc pháp lý đã có. Rủi ro: auto-invoice phụ thuộc HĐ `active` → có thể bỏ sót tháng. **Đề xuất:** dashboard nhắc "chưa upload chữ ký" khi đã sinh mẫu; định nghĩa nhắc cho `draft` cũ. (Không vi phạm quyết định — chỉ là tinh chỉnh vận hành.)
- **Lỗi — parse/OCR lệch (D18):** file gốc upload được giữ làm chứng cứ; field từ parse chỉ là hỗ trợ, không phải nguồn chuẩn. Tốt — không mất dữ liệu.
- **Kiểm tra D29 ✅:** bước 7–8 do **chủ trọ làm toàn bộ**; tenant không cần app. Ký là bước vật lý duy nhất, do thiết kế (bản chất của wet-sign, không phải dependency phần mềm).
- **Kiểm tra D22 ✅:** luôn 1 HĐ đại diện; payment config (a)/(b) do chủ trọ chọn. Không nhiều HĐ/phòng — khớp partial unique index 1 `active` / phòng.
- **Kiểm tra D25 ✅:** `issued_by_user_id` là owner phòng (chính mình). Không có delegation chéo phòng.

---

## Giai đoạn 3 — Chốt số điện nước tháng đầu

### 3.1 Step-by-Step User Behavior

**Hành vi Chủ trọ** (Web — chốt số công tơ **3.3**):
1. Chụp ảnh công tơ điện/nước của phòng.
2. Hệ thống chạy **OCR + xác nhận tay** (1 chạm) → tạo `MeterReading` cho `(room_id, period)`.
3. **Bot post card kết quả chốt số vào Chat riêng phòng** (D24′ auto-remind, type `bot`): số cũ/mới, tiêu thụ, ảnh đối chứng → tenant active đối chiếu ngay trong chat; tenant passive không cần app (ảnh gửi kênh ngoài nếu tranh cãi — D29).
4. *Baseline kỳ đầu:* **chủ trọ nhập số cũ (baseline) thủ công** lần đầu (edge case đã ghi trong `tech-feasibility.md`), sau đó chụp số hiện tại. Điện năng tiêu thụ = hiện tại − baseline.

**Hành vi Người thuê:** *Không có* (cả 2 nhánh — tenant không có vai trò tạo dữ liệu; theo D29 không có tương tác bắt buộc app tenant ở bước này; active tenant chỉ nhận card chốt số trong chat).

**Phản hồi của Hệ thống & Thay đổi trạng thái:** lưu `MeterReading`; unique `(room_id, period)` ngăn chốt trùng. Giá trị tiêu thụ sẵn sàng cho bước sinh hóa đơn. Card chốt số trong chat là bằng chứng truy vấn được (không phải nguồn dữ liệu).

### 3.2 Artifact & Data Handoff

- Sinh ra: `MeterReading(current, baseline, consumption, period)`.
- Cung cấp cho: **GĐ 4** → tiền điện/nước = consumption × nguồn rate (**D16**).

### 3.3 Logic Gap & Failure Mode Audit

- **Kiểm tra D16 ✅:** consumption không dính rate ở đây; việc chọn rate xảy ra lúc lập hóa đơn (**D16**: room → building → landlord default). Không mâu thuẫn.
- **Kiểm tra D24′ ✅:** bot post card kết quả chốt số vào Chat phòng (type `bot`, không phải nguồn dữ liệu — nguồn là `MeterReading`); FCM offline + DB persistence giữ chống chịu khi tenant/landlord offline (D29). Không thành điểm gãy.
- **Lỗi — tenant tranh cãi số (D29):** tenant không ở app → tranh cãi qua **kênh ngoài (SĐT)**; chủ trọ chụp lại / đính kèm ảnh chứng cứ. Không gãy; giải quyết thủ công. **Đề xuất:** giữ ảnh công tơ đã chụp đính kèm với reading để chủ trọ gửi qua kênh ngoài khi cần — hỗ trợ kênh solo giải quyết tranh chấp.
- **Thứ tự:** hóa đơn cho 1 kỳ **không được** sinh trước khi có `MeterReading` của kỳ đó. Nếu chủ trọ chốt lệch thứ tự tháng → unique `(room_id, period)` ngăn ghi đè nhưng cho phép tạo lệch thứ tự → hóa đơn có thể tham chiếu reading chưa có baseline. **Đề xuất:** đặt điều kiện sinh hóa đơn = (a) HĐ `active` VÀ (b) reading hoàn tất cho kỳ.

---

## Giai đoạn 4 — Hóa đơn & thanh toán tháng đầu

### 4.1 Step-by-Step User Behavior

**Hành vi Chủ trọ** (Web — hóa đơn **3.4/3.5/3.10**):
1. Hệ thống auto-sinh `Invoice` = **tiền thuê + điện nước(từ chốt số) + phí tùy chọn**; 1 hóa đơn / `(contract_id, period)`. Status = **`pending`**.
2. Tiền điện nước = consumption × **override phòng → building → mặc định landlord (D16)**. Prorate nếu HĐ bắt đầu giữa tháng (**business-rules §3**).
3. Chủ trọ rà soát hóa đơn → **phát hành** (tùy chọn đính kèm ghi chú / export Excel).
4. **Kênh chat (Property Chat, D24′):** khi phát hành, **bot post card hóa đơn vào Chat riêng phòng** (header "Hóa đơn T08/2026", tổng, hạn — loại `bot`/card) + **`@mention` tenant**. Realtime khi app mở; tenant offline → FCM push (không phụ thuộc socket). Tenant thấy card ngay trong chat và có thể trả lời/đối chiếu (ảnh công tơ, phí, sai sót) trước khi trả.
5. **Chuyển tới tenant:**
   - **Nhánh 1 (Active):** tenant thấy hóa đơn qua **hộp thư Mobile (2.4) + card trong Chat phòng (D24′)**; thảo luận/xác nhận trong chat nếu cần; thanh toán qua **VNPay/MoMo dynamic named-QR** (**2.5/3.10**) hoặc quét QR động từ card chat.
   - **Nhánh 2 (Passive, D29):** chủ trọ gửi hóa đơn qua **kênh ngoài (SĐT) / QR ngân hàng động / giấy**; chat app tùy chọn/trống. Tenant quét QR bằng **app ngân hàng bất kỳ** hoặc trả **tiền mặt**.

**Hành vi Người thuê có thể là 1 trong 2 nhánh — rồi thanh toán:**
- **Nhắc nợ / quá hạn (chat):** hóa đơn đến hạn/quá hạn → **bot post card nhắc vào Chat riêng phòng + FCM push** (D24′ auto-remind); chủ trọ có thể nhắc tay qua chat (active) hoặc kênh ngoài (passive, D29).
- **Online:** thanh toán qua QR định danh động hoặc MoMo/VNPay → **webhook callback → đối soát tự động đánh dấu hóa đơn `paid`** (**3.10**, khác biệt cốt lõi).
- **Tiền mặt (D29):** tenant trả tiền mặt; **chủ trọ ghi nhận tay** 1 `Payment(method: cash)` → hóa đơn `paid`.
- **Mock (demo):** toggle tùy chọn `ENABLE_MOCK_PAYMENT` (fallback R1).

**Phản hồi của Hệ thống & Thay đổi trạng thái:** `Invoice.status: pending → paid` (hoặc `overdue` nếu quá hạn, hoặc `void` nếu sai). `Payment.status: pending → success/failed`; giao dịch fail → retry (1 Invoice−N Payment). Biểu đồ doanh thu/công nợ dashboard cập nhật (**D20**).

### 4.2 Artifact & Data Handoff

- Sinh ra: `Invoice` (pending/paid/overdue), bản ghi `Payment` (method), bằng chứng đối soát (`raw_gateway_response` cho QR; `transaction_id` nullable cho tiền mặt), **card hóa đơn + card nhắc nợ** (`Message` type `bot`) trong Chat phòng (**D24′**).
- Cung cấp cho: **GĐ 5** bối cảnh tài chính; **GĐ 6** thanh lý (lịch sử đã trả định hướng hoàn cọc); trạng thái công nợ dashboard; tenant active tra cứu hóa đơn/thảo luận trực tiếp trong chat.

### 4.3 Logic Gap & Failure Mode Audit

- **Kiểm tra D16 ✅:** phân giải rate theo thứ tự **room → building → landlord default**, đúng quyết định mới (override > mặc định). *Một nút còn lại:* **open question #6 — flat hay bậc thang EVN** chưa chốt trong `product-sketch.md §6`. Trước khi chốt, auto-invoice **không được giả định** bậc thang EVN — triển khai nên mặc định flat cho tới khi P1-07 đóng câu này. Đánh dấu **open, không phải vi phạm**.
- **Kiểm tra D22 ✅ bao trùm phòng ở ghép tại đây:** config (a) rep-payer → 1 hóa đơn cho lead, chia offline. Config (b) shared invoice → hệ thống track phần góp từng người + trạng thái đã trả/chưa. Cả hai đều chủ trọ nhìn thấy. **Full bill-splitting (D4) giữ Phase 1+ — không mâu thuẫn.**
- **Lỗi — chủ trọ gửi nhầm hóa đơn (nguyên tắc audit-trail D18/D20):** quy tắc trong `tech-feasibility.md`: **không sửa hóa đơn đã gửi → `void` hóa đơn sai + tạo hóa đơn thay thế**. Điều này giữ vết audit. **Không gãy.**
- **Kiểm tra D29 ✅:** giao & đối soát đều hoạt động khi tenant offline:
  - QR quét bằng **app ngân hàng bất kỳ** → không cần đăng nhập.
  - Tiền mặt → ghi tay `method: cash`.
- **Lỗi — tenant không trả / không phản hồi:** hóa đơn → `overdue`; **bot nhắc card vào chat phòng + FCM** (active) hoặc chủ trọ nhắc qua kênh ngoài (SĐT, passive/D29). Không bao giờ chặn thao tác của chủ trọ. **Không gãy.**
   - **Đề xuất (nhắc nợ):** nhắc công nợ (**3.6**) là Stretch — chỉ đẩy lên MVP nếu demo cần trạng thái công nợ ở GĐ 6. Không vi phạm nếu vắng.
- **Kiểm tra D24′ (chat) ✅ tại GĐ 4:** bot card hóa đơn + nhắc nợ chạy trên **Chat riêng phòng** (realtime khi mở / FCM offline / DB persistence mở lại). Baseline chống chịu giữ nguyên cho cả 2 nhánh: tenant active thấy card trong chat, tenant passive không cần chat — **không bắt buộc login để nhận hóa đơn** (D29).
- **Lỗi — mất callback thanh toán / webhook fail (QR):** mô hình retry (1 Invoice−N Payment) hấp thụ; chủ trọ cũng có thể ghi `cash`/xử lý tay. Lấy từ `raw_gateway_response` hỗ trợ debug. **Không gãy.**

---

## Giai đoạn 5 — Sự cố / Sửa chữa

### 5.1 Step-by-Step User Behavior

**Khởi nguồn (cả 2 bên):**
- **Nhánh 1 (Active tenant):** tenant mở Mobile → chat riêng phòng → gõ `@issue` (mô tả + ảnh) hoặc mở issue panel → tạo `IssueReport` `open`. Bot post card vào chat + FCM push tới chủ trọ (**D24′**).
- **Nhánh 2 (Passive, D29):** tenant báo qua **SĐT/điện thoại/giấy** — không app. **Chủ trọ tự tạo `IssueReport` trên Web và theo dõi** (**D29**: "landlord tạo/tracker").

**Hành vi Chủ trọ** (Web hoặc mobile-lite chủ trọ với push "duyệt sự cố" — **D13**):
1. Nhận FCM/thông báo.
2. Đặt `in_progress`, trao đổi kế hoạch sửa.
3. **Thread:** Property Chat riêng phòng (**D24′**) — realtime Socket.io khi app mở, FCM offline, DB persistence khi mở lại.
   - Tenant active: nhắn trong app, `@issue`/`@mention`, bot auto-remind.
   - Tenant passive: phối hợp qua **SĐT/điện thoại/giấy** (**D29**); chat app tùy chọn/trống.
4. Sửa xong → đặt **`resolved`**, ghi chú kết quả.

**Phản hồi của Hệ thống & Thay đổi trạng thái:** `IssueReport.status: open → in_progress → resolved`. Tùy chọn: phòng → `maintenance` trong lúc sửa (derive, theo dashboard **D20**).

### 5.2 Artifact & Data Handoff

- Sinh ra: `IssueReport` (+ thread comments, ảnh).
- Cung cấp cho: dashboard maintenance view (**D20**); tùy chọn theo dõi chi phí sửa trong tương lai.

### 5.3 Logic Gap & Failure Mode Audit

- **Kiểm tra D29 ✅:** sự cố có thể được tạo và theo dõi hoàn toàn **bởi một mình chủ trọ**; chat app không chặn. Đây là module nhẹ nhất dưới D29 — khớp stress-test App. B ("chat dùng nếu tenant login, còn không xử lý ngoài app (SĐT/kênh ngoài)").
- **Lỗi — chủ trọ không giải quyết:** sự cố kẹt `open`/`in_progress`. **Không gãy vòng đời** (không chặn thanh toán/trả phòng) — chỉ là vấn đề tồn đọng vận hành. **Đề xuất:** nhắc sự cố tồn đọng; tùy chọn.
- **Ghi chú D24′ (P1-14):** Property Chat đã chốt (Socket.io). Baseline chống chịu = **FCM + DB persistence** (không phụ thuộc socket) — draft nhất quán cho cả nhánh active/passive (D29).
- **Không phát hiện vi phạm quyết định ở giai đoạn này.**

---

## Giai đoạn 6 — Trả phòng & thanh lý cọc

### 6.1 Step-by-Step User Behavior

**Hành vi Chủ trọ** (Web — vòng đời hợp đồng):
1. Đến `end_date` → HĐ tự chuyển **`expired`**. Trả sớm → chủ trọ thao tác đặt **`terminated`**.
2. Tháng cuối **prorate** nếu trả giữa tháng (**business-rules §3**).
3. **Hóa đơn cuối** sinh cho số dư còn lại → chuyển/thanh toán như GĐ 4 (online / QR động / tiền mặt — cả 2 nhánh).
4. **Thanh lý cọc:** hệ thống lưu số tiền cọc trên HĐ; **việc hoàn/khấu trừ thực tế giải quyết ngoài hệ thống (giấy / 2 bên)** — hệ thống chỉ ghi số tiền, không ghi chi tiết giải ngân. Chủ trọ ghi trạng thái cuối lên HĐ.

**Hành vi Người thuê:**
- **Nhánh 1 (Active):** tenant thấy hóa đơn cuối + trạng thái HĐ trong app.
- **Nhánh 2 (Passive, D29):** tenant xử lý qua Zalo/giấy; không cần app.

**Phản hồi của Hệ thống & Thay đổi trạng thái:** `Contract.status: active → expired/terminated`. Trạng thái phòng derive → **`available`** (không HĐ active) → quay về ô trống dashboard + tìm kiếm lại. **CCCD / tạm trú đóng:** chủ trọ khai báo/báo tạm vắng **thủ công** (Phase 1+, D17) — MVP chỉ lưu ảnh CCCD; không nộp hồ sơ.

### 6.2 Artifact & Data Handoff

- Sinh ra: HĐ terminated/expired; hóa đơn cuối prorate + thanh toán; phòng `available`; bản ghi cọc đã chốt.
- Cung cấp cho: **GĐ 1 lần nữa** (phòng vào lại onboarding → vòng sau); churn ô trống dashboard; lịch sử uy tín tenant (**D26**, Stretch, chỉ consent).

### 6.3 Logic Gap & Failure Mode Audit

- **Kiểm tra D17 ✅:** khai báo tạm trú/tạm vắng **ngoài MVP** (D17 → Phase 1+). Hệ thống không chặn trả phòng vì khoản này. Ảnh CCCD vẫn được lưu. **Không gãy.**
- **Cọc:** hoàn trả xử lý ngoài hệ thống do thiết kế — ranh giới có chủ đích (rủi ro kiện tụng cọc tránh khỏi MVP). **Không mâu thuẫn** miễn app ghi rõ + hiển thị số tiền cọc; khuyến nghị thêm checkbox **"đã thanh lý cọc"** để tránh nỗi đau "cọc bị giam oan" kinh điển (từ `vision.md`).
- **Lỗi — còn hóa đơn cuối chưa trả trước khi trả phòng:** chủ trọ có thể giữ cọc đến khi trả đủ (2 bên). App chỉ đánh dấu hóa đơn `overdue`. Không gãy phần mềm.
- **Kiểm tra D25 ✅:** sau khi terminated, `owner_id` phòng không đổi (vòng sau cùng chủ). Không cần gán lại → không có lỗ hổng sở hữu.
- **Vào lại vòng lặp:** phòng trở về `available` → GĐ 1 lặp lại sạch (không xung đột unique index vì HĐ cũ không còn `active` → HĐ `active` mới được phép).

---

## Tổng hợp kiểm chứng

### Chạy đủ → các giai đoạn khớp nhau chưa? ✅ (kèm 2 điểm cần lưu ý)

| Giai đoạn | Sống sót D29 (solo)? | Chuỗi HĐ/trạng thái có bước kế tiếp? | Quyết định tham chiếu |
|-----------|----------------------|--------------------------------------|-----------------------|
| 1 Onboarding | ✅ (chưa có tenant) | Room `available` → GĐ 2 | D16, D25, D20 |
| 2 Ký HĐ | ✅ (bước 7–8 chỉ chủ trọ) | `draft→signed→active` → GĐ 3–4 | D18, D17, D22, D25 |
| 3 Chốt số | ✅ (tenant không có vai trò) | Reading → GĐ 4 | D16, F5 |
| 4 HĐ/Thanh toán | ✅ (QR/tiền mặt không cần login; chat là phụ trợ FCM+DB) | `pending→paid/overdue/void` → GĐ 6 | D16, D22, D29, D18(audit-trail), D24′ (bot card + nhắc nợ) |
| 5 Sự cố | ✅ (chủ trọ tự tạo) | `open→in_progress→resolved` | D29, D24′ |
| 6 Trả phòng | ✅ (cọc 2 bên, tạm trú thủ công) | `expired/terminated` → phòng `available` → GĐ 1 | D17, D25, §3 prorate |

**Không tìm thấy điểm gãy logic nào** — mọi nhánh (tenant active HOẶC passive) đều có đường liền mạch qua toàn bộ vòng đời. Bước vật lý duy nhất (ký giấy) là bản chất pháp lý của wet-sign, không phải lỗ hổng phần mềm.

### Điểm cần lưu ý mở (không phải vi phạm — trình lên P1-07 / P1-05)

1. **Fallback đơn giá (D16/UC-L3):** nếu phòng không có cả mặc định tòa lẫn override phòng → auto-invoice bị chặn. Đóng bằng quy tắc bắt buộc-rate hoặc hàng mặc định trong P1-07.
2. **Flat vs bậc thang EVN (open Q#6):** mở từ lâu; auto-invoice phải mặc định flat cho tới khi chốt (P1-07).
3. **Nhắc HĐ `draft` tồn (D18):** HĐ đã ký giấy nhưng chưa upload có thể âm thầm bỏ sót tháng tính tiền — đề xuất nhắc "chưa upload chữ ký" (tinh chỉnh vận hành).
4. **Biên bản thanh lý cọc (GĐ 6):** đề xuất cờ thanh lý rõ ràng để lưu bằng chứng cho nỗi đau tranh chấp cọc kinh điển.
5. **P1-14 (D24′) Property Chat:** đã chốt Socket.io (chat phòng + chung toà, bot `@issue`/`@mention`); baseline chống chịu = **FCM + DB persistence** (không phụ thuộc socket, D29).

### Đối soát tuân thủ quyết định (6 quyết định được nêu)

- **D16 (landlord-default + building/room override)** ✅ Triển khai đúng ở GĐ 4.3 (room → building → landlord); điểm tồn duy nhất = open Q#6 + watch-item thiếu-rate.
- **D17 (CCCD khi tạo HĐ)** ✅ Chụp 1 lần / tenant ở GĐ 2.2; tạm trú đầy đủ đúng là deferred (Phase 1+); OCR auto-fill = 5.6 **MVP** (nâng từ Stretch 31/08), dùng lại pipeline.
- **D18 (template → wet-sign → upload; không OTP/PIN/e_ack)** ✅ Ký là con đường pháp lý duy nhất; không có chữ ký số/OTP/PIN ở đâu; giữ file gốc làm chứng cứ.
- **D22 (1 HĐ đại diện + payment config a/b)** ✅ Phòng ở ghép luôn 1 HĐ lead; payment config do chủ trọ chọn; full split deferred.
- **D25 (1 chủ/phòng, Room.owner_id BẮT BUỘC, HĐ do owner phát hành)** ✅ GĐ 1 đặt owner_id; GĐ 2 phát hành theo owner; GĐ 6 không cần gán lại.
- **D29 (resilience solo, zero tenant login, BẮT BUỘC)** ✅ Mọi giai đoạn, Nhánh 2 giữ vòng đời sống qua kênh ngoài (SĐT)/QR/tiền mặt/giấy; xác minh ở bảng full-run. App tenant giữ tùy chọn/passive suốt vòng đời.

---

## Phụ lục — Diễn giải theo lời chủ trọ (một hơi)

> "Tôi thêm tòa nhà, đặt giá điện/nước, rồi thêm từng phòng và gắn mình làm chủ phòng. Khi khách dọn vào, tôi tạo HĐ, chụp CCCD của họ, điền tiền thuê và cọc, rồi app in ra mẫu đã điền sẵn — hai bên ký tay trên giấy, tôi scan lại, phòng chuyển sang occupied. Với phòng ở ghép tôi chọn hoặc lead trả, hoặc app theo dõi phần góp từng người. Mỗi tháng tôi chụp ảnh công tơ, app OCR, tôi xác nhận, hóa đơn tự sinh theo giá phòng (hoặc theo mặc định của chủ) và tôi gửi qua kênh ngoài kèm QR động. Tenant có thể quét QR đó bằng app ngân hàng bất kỳ — không cần app của tôi — hoặc trả tiền mặt và tôi đánh dấu đã trả. Có gì hỏng, hoặc họ báo trong app hoặc tôi tự ghi lại và phối hợp qua kênh ngoài. Khi họ ra, tôi chấm dứt HĐ, tháng cuối prorate, thanh lý cọc trên giấy, và phòng quay về available cho khách kế. Và việc nào cũng không bao giờ phải chờ tenant đăng nhập."

---

*Tài liệu sinh ra để kiểm chứng các luồng khớp 100%. Mọi thay đổi về scope/quyết định vượt ngoài việc kiểm chứng này phải qua duyệt của PM và cập nhật `decisions.md` / `business-rules.md` (P1-07) / `requirement.md` nếu áp dụng.*
