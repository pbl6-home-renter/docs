# P10-06 — Khôi phục luồng áp mẫu và sinh hợp đồng nháp

**Loại:** Regression · **Ưu tiên đề xuất:** High · **Trạng thái:** 🔵 In progress — đã merge, chờ nghiệm thu  
**Owner đề xuất:** `leminhkhai345` · **Reviewer:** BE Lead / API owner · **Repo:** `Tenancy-Service`, `api-docs`, `fe`  
**Phụ thuộc:** P6-01c, P6-04 · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## Cập nhật triển khai 14/11/2026

PM đã chốt D5: sinh nháp trả trực tiếp 200 application/pdf, không lưu Media. [Apply Tenancy #48](https://github.com/pbl6-home-renter/Tenancy-Service/pull/48), [PDF Tenancy #51](https://github.com/pbl6-home-renter/Tenancy-Service/pull/51), [API docs #62](https://github.com/pbl6-home-renter/api-doc/pull/62), [API docs #65](https://github.com/pbl6-home-renter/api-doc/pull/65) và [FE #42](https://github.com/pbl6-home-renter/fe/pull/42) đã merge. Còn chạy migration và kiểm tra apply → tải PDF qua Gateway với quyền và dữ liệu thật.

## Bối cảnh và vấn đề

P6-01c/`docs#67` ghi Done và mô tả bốn operation hợp đồng mẫu. Tại baseline Tenancy `3f91141`, controller có hai GET template nhưng thiếu route `PUT /contracts/{contractId}/apply-template` và `POST /contracts/{contractId}/generate-draft-document`; FE vẫn gọi hai API này. Các PR triển khai hiện đã merge như ghi ở trên, nhưng chưa có bằng chứng kiểm thử deployment/Gateway.

## User story

Là chủ nhà, tôi muốn áp mẫu vào hợp đồng nháp và tải tài liệu nháp để in, ký tay rồi upload bản đã ký theo D18. Tài liệu phải gắn đúng hợp đồng và không thể áp/sinh từ hợp đồng của chủ nhà khác.

## Contract và rule

| Operation | Điều kiện | Kết quả |
|---|---|---|
| `PUT /contracts/{contractId}/apply-template` | landlord sở hữu contract draft, template tồn tại | 200 `CONTRACT_TEMPLATE_APPLIED` theo schema hiện hành |
| `POST /contracts/{contractId}/generate-draft-document` | contract draft, dữ liệu render hợp lệ | 200 `application/pdf` binary, không lưu Media (D5) |
| Một trong hai operation cho contract không phải draft | đã xác thực và có quyền | 409 theo OpenAPI |

D18: ký tay và upload bản ký; không bổ sung OTP, ký số hoặc tự kích hoạt. PM đã chốt D5 cho cách trả tài liệu nháp.

## Các bước triển khai

1. Đối chiếu PR/commit P6-01c, contract YAML và route runtime trên nhánh tích hợp; ghi chứng cứ route thực tế. D5 chọn trả PDF trực tiếp, không cần adapter lưu Media cho bản nháp.
2. Nếu route thật sự thiếu, khôi phục command apply, kiểm tra template/draft/ownership trong transaction, lưu lựa chọn theo domain hiện tại; đăng ký controller, DI và mapping error. **Kiểm tra:** apply mẫu hợp lệ trả 200 và reload contract phản ánh mẫu; template không tồn tại trả lỗi theo docs.
3. Sinh PDF từ dữ liệu contract được phép và validate biến; trả trực tiếp file binary, không lưu Media (D5). **Kiểm tra:** tải được PDF đúng owner; thiếu dữ liệu bắt buộc trả lỗi rõ ràng.
4. FE thử lại hai bước, loading/retry và thông báo lỗi qua interceptor. Đồng bộ request/response/sequence diagram `api-docs`, bundle và link hai PR. **Kiểm tra:** UI tạo draft → áp mẫu → sinh và tải file; active/owner khác bị từ chối.
5. Test backend cho authorization, trạng thái và biến thiếu; build/lint các repo liên quan, kiểm tra thủ công Gateway. Chia PR khi vượt giới hạn.

## Acceptance

- Hai API có contract và behavior nhất quán, PDF được trả trực tiếp, không tạo media giả; không thay đổi trạng thái contract ngoài rule được duyệt.
- User khác không đọc/sửa document; contract active, template sai và dữ liệu thiếu được xử lý đúng, không ghi dữ liệu dang dở gây hiểu nhầm.
- Có bằng chứng truy vết P6-01c, API test, PDF mẫu đã ẩn dữ liệu cá nhân và kết quả FE integration. Kiểm tra tải PDF trực tiếp qua Gateway theo D5.
