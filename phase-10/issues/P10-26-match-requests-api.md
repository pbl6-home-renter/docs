# P10-26 — API yêu cầu và phản hồi tìm bạn ở ghép

**Loại:** Backend · **Trạng thái:** 🔵 In progress — approved by P10-D89

**Owner đề xuất:** BE Lead / người được giao · **Reviewer:** PM / API owner · **Repo:** `Tenancy-Service`, `api-docs`, `community-service` (integration test)

**Phụ thuộc:** P10-25, P10-11, P1-13 · **Ước lượng:** chưa chốt · **Issue:** `docs#TBD`

## Bối cảnh và contract

OpenAPI đang designing cho `GET/POST /match-requests` và `POST /match-requests/{id}/accept-request`, `reject-request`, `withdraw-request`; chưa thấy controller tương ứng trong các service đã rà. Là tenant tham gia matching, tôi muốn gửi và phản hồi lời mời theo quyền của mình. Không thể coi tên endpoint là đủ để chốt state machine hoặc notification.

## Triển khai sau khi được duyệt

1. Đối chiếu P1-13, P1-D28/D29 và OpenAPI; PM chốt state machine, ai gửi/nhận/rút, lặp request, account bị khóa, privacy và notification dependency. **Kiểm tra:** bảng state/action gồm happy path, action sai actor và retry.
2. Đồng bộ schema/API, áp dụng aggregate và persistence trong service owner; kiểm tra authorization và invariant trong transaction. **Kiểm tra:** requester không accept thay recipient, duplicate hoặc chuyển trạng thái sai được xử lý theo contract đã chốt.
3. Nếu notification được duyệt, dùng outbox/inbox hiện có với recipient do service nguồn xác định; không thêm notification trước khi contract được chốt. **Kiểm tra:** replay event không tạo tác động trùng.
4. Test các chuyển trạng thái, race, idempotency, privacy và pagination; build/lint/test, API docs lint/bundle, smoke qua Gateway.

## Acceptance

- Chỉ actor được phép gửi, chấp nhận, từ chối hoặc rút theo state machine được phê duyệt; trường hợp đồng thời và retry không làm trạng thái mâu thuẫn.
- Không phụ thuộc tenant thụ động phải tạo account; notification/AI ngoài phần được duyệt không được giả lập.

## Approved contract (P10-D89, 2026-11-16 UTC)

The user approved direct tenant-to-tenant requests with notifications and UUID `Idempotency-Key` reuse semantics. Tenancy Service owns persistence and the four public operations; Community consumes the match request domain events. The target must be an active tenant with a currently discoverable roommate profile when a new request is created. The requester must be an active tenant. Existing requests remain actionable if the target profile later becomes hidden or the room becomes full; an account that is locked cannot act while locked. The recipient never needs an account for any landlord-only rental workflow under D29.

| State | Actor / action | Result | Retry / invalid actor |
|---|---|---|---|
| none | active requester sends to another eligible tenant with a new key | `pending`; notify target | same key and target returns current request without notification; wrong target for key is 409 |
| pending | target accepts | `accepted`; notify requester | repeated accept returns current request; requester/third party gets 403 |
| pending | target rejects | `rejected`; notify requester | repeated reject returns current request; requester/third party gets 403 |
| pending | requester withdraws | `withdrawn`; notify target | repeated withdraw returns current request; target/third party gets 403 |
| pending | either party sends another new request for the same unordered pair | 409 `DUPLICATE_MATCH_REQUEST` | database unique index resolves concurrent attempts |
| accepted / rejected / withdrawn | different action | 409 `MATCH_REQUEST_NOT_PENDING` | the completed action is idempotent |
| rejected / withdrawn | requester sends with a new key | new `pending` request | same old key replays the old request |

Lists include only requests involving the caller and omit phone, AI scores, and conversation IDs. Each transition locks the request row; creation uses database uniqueness for the pending pair and request key. The outbox row is committed with the state change. Tenancy emits `match_request.created`, `match_request.accepted`, `match_request.rejected`, or `match_request.withdrawn`, with `matchRequestId` and the source-selected `recipientUserId`. Community creates the notification, deduplicates event replay, and delivers through its existing notification pipeline. Deploy Community before enabling the Tenancy producer. P10-27 Web UI, AI, chat, and contact disclosure are outside this slice.

Match notification title and body in the inbox and socket payload are stable codes; `data.messageKey` identifies the event so clients can translate. Web provides Vietnamese and English translations. Community sends the same codes through FCM; device-side translation remains to be implemented before enabling these push messages for end users.

New match events include `actorUserId` and the active actor's Identity display-name snapshot: requester for create/withdraw, target for accept/reject. Community passes them into notification `data` and push data; Web interpolates the name in its toast and inbox. The consumer also accepts older events without these additive fields. Notifications use `/roommates?matchRequestId=<id>` as the Web deep link. `/roommates` currently renders a placeholder, so opening a specific request and mobile deep link handling require the deferred P10-27 UI.
