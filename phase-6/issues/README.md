# Phase 6 — Task tracker

Use [`_TEMPLATE.md`](_TEMPLATE.md) v2. Each task links to its GitHub issue; assignees below follow the task documents. GitHub issue states were checked on 2026-11-01. A split parent remains open until its implementation sub-issues are complete.

## Decisions and prerequisites

- [Published P6-D60](../discovery/decisions.md): baseline inputs and **atomic bulk** (PR #94). One invalid reading rolls back the whole request; successful responses contain only `SUCCESS` results.
- [P6-D61–D78](../decisions.md): Payment/deposit settlement deferred; Contract, Invoice, manual MeterReading, media and tenant-linking decisions. P6-D75 defines source precedence; P6-D78 removes OCR from the MVP.
- P6-11 and P6-12 are Done per PM confirmation. The merged P6-02h/g1–g4 backend changes are synchronized with `api-doc` in separate documentation PRs. P6-10a/b were removed from the active tracker.
- It5: 02/11–08/11. It6: 09/11–15/11. It7: 16/11–22/11. P6-06d may move to It7 only after PM confirmation.
- Project #3 field synchronization is pending: the current GitHub credentials do not grant Projects access. This table records the intended iterations; it does not claim those fields were applied remotely.

## Iteration 5 — core work and prerequisites

| ID / GitHub | Task | Assignee | Estimate | Status | Dependencies |
|---|---|---|---|---|---|
| [P6-01](P6-01-tenancy-contract-vertical-slice.md) · [#64](https://github.com/pbl6-home-renter/docs/issues/64) | Contract vertical slice (Epic) | leminhkhai345 | 18 It5 + 8 It6 | 🟡 Open | P5-08, P5-09, P6-04 |
| [P6-01a](P6-01a-contract-domain-persistence.md) · [#65](https://github.com/pbl6-home-renter/docs/issues/65) | Contract domain model, persistence và migration | leminhkhai345 | 3 points | 🟢 Done | P5-09a |
| [P6-01b](P6-01b-contract-create-and-manage-draft.md) · [#66](https://github.com/pbl6-home-renter/docs/issues/66) | Tạo và quản lý hợp đồng nháp | leminhkhai345 | 5 points | 🟢 Done | P6-01a, P5-09b |
| [P6-01c](P6-01c-contract-template-and-draft-document.md) · [#67](https://github.com/pbl6-home-renter/docs/issues/67) | Mẫu hợp đồng, áp mẫu và sinh tài liệu nháp | leminhkhai345 | 5 points | 🟢 Done | P6-01b, P6-04 |
| [P6-01d](P6-01d-contract-activate-signed-file.md) · [#68](https://github.com/pbl6-home-renter/docs/issues/68) | Upload bản ký và kích hoạt hợp đồng | leminhkhai345 | 5 points | 🟡 Open | P6-01b, P6-04, P6-12 |
| [P6-02](P6-02-tenancy-billing-vertical-slice.md) · [#70](https://github.com/pbl6-home-renter/docs/issues/70) | Billing vertical slice (Epic) | leminhkhai345 | 20 It5 + 14 It6 | 🟡 Open | P5-09, P5-08b |
| [P6-02a](P6-02a-billing-contract-alignment.md) · [#71](https://github.com/pbl6-home-renter/docs/issues/71) | Chốt contract Billing theo D39 | leminhkhai345 | 2 points | 🟡 Open | — |
| [P6-02b](P6-02b-rate-policy-domain-persistence.md) · [#72](https://github.com/pbl6-home-renter/docs/issues/72) | RatePolicy domain và persistence | leminhkhai345 | 3 points | 🟡 Open | P6-02a |
| [P6-02c](P6-02c-rate-policy-api.md) · [#73](https://github.com/pbl6-home-renter/docs/issues/73) | API RatePolicy (tạo, batch tòa, sửa, tắt, liệt kê) | leminhkhai345 | 5 points | 🟡 Open | P6-02b, P5-09b, P5-08b |
| [P6-02d](P6-02d-billing-setting.md) · [#74](https://github.com/pbl6-home-renter/docs/issues/74) | BillingSetting domain + API | leminhkhai345 | 3 points | 🟡 Open | P6-02a, P6-02c |
| [P6-02e](P6-02e-meter-reading-create-list.md) · [#75](https://github.com/pbl6-home-renter/docs/issues/75) | MeterReading: nhập tay từng chỉ số và liệt kê | leminhkhai345 | 5 points | 🟡 Open | P6-02a, P5-09b |
| [P6-02f](P6-02f-meter-reading-bulk.md) · [#76](https://github.com/pbl6-home-renter/docs/issues/76) | Chốt chỉ số hàng loạt theo tòa | leminhkhai345 | 2 points | 🟡 Open | P6-02e |
| [P6-03](P6-03-fe-landlord-building-room-screens.md) · [#79](https://github.com/pbl6-home-renter/docs/issues/79) | Màn hình Building/Room cho Landlord và duyệt Building cho Admin (Epic) | ThaiBao11125 | 18 points tổng (P6-03a 5 | 🟢 Done | P5-01, P5-07, P5-08, P5-09, P6-04, P6-03b |
| [P6-03a](P6-03a-fe-building-api-list-detail.md) · [#80](https://github.com/pbl6-home-renter/docs/issues/80) | Building API layer, danh sách và chi tiết Building của tôi | ThaiBao11125 | 5 points | 🟢 Done | P5-08c |
| [P6-03b](P6-03b-fe-building-create-edit-delete.md) · [#81](https://github.com/pbl6-home-renter/docs/issues/81) | Wizard tạo Building, sửa và xóa Building | ThaiBao11125 | 5 points | 🟢 Done | P6-03a, P5-08b, P5-08c, P5-08f, P6-04 |
| [P6-03c](P6-03c-fe-room-list-create-edit.md) · [#82](https://github.com/pbl6-home-renter/docs/issues/82) | Danh sách, tạo, sửa, xóa Room trong một Building | ThaiBao11125 | 5 points | 🟢 Done | P6-03a, P5-09b, P5-09c |
| [P6-03d](P6-03d-fe-admin-building-approval.md) · [#83](https://github.com/pbl6-home-renter/docs/issues/83) | Admin duyệt/từ chối Building | ThaiBao11125 | 3 points | 🟢 Done | P6-03a, P5-08d |
| [P6-04](P6-04-identity-media-presign-upload.md) · [#84](https://github.com/pbl6-home-renter/docs/issues/84) | Media upload 2 bước (presign → PUT → complete) và đọc/xóa media | baoduong17 | 8 points | 🟡 Open | P6-03b, P6-03d |
| [P6-08](P6-08-tenancy-administrative-units.md) · [#89](https://github.com/pbl6-home-renter/docs/issues/89) | Local administrative geography API (Tenancy) | baoduong17 | 3 points | 🟢 Done | — |
| [P6-11](P6-11-tenancy-internal-ownership.md) · [#110](https://github.com/pbl6-home-renter/docs/issues/110) | Tenancy: `GET /internal/ownership/{ownerType}/{ownerId}` cho Media | baoduong17 | 2 points | 🟢 Done | P6-01e1, P6-02h |
| [P6-12](P6-12-identity-internal-media-lookup.md) · [#111](https://github.com/pbl6-home-renter/docs/issues/111) | Identity: `GET /internal/media/{mediaId}` cho service nội bộ | baoduong17 | 1 point | 🟢 Done | P6-04 |

## Iteration 6 — implementation backlog

| ID / GitHub | Task | Assignee | Estimate | Status | Dependencies |
|---|---|---|---|---|---|
| [P6-01e](P6-01e-contract-members-and-checkout.md) · [#69](https://github.com/pbl6-home-renter/docs/issues/69) | Thành viên HĐ, HĐ của tenant, checkout (đã tách) | leminhkhai345 | 8 points (tổng e1–e3) | 🟡 Open · split | P6-01d |
| [P6-01e1](P6-01e1-contract-members.md) · [#95](https://github.com/pbl6-home-renter/docs/issues/95) | Thành viên hợp đồng: bảng, tự thêm đại diện khi activate, API thêm/xem/sửa/rời | leminhkhai345 | 3 points | 🟡 Open | P6-01d |
| [P6-01e2](P6-01e2-tenant-my-contracts.md) · [#96](https://github.com/pbl6-home-renter/docs/issues/96) | Tenant xem hợp đồng của mình (`GET /me/contracts`) | leminhkhai345 | 2 points | 🟡 Open | P6-01e1 |
| [P6-01e3](P6-01e3-contract-checkout.md) · [#97](https://github.com/pbl6-home-renter/docs/issues/97) | Checkout: kết thúc hợp đồng, member rời, phòng chuyển `maintenance` (+ sửa số xe khi HĐ `active`) | leminhkhai345 | 3 points | 🟡 Open | P6-01e1, P6-01d, P6-02g1 |
| [P6-02g](P6-02g-invoice-outline.md) · [#77](https://github.com/pbl6-home-renter/docs/issues/77) | Invoice: sinh theo tòa + kỳ, phát hành, hủy, tenant xem (issue cha) | leminhkhai345 | 11 points (tổng sub-issue) | Backend merged; docs/gateway pending | P6-02c, P6-02e, P6-02h, P6-01e1, P6-01e2 |
| [P6-02g1](P6-02g1-invoice-domain-calculator.md) · [#98](https://github.com/pbl6-home-renter/docs/issues/98) | Invoice: aggregate, bảng `invoices` và calculator tính tiền thuần | leminhkhai345 | 3 points | Backend merged | P6-02c, P6-02e |
| [P6-02g2](P6-02g2-invoice-generate.md) · [#99](https://github.com/pbl6-home-renter/docs/issues/99) | Invoice: sinh / tính lại hóa đơn `pending` theo tòa + kỳ | leminhkhai345 | 3 points | Backend merged; docs pending | P6-02g1, P6-02h, P6-01e1 |
| [P6-02g3](P6-02g3-invoice-landlord-manage.md) · [#100](https://github.com/pbl6-home-renter/docs/issues/100) | Invoice: landlord xem, sửa phí khác, phát hành hàng loạt, hủy | leminhkhai345 | 3 points | Backend merged; docs pending | P6-02g2 |
| [P6-02g4](P6-02g4-invoice-tenant-view.md) · [#101](https://github.com/pbl6-home-renter/docs/issues/101) | Invoice: tenant xem hóa đơn của mình | leminhkhai345 | 2 points | Tenancy merged; gateway pending | P6-02g3, P6-01e2, P6-01e1 |
| [P6-02h](P6-02h-meter-reading-ocr-preview.md) · [#78](https://github.com/pbl6-home-renter/docs/issues/78) | MeterReading: manual entry, baseline, optional image evidence, PATCH with issued-period lock | leminhkhai345 | 3 points | Backend merged; docs pending | P6-02g1, P6-02g2 |
| [P6-06](P6-06-fe-contract-invoice-screens.md) · [#86](https://github.com/pbl6-home-renter/docs/issues/86) | Màn Hợp đồng, Chỉ số điện nước và Hóa đơn cho landlord (Web) — Epic | ThaiBao11125 | 12 points | 🟡 Open · split | P6-03c, P6-01b, P6-02e, P6-02g1 |
| [P6-06a](P6-06a-fe-contract-list-create-activate.md) · [#102](https://github.com/pbl6-home-renter/docs/issues/102) | Danh sách, tạo hợp đồng nháp, áp mẫu và kích hoạt hợp đồng (Web) | ThaiBao11125 | 3 points | 🟡 Open | P6-01b, P6-01c, P6-01d, P6-03c |
| [P6-06b](P6-06b-fe-meter-reading-entry.md) · [#103](https://github.com/pbl6-home-renter/docs/issues/103) | Nhập tay chỉ số điện nước theo tòa và kỳ, ảnh minh chứng tùy chọn (Web) | ThaiBao11125 | 3 points | 🟡 Open | P6-02e, P6-02f, P6-02h, P6-03c |
| [P6-06c](P6-06c-fe-invoice-screens.md) · [#104](https://github.com/pbl6-home-renter/docs/issues/104) | Sinh, xem, sửa phí khác, phát hành và hủy hóa đơn (Web) | ThaiBao11125 | 3 points | 🟡 Open | P6-02g1, P6-06b, P6-06a, P6-01e3 |
| [P6-06d](P6-06d-fe-contract-members-checkout.md) · [#105](https://github.com/pbl6-home-renter/docs/issues/105) | Thành viên hợp đồng và trả phòng (Web) | ThaiBao11125 | 3 points | 🟡 Open | P6-06a, P6-01e1, P6-01e3, P6-03c |
| [P6-07](P6-07-demo-seed-and-staging.md) · [#87](https://github.com/pbl6-home-renter/docs/issues/87) | Seed dữ liệu demo, chốt staging, kịch bản demo | baoduong17 | 3 points | 🟡 Open | P6-01e1, P6-02g1, P6-11 |

## Stretch — outside Phase 6 MVP

| ID / GitHub | Task | Assignee | Estimate | Status | Dependencies |
|---|---|---|---|---|---|
| [P6-05](P6-05-payment-cash-mock.md) · [#85](https://github.com/pbl6-home-renter/docs/issues/85) | Ghi nhận thanh toán tiền mặt / mock cho hóa đơn | baoduong17 | ~8 points | ⏪ Deferred | P6-02 |

## Dependency order

- Contract: `P6-01a → P6-01b → (P6-01c ∥ P6-01d) → P6-01e1 → (P6-01e2 ∥ P6-01e3)`. Activation prerequisite P6-12 is Done; checkout also requires P6-02g1.
- Billing It5: `P6-02a → P6-02b → P6-02c → P6-02d`; readings e/f follow the aligned contract and Room API.
- Web: `P6-06a → P6-06d`; meter entry b and contract a can proceed independently; invoice c follows b and the active-contract update in e3.
- Demo P6-07 follows the core integrations and uses manual meter input with optional image evidence. Payment is not a demo dependency.

## Tracking convention

Keep task documents, this table and GitHub issues consistent. Implementation PRs use `Closes pbl6-home-renter/docs#<number>`. A documentation PR references implementation issues without closing them. Community Service remains a design proposal; implementation issues require design gates A–C to be approved first.
