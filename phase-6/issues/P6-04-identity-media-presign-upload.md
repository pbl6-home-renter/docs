# P6-04 — Media upload 2 bước (presign → PUT → complete) và đọc/xóa media

**Trạng thái:** 🟡 Open  
**Người phụ trách:** baoduong17  
**Người review:** BE member (leminhkhai345 hoặc huynhtiennhat0403)  
**Ước lượng:** 8 points · 18–24 giờ  
**Phụ thuộc:** — (chặn P6-03b, P6-03d, và upload file HĐ ký trong Contract)  
**Repo / branch:** `Identity-Service` · `feature/p6-04-media-upload`; `infra` (env R2); `api-doc` (sửa contract nếu chốt mục dưới)  
**Issue:** `docs#TBD`

## Mục tiêu

Client xin presigned URL (`201 MEDIA_UPLOAD_TICKET_ISSUED`), PUT file thẳng lên Cloudflare R2, rồi gọi complete để chốt (`200 MEDIA_UPLOAD_COMPLETED`). Sau đó đọc được file qua `GET /media/{id}` và xóa mềm qua `DELETE /media/{id}`. Bảng `media` nằm trong `identity_db`.

## Contract

- `api-doc/src/paths/media/media-presign-upload.yaml` → `postMediaPresignUpload`:
  - Body `api-doc/src/requests/operations/media-upload-presign-request-dto.yaml`: `ownerType`, `ownerId`, `purpose`, `fileName`, `contentType` (`image/jpeg|png|webp`, `application/pdf`), `captureSource?`, `size`.
  - Response `api-doc/src/responses/dtos/operations/media-upload-presign-response-dto.yaml`: `id`, `ownerType`, `ownerId`, `purpose`, `uploadUrl`, `requiredHeaders`, `expiresIn` (= 900).
  - Lỗi `422 MEDIA_TYPE_NOT_ALLOWED | INVALID_PURPOSE | VALIDATION_FAILED`, `403 FORBIDDEN`.
  - Rule: `purpose = meter_reading_evidence` thì tenant chỉ được dùng `captureSource = camera_direct`.
- `api-doc/src/paths/media/media-mediaId-complete-upload.yaml` → `postMediaMediaidCompleteUpload`: `200 MEDIA_UPLOAD_COMPLETED` (`MediaCompleteUploadResponseDto`), `409 UPLOAD_NOT_COMPLETED`, `410 TICKET_EXPIRED`, `404`, `403`.
- `api-doc/src/paths/media/media-mediaId.yaml`:
  - `getMediaMediaid`: stream file (`Content-Type`, `Content-Disposition`), `410 MEDIA_DELETED`.
  - `deleteMediaMediaid`: `204`, `409 CANNOT_DELETE`.
- Thiết kế bảng: `pm/phase-1/discovery/database-design.md` §2.25 (`owner_type`, `owner_id` không có FK, `purpose`, `file_type`, `url`, `size_bytes`, `user_id`; index `(owner_type, owner_id)`; partial unique 1 `cover_photo`/owner).
- Storage: `pm/phase-3/discovery/free-tier-db-storage.md` Phần 2–3 (Cloudflare R2, presigned PUT bind `Content-Type`, TTL 900s, chặn SVG/HTML; env `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`).

## Tham chiếu code

| Cần | Copy pattern từ |
|---|---|
| Cấu trúc module CQRS + Clean Architecture | `Identity-Service/src/modules/users/` (commands, queries, domain, infrastructure/persistence, presentation/http) |
| Command có UoW | `src/modules/users/application/commands/user-update-me/` |
| Port + adapter hạ tầng | `src/modules/users/application/ports/password-hasher.port.ts` + `infrastructure/services/bcrypt-password-hasher.ts` |
| Gọi service khác (kiểm tra quyền sở hữu) | `src/modules/users/infrastructure/services/tenancy-user-stats.service.ts` (`INTERNAL_HTTP_DI_TOKEN.CLIENT`, `PeerService.TENANCY`) |
| Config env | `src/shared/infrastructure/config/api-config.service.ts` |
| Migration | `src/database/migrations/1791986400000-create-password-reset-tokens.ts` |

## Điểm cần chốt (trước Bước 4)

1. **Giấy tờ của Building chưa tồn tại:** `BuildingCreateRequestDto.ownershipCertificateMediaIds` (minItems 1) cần media id **trước** khi tạo Building, nhưng presign đòi `ownerId`. **Đề xuất A:** cho phép `purpose = ownership_proof` presign với `ownerId` bỏ trống (media "chưa gắn"); khi Tenancy tạo Building thì gọi internal `POST /internal/media/attach { mediaIds, ownerType: 'building', ownerId, userId }` để gắn. Phương án B: tạo Building trước, upload sau, rồi mới gửi duyệt (phải sửa contract Building). Chốt rồi sửa `api-doc`.
2. **Kiểm tra quyền sở hữu entity cha** (landlord chỉ upload cho Room/Building của mình): cần Tenancy có endpoint internal, ví dụ `GET /internal/ownership/{ownerType}/{ownerId}` trả `landlordId`. MVP: làm cho `building`, `room`, `contract`; các ownerType khác để `TODO`.
3. **Public read:** ảnh phòng `available` là public. MVP có thể trả signed GET URL (redirect 302) thay vì proxy stream. Nếu đổi thì phải sửa contract (`200 octet-stream`).

## Các bước triển khai

### Bước 1 — Chuẩn bị R2 và chạy service local

- **Cách làm:**
  - Tạo bucket R2 private `rentify-media` (dev/staging dùng chung, prefix theo env), tạo API token Object Read & Write.
  - Cấu hình CORS bucket cho `PUT` từ origin web (localhost + domain staging).
  - Thêm env vào `Identity-Service/.env.example` và `infra` (env mẫu của service identity): `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`, `MEDIA_UPLOAD_TTL_SECONDS=900`, `MEDIA_MAX_SIZE_BYTES=10485760`.
  - `npm ci && npm run migration:run && npm run start:dev`.
- **Kiểm tra bước:** `GET /api/v1/identity/health` (theo `ServiceConstants.PATH`) trả `200`; có thể upload 1 file bằng `aws s3 cp --endpoint-url https://<account>.r2.cloudflarestorage.com`.

### Bước 2 — Domain `media`

- **File tạo** (`src/modules/media/domain/`):
  - `enums/media-owner-type.enum.ts`, `media-purpose.enum.ts`, `media-file-type.enum.ts`, `media-status.enum.ts` (`pending_upload | uploaded | deleted`).
  - `entities/media.props.ts`, `entities/media.ts`: `Media.requestUpload(...)` (status `pending_upload`, `expiresAt = now + ttl`), `markUploaded()`, `delete()`, `isExpired(now)`.
  - `constants/media-purpose-matrix.constant.ts`: ma trận `ownerType → purpose[]` hợp lệ theo §2.25 (ví dụ `building → cover_photo|gallery_photo|ownership_proof`).
  - `exceptions/`: `media-type-not-allowed`, `invalid-purpose`, `ticket-expired` (410), `upload-not-completed` (409), `media-deleted` (410), `media-not-found` (404 `RESOURCE_NOT_FOUND`), đều kế thừa `DomainException`.
  - `repositories/media.repository.interface.ts`.
- **Kiểm tra bước:** `npm run build` pass; viết unit test nhỏ cho ma trận purpose và `isExpired`.

### Bước 3 — Persistence và migration

- **File tạo:** `src/modules/media/infrastructure/persistence/media.typeorm-entity.ts`, `mappers/media.mapper.ts`, `media.repository.ts`.
- **Cách làm:**
  - Cột theo §2.25, thêm `storage_key varchar(512)`, `content_type`, `status`, `expires_at timestamptz`, `owner_id uuid null` (nếu chốt phương án A ở Điểm cần chốt 1).
  - `npm run migration:generate -- src/database/migrations/create-media-table` → mở file, **chỉ giữ** `CREATE TYPE`/`CREATE TABLE "media"`/index của media (xóa dòng thừa, xem lỗi tương tự ở P5-08b Bước 1).
  - Index `(owner_type, owner_id)` + partial unique `(owner_type, owner_id, purpose) WHERE purpose='cover_photo' AND is_deleted=false`.
- **Kiểm tra bước:** `npm run migration:run` từ DB trống pass, `migration:revert` pass.

### Bước 4 — Port storage + adapter R2

- **File tạo:**
  - `src/modules/media/application/ports/object-storage.port.ts`: `createPresignedPut({ key, contentType, contentLength, expiresIn })`, `headObject(key)`, `createPresignedGet(key, expiresIn)` hoặc `getObjectStream(key)`, `deleteObject(key)`.
  - `src/modules/media/infrastructure/storage/r2-object-storage.ts`: dùng `@aws-sdk/client-s3` + `@aws-sdk/s3-request-presigner` (`npm i`), `endpoint = https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com`, `region: 'auto'`; ký kèm `ContentType` để R2 từ chối nếu client gửi sai.
  - Config: thêm `storage` vào `api-config.service.ts`.
- **Kiểm tra bước:** script nhỏ hoặc test gọi `createPresignedPut` rồi `curl -X PUT -H "Content-Type: image/jpeg" --data-binary @a.jpg "<url>"` → `200`; `headObject` thấy file.

### Bước 5 — Presign command + endpoint

- **File tạo:**
  - `src/modules/media/application/commands/media-presign-upload/{command,command.handler}.ts`.
  - `src/modules/media/presentation/http/requests/media-presign-upload.request.dto.ts`, `responses/media-presign-upload.response.dto.ts`, `constants/media-response-code.constant.ts`, `controllers/media.controller.ts`.
- **Cách làm (handler):**
  1. Kiểm tra `contentType` thuộc allowlist, `size ≤ MEDIA_MAX_SIZE_BYTES`, đuôi `fileName` khớp MIME → nếu sai trả `MEDIA_TYPE_NOT_ALLOWED`.
  2. Kiểm tra `purpose` hợp lệ với `ownerType` theo ma trận → nếu sai trả `INVALID_PURPOSE`.
  3. Rule `meter_reading_evidence` + role tenant ⇒ `captureSource` phải là `camera_direct`.
  4. Kiểm tra quyền sở hữu entity cha (Điểm cần chốt 2) qua port `IOwnershipChecker` (adapter gọi Tenancy).
  5. `storageKey = ${ownerType}/${ownerId ?? 'unattached'}/${mediaId}.${ext}` → lưu `Media` `pending_upload` → `createPresignedPut`.
  6. Trả `201 MEDIA_UPLOAD_TICKET_ISSUED` với `requiredHeaders: { 'Content-Type': contentType }`, `expiresIn: 900`.
- **Kiểm tra bước:** Apidog `POST /media/presign-upload` → `201`; PUT file bằng `uploadUrl` thành công; gửi `image/svg+xml` → `422 MEDIA_TYPE_NOT_ALLOWED`.

### Bước 6 — Complete upload

- **File tạo:** `application/commands/media-complete-upload/*`, thêm route `POST /media/:mediaId/complete-upload`.
- **Cách làm:** chỉ uploader được complete (`user_id = currentUser.id`, nếu không thì `403`); nếu hết hạn thì `410 TICKET_EXPIRED`; `headObject` không thấy file thì `409 UPLOAD_NOT_COMPLETED`; kích thước/MIME thật lệch so với ticket thì xóa object và trả `422`; hợp lệ thì `markUploaded()`, set `url`/`size_bytes`, trả `200 MEDIA_UPLOAD_COMPLETED`.
- **Kiểm tra bước:** complete trước khi PUT → `409`; complete sau PUT → `200`; complete lần 2 → vẫn `200` (idempotent) hoặc theo contract.

### Bước 7 — Get/stream và delete

- **File tạo:** `application/queries/media-get/*`, `application/commands/media-delete/*`; thêm route `GET /media/:mediaId`, `DELETE /media/:mediaId`.
- **Cách làm:**
  - GET: media `deleted` → `410 MEDIA_DELETED`; quyền đọc theo §2.25 (MVP: uploader, admin, landlord sở hữu entity cha; ảnh `room`/`building` cover/gallery → public, khai báo bằng `@Public()` + kiểm tra trong handler). Stream từ R2 với header `Content-Type`, `Content-Disposition`.
  - DELETE: chỉ uploader/admin; `ownership_proof` của Building đã duyệt hoặc `contract_signed` của HĐ active → `409 CANNOT_DELETE`; còn lại soft delete + `deleteObject` (hoặc giữ object, ghi `TODO(lifecycle)`).
- **Kiểm tra bước:** tải file về khớp bản gốc (so `sha256sum`); xóa → GET trả `410`.

### Bước 8 — Internal attach (nếu chốt phương án A) và gateway

- **File tạo:** `presentation/http/controllers/media-internal.controller.ts` (`@InternalOnly()`, `@ApiExcludeController()` như `user-internal.controller.ts`) → `POST /internal/media/attach`.
- **File sửa (repo `api-gateway`):** route `/api/v1/media/*` → identity (kiểm tra bảng route hiện có).
- **Kiểm tra bước:** gọi qua gateway staging → presign/complete/get đều chạy; endpoint `internal/*` không truy cập được từ ngoài gateway.

## Quyết định tạm thời / Ngoài phạm vi

- Không resize/thumbnail (client tự nén trước khi upload, theo free-tier-db-storage §2).
- Không làm lifecycle tự xóa file `pending_upload` quá hạn; ghi `TODO(cleanup-job)`.
- Video không hỗ trợ (allowlist chỉ có ảnh + PDF).

## Cập nhật `api-doc` (bắt buộc trước khi đóng issue)

- [ ] Sửa contract theo các quyết định ở Điểm cần chốt (ownerId optional cho `ownership_proof`, internal attach không đưa vào spec public).
- [ ] Sequence diagram cho presign + complete: Client → Gateway → Identity → R2; Client → R2 (PUT); Client → Identity complete → R2 HEAD.
- [ ] `x-apidog-status` → `released` cho 4 endpoint; sync Apidog.

## Manual verification (Apidog + curl)

1. Landlord presign `ownerType=room` của phòng mình → `201`; PUT; complete → `200`; GET trả đúng ảnh.
2. Landlord presign cho phòng của landlord khác → `403`.
3. `contentType=image/svg+xml` → `422 MEDIA_TYPE_NOT_ALLOWED`; `ownerType=room, purpose=cccd_front` → `422 INVALID_PURPOSE`.
4. Tenant `meter_reading_evidence` + `device_storage` → `422`.
5. Đợi > 900s rồi complete → `410 TICKET_EXPIRED`.
6. DELETE → `204`; GET lại → `410 MEDIA_DELETED`.

## Definition of Done

- [ ] Bước 1–8 qua phần Kiểm tra bước; Điểm cần chốt 1–3 có quyết định ghi trong issue.
- [ ] `npm run build` + `npm run lint` pass; migration chạy từ DB trống.
- [ ] Env R2 có trên EC2 staging (không commit secret).
- [ ] PR ghi `Closes pbl6-home-renter/docs#TBD`, kèm PR `api-doc`/`api-gateway`/`infra` liên quan.
