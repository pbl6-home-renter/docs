# P10-37 — Nghiệm thu Backend bằng đúng bản mobile tenant

**Trạng thái:** 🟡 Open — chuẩn bị matrix; kiểm tra app chờ source/build đang dùng  
**Ưu tiên:** P0 cho phòng đang thuê; P1 cho vòng smoke đầy đủ  
**Repo:** mobile, api-docs, pm · **Owner đề xuất:** Mobile / BE / API owner  
**Phụ thuộc:** P10-31/32/33/35/36; favorite theo trạng thái P10-24 · **Scope:** M cho test/evidence, sửa app là PR riêng nếu có lỗi

## Mục tiêu và cách sửa

Người dùng xác nhận lỗi trên mobile. Bản local chỉ có MainActivity mẫu nên chưa thấy endpoint/DTO/cache thật. Ghi branch/build được dùng, đối chiếu màn phòng đang thuê với `/me/room-hub` hoặc `/me/contracts` đã lọc active; không dùng `/rooms` (available công khai) hoặc `/me/rooms` (landlord). Kiểm tra envelope data/pagination, filter status, DTO và refresh sau kích hoạt/link. Khác biệt giữa API rỗng và parse/cache phải có bằng chứng riêng.

## Acceptance

- [ ] Tenant có account trước/sau hợp đồng đều thấy đúng phòng sau active/link; draft có trạng thái phù hợp, không bị coi là phòng đang thuê; response có dữ liệu phải hiển thị trên app sau refetch.
- [ ] Hai tenant khác phòng không đọc được phòng/hợp đồng riêng của nhau; empty và API/parse error phân biệt; chuyển account không dùng lại cache account trước.
- [ ] A1/A3 parse và contact hoạt động, A2 render ảnh thật; favorite chỉ nghiệm thu khi P10-24 đã triển khai. Có mapping endpoint → spec/bundle → server version → mobile build, không tuyên bố pass phần chưa test.

## Verification

Chạy matrix trong [plan](../../tasks/plan.md): trước/sau verify/activation, event retry, `0/+84`, pending/locked, account khác và dữ liệu nhiều phòng/trang. Chạy build Android trên source đúng: `gradlew.bat :app-tenant:assembleDebug`; api-docs lint/bundle và compare JSON với schema. Lưu request/response đã che token/PII trong evidence PM. Rà các parser tạm `BuildingWardResolver`, nullable landlord và coverUrl trên source thật trước khi bỏ workaround.

**File dự kiến:** smoke matrix/evidence, contract fixtures, DTO regression của mobile đúng branch nếu cần; không viết test giả cho scaffold hiện có. Các YAML/bundle thay đổi phải theo PR tính năng tương ứng, task này chỉ đối chiếu tổng thể.
