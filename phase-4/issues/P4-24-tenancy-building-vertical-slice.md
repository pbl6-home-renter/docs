# P4-24 — Building vertical slice

**Trạng thái:** 🟡 Open  
**Người phụ trách:** BE member  
**Người review:** BE Lead, API owner, PM  
**Ước lượng:** 8 points · 18–24 giờ  
**Độ ưu tiên:** High

## Bối cảnh

Thay vì triển khai rời rạc từng layer, Building cần được làm thành một vertical slice chạy từ request đến database và outbox. Đây là slice mẫu để team triển khai Room và các domain tiếp theo.

## Phạm vi công việc

- Xác định Building aggregate và invariant nghiệp vụ cần thiết.
- Tạo command/query phù hợp với requirement hiện tại.
- Tạo application handler và transaction boundary.
- Tạo repository port và persistence adapter.
- Tạo controller, DTO, validation và response contract.
- Map domain event sang integration event.
- Append outbox message trong cùng transaction với Building aggregate.
- Đồng bộ route, schema và error contract với `api-docs`/Apidog.

## Tiêu chí nghiệm thu

- Building API chạy được với tenancy database.
- Aggregate và outbox row được ghi trong cùng transaction.
- Khi rollback, không còn aggregate hoặc outbox row dở dang.
- API owner đã cập nhật API contract.
- Manual verification được ghi lại trong PR/issue.
- Không publish trực tiếp từ command handler.

---

## 1. Checklist theo tầng

### Domain

- [ ] Định nghĩa Building aggregate root.
- [ ] Đặt invariant: tên, owner/reference và trạng thái phải hợp lệ theo requirement.
- [ ] Có factory/method nghiệp vụ thay vì expose setter tùy ý.
- [ ] Phát domain event sau khi aggregate thay đổi hợp lệ.

### Application

- [ ] Tạo command input và handler.
- [ ] Handler mở UoW/transaction context.
- [ ] Load hoặc tạo aggregate qua repository port.
- [ ] Gọi method nghiệp vụ của aggregate.
- [ ] Persist aggregate với transaction context.
- [ ] Append domain events vào outbox trong cùng transaction.
- [ ] Commit trước khi trả response.

### Infrastructure và presentation

- [ ] Implement repository bằng TypeORM adapter.
- [ ] Map DTO sang command, không truyền request object vào domain.
- [ ] Map lỗi domain/application sang error code API.
- [ ] Tạo Swagger/OpenAPI schema tương ứng.
- [ ] Không gọi RabbitMQ trực tiếp từ controller/handler.

## 2. Luồng xử lý chuẩn

```text
HTTP Request
  → Controller/DTO validation
  → Command Handler
  → UoW transaction
  → Building Aggregate
  → Repository save + Outbox append
  → Commit database
  → Relay publish integration event
```

## 3. Manual verification

- Tạo Building hợp lệ.
- Gửi dữ liệu thiếu hoặc sai để kiểm tra validation.
- Tạo dữ liệu trùng để kiểm tra business/database error.
- Buộc lỗi trước commit và xác nhận không có aggregate/outbox dở dang.
- Kiểm tra relay xử lý event sau khi command đã commit.
