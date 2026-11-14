# P10-11 — Phân loại và chốt phạm vi các API còn ở thiết kế

**Loại:** Discovery / scope decision · **Ưu tiên đề xuất:** Medium · **Trạng thái:** ⚪ Blocked chờ PM  
**Owner đề xuất:** PM / API owner · **Repo:** `pm`, `api-docs` · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## Bối cảnh

Đối chiếu operation cho thấy API roommate/match, favorite rooms, room hub, IssueReport, bot reminder và VietQR config còn `designing` và chưa thấy controller tương ứng trong bốn repo được yêu cầu. Payment/deposit-settlement đã `deprecated` theo contract hiện tại; P6-D61/D78 cùng quyết định Phase 7/9 giới hạn nhiều tính năng. Không thể lấy sự hiện diện của YAML làm phê duyệt nghiệp vụ hay khẳng định endpoint bị thiếu chỉ dựa trên tên operationId.

## Các bước thực hiện

P10-12–30 đã tạo các issue con theo khả năng để ghi dependency và acceptance dự kiến. Issue này vẫn là nơi rà soát coverage và chốt phạm vi; các issue con deferred/blocked không tự trở thành phê duyệt implementation và không thay P6/P9 đã có.

1. Dùng [kiểm kê API](../discovery/api-inventory.md), kiểm tra controller theo method/path, gateway, repo sở hữu và tracker cũ; ghi rõ `implemented`, `partial`, `missing`, `deferred`, `deprecated` hoặc `unknown`, kèm bằng chứng và baseline branch.
2. Với mỗi nhóm (room hub/favorite; roommate/match; IssueReport; reminders; VietQR/payment), đối chiếu yêu cầu và decision mới nhất; PM chọn đưa vào backlog triển khai hay giữ deferred. Không phục hồi Payment/OCR chỉ từ ví dụ trong OpenAPI.
3. Nếu chấp thuận phạm vi, chốt actor, luồng, business rules, lỗi, dữ liệu, bảo mật, API và dependency; tách issue BE/FE nhỏ có acceptance và kiểm thử theo luồng. Update decision log/schedule khi scope thực sự thay đổi.
4. Nếu chưa có rule hoặc service owner, đánh dấu blocked và nêu câu hỏi cụ thể; không tạo code giả, không thay đổi trạng thái API `released`.

## Acceptance

- Mỗi nhóm API có trạng thái, bằng chứng và liên kết issue cũ hoặc quyết định PM; không gộp API deprecated vào việc triển khai mặc định.
- Nhóm được duyệt có issue triển khai độc lập đủ contract/acceptance; nhóm chưa duyệt có blocker và owner ra quyết định.
