# P10-02 — Trả số phòng và tỷ lệ lấp đầy thực tế

> **Quyết định PM D1:** Áp dụng công thức và quy tắc làm tròn bên dưới.

**Trạng thái:** 🔵 In progress — đã merge, chờ nghiệm thu · **Owner đề xuất:** `leminhkhai345` · **Reviewer:** BE Lead / PM  
**Repo:** `Tenancy-Service`, `api-docs` · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`  
**Phụ thuộc:** P5-08c/d, P5-09b. Thống kê là phần tạm hoãn trong P5-08c/d.

## Cập nhật triển khai 14/11/2026

PM đã chốt công thức D1 theo issue. [Tenancy #49](https://github.com/pbl6-home-renter/Tenancy-Service/pull/49) và [API docs #63](https://github.com/pbl6-home-renter/api-doc/pull/63) đã merge; build/lint và unit test pass. Còn kiểm tra PostgreSQL, phòng xóa mềm, phân quyền và Gateway.

## Bối cảnh và contract

`MyBuildingListResponseDto` và `MyBuildingDetailResponseDto` luôn gán `occupiedRooms=0`, `occupancyRate='0%'`; admin detail cũng gán `'0%'`. FE đang dùng các giá trị này. P5-08c yêu cầu hoàn thiện thống kê khi Room có dữ liệu. `RoomStatus.OCCUPIED` được domain suy ra từ hợp đồng hiệu lực; không đếm phòng xóa mềm. Trả thêm `totalRooms` cho landlord list/detail để FE có mẫu số thật; giữ `occupancyRate` dạng chuỗi phần trăm như contract hiện hành.

## Triển khai

1. Đối chiếu P5-08c/d, schema `my-building-*-response-dto.yaml`, `admin-building-detail-response-dto.yaml` và query hiện tại. Cập nhật OpenAPI landlord list/detail: `totalRooms` integer ≥ 0; bỏ mô tả giá trị tạm; admin detail trả tỷ lệ thực. Bundle contract. **Kiểm tra:** lint và example biểu diễn 2/4 = `50%`.
2. Bổ sung read model/query tổng hợp theo building, đếm Room chưa xóa và Room `occupied`; dữ liệu chỉ thuộc các building được query hiện tại cho phép. Ghép tổng hợp theo lô cho trang list, không query theo từng dòng. Với zero rooms trả `0` và `0%`; phần trăm làm tròn tối đa một chữ số thập phân, bỏ số 0 thừa. **Kiểm tra:** 0/0 → `0%`, 1/3 → `33.3%`, 2/4 → `50%`; phòng đã xóa không được đếm.
3. Map kết quả vào landlord list/detail và admin detail, không tính ở DTO từ giá trị mặc định. **Kiểm tra:** cùng một tòa trả nhất quán giữa ba endpoint; landlord khác không xem được dữ liệu riêng.
4. Viết test query/mapping cho các ví dụ, pagination và soft-delete; chạy build, lint, test liên quan và thử API qua Gateway. Phối hợp P10-03 để kiểm tra định dạng `%`.

## Acceptance

- Số phòng, số đang thuê và tỷ lệ của từng tòa phản ánh Room hiện tại; endpoint không trả số 0 giả khi có dữ liệu.
- Pagination, quyền hiện có, zero rooms và định dạng phần trăm hoạt động đúng; API docs và implementation được cập nhật cùng đợt.
- Không mở rộng sang doanh thu, Payment hay dashboard toàn hệ thống.

## User story và dữ liệu

Là chủ nhà hoặc admin, tôi muốn biết tòa có bao nhiêu phòng và bao nhiêu phòng đã thuê để đánh giá mức lấp đầy. Nguồn dữ liệu là Room thuộc building, chưa soft-delete; Room `occupied` dùng làm tử số, tất cả Room chưa xóa làm mẫu số. Số liệu được tính theo từng building và không dựa trên trang Room mà FE đang xem.

| Dữ liệu hợp lệ | `totalRooms` | `occupiedRooms` | `occupancyRate` |
|---|---:|---:|---|
| Không có phòng | 0 | 0 | `0%` |
| 1 occupied, 2 available | 3 | 1 | `33.3%` |
| 2 occupied, 2 maintenance | 4 | 2 | `50%` |
| 1 occupied đã xóa, 1 available | 1 | 0 | `0%` |

## Kịch bản kiểm thử và bàn giao

- Tạo hai landlord với building riêng; list của A chỉ tổng hợp room của A. Admin detail cho cùng building có tỷ lệ giống landlord detail.
- Tạo nhiều building vượt một trang: phép tổng hợp phải đúng từng dòng và không làm sai `totalItems`, filter hay sort. Kiểm tra query log để tránh N+1.
- Đổi trạng thái Room, refresh endpoint và đối chiếu SQL; thử building không có Room và Room đã soft-delete. Không dựa vào giá trị hardcode trong example.
- PR nêu query/DTO thay đổi, mô tả tương thích với client cũ, bằng chứng build, lint, test và kết quả `npm run lint`/`npm run bundle` ở `api-docs`.
