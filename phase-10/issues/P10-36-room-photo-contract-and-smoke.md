# P10-36 — Đồng bộ contract ảnh phòng và kiểm tra ảnh thật

**Trạng thái:** 🟡 Open — plan ngày 18/11/2026  
**Ưu tiên:** P1 · **Repo:** api-docs, Tenancy-Service/Identity-Service nếu smoke phát hiện lỗi  
**Owner đề xuất:** API / Media owner · **Phụ thuộc:** Không · **Scope:** M; sửa lỗi runtime phát hiện thêm bằng PR riêng

## Mục tiêu và cách sửa

A2: list runtime dùng photoMediaIds/photoUrls, spec list còn thumbnailUrl; cả 4 phòng public chưa gắn media. Chốt photoUrls list/detail theo yêu cầu, cập nhật source schema/ví dụ và bundle. Đối chiếu client trước khi loại thumbnailUrl. Chuẩn bị phòng test có ảnh thật qua presign → PUT bytes → complete → attach photoMediaIds; owner phải là phòng tồn tại và landlord đúng quyền. Đọc URL do Media cấp, không tự ghép URL storage.

## Acceptance

- [ ] Spec/bundle khớp photoUrls và photoMediaIds thực tế; ảnh rỗng trả mảng rỗng; client cũ dùng thumbnailUrl có phương án tương thích đã kiểm tra.
- [ ] Có ít nhất một phòng test gắn media đã uploaded; URL ảnh list/detail GET được nội dung ảnh thật không token, đúng content type và quyền public của room photo.
- [ ] Media khác owner/chưa complete/không đúng purpose không làm lộ ảnh; nếu lookup/fallback trả đường dẫn metadata thay bytes phải tách lỗi runtime để sửa và kiểm chứng lại.

## Verification

api-docs lint/bundle; smoke bằng landlord test hợp lệ, GET anonymous URL và render trên tenant. Chỉ 401 không chứng minh route Media tồn tại vì middleware có thể trả trước routing. Lưu evidence media ID/phòng test và status, không lưu signed upload URL/token dài hạn.

**File dự kiến:** list schema, room paths/examples, generated bundle và smoke evidence/runbook. Chưa kết luận upload UI landlord thiếu trong bản mobile đang chạy vì source local chỉ là scaffold; feature upload UI được lên follow-up riêng khi có source đúng.

**Tham chiếu:** A2, [plan](../../tasks/plan.md).
