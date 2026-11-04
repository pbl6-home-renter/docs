# Phase 7 decisions

## P7-D80 — Phạm vi Web Chat v1 (2026-11-03, 15:53 UTC)

- PM đã chốt các quyết định FE Chat v1 tại [web-chat-v1-decisions.md](web-chat-v1-decisions.md): desktop hai cột; chat 1:1 và nhóm tự do; list/search/history/text/unread; direct chỉ hiện sau tin đầu tiên, group hiện khi tạo; Socket dùng chung sau đăng nhập; badge tổng unread `9+`; toast tin chat có sender, conversation và preview; retry khi mạng trở lại với cùng `clientMessageId`.
- Phạm vi này thay thế lựa chọn responsive web trong lượt hỏi đáp trước: FE chat tập trung desktop, còn điện thoại dùng ứng dụng mobile riêng. Lựa chọn toast chỉ có tên cũng đã được thay bằng toast có đoạn preview.
- Cần bổ sung/đối chiếu API tìm user cho user thường, tìm conversation, sự kiện tin mới tới user room, tổng unread và ràng buộc nhóm tối thiểu ba thành viên trước khi code FE. Đây là dependency thiết kế, chưa coi là API/event đã duyệt.

## P7-D78 — Hành vi system message khi kick/rời nhóm (2026-11-02)

- Kick hoặc tự rời nhóm ghi một system message riêng trong cùng transaction với thay đổi membership.
- Khi admin cuối cùng bị kick hoặc tự rời, hệ thống chuyển admin cho thành viên active còn lại tham gia sớm nhất và ghi thêm một system message riêng về việc chuyển admin.
- `leftSequence` của member rời/kick bao gồm message membership và, nếu có, message chuyển admin được ghi trong cùng transaction. Member read-only vẫn xem được các message này.
- Nếu không còn thành viên user active để tiếp nhận admin hoặc để duy trì nhóm, thao tác bị từ chối nguyên tử; không xóa/đóng conversation.
- Payload là discriminated union: `member_kicked` và `member_left` chứa `actorUserId` cùng snapshot `member`; `admin_transferred` chứa `actorUserId` cùng snapshot admin mới trong `member`.

## P7-D79 — System message đổi vai trò thành viên (2026-11-02)

- Đổi vai trò ghi system message `member_role_changed` với `actorUserId`, snapshot `member`, `oldRole` và `newRole` (`admin|member`).
- Role change và system message được ghi cùng transaction. Nếu role đích giống role hiện tại, trả thành công nhưng không ghi message trùng.
- Chỉ admin active được đổi vai trò user active trong group; không thể hạ admin cuối cùng. Không gửi FCM.

## P7-D01 — Xếp lịch và phân công Community Service (2026-11-01)

- Community Service được đưa vào Phase 7 như một track song song với Phase 6, bắt đầu từ It5 (02/11–08/11); không dời các task Phase 6 đã giao.
- It5 tập trung các issue P7-01–06: API contract alignment, Gateway/runtime và generic Conversation/Member/Message persistence. API conversation thực hiện tiếp ở It6; message history/unread ở It7 theo dependency tracker.
- `baoduong17` phụ trách backend Community; `ThaiBao11125` phụ trách Web; `tphuongin` phụ trách Android.
- Các phần Socket/Media/Inbox/FCM, client, contextual/domain event và bot đi theo dependency ở It6–It8. Domain event publisher không phải công việc mở đầu của It5.
- It8 chưa có ngày chính thức; PM sẽ cập nhật lịch khi iteration đó được lên kế hoạch.
