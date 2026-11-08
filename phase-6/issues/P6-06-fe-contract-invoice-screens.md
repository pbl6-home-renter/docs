# P6-06 — Màn Hợp đồng, Chỉ số điện nước và Hóa đơn cho landlord (Web) — Epic

**Trạng thái:** 🟡 Open (đã tách sub-issue a–d)  
**Người phụ trách:** ThaiBao11125  
**Người review:** baoduong17  
**Ước lượng:** 12 points (4 sub-issue × 3 points) · 24–32 giờ  
**Phụ thuộc:** chặn **cả 4** sub-issue; P6-03c (feature `rooms` trên FE); BE P6-01b–e, P6-02e–h, P6-02g1–g3
**Iteration:** It6 (09/11–15/11); P6-06d có thể dời It7  
**Repo:** `fe`  
**Issue:** `docs#86`

> **Đọc trước khi code:** `fe/AGENTS.md` và skill trong `fe/.agents/skills/`. Theo [`P6-D75`](../decisions.md#d75--thứ-tự-ưu-tiên-nguồn-và-cách-xử-lý-câu-hỏi-mở), các issue con không mô tả cách viết code; nguồn mâu thuẫn: `decisions.md` > `api-docs` > skill > issue.

## Mục tiêu

Landlord thao tác trọn vòng đời trên Web và dừng ở **phát hành hóa đơn** (`P6-D61`): tạo HĐ nháp → áp mẫu, tải bản nháp → upload bản ký, kích hoạt → nhập chỉ số điện nước thủ công có ảnh minh chứng → lập hóa đơn theo tòa + kỳ → sửa phí khác → phát hành / hủy và lập lại → quản lý thành viên → trả phòng.

## Sub-issue

| ID | Task | Pts | Phụ thuộc chính | Màn UI (outline Phase 2) |
|---|---|---|---|---|
| [P6-06a](P6-06a-fe-contract-list-create-activate.md) · [#102](https://github.com/pbl6-home-renter/docs/issues/102) | Danh sách, tạo HĐ nháp, áp mẫu, bản nháp, upload bản ký, kích hoạt | 3 | P6-01b/c/d, P6-03c | LL-11, LL-12, LL-13, LL-14 |
| [P6-06b](P6-06b-fe-meter-reading-entry.md) · [#103](https://github.com/pbl6-home-renter/docs/issues/103) | Nhập chỉ số theo tòa + kỳ, ảnh minh chứng, khóa kỳ | 3 | P6-02e/f, P6-02h | LL-18, LL-18b |
| [P6-06c](P6-06c-fe-invoice-screens.md) · [#104](https://github.com/pbl6-home-renter/docs/issues/104) | Lập hóa đơn (kết quả + phòng bị chặn), danh sách, chi tiết, phí khác, phát hành, hủy + lập lại | 3 | P6-02g1–g3, P6-01e3 (sửa số xe HĐ `active`) | LL-21, LL-22 (phần phát hành) |
| [P6-06d](P6-06d-fe-contract-members-checkout.md) · [#105](https://github.com/pbl6-home-renter/docs/issues/105) | Tab thành viên, trả phòng, phòng sẵn sàng cho thuê — ⚠️ **có thể dời It7** | 3 | P6-01e1, P6-01e3, P6-06a | LL-15, LL-16, LL-17, LL-32 |
| **Tổng** | | **12** | | |

Thứ tự: `P6-06a → P6-06d`; `P6-06b → P6-06c` (link sửa `READING_MISSING`); `P6-06a → P6-06c` (Dialog số xe cho link `VEHICLE_COUNT_MISSING`). `P6-06a` và `P6-06b` làm song song được.

## Quyết định chi phối

`P6-D61` (không thu tiền, không quyết toán cọc) · `P6-D62` (checkout) · `P6-D63` (thành viên) · `P6-D64` (vòng đời hóa đơn) · `P6-D65` (tiền là string, làm tròn tổng) · `P6-D66` (MeterReading) · `P6-D67` (OCR qua ai-service) · `P6-D68` (field tạo HĐ) · `P6-D69` (tạo trước, upload sau) · `P6-D70` (reading: `evidenceMediaId`, `PATCH` mới nhất, bulk `BASELINE_REQUIRED`) · `P6-D71` (sửa số xe khi `active`, rule ngày/trùng member, field chi tiết HĐ) · `P6-D72` (hủy có lý do, không QR/`sendNotification`) · `P6-D74` (không chọn tài khoản tenant) · `P1-D39` (trạng thái hóa đơn `pending|issued|void`).

## Phạm vi đã bỏ so với outline cũ và UI Screen Outline v0.1

| Phần bị bỏ | Lý do |
|---|---|
| Ghi nhận thu tiền mặt (`payments/record-cash-payment`, LL-23), trạng thái "đã thu" | `P6-D61` — Payment là Stretch |
| Quyết toán cọc (`deposit-settlement`, LL-31) | `P6-D61` |
| Hóa đơn quyết toán riêng khi trả phòng (LL-30, `createSettlementInvoice`) | `P6-D64` — dùng phí khác của hóa đơn kỳ cuối |
| Sửa hóa đơn đã phát hành (LL-21b) | `P6-D64` — thay bằng hủy + lập lại |
| Trạng thái "Quá hạn / 1 phần / Đã đủ" (LL-21a), danh sách công nợ, quét nợ, nhắc hạn (LL-24, LL-25, LL-25b) | `P1-D39`, `P6-D64` (gỡ `overdue-debts`, `send-reminder`) |
| Trường `rentalType`, CCCD, `paymentDueDay` khi tạo HĐ (LL-11) | `P6-D68` |
| CCCD/ảnh CCCD/cờ đại diện của thành viên, "xóa" thành viên (LL-16, LL-17) | `P6-D63` (rời = `leftAt`) |
| Toggle "Có xe" từng thành viên (LL-16/LL-54) | `P1-D32`, `P6-D65` — số xe ở HĐ |
| OCR preview trong Tenancy | Chưa có endpoint được công bố trong phạm vi issue hiện tại |
| Phòng `pending_cleanup` sau trả phòng | `P6-D62` — dùng `maintenance` + `mark-ready` |
| Ô chọn tài khoản tenant khi tạo HĐ/thêm thành viên | `P6-D74` — Stretch |
| VietQR trên hóa đơn (LL-22), checkbox gửi thông báo khi phát hành | `P6-D72` |
| Xóa chỉ số điện nước | `P6-D70` — chỉ `PATCH` reading mới nhất |
| Cấu hình đơn giá / billing setting của tòa (dòng "c" outline cũ) | Không thuộc epic này; card đơn giá đã có ở `fe/src/features/buildings/components/building-rate-policies-card.tsx` |

## Vấn đề còn mở → đã chốt

| Vấn đề | Quyết định | Sub-issue |
|---|---|---|
| Landlord tìm tenant có sẵn để gán `tenantId` | `P6-D74` — không làm, chỉ nhập họ tên + SĐT | P6-06a, P6-06d |
| Biết reading đã có ảnh sau khi tải lại | `P6-D70` — response có `evidenceMediaId`, gắn bằng `PATCH` | P6-06b |
| VietQR, `sendNotification` khi phát hành | `P6-D72` — bỏ cả hai | P6-06c |
| Sửa `vehicleCount` khi HĐ `active` | `P6-D71` — được sửa `vehicleCount`/`description` (BE ở P6-01e3) | P6-06a, P6-06c |
| `ContractDetailResponseDto` thiếu field tài liệu | `P6-D71` — thêm `templateKey`, `draftDocumentMediaId`, `signedContractMediaId`, `roomName`, `buildingId` | P6-06a |

## Quy định chung cho sub-issue

- Mỗi sub-issue theo [`_TEMPLATE.md`](_TEMPLATE.md) v2, tối đa 3 points.
- i18n: namespace `contracts` (a, d), `meterReadings` (b), `invoices` (c); key thêm ở **cả `vi` và `en`**; mã API ở `apiSuccess.*` / `apiErrors.*`.
- DoD chung: `npm run build`, `npm run lint`, `npm run i18n:check` pass; không viết file `*.test.ts`; PR `Closes pbl6-home-renter/docs#<số>`.

## Definition of Done (epic)

- [ ] P6-06a–c đóng trong It6; P6-06d đóng trong It6 hoặc được PM xác nhận dời It7.
- [ ] Demo trên staging: tạo HĐ → kích hoạt → nhập chỉ số thủ công có ảnh minh chứng → lập hóa đơn → phát hành, không lỗi console.
- [ ] Các sub-issue làm đúng các D-ID ở mục "Vấn đề còn mở → đã chốt".
