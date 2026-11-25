# P12-09 — Nghiên cứu phương án kiểm thử hiệu năng cho Rentify

**Trạng thái:** 🟡 Open  
**Người phụ trách:** Thu Phương  
**Ước lượng:** Chưa chốt; xác định sau khi làm rõ phạm vi nghiên cứu  
**Phụ thuộc:** Không  
**Đầu ra:** Tài liệu nghiên cứu được liên kết trong issue này  
**Quyết định phạm vi:** P12-D99

## Bối cảnh

Rentify gồm nhiều ứng dụng và dịch vụ. Trước khi triển khai kiểm thử hiệu năng, nhóm cần thống nhất các luồng cần đo, giả định về tải, chỉ số đánh giá và môi trường thử nghiệm. Hiện chưa có ngưỡng hiệu năng hoặc công cụ kiểm thử tải nào được phê duyệt.

## Mục tiêu

Đề xuất phương án kiểm thử hiệu năng khả thi cho Rentify, đủ cụ thể để nhóm chọn phạm vi thử nghiệm đầu tiên và tách các task triển khai tiếp theo.

## Nội dung nghiên cứu

1. **Xác định luồng ưu tiên:** Khảo sát các hành trình người dùng và API có ảnh hưởng lớn đến trải nghiệm hoặc có khả năng chịu tải cao. Nêu dịch vụ liên quan, lý do ưu tiên và xác nhận danh sách với nhóm.
2. **Xây dựng mô hình tải:** Đề xuất số người dùng đồng thời, tần suất thao tác, tỷ lệ giữa các loại yêu cầu, dữ liệu thử nghiệm và thời lượng chạy. Mô tả kịch bản tải thông thường, tải tăng dần và tải đột biến; đánh dấu các giả định cần xác nhận.
3. **Xác định cách đo:** Đề xuất các chỉ số tại phía client, service và database, gồm thời gian phản hồi p95/p99, throughput, tỷ lệ lỗi và mức sử dụng tài nguyên. Phân biệt ngưỡng đề xuất với mục tiêu đã được nhóm chốt.
4. **Đánh giá công cụ:** So sánh ngắn các lựa chọn phù hợp theo khả năng mô phỏng luồng thực tế, bảo trì kịch bản, báo cáo, tích hợp CI và công sức vận hành. Đề xuất một công cụ chính và giải thích lý do.
5. **Chuẩn bị môi trường:** Nêu yêu cầu về môi trường, dữ liệu, giám sát và biện pháp tránh ảnh hưởng đến người dùng thật khi chạy thử.
6. **Đề xuất bước đầu tiên:** Xác định phạm vi nhỏ nhất có giá trị cho lần thử nghiệm đầu, cách phân tích kết quả, nhận diện điểm nghẽn và hướng mở rộng sau đó.

## Kết quả bàn giao

Một tài liệu nghiên cứu ngắn, gồm:

- Danh sách luồng và API được ưu tiên, tiêu chí lựa chọn và các dịch vụ liên quan.
- Kịch bản tải ban đầu, dữ liệu đầu vào, giả định và yêu cầu môi trường.
- Chỉ số cần đo, cách thu thập và các ngưỡng đề xuất được ghi rõ là tạm thời.
- Công cụ được đề xuất, tóm tắt so sánh và các đánh đổi.
- Phạm vi thử nghiệm đầu tiên, các task triển khai tiếp theo, rủi ro và những quyết định cần nhóm xác nhận.

## Tiêu chí hoàn thành

- [ ] Nhóm có thể review tài liệu và quyết định phạm vi của lần kiểm thử hiệu năng đầu tiên.
- [ ] Các giả định về lưu lượng, dữ liệu và ngưỡng chấp nhận được ghi rõ; giá trị chưa được duyệt không được trình bày như cam kết.
- [ ] Có thể tách task triển khai từ tài liệu mà không cần nghiên cứu lại từ đầu.
- [ ] Tài liệu nêu nơi lưu kết quả và cách báo cáo điểm nghẽn phát hiện được.

## Ngoài phạm vi

Triển khai bộ kiểm thử hoàn chỉnh, chạy benchmark chính thức, thiết lập SLA/SLO hoặc khẳng định Rentify đạt một ngưỡng hiệu năng cụ thể.
