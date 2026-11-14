# P10-01 — Chặn xóa phòng đang có hợp đồng hiệu lực

**Trạng thái:** 🟢 Done — code đã merge · **Owner đề xuất:** `leminhkhai345` · **Reviewer:** BE Lead / PM  
**Repo:** `Tenancy-Service`, `api-docs` · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`  
**Phụ thuộc:** P5-09c, P6-01d. P5-09c đã chủ ý hoãn điều kiện này, nên đây là phần tiếp nối riêng.

## Cập nhật triển khai 14/11/2026

[Tenancy #47](https://github.com/pbl6-home-renter/Tenancy-Service/pull/47) và [API docs #61](https://github.com/pbl6-home-renter/api-doc/pull/61) đã merge. Còn kiểm tra điều kiện xóa qua Gateway và dữ liệu thật.

## Bối cảnh và mục tiêu

P2-D50 quy định `DELETE /rooms/{roomId}` trả `409 ROOM_HAS_ACTIVE_CONTRACT` khi phòng có hợp đồng hiệu lực. Handler `room-delete.command.handler.ts` hiện khóa phòng và xóa nhưng để TODO; Contract đã có `existsActiveByRoom`. Xóa phòng không được làm mất dấu phòng đang phục vụ hợp đồng. API hiện chưa mô tả 409, cần đồng bộ contract.

## Triển khai

1. Đọc P2-D50, P5-09c, flow activate và `contract.repository.ts`; xác nhận thứ tự khóa và trạng thái `active`. Cập nhật `api-docs/src/paths/rooms/rooms-roomId.yaml` mô tả 409 và error code theo envelope hiện hành; bundle spec. **Kiểm tra:** OpenAPI lint và operation có 409 rõ ràng.
2. Trong transaction xóa, sau kiểm tra owner và khóa phòng, kiểm tra `existsActiveByRoom(roomId, context)` qua port; nếu có thì ném domain exception tương ứng trước khi mutate/save/outbox. Giữ nguyên 403/404 và soft-delete khi hợp lệ. **Kiểm tra:** phòng active trả 409, không đổi `is_deleted`, không thêm `room.deleted`; phòng không active xóa thành công.
3. Đối chiếu activation và delete cùng khóa room, bảo đảm khi chạy đồng thời không thể vừa activate thành công vừa xóa phòng; giữ thứ tự khóa nhất quán. **Kiểm tra:** chạy hai transaction đồng thời theo cả hai thứ tự, tối đa một thao tác thành công; không deadlock hoặc tạo contract active trỏ đến phòng đã xóa.
4. Bổ sung unit/integration test có ý nghĩa cho active, không active, không sở hữu, rollback và race; chạy build, lint, test liên quan; thử API qua Gateway.

## Acceptance

- Phòng có contract active trả `409 ROOM_HAS_ACTIVE_CONTRACT`, không xóa và không phát event xóa; phòng không có contract active vẫn xóa theo contract hiện hành.
- Owner khác và ID không tồn tại giữ 403/404; hành vi đồng thời delete/activate bảo toàn invariant.
- API docs, bằng chứng test và PR implementation liên kết nhau; không thay đổi nghiệp vụ hợp đồng khác.

## User story và quy tắc nghiệp vụ

Là chủ nhà, tôi muốn gỡ phòng khai báo nhầm nhưng hệ thống phải ngăn thao tác nếu phòng còn hợp đồng hiệu lực, để dữ liệu vận hành không mâu thuẫn. P2-D50 là quy tắc đã chốt; P5-09c chỉ hoãn kiểm tra vì Contract chưa tồn tại. Lỗi trả theo envelope dự án, không trả chi tiết hợp đồng cho người không sở hữu.

| Trạng thái trước thao tác | Kết quả mong đợi | Dữ liệu sau thao tác |
|---|---|---|
| Owner, có contract `active` | 409 `ROOM_HAS_ACTIVE_CONTRACT` | Room, contract và outbox không đổi |
| Owner, không có contract `active` | 204 | Room soft-delete, phát event như flow hiện có |
| Không phải owner | 403 | Không thay đổi dữ liệu |
| Room không tồn tại/đã xóa | 404 | Không thay đổi dữ liệu |

## Kịch bản nghiệm thu chi tiết

- **Given** phòng R thuộc A và có contract active, **When** A gửi DELETE, **Then** nhận 409 và tìm lại được R cùng contract; không có event `room.deleted` mới.
- **Given** R không có contract active, **When** A xóa R, **Then** nhận 204, list không còn R, bản ghi hợp đồng lịch sử vẫn nguyên.
- **Given** B không sở hữu R, **When** B gọi DELETE, **Then** nhận 403 bất kể trạng thái contract; không lộ thông tin tenant.
- Chạy đồng thời activation và delete trên cùng phòng, xác minh database/outbox ở cả hai thứ tự thực thi. Đính kèm request/response đã che thông tin nhạy cảm, log test và link PR contract.

## Ranh giới và hoàn tất

Không tự thay đổi cách xử lý hợp đồng `suspended` hoặc luật cascade: nếu decision hiện hành yêu cầu chặn thêm trạng thái, ghi blocker cho PM trước khi triển khai phần đó. Hoàn tất khi test liên quan, build/lint, OpenAPI lint/bundle và review cùng pass; kiểm tra `ROOM_HAS_ACTIVE_CONTRACT` nhất quán giữa exception, filter và docs.
