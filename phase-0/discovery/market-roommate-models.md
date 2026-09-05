# Market & Roommate Models — MVP Research

> Research draft for PBL6 long-term rental platform (landlord web + tenant mobile), Vietnam.
> Audience: students / young workers. Language: English (bilingual Vietnamese later).
> Status: ✅ **FINALIZED** (29/08) — PM decision locked as D21/D22/D26. Observed models & trade-offs below are the rationale.
> Source of truth for scope: `pm/phase-0/requirement.md`.

---

## TOPIC 1 — Landlord Intervention in Roommate Matching

### 1.1 Observed models in the real market

- **Roomi (US/global, 200+ cities)** — P2P roommate finder. The "lister" (a tenant with a spare room or a landlord) sets **roommate preferences** (gender, age range, budget, house rules, pet-friendliness) as filters. There is **no landlord approval step** on who matches whom; users swipe/match directly. Trust is handled by optional **ID verification + paid background checks** and listing verification (lease/utility bill/ID). *(Model a / c — constraints only, landlord outside.)*
- **Spotahome (Europe/LatAm, mid/long-term)** — Books individual **rooms in shared flats** monthly+. The provider (landlord/operator) lists the room; each incoming tenant is accepted by the provider, but the provider does **not vet or approve your specific roommates** — you share with whoever else is booked. *(Model a — constraints/house rules set; no match vetting.)*
- **Airbnb "Shared room"** — Host lists a shared sleeping space; **guests book independently** and are assigned to share with strangers. Host sets house rules but does **not approve the composition** of co-guests. *(Model a / c.)*
- **Zillow Rental Manager / "Roommates" + US classifieds** — Landlord or current tenant posts a room; applicants are screened by the **poster** (often the landlord runs a background/credit check on each applicant). Landlord effectively **approves each occupant**. *(Model b — landlord approves/rejects.)*
- **Vietnamese platforms — Chợ Tốt Nhà, Phòng Trọ 123, Batdongsan, Nhatro123, Bds123** — Pure **classifieds**. The "Tìm người ở ghép" (find roommate) sections are **tenant-to-tenant posts**: a tenant advertises a spare bed/room and others message them directly. **Landlord is fully outside** the matching; no vetting, no verification beyond the listing. *(Model c — pure P2P, landlord outside.)*
- **Facebook "Tìm người ở ghép" groups** — Entirely peer-to-peer; tenants post and coordinate. Landlord invisible. High scam/ghost-listing risk, no identity assurance. *(Model c.)*
- **University housing (VNU, RMIT, dormitories)** — The **institution assigns roommates** based on gender, faculty, intake period. This is the closest real example of an authority **imposing matches** (Model b, but the "landlord" is the school, not a private owner).

### 1.2 Trade-offs

| Model | Pros | Cons |
|-------|------|------|
| **(a) Landlord sets constraints only** (gender, max people, house rules, quiet hours) and does NOT vet matches | Low friction; scales; respects tenant autonomy; landlord avoids liability for "bad" matches; fits Vietnamese classified norm | Landlord has little control over who actually lives there; mismatch/dispute risk falls on tenants |
| **(b) Landlord approves/rejects each match** | Landlord control & quality; reduces bad-actor risk; common in US managed rentals | High operational cost; slow; privacy friction (landlord sees applicant data); legal exposure if rejection is discriminatory (gender/religion) |
| **(c) Pure P2P, landlord fully outside** | Simplest to build; mirrors Chợ Tốt/Facebook behavior users already know | No trust layer; scams; landlord may violate lease by unknowingly exceeding occupancy; platform adds little value |

### 1.3 RECOMMENDED MODEL for MVP — **Model (a)**

**Adopt Model (a): landlord/property sets only constraints (max occupancy, gender policy, house rules, price), and does NOT approve individual roommate matches. Matching is P2P between tenants, with an in-app verification badge.**

**Rationale (privacy + Vietnam legal constraints):**
- Matches Vietnamese user behavior (Chợ Tốt / Phòng Trọ 123 / Facebook groups are all Model c/a) — lowest adoption friction for students.
- Avoids Model (b)'s discrimination and privacy pitfalls: under **Decree 13/2023/ND-CP (PDPD)**, processing identity/ID data for approval decisions requires explicit, purpose-specific consent and raises sensitive-data obligations; a landlord "approving people" would push the platform into acting on personal data it should minimize.
- Landlord stays a **constraint-setter**, not a decision-maker on individuals → reduces the platform's data-processing scope and liability.
- Provide **optional ID verification** (consented, per PDPD Art. 11) as a trust signal, but never force landlord gatekeeping.

---

## TOPIC 2 — Shared-Room Contract & Payment

### 2.1 Observed models

- **(a) One representative contract + one representative payer** — Common in **Vietnam today**: a "lead tenant" (trưởng phòng) signs the lease with the landlord and pays the full rent; roommates **split offline** via bank transfer / MoMo / Zalo Pay. Phòng Trọ 123 / Chợ Tốt listings assume this. Legally, the lead tenant is jointly liable to the landlord.
- **(b) Each tenant signs own contract + system splits the bill** — Seen in **US student-housing / co-living** (managed co-living operators, roommate-friendly PMS). Each occupant has a separate lease addendum and is billed their share; the platform/PM collects per person. Higher legal clarity per person, but heavier contract & billing infrastructure.
- **(c) One contract but system tracks each person's share** — Hybrid: single lease between landlord and the group, but the **app records each member's owed share** and tracks who has paid. Used by some rent-splitting apps (Splitwise-style logic) layered on a traditional lease. Landlord still deals with one payer; internal splitting is auditable.

*(Airbnb note: Airbnb does NOT support guest-side split payment — the primary booker pays in full and reimburses others; only host-side co-host payouts are split. Relevant if we ever copy short-stay flows, but not for long-term leases.)*

### 2.2 Trade-offs

| Model | Pros | Cons |
|-------|------|------|
| **(a) One rep contract + one rep payer, offline split** | Matches Vietnam reality; simplest; no complex billing | Lead tenant bears all legal/financial risk; platform blind to who actually paid; disputes hard to resolve |
| **(b) Per-person contract + system split** | Clear individual liability; transparent; reduces lead-tenant risk | Complex legal templates; more support load; landlords may reject multiple contracts; KYC per person |
| **(c) One contract + system tracks shares** | Single lease (landlord-friendly) yet transparent splitting; audit trail | Still collective liability to landlord; someone must still pay the landlord in full |

### 2.3 RECOMMENDED MODEL for MVP — ✅ Finalized as D22

**PM chose: Contract = always 1 representative (lead tenant signs). Payment = landlord configurable — choose (1) representative payer (lead pays, offline split) OR (2) shared invoice (app tracks each person's share + payment status).**

**Rationale (Vietnam reality + legal liability):**
- Reflects the **actual Vietnamese practice** (lead tenant pays landlord, splits via bank transfer) — landlords will not change their contract habit for an MVP.
- Keeps landlord liability simple (single counterparty) while giving **tenants an in-app audit trail** of who-owes-what, reducing the #1 student complaint: roommate non-payment.
- Avoids the legal/operational burden of Model (b) (multiple contracts, per-person KYC, landlord buy-in) which is premature for MVP.
- We can **later** graduate to Model (b) if landlords request individual contracts. Note: under PDPD, storing each member's payment records is "basic personal data" — keep it consented and minimal.

---

## TOPIC 3 — Tenant Rental History / Credibility

### 3.1 Observed models & examples

- **(a) Platform-internal history only** — e.g., **Airbnb / Booking reviews**: trust is built from **past transactions inside the same platform** (ratings, reviews, verified ID). Portable only within the app. This is the dominant low-friction model globally.
- **(b) Cross-platform credit/score** — e.g., **US Experian RentBureau**: landlords and PMS report rent payments (positive + negative) to a credit bureau; ~36M renter profiles, used in screening. Requires FCRA-style regulation, bureau infrastructure, and landlord participation. **Vietnam has NO equivalent** — no rental credit bureau, no cross-platform rental history; CIC (Credit Information Center) covers bank credit only, not rent.
- **(c) Defer / no feature** — Many Vietnamese platforms (Chợ Tốt, Phòng Trọ 123) **do not assess credibility at all**; trust is left to cash deposits and face-to-face meetings. Facebook groups rely on mutual connections.

### 3.2 Trade-offs

| Model | Pros | Cons |
|-------|------|------|
| **(a) Internal history, shown with tenant consent** | Builds trust over time; privacy-safe; fully within our control; PDPD-compliant if consented | Cold-start problem (new users have no history); limited to our user base |
| **(b) Cross-platform credit/score** | Strong signal; reduces bad tenants | **Not feasible in Vietnam** (no bureau, no data source); major PDPD cross-border + sensitive-data risk; high cost; potential for discriminatory profiling |
| **(c) Defer / no feature** | Zero build; matches local norm | No trust differentiation; scams persist |

### 3.3 RECOMMENDED MODEL for MVP — ✅ Finalized as D26 (Stretch)

**PM chose Model (a) as Stretch (not MVP): platform-internal rental history (past rentals, on-time payments, reviews) shown only with the tenant's explicit consent, plus optional consented ID verification. Defer any cross-platform/credit-score feature (Model b) entirely.**

**Rationale (privacy + PDPD 2023):**
- **PDPD 13/2023/ND-CP** is consent-centric (Art. 11): any credibility feature must rest on **voluntary, informed, revocable consent**, and silence ≠ consent. An internal, consented history satisfies this; a scored/aggregated external profile would not.
- Vietnam has **no rental credit infrastructure** — Model (b) is both infeasible and legally hazardous (sensitive data, cross-border transfer rules, DPO obligation for sensitive-data processors under PDPD).
- Internal history **minimizes data** (data minimization principle, Art. 3) and keeps processing inside our boundary — lowest compliance surface for an MVP.
- Cold-start is acceptable for MVP; we can later add **consented** linkages (e.g., reference from a previous landlord) without building a credit bureau.

---

## Cross-cutting notes for MVP

1. **Consent is the backbone** — every credibility/identity feature must implement PDPD Art. 11 (clear purpose, type of data, who processes it, rights; revocable; silence ≠ consent).
2. **Landlord = constraint-setter, not gatekeeper** — reduces our personal-data processing scope across all three topics.
3. **Mirror local behavior** — Chợ Tốt / Phòng Trọ 123 / Facebook "ở ghép" patterns (Model a/c, lead-tenant payment, no scoring) give the fastest student adoption.
4. **Defer heavy infra** — per-person contracts and credit scoring are post-MVP, not MVP.
