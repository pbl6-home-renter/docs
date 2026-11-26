# P13-11 — Báo cáo vi phạm và khiếu nại khóa tài khoản

**Trạng thái:** ⏸ Deferred (chờ PM duyệt phạm vi)
**Người phụ trách (đề xuất):** PM/leader
**Ước lượng:** chưa ước lượng (dự kiến lớn hơn 3 points, cần tách nhỏ khi duyệt)
**Phụ thuộc:** —
**Repo dự kiến:** `Identity-Service`, `community-service`, `fe`, `mobile`, `api-docs`

> Ghi lại để không mất ý tưởng. **Không triển khai** cho tới khi PM duyệt và có quyết định mới trong `decisions.md` (P13-D107).

## Vì sao cần

- Admin cần căn cứ trước khi khóa: hiện chỉ có ô lý do tự do, không có nơi người dùng báo cáo vi phạm.
- Người bị khóa nhầm chưa có cách được mở lại trong app.

## Phạm vi đề xuất (theo tài liệu nghiệp vụ gốc)

### Báo cáo vi phạm
- Người dùng báo cáo một tài khoản khác kèm loại vi phạm (6 loại ở P13-09) và mô tả.
- Hàng chờ báo cáo cho admin; admin xem xét rồi mới khóa.

### Khiếu nại
- Nút "Gửi khiếu nại" trên màn tài khoản bị khóa. Form: lý do khóa (chỉ xem), nội dung giải trình (bắt buộc), file đính kèm (không bắt buộc), thông tin liên hệ.
- Mỗi người chỉ có một khiếu nại đang chờ. Bị từ chối thì gửi lại sau một khoảng thời gian (ví dụ 7 ngày).
- Hàng chờ khiếu nại riêng cho admin. Chấp nhận → mở khóa. Từ chối → bắt buộc ghi lý do.
- Kết quả gửi qua thông báo trong app và email (community đã có module email).

## Câu hỏi cần chốt khi duyệt

- [ ] Có làm báo cáo vi phạm, hay chỉ làm khiếu nại?
- [ ] Thời gian xử lý mục tiêu hiển thị cho người khiếu nại?
- [ ] Khoảng chờ gửi lại sau khi bị từ chối?
- [ ] Module đặt ở Identity hay community? File đính kèm dùng module media nào?
- [ ] Mobile có làm trong cùng đợt không?

## Trong lúc chờ

Màn tài khoản bị khóa hiển thị lý do khóa; người dùng liên hệ admin ngoài app.
