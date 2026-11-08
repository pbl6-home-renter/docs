# P6-06d — Thành viên hợp đồng và trả phòng (Web)

**Epic:** [P6-06](P6-06-fe-contract-invoice-screens.md)  
**Trạng thái:** 🟡 Open — ⚠️ **Nguy cơ trễ — có thể dời sang It7** (phụ thuộc BE P6-01e1/e3 viết trong It6)  
**Người phụ trách:** ThaiBao11125  
**Người review:** baoduong17  
**Ước lượng:** 3 points · 6–8 giờ  
**Phụ thuộc:** P6-06a (trang chi tiết HĐ); BE P6-01e1 (thành viên HĐ theo `P6-D63`), P6-01e3 (checkout theo `P6-D62`);; FE P6-03c (API phòng: `GET /rooms/{id}`, `mark-ready`) 
**Repo / branch:** `fe` · `feat/p6-06d-contract-members-checkout`  
**Iteration:** It6 (09/11–15/11)  
**Issue:** `docs#105`

> **Đọc trước khi code:** `fe/AGENTS.md` và skill trong `fe/.agents/skills/` (`fe-feature-workflow` → `fe-structure` → `fe-code-style` → `fe-ui-ux` + `references/*`). Issue **không** quy định cách đặt file, đặt tên hay style — nếu issue nói khác skill thì làm theo skill. Nguồn mâu thuẫn xử lý theo [`P6-D75`](../decisions.md#d75--thứ-tự-ưu-tiên-nguồn-và-cách-xử-lý-câu-hỏi-mở): `decisions.md` > `api-docs` > skill > issue.

## Mục tiêu

Trên trang chi tiết HĐ (`/contracts/:id`, P6-06a) có tab **Thành viên**: xem người đang ở và đã rời, thêm người ở ghép, ghi nhận người rời đi. HĐ `active` có nút **Trả phòng**: nếu chưa phát hành hóa đơn kỳ trả phòng thì báo rõ và dẫn tới trang hóa đơn; thành công thì HĐ `terminated`, phòng hiện **Bảo trì** kèm nút **Sẵn sàng cho thuê**.

## Quyết định áp dụng

- `P6-D63` — người đại diện tự thành member khi activate (FE không thêm tay); danh sách member **không** có cờ đại diện; thêm/rời chỉ khi HĐ `active` (`409 CONTRACT_NOT_ACTIVE`); rời = set `leftAt`, không xóa bản ghi (`P2-D44`); `ContractMemberAddRequestDto` chỉ còn `contractId`, `tenantId?`, `tenantName`, `tenantPhone?`, `joinedAt`; ảnh CCCD member, tự liên kết theo SĐT là Stretch.
- `P6-D62` — checkout cần HĐ `active` **và** hóa đơn kỳ chứa ngày trả phòng đã `issued` (không còn `pending`), sai → `409 SETTLEMENT_NOT_READY`; thành công: HĐ `terminated`, member còn ở được set `leftAt = completedOn`, phòng `maintenance`; landlord bấm `mark-ready` để phòng về `available`. Không phí chấm dứt sớm, không tự prorate.
- `P6-D64` — chênh lệch tiền phòng/đền bù khi trả phòng ghi bằng phí khác của hóa đơn kỳ cuối (làm ở P6-06c), không có hóa đơn quyết toán.
- `P6-D61` — không có quyết toán cọc.
- `P6-D65` — `headCount` đếm theo `joinedAt`/`leftAt`; vì vậy ngày vào/rời phải nhập đúng.
- `P6-D71` — `joinedAt` ∈ [`startDate`, `endDate`] của HĐ; `leftOn` ≥ `joinedAt` và ≤ `endDate`; `completedOn` ≥ `startDate` và ≤ hôm nay; trùng `tenantPhone` với member chưa rời → `409 MEMBER_ALREADY_EXISTS`; nhóm Đang ở / Đã rời theo `status` (`active`/`left`) của response, không có CCCD/cờ đại diện; HĐ `active` sửa được số xe (Dialog ở P6-06a).
- `P6-D74` — **không** có ô chọn tài khoản tenant; chỉ nhập họ tên + SĐT, không gửi `tenantId`.

## Contract

| Endpoint (`api-docs/src/paths/`) | Thành công | Lỗi cần xử lý trên UI |
|---|---|---|
| `GET /contract-members?filter[contractId]` (`contracts/contract-members.yaml`, `getContractMembers`) | `200 CONTRACT_MEMBERS_FETCHED` | `422 CONTRACT_ID_REQUIRED` |
| `POST /contract-members` (`postContractMembers`) | `201 CONTRACT_MEMBER_ADDED` | `409 MEMBER_ALREADY_EXISTS`, `409 CONTRACT_NOT_ACTIVE`, `422 TENANT_IDENTITY_INVALID`, `422 VALIDATION_FAILED` |
| `POST /contract-members/{id}/leave-contract` (`postContractMembersContractmemberidLeaveContract`) | `200 CONTRACT_MEMBER_LEFT` | `409 MEMBER_ALREADY_LEFT`, `422 LEFT_DATE_INVALID` |
| `POST /contracts/{id}/complete-checkout` (`contracts-contractId-complete-checkout.yaml`) | `200 CONTRACT_CHECKOUT_COMPLETED` | `409 CONTRACT_NOT_ACTIVE`, `409 SETTLEMENT_NOT_READY`, `422 VALIDATION_FAILED` (ngày ngoài [`startDate`, hôm nay] hoặc trước ngày vào của một thành viên) |
| `GET /rooms/{roomId}` (`rooms/rooms-roomId.yaml`) | `200 ROOM_FETCHED` | `404` |
| `POST /rooms/{roomId}/mark-ready` (`rooms/rooms-roomId-mark-ready.yaml`) | `200 ROOM_MARKED_READY` | `409 INVALID_ROOM_TRANSITION` |

### Mapping field

| DTO field | UI | Validation / ghi chú |
|---|---|---|
| `contractId` | lấy từ URL | không cho nhập |
| `tenantName` | "Họ tên" | bắt buộc, 1–254 ký tự |
| `tenantPhone` | "Số điện thoại" | **bắt buộc** vì web không gửi `tenantId` (`P0-D29`, `P6-D74`), `^(0[0-9]{9}\|\+84[0-9]{9})$` |
| `joinedAt` | "Ngày vào ở" (mặc định hôm nay, kẹp vào khoảng HĐ) | bắt buộc, `YYYY-MM-DD`, trong [`startDate`, `endDate`] của HĐ (`P6-D71`; FE chặn trước bằng zod, BE vẫn kiểm) |
| `tenantId` | — | không gửi (`P6-D74`) |
| `leftOn` (leave) | "Ngày rời đi" trong Dialog | bắt buộc, ≥ `joinedAt` và ≤ `endDate` (`P6-D71`); sai → `LEFT_DATE_INVALID` dưới field |
| `completedOn` (checkout) | "Ngày trả phòng" trong Dialog | bắt buộc, mặc định hôm nay, trong [`startDate`, hôm nay] (`P6-D71`) |
| response `tenantName`, `tenantPhone`, `joinedAt`, `leftAt`, `status` | cột danh sách; nhóm "Đang ở" (`status=active`, kể cả `leftAt` tương lai) / "Đã rời" (`status=left`) | `P6-D71`; không có CCCD, cờ đại diện |
| room `status` | badge phòng trên card HĐ | `maintenance` → nút "Sẵn sàng cho thuê" |

## Tham chiếu code

- Thêm vào feature `fe/src/features/contracts/` (P6-06a) phần members + checkout; phòng dùng hook của `fe/src/features/rooms/` (P6-03c), không viết lại.
- Copy pattern Dialog xác nhận + mutation: `fe/src/features/buildings/components/delete-building-dialog.tsx`, `hooks/use-delete-building-mutation.ts`; form trong Dialog: `building-edit-modal.tsx` + `forms/use-building-edit-form.ts`.
- Tab trên trang chi tiết: khung "chi tiết" trong `fe-ui-ux/references/screen-patterns.md`.

## Các bước triển khai

### Bước 1 — Xác nhận contract BE đã sẵn sàng

- **Cách làm:** đọc [P6-01e1](P6-01e1-contract-members.md), [P6-01e3](P6-01e3-contract-checkout.md); chỉ bắt đầu khi hai task này merge và `api-docs` phản ánh contract hiện hành (`contract-member-*`, `complete-checkout`; bỏ `identityCardNumber`, `isRepresentative`, `pending_cleanup`). Chưa có đến giữa It6 → báo PM dời sang It7, ghi vào comment issue.
- **Kiểm tra bước:** Apidog: activate 1 HĐ → `GET /contract-members?filter[contractId]` có sẵn người đại diện.

### Bước 2 — Tầng dữ liệu members + checkout

- **Cách làm:** DTO, API, query keys, hook cho list/add/leave member và checkout, theo `fe-feature-workflow` Bước 2. Mutation checkout invalidate `contracts`, `rooms`, `invoices`.
- **Kiểm tra bước:** `npm run build` pass.

### Bước 3 — Tab Thành viên

- **Cách làm:** tab trên `/contracts/:id`, 2 nhóm Đang ở / Đã rời. HĐ `active`: nút **Thêm thành viên** (Dialog form theo Mapping) và menu dòng **Ghi nhận rời đi** (Dialog ngày rời). HĐ khác `active`: ẩn nút, hiện ghi chú "Chỉ thêm/rời thành viên khi hợp đồng đang hiệu lực". `409 MEMBER_ALREADY_EXISTS` → lỗi dưới field SĐT ("Số điện thoại đã có trong hợp đồng").
- **Kiểm tra bước:** thêm "Nguyễn Văn C" → xuất hiện ở nhóm Đang ở; ghi nhận rời ngày hôm qua → chuyển sang Đã rời, không biến mất; rời ngày mai → vẫn ở Đang ở, hiện ngày rời; thêm lại cùng SĐT người đang ở → lỗi dưới field SĐT.

### Bước 4 — Dialog Trả phòng

- **Cách làm:** nút **Trả phòng** chỉ hiện khi HĐ `active`. Dialog giải thích điều kiện ("Cần phát hành hóa đơn của kỳ chứa ngày trả phòng; tiền đền bù/chênh lệch thêm vào phí khác của hóa đơn đó") + ô ngày. `409 SETTLEMENT_NOT_READY` → `AlertBanner` trong Dialog + nút **Mở hóa đơn kỳ <YYYY-MM>** tới `/invoices?buildingId=…&period=…` (P6-06c). Thành công → toast, badge HĐ `terminated`, tab Thành viên làm mới.
- **Kiểm tra bước:** ô ngày không cho chọn ngày mai/trước `startDate`; kỳ trả phòng còn hóa đơn `pending` → báo đúng + link mở đúng bộ lọc; phát hành xong rồi trả phòng → HĐ `terminated`, mọi member chuyển Đã rời.

### Bước 5 — Phòng sau khi trả: Sẵn sàng cho thuê

- **Cách làm:** card HĐ hiện trạng thái phòng (`GET /rooms/{roomId}`). Phòng `maintenance` → nút **Sẵn sàng cho thuê** → Dialog xác nhận → `mark-ready`. `409 INVALID_ROOM_TRANSITION` → toast + làm mới.
- **Kiểm tra bước:** sau checkout card hiện "Bảo trì"; bấm Sẵn sàng → "Còn trống"; Select phòng ở Dialog tạo HĐ (P6-06a) lại thấy phòng này.

### Bước 6 — i18n, rà soát

- **Cách làm:** text vào `src/i18n/locales/vi/contracts.json` rồi `en/contracts.json` cùng key (namespace của P6-06a); `apiSuccess.*`/`apiErrors.*` cho mọi mã ở bảng Contract (mã phòng nằm ở namespace của `rooms` nếu P6-03c đã thêm).
- **Kiểm tra bước:** 360px không cuộn ngang; vi ↔ en không còn chuỗi cứng; `npm run build`, `npm run lint`, `npm run i18n:check` pass.

## Ngoài phạm vi

- LL-17 "xóa thành viên" — thay bằng ghi nhận rời (`leftAt`) theo `P6-D63`, `P2-D44`.
- LL-15/LL-16 trường CCCD, ảnh CCCD member, cờ "người đại diện" — `P6-D63`.
- LL-16/LL-54 toggle "Có xe" từng thành viên — số xe nằm ở `contracts.vehicleCount` (`P1-D32`, `P6-D65`), sửa bằng Dialog số xe của P6-06a khi HĐ `active` (`P6-D71`).
- Ô chọn tài khoản tenant, tự liên kết theo SĐT — Stretch (`P6-D74`).
- Sửa thông tin thành viên (`PATCH /contract-members/{id}`) — `P6-D63` không yêu cầu; làm sau nếu PM duyệt.
- LL-29 chốt số lần cuối: dùng màn P6-06b như mọi kỳ. LL-30 hóa đơn quyết toán riêng — `P6-D64`. LL-31 quyết toán cọc — `P6-D61`. Phí chấm dứt sớm, tự prorate theo ngày trả — `P6-D62`.
- Hai HĐ trong cùng một kỳ của một phòng — ngoài MVP theo `P6-D62`.

## Blocker

- Không có. (Liên kết tài khoản: `P6-D74`; rule ngày/trùng/`status` member: `P6-D71`.) BE chi tiết: [P6-01e1](P6-01e1-contract-members.md), [P6-01e3](P6-01e3-contract-checkout.md).

## Acceptance

- [ ] Tab Thành viên của HĐ vừa activate có người đại diện; không có nút thêm tay người đại diện.
- [ ] Thêm thành viên → `201 CONTRACT_MEMBER_ADDED`; HĐ không `active` → không có nút, gọi ép → `409 CONTRACT_NOT_ACTIVE` hiển thị đúng.
- [ ] Form thêm thành viên không có ô chọn tài khoản; trùng SĐT người đang ở → `409 MEMBER_ALREADY_EXISTS` dưới field SĐT; ngày vào ngoài khoảng HĐ bị chặn.
- [ ] Ghi nhận rời → `200 CONTRACT_MEMBER_LEFT`, thành viên chuyển nhóm theo `status`; ngày sai → `422 LEFT_DATE_INVALID` dưới field.
- [ ] Trả phòng khi hóa đơn kỳ chưa phát hành → `409 SETTLEMENT_NOT_READY` + link tới hóa đơn đúng tòa/kỳ.
- [ ] Trả phòng hợp lệ → `200 CONTRACT_CHECKOUT_COMPLETED`, HĐ `terminated`, phòng `maintenance`.
- [ ] Sẵn sàng cho thuê → `200 ROOM_MARKED_READY`, phòng `available`.

## Definition of Done

- [ ] Mọi bước qua phần Kiểm tra bước; mọi ô Acceptance được người làm tick, kèm ảnh desktop + 360px trong PR.
- [ ] `npm run build` + `npm run lint` + `npm run i18n:check` pass; không có file `*.test.ts`; key có ở cả `vi` và `en`.
- [ ] Không sửa file ngoài phạm vi; PR vào `main` ghi `Closes pbl6-home-renter/docs#105`, ≥ 1 reviewer approve.
