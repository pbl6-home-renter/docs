# P10-12 — Gửi bot reminder thủ công vào hội thoại

**Loại:** Backend · **Trạng thái:** ⚪ Blocked — chốt template/resource contract  
**Owner đề xuất:** `baoduong17` · **Reviewer:** BE Lead / PM · **Repo:** `community-service`, `api-docs`  
**Phụ thuộc:** P7-CB-15; P9-03/04/08 theo template; P6-D78 · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## Bối cảnh và mục tiêu

Là chủ nhà, tôi muốn chủ động gửi thông báo theo mẫu vào hội thoại liên quan để người thuê nhận được thông tin nhất quán. Phase 7 backlog CB-15 đã mô tả luồng này, nhưng rà soát chưa thấy handler `POST /conversations/{conversationId}/bot-reminders`. Issue này chuyển phần backend của CB-15 thành task triển khai có thể theo dõi; không mở lại chat v1.

## Quyết định và contract

- Theo CB-15, chỉ gửi khi landlord chủ động yêu cầu; lưu bot message vào history, phát realtime và push theo preference; retry theo `clientMessageId` không tạo bản sao.
- `api-docs/src/paths/chat/conversation-bot-reminders.yaml` đang `designing`, nhận `templateType`, `resourceId`, `clientMessageId`, dự kiến `201 BOT_REMINDER_SENT`. Schema hiện có `ocr_result`, `invoice`, `contract_expiring`.
- **Blocker:** PM/API owner chốt template được phép, nội dung snapshot, dữ liệu nguồn và quyền resource/context. P6-D78 hoãn OCR; không triển khai `ocr_result` bằng dữ liệu giả hoặc tự sửa enum. Những template cần notification/payment ngoài scope cũng phải được xác nhận.

## Các bước triển khai

1. Đối chiếu CB-15, message idempotency, context membership, OpenAPI và P6-D78; lập bảng template → resource → source → quyền → nội dung. API owner cập nhật YAML/diagram sau khi decision được ghi. **Kiểm tra:** bảng nêu được một resource hợp lệ và một trường hợp không có quyền cho từng template được duyệt.
2. Kết nối nguồn dữ liệu theo contract nội bộ được duyệt; dùng read-only internal HTTP/port hiện có, không truy cập DB service khác. Xử lý resource không tồn tại, sai context và service nguồn lỗi theo contract. **Kiểm tra:** landlord A không thể tạo reminder bằng resource của B; không tạo message khi nguồn lỗi.
3. Bổ sung use case và endpoint: kiểm tra user/context/resource, tạo payload từ nguồn tin cậy, lưu message theo transaction và idempotency pattern hiện hành, phát Socket/FCM sau commit. **Kiểm tra:** gửi cùng key hai lần chỉ có một message và một side effect logic.
4. Đồng bộ OpenAPI, response/error và test domain/application; chạy backend build/lint/test và API qua Gateway. **Kiểm tra:** gửi hợp lệ xuất hiện trong history và client khác nhận event; member không hợp lệ bị từ chối.

## Acceptance

- Mỗi template được duyệt tạo message đúng resource/conversation, không lộ dữ liệu ngoài quyền; không tạo message nếu validation hoặc nguồn dữ liệu lỗi.
- Retry an toàn, message lưu trước khi phát; chat preference ảnh hưởng push theo rule hiện có, Socket/historical sync vẫn nhất quán.
- Có bằng chứng test authorization, sai context, duplicate, source unavailable, response và PR OpenAPI; không có scheduler hoặc OCR mới.
