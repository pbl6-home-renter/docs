# Rentify — Stitch Prompts — MOBILE (2 separate apps: Tenant & Landlord)

> **⚠️ ARCHITECTURE v1.2:** Tenant and Landlord are now **two completely
> separate mobile apps** (two separate Stitch projects) — NOT one shared
> app with a role picker. This file contains prompts for BOTH apps,
> clearly separated into two ZONES so they never get mixed up:
> - **ZONE A (below): "Rentify Tenant — Mobile App"** — open a Stitch
>   project named exactly this, and paste ONLY the Zone A prompts into it.
> - **ZONE B (further down): "Rentify Landlord — Mobile App"** — open a
>   SEPARATE, SECOND Stitch project named exactly this, and paste ONLY the
>   Zone B prompts into it.
>
> Do not mix screens between the two projects. Each zone is fully
> self-contained (its own Auth flow, its own screen numbering starting at
> 1). Within each zone, paste **one prompt block at a time**, in order,
> waiting for each batch to finish before pasting the next (Stitch appends
> to the project, it doesn't overwrite).
>
> Every screen description below states EXACTLY what must appear — no more,
> no less. If Stitch adds anything not listed (a badge, a claim, a label,
> extra copy), that is a fabrication and must be removed via a follow-up
> Edit prompt. See the STRICT CONTENT RULE inside the Design System block
> below — it exists specifically to prevent this.

---

## 🎨 DESIGN SYSTEM (identical for every prompt in this file — Tenant and Landlord alike)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real aligned lists/tables, not everything stuffed into its own floating
rounded card. Numbers look like real data (specific, slightly irregular
values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type size/weight
and spacing, not from wrapping things in boxes or decorative labels. Icons
are small and functional, never decorative illustrations. This is a
FULL-COLOR request (not a grayscale wireframe).

STRICT CONTENT RULE (critical — read carefully): Generate EXACTLY the
elements listed in the "SCREENS TO GENERATE" section below for each screen
— nothing more. Do NOT invent additional badges, banners, taglines,
security/trust claims, status indicators, decorative icons, marketing
copy, or "polish" elements that are not explicitly listed. If a screen's
spec lists 5 elements, the screen should have exactly those 5 elements.
When in doubt, generate LESS rather than more. This rule exists because
past generations invented things like a fake "256-bit encrypted" security
badge, a fabricated "Ready" status indicator, an invented "AUTH" category
label, and a made-up "Bank-grade identity screening" claim — NONE of that
is acceptable. Every single piece of text or UI element on a screen must
trace back to an explicit line in the spec below.

EXPLICITLY BANNED:
- No all-caps text anywhere
- No middle-dot (·), slash (//), or decorative em-dash chrome in headings or labels
- No code-style naming visible in the UI (no "SCREEN_01", no "SPEC_X")
- No monospace font anywhere — use exactly one typeface: Inter
- No gratuitous drop shadows on every card — shadows only where specified below
- No wrapping every section/block in an identical bordered card — use plain
  whitespace as the default separator; only add a border or shadow when a
  rule below calls for it
- No suspiciously round/fake demo numbers — use specific, slightly irregular numbers
- No decorative illustration or gradient hero blocks with no real function
- No filled/colored pill-shaped badges anywhere — use the mandatory
  dot-indicator / outlined-tag system below instead
- No internal/dev category labels or chips (e.g. "AUTH", "SCREEN_X",
  section tags) rendered as visible UI elements — these are for our own
  organizational reference only and must never appear to a real user
- No fabricated status, security, or trust indicators anywhere (e.g.
  "256-bit encrypted", "Ready", "Bank-grade identity screening", "Verified
  by [made-up brand]") — every piece of text/badge on a screen must come
  directly from this spec; do not invent extra system-status or trust
  signals to make a screen look more polished

DESIGN TOKENS (use exactly these values):
- Background: #F8FBFE (very light pastel blue tint, near-white — not pure
  white, not warm cream)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active nav tab icon. Do NOT apply it to every button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — do not soften to orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data (amounts, meter
  readings) uses Inter's tabular figures.
- Shape & elevation (CONTEXTUAL, not one fixed value everywhere):
  - Hero/highlight card (the one standout element per screen): 24px corner
    radius + a soft shadow tinted toward the background blue,
    rgba(30,111,217,0.10)
  - Regular list/content cards: 14px corner radius, flat, NO shadow — 1px
    solid border (#D7E3F2) only
  - Buttons: 12px corner radius
- Badges & tags (MANDATORY on every screen with any status or descriptive label):
  - Live status (room availability, verification, payment/invoice status,
    issue status): a small 7px filled dot in the semantic color, followed
    by plain navy text — NO colored background fill, NO pill container.
  - Descriptive constraint tag (fixed attributes like "Female Only", "Max 3
    People", "No Pets"): a rectangular tag, 7px corner radius, 1px solid
    border (#D7E3F2), NO background fill, plain navy text — same outlined
    style regardless of whether the attribute reads positive or negative.
  - NEVER use a filled/colored pill badge anywhere in this project.
- Layout: on the Dashboard screen, cards may overlap/stagger slightly for
  visual depth (the one screen where that's appropriate). On list/data
  screens (invoices, members, search results), use a strict aligned grid —
  no overlapping, no staggering; clarity over personality.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  the Primary Accent color #1E6FD9. This is a placeholder — it can be
  swapped later via a short, targeted Edit prompt without affecting other
  screens.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: mobile portrait 375x812px unless noted otherwise.
```

---
---

# ZONE A — "Rentify Tenant — Mobile App" (34 screens, 7 prompts)

> Open a Stitch project named **"Rentify Tenant — Mobile App"**. This app
> serves ONLY tenants/guests — there is no role picker, no landlord
> content anywhere in this project. Bottom navigation (5 tabs, shown on
> every screen once logged in): **Find a room · Roommate Match · Messages
> · My Room · Account**.

## Prompt T1/7 — Auth (8 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real aligned lists/tables, not everything stuffed into its own floating
rounded card. Numbers look like real data (specific, slightly irregular
values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type size/weight
and spacing, not from wrapping things in boxes or decorative labels. Icons
are small and functional, never decorative illustrations. This is a
FULL-COLOR request (not a grayscale wireframe).

STRICT CONTENT RULE (critical — read carefully): Generate EXACTLY the
elements listed in the "SCREENS TO GENERATE" section below for each screen
— nothing more. Do NOT invent additional badges, banners, taglines,
security/trust claims, status indicators, decorative icons, marketing
copy, or "polish" elements that are not explicitly listed. If a screen's
spec lists 5 elements, the screen should have exactly those 5 elements.
When in doubt, generate LESS rather than more. This rule exists because
past generations invented things like a fake "256-bit encrypted" security
badge, a fabricated "Ready" status indicator, an invented "AUTH" category
label, and a made-up "Bank-grade identity screening" claim — NONE of that
is acceptable. Every single piece of text or UI element on a screen must
trace back to an explicit line in the spec below.

EXPLICITLY BANNED:
- No all-caps text anywhere
- No middle-dot (·), slash (//), or decorative em-dash chrome in headings or labels
- No code-style naming visible in the UI (no "SCREEN_01", no "SPEC_X")
- No monospace font anywhere — use exactly one typeface: Inter
- No gratuitous drop shadows on every card — shadows only where specified below
- No wrapping every section/block in an identical bordered card — use plain
  whitespace as the default separator; only add a border or shadow when a
  rule below calls for it
- No suspiciously round/fake demo numbers — use specific, slightly irregular numbers
- No decorative illustration or gradient hero blocks with no real function
- No filled/colored pill-shaped badges anywhere — use the mandatory
  dot-indicator / outlined-tag system below instead
- No internal/dev category labels or chips (e.g. "AUTH", "SCREEN_X",
  section tags) rendered as visible UI elements — these are for our own
  organizational reference only and must never appear to a real user
- No fabricated status, security, or trust indicators anywhere (e.g.
  "256-bit encrypted", "Ready", "Bank-grade identity screening", "Verified
  by [made-up brand]") — every piece of text/badge on a screen must come
  directly from this spec; do not invent extra system-status or trust
  signals to make a screen look more polished

DESIGN TOKENS (use exactly these values):
- Background: #F8FBFE (very light pastel blue tint, near-white — not pure
  white, not warm cream)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active nav tab icon. Do NOT apply it to every button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — do not soften to orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data (amounts, meter
  readings) uses Inter's tabular figures.
- Shape & elevation (CONTEXTUAL, not one fixed value everywhere):
  - Hero/highlight card (the one standout element per screen): 24px corner
    radius + a soft shadow tinted toward the background blue,
    rgba(30,111,217,0.10)
  - Regular list/content cards: 14px corner radius, flat, NO shadow — 1px
    solid border (#D7E3F2) only
  - Buttons: 12px corner radius
- Badges & tags (MANDATORY on every screen with any status or descriptive label):
  - Live status (room availability, verification, payment/invoice status,
    issue status): a small 7px filled dot in the semantic color, followed
    by plain navy text — NO colored background fill, NO pill container.
  - Descriptive constraint tag (fixed attributes like "Female Only", "Max 3
    People", "No Pets"): a rectangular tag, 7px corner radius, 1px solid
    border (#D7E3F2), NO background fill, plain navy text — same outlined
    style regardless of whether the attribute reads positive or negative.
  - NEVER use a filled/colored pill badge anywhere in this project.
- Layout: on the Dashboard screen, cards may overlap/stagger slightly for
  visual depth (the one screen where that's appropriate). On list/data
  screens (invoices, members, search results), use a strict aligned grid —
  no overlapping, no staggering; clarity over personality.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  the Primary Accent color #1E6FD9. This is a placeholder — it can be
  swapped later via a short, targeted Edit prompt without affecting other
  screens.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: mobile portrait 375x812px unless noted otherwise.

CONTEXT: The authentication flow for the Tenant app. There is no role
selection anywhere — this app is exclusively for Tenants/Guests. Generate
the following 8 screens, named EXACTLY as numbered below.

SCREENS TO GENERATE:

1. Splash
- ONLY a centered Rentify logo (placeholder) on the #F8FBFE background.
  Nothing else on screen — no buttons, no status text, no progress
  indicator, no tagline.
- Comes from: app launch (first screen in the session).
- Goes to: auto-advances after ~1-2s. If a valid token exists → straight
  to "9. Home / Room List". If no token → "2. Login".

2. Login
- Exactly these elements: Email input, Password input (with an eye icon to
  show/hide), a full-width "Log in" button (Primary Accent), a "Forgot
  password?" link below the button, and a "Don't have an account? Sign up"
  line at the bottom. Inline error state (a STATE of this same screen, not
  a separate screen): red outline around the inputs + small red text
  "Incorrect email or password" below the button.
- Comes from: "1. Splash" (no token), or any action elsewhere that
  requires login (opens as a bottom sheet sliding up over the current
  screen), or from "7. Logout Confirmation" after logging out.
- Goes to: correct login → "9. Home / Room List" (if the account is
  restricted, see the banner behavior described in "6"). Tapping "Forgot
  password?" → "3. Forgot Password". Tapping "Sign up" → "5. Sign Up".

3. Forgot Password — Enter Email
- Exactly these elements: a title "Forgot your password?", one short
  description line, one Email input, a "Send reset link" button. After
  tapping send, the SAME screen shows a success state: the button area is
  replaced by a green checkmark icon + text "Sent! Check your inbox".
- Comes from: "2. Login" ("Forgot password?" link).
- Goes to: a "Back to Login" button → "2. Login".

4. Reset Password
- Exactly these elements: a title "Set a new password", two inputs (New
  Password, Confirm Password), a "Reset password" button.
- Comes from: the email link (simulated from "3" for demo purposes — this
  is a real production screen, just reached differently in a live app).
- Goes to: success → "2. Login" with a small success banner "Password
  changed successfully, please log in again".

5. Sign Up
- Exactly these elements: Email, Password, Confirm Password (both with an
  eye icon), Full name, Phone number inputs, a "Sign up" button, and a
  "Already have an account? Log in" line at the bottom. Inline validation:
  if Password and Confirm Password don't match, show a red outline + small
  red text "Passwords don't match" under the Confirm Password field.
- Comes from: "2. Login" (sign-up link), or directly from any gated action.
- Goes to: successful sign-up → straight into "9. Home / Room List".

6. Account Restricted (banner state)
- This is a variant of "24. My Room Hub" (see Prompt T5) with ONE addition:
  a persistent warning banner at the very top of the screen (light red
  background, red #DC2626 left border, a warning icon) reading: "Your
  account is restricted: you can only view & pay your current lease. You
  cannot renew or search for a new room." Below the banner, the "Find a
  room" and "Roommate Match" bottom-nav tab icons appear visually dimmed
  (gray instead of navy/accent); tapping either shows a small tooltip "This
  feature is restricted". Do not add anything else beyond this banner and
  the dimmed tabs — everything else on the screen is identical to the
  normal "24. My Room Hub".
- Comes from: logging in successfully with a restricted account.
- Goes to: the other tabs (Messages, My Room, Account) work normally.

7. Logout Confirmation
- Exactly these elements: a small dialog (bottom sheet) with the text "Are
  you sure you want to log out?" and two buttons: "Log out" (red #DC2626)
  and "Cancel" (navy outline).
- Comes from: the "Log out" item on "33. Profile" (Prompt T7).
- Goes to: confirm → clears the session, returns to "2. Login". Cancel →
  closes the dialog, no navigation.

8. Generic Error
- Exactly these elements: a simple non-decorative icon, a title that
  depends on the error type ("No internet connection" / "Something went
  wrong" / "Page not found"), one short description line, a "Try again"
  button.
- Comes from: any screen when an API call fails.
- Goes to: "Try again" → returns to the action/screen that failed.
```

---

## Prompt T2/7 — Room Search & Detail (4 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real aligned lists/tables, not everything stuffed into its own floating
rounded card. Numbers look like real data (specific, slightly irregular
values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type size/weight
and spacing, not from wrapping things in boxes or decorative labels. Icons
are small and functional, never decorative illustrations. This is a
FULL-COLOR request (not a grayscale wireframe).

STRICT CONTENT RULE (critical — read carefully): Generate EXACTLY the
elements listed in the "SCREENS TO GENERATE" section below for each screen
— nothing more. Do NOT invent additional badges, banners, taglines,
security/trust claims, status indicators, decorative icons, marketing
copy, or "polish" elements that are not explicitly listed. If a screen's
spec lists 5 elements, the screen should have exactly those 5 elements.
When in doubt, generate LESS rather than more. This rule exists because
past generations invented things like a fake "256-bit encrypted" security
badge, a fabricated "Ready" status indicator, an invented "AUTH" category
label, and a made-up "Bank-grade identity screening" claim — NONE of that
is acceptable. Every single piece of text or UI element on a screen must
trace back to an explicit line in the spec below.

EXPLICITLY BANNED:
- No all-caps text anywhere
- No middle-dot (·), slash (//), or decorative em-dash chrome in headings or labels
- No code-style naming visible in the UI (no "SCREEN_01", no "SPEC_X")
- No monospace font anywhere — use exactly one typeface: Inter
- No gratuitous drop shadows on every card — shadows only where specified below
- No wrapping every section/block in an identical bordered card — use plain
  whitespace as the default separator; only add a border or shadow when a
  rule below calls for it
- No suspiciously round/fake demo numbers — use specific, slightly irregular numbers
- No decorative illustration or gradient hero blocks with no real function
- No filled/colored pill-shaped badges anywhere — use the mandatory
  dot-indicator / outlined-tag system below instead
- No internal/dev category labels or chips (e.g. "AUTH", "SCREEN_X",
  section tags) rendered as visible UI elements — these are for our own
  organizational reference only and must never appear to a real user
- No fabricated status, security, or trust indicators anywhere (e.g.
  "256-bit encrypted", "Ready", "Bank-grade identity screening", "Verified
  by [made-up brand]") — every piece of text/badge on a screen must come
  directly from this spec; do not invent extra system-status or trust
  signals to make a screen look more polished

DESIGN TOKENS (use exactly these values):
- Background: #F8FBFE (very light pastel blue tint, near-white — not pure
  white, not warm cream)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active nav tab icon. Do NOT apply it to every button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — do not soften to orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data (amounts, meter
  readings) uses Inter's tabular figures.
- Shape & elevation (CONTEXTUAL, not one fixed value everywhere):
  - Hero/highlight card (the one standout element per screen): 24px corner
    radius + a soft shadow tinted toward the background blue,
    rgba(30,111,217,0.10)
  - Regular list/content cards: 14px corner radius, flat, NO shadow — 1px
    solid border (#D7E3F2) only
  - Buttons: 12px corner radius
- Badges & tags (MANDATORY on every screen with any status or descriptive label):
  - Live status (room availability, verification, payment/invoice status,
    issue status): a small 7px filled dot in the semantic color, followed
    by plain navy text — NO colored background fill, NO pill container.
  - Descriptive constraint tag (fixed attributes like "Female Only", "Max 3
    People", "No Pets"): a rectangular tag, 7px corner radius, 1px solid
    border (#D7E3F2), NO background fill, plain navy text — same outlined
    style regardless of whether the attribute reads positive or negative.
  - NEVER use a filled/colored pill badge anywhere in this project.
- Layout: on the Dashboard screen, cards may overlap/stagger slightly for
  visual depth (the one screen where that's appropriate). On list/data
  screens (invoices, members, search results), use a strict aligned grid —
  no overlapping, no staggering; clarity over personality.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  the Primary Accent color #1E6FD9. This is a placeholder — it can be
  swapped later via a short, targeted Edit prompt without affecting other
  screens.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: mobile portrait 375x812px unless noted otherwise.

CONTEXT: The "Find a room" tab — the default tab after login, and also the
first thing a not-yet-logged-in visitor sees when they open the app for
the first time (browsing is allowed without an account; login is only
required to save a room or contact a landlord).

SCREENS TO GENERATE:

9. Home / Room List
- Exactly these elements: a header with a search bar (input + magnifying-
  glass icon) and a Filter icon next to it; below, a vertically scrolling
  list of room cards. Each card contains exactly: a cover photo, the price
  (bold, large), the area/district name, the room size, up to 2 outlined
  constraint tags (e.g. "Female Only"), and a distance value if available.
  Bottom navigation with 5 tabs, "Find a room" tab active.
- Comes from: app open (not logged in or logged in as Tenant), or tapping
  the "Find a room" tab from anywhere.
- Goes to: tapping the Filter icon → "10. Room Filter" (bottom sheet).
  Tapping a room card → "11. Room Detail". Tapping a "Saved" icon in the
  header → "12. Saved Rooms".

10. Room Filter
- A bottom sheet (~80% of screen height) containing exactly: a price-range
  slider (two handles), a size slider, an area/district selector
  (dropdown or chips), amenity checkboxes (AC, loft bed, wifi, flexible
  hours), and a full-width "Apply" button (Primary Accent) fixed at the
  bottom of the sheet.
- Comes from: the Filter icon on "9. Home / Room List".
- Goes to: "Apply" → closes the sheet, returns to "9" with filtered
  results.

11. Room Detail
- Exactly these elements, top to bottom: a full-width photo gallery with
  carousel dots; the room title + price (bold, large); the full address
  with a location icon (shown in full immediately, never hidden/redacted);
  a row of exactly 3 outlined constraint tags (e.g. "Female Only", "Max 3
  People", "Available Now"); a row of amenity icons with small labels; a
  2-3 line description paragraph; a landlord-contact block containing
  exactly: a circular avatar, the landlord's name, a green dot-indicator
  "Verified" tag, a phone number, and a small "Call" button; a fixed
  bottom bar with a heart "Save" icon on the left and a large "Contact
  Landlord" button (Primary Accent) on the right. The whole screen stays
  neutral in color — the ONLY accent-colored element is the "Contact
  Landlord" button.
- Comes from: tapping a card on "9" or "12".
- Goes to: the heart icon while logged out → opens "2. Login" as a bottom
  sheet; while logged in → saves immediately (icon fills solid red), no
  screen change. "Contact Landlord" while logged out → gated "2. Login";
  while logged in → opens "19. Landlord Direct Chat" (Prompt T4).

12. Saved Rooms
- A list of saved rooms, each item identical to the cards on "9" plus a
  solid red heart icon in the corner for quick unsaving. Empty state:
  exactly a simple non-decorative icon + the text "You haven't saved any
  rooms yet."
- Comes from: the "Saved" icon on "9", or a shortcut on "33. Profile".
- Goes to: tapping an item → "11. Room Detail". Tapping the heart icon on
  an item → unsaves immediately, no navigation.
```

---

## Prompt T3/7 — Roommate Match (5 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real aligned lists/tables, not everything stuffed into its own floating
rounded card. Numbers look like real data (specific, slightly irregular
values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type size/weight
and spacing, not from wrapping things in boxes or decorative labels. Icons
are small and functional, never decorative illustrations. This is a
FULL-COLOR request (not a grayscale wireframe).

STRICT CONTENT RULE (critical — read carefully): Generate EXACTLY the
elements listed in the "SCREENS TO GENERATE" section below for each screen
— nothing more. Do NOT invent additional badges, banners, taglines,
security/trust claims, status indicators, decorative icons, marketing
copy, or "polish" elements that are not explicitly listed. If a screen's
spec lists 5 elements, the screen should have exactly those 5 elements.
When in doubt, generate LESS rather than more. This rule exists because
past generations invented things like a fake "256-bit encrypted" security
badge, a fabricated "Ready" status indicator, an invented "AUTH" category
label, and a made-up "Bank-grade identity screening" claim — NONE of that
is acceptable. Every single piece of text or UI element on a screen must
trace back to an explicit line in the spec below.

EXPLICITLY BANNED:
- No all-caps text anywhere
- No middle-dot (·), slash (//), or decorative em-dash chrome in headings or labels
- No code-style naming visible in the UI (no "SCREEN_01", no "SPEC_X")
- No monospace font anywhere — use exactly one typeface: Inter
- No gratuitous drop shadows on every card — shadows only where specified below
- No wrapping every section/block in an identical bordered card — use plain
  whitespace as the default separator; only add a border or shadow when a
  rule below calls for it
- No suspiciously round/fake demo numbers — use specific, slightly irregular numbers
- No decorative illustration or gradient hero blocks with no real function
- No filled/colored pill-shaped badges anywhere — use the mandatory
  dot-indicator / outlined-tag system below instead
- No internal/dev category labels or chips (e.g. "AUTH", "SCREEN_X",
  section tags) rendered as visible UI elements — these are for our own
  organizational reference only and must never appear to a real user
- No fabricated status, security, or trust indicators anywhere (e.g.
  "256-bit encrypted", "Ready", "Bank-grade identity screening", "Verified
  by [made-up brand]") — every piece of text/badge on a screen must come
  directly from this spec; do not invent extra system-status or trust
  signals to make a screen look more polished

DESIGN TOKENS (use exactly these values):
- Background: #F8FBFE (very light pastel blue tint, near-white — not pure
  white, not warm cream)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active nav tab icon. Do NOT apply it to every button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — do not soften to orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data (amounts, meter
  readings) uses Inter's tabular figures.
- Shape & elevation (CONTEXTUAL, not one fixed value everywhere):
  - Hero/highlight card (the one standout element per screen): 24px corner
    radius + a soft shadow tinted toward the background blue,
    rgba(30,111,217,0.10)
  - Regular list/content cards: 14px corner radius, flat, NO shadow — 1px
    solid border (#D7E3F2) only
  - Buttons: 12px corner radius
- Badges & tags (MANDATORY on every screen with any status or descriptive label):
  - Live status (room availability, verification, payment/invoice status,
    issue status): a small 7px filled dot in the semantic color, followed
    by plain navy text — NO colored background fill, NO pill container.
  - Descriptive constraint tag (fixed attributes like "Female Only", "Max 3
    People", "No Pets"): a rectangular tag, 7px corner radius, 1px solid
    border (#D7E3F2), NO background fill, plain navy text — same outlined
    style regardless of whether the attribute reads positive or negative.
  - NEVER use a filled/colored pill badge anywhere in this project.
- Layout: on the Dashboard screen, cards may overlap/stagger slightly for
  visual depth (the one screen where that's appropriate). On list/data
  screens (invoices, members, search results), use a strict aligned grid —
  no overlapping, no staggering; clarity over personality.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  the Primary Accent color #1E6FD9. This is a placeholder — it can be
  swapped later via a short, targeted Edit prompt without affecting other
  screens.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: mobile portrait 375x812px unless noted otherwise.

CONTEXT: The "Roommate Match" tab. Browsing the feed requires no login;
sending a request, creating a profile, and messaging require login. If the
account is restricted (screen "6"), this whole tab is dimmed/locked.

SCREENS TO GENERATE:

13. Match Feed
- A REGULAR vertical scroll (explicitly NOT a Tinder-style swipe
  interaction) — each card takes up most of the screen and contains
  exactly: a large photo, display name, short bio, budget, desired area, an
  age/gender outlined tag, and one additional outlined tag "Match: 87%"
  (an AI-computed compatibility score — vary the percentage slightly
  across different cards, e.g. 87%, 72%, 94%, to look like real computed
  data; use the same outlined-tag style, NOT a colored pill). Header
  contains exactly two icons: "My Profile" and "Requests" (the latter with
  a small red badge if there are new requests).
- Comes from: tapping the "Roommate Match" tab from anywhere.
- Goes to: tapping a card → "14. Roommate Profile Detail". Tapping "My
  Profile" → "15. Create/Edit Roommate Profile" (gated login). Tapping
  "Requests" → "16. Sent/Received Requests" (gated login).

14. Roommate Profile Detail
- Exactly: a large photo, the full description (lifestyle, budget, desired
  area, move-in timing), the same "Match: 87%" outlined tag near the top,
  and a large "Send Request" button fixed at the bottom.
- Comes from: tapping a card on "13".
- Goes to: "Send Request" while logged out → gated "2. Login"; while
  logged in → sends immediately, shows a toast "Request sent", stays on
  this screen, the button becomes "Request Sent" (disabled, gray).

15. Create/Edit Roommate Profile
- Exactly: a photo upload field, a lifestyle description textarea, a
  budget input, a desired-area input, a move-in-timing input, and — at the
  very top of the form — a toggle "Looking for a roommate: On/Off" (when
  off, the profile is hidden from the Feed). A "Save" button fixed at the
  bottom.
- Comes from: the "My Profile" icon on "13".
- Goes to: "Save" → returns to "13".

16. Sent/Received Requests
- Exactly two tabs at the top: "Sent" and "Received". Each list item shows
  an avatar, name, and status. On "Received": each item additionally has
  two small buttons directly on it — "Accept" (Accent) and "Decline"
  (outline) — actioned right there, no separate detail view needed. On
  "Sent": only the status text is shown (Pending / Declined), no buttons.
- Comes from: the "Requests" icon on "13".
- Goes to: "Accept" on a "Received" item → "17. Match Success". "Decline"
  → the item disappears from the list, no navigation.

17. Match Success
- Exactly: a simple non-decorative icon or illustration (e.g. two
  overlapping circles), a title "It's a match!", the matched person's
  name, and a large "Message now" button (Primary Accent). Do NOT show any
  phone number, Zalo handle, or other contact info on this screen.
- Comes from: "Accept" on "16".
- Goes to: "Message now" → "22. Roommate Match Chat" (Prompt T4).
```

---

## Prompt T4/7 — Inbox/Chat (5 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real aligned lists/tables, not everything stuffed into its own floating
rounded card. Numbers look like real data (specific, slightly irregular
values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type size/weight
and spacing, not from wrapping things in boxes or decorative labels. Icons
are small and functional, never decorative illustrations. This is a
FULL-COLOR request (not a grayscale wireframe).

STRICT CONTENT RULE (critical — read carefully): Generate EXACTLY the
elements listed in the "SCREENS TO GENERATE" section below for each screen
— nothing more. Do NOT invent additional badges, banners, taglines,
security/trust claims, status indicators, decorative icons, marketing
copy, or "polish" elements that are not explicitly listed. If a screen's
spec lists 5 elements, the screen should have exactly those 5 elements.
When in doubt, generate LESS rather than more. This rule exists because
past generations invented things like a fake "256-bit encrypted" security
badge, a fabricated "Ready" status indicator, an invented "AUTH" category
label, and a made-up "Bank-grade identity screening" claim — NONE of that
is acceptable. Every single piece of text or UI element on a screen must
trace back to an explicit line in the spec below.

EXPLICITLY BANNED:
- No all-caps text anywhere
- No middle-dot (·), slash (//), or decorative em-dash chrome in headings or labels
- No code-style naming visible in the UI (no "SCREEN_01", no "SPEC_X")
- No monospace font anywhere — use exactly one typeface: Inter
- No gratuitous drop shadows on every card — shadows only where specified below
- No wrapping every section/block in an identical bordered card — use plain
  whitespace as the default separator; only add a border or shadow when a
  rule below calls for it
- No suspiciously round/fake demo numbers — use specific, slightly irregular numbers
- No decorative illustration or gradient hero blocks with no real function
- No filled/colored pill-shaped badges anywhere — use the mandatory
  dot-indicator / outlined-tag system below instead
- No internal/dev category labels or chips (e.g. "AUTH", "SCREEN_X",
  section tags) rendered as visible UI elements — these are for our own
  organizational reference only and must never appear to a real user
- No fabricated status, security, or trust indicators anywhere (e.g.
  "256-bit encrypted", "Ready", "Bank-grade identity screening", "Verified
  by [made-up brand]") — every piece of text/badge on a screen must come
  directly from this spec; do not invent extra system-status or trust
  signals to make a screen look more polished

DESIGN TOKENS (use exactly these values):
- Background: #F8FBFE (very light pastel blue tint, near-white — not pure
  white, not warm cream)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active nav tab icon. Do NOT apply it to every button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — do not soften to orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data (amounts, meter
  readings) uses Inter's tabular figures.
- Shape & elevation (CONTEXTUAL, not one fixed value everywhere):
  - Hero/highlight card (the one standout element per screen): 24px corner
    radius + a soft shadow tinted toward the background blue,
    rgba(30,111,217,0.10)
  - Regular list/content cards: 14px corner radius, flat, NO shadow — 1px
    solid border (#D7E3F2) only
  - Buttons: 12px corner radius
- Badges & tags (MANDATORY on every screen with any status or descriptive label):
  - Live status (room availability, verification, payment/invoice status,
    issue status): a small 7px filled dot in the semantic color, followed
    by plain navy text — NO colored background fill, NO pill container.
  - Descriptive constraint tag (fixed attributes like "Female Only", "Max 3
    People", "No Pets"): a rectangular tag, 7px corner radius, 1px solid
    border (#D7E3F2), NO background fill, plain navy text — same outlined
    style regardless of whether the attribute reads positive or negative.
  - NEVER use a filled/colored pill badge anywhere in this project.
- Layout: on the Dashboard screen, cards may overlap/stagger slightly for
  visual depth (the one screen where that's appropriate). On list/data
  screens (invoices, members, search results), use a strict aligned grid —
  no overlapping, no staggering; clarity over personality.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  the Primary Accent color #1E6FD9. This is a placeholder — it can be
  swapped later via a short, targeted Edit prompt without affecting other
  screens.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: mobile portrait 375x812px unless noted otherwise.

CONTEXT: The "Messages" tab — a unified inbox holding three kinds of
conversation: (1) a direct 1:1 chat with a Landlord (before any lease
exists, tied to the Landlord rather than to a specific room), (2) a group
Property Chat per room (exists only once a lease becomes Active, includes
every room member; automatically becomes read-only once the lease ends —
do not remove history, just disable the message input and show a small
"This conversation is archived" note), and (3) a Roommate Match chat
(peer-to-peer, created after a successful match). This entire tab requires
login.

SCREENS TO GENERATE:

18. Inbox
- A vertically scrolling list of threads. Each item shows exactly: avatar,
  name (Landlord name / Room name / Matched person's name), last message
  preview, timestamp, an unread-count badge if applicable, and one small
  plain single-color type icon in the corner (a house icon for "Landlord
  chat", a group icon for "Property Chat", a two-people icon for "Match")
  — NOT a colored pill. Sorted by most recent message.
- Comes from: tapping the "Messages" tab, or a new thread appearing after
  tapping "Contact Landlord" on "11", or after a match on "17".
- Goes to: a Landlord-type thread → "19. Landlord Direct Chat". A room
  Property Chat thread → "20. Property Group Chat (Room)". A building-wide
  chat thread → "21. Property Group Chat (Building)". A Match thread →
  "22. Roommate Match Chat".

19. Landlord Direct Chat
- Standard chat UI: message bubbles (mine on the right in light-accent
  color, the other person's on the left in white with a 1px border), a
  text input + attach-photo icon at the bottom. Header: avatar + landlord
  name + the room/address being discussed (small text under the name).
- Comes from: "18" (tapping a thread), or directly from "Contact Landlord"
  on "11. Room Detail".
- Goes to: back arrow → "18".

20. Property Group Chat (Room)
- Group chat UI: message bubbles show the sender's name above them
  (multiple members); supports a special "card" message type (e.g. "New
  invoice") shown as a bordered info block, NOT a normal chat bubble. The
  input supports @mentioning members. IF the lease has ended: show a small
  "This conversation is archived" note at the top and disable the message
  input (existing messages remain visible).
- Comes from: "18", or a deep link from "24. My Room Hub" (Prompt T5).
- Goes to: back arrow → "18" (or back to "24" if entered from there).

21. Property Group Chat (Building)
- Same as "20" but scoped to the whole building (multiple rooms). Supports
  only text/photo/file + mentions — no invoice cards here, and no archive
  state (this chat doesn't end with any one lease).
- Comes from: "18".
- Goes to: back arrow → "18".

22. Roommate Match Chat
- Standard 1:1 chat UI (like "19") but with header context text "Matched
  via Roommate Match on [date]" instead of a room address.
- Comes from: "18", or automatically opened from "Message now" on "17".
- Goes to: back arrow → "18".
```

---

## Prompt T5/7 — My Room Hub (7 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real aligned lists/tables, not everything stuffed into its own floating
rounded card. Numbers look like real data (specific, slightly irregular
values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type size/weight
and spacing, not from wrapping things in boxes or decorative labels. Icons
are small and functional, never decorative illustrations. This is a
FULL-COLOR request (not a grayscale wireframe).

STRICT CONTENT RULE (critical — read carefully): Generate EXACTLY the
elements listed in the "SCREENS TO GENERATE" section below for each screen
— nothing more. Do NOT invent additional badges, banners, taglines,
security/trust claims, status indicators, decorative icons, marketing
copy, or "polish" elements that are not explicitly listed. If a screen's
spec lists 5 elements, the screen should have exactly those 5 elements.
When in doubt, generate LESS rather than more. This rule exists because
past generations invented things like a fake "256-bit encrypted" security
badge, a fabricated "Ready" status indicator, an invented "AUTH" category
label, and a made-up "Bank-grade identity screening" claim — NONE of that
is acceptable. Every single piece of text or UI element on a screen must
trace back to an explicit line in the spec below.

EXPLICITLY BANNED:
- No all-caps text anywhere
- No middle-dot (·), slash (//), or decorative em-dash chrome in headings or labels
- No code-style naming visible in the UI (no "SCREEN_01", no "SPEC_X")
- No monospace font anywhere — use exactly one typeface: Inter
- No gratuitous drop shadows on every card — shadows only where specified below
- No wrapping every section/block in an identical bordered card — use plain
  whitespace as the default separator; only add a border or shadow when a
  rule below calls for it
- No suspiciously round/fake demo numbers — use specific, slightly irregular numbers
- No decorative illustration or gradient hero blocks with no real function
- No filled/colored pill-shaped badges anywhere — use the mandatory
  dot-indicator / outlined-tag system below instead
- No internal/dev category labels or chips (e.g. "AUTH", "SCREEN_X",
  section tags) rendered as visible UI elements — these are for our own
  organizational reference only and must never appear to a real user
- No fabricated status, security, or trust indicators anywhere (e.g.
  "256-bit encrypted", "Ready", "Bank-grade identity screening", "Verified
  by [made-up brand]") — every piece of text/badge on a screen must come
  directly from this spec; do not invent extra system-status or trust
  signals to make a screen look more polished

DESIGN TOKENS (use exactly these values):
- Background: #F8FBFE (very light pastel blue tint, near-white — not pure
  white, not warm cream)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active nav tab icon. Do NOT apply it to every button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — do not soften to orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data (amounts, meter
  readings) uses Inter's tabular figures.
- Shape & elevation (CONTEXTUAL, not one fixed value everywhere):
  - Hero/highlight card (the one standout element per screen): 24px corner
    radius + a soft shadow tinted toward the background blue,
    rgba(30,111,217,0.10)
  - Regular list/content cards: 14px corner radius, flat, NO shadow — 1px
    solid border (#D7E3F2) only
  - Buttons: 12px corner radius
- Badges & tags (MANDATORY on every screen with any status or descriptive label):
  - Live status (room availability, verification, payment/invoice status,
    issue status): a small 7px filled dot in the semantic color, followed
    by plain navy text — NO colored background fill, NO pill container.
  - Descriptive constraint tag (fixed attributes like "Female Only", "Max 3
    People", "No Pets"): a rectangular tag, 7px corner radius, 1px solid
    border (#D7E3F2), NO background fill, plain navy text — same outlined
    style regardless of whether the attribute reads positive or negative.
  - NEVER use a filled/colored pill badge anywhere in this project.
- Layout: on the Dashboard screen, cards may overlap/stagger slightly for
  visual depth (the one screen where that's appropriate). On list/data
  screens (invoices, members, search results), use a strict aligned grid —
  no overlapping, no staggering; clarity over personality.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  the Primary Accent color #1E6FD9. This is a placeholder — it can be
  swapped later via a short, targeted Edit prompt without affecting other
  screens.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: mobile portrait 375x812px unless noted otherwise.

CONTEXT: The "My Room" tab — where a Tenant manages their current (or
past) lease. If the Tenant has EXACTLY ONE lease (active or ended), tapping
this tab goes STRAIGHT into the Hub ("24"), skipping the list screen
("23"). The list only appears when there are 2+ leases.

SCREENS TO GENERATE:

23. Lease List
- Exactly two tabs: "Active" / "Ended". Each item shows a room photo,
  address, lease term, and a status dot-indicator badge.
- Comes from: tapping the "My Room" tab — ONLY when there are 2+ leases.
- Goes to: tapping an item → "24. My Room Hub".

24. My Room Hub
- Header: photo + address + lease status. Below, a menu-style list (icon +
  label + right-chevron per row).
  - IF the lease is ACTIVE: exactly these rows — "View Lease", "Members",
    "Invoices", "Issues", "Chat".
  - IF the lease has ENDED: the same rows but each labeled "(History)",
    with NO payment button reachable through Invoices, NO way to file a
    new Issue, and Chat leads to the archived/read-only state described in
    "20".
- Comes from: "23" (if 2+ leases), or directly from the "My Room" tab (if
  exactly one lease).
- Goes to: "View Lease" → "25". "Members" → "26". "Invoices" → "27".
  "Issues" → "30" (Prompt T6). "Chat" → deep-links to "20" or "21" (Prompt
  T4) — the Hub is only a shortcut, it doesn't own a chat screen.

25. View Lease
- Read-only, exactly: rent amount, deposit amount, start/end dates, lease
  terms text, and the signed lease file/photo (or a note "Awaiting the
  Landlord to upload the signed file" if not yet available). No editing or
  signing controls of any kind.
- Comes from: "24".
- Goes to: back → "24".

26. Member List
- Read-only. Each item shows ONLY an avatar + full name — no phone number,
  no vehicle info, no other details of other members. No add/remove
  controls (Tenants cannot manage members).
- Comes from: "24".
- Goes to: back → "24".

27. Invoice List
- A list by month. Each item shows: month/year, total amount, and a status
  dot-indicator (Unpaid = gray, Overdue = red, Paid = green, Partial =
  gray with extra text "50% paid").
- Comes from: "24".
- Goes to: tapping an item → "28. Invoice Detail".

28. Invoice Detail
- An aligned breakdown list (not separate cards per line): "Room rent",
  "Electricity", "Water", "Other services (wifi/trash/laundry)" — each row
  with the amount right-aligned. Total at the bottom (bold, larger).
  Payment status text, and "Paid: X / Remaining: Y" if partially paid. A
  large "Pay" button fixed at the bottom (hidden if fully paid, or if this
  is an ended lease).
- Comes from: "27".
- Goes to: back → "27". "Pay" → "29. Payment".

29. Payment
- Exactly three channel options, shown as tabs or segmented buttons:
  "VietQR" (a dynamic QR code + the exact amount), "Cash" (text
  instructions: "Please pay the Landlord directly, then wait for
  confirmation"), and "E-wallet (VNPay/MoMo)" (placeholder logos for VNPay
  and MoMo + a short instruction "Redirects to your wallet app"). Any
  member of the room can see and use this screen.
- Comes from: "28" (Pay button).
- Goes to: after confirming → returns to "28" with the updated status.
```

---

## Prompt T6/7 — Issues (3 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real aligned lists/tables, not everything stuffed into its own floating
rounded card. Numbers look like real data (specific, slightly irregular
values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type size/weight
and spacing, not from wrapping things in boxes or decorative labels. Icons
are small and functional, never decorative illustrations. This is a
FULL-COLOR request (not a grayscale wireframe).

STRICT CONTENT RULE (critical — read carefully): Generate EXACTLY the
elements listed in the "SCREENS TO GENERATE" section below for each screen
— nothing more. Do NOT invent additional badges, banners, taglines,
security/trust claims, status indicators, decorative icons, marketing
copy, or "polish" elements that are not explicitly listed. If a screen's
spec lists 5 elements, the screen should have exactly those 5 elements.
When in doubt, generate LESS rather than more. This rule exists because
past generations invented things like a fake "256-bit encrypted" security
badge, a fabricated "Ready" status indicator, an invented "AUTH" category
label, and a made-up "Bank-grade identity screening" claim — NONE of that
is acceptable. Every single piece of text or UI element on a screen must
trace back to an explicit line in the spec below.

EXPLICITLY BANNED:
- No all-caps text anywhere
- No middle-dot (·), slash (//), or decorative em-dash chrome in headings or labels
- No code-style naming visible in the UI (no "SCREEN_01", no "SPEC_X")
- No monospace font anywhere — use exactly one typeface: Inter
- No gratuitous drop shadows on every card — shadows only where specified below
- No wrapping every section/block in an identical bordered card — use plain
  whitespace as the default separator; only add a border or shadow when a
  rule below calls for it
- No suspiciously round/fake demo numbers — use specific, slightly irregular numbers
- No decorative illustration or gradient hero blocks with no real function
- No filled/colored pill-shaped badges anywhere — use the mandatory
  dot-indicator / outlined-tag system below instead
- No internal/dev category labels or chips (e.g. "AUTH", "SCREEN_X",
  section tags) rendered as visible UI elements — these are for our own
  organizational reference only and must never appear to a real user
- No fabricated status, security, or trust indicators anywhere (e.g.
  "256-bit encrypted", "Ready", "Bank-grade identity screening", "Verified
  by [made-up brand]") — every piece of text/badge on a screen must come
  directly from this spec; do not invent extra system-status or trust
  signals to make a screen look more polished

DESIGN TOKENS (use exactly these values):
- Background: #F8FBFE (very light pastel blue tint, near-white — not pure
  white, not warm cream)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active nav tab icon. Do NOT apply it to every button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — do not soften to orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data (amounts, meter
  readings) uses Inter's tabular figures.
- Shape & elevation (CONTEXTUAL, not one fixed value everywhere):
  - Hero/highlight card (the one standout element per screen): 24px corner
    radius + a soft shadow tinted toward the background blue,
    rgba(30,111,217,0.10)
  - Regular list/content cards: 14px corner radius, flat, NO shadow — 1px
    solid border (#D7E3F2) only
  - Buttons: 12px corner radius
- Badges & tags (MANDATORY on every screen with any status or descriptive label):
  - Live status (room availability, verification, payment/invoice status,
    issue status): a small 7px filled dot in the semantic color, followed
    by plain navy text — NO colored background fill, NO pill container.
  - Descriptive constraint tag (fixed attributes like "Female Only", "Max 3
    People", "No Pets"): a rectangular tag, 7px corner radius, 1px solid
    border (#D7E3F2), NO background fill, plain navy text — same outlined
    style regardless of whether the attribute reads positive or negative.
  - NEVER use a filled/colored pill badge anywhere in this project.
- Layout: on the Dashboard screen, cards may overlap/stagger slightly for
  visual depth (the one screen where that's appropriate). On list/data
  screens (invoices, members, search results), use a strict aligned grid —
  no overlapping, no staggering; clarity over personality.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  the Primary Accent color #1E6FD9. This is a placeholder — it can be
  swapped later via a short, targeted Edit prompt without affecting other
  screens.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: mobile portrait 375x812px unless noted otherwise.

CONTEXT: These screens live INSIDE "24. My Room Hub", NOT as a separate
top-level tab. They only show issues belonging to the specific room/lease
whose Hub is currently open.

SCREENS TO GENERATE:

30. Room Issue List
- A list of reported issues, each item: a short one-line description, the
  report date, and a status dot-indicator (Open = gray, In Progress =
  accent blue, Resolved = green). A floating "+ Report an issue" button in
  the bottom-right corner (shown ONLY if the lease is Active).
- Comes from: the "Issues" item on "24".
- Goes to: tapping an item → opens "31. Issue Detail Popup" (a bottom
  sheet, NOT a separate page). Tapping "+ Report an issue" → "32. Report an
  Issue".

31. Issue Detail Popup
- A bottom sheet (~70% of screen height) over "30" (background dimmed
  behind it). Contains exactly: the full description + attached photos, a
  horizontal status stepper (Open → In Progress → Resolved, current step
  highlighted), and below it a built-in discussion thread (a short message
  list + a reply input at the bottom of the sheet).
- Comes from: tapping an item on "30".
- Goes to: swipe down / close (X) → closes, returns to "30".

32. Report an Issue
- Exactly: a description textarea, and a photo-attachment area offering
  BOTH "Take a photo" AND "Choose from library" (not restricted to camera-
  only). A "Submit report" button fixed at the bottom.
- Comes from: "+ Report an issue" on "30".
- Goes to: "Submit report" → returns to "30", the new item appears at the
  top, status "Open".
```

---

## Prompt T7/7 — Account (2 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real aligned lists/tables, not everything stuffed into its own floating
rounded card. Numbers look like real data (specific, slightly irregular
values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type size/weight
and spacing, not from wrapping things in boxes or decorative labels. Icons
are small and functional, never decorative illustrations. This is a
FULL-COLOR request (not a grayscale wireframe).

STRICT CONTENT RULE (critical — read carefully): Generate EXACTLY the
elements listed in the "SCREENS TO GENERATE" section below for each screen
— nothing more. Do NOT invent additional badges, banners, taglines,
security/trust claims, status indicators, decorative icons, marketing
copy, or "polish" elements that are not explicitly listed. If a screen's
spec lists 5 elements, the screen should have exactly those 5 elements.
When in doubt, generate LESS rather than more. This rule exists because
past generations invented things like a fake "256-bit encrypted" security
badge, a fabricated "Ready" status indicator, an invented "AUTH" category
label, and a made-up "Bank-grade identity screening" claim — NONE of that
is acceptable. Every single piece of text or UI element on a screen must
trace back to an explicit line in the spec below.

EXPLICITLY BANNED:
- No all-caps text anywhere
- No middle-dot (·), slash (//), or decorative em-dash chrome in headings or labels
- No code-style naming visible in the UI (no "SCREEN_01", no "SPEC_X")
- No monospace font anywhere — use exactly one typeface: Inter
- No gratuitous drop shadows on every card — shadows only where specified below
- No wrapping every section/block in an identical bordered card — use plain
  whitespace as the default separator; only add a border or shadow when a
  rule below calls for it
- No suspiciously round/fake demo numbers — use specific, slightly irregular numbers
- No decorative illustration or gradient hero blocks with no real function
- No filled/colored pill-shaped badges anywhere — use the mandatory
  dot-indicator / outlined-tag system below instead
- No internal/dev category labels or chips (e.g. "AUTH", "SCREEN_X",
  section tags) rendered as visible UI elements — these are for our own
  organizational reference only and must never appear to a real user
- No fabricated status, security, or trust indicators anywhere (e.g.
  "256-bit encrypted", "Ready", "Bank-grade identity screening", "Verified
  by [made-up brand]") — every piece of text/badge on a screen must come
  directly from this spec; do not invent extra system-status or trust
  signals to make a screen look more polished

DESIGN TOKENS (use exactly these values):
- Background: #F8FBFE (very light pastel blue tint, near-white — not pure
  white, not warm cream)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active nav tab icon. Do NOT apply it to every button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — do not soften to orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data (amounts, meter
  readings) uses Inter's tabular figures.
- Shape & elevation (CONTEXTUAL, not one fixed value everywhere):
  - Hero/highlight card (the one standout element per screen): 24px corner
    radius + a soft shadow tinted toward the background blue,
    rgba(30,111,217,0.10)
  - Regular list/content cards: 14px corner radius, flat, NO shadow — 1px
    solid border (#D7E3F2) only
  - Buttons: 12px corner radius
- Badges & tags (MANDATORY on every screen with any status or descriptive label):
  - Live status (room availability, verification, payment/invoice status,
    issue status): a small 7px filled dot in the semantic color, followed
    by plain navy text — NO colored background fill, NO pill container.
  - Descriptive constraint tag (fixed attributes like "Female Only", "Max 3
    People", "No Pets"): a rectangular tag, 7px corner radius, 1px solid
    border (#D7E3F2), NO background fill, plain navy text — same outlined
    style regardless of whether the attribute reads positive or negative.
  - NEVER use a filled/colored pill badge anywhere in this project.
- Layout: on the Dashboard screen, cards may overlap/stagger slightly for
  visual depth (the one screen where that's appropriate). On list/data
  screens (invoices, members, search results), use a strict aligned grid —
  no overlapping, no staggering; clarity over personality.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  the Primary Accent color #1E6FD9. This is a placeholder — it can be
  swapped later via a short, targeted Edit prompt without affecting other
  screens.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: mobile portrait 375x812px unless noted otherwise.

CONTEXT: The "Account" tab — the last tab on the bottom navigation.

SCREENS TO GENERATE:

33. Profile
- Exactly: a large avatar (editable) + name (editable). Two clearly READ-
  ONLY fields below (light gray background, small lock icon): Phone
  number, Email — with a small caption "Cannot be changed, it's tied to
  your lease." A menu list below: "Change password", "Saved Rooms"
  (shortcut to "12"), "Notification Settings", and "Log out" (red text).
- Comes from: tapping the "Account" tab from anywhere.
- Goes to: "Change password" → opens a flow like "3/4". "Saved Rooms" →
  "12". "Notification Settings" → "34". "Log out" → "7. Logout
  Confirmation".

34. Notification Settings
- Exactly one single large toggle switch: "Enable notifications" — NOT
  broken down by notification type.
- Comes from: "33".
- Goes to: back → "33".
```

---
---

# ZONE B — "Rentify Landlord — Mobile App" (55 screens, 11 prompts)

> Open a **SECOND, SEPARATE** Stitch project named exactly **"Rentify
> Landlord — Mobile App"**. This app serves ONLY landlords — there is no
> tenant content, no room-browsing/roommate-matching feed, anywhere in this
> project. Paste the same 🎨 DESIGN SYSTEM block from the very top of this
> file at the start of every prompt below too. Bottom navigation (5 tabs,
> shown once logged in): **Dashboard · Manage Properties · Issues · Chat ·
> Settings**.

## Prompt L1/11 — Auth (8 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real aligned lists/tables, not everything stuffed into its own floating
rounded card. Numbers look like real data (specific, slightly irregular
values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type size/weight
and spacing, not from wrapping things in boxes or decorative labels. Icons
are small and functional, never decorative illustrations. This is a
FULL-COLOR request (not a grayscale wireframe).

STRICT CONTENT RULE (critical — read carefully): Generate EXACTLY the
elements listed in the "SCREENS TO GENERATE" section below for each screen
— nothing more. Do NOT invent additional badges, banners, taglines,
security/trust claims, status indicators, decorative icons, marketing
copy, or "polish" elements that are not explicitly listed. If a screen's
spec lists 5 elements, the screen should have exactly those 5 elements.
When in doubt, generate LESS rather than more. This rule exists because
past generations invented things like a fake "256-bit encrypted" security
badge, a fabricated "Ready" status indicator, an invented "AUTH" category
label, and a made-up "Bank-grade identity screening" claim — NONE of that
is acceptable. Every single piece of text or UI element on a screen must
trace back to an explicit line in the spec below.

EXPLICITLY BANNED:
- No all-caps text anywhere
- No middle-dot (·), slash (//), or decorative em-dash chrome in headings or labels
- No code-style naming visible in the UI (no "SCREEN_01", no "SPEC_X")
- No monospace font anywhere — use exactly one typeface: Inter
- No gratuitous drop shadows on every card — shadows only where specified below
- No wrapping every section/block in an identical bordered card — use plain
  whitespace as the default separator; only add a border or shadow when a
  rule below calls for it
- No suspiciously round/fake demo numbers — use specific, slightly irregular numbers
- No decorative illustration or gradient hero blocks with no real function
- No filled/colored pill-shaped badges anywhere — use the mandatory
  dot-indicator / outlined-tag system below instead
- No internal/dev category labels or chips (e.g. "AUTH", "SCREEN_X",
  section tags) rendered as visible UI elements — these are for our own
  organizational reference only and must never appear to a real user
- No fabricated status, security, or trust indicators anywhere (e.g.
  "256-bit encrypted", "Ready", "Bank-grade identity screening", "Verified
  by [made-up brand]") — every piece of text/badge on a screen must come
  directly from this spec; do not invent extra system-status or trust
  signals to make a screen look more polished

DESIGN TOKENS (use exactly these values):
- Background: #F8FBFE (very light pastel blue tint, near-white — not pure
  white, not warm cream)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active nav tab icon. Do NOT apply it to every button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — do not soften to orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data (amounts, meter
  readings) uses Inter's tabular figures.
- Shape & elevation (CONTEXTUAL, not one fixed value everywhere):
  - Hero/highlight card (the one standout element per screen): 24px corner
    radius + a soft shadow tinted toward the background blue,
    rgba(30,111,217,0.10)
  - Regular list/content cards: 14px corner radius, flat, NO shadow — 1px
    solid border (#D7E3F2) only
  - Buttons: 12px corner radius
- Badges & tags (MANDATORY on every screen with any status or descriptive label):
  - Live status (room availability, verification, payment/invoice status,
    issue status): a small 7px filled dot in the semantic color, followed
    by plain navy text — NO colored background fill, NO pill container.
  - Descriptive constraint tag (fixed attributes like "Female Only", "Max 3
    People", "No Pets"): a rectangular tag, 7px corner radius, 1px solid
    border (#D7E3F2), NO background fill, plain navy text — same outlined
    style regardless of whether the attribute reads positive or negative.
  - NEVER use a filled/colored pill badge anywhere in this project.
- Layout: on the Dashboard screen, cards may overlap/stagger slightly for
  visual depth (the one screen where that's appropriate). On list/data
  screens (invoices, members, search results), use a strict aligned grid —
  no overlapping, no staggering; clarity over personality.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  the Primary Accent color #1E6FD9. This is a placeholder — it can be
  swapped later via a short, targeted Edit prompt without affecting other
  screens.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: mobile portrait 375x812px unless noted otherwise.

CONTEXT: The authentication flow for the Landlord app. There is no role
selection anywhere — this app is exclusively for Landlords. Generate the
following 8 screens, named EXACTLY as numbered below.

SCREENS TO GENERATE:

1. Splash
- ONLY a centered Rentify logo (placeholder) on the #F8FBFE background.
  Nothing else on screen.
- Comes from: app launch.
- Goes to: auto-advances after ~1-2s. Valid token → "9a/9b. Dashboard". No
  token → "2. Login".

2. Login
- Exactly: Email input, Password input (eye icon), full-width "Log in"
  button, "Forgot password?" link, "Don't have an account? Sign up" line.
  Inline error state: red outline + "Incorrect email or password" text.
- Comes from: "1. Splash", any gated action (bottom sheet), or "7. Logout
  Confirmation".
- Goes to: correct login, account normal → "9a/9b. Dashboard" (Prompt L2).
  Correct login, account locked → "6. Account Locked". "Forgot password?"
  → "3". "Sign up" → "5".

3. Forgot Password — Enter Email
- Exactly: title "Forgot your password?", one description line, Email
  input, "Send reset link" button; on send, same screen shows a success
  state (green checkmark + "Sent! Check your inbox").
- Comes from: "2" (Forgot password link).
- Goes to: "Back to Login" → "2".

4. Reset Password
- Exactly: title "Set a new password", New Password + Confirm Password
  inputs, "Reset password" button.
- Comes from: the email link (simulated from "3").
- Goes to: success → "2" with a success banner.

5. Sign Up
- Exactly: Email, Password, Confirm Password (eye icons), Full name, Phone
  number inputs, "Sign up" button, "Already have an account? Log in" line.
  Inline validation: mismatched passwords → red outline + "Passwords
  don't match" text.
- Comes from: "2" (sign-up link), or any gated action.
- Goes to: successful sign-up → "9a. Dashboard — Empty State" (Prompt L2),
  since a brand-new Landlord has no buildings yet.

6. Account Locked
- Exactly: a large lock icon, title "Your account is locked", description
  "All your properties have been hidden from public search. Please contact
  support for more details.", two buttons "Contact support" (outline) and
  "Log out" (red text). No other way out of this screen.
- Comes from: "2" when the account is detected as locked.
- Goes to: "Log out" → "7. Logout Confirmation".

7. Logout Confirmation
- Exactly: dialog text "Are you sure you want to log out?", buttons "Log
  out" (red) / "Cancel".
- Comes from: "Log out" on "51. Profile" (Prompt L11), or "6".
- Goes to: confirm → "2". Cancel → closes, no navigation.

8. Generic Error
- Exactly: a simple icon, an error-type title, one description line, "Try
  again" button.
- Comes from: any screen on API failure.
- Goes to: "Try again" → returns to the failed action.
```

---

## Prompt L2/11 — Dashboard (1 screen, 2 variants)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real aligned lists/tables, not everything stuffed into its own floating
rounded card. Numbers look like real data (specific, slightly irregular
values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type size/weight
and spacing, not from wrapping things in boxes or decorative labels. Icons
are small and functional, never decorative illustrations. This is a
FULL-COLOR request (not a grayscale wireframe).

STRICT CONTENT RULE (critical — read carefully): Generate EXACTLY the
elements listed in the "SCREENS TO GENERATE" section below for each screen
— nothing more. Do NOT invent additional badges, banners, taglines,
security/trust claims, status indicators, decorative icons, marketing
copy, or "polish" elements that are not explicitly listed. If a screen's
spec lists 5 elements, the screen should have exactly those 5 elements.
When in doubt, generate LESS rather than more. This rule exists because
past generations invented things like a fake "256-bit encrypted" security
badge, a fabricated "Ready" status indicator, an invented "AUTH" category
label, and a made-up "Bank-grade identity screening" claim — NONE of that
is acceptable. Every single piece of text or UI element on a screen must
trace back to an explicit line in the spec below.

EXPLICITLY BANNED:
- No all-caps text anywhere
- No middle-dot (·), slash (//), or decorative em-dash chrome in headings or labels
- No code-style naming visible in the UI (no "SCREEN_01", no "SPEC_X")
- No monospace font anywhere — use exactly one typeface: Inter
- No gratuitous drop shadows on every card — shadows only where specified below
- No wrapping every section/block in an identical bordered card — use plain
  whitespace as the default separator; only add a border or shadow when a
  rule below calls for it
- No suspiciously round/fake demo numbers — use specific, slightly irregular numbers
- No decorative illustration or gradient hero blocks with no real function
- No filled/colored pill-shaped badges anywhere — use the mandatory
  dot-indicator / outlined-tag system below instead
- No internal/dev category labels or chips (e.g. "AUTH", "SCREEN_X",
  section tags) rendered as visible UI elements — these are for our own
  organizational reference only and must never appear to a real user
- No fabricated status, security, or trust indicators anywhere (e.g.
  "256-bit encrypted", "Ready", "Bank-grade identity screening", "Verified
  by [made-up brand]") — every piece of text/badge on a screen must come
  directly from this spec; do not invent extra system-status or trust
  signals to make a screen look more polished

DESIGN TOKENS (use exactly these values):
- Background: #F8FBFE (very light pastel blue tint, near-white — not pure
  white, not warm cream)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active nav tab icon. Do NOT apply it to every button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — do not soften to orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data (amounts, meter
  readings) uses Inter's tabular figures.
- Shape & elevation (CONTEXTUAL, not one fixed value everywhere):
  - Hero/highlight card (the one standout element per screen): 24px corner
    radius + a soft shadow tinted toward the background blue,
    rgba(30,111,217,0.10)
  - Regular list/content cards: 14px corner radius, flat, NO shadow — 1px
    solid border (#D7E3F2) only
  - Buttons: 12px corner radius
- Badges & tags (MANDATORY on every screen with any status or descriptive label):
  - Live status (room availability, verification, payment/invoice status,
    issue status): a small 7px filled dot in the semantic color, followed
    by plain navy text — NO colored background fill, NO pill container.
  - Descriptive constraint tag (fixed attributes like "Female Only", "Max 3
    People", "No Pets"): a rectangular tag, 7px corner radius, 1px solid
    border (#D7E3F2), NO background fill, plain navy text — same outlined
    style regardless of whether the attribute reads positive or negative.
  - NEVER use a filled/colored pill badge anywhere in this project.
- Layout: on the Dashboard screen, cards may overlap/stagger slightly for
  visual depth (the one screen where that's appropriate). On list/data
  screens (invoices, members, search results), use a strict aligned grid —
  no overlapping, no staggering; clarity over personality.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  the Primary Accent color #1E6FD9. This is a placeholder — it can be
  swapped later via a short, targeted Edit prompt without affecting other
  screens.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: mobile portrait 375x812px unless noted otherwise.

CONTEXT: The "Dashboard" tab — the default tab after login. Generate BOTH
variants.

SCREENS TO GENERATE:

9a. Dashboard — Empty State
- Exactly: a hero card (24px radius + soft blue shadow) centered on
  screen, containing a welcome icon, title "Welcome to Rentify!",
  description "Start by adding your first Building/Property", and a large
  "+ Add Building" button. Below it, the Revenue/Debt/Room Map sections
  still visible but dimmed ("no data yet" style).
- Comes from: first login/sign-up, no Building yet.
- Goes to: "+ Add Building" → "10. Building List" (empty, Prompt L3) then
  straight into "11. Add Building — Step 1/3".

9b. Dashboard — Full State
- Exactly: one hero card (24px + blue shadow) combining 3 stats: "Monthly
  Revenue — $4,317", "Outstanding Debt — $612", "Occupancy Rate — 87%".
  Below it, a bar chart of monthly revenue (Accent-colored bars, realistic
  varying heights, no card wrapper needed). Below that, a "Room Map" — a
  visual grid, each cell = one room, color-coded by status (light green =
  vacant, Accent = occupied, gray = pending cleanup), with a small color
  legend underneath. Cards on this screen specifically may overlap/stagger
  slightly for depth (the only screen where this is allowed).
- Comes from: login with ≥1 approved building.
- Goes to: tapping a Room Map cell → "18. Room Detail" (Prompt L3).
  Tapping "Outstanding Debt" → "40. Debt List" (Prompt L7).
```

---

## Prompt L3/11 — Buildings & Rooms (13 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real aligned lists/tables, not everything stuffed into its own floating
rounded card. Numbers look like real data (specific, slightly irregular
values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type size/weight
and spacing, not from wrapping things in boxes or decorative labels. Icons
are small and functional, never decorative illustrations. This is a
FULL-COLOR request (not a grayscale wireframe).

STRICT CONTENT RULE (critical — read carefully): Generate EXACTLY the
elements listed in the "SCREENS TO GENERATE" section below for each screen
— nothing more. Do NOT invent additional badges, banners, taglines,
security/trust claims, status indicators, decorative icons, marketing
copy, or "polish" elements that are not explicitly listed. If a screen's
spec lists 5 elements, the screen should have exactly those 5 elements.
When in doubt, generate LESS rather than more. This rule exists because
past generations invented things like a fake "256-bit encrypted" security
badge, a fabricated "Ready" status indicator, an invented "AUTH" category
label, and a made-up "Bank-grade identity screening" claim — NONE of that
is acceptable. Every single piece of text or UI element on a screen must
trace back to an explicit line in the spec below.

EXPLICITLY BANNED:
- No all-caps text anywhere
- No middle-dot (·), slash (//), or decorative em-dash chrome in headings or labels
- No code-style naming visible in the UI (no "SCREEN_01", no "SPEC_X")
- No monospace font anywhere — use exactly one typeface: Inter
- No gratuitous drop shadows on every card — shadows only where specified below
- No wrapping every section/block in an identical bordered card — use plain
  whitespace as the default separator; only add a border or shadow when a
  rule below calls for it
- No suspiciously round/fake demo numbers — use specific, slightly irregular numbers
- No decorative illustration or gradient hero blocks with no real function
- No filled/colored pill-shaped badges anywhere — use the mandatory
  dot-indicator / outlined-tag system below instead
- No internal/dev category labels or chips (e.g. "AUTH", "SCREEN_X",
  section tags) rendered as visible UI elements — these are for our own
  organizational reference only and must never appear to a real user
- No fabricated status, security, or trust indicators anywhere (e.g.
  "256-bit encrypted", "Ready", "Bank-grade identity screening", "Verified
  by [made-up brand]") — every piece of text/badge on a screen must come
  directly from this spec; do not invent extra system-status or trust
  signals to make a screen look more polished

DESIGN TOKENS (use exactly these values):
- Background: #F8FBFE (very light pastel blue tint, near-white — not pure
  white, not warm cream)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active nav tab icon. Do NOT apply it to every button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — do not soften to orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data (amounts, meter
  readings) uses Inter's tabular figures.
- Shape & elevation (CONTEXTUAL, not one fixed value everywhere):
  - Hero/highlight card (the one standout element per screen): 24px corner
    radius + a soft shadow tinted toward the background blue,
    rgba(30,111,217,0.10)
  - Regular list/content cards: 14px corner radius, flat, NO shadow — 1px
    solid border (#D7E3F2) only
  - Buttons: 12px corner radius
- Badges & tags (MANDATORY on every screen with any status or descriptive label):
  - Live status (room availability, verification, payment/invoice status,
    issue status): a small 7px filled dot in the semantic color, followed
    by plain navy text — NO colored background fill, NO pill container.
  - Descriptive constraint tag (fixed attributes like "Female Only", "Max 3
    People", "No Pets"): a rectangular tag, 7px corner radius, 1px solid
    border (#D7E3F2), NO background fill, plain navy text — same outlined
    style regardless of whether the attribute reads positive or negative.
  - NEVER use a filled/colored pill badge anywhere in this project.
- Layout: on the Dashboard screen, cards may overlap/stagger slightly for
  visual depth (the one screen where that's appropriate). On list/data
  screens (invoices, members, search results), use a strict aligned grid —
  no overlapping, no staggering; clarity over personality.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  the Primary Accent color #1E6FD9. This is a placeholder — it can be
  swapped later via a short, targeted Edit prompt without affecting other
  screens.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: mobile portrait 375x812px unless noted otherwise.

CONTEXT: The "Manage Properties" tab. Creating a new Building follows a
multi-step wizard, each step its own screen (do NOT merge into one long
form). The utility-rate step is a two-tier choice: first pick a rate TYPE,
then fill in the specific config for that type.

SCREENS TO GENERATE:

10. Building List
- Exactly: a card list, each card showing name, address, an approval-
  status dot-indicator (gray "Pending review", green "Approved", red
  "Rejected"), and vacant/occupied room counts. A floating "+ Add Building"
  button bottom-right.
- Comes from: the "Manage Properties" tab, or "9a" (CTA, skips straight to
  "11" the first time).
- Goes to: "+ Add Building" → "11". Tapping a card → "14. Building Detail".

11. Add Building — Step 1/3
- Exactly: a 3-step progress indicator (step 1 active), Name/Address/
  Number-of-floors inputs, "Continue" button.
- Comes from: "10" or "9a".
- Goes to: "Continue" → "12".

12. Upload Ownership Documents — Step 2/3
- Exactly: step 2 active, an upload area with "Take photo" + "Choose from
  library" buttons, supporting MULTIPLE images (thumbnail grid, each
  removable), caption "Land-use certificate / property deed or a legal
  authorization letter — required for Admin approval."
- Comes from: "11".
- Goes to: "Continue" → "13".

13. Choose Utility Rate Type — Step 3/3
- Exactly: step 3 active, three selectable cards with short descriptions —
  "Fixed rate" (flat price per kWh/cubic meter, the simplest option), "EVN
  tiered" (price increases across consumption tiers, like Vietnam's
  national grid pricing), "Per-person flat fee" (flat monthly charge per
  occupant, not tied to meter readings). "Continue" button.
- Comes from: "12", or "14. Building Detail" ("Edit Utility Rates" menu
  item, when revisiting later).
- Goes to: "Fixed rate" → "13a". "EVN tiered" → "13b". "Per-person flat
  fee" → "13c".

13a. Configure Fixed Rate
- Exactly: electricity-rate input (per kWh), water-rate input (per cubic
  meter or per person), optional wifi/trash/laundry fee inputs, "Finish"
  button.
- Comes from: "13" (Fixed rate option).
- Goes to: "Finish" → if creating a new building, "10" (new building at
  top with "Pending review" badge); if editing an existing one, "14".

13b. Configure EVN Tiered Rate
- Exactly: a dynamic multi-row table — each row "From X to Y kWh" + a
  price; a "+ Add tier" button; a small remove icon per row (min. 1 row).
  Same optional fee inputs below the table. "Finish" button.
- Comes from: "13" (EVN tiered option).
- Goes to: "Finish" → same behavior as "13a".

13c. Configure Per-Person Flat Rate
- Exactly: one input "Utility flat fee per person per month", same
  optional fee inputs below it, "Finish" button.
- Comes from: "13" (Per-person flat fee option).
- Goes to: "Finish" → same behavior as "13a".

14. Building Detail
- Header: name, address, a large status badge. IF "Pending review": a
  light yellow banner "Awaiting Admin approval, rooms cannot be added
  yet." IF "Rejected": a light red banner with the specific reason + a
  "Resubmit documents" button. IF "Approved": exactly this menu — "Edit
  Utility Rates", "Configure VietQR Payment Account", "View Room List".
- Comes from: "10" (tapping a card).
- Goes to: "Resubmit documents" → "12" (reopened). "Edit Utility Rates" →
  "13" (reopened to change type/values any time). "Configure VietQR" →
  "15". "View Room List" → "16".

15. Configure Building VietQR Account
- Exactly: Bank account number, Bank name, Account holder name inputs,
  caption "Used to auto-generate the VietQR code for every invoice in this
  building's rooms.", "Save" button.
- Comes from: "14" (only if Approved).
- Goes to: "Save" → "14".

16. Room List (Room Map for this Building)
- The same visual Room Map style as "9b" but filtered to just this
  building — a grid by floor, color-coded by status. Exactly two buttons
  in the header: "+ Add Room" and "Bulk Meter Reading" (camera/lightning
  icon).
- Comes from: "14" (View Room List).
- Goes to: tapping a room cell → "18. Room Detail". "+ Add Room" → "17"
  (only enabled if the building is Approved). "Bulk Meter Reading" → "28.
  Bulk Reading Entry" (Prompt L5).

17. Add New Room
- Exactly: Room number, Size, Rent price inputs, optional rules (gender
  dropdown: No preference/Male only/Female only, amenity checkboxes), a
  "Description" textarea, a "Keywords" input (e.g. "near university,
  quiet, has a balcony") with a "✨ Generate description with AI" button
  next to it (show the Description textarea already populated with a
  sample AI-generated Vietnamese description as the default state, to
  demonstrate the feature — it remains editable by hand), "Create room"
  button.
- Comes from: "16" (+ Add Room).
- Goes to: "Create room" → "16", new room cell appears (Vacant color).

18. Room Detail
- Exactly: an overview card (room photo, price, a large status badge). IF
  there's an active lease: a condensed lease summary (lead tenant's name,
  term) + a "Utility Menu" button. IF no lease: a "Create new lease"
  button. Always: a small "+ Report issue" button in the corner, and a
  small collapsed "Advanced" section (collapsed by default) revealing one
  link "Custom utility rate for this room" — tapping it opens the same
  "13. Choose Utility Rate Type" flow, scoped to just this room
  (overriding the building's default).
- Comes from: "16" (tapping a cell), or "9b" (Room Map cell).
- Goes to: "Utility Menu" (if leased) → "19". "Create new lease" (if not)
  → "20. Create Lease" (Prompt L4). "+ Report issue" → "43. Landlord
  Creates an Issue" (Prompt L8). "Advanced" → room-scoped "13".

19. Room Utility Menu
- Exactly this menu list: "Members", "Meter Reading", "Invoices", "Chat",
  "Move-out / Settlement". Shown ONLY when the room has an Active lease.
- Comes from: "18" (Utility Menu button).
- Goes to: "Members" → "24" (Prompt L4). "Meter Reading" → "27" (Prompt
  L5). "Invoices" → "34" (Prompt L6). "Chat" → deep-link "50. Chat Thread
  Detail" (Prompt L10) for this room. "Move-out" → "44" (Prompt L9).
```

---

## Prompt L4/11 — Lease & Members (7 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real aligned lists/tables, not everything stuffed into its own floating
rounded card. Numbers look like real data (specific, slightly irregular
values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type size/weight
and spacing, not from wrapping things in boxes or decorative labels. Icons
are small and functional, never decorative illustrations. This is a
FULL-COLOR request (not a grayscale wireframe).

STRICT CONTENT RULE (critical — read carefully): Generate EXACTLY the
elements listed in the "SCREENS TO GENERATE" section below for each screen
— nothing more. Do NOT invent additional badges, banners, taglines,
security/trust claims, status indicators, decorative icons, marketing
copy, or "polish" elements that are not explicitly listed. If a screen's
spec lists 5 elements, the screen should have exactly those 5 elements.
When in doubt, generate LESS rather than more. This rule exists because
past generations invented things like a fake "256-bit encrypted" security
badge, a fabricated "Ready" status indicator, an invented "AUTH" category
label, and a made-up "Bank-grade identity screening" claim — NONE of that
is acceptable. Every single piece of text or UI element on a screen must
trace back to an explicit line in the spec below.

EXPLICITLY BANNED:
- No all-caps text anywhere
- No middle-dot (·), slash (//), or decorative em-dash chrome in headings or labels
- No code-style naming visible in the UI (no "SCREEN_01", no "SPEC_X")
- No monospace font anywhere — use exactly one typeface: Inter
- No gratuitous drop shadows on every card — shadows only where specified below
- No wrapping every section/block in an identical bordered card — use plain
  whitespace as the default separator; only add a border or shadow when a
  rule below calls for it
- No suspiciously round/fake demo numbers — use specific, slightly irregular numbers
- No decorative illustration or gradient hero blocks with no real function
- No filled/colored pill-shaped badges anywhere — use the mandatory
  dot-indicator / outlined-tag system below instead
- No internal/dev category labels or chips (e.g. "AUTH", "SCREEN_X",
  section tags) rendered as visible UI elements — these are for our own
  organizational reference only and must never appear to a real user
- No fabricated status, security, or trust indicators anywhere (e.g.
  "256-bit encrypted", "Ready", "Bank-grade identity screening", "Verified
  by [made-up brand]") — every piece of text/badge on a screen must come
  directly from this spec; do not invent extra system-status or trust
  signals to make a screen look more polished

DESIGN TOKENS (use exactly these values):
- Background: #F8FBFE (very light pastel blue tint, near-white — not pure
  white, not warm cream)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active nav tab icon. Do NOT apply it to every button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — do not soften to orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data (amounts, meter
  readings) uses Inter's tabular figures.
- Shape & elevation (CONTEXTUAL, not one fixed value everywhere):
  - Hero/highlight card (the one standout element per screen): 24px corner
    radius + a soft shadow tinted toward the background blue,
    rgba(30,111,217,0.10)
  - Regular list/content cards: 14px corner radius, flat, NO shadow — 1px
    solid border (#D7E3F2) only
  - Buttons: 12px corner radius
- Badges & tags (MANDATORY on every screen with any status or descriptive label):
  - Live status (room availability, verification, payment/invoice status,
    issue status): a small 7px filled dot in the semantic color, followed
    by plain navy text — NO colored background fill, NO pill container.
  - Descriptive constraint tag (fixed attributes like "Female Only", "Max 3
    People", "No Pets"): a rectangular tag, 7px corner radius, 1px solid
    border (#D7E3F2), NO background fill, plain navy text — same outlined
    style regardless of whether the attribute reads positive or negative.
  - NEVER use a filled/colored pill badge anywhere in this project.
- Layout: on the Dashboard screen, cards may overlap/stagger slightly for
  visual depth (the one screen where that's appropriate). On list/data
  screens (invoices, members, search results), use a strict aligned grid —
  no overlapping, no staggering; clarity over personality.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  the Primary Accent color #1E6FD9. This is a placeholder — it can be
  swapped later via a short, targeted Edit prompt without affecting other
  screens.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: mobile portrait 375x812px unless noted otherwise.

CONTEXT: Creating a lease only captures ONE lead-tenant's details at
first; other roommates are added afterward via the Members screens, each
with a simple vehicle declaration.

SCREENS TO GENERATE:

20. Create Lease
- Exactly: full name, phone, ID number, address of the lead tenant; and
  Deposit, Rent amount, Start date (date picker), Term (dropdown, number
  of months) fields. "Continue" button.
- Comes from: "18" (Create new lease).
- Goes to: "Continue" → "21".

21. Choose Lease Template
- Exactly: a list of pre-built system templates (thumbnail + name), a
  radio selector, a "Skip, use the standard template" option, "Generate
  file" button.
- Comes from: "20".
- Goes to: "Generate file" → "22".

22. Export Lease PDF
- Exactly: a brief loading state — a spinner + text "Generating your lease
  file..." — that auto-advances. This is an action/loading state, not an
  interactive screen; do not add anything else to it.
- Comes from: "21".
- Goes to: auto-advances after ~1-2s → "23".

23. Upload Signed Lease
- Exactly: instructions "Please print, sign by hand, and upload a
  photo/file of the signed lease here.", an upload area (camera or
  file/photo picker), "Confirm & Activate Lease" button.
- Comes from: "22" (auto).
- Goes to: "Confirm & Activate Lease" → "18", room status becomes
  "Occupied", lease becomes Active, a group Property Chat is created
  automatically.

24. Member List
- Exactly: a list of current members — avatar, full name, phone, ID
  number (Landlords see full details), and a small vehicle icon next to
  the name for any member who has a vehicle registered (show it on at
  least one sample row, omit it on another, to demonstrate the
  conditional display). A floating "+ Add member" button.
- Comes from: "19" (Members item).
- Goes to: "+ Add member" → "25". Swipe/menu on an item → "Remove" → "26".

25. Add New Member
- Exactly: full name, phone, ID number inputs, and a toggle "Has a vehicle
  (motorbike/car): Yes/No" (simple on/off, no license plate or vehicle-
  type detail). "Add" button.
- Comes from: "24".
- Goes to: "Add" → "24", new member appears and is auto-added to the
  room's Property Chat.

26. Confirm Remove Member
- Exactly: dialog "Remove [Name] from this room?", buttons "Remove" (red)
  / "Cancel". No special "lead tenant" handling — every member is treated
  identically.
- Comes from: "24" (Remove menu).
- Goes to: confirm → "24" (updated, removed from Property Chat).
```

---

## Prompt L5/11 — Meter Reading (6 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real aligned lists/tables, not everything stuffed into its own floating
rounded card. Numbers look like real data (specific, slightly irregular
values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type size/weight
and spacing, not from wrapping things in boxes or decorative labels. Icons
are small and functional, never decorative illustrations. This is a
FULL-COLOR request (not a grayscale wireframe).

STRICT CONTENT RULE (critical — read carefully): Generate EXACTLY the
elements listed in the "SCREENS TO GENERATE" section below for each screen
— nothing more. Do NOT invent additional badges, banners, taglines,
security/trust claims, status indicators, decorative icons, marketing
copy, or "polish" elements that are not explicitly listed. If a screen's
spec lists 5 elements, the screen should have exactly those 5 elements.
When in doubt, generate LESS rather than more. This rule exists because
past generations invented things like a fake "256-bit encrypted" security
badge, a fabricated "Ready" status indicator, an invented "AUTH" category
label, and a made-up "Bank-grade identity screening" claim — NONE of that
is acceptable. Every single piece of text or UI element on a screen must
trace back to an explicit line in the spec below.

EXPLICITLY BANNED:
- No all-caps text anywhere
- No middle-dot (·), slash (//), or decorative em-dash chrome in headings or labels
- No code-style naming visible in the UI (no "SCREEN_01", no "SPEC_X")
- No monospace font anywhere — use exactly one typeface: Inter
- No gratuitous drop shadows on every card — shadows only where specified below
- No wrapping every section/block in an identical bordered card — use plain
  whitespace as the default separator; only add a border or shadow when a
  rule below calls for it
- No suspiciously round/fake demo numbers — use specific, slightly irregular numbers
- No decorative illustration or gradient hero blocks with no real function
- No filled/colored pill-shaped badges anywhere — use the mandatory
  dot-indicator / outlined-tag system below instead
- No internal/dev category labels or chips (e.g. "AUTH", "SCREEN_X",
  section tags) rendered as visible UI elements — these are for our own
  organizational reference only and must never appear to a real user
- No fabricated status, security, or trust indicators anywhere (e.g.
  "256-bit encrypted", "Ready", "Bank-grade identity screening", "Verified
  by [made-up brand]") — every piece of text/badge on a screen must come
  directly from this spec; do not invent extra system-status or trust
  signals to make a screen look more polished

DESIGN TOKENS (use exactly these values):
- Background: #F8FBFE (very light pastel blue tint, near-white — not pure
  white, not warm cream)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active nav tab icon. Do NOT apply it to every button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — do not soften to orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data (amounts, meter
  readings) uses Inter's tabular figures.
- Shape & elevation (CONTEXTUAL, not one fixed value everywhere):
  - Hero/highlight card (the one standout element per screen): 24px corner
    radius + a soft shadow tinted toward the background blue,
    rgba(30,111,217,0.10)
  - Regular list/content cards: 14px corner radius, flat, NO shadow — 1px
    solid border (#D7E3F2) only
  - Buttons: 12px corner radius
- Badges & tags (MANDATORY on every screen with any status or descriptive label):
  - Live status (room availability, verification, payment/invoice status,
    issue status): a small 7px filled dot in the semantic color, followed
    by plain navy text — NO colored background fill, NO pill container.
  - Descriptive constraint tag (fixed attributes like "Female Only", "Max 3
    People", "No Pets"): a rectangular tag, 7px corner radius, 1px solid
    border (#D7E3F2), NO background fill, plain navy text — same outlined
    style regardless of whether the attribute reads positive or negative.
  - NEVER use a filled/colored pill badge anywhere in this project.
- Layout: on the Dashboard screen, cards may overlap/stagger slightly for
  visual depth (the one screen where that's appropriate). On list/data
  screens (invoices, members, search results), use a strict aligned grid —
  no overlapping, no staggering; clarity over personality.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  the Primary Accent color #1E6FD9. This is a placeholder — it can be
  swapped later via a short, targeted Edit prompt without affecting other
  screens.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: mobile portrait 375x812px unless noted otherwise.

CONTEXT: Two parallel flows sharing the same Camera/OCR screens — a
SINGLE reading (from Room Detail) and a BULK reading (from the building's
Room List). This is exclusively a Landlord responsibility.

SCREENS TO GENERATE:

27. Single Meter Reading
- Exactly two buttons: "Take a photo of the meter" and "Choose from
  library".
- Comes from: "19" (Meter Reading item).
- Goes to: either option → "31. Camera — Meter Photo" (if Take photo) or
  straight to "32. OCR Result" (if choosing from library).

28. Bulk Reading Entry
- Exactly: a confirmation screen "Start meter reading for 20 rooms in this
  building?" + a condensed list of the rooms to be read + a "Start"
  button.
- Comes from: the "Bulk Meter Reading" button on "16".
- Goes to: "Start" → "29".

29. Bulk Reading Flow
- Exactly: a header showing "Room 3/20" + the current room's name/number +
  a progress bar (Accent color); below it, reuse the exact UI of "31" and
  "32" for the current room; two buttons at the bottom: "Next" and "Skip
  this room".
- Comes from: "28" (Start).
- Goes to: "Next"/"Skip" → advances to the next room on this same screen
  (counter increases). List exhausted → "30".

30. Bulk Reading Summary
- Exactly: title "18 of 20 rooms completed.", a list of remaining rooms (if
  any) with a reason (e.g. "Room vacant", "Photo unclear, needs a redo"),
  "Done" button.
- Comes from: "29" (exhausted).
- Goes to: "Done" → "16".

31. Camera — Meter Photo
- Exactly: a full-screen camera viewfinder, a large round shutter button
  at the bottom; supports the electricity meter and water meter one after
  another (2 shots, with a label above the viewfinder: "Electricity
  meter" / "Water meter").
- Comes from: "27" (Take photo), or within the loop in "29".
- Goes to: after both photos → "32".

32. OCR Result
- Exactly: the 2 photos just taken/chosen, each with the OCR-recognized
  number next to it (an editable input, tabular figures). IF OCR fails
  completely: replace with a banner "Couldn't read this — please enter the
  value manually" + an empty input (no fake suggested number). "Confirm"
  button.
- Comes from: "31", or choosing from library on "27".
- Goes to: "Confirm" → single flow → "33. Invoice Preview" (Prompt L6);
  bulk flow → back to "29" for the next room.
```

---

## Prompt L6/11 — Invoices (5 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real aligned lists/tables, not everything stuffed into its own floating
rounded card. Numbers look like real data (specific, slightly irregular
values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type size/weight
and spacing, not from wrapping things in boxes or decorative labels. Icons
are small and functional, never decorative illustrations. This is a
FULL-COLOR request (not a grayscale wireframe).

STRICT CONTENT RULE (critical — read carefully): Generate EXACTLY the
elements listed in the "SCREENS TO GENERATE" section below for each screen
— nothing more. Do NOT invent additional badges, banners, taglines,
security/trust claims, status indicators, decorative icons, marketing
copy, or "polish" elements that are not explicitly listed. If a screen's
spec lists 5 elements, the screen should have exactly those 5 elements.
When in doubt, generate LESS rather than more. This rule exists because
past generations invented things like a fake "256-bit encrypted" security
badge, a fabricated "Ready" status indicator, an invented "AUTH" category
label, and a made-up "Bank-grade identity screening" claim — NONE of that
is acceptable. Every single piece of text or UI element on a screen must
trace back to an explicit line in the spec below.

EXPLICITLY BANNED:
- No all-caps text anywhere
- No middle-dot (·), slash (//), or decorative em-dash chrome in headings or labels
- No code-style naming visible in the UI (no "SCREEN_01", no "SPEC_X")
- No monospace font anywhere — use exactly one typeface: Inter
- No gratuitous drop shadows on every card — shadows only where specified below
- No wrapping every section/block in an identical bordered card — use plain
  whitespace as the default separator; only add a border or shadow when a
  rule below calls for it
- No suspiciously round/fake demo numbers — use specific, slightly irregular numbers
- No decorative illustration or gradient hero blocks with no real function
- No filled/colored pill-shaped badges anywhere — use the mandatory
  dot-indicator / outlined-tag system below instead
- No internal/dev category labels or chips (e.g. "AUTH", "SCREEN_X",
  section tags) rendered as visible UI elements — these are for our own
  organizational reference only and must never appear to a real user
- No fabricated status, security, or trust indicators anywhere (e.g.
  "256-bit encrypted", "Ready", "Bank-grade identity screening", "Verified
  by [made-up brand]") — every piece of text/badge on a screen must come
  directly from this spec; do not invent extra system-status or trust
  signals to make a screen look more polished

DESIGN TOKENS (use exactly these values):
- Background: #F8FBFE (very light pastel blue tint, near-white — not pure
  white, not warm cream)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active nav tab icon. Do NOT apply it to every button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — do not soften to orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data (amounts, meter
  readings) uses Inter's tabular figures.
- Shape & elevation (CONTEXTUAL, not one fixed value everywhere):
  - Hero/highlight card (the one standout element per screen): 24px corner
    radius + a soft shadow tinted toward the background blue,
    rgba(30,111,217,0.10)
  - Regular list/content cards: 14px corner radius, flat, NO shadow — 1px
    solid border (#D7E3F2) only
  - Buttons: 12px corner radius
- Badges & tags (MANDATORY on every screen with any status or descriptive label):
  - Live status (room availability, verification, payment/invoice status,
    issue status): a small 7px filled dot in the semantic color, followed
    by plain navy text — NO colored background fill, NO pill container.
  - Descriptive constraint tag (fixed attributes like "Female Only", "Max 3
    People", "No Pets"): a rectangular tag, 7px corner radius, 1px solid
    border (#D7E3F2), NO background fill, plain navy text — same outlined
    style regardless of whether the attribute reads positive or negative.
  - NEVER use a filled/colored pill badge anywhere in this project.
- Layout: on the Dashboard screen, cards may overlap/stagger slightly for
  visual depth (the one screen where that's appropriate). On list/data
  screens (invoices, members, search results), use a strict aligned grid —
  no overlapping, no staggering; clarity over personality.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  the Primary Accent color #1E6FD9. This is a placeholder — it can be
  swapped later via a short, targeted Edit prompt without affecting other
  screens.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: mobile portrait 375x812px unless noted otherwise.

CONTEXT: From confirmed meter readings, the system auto-calculates the
monthly invoice. There's also a flow to review/edit/cancel already-issued
invoices, only allowed while zero payments have been recorded.

SCREENS TO GENERATE:

33. Invoice Preview (before issuing)
- Exactly: an aligned breakdown — Room rent, Electricity (kWh × rate =
  amount), Water, Other services; total at the bottom (bold, larger); every
  line tap-to-edit. A large "Issue Invoice" button.
- Comes from: "32" (confirmed readings, single flow).
- Goes to: "Issue Invoice" → "36".

34. Issued Invoice List
- Exactly: a list by month for one room — month, total amount, a status
  dot-indicator (Unpaid/Overdue/Partial/Paid/Cancelled — Cancelled shown
  with muted strikethrough text).
- Comes from: "19" (Invoices item).
- Goes to: an item with NO payment yet → "35. Edit/Cancel Invoice". An
  item with some payment already → view-only detail (no edit/cancel). A
  "Confirm cash payment" button on an unpaid/partial item → "37".

35. Edit/Cancel Invoice
- Reuses the exact UI of "33" (editable breakdown), plus a "Cancel
  Invoice" button (red, outline) at the bottom. These edit/cancel controls
  appear ONLY when the invoice has zero payments recorded.
- Comes from: "34" (unpaid item).
- Goes to: "Save changes" → "34", invoice updates + a new VietQR code is
  generated + an "Invoice updated" card posts to the room's Property Chat.
  "Cancel Invoice" → confirmation dialog → "34" with status "Cancelled".

36. Issue Invoice
- Exactly: a success state — large green checkmark icon, "Invoice for
  September 2026 issued", the newly generated VietQR code, text
  "Notification sent to the room's Chat.", "Done" button.
- Comes from: "33" (Issue Invoice).
- Goes to: "Done" → "34".

37. Confirm Cash Payment
- Exactly: three figures — Total invoice / Paid / Remaining; a prominent
  default button "✓ Confirm FULL payment received"; below it, a smaller
  link-style line "Or enter the amount received" that reveals an amount
  input + a secondary "Confirm" button when tapped.
- Comes from: "34" (Confirm cash payment button).
- Goes to: confirming → "34", status/amounts update automatically.
```

---

## Prompt L7/11 — Billing Cycle & Debt (3 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real aligned lists/tables, not everything stuffed into its own floating
rounded card. Numbers look like real data (specific, slightly irregular
values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type size/weight
and spacing, not from wrapping things in boxes or decorative labels. Icons
are small and functional, never decorative illustrations. This is a
FULL-COLOR request (not a grayscale wireframe).

STRICT CONTENT RULE (critical — read carefully): Generate EXACTLY the
elements listed in the "SCREENS TO GENERATE" section below for each screen
— nothing more. Do NOT invent additional badges, banners, taglines,
security/trust claims, status indicators, decorative icons, marketing
copy, or "polish" elements that are not explicitly listed. If a screen's
spec lists 5 elements, the screen should have exactly those 5 elements.
When in doubt, generate LESS rather than more. This rule exists because
past generations invented things like a fake "256-bit encrypted" security
badge, a fabricated "Ready" status indicator, an invented "AUTH" category
label, and a made-up "Bank-grade identity screening" claim — NONE of that
is acceptable. Every single piece of text or UI element on a screen must
trace back to an explicit line in the spec below.

EXPLICITLY BANNED:
- No all-caps text anywhere
- No middle-dot (·), slash (//), or decorative em-dash chrome in headings or labels
- No code-style naming visible in the UI (no "SCREEN_01", no "SPEC_X")
- No monospace font anywhere — use exactly one typeface: Inter
- No gratuitous drop shadows on every card — shadows only where specified below
- No wrapping every section/block in an identical bordered card — use plain
  whitespace as the default separator; only add a border or shadow when a
  rule below calls for it
- No suspiciously round/fake demo numbers — use specific, slightly irregular numbers
- No decorative illustration or gradient hero blocks with no real function
- No filled/colored pill-shaped badges anywhere — use the mandatory
  dot-indicator / outlined-tag system below instead
- No internal/dev category labels or chips (e.g. "AUTH", "SCREEN_X",
  section tags) rendered as visible UI elements — these are for our own
  organizational reference only and must never appear to a real user
- No fabricated status, security, or trust indicators anywhere (e.g.
  "256-bit encrypted", "Ready", "Bank-grade identity screening", "Verified
  by [made-up brand]") — every piece of text/badge on a screen must come
  directly from this spec; do not invent extra system-status or trust
  signals to make a screen look more polished

DESIGN TOKENS (use exactly these values):
- Background: #F8FBFE (very light pastel blue tint, near-white — not pure
  white, not warm cream)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active nav tab icon. Do NOT apply it to every button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — do not soften to orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data (amounts, meter
  readings) uses Inter's tabular figures.
- Shape & elevation (CONTEXTUAL, not one fixed value everywhere):
  - Hero/highlight card (the one standout element per screen): 24px corner
    radius + a soft shadow tinted toward the background blue,
    rgba(30,111,217,0.10)
  - Regular list/content cards: 14px corner radius, flat, NO shadow — 1px
    solid border (#D7E3F2) only
  - Buttons: 12px corner radius
- Badges & tags (MANDATORY on every screen with any status or descriptive label):
  - Live status (room availability, verification, payment/invoice status,
    issue status): a small 7px filled dot in the semantic color, followed
    by plain navy text — NO colored background fill, NO pill container.
  - Descriptive constraint tag (fixed attributes like "Female Only", "Max 3
    People", "No Pets"): a rectangular tag, 7px corner radius, 1px solid
    border (#D7E3F2), NO background fill, plain navy text — same outlined
    style regardless of whether the attribute reads positive or negative.
  - NEVER use a filled/colored pill badge anywhere in this project.
- Layout: on the Dashboard screen, cards may overlap/stagger slightly for
  visual depth (the one screen where that's appropriate). On list/data
  screens (invoices, members, search results), use a strict aligned grid —
  no overlapping, no staggering; clarity over personality.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  the Primary Accent color #1E6FD9. This is a placeholder — it can be
  swapped later via a short, targeted Edit prompt without affecting other
  screens.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: mobile portrait 375x812px unless noted otherwise.

SCREENS TO GENERATE:

38. Billing Cycle & Debt Scan Settings
- Exactly: a scope selector — "Entire profile" / "One specific building" /
  "One specific room" (segmented control or radio group; a narrower scope
  overrides a broader one). "Continue" button.
- Comes from: the "Billing Cycle Settings" item on "51. Profile" (Prompt
  L11).
- Goes to: "Continue" → "39".

39. Due Date Settings
- Exactly: Monthly billing date (e.g. "Day 5"), Payment due period (e.g.
  "+7 days"), Reminder timing (e.g. "Remind 2 days before due") inputs,
  "Save" button.
- Comes from: "38".
- Goes to: "Save" → "38".

40. Debt List
- Exactly: a simple, strictly aligned list — Room/Building name, Amount
  still owed (red, bold), Days since the expected payment day. Do NOT label
  the column "Days overdue" and do NOT show an "Overdue" badge: this system
  has no overdue state, no due date, and no penalty (D39).
- Comes from: the "Outstanding Debt" section on "9b. Dashboard" (Prompt
  L2).
- Goes to: a row → "34. Issued Invoice List" (Prompt L6) for that room.
```

---

## Prompt L8/11 — Issues (3 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real aligned lists/tables, not everything stuffed into its own floating
rounded card. Numbers look like real data (specific, slightly irregular
values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type size/weight
and spacing, not from wrapping things in boxes or decorative labels. Icons
are small and functional, never decorative illustrations. This is a
FULL-COLOR request (not a grayscale wireframe).

STRICT CONTENT RULE (critical — read carefully): Generate EXACTLY the
elements listed in the "SCREENS TO GENERATE" section below for each screen
— nothing more. Do NOT invent additional badges, banners, taglines,
security/trust claims, status indicators, decorative icons, marketing
copy, or "polish" elements that are not explicitly listed. If a screen's
spec lists 5 elements, the screen should have exactly those 5 elements.
When in doubt, generate LESS rather than more. This rule exists because
past generations invented things like a fake "256-bit encrypted" security
badge, a fabricated "Ready" status indicator, an invented "AUTH" category
label, and a made-up "Bank-grade identity screening" claim — NONE of that
is acceptable. Every single piece of text or UI element on a screen must
trace back to an explicit line in the spec below.

EXPLICITLY BANNED:
- No all-caps text anywhere
- No middle-dot (·), slash (//), or decorative em-dash chrome in headings or labels
- No code-style naming visible in the UI (no "SCREEN_01", no "SPEC_X")
- No monospace font anywhere — use exactly one typeface: Inter
- No gratuitous drop shadows on every card — shadows only where specified below
- No wrapping every section/block in an identical bordered card — use plain
  whitespace as the default separator; only add a border or shadow when a
  rule below calls for it
- No suspiciously round/fake demo numbers — use specific, slightly irregular numbers
- No decorative illustration or gradient hero blocks with no real function
- No filled/colored pill-shaped badges anywhere — use the mandatory
  dot-indicator / outlined-tag system below instead
- No internal/dev category labels or chips (e.g. "AUTH", "SCREEN_X",
  section tags) rendered as visible UI elements — these are for our own
  organizational reference only and must never appear to a real user
- No fabricated status, security, or trust indicators anywhere (e.g.
  "256-bit encrypted", "Ready", "Bank-grade identity screening", "Verified
  by [made-up brand]") — every piece of text/badge on a screen must come
  directly from this spec; do not invent extra system-status or trust
  signals to make a screen look more polished

DESIGN TOKENS (use exactly these values):
- Background: #F8FBFE (very light pastel blue tint, near-white — not pure
  white, not warm cream)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active nav tab icon. Do NOT apply it to every button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — do not soften to orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data (amounts, meter
  readings) uses Inter's tabular figures.
- Shape & elevation (CONTEXTUAL, not one fixed value everywhere):
  - Hero/highlight card (the one standout element per screen): 24px corner
    radius + a soft shadow tinted toward the background blue,
    rgba(30,111,217,0.10)
  - Regular list/content cards: 14px corner radius, flat, NO shadow — 1px
    solid border (#D7E3F2) only
  - Buttons: 12px corner radius
- Badges & tags (MANDATORY on every screen with any status or descriptive label):
  - Live status (room availability, verification, payment/invoice status,
    issue status): a small 7px filled dot in the semantic color, followed
    by plain navy text — NO colored background fill, NO pill container.
  - Descriptive constraint tag (fixed attributes like "Female Only", "Max 3
    People", "No Pets"): a rectangular tag, 7px corner radius, 1px solid
    border (#D7E3F2), NO background fill, plain navy text — same outlined
    style regardless of whether the attribute reads positive or negative.
  - NEVER use a filled/colored pill badge anywhere in this project.
- Layout: on the Dashboard screen, cards may overlap/stagger slightly for
  visual depth (the one screen where that's appropriate). On list/data
  screens (invoices, members, search results), use a strict aligned grid —
  no overlapping, no staggering; clarity over personality.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  the Primary Accent color #1E6FD9. This is a placeholder — it can be
  swapped later via a short, targeted Edit prompt without affecting other
  screens.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: mobile portrait 375x812px unless noted otherwise.

CONTEXT: The "Issues" tab — aggregates every issue from every Building/
Room. Every issue is pre-tagged with its room/building automatically
(Tenants never manually select a room when reporting).

SCREENS TO GENERATE:

41. Issues Tab
- Exactly: a list of every issue, each item MUST show a "Building — Room
  number" label (e.g. "Block A — Room 203"), plus a short description and
  a status dot-indicator. Filter chips at the top (All / Open / In
  Progress / Resolved).
- Comes from: tapping the "Issues" tab from anywhere.
- Goes to: tapping an item → opens "42. Issue Detail Popup" (bottom
  sheet).

42. Issue Detail Popup
- Exactly: a bottom sheet — header "Building — Room — Reported by", full
  description + photos, a dropdown/segmented control to change status (In
  Progress / Resolved / Cancelled), and a "View in Room Chat" button
  (outline, chat icon) that deep-links to that room's Property Chat.
  There is NO built-in discussion thread embedded in this popup (unlike
  the Tenant side).
- Comes from: tapping an item on "41".
- Goes to: changing status → updates immediately, closes to "41". "View in
  Room Chat" → "50. Chat Thread Detail" (Prompt L10) for that room.

43. Landlord Creates an Issue
- Exactly: a description textarea + camera/library photo attachment. The
  room context is auto-attached based on the currently open room (shown in
  the header, not editable).
- Comes from: "+ Report issue" on "18. Room Detail" (Prompt L3).
- Goes to: "Submit" → "41", new item appears at the top.
```

---

## Prompt L9/11 — Move-out / Settlement (5 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real aligned lists/tables, not everything stuffed into its own floating
rounded card. Numbers look like real data (specific, slightly irregular
values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type size/weight
and spacing, not from wrapping things in boxes or decorative labels. Icons
are small and functional, never decorative illustrations. This is a
FULL-COLOR request (not a grayscale wireframe).

STRICT CONTENT RULE (critical — read carefully): Generate EXACTLY the
elements listed in the "SCREENS TO GENERATE" section below for each screen
— nothing more. Do NOT invent additional badges, banners, taglines,
security/trust claims, status indicators, decorative icons, marketing
copy, or "polish" elements that are not explicitly listed. If a screen's
spec lists 5 elements, the screen should have exactly those 5 elements.
When in doubt, generate LESS rather than more. This rule exists because
past generations invented things like a fake "256-bit encrypted" security
badge, a fabricated "Ready" status indicator, an invented "AUTH" category
label, and a made-up "Bank-grade identity screening" claim — NONE of that
is acceptable. Every single piece of text or UI element on a screen must
trace back to an explicit line in the spec below.

EXPLICITLY BANNED:
- No all-caps text anywhere
- No middle-dot (·), slash (//), or decorative em-dash chrome in headings or labels
- No code-style naming visible in the UI (no "SCREEN_01", no "SPEC_X")
- No monospace font anywhere — use exactly one typeface: Inter
- No gratuitous drop shadows on every card — shadows only where specified below
- No wrapping every section/block in an identical bordered card — use plain
  whitespace as the default separator; only add a border or shadow when a
  rule below calls for it
- No suspiciously round/fake demo numbers — use specific, slightly irregular numbers
- No decorative illustration or gradient hero blocks with no real function
- No filled/colored pill-shaped badges anywhere — use the mandatory
  dot-indicator / outlined-tag system below instead
- No internal/dev category labels or chips (e.g. "AUTH", "SCREEN_X",
  section tags) rendered as visible UI elements — these are for our own
  organizational reference only and must never appear to a real user
- No fabricated status, security, or trust indicators anywhere (e.g.
  "256-bit encrypted", "Ready", "Bank-grade identity screening", "Verified
  by [made-up brand]") — every piece of text/badge on a screen must come
  directly from this spec; do not invent extra system-status or trust
  signals to make a screen look more polished

DESIGN TOKENS (use exactly these values):
- Background: #F8FBFE (very light pastel blue tint, near-white — not pure
  white, not warm cream)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active nav tab icon. Do NOT apply it to every button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — do not soften to orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data (amounts, meter
  readings) uses Inter's tabular figures.
- Shape & elevation (CONTEXTUAL, not one fixed value everywhere):
  - Hero/highlight card (the one standout element per screen): 24px corner
    radius + a soft shadow tinted toward the background blue,
    rgba(30,111,217,0.10)
  - Regular list/content cards: 14px corner radius, flat, NO shadow — 1px
    solid border (#D7E3F2) only
  - Buttons: 12px corner radius
- Badges & tags (MANDATORY on every screen with any status or descriptive label):
  - Live status (room availability, verification, payment/invoice status,
    issue status): a small 7px filled dot in the semantic color, followed
    by plain navy text — NO colored background fill, NO pill container.
  - Descriptive constraint tag (fixed attributes like "Female Only", "Max 3
    People", "No Pets"): a rectangular tag, 7px corner radius, 1px solid
    border (#D7E3F2), NO background fill, plain navy text — same outlined
    style regardless of whether the attribute reads positive or negative.
  - NEVER use a filled/colored pill badge anywhere in this project.
- Layout: on the Dashboard screen, cards may overlap/stagger slightly for
  visual depth (the one screen where that's appropriate). On list/data
  screens (invoices, members, search results), use a strict aligned grid —
  no overlapping, no staggering; clarity over personality.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  the Primary Accent color #1E6FD9. This is a placeholder — it can be
  swapped later via a short, targeted Edit prompt without affecting other
  screens.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: mobile portrait 375x812px unless noted otherwise.

SCREENS TO GENERATE:

44. Final Meter Reading
- Reuses the exact UI of "31/32" (Camera/Upload + OCR), header retitled
  "Final meter reading before move-out."
- Comes from: "Move-out / Settlement" on "19. Room Utility Menu".
- Goes to: after confirming readings → "45".

45. Final Settlement Invoice
- Exactly: Electricity/water auto-calculated from the just-confirmed
  readings; the "Room rent" line is a FREE-TEXT INPUT for the Landlord to
  type manually (not a rigid per-day formula) — a small gray hint line
  below it: "Suggested (pro-rated by days stayed): $X,XXX" for reference
  only. "Continue" button.
- Comes from: "44".
- Goes to: "Continue" → "46".

46. Deposit Settlement
- Exactly: "Original deposit: $X" text; one input "Deduction amount" (if
  any) + one text input "Reason for deduction"; an auto-calculated
  "Deposit to be refunded = Deposit − Deductions − Unpaid final invoice"
  shown below (bold, larger). "Continue" button.
- Comes from: "45".
- Goes to: "Continue" → "47".

47. Confirm Move-out Complete
- Exactly: a summary of the final-invoice status (paid/unpaid) and the
  deposit refund amount; a "Confirm move-out complete" button.
- Comes from: "46".
- Goes to: confirm → lease becomes "Ended" → "48".

48. Pending Cleanup Status
- Exactly: a room card with a large "Pending Cleanup" badge (gray), a
  "Mark room ready for re-listing" button.
- Comes from: "47" (automatic).
- Goes to: "Mark room ready" → "16. Room List" (Prompt L3), the room cell
  turns "Vacant" color.
```

---

## Prompt L10/11 — Chat Inbox (2 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real aligned lists/tables, not everything stuffed into its own floating
rounded card. Numbers look like real data (specific, slightly irregular
values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type size/weight
and spacing, not from wrapping things in boxes or decorative labels. Icons
are small and functional, never decorative illustrations. This is a
FULL-COLOR request (not a grayscale wireframe).

STRICT CONTENT RULE (critical — read carefully): Generate EXACTLY the
elements listed in the "SCREENS TO GENERATE" section below for each screen
— nothing more. Do NOT invent additional badges, banners, taglines,
security/trust claims, status indicators, decorative icons, marketing
copy, or "polish" elements that are not explicitly listed. If a screen's
spec lists 5 elements, the screen should have exactly those 5 elements.
When in doubt, generate LESS rather than more. This rule exists because
past generations invented things like a fake "256-bit encrypted" security
badge, a fabricated "Ready" status indicator, an invented "AUTH" category
label, and a made-up "Bank-grade identity screening" claim — NONE of that
is acceptable. Every single piece of text or UI element on a screen must
trace back to an explicit line in the spec below.

EXPLICITLY BANNED:
- No all-caps text anywhere
- No middle-dot (·), slash (//), or decorative em-dash chrome in headings or labels
- No code-style naming visible in the UI (no "SCREEN_01", no "SPEC_X")
- No monospace font anywhere — use exactly one typeface: Inter
- No gratuitous drop shadows on every card — shadows only where specified below
- No wrapping every section/block in an identical bordered card — use plain
  whitespace as the default separator; only add a border or shadow when a
  rule below calls for it
- No suspiciously round/fake demo numbers — use specific, slightly irregular numbers
- No decorative illustration or gradient hero blocks with no real function
- No filled/colored pill-shaped badges anywhere — use the mandatory
  dot-indicator / outlined-tag system below instead
- No internal/dev category labels or chips (e.g. "AUTH", "SCREEN_X",
  section tags) rendered as visible UI elements — these are for our own
  organizational reference only and must never appear to a real user
- No fabricated status, security, or trust indicators anywhere (e.g.
  "256-bit encrypted", "Ready", "Bank-grade identity screening", "Verified
  by [made-up brand]") — every piece of text/badge on a screen must come
  directly from this spec; do not invent extra system-status or trust
  signals to make a screen look more polished

DESIGN TOKENS (use exactly these values):
- Background: #F8FBFE (very light pastel blue tint, near-white — not pure
  white, not warm cream)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active nav tab icon. Do NOT apply it to every button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — do not soften to orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data (amounts, meter
  readings) uses Inter's tabular figures.
- Shape & elevation (CONTEXTUAL, not one fixed value everywhere):
  - Hero/highlight card (the one standout element per screen): 24px corner
    radius + a soft shadow tinted toward the background blue,
    rgba(30,111,217,0.10)
  - Regular list/content cards: 14px corner radius, flat, NO shadow — 1px
    solid border (#D7E3F2) only
  - Buttons: 12px corner radius
- Badges & tags (MANDATORY on every screen with any status or descriptive label):
  - Live status (room availability, verification, payment/invoice status,
    issue status): a small 7px filled dot in the semantic color, followed
    by plain navy text — NO colored background fill, NO pill container.
  - Descriptive constraint tag (fixed attributes like "Female Only", "Max 3
    People", "No Pets"): a rectangular tag, 7px corner radius, 1px solid
    border (#D7E3F2), NO background fill, plain navy text — same outlined
    style regardless of whether the attribute reads positive or negative.
  - NEVER use a filled/colored pill badge anywhere in this project.
- Layout: on the Dashboard screen, cards may overlap/stagger slightly for
  visual depth (the one screen where that's appropriate). On list/data
  screens (invoices, members, search results), use a strict aligned grid —
  no overlapping, no staggering; clarity over personality.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  the Primary Accent color #1E6FD9. This is a placeholder — it can be
  swapped later via a short, targeted Edit prompt without affecting other
  screens.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: mobile portrait 375x812px unless noted otherwise.

CONTEXT: The "Chat" tab — unifies ALL threads (1:1 chats with prospective
tenants + Property Group Chats for every room + building-wide chats) into
a single Inbox.

SCREENS TO GENERATE:

49. Inbox (Chat tab)
- A thread list like the Tenant app's Inbox, from the Landlord's
  perspective: each item adds a "Building — Room" label if it's a
  Property Chat, or the prospective tenant's name if it's a direct chat.
- Comes from: tapping the "Chat" tab from anywhere.
- Goes to: tapping a thread → "50. Chat Thread Detail".

50. Chat Thread Detail
- Shared UI for all 3 thread types (direct chat / room group chat /
  building-wide chat), content varying by type as described for the
  Tenant app's equivalent screens.
- Comes from: "49", or a deep link from "19. Room Utility Menu" (Chat
  item), or from "42. Issue Detail Popup" ("View in Room Chat").
- Goes to: back → "49" (or back to whichever screen deep-linked here).
```

---

## Prompt L11/11 — Settings (2 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real aligned lists/tables, not everything stuffed into its own floating
rounded card. Numbers look like real data (specific, slightly irregular
values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type size/weight
and spacing, not from wrapping things in boxes or decorative labels. Icons
are small and functional, never decorative illustrations. This is a
FULL-COLOR request (not a grayscale wireframe).

STRICT CONTENT RULE (critical — read carefully): Generate EXACTLY the
elements listed in the "SCREENS TO GENERATE" section below for each screen
— nothing more. Do NOT invent additional badges, banners, taglines,
security/trust claims, status indicators, decorative icons, marketing
copy, or "polish" elements that are not explicitly listed. If a screen's
spec lists 5 elements, the screen should have exactly those 5 elements.
When in doubt, generate LESS rather than more. This rule exists because
past generations invented things like a fake "256-bit encrypted" security
badge, a fabricated "Ready" status indicator, an invented "AUTH" category
label, and a made-up "Bank-grade identity screening" claim — NONE of that
is acceptable. Every single piece of text or UI element on a screen must
trace back to an explicit line in the spec below.

EXPLICITLY BANNED:
- No all-caps text anywhere
- No middle-dot (·), slash (//), or decorative em-dash chrome in headings or labels
- No code-style naming visible in the UI (no "SCREEN_01", no "SPEC_X")
- No monospace font anywhere — use exactly one typeface: Inter
- No gratuitous drop shadows on every card — shadows only where specified below
- No wrapping every section/block in an identical bordered card — use plain
  whitespace as the default separator; only add a border or shadow when a
  rule below calls for it
- No suspiciously round/fake demo numbers — use specific, slightly irregular numbers
- No decorative illustration or gradient hero blocks with no real function
- No filled/colored pill-shaped badges anywhere — use the mandatory
  dot-indicator / outlined-tag system below instead
- No internal/dev category labels or chips (e.g. "AUTH", "SCREEN_X",
  section tags) rendered as visible UI elements — these are for our own
  organizational reference only and must never appear to a real user
- No fabricated status, security, or trust indicators anywhere (e.g.
  "256-bit encrypted", "Ready", "Bank-grade identity screening", "Verified
  by [made-up brand]") — every piece of text/badge on a screen must come
  directly from this spec; do not invent extra system-status or trust
  signals to make a screen look more polished

DESIGN TOKENS (use exactly these values):
- Background: #F8FBFE (very light pastel blue tint, near-white — not pure
  white, not warm cream)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active nav tab icon. Do NOT apply it to every button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — do not soften to orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data (amounts, meter
  readings) uses Inter's tabular figures.
- Shape & elevation (CONTEXTUAL, not one fixed value everywhere):
  - Hero/highlight card (the one standout element per screen): 24px corner
    radius + a soft shadow tinted toward the background blue,
    rgba(30,111,217,0.10)
  - Regular list/content cards: 14px corner radius, flat, NO shadow — 1px
    solid border (#D7E3F2) only
  - Buttons: 12px corner radius
- Badges & tags (MANDATORY on every screen with any status or descriptive label):
  - Live status (room availability, verification, payment/invoice status,
    issue status): a small 7px filled dot in the semantic color, followed
    by plain navy text — NO colored background fill, NO pill container.
  - Descriptive constraint tag (fixed attributes like "Female Only", "Max 3
    People", "No Pets"): a rectangular tag, 7px corner radius, 1px solid
    border (#D7E3F2), NO background fill, plain navy text — same outlined
    style regardless of whether the attribute reads positive or negative.
  - NEVER use a filled/colored pill badge anywhere in this project.
- Layout: on the Dashboard screen, cards may overlap/stagger slightly for
  visual depth (the one screen where that's appropriate). On list/data
  screens (invoices, members, search results), use a strict aligned grid —
  no overlapping, no staggering; clarity over personality.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  the Primary Accent color #1E6FD9. This is a placeholder — it can be
  swapped later via a short, targeted Edit prompt without affecting other
  screens.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: mobile portrait 375x812px unless noted otherwise.

SCREENS TO GENERATE:

51. Profile
- Exactly: avatar + name + phone (editable). Does NOT contain any bank-
  account info (that lives at the building level — see "15"). Menu:
  "Billing Cycle & Debt Scan Settings", "Notification Settings", "Log out"
  (red text).
- Comes from: tapping the "Settings" tab from anywhere.
- Goes to: "Billing Cycle Settings" → "38" (Prompt L7). "Notification
  Settings" → "52". "Log out" → "7. Logout Confirmation" (Prompt L1).

52. Notification Settings
- Exactly one toggle switch: "Enable notifications" — identical to the
  Tenant app, not broken down by type.
- Comes from: "51".
- Goes to: back → "51".
```

---

## ✅ DONE — Zone A (34 screens, 7 prompts) + Zone B (55 screens, 11 prompts) = 89 screens total for the Mobile file (2 separate apps)
