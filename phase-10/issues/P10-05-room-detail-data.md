# P10-05 — Hiển thị hợp đồng và chỉ số thật ở trang phòng

**Trạng thái:** 🔵 In progress — thiếu bảo đảm kỳ mới nhất · **Owner đề xuất:** `ThaiBao11125` · **Reviewer:** FE Lead / API owner  
**Repo:** `fe` · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD` · **Phụ thuộc:** P6-01e1, P6-02e; xác minh API đã deploy.

## Cập nhật triển khai 14/11/2026

[FE #40](https://github.com/pbl6-home-renter/fe/pull/40) đã merge dữ liệu xác thực cho hợp đồng, thành viên và chỉ số. API meter readings không công bố sort; UI chỉ chọn kỳ lớn nhất trong trang trả về, chưa bảo đảm mới nhất toàn bộ lịch sử. Cần API/sắp xếp hoặc cách tải đầy đủ và kiểm thử Gateway.

## Bối cảnh và mục tiêu

`RoomDetailResponseDto` hiện để `currentContract=null`, `currentMembers=[]`, `latestMeterReadings=null` theo phần tạm hoãn của P5-09d; trang landlord dùng trực tiếp các giá trị này và hiển thị “phòng trống” hoặc “chưa có chỉ số” ngay cả khi dữ liệu đã tồn tại. `GET /rooms/{id}` là public: không đưa dữ liệu hợp đồng, phone hay chỉ số riêng tư vào response công khai. FE đã có client Contract, Member và MeterReading được xác thực.

## Triển khai

1. Đối chiếu API `GET /contracts`, `/contract-members`, `/meter-readings` trong `api-docs` và hooks hiện có: xác minh filter theo room, active status, pagination, sắp xếp và field ngày/giá trị. Nếu contract thiếu khả năng xác định dữ liệu đúng, ghi blocker kèm operation cụ thể cho API owner; không suy đoán hoặc chọn bản ghi trang đầu. **Kiểm tra:** request landlord trả đúng hợp đồng active và readings của room, owner khác bị từ chối/không nhận dữ liệu.
2. Thêm query có xác thực cho contract active theo room; khi có contract, tải thành viên theo contract, xử lý pagination và map field thực tế. Sau checkout hoặc sửa member invalidate query liên quan. **Kiểm tra:** phòng active hiện hợp đồng và thành viên; phòng thực sự không active mới hiện trạng thái trống.
3. Tải chỉ số mới nhất theo từng loại bằng filter/sort được API hỗ trợ; không giả định hai loại cùng ngày. Nếu UI chỉ có một `recordedAt` chung và không thể biểu diễn trung thực, hiển thị ngày riêng theo từng loại hoặc bỏ ngày chung. **Kiểm tra:** điện/nước có ngày khác nhau, có một loại, giá trị 0 và không có dữ liệu đều hiển thị đúng.
4. Tách loading/error/empty theo từng card; dùng toast/interceptor và bản dịch `vi`/`en`. Khi lỗi API không báo “phòng trống/chưa có chỉ số”. **Kiểm tra:** lỗi 403/500 hoặc mạng hiện trạng thái lỗi và retry; đổi room không hiện dữ liệu phòng trước.
5. Chạy FE build, lint, i18n; kiểm tra thủ công qua Gateway bằng hai landlord và dữ liệu thật. Không thêm test FE trái quy ước.

## Acceptance

- Trang chủ phòng hiển thị hợp đồng active, member và chỉ số mới nhất đúng dữ liệu nguồn; empty chỉ khi API xác nhận không có.
- Dữ liệu riêng chỉ lấy từ API đã xác thực và giữ kiểm tra ownership; public room endpoint không lộ contract/member/readings.
- Loading, lỗi, pagination và cập nhật sau mutation không tạo kết quả sai; nếu API hiện có không đủ, issue bị blocked ở phần tương ứng và ghi bằng chứng.

## User story và ranh giới quyền

Là chủ nhà, tôi muốn xem hợp đồng và số điện nước mới nhất của phòng để tiếp tục vận hành mà không cần kiểm tra thủ công nhiều màn hình. Room public có thể được khách xem; thông tin hợp đồng, thành viên và chỉ số là dữ liệu riêng, phải lấy qua endpoint có kiểm tra quyền. P5-09d đã chủ ý để các field trên public detail rỗng, vì vậy không xem placeholder là bằng chứng phòng trống.

## Ma trận nghiệm thu

| Điều kiện | Hiển thị mong đợi |
|---|---|
| Có hợp đồng active và 2 thành viên | Mã, kỳ và hai thành viên khớp API; không hiển thị tenant đã rời nếu contract quy định loại trừ |
| API trả danh sách hợp đồng active rỗng | Chỉ lúc đó mới hiện trạng thái không có hợp đồng |
| Điện = 0, nước chưa có | Hiển thị `0` cho điện, trạng thái chưa có cho nước |
| Một API bị 403/500 | Card tương ứng có lỗi/retry; card khác vẫn hoạt động; không báo trống |
| Đổi room trong lúc request cũ đang chạy | Không hiển thị kết quả của room cũ ở room mới |

## Bàn giao và blocker

Ghi operationId, filter, sort, DTO và ảnh màn hình đã che dữ liệu cá nhân trong PR. Nếu API không cho xác định bản ghi mới nhất theo từng loại hoặc không phân trang thành viên được, nêu trường thiếu, ví dụ request và liên kết issue backend; không đoán thứ tự dữ liệu. Chỉ đóng sau khi xác minh hai landlord, một phòng thực sự trống và một phòng có dữ liệu.
