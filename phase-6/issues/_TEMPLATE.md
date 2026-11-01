# P6-XX — <Tên task ngắn, động từ đầu câu>

**Epic:** [P6-YY](P6-YY-<slug>.md) (bỏ dòng này nếu task không thuộc epic)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** <GitHub username>  
**Người review:** <BE Lead / FE Lead / API owner>  
**Ước lượng:** <pts> points · <giờ> giờ (**tối đa 3 points, khoảng ≤ 15 file mỗi PR** — lớn hơn thì tách sub-issue)  
**Phụ thuộc:** <ID task phải xong trước, hoặc —>  
**Repo / branch:** `<repo>` · `feature/p6-xx-<slug>`  
**Issue:** `docs#<số>`

> **Đọc trước khi code:** `AGENTS.md` và skill trong `.agents/skills/` của repo (backend: `be-feature-workflow`; FE: `fe-feature-workflow`). Issue **không** quy định cách đặt file, đặt tên hay style — nếu issue nói khác skill thì làm theo skill. Nguồn mâu thuẫn xử lý theo [`P6-D75`](../decisions.md#d75--thứ-tự-ưu-tiên-nguồn-và-cách-xử-lý-câu-hỏi-mở): `decisions.md` > `api-docs` > skill > issue.

## Mục tiêu

<1–2 câu mô tả kết quả nhìn thấy được khi xong, ví dụ: "Landlord gọi `POST /contracts` tạo được hợp đồng nháp, nhận `201 CONTRACT_CREATED`.">

## Quyết định áp dụng

<Liệt kê D-ID kèm tiền tố phase và 1 dòng tóm tắt phần áp dụng cho task này. Issue không tự đặt business rule mới; thiếu rule thì ghi vào mục "Blocker" và **không làm phần đó**.>

- `P6-D6x` — …
- `P1-D39` — …

## Contract

- Endpoint: `api-docs/src/paths/<module>/<file>.yaml` (`<operationId>`).
- Request DTO: `api-docs/src/requests/<...>.yaml`.
- Response DTO: `api-docs/src/responses/<...>.yaml`.
- Role, status code, success code, error code cần xử lý.

### Mapping field

| Request / Response field | Domain prop | Cột DB (`database-design.md` §…) | Ghi chú / validation |
|---|---|---|---|
| `<field>` | `<prop>` | `<column>` | <rule, đơn vị, nullable> |

### Ví dụ số (bắt buộc nếu task có tính toán)

| Input | Kết quả mong đợi |
|---|---|
| <vd: chỉ số cũ 1200, mới 1380, giá 3.500đ> | <vd: tiêu thụ 180, thành tiền 630.000đ> |

## Tham chiếu code

- Module mẫu để copy pattern (đường dẫn thật trong repo, vd. `Tenancy-Service/src/modules/rate-policy/`).
- Domain/repository/hàm có sẵn được dùng lại (không viết lại).

## Các bước triển khai

> Mỗi bước ≤ ½ ngày. Mỗi bước có **Kiểm tra bước** chạy được (request cụ thể, câu SQL, kết quả mong đợi) — không chấp nhận chỉ "`npm run build` pass".

### Bước 1 — Đọc contract và chạy service local

- **Cách làm:**
  - Pull `main`, tạo branch `feature/p6-xx-<slug>`.
  - Đọc mục Contract + Quyết định áp dụng; field/route/error code chưa rõ thì comment vào issue **trước** khi code.
  - `npm ci && npm run migration:run && npm run start:dev`.
- **Kiểm tra bước:** `GET /api/v1/<path>/health` trả `200`; Swagger mở được.

### Bước 2 — <tên bước>

- **File tạo/sửa:** `<đường dẫn>` (*mới* / *sửa*).
- **Cách làm:** <class/method cần viết, gọi domain nào, map field nào — không lặp lại quy ước code đã có trong skill>
- **Kiểm tra bước:** <lệnh hoặc request cụ thể + kết quả mong đợi>

### Bước N — Hoàn thiện Swagger và `api-docs`

- **Kiểm tra bước:** `npm run build` + `npm run lint` pass; Swagger hiển thị đúng `operationId`.

## Ngoài phạm vi

- <Những gì cố ý chưa làm, kèm D-ID hoặc task sẽ làm sau.>

## Blocker

- <Câu hỏi nghiệp vụ còn mở → chờ D-ID mới. Để trống nếu không có.>

## Cập nhật `api-docs` (bắt buộc trước khi đóng issue)

- [ ] Sequence diagram (mermaid trong `description`) khớp implementation.
- [ ] `x-apidog-status: designing` → `released` cho endpoint đã verify.
- [ ] Phát hiện contract sai → sửa theo `decisions.md`, API owner duyệt, `npm run bundle`, link PR `api-docs` vào issue.

## Acceptance (Apidog)

- [ ] Happy path → `<status> <CODE>`.
- [ ] Thiếu/sai dữ liệu → `422 VALIDATION_FAILED`.
- [ ] Sai role → `403 FORBIDDEN`; không có token → `401`; tài nguyên của landlord khác → `404`/`403` theo contract.
- [ ] <Case nghiệp vụ riêng, mỗi case một dòng có mã lỗi.>

## Definition of Done

- [ ] Mọi bước qua phần Kiểm tra bước; mọi ô Acceptance được **tick bởi người làm**, kèm export Apidog hoặc ảnh chụp trong PR.
- [ ] `npm run build` + `npm run lint` pass; không có file test, không sửa file ngoài phạm vi (kể cả `src/shared`).
- [ ] Migration (nếu có) sinh bằng `migration:generate`, `migration:run` + `migration:revert` pass từ DB trống.
- [ ] PR vào `main` ghi `Closes pbl6-home-renter/docs#<số issue>`, ≥ 1 reviewer approve.
