# P5-09a — Room domain model và persistence

**Epic:** [P5-09](P5-09-tenancy-room-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** BE member  
**Người review:** BE Lead  
**Ước lượng:** 3 points · 6–8 giờ  
**Phụ thuộc:** P5-08a

## Mục tiêu

Dựng Room aggregate, invariant và tầng persistence theo pattern của P5-08a.

## Việc cần làm

### Domain

- [ ] Định nghĩa Room aggregate root theo bảng `rooms` trong `database-design.md` §2.5.
- [ ] Invariant: `name` 1–254, `description` 1–500 (nullable), `floor_number > 0`, `area > 0`, `max_occupancy > 0`, `rent_price >= 0`, `amenities` là object (default `{}`), `gender_policy` ∈ `any|male|female` (default `any`).
- [ ] `landlord_id` và `building_id` bắt buộc (D25 — 1 chủ/phòng).
- [ ] `status` ∈ `available|occupied|maintenance`; Room mới mặc định `available`. `occupied` là trạng thái derived từ Contract — chưa có Contract nên chưa có luồng chuyển sang `occupied`.
- [ ] Factory `create(...)` và method nghiệp vụ (`update`, `delete`, chuyển trạng thái); không expose setter tùy ý.
- [ ] Aggregate ghi nhận domain event (`RoomCreated`, `RoomUpdated`, `RoomDeleted`, `RoomStatusChanged`).

### Persistence

- [ ] TypeORM entity kế thừa base entity của boilerplate (soft-delete `is_deleted`).
- [ ] Migration tạo bảng `rooms`; FK `building_id → buildings` (cùng `tenancy_db`).
- [ ] `landlord_id` là uuid thường — **không** tạo cross-database FK sang Identity.
- [ ] Unique `(building_id, name)` cho Room chưa bị xóa (phục vụ `DUPLICATE_ROOM`).
- [ ] Repository port + TypeORM adapter nhận transaction context từ UoW; mapper entity ↔ aggregate.

## Tiêu chí nghiệm thu

- Migration chạy được trên tenancy database và rollback được.
- Aggregate từ chối dữ liệu sai invariant.
- Repository adapter save/load được aggregate trong transaction context của UoW.
