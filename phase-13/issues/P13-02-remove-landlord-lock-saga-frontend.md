# P13-02 — FE: Gỡ giao diện tạm ngưng hợp đồng do khóa landlord

**Trạng thái:** 🟡 Open
**Người phụ trách (đề xuất):** `ThaiBao11125`
**Người review:** PM/leader
**Ước lượng:** 1 point
**Phụ thuộc:** P13-01
**Repo / branch:** `fe` · `feature/p13-02-remove-landlord-lock-saga-ui`

> **Đọc trước khi code:** [`decisions.md`](../decisions.md) (P13-D101), `AGENTS.md` và skill `fe-feature-workflow` của repo `fe`.

## Mục tiêu

Web không còn trạng thái "Tạm ngưng", không còn màn/hộp thoại chọn khôi phục hoặc chấm dứt hợp đồng sau khi landlord được mở khóa.

## Phạm vi

| Hạng mục | Vị trí tham khảo |
|---|---|
| Giá trị `suspended` trong enum, constant, màu badge, filter | `fe/src/features/contracts/enums/contract-status.enum.ts`, `constants/contract.constants.ts` |
| Màn/hộp thoại chọn khôi phục/chấm dứt (P11-13), API client gọi `lock-cycles/.../decision`, xử lý 4 mã lỗi | `fe/src/features/contracts/` |
| Mục registry thông báo tạm ngưng / cần quyết định / khôi phục / chấm dứt do khóa | `fe/src/features/notifications/utils/notification-registry.ts` |
| Key i18n không còn dùng | `fe/src/i18n/locales/{vi,en}/contracts.json`, `notifications.json` |

Bản ghi thông báo cũ thiếu mục registry vẫn hiển thị `title`/`body` như server gửi (P12-D96), nên không cần giữ lại các mục đã gỡ.

## Acceptance

- [ ] Không còn chuỗi "Tạm ngưng" hoặc nút "Khôi phục / Chấm dứt do khóa" ở danh sách và chi tiết hợp đồng.
- [ ] Không còn request nào tới `lock-cycles/.../decision`.
- [ ] Trang `/notifications` vẫn mở được với các thông báo cũ liên quan khóa landlord.

## Definition of Done

- [ ] `npm run build`, `npm run lint`, `npm run i18n:check` pass; không viết file test.
- [ ] PR vào `main`, ≥ 1 reviewer.
