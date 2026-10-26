# P6-01c — Mẫu hợp đồng, áp mẫu và sinh tài liệu nháp

**Epic:** [P6-01](P6-01-tenancy-contract-vertical-slice.md)  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** leminhkhai345  
**Người review:** baoduong17 (BE Lead, API owner)  
**Ước lượng:** 5 points · 10–14 giờ  
**Phụ thuộc:** P6-01b; P6-04 (Media, phần lưu file do server sinh ra)  
**Repo / branch:** `Tenancy-Service` · `feature/p6-01c-contract-template`  
**Issue:** `docs#TBD`

## Mục tiêu

Landlord xem được danh sách mẫu HĐ có sẵn, áp một mẫu vào HĐ nháp, và bấm "Sinh tài liệu nháp" để nhận file PDF đã điền sẵn thông tin (`201 CONTRACT_DRAFT_GENERATED`, trả `mediaId`). Landlord in file này ra để hai bên ký tay (D18).

## Contract

| Endpoint | operationId | Role | Thành công | Lỗi nghiệp vụ |
|---|---|---|---|---|
| `GET /contract-templates` | `getContractTemplates` | landlord | `200 CONTRACT_TEMPLATES_FETCHED` (offset pagination) | `403` |
| `GET /contract-templates/{templateKey}` | `getContractTemplatesTemplatekey` | landlord | `200 CONTRACT_TEMPLATE_FETCHED` | `404` |
| `PUT /contracts/{contractId}/apply-template` | `putContractsContractidApplyTemplate` | landlord | `200 CONTRACT_TEMPLATE_APPLIED` | `404 TEMPLATE_NOT_FOUND`, `404 CONTRACT_NOT_FOUND`, `409 CONTRACT_NOT_DRAFT` |
| `POST /contracts/{contractId}/generate-draft-document` | `postContractsContractidGenerateDraftDocument` | landlord | `201 CONTRACT_DRAFT_GENERATED` | `409 CONTRACT_NOT_DRAFT`, `422 TEMPLATE_DATA_INVALID` |

- File path: `api-doc/src/paths/contracts/contract-templates.yaml`, `contract-templates-templateKey.yaml`, `contracts-contractId-apply-template.yaml`, `contracts-contractId-generate-draft-document.yaml`.
- Request: `src/requests/contracts/contract-template-apply-request-dto.yaml` và `contract-draft-generate-request-dto.yaml`, cả hai chỉ có `templateKey`.
- Response:
  - `src/responses/dtos/contracts/contract-template-list-response-dto.yaml` (`templateKey`, `title`, `version`);
  - `contract-template-detail-response-dto.yaml` (thêm `requiredVariables: string[]`);
  - `contract-template-apply-response-dto.yaml` (`id`, `templateKey`, `status`);
  - `contract-draft-generate-response-dto.yaml` (`contractId`, `mediaId`, `purpose = contract_template`).
- Bảng `contract_templates` thuộc `tenancy_db` (`pm/phase-3/discovery/database-per-service.md`).
- File lưu dạng `Media(owner_type='contract', purpose='contract_template')` (`database-design.md` §2.7, bảng `media`).

## Tham chiếu code

| Cần | Copy pattern từ |
|---|---|
| Seeder (typeorm-extension) | `src/modules/sample/infrastructure/seeds/sample-create.seeder.ts`; chạy bằng `npm run seed:run` |
| Command handler, `findByIdForUpdate` | `contract-update` (P6-01b) |
| Query handler, phân trang | `contract-list` (P6-01b), `TypeOrmOffsetPaginator` |
| Internal HTTP client sang service khác | `src/shared/application/ports/internal-http-client.port.ts`, `src/shared/infrastructure/http/internal-http-client.service.ts` |
| Domain method `applyTemplate`, `attachDraftDocument` | `ContractEntity` (P6-01a) |

## Các bước triển khai

### Bước 1 — Chốt cách lưu file với P6-04

- **Vấn đề:**
  - Media thuộc Identity-Service. Luồng chuẩn là client xin presigned URL, `PUT` lên Cloudflare R2, rồi gọi `complete-upload`.
  - Ở đây chính **server** Tenancy sinh ra file.
  - `InternalHttpClient` hiện chỉ có `get<T>()`.
- **Cách làm:**
  - Thống nhất với người làm P6-04 và baoduong17 một internal endpoint, đề xuất `POST /internal/media` (`@InternalOnly`, `SERVICE_TOKEN`). Body: `{ ownerType: 'contract', ownerId, purpose: 'contract_template', mimeType: 'application/pdf', fileName, sizeBytes }`. Trả về `{ mediaId, uploadUrl }`.
  - Tenancy `PUT` buffer lên `uploadUrl`, sau đó gọi `POST /internal/media/{id}/complete`.
  - Ghi quyết định vào comment issue.
- **Kiểm tra bước:** có comment chốt endpoint. Nếu P6-04 chưa xong thì làm Bước 2–5 trước; Bước 6 dùng adapter giả (xem Quyết định tạm thời).

### Bước 2 — Bảng và seed `contract_templates`

- **File tạo** (trong `src/modules/contract/`):
  - `domain/entities/contract-template.entity.ts`: read model đơn giản gồm `templateKey`, `title`, `version`, `body` (HTML có biến `{{tenantName}}`…), `requiredVariables: string[]`, `isActive`.
  - `infrastructure/persistence/contract-template.typeorm-entity.ts` (bảng `contract_templates`, `template_key varchar(100)` unique), mapper và repository (`findActivePage`, `findByKey`).
  - Migration: `npm run migration:generate -- src/database/migrations/CreateContractTemplatesTable`, **chỉ giữ câu lệnh của `contract_templates`**.
  - `infrastructure/seeds/contract-template.seeder.ts`: seed 1 mẫu `standard-room-lease-v1`, nội dung tiếng Việt cơ bản ("Hợp đồng thuê phòng trọ"). Biến gồm `landlordName`, `tenantName`, `tenantPhone`, `tenantCccd`, `roomName`, `buildingAddress`, `rentPrice`, `depositAmount`, `startDate`, `endDate`, `paymentDueDay`. Seeder phải idempotent (upsert theo `template_key`).
- **Kiểm tra bước:** `npm run migration:run && npm run seed:run` chạy hai lần không lỗi, chỉ có 1 row.

### Bước 3 — Queries mẫu HĐ

- **File tạo:**
  - `application/queries/contract-template-list/`;
  - `application/queries/contract-template-get/` (không thấy thì `404 RESOURCE_NOT_FOUND`);
  - response DTO `contract-template-list-item.response.dto.ts`, `contract-template-detail.response.dto.ts`;
  - controller `contract-template.controller.ts` (`@Controller('contract-templates')`, `@Roles(UserRole.LANDLORD)`).
- **Kiểm tra bước:** `GET /api/v1/contract-templates` trả 1 item; `GET /contract-templates/khong-co` trả `404`.

### Bước 4 — Apply template

- **File tạo:** `application/commands/contract-apply-template/` (command và handler).
- **Cách làm:** trong UoW:
  1. `templateRepository.findByKey(key)`; không thấy hoặc `!isActive` thì ném `TemplateNotFoundException` (`404`, `TEMPLATE_NOT_FOUND`).
  2. `contractRepository.findByIdForUpdate`; không thấy thì `404 CONTRACT_NOT_FOUND`, khác landlord thì `403`.
  3. `contract.applyTemplate(key)`; không phải `draft` thì `409 CONTRACT_NOT_DRAFT`.
  4. `save` và append outbox.
- **Kiểm tra bước:** `PUT /contracts/{id}/apply-template` trả `200` với `templateKey` mới.

### Bước 5 — Render PDF

- **File tạo:**
  - `application/ports/contract-document-renderer.port.ts`: `render(templateBody, variables): Promise<Buffer>`.
  - `infrastructure/document/pdf-contract-document.renderer.ts`.
- **Cách làm:**
  - Thay biến bằng `handlebars`. Biến thiếu so với `requiredVariables` thì ném `TemplateDataInvalidException` (`422`, `TEMPLATE_DATA_INVALID`).
  - Xuất PDF bằng `pdfkit`, nhúng font Unicode có dấu tiếng Việt (ví dụ Roboto TTF đặt trong `assets/fonts/`).
  - Không dùng Puppeteer vì EC2 RAM thấp.
  - Lấy biến từ: Contract; Room/Building (repository cùng DB); `landlordName` qua `InternalHttpClient.get` sang Identity (đã có internal user lookup), lỗi thì để trống và log warning.
- **Kiểm tra bước:** script tạm hoặc test render ra file `draft.pdf`, mở được và hiển thị đúng chữ có dấu.

### Bước 6 — Generate draft document

- **File tạo:**
  - `application/ports/media-storage.port.ts`: `uploadServerFile({ ownerId, purpose, buffer, fileName }): Promise<Uuid>`;
  - `infrastructure/media/identity-media-storage.adapter.ts`, gọi endpoint chốt ở Bước 1 (thêm method `post` vào `InternalHttpClient` nếu cần, và báo BE Lead đồng bộ lại `boilerplate`);
  - `application/commands/contract-generate-draft/`.
- **Cách làm:**
  1. Load contract. Phải là `draft`, nếu không trả `409`. Kiểm tra quyền landlord.
  2. Render PDF (Bước 5).
  3. `mediaStorage.uploadServerFile(...)`. Bước này nằm **ngoài** transaction DB.
  4. Mở UoW: `contract.attachDraftDocument(mediaId)`, `save`, append outbox.
  5. Trả `{ contractId, mediaId, purpose: 'contract_template' }`.
- **Kiểm tra bước:**
  - `POST /contracts/{id}/generate-draft-document` trả `201`;
  - `GET /media/{mediaId}` (P6-04) trả URL tải được đúng file PDF.

### Bước 7 — Đăng ký module và Swagger

- **File sửa:** `contract.module.ts` (controller, handler, provider cho 2 port); `contract-response-code.constant.ts` thêm `CONTRACT_TEMPLATES_FETCHED`, `CONTRACT_TEMPLATE_FETCHED`, `CONTRACT_TEMPLATE_APPLIED`, `CONTRACT_DRAFT_GENERATED`.
- **Kiểm tra bước:** `npm run build` + `npm run lint` pass; Swagger có đủ 4 `operationId`.

## Quyết định tạm thời / Ngoài phạm vi

- Nếu P6-04 chưa có internal upload: tạo `LocalMediaStorageAdapter` ghi file vào `tmp/` và trả UUID giả, chọn bằng biến env `MEDIA_STORAGE_DRIVER=local`. **Không merge vào `main` khi adapter thật chưa có**, ghi blocker vào issue.
- Chỉ xuất PDF, không làm Word (`.docx`); ghi `TODO`.
- CRUD mẫu HĐ (admin/landlord tự tạo mẫu) ngoài phạm vi; mẫu chỉ đến từ seeder.
- `templateVariables` tùy chỉnh do landlord nhập: chưa hỗ trợ, chỉ dùng biến lấy từ dữ liệu hệ thống.

## Cập nhật `api-doc`

- [ ] Sequence diagram cho apply-template và generate-draft-document. Diagram của generate phải có bước upload sang Identity/R2 ngoài transaction.
- [ ] Nếu có internal endpoint mới ở Identity: người làm P6-04 cập nhật `api-doc` (route internal không public qua gateway).
- [ ] `x-apidog-status` → `released` cho 4 endpoint; sync Apidog.

## Manual verification (Apidog)

1. `GET /contract-templates` → `200`, có `standard-room-lease-v1`.
2. Apply `standard-room-lease-v1` cho HĐ draft → `200 CONTRACT_TEMPLATE_APPLIED`; với key không tồn tại → `404 TEMPLATE_NOT_FOUND`.
3. Generate → `201`, tải file từ `mediaId` mở được, đúng tên tenant, giá thuê và ngày.
4. Generate trên HĐ `active` → `409 CONTRACT_NOT_DRAFT`.
5. HĐ thiếu `paymentDueDay` (biến bắt buộc) → `422 TEMPLATE_DATA_INVALID`.

## Definition of Done

- [ ] Bước 1–7 đã qua phần Kiểm tra bước; dùng adapter media thật (không phải `local`).
- [ ] `npm run build` + `npm run lint` pass.
- [ ] PR ghi `Closes pbl6-home-renter/docs#TBD`; đính kèm file PDF mẫu đã sinh.
- [ ] baoduong17 approve.
