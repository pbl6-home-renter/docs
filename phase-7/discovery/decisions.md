# Phase 7 decisions

## P7-D78 — Hành vi system message khi kick/rời nhóm (2026-11-02)

- Kick hoặc tự rời nhóm ghi một system message riêng trong cùng transaction với thay đổi membership.
- Khi admin cuối cùng bị kick hoặc tự rời, hệ thống chuyển admin cho thành viên active còn lại tham gia sớm nhất và ghi thêm một system message riêng về việc chuyển admin.
- `leftSequence` của member rời/kick bao gồm message membership và, nếu có, message chuyển admin được ghi trong cùng transaction. Member read-only vẫn xem được các message này.
- Nếu không còn thành viên user active để tiếp nhận admin hoặc để duy trì nhóm, thao tác bị từ chối nguyên tử; không xóa/đóng conversation.
- Payload là discriminated union: `member_kicked` và `member_left` chứa `actorUserId` cùng snapshot `member`; `admin_transferred` chứa `actorUserId` cùng snapshot admin mới trong `member`.

## P7-D01 — Xếp lịch và phân công Community Service (2026-11-01)

- Community Service được đưa vào Phase 7 như một track song song với Phase 6, bắt đầu từ It5 (02/11–08/11); không dời các task Phase 6 đã giao.
- It5 tập trung các issue P7-01–06: API contract alignment, Gateway/runtime và generic Conversation/Member/Message persistence. API conversation thực hiện tiếp ở It6; message history/unread ở It7 theo dependency tracker.
- `baoduong17` phụ trách backend Community; `ThaiBao11125` phụ trách Web; `tphuongin` phụ trách Android.
- Các phần Socket/Media/Inbox/FCM, client, contextual/domain event và bot đi theo dependency ở It6–It8. Domain event publisher không phải công việc mở đầu của It5.
- It8 chưa có ngày chính thức; PM sẽ cập nhật lịch khi iteration đó được lên kế hoạch.
