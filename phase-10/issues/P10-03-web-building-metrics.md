# P10-03 — Hiển thị số liệu tòa đúng phạm vi trên Web

> **Quyết định PM D2:** Các thẻ phòng, tỷ lệ và tòa đã duyệt tính theo trang; tổng tòa dùng pagination.totalItems.

**Trạng thái:** 🔵 In progress — còn thẻ số liệu theo trang · **Owner đề xuất:** `ThaiBao11125` · **Reviewer:** FE Lead / PM  
**Repo:** `fe` · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD` · **Phụ thuộc:** P10-02.

## Cập nhật triển khai 14/11/2026

PM đã chốt D2: thẻ phòng, đang thuê, tỷ lệ và đã duyệt tính theo các dòng trang hiện tại; tổng tòa lấy từ pagination. [FE #36](https://github.com/pbl6-home-renter/fe/pull/36) đã merge phần định dạng %. F9 cho thẻ số liệu, nhãn và xử lý lỗi chưa được triển khai.

## Bối cảnh và mục tiêu

`use-building-list.ts` cộng số phòng và tòa đã duyệt từ `rawBuildings` của trang đang tải, nhưng dùng `pagination.totalItems` làm tổng số tòa; thẻ tổng hợp vì vậy trộn hai phạm vi. Cột tỷ lệ dùng `Number('0%')` và thêm `%` lần nữa, trong khi API trả chuỗi có `%`. Landlord cần xem số liệu không gây hiểu nhầm khi phân trang.

## Triển khai

1. Dùng DTO P10-02; thống nhất thẻ số phòng, số đã thuê, tỷ lệ, số tòa duyệt là **thống kê của các dòng đang hiển thị**; thêm nhãn i18n rõ phạm vi trang ở cả `vi`/`en`. Tổng số tòa từ pagination có nhãn riêng theo kết quả filter của server. Không suy tổng toàn bộ danh sách từ một trang. **Kiểm tra:** hai trang có số khác nhau cho ra số trang tương ứng.
2. Chuẩn hóa hiển thị tỷ lệ một lần: chấp nhận chuỗi có `%` từ contract, thanh tiến độ dùng giá trị số hợp lệ, text chỉ một dấu `%`; không biến thiếu dữ liệu thành 0 giả. **Kiểm tra:** `33.3%` hiển thị `33.3%`, thanh 33.3%; zero rooms hiện `0%`.
3. Rà desktop/mobile, loading/error/empty và khi đổi trang/filter; cập nhật query invalidation nếu Room thay đổi khiến thống kê cũ. **Kiểm tra:** refresh/đổi trang không trộn dữ liệu cũ; API lỗi không báo 0 như dữ liệu thật.
4. Chạy `npm run build`, `npm run lint`, `npm run i18n:check`; lưu ảnh hoặc mô tả kết quả kiểm thử thủ công. Không thêm test file FE trái quy ước repo.

## Acceptance

- Mọi thẻ nêu rõ phạm vi và không cộng trang hiện tại thành tổng toàn bộ; list/detail hiển thị tỷ lệ đúng một dấu `%`.
- Pagination, filter, empty/error và thay đổi Room không gây số liệu sai hoặc giả.

## User story và tình huống hiện tại

Là chủ nhà, tôi cần phân biệt số liệu của các tòa đang hiển thị với tổng kết quả để không tưởng số phòng của một trang là toàn bộ tài sản. Hiện `totalBuildings` đến từ pagination trong khi `totalRooms`, `occupiedRooms`, `approvedCount` tính từ `rawBuildings`; khi bật tìm kiếm tập dữ liệu còn thay đổi theo giới hạn 100 bản ghi. P10-04 xử lý search server, issue này xử lý phép tính và nhãn.

## Ma trận nghiệm thu

| Trường hợp | Kỳ vọng |
|---|---|
| Trang 1 có 2 tòa/3 phòng, trang 2 có 1 tòa/5 phòng | Thẻ theo trang lần lượt 3 và 5; tổng kết quả giữ theo pagination có nhãn riêng |
| Server trả `33.3%` | Desktop/mobile đều chỉ có một dấu `%`; thanh tiến độ 33.3% |
| API lỗi hoặc thiếu field | Không chuyển lỗi thành số 0 hoặc thông báo thành công |
| Filter khiến trang hiện tại rỗng | Reset/pagination theo convention và hiển thị empty phù hợp |

Giữ issue Open sau khi sửa format phần trăm đơn lẻ; chỉ đóng khi scope số liệu theo trang, loading/error, invalidation và dữ liệu P10-02 được kiểm tra. Đính kèm ảnh desktop/mobile, input API và lệnh kiểm tra vào PR.
