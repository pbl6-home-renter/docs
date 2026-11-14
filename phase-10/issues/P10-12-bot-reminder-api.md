# P10-12 — Gửi bot reminder thủ công vào hội thoại

**Loại:** Backend · **Trạng thái:** 🔵 In progress — PR code chờ review/merge

**Owner đề xuất:** `baoduong17` · **Reviewer:** BE Lead / PM · **Repo:** `community-service`, `api-docs`

**Phụ thuộc:** P7-CB-15; P9-03/04/08 theo template; P6-D78 · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## Bối cảnh và mục tiêu

Là chủ nhà, tôi muốn chủ động gửi thông báo theo mẫu vào hội thoại liên quan để người thuê nhận được thông tin nhất quán. Phase 7 backlog CB-15 đã mô tả luồng này, nhưng rà soát chưa thấy handler `POST /conversations/{conversationId}/bot-reminders`. Issue này chuyển phần backend của CB-15 thành task triển khai có thể theo dõi; không mở lại chat v1.

## Quyết định và contract

- Theo CB-15, chỉ gửi khi landlord chủ động yêu cầu; lưu bot message vào history, phát realtime và push theo preference; retry theo `clientMessageId` không tạo bản sao.
- `api-docs/src/paths/chat/conversation-bot-reminders.yaml` đang `designing`, nhận `templateType`, `resourceId`, `clientMessageId`, dự kiến `201 BOT_REMINDER_SENT`. Schema hiện có `ocr_result`, `invoice`, `contract_expiring`.
- **Quyết định 14/11/2026:** Người yêu cầu cho phép tự thiết kế nội dung thông báo và sử dụng notification/payment khi cần. Phạm vi đợt này, nguồn dữ liệu và quyền được ghi bên dưới. P6-D78 hoãn OCR; không triển khai `ocr_result` bằng dữ liệu giả.

## Rà soát triển khai 14/11/2026

Đã đối chiếu Community, Tenancy và API contract. Ngày 14/11/2026, người yêu cầu cho phép tự chọn nội dung thông báo và sử dụng notification/payment khi cần. Đợt này triển khai hai mẫu thông báo `invoice` và `contract_expiring`, theo dữ liệu thật; không khẳng định trạng thái thanh toán khi nguồn chưa cung cấp. OCR vẫn deferred. Không coi `designing` là endpoint đã triển khai.

[Community #36](https://github.com/pbl6-home-renter/community-service/pull/36) đang chờ review/merge; [API contract ca8253a](https://github.com/pbl6-home-renter/api-doc/commit/ca8253a) đã được push lên main, endpoint vẫn `designing`. Backend build/lint và 87 unit tests đạt. Gateway, Socket hai client, PostgreSQL cạnh tranh đồng thời và FCM với dữ liệu thật chưa được kiểm tra.

| Mẫu | Dữ liệu có thể đối chiếu | Điểm cần chốt |
|---|---|---|
| `invoice` | `GET /invoices/{id}` kiểm tra chủ sở hữu; response có `contractId`, `period`, `totalAmount`, `invoiceStatus`. | Hóa đơn `issued`, đúng hợp đồng; nêu kỳ và tổng. `issued` không phải bằng chứng chưa thanh toán. |
| `contract_expiring` | `GET /contracts/{id}` kiểm tra chủ sở hữu; response có `id`, `status`, `endDate`. | Hợp đồng active, đúng hội thoại; nêu ngày kết thúc. Chủ nhà tự chọn thời điểm gửi. |
| `ocr_result` | OCR đã deferred theo P6-D78. | Không triển khai nếu chưa có quyết định thay đổi phạm vi. |

Trong đợt này, chỉ gửi từ hội thoại hợp đồng đúng resource; yêu cầu landlord là thành viên active và Tenancy xác thực quyền bằng token người dùng. Hóa đơn phải `issued`; hợp đồng phải `active`. Nội dung nêu kỳ và tổng hóa đơn hoặc ngày kết thúc hợp đồng, không tự suy đoán đã/chưa thanh toán. Tin nhắn được gửi thủ công, không có scheduler. Message cần lưu snapshot, transaction, sequence, Socket/push và chống trùng khi retry.

## Các bước triển khai

1. Đối chiếu CB-15, message idempotency, context membership, OpenAPI và P6-D78; lập bảng template → resource → source → quyền → nội dung. API owner cập nhật YAML/diagram sau khi decision được ghi. **Kiểm tra:** bảng nêu được một resource hợp lệ và một trường hợp không có quyền cho từng template được duyệt.
2. Kết nối nguồn dữ liệu theo contract nội bộ được duyệt; dùng read-only internal HTTP/port hiện có, không truy cập DB service khác. Xử lý resource không tồn tại, sai context và service nguồn lỗi theo contract. **Kiểm tra:** landlord A không thể tạo reminder bằng resource của B; không tạo message khi nguồn lỗi.
3. Bổ sung use case và endpoint: kiểm tra user/context/resource, tạo payload từ nguồn tin cậy, lưu message theo transaction và idempotency pattern hiện hành, phát Socket/FCM sau commit. **Kiểm tra:** gửi cùng key hai lần chỉ có một message và một side effect logic.
4. Đồng bộ OpenAPI, response/error và test domain/application; chạy backend build/lint/test và API qua Gateway. **Kiểm tra:** gửi hợp lệ xuất hiện trong history và client khác nhận event; member không hợp lệ bị từ chối.

## Acceptance

- Mỗi template được duyệt tạo message đúng resource/conversation, không lộ dữ liệu ngoài quyền; không tạo message nếu validation hoặc nguồn dữ liệu lỗi.
- Retry an toàn, message lưu trước khi phát; chat preference ảnh hưởng push theo rule hiện có, Socket/historical sync vẫn nhất quán.
- Có bằng chứng test authorization, sai context, duplicate, source unavailable, response và PR OpenAPI; không có scheduler hoặc OCR mới.
