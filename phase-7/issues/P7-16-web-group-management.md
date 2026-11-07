# P7-16 — Quản lý nhóm chat trên Web

**Assignee:** `ThaiBao11125` · **Iteration:** Chưa gán · **Ước lượng:** 5 points
**Repo:** `fe` · **Phụ thuộc:** P7-09–12 Community group APIs, CB-07 Media · **Trạng thái:** 🟡 In progress

## Context agent

Đọc `fe/AGENTS.md` và các skill bắt buộc. Dùng API hiện có của Community; không dựng lại business rule ở FE. Nguồn chuẩn: [Community design](../../phase-6/discovery/community-service-design.md), P7-D78/P7-D79 và các issue [P7-09](P7-09-list-add-members.md)–[P7-12](P7-12-update-group-metadata.md).

## Quy tắc đã chốt

- Chỉ active admin thay đổi tên/ảnh nhóm, thêm/xóa thành viên, đổi role `admin` ↔ `member` hoặc chỉ định thêm admin.
- Active member được rời nhóm; quyền/history khi rời theo Community API. Nếu admin cuối rời, backend tự chuyển admin theo quy tắc đã chốt.
- Thay đổi nhóm có system message; không gửi FCM cho thay đổi nhóm.
- Không hỗ trợ sửa/xóa tin nhắn; việc quản lý nhóm không xóa history.
- Ảnh nhóm dùng upload private `ownerType=conversation`, `purpose=conversation_avatar`, sau đó PATCH metadata bằng `avatarMediaId`.

## Acceptance

- [ ] Group header có lối vào quản lý; direct conversation không có.
- [ ] Thành viên thường chỉ xem danh sách và có thể rời nhóm; không thấy thao tác admin.
- [ ] Admin đổi tên/ảnh, thêm user directory, kick member, đổi role và rời nhóm qua API hiện có.
- [ ] Không cho UI hạ admin cuối; backend vẫn là nguồn kiểm tra cuối cùng và lỗi được hiển thị rõ.
- [ ] Sau mutation, detail/list/member/history được đồng bộ; system message mới hiển thị.
- [ ] Có xác nhận trước kick/rời nhóm, loading/error/empty states và i18n Việt/Anh.
- [ ] Ảnh dùng media API hiện hành; không gửi binary qua Community.
- [ ] `npm run build`, `npm run lint`, `npm run i18n:check` pass.

## Không làm

Không thêm API/backend rules, chat building/contract management, system-message FCM, sửa/xóa message hoặc bot reminder.
