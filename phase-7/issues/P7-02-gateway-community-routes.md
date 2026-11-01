# P7-02 — Route API Community và PushDevice qua Gateway

**Assignee:** `baoduong17` · **Iteration:** It5 · **Ước lượng:** 1 point
**Repo:** `api-gateway` · **Phụ thuộc:** — · **Trạng thái:** 🟡 Open

## Bối cảnh agent cần đọc

Đọc issue này, `api-gateway/AGENTS.md`, `api-gateway/src/constants/route-paths.constants.ts`, [API Chat đã duyệt](../../phase-6/discovery/community-service-design.md) và [P7-D01](../discovery/decisions.md). Gateway đã có `GatewayService.Community` và route prefix `/conversations`, `/messages`, `/notifications`; `/me` hiện do Identity nhận. Route matching dùng prefix cụ thể nhất.

## Mục tiêu

Các public API Community được chuyển tới Community Service; `/api/v1/me/push-devices` cũng thuộc Community mà vẫn giữ nguyên URL client. Các đường `/api/v1/me` khác tiếp tục đi Identity.

## Acceptance

- [ ] Thêm route cụ thể `/me/push-devices` cho Community, không chuyển toàn bộ `/me` khỏi Identity.
- [ ] Xác nhận `/conversations`, `/messages`, `/notifications`, `/me/notification-preference` vẫn map tới Community.
- [ ] Route health/service mapping hiện có không bị đổi ngoài phạm vi.
- [ ] Chạy các lệnh build/lint sẵn có của repo; ghi kết quả route mapping vào PR.

## Không làm

- Không tạo endpoint PushDevice trong issue này, không sửa Identity, không đổi URL client.
- Không thêm route `/issues` hoặc tính năng IssueReport mới.
