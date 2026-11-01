# P6-07 — Seed dữ liệu demo, chốt staging, kịch bản demo

**Trạng thái:** 🟡 Open  
**Người phụ trách:** baoduong17  
**Người review:** cả team  
**Ước lượng:** 3 points · 8 giờ  
**Phụ thuộc:** P6-01e1–e3, P6-02g1–g3, P6-10b, P6-11 (seed chạy được khi các bảng đã có migration)  
**Repo / branch:** `Identity-Service`, `Tenancy-Service` · `feature/p6-07-demo-seed`; `pm` (kịch bản demo)  
**Iteration:** It6 (seed) → It7 (diễn tập)  
**Issue:** `docs#87`

> Đọc `AGENTS.md` + skill `be-feature-workflow` của repo trước.

## Mục tiêu

Staging có dữ liệu thật để demo vòng đời landlord-solo **từ tòa nhà tới phát hành hóa đơn**, chạy lại seed không nhân đôi dữ liệu, và có `pm/phase-6/demo-script.md` để cả team diễn tập.

## Quyết định áp dụng

- `P6-D61` — không có Payment: demo dừng ở `issued`; không seed thanh toán, không seed quyết toán cọc.
- `P6-D62` — có 1 HĐ đã checkout (`terminated`) để demo phòng `maintenance` → `mark-ready`.
- `P6-D64` — hóa đơn sinh bằng `POST /invoices/generate`; seed có đủ 3 trạng thái `pending`, `issued`, `void` (kèm bản thay thế trỏ `voided_invoice_id`).
- `P6-D65` — tiền/chỉ số là string decimal.
- `P1-D34` — mỗi phòng đang thuê có reading baseline trước kỳ đầu.
- `P0-D29` — 2 member không có tài khoản (`tenant_id NULL`).

## Dữ liệu

| Nhóm | Số lượng | Ghi chú |
|---|---|---|
| User (Identity) | 1 admin, 2 landlord, 6 tenant | UUID **cố định** khai báo trong một hằng số dùng chung giữa 2 seeder (Tenancy seed `landlord_id`/`tenant_id` bằng đúng UUID này). Mật khẩu demo ghi trong `demo-script.md`, không ghi trong code |
| Building | 3 `approved`, 1 `pending` (cho demo admin duyệt) | Landlord A 2 tòa, landlord B 2 tòa |
| Room | 20 | đủ `available` / `occupied` / `maintenance` |
| RatePolicy | 1 bộ/tòa + 1 bộ override ở 1 phòng | có điện EVN bậc thang, nước khoán đầu người, phí QLVH `per_area_m2`, gửi xe `per_vehicle` |
| BillingSetting | 1/tòa | |
| Contract | 8 `active`, 1 `terminated`, 1 `draft` | 1 HĐ bắt đầu giữa tháng (để thấy prorate §8) |
| ContractMember | đại diện + 0–2 member mỗi HĐ | 2 member `tenant_id NULL` |
| MeterReading | baseline + 2 kỳ (`2026-09`, `2026-10`) cho mọi phòng có HĐ | 1 phòng thiếu chỉ số nước kỳ `2026-10` (để demo `blocked READING_MISSING`) |
| Invoice | kỳ `2026-09`: tất cả `issued`, 1 cặp `void` + bản thay thế; kỳ `2026-10`: `pending` | tạo bằng chính calculator của P6-02g1, không tự điền số |

## Tham chiếu code

- Seeder mẫu: `boilerplate/src/modules/sample/infrastructure/seeds/sample-create.seeder.ts`, `Identity-Service/src/modules/users/infrastructure/seeds/admin.seeder.ts` (idempotent).
- Lệnh: `npm run seed:run` (typeorm-extension, `src/shared/infrastructure/database/data-source.ts`).

## Các bước triển khai

### Bước 1 — Seed Identity

- **File tạo:** seeder user demo trong `Identity-Service/src/modules/users/infrastructure/seeds/` (*mới*).
- **Cách làm:** upsert theo email; UUID cố định; landlord có `LandlordProfile`.
- **Kiểm tra bước:** chạy `npm run seed:run` 2 lần → `SELECT count(*) FROM users;` không đổi giữa 2 lần; đăng nhập được bằng tài khoản landlord A.

### Bước 2 — Seed Tenancy: tòa, phòng, đơn giá, HĐ, member

- **File tạo:** seeder trong `infrastructure/seeds/` của từng module liên quan (*mới*), theo thứ tự building → room → rate-policy/billing-setting → contract → member.
- **Cách làm:** tạo qua domain entity + repository (để giữ invariant), không `INSERT` SQL thô; upsert theo khóa tự nhiên (tên tòa + landlord, mã phòng + tòa).
- **Kiểm tra bước:** chạy 2 lần → số dòng các bảng không đổi; `GET /api/v1/contracts` với landlord A thấy đúng số HĐ.

### Bước 3 — Seed reading và hóa đơn

- **Cách làm:** reading theo bảng; hóa đơn sinh bằng use case generate của P6-02g2 (gọi command qua `CommandBus` trong seeder hoặc chạy `POST /invoices/generate` bằng script), rồi issue/void theo bảng.
- **Kiểm tra bước:** `POST /invoices/generate { buildingId: <tòa 1>, period: "2026-10" }` trên DB đã seed → `blocked` có đúng 1 phòng `READING_MISSING`; kiểm tra tay 1 hóa đơn kỳ `2026-09` khớp bảng Ví dụ số của P6-02g1.

### Bước 4 — Staging

- **Cách làm:** deploy mọi service (identity, tenancy, ai, gateway, web) bằng workflow từng repo; chạy migration + seed trên staging.
- **Kiểm tra bước:** `GET /api/v1/{identity,tenancy,ai}/health` qua gateway → `200`; web đăng nhập landlord A thấy dashboard có dữ liệu.

### Bước 5 — Kịch bản demo + diễn tập

- **File tạo:** `pm/phase-6/demo-script.md` (*mới*): tài khoản, thứ tự màn hình (admin duyệt tòa → landlord tạo HĐ, upload bản ký, activate → thêm member → chụp công tơ OCR → generate hóa đơn → xử lý phòng bị chặn → phát hành → void + tạo lại → checkout → mark-ready), câu nói cho từng bước, phương án dự phòng khi OCR/API lỗi (nhập tay, dữ liệu đã seed sẵn).
- **Kiểm tra bước:** diễn tập 1 lần cuối It6 với cả team; bug ghi thành issue It7.

## Ngoài phạm vi

- Payment, quyết toán cọc, VietQR (`P6-D61`).
- Seed ảnh lên R2: chỉ seed ảnh minh chứng cho 2 reading và 1 bản ký HĐ bằng cách upload thật qua Identity trong lúc chuẩn bị demo (không seed thẳng vào bảng `media`).
- Mobile.

## Acceptance

- [ ] Seed chạy 2 lần không nhân đôi (đếm dòng trước/sau, đính kèm PR).
- [ ] Staging: 3 health `200`, đăng nhập 3 vai trò được.
- [ ] Đi hết `demo-script.md` trên staging không lỗi chặn.

## Definition of Done

- [ ] PR Identity + Tenancy merged; `demo-script.md` được team review.
- [ ] Biên bản diễn tập + danh sách bug It7.
