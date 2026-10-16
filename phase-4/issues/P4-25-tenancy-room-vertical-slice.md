# P4-25 — Room vertical slice

**Trạng thái:** 🟡 Open  
**Người phụ trách:** BE member  
**Người review:** BE Lead, API owner, PM  
**Ước lượng:** 13 points · 30–45 giờ  
**Độ ưu tiên:** High

## Bối cảnh

Room phụ thuộc vào Building và cần thể hiện rõ validation quan hệ giữa aggregate và persistence record. Task này kế thừa pattern từ Building vertical slice nhưng không được rút gọn thành CRUD thiếu domain rule.

## Phạm vi công việc

- Xác định Room aggregate và business rule liên quan.
- Xử lý quan hệ Room–Building theo domain và database constraint.
- Tạo command/query handler, repository port và persistence adapter.
- Tạo controller, DTO, validation và response contract.
- Xử lý Building không tồn tại, không khả dụng hoặc Room không hợp lệ.
- Tạo outbox event khi nghiệp vụ yêu cầu thông báo sang service khác.
- Tạo consumer/inbox integration nếu Room cần nhận event từ service khác.
- Đồng bộ implementation với `api-docs` và Apidog.

## Tiêu chí nghiệm thu

- Room API chạy được trên tenancy database.
- Quan hệ Building–Room được kiểm tra ở đúng application/domain boundary.
- Không có cross-database foreign key tới Identity Service.
- Outbox được ghi cùng transaction nếu Room phát integration event.
- Duplicate event được inbox/dedup xử lý an toàn nếu có consumer.
- Manual verification và API contract được bàn giao đầy đủ.

---

## 1. Checklist theo nghiệp vụ

### Room aggregate

- [ ] Xác định field bắt buộc và trạng thái hợp lệ của Room.
- [ ] Xác định rule Room phải thuộc một Building hợp lệ.
- [ ] Xác định rule không cho tạo/cập nhật Room khi Building không còn khả dụng.
- [ ] Phân biệt lỗi không tìm thấy dữ liệu và lỗi vi phạm business rule.

### Command/query

- [ ] Tạo command cho các thao tác được requirement cho phép.
- [ ] Tạo query list/detail với pagination nếu cần.
- [ ] Không đưa query logic vào entity persistence.
- [ ] Handler dùng explicit transaction context cho write operation.

### Integration

- [ ] Xác định event nào cần phát khi Room được tạo/cập nhật.
- [ ] Event có `message_id`, `event_type`, `aggregate_id`, timestamp và metadata cần thiết.
- [ ] Nếu có consumer, ghi inbox và business side effect trong cùng transaction.
- [ ] Duplicate event không làm thay đổi dữ liệu lần hai.

## 2. Manual verification

1. Tạo Room với Building hợp lệ.
2. Tạo Room với Building không tồn tại.
3. Cập nhật/xóa dữ liệu theo từng trạng thái hợp lệ.
4. Gửi request duplicate và kiểm tra idempotency nếu endpoint yêu cầu.
5. Kiểm tra outbox row và event payload.
6. Kiểm tra API docs khớp request/response thực tế.
