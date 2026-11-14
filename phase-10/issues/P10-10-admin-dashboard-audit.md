# P10-10 — Chốt nguồn dữ liệu dashboard và nhật ký quản trị

**Loại:** Discovery / blocker · **Ưu tiên đề xuất:** Medium · **Trạng thái:** ⚪ Blocked chờ quyết định PM/API owner  
**Owner đề xuất:** PM + BE Lead · **Repo:** `api-docs`, `Identity-Service`, `Tenancy-Service`, `fe`  
**Phụ thuộc:** Quyết định phạm vi và nguồn dữ liệu · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## Bối cảnh

`GET /dashboard`, `GET /audit-logs`, `GET /audit-logs/{id}` trong OpenAPI đang `designing`; chưa tìm thấy controller tương ứng trong ba service. `/admin` và `/admin/audit-logs` trên Web đang là placeholder. Dashboard contract còn có `systemTransactionVolume` trong khi Payment deferred; audit log chưa có nguồn dữ liệu và retention được chốt. Không thể coi các field trong example là số liệu sẵn có.

## Kết quả cần bàn giao

1. Lập bảng từng metric/field, service sở hữu, nguồn đọc và quyền admin; phân loại khả thi, deferred hoặc cần thay đổi contract. Làm rõ `from/to` áp dụng cho metric nào và thời điểm số liệu.
2. Đối chiếu business rule với phạm vi Phase 6/9; PM quyết định có triển khai dashboard/audit ở Phase 10 và định nghĩa audit event tối thiểu, visibility, retention, redaction. Không lưu password/token/PII không cần thiết.
3. Nếu được chốt, API owner cập nhật contract, chọn cách tổng hợp phù hợp database-per-service; tách issue backend và FE theo từng outcome, kèm test authorization, date range, unavailable peer, pagination và empty state. Không tự dựng distributed transaction hoặc số liệu giả.
4. Nếu chưa được duyệt, giữ blocker và đưa placeholder/menu vào danh sách kiểm tra UX; không gán API `released` chỉ vì đã có file YAML.

## Acceptance

- Có quyết định PM và bảng mapping field → nguồn dữ liệu → quyền → trạng thái; Payment volume không được mặc định tính khi Payment chưa triển khai.
- Các issue triển khai phát sinh có contract được phê duyệt và dependency rõ ràng, hoặc có quyết định defer với lý do. Không tính placeholder UI là đã hoàn thành.
