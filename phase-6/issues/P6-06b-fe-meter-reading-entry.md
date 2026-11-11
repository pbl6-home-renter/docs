# P6-06b — Manual meter reading entry with optional image evidence (Web)

**Epic:** [P6-06](P6-06-fe-contract-invoice-screens.md)
**Status:** Open; frontend completion has not been verified in this documentation pass.
**Owner:** ThaiBao11125 · **Review:** baoduong17 · **Estimate:** 3 points
**Dependencies:** P6-02e/f/h backend and P6-03c Room API
**Repo:** `fe` · **Iteration:** It6 · **Issue:** `docs#103`

> [P6-D78](../decisions.md#d78--manual-meter-readings-with-image-evidence) supersedes the former OCR and mandatory-image requirements. The linked backend implementation has merged; this frontend issue must use the current API contract.

## Goal

The landlord chooses a building and period, enters electricity and water values manually, and saves one room or an atomic building batch. The UI shows previous/current values, consumption, baseline needs, and a locked state when the period has an issued invoice. Photos are optional evidence that may be attached after the reading is saved. Image upload failure does not discard the reading or block invoice generation.

## API and field contract

| Operation | Purpose |
|---|---|
| `GET /meter-readings` | Paginated readings filtered by building and period; each item includes `evidenceMediaIds` and `evidenceMediaUrls` arrays. |
| `POST /meter-readings` | Create a baseline or ordinary reading with a manual decimal string; no `source`, `ocrValue`, or image ID at creation. |
| `POST /meter-readings/bulk` | Atomic create of 1–200 reading items; a missing baseline returns `422 BASELINE_REQUIRED` and saves none. |
| `PATCH /meter-readings/{meterReadingId}` | Change the latest reading before issue, and/or attach one uploaded image using `evidenceMediaId`. |
| `PATCH /meter-readings/{readingId}/evidence` | Attach one or more uploaded images using `evidenceMediaIds`. |

`currentReading` is a non-negative decimal string with at most two fractional digits. The first ordinary reading of a period uses that period's baseline as `previousReading`. The backend rejects an older reading update with `409 METER_READING_NOT_LATEST` and an issued period with `409 PERIOD_ALREADY_INVOICED` (P6-D70). The `evidenceMediaIds` array may be empty; the UI can offer an Add photo action without treating that state as a validation error.

## UI flow

1. Load rooms and existing readings for the selected building and `YYYY-MM` period. Show an empty state until a building is selected.
2. For each room, show electricity and water previous/current/consumption values. Offer manual entry and a baseline entry for a new contract. Keep unsaved values when validation fails.
3. Save an individual reading with `POST /meter-readings`, or submit complete values with `POST /meter-readings/bulk`. When a bulk item fails, show the error and keep the entire form for correction because the batch is atomic.
4. Optionally upload a photo through Media with `ownerType=meter_reading`, `ownerId=<readingId>`, `purpose=meter_reading_evidence`, then attach the media ID by PATCH. If upload or PATCH fails, keep the saved reading and let the user retry the photo step.
5. After reload, derive the photo state from `evidenceMediaIds`/`evidenceMediaUrls`; do not store a separate client-only flag. An issued period is read-only.

## Verification

- Manual entry succeeds with no image and remains visible after reload.
- A baseline and ordinary reading coexist in the first period; consumption uses their difference.
- One invalid bulk item leaves no new readings; correcting it allows the whole batch to save.
- Uploaded evidence remains visible after reload; a failed upload can be retried without creating a duplicate reading.
- Older readings and issued periods cannot be edited.

Do not add OCR preview calls, `source`, `ocrValue`, or an image requirement to this MVP. API documentation and frontend behavior should follow P6-D78 and the merged Tenancy contract.
