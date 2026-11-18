# P10-34 — Adapter tra contact chủ trọ từ Identity

**Trạng thái:** 🔵 Code local đã kiểm tra — chờ review/deploy
**Ưu tiên:** P0 · **Repo:** Tenancy-Service · **Owner đề xuất:** BE Room  
**Phụ thuộc:** GET nội bộ Identity users đã có · **Scope:** M, khoảng 4–5 file

## Mục tiêu và cách sửa

Đã có port/adapter/binding tra Identity; kiểm tra mapping tối thiểu và sai role/ID, lỗi phụ thuộc giữ nguyên. Policy owner không còn hợp lệ trả 404 theo P10-D90; outage/malformed contact trả 503. [Evidence](../discovery/mobile-backend-implementation.md).

Room detail có TODO chờ Identity, nhưng Identity hiện có `/internal/users?ids=...` trả id/name/phone/role/status/isDeleted. Tạo application port và adapter nội bộ trả contact tối thiểu cho landlordId; khai báo peer DTO tại Tenancy. Bind DI ở room module. Chỉ đọc Identity, không cross-service DB join hoặc copy implementation từ service khác.

## Acceptance

- [ ] Port trả đúng id/name/phone cho landlord hợp lệ, gọi Identity bằng internal client/service authentication hiện có.
- [ ] Không trả email hoặc full Identity DTO; phân biệt không tìm thấy/sai role/deleted với lỗi mạng, không tạo dữ liệu contact giả.
- [ ] Adapter có test success/not-found/outage và DI resolve được khi build/start.

## Verification

Focused adapter test, Tenancy build/lint, smoke internal lookup bằng môi trường test. Chốt cách xử lý chủ trọ đã xóa trước release P10-35; không suy luận từ null hiện có.

**File dự kiến:** port, adapter, room DI/module binding và adapter spec. Không sửa Identity API nếu API hiện có đáp ứng đủ.

**Tham chiếu:** A3, [plan](../../tasks/plan.md).
