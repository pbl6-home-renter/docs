# P10-04 — Tìm tòa trên toàn bộ danh sách được phép xem

> **Quyết định PM D4:** Dùng filter[search] theo contract bên dưới.

**Trạng thái:** 🟢 Done — code đã merge · **Owner đề xuất:** BE `leminhkhai345`, FE `ThaiBao11125` · **Reviewer:** BE/FE Lead

**Repo:** `Tenancy-Service`, `api-docs`, `fe` · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD` · **Phụ thuộc:** P5-08c, P6-03a.

## Cập nhật triển khai 14/11/2026

PM đã chốt D4 `filter[search]`. [Tenancy #50](https://github.com/pbl6-home-renter/Tenancy-Service/pull/50), [API docs #64](https://github.com/pbl6-home-renter/api-doc/pull/64) và [FE #43](https://github.com/pbl6-home-renter/fe/pull/43) đã merge. FE đã kiểm tra build, lint, i18n và tìm kiếm nhiều trang, ký tự đặc biệt bằng API giả lập; chưa kiểm tra Gateway với dữ liệu thật.

## Bối cảnh và contract

`use-building-list.ts` chỉ tải tối đa 100 tòa đầu rồi lọc tên/địa chỉ ở client. Kết quả sau tòa thứ 100 không thể tìm thấy, pagination và count cũng không phản ánh toàn bộ. Thêm filter tùy chọn `filter[search]` vào `GET /me/buildings`: tìm chuỗi con không phân biệt chữ hoa/thường trong `name` hoặc `address`, trim đầu/cuối; bỏ filter nếu rỗng. Tìm kiếm chỉ trên tòa thuộc landlord hiện tại, kết hợp status, sorting và pagination hiện có.

## Triển khai

1. Cập nhật `api-docs/src/paths/buildings/me-buildings.yaml` với filter, ví dụ và validation theo quy ước query hiện có; bundle. **Kiểm tra:** client cũ không truyền filter vẫn có response như trước.
2. Thêm filter vào DTO, query port và query DB; parameterize và escape ký tự wildcard để tìm `%`, `_` như ký tự thông thường; áp điều kiện owner, status, search trước đếm/phân trang. **Kiểm tra:** tạo 101 tòa của cùng owner, chỉ tòa 101 chứa từ khóa → tổng 1 và trả đúng tòa; tòa của owner khác không xuất hiện.
3. FE gửi filter vào query key/params, debounce theo pattern hiện có, bỏ `SEARCH_FETCH_SIZE` và client-side slice; reset về trang 1 khi search thay đổi, dùng pagination server. **Kiểm tra:** tìm dữ liệu sau trang đầu, đổi filter, xóa tìm kiếm và refresh đều đúng; loading/error không hiện kết quả cũ như kết quả mới.
4. Test backend cho owner, status+search, wildcard, empty và phân trang; build/lint backend, lint/bundle API; FE build/lint/i18n và manual test qua Gateway. Tách PR backend contract và FE theo dependency.

## Acceptance

- Kết quả, total và phân trang bao phủ mọi tòa khớp thuộc owner, kể cả sau bản ghi thứ 100; không rò dữ liệu owner khác.
- Client cũ tương thích; tìm kiếm không giới hạn ở trang đã tải và FE thể hiện loading/error đúng.

## User story và tiêu chí nghiệp vụ

Là chủ nhà có nhiều tòa, tôi muốn tìm theo tên hoặc địa chỉ để mở đúng hồ sơ dù tòa không ở trang đầu. Search kết hợp với status hiện hành theo phép AND; tên hoặc địa chỉ khớp theo OR. Không tìm tòa đã xóa hoặc tòa của landlord khác. Không tạo quy tắc bỏ dấu nếu contract chưa quy định.

## Kịch bản nghiệm thu

1. Tạo ít nhất 101 tòa cho A, một tòa ở cuối chứa từ khóa duy nhất, một tòa khớp thuộc B; A search → chỉ nhận tòa của A, `totalItems=1`.
2. Search một chuỗi có `%`, `_` hoặc dấu `\` → coi là ký tự thông thường; không bị mở rộng thành wildcard SQL. Test khoảng trắng đầu/cuối, chữ hoa/thường và chuỗi rỗng.
3. Kết hợp `filter[status]`, sort và `pageSize` nhỏ: đếm trước pagination, không trùng hoặc thiếu dòng giữa các trang; xóa search trả lại danh sách theo filter.
4. Trên FE: vào trang 3 rồi đổi search → về trang 1; F5 giữ filter; lỗi mạng có retry và không báo không tìm thấy; kiểm tra ở 360px và desktop.

## Bàn giao

Link PR backend/API và PR FE theo thứ tự merge; đính kèm ví dụ request, response, kết quả backend test, FE build/lint/i18n. Nếu API contract bị thay đổi thêm, phải review tính tương thích client cũ trước khi merge.
