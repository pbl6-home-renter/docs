# P6-02 — Billing vertical slice (Epic)

> Nhóm Billing trong `tenancy-service`: đơn giá & phí định kỳ (`RatePolicy`), ngày thu dự kiến (`BillingSetting`), chốt chỉ số điện nước (`MeterReading`), và — ở Iteration 6 — hóa đơn (`Invoice`) cùng OCR preview.

**Trạng thái:** 🟡 Open  
**Người phụ trách:** huynhtiennhat0403  
**Người review:** baoduong17 (BE Lead, API owner), PM  
**Ước lượng:** 20 points cho It5 (P6-02a → P6-02f); It6 ước lượng lại khi viết chi tiết P6-02g/h  
**Độ ưu tiên:** High  
**Phụ thuộc:** P5-09 (bảng `rooms` + Room API), P5-08b (pattern UoW + Outbox)  
**Issue:** `docs#TBD`

## Bối cảnh

MVP lõi cần luồng **chốt số → sinh hóa đơn → ghi nhận thanh toán** chạy end-to-end (`requirement.md`, D29 landlord-solo). Billing là điều kiện đầu vào của Invoice: thiếu bộ đơn giá hoặc thiếu chỉ số thì không lập được hóa đơn (`utility-billing-calculations.md` §11 EC2/EC3).

Issue này là issue cha. Công việc thực tế giao qua các sub-issue; issue cha chỉ đóng khi mọi sub-issue It5 Done (P6-02g/h có thể chuyển sang epic riêng nếu It6 thay đổi).

## Sub-issue

| ID | Task | Endpoint | Iteration | Estimate | Phụ thuộc |
|---|---|---|---|---|---|
| [P6-02a](P6-02a-billing-contract-alignment.md) | Chốt contract Billing theo D39 | — (`api-doc`) | It5 | 2 pts | — |
| [P6-02b](P6-02b-rate-policy-domain-persistence.md) | RatePolicy domain và persistence | — | It5 | 3 pts | P6-02a |
| [P6-02c](P6-02c-rate-policy-api.md) | API RatePolicy (tạo, batch tòa, sửa, tắt, liệt kê) | `GET/POST /rate-policies`, `PATCH /rate-policies/{id}`, `POST /rate-policies/{id}/deactivate-policy`, `POST /buildings/{id}/rate-policies/batch` | It5 | 5 pts | P6-02b, P5-09b |
| [P6-02d](P6-02d-billing-setting.md) | BillingSetting domain + API | `GET/POST /billing-settings`, `PATCH /billing-settings/{id}` | It5 | 3 pts | P6-02a, P6-02c (pattern) |
| [P6-02e](P6-02e-meter-reading-create-list.md) | MeterReading domain + nhập tay từng chỉ số + liệt kê | `POST /meter-readings`, `GET /meter-readings` | It5 | 5 pts | P6-02a, P5-09b |
| [P6-02f](P6-02f-meter-reading-bulk.md) | Chốt chỉ số hàng loạt theo tòa | `POST /meter-readings/bulk` | It5 | 2 pts | P6-02e |
| [P6-02g](P6-02g-invoice-outline.md) | Invoice: sinh pending, phát hành, xem, hủy, tenant xem *(outline)* | `/invoices/*` | It6 | ~13 pts | P6-02c, P6-02e, epic Contract (`contracts` + `contract_members`) |
| [P6-02h](P6-02h-meter-reading-ocr-preview.md) | OCR preview chỉ số *(outline, chờ chốt OCR)* | `POST /meter-readings/preview-ocr-result` | It6 | ~5 pts | P6-02e, Media upload, quyết định OCR |

Thứ tự It5: `P6-02a → P6-02b → P6-02c → (P6-02d ∥ P6-02e) → P6-02f`.

> **P6-02a phải merge trước** khi code P6-02b/d/e: contract hiện tại của RatePolicy/BillingSetting mâu thuẫn với D39 và giữa các endpoint với nhau (chi tiết trong P6-02a).

## Ngoài phạm vi epic này (It5)

- Sinh/phát hành hóa đơn, tính tiền (thuộc P6-02g, It6).
- OCR (P6-02h); lưu liên kết ảnh chứng cứ vào `media` — media flow do baoduong17 làm song song; It5 chỉ nhận `evidenceMediaId` và để `TODO(media)`.
- `GET /invoices/overdue-debts`, `POST /invoices/send-reminder`, reminder channel SMS/Zalo — trái D39 (không cưỡng chế thu tiền) hoặc ngoài MVP.
- `PUT /buildings/{id}/vietqr-config` — thuộc nhóm Payment.

## Tiêu chí nghiệm thu chung (mọi sub-issue có write operation)

- Aggregate và outbox row ghi trong cùng transaction (`IUnitOfWork.run`); rollback không để lại dữ liệu dở dang.
- `landlord_id` lấy từ JWT; mọi thao tác trên building/room kiểm tra quyền sở hữu (`landlordId === user.id`) → sai thì `403 FORBIDDEN`.
- Tiền và chỉ số dùng `numeric`/string trong DB và API — **cấm float** (`utility-billing-calculations.md` §0).
- Route, schema, error code khớp `api-doc` sau P6-02a; endpoint đã verify có sequence diagram và `x-apidog-status: released`.
- Manual verification ghi lại trong PR; PR ghi `Closes pbl6-home-renter/docs#<số issue>`.

## Cấu trúc module đề xuất (`Tenancy-Service`)

Theo cách tổ chức per-aggregate hiện có (`src/modules/building`, `src/modules/room`):

```text
src/modules/rate-policy/      ← P6-02b, P6-02c
src/modules/billing-setting/  ← P6-02d
src/modules/meter-reading/    ← P6-02e, P6-02f
```

Kiểm tra quyền sở hữu Building/Room bằng cách import `BuildingModule` / `RoomModule` (đã export `BUILDING_DI_TOKEN.REPOSITORY`, `ROOM_DI_TOKEN.REPOSITORY`).

## Nguồn tham chiếu

- `pm/phase-1/discovery/database-design.md` §2.9–§2.12.
- `pm/phase-1/discovery/utility-billing-calculations.md` (§0 quy ước, §1 ma trận rate kind, §4 resolve, §11 edge case, §12 D31–D33).
- `api-doc/src/paths/billing/*.yaml`, `api-doc/src/paths/buildings/buildings-buildingId-rate-policies-batch.yaml`, `api-doc/src/paths/invoices/*.yaml`.
- Slice mẫu: [P5-08b](../../phase-5/issues/P5-08b-building-create-command.md).
