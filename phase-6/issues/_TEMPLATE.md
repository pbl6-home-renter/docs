# P6-XX — <Tên task ngắn, động từ đầu câu>

**Epic:** [P6-YY](P6-YY-<slug>.md) (bỏ dòng này nếu task không thuộc epic)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** <GitHub username>  
**Người review:** <BE Lead / FE Lead / API owner>  
**Ước lượng:** <pts> points · <giờ> giờ  
**Phụ thuộc:** <ID task phải xong trước, hoặc —>  
**Repo / branch:** `<repo>` · `feature/p6-xx-<slug>`

## Mục tiêu

<1–2 câu mô tả kết quả nhìn thấy được khi xong, ví dụ: "Landlord gọi `POST /contracts` tạo được hợp đồng nháp, nhận `201 CONTRACT_CREATED`.">

## Contract

- Endpoint: `api-doc/src/paths/<module>/<file>.yaml` (`<operationId>`).
- Request DTO: `api-doc/src/requests/<...>.yaml`.
- Response DTO: `api-doc/src/responses/<...>.yaml` (hoặc schema trong `openapi.yaml`).
- Role, status code, success code, error code cần xử lý.
- Business rule bắt buộc (trích từ contract hoặc `pm/phase-1/discovery/*`).

## Tham chiếu code

- Slice mẫu cần copy pattern, kèm đường dẫn file thật trong repo (ví dụ `Tenancy-Service/src/modules/sample/application/commands/sample-create/`).
- Domain/repository đã có sẵn và được dùng lại (không viết lại).

## Các bước triển khai

> Mỗi bước làm trong ≤ ½ ngày. Hoàn thành **Kiểm tra bước** trước khi sang bước tiếp theo.

### Bước 1 — Đọc contract và chạy service local

- **Cách làm:**
  - Pull `main`, tạo branch `feature/p6-xx-<slug>`.
  - Đọc các file trong mục Contract, ghi lại field/route/error code chưa rõ vào comment của issue.
  - `npm ci && npm run migration:run && npm run start:dev`.
- **Kiểm tra bước:** `GET /api/v1/health` trả `200`; Swagger mở được tại `/docs`.

### Bước 2 — <tên bước>

- **File tạo/sửa:** `src/modules/<module>/<layer>/<file>.ts` (ghi rõ *mới* hay *sửa*).
- **Cách làm:**
  - <tên class/method cần viết, gọi hàm domain nào, map field nào>
- **Kiểm tra bước:** <lệnh hoặc request cụ thể + kết quả mong đợi>

### Bước N — Đăng ký module và hoàn thiện Swagger

- **File sửa:** `<module>.module.ts`, controller.
- **Kiểm tra bước:** `npm run build` và `npm run lint` pass; Swagger hiển thị đúng `operationId`.

## Quyết định tạm thời / Ngoài phạm vi

- <Những gì cố ý chưa làm, kèm `TODO` cần để lại trong code.>

## Cập nhật `api-doc` (bắt buộc trước khi đóng issue)

- [ ] Viết/cập nhật sequence diagram (block mermaid trong `description`) khớp implementation.
- [ ] Đổi `x-apidog-status: designing` → `released` cho endpoint đã verify.
- [ ] Sửa contract nếu phát hiện sai (cần API owner duyệt), sync Apidog, link PR `api-doc` vào issue.

## Manual verification (Apidog)

1. Happy path → `<status> <CODE>`.
2. Thiếu/sai dữ liệu → `422 VALIDATION_FAILED`.
3. Sai role → `403 FORBIDDEN`; không có token → `401`.
4. <Case nghiệp vụ riêng của task.>

## Definition of Done

- [ ] Mọi bước ở trên đã qua phần Kiểm tra bước.
- [ ] `npm run build` + `npm run lint` pass.
- [ ] PR vào `main` có mô tả `Closes pbl6-home-renter/docs#<số issue>` và link file `api-doc` đã dùng.
- [ ] Ít nhất 1 reviewer approve; ảnh chụp hoặc export Apidog đính kèm PR.
