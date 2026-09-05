# Realtime (WebSocket) Feasibility — Property Chat Platform

- **Issue:** P1-14 | **Assignee:** BE | **Reviewers:** PM (scope), Mobile (socket client), FE (web socket client)
- **Status:** 🟡 Feasibility study — awaiting teacher finalization (chi tiết chat chưa chốt) + BE effort fill-in
- **Decision ref:** D24′ (Property Chat — final, chờ teacher duyệt chi tiết)
- **Related:** `decisions.md` D24/D24′, `business-rules.md` §6, `feature-list.md` 2.7/6.6, `user-behavior-workflow.md`, `tech-feasibility.md` §5

---

## 0. TL;DR

Thầy muốn một **hệ sinh thái giữ chân người dùng** trong app (giảm ra-vào), thể hiện qua **socket realtime**. Kết quả khảo sát từ team kéo scope ra khỏi "ticket-thread" đơn thuần sang một **Property Chat Platform**: chat realtime + **bot tự động** + **@issue command** + **@mention**, cho mỗi phòng và toà nhà.

**Recommendation: Option A′ (tiến hóa của Option A)** — WebSocket dùng **Socket.io** cho Property Chat (KHÔNG full messenger Zalo-like): ~2 loại conversation (phòng + toà chung), realtime display khi app mở, **FCM là kênh offline notification** (không phụ thuộc socket), DB persistence làm nguồn sự thật khi app mở lại.

**Effort ước tính sơ bộ: 3 tuần toàn team (1 tuần/người parallel)** — con số cần BE/FE/Mobile xác nhận (ô TBD bên dưới). Rủi ro chính: scope phình so với ticket-thread (~3–4 ngày), demo background-kill, và sự phụ thuộc vào việc **tái dùng IssueReport** để giữ @issue đơn giản.

---

## 1. Bối cảnh & Động lực

- **Approach trước P1-14 (đã thay bằng D24′):** ticket-thread REST + FCM + pull-to-refresh; **không socket, không presence, không read receipt**. Lý do trước đây: WebSocket khó document Swagger/Apidog (yêu cầu môn học), demo risk, ~10–16 p-d cho nhu cầu ít cụ thể.
- **Teacher 27/08:** muốn socket realtime, muốn **hệ sinh thái** — người dùng không phải ra-vào app.
- **F4/D7 trước đây:** cân nhắc Zalo deep-link làm kênh — **team giờ LOẠI Zalo khỏi phương án** (không còn trong app).
- **Khảo sát thực tế (cuộc thảo luận P1-14):** tần suất nhắn trong thread **chưa được đo** — không có dữ liệu retention; quyết định socket hiện dựa trên yêu cầu của thầy hơn là nhu cầu data.

**Điểm then chốt:** số liệu effort và tần suất dùng chưa có. Ước lượng ~1 tuần BE/FE/Mobile là con số của PM, **chưa được members xác nhận**. Người viết bài này (PM) ghi rõ con số là TBD để tránh cam kết sai.

---

## 2. Options

### Option A′ — Property Chat Platform (Recommended)
WebSocket (Socket.io) cho **Property Chat**: không phải full messenger, nhưng rộng hơn ticket-thread — **2 loại conversation**, bot, @issue, @mention.

### Option B — Full realtime chat (Zalo-like)
Chat 1-1 + group tùy biến, sticker/voice/location/poll, moderation, multi-device sync, read-receipt — **out-of-scope MVP, LỚN** (~10–16 p-d theo F6). So với A′, B thêm nhiều loại nội dung & tính năng xã hội mà bài toán quản lý trọ **không cần**.

### Option C — Giữ FCM + polling, không socket
Không socket. Giữ ticket-thread. **Không thỏa yêu cầu thầy về "hệ sinh thái/không ra-vào app".**

> **Q: vì sao BỎ Option C?** Teacher đã xác nhận "*dùng socket*" (chi tiết chưa chốt). C là giữ hiện trạng — không đạt kỳ vọng thầy. Vẫn nêu để so sánh như baseline/fallback khi có rủi ro quá lớn.

---

## 3. Kiến trúc đề xuất (Option A′)

### 3.1 Thuật ngữ (tránh nhầm `room`)

| Thuật ngữ | Nghĩa |
|---|---|
| **Room** | Phòng NHÀ (101, 102…) — entity phòng trong hệ thống. |
| **Conversation** | Chat. Không dùng "room" cho chat để tránh nhầm với phòng nhà. |
| **Chat riêng phòng** | Conversation giữa landlord ↔ tenants của 1 phòng. |
| **Chat chung toà** | Conversation cho cả building: giao lưu + landlord nhắc tổng. |

### 3.2 Cấu trúc Conversation

| Loại | Members | Mục đích | Bot/Command |
|---|---|---|---|
| **Chat riêng phòng** | Landlord + tenants của phòng đó | Trao đổi cụ thể phòng, sự cố | ✅ Bot remind + `@issue` + `@mention` |
| **Chat chung toà** | Landlord + TẤT CẢ tenants trong building | Giao lưu, landlord nhắc tổng | ❌ Chỉ text/image/file + `@mention` (không bot/command phòng) |

- **Membership multi-room (D13):** 1 user có thể join nhiều conversations (thuê nhiều phòng, vừa landlord vừa tenant).
- **Landlord:** join **N chats riêng phòng + 1 chat chung toà** (tất cả mọi lúc). Tenant: join **1 chat phòng mình + 1 chat chung toà**.

### 3.3 Business flow (chat thay thế ticket-thread)

```
┌──────────────────────────────────────────────────────────────┐
│ Chat riêng phòng 101                                         │
├──────────────────────────────────────────────────────────────┤
│ [Landlord]: Chào em, tháng này nhớ thanh toán trước 15/09 nhé │
│ [Tenant]   : @landlord dạ để tối em chuyển khoản ạ            │
│ [Bot]      : 📊 Kết quả chốt số điện T8: 101 — 250kWh          │
│              → 950,000đ. Xem hóa đơn: [card]                  │
│ [Tenant]   : @issue máy lạnh phòng em bị chảy nước (ảnh)     │
│ [Bot]      : 📋 Đã tạo issue #101-003 "Máy lạnh chảy nước"     │
│              [card] → trạng thái Open                          │
└──────────────────────────────────────────────────────────────┘
```

**Chat riêng phòng** = thay thế hoàn toàn khái niệm "ticket-thread" trước đây. **@issue** tạo `IssueReport` → post card vào chat → issue panel theo dõi vòng đời.

### 3.4 Bot engine

- **Identity:** bot là 1 user hệ thống, có tên + avatar riêng (`sender_id = bot_user_id`, `type = 'bot'`). Bot **thay mặt landlord nhắn** nhưng là định danh riêng.
- **Auto (cron)** — trigger theo sự kiện:
  - **OCR:** landlord chụp ảnh điện/nước → OCR → verify số → **bot gửi card kết quả vào chat phòng**.
  - **Hóa đơn:** tạo hóa đơn / đến hạn / quá hạn → bot nhắc (có thể cấu hình).
  - **Hợp đồng:** hết hạn (trước N ngày — con số chốt sau) → bot nhắc.
- **Command-based** — cho phép user (tenant + landlord) gọi:
  - `@issue <mô tả>` (+ ảnh) → tạo IssueReport → card vào chat → **notify conversation**.
  - *(TBD — mở để thêm `@remind`, `@invoice`… sau MVP)*
- **Mention `@username`:** notify đến user được mention (như Messenger/Zalo), có autocomplete gợi ý khi gõ `@`.

> **MVP commands:** chỉ `@issue`. `@remind`/`@invoice` ghi là TBD/MVP-nice-to-haves. Nhắc tiền/hợp đồng trong MVP đến từ **bot auto** (cron) hơn là command người gõ.

### 3.5 Message types (MVP)

| Type | Nội dung | Mô tả |
|---|---|---|
| `text` | Tin nhắn thường | Text thuần |
| `image` | Ảnh | Landlord/tenant gửi ảnh |
| `file` | File (PDF hóa đơn/hợp đồng) | Upload file |
| `bot` | Card/bot message | Header + title + ảnh (optional) + link (optional) + body |

> Còn lại (voice, sticker, location, poll, video, contact…) = **nice-to-have**, ngoài MVP. Tham khảo Zalo nhưng không bắt buộc cho MVP.

### 3.6 Card / formatted message

```
┌──────────────────────────────┐
│ 💰 Hóa đơn T08/2026          │  ← header + title
│ Phòng: 101                    │
│ Tổng: 4,650,000đ             │
│ Hạn: 15/09/2026              │  ← body
│ 🔗 [link]                    │  ← link (optional)
└──────────────────────────────┘
```

### 3.7 Connection & realtime model

- **Socket.io** (auto-reconnect + rooms/namespace built-in + fallback polling chống firew themselves).
- **1 connection / user** → join nhiều conversations (landlord join N+1). Server route event theo từng conversation khi emit.
- **Auth:** JWT verify trên WS handshake → join conversations mà user là member.
- **Realtime display chỉ khi app ĐANG MỞ.** App mở lại → **load history từ DB (lazy load, cursor-based)**.
- **Offline = FCM push** (nội dung/link vào conversation) — **KHÔNG phụ thuộc socket**. Email: nice-to-have fallback.

### 3.8 Message & data model (đính kèm cho BE, refine tại P1-18)

```
Conversation
├── id (uuid PK)
├── kind: 'room' | 'building'        -- chat riêng phòng | chat chung toà
├── room_id (FK → Room, nullable)    -- set khi kind='room'
├── building_id (FK → Building)      -- set khi kind='building'
├── bot_config (jsonb, nullable)     -- auto-remind config per conversation

ConversationMember
├── conversation_id (FK)
├── user_id (FK)
├── role: 'landlord' | 'tenant'
├── settings (jsonb)                 -- mute/unmute, remind on/off per role

Message
├── id (uuid PK)
├── conversation_id (FK)
├── sender_id (FK → User | NULL = bot)
├── type: 'text' | 'image' | 'file' | 'bot'
├── content (text)
├── metadata (jsonb)                 -- card payload, issue_id, reminder_type...
├── is_pinned (bool)
├── created_at

IssueReport (TÁI DÙNG entity hiện tại)
├── (giữ: open → in_progress → resolved, room_id, tenant_id, images)
├── + conversation_id (FK, optional) -- liên kết khi tạo qua @issue
├── + issue_no (vD "101-003")        -- hiển thị trong card
```

### 3.9 Socket.io events (đính kèm)

| Event | Direction | Payload |
|---|---|---|
| `join-conversation` | C→S | `{ conversationId }` |
| `leave-conversation` | C→S | `{ conversationId }` |
| `send-message` | C→S | `{ conversationId, content, type, metadata }` |
| `new-message` | S→C | `{ message }` |
| `mention` | S→C | `{ message, mentionedUserIds }` |
| `issue-created` | S→C | `{ issue, card }` |
| `issue-updated` | S→C | `{ issue, card }` |
| `message-pinned` | S→C | `{ messageId, isPinned }` |

### 3.10 REST endpoints (document trong Swagger)

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/conversations` | List conversations của user |
| GET | `/conversations/:id/messages` | History (cursor pagination) |
| POST | `/conversations/:id/messages` | Gửi tin (REST fallback / offline queue) |
| POST | `/conversations/:id/pin/:messageId` | Pin/unpin |
| GET | `/issues?conversationId=` | List issues theo conversation |
| POST | `/issues` | Tạo issue (nguồn: @issue + panel) |
| PATCH | `/issues/:id` | Update issue status |
| GET/PATCH | `/settings` (landlord/building/room/contract/conversation) | Settings reads/writes (default→override, §3.11) |
| GET/PATCH | `/conversations/:id/settings` | Notification/remind settings per role |

> **Document WS events:** dùng **markdown trong repo** (bảng §3.9). Thầy không quan tâm format, chỉ cần **demo được**. Swagger giữ cho REST; WS events để markdown — thỏa yêu cầu môn học vì REST vẫn là phần contract chính. (AsyncAPI optional, không bắt buộc.)

### 3.11 Settings — mô hình đề xuất (default → override)

> **Trạng thái:** đề xuất kiến trúc, **chưa chốt** — cần PM duyệt + khớp `requirement.md` trước khi implement (không vượt scope hiện có).

**Nguyên tắc:** 1 tab Settings thống nhất, theo phân cấp **default → override**:
- **Landlord default (global)** → áp cho mọi tòa building của chủ trọ đó. Landlord chỉ set **1 lần**; không phải khai lại từng building.
- **Building override** → áp cho 1 building (vd dãy A giá nước khác, căn hộ dịch vụ chu kỳ khác). Chỉ khai khi building khác biệt so với default landlord.
- **Override cấp thấp hơn** (per **room** / per **contract** / per **conversation** / per **role** / per **user**) chỉ ghi đè field cụ thể đã bật.
- Mọi override là **opt-in**: không ghi đè → dùng default cấp trên.
- **Thứ tự phân giải:** `room → building → landlord` (lấy override không-rỗng ở tầng cụ thể nhất).

**Bốn nhóm setting** (ghi chú nguồn quyết định hiện có):

| Nhóm | Field | Default (landlord, global) | Override (building → thấp hơn) | Nguồn quyết định |
|---|---|---|---|---|
| **Notification / chat** | mute/unmute, remind on/off, FCM on/off, bot nhắc theo sự kiện (OCR/hóa đơn/HĐ) | landlord default (bot nhắc mặc định bật) | building → per conversation · per role (tenant vs landlord) · per user | D24′, §3.8 `ConversationMember.settings` |
| **Điện/nước (utility rate)** | giá điện, giá nước, bậc thang EVN (nếu có), ngày chốt số | landlord default (đặt 1 lần cho mọi building) | building → per **room** (room override) | D16, feature 3.11 |
| **Hóa đơn (invoice)** | chu kỳ xuất, ngày hạn, cách gửi (FCM / kênh ngoài app), dòng/format | landlord default | building → per contract / per room | D24′ bot remind, D29 (đẩy ngoài) |
| **Hợp đồng (contract)** | template HĐ mặc định, thời hạn, cảnh báo hết hạn (trước N ngày) | landlord default | building → per contract | D18 |

**Per-role tách bạch (tenant vs landlord):**
- **Landlord:** settings là **cấu hình nghiệp vụ** (giá, chu kỳ, template, remind bot, giới hạn gửi) — đặt **global 1 lần**, rồi chỉ override per-building khi khác. Landlord nhìn toàn bộ tab Settings của tòa mình (kèm source cho thấy đang dùng global hay override).
- **Tenant:** settings chỉ là **cá nhân hóa nhận** (mute/notification per conversation, ngôn ngữ); tenant KHÔNG thấy/sửa cấu hình giá/hợp đồng/chu kỳ.

**Hợp lý hóa 1 tab:** gom hết vào 1 "Settings" tab là **hợp lý** cho landlord (1 nơi quản lý tòa) và tenant (1 nơi quản lý cá nhân) — nhưng chia **2 view riêng theo role** (landlord = điều hành, tenant = cá nhân). Đề xuất này cần PM chốt trước khi đưa vào `requirement.md`.

**Điểm lưu ý cho BE (schema):**
- `LandlordProfile.default_settings` (jsonb) — **global default** cho mọi building của chủ.
- `Building.settings` (jsonb, nullable) — override cấp building.
- `Room.settings` / `Contract.settings` (jsonb, nullable) — override cấp thấp hơn.
- `ConversationMember.settings` (jsonb) — override per role/user (đã có ở §3.8).
- Trước khi hiển thị: `effective = override ⋈ default` (nested-merge, không ghi đè trống) theo thứ tự `room → building → landlord`.

---

## 4. Effort & Risk

### 4.1 Effort so sánh options

| Option | Effort | So với ticket-thread baseline |
|---|---|---|
| **A′ Property Chat** | **~3 tuần toàn team (1 tuần/người parallel)** — TBD cần xác nhận | +~2 tuần |
| B Full chat | ~10–16 p-d (F6) | +~1.5–3 tuần |
| C FCM + polling (no socket) | ~3–4 p-d (F6) | baseline |

### 4.2 Effort breakdown Option A′ (PM ước lượng — **TBD cho từng member**)

**BE — ~7 ngày (TBD):**

| Task | Ngày |
|---|---|
| Socket.io gateway + JWT auth + join conversations | TBD |
| Message CRUD + History lazy-load pagination | TBD |
| DB schema: Conversation, ConversationMember, Message, IssueReport mở rộng | TBD |
| Bot engine (cron: OCR-result, invoice, contract-expiry) | TBD |
| Command parser `@issue` + card generation | TBD |
| Mention system + FCM push integration | TBD |
| REST endpoints + Swagger | TBD |
| **Tổng** | **TBD (~7?)** |

**FE (web) — ~7 ngày (TBD):**

| Task | Ngày |
|---|---|
| Socket.io client + auto-reconnect | TBD |
| Conversation list + switcher (nhiều phòng + toà chung) | TBD |
| Chat UI (message list, input, lazy-load) | TBD |
| Card / bot message rendering | TBD |
| Mention autocomplete gợi ý | TBD |
| Issue panel UI | TBD |
| Notification/remind settings UI (per role) | TBD |
| **Tổng** | **TBD (~7?)** |

**Mobile (Android) — ~7 ngày (TBD):**

| Task | Ngày |
|---|---|
| Socket.io client + background handling | TBD |
| Chat UI (RecyclerView + lazy-load) | TBD |
| Conversation list + switcher | TBD |
| Issue panel | TBD |
| FCM + deep-link vào conversation | TBD |
| Mention autocomplete | TBD |
| Notification settings | TBD |
| **Tổng** | **TBD (~7?)** |

> **⚠️ TBD:** con số trên là ước lượng PM; **bắt buộc BE/FE/Mobile xác nhận** trước khi chốt scope. Nếu tổng >3 tuần → plan B: cắt `@issue`/issue-panel sang phase sau, chỉ giữ chat + bot auto-remind.

### 4.3 Risks

| # | Risk | L×I | Mitigation |
|---|---|---|---|
| RR1 | **Scope phình so với ticket-thread baseline** (chat+bot+command ~3 tuần vs ~3–4 ngày) | H×H | Chốt MVP rõ (chỉ `@issue` + bot auto + mention); phần còn lại nice-to-have; xác nhận effort 3 members trước khi cam kết |
| RR2 | **Android kill socket background → mất realtime** | M×H | Realtime chỉ verify khi app mở; **FCM là nguồn offline** — không phụ thuộc socket để nhận tin |
| RR3 | **Demo risk** (socket die mid-demo, Render cold-start 30–60s khiến WS mất) | M×H | Keep-alive ping; fallback mở lại app load history từ DB; kịch bản demo backup (trình bày bằng data seed nếu socket lỗi) |
| RR4 | **Tần suất dùng chưa đo** — socket có thể "thừa" cho nhu cầu thực | L×M | Giữ FCM+DB làm fallback; quyết định dựa trên yêu cầu thầy (đã xác nhận dùng socket) |
| RR5 | **Bot + @issue phức tạp nếu IssueReport không tái dùng** | M×M | **Tái dùng IssueReport hiện tại** làm foundation, chỉ thêm fields — tránh xây mới |
| RR6 | **Swagger/Apidog ghi WS không gọn** | L×M | WS events document markdown; Swagger giữ REST (đủ điều kiện môn học) |
| RR7 | **Kỳ vọng "hệ sinh thái" vô hạn của thầy** (thêm tính năng ngoài scope) | H×M | Chốt MVP scope tại challenge; mọi thêm ngoài scope → PM approve (D3 responsibility) |

---

## 5. Recommendation

**Chọn Option A′ — Property Chat Platform (bổ sung vào D24′).**

**Rationale:**
1. Teacher muốn socket + hệ sinh thái → **chỉ A′ (hoặc B) đáp ứng**. C là baseline fallback, không phải đích.
2. **A′ đủ** cho bài toán trọ mà KHÔNG kéo theo chi phí xã hội của B (sticker/voice/moderation/read-receipt…).
3. **FCM là lưới an toàn:** kể cả socket chết, tenant/landlord vẫn nhận notification + load history từ DB → giảm demo risk đáng kể vs quan niệm "socket-toàn-định".
4. **Tái dùng IssueReport + tách bot-chỉ-ở-chat-phòng** giữ scope có giới hạn.

**Fallback (nếu effort xác nhận >3 tuần / team không agree):** cắt `@issue`+issue-panel để Phase sau, MVP chỉ còn **chat realtime (2 conversation) + bot auto-remind + mention**. Đây vẫn là "hệ sinh thái" đáp ứng thầy mà rủi ro thấp hơn.

---

## 6. Actions

- [ ] **BE:** xác nhận effort breakdown §4.2 (spike Socket.io gateway 1 ngày nếu cần) → điền TBD.
- [ ] **FE/Mobile:** xác nhận effort + spike socket client.
- [ ] **PM:** trình teacher scope A′ (chat 2 conversation + bot + @issue + mention) để thầy duyệt chi tiết → xác nhận D24′ (final).
- [ ] **PM/BE:** cập nhật `business-rules.md` §6, `feature-list.md` 2.7/6.6, `user-behavior-workflow.md`, DB schema (P1-18).
- [ ] **PM:** chốt mô hình Settings §3.11 (1 tab, default→override, 4 nhóm, view theo role) → cập nhật `requirement.md` + `feature-list.md` nếu duyệt.

---

## 7. Definition of Done (P1-14)

- [ ] 3 options so sánh có con số effort → ✅ (A′ ~3 tuần, B ~10–16 p-d, C ~3–4 p-d) — **con số A′ cần member xác nhận**
- [ ] Cách document WS dưới yêu cầu môn học → ✅ (REST→Swagger, WS events→markdown)
- [ ] Recommendation rõ ràng + PM xác nhận D24′ ↔ Option A′
- [ ] Settings model (default→override, 4 nhóm, view theo role) ghi rõ §3.11 + PM chốt — **pending**
- [ ] Effort breakdown được 3 members điền & chốt (hiện TBD) — **pending**
