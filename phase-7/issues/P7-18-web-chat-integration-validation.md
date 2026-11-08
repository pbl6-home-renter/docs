# P7-18 — Kiểm chứng tích hợp Web Chat qua Gateway

**Assignee:** `ThaiBao11125` · **Iteration:** Chưa gán · **Ước lượng:** 2 points
**Repo:** `fe`, `api-gateway`, `community-service` · **Phụ thuộc:** P7-15–17 · **Trạng thái:** 🟢 Done

## Acceptance

- [ ] Hai user Landlord/Tenant thực hiện direct/group chat qua Gateway; quyền membership/admin được kiểm tra.
- [ ] Socket reconnect và user-room event cập nhật cache/list/inbox; không trùng message hoặc unread.
- [ ] Mark-read đồng bộ giữa hai tab/device; push preference không xóa inbox.
- [ ] Deep link notification mở route nội bộ phù hợp.
- [ ] Kiểm tra desktop chính và responsive mobile browser; ghi rõ schema/migration/runtime prereqs.
- [ ] Ghi kết quả và lỗi quan sát được; không coi build pass là end-to-end pass.
