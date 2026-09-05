# Short-Term vs Long-Term Rental: Feasibility Analysis

> Status: 🟡 DRAFT — inputs to decision D9 (long-term-only; this analysis reaffirms).
> Context: 5-person student team, 13–14 week timeline, SE course (PBL6). Product = long-term rental management (landlord web + tenant mobile + AI): monthly contracts, OCR utility-meter closing, auto-invoice, dynamic-QR payment reconciliation, roommate matching.
> Position: The team leans toward **NOT implementing short-term (Airbnb-style)** in this PBL6 scope.

---

## 1. Two Directions

### (A) Combine short-term + long-term in one platform
Extend the product to serve both:
- **Long-term:** monthly contracts, recurring invoices, utility closing, recurring QR payment.
- **Short-term:** daily pricing, availability calendar, OTA sync (Booking/Airbnb), nightly bookings, check-in/out, housekeeping.

The platform would need a unified data model and UI that somehow serves two very different guest journeys.

### (B) Long-term only — keep the schema extensible
Ship the planned long-term product. Keep `property_type` (and related fields) open in the database schema so short-term *could* be added later as a separate module without a redesign. No short-term features are built now.

---

## 2. Direction A — Deep Dive (What "Combine" Actually Requires)

The two models are **not the same workflow with different settings** — they are different businesses sharing a building.

| Concern | Long-term (our plan) | Short-term (Airbnb-style) | Extra work to combine |
|---|---|---|---|
| **Pricing model** | Per-month rent, usually fixed | Per-night, dynamic by date/season/demand | New pricing engine: date-based rates, weekend/season multipliers, minimum-stay rules |
| **Calendar / availability** | Occupied vs vacant (contractbound) | Granular per-night availability, blocking, gap-filling | Full booking calendar + conflict resolution per night |
| **OTA synchronization** | None | Sync to Booking.com / Airbnb via API/ical | Integrations + mapping + two-way sync + rate-limiter handling |
| **Contract type** | Monthly contract, e-sign, deposit, notice period | Nightly booking confirmation, no long contract | Separate "booking" entity; legal template differs entirely |
| **Utility closing** | Monthly OCR meter read → prorate | Per-stay (check-in/out meter or flat fee) | Different closing logic; per-stay vs monthly computation |
| **Payment reconciliation** | Recurring dynamic-QR per invoice | Per-booking (OTA payout + guest prepay) | Separate reconciliation path; OTA payout mismatch handling |
| **Legal / tax** | Residential tenancy law, monthly tax | Tourism license, accommodation tax, local short-term regs | New compliance surface; varies by city |
| **Housekeeping** | None (tenant self-manages) | Cleaning schedule between stays, turnover tasks | Housekeeping module + staff assignment |
| **Guest onboarding** | Tenant KYC, lease signing | Instant booking, ID at check-in, key handover | Different onboarding UX; messaging/chat with guest |

**Estimated additional modules (Direction A):**
- Dynamic pricing & availability calendar service
- OTA sync adapter layer (Booking/Airbnb/Agoda)
- Nightly booking & check-in/out workflow
- Housekeeping/turnover management
- Per-stay utility & tourism-tax engine
- Dual payment reconciliation (OTA payouts + QR)
- Reworked UI for two distinct user journeys

**Rough effort:** roughly **+60–80% scope** on top of the already-full long-term plan — effectively a second product.

---

## 3. Why Combining Is Infeasible in 13–14 Weeks / 5 People

1. **No shared lifecycle.** Long-term and short-term share almost nothing past "a room exists." Long-term = contract → recurring monthly invoice → utility close → QR reconcile. Short-term = availability → book → check-in → clean → check-out → OTA payout. There is **no common workflow to reuse**; combining means building two products with one login.
2. **Risk of shallow delivery.** Splitting effort means both sides are half-built. A shallow short-term module loses to **Smoobu** / **ezCloud** (Vietnam-focused channel manager + PMS for hotels/short-term). A shallow long-term module loses to **Mona House** / **KiotViet** (established Vietnamese property/rental management). Doing both weakly = losing on both fronts.
3. **Grading reality (SE course / PBL6).** Course assessment favors **depth, coherence, and a working demo** over feature breadth. A focused long-term platform with working OCR + auto-invoice + dynamic-QR reconciliation is demonstrable and gradeable. A sprawling half-short/half-long app is harder to present and easier to critique as "not finished."
4. **Team skill spread already maxed.** 5 people already cover PM, FE, Mobile, BE, AI. Adding OTA integration, pricing engine, and housekeeping is work with no owner and no slack in the schedule.

---

## 4. Talking Points — Defending "Long-Term Only" to the Teacher

- **"We chose depth over breadth."** PBL6 is a 14-week course; a working long-term 闭环 (contract → invoice → utility → QR pay) is a complete, demonstrable story. Short-term would dilute it.
- **"The two are different businesses."** Same building, completely different workflows, legal frames, and pricing. Combining is two products, not one feature.
- **"We studied the market."** Specialized tools already win: Smoobu/ezCloud for short-term, Mona House/KiotViet for long-term. A student team cannot out-ship either in 14 weeks; we focus where we can deliver real value.
- **"We are not closing the door."** `property_type` and the schema stay extensible. If short-term is needed later (post-course, or a future phase), it slots in as a new module without rework — this is informed scoping, not a limitation.
- **"Our AI features fit long-term."** Roommate matching and OCR utility closing are long-term-specific. They have no meaningful short-term equivalent, so our AI investment is protected.
- **"Scope is the source of truth."** `pm/requirement.md` defines long-term. Adding short-term is scope creep without PM/teacher-approved change control.

---

## 5. Recommendation

**Build long-term only.** Deliver the planned platform end-to-end: monthly contracts, OCR utility closing, auto-invoice, dynamic-QR reconciliation, roommate matching.

Keep the data model extensible — retain `property_type` (and availability/rate fields) as open, nullable columns so a short-term module *could* be added in a later phase without schema redesign. Document this decision in the project plan and decision log.

**Bottom line:** Combining is technically possible but educationally and practically infeasible in this timeline. Long-term-only is the responsible, gradeable, and strategically sound choice.
