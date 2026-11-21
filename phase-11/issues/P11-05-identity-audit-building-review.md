# P11-05 — Identity: ghi audit khi admin duyệt/từ chối tòa

**Trạng thái:** 🟡 Open  
**Người phụ trách (đề xuất):** `huynhtiennhat0403`  
**Người review:** BE Lead  
**Ước lượng:** 2 points · khoảng 6 giờ  
**Phụ thuộc:** P11-04 (bảng `audit_logs` + `DbAuditRecorder`), P11-10 (port `AuditRecorder`)  
**Repo / branch:** `Identity-Service` · `feature/p11-05-audit-building-review`  
**Quyết định áp dụng:** [P11-D92](../decisions.md#d92--admin-dashboard-và-audit-log)

## User story

> Là **admin**, tôi muốn **nhật ký ghi lại lần duyệt và từ chối tòa nhà của mọi admin**, để **trả lời được chủ trọ khi họ hỏi ai đã từ chối tòa của họ và với lý do gì**.

## Mô tả

- Tenancy **đã publish** `building.approved` và `building.rejected` qua outbox. Payload có `aggregateId` (buildingId), `reviewedBy`, `reviewedAt`, `note`. **Không cần sửa Tenancy.**
- Thêm subscriber trong `src/modules/audit-log/presentation/messaging/`, theo mẫu `src/modules/media/presentation/messaging/media-owner-deleted.subscriber.ts` (`@RabbitSubscribe`, queue riêng của Identity, có retry/DLQ như các subscriber khác).
- Map event sang audit:

  | Event | `action` | `actor_id` | `entity_id` | `metadata` | `created_at` |
  |---|---|---|---|---|---|
  | `building.approved` | `building.approved` | `reviewedBy` | `aggregateId` | `{ note }` (note có thể null) | `reviewedAt` |
  | `building.rejected` | `building.rejected` | `reviewedBy` | `aggregateId` | `{ note }` | `reviewedAt` |

- `source_service = tenancy`, `source_event_id = id của message`.
- **Gọi trực tiếp port `AuditRecorder.record(entry, context)`** (P11-10, adapter từ P11-04), truyền `context` của transaction inbox. Như vậy dòng audit và dòng `processed_events` được ghi cùng một transaction.
  - **Không dùng `@Audited` ở đây**: decorator ghi *sau* commit nên không cùng transaction với inbox. Nếu ghi audit lỗi mà message đã được đánh dấu xử lý thì sẽ mất log và không được retry. Với consumer, toàn bộ công việc chính là ghi audit, nên gọi port trực tiếp là đúng.
- **Idempotent:** dùng inbox `processed_events` + unique `source_event_id` (`ON CONFLICT DO NOTHING` trong adapter). Nhận lại cùng message thì bỏ qua, không lỗi.

## Acceptance criteria

- [ ] **Given** admin duyệt một tòa trên Tenancy, **when** event được relay, **then** trong vài giây Identity có 1 dòng `building.approved` với `actor_id` = admin đó, `entity_id` = id tòa.
- [ ] **Given** admin từ chối tòa với ghi chú "Thiếu giấy phép", **then** dòng `building.rejected` có `metadata.note = "Thiếu giấy phép"`.
- [ ] **Given** cùng một message được giao 2 lần (at-least-once), **then** chỉ có 1 dòng audit.
- [ ] **Given** ghi audit lỗi giữa chừng, **then** transaction rollback, `processed_events` không có message đó, và message được retry.
- [ ] **Given** payload thiếu `reviewedBy` hoặc sai định dạng, **then** message vào retry/DLQ theo cơ chế chung, không làm crash consumer.
- [ ] `created_at` của dòng audit bằng `reviewedAt` trong event (thời điểm thao tác thật, không phải lúc consume).

## Definition of Done

- [ ] Unit test cho mapper event → audit (approved, rejected, note null).
- [ ] Smoke trên staging: duyệt + từ chối 1 tòa, chụp kết quả `SELECT` trong `audit_logs`, đính kèm PR.
- [ ] `npm run build`, `npm run lint`, `npm test` pass.
- [ ] Ghi tên queue/binding mới vào README của Identity (mục messaging) nếu README có liệt kê.
