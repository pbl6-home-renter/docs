# P6-09 — Đồng bộ `api-docs` cho It6 theo `decisions.md`

**Trạng thái:** 🟡 Open  
**Người phụ trách:** baoduong17 (API owner)  
**Người review:** leminhkhai345, huynhtiennhat0403, ThaiBao11125 (mỗi người duyệt phần mình sẽ code)  
**Ước lượng:** 3 points · 6–8 giờ  
**Phụ thuộc:** `pm/phase-6/decisions.md` (D61–D75; retain P6-D60 atomic bulk semantics)  
**Repo / branch:** `api-docs` · `docs/p6-09-it6-alignment`; `api-gateway` · `feature/p6-09-me-invoices-route`  
**Iteration:** It5 prerequisite  
**Issue:** `docs#106`  
**Hạn:** 06/11 (trước khi It6 bắt đầu — mọi task BE/FE It6 phụ thuộc task này)

> Đọc `AGENTS.md` + skill của repo trước khi sửa. Nguồn mâu thuẫn xử lý theo [`P6-D75`](../decisions.md#d75--thứ-tự-ưu-tiên-nguồn-và-cách-xử-lý-câu-hỏi-mở).

## Mục tiêu

`api-docs` khớp 100% với `decisions.md` trước khi dev It6 bắt đầu, để không ai phải "code theo issue hay theo doc". Sau task này, mọi issue It6 chỉ trích contract, không mô tả lại.

## Quyết định áp dụng

- `P6-D61` — Payment, quyết toán cọc → Stretch.
- `P6-D62` — Checkout trả `terminated`, phòng → `maintenance`, bỏ `pending_cleanup`.
- `P6-D63` — DTO thêm member khớp bảng `contract_members`.
- `P6-D64` — `POST /invoices/generate`, `/me/invoices`, bỏ overdue/reminder/settlement invoice.
- `P6-D66` — MeterReading `source`/`ocrValue`, retain nullable `evidenceMediaId` under D70; remove `readingDate`, `409 PERIOD_ALREADY_INVOICED`.
- `P6-D67` — OCR chuyển sang `paths/ai/`.
- `P6-D68` — Bỏ `rentalType`, `tenantCccd`, `paymentDueDay` khỏi Contract.

- `P6-D70`–`P6-D74` — reading PATCH/baseline, active contract updates, member dates, invoice precision/void reason, internal lookups, tenant account linking deferred.

## Danh sách thay đổi

### Contract (`src/paths/contracts/`, `src/requests/contracts/`, `src/schemas/contract/`)

| File | Thay đổi | D-ID |
|---|---|---|
| `requests/contracts/contract-create-request-dto.yaml`, `contract-update-request-dto.yaml` | Xóa `rentalType`, `tenantCccd`, `paymentDueDay`; `templateKey`/`templateVariables` chỉ giữ ở `contract-template-apply-request-dto.yaml`. Đối chiếu field với `Tenancy-Service/src/modules/contract/presentation/http/requests/create-contract.request.ts` | D68 |
| `requests/contracts/contract-member-add-request-dto.yaml` | Xóa `identityCardNumber`, `dateOfBirth`, `gender`, `isRepresentative`. Giữ `contractId`, `tenantId?`, `tenantName`, `tenantPhone?`, `joinedAt` | D63 |
| `schemas/contract/contract-member.yaml` | Xóa các field tương ứng nếu có | D63 |
| `paths/contracts/contract-members.yaml` | Mô tả: chỉ thêm khi HĐ `active` (`409 CONTRACT_NOT_ACTIVE`); đại diện được thêm tự động khi activate | D63 |
| `paths/contracts/contracts-contractId-complete-checkout.yaml` | Ví dụ `status: terminated`; bỏ `pending_cleanup`, mô tả phòng → `maintenance` + `mark-ready`; mô tả điều kiện `409 SETTLEMENT_NOT_READY` (hóa đơn kỳ chứa `completedOn` phải `issued`); bỏ mọi nhắc tới quyết toán cọc | D62 |
| `paths/contracts/contracts-contractId-deposit-settlement.yaml` | `deprecated: true`, `x-apidog-status: obsolete`, mô tả "Stretch — P6-D61" | D61 |

### Invoice (`src/paths/invoices/`)

| File | Thay đổi | D-ID |
|---|---|---|
| `paths/invoices/invoices-generate.yaml` (*mới*) | `POST /invoices/generate`, landlord. Body `InvoiceGenerateRequestDto { buildingId, period }`. `200 INVOICES_GENERATED` → `{ generated: InvoiceListItem[], recalculated: InvoiceListItem[], blocked: [{ roomId, contractId, reasonCode }] }`. `reasonCode` ∈ `READING_MISSING`, `RATE_MISSING`, `AREA_MISSING`, `HEADCOUNT_ZERO`, `VEHICLE_COUNT_MISSING`, `TIER_CONFIG_INVALID`, `TOTAL_NEGATIVE`. `404 BUILDING_NOT_FOUND`, `422 VALIDATION_FAILED` | D64 |
| `paths/invoices/me-invoices.yaml` (*mới*) | `GET /me/invoices`, tenant, phân trang, chỉ hóa đơn `issued` của HĐ mà user là đại diện hoặc member chưa rời. Dời nội dung từ `invoices-tenant.yaml` | D64 |
| `invoices-tenant.yaml`, `invoices-overdue-debts.yaml`, `invoices-send-reminder.yaml` | Xóa file + ref trong `openapi.yaml` (dòng ~167–180) + DTO chỉ dùng cho chúng (`overdue-debt-list-response-dto.yaml`, `invoice-reminders-send-request-dto.yaml`) | D64 |
| `invoices.yaml` | Bỏ operation `POST` (`createSettlementInvoice`) + `settlement-invoice-create-*.yaml`; giữ `GET` (landlord list, filter `buildingId`, `period`, `status`) | D64 |
| `invoices-invoiceId.yaml` | `PATCH` chỉ nhận `otherFees`, `note`; chỉ khi `pending` (`409 INVOICE_NOT_PENDING`); `422 TOTAL_NEGATIVE`. `GET` dùng chung landlord/tenant (tenant chỉ thấy `issued`) | D64 |
| `invoices-invoiceId-cancel-invoice.yaml` | Chuyển `void`; bỏ `409 INVOICE_ALREADY_PAID` (không còn Payment) | D61, D64 |
| `schemas/billing/invoice.yaml` | `status` chỉ `pending | issued | void`; không có field thu tiền/`dueDate`; tiền là string decimal | P1-D39, D65 |

### MeterReading (`src/paths/billing/`, `src/requests/rooms/`, `src/schemas/billing/meter-reading.yaml`)

| Thay đổi | D-ID |
|---|---|
| Schema + request: bỏ `readingDate` (giữ `evidenceMediaId` — D70); thêm `buildingId` (response), `source: manual \| ocr` (mặc định `manual`), `ocrValue?: string`. Đối chiếu với nhánh `origin/feature/p6-02e-meter-reading` | D66 |
| `PATCH` reading: add `409 PERIOD_ALREADY_INVOICED` and `409 METER_READING_NOT_LATEST`; no `DELETE` in MVP (D70) | D66 |
| Mô tả `POST /meter-readings`: ảnh minh chứng upload **sau** khi tạo, `ownerType=meter_reading`, `ownerId=<id>` | D66, D69 |
| Xóa `meter-readings-preview-ocr-result.yaml` + ref + request DTO | D67 |

### AI (`src/paths/ai/` *mới*)

| Thay đổi | D-ID |
|---|---|
| `paths/ai/ai-meter-readings-ocr.yaml`: `POST /ai/meter-readings/ocr`, role `landlord`, `multipart/form-data` field `image` (JPEG/PNG/WebP, ≤ 5 MB) + `meterType: electricity \| water`. `200 METER_READING_OCR_COMPLETED` → `{ value: string \| null, confidence: number }`. Lỗi: `413 IMAGE_TOO_LARGE`, `415 MEDIA_TYPE_NOT_ALLOWED`, `504 OCR_TIMEOUT`, `502 OCR_UNAVAILABLE`, `429 TOO_MANY_REQUESTS` | D67 |
| Thêm tag `AI` trong `openapi.yaml` | D67 |

### Payment (`src/paths/payments/`)

- Mọi operation: `deprecated: true`, `x-apidog-status: obsolete`, mô tả "Stretch — P6-D61". **Không xóa** để giữ thiết kế cho sau.

### Gateway (`api-gateway`)

- `src/constants/route-paths.constants.ts`: thêm `'/me/invoices'` vào danh sách `GatewayService.Tenancy` (theo `api-gateway/docs/02-routing.md` mục "Path `/me/*` thuộc nhiều service"). Route `/ai` làm ở P6-10a.

## Các bước triển khai

### Bước 1 — Contract và member

- **Cách làm:** sửa các file trong bảng Contract.
- **Kiểm tra bước:** `npm run lint` không lỗi; `grep -rn "pending_cleanup\|tenantCccd\|rentalType\|isRepresentative" src/` không còn kết quả.

### Bước 2 — Invoice

- **Cách làm:** thêm `invoices-generate.yaml`, `me-invoices.yaml`, request/response DTO tương ứng (đặt cạnh DTO invoice hiện có, đặt tên theo cách các file cùng thư mục đang đặt); xóa path/DTO thừa.
- **Kiểm tra bước:** `npm run lint` pass; `grep -rn "overdue\|send-reminder\|createSettlementInvoice\|invoices/tenant" src/` không còn kết quả; `npm run preview` thấy `POST /invoices/generate` có ví dụ `blocked[]`.

### Bước 3 — MeterReading và AI

- **Kiểm tra bước:** `grep -rn "preview-ocr-result\|readingDate" src/` không còn kết quả; preview thấy tag `AI` với request multipart; `evidenceMediaId` remains nullable in reading responses. Bulk remains atomic (P6-D60), missing baseline rolls back the whole request with `BASELINE_REQUIRED`.

### Bước 4 — Payment deprecated, bundle, gateway

- **Cách làm:** đánh dấu deprecated; `npm run bundle`; sửa gateway route.
- **Kiểm tra bước:**
  - `reference/rentify.json` được cập nhật, CI "contract-check" chạy trên PR (báo BREAKING là đúng mong đợi — ghi rõ trong mô tả PR là theo `decisions.md`).
  - Gateway: `GET /api/v1/me/invoices` với token tenant qua gateway local trả `404` từ **Tenancy** (chưa có endpoint), không phải `404 ROUTE_NOT_FOUND` của Identity.

### Bước 5 — Sync Apidog và thông báo

- **Cách làm:** sync Apidog; comment link PR vào các issue It6 (P6-01e1–e3, P6-02g1–g4, P6-02h, P6-06a–d, P6-10b).
- **Kiểm tra bước:** mỗi dev It6 approve PR phần của mình.

## Ngoài phạm vi

- Endpoint internal (`GET /internal/ownership/...`) không nằm trong `api-docs` public — xem P6-11.
- Sequence diagram + `released` của từng endpoint do task code tương ứng cập nhật.

## Acceptance

- [ ] `npm run lint` + `npm run bundle` pass, `reference/rentify.json` commit cùng PR.
- [ ] 4 lệnh grep ở các bước không còn kết quả.
- [ ] Mỗi dòng trong các bảng trên có commit tương ứng; PR mô tả liệt kê D-ID.
- [ ] Gateway route `/me/invoices` → Tenancy.

## Definition of Done

- [ ] PR `api-docs` + PR `api-gateway` merged, Apidog đã sync.
- [ ] Dev It6 xác nhận đã đọc (approve PR).

## Bổ sung theo D70–D72

| Thay đổi | D-ID |
|---|---|
| Member response: bỏ `identityCardNumber`, `isRepresentative`; `status` chỉ `active \| left` | D71 |
| `PATCH /contracts/{id}`: HĐ `active` chỉ sửa `vehicleCount`, `description` | D71 |
| Chi tiết HĐ thêm `templateKey`, `draftDocumentMediaId`, `signedContractMediaId`, `roomName`, `buildingId` | D71 |
| Mô tả khoảng ngày `joinedAt`/`leftOn`/`completedOn` và rule `MEMBER_ALREADY_EXISTS` | D71 |
| MeterReading: **giữ** `evidenceMediaId`; thêm `PATCH /meter-readings/{id}` (`409 METER_READING_NOT_LATEST`, `409 PERIOD_ALREADY_INVOICED`); atomic bulk: missing baseline → `BASELINE_REQUIRED` and full rollback (P6-D60) | D70 |
| `cancel-invoice`: `reason` bắt buộc 1–500 ký tự; bỏ `sendNotification`, `vietQrContent` | D72 |
