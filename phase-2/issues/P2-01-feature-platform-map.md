# P2-01 — Feature → Platform Map

**Status:** 🔵 In progress
**Owner:** PM (draft) · FE + Mobile (verify)
**Input:** `phase-1/discovery/user_flow/*.md` (chỉ user flow)
**Output:** `discovery/product-platform-map.md`
**Cấu trúc bảng:** 5 cột quyền (Tenant View/Edit, Landlord View/Edit, Anonymous) + 2 cột nền tảng (Web, Mobile)

---

## Background

Phase 1 đã hoàn thành user flow 4 vai trò (landlord, tenant, admin, shared). Trước khi thiết kế wireframe hay API, cần xác định rõ **feature nào xuất hiện trên nền tảng nào** (Web landlord, Mobile tenant, Mobile landlord-lite, Admin web, Tenant web) để tránh build thừa/thiếu.

## Mục đích

Từ user flow, liệt kê **tất cả feature** trong hệ thống → map mỗi feature lên nền tảng tương ứng + ghi nhãn primary/secondary.

## Chi tiết thực hiện

### Bước 1: Liệt kê feature từ user flow

- Đọc 4 file user flow: `landlord_user_flow.md`, `tenant-user-flow.md`, `admin_user_flow.md`, `shared_user_flow.md`
- Mỗi flow section = 1 feature hoặc nhóm feature
- Ghi ra danh sách flat list: feature name + mô tả 1 dòng + user flow source (file + section)

### Bước 2: Map quyền + nền tảng

Với mỗi feature, xác định:

| Cột | Ý nghĩa |
|-----|---------|
| Feature | Tên feature |
| TenantV | Tenant có thể xem |
| TenantE | Tenant có thể tạo/sửa/xóa |
| LandlordV | Chủ trọ có thể xem |
| LandlordE | Chủ trọ có thể tạo/sửa/xóa |
| Anon | Khách vãng lai (chưa login) truy cập được |
| Web | Feature có trên nền tảng Web (React) |
| Mobile | Feature có trên nền tảng Mobile (Kotlin/Android) |

**Nhãn:** ✅ = có · — = không

### Bước 3: Verify

- FE + Mobile đọc bảng map → xác nhận / đề xuất sửa
- PM tổng hợp → chốt final

## Definition of Done

- [x] File `discovery/product-platform-map.md` tồn tại
- [x] Mỗi feature trong user flow đều có trong bảng map
- [x] Mỗi feature đều có quyền tenant/landlord/anonymous xác định
- [x] Mỗi feature đều có nền tảng Web/Mobile xác định
- [ ] FE đã verify và approve
- [ ] Mobile đã verify và approve
- [ ] Không có open question chưa resolve
