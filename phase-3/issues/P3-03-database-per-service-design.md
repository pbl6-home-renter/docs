# P3-03 — Hiện thực hoá D53: ranh giới dữ liệu theo service (database-per-service)

**Status:** 🔵 In progress — thiết kế xong, chờ review + duyệt D52–D58
**Assignee:** BE Lead
**Stakeholders / Reviewers:** PM (duyệt scope), GV SOA (câu hỏi 3 ở §9)
**Created:** 2026-10-05
**Due date:** 2026-10-09 (EOD) — phải xong **trước** khi BE scaffold NestJS
**Priority:** 🔴 High / Blocker (chặn scaffold `tenancy_db` — 24 cột FK phải quyết định trước khi viết entity)

> **Không phải task "tách DB".** Phase 3 chưa có dòng code nào, nên không có gì để tách. Đây là task
> **thiết kế ranh giới dữ liệu** để BE scaffold đúng ngay từ đầu — rẻ hơn nhiều so với viết schema
> đơn rồi phân mảnh sau. Xem `microservices-architecture.md` §10 R7.

**Input:**

- `pm/phase-1/discovery/database-design.md` — SoT 24 entity đã mô tả, một schema
- `pm/phase-3/discovery/decisions.md` — **D52** (4 service) · **D53** (database-per-service) · D55 (gateway) · D57 (Saga/outbox) · D58 (1 repo / service)
- `pm/phase-3/discovery/microservices-architecture.md` §3.1, §4, §6, §7.3
- `pm/phase-1/discovery/utility-billing-calculations.md` — nguồn đếm `head_count`
- `pm/phase-2/discovery/api-conventions.md` §12, §13
- `pm/requirement.md` D29

**Deliverable:**

| # | Artifact | Vị trí |
|---|----------|--------|
| 1 | Báo cáo ranh giới dữ liệu | `pm/phase-3/discovery/database-per-service.md` |
| 2 | Section `## 1` + marker `Service` trên SoT schema | `pm/phase-1/discovery/database-design.md` |

---

## 1. Background

`microservices-architecture.md` §6.1 vẽ ra 4 database + 4 Postgres role, nhưng dừng ở **sơ đồ**.
`decisions.md:66` (D53) tự nêu ba việc còn lại:

> *"database-design.md needs a `service` column on all 25 entities and an explicit statement of which
> tables must not carry foreign keys. The existing ERD is a single-schema diagram and will have to be
> split into four."*

**Chưa ai làm 3 việc đó.** `database-design.md` vẫn mô tả một schema duy nhất, không entity nào có
marker service, và không tài liệu nào liệt kê cột FK nào phải bỏ.

Đây là việc chặn scaffold vì khi viết entity đầu tiên, BE phải biết ngay `rooms.landlord_id` có
được khai `REFERENCES users` hay không. Nếu không có register, BE sẽ viết FK, rồi phải gỡ — và gỡ FK
sau khi đã có dữ liệu thật thì tốn hơn nhiều lần so với không viết.

## 2. Vì sao là docs-only, không phải task migration

| Không làm | Vì sao |
|-----------|--------|
| Không viết DDL / migration | Chưa có code, D52–D58 chưa duyệt |
| Không sửa `api-spec.md` | Thuộc D58, cần PM review riêng |
| Không đụng `api-docs/` | Thuộc D58, tách thành task khác |
| Không chốt lại ranh giới 4 service | Thuộc D52, đã chốt |

## 3. Các hạng mục

### Task 1 — Gán service sở hữu cho từng entity

- [x] Bảng tra cứu ngược: entity → bảng → database → service
- [x] Marker `Service` trên từng heading `### 2.x` trong `database-design.md`
- [x] Bảng "một entity thuộc trọn vẹn một service" + đối chiếu số lượng

### Task 2 — Register FK chéo, từng cột một

- [x] Liệt kê **từng cột** phải bỏ `REFERENCES`, không nêu nguyên tắc chung
- [x] Mỗi dòng ghi cơ chế thay thế (HTTP + cache / event / đổi tên cột)
- [x] Tách riêng 3 chỗ bỏ FK làm mất toàn vẹn tham chiếu thật → phải bù bằng code
- [x] Liệt kê các trường jsonb **không được** "sửa" thành FK

### Task 3 — Tách ERD thành 4 ERD

- [x] 4 ERD Mermaid theo service, phân biệt FK thật (`--`) và logical reference (`..>`)
- [x] Đánh dấu cột đã bỏ FK bằng comment `NO FK`
- [x] Nêu quan hệ với `erd-v1.md` của P2-04 để không có hai ERD cạnh tranh

### Task 4 — Ma trận Postgres role & grant

- [x] 8 role: 4 owner `NOLOGIN` + 4 app `LOGIN`, tách owner khỏi app login
- [x] Script bootstrap chạy được, copy/paste là lên
- [x] **`REVOKE ... FROM PUBLIC`** — bước quyết định cơ chế có thật hay không
- [x] `ALTER DEFAULT PRIVILEGES` — nếu thiếu, bảng tạo sau sẽ không có grant
- [x] Ngoại lệ `service_registry` (không thuộc service nào) + role riêng cho gateway
- [x] 3 truy vấn chứng minh cơ chế hoạt động, dán kết quả vào báo cáo W9

### Task 5 — Layout migration

- [x] Migration nằm trong repo của service, không có thư mục chung
- [x] Chạy bằng role owner, tự migrate lúc boot, không có bước "migrate tất cả" ở trung tâm
- [x] Cấm migration đặt FK sang database khác — không ngoại lệ

### Task 6 — Register nhân bản dữ liệu

- [x] Phân biệt dữ liệu hiển thị (được nhân bản) với dữ liệu quyết định (không)
- [x] Chỉ giữ 2 bản sao được phép, giữ hẹp
- [x] `billing_read_models` phải là projection, nêu vì sao Dashboard không còn trả được bằng 1 query
- [x] Cạm bẫy: không denormalize `head_count`; không xoá business snapshot D29/D39

### Task 7 — Nêu gap mà D53 chưa biết

- [x] `### 2.6` không tồn tại trong `database-design.md` (đếm thực tế 24 heading, không phải 25)
- [x] 7 bảng mới do P3-02 sinh ra chưa có SoT schema
- [x] 5 câu hỏi chặn, ghi rõ người trả lời

## 4. Definition of Done

- [x] `pm/phase-3/discovery/database-per-service.md` tồn tại, đủ 9 phần
- [x] Đủ **24** marker `Service` trên các heading đang có; **không** tạo `### 2.6`
- [x] Register FK chéo liệt kê **24 cột**, mỗi cột một dòng, có cơ chế thay thế
- [x] 4 ERD Mermaid phân biệt được FK thật và logical reference
- [x] Ma trận grant chứa `REVOKE ... FROM PUBLIC` và `ALTER DEFAULT PRIVILEGES`
- [x] Có 3 truy vấn chứng minh cơ chế chặn cross-service join
- [x] Tiếng Việt có dấu trong `database-design.md` không bị hỏng sau khi sửa
- [ ] **D52 + D53 chuyển 🟡 Proposed → ✅ Accepted** (PM) — chặn việc dùng làm schema
- [ ] **§9 câu 1:** `### 2.6` là entity nào (PM + BE) — chặn scaffold `tenancy_db`
- [ ] **§9 câu 3:** GV có tính API Gateway vào 4 service không (GV SOA) — quyết định 4 hay 5 database
- [ ] PM review

> **4 mục chưa đánh dấu là việc của người khác, không phải việc còn bỏ dở của task này.** Task này
> xong khi tài liệu và register đủ; quyết định duyệt thuộc PM + GV.

## 5. Ghi chú cho lần scaffold sau này

Thứ tự bắt buộc khi BE bắt đầu code:

1. Chạy `db/00-bootstrap.sql` (§5.2) — **trước**, vì app không tự tạo được database/role của mình.
2. Chạy 3 truy vấn ở §5.4 — xác nhận cơ chế chặn hoạt động **trước** khi viết entity đầu tiên.
3. Rồi mới scaffold NestJS theo 4 service.
4. Entity đầu tiên của mỗi service phải viết theo register §3, không theo trực giác "thì FK cho
   an toàn".

## 6. Cross-ref

- `microservices-architecture.md` §3.1, §4.3, §4.5, §6.1, §7.3, §10 R7
- `decisions.md` D52 · D53 · D55 · D57 · D58
- `P3-02-microservices-architecture-research.md` (báo cáo cha)
- `P2-04-erd.md` (ERD một schema — chưa tạo, cần chốt quan hệ với §4 ERD ở trên)