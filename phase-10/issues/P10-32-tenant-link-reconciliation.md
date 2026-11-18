# P10-32 — Kiểm tra projection và reconcile hợp đồng cũ

**Trạng thái:** 🟡 Open — plan ngày 18/11/2026, chưa chạy repair  
**Ưu tiên:** P0 · **Repo:** Tenancy-Service, Identity-Service nếu cần bootstrap  
**Owner đề xuất:** BE Contract / Identity · **Phụ thuộc:** P10-31 · **Scope:** M mỗi PR; tách bootstrap Identity và repair Tenancy

## Mục tiêu và cách sửa

Sửa handler không tự sửa contract/member NULL đã có hoặc account không được bootstrap vào projection. Đọc record ca lỗi bằng quyền phù hợp: status, tenantId, phone chuẩn hóa, account status/role, projection và outbox/inbox. Kiểm tra migration, queue binding, retry/DLQ và version deploy. Chuẩn bị maintenance command dry-run/apply theo batch để reconcile các ID NULL bằng nguồn Identity hiện tại đã xác minh; cập nhật contract, member và linked outbox trong transaction. Không gọi HTTP trong transaction dữ liệu; không tự chuyển link lịch sử sang account khác.

Identity internal users hiện chỉ lookup theo danh sách ID, không được giả định có list-all/lookup-phone. Nếu thiếu nguồn account lịch sử, tách bootstrap/export nội bộ có phân trang thành PR riêng và chỉ truyền các trường cần thiết. Event cũ đã inbox-dedup không tự chạy lại; không tạo registration giả hoặc xóa inbox để ép xử lý lại.

## Acceptance

- [ ] Có kết luận dựa trên record cụ thể và trạng thái triển khai; phân biệt draft, ID NULL, projection thiếu và API có dữ liệu nhưng app không hiển thị.
- [ ] Dry-run báo số lượng/ID dự kiến, conflict được bỏ qua; apply chỉ link NULL với active tenant/phone chính xác, đồng bộ representative và member, ghi event cần cho chat.
- [ ] Chạy lại không thay đổi thêm hoặc nhân đôi event; mutation/outbox rollback cùng nhau; bootstrap có thể chạy lại và không phục hồi account đã locked/deleted từ snapshot lỗi thời.

## Verification

Thử dữ liệu account/hợp đồng trước/sau deploy; phone `0/+84`, conflict, representative/member, record đã có ID, retry và outbox failure. Chạy focused Jest, build/lint các repo thay đổi. Kiểm tra DB có quyền, API tenant và membership Community sau khi drain event. Requeue chỉ thực hiện cho event thực sự failed/unprocessed sau khi xác định nguyên nhân.

**File dự kiến:** maintenance command/service, CLI entry, test và runbook Tenancy; source/export Identity là PR riêng nếu cần. Không apply live trong lúc chỉ chuẩn bị plan/tool.

**Tham chiếu:** [plan](../../tasks/plan.md), P9-01/02.
