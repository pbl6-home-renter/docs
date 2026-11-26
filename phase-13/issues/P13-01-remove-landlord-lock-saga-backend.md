# P13-01 — BE: Gỡ saga tạm ngưng hợp đồng khi khóa landlord

**Trạng thái:** 🟡 Open
**Người phụ trách (đề xuất):** `leminhkhai345`
**Người review:** `baoduong17`
**Ước lượng:** 3 points
**Phụ thuộc:** —
**Repo / branch:** `Tenancy-Service`, `api-docs` · `feature/p13-01-remove-landlord-lock-saga`

> **Đọc trước khi code:** [`decisions.md`](../decisions.md) (P13-D101), `AGENTS.md` và skill trong `.agents/skills/` của repo. Nguồn mâu thuẫn: `decisions.md` > `api-docs` > issue.

## Mục tiêu

Khi admin khóa landlord, mọi hợp đồng của landlord **giữ nguyên trạng thái**. Tenant vẫn thấy phòng trong room hub, hóa đơn vẫn sinh được sau khi landlord mở khóa. Toàn bộ cơ chế `suspended` / lock cycle / hạn 7 ngày bị gỡ.

## Hiện trạng

- `identity-lifecycle.subscriber.ts` (`onUserLocked`): chuyển hợp đồng `active` của landlord sang `suspended`, tạo lock cycle (`graceDeadline = lockedAt + 7 ngày`), gửi thông báo `CONTRACT_SUSPENDED`.
- `landlord-lock-grace.scheduler.ts` quét mỗi 60 giây; hết hạn thì tự `terminated`.
- API `PUT /contracts/{contractId}/lock-cycles/{lockCycleId}/decision` cho landlord chọn khôi phục/chấm dứt, kèm 4 mã lỗi.
- Chi tiết: [P12-11 mục 4](../../phase-12/issues/P12-11-locked-account-behavior-spec.md).

## Phạm vi

### Gỡ bỏ

| Thành phần | Đường dẫn (`Tenancy-Service/src/modules/contract/`) |
|---|---|
| Xử lý landlord trong `onUserLocked` / `onUserUnlocked` | `presentation/messaging/identity-lifecycle.subscriber.ts` — **giữ** phần xử lý tenant (projection `tenant_users`, tự liên kết khi mở khóa) |
| Entity, repository, mapper lock cycle | `domain/entities/landlord-lock-cycle.entity.ts` và phần infrastructure tương ứng |
| Lệnh quét hạn + scheduler | `application/commands/landlord-lock-grace-scan/`, `infrastructure/scheduler/landlord-lock-grace.scheduler.ts` |
| Lệnh + endpoint quyết định | `application/commands/contract-lock-decision/` và controller route `lock-cycles/.../decision` |
| Mã lỗi | `CONTRACT_LOCK_DECISION_CONFLICT`, `LANDLORD_LOCK_CYCLE_STALE`, `LANDLORD_LOCK_CYCLE_NOT_AWAITING_DECISION`, `ContractLockDecisionInvalid` |
| Thông báo do khóa | Tạm ngưng / cần quyết định / khôi phục / chấm dứt do khóa (phần tương ứng của P12-03) |
| Trường liên quan trên hợp đồng | `lockTerminationCycleId` và origin `grace_expired` nếu không còn nơi dùng |
| Hằng số | `LANDLORD_LOCK_GRACE_PERIOD_MS` |

### Migration

1. `UPDATE contracts SET status = 'active' WHERE status = 'suspended'`.
2. Drop bảng lock cycle và các cột chỉ phục vụ lock cycle.
3. **Không** đụng tới hợp đồng đã `terminated` trước đây (P13-D101).
4. Bỏ giá trị `SUSPENDED` khỏi `ContractStatus` sau khi không còn dòng nào dùng.

### api-docs

- Xóa path `lock-cycles/{lockCycleId}/decision`, schema và 4 mã lỗi.
- Bỏ `suspended` khỏi enum trạng thái hợp đồng; sửa mô tả hành vi khóa landlord ở các endpoint hợp đồng.
- `npm run lint` + `npm run bundle`.

## Các bước

1. Gỡ xử lý landlord trong subscriber; viết unit test: landlord bị khóa → hợp đồng không đổi; tenant bị khóa → hành vi cũ giữ nguyên.
2. Gỡ scheduler, lệnh, endpoint, mã lỗi, thông báo; đăng ký lại module cho gọn.
3. Sinh migration bằng `npm run migration:generate`, thêm câu `UPDATE` ở trên.
4. Cập nhật api-docs, bundle.

## Acceptance

- [ ] Admin khóa landlord có hợp đồng `active` → hợp đồng vẫn `active`; không có thông báo hợp đồng nào được gửi.
- [ ] Tenant của landlord đó vẫn thấy phòng ở `GET /me/room-hub`.
- [ ] Admin mở khóa → không có bước chọn khôi phục/chấm dứt; landlord thao tác hợp đồng, hóa đơn bình thường.
- [ ] Gọi API decision cũ → `404`.
- [ ] Sau migration không còn hợp đồng `suspended`; `migration:run` và `migration:revert` chạy được.
- [ ] Tenant bị khóa / mở khóa: projection và tự liên kết hợp đồng vẫn đúng như trước.

## Definition of Done

- [ ] `npm test`, `npm run build`, `npm run lint` pass; ba lệnh grep kiểm tra dependency rule không in gì.
- [ ] api-docs đã bundle, PR riêng, link vào issue.
- [ ] Mỗi repo một PR vào `main`, ≥ 1 reviewer.

## Ngoài phạm vi

- Gỡ UI phía Web: [P13-02](P13-02-remove-landlord-lock-saga-frontend.md).
- Khôi phục hợp đồng đã bị chấm dứt trước đây.
