# P9-05 — Community: notification type/category `system`

**Epic:** Tích hợp event Phase 9  
**Trạng thái:** 🟡 Open  
**Coder:** `huynhtiennhat0403`  
**Người review:** PM  
**Ước lượng:** 2 points · 8 giờ  
**Phụ thuộc:** P7-15; P7-D82  
**Repo:** `community-service/`, `fe/`  
**Issue:** `docs#TBD`

## Mục tiêu

Cho phép thông báo Building/account/contract dùng type và preference `system` riêng, không xếp nhầm vào invoice hoặc issue.

## Contract

- Thêm `system` vào NotificationType và NotificationCategory phía Community, validation, persistence, mặc định và API DTO.
- User mới mặc định `system.pushEnabled=true`.
- `system` delivery tra preference `system`. Khi tắt, không gửi FCM và không hiện Web toast; vẫn lưu inbox và phát Socket sync theo P7-D82.
- Cập nhật Web notification types, event guard, danh sách preference, nhãn category và icon/fallback để nhận `system`.
- Giữ nguyên hành vi `invoice` và `issue` hiện có.

## Acceptance

- GET/PUT preference đọc/ghi được `system`, mặc định bật khi chưa có giá trị lưu.
- `notification.requested` type `system` được lưu và phát Socket; FCM/toast tuân theo preference.
- Invoice/issue notification cũ vẫn qua validation và giữ nguyên delivery.

## Ngoài phạm vi

- UI preference Android, tạo IssueReport hoặc đổi cách điều khiển preference chat.

## Checklist review

- [ ] Community và Web dùng chung contract `system`.
- [ ] Category hiện có và semantics P7-D82 không đổi.
- [ ] PM review trước khi merge.
