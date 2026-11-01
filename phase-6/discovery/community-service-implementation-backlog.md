# Backlog triển khai Community Service

> **Trạng thái:** Đã được xếp lịch và gán owner trong [Phase 7 task tracker](../../phase-7/issues/README.md).
> **Phạm vi lịch:** Track Phase 7 chạy song song; bắt đầu It5 (02/11–08/11) với CB-01–05. Các task còn lại được xếp theo dependency tới It8.
> **Thiết kế đã duyệt:** [ERD và business/API design](community-service-design.md).
> **API chuẩn:** `api-docs/src/openapi.yaml`; bundle `api-docs/reference/rentify.json`.

## 1. Mục tiêu

Chia Community Service thành các lát triển khai có thể review riêng, theo dependency giữa Community, Tenancy, Identity/Media, Gateway, Web và Android. Backlog này không thay đổi scope hoặc lịch Phase 6. Mã P7-CB, owner và iteration được theo dõi tại Phase 7; các PR triển khai sẽ được tách nhỏ theo template của repo tương ứng.

## 2. Hiện trạng repo đã đối chiếu

| Repo | Hiện trạng liên quan | Ý nghĩa với backlog |
|---|---|---|
| `community-service` | Đã có scaffold NestJS, health, sample module, outbox/inbox hạ tầng; chưa có module chat, notification nghiệp vụ, Socket hoặc PushDevice. Package hiện chưa có Socket.IO/FCM provider. Migration hiện có mới tạo bảng outbox/inbox. | Tiếp tục từ service có sẵn; không scaffold service mới. |
| `Tenancy-Service` | Có outbox và event `building.created`, `contract.created`; payload hiện có `buildingId/landlordId` và `contractId/roomId/landlordId/tenantId`, chưa đủ cho toàn bộ member-sync như thiết kế. Chưa tìm thấy event ContractMember add/kick tương ứng trong module hiện tại. | Cần đối chiếu/gắn thêm producer event vào luồng ContractMember đã có; Community không tự đọc DB Tenancy. |
| `Identity-Service` Media | Có R2 presign/complete, `CHAT_ATTACHMENT`, owner type `message`; resolver cho `MESSAGE`/`ISSUE_REPORT` hiện là `UnavailableOwnerResolver`. | V1 chốt `ownerType=conversation`, `ownerId=conversationId`; cần thêm owner type/policy và resolver gọi Community để xác thực thành viên. |
| `api-gateway` | Service Community đã có trong enum; prefix Community chưa có `/me/push-devices`. Prefix Identity `/me` hiện đang sở hữu đường dẫn này. | Chuyển riêng `/api/v1/me/push-devices` sang Community bằng route cụ thể hơn, giữ nguyên URL client. |
| `infra` | Community đã có block tùy chọn trong internal compose, hiện đang comment. | Chỉ bật khi có image/env và quyết định rollout; không mở cổng trực tiếp ra Internet. |
| `fe` | Có API client và Media upload dùng chung; chưa có feature chat/inbox. | Tái sử dụng upload client khi tương thích; bổ sung feature chat và notification theo API đã duyệt. |
| `mobile` | Android có app tenant và landlord; chưa thấy feature chat/notification hoặc đăng ký FCM trong ứng dụng. | V1 target mobile là Android; không mở rộng iOS trong backlog này. |

## 3. Thứ tự phụ thuộc

```text
Chat core (không chờ domain event publisher)
  Community runtime → conversation/member/message REST → Socket → web/mobile chat
                                                   └── Media owner conversation → gửi ảnh

Tích hợp domain làm sau
  Building/Contract/ContractMember events → contextual chat
  Invoice/Issue events → notification inbox → Socket/FCM → web/mobile
  Resource data → bot reminder theo mẫu, landlord gửi thủ công
```

Contract/building chat phụ thuộc event producer và đồng bộ membership. Direct/group chat không phụ thuộc domain event. Business notification chỉ nhận recipient/content do source service cung cấp. Email reset password tiếp tục thuộc Identity.

## 4. Các giai đoạn và task đề xuất

### Giai đoạn 1 — Runtime và chat direct/group cơ bản

#### CB-01 · Bật Community route và runtime nội bộ

**Kết quả:** Gateway chuyển API Community và PushDevice về service Community; service chạy được trong môi trường tích hợp nội bộ.

**Acceptance criteria:**

- [ ] Gateway route `/api/v1/conversations`, `/messages`, `/notifications`, `/me/notification-preference` và `/me/push-devices` tới Community; Identity vẫn nhận các route `/me` còn lại.
- [ ] Community có cấu hình URL/port/health và deployment profile nhất quán với service hiện hữu; chỉ expose qua Gateway.
- [ ] Web/Android dùng URL path chuẩn đã duyệt, không gọi thẳng Community host.

**Verification:** Kiểm tra route resolver chọn Community cho `/api/v1/me/push-devices`, Identity cho `/api/v1/me/...` khác; health route trả thành công qua cấu hình nội bộ.

**Dependencies:** Xác nhận môi trường deploy và service URL.
**Repo/files dự kiến:** `api-gateway/src/constants/route-paths.constants.ts`, config Gateway; `infra/docker-compose.internal.yml`, env example/deploy; `community-service/src/config/`.
**Quy mô:** M.

#### CB-02 · Lưu conversation và membership generic

**Kết quả:** Community lưu được `Conversation` và `ConversationMember` theo ERD, bao gồm direct/group/context, role, status và read state.

**Acceptance criteria:**

- [ ] Migration/entity/repository có unique canonical pair cho direct, unique `(contextType, contextId)` cho context chat, và ràng buộc membership phù hợp.
- [ ] Member hỗ trợ `active/read_only`, role `admin/member/system`, `leftSequence`, `lastReadSequence`; participant system không cần tài khoản Identity.
- [ ] Migration chạy/revert được theo chuẩn service; không sửa `src/shared` riêng của Community.

**Verification:** Chạy migration trên DB rỗng và revert; kiểm tra unique constraint chặn direct/context trùng và membership kép.

**Dependencies:** Không phụ thuộc domain event publisher.
**Repo/files dự kiến:** `community-service/src/modules/conversation/`, `src/database/migrations/` (hoặc vị trí migration theo DataSource hiện tại).
**Quy mô:** M.

#### CB-03 · Tạo/list/resolve direct và group

**Kết quả:** User đăng nhập tạo direct/group, xem danh sách và tra context conversation theo OpenAPI.

**Acceptance criteria:**

- [ ] `POST /conversations` tạo group với caller là admin; direct luôn resolve một conversation duy nhất cho cặp và kích hoạt lại hai membership khi mở lại.
- [ ] `GET /conversations` hỗ trợ phân trang, unread count/last message và lookup theo `contextType + contextId`.
- [ ] User không thuộc conversation không đọc được detail/history; context chỉ trả cho user có membership đọc.

**Verification:** Thử tạo direct cùng cặp hai lần, tạo group, list, mở lại direct sau khi rời; xác nhận constraint và response code khớp OpenAPI.

**Dependencies:** CB-02.
**Repo/files dự kiến:** `community-service/src/modules/conversation/{domain,application,infrastructure,presentation}/`; `api-docs/src/paths/chat/conversations.yaml`.
**Quy mô:** M.

#### CB-04 · Quản trị thành viên nhóm

**Kết quả:** Admin thêm/xóa member, đổi role, đổi tên/ảnh group; member có thể tự rời.

**Acceptance criteria:**

- [ ] Admin có thể appoint admin; không thể hạ admin cuối cùng; khi admin cuối rời/bị xóa, quyền chuyển cho member còn lại tham gia sớm nhất.
- [ ] Kick/leave chuyển membership sang read-only, đóng băng `leftSequence`, chặn send và realtime; re-add kích hoạt row cũ và mở toàn bộ history.
- [ ] Mọi thay đổi group ghi system message và phát Socket, không gửi FCM.

**Verification:** Kiểm tra admin/member/last-admin, leave/kick/re-add, history boundary và system message qua API.

**Dependencies:** CB-03.
**Repo/files dự kiến:** Conversation application/presentation; API paths `conversation-members*.yaml`, `conversations-conversationId.yaml`.
**Quy mô:** M.

#### CB-05 · Lưu message, history và unread cursor

**Kết quả:** User gửi/đọc text message theo sequence; retry an toàn và unread state nhất quán.

**Acceptance criteria:**

- [ ] `Message` có sequence tăng dần theo conversation; `POST /messages` idempotent theo `(senderMemberId, clientMessageId)`.
- [ ] `GET /messages` cursor-paginated; active member đọc toàn bộ, read-only chỉ tới `leftSequence`; không hỗ trợ edit/delete/mention.
- [ ] Mark-read chỉ tăng `lastReadSequence`; unread count theo conversation và đồng bộ trên mọi thiết bị khi phát read-state event.

**Verification:** Gửi lại cùng client ID, phân trang qua sequence, mark-read lùi/tiến, kiểm tra read-only boundary và unread count.

**Dependencies:** CB-02, CB-03.
**Repo/files dự kiến:** `community-service/src/modules/message/`, ConversationMember persistence; `api-docs/src/paths/chat/messages*.yaml`.
**Quy mô:** M.

#### Checkpoint A — Chat REST

- [ ] Conversation, group membership và message flow khớp OpenAPI v1.
- [ ] Migration/unique/idempotency/read-boundary được xác minh trên môi trường development.
- [ ] Review thiết kế quyền trước khi thêm realtime hoặc client.

### Giai đoạn 2 — Realtime và ảnh chat

#### CB-06 · Socket auth, membership và chat events

**Kết quả:** Web/Android nhận message, membership/system changes và read-state realtime trên session hợp lệ.

**Acceptance criteria:**

- [ ] Socket xác thực JWT; join conversation cần membership active; kick/leave loại session khỏi room.
- [ ] Member read-only không nhận message mới; có thể tải lịch sử cho phép qua REST.
- [ ] Message được lưu trước khi phát; event chứa `conversationId`, `messageId`, `sequence`, sender/type/content-or-media và timestamp.

**Verification:** Mở hai session cùng/khác user, join hợp lệ/trái phép, kick khi đang online và reconnect bằng REST cursor.

**Dependencies:** CB-04, CB-05; CB-01 cho route/network.
**Repo/files dự kiến:** Community gateway/socket module, auth integration; API/Socket contract.
**Quy mô:** M.

#### CB-07 · Upload và đọc ảnh gắn với conversation

**Kết quả:** Client presign ảnh với `ownerType=conversation`, `ownerId=conversationId`, upload/download qua URL R2 có thời hạn; Community lưu `mediaId`, Media Service xác thực quyền qua Community.

**Acceptance criteria:**

- [ ] Identity Media hỗ trợ owner type `conversation` cho purpose `chat_attachment`; active member được upload, còn quyền đọc kiểm tra media đã gắn với message mà caller được phép đọc; owner ID phải là conversation ID và chỉ chấp nhận ảnh jpeg/png/webp.
- [ ] `POST /messages` nhận một `mediaId` cho mỗi image message; chỉ media upload hoàn tất, có owner ID trùng conversation và thuộc message đó mới được gắn.
- [ ] Read-only member chỉ tải được ảnh gắn với message có sequence `<= leftSequence`; ảnh upload dở hoặc chưa gắn message không hiển thị.
- [ ] Push preview ảnh hiển thị “Đã gửi ảnh”; không lưu binary trong Community.
- [ ] Draft hết hạn không vào history/unread; media chưa gửi được dọn theo chính sách retention đã cấu hình.

**Verification:** Upload/complete/read URL, thử gắn media của conversation khác và media chưa complete; kiểm tra URL hết hạn vẫn cần xin URL mới.

**Dependencies:** CB-02, CB-03, CB-05.
**Repo/files dự kiến:** `Identity-Service/src/modules/media/`; `community-service/src/modules/message/`; Media client trong FE/Android.
**Quy mô:** M.

### Giai đoạn 3 — Notification inbox và delivery

#### CB-08 · Notification, preference và PushDevice persistence/API

**Kết quả:** User có business inbox bền vững, mark-read đồng bộ, cấu hình push theo loại và quản lý FCM token Android.

**Acceptance criteria:**

- [ ] Notification lưu recipient, source/event ID, type/title/body/deepLink/data snapshot, created/read time; unique dedup theo source/event/recipient.
- [ ] Inbox hỗ trợ list cursor, unread filter, mark-one/all; không có delete; preference `chat|invoice|issue` mặc định bật và chỉ điều khiển push.
- [ ] Community sở hữu PushDevice; owner lấy từ JWT; duplicate token được upsert/diễn giải idempotent; chỉ platform Android trong v1.

**Verification:** Tạo nhiều recipient cho event, đọc trên session khác, tắt preference nhưng inbox vẫn còn, register/revoke token chính chủ.

**Dependencies:** CB-01; CB-02 có thể tái sử dụng member/auth pattern.
**Repo/files dự kiến:** `community-service/src/modules/notification/`, migrations; PushDevice module; `api-gateway/src/constants/route-paths.constants.ts`.
**Quy mô:** M.

#### CB-09 · Nhận integration event và persist inbox idempotent

**Kết quả:** Community consume event RabbitMQ từ producer nghiệp vụ; lưu inbox row cùng dedup marker và không mất inbox nếu delivery push lỗi.

**Acceptance criteria:**

- [ ] Consumer dùng inbox/processed-events hiện có; message redelivery không tạo notification trùng.
- [ ] Source event mang recipient list và snapshot content; Community không tự suy ra recipient từ contract/issue.
- [ ] Ghi notification và dấu processed event theo transaction boundary phù hợp; lỗi xử lý theo retry/DLQ boilerplate.

**Verification:** Replay cùng event, gửi event malformed/unknown, kiểm tra số inbox item và trạng thái retry/DLQ.

**Dependencies:** CB-08. Event producers được nối ở giai đoạn tích hợp sau.
**Repo/files dự kiến:** `community-service/src/modules/notification/presentation/messaging/`, application handler, InboxModule integration.
**Quy mô:** M.

#### CB-10 · Phát notification qua Socket và FCM

**Kết quả:** Business notification và chat message được fan-out cùng ID đến các session/thiết bị phù hợp.

**Acceptance criteria:**

- [ ] Socket phát notification tới mọi session đang kết nối; FCM phát tới mọi Android PushDevice khi preference tương ứng bật.
- [ ] Một inbox row duy nhất được dùng cho mọi channel; client có ID ổn định để khử trùng Socket/FCM.
- [ ] Chat push gồm sender + text preview hoặc “Đã gửi ảnh” + deep link; system group-change message không FCM.

**Verification:** User đăng nhập nhiều session/device, gửi event/message và xác nhận fan-out/dedupe; FCM failure không rollback inbox.

**Dependencies:** CB-06, CB-08, CB-09.
**Repo/files dự kiến:** Community notification/chat delivery providers, FCM config; deployment secrets/runtime config.
**Quy mô:** M.

#### Checkpoint B — Chat và notification backend

- [ ] REST, Socket, Inbox, read sync, FCM/PushDevice khớp contract v1.
- [ ] Xác minh redelivery idempotency, multi-device dedupe, media authorization và read-only access.
- [ ] Chốt event producer invoice/issue thật trước khi bật production consumer.

### Giai đoạn 4 — Tích hợp source domain và client

#### CB-11 · Đồng bộ conversation context và ContractMember

**Kết quả:** Conversation theo building/contract được tạo từ event; member lifecycle đồng bộ theo quy tắc đã duyệt.

**Acceptance criteria:**

- [ ] Building.created tạo một building conversation và owner admin; mỗi contract có một contract conversation.
- [ ] ContractMember add/kick được phản ánh idempotent; kick chỉ làm read-only ở contract chat; checkout/contract end không tự kick; building membership thay đổi theo đúng decision.
- [ ] Event consumer dùng payload thật; nếu sự kiện thiếu building/tenant/member IDs thì producer được bổ sung trong Tenancy cùng outbox transaction.

**Verification:** Replay building/contract/member events, kiểm tra unique context, membership trùng, kick boundary và contract/building chat separation.

**Dependencies:** CB-02, CB-03, CB-04; phụ thuộc các luồng Tenancy ContractMember liên quan, gồm P6-01e khi còn mở. Domain event producer là task tích hợp giai đoạn này, không phải prerequisite cho chat direct/group.

**Repo/files dự kiến:** `community-service/src/modules/conversation/presentation/messaging/`; `Tenancy-Service/src/modules/building/`, `contract/` và ContractMember module thực tế.
**Quy mô:** M.

#### CB-12 · Tích hợp event phát hành invoice và issue

**Kết quả:** Invoice/issue business events tới được inbox của đúng recipients do source service chọn.

**Acceptance criteria:**

- [ ] Invoice issued producer dùng outbox transaction và payload notification đã chốt; recipient rule nằm ở Tenancy/Invoice owner.
- [ ] Issue event chỉ được nối từ service/module phát issue đã được xác định; task không tạo IssueReport, `@issue` hay Issue panel.
- [ ] End-to-end event lưu một inbox item/recipient, rồi Socket/FCM tuân theo preference.

**Verification:** Tạo/ phát hành mỗi loại event trong service nguồn và xác nhận recipient, snapshot, deeplink, dedup, push preference.

**Dependencies:** CB-09, CB-10; producer Invoice phụ thuộc luồng Invoice P6-02; producer Issue phụ thuộc owner/module tương ứng nếu chưa tồn tại. Chưa làm publisher trước khi hoàn tất chat core.

**Repo/files dự kiến:** `Tenancy-Service/src/modules/invoice/` (sau khi có module), source issue service/module khi được chỉ định, `community-service/src/modules/notification/`.
**Quy mô:** M; có thể tách producer thành issue riêng khi source event contract rõ.

#### CB-13 · Web chat và business inbox

**Kết quả:** Web user tạo/open direct/group chat, quản lý nhóm theo quyền, gửi text/ảnh, xem history/unread và đọc business notification.

**Acceptance criteria:**

- [ ] Web dùng OpenAPI client hiện có; hiển thị conversation list, thread, group actions, system message và read-only boundary.
- [ ] Realtime dùng Socket event; reconnect tải phần thiếu qua cursor API; không tạo business inbox row từ chat message.
- [ ] Inbox hiển thị invoice/issue; mark-read đồng bộ; cài đặt push không làm ẩn inbox.

**Verification:** Chạy luồng hai user/group, bị kick khi đang online, upload ảnh, nhận invoice/issue event và mở đúng deep link.

**Dependencies:** CB-03–CB-10; context chat có thể hoàn thiện riêng qua CB-11.
**Repo/files dự kiến:** `fe/src/features/chat/`, `fe/src/features/notifications/`, API/socket client và route/navigation.
**Quy mô:** M, chia chat/inbox thành subtask nếu vượt giới hạn PR.

#### CB-14 · Android chat, push registration và notification inbox

**Kết quả:** Android tenant/landlord dùng chat và inbox, đăng ký token FCM và mở đúng deep link.

**Acceptance criteria:**

- [ ] Cả app-tenant và app-landlord dùng cùng contract/service patterns nếu cả hai role có chat; user chỉ thao tác conversation theo membership.
- [ ] Token Android được đăng ký/thu hồi với Community; push chat/business hiển thị preview theo preference; system message không push.
- [ ] Notification/chat navigation xử lý mở app nền/tắt và tải lại history qua API khi thiết bị offline.

**Verification:** Hai tài khoản Android, hai thiết bị/session, app foreground/background, mark-read sync, push toggle và deep link.

**Dependencies:** CB-03–CB-10; Firebase project/config và Android notification channel do app owner cấp.
**Repo/files dự kiến:** `mobile/app-tenant/`, `mobile/app-landlord/`, shared modules hiện hữu; `mobile/gradle/libs.versions.toml`.
**Quy mô:** M, tách tenant/landlord nếu vượt giới hạn PR.

### Giai đoạn 5 — Bot reminder và phát hành

#### CB-15 · Bot reminder theo mẫu, landlord chủ động gửi

**Kết quả:** Landlord chọn mẫu OCR result/invoice/contract expiring và xác nhận; bot đăng message vào conversation liên quan.

**Acceptance criteria:**

- [ ] `POST /conversations/{id}/bot-reminders` kiểm tra landlord có quyền với context/resource, `templateType`, `resourceId` và `clientMessageId`.
- [ ] Bot message được lưu trong Message history với template payload, phát Socket/FCM như chat; retry cùng ID không tạo trùng.
- [ ] Không có scheduler/cron gửi reminder tự động; client chỉ gửi request khi landlord chủ động bấm gửi.

**Verification:** Một case mỗi template, tài nguyên không thuộc landlord, conversation sai context, retry idempotent và push preference.

**Dependencies:** CB-05, CB-06, CB-10, CB-11/CB-12; nội dung/field cần cho từng template phải có trong source data/event contract.

**Repo/files dự kiến:** `community-service/src/modules/message/` và `conversation/`; Web/Android action; `api-docs/src/paths/chat/conversation-bot-reminders.yaml`.
**Quy mô:** M.

#### CB-16 · Staging, vận hành và rollout

**Kết quả:** Community bật an toàn trong môi trường staging/internal, có migration, secrets, logs và cách quan sát event/push failure.

**Acceptance criteria:**

- [ ] Internal compose bật Community bằng image/env; không public port RabbitMQ hoặc service.
- [ ] Secrets cấu hình cho FCM/Socket/storage; health/deploy path hoạt động; Gateway chỉ route public API.
- [ ] Có quy trình requeue/DLQ, migration/revert, dữ liệu test và checklist smoke qua Apidog trên staging.

**Verification:** Deploy staging, kiểm tra end-to-end chat/inbox/mobile push, rollback migration theo môi trường dev và tắt service trả lỗi Gateway dự kiến.

**Dependencies:** CB-01–CB-15; rollout chỉ sau PM xác nhận lịch và owner.

**Repo/files dự kiến:** `infra/`, `.github/workflows/` của Community, `community-service/`, `api-docs/`.
**Quy mô:** M.

## 5. Checkpoint và cách chuyển thành issue

| Checkpoint | Điều kiện review |
|---|---|
| **A — Sau CB-01–CB-05** | Chat REST, membership, idempotency, sequence/read cursor chạy đúng. Review trước Socket/client; chưa cần domain event publisher. |
| **B — Sau CB-06–CB-10** | Realtime, Media, Inbox, FCM và multi-device semantics hoàn chỉnh; push lỗi không làm mất inbox. |
| **C — Sau CB-11–CB-14** | Context sync, business event và Web/Android flows được kiểm tra theo đúng producer contracts. |
| **D — Sau CB-15–CB-16** | Bot thủ công và staging/rollout hoàn tất; PM review trước khi đánh dấu sẵn sàng demo. |

Backlog được lập lịch theo [Phase 7 task tracker](../../phase-7/issues/README.md). Trước khi bắt đầu từng PR, tách CB thành issue nhỏ theo template phù hợp (không quá 3 points hoặc khoảng 15 file/PR), giữ mã P7-CB làm dependency map cấp cao.

## 6. Rủi ro và điểm cần xác nhận khi tạo issue code

| Điểm | Ảnh hưởng | Xử lý trước/sát task |
|---|---|---|
| Event ContractMember add/kick và Invoice/Issue chưa thấy đầy đủ trong producer hiện trạng | Context/member sync hoặc notification không thể chạy chỉ bằng consumer Community. | Để ở giai đoạn tích hợp sau chat core; map event thật trong CB-11/CB-12, bổ sung producer tại service nguồn; Community không tự lookup DB. |
| Identity Media hiện chưa có `ownerType=conversation` và Community owner resolver chưa hoạt động | Upload/read có thể bị từ chối hoặc media bị gắn sai quyền. | Quyết định owner đã chốt; triển khai policy và Community authorization trong CB-07 trước khi gửi ảnh. |
| Bot template cần trường dữ liệu từ OCR/Invoice/Contract | Có endpoint nhưng không thể render nội dung đúng/ủy quyền đúng nếu nguồn chưa phát dữ liệu cần thiết. | Chỉ làm CB-15 sau khi CB-11/CB-12 xác nhận payload hoặc internal read contract cụ thể. |
| Gateway `/me` hiện thuộc Identity | PushDevice route có thể đi sai service nếu không thêm route cụ thể hơn. | CB-01 có test route matching trước khi client tích hợp. |
| Web/Android và Community đều chưa có chat implementation | Khối lượng UI/realtime lớn hơn REST contract. | Tách subtask theo app và giữ checkpoint A/B/C làm gate review. |

## 7. Ngoài backlog này

- `@issue`, IssueReport creation/chat panel, `MessageMention`, message edit/delete, file đính kèm ngoài ảnh, read receipt từng message.
- Push web qua FCM; web nhận realtime Socket và đọc inbox qua API.
- Email business notification; forgot/reset password vẫn thuộc Identity.
- Notification recipient discovery trong Community; recipient do source service cung cấp.
- Bot reminder tự chạy theo cron/scheduler.
- Event publisher invoice/issue không nằm trong lát cắt mở đầu; làm khi source contract và recipient đã sẵn sàng.

## 8. Tài liệu đối chiếu

- [Thiết kế Community Service](community-service-design.md) — phạm vi, BL/ERD/API/event contract đã duyệt.
- [`pm/phase-6/README.md`](../README.md), [`issues/README.md`](../issues/README.md), [`issues/_TEMPLATE.md`](../issues/_TEMPLATE.md) — lịch/Stretch, task convention.
- `community-service/src/app.module.ts`, `src/modules/{sample,health,inbox,outbox}/` — scaffold và messaging hiện có.
- `Tenancy-Service/src/modules/{building,contract}/domain/events/` — event producer hiện tại cần đối chiếu.
- `Identity-Service/src/modules/media/` — owner types, upload policy và resolver.
- `api-gateway/src/constants/route-paths.constants.ts`, `infra/docker-compose.internal.yml` — routing/deployment hiện trạng.
- `api-docs/src/openapi.yaml` — API contract chuẩn đã duyệt.
