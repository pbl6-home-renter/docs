# P12-05 — Báo admin khi có tòa mới chờ duyệt

**Trạng thái:** 🟡 Open
**Người phụ trách (đề xuất):** `huynhtiennhat0403` (Identity) + `baoduong17` (Tenancy)
**Người review:** BE Lead, FE Lead
**Ước lượng:** 3 points
**Phụ thuộc:** P12-01, P12-04
**Repo / branch:** `Identity-Service`, `Tenancy-Service`, `fe` · `feature/p12-05-building-pending-review-notification`

> **Đọc trước khi code:** [`community-service/docs/notifications.md`](https://github.com/pbl6-home-renter/community-service/blob/main/docs/notifications.md) (quy ước payload, checklist), `AGENTS.md` và skill trong `.agents/skills/` của từng repo. Nguồn mâu thuẫn: `decisions.md` > `docs/notifications.md` > issue.

## Mục tiêu

Admin nhận thông báo khi landlord gửi tòa mới, bấm vào mở trang duyệt tòa.

## Quyết định áp dụng

- `P12-D95`, `P12-D97`.

## Thông báo cần gửi

| `messageKey` | Khi nào gửi | Người nhận | `data` (ngoài `messageKey`) | Trang mở trên Web |
|---|---|---|---|---|
| `building.pending_review` | Landlord tạo tòa (trạng thái chờ duyệt) | Tất cả admin đang hoạt động | `buildingId`, `buildingName`, `landlordName` | `/admin/buildings/{id}` |

## Tham chiếu code

- Identity: thêm endpoint nội bộ (`@InternalOnly()`, dưới `internal/...`) trả danh sách id admin `active`. Mẫu: `Identity-Service/src/modules/users/presentation/http/controllers/user-internal.controller.ts`.
- Tenancy: `building-create` gọi Identity qua `INTERNAL_HTTP_DI_TOKEN.CLIENT` (GET, không retry), kiểu response redeclare tại Tenancy.

## Các bước

1. Identity: endpoint nội bộ + unit test use case.
2. Tenancy: lấy danh sách admin **trước** transaction tạo tòa; gọi thất bại thì vẫn tạo tòa, chỉ log warning và không gửi thông báo.
3. fe: mục registry (route `ROUTES.ADMIN.BUILDING_DETAIL`) + i18n.

## Blocker

- Cần BE Lead xác nhận cho phép Tenancy gọi Identity lúc tạo tòa (thêm phụ thuộc runtime).

## Definition of Done

- [ ] Service nguồn: unit test payload (có `messageKey`, đủ tham số, `title`/`body` lấy từ class constant, đúng người nhận, không gửi cho người thao tác).
- [ ] Event ghi outbox trong cùng transaction với thay đổi nghiệp vụ; `npm test`, `npm run build`, `npm run lint` pass.
- [ ] fe: mục registry + key i18n `vi`/`en` trong `notifications.json`; `npm run build`, `npm run lint`, `npm run i18n:check` pass; không viết file test.
- [ ] Cập nhật bảng mục 5 trong `community-service/docs/notifications.md` (đổi trạng thái thành "Đã có").
- [ ] Chạy tay, đính kèm ảnh vào PR: thao tác → có bản ghi trong bảng `notifications` (community) → toast hiện trên web → bấm mở đúng trang → F5 lại `/notifications` vẫn hiển thị đúng cả `vi` và `en`.
- [ ] Mỗi repo một PR vào `main`, ghi chung issue này, ≥ 1 reviewer.
