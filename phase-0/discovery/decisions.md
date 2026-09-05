# Decisions Log — Phase 0

> Quyết định được ghi tại đây; khi Notion decision log hoạt động, migrate sang đó.
> Tham chiếu chéo: `vision.md`, `assumptions-risks.md`, issue `P0-03`.
> **ID span D1–D29.** Đã loại/hợp nhất để tránh chồng lấn: **D2→D28** (AI matching), **D6 bỏ** (quy trình 1 lần, đã xong), **D8→D28** (AI matching), **D14→D18** (ký hợp đồng), **D23→D9** (dài hạn-only), **D27→D17** (tạm trú), **D15 bỏ** (Contract Explainer khỏi AI scope — AI chỉ còn 2 feature). D12 không tồn tại (skipped). **Bỏ khỏi log 05/09 (nội dung đã nằm gọn trong doc gốc, gọn log):** **D3 → `requirement.md`** (LLM adapter), **D5 → `AGENTS.md`** (song ngữ docs), **D7 → `requirement.md`/`vision.md` §5** (integration-first), **D10 → `vision.md` §1** (segment mục tiêu), **D19 → `feature-list.md`** 1.6/6.6 (bỏ import). Tham chiếu chéo còn lại trỏ về các doc đó. Giữ ID ổn định để tham chiếu chéo trong repo không đổi. Quyết định Phase 1: xem `../../phase-1/discovery/decisions.md` (D30+).

## Index

| ID | Date | Decision | Status |
|---|---|---|---|
| D1 | 2026-08-22 | Định vị vision: **nền tảng hai chiều** (landlord ops + tenant portal cùng vòng đời) | ✅ Accepted |
| D4 | 2026-08-22 | Chia tiền ở ghép ("Không gian phòng") → **Phase 1+** | ✅ Accepted |
| D9 | 2026-08-22 | Scope **dài hạn only** — từ chối bổ sung homestay/cho thuê ngắn hạn (29/08 reaffirm bằng phân tích, hấp thụ D23) | ✅ Accepted |
| D13 | 2026-08-23 | **Cross-platform role coverage**: web + mobile đều phục vụ cả landlord lẫn tenant (staging primary → secondary) | ✅ Accepted |
| D16 | 2026-08-27 | **Cấu hình đơn giá điện/nước:** landlord default (global) + ghi đè tòa/phòng | ✅ Accepted |
| D17 | 2026-08-27 / 31 | **CCCD & tạm trú:** lưu ảnh CCCD 1 lần tại e-contract; **OCR trích info CCCD = MVP** (31/08, feature 5.6); khai báo tạm trú/tạm vắng đầy đủ → Phase 1+; research API DVC = spike only (hấp thụ D27) | ✅ Accepted |
| D18 | 2026-08-29 / 31 | **Contract signing (chữ ký số/OTP không giá trị pháp lý):** app sinh mẫu HĐ → user up file **ký tay 2 bên** (wet-sign) làm artifact pháp lý; **bỏ OTP/PIN/`e_ack`** (31/08). Hấp thụ D14 | ✅ Accepted |
| D20 | 2026-08-29 | **Dashboard chủ trọ MVP:** màn hình lịch phòng trống/đang thuê trực quan + biểu đồ doanh thu/công nợ realtime (nâng 1.3 + 3.7) | ✅ Accepted |
| D21 | 2026-08-29 / 31 | **Ghép bạn: chủ trọ CÓ quyền set yêu cầu/ràng buộc** (max người/phòng, policy giới tính, nội quy, budget-range = hard filter); **không** duyệt/veto từng cặp cá nhân (Model a — R1) | ✅ Accepted |
| D22 | 2026-08-29 | **HĐ ở ghép: 1 HĐ đại diện (lead ký) + payment config linh hoạt:** landlord chọn (1) đại diện thanh toán HOẶC (2) hóa đơn chia sẻ nhiều người (app track phần góp + trạng thái trả). D4 full split → Phase 1+ | ✅ Accepted |
| D24 | 2026-08-29 | **Property Chat Platform** (Socket.io): chat riêng phòng + chat chung toà, bot auto-remind, `@issue`, `@mention`; FCM offline + DB persistence | ✅ Accepted (P1-14; chờ teacher duyệt chi tiết) |
| D25 | 2026-08-29 / 31 | **Ownership DB (chốt 31/08 theo `ownership-model.md`):** nhiều chủ trên 1 tòa, **1 chủ / phòng** (`Room.owner_id` BẮT BUỘC); giữ Floor; **bỏ Manager/delegation** khỏi MVP | ✅ Accepted |
| D26 | 2026-08-29 | **Lịch sử uy tín người thuê:** platform-internal, consent-based (Model a — R1); defer cross-platform credit (PDPD 2023). **Stretch** — không bắt buộc MVP | ✅ Accepted |
| D28 | 2026-08-29 | **AI matching: Stretch + spec** (P1-13), hấp thụ biên giới kỹ thuật D8 | ✅ Accepted |
| D29 | 2026-08-29 | **Landlord-can-operate-solo resilience (MANDATORY):** hệ thống PHẢI chạy được khi tenant KHÔNG login; landlord làm toàn bộ vòng đời một mình, tenant app optional/passive; roommate matching vẫn chạy cho tenant có account | ✅ Accepted (bắt buộc) |

---

## D1 — Two-sided positioning

- **Context:** Bằng chứng hỗ trợ cả trục landlord-first (pain #1+#2 chủ trọ = 35 điểm, khách trả tiền) lẫn tenant-first (gap "giai đoạn Ở", ux-mobile). Vision ≤4 câu phải chọn trọng tâm.
- **Decision:** Hai phía song song trong cùng vòng đời — tự động hóa vận hành cho chủ trọ + cổng trải nghiệm cho người thuê.
- **Alternatives rejected:** automation chủ trọ làm trung tâm (mất khác biệt giai đoạn "Ở"); tenant-first (lệch core quản lý của `requirement.md`).
- **Impact:** Câu vision nêu cả hai phía; value prop canvas 3 personas trong `vision.md`. Xem **D29**: tenant portal là optional/passive — hai chiều chỉ áp dụng KHI tenant có account; hệ thống vẫn chạy nếu tenant không login (landlord vận hành một mình).

## D4 — Bill splitting → Phase 1+

- **Context:** Concept "Không gian phòng + Trưởng phòng + chia tiền" (ux-mobile Module 2.3) vượt core của `requirement.md`; thêm bài toán phân quyền + trạng thái đóng tiền cho team 5 người.
- **Decision:** Đẩy Phase 1+; không đưa vào value prop MVP.
- **Impact:** `p0-02/discovery-ux-mobile.md` Module 2.3 giờ là Phase 1+ — Mobile annotate lại tài liệu của mình; PM nhắc tại daily sync.

## D9 — Scope dài hạn only, từ chối homestay/cho thuê ngắn hạn

- **Context:** Thầy đề xuất bổ sung khả năng cho thuê homestay ngắn hạn; PM lo 13–14 tuần không đủ triển khai 2 business logic khác nhau.
- **Decision:** Sản phẩm phục vụ **cho thuê dài hạn** (phòng trọ/căn hộ mini, hợp đồng theo tháng, chốt số điện nước định kỳ). Homestay/Airbnb-style out of scope. Schema vẫn giữ field `property_type` trên `Building` để Phase 1+ mở rộng mà không phá mô hình dữ liệu hiện có.
- **Lập luận từ chối:**
  - Hai vòng đời không dùng chung luồng nghiệp vụ nào: giá/đêm + calendar check-in/out + đồng bộ OTA ↔ hợp đồng tháng + chốt số định kỳ + đối soát QR.
  - Chính Mona House cũng mất nhiều năm để hỗ trợ hybrid; Smoobu/ezCloud chuyên ngắn hạn và không có chốt số điện nước dài hạn — làm hời hợt cả hai sẽ thua đối thủ chuyên biệt ở cả hai mảng.
  - 13–14 tuần × team 5 người: làm sâu một lifecycle > làm nông hai lifecycle (đúng tiêu chí SE của môn học).
- **Cập nhật 29/08 (hấp thụ D23):** thầy yêu cầu chứng minh khả thi/không khả thi kết hợp → `short-vs-long-term-analysis.md` chốt **bất khả thi trong 13–14 tuần** (+60–80% scope). Giữ D9 nguyên vẹn; dùng file analysis làm talking point khi bảo vệ thầy.
- **Impact:** `vision.md` §7 Scope Boundary; risk R3 cập nhật; `product-sketch.md` §5 link file `short-vs-long-term-analysis.md`.

---

## D13 — Cross-platform role coverage: web + mobile phục vụ cả 2 role

- **Context:** PM yêu cầu "cả 2 role hoạt động tốt trên cả 2 platform". Backend đã role-agnostic sẵn (JWT `sub`+`role`, guard `@Roles()` không phân biệt nguồn request) — điểm cần chốt nằm ở frontend scope: trước đó web chỉ có landlord-screen, mobile chỉ có tenant-screen.
- **Decision:**
  - **Cả 2 role hoạt động tốt trên cả 2 platform:** landlord-web + landlord-mobile đều có đầy đủ chức năng ops; tenant-web + tenant-mobile đều có đầy đủ chức năng portal. Không phân primary/secondary — linh hoạt, user chọn platform phù hợp.
  - Backend giữ nguyên `User.role` enum đơn — mỗi user chỉ thuộc 1 role, không multi-role. Landlord và tenant là 2 user tách biệt, không phải 1 user nhiều role.
- **Lý do/cảnh báo:** effort FE tăng (~8 screens: 4 web + 4 mobile), QA matrix nền tảng × role phình → rủi ro R3/R7.
- **Impact:** `tech-feasibility.md` §2 (JWT payload, không đổi role model); UI scope P0-06 liệt kê rõ screens theo role × platform; ký HĐ theo D18 chỉ cần landlord up file đã ký giấy (tenant không bắt buộc có app — hỗ trợ D29).

## D16 — Cấu hình đơn giá điện/nước: landlord-default (global) + ghi đè tòa/phòng

- **Context:** UC-L3 (auto-invoice) phụ thuộc cấu hình đơn giá; thiếu rate → hóa đơn bị chặn. Cần chốt mức hạt (granularity) của đơn giá điện/nước: chung toàn tòa hay riêng từng phòng.
- **Decision:**
  - **Landlord default (global)** giữ đơn giá mặc định `electricityRate`, `waterRate` — set **1 lần**, áp cho **mọi tòa** của chủ trọ (không phải khai lại từng building).
  - `Building` có thể ghi đè qua `buildingElectricityRate`/`buildingWaterRate` (khi tòa khác biệt).
  - `Room` ghi đè qua field tùy chọn `electricityRateOverride`, `waterRateOverride`.
  - Hóa đơn đọc theo thứ tự: **room override → building override → landlord default**.
- **Lập luận:** mô hình linh hoạt chuẩn (Mona House: "giá theo phòng") — chủ trọ có thể áp khác nhau cho tầng trệt / lầu, hoặc công tơ riêng. Vẫn giữ nhập liệu tối thiểu: chỉ set **1 lần global**, tòa/phòng chỉ khai khi khác.
- **Chưa chốt (open):** đơn giá **flat** hay **bậc thang EVN** → giữ là open question #6 trong `product-sketch.md` §6.
- **Impact:** schema `LandlordProfile.default_settings` + `Building` + `Room`; feature **3.11** trong `feature-list.md` (MVP); UC-L3 rõ nguồn rate; đồng bộ mô hình Settings §3.11 `realtime-feasibility.md`.

## D17 — CCCD tại e-contract & xử lý tạm trú/tạm vắng

- **Context:** Luật Cư trú 2020 bắt chủ trọ khai báo tạm trú cho người thuê và báo tạm vắng khi họ rời. Đây là pain tuân thủ thật, nhưng khai báo điện tử đầy đủ cần tích hợp Cổng Dịch vụ công (rủi ro pháp lý/kỹ thuật, trái D7 integration-first).
- **Decision:**
  - Tại e-contract (**3.1**): chủ trọ **chụp & lưu ảnh CCCD 1 lần** cho mỗi tenant (bằng chứng định danh, phục vụ cả hợp đồng lẫn tương lai khai báo).
  - **OCR trích xuất thông tin CCCD** (số, họ tên, ngày sinh, địa chỉ) = tính năng **MVP** (nâng từ Stretch 31/08; feature **5.6**), tái dùng pipeline OCR công tơ.
  - **Khai báo tạm trú/tạm vắng đầy đủ** (tờ khai in/xuất, nộp cơ quan) = **Phase 1+**; chưa làm MVP, chờ phỏng vấn thầy (C3) xác nhận nhu cầu.
  - Không tích hợp API cơ quan nhà nước ở MVP (D7: app own dữ liệu, delegate nộp).
- **Cập nhật 29/08 (hấp thụ D27):** thầy yêu cầu research API dịch vụ công → **research spike** (P1-15): kết luận 🔴 **không có public API** cho bên thứ ba → chỉ giữ hướng thay thế "điền hộ + deep-link" cho Phase 1+. Implement tạm trú không đổi (Phase 1+), file `tam-tru-api-research.md`.
- **Impact:** `feature-list.md` 3.1 bổ sung lưu CCCD; **5.6 nâng thành MVP**; tạm trú đẩy vào Out-of-Scope/Phase 1+; `product-sketch.md` §6 thêm open question.

---

## D18 — Contract signing revamp (chữ ký số không giá trị pháp lý)

- **Context:** Thầy (27/08) chỉ ra chữ ký số/PIN/OTP trong app **không có giá trị pháp lý**. Nguyên D14 coi `e_sign` PIN là chữ ký điện tử — cần bỏ. Thầy muốn app **sinh mẫu đơn**, user up file doc đã ký (wet-sign 2 bên) để xác nhận. **31/08: bỏ luôn OTP/PIN.** Không có bất kỳ cơ chế ký điện tử nào trong app.
- **Decision (chỉ còn 1 cơ chế):**
  - **Artifact pháp lý = `template_upload`:** app sinh mẫu HĐ chuẩn (Word/PDF, điền sẵn thông tin) → 2 bên **ký tay trên giấy** → landlord **up file đã ký** → hệ thống lưu làm chứng cứ + ghi `signed_at`, `uploaded_file`. Đây là fallback thay `paper_scan` (D14 cũ).
  - **Bỏ OTP/PIN/`e_ack` hoàn toàn** (31/08): không tồn tại `e_sign`, `e_ack`, `pin_verified`, `transaction_pin_hash`, OTP SMS/FCM. Không có "soft acknowledgment" nào trong app — nếu chưa có file ký thì HĐ chưa signed.
  - App vẫn own vòng đời HĐ (trạng thái, nhắc hạn, biên bản) — tách biệt khỏi giá trị pháp lý.
- **Hấp thụ D14 (phần còn giá trị):** `signature_mode` duy nhất còn là `template_upload` (không còn enum `e_sign`/`e_ack`); "một bên từ chối ký điện tử" **không tồn tại nữa** — luôn ký giấy + up file (đúng Integration-first D7); **parse/OCR PDF → field có cấu trúc** (deposit, monthly_rent, rates, dates, terms) + giữ file gốc làm chứng cứ.
- **Impact:** `feature-list.md` 3.1 đổi cơ chế ký; `business-rules.md` §2 cập nhật; `tech-feasibility.md` schema Contract bỏ `transaction_pin_hash`/`e_ack`, `signature_mode` = enum 1 giá trị; `exit-criteria.md` bỏ cơ chế PIN.

## D20 — Dashboard chủ trọ MVP

- **Context:** Thầy (27/08) yêu cầu màn hình theo dõi lịch phòng trống/đang thuê trực quan + biểu đồ doanh thu/công nợ realtime.
- **Decision:** Đưa vào **MVP**: nâng 1.3 room-map → dashboard trực quan (occupied/vacant/maint); nâng 3.7 ledger → biểu đồ doanh thu/công nợ realtime (period grouping tháng/quý/năm). "Realtime" = refresh trên mở màn hình + FCM push sự kiện mới (chưa nhất thiết socket — xem D24).
- **Impact:** `feature-list.md` 1.3 + 3.7 → MVP; `business-rules.md` bổ sung §Dashboard.

## D21 — Ghép bạn: chủ trọ CÓ quyền set yêu cầu (hard filter), không duyệt từng cặp

- **Context:** Thầy hỏi chủ trọ có can thiệp ghép bạn không. R1 (market research) chỉ ra VN (Chợ Tốt/Phòng Trọ 123/FB groups) là P2P, chủ trọ đứng ngoài; Model (b) duyệt từng cặp vi phạm PDPD (xử lý dữ liệu cá nhân để ra quyết định) + rủi ro phân biệt đối xử.
- **Decision (làm rõ 31/08):** **Chủ trọ CÓ quyền set yêu cầu/ràng buộc cho phòng của mình** — đây là **hard filter** mà hệ thống bắt buộc áp dụng trước khi ghép: `max occupancy` (max người/phòng), `gender policy`, `house rules` (nội quy), `budget-range` (mức giá khả năng chi trả). Bất kỳ ứng viên nào vi phạm ràng buộc → **bị loại**, không vào pool match của phòng đó. **Chủ trọ KHÔNG được duyệt/veto từng cặp cá nhân** trước khi tenant tự chọn (Model a). Nếu chủ trọ KHÔNG set ràng buộc → phòng mở tự do, mọi tenant đủ điều kiện cơ bản đều vào pool.
  - Ràng buộc là **khai báo ý định của chủ trọ** (giúp tenant lọc sớm, giảm match trượt), KHÔNG phải cơ chế loại bỏ con người theo đánh giá chủ quan — đúng PDPD, tránh phân biệt đối xử.
  - Matching P2P giữa tenants + badge xác minh ID tự nguyện (D26).
- **Impact:** `feature-list.md` Module 4 cập nhật; `business-rules.md` §5 Roommate.

## D22 — HĐ ở ghép: 1 đại diện + payment config linh hoạt

- **Context:** Nhiều người ở ghép 1 phòng: ký đại diện hay từng người? Thanh toán đại diện hay chia? R1 chỉ ra VN thực tế = trưởng phòng ký + trả, chia offline.
- **Decision:**
  - **HĐ:** luôn **1 hợp đồng đại diện** (lead tenant ký với landlord) — đơn giản pháp lý, landlord chỉ dealing 1 bên.
  - **Payment:** landlord **tự cấu hình** theo từng phòng: (1) **đại diện thanh toán** (lead trả, chia offline — Model a) HOẶC (2) **hóa đơn chia sẻ** (app track phần góp từng người + trạng thái đã trả/chưa — Model c).
- **Impact:** `business-rules.md` §4 (Invoice/Payment config), `feature-list.md` Module 4.

## D24 — Realtime socket thread (chờ BE) → ✅ D24′ Property Chat Platform

- **Context:** Thầy muốn socket realtime cho thread trao đổi, muốn **hệ sinh thái giữ chân người dùng** (không ra-vào app). P1-14 feasibility hoàn tất → `discovery/realtime-feasibility.md`.
- **Decision (final):** **Property Chat Platform** (Option A′, Socket.io):
  - **2 loại Conversation:** **chat riêng phòng** (landlord ↔ tenants phòng đó) + **chat chung toà** (giao lưu + landlord nhắc tổng).
  - **Realtime display khi app mở**; **FCM push là nguồn offline** (không phụ thuộc socket); DB persistence load history (lazy-load) khi mở lại.
  - **Bot engine** (identity riêng): auto-remind theo cron (OCR-result, hóa đơn, hợp đồng hết hạn) gửi card vào chat phòng; **command `@issue`** tạo IssueReport → card → notify conversation; **mention `@user`** với autocomplete (như Messenger/Zalo).
  - **Bot/command chỉ ở chat riêng phòng**; chat chung toà chỉ text/image/file + mention.
  - **Message types MVP:** text, image, file, bot/card (voice/sticker/poll… nice-to-have).
  - **Tái dùng `IssueReport`** (open→in_progress→resolved) làm foundation cho @issue + issue panel; membership đa conversation (D13).
  - **Không dùng Zalo làm kênh sản phẩm.**
- **Effort:** ~3 tuần toàn team (1 tuần/người parallel) — **con số TBD, cần BE/FE/Mobile xác nhận** (`realtime-feasibility.md` §4). Fallback nếu effort quá: cắt `@issue`+issue-panel sang phase sau, MVP chỉ chat realtime + bot auto-remind.
- **Điều kiện teacher:** thầy đã đồng ý hướng socket; **chi tiết (conversation/bot/command) cần thầy duyệt** trước khi implement.
- **Impact:** `business-rules.md` §6, `feature-list.md` 2.7/6.6, `discovery/user_flow/` (chat per-role), DB schema (P1-18), `requirement.md` (scope).

## D25 — Ownership DB model: 1 owner per room (chốt theo ownership-model.md)

- **Context:** TH tòa 59 phòng: A sở hữu 50, B/C/D mỗi người 3; **mỗi phòng chỉ 1 chủ**. Chủ tòa nhà có thể không xác định — sở hữu xác định ở mức phòng.
- **Decision (chốt 31/08 theo `discovery/ownership-model.md`):** `Building → optional Floor → Room`, **`Room.owner_id` NOT NULL** (1 chủ / phòng). `Floor.owner_id` nullable = gợi ý/kiểm tra nhất quán, không phải nguồn chân lý (`Room.owner_id` luôn thắng). Building **không bắt buộc owner** (bỏ `manager_id` cấp building). **Bỏ Manager/delegation hoàn toàn ở MVP** — không `managerId`/`on_behalf_of`/`delegation_proof`. Cách ủy quyền `manager_id`/`ownership_shares` → Phase 1+ nếu có nhu cầu. Hợp đồng phát hành bởi `Room.owner_id` (`Contract.issued_by_user_id` NOT NULL). P1-12 BE chỉ còn là triển khai theo model này, không còn là quyết định mở.
- **Impact:** `business-rules.md` §1 cập nhật; ERD v1 bổ sung (`floors`, `rooms.floor_id`, `rooms.owner_id`, `contracts.issued_by_user_id`); backfill `owner_id` trước khi đặt NOT NULL.

## D26 — Lịch sử uy tín người thuê — Stretch

- **Context:** Thầy đề xuất lịch sử thuê để đánh giá uy tín. R1: VN không có bureau tín dụng thuê; cross-platform score vi phạm PDPD 2023.
- **Decision:** **Platform-internal history** (kỳ thuê trước trong app, thanh toán đúng hạn, review) — chỉ hiển thị khi tenant **đồng ý** + ID verification tự nguyện. **Defer** cross-platform credit. **Stretch** (không bắt buộc MVP).
- **Impact:** `feature-list.md` 2.10 (Stretch, consent); `business-rules.md` §7.

## D28 — AI matching: Stretch + spec

- **Context:** Thầy muốn làm rõ logic ghép đôi AI. Nguyên D8 giữ matching trong MVP với biên giới; quyết định mới hạ xuống **Stretch** và giao AI member viết spec (P1-13).
- **Decision:** Giữ **Stretch**; AI member viết spec luồng ghép đôi (P1-13) — input rule-filter → LLM score + advice, cache `(requester,target)`, moderation text-only.
- **Hấp thụ D8 (biên giới kỹ thuật):** scoring **hybrid rule-filter cứng TRƯỚC** → LLM score + advice cho ứng viên qua filter; **cache mỗi cặp `(requester, target)` 1 lần** (unique constraint) → ~$0.02–0.03/cặp ở quy mô demo; **moderation text-only** ở MVP (OCR ảnh = stretch); **seed ≥10 profile/khu vực**; success criteria chỉ đo trên pool seed (<15s), không cam kết growth. Rủi ro thật = **marketplace cold-start**, không phải code.
- **Impact:** `discovery/ai-matching-spec.md`; OpenAPI `/ai/matchmaking`; cập nhật theo D29 (matching chỉ chạy tenant có account).

---

## D29 — Landlord-can-operate-solo resilience (MANDATORY)

- **Context:** User non-tech (bỏ import — `feature-list.md`) + thầy muốn tăng vòng đời app. Thực tế: nhiều tenant (sinh viên/người thuê) sẽ không bao giờ login app. Cần đảm bảo hệ thống vẫn vận hành trơn tru khi **tenant KHÔNG login**.
- **Decision (NGUYÊN TẮC BẮT BUỘC):** hệ thống **PHẢI** vận hành được với **zero tenant login**. Landlord làm toàn bộ vòng đời một mình: tạo HĐ (D18), up CCCD (D17), chốt số điện nước (OCR), xuất hóa đơn, đẩy cho tenant qua **dynamic-QR (quét bằng app ngân hàng bất kỳ) / tiền mặt / giấy / kênh ngoài**, đối soát. Tenant touchpoints delegated — tenant app là **optional/passive**, không bắt buộc.
- **Roommate matching (D21/D28) không bị ảnh hưởng:** chỉ chạy cho tenant **CÓ account**; tenant không account = vắng mặt khỏi pool (edge case bình thường, không blocker).
- **Impact:** `requirement.md` (scope), `business-rules.md` §8, `feature-list.md`, `product-sketch.md`; stress-test chi tiết tại **Phụ lục B** bên dưới; P1-13 cập nhật theo D29.

---

# Phụ lục — Decision Graph & Landlord-Solo Resilience (D29)

> Tổng hợp cho trao đổi với thầy + design-principle D29.
> Xâu chuỗi D1–D29 thành một narrative; stress-test kịch bản "tenant không login".
> Nguồn: `requirement.md`, `feature-list.md`, `decisions.md` (D1–D29), `market-roommate-models.md`, `short-vs-long-term-analysis.md`.

## A. Decision Spine (D1 → D29)

Các quyết định tạo thành một chuỗi thống nhất, không phải lựa chọn rời rạc:

1. **D1 (two-sided)** đặt tầm nhìn: landlord ops + tenant portal trong cùng vòng đời — spine mọi thứ treo vào.
2. **Integration-first** (xem `requirement.md` / `vision.md` §5) → own data/compute (OCR, hóa đơn, QR recon); giao tiếp nghiệp vụ qua **Property Chat (D24′)**; FCM là kênh thông báo. Bật khả năng cho **D29** (tenant ở ngoài app của ta).
3. **D9 (long-term-only)** → loại ngắn hạn; chứng minh bất khả thi (analysis doc, hấp thụ D23). Schema mở (`property_type`).
4. **D13 (cross-platform roles)** → web + mobile đều phục vụ landlord & tenant (primary/secondary staged).
5. **D18 (contract signing, hấp thụ D14)** → thầy: chữ ký số/OTP không giá trị pháp lý → app sinh mẫu HĐ, user up file **ký tay 2 bên** (wet-sign) làm artifact; **bỏ OTP/PIN hoàn toàn** (31/08).
6. **D4 → D22 (shared rooms)** → luôn 1 HĐ đại diện (lead ký); landlord config payment = rep-payer (chia offline) HOẶC shared-invoice tracking (app ghi phần góp + trạng thái trả); full bill-splitting deferred (D4).
7. **D24 (Property Chat & realtime)** → **D24′ Property Chat Platform** (Socket.io): chat riêng phòng + chat chung toà, bot auto-remind, `@issue`, `@mention`; FCM là offline channel, DB persistence khi mở lại. Không dùng Zalo làm kênh sản phẩm.
8. **D28 (AI matching, hấp thụ D8)** → Stretch; spec do AI (P1-13). Chỉ chạy cho tenant opted-in.
9. **D21 (landlord CÓ quyền set yêu cầu)** → landlord set hard-filter ràng buộc phòng (occupancy/gender/rules/budget), không vet từng cá nhân (PDPD-safe).
10. **D26 (tenant history)** → platform-internal, consent-based; không cross-platform credit (PDPD 2023). Đã chốt **Stretch**.
11. **Bỏ import** (xem `feature-list.md` 1.6/6.6) + **D20 (dashboard chủ trọ)** → focus landlord non-tech; realtime occupancy/revenue/debt dashboard.
12. **D25 (ownership, chốt theo `ownership-model.md`)** → nhiều chủ trên 1 tòa, **1 chủ / phòng** (`Room.ownerId` NOT NULL); Floor optional; **bỏ manager/delegation trong MVP**.
13. **D17 (tạm trú; research spike P1-15)** → research spike only; implement Phase 1+.
14. **D29 (resilience, mandatory)** → nối tất cả: hệ thống sống sót khi tenant không bao giờ login.

## B. Stress-Test — Landlord vận hành một mình (D29)

| Module | Behavior khi tenant KHÔNG login | Hard dep vào tenant login? |
|--------|---------------------------------|---------------------------|
| Room / Building | Landlord CRUD bình thường | ❌ |
| Contract (D18) | Landlord tạo, sinh mẫu HĐ, up file đã ký; tenant không cần app | ❌ |
| Utility closing | Landlord chốt số (OCR) bình thường | ❌ |
| Invoice / Payment (D22) | Landlord xuất hóa đơn + dynamic-QR; tenant quét QR bằng app ngân hàng bất kỳ hoặc trả tiền mặt; landlord đối soát | ❌ (QR/cash, không cần login app mình) |
| Issue reporting | Landlord tạo/tracker; **chat riêng phòng (realtime + bot @issue)** nếu tenant login, còn không → bot/notification qua FCM + kênh ngoài app | ❌ (FCM + DB persistence, không phụ thuộc socket) |
| Roommate / AI (D21/D28) | Chỉ chạy cho tenant CÓ account; tenant không account = vắng mặt pool (edge case, không blocker) | ⚠️ chỉ với opted-in tenant (by design) |
| Dashboard (D20) | Thuần landlord | ❌ |
| Tạm trú (D17) | Landlord làm thay (research API) | ❌ |

**Kết luận:** Không có hard-dependency vào tenant login. D29 thoả — hệ thống vận hành trọn vòng đời chỉ với landlord.

## C. D29 — Formal Statement

- **Principle (MANDATORY):** The platform MUST function with **zero tenant logins**. Landlord manages the full lifecycle solo.
- **Tenant touchpoints delegated:** dynamic-QR (scanned by any banking app), cash, paper, kênh ngoài app.
- **Tenant app = optional / passive** — never a blocker for landlord operations.
- **Roommate matching unaffected** — runs for opted-in tenants; passive tenants simply absent from the pool.

## D. Talking Points cho thầy

- User non-tech (bỏ import) → resilience là **điểm mạnh**, không phải thiếu sót: landlord-first ops, tenant optional.
- Thể hiện sự trưởng thành về SE: **graceful degradation** — hệ thống không sập khi một phía (tenant) vắng mặt.
- Vẫn giữ định vị hai chiều (D1): khi tenant CÓ account, họ được trải nghiệm đầy đủ (tìm phòng, thanh toán QR, ghép bạn AI).

## E. Open / Risk

- Nếu tỉ lệ tenant passive cao → matching pool nhỏ (cold-start) → mitigate bằng seed data demo (D28).
- Cần test kịch bản "landlord-only" trong demo (M3/M4) để chứng minh D29 trước thầy.