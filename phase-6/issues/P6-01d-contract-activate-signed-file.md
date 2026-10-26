# P6-01d — Upload bản ký và kích hoạt hợp đồng

**Epic:** [P6-01](P6-01-tenancy-contract-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** leminhkhai345  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 5 points · 10–14 giờ  
**Phụ thuộc:** P6-01b; P6-04 (Media: upload `contract_signed` + internal lookup)  
**Repo / branch:** `Tenancy-Service` · `feature/p6-01d-contract-activate`  
**Issue:** `docs#68`

## Mục tiêu

Sau khi hai bên ký tay, landlord upload bản ký (ảnh hoặc PDF) qua luồng media của P6-04, rồi gọi `POST /contracts/{id}/activate-contract`. HĐ chuyển `active`, phòng chuyển `occupied` trong **cùng một transaction**, và relay publish `ContractActivated`. Chưa có file ký thì không kích hoạt được (D18).

## Contract

- Endpoint: `api-doc/src/paths/contracts/contracts-contractId-activate-contract.yaml` (`postContractsContractidActivateContract`), role landlord.
- Request: `src/requests/contracts/contract-activate-request-dto.yaml`, chỉ có `signedContractMediaId: uuid` (bắt buộc).
- Response `200 CONTRACT_ACTIVATED`: `src/responses/dtos/contracts/contract-activate-response-dto.yaml` (`id`, `status = active`, `activatedAt`).
- Lỗi:
  - `404` HĐ không tồn tại;
  - `403` không phải chủ;
  - `409 CONTRACT_NOT_READY`: HĐ không ở `draft`/`signed`, hoặc phòng đang `maintenance`;
  - `409 SIGNED_FILE_MISSING`: media không tồn tại, chưa upload xong, hoặc không phải `owner_type = contract`, `owner_id = contractId`, `purpose = contract_signed`;
  - `409 ACTIVE_CONTRACT_EXISTS`: race với HĐ khác của cùng phòng, nhờ unique index.
- Rule:
  - D18: không OTP/PIN, file ký là nguồn pháp lý;
  - `Room.status = occupied` **chỉ** được suy ra từ HĐ active. `Room.changeStatus` hiện chặn `OCCUPIED` (`src/modules/room/domain/entities/room.entity.ts`).

## Tham chiếu code

| Cần | Copy pattern từ |
|---|---|
| Command handler UoW + outbox, nhiều aggregate | `contract-create` (P6-01b) |
| Domain `activate(signedMediaId, now)` | `ContractEntity` (P6-01a) |
| Room aggregate, event `RoomStatusChangedEvent` | `src/modules/room/domain/entities/room.entity.ts`, `domain/events/room-status-changed.event.ts` |
| Gọi Identity (GET) | `src/shared/infrastructure/http/internal-http-client.service.ts`, `src/shared/application/http/peer-service.enum.ts` |

## Các bước triển khai

### Bước 1 — Chốt endpoint tra cứu media với P6-04

- **Cách làm:**
  - Thống nhất internal endpoint `GET /internal/media/{mediaId}` (đề xuất). Trả về `{ id, ownerType, ownerId, purpose, status }`, trong đó `status = uploaded` sau `complete-upload`.
  - Đồng thời xác nhận FE upload bản ký với `ownerType = contract`, `ownerId = <contractId>`, `purpose = contract_signed`. MIME cho phép theo D40: `image/jpeg`, `image/png`, `image/webp`, `application/pdf`.
- **Kiểm tra bước:** comment chốt trên issue; gọi thử endpoint trên staging hoặc local Identity trả đúng JSON.

### Bước 2 — Thêm `occupy`/`release` cho Room

- **File sửa:** `src/modules/room/domain/entities/room.entity.ts`.
- **Cách làm:**
  - Thêm `occupyByContract(contractId: Uuid)`:
    - `assertNotDeleted()`;
    - nếu `status === MAINTENANCE` thì ném `InvalidRoomException` (handler map sang `409 CONTRACT_NOT_READY`);
    - nếu đã `OCCUPIED` thì không làm gì;
    - còn lại set `OCCUPIED` và add `RoomStatusChangedEvent(id, previous, OCCUPIED)`.
  - Giữ nguyên rule chặn `OCCUPIED` trong `changeStatus` (chỉ đi qua method mới).
  - `releaseByContract()` để dành cho checkout ở P6-01e: chỉ viết method, chưa dùng.
- **Kiểm tra bước:** build pass. `changeStatus(OCCUPIED)` vẫn ném lỗi; `occupyByContract` thành công trên phòng `available`.

### Bước 3 — Port và adapter kiểm tra media

- **File tạo:**
  - `src/modules/contract/application/ports/media-lookup.port.ts`: `findMedia(id: Uuid): Promise<MediaInfo | null>`.
  - `src/modules/contract/infrastructure/media/identity-media-lookup.adapter.ts`: `internalHttpClient.get(PeerService.IDENTITY, \`/internal/media/${id}\`)`; `404` thì trả `null`.
- **Cách làm:** lỗi peer (`PeerServiceException`, timeout) **không** được nuốt mà để trả `503` theo filter chung. Không kích hoạt HĐ khi chưa xác minh được file.
- **Kiểm tra bước:** tắt Identity rồi gọi activate → `503`; HĐ vẫn `draft`.

### Bước 4 — Activate command

- **File tạo:** `src/modules/contract/application/commands/contract-activate/contract-activate.command.ts` và `.command.handler.ts`.
- **Cách làm:**
  1. **Ngoài transaction:** `media = mediaLookup.findMedia(signedContractMediaId)`. Nếu `null`, `ownerType !== 'contract'`, `ownerId !== contractId`, `purpose !== 'contract_signed'` hoặc `status !== 'uploaded'`, ném `SignedFileMissingException` (`409`, `SIGNED_FILE_MISSING`, tạo file trong `domain/exceptions/`).
  2. `unitOfWork.run(ctx => …)`:
     - `contract = contractRepository.findByIdForUpdate(id, ctx)`. Không thấy thì `404`; khác landlord thì `403`.
     - `room = roomRepository.findByIdForUpdate(contract.roomId, ctx)`.
     - `contract.activate(mediaId, new Date())`. Domain ném `CONTRACT_NOT_READY` nếu sai trạng thái.
     - `room.occupyByContract(contract.id)`. Bắt `InvalidRoomException` rồi ném lại `ContractNotReadyException`.
     - `contractRepository.save`, `roomRepository.save`.
     - `outboxRepository.append([...contract.pullDomainEvents(), ...room.pullDomainEvents()].map(OutboxMessage.fromDomainEvent), ctx)`.
  3. Bắt unique violation `UQ_contracts_room_active` → `ActiveContractExistsException`.
- **Kiểm tra bước:** build pass.

### Bước 5 — DTO, controller, module

- **File tạo:**
  - `presentation/http/requests/activate-contract.request.ts` (`@IsUUID() signedContractMediaId`);
  - `presentation/http/responses/contract-activate.response.dto.ts`.
- **File sửa:**
  - `contract.controller.ts`: `@Post(':contractId/activate-contract') @Roles(UserRole.LANDLORD) @HttpCode(200) @ResponseCode(CONTRACT_ACTIVATED)`, `operationId: 'postContractsContractidActivateContract'`.
  - `contract-response-code.constant.ts`: `CONTRACT_ACTIVATED`.
  - `contract.module.ts`: handler, provider `MediaLookupPort` → adapter, import `InternalHttpModule` nếu chưa có.
- **Kiểm tra bước:** Swagger hiện endpoint; body thiếu `signedContractMediaId` trả `422`.

### Bước 6 — Kiểm tra transaction và event

- **Cách làm:**
  - Activate thành công: `contracts.status = active`, `activated_at` có giá trị, `rooms.status = occupied`. Outbox có 2 row `ContractActivated` và `RoomStatusChanged` cùng thời điểm.
  - Tạm `throw` sau `roomRepository.save`: API `500`, HĐ vẫn `draft`, phòng vẫn `available`, không có outbox mới. Xóa dòng throw.
  - Tạo HĐ draft thứ hai cho cùng phòng rồi activate → `409 CONTRACT_NOT_READY` (phòng đã occupied) hoặc `409 ACTIVE_CONTRACT_EXISTS`. Ghi lại kết quả thực tế.
- **Kiểm tra bước:** ghi query và kết quả vào PR.

## Quyết định tạm thời / Ngoài phạm vi

- Trạng thái `signed` (đã upload file nhưng chưa activate) chưa dùng: activate đi thẳng `draft → active`. Nếu PM muốn tách hai bước thì mở issue riêng.
- Tạo kênh chat phòng sau khi activate (community-service, Stretch): chỉ cần event `ContractActivated` có trong outbox.
- Kiểm tra `startDate` so với ngày hiện tại: không chặn, vì landlord có thể nhập HĐ cũ (D29).
- Nếu P6-04 chưa có `GET /internal/media/{id}`: dùng adapter giả chỉ kiểm tra UUID hợp lệ, bật bằng `MEDIA_LOOKUP_DRIVER=stub`, **không merge `main`**.

## Cập nhật `api-doc`

- [ ] Sequence diagram: Gateway → Tenancy → Identity (`GET /internal/media/{id}`) → DB transaction (contract + room + outbox) → Relay → RabbitMQ.
- [ ] Ghi rõ trong `description` các điều kiện của `SIGNED_FILE_MISSING` và `CONTRACT_NOT_READY` như mục Contract.
- [ ] `x-apidog-status` → `released`; sync Apidog.

## Manual verification (Apidog)

1. Upload bản ký qua P6-04 (`purpose = contract_signed`, `ownerId = contractId`), activate → `200 CONTRACT_ACTIVATED`; phòng thành `occupied`.
2. Media ID ngẫu nhiên → `409 SIGNED_FILE_MISSING`.
3. Media của HĐ khác hoặc purpose khác → `409 SIGNED_FILE_MISSING`.
4. Activate lần hai → `409 CONTRACT_NOT_READY`.
5. Phòng đang `maintenance` → `409 CONTRACT_NOT_READY`.
6. Token tenant → `403`.

## Definition of Done

- [ ] Bước 1–6 đã qua phần Kiểm tra bước, dùng media thật của P6-04.
- [ ] `npm run build` + `npm run lint` pass.
- [ ] PR ghi `Closes pbl6-home-renter/docs#68`; đính kèm kết quả query Bước 6.
- [ ] baoduong17 approve.
