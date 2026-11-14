# P10-18 — Kiểm chứng Chat v2 và attachment xuyên service

**Loại:** Integration / QA · **Trạng thái:** 🟡 Open  
**Owner đề xuất:** `ThaiBao11125` + `baoduong17` · **Reviewer:** PM · **Repo:** `fe`, `community-service`, `Identity-Service`, `api-gateway`, `api-docs`  
**Phụ thuộc:** P7-D83, P7-18; các PR chat/media đang triển khai · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## Bối cảnh

P7-18 kiểm chứng Web Chat v1. P7-D83 bổ sung read receipt, typing, search và reply; handoff v2 ghi chưa chạy E2E với service thật. Các branch workspace có thêm attachment đang thay đổi; sự tồn tại của code không xác nhận đã merge hoặc release.

## Phạm vi và tiền đề

- Baseline P7-D83: typing, read receipt, tìm tin, mở tin, reply và reconnect. Attachment ngoài ảnh chỉ kiểm thử nếu contract/decision mới đã chấp thuận và các PR liên quan sẵn sàng; không mặc định mở rộng scope v2.
- Dùng môi trường dev/staging, tối thiểu hai user và nhóm ba người; chuẩn bị một member bị kick/read-only. Lưu commit, version contract, migration, route Gateway và trạng thái PR trước khi chạy.
- Không thu thập token, nội dung chat thật hay PII vào evidence; chỉ dùng tài khoản/dữ liệu thử nghiệm.

## Các bước và kịch bản

1. Đối chiếu P7-18, handoff v2, contract REST/Socket và các issue/PR hiện có; lập checklist phần chưa có evidence để không chạy trùng. **Kiểm tra:** mọi case map tới decision hoặc contract, ghi branch/commit và dependency đang chờ.
2. Với direct/group, kiểm tra mark-read tăng cursor, read-only không nhận event mới; typing chỉ gửi sau join, timeout và reconnect theo P7-D83. **Kiểm tra:** sender thấy đúng người đã đọc, không tự hiện typing của mình và người bị loại không nhận event.
3. Tìm từ có/không dấu, cursor và mở tin cũ; reply hợp lệ, tin khác hội thoại/không còn khả dụng; retry cùng `clientMessageId`. **Kiểm tra:** quyền history/read-only đúng, không lộ nội dung bị ẩn, không tạo tin đôi.
4. Kiểm tra upload/read attachment được duyệt, quyền thành viên và expired URL; restart/reconnect và phục hồi history. **Kiểm tra:** media sai conversation hoặc member không đủ quyền bị từ chối; file chưa complete không được coi đã gửi.
5. Chạy build/lint/i18n FE và build/lint/test phù hợp ở service có thay đổi; lưu bảng expected/actual, correlation ID và link lỗi. Lỗi được ghi vào issue hiện có hoặc issue riêng, không đóng bằng checklist build.

## Acceptance

- Mọi case thuộc scope được phê duyệt có evidence pass hoặc lỗi có issue/dependency và owner; không đánh dấu pass khi chưa có môi trường.
- Kiểm chứng được quyền read-only, idempotency, reconnect, REST/Socket sync và media authorization ở ít nhất hai user.
- P7-18 được tham chiếu cho v1; issue này chỉ bổ sung evidence v2 và attachment được duyệt.
