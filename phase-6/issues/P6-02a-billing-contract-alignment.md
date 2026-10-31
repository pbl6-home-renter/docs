# P6-02a — Chốt contract Billing theo D39

**Epic:** [P6-02](P6-02-tenancy-billing-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** huynhtiennhat0403  
**Người review:** baoduong17 (API owner) — **bắt buộc approve trước khi code P6-02b/d/e**  
**Ước lượng:** 2 points · 4–6 giờ  
**Phụ thuộc:** —  
**Repo / branch:** `api-doc` · `docs/p6-02a-billing-contract`  
**Issue:** `docs#71`

## Mục tiêu

Contract RatePolicy / BillingSetting / MeterReading trong `api-doc` nhất quán với nhau và với `database-design.md` §2.9–§2.11 (D39), để P6-02b → P6-02f code theo một nguồn duy nhất.

## Contract hiện tại và các mâu thuẫn đã phát hiện

| # | Chỗ | Vấn đề | Đề xuất (API owner chốt) |
|---|---|---|---|
| 1 | `src/schemas/billing/rate-policy.yaml` vs `src/requests/rooms/rate-policy-create-request-dto.yaml` | Schema domain = **1 bộ/scope chứa `rates[]`** (D39); request tạo lại là **1 mục giá đơn lẻ** (`type`, `rateKind`, `steps`), thiếu `unitPrice`, `billingUnit`, và **thiếu `buildingId`** (không tạo được bộ scope `building`). | Request `RatePolicyCreateRequestDto` = `{ scope, buildingId?, roomId?, rates: RateItem[] }` (bắt `buildingId` khi `scope=building`, `roomId` khi `scope=room`). |
| 2 | `src/requests/buildings/building-rate-policies-batch-create-request-dto.yaml` | Enum khác hẳn: `category` (`ELECTRICITY`, `INTERNET`, `TRASH`…), `rateKind` (`FLAT`, `PROGRESSIVE`, `PER_PERSON`, `PER_ROOM`), bậc `fromStep/toStep/stepPrice`. | Dùng chung `RateItem` của #1 (enum chữ thường như DB). Batch = **upsert bộ scope building** của tòa trên path (bước 3 wizard). |
| 3 | `RateItem` (mới, đặt tại `src/schemas/billing/rate-item.yaml`) | Chưa tồn tại riêng. | `{ type, name (1–100), rateKind, unitPrice (string decimal, null nếu tiered), steps ([{from,to,price}] chỉ khi tiered, `to=null` ở bậc cuối), billingUnit }` theo shape `rates[]` §2.9. |
| 4 | `src/requests/rooms/rate-policy-update-request-dto.yaml` + `rate-policies-ratePolicyId.yaml` | PATCH chỉ "đổi tên" nhưng bộ (set) không có `name`; D39 yêu cầu **đổi giá = UPDATE tại chỗ**. | Body `{ rates?: RateItem[], isActive?: boolean }`, `minProperties: 1`. Bỏ `RATE_POLICY_LOCKED` (D39 không khóa; hóa đơn đã phát hành giữ snapshot). |
| 5 | Response DTO `rate-policy-create/list/update/deactivate-response-dto.yaml` | Trả từng mục (`type`, `rateKind`) thay vì bộ. | Trả `{ id, landlordId, scope, buildingId, roomId, rates, isActive, createdAt, updatedAt }`. |
| 6 | Lỗi RatePolicy | `422 INVALID_RATE_KIND` chỉ có trong description. | Khai báo enum lỗi `422`: `INVALID_RATE_KIND` (D33: điện chỉ `flat`/`tiered`; `per_head` chỉ cho nước/phí), `TIER_CONFIG_INVALID` (tiered thiếu `steps` / bậc cuối `to≠null` / bậc không liên tục), `VALIDATION_FAILED`. `409 ACTIVE_POLICY_EXISTS` khi scope đã có bộ (kể cả đang tắt → dùng PATCH `isActive: true`). |
| 7 | `src/requests/rooms/billing-setting-create-request-dto.yaml` (+ update, response) | Có `dueDays`, `debtScanEnabled`, `gracePeriodDays`, `overdueReminderIntervalDays`, `reminderChannels`, `meterCutoffDay`, `invoiceIssuanceDay` — **trái D39** (không cưỡng chế thu, không `overdue`) và không có trong bảng `billing_settings`. | Create = `{ scope, buildingId?, roomId?, paymentDueDay (1–28, default 5), remindDay? (1–28), botEnabled (default true) }`; Update = cùng field trừ scope/target + `isActive`. Response trả đủ các field này. **P6-02d đã chốt:** hai ngày độc lập, không dùng `DUE_DAYS_INVALID` khi `remindDay > paymentDueDay`; setting cấp phòng lấy `buildingId` từ Room và trả cả hai ID. |
| 8 | `src/requests/rooms/meter-reading-create-request-dto.yaml` | `previousReading` bắt buộc, nhưng DB quy định = `currentReading` kỳ trước (§2.11). | `previousReading` **chỉ bắt buộc khi `isBaseline=true`**; còn lại server tự lấy từ kỳ gần nhất, nếu client gửi khác → `422 CURRENT_READING_INVALID`? *(API owner chốt: bỏ field hoặc giữ để đối chiếu)*. |
| 9 | Bulk meter readings | Có `readingMethod` (`CAMERA_CAPTURE`/`FILE_UPLOAD`) nhưng DB không lưu; response có `status: WARNING` không định nghĩa khi nào. | Giữ `readingMethod` (chỉ log). Bulk **all-or-nothing**: lỗi bất kỳ dòng → `422`/`409`, không ghi gì. `WARNING` = tiêu thụ > 3× kỳ trước (chỉ cảnh báo) *(hoặc bỏ enum)*. |

## Tham chiếu

- `pm/phase-1/discovery/database-design.md` §2.9, §2.10, §2.11.
- `pm/phase-1/discovery/utility-billing-calculations.md` §0, §1, §11, §12 (D31–D33, D39).
- Cách tổ chức file contract: `api-doc/src/openapi.yaml` dòng `# RatePolicy DTOs`, `# BillingSetting DTOs`, `# MeterReading DTOs`.

## Các bước triển khai

### Bước 1 — Mở issue thảo luận với API owner

- **Cách làm:**
  - Clone `api-doc`, tạo branch `docs/p6-02a-billing-contract`.
  - Copy bảng mâu thuẫn ở trên vào comment issue, tag `baoduong17`, chốt từng dòng (#1–#9) **trước khi** sửa file.
- **Kiểm tra bước:** mỗi dòng trong bảng có quyết định "theo đề xuất" hoặc phương án thay thế được ghi trong comment.

### Bước 2 — Tạo `RateItem` và sửa RatePolicy request/response

- **File tạo:** `src/schemas/billing/rate-item.yaml`; đăng ký `RateItem` trong `src/openapi.yaml` (mục `# Domain: Billing`).
- **File sửa:** `src/schemas/billing/rate-policy.yaml` (`rates.items` → `$ref` `RateItem`), `src/requests/rooms/rate-policy-create-request-dto.yaml`, `src/requests/rooms/rate-policy-update-request-dto.yaml`, `src/requests/buildings/building-rate-policies-batch-create-request-dto.yaml`, 4 file `src/responses/dtos/rooms/rate-policy-*-response-dto.yaml`.
- **Cách làm:** theo dòng #1–#5; sửa luôn `example` trong `src/paths/billing/rate-policies*.yaml` và `src/paths/buildings/buildings-buildingId-rate-policies-batch.yaml` (example EVN 6 bậc: 1893/1956/2283/2833/2927/3451 — §12).
- **Kiểm tra bước:** `npm run lint` (Redocly lint `src/openapi.yaml`) và `npm run bundle` pass; không lỗi `$ref`; example khớp schema.

### Bước 3 — Khai báo error code RatePolicy

- **File sửa:** `src/paths/billing/rate-policies.yaml` (`post` → thêm response `422` có enum `INVALID_RATE_KIND`, `TIER_CONFIG_INVALID`, `VALIDATION_FAILED`, giữ `409 ACTIVE_POLICY_EXISTS`), `src/paths/billing/rate-policies-ratePolicyId.yaml` (bỏ `409 RATE_POLICY_LOCKED`, `422` như trên), batch path (thêm `INVALID_RATE_KIND`, `TIER_CONFIG_INVALID`).
- **Cách làm:** copy khối `422` dạng enum + `examples` từ `src/paths/billing/meter-readings-bulk.yaml`.
- **Kiểm tra bước:** bundle pass; mở Apidog preview thấy đủ example lỗi.

### Bước 4 — Sửa BillingSetting theo D39

- **File sửa:** `src/requests/rooms/billing-setting-create-request-dto.yaml`, `billing-setting-update-request-dto.yaml`, `src/responses/dtos/rooms/billing-setting-*-response-dto.yaml`, `src/schemas/billing/billing-setting.yaml`, example trong `src/paths/billing/billing-settings*.yaml`.
- **Cách làm:** theo dòng #7; xóa field reminder/overdue.
- **Kiểm tra bước:** `grep -rn "debtScanEnabled\|gracePeriodDays\|overdueReminder\|dueDays" src/` không còn kết quả trong nhóm billing-setting.

### Bước 5 — Sửa MeterReading

- **File sửa:** `src/requests/rooms/meter-reading-create-request-dto.yaml`, `src/requests/rooms/bulk-meter-reading-create-request-dto.yaml`, `src/paths/billing/meter-readings-bulk.yaml` (mô tả all-or-nothing + ý nghĩa `WARNING`).
- **Cách làm:** theo dòng #8, #9; bổ sung `422 CURRENT_READING_INVALID` vào `post` của `src/paths/billing/meter-readings.yaml` nếu chưa có trong enum.
- **Kiểm tra bước:** bundle pass.

### Bước 6 — PR và sync

- **Cách làm:** PR vào `main` của `api-doc` (workflow changelog sẽ tự sinh entry), sync Apidog.
- **Kiểm tra bước:** baoduong17 approve; changelog bot ghi nhận thay đổi breaking của RatePolicy/BillingSetting.

## Quyết định tạm thời / Ngoài phạm vi

- Không đụng `src/paths/invoices/*` (xử lý trong P6-02g).
- Giữ `x-apidog-status: designing`; chỉ đổi `released` khi endpoint chạy thật (P6-02c → P6-02f).

## Definition of Done

- [ ] 9 điểm trong bảng đã có quyết định ghi trong issue và phản ánh vào `api-doc`.
- [ ] Bundle/lint `api-doc` pass; Apidog đã sync.
- [ ] PR `api-doc` merge, ghi `Closes pbl6-home-renter/docs#71`.
