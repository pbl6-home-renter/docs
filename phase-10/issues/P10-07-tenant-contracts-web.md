# P10-07 — Người thuê xem danh sách và chi tiết hợp đồng trên Web

**Loại:** Feature gap · **Ưu tiên đề xuất:** High · **Trạng thái:** 🟢 Done — code đã merge  
**Owner đề xuất:** `ThaiBao11125` · **Reviewer:** FE Lead / PM · **Repo:** `fe`  
**Phụ thuộc:** P6-01e2, API Gateway route `/me/contracts` · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## Cập nhật triển khai 14/11/2026

[FE #39](https://github.com/pbl6-home-renter/fe/pull/39) đã merge danh sách và chi tiết chỉ đọc. Còn kiểm tra Gateway, phân trang, quyền tenant đại diện/thành viên/đã rời và giao diện mobile.

## Bối cảnh

Tenant navigation trỏ `/contracts`, nhưng `landlord.routes.tsx` chỉ cho role landlord và FE chưa gọi `GET /me/contracts`. API Tenancy và `api-docs/src/paths/contracts/me-contracts.yaml` đã mô tả danh sách cho tenant; điều kiện server bao gồm tenant đại diện hoặc member chưa rời. Người thuê hiện không thể xem hợp đồng từ menu tương ứng.

## User story và contract

Là tenant có tài khoản liên kết, tôi muốn xem hợp đồng của mình và mở chi tiết để tra thông tin thuê, trong khi không thấy hợp đồng của người khác. `GET /me/contracts` trả `CONTRACTS_MY_FETCHED` cùng offset pagination; filter `status`, `roomId`; chỉ tenant. Chi tiết dùng `GET /contracts/{id}` theo quyền được API cho phép. Không dùng API list landlord `/contracts` cho tenant, không tự cấp quyền từ giao diện.

| Tình huống | Kết quả mong đợi |
|---|---|
| Tenant là đại diện hoặc member chưa rời | Hợp đồng xuất hiện một lần và có thể mở chi tiết |
| Member đã rời hoặc tenant khác | Không nằm trong list; detail áp dụng lỗi quyền của API |
| Tenant không có hợp đồng | Empty state với hướng dẫn phù hợp, không có dữ liệu giả |
| API lỗi | Error state/retry, không biến lỗi thành empty |

## Các bước triển khai

1. Xác minh request/response, status và Gateway của `/me/contracts`; đối chiếu DTO thực tế, detail và route collisions. **Kiểm tra:** tenant A có contract; tenant B không có contract A; gọi URL qua Gateway đúng quyền.
2. Thêm DTO/client/query key và hook phân trang theo `ListParams` ở feature contracts; params vào query key, không hardcode page size. **Kiểm tra:** page 1/2, status và reload URL giữ filter hợp lệ.
3. Tạo list cho tenant dùng UI primitives, các field `contractCode`, `roomName`, `buildingName`, ngày, `status` theo DTO; hỗ trợ loading/empty/error và i18n. **Kiểm tra:** dữ liệu nhiều trang hiển thị đúng, ngày và trạng thái theo locale.
4. Dùng route dispatcher theo role cho `/contracts` và `/:id`, tạo detail read-only phù hợp; không render nút edit/activate/checkout của landlord. **Kiểm tra:** tenant truy cập URL trực tiếp, người không có quyền nhận 403/404 như API.
5. Chạy build/lint/i18n; test thủ công tenant đại diện, member, đã rời, contract không tồn tại, lỗi mạng và màn hình 360px. Đính kèm ảnh che dữ liệu thật.

## Acceptance

- Tenant mở được list/detail từ menu, dữ liệu chỉ đến từ API xác thực; landlord flow không bị ảnh hưởng.
- Pagination, trạng thái rỗng/lỗi và quyền user khác hoạt động đúng; UI không cung cấp thao tác landlord.
- Build/lint/i18n pass và có bằng chứng Gateway. Nếu Gateway chưa route, ghi blocker ở dependency, không mock.
