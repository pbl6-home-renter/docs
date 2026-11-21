# P11-09 — Spike: so sánh dịch vụ VietQR có sandbox

**Loại:** Research / spike (time-box)  
**Trạng thái:** 🟡 Open  
**Người phụ trách (đề xuất):** `leminhkhai345`  
**Người review:** PM, BE Lead  
**Ước lượng:** 3 points · **time-box 10 giờ** (hết giờ thì nộp kết quả đang có, ghi rõ phần chưa xong)  
**Phụ thuộc:** —  
**Repo:** tài liệu trong `pm/phase-11/discovery/`; PoC (nếu có) trên branch riêng `spike/p11-09-vietqr`, **không merge**  
**Quyết định áp dụng:** [P11-D93](../decisions.md#d93--vietqr-chỉ-làm-spike-sandbox), P6-D61 (Payment deferred), P6-D72 (bỏ VietQR khỏi invoice)

## User story

> Là **PM**, tôi muốn **một bản so sánh các dịch vụ VietQR có môi trường sandbox, kèm flow, công nghệ, rủi ro và biện pháp**, để **quyết định nhóm có làm thanh toán QR cho hóa đơn hay không, và nếu làm thì dùng dịch vụ nào**.

## Bối cảnh

- Spec có `PUT /buildings/{buildingId}/vietqr-config` (`designing`), cấu hình tài khoản nhận tiền **theo tòa nhà**. Chưa có code.
- Identity **đã có tài khoản nhận tiền theo chủ trọ**: `landlord-profiles/domain/value-objects/payout-account.vo.ts` và event `landlord-payout-account-updated`. → Có nguy cơ hai nguồn cấu hình mâu thuẫn.
- Invoice chỉ có trạng thái `pending` / `issued` / `void`, **chưa có `paid`**. QR chỉ có ý nghĩa khi có cách đánh dấu "đã thanh toán" (P6-05 đang deferred).
- `requirement.md`: thanh toán "VietQR sandbox + dynamic named-QR"; D39: tiền mặt/mock là kênh chính, tự động đối soát là Stretch; app không cưỡng chế thu tiền.

## Gợi ý dịch vụ để khảo sát

Đây là danh sách xuất phát. Thông tin dưới đây lấy từ tìm kiếm nhanh, **thành viên phải tự kiểm tra lại trên trang chính thức** (điều kiện đăng ký, có miễn phí không, sandbox còn hoạt động không).

| Dịch vụ | Sandbox / test mode | Điểm đáng chú ý | Tài liệu |
|---|---|---|---|
| **SePay** | Có Test mode tách biệt production | Giả lập giao dịch ngân hàng (1.000 – 499.000.000đ), giả lập quét VietQR trên UI, webhook chạy như live, có log gửi webhook; cổng thanh toán có sandbox riêng và IPN; có SDK Node.js | [Test mode](https://developer.sepay.vn/en/tien-ich-khac/test-mode) · [Giả lập VietQR](https://developer.sepay.vn/en/tien-ich-khac/test-mode/mo-phong-tao-ma-vietqr) · [Giả lập giao dịch](https://developer.sepay.vn/en/tien-ich-khac/test-mode/mo-phong-giao-dich) · [Webhook test mode](https://developer.sepay.vn/en/sepay-webhooks/test-mode/bat-dau-nhanh) · [Gateway sandbox](https://developer.sepay.vn/en/cong-thanh-toan/sandbox) · [SDK Node.js](https://developer.sepay.vn/en/cong-thanh-toan/sdk/nodejs) |
| **VietQR.vn API** | Môi trường mặc định là sandbox | Có API "Test Callback" giả lập thanh toán thành công mà không cần quét QR. Phía mình phải tự dựng API cấp token và API nhận đồng bộ giao dịch, rồi khai báo trên VietQR.vn | [Payment APIs](https://api.vietqr.vn/en/v1/vietqr-payment-apis) · [Test Callback](https://api.vietqr.vn/en/v1/vietqr-apis/test-callback) · [Các bước tạo QR](https://api.vietqr.vn/en/v1/overview/step-to-create-a-vietqr-code) |
| **ZaloPay** | Có sandbox (`sbmc.zalopay.vn`) và thẻ test | Là cổng ví điện tử, không phải chuyển khoản ngân hàng VietQR thuần; tham khảo nếu muốn so sánh mô hình cổng thanh toán | [Test resources](https://docs.zalopay.vn/docs/developer-tools/test-instructions/testing) |
| **payOS** | **Chưa xác minh** có sandbox | Hay được dùng cho đồ án; cần kiểm tra trực tiếp trên tài liệu chính thức xem có test mode không | tự tìm |
| **VNPAY** | Có sandbox cổng thẻ | Một bài cộng đồng năm 2022 cho biết sandbox **không hỗ trợ test QR**; chưa xác minh với tài liệu chính thức | tự tìm |
| **Sinh QR tĩnh tự build** (chuẩn EMVCo/NAPAS 247) | Không cần sandbox | Tự sinh chuỗi QR có số tài khoản, số tiền, nội dung = mã hóa đơn; miễn phí, không phụ thuộc bên thứ ba, nhưng **không có đối soát tự động** (landlord tự xác nhận) | tự tìm |

## Kết quả cần bàn giao

Tài liệu `pm/phase-11/discovery/vietqr-sandbox-research.md` (tiếng Việt), gồm:

1. **Bảng so sánh** ít nhất 3 dịch vụ trên, theo các tiêu chí: có sandbox không, chi phí/điều kiện đăng ký (cần doanh nghiệp hay cá nhân được), có webhook/đối soát tự động không, có SDK Node.js không, độ khó tích hợp (ước lượng points), giới hạn đã biết.
2. **Phân tích flow** (sequence diagram mermaid) cho phương án đề xuất:
   - Landlord cấu hình tài khoản nhận tiền.
   - Phát hành hóa đơn → sinh QR động (số tiền + nội dung chuyển khoản chứa mã hóa đơn).
   - Tenant quét QR trên Web/app và chuyển khoản.
   - Ghi nhận thanh toán: tự động qua webhook, hoặc landlord bấm xác nhận.
   - Hóa đơn chuyển sang trạng thái đã thanh toán; notification cho hai bên.
3. **Đề xuất nơi lưu tài khoản nhận tiền:** dùng `payout account` có sẵn ở Identity (theo chủ trọ) hay cấu hình theo tòa như spec. Nêu lý do và ảnh hưởng tới API `vietqr-config` (giữ, sửa hay retire).
4. **Công nghệ dự kiến:** service nào chịu trách nhiệm (Tenancy, hay mở lại `payment-service` đang comment trong `infra/docker-compose.internal.yml`), event nào cần thêm, endpoint webhook đặt ở đâu và đi qua gateway thế nào.
5. **Bảng rủi ro và biện pháp**, tối thiểu xét các rủi ro sau:

   | Rủi ro | Biện pháp cần đề xuất |
   |---|---|
   | Lộ số tài khoản ngân hàng của chủ trọ | ? |
   | QR sai số tiền hoặc dùng lại cho hóa đơn khác | ? |
   | Tenant chuyển khoản sai nội dung, không khớp được hóa đơn | ? |
   | Webhook giả mạo hoặc bị gửi lặp | ? |
   | Hóa đơn bị hủy/tính lại sau khi đã phát QR | ? |
   | Dịch vụ bên thứ ba ngừng sandbox, đổi API hoặc thu phí | ? |
   | Key sandbox bị commit lên Git | ? |
   | Trộn lẫn giao dịch sandbox với dữ liệu thật trên staging | ? |

6. **Khuyến nghị cuối:** chọn 1 trong 3 hướng, kèm ước lượng points nếu làm:
   - (a) Làm đầy đủ: QR động + đối soát tự động qua webhook sandbox.
   - (b) Làm rút gọn: QR động + landlord bấm "đã nhận tiền" (không webhook).
   - (c) Không làm: retire API `vietqr-config`, giữ tiền mặt/mock theo D39.
7. **(Tùy chọn) PoC:** một script hoặc branch gọi sandbox của dịch vụ đề xuất, sinh 1 QR và nhận 1 webhook giả lập. Ảnh chụp kết quả đưa vào tài liệu.

## Acceptance criteria

- [ ] **Given** tài liệu đã nộp, **then** có bảng so sánh ≥ 3 dịch vụ, mỗi ô thông tin có link nguồn chính thức kèm ngày kiểm tra.
- [ ] Có ít nhất 1 sequence diagram mermaid render được trên GitHub.
- [ ] Có đề xuất rõ ràng về nơi lưu tài khoản nhận tiền và số phận của API `vietqr-config`.
- [ ] Bảng rủi ro có đủ 8 dòng trên, mỗi dòng có biện pháp cụ thể (không ghi chung chung "cẩn thận").
- [ ] Có khuyến nghị (a)/(b)/(c) kèm ước lượng points, đủ để PM ra quyết định mới.
- [ ] Không có key, secret, số tài khoản thật nào trong tài liệu hay branch PoC.

## Ngoài phạm vi

- Merge code thanh toán vào `main`; sửa contract `api-docs`; giao dịch tiền thật.
- Quyết toán tiền cọc, hoàn tiền, nhắc nợ, phạt trễ hạn (trái D39).

## Definition of Done

- [ ] Tài liệu được merge vào `pm/phase-11/discovery/` sau khi PM và BE Lead review.
- [ ] PM ghi quyết định tiếp theo (D-ID mới trong `phase-11/decisions.md`) dựa trên khuyến nghị.
