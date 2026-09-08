# Decisions Log — Phase 1

> Quyết định phát sinh trong Phase 1 được ghi tại đây. Quyết định nền Phase 0 (D1–D29): xem `../../phase-0/discovery/decisions.md`.
> Quy tắc (AGENTS.md `pm/`): ID tăng dần, **không renumber/reuse** — tham chiếu chéo trong repo dựa vào ID ổn định.
> Khi Notion decision log hoạt động, bổ sung liên kết tương ứng.

## Index

| ID | Date | Decision | Status |
|---|---|---|---|
| D30 | 2026-09-05 | **Đơn giá điện/nước versioned + phí định kỳ** — thay số cứng flat bằng bảng `UtilityRatePolicy` (flat/tiered/per_head) + `RecurringFee` (4 fee_kind), snapshot hóa đơn; đóng open question #6 `product-sketch.md` | ✅ Accepted |
| D31 | 2026-09-05 | **Preset đơn giá + cấm nhập tay bậc thang** — landlord chỉ chọn từ preset (EVN/TT25/nước địa phương) hoặc nhập 1 số flat/khoán; `steps` jsonb chỉ từ seed preset, không hiển thị form bậc thang trong UI; override tòa/phòng là chế độ nâng cao (ẩn mặc định) | ✅ Accepted |
| D32 | 2026-09-06 | **Onboarding không chặn + kê khai xe tại HĐ + preset phí + phí 1 lần** — `LandlordProfile.elec_policy_id`/`water_policy_id` nullable (NULL = chưa cấu hình, block lúc lập hóa đơn không phải login); `Contract.vehicle_count` khai lúc tạo/cập nhật HĐ; preset phí seed (Wifi/QLVH/Gửi xe/Vệ sinh) + `other_fees` 1 lần trong hóa đơn | ✅ Accepted |
| D33 | 2026-09-06 | **Thanh toán một phần + thu dư/thiếu nhắc trong history + hóa đơn theo phòng + điện bỏ khoán đầu người** — đóng 6 điểm chết chuỗi hóa đơn (partial unique, auto-sinh theo phòng, `partially_paid`, overpay reminder, voided-webhook, `other_fees` âm); xóa `user-behavior-workflow.md` | ✅ Accepted |
| D34 | 2026-09-06 | **Baseline công tơ bắt buộc bằng OCR khi bàn giao + trigger D33② không tạo được hóa đơn thì xếp vào danh sách chờ sửa lỗi** — bỏ nhập tay chỉ số cũ (kỳ đầu = baseline OCR bàn giao, thay đồng hồ = baseline mới OCR); nối §6↔§7, §3/§4 → §10 | ✅ Accepted |
| D35 | 2026-09-06 | **Cho phép hiệu chỉnh tay số đọc khi OCR sai/mờ** — VerifyReading: chụp lại HOẶC sửa tay đúng số thực tế (chốt tháng §6, baseline bàn giao §5, thay đồng hồ EC1); sửa tay chỉ là hiệu chỉnh, bắt buộc có ảnh công tơ làm nguồn | ✅ Accepted |
| D36 | 2026-09-06 | **Bỏ `charged_in_invoice` khỏi `RecurringFee`** — mọi phí định kỳ đều thu qua hóa đơn app; bỏ khái niệm "trả thẳng BQL / chỉ tham khảo" ngoài MVP; đơn giản hóa flow phí (D30/D32 cập nhật theo). Đồng thời chốt: `is_active=false` ở cấp nào → **kế thừa cấp trên** (đồng bộ policy + fee) | ✅ Accepted |
| D37 | 2026-09-06 | **Tinh chỉnh schema Invoice: bỏ cột điện/nước kép + void soft + due_date = issued_at + N** — chỉ giữ `rent_amount`+`total_amount` cột (điện/nước/phí đọc snapshot jsonb); `issued_at`/`due_date` nullable (set khi Phát hành); `due_date = issued_at + N ngày` (N mặc định 5) làm gốc quét `overdue`; void = giữ bản cũ `status='void'` + liên kết new→old (giữ tên `voided_invoice_id`, làm rõ comment) | ✅ Accepted |
| D38 | 2026-09-06 | **Tạm trú: mock gateway thay được API thật + per-landlord credential + admin toggle** — thiết kế/demo artifact (không binding nghiệp vụ); `ResidencyGateway` interface (mock ⇄ real đổi bằng config); landlord tự khai báo credential (`CsltId`/username/password, chi tiết encrypt để BE Phase 2); admin toggle mock/real, **duyệt tay chỉ ở mock mode**; giữ D17 (MVP CCCD+OCR, nộp hồ sơ → Phase 1+) | ✅ Accepted |

---

## D30 — UtilityRatePolicy & RecurringFee: đơn giá điện/nước + phí định kỳ theo phiên bản

- **Context:** Open question #6 trong `product-sketch.md` §6 ("đơn giá điện/nước **flat hay bậc thang EVN**") chưa chốt. Schema cũ (D16) chỉ lưu số **decimal** trên `LandlordProfile`/`Building`/`Room` → không chứa được: bậc thang EVN 6 bậc, bậc 3 TT 25/2018 (đồng hồ phụ/sub-meter), khoán **đầu người**, và **không có lịch sử giá theo thời gian** (đổi giá giữa kỳ, `effective_from/to`). Ngoài ra thực tế chủ trọ còn thu **phí định kỳ** (Wifi, vệ sinh, gửi xe, QLVH chung cư) mà schema cũ không có chỗ lưu.
- **Decision (mô hình tính tiền phiên bản hóa):**
  - **`UtilityRatePolicy`** (bảng mới): đơn giá theo `rate_kind` = `flat` | `tiered` | `per_head`; `steps` jsonb `[{from,to,price}]` (`to=null` = mở ∞) cho bậc thang; `effective_from/to` + `is_active` cho lịch sử giá; `scope` = `landlord` | `building` | `room` (`landlord` = mặc định cả nhà, trỏ từ `LandlordProfile.elec/water_policy_id`).
  - **Chuỗi kế thừa giữ nguyên tinh thần D16:** room → building → landlord default. Field cũ được thay bằng con trỏ **`elec_policy_id`/`water_policy_id`** trên cả 3 bảng (đặt tên ngắn, bỏ "default/override" vì gây nhầm cấp); `NULL` = kế thừa cấp trên; không resolve được policy hiệu lực → **chặn hóa đơn**.
  - **`RecurringFee`** (bảng mới): phí định kỳ ngoài điện/nước, `fee_kind` = `fixed_per_period` | `per_head` | `per_area_m2` | `per_vehicle`; `scope` = `landlord` | `building` | `room` (`landlord` = mặc định áp mọi phòng/mọi tòa, override ở tòa/phòng); mọi phí thu qua hóa đơn app (`charged_in_invoice` đã gỡ — D36).
  - **`MeterReading`** thêm `utility_type` enum(`electricity`/`water`) — thực tế mỗi phòng 2 công tơ riêng; UNIQUE trở thành `(room_id, utility_type, period)`, mỗi loại 1 ảnh OCR evidence riêng; **đủ cả 2 loại mới được lập hóa đơn**.
  - **`Invoice`** thêm `utility_breakdown` + `fees_breakdown` (jsonb, **snapshot bất biến** cấu hình & đầu vào đã dùng) — hóa đơn không đổi sau phát hành; sai sót → `void` + tạo mới (`voided_invoice_id`).
  - **Giữ nguyên ngoài MVP (Phase 1+):** công tơ tổng/master-meter & chia tỷ lệ hao hụt (chủ trọ vẫn chốt sub-meter, hao hụt gộp vào đơn giá flat); bảng `VehicleRegister` (số xe nhập tay mỗi kỳ); tính bậc thang theo quota nhân khẩu tự động (chỉ qua cấu hình `steps` + `effective_from`).
- **Alternatives rejected:** giữ nguyên số decimal flat (không chứa bậc thang/khoán/lịch sử giá); append-only log giá riêng tách bảng (thêm nguồn chân lý thứ hai, phức tạp hóa mà không thêm khả năng).
- **Impact:** `discovery/database-design_v3.md` §2.8–2.11 (thêm 2 bảng, đổi field, renumber 2.10→2.21, §3 ERD, §4 traceability, §5.2 permission); `discovery/utility-billing-calculations.md` (mới — spec 100% case + pseudocode + edge case); `user_flow/landlord_user_flow.md` §3/§4/§6/§7/§9; `user_flow/tenant-user-flow.md` Flow 3.6/3.4 + §6 inventory; `business-rules.md` §3/§4 (FROZEN v1.1). Preset EVN 6 bậc (QĐ 2941/QĐ-BCT) + bậc 3 TT 25/2018 = **seed config**, không hard-code trong code. **Đóng open question #6** của `product-sketch.md`.
- **Status:** ✅ Accepted 2026-09-05 (user/PM duyệt).

---

## D31 — Preset đơn giá + cấm nhập tay bậc thang (TX thân thiện landlord lớn tuổi)

- **Context:** Phân khúc chủ trọ trọng yếu là **người lớn tuổi, ít hiểu biết công nghệ**. Cấu hình `UtilityRatePolicy` đầy đủ (tự gõ `steps` bậc thang, chọn `scope` từng cấp) là model hợp lý cho dữ liệu, nhưng **không phù hợp làm màn hình chính** cho đối tượng này. Đồng thời câu hỏi: với bậc thang, nên **hardcode** trong code (đã có luật EVN làm chuẩn) hay giữ `steps` jsonb?
- **Decision:**
  - **Không hardcode giá.** Giá EVN/QĐ đổi theo quyết định (QĐ 2941/QĐ-BCT 11/10/2024) và tồn tại **nhiều bộ bậc hợp lệ đồng thời**: EVN 6 bậc hộ gia đình, **Bậc 3 TT 25/2018** (HĐ < 12 tháng / không kê khai đủ nhân khẩu), bậc nước theo **từng Công ty Cấp nước địa phương**. Thuật toán `calcTiered` là **code** (test được, bất biến); dữ liệu giá là **config** (đổi khi có QĐ mới — chỉ cập nhật seed, không deploy code/app). Giữ `steps` jsonb trong schema như D30.
  - **`steps` chỉ đến từ preset seed, không bao giờ nhập tay** trong UI thường (lỗi cấu hình `TIER_CONFIG_INVALID` giảm thiểu). Preset gồm: EVN 6 bậc, Bậc 3 TT 25/2018 (flat 2.283đ hoặc tiered 1 bậc), bậc nước địa phương (seed theo vùng).
  - **UX chính (đại đa số chủ trọ): chọn 1 trong 3 nút to — "Giá theo EVN" / "1 số cố định" / "Khoán đầu người"** → nhập tối đa số lượng phát sinh. Onboarding gợi ý sẵn giá phổ biến (`4.000đ/kWh`, khoán `80.000đ/người`), landlord chỉ xác nhận. *(D33 — nút "Khoán đầu người" chỉ còn cho NƯỚC; điện chỉ 2 nút EVN / 1 số cố định.)*
  - **Override tòa/phòng = chế độ nâng cao (ẩn mặc định, collapse/advance-only).** Mặc định "1 giá áp cho cả nhà" (dùng scope `landlord`); "áp cho tất cả phòng / copy từ tòa khác" để giảm thao tác lặp.
  - **Không thay đổi schema**, chỉ chốt quy tắc sử dụng + thiết kế UX phủ trên model D30.
- **Alternatives rejected:** hardcode bậc thang trong code (đổi giá phải deploy + update app; không chứa được TT 25/2018 và nước theo vùng); bỏ `scope` building/room (override phòng là nhu cầu thật — phòng dịch vụ giá điện riêng).
- **Impact:** `discovery/database-design_v3.md` §2.8 (ghi chú "steps chỉ từ preset"); `user_flow/landlord_user_flow.md` §3 (onboarding preset) + §4 (override ẩn nâng cao); `discovery/utility-billing-calculations.md` §12 (note bắt buộc chọn preset) — cập nhật tháng 2026-09.
- **Status:** ✅ Accepted 2026-09-05 (user/PM duyệt).

---

## D32 — Onboarding không chặn + kê khai xe tại HĐ + preset phí + phí 1 lần

- **Context:** Dòng cấu hình đơn giá/phí mới hoàn thiện sau D30/D31, xuất hiện 3 vướng mắc: (1) gate bắt buộc chọn giá ở **login** phản UX với landlord lớn tuổi — nếu chưa biết giá thực tế thì bị chặn không vào được dashboard; (2) phí `per_vehicle` theo spec cũ **nhập tay mỗi kỳ** — thực tế số xe là thông tin ổn định gắn với hợp đồng, nên kê khai 1 lần lúc tạo/cập nhật HĐ; (3) phí định kỳ chưa có preset giúp chủ trọ lớn tuổi thao tác nhanh, và thiếu chỗ cho **phí 1 lần** (nệm mới, sửa thiết bị).
- **Decision:**
  - **Onboarding không chặn:** `LandlordProfile.elec_policy_id`/`water_policy_id` đổi **NOT NULL → nullable** (sửa D30). Ngữ nghĩa nhất quán: `NULL` ở mọi cấp = kế thừa cấp trên; tại đỉnh chuỗi, không resolve được policy hiệu lực → **block lúc lập hóa đơn** (`RATE_MISSING`, EC3) — **không block khi đăng nhập**. Lần đầu vào dashboard hiện **banner nhẹ** với nút "Cài đặt ngay" / "Để sau"; banner còn hiển thị tới khi cấu hình xong.
  - **Kê khai xe tại HĐ:** thêm `Contract.vehicle_count` (int, nullable) — khai lúc tạo/cập nhật hợp đồng (cạnh CCCD/tiền cọc). Phí `per_vehicle` tính theo số này, snapshot vào `fees_breakdown`; đổi giữa kỳ → cập nhật HĐ, áp **từ kỳ sau**. `NULL` khi có phí `per_vehicle` hoạt động → block (`VEHICLE_COUNT_MISSING`, EC8). (Bảng `VehicleRegister` vẫn ngoài MVP như D30.)
  - **Preset phí seed (đồng hành D31):** Module 6 tab Phí định kỳ cho chọn preset mẫu **Wifi / Quản lý vận hành / Gửi xe / Vệ sinh rác / Phí tự nhập** — chọn preset tự điền `fee_kind` + `unit_price` (Wifi `fixed_per_period` 100.000đ; QLVH `per_area_m2` 10.000đ/m²; Gửi xe `per_vehicle` 80.000đ; Vệ sinh `fixed_per_period` 50.000đ), chủ trọ chỉ xác nhận hoặc chỉnh số rồi chọn phạm vi + `effective_from`. Preset = seed config (không hard-code), vẫn cho tự nhập phí bất kỳ.
  - **Phí 1 lần (`other_fees`):** thêm trực tiếp lúc lập hóa đơn (preset gợi ý + gõ tên/số tự do), snapshot jsonb vào hóa đơn; nằm trong bất biến `rent + electricity + water + fees + other_fees == total_amount`.
  - **Override tòa/phòng dồn về một nơi:** form **tạo** tòa/phòng không hỏi đơn giá (mặc định `NULL` = kế thừa); mọi đổi giá/override thao tác tại **Module 6 — Cài đặt đơn giá & phí** (chọn preset → tạo policy mới scope building/room `effective_from`, không sửa policy cũ).
- **Alternatives rejected:** giữ NOT NULL + gate login bắt buộc (chặn người chưa biết giá, phản UX D31); tiếp tục nhập số xe mỗi kỳ ở màn lập hóa đơn (thao tác lặp, dễ sai, có sẵn HĐ là nơi khai đúng); không làm preset phí (chủ trọ lớn tuổi gõ tay từng trường dễ nhầm/sai đơn vị).
- **Impact:** `discovery/database-design_v3.md` §2.2 (nullable policy) + §2.6 (`contracts.vehicle_count`) + §2.9 (note preset phí) + §4 traceability; `discovery/utility-billing-calculations.md` §1.2/F4 + §3 (input) + §5–§7 + §9 (`other_fees`) + §10 (pseudocode) + §11 EC8 + §12; `user_flow/landlord_user_flow.md` §3 (banner Để sau + tách preset điện/nước) + §4 (bỏ override form tạo) + §5 (kê khai xe) + §7 (phí 1 lần) + §10 (Module 6); `business-rules.md` §3/§4 (FROZEN v1.1).
- **Status:** ✅ Accepted 2026-09-06 (user/PM duyệt).

---

## D33 — Thanh toán một phần, thu dư/thiếu nhắc, hóa đơn theo phòng, điện bỏ khoán đầu người

- **Context:** Rà điểm chết toàn chuỗi hóa đơn (landlord §7 ↔ tenant §3.6 ↔ `utility-billing-calculations.md` ↔ DB schema) phát hiện các vướng: (1) UNIQUE `(contract_id, period)` chặn tạo hóa đơn thay thế sau `void`; (2) luồng "auto-sinh hóa đơn toàn kỳ" mâu thuẫn thực tế (điện/nước phải đi chụp **từng phòng** → dữ liệu đủ không đồng thời, không batch toàn kỳ); (3) không có khái niệm **trả một phần** — Payment chưa đủ gần như vô dụng trong UI; (4) **thu dư/thiếu** không có hướng xử lý; (5) webhook trả tiền tới hóa đơn đã `void` không được định nghĩa; (6) không có cơ chế giảm trừ/miễn giảm trên hóa đơn. Ngoài ra `per_head` cho **điện** (E3) thực tế hiếm/sai nghiệp vụ (điện thu theo công tơ), và doc kiểm chứng cũ `user-behavior-workflow.md` **lệch nhiều** với quyết định hiện hành.
- **Decision:**
  - **① Partial unique index:** `Invoice` UNIQUE → **`(contract_id, period) WHERE status != 'void'`** — cho phép tạo hóa đơn thay thế sau khi void bản sai.
  - **② Hóa đơn auto-sinh theo TỪNG PHÒNG (không batch toàn kỳ):** hệ thống tự sinh `Invoice pending` cho 1 phòng **ngay khi phòng đó đủ** (a) đủ cả 2 `MeterReading` điện+nước kỳ hiện tại VÀ (b) policy/phí resolve OK (EC2–EC13 không lỗi). Landlord thấy danh sách "phòng chốt số xong ở kỳ này" → rà soát từng phiếu → phát hành. Không auto-phát hành hàng loạt toàn kỳ.
  - **③ Trả một phần = enum + status rõ ràng:** `Invoice.status` thêm giá trị **`partially_paid`** (enum đánh dấu). Quy tắc chuyển trạng thái: Σ(amount success) < total → `partially_paid` (đã thu được tiền, còn thiếu); `paid` khi Σ ≥ total; `overdue` khi quá hạn còn thiếu (> 0).
  - **Overpay (thu dư) / thiếu:** KHÔNG hoàn tiền tự động, KHÔNG bù trừ kỳ sau ở MVP. Ghi nhận đủ số tiền thực nhận (đối soát theo **mã định danh hóa đơn**, không theo amount); khi Σ(bản ghi) ≠ tổng hóa đơn → **chỉ hiển thị nhắc "thu dư X / còn thiếu Y" khi mở tab History** (landlord và tenant). Người dùng tự đối soát ngoài app — PM xác nhận "thừa/thiếu tiền người ta nhớ nhanh".
  - **④ Điện KHÔNG có `per_head`:** `rate_kind` điện chỉ `flat` | `tiered`; nước giữ cả `flat`/`tiered`/`per_head`. Bỏ E3/§5.4 + preset "Khoán đầu người" cho điện (landlord §3 §10); nước giữ khoán đầu người. Validate service (không phải enum DB).
  - **⑤ Webhook tới hóa đơn `void`:** không set `paid`, ghi nhận Payment + **cảnh báo chủ trọ** đối soát (cờ trong history).
  - **⑥ `other_fees` cho phép ÂM = giảm trừ/miễn giảm** (vd hỗ trợ 500k, giảm phí sửa): amount âm snapshot giữ dấu; bất biến `Σ == total` vẫn đúng; **block nếu `total_amount < 0`** (`TOTAL_NEGATIVE`, EC17). Preset gợi ý mở rộng thêm các mục "Giảm trừ" (âm).
  - **Xóa `pm/phase-0/user-behavior-workflow.md`** — doc kiểm chứng A→Z lệch nhiều; per-role `user_flow/` (P1-19) là SoT duy nhất. Cập nhật toàn bộ tham chiếu (P1-01/P1-05/P1-13/P1-19, README.md phase-1, phase-0 discovery README, `realtime-feasibility.md`, `decisions.md` phase-0).
- **Alternatives rejected:** giữ UNIQUE cứng (chặn tạo lại sau void — buộc dùng id khác/soft-delete gãy audit); batch toàn kỳ (mâu thuẫn thực tế chụp từng phòng); chỉ hiển thị "đã thu x/còn nợ y" mà không có status riêng (PM yêu cầu enum + status tường minh); auto-refund khi thu dư (quá tay cho MVP, tiền về TK doanh nghiệp khó tự chuyển); giữ điện khoán đầu người (hiếm, dễ nhầm với nước, đúng chuẩn thuê phòng là tính theo kWh).
- **Impact:** `discovery/database-design_v3.md` §2.8 (`rate_kind` note điện bỏ per_head), §2.11 (`status` thêm `partially_paid`, partial unique), §2.12 (Payment + overpay/thiếu note, shared_tracking giữ), §4 traceability; `discovery/utility-billing-calculations.md` §1/§5 (§5.4 bỏ E3), §9 (`other_fees` âm), §10 (pseudocode per-phòng + negative), §11 (EC15–EC17), §12 (preset điện 2 loại); `user_flow/landlord_user_flow.md` §3/§7/§10; `business-rules.md` §3/§4 (FROZEN v1.1 → v1.2); `issues/P1-19-user-flow-verify.md` (note doc cũ đã xóa).
- **Status:** ✅ Accepted 2026-09-06 (user/PM duyệt).

---

## D34 — Baseline công tơ bắt buộc OCR khi bàn giao + xử lý khi auto-trigger không tạo được hóa đơn

- **Context:** Rà `landlord_user_flow.md` phát hiện 3 lỗi thiết kế: (1) §6 vẫn giữ nhánh **"nhập chỉ số baseline bằng tay"** cho kỳ đầu — mâu thuẫn §8 `utility-billing-calculations.md` ("kỳ đầu: baseline đọc tại ngày dọn vào") và dễ gõ sai số công tơ thật; (2) §6 kết bằng "phải chốt xong toàn bộ phòng mới chuyển sang lập hóa đơn" — mâu thuẫn D33② (auto-sinh theo **từng phòng**); (3) chưa định nghĩa hành vi khi auto-trigger D33② **không tạo được hóa đơn** (chỉ đủ 2 chỉ số nhưng policy/phí block).
- **Decision:**
  - **Baseline = OCR là nguồn bắt buộc (không "chế số").** Lúc **bàn giao phòng** (`landlord_user_flow.md` §5): chụp ảnh cả 2 đồng hồ điện+nước → OCR → lưu `MeterReading is_baseline=true previous=0 current=chỉ số OCR reading_date=ngày bàn giao`. Kỳ chốt đầu tiên lấy baseline này làm chỉ số cũ (HĐ vào/ra giữa tháng → điện/nước theo lượng thực từ ngày bàn giao, §8). Thay đồng hồ giữa kỳ (EC1) → baseline mới cũng qua OCR. Bỏ màn "nhập tay baseline" như nguồn số tự do; khi OCR sai/mờ → **hiệu chỉnh tay số thực tế hoặc chụp lại** (tinh chỉnh D35).
  - **Trigger D33② không tạo được hóa đơn → phòng vào danh sách "Đã chốt số - chờ sửa lỗi"**: hệ thống tự sinh `Invoice pending` chỉ khi (a) đủ 2 `MeterReading` VÀ (b) policy/phí resolve OK (EC2–EC13). Phòng đủ chỉ số nhưng block (EC3/EC6/EC7/EC8/EC13/EC17) không bị bỏ quên: xếp vào danh sách theo dõi kèm **mã lỗi ECx** + nút hành động vào đúng màn sửa (thiết lập đơn giá §10 / nhập diện tích §4 / khai thành viên & xe §5); bot nhắc 1 lần; sửa xong → trigger chạy lại tự tạo `Invoice pending`.
  - **§6 ↔ §7 nối liền theo per-room** (bỏ "chờ chốt xong cả lô"); §7 entry = chọn Tòa + Kỳ → 3 nhánh: đủ (Invoice pending) / chưa đủ chỉ số → §6 / đủ chỉ số nhưng block ECx → danh sách chờ sửa lỗi.
- **Alternatives rejected:** giữ nhập tay baseline tự do không qua ảnh (dễ sai số thật, không gắn ngày bàn giao; hóa đơn có thể tính sai ngay kỳ đầu); để phòng block nằm im trong "chưa chốt" (chủ trọ không biết phải sửa gì, hóa đơn chết thầm).
- **Impact:** `user_flow/landlord_user_flow.md` §5 (bàn giao OCR baseline), §6 (bỏ nhập tay, nối §7, nhánh trigger-fail), §7 (entry chọn Tòa+Kỳ + danh sách chờ sửa lỗi + ReTrigger); `db-design_v3.md` §2.10 (`previous_reading`/`is_baseline` note OCR bắt buộc; **bỏ `confirmed_at`** — bản ghi chỉ insert lúc xác nhận nên dùng `created_at` chuẩn, giữ `reading_date` cho ngày đọc thực tế); `utility-billing-calculations.md` §11 EC1 (bỏ "hoặc nhập tay"); `business-rules.md` §3/§4.
- **Status:** ✅ Accepted 2026-09-06 (user/PM duyệt).

---

## D35 — Cho phép hiệu chỉnh tay số đọc khi OCR sai/mờ (tinh chỉnh D34)

- **Context:** D34 ghi "ảnh OCR sai/mờ → chụp lại, không chỉnh tay" cấm tuyệt đối việc sửa tay. PM phản hồi: khi ảnh rõ nhưng OCR đọc lệch chữ số (thường gặp với đồng hồ cơ/ảnh góc lệch) thì bắt chụp lại bất tiện; người dùng cần được **sửa tay đúng số thực tế**.
- **Decision:** Tại bước `VerifyReading` (§6 landlord), nếu ảnh mờ/OCR sai → người dùng chọn 1 trong 2: **Chụp lại ảnh rõ hơn** HOẶC **Sửa tay số đọc đúng thực tế** rồi Xác nhận (lưu kèm ảnh evidence gốc để đối chứng). Áp dụng đồng nhất cho: chốt số hàng tháng (§6), baseline bàn giao (§5) và baseline khi thay đồng hồ (EC1). Giới hạn lại ý "không nhập tay" của D34: **bắt buộc có ảnh công tơ làm nguồn** — không được bỏ qua ảnh để gõ số tùy ý; sửa tay chỉ là hiệu chỉnh giá trị OCR.
- **Alternatives rejected:** giữ cấm tuyệt đối sửa tay (bất tiện khi ảnh rõ mà OCR sai); biến nhập tay thành nguồn chính (mất đối chứng bằng ảnh, dễ gõ sai).
- **Impact:** `user_flow/landlord_user_flow.md` §5/§6; `db-design_v3.md` §2.10 (`previous_reading`/`is_baseline` note); `utility-billing-calculations.md` §11 EC1; `business-rules.md` §3; phase-0 `assumptions-risks.md` A5 + `tech-feasibility.md` §3.1.
- **Status:** ✅ Accepted 2026-09-06 (user/PM duyệt).

---

## D36 — Bỏ `charged_in_invoice` khỏi RecurringFee + chốt `is_active=false` = kế thừa cấp trên

- **Context:** Rà schema `RecurringFee` (D30) thấy cột `charged_in_invoice` (mặc định `true`, `false` = tenant trả thẳng BQL — chỉ tham khảo) **vô dụng** với MVP: khái niệm "phí thu ngoài hóa đơn/quản lý chung cư" không thuộc scope (`requirement.md` = nhà trọ/tòa chủ trọ tự quản), và cả 2 trạng thái đều cần xử lý trong app → thêm phức tạp mà không thêm giá trị. Song song, ngữ nghĩa `is_active=false` có 2 tài liệu ghi khác nhau (DB: "không phát sinh phí"; utility-billing §7: "kế thừa cấp trên") cần chốt 1.
- **Decision:**
  - **Bỏ hẳn cột `charged_in_invoice`** khỏi `RecurringFee`. Mọi phí định kỳ **đều thu qua hóa đơn app**. Dọn tham chiếu: DB §2.9, `landlord_user_flow.md` §10, `utility-billing-calculations.md` §7/D32 note, `business-rules.md` §3, D30/D32 in log.
  - **`is_active=false` ở cấp nào → bỏ qua cấp đó, kế thừa cấp trên** (thứ tự room > building > landlord) — áp đồng nhất cho **cả `UtilityRatePolicy` lẫn `RecurringFee`** (không phân biệt "policy kế thừa / fee không phát sinh").
- **Alternatives rejected:** giữ `charged_in_invoice` (thêm 1 trạng thái ít dùng, cần UI + logic hiển thị riêng); đổi `is_active=false` về "không phát sinh" cho fee (không nhất quán với policy, khó giải thích override tắt).
- **Impact:** `database-design_v3.md` §2.8/§2.9 (bỏ cột + note `is_active`); `landlord_user_flow.md` §10 (node chọn phạm vi bỏ bước charged_in_invoice); `utility-billing-calculations.md` §7 + §12; `business-rules.md` §3.
- **Status:** ✅ Accepted 2026-09-06 (user/PM duyệt).

---

## D37 — Tinh chỉnh schema Invoice: bỏ cột điện/nước kép + void là soft + `due_date = issued_at + N`

- **Context:** Rà table `Invoice` (§2.11) phát hiện: (1) bộ cột `electricity_amount`/`water_amount` **trùng** với snapshot `utility_breakdown` (chứa `amount` mỗi loại) → cột kép dễ drift, dashboard có thể đọc thẳng snapshot; riêng `rent_amount` không nằm snapshot nào nên giữ cột. (2) `voided_invoice_id` mô tả mơ hồ chiều trỏ; cần chốt chính sách void (xóa hay giữ). (3) `issued_at`/`due_date` bắt buộc NOT NULL nhưng hóa đơn `pending` (D33② auto-sinh) chưa phát hành thì chưa có 2 trường này — sai ràng buộc; đồng thời chưa định nghĩa `due_date` tính thế nào.
- **Decision:**
  - **Bỏ `electricity_amount`/`water_amount`.** Chỉ `rent_amount` (prorated `monthly_rent`, §8) + `total_amount` là cột denormalized (D20); điện/nước/phí lấy từ `utility_breakdown`/`fees_breakdown` = nguồn duy nhất. Invariant: `rent_amount + Σ(utility_breakdown.amount) + Σ(fees_breakdown.amount) + Σ(other_fees.amount) == total_amount`.
  - **Void = soft (không xóa):** bản cũ giữ `status='void'` (audit D18/D20, webhook trễ vẫn đối soát D33⑤), tạo bản mới; partial unique `(contract_id, period) WHERE status != 'void'` cho phép thay thế. Cột `voided_invoice_id`: giữ tên, làm rõ **hóa đơn mới trỏ tới bản cũ đã bị void nó thay thế (new → old)**.
  - **`issued_at` (timestamp, nullable)** = thời điểm Phát hành (rời `pending`); **`due_date` (date, nullable)** = `issued_at + N ngày` (N cấu hình, **mặc định 5**); cả 2 set cùng lúc khi landlord bấm Phát hành. `due_date` là mốc quét định kỳ → `overdue` (landlord §7).
- **Alternatives rejected:** giữ cột điện/nước (đọc 2 nơi, drift, dashboard dùng jsonb được); void hard-delete (mất audit, gãy đối soát webhook trễ, tenant đã nhận card cũ mất dấu vết); `due_date` = ngày cố định mùng X hay chủ trọ tự chọn (thao tác thêm / khó dự đoán so với phát hành + N).
- **Impact:** `database-design_v3.md` §2.11 (bỏ 2 cột, sửa `voided_invoice_id` comment, tách `issued_at`/`due_date` nullable + note due rule); `utility-billing-calculations.md` §9 (invariant + note cột); `business-rules.md` §4; phase-0 `tech-feasibility.md` §3.1 (bỏ 2 cột, note due).
- **Status:** ✅ Accepted 2026-09-06 (user/PM duyệt).

---

## D38 — Tạm trú: mock gateway thay được API thật + per-landlord credential + admin toggle

- **Context:** Research v1 `tam-tru-api-research.md` kết luận "🔴 Blocked — không có public API". Sau đó nhóm tìm được **tài liệu kỹ thuật chính thức về API Khai báo tạm trú (KBTT) cho Cơ sở lưu trú (CSLT)** của Cục Quản lý Xuất nhập cảnh – Bộ Công an (`api-kbtt.xuatnhapcanh.gov.vn`): OAuth 2.0 (Bearer Token), `POST /authorization-service/oauth/token`, per-CSLT credential (`CsltId`, username, password). Không gọi thật được từ app sinh viên (thiếu quyền + phân khúc sản phẩm là thuê **dài hạn** D9 không khớp loại hình "thông báo lưu trú ngắn hạn"). Tuy nhiên tài liệu này là chuẩn để dựng **mock gateway** minh họa kiến trúc tích hợp cho hội đồng.
- **Decision (thiết kế/demo artifact — không ràng buộc nghiệp vụ pháp lý, giữ nguyên D17 cho MVP):**
  - **Gateway Adapter:** định nghĩa interface `ResidencyGateway` (`getToken`/`declare`/`refresh`/`getStatus`) trong backend; 2 implementation `MockGateway` và `RealBcaGateway` đổi qua cấu hình (`gateway.env`). Logic nghiệp vụ + payload contract viết **1 lần theo interface** — đổi API thật = đổi cấu hình + nguồn credential + tắt duyệt tay, **không đổi logic/payload**.
  - **Per-landlord credential:** mỗi CSLT = 1 bộ credential riêng; **landlord tự khai báo** trong tài khoản của mình. Model gợi ý `LandlordGatewayCredential` (`landlord_id`, `cslt_id`, `username`, `password_encrypted`, `gateway_env`, `is_active`). **Chi tiết mã hóa lưu trữ để BE quyết định ở Phase 2** (doc này chỉ ở mức thiết kế).
  - **Admin toggle mock/real:** Admin Portal (Cấu hình hệ thống) có switch mock/real. **Mock mode:** bật **duyệt tay** (admin xem hồ sơ, trigger duyệt/từ chối thủ công mô phỏng phản hồi cơ quan). **Real mode:** **tắt duyệt tay** (cơ quan đảm nhận), trạng thái lấy từ response thật. Duyệt tay là hành vi mô phỏng của mock, không tồn tại khi real → tự ẩn.
  - **MVP bất biến (D17):** chỉ lưu ảnh CCCD tại e-contract + OCR trích info 5.6; không tự động nộp hồ sơ. Nộp hồ sơ đầy đủ vẫn Phase 1+.
  - **UX song song (không phụ thuộc mock):** sinh PDF tờ khai CT01/CT04 + deep-link/hướng dẫn tới Cổng DVC Quốc gia / VNeID.
- **Alternatives rejected:** bỏ tích hợp, chỉ giữ hướng "điền hộ + deep-link" (v1 — ít giá trị trình bày, không thể hiện tư duy thiết kế tầng tích hợp); gọi thẳng API thật trong MVP (không có quyền, loại hình không khớp D9, vi phạm D7 integration-first).
- **Impact:** `phase-0/discovery/tam-tru-api-research.md` (rewrite v2 — kiến trúc gateway adapter + mock + credential + toggle); `phase-1/report-phase1.md` §4.3 (cập nhật phương án trình bày); Design/DB schema gợi ý (`LandlordGatewayCredential`, `GatewayConfig`) để BE xử lý Phase 2. Không đổi `business-rules.md` MVP.
- **Status:** ✅ Accepted 2026-09-06 (user/PM duyệt).