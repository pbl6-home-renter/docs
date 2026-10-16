# P4-17 — Khảo sát Google Stitch và đề xuất nền tảng giao diện

**Trạng thái:** 🟡 Open  
**Người phụ trách:** FE member  
**Người review:** FE Lead, PM  
**Ước lượng:** 5 points · 8–12 giờ  
**Độ ưu tiên:** High / Blocker cho P4-18 và P4-19

## Bối cảnh

Frontend đã có một số component và layout ban đầu. Trước khi triển khai F1/F2 cần xác định những gì Google Stitch đã cung cấp và phần nào nên đưa về codebase dùng chung. Nếu bỏ qua bước này, mỗi member có thể tự tạo Button, Card, Table hoặc Layout khác nhau.

## Yêu cầu task

Member chủ động inspect các project Google Stitch và design reference của Rentify. Không áp đặt trước danh sách component phải làm. Sau khi khảo sát, member tự lập danh sách và đề xuất phạm vi triển khai.

## Nội dung cần tự đánh giá

- Design token cần chuẩn hóa.
- Base component xuất hiện lặp lại.
- Layout và navigation pattern dùng chung được.
- Component chỉ thuộc feature và không nên đưa vào shared UI.
- Khác biệt giữa Tenant, Landlord và Admin shell.
- Loading, empty, error, disabled và validation state cần hỗ trợ.
- Phần có thể reuse và phần cần viết lại theo kiến trúc hiện tại.

## Kết quả bàn giao

- Ghi chú khảo sát do member tự lập.
- Danh sách đề xuất base component, token, layout và page pattern.
- Phân loại shared component và feature-specific component.
- Đề xuất phạm vi cụ thể cho P4-18 và P4-19.
- Các điểm chưa rõ cần PM/FE Lead quyết định.

## Tiêu chí nghiệm thu

- FE Lead và PM review kết quả khảo sát.
- Có quyết định phần nào được code trong foundation.
- F1/F2 chỉ bắt đầu sau khi phạm vi nền tảng được chốt.
- Task này không yêu cầu triển khai toàn bộ component.

---

## 1. Cách thực hiện đề xuất

### Bước 1 — Thu thập design reference

- [ ] Mở và phân loại các project Google Stitch hiện có.
- [ ] Xác định project thuộc Tenant, Landlord hay Admin.
- [ ] Ghi lại các màn hình đại diện cho dashboard, form, list, detail và empty state.
- [ ] Đối chiếu với `pm/phase-2/discovery/Rentify_Stitch_Prompts_Web.md`.

### Bước 2 — Tìm pattern lặp lại

- [ ] Ghi nhận component xuất hiện ở nhiều màn hình.
- [ ] Ghi nhận variant, size, trạng thái và behavior của từng component.
- [ ] Ghi nhận token về màu, font, spacing, radius, shadow và breakpoint.
- [ ] Phân biệt component dùng chung với component chỉ thuộc một feature.

### Bước 3 — Đề xuất phạm vi code

- [ ] Tự lập inventory theo primitive, composite, layout và page pattern.
- [ ] Đề xuất thứ tự ưu tiên theo nhu cầu F1/F2.
- [ ] Ước lượng component cần code mới và component có thể reuse.
- [ ] Nêu rõ phần chưa đủ thông tin cần PM/FE Lead quyết định.

## 2. Mẫu kết quả cần bàn giao

| Nhóm | Tên/pattern | Dùng ở đâu | Đề xuất | Ghi chú |
|---|---|---|---|---|
| Primitive | ... | ... | Code/reuse/defer | ... |
| Composite | ... | ... | Code/reuse/defer | ... |
| Layout | ... | ... | Code/reuse/defer | ... |

Member được điều chỉnh format bảng, nhưng phải thể hiện lý do ưu tiên và mối liên hệ với F1/F2.

## 3. Tiêu chí review

- Không chỉ copy ảnh hoặc link Stitch mà thiếu phân tích khả năng triển khai.
- Không biến task research thành task code toàn bộ UI.
- Đề xuất phải phù hợp cấu trúc hiện tại của `fe/`.
- Kết quả phải giúp FE Lead chia P4-18/P4-19 thành phần việc cụ thể.
