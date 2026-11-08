# P6-06c — Sinh, xem, sửa phí khác, phát hành và hủy hóa đơn (Web)

**Epic:** [P6-06](P6-06-fe-contract-invoice-screens.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** ThaiBao11125  
**Người review:** baoduong17  
**Ước lượng:** 3 points · 6–8 giờ  
**Phụ thuộc:**; BE P6-02g1–g3 (generate, list/detail/patch, issue/void); FE P6-06b (link sửa chỉ số), P6-06a (link sửa HĐ, Dialog số xe khi `active`); BE P6-01e3 (`PATCH /contracts/{id}` cho HĐ `active`) 
**Repo / branch:** `fe` · `feat/p6-06c-invoice-screens`  
**Iteration:** It6 (09/11–15/11)  
**Issue:** `docs#104`

> **Đọc trước khi code:** `fe/AGENTS.md` và skill trong `fe/.agents/skills/` (`fe-feature-workflow` → `fe-structure` → `fe-code-style` → `fe-ui-ux` + `references/*`). Issue **không** quy định cách đặt file, đặt tên hay style — nếu issue nói khác skill thì làm theo skill. Nguồn mâu thuẫn xử lý theo [`P6-D75`](../decisions.md#d75--thứ-tự-ưu-tiên-nguồn-và-cách-xử-lý-câu-hỏi-mở): `decisions.md` > `api-docs` > skill > issue.

## Mục tiêu

Landlord vào **Hóa đơn**, chọn tòa + kỳ, bấm **Lập hóa đơn** → thấy kết quả: hóa đơn mới, hóa đơn được tính lại, phòng bị chặn kèm lý do và link tới chỗ cần sửa. Landlord xem chi tiết từng hóa đơn (bảng breakdown), sửa phí khác/ghi chú khi `pending`, chọn nhiều hóa đơn để **Phát hành**, và **Hủy** hóa đơn đã phát hành rồi lập lại.

## Quyết định áp dụng

- `P6-D64` — sinh theo yêu cầu `POST /invoices/generate { buildingId, period }`; thiếu dữ kiện → `blocked[] { roomId, contractId, reasonCode }`; `pending` sửa được `otherFees`, `note`, generate lại giữ `otherFees`/`note`; `issued` bất biến, sai thì `void` rồi generate lại (bản mới có `voidedInvoiceId`); phát hành hàng loạt có `Idempotency-Key`; không có hóa đơn quyết toán riêng.
- `P1-D39` — trạng thái chỉ `pending | issued | void`; không có "quá hạn", không có trạng thái thu.
- `P6-D61` — không có màn thu tiền, không hiện "đã thu"; demo dừng ở `issued`.
- `P1-D33` (⑥) — `otherFees` cho phép số âm; tổng âm bị chặn `TOTAL_NEGATIVE` (EC17).
- `P6-D65` — tiền là string decimal; chỉ `totalAmount` làm tròn; hiển thị bằng `formatVnd`, không cộng lại tổng ở FE.
- `P6-D72` — dòng giữ 4 chữ số thập phân, `totalAmount` = round(Σ dòng) nên Σ dòng hiển thị có thể lệch tổng < 1 đồng (không "sửa" ở FE); hủy bắt buộc `reason` 1–500 ký tự; **không** có `sendNotification` khi phát hành, **không** hiển thị QR (`vietQrContent` đã gỡ).
- `P6-D71` — HĐ `active` sửa được `vehicleCount` → link `VEHICLE_COUNT_MISSING` mở Dialog sửa số xe của HĐ (P6-06a), sửa xong lập lại hóa đơn là hết chặn.

## Contract

| Endpoint (`api-docs/src/paths/invoices/`) | Thành công | Lỗi cần xử lý trên UI |
|---|---|---|
| `POST /invoices/generate` ( thêm) | `200`/`201` + `generated[]`, `recalculated[]`, `blocked[]` (tên field theo api-docs) | `403`, `404` tòa, `422 VALIDATION_FAILED` |
| `GET /invoices` (`invoices.yaml`, `getInvoices`) — `filter[buildingId]`, `filter[period]`, `filter[status]`, `filter[roomId]` | `200 INVOICES_FETCHED` | `422` |
| `GET /invoices/{id}` (`getInvoicesInvoiceid`) | `200 INVOICE_FETCHED` | `404` |
| `PATCH /invoices/{id}` (`patchInvoicesInvoiceid`) — `otherFees[]`, `note` | `200 INVOICE_UPDATED` | `409 INVOICE_ALREADY_ISSUED`, `422 TOTAL_NEGATIVE`, `VALIDATION_FAILED` |
| `POST /invoices/issue-invoice` (`postInvoicesIssueInvoice`) + header `Idempotency-Key` | `INVOICES_ISSUE_REQUESTED`, `succeeded[]` / `failed[{ invoiceId, code }]` | `409 IDEMPOTENCY_KEY_REUSED`, `422 INVOICE_IDS_REQUIRED`, `INVOICE_IDS_TOO_LARGE` |
| Hủy: `POST /invoices/{id}/cancel-invoice` `{ reason }` (`postInvoicesInvoiceidCancelInvoice`) → `void` | `200 INVOICE_CANCELLED` | `409 INVOICE_ALREADY_VOIDED`, `422 VALIDATION_FAILED` (`reason`) |

Mã `reasonCode` trong `blocked[]` (`pm/phase-1/discovery/utility-billing-calculations.md` §11) và nơi sửa:

| `reasonCode` | Hiển thị | Link sửa |
|---|---|---|
| `READING_MISSING` (EC2) | Thiếu chỉ số điện/nước | `/meter-readings?buildingId=…&period=…` (P6-06b) |
| `RATE_MISSING` (EC3), `TIER_CONFIG_INVALID` (EC13) | Thiếu/sai cấu hình đơn giá | `/buildings/:id` (card đơn giá) |
| `AREA_MISSING` (EC6) | Phòng chưa có diện tích | trang/dialog sửa phòng (P6-03c) |
| `HEADCOUNT_ZERO` (EC7) | HĐ chưa có thành viên | `/contracts/:id` tab Thành viên (P6-06d) |
| `VEHICLE_COUNT_MISSING` (EC8) | HĐ chưa khai số xe | `/contracts/:id?edit=vehicle` → Dialog sửa số xe của HĐ `active` (P6-06a, `P6-D71`) |
| `TOTAL_NEGATIVE` (EC17) | Tổng âm do phí khác | `/invoices/:id` |
| mã khác | text chung "Không lập được hóa đơn" + mã | — |

### Mapping field

| DTO field | UI | Validation / ghi chú |
|---|---|---|
| `buildingId`, `period` (generate) | Select Tòa + picker Kỳ trên thanh lọc | bắt buộc; kỳ `YYYY-MM` |
| `code`, `roomName`, `tenantName`, `period`, `status`, `totalAmount` | cột danh sách | chỉ đọc |
| `breakdown[]` (`type`, `name`, `rateKind`, `quantity`, `unit`, `unitPrice`, `prorateRatio`, `amount`; tên theo api-docs sau ) | bảng "Chi tiết dịch vụ" ở trang chi tiết | chỉ đọc, giữ số thập phân như API trả |
| `otherFees[].name` | "Nội dung" | bắt buộc, không rỗng |
| `otherFees[].amount` | "Số tiền" (cho nhập dấu `-`) | bắt buộc, khác 0, số nguyên đồng; âm = giảm trừ |
| `note` | "Ghi chú" (`Textarea`) | tuỳ chọn |
| `invoiceIds[]` (issue) | checkbox dòng `pending` trên DataTable | ≥ 1, không trùng |
| `reason` (hủy) | "Lý do hủy" (`Textarea`) trong Dialog | bắt buộc, 1–500 ký tự (`P6-D72`) |
| `voidReason` | dòng "Lý do hủy" ở chi tiết hóa đơn `void` | chỉ đọc |
| `voidedInvoiceId` | dòng "Thay thế hóa đơn <code>" ở chi tiết | chỉ đọc |

## Tham chiếu code

- Feature mới: `fe/src/features/invoices/`. Copy pattern từ `fe/src/features/buildings/` (list page + columns + mobile row, detail page, Dialog sửa).
- DataTable có chọn dòng: `fe/src/components/ui/data-table/` + `fe/src/hooks/use-data-table.ts` (`features.selection`), `use-data-table-state.ts`.
- Mảng `otherFees`: `useFieldArray` của react-hook-form, schema theo `fe-code-style`; lỗi 422 vào field bằng `setFormApiErrors`.
- Format: `formatVnd`, `formatMonth` (`fe/src/lib/utils/format.ts`).
- Menu `landlord-invoices` (`/invoices`) đã có trong `fe/src/config/navigation.config.ts`; route chưa có trong `fe/src/app/routes/roles/landlord.routes.tsx`.

## Các bước triển khai

### Bước 1 — Đọc contract hiện hành trong `api-docs`, chuẩn bị dữ liệu

- **Cách làm:** ghi vào comment issue: response `generate`, tên field `breakdown` (đối chiếu `P6-D72`: không còn `sendNotification`, `vietQrContent`). Staging: tòa 3 phòng có HĐ active; 2 phòng đủ chỉ số kỳ, 1 phòng thiếu nước.
- **Kiểm tra bước:** Apidog `POST /invoices/generate` trả 2 hóa đơn + 1 `blocked` `READING_MISSING`.

### Bước 2 — Tầng dữ liệu `invoices`

- **Cách làm:** DTO, API, query keys, hook cho generate, list, detail, patch, issue, void. `Idempotency-Key` sinh bằng `crypto.randomUUID()` **một lần cho mỗi lần bấm Phát hành**, thử lại cùng lô thì dùng lại key. Namespace `invoices` theo `fe-structure` §5.
- **Kiểm tra bước:** `npm run build` pass.

### Bước 3 — Trang `/invoices`: lọc + DataTable + lập hóa đơn

- **Cách làm:** thanh lọc Tòa, Kỳ, Trạng thái (`pending`/`issued`/`void`) trên URL; DataTable cột theo Mapping, bấm dòng → `/invoices/:id`. Nút **Lập hóa đơn** (bật khi đã chọn Tòa + Kỳ) → Dialog kết quả 3 nhóm: "Tạo mới", "Tính lại", "Chưa lập được" (mỗi dòng: phòng, lý do i18n theo `reasonCode`, nút tới link sửa). Đóng Dialog → làm mới danh sách.
- **Kiểm tra bước:** lập hóa đơn tòa demo → Dialog có 2 dòng mới + 1 dòng "Thiếu chỉ số" có link sang `/meter-readings` đúng tòa/kỳ; bấm Lập lại → 2 dòng ở nhóm "Tính lại". Phòng có phí gửi xe mà HĐ chưa khai số xe → dòng `VEHICLE_COUNT_MISSING`, bấm link → Dialog số xe, lưu, quay lại Lập lại → phòng đó vào "Tạo mới".

### Bước 4 — Trang chi tiết `/invoices/:id`

- **Cách làm:** khung "chi tiết": header (mã, phòng, người thuê, kỳ, badge trạng thái), bảng breakdown, bảng phí khác, ghi chú, tổng. Hóa đơn `pending`: nút **Sửa phí khác** mở Dialog `useFieldArray` (thêm/xóa dòng, cho số âm) → `PATCH`; `422 TOTAL_NEGATIVE` → `AlertBanner` trong Dialog "Tổng hóa đơn không được âm". Hóa đơn `issued`/`void`: chỉ xem.
- **Kiểm tra bước:** thêm dòng "Giảm trừ" −100.000 → tổng giảm 100.000 sau khi lưu; nhập giảm trừ lớn hơn tổng → báo `TOTAL_NEGATIVE`, dữ liệu không đổi.

### Bước 5 — Phát hành hàng loạt

- **Cách làm:** chọn dòng `pending` trên DataTable (dòng khác không chọn được) → thanh hành động "Phát hành (n)" → Dialog xác nhận nêu "Sau khi phát hành không sửa được" (không có checkbox gửi thông báo, `P6-D72`) → `POST issue-invoice` body chỉ `invoiceIds`. Kết quả: toast số thành công; `failed[]` hiện danh sách mã hóa đơn + lý do i18n. Trang chi tiết `pending` có nút Phát hành dùng cùng endpoint với 1 id.
- **Kiểm tra bước:** chọn 2 hóa đơn → cả 2 thành `issued`; bấm lại nhanh 2 lần → chỉ 1 request mới (nút khóa khi đang gửi), không lỗi trùng.

### Bước 6 — Hủy và lập lại

- **Cách làm:** hóa đơn `issued`: nút **Hủy hóa đơn** → Dialog lý do (bắt buộc, ≤ 500 ký tự, kiểm bằng zod trước khi gọi) → `cancel-invoice`. Sau khi hủy hiện `AlertBanner` + nút **Lập lại hóa đơn kỳ này** gọi `generate` cho tòa + kỳ của hóa đơn, xong điều hướng tới hóa đơn mới. Chi tiết hóa đơn mới hiện "Thay thế hóa đơn <code>" nếu có `voidedInvoiceId`.
- **Kiểm tra bước:** để trống lý do → lỗi dưới field, không gọi API; hủy 1 hóa đơn `issued` → badge `void`, chi tiết hiện lý do; lập lại → có hóa đơn `pending` mới cùng phòng/kỳ, hiện dòng thay thế.

### Bước 7 — Route, i18n, rà soát

- **Cách làm:** thêm `/invoices`, `/invoices/:id` vào `landlord.routes.tsx`. Text vào `src/i18n/locales/vi/invoices.json` rồi `en/invoices.json` cùng key (gồm nhãn mọi `reasonCode`); `apiSuccess.*`/`apiErrors.*` cho mã ở bảng Contract.
- **Kiểm tra bước:** 360px không cuộn ngang; vi ↔ en không còn chuỗi cứng; `npm run build`, `npm run lint`, `npm run i18n:check` pass.

## Ngoài phạm vi

- LL-21a trạng thái "Quá hạn / 1 phần / Đã đủ" và LL-25b danh sách công nợ — bỏ theo `P1-D39`, `P6-D61`, `P6-D64` (gỡ `overdue-debts`, `send-reminder`).
- LL-21b sửa hóa đơn đã phát hành — bỏ theo `P6-D64` (thay bằng hủy + lập lại).
- LL-23 xác nhận thu tiền mặt, "đã thu" — `P6-D61` (Stretch).
- LL-24/LL-25 quét nợ, nhắc hạn — `P6-D64`, `P1-D39`.
- LL-30 hóa đơn quyết toán riêng (`createSettlementInvoice`) — `P6-D64`; chênh lệch kỳ trả phòng ghi bằng phí khác.
- LL-22 gửi card vào Chat phòng (community-service là Stretch), VietQR trên hóa đơn, checkbox gửi thông báo khi phát hành — `P6-D72`, `P6-D61`; xuất `xlsx/csv/pdf`.

## Blocker

- Không có. (VietQR, `sendNotification`: `P6-D72`; sửa số xe khi HĐ `active`: `P6-D71`.)

## Acceptance

- [ ] Lập hóa đơn tòa + kỳ → Dialog 3 nhóm; mỗi `reasonCode` có nhãn i18n và link sửa đúng; link `VEHICLE_COUNT_MISSING` mở Dialog số xe và sửa được khi HĐ `active`.
- [ ] Lập lại khi đã có `pending` → hóa đơn ở nhóm "Tính lại", phí khác + ghi chú giữ nguyên.
- [ ] `/invoices` lọc theo tòa, kỳ, trạng thái; F5 giữ bộ lọc; chỉ có 3 trạng thái `pending/issued/void`.
- [ ] Sửa phí khác có dòng âm → `200 INVOICE_UPDATED`; tổng âm → `422 TOTAL_NEGATIVE` hiển thị trong Dialog.
- [ ] Phát hành 2 hóa đơn → `succeeded` 2; hóa đơn lỗi hiện trong danh sách `failed` với lý do.
- [ ] Hóa đơn `issued` không có nút sửa; hủy (có lý do) → `void`, hiện `voidReason`; lập lại → hóa đơn mới có `voidedInvoiceId`.
- [ ] Không có QR, không có checkbox gửi thông báo.

## Definition of Done

- [ ] Mọi bước qua phần Kiểm tra bước; mọi ô Acceptance được người làm tick, kèm ảnh desktop + 360px trong PR.
- [ ] `npm run build` + `npm run lint` + `npm run i18n:check` pass; không có file `*.test.ts`; key có ở cả `vi` và `en`.
- [ ] Không sửa file ngoài phạm vi; PR vào `main` ghi `Closes pbl6-home-renter/docs#104`, ≥ 1 reviewer approve.
