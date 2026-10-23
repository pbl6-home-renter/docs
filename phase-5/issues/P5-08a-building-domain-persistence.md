# P5-08a — Building domain model và persistence

**Epic:** [P5-08](P5-08-tenancy-building-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** BE member  
**Người review:** BE Lead  
**Ước lượng:** 3 points · 6–8 giờ  
**Phụ thuộc:** P4-21

## Mục tiêu

Dựng Building aggregate, invariant và tầng persistence để các sub-issue sau chỉ cần thêm use case, không sửa lại model.

## Việc cần làm

### Domain

- [ ] Định nghĩa Building aggregate root theo bảng `buildings` trong `database-design.md`.
- [ ] Invariant: `name` 1–254, `province`/`ward` 1–100, `address` 1–254, `latitude` −90..90, `longitude` −180..180, `landlord_id` bắt buộc.
- [ ] State machine `status`: `pending → approved` hoặc `pending → rejected`; mọi chuyển trạng thái khác là lỗi nghiệp vụ.
- [ ] `note` bắt buộc khi `rejected` (1–500 ký tự).
- [ ] Có factory `create(...)` và method nghiệp vụ (`update`, `approve`, `reject`, `delete`); không expose setter tùy ý.
- [ ] Aggregate ghi nhận domain event (`BuildingCreated`, `BuildingUpdated`, `BuildingApproved`, `BuildingRejected`, `BuildingDeleted`) để handler append vào outbox.

### Persistence

- [ ] TypeORM entity kế thừa base entity của boilerplate (soft-delete `is_deleted`).
- [ ] Migration tạo bảng `buildings` với enum `status` default `pending`.
- [ ] `landlord_id`, `reviewed_by` là uuid thường — **không** tạo cross-database FK sang Identity.
- [ ] Repository port trong domain/application; TypeORM adapter trong infrastructure, nhận transaction context từ UoW.
- [ ] Mapper entity ↔ aggregate.

## Tiêu chí nghiệm thu

- Migration chạy được trên tenancy database và rollback được.
- Aggregate từ chối dữ liệu sai invariant và chuyển trạng thái không hợp lệ.
- Repository adapter save/load được aggregate trong transaction context của UoW.
