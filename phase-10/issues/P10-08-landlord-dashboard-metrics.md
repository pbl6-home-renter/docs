# P10-08 — Sửa tổng quan chủ nhà khi có nhiều tòa hoặc lỗi API

> **Quyết định PM D3:** Các tổng dùng pagination.totalItems theo từng filter.

**Loại:** Bug · **Ưu tiên đề xuất:** High · **Trạng thái:** 🟢 Done — code đã merge  
**Owner đề xuất:** `ThaiBao11125` · **Reviewer:** FE Lead · **Repo:** `fe`  
**Phụ thuộc:** `GET /me/buildings` theo P5-08c · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## Cập nhật triển khai 14/11/2026

PM đã chốt D3 dùng pagination.totalItems. [FE #38](https://github.com/pbl6-home-renter/fe/pull/38) đã merge; còn kiểm tra dữ liệu trên 20 tòa, trạng thái lỗi/retry và giao diện qua Gateway.

## Vấn đề và mục tiêu

`landlord-dashboard-page.tsx` chỉ tải trang đầu `pageSize: 20`; `landlord-dashboard-full-state.tsx` lấy `buildings.length` và đếm trạng thái trên trang đó nhưng gắn nhãn tổng số tòa. Khi request lỗi, `data?.items || []` khiến dashboard hiện chưa có tòa. Chủ nhà cần số tổng và trạng thái đúng, đồng thời biết khi dữ liệu không tải được.

## Quy tắc dữ liệu

Tổng, approved, pending lấy từ `pagination.totalItems` của các query `/me/buildings` với filter status tương ứng; chỉ tính `others = total - approved - pending` nếu các trạng thái và bộ lọc bao phủ dữ liệu theo enum contract, nếu không thì không hiển thị phép suy diễn. Danh sách preview dùng trang hiện có và ghi nhãn là danh sách xem trước, không dùng chiều dài preview làm tổng. Không tự tạo API dashboard doanh thu hoặc số liệu Payment.

## Triển khai

1. Kiểm tra filter/status trong OpenAPI và danh sách trạng thái; xác minh query với hai landlord qua Gateway. **Kiểm tra:** pagination count theo từng filter đúng ở dữ liệu >20 tòa.
2. Dùng các query count có filter, query key đầy đủ và lấy `pagination.totalItems`; giữ preview giới hạn bằng pagination UI convention. Tách loading/partial error và ErrorState/retry khỏi empty. **Kiểm tra:** tắt mạng không thấy empty state “chưa có tòa”.
3. Cập nhật nhãn `vi`/`en` cho preview và số liệu, tránh text hardcode; invalidation sau create/update/approval. **Kiểm tra:** 25 tòa, 21 approved, 3 pending, 1 rejected → thẻ hiển thị 25/21/3/1; preview không nhận là tổng.
4. Chạy FE build/lint/i18n; thử filter, user không có tòa, lỗi mạng, tạo tòa mới, 360px/desktop.

## Acceptance

- Count được tính trên toàn bộ tập server trả về, không thay đổi sai khi danh sách vượt một trang.
- Lỗi API, empty thực sự và trạng thái tải được phân biệt; mọi text có i18n và không lộ dữ liệu owner khác.
- Bằng chứng kiểm thử dùng dataset >20, ảnh màn hình và kết quả kiểm tra được đính kèm PR.
