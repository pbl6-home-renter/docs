# P6-02h — MeterReading: migration, baseline kỳ đầu, `source`/`ocrValue`, `PATCH` có khóa kỳ

**Epic:** [P6-02](P6-02-tenancy-billing-vertical-slice.md)  
**Trạng thái:** 🟡 Open (viết lại theo `P6-D66`/`P6-D67`/`P6-D70` — thay outline "OCR preview" cũ; ước lượng tăng 2 → 3 points vì thêm baseline kỳ đầu + `evidenceMediaId`, bỏ `DELETE`)  
**Người phụ trách:** leminhkhai345  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 3 points · 8–10 giờ  
**Phụ thuộc:** P6-02g1 (bảng `invoices` — chỉ cần cho bước 5). **P6-02g2 phụ thuộc task này** (migration phải merge trước, `P6-D70`).
**Repo / branch:** `Tenancy-Service` · `feature/p6-02h-meter-reading-source-lock`  
**Iteration:** It6 (09/11–15/11)  
**Issue:** `docs#78`

> **Đọc trước khi code:** `AGENTS.md` và skill trong `.agents/skills/` của repo (backend: `be-feature-workflow`). Issue **không** quy định cách đặt file, đặt tên hay style — nếu issue nói khác skill thì làm theo skill. Nguồn mâu thuẫn xử lý theo [`P6-D75`](../decisions.md#d75--thứ-tự-ưu-tiên-nguồn-và-cách-xử-lý-câu-hỏi-mở): `decisions.md` > `api-docs` > skill > issue.

## Hiện trạng code (kiểm ngày 01/11/2026)

- Module `src/modules/meter-reading/` **đã merge vào `main`** (`6251329` feat P6-02e + `05374e5` fix). Nhánh `origin/feature/p6-02e-meter-reading` (`35cccd3`) chỉ còn là bản cũ hơn, không cần merge nữa.
- **Chưa có migration** cho `meter_readings`: `src/database/migrations/` không có file nào tạo bảng này → DB mới chạy `migration:run` xong gọi `POST /meter-readings` sẽ lỗi `relation "meter_readings" does not exist`. **Phải sửa trước mọi việc Invoice** (P6-02g2 đọc reading).
- Unique index hiện là `(room_id, type, period) WHERE is_deleted = false` → kỳ có baseline không nhập được reading chốt tháng, điện/nước kỳ đầu luôn 0 (trái calc §8). `P6-D70` đổi thành partial bỏ baseline.
- Handler tạo lấy `previous` bằng `findLatestBefore(period)` → bỏ qua baseline cùng kỳ.
- `evidenceMediaId` có ở 8 file (props, entity, command, handler, mapper, typeorm entity, request, response) — **giữ lại** (`P6-D70`), chỉ bỏ việc bắt buộc khi tạo.
- Entity khai báo mỗi prop hai lần (interface `MeterReadingRecordProps` + 10 tham số `readonly` của constructor). Không phải lỗi; chỉ gọn lại nếu skill yêu cầu, không mở rộng phạm vi.
- Chưa có `source`, `ocrValue`, chưa có endpoint sửa. Bulk (P6-02f) chưa có code.

## Mục tiêu

Bảng `meter_readings` được tạo bằng migration đúng shape cuối; kỳ đầu tính tiêu thụ thực từ baseline; reading lưu được nguồn nhập (`manual`/`ocr`), số AI gợi ý và `evidenceMediaId`; landlord sửa reading mới nhất khi kỳ chưa phát hành hóa đơn, còn kỳ đã phát hành thì nhận `409 PERIOD_ALREADY_INVOICED`.

## Quyết định áp dụng

- `P6-D70` — UNIQUE partial `(room_id, type, period) WHERE is_baseline = false AND is_deleted = false`; kỳ đầu `previous` = `current` của baseline cùng phòng/loại; `PATCH /meter-readings/{id}` `{ currentReading?, evidenceMediaId? }` chỉ cho reading **mới nhất** (`409 METER_READING_NOT_LATEST`) và kỳ chưa `issued` (`409 PERIOD_ALREADY_INVOICED`); **không có `DELETE`**; giữ `evidence_media_id` nullable; bulk remains atomic; missing baseline → `BASELINE_REQUIRED` with full rollback (P6-D60); migration sinh ở task này.
- `P6-D66` — thêm `source: manual | ocr` (mặc định `manual`) và `ocrValue?`; giữ `buildingId`; bỏ `readingDate`; ảnh = `Media(owner_type='meter_reading', purpose='meter_reading_evidence')` upload **sau** khi tạo, FE đảm bảo có ảnh; giữ bulk. (Phần "bỏ `evidenceMediaId`" đã bị `P6-D70` sửa.)
- `P6-D67` — OCR chạy ở `ai-service` (`POST /api/v1/ai/meter-readings/ocr`); **Tenancy không gọi AI**, vẫn tự kiểm `current ≥ previous` (EC1). Gỡ `meter-readings-preview-ocr-result` khỏi Tenancy.
- `P6-D69` — upload ảnh sau khi có `readingId` thật; Identity hỏi quyền qua `GET /internal/ownership/meter_reading/{id}` (P6-11).
- `P6-D65` — chỉ số là `numeric` trong DB, string trong JSON.

## Contract (đồng bộ cùng implementation theo quyết định đã duyệt)

| Endpoint | operationId | Success | Lỗi riêng |
|---|---|---|---|
| `POST /meter-readings` | `postMeterReadings` | `201 METER_READING_CREATED` | `409 DUPLICATE_METER_READING`, `422 CURRENT_READING_INVALID`, `BASELINE_REQUIRED`, `VALIDATION_FAILED` |
| `PATCH /meter-readings/{meterReadingId}` | `patchMeterReadingsMeterreadingid` | `200 METER_READING_UPDATED` | `404 METER_READING_NOT_FOUND`, `409 PERIOD_ALREADY_INVOICED`, `409 METER_READING_NOT_LATEST`, `422 CURRENT_READING_INVALID` |

- Không có `DELETE` trong MVP (`P6-D70`) — nhập sai thì `PATCH`.
- File contract: `api-docs/src/paths/billing/meter-readings.yaml`, `meter-readings-meterReadingId.yaml`; request `api-docs/src/requests/rooms/meter-reading-create-request-dto.yaml`, `meter-reading-update-request-dto.yaml`; schema `api-docs/src/schemas/billing/meter-reading.yaml`. Cập nhật spec cùng PR implementation: bỏ `EVIDENCE_REQUIRED`, `readingDate`, `meter-readings-preview-ocr-result.yaml`; giữ `evidenceMediaId` nullable trong response.
- Role: `landlord`; phòng của landlord khác → `403`.

### Mapping field

| Request / Response field | Domain prop | Cột DB (§2.11 + `P6-D66`/`P6-D70`) | Ghi chú / validation |
|---|---|---|---|
| `source` | `source` | `source meter_reading_source_enum` NOT NULL default `manual` | `manual \| ocr` |
| `ocrValue` | `ocrValue` | `ocr_value numeric` NULL | cùng pattern `MeterValue`; `source=manual` ⇒ phải NULL (CHECK); `source=ocr` mà thiếu → `422 VALIDATION_FAILED` |
| `currentReading` | `currentReading` | `current_reading` | được khác `ocrValue` (người dùng sửa tay, `P1-D35`) |
| `evidenceMediaId` | `evidenceMediaId` | `evidence_media_id uuid` NULL | **không** bắt buộc khi tạo; gắn qua `PATCH` sau khi upload; response luôn trả (null nếu chưa có ảnh) |
| `readingDate` | — | không có cột | `P6-D66` |
| PATCH body | — | — | chỉ `currentReading?`, `evidenceMediaId?` (ít nhất 1 field); không đổi `roomId/type/period/isBaseline/source/ocrValue` |

Index: `UQ_meter_readings_room_type_period` **partial** `(room_id, type, period) WHERE is_baseline = false AND is_deleted = false`.

### Ví dụ số

| Input | Kết quả mong đợi |
|---|---|
| Phòng P102 (HĐ mới, bàn giao 01/09): baseline `2026-09` `current=1200`; reading chốt tháng `2026-09` `current=1260` | cả hai `201`; reading chốt tháng `previousReading` = **1200** (từ baseline), `consumption` = **60** |
| Phòng P101, kỳ `2026-10`: OCR gợi ý `1550`, người dùng sửa thành `1552` → POST `source=ocr, ocrValue=1550, currentReading=1552`, previous `1200` | `201`, `consumption` = **352**, `ocrValue` = `1550` lưu để audit |
| PATCH reading `2026-10` `currentReading=1540` (chưa có hóa đơn) | `200`, `consumption` = **340**; generate (g2) lại → điện tính trên 340 kWh |
| PATCH reading `2026-10` `{ evidenceMediaId }` | `200`, response có `evidenceMediaId`; `consumption` không đổi |
| PATCH `currentReading=1100` (< previous 1200) | `422 CURRENT_READING_INVALID` |
| Hóa đơn `2026-10` của phòng đã `issued`, PATCH reading `2026-10` | `409 PERIOD_ALREADY_INVOICED` |
| Đã có reading `2026-11`, PATCH reading `2026-10` | `409 METER_READING_NOT_LATEST` |
| Phòng chưa có baseline nào, POST `isBaseline=false` | `422 BASELINE_REQUIRED` |

## Tham chiếu code

- Module đang sửa: `Tenancy-Service/src/modules/meter-reading/` (handler mẫu `application/commands/meter-reading-create/meter-reading-create.command.handler.ts` — lock Room bằng `findByIdForUpdate`).
- Migration mẫu: `src/database/migrations/1793436837898-CreateBillingSettingsTable.ts`.
- Enum DB mẫu: `contract_status_enum` trong `1793335626475-CreateContractsTable.ts`.
- Kiểm tra kỳ đã phát hành: port trong module meter-reading, adapter query bảng `invoices` (`room_id`, `period`, `status='issued'`, `is_deleted=false`) — **không import module invoice** (invoice đã phụ thuộc meter-reading, import ngược sẽ vòng).

## Các bước triển khai

### Bước 1 — Thêm `source`/`ocrValue`, `evidenceMediaId` thành tùy chọn

- **Cách làm:** giữ `evidenceMediaId` ở 8 file nhưng optional/nullable, bỏ chỗ ném `EvidenceRequiredException` khi tạo; thêm enum `source`, VO cho `ocrValue` (dùng `MeterValue`), rule `manual ⇒ ocrValue null`.
- **Kiểm tra bước:** `grep -rn EvidenceRequired src` không còn kết quả; `npm run build` pass.

### Bước 2 — Migration tạo bảng `meter_readings`

- **Cách làm:** đổi unique index trong typeorm entity thành partial `WHERE is_baseline = false AND is_deleted = false`. Trước khi generate, chạy trên staging `SELECT to_regclass('public.meter_readings');` — nếu bảng đã được tạo tay, báo baoduong17 để drop (chưa có dữ liệu thật). `npm run migration:generate -- name=CreateMeterReadingsTable`, chỉ giữ phần `meter_readings` (FK room/building, unique partial, 3 CHECK hiện có + CHECK `source`/`ocr_value`, cột `evidence_media_id uuid NULL`).
- **Kiểm tra bước:** DB trống: `migration:run` → `migration:revert` → `migration:run` pass; `\d meter_readings` có `evidence_media_id`, `source` default `manual`, index unique có `WHERE (is_baseline = false AND is_deleted = false)`.

### Bước 3 — `POST /meter-readings`: baseline kỳ đầu + `source`/`ocrValue`

- **Cách làm:** `isBaseline=false` lấy `previous` = reading mới nhất (chưa xóa) của `(room, type)` có `period < kỳ` **hoặc** là baseline cùng kỳ (baseline xếp trước reading thường cùng kỳ). Không có gì → `422 BASELINE_REQUIRED`. Để kiểm tra này ở chỗ bulk (P6-02f) gọi lại được theo từng item.
- **Kiểm tra bước:** dòng 1, 2 và dòng cuối bảng Ví dụ số; `source: "manual", ocrValue: "1550"` → `422 VALIDATION_FAILED`; POST lại reading chốt tháng `2026-09` → `409 DUPLICATE_METER_READING`.

### Bước 4 — `PATCH` có khóa kỳ

- **Cách làm:** UoW: lock Room → load reading (`404`) → check landlord (`403`) → port "kỳ đã phát hành" → `409 PERIOD_ALREADY_INVOICED` → reading không phải mới nhất của `(room, type)` (baseline cùng kỳ tính là cũ hơn reading thường) → `409 METER_READING_NOT_LATEST` → gán `currentReading` (tính lại; baseline retains the landlord-supplied `previousReading` under P6-D60) và/hoặc `evidenceMediaId`; `current < previous` → `422`. Outbox `meter_reading.updated`.
- **Kiểm tra bước:** dòng 3–7 bảng Ví dụ số. Giả lập phát hành bằng SQL nếu g3 chưa xong: `UPDATE invoices SET status='issued', issued_at=now() WHERE room_id='<P101>' AND period='2026-10'`.

### Bước 5 — Swagger + api-docs

- **Kiểm tra bước:** Swagger hiện POST/GET/PATCH, không có DELETE, không còn route `preview-ocr-result`; `npm run build` + `npm run lint` pass.

## Ngoài phạm vi

- `ai-service` và endpoint OCR (`P6-D67`, task riêng). Upload ảnh minh chứng (FE P6-06b + Identity Media, `P6-D69`); `GET /internal/ownership` (P6-11).
- Bulk: P6-02f tự áp dụng `P6-D66`/`P6-D70` khi làm (`source`/`ocrValue` mỗi dòng; a missing baseline returns `BASELINE_REQUIRED` and rolls back the entire bulk request (P6-D60)).
- `DELETE` reading và sửa reading không phải mới nhất (cascade `previous_reading` kỳ sau) — `P6-D70` không làm trong MVP.

## Blocker

- Không có.

## Cập nhật `api-docs` (bắt buộc trước khi đóng issue)

- [ ] Sequence diagram PATCH (lock Room → check kỳ đã phát hành → check mới nhất → save + outbox).
- [ ] `x-apidog-status: released` cho POST/PATCH; `npm run bundle`.

## Acceptance (Apidog)

- [ ] DB trống + `migration:run` → `POST /meter-readings` chạy được (`201 METER_READING_CREATED`).
- [ ] Baseline + reading chốt tháng cùng kỳ đầu → `consumption` = current − baseline (không phải 0).
- [ ] `source=ocr` + `ocrValue` lưu và trả về; `manual` + `ocrValue` → `422 VALIDATION_FAILED`.
- [ ] PATCH `currentReading` / `evidenceMediaId` kỳ chưa phát hành → `200`; kỳ đã phát hành → `409 PERIOD_ALREADY_INVOICED`; không phải mới nhất → `409 METER_READING_NOT_LATEST`.
- [ ] Phòng chưa có baseline → `422 BASELINE_REQUIRED`.
- [ ] Phòng landlord khác → `403`; id lạ → `404 METER_READING_NOT_FOUND`; token tenant → `403`.

## Definition of Done

- [ ] Mọi bước qua phần Kiểm tra bước; mọi ô Acceptance được **tick bởi người làm**, kèm export Apidog trong PR.
- [ ] `npm run build` + `npm run lint` pass; không có file test, không sửa `src/shared`.
- [ ] Migration sinh bằng `migration:generate`, `migration:run` + `migration:revert` pass từ DB trống.
- [ ] PR vào `main` ghi `Closes pbl6-home-renter/docs#78`, baoduong17 approve.
