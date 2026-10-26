# P6-06 — Màn hình Contract, Meter reading và Invoice cho landlord (Web)

**Trạng thái:** ⚪ Outline (viết chi tiết trong It5)  
**Người phụ trách:** ThaiBao11125  
**Người review:** baoduong17  
**Ước lượng:** ~13 points · 30–40 giờ (ước tính sơ bộ, sẽ tách sub-issue)  
**Phụ thuộc:** P6-03 (pattern màn hình CRUD), P6-01a–d, P6-02 (API sẵn sàng trên staging)  
**Iteration:** It6 (09/11–15/11)

## Mục tiêu

Landlord thao tác trọn vòng đời trên Web: tạo hợp đồng từ mẫu → tải bản nháp → upload bản ký → kích hoạt; nhập chỉ số điện nước (đơn lẻ/bulk); phát hành và xem hóa đơn; ghi nhận thu tiền mặt.

## Phạm vi dự kiến (sub-issue khi viết chi tiết)

| Sub | Màn hình | API |
|---|---|---|
| a | Danh sách và chi tiết hợp đồng; wizard tạo hợp đồng (chọn phòng → mẫu → thông tin) | `contracts`, `contract-templates`, `apply-template` |
| b | Tải bản nháp, upload bản ký (media presign), kích hoạt | `generate-draft-document`, `media/*` (P6-04), `activate-contract` |
| c | Cấu hình đơn giá và billing setting của toà; nhập chỉ số đơn lẻ/bulk | `rate-policies`, `billing-settings`, `meter-readings`, `meter-readings/bulk` |
| d | Danh sách và chi tiết hóa đơn, phát hành, hủy, ghi nhận tiền mặt | `invoices*`, `payments/record-cash-payment` (P6-05) |

## Ghi chú khi viết chi tiết

- Dùng lại API client, query/mutation và form foundation từ P5-02…P5-06, và pattern màn hình từ P6-03.
- Đối chiếu `phase-1/discovery/user_flow/landlord_user_flow.md` và `phase-2/discovery/Rentify_UI_Screen_Outline_v0.1.md`.
- Thông báo UI dùng API `code` + i18n (quy định Phase 5).
