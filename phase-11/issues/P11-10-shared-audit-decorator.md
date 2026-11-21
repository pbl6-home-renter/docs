# P11-10 — Boilerplate: decorator `@Audited` và port `AuditRecorder` generic

**Trạng thái:** 🟡 Open  
**Người phụ trách (đề xuất):** `huynhtiennhat0403`  
**Người review:** BE Lead  
**Ước lượng:** 2 points · khoảng 8 giờ  
**Phụ thuộc:** — (làm song song với P11-01)  
**Repo / branch:** `boilerplate` · `feature/p11-10-shared-audit-decorator`; sau đó copy file sang `Identity-Service`, `Tenancy-Service`, `community-service`  
**Quyết định áp dụng:** [P11-D92](../decisions.md#d92--admin-dashboard-và-audit-log) (mục "Cơ chế ghi")

## User story

> Là **dev backend**, tôi muốn **khai báo "lệnh này cần ghi audit" bằng một decorator trên command handler**, để **không phải chép code ghi log vào từng handler, và sau này service khác hoặc hành động khác chỉ cần gắn decorator là có audit**.

## Thiết kế

Toàn bộ nằm trong `boilerplate/src/shared/`, **không biết gì về bảng `audit_logs`**. Mỗi service tự bind adapter lưu trữ.

### 1. Kiểu dữ liệu và port — `shared/application/audit/`

```ts
export interface AuditEntry {
  action: string;            // vd 'user.locked'
  entityType: string;        // vd 'user'
  entityId: string | null;
  actorId: string | null;
  metadata?: Record<string, unknown>;
  occurredAt?: Date;         // mặc định: thời điểm ghi
  sourceEventId?: string;    // dùng khi ghi từ event (dedup)
}

export interface AuditRecorder {
  /** Có `context` thì ghi chung transaction đó; không có thì tự mở transaction riêng. */
  record(entry: AuditEntry, context?: TransactionContext): Promise<void>;
}

export const AUDIT_RECORDER_DI_TOKEN = Symbol('AUDIT_RECORDER');
```

### 2. Decorator — `shared/application/audit/audited.decorator.ts`

Decorator **chỉ gắn metadata** (Reflect), không tự gọi DB, nên không vi phạm dependency rule của tầng application.

```ts
@Audited<UserLockCommand, User>({
  action: 'user.locked',
  entityType: 'user',
  actorId: (cmd) => cmd.adminId,
  entityId: (cmd) => cmd.userId,
  metadata: (cmd) => ({ lockReason: cmd.lockReason }),
  // skipIf?: (cmd, result) => boolean   — trả true thì không ghi
  // onError?: 'log' | 'throw'           — mặc định 'log'
})
async execute(command: UserLockCommand): Promise<User> { ... }
```

Các resolver nhận `(args, result)` của method, nên dùng được cho bất kỳ handler nào, không gắn với `user`.

### 3. Explorer — `shared/infrastructure/audit/`

- `AuditExplorer` dùng `DiscoveryService` + `MetadataScanner` của `@nestjs/core`, chạy ở `onModuleInit`. Nó tìm mọi provider có method gắn `@Audited` và bọc method đó:
  1. Gọi method gốc. Method ném lỗi → **không ghi**, ném lỗi ra như cũ.
  2. Thành công → chạy `skipIf`; nếu không bỏ qua thì gọi `AuditRecorder.record(entry)` **không truyền context** (ghi sau khi transaction của lệnh đã commit).
  3. `record` lỗi: `onError = 'log'` → ghi `logger.error` kèm action/entityId, **trả kết quả bình thường**; `'throw'` → ném lỗi.
- `AuditModule` (global) đăng ký explorer. Service **không dùng** `@Audited` thì không cần bind recorder.
- Có method gắn `@Audited` nhưng service chưa bind `AUDIT_RECORDER_DI_TOKEN` → **báo lỗi khi khởi động** (fail fast), không im lặng bỏ qua.

### 4. Cách mở rộng sau này (ghi vào `boilerplate/docs/architecture.md`, chưa làm)

- Thêm hành động mới trong Identity: thêm action vào danh sách + allowlist metadata, gắn `@Audited` lên handler. Không sửa shared.
- Service khác cần audit: bind một `OutboxAuditRecorder` publish event `audit.recorded` qua outbox; Identity consume và lưu (giống P11-05).

## Đồng bộ sang các service — **chú ý**

`src/shared` của các service **đã lệch** so với boilerplate ở nhiều file (ví dụ `application/di-tokens.ts`, `application/auth/*`, `application/http/*` của Identity). **Không chép đè cả thư mục `src/shared`.** Chỉ copy đúng các file mới:

- `shared/application/audit/**`
- `shared/infrastructure/audit/**`

Nếu cần thêm token vào `di-tokens.ts` thì sửa tay từng service, hoặc đặt token trong file riêng của thư mục `audit/` để khỏi đụng `di-tokens.ts` (khuyến nghị).

## Acceptance criteria

- [ ] **Given** một handler test gắn `@Audited` và recorder giả, **when** handler chạy thành công, **then** recorder nhận đúng 1 `AuditEntry` với action, entityType, entityId, actorId, metadata lấy từ resolver.
- [ ] **Given** handler ném lỗi, **then** recorder không được gọi và lỗi gốc vẫn được ném ra.
- [ ] **Given** `skipIf` trả `true`, **then** recorder không được gọi.
- [ ] **Given** recorder ném lỗi và `onError = 'log'`, **then** handler vẫn trả kết quả, có 1 dòng `logger.error`.
- [ ] **Given** recorder ném lỗi và `onError = 'throw'`, **then** lỗi được ném ra.
- [ ] **Given** service có `@Audited` nhưng chưa bind recorder, **then** app báo lỗi rõ ràng khi khởi động.
- [ ] **Given** service không dùng `@Audited` (Tenancy, community), **when** copy file sang và khởi động, **then** service chạy bình thường.
- [ ] Ba lệnh kiểm tra dependency rule trong `CLAUDE.md` không in gì.

## Ngoài phạm vi

- Bảng `audit_logs`, adapter ghi DB, allowlist metadata (P11-04).
- `OutboxAuditRecorder` cho service khác.
- Sửa Unit of Work để ghi chung transaction (đã chọn "ghi sau commit" theo P11-D92).

## Definition of Done

- [ ] Unit test cho explorer (5 case đầu của Acceptance) trong `boilerplate/test/unit/shared/`.
- [ ] `npm run build`, `npm run lint`, `npm test` pass ở boilerplate và ở cả 3 service sau khi copy.
- [ ] Mục "Audit" được thêm vào `boilerplate/docs/architecture.md` (cách dùng + cách mở rộng).
- [ ] PR boilerplate merge trước; PR copy sang từng service ghi rõ "chỉ thêm `shared/**/audit/**`".
