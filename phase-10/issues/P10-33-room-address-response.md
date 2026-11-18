# P10-33 — Trả địa chỉ và tên tòa trong API phòng

**Trạng thái:** 🟡 Open — plan ngày 18/11/2026  
**Ưu tiên:** P0 · **Repo:** Tenancy-Service, api-docs · **Owner đề xuất:** BE Room / API owner  
**Phụ thuộc:** Không · **Scope:** M mỗi slice; chia list/detail và cập nhật spec cùng slice

## Mục tiêu và cách sửa

A1 được xác nhận bằng API live và source. List đã query ward nhưng DTO không trả; buildingName chưa select. Detail thiếu cả query và mapping address/ward/province. Lấy các trường từ building ngay trong truy vấn phòng, không buộc mobile tải danh sách tòa để ghép. Sửa list read-model/DTO cho ward/buildingName; sửa detail read-model/query/DTO cho address/ward/province. Loại district khỏi schema địa chỉ phòng và ví dụ liên quan; không đổi district của domain khác.

## Acceptance

- [ ] GET `/rooms` trả ward/buildingName đúng tòa; GET `/rooms/{id}` trả address/ward/province đúng dữ liệu building.
- [ ] Không có district bắt buộc trong contract phòng; quy định required/nullability khớp dữ liệu thực tế, không dùng chuỗi giả để qua parse.
- [ ] Phân trang/filter hiện hành và quyền public/owner/admin không hồi quy; mỗi thay đổi response có YAML/bundle tương ứng.

## Verification

Kiểm tra full response serialization thay vì chỉ repository; fixture hai tòa khác ward/province và truy vấn nhiều trang. Chạy Jest focused room DTO/query, build/lint; api-docs lint/bundle. GET qua gateway và parse bằng DTO mobile đúng branch, đối chiếu room với building của nó.

**File dự kiến:** `room-read.repository.ts`, result/DTO list và detail, serialization regression; chia hai slice nhỏ. Spec `public-room-list-response-dto.yaml`, `room-detail-response-dto.yaml`, ví dụ room paths và generated bundle theo slice.

**Tham chiếu:** A1, [plan](../../tasks/plan.md).
