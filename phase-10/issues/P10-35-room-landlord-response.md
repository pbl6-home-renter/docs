# P10-35 — Điền chủ trọ vào response chi tiết phòng

**Trạng thái:** 🟡 Open — plan ngày 18/11/2026  
**Ưu tiên:** P0 · **Repo:** Tenancy-Service, api-docs nếu đổi semantics  
**Owner đề xuất:** BE Room · **Phụ thuộc:** P10-34 · **Scope:** M, khoảng 4–5 file chức năng/test

## Mục tiêu và cách sửa

Detail DTO hiện luôn mặc định landlord null, controller chỉ gọi fromReadModel. Sau kiểm tra quyền phòng, dùng contact port P10-34 và map contact vào result/DTO. Cập nhật Swagger để khớp contract `id/name/phone`. Dùng lỗi phụ thuộc chuẩn khi Identity tạm unavailable; không coi outage là chủ trọ không tồn tại. Không điền thêm currentContract/currentMembers cho public chỉ để xử lý contact.

## Acceptance

- [ ] Phòng hợp lệ có `landlord: {id,name,phone}` đúng chủ trọ trên cả GET anonymous và authenticated theo contract public hiện hành.
- [ ] Không lộ email/full Identity response; quyền với phòng chưa duyệt/đã xóa hoặc landlord khác không bị nới lỏng.
- [ ] Not-found/outage có hành vi được ghi rõ, DTO/spec thống nhất; không trả null giả thành công cho trường contract yêu cầu bắt buộc.

## Verification

Regression query + serialized DTO, hai landlord, anonymous/login, phòng không được xem, Identity not-found/outage. Chạy focused Jest, build/lint; nếu contract đổi thì lint/bundle api-docs. GET gateway và dùng mobile kiểm tra thẻ chủ trọ, gọi điện, nhắn tin bằng ID đúng.

**File dự kiến:** room detail handler/result/response DTO và regression; spec/bundle nếu thay đổi hành vi so với contract hiện có.

**Tham chiếu:** A3, [plan](../../tasks/plan.md).
