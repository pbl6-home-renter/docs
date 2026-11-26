# P12-11 — Làm rõ hành vi tài khoản bị khóa (tenant và landlord)

**Trạng thái:** 🟡 Open
**Người phụ trách (đề xuất):** PM
**Người review:** `leminhkhai345` (owner luồng khóa landlord), BE Lead, FE Lead
**Ước lượng:** 1 point
**Phụ thuộc:** —
**Liên quan:** P4-12 (API khóa/mở khóa), P9-06/P9-07 (saga khóa landlord), P11-13 (FE chọn khôi phục/chấm dứt), P12-02 (thông báo khóa), P12-09/P12-10 (quyền chỉ đọc theo P12-D100)
**Đầu ra:** Issue này là bản đặc tả hành vi; kèm quyết định cho các điểm ở mục 7.

## Mục tiêu

Nhóm chưa thống nhất "bị khóa" nghĩa là gì: user còn làm được gì, hợp đồng và hóa đơn thay đổi ra sao, và tenant khác landlord ở điểm nào. Issue này ghi lại **hành vi thực tế của code tại commit hiện tại** (Identity, Tenancy, community, fe) thành các bảng, chỉ ra chỗ code lệch tài liệu, và liệt kê các điểm PM cần chốt. P12-09, P12-10 và P11-13 dùng issue này làm nguồn tham chiếu.

> Mọi hành vi dưới đây được đọc trực tiếp từ code. Khi code thay đổi (ví dụ sau khi P12-09/P12-10 merge), cập nhật cột tương ứng trong issue này.

## 1. Khóa và mở khóa (Identity)

| Hạng mục | Hành vi |
|---|---|
| Ai khóa/mở khóa | Chỉ admin: `POST /users/{id}/lock` (bắt buộc `lockReason`), `POST /users/{id}/unlock` |
| Admin tự khóa mình | Bị chặn (`UserLockCannotSelfException`) |
| Khóa user chưa xác minh email | Bị chặn: 409 `EMAIL_NOT_VERIFIED` |
| Khóa user đang bị khóa / mở khóa user không bị khóa | Bị chặn (`UserLockAlreadyLocked` / `UserUnlockNotLocked`) |
| Dữ liệu ghi khi khóa | `status=locked`, `lockReason`, `lockedAt`, một bản ghi `user_lock_periods`. Audit `user.locked` kèm `lockReason` |
| Dữ liệu ghi khi mở khóa | `status=active`, xóa `lockReason`/`lockedAt`, đóng lock period. Audit `user.unlocked` |
| Event (outbox, cùng transaction) | `user.locked` / `user.unlocked` gửi Tenancy (`tenancy.identity-lifecycle`). `notification.requested` gửi cho chính người bị khóa/mở khóa (P12-02) |

Code: `Identity-Service/src/modules/users/domain/entities/user.ts`, `application/commands/user-lock/`, `user-unlock/`.

## 2. Người bị khóa còn làm được gì (chung cho tenant và landlord)

Cơ chế: `ActiveUserGuard` (trong `src/shared`, giống nhau ở mọi service) đọc claim `status` của JWT. Nếu `status=locked` và route không có `@AllowLocked()` thì trả **403 `ACCOUNT_LOCKED`**.

| Hành động | Hiện tại | Sau P12-09/P12-10 (theo P12-D99, P12-D100) |
|---|---|---|
| Đăng nhập | ✅ Được (login chỉ chặn `pending_verification`; token mang `status=locked`) | ✅ Giữ nguyên |
| Refresh token | ✅ Được (khóa **không** thu hồi phiên) | ✅ Giữ nguyên |
| Đăng xuất | ✅ Được (`@AllowLocked`) | ✅ Giữ nguyên |
| `GET /me` | ✅ Được (`@AllowLocked` ở cấp class `UserController`) | ✅ Được |
| `PATCH /me`, đổi mật khẩu | ✅ **Vẫn được**, vì `@AllowLocked` ở cấp class | ❌ Chặn (chỉ `GET /me` được mở) |
| Xem tòa nhà công khai (`GET /buildings`, `GET /buildings/:id`) | ✅ Được | ✅ Được |
| Thông báo (`/notifications`, đọc, đánh dấu đã đọc, socket) | ❌ 403 | ✅ Được theo P12-D99 (chỉ thông báo, không chat) |
| Phòng/hợp đồng/hóa đơn của mình (chỉ đọc) | ❌ 403 | ✅ Được theo P12-D100 |
| Thanh toán hóa đơn | — Chưa có endpoint thanh toán trong Tenancy | ✅ Theo P12-D100 (cần xác định endpoint, xem mục 7) |
| Mọi thao tác ghi khác (hợp đồng, phòng, hóa đơn, chỉ số, chat, roommate, match request, issue…) | ❌ 403 | ❌ 403 |
| Web (fe) | Mọi route bảo vệ chuyển sang `/403` khi `user.status === locked` (`protected-route.tsx`) | Allowlist route chỉ đọc + banner (P12-10) |

### Độ trễ hiệu lực

Khóa dựa vào claim trong access token (TTL **15 phút**, `token.service.ts`).

| Tình huống | Hành vi |
|---|---|
| Vừa bị khóa, access token cũ còn `status=active` | Vẫn dùng đầy đủ quyền đến khi token hết hạn (tối đa 15 phút) |
| Sau lần refresh/login tiếp theo | Token mang `locked`, bị chặn |
| Vừa được mở khóa, token cũ còn `locked` | Vẫn 403 cho đến khi refresh/login lại |

## 3. Tenant bị khóa

Tenancy **không thay đổi hợp đồng** khi tenant bị khóa (P9-06).

| Hạng mục | Ảnh hưởng |
|---|---|
| Hợp đồng đang ở (đại diện hoặc thành viên) | Không đổi, vẫn `active`. Landlord quản lý bình thường |
| Hóa đơn | Vẫn sinh và phát hành cho phòng. Tenant không xem được trên app cho tới khi P12-09/P12-10 xong |
| Projection `tenant_users` (Tenancy) | Tenant bị xóa khỏi projection khi nhận `user.locked` |
| Landlord tạo hợp đồng / thêm thành viên bằng SĐT của tenant đang bị khóa | Vẫn tạo được nhưng **không tự liên kết** (`tenantId = null`) |
| Khi mở khóa | Tenant được thêm lại vào projection; hệ thống tự liên kết các hợp đồng/thành viên chưa liên kết có cùng SĐT |
| Chat hợp đồng | Không bị kick khỏi conversation; không gọi được API chat. Người khác chat bình thường |
| Thông báo | Chỉ tenant nhận notice khóa/mở khóa. Landlord không được báo |

Code: `Tenancy-Service/src/modules/contract/presentation/messaging/identity-lifecycle.subscriber.ts` (`onUserLocked`, `onUserChanged`).

## 4. Landlord bị khóa (saga P9-06/P9-07)

### 4.1. Khi Tenancy nhận `user.locked`

| Hạng mục | Ảnh hưởng |
|---|---|
| Hợp đồng `active` của landlord | Tất cả chuyển sang **`suspended`** |
| Hợp đồng `draft`, `terminated`… | Không đổi |
| Lock cycle | Tạo mới, state `pending`, `graceDeadline = lockedAt + 7 ngày` (`LANDLORD_LOCK_GRACE_PERIOD_MS`) |
| Thông báo | Landlord và mọi tenant đã liên kết (đại diện + thành viên active) nhận `CONTRACT_SUSPENDED`; mỗi người chỉ thấy hợp đồng của mình |
| Phòng | Vẫn `occupied`; không xóa được (checker coi `suspended` là đang có hợp đồng) |
| Hóa đơn | Không sinh hóa đơn mới cho hợp đồng `suspended` (`isActiveDuring` yêu cầu `ACTIVE`). Hóa đơn đã phát hành giữ nguyên |
| Thêm/rời thành viên | Bị chặn (yêu cầu hợp đồng `ACTIVE`) |
| Tenant xem hợp đồng | Vẫn thấy (truy vấn tenant tính cả `suspended`). Room hub chỉ lấy `ACTIVE` nên phòng **không hiện ở room hub** |
| Tòa nhà/phòng công khai | Không bị ẩn khỏi tìm kiếm |

### 4.2. Các nhánh xử lý sau khi khóa

Scheduler trong Tenancy quét lock cycle đến hạn **mỗi 60 giây** và hỏi Identity về lock period qua internal HTTP.

| Tình huống | Tenancy xử lý | Kết quả hợp đồng | Ai được báo |
|---|---|---|---|
| Mở khóa **trước hạn**, còn hợp đồng `suspended` | Cycle sang `decision_pending`, dừng auto-terminate | Giữ `suspended` **vô thời hạn** đến khi landlord chọn | Landlord (`decision_required`) |
| Mở khóa trước hạn, không còn hợp đồng `suspended` | Cycle sang `completed` | — | — |
| Landlord chọn **Khôi phục** | Kiểm tra phòng còn `occupied` và không có hợp đồng khác chiếm phòng | `active` | Landlord + tenant (`restore`) |
| Khôi phục khi phòng không còn hợp lệ | Lỗi `ContractRestoreRoomUnavailable` | Giữ `suspended` | — |
| Landlord chọn **Chấm dứt** | Lưu `lockTerminationCycleId` | `terminated`, `handoverRequired=true` | Landlord + tenant (`terminate`) |
| **Hết 7 ngày, vẫn bị khóa** | Tự chấm dứt mọi hợp đồng `suspended` của cycle | `terminated` (origin `grace_expired`) | Landlord + tenant (`terminate`) |
| Mở khóa **sau** hạn | Không có bước chọn | Giữ `terminated` | Chỉ notice mở khóa tài khoản |
| Bị khóa lại khi cycle cũ chưa xong | Cycle cũ `superseded`; hợp đồng còn `suspended` chuyển sang cycle mới; hạn 7 ngày tính lại | Giữ `suspended` | Như lúc khóa |
| Identity không phản hồi / dữ liệu không khớp | Scheduler hoãn, log reconcile, thử lại tick sau. API quyết định trả lỗi peer unavailable | Không đổi | — |
| Event hoặc lựa chọn bị gửi trùng | Inbox dedup; chọn lại cùng hành động trả kết quả cũ | Không đổi | Không gửi trùng |

API quyết định: `PUT /contracts/{contractId}/lock-cycles/{lockCycleId}/decision`, body `{ action: "restore" | "terminate" }`.

| Mã lỗi | Khi nào |
|---|---|
| `CONTRACT_LOCK_DECISION_CONFLICT` | Đã chọn hành động khác trước đó |
| `LANDLORD_LOCK_CYCLE_STALE` | Cycle đã bị thay bằng cycle mới, hoặc landlord bị khóa lại |
| `LANDLORD_LOCK_CYCLE_NOT_AWAITING_DECISION` | Cycle không còn `decision_pending` |
| `ContractLockDecisionInvalid` | Hợp đồng không thuộc cycle hoặc không còn `suspended` |

### 4.3. Sau khi bị chấm dứt do khóa

| Hạng mục | Hành vi |
|---|---|
| Phòng | Vẫn `occupied` đến khi landlord hoàn tất trả phòng (`contract-checkout-complete`) |
| Checkout | Không kiểm tra quyết toán kỳ (khác checkout thường). Khi xong, thành viên rời và phòng được giải phóng |
| Danh sách tenant của landlord | Vẫn tính là "đang ở" cho đến khi có `handoverCompletedOn` |
| Tiền cọc | Không hoàn, không hứa hoàn (ngoài phạm vi Phase 9) |

Code: `Tenancy-Service/src/modules/contract/` — `domain/entities/landlord-lock-cycle.entity.ts`, `application/commands/landlord-lock-grace-scan/`, `application/commands/contract-lock-decision/`, `infrastructure/scheduler/landlord-lock-grace.scheduler.ts`.

## 5. So sánh nhanh

| | Tenant bị khóa | Landlord bị khóa |
|---|---|---|
| Đăng nhập / `me` / đăng xuất | Được | Được |
| API nghiệp vụ | 403 (trừ phần mở theo P12-D99/D100) | 403 (trừ phần mở theo P12-D99/D100) |
| Hợp đồng | Không đổi | `suspended` → khôi phục hoặc chấm dứt |
| Hóa đơn mới | Vẫn sinh | Dừng |
| Người khác bị ảnh hưởng | Không (chỉ không tự liên kết hợp đồng mới) | Mọi tenant trong hợp đồng active |
| Thông báo cho người khác | Không | Có (suspend, restore, terminate) |
| Hạn chót | Không | 7 ngày, hết hạn tự chấm dứt |
| Việc cần làm sau mở khóa | Không | Chọn khôi phục/chấm dứt từng hợp đồng (P11-13); nếu chấm dứt thì làm trả phòng |

## 6. Code lệch tài liệu

| # | Tài liệu nói | Code đang làm | Đề xuất |
|---|---|---|---|
| 1 | P4-12: khóa thì thu hồi refresh token, không đăng nhập được | Cố ý giữ phiên, vẫn cho login (`AuthRevokeTokensOnUserEventsHandler` bỏ qua `UserLockedEvent`) | Giữ hành vi code (P12-D100 đã dựa vào việc vẫn đăng nhập được); ghi chú vào P4-12 là đã thay thế |
| 2 | P12-D100: chặn `PATCH /me`, đổi mật khẩu | `@AllowLocked` ở cấp class nên hiện đang cho phép | Đã nằm trong P12-09 |
| 3 | P12-D100: cho phép thanh toán hóa đơn | Tenancy chưa có endpoint thanh toán | Xác định endpoint hoặc tách khỏi P12-09/P12-10 (mục 7) |

## 7. Các điểm PM cần chốt

- [ ] **Thanh toán:** dùng endpoint nào (payment service VNPAY chưa có trong code)? Nếu chưa có, P12-10 chỉ hiển thị thông tin chuyển khoản/VietQR.
- [ ] **Khoảng trễ 15 phút** sau khi khóa: chấp nhận (ghi rõ trong tài liệu) hay cần cơ chế thu hồi tức thì?
- [ ] **Tòa/phòng của landlord bị khóa** có ẩn khỏi tìm kiếm công khai không?
- [ ] **Room hub của tenant** khi hợp đồng `suspended`: có hiển thị phòng kèm trạng thái "tạm ngưng" không (hiện đang biến mất)?
- [ ] **Tenant bị khóa:** có báo landlord không? Hóa đơn vẫn sinh như hiện tại có đúng ý không?
- [ ] **Hợp đồng kẹt `suspended`:** khi landlord mở khóa trước hạn nhưng không chọn, hợp đồng treo vô thời hạn. Cần hạn chót cho bước chọn không, hay chỉ cần P11-13 xong là đủ?
- [ ] **Landlord bị khóa xem dữ liệu chỉ đọc (P12-D100):** landlord có được xem danh sách hợp đồng `suspended` và hóa đơn của mình không, hay chỉ tenant?

## Definition of Done

- [ ] Leader luồng khóa landlord và BE Lead xác nhận các bảng ở mục 1–5 khớp với code.
- [ ] Mỗi điểm ở mục 7 có quyết định, ghi thành một mục mới trong `phase-12/decisions.md`. Điểm nào cần code thì tách task riêng.
- [ ] Cập nhật P4-12 (ghi chú hành vi phiên đã thay đổi) và tham chiếu issue này từ P12-09, P12-10, P11-13.
- [ ] Cập nhật trạng thái trong `issues/README.md`.

## Ngoài phạm vi

- Sửa code. Issue này chỉ đặc tả và chốt quyết định; thay đổi code nằm trong P12-09, P12-10, P11-13 hoặc task mới tách ra.
- Hoàn cọc khi chấm dứt hợp đồng do khóa.
