# P5-05 — Xây dựng query/mutation foundation

**Assignee:** FE Intern  
**Priority:** High  
**Estimate:** 5 pts · 10–14h  
**Phụ thuộc:** P5-02, P5-03, P5-04  
**Trạng thái:** Open

## Bối cảnh

Mỗi page không được tự gọi Axios, tự tạo loading state và tự viết toast/cache logic. Foundation phải đủ đơn giản để intern dùng đúng, nhưng không được che mất behavior của TanStack Query.

## Mục tiêu

Tạo wrapper mỏng, có type rõ ràng, cho query/mutation và query key của Auth.

## Việc cần làm

- Tạo `useAppQuery` và `useAppMutation` dựa trên TanStack Query v5.
- Chuẩn hóa query key factory; trong batch này chỉ khai báo key Auth cần thiết.
- Cấu hình query không retry lỗi client 4xx thông thường.
- Mutation không retry mặc định.
- Cho phép feature truyền `onSuccess`, `onError`, `enabled`, `staleTime` và các option chuẩn.
- Global error toast lấy code → i18n.
- Hỗ trợ `suppressErrorToast` cho form cần inline error.
- Hỗ trợ success toast theo success code.
- Có helper invalidate/reset cache cho logout hoặc session invalid.

## Ngoài phạm vi

- Không tạo model hoặc query key Building/Room/Contract/Billing.
- Không tạo cursor abstraction.
- Không đặt URL endpoint trong wrapper.
- Không giấu toàn bộ TanStack Query options sau một abstraction khó debug.

## Deliverables

- Wrapper và Auth query key factory.
- Ví dụ usage tối thiểu trong Auth hook/test.
- Test hoặc manual verification cho retry, toast suppression và invalidate.

## Definition of Done

- Auth hook dùng được wrapper mà không lặp logic chung.
- Mutation có thể invalidate đúng query key sau success.
- Form có thể tắt global toast.
- Không có query key cho module chưa triển khai.
- `npm run build`, `npm run lint` pass.
