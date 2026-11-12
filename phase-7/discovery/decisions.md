# Phase 7 decisions

## P7-D83 — Phạm vi Web Chat v2 (2026-11-12)

- Chat v2 bổ sung trạng thái đã xem cho người gửi, đang nhập, tìm nội dung tin trong một hội thoại, mở tin tìm được (`maxSequence`) và trả lời trích dẫn. Chi tiết tại [web-chat-v2-decisions.md](web-chat-v2-decisions.md).
- Đây là quyết định mới, không sửa P7-D80: Web Chat v1 vẫn ghi đúng việc typing và trạng thái đã xem từng tin nằm ngoài mốc đầu.
- Không thêm trạng thái “Đã nhận”. Reaction, thu hồi, ghim, tắt tiếng và chia sẻ file để đợt sau.
- Trạng thái đã xem luôn hiển thị; chỉ thành viên `active` được tính.

## P7-D81 — Trạng thái sau demo và chia backlog Web (2026-11-07)

- Web Chat v1 đã được user demo và xác nhận ổn định; readiness audit ngày 04/11 chỉ là ảnh chụp lịch sử, không còn phản ánh trạng thái hiện tại.
- Việc Web tiếp theo tách thành Notification inbox/push preference, quản lý group, gửi ảnh, rồi kiểm chứng tích hợp qua Gateway. Không tự gán các task này vào It8 khi chưa chốt lịch.
- Inbox có unread thì chuông Web hiển thị dot, không hiển thị số vì Community chưa có tổng unread notification endpoint.
- Notification page dùng API cursor list, mark-one/all, GET/PUT preference và hai Socket event đã có; không thêm API backend cho phạm vi này.
- Group management FE dùng các endpoint Community đã có. Group avatar dùng `ownerType=conversation`, `purpose=conversation_avatar`, presigned upload rồi PATCH `avatarMediaId`.

## P7-D82 — Preference điều khiển thông báo nổi Web và push thiết bị (2026-11-07)

- Với từng nhóm `chat`, `invoice`, `issue`, khi user tắt thông báo thì không gửi push tới thiết bị và không hiện toast nổi trong Web.
- Việc tắt không chặn Socket event cần cho đồng bộ, không xóa/lọc business notification khỏi inbox, và không ngăn cập nhật conversation list/unread của chat.
- Khi bật, chat toast dùng `chat:message-received`; Invoice/Issue toast dùng payload `notification:created` (`notificationId`, `type`, `title`, `body`, `deepLink`, `data`, `createdAt`). Click toast đánh dấu notification business đã đọc và mở deep link nội bộ; URL không hợp lệ mở inbox.
- Preference theo category hiện được lưu qua API `pushEnabled`; FE dùng cùng giá trị để quyết định hiển thị toast Web, còn Community áp dụng cho push thiết bị.

## P7-D80 — Phạm vi Web Chat v1 (2026-11-03, 15:53 UTC)

- PM đã chốt các quyết định FE Chat v1 tại [web-chat-v1-decisions.md](web-chat-v1-decisions.md): desktop hai cột; chat 1:1 và nhóm tự do; list/search/history/text/unread; direct chỉ hiện sau tin đầu tiên, group hiện khi tạo; Socket dùng chung sau đăng nhập; badge tổng unread `9+`; toast tin chat có sender, conversation và preview; retry khi mạng trở lại với cùng `clientMessageId`.
- Phạm vi này thay thế lựa chọn responsive web trong lượt hỏi đáp trước: FE chat tập trung desktop, còn điện thoại dùng ứng dụng mobile riêng. Lựa chọn toast chỉ có tên cũng đã được thay bằng toast có đoạn preview.
- Tại thời điểm ghi P7-D80, các API tìm user, tìm conversation, unread summary, sự kiện tin mới tới user room và ràng buộc nhóm tối thiểu ba thành viên còn là dependency cần đối chiếu. Các dependency này đã được xử lý sau đó; xem [trạng thái Web Chat hiện tại](web-chat-v1-current-status.md) để biết phần nào đã triển khai và phần nào còn lại.

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
