# P1-04 — Shared Conventions (Quy ước chung FE + Mobile)

**Status:** 🟡 Open
**Assignee:** FE + Mobile (mỗi người đề xuất) · **PM (duyệt & chốt)**
**Depends on:** P1-02, P1-03 (tech stack — để biết mình dùng thư viện/bộ validate gì)
**Deliverable:** Bảng quy ước chung đã chốt → `pm/phase-1/discovery/shared-conventions.md`

---

## Mục đích

Thống nhất các quy ước **chung giữa Web (React) và Mobile (Android)** để người dùng có trải nghiệm nhất quán trên cả 2 nền tảng, và để FE/Mobile nói chuyện API với backend không lệch.

> **Cách làm:** FE và Mobile **mỗi người đề xuất** convention của mình dựa trên tech stack đã chọn (P1-02/P1-03). Khi lệch nhau, PM sẽ **chọn & chốt 1 chuẩn chung** — nếu lệch cái nào thì bắt cả 2 sửa theo.
>
> Backend là nguồn chân lý cho validate/error — client-side chỉ là tiện ích UX.

---

## Các chủ đề cần đề xuất & thống nhất

### 1. Validation rules
- Đề xuất rule + regex cho: **email**, **số điện thoại VN** (0xx-xxx-xxxx), **price (VND, số nguyên không thập phân)**, **CCCD (12 số)**, **password** (tối thiểu gì).
- FE dùng Zod schema gì, Mobile dùng extension function gì — để **cùng kết quả** với nhau.

### 2. Error response & hiển thị
- Thống nhất **format lỗi API** (statusCode, message, error, details:[{field,message}], timestamp) — cần backend đồng ý.
- Ánh xạ: 400/401/403/404/422/500 → hành vi UI (hiện field-error / redirect login / toast / page 404...).

### 3. Date / Time / Currency format
- **Date:** `DD/MM/YYYY` (vi-VN)? Format long (có giờ)? Relative ("2 ngày trước")?
- **Currency:** `2.000.000 VNĐ` (dấu chấm, không thập phân)? Code mẫu FE (`Intl.NumberFormat`) + Mobile (`NumberFormat.getCurrencyInstance(Locale("vi","VN"))`).
- **Timezone:** API luôn ISO 8601 UTC, chuyển local ở UI.

### 4. Image handling
- Max size (ảnh phòng / avatar / ảnh công tơ / scan PDF), định dạng cho phép (JPEG/PNG/WebP/PDF), nén/resize trước upload.

### 5. API contract alignment
- Cách FE (generate type từ OpenAPI — tool gì) và Mobile (openapi-generator hay viết tay DTO) tiêu thụ chung spec.
- Mock server khi BE chưa xong (Apidog mock / MSW / WireMock).

### 6. Translation / i18n 🔤 (BẮT BUỘC thống nhất)
Mục tiêu: **1 nguồn chuỗi dịch dùng chung cho cả Web (React) và Mobile (Android)**, không ai tự viết chuỗi rời mỗi nơi.

> Yêu cầu kỹ thuật (mỗi bên đề xuất cách hiện thực, PM chốt 1 phương án chung):
> - **1 file gốc chung** (vd JSON/YAML/CSV trong repo hub hoặc file `.xlsx` chia sẻ) chứa mọi text UI với key → (vi, en, ...).
> - Cách FE và Mobile **đọc từ cùng file đó** (cùng key naming, cùng cấu trúc). Ví dụ: FE dùng `i18next` / `react-i18next`, Mobile dùng `Android string resources` nhưng **video ra từ cùng nguồn** qua script sinh (codegen). Nêu rõ: dùng tool nào để **sinh** `strings.xml` (Android) và `en/vi.json` (React) từ 1 file nguồn.
> - **Quy ước key**: naming (vd `login.title`, `invoice.status.paid`) để 2 bên khớp.
> - **Track từ nào đang dùng / không dùng / thiếu:**
>   - *Từ thiếu* (referenced trong code nhưng không có trong file nguồn) → **báo lỗi** (fail build, hoặc test check).
>   - *Từ thừa* (có trong file nhưng không ai dùng) → **cảnh báo/unused**, để dọn.
>   - Đề xuất cơ chế: script kiểm tra (linter/test) + nêu tool & cách chạy.
> - **Đối tượng có nhu cầu dịch:** Dem ngôn ngữ MVP (vi) nhưng giữ cấu trúc sẵn cho en. Nếu chưa cần 2 ngôn ngữ UI, vẫn thống nhất hạ tầng để sau này thêm nhanh.

### 7. Design token (đầu vào cho P1-05)
- Đề xuất **primary color**, **typography scale**, **spacing (4px base)**, **border-radius**, dark mode có hay không.
- Lưu ý: quyết định UI thật nằm ở P1-05; mục này chỉ chốt **token giá trị** để P1-05 dùng.

---

## Yêu cầu output

1. FE và Mobile mỗi người điền đề xuất vào một phần trong document (hoặc file riêng):
   - `pm/phase-1/discovery/fe-proposal.md` (đã có) — thêm mục "Shared conventions".
   - `pm/phase-1/discovery/mobile-proposal.md` (đã có) — thêm mục "Shared conventions".
2. PM review → chốt bảng chung vào `pm/phase-1/discovery/shared-conventions.md`.
3. Nếu không thống nhất được 1 mục → PM quyết định, ghi lý do.

## Định nghĩa "Done"

- [ ] FE + Mobile đã đề xuất cho đủ các mục 1–7 (gồm **mục 6 Translation/i18n**: hyperfile chung + script sinh + cơ chế báo thiếu/thừa key).
- [ ] PM chốt bảng `shared-conventions.md`.
- [ ] Mọi feature ảnh hưởng 2 platform được đánh dấu trong proposal.
