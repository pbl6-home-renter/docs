# Prompt Codex — Phase 10 (dán nguyên file này vào Codex)

Bạn là kỹ sư thực hiện các task Phase 10 của Rentify. Claude đã làm riêng: route Gateway `/me/invoices` và P10-01 (chặn xóa phòng) — KHÔNG làm lại hai việc đó.
Quyết định PM đã chốt: D1 công thức occupancy như P10-02; D2 thẻ số liệu theo trang; D3 dashboard dùng pagination.totalItems; D4 `filter[search]`; D5 generate-draft trả thẳng PDF, không Media; D7 tenant "Phòng của tôi" dựng từ /me/contracts + /me/invoices, không làm /me/room-hub.

Thứ tự làm: F3 → F4 → F5 (Tenancy-Service + api-docs) → F6a → F6b → F6c → F7 → F8 (fe) → F9 → F10 → F11 (fe; code theo spec api-docs mới của F3–F5, ghi "Depends on <link PR>" trong mô tả PR).
Mỗi task = 1 nhánh riêng từ origin/main + 1 PR (gh pr create --base main). Sau mỗi task chạy đủ lệnh kiểm tra rồi mới sang task kế. Nếu một task bị chặn (thiếu API/field, spec mâu thuẫn), ghi lý do vào mô tả PR draft và chuyển task tiếp theo. Cuối cùng in bảng tóm tắt: task → nhánh → link PR → lệnh đã pass → điểm còn mở.

### F0. Phần chung (dán đầu mỗi prompt)

Bạn làm việc trong workspace PBL6 (Rentify). Mỗi thư mục con là 1 git repo riêng; chạy git/npm trong đúng repo.
Đọc trước: CLAUDE.md ở root workspace, AGENTS.md/README của repo đang sửa, và file issue được nêu.
Quy tắc bắt buộc:
- Tạo nhánh từ origin/main: feature/<issue-id-lowercase>-<slug>. Không push lên main. Commit message tiếng Anh, conventional commits.
- Backend: Clean Architecture + DDD + CQRS như boilerplate/src/modules/sample. Domain không import NestJS/TypeORM. KHÔNG sửa src/shared/.
- Mọi thay đổi API phải sửa api-docs/src/** rồi chạy `npm run lint` và `npm run bundle` trong api-docs (commit cả reference/rentify.json), làm PR riêng ở repo api-docs.
- Lỗi trả qua DomainException + envelope chuẩn; error code UPPER_SNAKE.
- FE: không viết *.test.ts; kiểm tra bằng `npm run build`, `npm run lint`, `npm run i18n:check`. Text UI qua i18next (vi + en). Dùng TanStack Query, query key gồm đủ params.
- Không đọc/in .env hay rentify-key.pem. Không thêm tính năng ngoài issue.
- Giữ PR ≤ ~15 file; nếu vượt, dừng và báo cách tách.
Khi xong: chạy build/lint/test của repo, (backend) 3 lệnh grep dependency-rule trong CLAUDE.md phải không in gì, mở PR mô tả bằng tiếng Việt: link issue, thay đổi, bằng chứng lệnh đã chạy, điểm cần reviewer chú ý.


### F3. Tenancy — P10-06 apply-template + generate draft PDF · M

Repo: Tenancy-Service (+ PR api-docs). Issue: pm/phase-10/issues/P10-06-contract-template-regression.md, P6-01c.
Sự thật đã xác minh: hai route chưa từng tồn tại trong lịch sử git. Đã có sẵn: ContractDocumentRendererPort (src/modules/contract/application/ports/contract-document-renderer.port.ts), PdfContractDocumentRenderer (infrastructure/document/pdf-contract-document.renderer.ts, pdfkit), đăng ký trong contract.module.ts; ContractTemplate entity + query get/list.
Quyết định PM (D5): generate-draft KHÔNG lưu Media, trả thẳng file PDF.
Làm:
1. Command contract-template-apply: PUT /contracts/:contractId/apply-template body { templateKey } (đọc schema trong api-docs/src/paths/contracts/contracts-contractId-apply-template.yaml). Trong transaction: findByIdForUpdate, check landlord sở hữu, status phải draft (khác → 409 theo spec), template active tồn tại (không → 404). Lưu lựa chọn template vào contract aggregate (thêm field + migration nếu chưa có: `npm run migration:generate -- name=AddContractTemplateKey`). Trả 200 CONTRACT_TEMPLATE_APPLIED với ContractDetail.
2. Query/command contract-draft-document-generate: POST /contracts/:contractId/generate-draft-document. Check owner, status draft, đã apply template (chưa → 409/422 theo spec, ghi rõ code). Build variables từ contract + room + building + tenant snapshot (chỉ dữ liệu Tenancy có), gọi renderer.render → Buffer. Controller trả StreamableFile, Content-Type application/pdf, Content-Disposition attachment; filename="contract-<code>-draft.pdf". Không tạo mediaId giả.
3. api-docs: sửa 2 YAML: x-apidog-status → developing; response generate-draft đổi thành 200 application/pdf (binary), bỏ mediaId; thêm lỗi 403/404/409. Bundle.
4. Unit test: owner khác 403, không phải draft 409, template không có 404, chưa apply mà generate → lỗi, happy path renderer được gọi đúng variables.
Verify: build/lint/test; gọi thử local qua Swagger /api/v1/<PATH>/swagger tải được PDF.


### F4. Tenancy — P10-02 occupancy thật · M

Repo: Tenancy-Service (+ PR api-docs). Issue: pm/phase-10/issues/P10-02-building-occupancy.md (PM đã chốt công thức D1 như trong issue).
Hiện trạng: building/presentation/http/responses/my-building-list.response.dto.ts, my-building-detail.response.dto.ts gán cứng occupiedRooms=0, occupancyRate='0%'; admin-building-detail.response.dto.ts gán '0%'.
Làm:
1. Port đọc thống kê trong building/application/ports (vd BuildingRoomStatsReader.getStats(buildingIds[]): Map<id,{totalRooms, occupiedRooms}>), adapter TypeORM 1 câu GROUP BY building_id đếm room chưa soft-delete và room status occupied. Không N+1.
2. Gắn vào queries building-list-mine, building-get-mine, building-get-admin; DTO nhận stats thay vì hằng số. Thêm totalRooms (int ≥0) vào list/detail landlord. Format: 0 phòng → "0%"; làm tròn tối đa 1 chữ số, bỏ .0 (1/3 → "33.3%", 2/4 → "50%"). Đặt hàm format thuần ở domain/application để unit test.
3. api-docs: my-building-*-response-dto.yaml thêm totalRooms, bỏ mô tả giá trị tạm, example 2/4 = 50%; admin detail tương tự. Bundle.
4. Unit test hàm format + handler (stats map vào đúng building, building không có room).


### F5. Tenancy — P10-04 BE `filter[search]` cho GET /me/buildings · S

Repo: Tenancy-Service (+ PR api-docs). Issue: pm/phase-10/issues/P10-04-building-search.md (D4 đã chốt).
Làm: thêm filter[search] (string, trim, max 100, rỗng = bỏ qua) vào request DTO của building-list-mine, query port và repository: ILIKE trên name OR address, escape '\', '%', '_' (ESCAPE '\'), parameterized; điều kiện AND với owner + status; áp trước count/pagination.
api-docs: src/paths/buildings/me-buildings.yaml thêm property search vào filter deepObject + ví dụ; bundle.
Test: hàm escape; handler truyền search xuống port. Không làm FE trong PR này.


### F6. fe — dọn fix % + P10-09 đổi mật khẩu + P10-08 dashboard · S×3 (3 PR nhỏ)

Repo: fe. Issues: P10-03 (phần format %), P10-09, P10-08.
PR a) Hai file đang sửa dở src/features/buildings/components/building-list-columns.tsx và building-list-mobile-row.tsx (format occupancyRate chuỗi có sẵn '%'): rà lại, đảm bảo chỉ 1 dấu %, progress bar parseFloat; commit thành PR fix/p10-03-occupancy-format.
PR b) P10-09: trang settings (route hiện placeholder) thêm mục "Bảo mật" với form đổi mật khẩu dùng src/features/auth/hooks/use-change-password-mutation.ts + forms/password.schema.ts + PasswordInput. 401 code USER_CHANGE_PASSWORD_INVALID_CURRENT: hiện lỗi inline ở currentPassword, KHÔNG để interceptor refresh/logout (kiểm tra interceptor theo error code). 204 → clear session local theo flow logout hiện có, điều hướng login + toast "đăng nhập lại". Disable nút khi pending. Không log password.
PR c) P10-08: src/features/dashboard/.../landlord-dashboard-page.tsx & landlord-dashboard-full-state.tsx: thay buildings.length bằng pagination.totalItems của các query /me/buildings (không filter, filter[status]=approved, =pending; lấy enum status từ api-docs để tính "khác" chỉ khi bao phủ đủ). Preview list ghi nhãn "xem trước". Tách isError → ErrorState có retry, không hiện empty "chưa có tòa". i18n vi/en.


### F7. fe — P10-07 tenant xem hợp đồng · M

Repo: fe. Issue: pm/phase-10/issues/P10-07-tenant-contracts-web.md. Gateway đã route /me/contracts → Tenancy.
Làm: đọc api-docs/src/paths/contracts/me-contracts.yaml lấy DTO; trong src/features/contracts thêm api getMyContracts(ListParams), query key ['contracts','me',params], hook phân trang. Tạo TenantContractListPage + TenantContractDetailPage (read-only, dùng GET /contracts/{id}), không nút edit/activate/checkout.
Routing: hiện /contracts chỉ cho landlord trong landlord.routes.tsx. Làm role dispatcher giống src/app/routes/invoice-route.tsx cho /contracts và /contracts/:id. Loading/empty/error riêng, i18n vi/en, responsive 360px.


### F8. fe — P10-05 room detail dữ liệu thật · M

Repo: fe. Issue: pm/phase-10/issues/P10-05-room-detail-data.md.
Không dùng currentContract/currentMembers/latestMeterReadings của GET /rooms/{id} (placeholder public). Dùng API xác thực:
- GET /contracts?filter[roomId]=<id>&filter[status]=active&pageSize=1 → HĐ active.
- GET /contract-members?filter[contractId]=<id> (kiểm tra tên filter thật trong api-docs/src/paths/contracts/contract-members.yaml), lấy hết trang.
- GET /meter-readings?filter[roomId]=<id>&filter[type]=electricity|water, gọi riêng mỗi loại; kiểm tra meter-readings.yaml có sort không — nếu KHÔNG có sort, đừng đoán "mới nhất": ghi chú trong PR và hiển thị theo period lớn nhất trong trang trả về kèm cảnh báo cho reviewer.
Mỗi card loading/error/empty riêng, ngày ghi theo từng loại. Query key gồm roomId để đổi phòng không lộ dữ liệu cũ. Invalidate sau checkout/sửa member.


### F9. fe — P10-03 thẻ số liệu + P10-04 FE search · S×2 (sau F4, F5 merge)

Repo: fe. Issues P10-03, P10-04. Phụ thuộc: Tenancy đã trả totalRooms/occupancy thật và hỗ trợ filter[search].
P10-03: src/features/buildings/hooks/use-building-list.ts — thẻ totalRooms/occupied/rate/approved tính từ các dòng trang hiện tại, nhãn i18n "trên trang này"; thẻ tổng tòa = pagination.totalItems nhãn "tổng kết quả". Lỗi API không hiện 0.
P10-04: bỏ SEARCH_FETCH_SIZE + lọc client; gửi filter[search] (debounce theo pattern có sẵn) vào params + query key; đổi search → về trang 1; giữ trên URL.


### F10. fe — P10-06 FE tải PDF nháp · S (sau F3)

Repo: fe. src/features/contracts/api/contract.api.ts: generateDraftDocument đổi sang responseType 'blob', bỏ ContractGenerateDraftResponseDto(mediaId); contract-step2-draft.tsx tạo object URL để xem/tải file, revoke khi unmount. apply-template giữ nguyên nhưng kiểm tra DTO khớp api-docs mới. Lỗi qua interceptor/toast.


### F11. fe — P10-15 lite "Phòng của tôi" + dashboard tenant · M (sau F1, F7)

Repo: fe. Issue P10-15 (bản lite theo D7: KHÔNG dùng /me/room-hub).
Dữ liệu: GET /me/contracts?filter[status]=active (room/building/ngày/kỳ) + GET /me/invoices (đã có feature tenant invoice). Tenant menu đang trỏ /rooms (route landlord) → làm role dispatcher cho /rooms như invoice-route.tsx; tenant thấy card phòng từ HĐ active (nhiều HĐ → nhiều card), link tới /contracts/:id và /invoices. Dashboard tenant (đang DashboardOverview placeholder): tóm tắt HĐ active + hóa đơn chưa thanh toán gần nhất. Không hiển thị payment/issue. Loading/empty/error, i18n.


