# P6-02h — Manual meter readings, first-period baseline and image evidence

**Epic:** [P6-02](P6-02-tenancy-billing-vertical-slice.md)  
**Implementation:** Merged in `Tenancy-Service/main` (`2a83778`); documentation alignment is in a separate PR.
**Owner:** leminhkhai345 · **Iteration:** It6 · **Issue:** `docs#78`
**Dependency:** P6-02g1 for the issued-invoice period lock; P6-02g2 depends on the baseline migration from this task.

> The filename is retained for stable links. OCR preview is no longer part of this task under [P6-D78](../decisions.md#d78--manual-meter-readings-with-image-evidence).

## Scope and accepted decisions

- P6-D60: bulk create is atomic. A missing baseline returns `422 BASELINE_REQUIRED` and rolls back the entire request. Successful rows have `SUCCESS` only.
- P6-D70: a first-period ordinary reading can coexist with its baseline; its previous value is the same-period baseline's current value. Only the latest reading may be updated, and an invoice already `issued` locks the period. No DELETE operation in this MVP.
- P6-D78: landlord enters the value manually. There is no OCR endpoint, `source` or `ocrValue`. Image upload follows reading creation; the image is evidence and its absence does not block generation.
- P6-D69: Media upload uses the actual reading ID as owner. The merged API returns `evidenceMediaIds` and `evidenceMediaUrls` arrays. The singular `evidenceMediaId` remains a PATCH input for attaching one image.

## Implemented API contract

| Endpoint | Role | Success | Main validation/error behavior |
|---|---|---|---|
| `POST /meter-readings` | landlord | `201 METER_READING_CREATED` | Requires room, type, period, currentReading and isBaseline. Initial baseline may supply previousReading. Missing baseline for an ordinary reading returns `422 BASELINE_REQUIRED`. |
| `POST /meter-readings/bulk` | landlord | `201 METER_READINGS_BULK_RECORDED` | 1–200 items, atomic. Missing baseline aborts the entire request. Each item has roomId, type and currentReading; no image ID at creation. |
| `GET /meter-readings` | landlord | `200 METER_READINGS_FETCHED` | Paginated readings and image IDs/URLs. |
| `PATCH /meter-readings/{meterReadingId}` | landlord | `200 METER_READING_UPDATED` | At least one of currentReading/evidenceMediaId; latest-reading and issued-period checks. `409 METER_READING_NOT_LATEST` / `PERIOD_ALREADY_INVOICED`. |
| `PATCH /meter-readings/{readingId}/evidence` | landlord | `200 METER_READING_UPDATED` | Attach uploaded `evidenceMediaIds` to an existing reading. |

Amounts and readings are decimal strings in JSON and `numeric` in PostgreSQL. `period` is `YYYY-MM`. The response contains `id`, `roomId`, `buildingId`, `type`, `period`, `previousReading`, `currentReading`, `consumption`, `isBaseline`, `evidenceMediaIds`, `evidenceMediaUrls` and `createdAt`. No `readingDate` or OCR audit fields exist.

## Verification examples

| Input | Expected result |
|---|---|
| Baseline `2026-09` current `1200`, then ordinary reading in the same period current `1260` | Previous `1200`, consumption `60`. |
| Ordinary reading without any baseline | `422 BASELINE_REQUIRED`; bulk request has no persisted rows. |
| PATCH latest reading before invoice issue | Updated consumption; new image evidence may be attached. |
| PATCH older reading or an issued period | `409 METER_READING_NOT_LATEST` or `409 PERIOD_ALREADY_INVOICED`. |
| Create without evidence image | Succeeds; image arrays are empty and invoice generation remains possible. |

## Documentation and release gate

- Update `api-doc` paths, schemas, examples and PATCH sequence diagram in the documentation PR; remove the old OCR preview contract.
- The code is merged. API lint/bundle and live endpoint checks belong to the documentation and release review. Do not mark Apidog examples as executed without evidence.
