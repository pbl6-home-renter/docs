# P8-05 — FE tenant: xem invoice đã phát hành và mở từ notification

**Epic:** Phase 8  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** `ThaiBao11125`  
**Người review:** FE reviewer / PM  
**Ước lượng:** 2 points · 8 giờ (**tối đa 3 points và khoảng 15 file mỗi PR**)  
**Phụ thuộc:** P6-02g4 (API tenant invoice), P7-15 (notification inbox/deep-link source)  
**Repo / branch:** `fe/` · `feature/p8-05-tenant-invoice-view`  
**Issue:** `docs#TBD`

> **Đọc trước khi code:** `fe/AGENTS.md`, `fe/.agents/skills/fe-feature-workflow/SKILL.md`, `fe-structure/SKILL.md`, `fe-code-style/SKILL.md`, `fe-ui-ux/SKILL.md`. P6-02g4 là API source; không tạo lại endpoint tenant invoice trong issue FE này.

## Mục tiêu

Tenant đăng nhập xem danh sách và chi tiết invoice đã phát hành của mình. Chọn notification liên quan invoice thì mở đúng trang chi tiết; FE luôn tải nội dung từ API P6-02g4 để backend xác thực quyền.

## Quyết định áp dụng

- `P6-D64`: tenant chỉ xem `issued`; `pending`/`void` không hiển thị.
- `P6-D63/D71`: tập hợp đồng của tenant theo đại diện hoặc member chưa rời; đây là logic backend, FE không tự xác định ownership.
- `P6-D74`: không tự liên kết tenant bằng số điện thoại; tenant chưa linked không được giả lập.
- `P6-D61/D72`: không có trạng thái thu tiền, QR, settlement hoặc payment action.
- P7-15 đã cung cấp notification inbox; dùng payload chỉ làm navigation hint, không làm nguồn invoice data.

## Contract

- List/detail dùng `GET /me/invoices` và `GET /invoices/{invoiceId}` theo P6-02g4. Xác nhận field/pagination/error trong `api-docs` và implementation.
- Notification deep link dùng payload/route convention P7-15 hiện có. Nếu payload chưa có invoice ID/reference, nêu blocker thay vì tự sửa schema Community.
- Auth/session/route guard dùng pattern hiện hữu của FE tenant.

### Mapping field

| Response/payload | UI | Quy tắc |
|---|---|---|
| invoice ID trong notification | điều hướng tới detail | chỉ dùng làm tham chiếu; detail vẫn gọi API |
| `period`, code, room/building summary | list/detail | hiển thị theo response, không tự nối dữ liệu từ payload |
| `breakdown[]`, `otherFees`, `note`, `totalAmount` | bảng chi tiết | giữ precision server trả; không tính lại total |
| `status`, `issuedAt` | trạng thái và ngày phát hành | chỉ render invoice API trả về; không tạo nhãn overdue/paid |
| API 404/403 | not found/không khả dụng | không để lộ tên/tổng invoice từ notification payload |

## Tham chiếu code

- Dùng route guard, notification inbox navigation, API hooks/query keys, `formatVnd`/`formatMonth` và responsive table/card patterns hiện có.
- Trước khi thêm route mới, tìm route tenant và invoice feature hiện có để không tạo page trùng.

## Các bước triển khai

### Bước 1 — List invoice

- **Cách làm:** tạo trang tenant list gọi `/me/invoices`; hiển thị skeleton, empty, error và paging theo response thật.
- **Kiểm tra bước:** account có invoice issued thấy đúng số item; account chưa có invoice thấy empty state; refresh giữ route.

### Bước 2 — Detail invoice

- **Cách làm:** gọi detail bằng ID từ list; render lines/total/note và trạng thái issued; không render action payment.
- **Kiểm tra bước:** mở detail của mình trả đúng dữ liệu API; ID không tồn tại/không thuộc tenant nhận not found theo contract.

### Bước 3 — Notification deep link

- **Cách làm:** khi chọn notification, điều hướng tới invoice detail; nếu chưa đăng nhập, lưu safe return path trong router rồi xác thực và tải lại API.
- **Kiểm tra bước:** link đúng mở đúng invoice; link invalid/void/out-of-scope không hiển thị payload như nội dung thật.

### Bước 4 — Case lỗi và responsive

- **Cách làm:** xử lý session hết hạn, đổi account, API timeout, invoice void sau khi notification gửi và viewport nhỏ.
- **Kiểm tra bước:** tenant khác đăng nhập cùng link không thấy title/amount; màn 360px đọc được danh sách và detail.

## Ngoài phạm vi

- Backend API tenant invoice (giữ P6-02g4), notification consumer/publisher (flow P8-08 sẽ được PM chốt sau).
- Thanh toán, QR, overdue, reminder, settlement, chỉnh sửa/hủy invoice.

## Blocker

- Nếu P6-02g4 chưa có endpoint trên môi trường FE hoặc P7-15 thiếu tham chiếu invoice trong payload, ghi blocker với operation/payload cụ thể; không tạo API mới.

## Acceptance

- [ ] Tenant chỉ thấy invoice `issued` do API P6-02g4 trả về.
- [ ] Deep link mở detail sau login; mọi trường hợp 404/403/void không làm lộ dữ liệu từ payload.
- [ ] Không có payment/QR/overdue/settlement action; loading/empty/error states hoạt động.
- [ ] List/detail responsive và refresh/back hoạt động theo router convention.

## Definition of Done

- [ ] Có ảnh desktop/360px và request evidence đã che PII.
- [ ] FE lint/build/i18n check pass theo repo; không mock API.
- [ ] PR ≤ 2 points/~15 file, FE reviewer approve.
