# P6-06a — Danh sách, tạo hợp đồng nháp, áp mẫu và kích hoạt hợp đồng (Web)

**Epic:** [P6-06](P6-06-fe-contract-invoice-screens.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** ThaiBao11125  
**Người review:** baoduong17  
**Ước lượng:** 3 points · 6–8 giờ  
**Phụ thuộc:**; BE P6-01b (`POST/GET/PATCH /contracts`), P6-01c (mẫu HĐ, apply-template, generate-draft-document), P6-01d (activate); FE P6-03c (API phòng `GET /me/rooms` để chọn phòng) 
**Repo / branch:** `fe` · `feat/p6-06a-contract-list-activate`  
**Iteration:** It6 (09/11–15/11)  
**Issue:** `docs#102`

> **Đọc trước khi code:** `fe/AGENTS.md` và skill trong `fe/.agents/skills/` (`fe-feature-workflow` → `fe-structure` → `fe-code-style` → `fe-ui-ux` + `references/*`), `fe/docs/media-upload-guide.md`. Issue **không** quy định cách đặt file, đặt tên hay style — nếu issue nói khác skill thì làm theo skill. Nguồn mâu thuẫn xử lý theo [`P6-D75`](../decisions.md#d75--thứ-tự-ưu-tiên-nguồn-và-cách-xử-lý-câu-hỏi-mở): `decisions.md` > `api-docs` > skill > issue.

## Mục tiêu

Landlord vào menu **Hợp đồng** thấy danh sách HĐ của mình (lọc theo tòa, trạng thái), tạo HĐ nháp cho một phòng trống bằng Dialog, mở chi tiết HĐ để áp mẫu, tải bản nháp PDF, upload bản đã ký và bấm **Kích hoạt** → HĐ chuyển `active`, phòng chuyển `occupied`.

## Quyết định áp dụng

- `P6-D68` — form tạo/sửa **không có** `rentalType`, `tenantCccd`, `paymentDueDay`; `templateKey`/`templateVariables` chỉ đổi qua `apply-template`.
- `P6-D69` — HĐ phải tồn tại trước; bản ký upload sau với `ownerType=contract`, `ownerId=<contractId>`, `purpose=contract_signed`.
- `P6-D63` — người đại diện nhập lúc tạo HĐ; thành viên khác thêm ở P6-06d.
- `P6-D74` — **không** có ô chọn tài khoản tenant; form chỉ nhập họ tên + SĐT, không gửi `tenantId` (NULL).
- `P6-D71` — HĐ `active` chỉ sửa được `vehicleCount` và `description` (field khác → `409 CONTRACT_NOT_DRAFT`); `ContractDetailResponseDto` có `templateKey`, `draftDocumentMediaId`, `signedContractMediaId`, `roomName`, `buildingId` → trang chi tiết dựng lại đủ sau F5.
- `P0-D18` — không OTP/PIN; file ký là căn cứ, chưa có file thì không kích hoạt.
- `P6-D62` — checkout và trạng thái `terminated` thuộc P6-06d; màn này chỉ hiển thị badge.

## Contract

| Endpoint (`api-docs/src/paths/contracts/`) | operationId | Thành công | Lỗi cần xử lý trên UI |
|---|---|---|---|
| `GET /contracts` (`contracts.yaml`) | `getContracts` | `200 CONTRACTS_FETCHED` | `422 VALIDATION_FAILED` (filter sai) |
| `POST /contracts` (`contracts.yaml`) | `postContracts` | `201 CONTRACT_CREATED` | `409 ACTIVE_CONTRACT_EXISTS`, `422 VALIDATION_FAILED` |
| `GET/PATCH /contracts/{contractId}` | `getContractsContractid`, `patchContractsContractid` | `200 CONTRACT_FETCHED`, `200 CONTRACT_UPDATED` | `404`, `409 CONTRACT_NOT_DRAFT` (HĐ `active` gửi field khác `vehicleCount`/`description`, `P6-D71`) |
| `GET /contract-templates` | `getContractTemplates` | `200 CONTRACT_TEMPLATES_FETCHED` | — |
| `PUT /contracts/{id}/apply-template` | `putContractsContractidApplyTemplate` | `200 CONTRACT_TEMPLATE_APPLIED` | `404 TEMPLATE_NOT_FOUND`, `409 CONTRACT_NOT_DRAFT` |
| `POST /contracts/{id}/generate-draft-document` | `postContractsContractidGenerateDraftDocument` | `201 CONTRACT_DRAFT_GENERATED` (`mediaId`) | `409 CONTRACT_NOT_DRAFT`, `422 TEMPLATE_DATA_INVALID` |
| `POST /contracts/{id}/activate-contract` | `postContractsContractidActivateContract` | `200 CONTRACT_ACTIVATED` | `409 CONTRACT_NOT_READY`, `409 SIGNED_FILE_MISSING`, `409 ACTIVE_CONTRACT_EXISTS`, `503` |
| Media `presign-upload` → PUT → `complete-upload` | (dùng `features/media`) | `MEDIA_UPLOAD_COMPLETED` | `MEDIA_TYPE_NOT_ALLOWED`, `MEDIA_FILE_TOO_LARGE` |

Role: landlord. Không tìm thấy hoặc HĐ của landlord khác → `404`/`403` → `ErrorState`. Kiểu số tiền theo `api-docs` hiện hành (`P6-D65`: tiền là string trong DTO) — hiển thị bằng `formatVnd`.

### Mapping field

| DTO field (`ContractCreateRequestDto`) | UI field | Validation (zod, theo `api-docs`) |
|---|---|---|
| `roomId` | Select "Phòng" (lọc theo tòa đã chọn, chỉ phòng `available`) | bắt buộc, uuid |
| `tenantName` | "Họ tên người đại diện" | bắt buộc, 1–254 ký tự |
| `tenantPhone` | "Số điện thoại" | bắt buộc, `^(0[0-9]{9}\|\+84[0-9]{9})$` |
| `rentPrice` | "Tiền thuê/tháng" (`NumberInput`) | bắt buộc, ≥ 0 |
| `depositAmount` | "Tiền cọc" (`NumberInput`) | bắt buộc, ≥ 0 |
| `startDate`, `endDate` | "Ngày bắt đầu", "Ngày kết thúc" | bắt buộc, `YYYY-MM-DD`, `endDate` > `startDate` |
| `vehicleCount` | "Số xe gửi" | tuỳ chọn, số nguyên ≥ 0 (`P1-D32`; trống khi tòa có phí `per_vehicle` sẽ chặn hóa đơn — `VEHICLE_COUNT_MISSING`); sửa được cả khi HĐ `active` (`P6-D71`) |
| `description` | "Ghi chú" (textarea) | tuỳ chọn, ≤ 500 ký tự; sửa được khi HĐ `active` (`P6-D71`) |
| `templateKey` (apply-template) | Select "Mẫu hợp đồng" | bắt buộc khi áp mẫu |
| `signedContractMediaId` (activate) | Ô upload "Bản hợp đồng đã ký" (1 file PDF/ảnh) | bắt buộc, lấy từ `complete-upload.id` |

Chi tiết (`ContractDetailResponseDto`, `P6-D71`): thêm `templateKey`, `draftDocumentMediaId`, `signedContractMediaId`, `roomName`, `buildingId`.

Cột danh sách (`ContractListResponseDto`): `contractCode`, `roomName`, `tenantName`, `tenantPhone`, `status`, `rentPrice`, `startDate`–`endDate`. Không hiển thị field không có trong DTO (AGENTS luật 8).

## Tham chiếu code

- Feature mới: `fe/src/features/contracts/`. Copy pattern từ `fe/src/features/buildings/` (DTO, api, query keys, hooks, list page + `building-list-columns.tsx`/`building-list-mobile-row.tsx`, detail page, Dialog tạo/sửa `building-create-modal.tsx`/`building-edit-modal.tsx`).
- DataTable: `fe/src/components/ui/data-table/` + `fe/src/hooks/use-data-table.ts`, `use-data-table-state.ts` (filter/trang trên URL).
- Upload sau khi tạo: `fe/src/features/media/hooks/use-media-upload.ts`, `use-media-object-url-query.ts` (mở file private), pattern `fe/src/features/buildings/hooks/use-ownership-proof-uploader.ts` — **truyền `ownerId` thật**, không dùng UUID `0000…` mặc định của hook đó.
- Chọn phòng: hook `GET /me/rooms` của feature `rooms` (P6-03c); chọn tòa dùng hook `use-my-buildings-query.ts`.
- Route hiện có là placeholder: `fe/src/app/routes/roles/landlord.routes.tsx` (`/contracts/new`, `/contracts/templates` → gỡ). Menu `landlord-contracts` (`/contracts`) đã có trong `fe/src/config/navigation.config.ts`.

## Các bước triển khai

### Bước 1 — Đọc contract và chuẩn bị dữ liệu

- **Cách làm:** tạo branch theo `fe-feature-workflow`. Đọc các file contract hiện hành trong `api-docs`; nếu field/mã lỗi lệch issue thì comment vào issue trước khi code. Trên staging chuẩn bị 1 tòa `approved` có 2 phòng `available` và 1 mẫu HĐ seed (`standard-room-lease-v1`).
- **Kiểm tra bước:** Apidog `GET /contract-templates` trả ≥ 1 item; `GET /me/rooms?filter[status]=available` trả phòng của tòa.

### Bước 2 — Tầng dữ liệu `contracts`

- **Cách làm:** DTO chép từ `api-docs`; API + query keys + một hook cho mỗi query/mutation ở bảng Contract. Namespace `contracts` khai báo theo `fe-structure` §5 (cả `API_CODE_NAMESPACES` trong `src/lib/api/api-messages.ts`).
- **Kiểm tra bước:** `npm run build` pass; tạm gọi hook list ở trang trống thấy dữ liệu trong React Query Devtools.

### Bước 3 — Trang danh sách `/contracts`

- **Cách làm:** khung "danh sách" trong `fe-ui-ux/references/screen-patterns.md`; DataTable với filter **Tòa** (`filter[buildingId]`) và **Trạng thái** (`filter[status]`), phân trang server. Badge trạng thái cho `draft`, `active`, `terminated`, `expired` (giá trị khác hiển thị badge trung tính). Bấm dòng → `/contracts/:id`. Đủ 4 trạng thái loading / empty / filtered-empty / error.
- **Kiểm tra bước:** chọn filter "Đang hiệu lực" → URL có `status=active`, F5 vẫn giữ filter; landlord chưa có HĐ → empty state có nút "Tạo hợp đồng".

### Bước 4 — Dialog tạo HĐ nháp và sửa HĐ nháp

- **Cách làm:** Dialog mở từ trang danh sách (AGENTS luật 7), field theo bảng Mapping. Chọn tòa trước, sau đó Select phòng chỉ liệt kê phòng `available`. Thành công → toast `CONTRACT_CREATED`, đóng Dialog, điều hướng `/contracts/:id`. `409 ACTIVE_CONTRACT_EXISTS` → lỗi dưới field Phòng. Cùng form mở chế độ sửa từ trang chi tiết khi `status=draft` (chỉ gửi field đã đổi). HĐ `active` → nút **Sửa số xe / ghi chú** mở Dialog chỉ có `vehicleCount` + `description` (`P6-D71`); route chi tiết nhận query `?edit=vehicle` để tự mở Dialog này (P6-06c link tới). HĐ `terminated`/khác → ẩn nút Sửa.
- **Kiểm tra bước:** để trống SĐT → lỗi i18n dưới field, không gọi API; tạo HĐ cho phòng đã có HĐ active (gọi bằng Apidog trước) → lỗi ở field Phòng; HĐ `active` mở `/contracts/:id?edit=vehicle` → Dialog số xe, lưu `2` → toast `CONTRACT_UPDATED`, chi tiết hiện 2 xe.

### Bước 5 — Trang chi tiết `/contracts/:id`: thông tin, áp mẫu, bản nháp

- **Cách làm:** khung "chi tiết": card thông tin HĐ + card **Tài liệu hợp đồng** dạng 3 bước có số thứ tự (Chọn mẫu → Tải bản nháp → Upload bản ký và kích hoạt). Trạng thái 3 bước dựng từ chi tiết HĐ (`templateKey`, `draftDocumentMediaId`, `signedContractMediaId` — `P6-D71`), không chỉ từ state trong phiên. Chọn mẫu từ `GET /contract-templates` → `PUT apply-template`. Nút "Sinh bản nháp PDF" → `POST generate-draft-document` → mở file bằng `useMediaObjectUrl(mediaId)` ở tab mới. `422 TEMPLATE_DATA_INVALID` → `AlertBanner` nhắc bổ sung thông tin HĐ (nút mở Dialog sửa). Chỗ để tab **Thành viên** (P6-06d) chỉ thêm khi làm P6-06d, không để placeholder giả.
- **Kiểm tra bước:** áp mẫu → toast `CONTRACT_TEMPLATE_APPLIED`; sinh bản nháp → tab mới mở PDF có tên người thuê và giá thuê đúng; F5 → vẫn thấy mẫu đã chọn và link bản nháp.

### Bước 6 — Upload bản ký và kích hoạt

- **Cách làm:** ô upload 1 file (PDF/JPEG/PNG/WebP, chặn MIME/kích thước trước bằng `validateMediaFile`) với `ownerType=contract`, `ownerId=contractId`, `purpose=contract_signed`, có progress và nút thử lại. Nút **Kích hoạt** chỉ bật khi upload `completed`; mở Dialog xác nhận nêu hệ quả "phòng chuyển Đang thuê". `409 SIGNED_FILE_MISSING` → giữ Dialog, yêu cầu upload lại; `409 CONTRACT_NOT_READY` → toast + làm mới chi tiết. Thành công → invalidate `contracts` và query phòng/tòa liên quan.
- **Kiểm tra bước:** bấm Kích hoạt khi chưa upload → nút bị khóa; upload PDF rồi kích hoạt → badge `active`, mở chi tiết tòa thấy phòng chuyển Đang thuê.

### Bước 7 — Route, menu, i18n, rà soát

- **Cách làm:** thay placeholder trong `landlord.routes.tsx` bằng `/contracts` và `/contracts/:id` (gỡ `/contracts/new`, `/contracts/templates`). Text vào `src/i18n/locales/vi/contracts.json` trước rồi `en/contracts.json` cùng key; `apiSuccess.*`/`apiErrors.*` cho mọi mã ở bảng Contract; thuật ngữ theo `fe-ui-ux/references/copy-vi.md`.
- **Kiểm tra bước:** đổi ngôn ngữ vi ↔ en không còn chuỗi cứng; 360px không cuộn ngang; `npm run build`, `npm run lint`, `npm run i18n:check` pass.

## Ngoài phạm vi

- Trường **CCCD**, **Địa chỉ** của LL-11 — bỏ theo `P6-D68` (CCCD lưu bằng ảnh Media, `P0-D17`; ảnh CCCD member là Stretch theo `P6-D63`).
- LL-12 "Bỏ qua, dùng mẫu chuẩn" và `templateVariables` tuỳ chỉnh — mẫu chỉ đến từ seed (P6-01c).
- Trạng thái `signed` riêng, xóa HĐ nháp (không có endpoint DELETE), xuất `xlsx/csv/pdf` của `GET /contracts`.
- Thành viên, checkout: P6-06d. Quyết toán cọc: Stretch theo `P6-D61`.
- Ô chọn tài khoản tenant / tự liên kết theo SĐT — Stretch (`P6-D74`).
- Upload nhiều ảnh cho bản ký: `activate` nhận đúng 1 `signedContractMediaId`; nhiều trang thì landlord gộp PDF.

## Blocker

- Không có. (Liên kết tài khoản tenant: `P6-D74`; field chi tiết HĐ: `P6-D71`, BE bổ sung ở P6-01c/d và đồng bộ `api-docs` trong cùng PR implementation.)

## Acceptance

- [ ] `/contracts` hiển thị DataTable đúng cột DTO, lọc theo tòa + trạng thái, phân trang, giữ filter khi F5.
- [ ] Tạo HĐ nháp qua Dialog → `201 CONTRACT_CREATED`, chuyển tới chi tiết; thiếu field → lỗi dưới field, không gọi API.
- [ ] Phòng đã có HĐ active → `409 ACTIVE_CONTRACT_EXISTS` hiện dưới field Phòng.
- [ ] Form tạo không có ô chọn tài khoản; request không có `tenantId`.
- [ ] HĐ `active`: sửa số xe / ghi chú → `200 CONTRACT_UPDATED`; `?edit=vehicle` mở đúng Dialog.
- [ ] Áp mẫu → `200 CONTRACT_TEMPLATE_APPLIED`; sinh bản nháp → mở được PDF; HĐ không phải `draft` → các nút này bị ẩn; F5 vẫn hiện đúng 3 bước tài liệu.
- [ ] Chưa upload bản ký → không kích hoạt được; upload xong + kích hoạt → `200 CONTRACT_ACTIVATED`, badge `active`.
- [ ] `409 SIGNED_FILE_MISSING` / `CONTRACT_NOT_READY` → thông báo i18n đúng mã, không trắng màn hình.

## Definition of Done

- [ ] Mọi bước qua phần Kiểm tra bước; mọi ô Acceptance được người làm tick, kèm ảnh desktop + 360px trong PR.
- [ ] `npm run build` + `npm run lint` + `npm run i18n:check` pass; không có file `*.test.ts`; key có ở cả `vi` và `en`.
- [ ] Không sửa file ngoài phạm vi; PR vào `main` ghi `Closes pbl6-home-renter/docs#102`, ≥ 1 reviewer approve.
