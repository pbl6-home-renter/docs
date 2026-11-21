# P11-11 — Web: màn Quản lý khách thuê cho chủ trọ

**Trạng thái:** 🟡 Open  
**Người phụ trách (đề xuất):** `ThaiBao11125`  
**Người review:** FE Lead  
**Ước lượng:** 3 points · khoảng 12 giờ  
**Phụ thuộc:** API `GET /contracts/tenants` và `GET /contracts/tenants/{contractMemberId}` đã merge (P10-16)  
**Repo / branch:** `fe` · `feature/p11-11-landlord-tenants`  
**Thay thế:** P10-17

## User story

> Là **chủ trọ**, tôi muốn **xem danh sách tất cả khách đang ở và đã từng ở trong các phòng của tôi, rồi mở chi tiết từng người để thấy họ đã ở phòng nào, hợp đồng nào, từ ngày nào**, để **liên hệ đúng người và tra lịch sử thuê mà không phải lật từng hợp đồng**.

## Hiện trạng

- `ROUTES.LANDLORD.TENANTS` và `ROUTES.LANDLORD.TENANT_DETAIL(':id')` trong `fe/src/app/routes/roles/landlord.routes.tsx` đang render placeholder `DashboardOverview`.
- FE chưa gọi `/contracts/tenants` ở đâu cả.

## Contract (đã có)

- `GET /contracts/tenants`: tham số `filter`, `sort` (`tenantName`), `order` (`asc` | `desc`), `pageNo`, `pageSize`. Mỗi item: `contractMemberId`, `tenantName`, `isLinked` (khách đã có tài khoản), `scope` (`current` = đang ở | `history` = đã rời), `contractCount`.
- `GET /contracts/tenants/{contractMemberId}`: thêm `memberships[]` gồm `contractId`, `roomId`, `contractStatus`, `joinedAt`, `leftAt`, `isCurrent`, `tenantName`, `tenantPhone`.
- Quy tắc gộp do backend làm: cùng `tenantId` là một khách; khách chưa có tài khoản (`tenantId` null) là từng dòng riêng. **FE không tự gộp theo tên hay SĐT.**

## Mô tả

**Màn danh sách `/tenants`**
- Bảng (dùng `data-table` có sẵn): Tên khách, Trạng thái ở (badge "Đang ở" / "Đã rời" theo `scope`), Tài khoản (badge "Đã liên kết" / "Chưa có tài khoản" theo `isLinked`), Số hợp đồng.
- Tìm theo tên, lọc theo trạng thái ở, sắp xếp theo tên. Lưu filter, sort, trang vào URL query.
- Bấm một dòng → `/tenants/:contractMemberId`.

**Màn chi tiết `/tenants/:id`**
- Phần đầu: tên, badge trạng thái ở và tài khoản, SĐT (lấy từ membership hiện tại; nếu không có thì từ membership gần nhất), nút gọi/copy SĐT.
- Danh sách lịch sử thuê (`memberships`, mới nhất trước): phòng, hợp đồng (liên kết sang trang chi tiết hợp đồng), trạng thái hợp đồng (dùng nhãn `contract-status` đã có), ngày vào, ngày rời.
- Membership đang ở được làm nổi bật.
- Id không tồn tại hoặc thuộc chủ trọ khác (API trả 404) → hiện trang "Không tìm thấy khách thuê" có nút quay lại.

**Chung:** skeleton khi tải, trạng thái rỗng ("Chưa có khách thuê nào" + nút tạo hợp đồng), lỗi + nút Thử lại; chuỗi qua i18n (vi + en); route chỉ cho landlord theo contract (hiện route cho cả `ADMIN`, cần bỏ `ADMIN` vì API chỉ cho landlord).

## Acceptance criteria

- [ ] **Given** chủ trọ có 3 khách đang ở và 2 khách đã rời, **when** mở `/tenants`, **then** thấy 5 dòng với badge trạng thái đúng.
- [ ] **Given** lọc "Đang ở", **then** chỉ còn 3 dòng; reload trang vẫn giữ bộ lọc.
- [ ] **Given** gõ tên vào ô tìm kiếm, **then** danh sách lọc theo tên (có debounce, không gọi API mỗi phím).
- [ ] **Given** một khách từng ở 2 hợp đồng, **when** mở chi tiết, **then** thấy 2 dòng lịch sử, dòng đang ở được làm nổi bật, bấm vào mở đúng hợp đồng.
- [ ] **Given** khách chưa có tài khoản, **then** vẫn hiển thị tên và SĐT từ hợp đồng, badge "Chưa có tài khoản".
- [ ] **Given** mở `/tenants/<id của chủ trọ khác>`, **then** hiện trang không tìm thấy, không lộ dữ liệu.
- [ ] **Given** chưa có khách nào, **then** hiện trạng thái rỗng có nút tạo hợp đồng.
- [ ] Đọc được ở chiều rộng điện thoại; chuyển ngôn ngữ vi/en không còn chuỗi hard-code.

## Ngoài phạm vi

- Sửa thông tin khách từ màn này (sửa qua hợp đồng/thành viên hợp đồng như hiện tại).
- Chọn tài khoản tenant khi tạo hợp đồng (P10-23, chờ PM chốt rule).

## Definition of Done

- [ ] Không viết file test. `npm run build`, `npm run lint`, `npm run i18n:check` pass.
- [ ] Ảnh chụp danh sách, bộ lọc, chi tiết, trạng thái rỗng, 404 (desktop + mobile) đính kèm PR.
