# P13-10 — FE: Nhắc landlord cập nhật dữ liệu sau khi được mở khóa

**Trạng thái:** 🟡 Open
**Người phụ trách (đề xuất):** `ThaiBao11125`
**Người review:** PM/leader
**Ước lượng:** 1 point
**Phụ thuộc:** P13-07
**Repo / branch:** `fe` · `feature/p13-10-post-unlock-banner`

> **Đọc trước khi code:** [`decisions.md`](../decisions.md) (P13-D101).

## Mục tiêu

Trong lúc bị khóa, đời thật vẫn chạy (tenant trả tiền mặt, hợp đồng hết hạn hoặc gia hạn, có người chuyển đi). Sau khi được mở khóa, landlord được nhắc kiểm tra lại dữ liệu bằng các thao tác sẵn có. App không chặn và không tự sửa gì.

## Phạm vi

- Điều kiện hiển thị: landlord có thông báo **mở khóa tài khoản** (P12-02) **chưa đọc**. Không cần API mới.
- Banner trên dashboard landlord, nội dung gợi ý: "Tài khoản của bạn vừa được mở khóa. Hãy kiểm tra lại hóa đơn, hợp đồng và tình trạng phòng."
- Hai lối tắt:
  - **Hóa đơn chưa thu** → danh sách hóa đơn lọc `status=issued` (sau P13-07, hóa đơn đã thu là `paid`).
  - **Hợp đồng đang hiệu lực** → danh sách hợp đồng lọc `status=active`.
- Nút "Đã xem": đánh dấu thông báo mở khóa là đã đọc → banner biến mất.

## Acceptance

- [ ] Admin mở khóa landlord → landlord đăng nhập thấy banner trên dashboard.
- [ ] Hai lối tắt mở đúng danh sách đã lọc.
- [ ] Bấm "Đã xem" hoặc đọc thông báo mở khóa ở `/notifications` → banner không hiện lại.
- [ ] Tenant được mở khóa không thấy banner này.

## Definition of Done

- [ ] `npm run build`, `npm run lint`, `npm run i18n:check` pass; không viết file test.
- [ ] Ảnh chụp trong PR.
