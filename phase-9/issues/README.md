# Tracker issue Phase 9

Số GitHub issue giữ `docs#TBD` đến khi PM tạo issue trên GitHub. Mỗi issue theo end-to-end một nhóm event; PM review toàn bộ contract và PR. Mỗi PR tối đa 3 points và khoảng 15 file.

| ID | Issue | Coder | Ước lượng | Trạng thái | Phụ thuộc |
|---|---|---|---:|---|---|
| P9-01 | [Tenant đăng ký → reconcile membership NULL → contract chat](P9-01-register-reconcile-null-tenant.md) | `leminhkhai345` | 3 points · 12 giờ | 🟡 Open | P8-06; P7-03/04/05 |
| P9-02 | [Tenant đã đăng ký → thêm member → contract chat](P9-02-link-member-after-registration.md) | `leminhkhai345` | 3 points · 12 giờ | 🟡 Open | P9-01 |
| P9-03 | [Vòng đời Building → building chat và thông báo duyệt](P9-03-building-context-and-notifications.md) | `huynhtiennhat0403` | 3 points · 12 giờ | 🟡 Open | P8-06; P7-03/04/05; P9-05 |
| P9-04 | [Vòng đời Contract → contract chat membership](P9-04-contract-context-and-members.md) | `huynhtiennhat0403` | 3 points · 12 giờ | 🟡 Open | P8-06; P9-01/P9-02; P7-03/04/05 |
| P9-05 | [Community: notification type/category system](P9-05-system-notification-category.md) | `huynhtiennhat0403` | 2 points · 8 giờ | 🟡 Open | P7-15; P7-D82 |
| P9-06 | [Landlord bị khóa → tạm ngưng contract và bắt đầu grace period](P9-06-landlord-lock-choreography.md) | `leminhkhai345` | 3 points · 12 giờ | 🟡 Open | P9-05; Identity user events |
| P9-07 | [Landlord mở khóa/hết hạn → khôi phục hoặc chấm dứt contract](P9-07-landlord-unlock-grace-expiry.md) | `leminhkhai345` | 3 points · 12 giờ | 🟡 Open | P9-06 |
| P9-08 | [Invoice phát hành → notification cho tenant](P9-08-invoice-notification.md) | `huynhtiennhat0403` | 3 points · 12 giờ | 🟡 Open | P6-02g; P9-05; P7-15 |
| P9-09 | [Smoke event xuyên service và lưu bằng chứng](P9-09-event-smoke.md) | `leminhkhai345`, `huynhtiennhat0403` | 2 points · 8 giờ | 🟡 Open | P9-01–P9-08 |

**Người review:** PM. **Issue notification:** để ngoài Phase 9 vì IssueReport là Stretch theo P6-D61 và code hiện chưa có Issue producer.
