# P1-01 — Feature → Platform Map

**Status:** 🟡 Open
**Assignee:** PM (soạn bản nháp) · **FE + Mobile** (verify)
**Depends on:** `../../phase-0/feature-list.md`, `../discovery/user_flow/` (per-role SoT), `../discovery/decisions.md`
**Deliverable:** Bảng mapping đã xác nhận (dùng làm input cho P1-02 / P1-03 / P1-05) → lưu `discovery/product-platform-map.md`

---

## Mục đích

Xác định **từng feature xuất hiện trên Web, Mobile, hay cả 2**, và đâu là nền tảng **primary**. Đây là input bắt buộc trước khi FE/Mobile chọn tech stack và thiết kế UI — vì bạn phải biết mình build gì.

## ⚠️ Bản chất: THAM KHẢO, chưa phải chuẩn

Bảng bên dưới là **bản nháp do PM soạn** — **không phải sự thật đã chốt**. Danh sách feature từ `feature-list.md` và cách gán platform có thể **chưa chuẩn / sai / thiếu**. Nhiệm vụ của FE + Mobile là **xem xét kỹ và đề xuất chỉnh sửa dựa trên thực tế bạn sẽ build** (màn hình nào khả thi, luồng nào rườm rà, feature nào cần thêm/bớt).

Vì vậy: phần **"Verdict cần từ FE & Mobile"** ở dưới là phần cốt lõi — bạn được quyền (và nên) **sửa cả tên feature, thêm/bớt feature, đổi platform, đổi primary/secondary**. PM chỉ chốt sau khi bạn đã góp ý.

## Input tham chiếu (source of truth — cũng chỉ là căn cứ, không cứng nhắc)

- `pm/phase-0/feature-list.md` — danh mục 37 feature + priority (**dùng làm danh sách gợi ý, không phải bắt buộc**).
- `pm/phase-1/discovery/user_flow/` — luồng nghiệp vụ theo từng vai trò (tenant / landlord / admin / shared) + ai làm trên màn hình nào.
- `pm/phase-0/discovery/decisions.md` — quyết định D1–D29 (đặc biệt D13 cross-platform, D19 no-import, D22 bill config, D29 landlord-solo).

## Chú thích nhãn

- **Web / Mobile** — nền tảng có feature đó.
- **PRIMARY** — nền tảng chính, build đầy đủ chiều sâu.
- **Secondary** — nền tảng phụ, bản đơn giản/thông tin (theo D13 staging).
- **Both** — cả 2 nền tảng cùng mức.
- **co-PRIMARY** — cả 2 đều là kênh chính (mỗi role khai thác từ platform chính của mình).
- **—** — không xuất hiện (deferred/no-import/không áp dụng).

---

## Bảng mapping đề xuất (FE + Mobile verify)

### Module 1 — Property Management

| # | Feature | Priority | Web | Mobile | Ghi chú |
|---|---------|----------|-----|--------|---------|
| 1.1 | Room CRUD | MVP | **PRIMARY** | — | Landlord ops console. Ngoài landlord-lite scope. |
| 1.2 | Building management (+ rate mặc định D16) | MVP | **PRIMARY** | — | Nhóm phòng, đặt giá. |
| 1.3 | Dashboard (room calendar + revenue/debt charts) | MVP | **PRIMARY** | Secondary | Web đầy đủ (D20); mobile-lite chỉ xem summary. |
| 1.4 | Room status tracking | Stretch | PRIMARY | — | Derive từ HĐ active. |
| 1.5 | Photo gallery per room | Nice | PRIMARY | — | Landlord upload trên web; tenant xem qua 2.3. |
| 1.6 | Bulk ops (export CSV/XLSX) | Dropped | — | — | **Dropped (D19)**. |

### Module 2 — Tenant Operations

| # | Feature | Priority | Web | Mobile | Ghi chú |
|---|---------|----------|-----|--------|---------|
| 2.1 | Map-based room search | MVP | Secondary | **PRIMARY** | Mobile là chính (GPS/map SDK). Web responsive tenant. |
| 2.2 | Advanced filters | MVP | Secondary | **PRIMARY** | |
| 2.3 | Room detail view | MVP | Secondary | **PRIMARY** | |
| 2.4 | Monthly invoice view | MVP | Secondary | **PRIMARY** | Landlord xem/quản lý ở Module 3 (web). |
| 2.5 | Online payment (VNPay/Momo) | MVP | Secondary | **PRIMARY** | Mobile native SDK; web redirect. D29: QR/tiền mặt không cần app. |
| 2.6 | Payment history | Stretch | Secondary | **PRIMARY** | |
| 2.7 | Issue reporting (`@issue` + card) | MVP | Secondary | **PRIMARY** | Tenant báo trên mobile; landlord quản lý ở 6.6/web. |
| 2.8 | Property Chat (D24′) | MVP | Secondary | **PRIMARY** | Chat riêng phòng + chung toà, bot, `@issue`, `@mention`; realtime Socket.io + FCM offline. |
| 2.9 | Favorite/save rooms | Nice | Secondary | **PRIMARY** | |
| 2.10 | Tenant rental history | Stretch | Secondary | **PRIMARY** | Consent-based (D26). |

### Module 3 — Contract & Billing

| # | Feature | Priority | Web | Mobile | Ghi chú |
|---|---------|----------|-----|--------|---------|
| 3.1 | E-contract creation + signing (template upload) | MVP | **PRIMARY** | Secondary | Landlord tạo/sinh mẫu/up file ký trên web (D18). Tenant xem trạng thái trên mobile. |
| 3.2 | E-contract listing & status | MVP | **PRIMARY** | Secondary | |
| 3.3 | OCR meter closing + manual confirm | MVP | **PRIMARY** | Secondary* | *Xem open question bên dưới — chụp ảnh công tơ nghiêng về mobile. |
| 3.4 | Auto-invoice generation | MVP | **PRIMARY** | Secondary | Landlord theo dõi/sinh trên web; tenant nhận trên mobile. |
| 3.5 | Invoice listing & status | MVP | **PRIMARY** | Secondary | |
| 3.6 | Payment tracking & reminders | Stretch | PRIMARY | Secondary | Nhắc qua FCM (6.4). |
| 3.7 | Realtime revenue & debt dashboard | MVP | **PRIMARY** | Secondary | Gộp với 1.3. |
| 3.8 | Multi-currency | Nice | PRIMARY | — | Không cần cho VN. |
| 3.9 | E-invoice legal compliance | Nice | PRIMARY | — | |
| 3.10 | Dynamic named-QR + auto-reconciliation | MVP | **PRIMARY** | — | Sinh QR trên web; tenant quét bằng app ngân hàng bất kỳ (không cần app). |
| 3.11 | Utility rate config | MVP | **PRIMARY** | — | Landlord cấu hình trên web. |

### Module 4 — Roommate Social

| # | Feature | Priority | Web | Mobile | Ghi chú |
|---|---------|----------|-----|--------|---------|
| 4.1 | Roommate profile | MVP | Secondary | **PRIMARY** | |
| 4.2 | Browse roommate profiles | MVP | Secondary | **PRIMARY** | |
| 4.3 | Match request / connect | MVP | Secondary | **PRIMARY** | P2P; chủ trọ không veto từng cặp (D21). |
| 4.4 | AI Matchmaking score + advice | Stretch | Secondary | **PRIMARY** | (D28) |
| 4.5 | Chat between matched roommates | Nice | — | — | **Nice-to-have** — liên hệ qua kênh ngoài (SĐT/Zalo sau mở khóa) hoặc Property Chat; không build 1-1 riêng trong MVP. |
| 4.6 | Personality quiz | Nice | Secondary | **PRIMARY** | |
| 4.7 | Landlord room/tenant constraints | MVP | **PRIMARY** | Secondary | Chủ trọ set hard-filter trên web (D21); tenant thấy khi browse. |

### Module 5 — AI Features

| # | Feature | Priority | Web | Mobile | Ghi chú |
|---|---------|----------|-----|--------|---------|
| 5.1 | Auto room description from keywords | MVP | **PRIMARY** | — | Landlord ops. |
| 5.2 | Roommate matchmaking score | Stretch | Secondary | **PRIMARY** | Hiển thị khi browse (tương tự 4.4). |
| 5.3 | Smart room recommendations | Nice | Secondary | **PRIMARY** | |
| 5.4 | Price suggestion | Nice | PRIMARY | — | |
| 5.6 | CCCD OCR extraction | MVP | **PRIMARY** | — | Trong luồng e-contract (3.1) trên web; tái dùng pipeline OCR. |

### Module 6 — Admin & System

| # | Feature | Priority | Web | Mobile | Ghi chú |
|---|---------|----------|-----|--------|---------|
| 6.1 | User authentication (JWT) | MVP | Both | Both | Cả 2 cần login. D29: tenant login tùy chọn. |
| 6.2 | Role-based access (roles array) | MVP | Both | Both | (D13) |
| 6.3 | User profile management | MVP | Both | Both | |
| 6.4 | Notification system (FCM) | Stretch | Secondary | **PRIMARY** | FCM là kênh chính (D7). Web dùng thông báo in-app. |
| 6.5 | Multi-language | Nice | Both | Both | Không cần cho VN MVP. |
| 6.6 | Property Chat issue/chat panel | MVP | **co-PRIMARY** | **co-PRIMARY** | Landlord quản lý trên web, tenant tham gia trên mobile (D24′). Item 2.8 giữ platform map đồng bộ. |

---

## Tóm tắt phân bố

| Nhóm | Web PRIMARY | Mobile PRIMARY | Both/co-PRIMARY | Dropped/Deferred |
|------|-------------|----------------|-----------------|------------------|
| Module 1 | 5 | 0 | 0 | 1 |
| Module 2 | 0 | 7 | 0 | 1 (2.8) |
| Module 3 | 6 | 0 | 0 | 1 (no-import)+0 |
| Module 4 | 1 | 4 | 0 | 1 (4.5) |
| Module 5 | 2 | 0 | 0 | 0 |
| Module 6 | 0 | 1 | 3 (6.1,6.2,6.6) | 0 |

**Nhận xét chính:** Module 1 & 3 thiên về **Web** (landlord ops). Module 2 & 4 thiên về **Mobile** (tenant). Auth/profile/Property Chat (6.6) xuất hiện ở **cả 2**. D29 giữ nhiều feature Web-primary vì landlord vận hành solo.

---

## Verdict cần từ FE & Mobile

Bảng trên là **bản nháp tham khảo**. Vui lòng đối chiếu với `feature-list.md` + `discovery/user_flow/` + `decisions.md` và **chủ động góp ý chỉnh sửa** (không chỉ xác nhận):

1. **Sai sót platform nào?** (feature bị gán thiếu/sai web-mobile)
2. **Primary/secondary có đúng với khối lượng thực tế bạn định build?**
3. **Feature nào nên thêm bớt / gộp tách / đổi tên?** — vì `feature-list.md` chỉ là gợi ý, hãy báo feature bạn thấy không cần thiết, hoặc thiếu màn hình thực tế bạn cần.
4. **3.3 OCR meter closing** — hiện để Web PRIMARY (landlord up ảnh). Bạn có cân nhắc đưa thêm nhánh **chụp ảnh trên mobile** (landlord-lite) vì lợi thế chụp tại hiện trường không? (Xem open question.)
5. Có feature nào bạn nghĩ nên **đổi platform** so với bảng không?

**Cách ghi kết quả:** FE và Mobile mỗi người ghi kết quả verify vào **`discovery/fe-proposal.md` / `discovery/mobile-proposal.md`** (mục "Feature map verify") — liệt kê: (a) đồng ý với feature nào, (b) đề xuất sửa/khác với bảng (sửa platform/priority/thêm/bớt), (c) lý do. PM tổng hợp → chốt bảng cuối vào `product-platform-map.md`.

---

## Open questions (chưa chốt, đưa ra để quyết định)

- **3.3 — OCR chốt số trên mobile:** chụp ảnh công tơ vốn là hành động tại hiện trường (bản chất mobile). Đề xuất cân nhắc thêm **Mobile landlord-lite: chụp ảnh + OCR confirm** (secondary). Chờ FE/Mobile + PM quyết định.
- **2.1 map search trên web:** có cần bản đồ thật trên web responsive hay chỉ danh sách + location link? (Ảnh hưởng chọn map lib FE.)
- **6.6 Property Chat realtime:** chờ P1-14 (D24′) — không ảnh hưởng quyết định platform, chỉ ảnh hưởng cơ chế cập nhật (FCM+DB persistence baseline).
