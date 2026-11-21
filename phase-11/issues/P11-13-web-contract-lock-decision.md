# P11-13 — Web: chủ trọ chọn khôi phục hoặc chấm dứt hợp đồng sau khi được mở khóa

**Trạng thái:** 🟡 Open  
**Người phụ trách (đề xuất):** `ThaiBao11125`  
**Người review:** FE Lead, `leminhkhai345` (owner luồng khóa landlord)  
**Ước lượng:** 2 points · khoảng 8 giờ  
**Phụ thuộc:** API `PUT /contracts/{contractId}/lock-cycles/{lockCycleId}/decision` và notification `decision_required` đã merge (P9-06/P9-07)  
**Repo / branch:** `fe` · `feature/p11-13-contract-lock-decision`

## User story

> Là **chủ trọ vừa được admin mở khóa tài khoản**, tôi muốn **chọn khôi phục hay chấm dứt từng hợp đồng đã bị tạm ngưng trong thời gian tôi bị khóa**, để **các phòng trở lại hoạt động bình thường hoặc được giải phóng đúng ý tôi**.

## Bối cảnh

- Khi landlord bị khóa, Tenancy chuyển các hợp đồng sang `suspended` và mở một *lock cycle* có hạn (grace deadline).
- Nếu được mở khóa **trước** hạn, cycle chuyển sang chờ quyết định và landlord nhận notification. Hợp đồng nào chưa được chọn thì **vẫn `suspended` mãi**.
- **Hiện FE chưa có màn nào gọi API quyết định**, và chưa xử lý loại notification này (`notification-content.ts` chỉ xử lý `issue.*` và `match_request.*`). Nghĩa là landlord không có cách nào gỡ hợp đồng khỏi trạng thái tạm ngưng.

## Contract (đã có)

- Notification `type = system`, `data = { landlordId, lockCycleId, contractIds[], graceDeadline, action }`.
  - `action = decision_required`: cần landlord chọn.
  - `action = restore` / `terminate`: thông báo kết quả, chỉ hiển thị.
- `PUT /contracts/{contractId}/lock-cycles/{lockCycleId}/decision`, body `{ action: "restore" | "terminate" }`. Response: `status` (`active` | `terminated`), `decidedAt`, `handoverRequired`.
- Lỗi cần xử lý:
  - Gửi lại **cùng** lựa chọn → trả lại kết quả đã lưu (coi như thành công).
  - `CONTRACT_LOCK_DECISION_CONFLICT`: đã chọn khác trước đó.
  - `LANDLORD_LOCK_CYCLE_STALE`: cycle đã bị thay bởi cycle mới.
  - `LANDLORD_LOCK_CYCLE_NOT_AWAITING_DECISION`: cycle không còn chờ quyết định.
  - Hợp đồng không thuộc cycle hoặc không còn `suspended`.

## Mô tả

1. **Notification:** thêm nội dung hiển thị cho notification `system` có `data.action` = `decision_required`, `restore`, `terminate` (tiêu đề/nội dung đã là mã i18n từ backend, bổ sung key vi + en nếu thiếu). Bấm notification `decision_required` → mở màn quyết định với `lockCycleId` và `contractIds`.
2. **Màn/dialog "Xử lý hợp đồng bị tạm ngưng":**
   - Liệt kê các hợp đồng trong `contractIds` (lấy chi tiết từng hợp đồng bằng API hợp đồng có sẵn): phòng, khách đại diện, ngày bắt đầu, trạng thái.
   - Mỗi hợp đồng có 2 nút "Khôi phục" và "Chấm dứt". "Chấm dứt" phải qua dialog xác nhận nói rõ hậu quả (hợp đồng kết thúc, cần bàn giao phòng).
   - Sau khi chọn: hiện kết quả trên dòng đó; nếu `handoverRequired = true` thì hiện nhắc "Cần hoàn tất trả phòng" kèm liên kết sang hợp đồng.
3. **Lối vào thứ hai:** trên trang chi tiết hợp đồng `suspended`, nếu đang có cycle chờ quyết định (lấy từ notification gần nhất có `contractIds` chứa hợp đồng này), hiện banner kèm 2 nút như trên. Nếu không xác định được cycle thì chỉ hiện banner giải thích trạng thái tạm ngưng, không hiện nút.
4. **Xử lý lỗi:** mỗi mã lỗi ở trên có thông báo tiếng Việt dễ hiểu; `STALE`/`NOT_AWAITING_DECISION` → báo "Yêu cầu này đã hết hiệu lực" và làm mới dữ liệu.
5. Chuỗi qua i18n (vi + en).

## Acceptance criteria

- [ ] **Given** landlord có 2 hợp đồng bị tạm ngưng và được mở khóa trước hạn, **when** mở notification "cần quyết định", **then** thấy màn liệt kê đúng 2 hợp đồng.
- [ ] **Given** bấm "Khôi phục" một hợp đồng, **then** hợp đồng chuyển `active`, dòng đó hiện "Đã khôi phục"; danh sách hợp đồng cũng thấy trạng thái mới.
- [ ] **Given** bấm "Chấm dứt", **then** phải xác nhận trước; sau đó hợp đồng `terminated` và hiện nhắc hoàn tất trả phòng nếu `handoverRequired`.
- [ ] **Given** bấm "Khôi phục" hai lần (double click hoặc mở lại màn), **then** không báo lỗi, hiển thị kết quả đã lưu.
- [ ] **Given** đã chấm dứt rồi lại bấm "Khôi phục", **then** báo đã có quyết định khác, không đổi dữ liệu.
- [ ] **Given** cycle đã hết hiệu lực, **then** báo "Yêu cầu này đã hết hiệu lực" và tải lại dữ liệu.
- [ ] **Given** notification `restore`/`terminate`, **then** chỉ hiển thị nội dung, bấm vào mở hợp đồng tương ứng.
- [ ] Nút bị khóa trong lúc đang gửi request; đọc được ở chiều rộng điện thoại.

## Ngoài phạm vi

- Thay đổi backend luồng khóa landlord.
- API liệt kê cycle đang chờ quyết định (nếu nhóm thấy cần để không phụ thuộc notification, ghi đề xuất vào PR để PM tạo task backend riêng).

## Definition of Done

- [ ] Không viết file test. `npm run build`, `npm run lint`, `npm run i18n:check` pass.
- [ ] Smoke trên staging: admin khóa landlord → mở khóa trước hạn → landlord khôi phục 1 và chấm dứt 1 hợp đồng; ảnh chụp đính kèm PR.
