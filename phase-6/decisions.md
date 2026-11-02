# Decisions Log — Phase 6

> Quyết định phát sinh trong Phase 6 (It5–It7) được ghi tại đây. ID tăng dần, **không renumber/reuse** (`pm/AGENTS.md`).
> Phase 0 (D1–D29): `../phase-0/discovery/decisions.md` · Phase 1 (D30–D39): `../phase-1/discovery/decisions.md` · Phase 2 (D39–D50): `../phase-2/discovery/decisions.md` · Phase 3 (D51–D59): `../phase-3/discovery/decisions.md`.

> Published **P6-D60** remains in [discovery/decisions.md](discovery/decisions.md). It defines atomic bulk requests and baseline inputs. This log continues with D61–D76; D75 is the source-precedence decision. No published ID is renumbered.

## Quy ước trích dẫn (áp dụng từ Phase 6)

- **Luôn ghi tiền tố phase khi trích quyết định:** `P1-D39`, `P2-D47`, `P3-D51`, `P6-D61`. Lý do: **D39 bị trùng** — `P1-D39` là billing (RatePolicy 1 bộ/scope, Invoice `pending|issued|void`, không cưỡng chế thu tiền), `P2-D39` là vòng đời tài khoản user. ID cũ giữ nguyên, không đổi.
- Issue, PR, comment review chỉ được nói "theo quyết định" khi trỏ tới một ID ở đây hoặc ở log các phase trước.

## Index

| ID | Ngày | Quyết định | Trạng thái |
|---|---|---|---|
| D61 | 2026-11-01 | Payment (tiền mặt/mock) và quyết toán cọc ra khỏi MVP → Stretch | ✅ Accepted |
| D62 | 2026-11-01 | Checkout: HĐ → `terminated`, member tự rời, phòng → `maintenance` rồi `mark-ready` | ✅ Accepted |
| D63 | 2026-11-01 | Thành viên HĐ: đại diện tự thành member khi activate; DTO thêm member khớp bảng `contract_members` | ✅ Accepted |
| D64 | 2026-11-01 | Invoice: sinh theo yêu cầu (theo tòa + kỳ), `pending` tính lại được, `issued` bất biến, không có hóa đơn quyết toán riêng | ✅ Accepted |
| D65 | 2026-11-01 | Quy tắc tính tiền hóa đơn còn bỏ ngỏ: `headCount`, xe, làm tròn, mã hóa đơn | ✅ Accepted |
| D66 | 2026-11-01 | MeterReading: giữ bulk, khóa sửa khi kỳ đã phát hành, ảnh minh chứng gắn sau qua Media, thêm `source`/`ocrValue` | ✅ Accepted |
| D67 | 2026-11-01 | OCR chỉ số công tơ chạy ở `ai-service` riêng (vision LLM), chỉ gợi ý — thay `P3-D51` | ✅ Accepted |
| D68 | 2026-11-01 | Field tạo HĐ chốt theo code đã merge: bỏ `rentalType`, `tenantCccd`, `paymentDueDay` khỏi Contract | ✅ Accepted |
| D69 | 2026-11-01 | Media của entity chưa tồn tại: tạo entity trước, upload sau với `ownerId` thật; Tenancy phải có `GET /internal/ownership` | ✅ Accepted |
| D70 | 2026-11-01 | MeterReading chi tiết: baseline không tính vào unique kỳ, `PATCH` reading mới nhất, giữ `evidenceMediaId` (sửa D66) | ✅ Accepted |
| D71 | 2026-11-01 | Contract/member: sửa `vehicleCount` khi `active`, khoảng ngày hợp lệ, chống trùng member, `status` member suy ra | ✅ Accepted |
| D72 | 2026-11-01 | Invoice chi tiết: độ chính xác dòng, thiếu mục điện/nước, `void_reason`, bỏ `sendNotification`/VietQR | ✅ Accepted |
| D73 | 2026-11-01 | Ownership nội bộ: `participantUserIds`/`status` theo owner type; Identity có `GET /internal/media/{id}` | ✅ Accepted |
| D74 | 2026-11-01 | Liên kết tài khoản tenant trên web để Stretch; form chỉ nhập họ tên + SĐT | ✅ Accepted |
| D75 | 2026-11-01 | Thứ tự ưu tiên nguồn khi mâu thuẫn + mọi câu hỏi mở phải có D-ID trước khi giao việc | ✅ Accepted |
| D76 | 2026-11-02 | Snapshot display name trên ConversationMember và Message | ✅ Accepted |

---


## D61 — Payment và quyết toán cọc ra khỏi MVP

- **Bối cảnh:** Chưa có `payment-service`; `P3-D52`/`P3-D57` chỉ ở trạng thái Proposed. Quyết toán cọc theo `database-design.md` §2.13 là một bản ghi `Payment` (`invoice_id NULL`, `contract_id`), nên phụ thuộc Payment.
- **Quyết định:**
  - P6-05 (thanh toán tiền mặt/mock) chuyển **Stretch**. Không tạo payment-service, không tạo module payment trong Tenancy ở Phase 6.
  - `POST /contracts/{id}/deposit-settlement` chuyển **Stretch** cùng Payment. **Không thêm cột** nào vào `contracts` — DB design hiện tại đã đủ.
  - Demo dừng ở bước **phát hành hóa đơn** (`issued`). Không có trạng thái "đã thu" ở bất kỳ màn nào.
  - Tiền đền bù hư hại khi trả phòng thu qua `other_fees` của hóa đơn kỳ cuối (`P1-D33` cho phép dòng âm/dương).
- **Hệ quả:** `api-docs` đánh dấu `x-apidog-status: deprecated` (hoặc gỡ) các path `payments/*`, `deposit-settlement`; FE không làm màn thu tiền. `P1-D39` "trạng thái thu suy ra từ Σ Payment" giữ nguyên, chỉ chưa triển khai.

## D62 — Checkout

- **Bối cảnh:** `contracts-contractId-complete-checkout.yaml` mô tả phòng chuyển `pending_cleanup` và trả ví dụ `status: expired`; `RoomStatus` (code + `database-design.md` §2.5) chỉ có `available | occupied | maintenance`; outline P6-01e nói `terminated`.
- **Quyết định:**
  - Điều kiện checkout: HĐ đang `active` **và** hóa đơn của kỳ chứa ngày trả phòng đã `issued` (không còn bản `pending` của kỳ đó). Không đạt → `409 SETTLEMENT_NOT_READY`.
  - Checkout `{ completedOn }`: HĐ → **`terminated`**; mọi member còn ở set `left_at = completedOn`; phòng → **`maintenance`**. Landlord bấm `POST /rooms/{id}/mark-ready` (đã có, P5-09c) để phòng về `available`.
  - Không có phí chấm dứt sớm, không tự prorate tiền phòng theo ngày trả — chênh lệch ghi bằng `other_fees` (D64).
  - Phòng có 2 HĐ trong cùng một kỳ (trả phòng rồi có khách mới trong cùng tháng) là **ngoài MVP**: HĐ mới bắt đầu từ kỳ sau.
- **Hệ quả:** `api-docs` bỏ `pending_cleanup`, sửa ví dụ thành `terminated`.

## D63 — Thành viên hợp đồng

- **Bối cảnh:** `ContractMemberAddRequestDto` (`api-docs/src/requests/contracts/contract-member-add-request-dto.yaml`) có `identityCardNumber`, `dateOfBirth`, `gender`, `isRepresentative` — bảng `contract_members` (`database-design.md` §2.8) không có các cột này; CCCD lưu bằng ảnh `Media` (`P0-D17`). UI LL-17 nói các member ngang hàng, `P0-D22` nói một người đại diện ký.
- **Quyết định:**
  - Khi HĐ **activate**, người đại diện (`contracts.tenant_id/tenant_name/tenant_phone`) **tự được thêm** làm `contract_members` với `joined_at = start_date`. Đại diện chỉ khác member khác ở chỗ đứng tên trên Contract; trong danh sách member không có cờ riêng.
  - Thêm/rời member chỉ khi HĐ `active` (ngược lại `409 CONTRACT_NOT_ACTIVE`). Rời = set `left_at`, **không xóa bản ghi** (`P2-D44`).
  - `ContractMemberAddRequestDto` còn: `contractId`, `tenantId?`, `tenantName`, `tenantPhone?`, `joinedAt`. Bỏ `identityCardNumber`, `dateOfBirth`, `gender`, `isRepresentative`.
  - Tenant được liên kết **chỉ qua `tenantId`** (landlord chọn user có sẵn). Tự liên kết theo số điện thoại là Stretch. Ảnh CCCD member là Stretch.
  - `GET /me/contracts` trả HĐ mà user là `contracts.tenant_id` **hoặc** là `contract_members.tenant_id` chưa rời.

## D64 — Vòng đời hóa đơn

- **Bối cảnh:** `P1-D33②` muốn tự sinh `pending` từng phòng khi đủ chỉ số (event-driven); calc doc §10 gọi `promptOtherFees()` ngay trong luồng sinh (không làm được khi tự động); `createSettlementInvoice` dùng cùng `(contract_id, period)` với hóa đơn tháng nên đụng partial unique index (§2.12); UI LL-21b cho sửa hóa đơn đã phát hành, trái `P1-D37`.
- **Quyết định:**
  - **Sinh theo yêu cầu**, không dùng event: `POST /invoices/generate { buildingId, period }`. Với mỗi HĐ `active` trong tòa có hiệu lực trong kỳ: đủ dữ kiện → tạo hoặc **tính lại** bản `pending`; thiếu dữ kiện → trả trong danh sách `blocked[] { roomId, contractId, reasonCode }` (thay "danh sách chờ sửa lỗi" của `P1-D34`, không lưu bảng riêng).
  - `pending` sửa được: thêm/xóa `other_fees`, `note`. Gọi generate lại thì tính lại phần điện/nước/phí/tiền phòng nhưng **giữ `other_fees` và `note`**.
  - `issued` **bất biến**. Sai thì `void` rồi generate lại → bản mới có `voided_invoice_id` trỏ bản cũ (`P1-D37`). Không làm "sửa sau khi phát hành" của LL-21b.
  - Trạng thái chỉ `pending | issued | void` (`P1-D39`). Gỡ `GET /invoices/overdue-debts`, `POST /invoices/send-reminder`.
  - **Không có hóa đơn quyết toán riêng**, không thêm cột `type`. Kỳ trả phòng chỉ có hóa đơn tháng bình thường; chênh lệch tiền phòng/đền bù ghi bằng `other_fees`. Gỡ `createSettlementInvoice` (`POST /invoices`).
  - Phát hành hàng loạt `POST /invoices/issue-invoice` theo `P2-D43` (kết quả từng hóa đơn, `Idempotency-Key`).
  - Tenant xem qua **`GET /me/invoices`** và `GET /invoices/{id}` (`P2-D48`); gỡ `GET /invoices/tenant`. Tenant chỉ thấy hóa đơn `issued`.

## D65 — Quy tắc tính tiền còn bỏ ngỏ

- **Bối cảnh:** `utility-billing-calculations.md` §3 đếm member theo `is_deleted=false`, còn `database-design.md` §2.8 đếm theo khoảng ở; §13 nói xe nhập mỗi kỳ, `P1-D32` nói `contract.vehicle_count`; `roundMoney` chưa định nghĩa; §10 dùng `contract.monthly_rent` nhưng cột là `rent_price`.
- **Quyết định:**
  - `headCount` = số member có `joined_at ≤ cuối kỳ` và (`left_at IS NULL` hoặc `left_at ≥ đầu kỳ`) — theo §2.8.
  - Số xe = `contracts.vehicle_count` (`P1-D32`); `NULL` khi có phí `per_vehicle` → `VEHICLE_COUNT_MISSING`.
  - Tiền phòng = `rent_price × prorateRatio` theo calc §8, dùng `start_date`/`end_date` của HĐ (không dùng ngày checkout).
  - Làm tròn theo **EC14**: các dòng giữ số chính xác (decimal), **chỉ làm tròn `total_amount`** về số nguyên đồng, kiểu half-up.
  - Mã hóa đơn `INV-YYYYMM-XXXX`, `XXXX` = 4 ký tự ngẫu nhiên `[A-Z0-9]`, unique toàn hệ thống; trùng thì sinh lại (tối đa 5 lần).
  - Mọi số tiền và chỉ số dùng `numeric` trong DB, string trong DTO/JSON, thư viện decimal trong code — cấm `number` cho tiền.

## D66 — MeterReading

- **Bối cảnh:** `P2-D47` (Pending) nói không làm bulk, nhưng P6-02f đã giao trong It5. Nhánh `feature/p6-02e-meter-reading` có `buildingId`, `evidenceMediaId`, thiếu migration; `api-docs` có `readingDate` mà code không có. Media `meter_reading_evidence` đòi `ownerId` = id của reading (D69), nên không thể có `evidenceMediaId` lúc tạo.
- **Quyết định:**
  - **Giữ bulk** (`POST /meter-readings/bulk`, P6-02f) — quyết định này ghi đè `P2-D47`.
  - ~~Bỏ `evidenceMediaId` khỏi reading~~ — **sửa bởi D70**: giữ `evidenceMediaId` nullable, gắn bằng `PATCH` sau khi upload. Ảnh minh chứng là `Media(owner_type='meter_reading', owner_id=<readingId>, purpose='meter_reading_evidence')`, upload **sau** khi tạo reading. Bắt buộc có ảnh (`P1-D35`) do FE đảm bảo trong MVP.
  - Thêm `source: manual | ocr` (mặc định `manual`) và `ocrValue?` (số AI gợi ý, để audit; khác `currentReading` khi người dùng sửa tay).
  - Giữ `buildingId` (lọc theo tòa, bulk). Bỏ `readingDate` khỏi `api-docs`; kỳ (`period`) là khóa.
  - Reading của một phòng/kỳ **chỉ sửa/xóa được khi kỳ đó chưa có hóa đơn `issued`** cho HĐ của phòng (`409 PERIOD_ALREADY_INVOICED`).

## D67 — OCR qua `ai-service`

- **Bối cảnh:** `P3-D51` (Pending) bỏ AI, dự định chạy Tesseract trong Tenancy. Tesseract đọc kém số công tơ cơ (bánh xe số) và 7 đoạn. Lead chốt làm OCR trong It6 bằng một AI service riêng.
- **Quyết định:**
  - Repo mới **`ai-service`** (NestJS, fork `boilerplate`, **không DB**, không outbox), cổng **3005** (3003/3004 đã dành cho payment/community trong `infra`; Security Group nội bộ mở rộng thành `3001-3005`), chạy trên host internal, đi qua gateway prefix `/api/v1/ai`.
  - Luồng: **FE chụp ảnh → `POST /api/v1/ai/meter-readings/ocr` (multipart) → hiện số gợi ý → người dùng xác nhận/sửa → `POST /meter-readings` (Tenancy, `source='ocr'`, `ocrValue`) → upload ảnh minh chứng (D66)**.
  - Engine: vision LLM (Claude Haiku, structured output `{ value: string | null, confidence: number }`). API key chỉ nằm ở `ai-service`.
  - Giới hạn: ảnh JPEG/PNG/WebP ≤ 5 MB, timeout 15 s, rate limit ở gateway. Lỗi/timeout/`value=null` → FE chuyển nhập tay (`P1-D35`).
  - AI chỉ gợi ý. Tenancy **không gọi** `ai-service` và vẫn tự kiểm tra `current ≥ previous` (EC1).
  - Gỡ `meter-readings-preview-ocr-result` khỏi Tenancy trong `api-docs`, thêm `paths/ai/`.
- **Hệ quả:** `P3-D51` → Superseded by `P6-D67`. `ai-service` sau này có thể chứa AI Auto-Description (`requirement.md`).

## D68 — Field tạo hợp đồng

- **Bối cảnh:** Mục #3 bảng chốt It5 (P6-01): `rentalType: DAILY` trái `P0-D9`, `tenantCccd` không có cột, `paymentDueDay` trùng `BillingSetting`. Code P6-01b đã merge (`Tenancy-Service` `c7f6258`) không có 3 field này.
- **Quyết định:** chốt theo code: bỏ `rentalType`, `tenantCccd`, `paymentDueDay` khỏi `ContractCreateRequestDto`/`ContractUpdateRequestDto`. Ngày thu chỉ ở `BillingSetting.payment_due_day`. `templateKey`/`templateVariables` chỉ đổi qua `apply-template` (P6-01c).

## D69 — Media cho entity chưa tồn tại

- **Bối cảnh:** Mục #1 bảng chốt It5. Code P6-04 (`Identity-Service` `964592c`) bắt buộc `ownerId`; FE (`fe/src/features/buildings/hooks/use-ownership-proof-uploader.ts`) đã làm theo cách tạo Building trước rồi upload. Identity kiểm tra quyền qua `TenancyOwnerResolver` gọi `GET /internal/ownership/{ownerType}/{ownerId}`, nhưng **Tenancy chưa có endpoint này**.
- **Quyết định:**
  - Phương án B: **tạo entity trước, upload sau** với `ownerId` thật — áp dụng cho Building (`ownership_proof`), Contract (`contract_signed`), MeterReading (`meter_reading_evidence`).
  - Tenancy thêm `GET /internal/ownership/{ownerType}/{ownerId}` (`@InternalOnly()`), trả `{ landlordId, participantUserIds, status }` cho `building`, `room`, `contract`, `contract_member`, `meter_reading`; không tìm thấy → `404`. Giao ở **P6-11**.

## D70 — MeterReading: baseline, sửa reading, ảnh minh chứng

- **Bối cảnh:** P6-02e (merged `6251329`) lưu baseline với `previous = current` và UNIQUE `(room_id, type, period)` → kỳ có baseline không nhập thêm được reading, điện/nước kỳ đầu luôn 0, trái calc §8. `api-docs` và code chưa có `PATCH`/`DELETE`. FE không biết reading đã có ảnh sau khi tải lại vì D66 bỏ `evidenceMediaId` và Media không có API liệt kê theo owner. Bulk chưa định nghĩa trường hợp phòng chưa có baseline. Bảng `meter_readings` chưa có migration.
- **Quyết định:**
  - UNIQUE thành **partial** `(room_id, type, period) WHERE is_baseline = false AND is_deleted = false`. Kỳ đầu: reading chốt tháng lấy `previous_reading` = `current_reading` của baseline cùng phòng/loại → tiêu thụ thực từ ngày bàn giao.
  - `PATCH /meter-readings/{id}` nhận `currentReading?`, `evidenceMediaId?`. Chỉ sửa được reading **mới nhất** của phòng + loại (`409 METER_READING_NOT_LATEST`) và kỳ chưa có hóa đơn `issued` (`409 PERIOD_ALREADY_INVOICED`). Không có `DELETE` trong MVP.
  - **Giữ** cột `evidence_media_id` nullable: FE upload ảnh (owner = reading) rồi `PATCH { evidenceMediaId }`. Response reading trả `evidenceMediaId` để FE biết đã có ảnh.
  - Bulk remains **atomic** under [P6-D60](discovery/decisions.md): a missing baseline returns `BASELINE_REQUIRED` and rolls back the entire request. Successful responses contain only `SUCCESS` results; no partial persistence or `WARNING` result. PM reaffirmed this on 2026-11-01 when reconciling PR #94.
  - Migration `meter_readings` được sinh ở P6-02h, phải merge trước P6-02g2.

## D71 — Contract và member: dữ liệu và ràng buộc

- **Bối cảnh:** `P1-D32` cho sửa số xe giữa kỳ, nhưng `PATCH /contracts/{id}` trả `409 CONTRACT_NOT_DRAFT` khi HĐ `active` → không gỡ được `VEHICLE_COUNT_MISSING`. `ContractMemberListResponseDto` có `status: ACTIVE|TEMPORARY_ABSENT|LEFT` không có cột tương ứng. Chưa có rule khoảng ngày và chống trùng member.
- **Quyết định:**
  - HĐ `active` chỉ sửa được `vehicleCount` và `description`; field khác vẫn `409 CONTRACT_NOT_DRAFT`. Hóa đơn `pending` dùng số mới khi generate lại; `issued` giữ snapshot (`P1-D32`).
  - `joinedAt` ∈ `[start_date, end_date]` của HĐ. `leftOn` ≥ `joinedAt` và ≤ `end_date`. Checkout `completedOn` ≥ `start_date` và ≤ hôm nay (không trả phòng ngày tương lai). Sai → `422 LEFT_DATE_INVALID` / `VALIDATION_FAILED` theo `api-docs`.
  - `MEMBER_ALREADY_EXISTS` khi trong cùng HĐ đã có member **chưa rời** trùng `tenantId` (nếu có) hoặc trùng `tenantPhone` (nếu có).
  - Member `status` suy ra: `active` khi `left_at IS NULL` hoặc `left_at > hôm nay`, ngược lại `left`. Bỏ `TEMPORARY_ABSENT`, `identityCardNumber`, `isRepresentative` khỏi response.
  - `ContractDetailResponseDto` trả thêm `templateKey`, `draftDocumentMediaId`, `signedContractMediaId`, `roomName`, `buildingId` (P6-01c/d bổ sung, P6-09 cập nhật `api-docs`).

## D72 — Invoice: chi tiết tính và hủy

- **Bối cảnh:** Prorate tạo số lẻ vô hạn (16/30); EC14 chỉ làm tròn tổng nên `Σ dòng ≠ total_amount`. Bộ rate thiếu mục điện/nước chưa định nghĩa. `InvoiceCancelRequestDto.reason` bắt buộc nhưng bảng không có cột. `InvoiceIssueRequestDto.sendNotification` và `vietQrContent` gắn với tính năng đã hoãn.
- **Quyết định:**
  - Số tiền từng dòng lưu `numeric(14,4)`, làm tròn half-up tới 4 chữ số; `total_amount` = round half-up về đồng của Σ dòng. Bất biến kiểm tra là `total_amount = round(Σ dòng)`, không phải `Σ dòng = total_amount`.
  - Bộ rate resolve được nhưng thiếu mục `electricity` hoặc `water` → chặn `RATE_MISSING`.
  - Thêm cột `void_reason text NULL`; `cancel-invoice` bắt buộc `reason` (1–500 ký tự).
  - Bỏ `sendNotification` khỏi `InvoiceIssueRequestDto` và `vietQrContent` khỏi response (Notification là Stretch, VietQR theo `P6-D61`). Web không hiển thị QR.

## D73 — Ownership nội bộ và tra cứu media

- **Bối cảnh:** `P6-D69` chưa định nghĩa `participantUserIds`/`status` cho từng owner type. P6-01d cần kiểm tra file bản ký nhưng Identity chưa có `GET /internal/media/{id}`.
- **Quyết định:**
  - `GET /internal/ownership/{ownerType}/{ownerId}`:
    - `building` → `landlordId`, participants rỗng, `status` = trạng thái duyệt của tòa.
    - `room` → `landlordId` của tòa, participants rỗng, `status` = `room.status`.
    - `contract` → `landlordId`, participants = `tenant_id` của HĐ + `tenant_id` member chưa rời (bỏ `NULL`), `status` = `contract.status`.
    - `contract_member` → như `contract` của member đó.
    - `meter_reading` → `landlordId`, participants = người tham gia HĐ `active` của phòng (để tenant tự chụp sau này), `status` = `null`.
  - Identity thêm `GET /internal/media/{mediaId}` (`@InternalOnly()`) trả `{ id, ownerType, ownerId, purpose, status }` — giao ở **P6-12**. Tenancy dùng để kiểm tra `signedContractMediaId` khi activate (P6-01d).

## D74 — Liên kết tài khoản tenant

- **Bối cảnh:** `P6-D63` nói landlord chọn user có sẵn (`tenantId`), nhưng landlord không có API tìm user (`GET /users` chỉ cho admin).
- **Quyết định:** Phase 6 web **không** có ô chọn tài khoản tenant; form HĐ và member chỉ nhập họ tên + SĐT, `tenantId = NULL` (`P0-D29`). `tenantId` chỉ có từ seed demo. Tự liên kết theo SĐT (qua Identity `GET /internal/users`) là Stretch. `GET /me/contracts`, `/me/invoices` vẫn làm cho mobile và dữ liệu seed.

> **Bổ sung D71 (2026-11-01):** giới hạn `leftOn ≤ end_date` chỉ áp dụng cho `leave-contract`; checkout sau `end_date` vẫn hợp lệ và set `left_at = completedOn` cho mọi member.


## D75 — Thứ tự ưu tiên nguồn và cách xử lý câu hỏi mở

- **Bối cảnh:** Iteration 4–5 có nhiều PR bị tranh cãi vì issue, `api-docs`, `database-design.md` và review nói ngược nhau (vd. Tenancy-Service #13, #14: "issue lỏ đó", "đáng ra sửa ở api doc"). Bảng "Chốt trước khi bắt đầu It5" trong `issues/README.md` có 6 mục nhưng không mục nào có ID.
- **Quyết định:**
  1. Khi các nguồn mâu thuẫn, thứ tự ưu tiên là: **`decisions.md` (D-ID mới nhất) > `api-docs` > skill của repo (`.agents/skills/`) > nội dung issue**. Dev gặp mâu thuẫn thì comment vào issue, làm theo nguồn cao hơn, không tự chế phương án thứ ba.
  2. Issue **không tự đặt business rule mới**. Câu hỏi nghiệp vụ phải được chốt thành D-ID trước khi issue được giao; issue chỉ trích ID.
  3. Issue **không mô tả cách viết code** (đặt file ở đâu, đặt tên gì) ngoài việc link skill; skill là nơi duy nhất giữ convention.
- **Hệ quả:** `_TEMPLATE.md` thêm mục "Quyết định áp dụng"; mỗi repo backend có `AGENTS.md` + `.agents/skills/` (nguồn: `boilerplate`).

## D76 — Snapshot tên người gửi trong chat

- **Bối cảnh:** `GET /conversations` hiển thị `lastMessage.senderName`, nhưng Message chỉ lưu `senderMemberId`. Gọi Identity mỗi lần tải danh sách thêm độ trễ và phụ thuộc runtime; client cũng không được tự gửi tên người khác.
- **Quyết định:**
  - Lưu `displayName` trên `ConversationMember`. Community lấy tên từ Identity internal lookup khi thêm hoặc kích hoạt lại member; client không được tự cung cấp tên.
  - Khi tạo message, lưu `senderNameSnapshot` bằng `ConversationMember.displayName` của sender. Snapshot message không đổi khi hồ sơ user đổi tên.
  - List/detail members trả `displayName`; conversation list lấy `lastMessage.senderName` từ Message snapshot, không gọi Identity.
  - Khi member được kích hoạt lại, cập nhật `displayName` theo Identity; message cũ giữ nguyên snapshot.
- **Hệ quả:** P7-07, P7-09 và consumer đồng bộ membership phải điền `displayName`; P7-13 phải copy snapshot vào Message. Schema Community cần migration thêm `conversation_members.display_name` và `messages.sender_name_snapshot`.
