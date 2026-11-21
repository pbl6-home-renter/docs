# P11-12 — Web: lưu phòng yêu thích cho người thuê

**Trạng thái:** 🟡 Open  
**Người phụ trách (đề xuất):** `ThaiBao11125`  
**Người review:** FE Lead  
**Ước lượng:** 2 points · khoảng 8 giờ  
**Phụ thuộc:** API `/me/favorite-rooms` đã merge (P10-24, theo P10-D90); cần deploy lên staging trước khi nghiệm thu  
**Repo / branch:** `fe` · `feature/p11-12-favorite-rooms`  
**Thay thế:** phần client Web của P10-24

## User story

> Là **người thuê đang tìm phòng**, tôi muốn **bấm trái tim để lưu phòng tôi thích và xem lại danh sách đã lưu**, để **so sánh các phòng sau này mà không phải tìm lại từ đầu**.

## Hiện trạng

- Nút trái tim đã có trên `room-public-card.tsx` nhưng **chỉ đổi state cục bộ** (`useState`), không gọi API; reload là mất.
- `use-tenant-home.ts` có comment "Reserved for toggle favorite mutation" và điều hướng `?favorites=true` nhưng trang tìm kiếm chưa xử lý tham số này.

## Contract (đã có)

- `GET /me/favorite-rooms`: phân trang; mỗi item có `roomId`, `name`, `rentPrice`, `buildingName`, `address`, `ward`, `province`, `area`, `genderPolicy`, `thumbnailUrl`, `photoUrls`, `isFavorited = true`. Mặc định sắp theo giá tăng dần. Phòng đã có người thuê hoặc không còn public bị ẩn khỏi danh sách (bản ghi vẫn giữ, phòng public lại thì hiện lại).
- `POST /me/favorite-rooms` (body `roomId`): `409 ALREADY_FAVORITED` nếu đã lưu, `404 RESOURCE_NOT_FOUND` nếu phòng không còn public.
- `DELETE /me/favorite-rooms/{roomId}`.
- Response tìm phòng public đã có `isFavorited`.

## Mô tả

1. **Hook mutation** `useToggleFavoriteRoom`: lưu/bỏ lưu theo trạng thái hiện tại, cập nhật lạc quan (optimistic) và hoàn tác nếu lỗi.
   - `409` khi lưu → coi như đã lưu (không báo lỗi).
   - `404` khi lưu → toast "Phòng không còn cho thuê", hoàn tác trái tim.
   - Sau khi đổi, invalidate query danh sách yêu thích và query tìm phòng.
2. **Nối nút trái tim** trên thẻ phòng ở trang tìm kiếm, trang chi tiết phòng public và dashboard tenant. Bỏ `useState` cục bộ, dùng `isFavorited` từ API.
3. **Danh sách đã lưu:** xử lý `?favorites=true` trên trang tìm phòng (hoặc tab "Đã lưu" riêng, chọn cách ít thay đổi layout nhất), gọi `GET /me/favorite-rooms`, dùng lại thẻ phòng hiện có; có phân trang.
4. **Chưa đăng nhập hoặc không phải tenant:** bấm trái tim → mở trang đăng nhập (tenant) hoặc ẩn nút (landlord/admin).
5. Chuỗi qua i18n (vi + en).

## Acceptance criteria

- [ ] **Given** tenant bấm trái tim trên một phòng, **then** trái tim đổi màu ngay; reload trang vẫn giữ trạng thái đã lưu.
- [ ] **Given** bấm lại trái tim, **then** phòng bị bỏ lưu và biến mất khỏi danh sách đã lưu.
- [ ] **Given** mở danh sách đã lưu, **then** thấy đúng các phòng đã lưu, sắp theo giá tăng dần.
- [ ] **Given** chưa lưu phòng nào, **then** hiện trạng thái rỗng kèm nút "Tìm phòng".
- [ ] **Given** phòng vừa có người thuê, **when** bấm lưu, **then** toast "Phòng không còn cho thuê" và trái tim trở lại trạng thái cũ.
- [ ] **Given** mạng lỗi khi bấm, **then** trái tim hoàn tác và có thông báo lỗi.
- [ ] **Given** người dùng chưa đăng nhập bấm trái tim, **then** được chuyển tới trang đăng nhập.
- [ ] **Given** đăng nhập landlord, **then** không thấy nút trái tim.
- [ ] Trái tim đồng bộ giữa trang tìm kiếm, chi tiết phòng và dashboard (lưu ở một nơi thì nơi khác cũng thấy).

## Definition of Done

- [ ] Không viết file test. `npm run build`, `npm run lint`, `npm run i18n:check` pass.
- [ ] Ảnh/clip ngắn: lưu, bỏ lưu, danh sách đã lưu, trạng thái rỗng, đính kèm PR.
