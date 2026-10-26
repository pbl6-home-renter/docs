# P6-07 — Seed dữ liệu demo và chốt staging

**Trạng thái:** ⚪ Outline  
**Người phụ trách:** baoduong17  
**Người review:** cả team  
**Ước lượng:** ~5 points · 10–14 giờ  
**Phụ thuộc:** P6-01, P6-02, P6-05  
**Iteration:** It6 → It7

## Mục tiêu

Staging (EC2) có dữ liệu thực tế để demo vòng đời landlord-solo, và có kịch bản demo để cả team diễn tập.

## Các bước (outline)

1. Seeder cho từng service (`npm run seed:run`, theo `src/modules/sample/infrastructure/seeds/sample-create.seeder.ts`):
   - 1 admin, 2 landlord, 6 tenant;
   - 3 toà đã duyệt, 1 toà pending, 20 phòng;
   - 8 hợp đồng active;
   - chỉ số điện nước 2 tháng, hóa đơn ở nhiều trạng thái.
2. Seeder idempotent (chạy lại không nhân đôi dữ liệu), giống `seed:admin` của Identity (P4-13).
3. Deploy toàn bộ service lên EC2 bằng `infra` scripts; kiểm tra health của từng service qua gateway.
4. Viết `pm/phase-6/demo-script.md`: các bước demo, tài khoản dùng, phương án dự phòng khi API lỗi.
5. Diễn tập 1 lần với team cuối It6, ghi lại bug vào It7.
