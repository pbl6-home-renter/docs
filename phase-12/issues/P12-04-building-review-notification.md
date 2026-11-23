# P12-04 — Báo landlord khi admin duyệt hoặc từ chối tòa

**Trạng thái:** 🟡 Open
**Người phụ trách (đề xuất):** `baoduong17`
**Người review:** `leminhkhai345`, FE Lead
**Ước lượng:** 2 points
**Phụ thuộc:** P12-01
**Repo / branch:** `Tenancy-Service`, `fe`, `api-docs` · `feature/p12-04-building-review-notification`

> **Đọc trước khi code:** [`community-service/docs/notifications.md`](https://github.com/pbl6-home-renter/community-service/blob/main/docs/notifications.md) (quy ước payload, checklist), `AGENTS.md` và skill trong `.agents/skills/` của từng repo. Nguồn mâu thuẫn: `decisions.md` > `docs/notifications.md` > issue.

## Mục tiêu

Landlord nhận thông báo ngay khi tòa được duyệt hoặc bị từ chối, bấm vào mở trang chi tiết tòa.

## Quyết định áp dụng

- `P12-D95`, `P12-D97`.

## Thông báo cần gửi

| `messageKey` | Khi nào gửi | Người nhận | `data` (ngoài `messageKey`) | Trang mở trên Web |
|---|---|---|---|---|
| `building.approved` | Admin duyệt tòa | Landlord của tòa | `buildingId`, `buildingName`, `note` | `/buildings/{id}` |
| `building.rejected` | Admin từ chối tòa | Landlord của tòa | `buildingId`, `buildingName`, `note` (lý do) | `/buildings/{id}` |

## Tham chiếu code

- `Tenancy-Service/src/modules/building/application/commands/building-approve/`, `building-reject/`: thêm event `notification.requested` vào cùng transaction đang ghi outbox `building.approved/rejected`.
- Mẫu payload: `Tenancy-Service/src/modules/invoice/domain/events/invoice-notification-requested.event.ts`.
- `api-docs/src/paths/buildings/buildings-buildingId-approve.yaml`, `...-reject.yaml`: bỏ câu "chưa gửi notification cho landlord", cập nhật sequence diagram, `npm run bundle`.

## Các bước

1. Tenancy: event + unit test cho approve và reject.
2. fe: 2 mục registry (route `ROUTES.LANDLORD.BUILDING_DETAIL`) + i18n; khi nhận thông báo loại này thì invalidate query danh sách/chi tiết tòa.
3. api-docs: sửa mô tả, bundle.

## Definition of Done

- [ ] Service nguồn: unit test payload (có `messageKey`, đủ tham số, `title`/`body` lấy từ class constant, đúng người nhận, không gửi cho người thao tác).
- [ ] Event ghi outbox trong cùng transaction với thay đổi nghiệp vụ; `npm test`, `npm run build`, `npm run lint` pass.
- [ ] fe: mục registry + key i18n `vi`/`en` trong `notifications.json`; `npm run build`, `npm run lint`, `npm run i18n:check` pass; không viết file test.
- [ ] Cập nhật bảng mục 5 trong `community-service/docs/notifications.md` (đổi trạng thái thành "Đã có").
- [ ] Chạy tay, đính kèm ảnh vào PR: thao tác → có bản ghi trong bảng `notifications` (community) → toast hiện trên web → bấm mở đúng trang → F5 lại `/notifications` vẫn hiển thị đúng cả `vi` và `en`.
- [ ] Mỗi repo một PR vào `main`, ghi chung issue này, ≥ 1 reviewer.
