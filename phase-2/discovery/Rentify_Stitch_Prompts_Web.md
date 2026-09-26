# Rentify — Stitch Prompts — WEB (2 separate apps: Tenant & Landlord, plus a separate Admin console)

> **⚠️ ARCHITECTURE v1.2:** Tenant and Landlord are now **two completely
> separate web apps** (two separate Stitch projects) — NOT one shared app
> with path-based role routing. Admin is a THIRD, fully independent web
> console. This file contains prompts for all three, clearly separated
> into ZONES so they never get mixed up:
> - **ZONE A (below): "Rentify Tenant — Web App"**
> - **ZONE B (further down): "Rentify Landlord — Web App"**
> - **ZONE C (at the end): "Rentify Admin — Web App"**
>
> Open THREE separate Stitch projects, named exactly as above, and paste
> only the matching zone's prompts into each. Do not mix screens between
> projects. Within each zone, paste **one prompt block at a time**, in
> order, waiting for each batch to finish before pasting the next.
>
> Every screen description below states EXACTLY what must appear — no more,
> no less. If Stitch adds anything not listed (a badge, a claim, a label,
> extra copy), that is a fabrication and must be removed via a follow-up
> Edit prompt. See the STRICT CONTENT RULE inside the Design System block
> below — it exists specifically to prevent this.

---

## 🎨 DESIGN SYSTEM (identical for every prompt in this file — all three zones)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.
```

---
---

# ZONE A — "Rentify Tenant — Web App" (34 screens, 7 prompts)

> Open a Stitch project named **"Rentify Tenant — Web App"**. This app
> serves ONLY tenants/guests — no landlord content anywhere. Fixed left
> sidebar nav (shown once logged in): **Find a room · Roommate Match ·
> Messages · My Room · Account**. Same business content as the Mobile
> Tenant app — only the layout differs (sidebar instead of bottom nav,
> modals instead of bottom sheets, multi-column grids instead of a single
> scrolling column).

## Prompt T1/7 — Auth (8 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.

CONTEXT: The authentication flow for the Tenant web app. No role selection
anywhere — this app is exclusively for Tenants/Guests.

SCREENS TO GENERATE:

1. Splash — SKIP. Web apps do not need a splash/loading screen; go
straight to "9. Home / Room List" (checking for a saved session happens
invisibly). Do not generate a numbered screen for this — screen numbering
below starts at "2" to stay aligned with the Mobile app's numbering for
easy cross-reference, but there is no screen "1" to build on Web.

2. Login
- A form card centered on the page (max-width ~420px) on the #F8FBFE
  background. Exactly: Email input, Password input (eye icon), full-width
  "Log in" button, "Forgot password?" link, "Don't have an account? Sign
  up" line. Inline error state: red input outline + small red error text.
- Comes from: a "Log in" button in the header of "9. Home", or any gated
  action anywhere (opens as a MODAL over the current page, not a page
  navigation).
- Goes to: correct login → "9. Home / Room List" (restricted-account
  banner behavior as in "6"). "Forgot password?" → "3". "Sign up" → "5".

3. Forgot Password — Enter Email
- A centered card: title, description line, Email input, "Send reset
  link" button; on send, the same card shows a success state.
- Comes from: "2" (Forgot password link).
- Goes to: "Back to Login" → "2".

4. Reset Password
- A centered card: two inputs (New Password, Confirm Password), "Reset
  password" button.
- Comes from: the email link (simulated from "3").
- Goes to: success → "2" with a success banner.

5. Sign Up
- A centered form card: Email, Password, Confirm Password (eye icons),
  Full name, Phone. "Sign up" button, "Already have an account? Log in"
  line. Inline validation: mismatched passwords → red outline + "Passwords
  don't match" text.
- Comes from: "2" (sign-up link).
- Goes to: success → "9. Home / Room List".

6. Account Restricted (banner state)
- A variant of "24. My Room Hub" (Prompt T5) with a persistent full-width
  warning banner right below the header/sidebar area (same copy as
  Mobile); "Find a room"/"Roommate Match" sidebar items appear dimmed.
- Comes from: logging in with a restricted account.
- Goes to: other sidebar items work normally.

7. Logout Confirmation
- A small centered modal: "Are you sure you want to log out?" buttons "Log
  out" (red) / "Cancel".
- Comes from: "Log out" on "33. Profile" (Prompt T7).
- Goes to: confirm → returns to "9. Home" (logged-out state).

8. Generic Error
- A centered error page: simple icon, error-type title, description, "Try
  again" button.
- Comes from: any page on API failure.
- Goes to: "Try again" → returns to the failed action.
```

---

## Prompt T2/7 — Room Search & Detail (4 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.

CONTEXT: Same business content as Mobile Prompt T2. On Web, the filter is
a persistent sidebar element rather than a hidden bottom sheet, so there is
no separate "Filter" screen — it's baked directly into "9".

SCREENS TO GENERATE:

9. Home / Room List
- Topbar: logo on the left, a search bar in the middle, a "Log in" button
  / account avatar on the right. Two-column layout: a FIXED LEFT SIDEBAR
  with the full filter set — price range, size, area/district, amenity
  checkboxes — always visible (not hidden behind a button). On the right:
  a grid of result cards (3 columns on a wide screen); each card contains
  exactly the same fields as the Mobile version's room cards.
- Comes from: navigating to the app's URL, or clicking the logo from any
  page.
- Goes to: clicking a card → "11. Room Detail". Changing a filter updates
  the grid immediately (no separate screen). Clicking a "Saved" icon in
  the topbar → "12. Saved Rooms".

10. (No separate Filter screen)
- Note: because the filter sidebar is always visible on Web, there is no
  screen "10" to build — do not create anything for this number.

11. Room Detail
- Two-column layout: left (~60%) has the photo gallery (carousel),
  description, amenities, a small location map if available. Right
  (~40%), STICKY while scrolling: a price card + exactly 3 constraint
  badges + the landlord-contact block (avatar, name, "Verified" tag,
  phone) + a "Contact Landlord" button (Accent, full width in this card) +
  a Save icon. Rest of the screen stays neutral in color.
- Comes from: "9" (clicking a card).
- Goes to: "Save" while logged out → modal "2. Login". "Contact Landlord"
  while logged in → opens "19. Landlord Direct Chat" (Prompt T4).

12. Saved Rooms
- A grid of cards like the home page, filtered to saved rooms; empty state
  with a simple icon + text.
- Comes from: the "Saved" icon in the topbar of "9", or the Account page.
- Goes to: clicking a card → "11. Room Detail".
```

---

## Prompt T3/7 — Roommate Match (5 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.

CONTEXT: Same content as Mobile Prompt T3. The feed becomes a multi-
column grid instead of a single scrolling column.

SCREENS TO GENERATE:

13. Match Feed
- Left sidebar: main nav (Find a room / Roommate Match / Messages / My
  Room / Account). Main content: a grid of profile cards (3-4 columns),
  each card containing exactly the same fields as the Mobile version
  (including the "Match: 87%" outlined tag, varied slightly per card).
  Topbar icons "My Profile" and "Requests".
- Comes from: the "Roommate Match" sidebar item.
- Goes to: clicking a card → "14. Roommate Profile Detail" (modal).
  "My Profile" → "15". "Requests" → "16".

14. Roommate Profile Detail
- A large modal centered on the page: photo, full description, the "Match:
  87%" tag, "Send Request" button.
- Comes from: "13".
- Goes to: sending a request → toast confirmation, modal closes.

15. Create/Edit Roommate Profile
- A two-column form (photo on the left, fields on the right), the
  "Looking for a roommate" toggle at the top. "Save" button.
- Comes from: "My Profile" icon on "13".
- Goes to: "Save" → "13".

16. Sent/Received Requests
- Two tabs, a TABLE list (avatar, name, date sent, status; on "Received":
  Accept/Decline buttons directly on the row).
- Comes from: "Requests" icon on "13".
- Goes to: "Accept" → "17".

17. Match Success
- A congratulations modal centered on the page, "Message now" button. No
  phone/Zalo shown.
- Comes from: "16" (Accept).
- Goes to: "Message now" → "22. Roommate Match Chat" (Prompt T4).
```

---

## Prompt T4/7 — Inbox/Chat (5 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.

CONTEXT: Same 3-thread-type inbox as Mobile, laid out as a classic 2-
column chat app (Gmail/Messenger style): a left column (~320px) with the
thread list, a right column showing the currently open conversation —
selecting a different thread swaps the right column's content, no page
navigation.

SCREENS TO GENERATE:

18. Inbox
- Left column: thread list (avatar, name, last message, unread badge,
  small type icon). Right column, default state: empty placeholder
  "Select a conversation to get started."
- Comes from: the "Messages" sidebar item.
- Goes to: clicking a thread → right column shows content matching
  "19/20/21/22" below.

19. Landlord Direct Chat
- Right-column content: header (landlord avatar + room context), message
  thread, input at the bottom.
- Comes from: selecting a thread on "18", or "Contact Landlord" on "11".
- Goes to: — (stays on "18" with this content shown).

20. Property Group Chat (Room)
- Right-column content: header (room name + member count), group messages
  with sender names, invoice cards as bordered blocks. IF the lease has
  ended: a "This conversation is archived" note + disabled input.
- Comes from: selecting a thread on "18", or a deep link from My Room Hub.
- Goes to: — .

21. Property Group Chat (Building)
- Similar to "20" but building-wide, no invoice cards, no archive state.
- Comes from: selecting a thread on "18".
- Goes to: — .

22. Roommate Match Chat
- Right-column content: header context "Matched via Roommate Match on
  [date]".
- Comes from: selecting a thread on "18", or automatically from "17".
- Goes to: — .
```

---

## Prompt T5/7 — My Room Hub (7 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.

CONTEXT: Same as Mobile Prompt T5. If exactly one lease, skip the list
screen and go straight to the Hub.

SCREENS TO GENERATE:

23. Lease List
- Two tabs "Active"/"Ended", a table or horizontal-card list.
- Comes from: the "My Room" sidebar item (only if 2+ leases).
- Goes to: clicking a row → "24. My Room Hub".

24. My Room Hub
- Two-column layout: left is a settings-style sub-nav (View Lease /
  Members / Invoices / Issues / Chat), right shows the selected item's
  content immediately (no separate page navigation per item). Content
  differs by lease status (Active: full menu; Ended: "(History)" labels,
  no payment button, no new-issue option, Chat archived).
- Comes from: "23" (if 2+ leases), or directly (if exactly one lease).
- Goes to: "Chat" → deep-links to "20. Property Group Chat (Room)" (Prompt
  T4). Other items show their content directly: "View Lease"→25,
  "Members"→26, "Invoices"→27, "Issues"→"30" (Prompt T6).

25. View Lease
- Right-column content of "24": read-only breakdown + signed lease file.
- Comes from/Goes to: selecting "View Lease" in "24".

26. Member List
- A table: Avatar, Full name only (NO phone, NO vehicle info — those are
  Landlord-only details).
- Comes from/Goes to: selecting "Members" in "24".

27. Invoice List
- A table: Month, Total amount, Status (dot-indicator).
- Comes from: selecting "Invoices" in "24".
- Goes to: clicking a row → "28. Invoice Detail" (modal or expanded
  right-side panel).

28. Invoice Detail
- A table-style breakdown, "Pay" button (hidden if fully paid or ended
  lease).
- Comes from: "27".
- Goes to: "Pay" → "29. Payment" (modal).

29. Payment
- Modal: exactly three channel tabs — VietQR / Cash / E-wallet
  (VNPay/MoMo, with placeholder logos + instruction text).
- Comes from: "28".
- Goes to: confirm → closes modal, "28" updates.
```

---

## Prompt T6/7 — Issues (3 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.

SCREENS TO GENERATE:

30. Room Issue List
- A table: Description, Report date, Status (dot-indicator). A "+ Report
  an issue" button top-right (only if lease Active).
- Comes from: "Issues" in "24. My Room Hub".
- Goes to: clicking a row → "31. Issue Detail Popup" (modal). "+ Report an
  issue" → "32".

31. Issue Detail Popup
- A MODAL centered on the page: description + photos, a horizontal status
  stepper, a built-in discussion thread below.
- Comes from: "30".
- Goes to: closing → "30".

32. Report an Issue
- A modal form: description textarea + a drag-and-drop/upload area (both
  camera-equivalent webcam capture and file upload allowed).
- Comes from: "30" (+ Report an issue).
- Goes to: submit → closes modal, "30" shows the new item.
```

---

## Prompt T7/7 — Account (2 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.

SCREENS TO GENERATE:

33. Profile
- A settings-page layout: avatar + name (editable) on the left, fields on
  the right (Phone/Email read-only with a lock icon). Menu: "Change
  password"/"Saved Rooms"/"Notification Settings"/"Log out".
- Comes from: the "Account" sidebar item.
- Goes to: "Notification Settings" → "34". "Log out" → "7" (Prompt T1).

34. Notification Settings
- One single toggle.
- Comes from/Goes to: "33".
```

---
---

# ZONE B — "Rentify Landlord — Web App" (55 screens, 11 prompts)

> Open a **SECOND, SEPARATE** Stitch project named exactly **"Rentify
> Landlord — Web App"**. This app serves ONLY landlords — no tenant
> content anywhere. Paste the 🎨 DESIGN SYSTEM block from the very top of
> this file at the start of every prompt below too. Fixed left sidebar
> nav: **Dashboard · Manage Properties · Issues · Chat · Settings**.

## Prompt L1/11 — Auth (7 screens — no Splash on Web)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.

CONTEXT: The authentication flow for the Landlord web app.

SCREENS TO GENERATE:

2. Login
- A form card centered on the page: Email, Password (eye icon), full-width
  "Log in" button, "Forgot password?" link, "Don't have an account? Sign
  up" line. Inline error state as on the Tenant app.
- Comes from: any gated action anywhere (modal), or the app's landing URL.
- Goes to: correct login, normal account → "9a/9b. Dashboard" (Prompt L2).
  Locked account → "6. Account Locked". "Forgot password?" → "3". "Sign
  up" → "5".

3. Forgot Password — Enter Email
- A centered card: title, description, Email input, "Send reset link"
  button; success state shown in the same card.
- Comes from: "2".
- Goes to: "Back to Login" → "2".

4. Reset Password
- A centered card: New Password + Confirm Password inputs, "Reset
  password" button.
- Comes from: the email link (simulated from "3").
- Goes to: success → "2" with a success banner.

5. Sign Up
- A centered form card: Email, Password, Confirm Password (eye icons),
  Full name, Phone. "Sign up" button. Inline validation for mismatched
  passwords.
- Comes from: "2" (sign-up link).
- Goes to: success → "9a. Dashboard — Empty State" (Prompt L2).

6. Account Locked
- A full-page block (no sidebar): lock icon, title "Your account is
  locked", description, two buttons "Contact support" and "Log out".
- Comes from: "2" when the account is detected as locked.
- Goes to: "Log out" → "7. Logout Confirmation".

7. Logout Confirmation
- A small centered modal: "Are you sure you want to log out?" buttons "Log
  out" (red) / "Cancel".
- Comes from: "Log out" on "51. Profile" (Prompt L11), or "6".
- Goes to: confirm → "2".

8. Generic Error
- A centered error page: icon, error-type title, description, "Try again"
  button.
- Comes from: any page on API failure.
- Goes to: "Try again" → returns to the failed action.
```

---

## Prompt L2/11 — Dashboard (1 screen, 2 variants)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.

CONTEXT: Fixed left sidebar: Dashboard / Manage Properties / Issues / Chat
/ Settings.

SCREENS TO GENERATE:

9a. Dashboard — Empty State
- A large hero card centered in the content area: welcome icon, title
  "Welcome to Rentify!", description "Start by adding your first
  Building/Property", "+ Add Building" button. Dimmed Revenue/Debt/Room
  Map sections below.
- Comes from: first login/sign-up, no Building yet.
- Goes to: "+ Add Building" → "11. Add Building — Step 1/3" (Prompt L3).

9b. Dashboard — Full State
- A wide dashboard layout: a full-width hero card with 3 stats at the top
  ("Monthly Revenue", "Outstanding Debt", "Occupancy Rate"); below,
  2 columns — a revenue bar chart (left, ~60%) and the Room Map grid
  (right, ~40%, or full-width below the chart if more space is needed).
  Cards may stagger slightly (only screen where this is allowed).
- Comes from: login with ≥1 approved building.
- Goes to: clicking a Room Map cell → "18. Room Detail" (Prompt L3).
  Clicking "Outstanding Debt" → "40. Debt List" (Prompt L7).
```

---

## Prompt L3/11 — Buildings & Rooms (13 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.

CONTEXT: Same as Mobile Prompt L3. The wizard stays as distinct steps
(may render as a multi-step modal or a page with a horizontal progress
bar). Utility rate configuration is a two-tier choice: type first, then
specific settings.

SCREENS TO GENERATE:

10. Building List
- A table/card grid: Name, Address, Approval status (dot), Room count.
  "+ Add Building" button top-right.
- Comes from: the "Manage Properties" sidebar item, or "9a" (CTA).
- Goes to: "+ Add Building" → "11". Clicking a row → "14. Building Detail".

11. Add Building — Step 1/3
- A modal/page with a 3-step progress bar. Name, Address, Number of
  floors inputs.
- Comes from: "10" or "9a".
- Goes to: "Continue" → "12".

12. Upload Ownership Documents — Step 2/3
- A drag-and-drop/upload area for multiple files, thumbnail preview grid.
- Comes from: "11".
- Goes to: "Continue" → "13".

13. Choose Utility Rate Type — Step 3/3
- Exactly three selectable cards: "Fixed rate", "EVN tiered", "Per-person
  flat fee", each with a short description as on Mobile. "Continue"
  button.
- Comes from: "12", or "14. Building Detail" ("Edit Utility Rates").
- Goes to: "Fixed rate" → "13a". "EVN tiered" → "13b". "Per-person flat
  fee" → "13c".

13a. Configure Fixed Rate
- Electricity/water rate inputs + optional wifi/trash/laundry fees.
  "Finish" button.
- Comes from: "13" (Fixed rate).
- Goes to: "Finish" → new building → "10"; editing existing → "14".

13b. Configure EVN Tiered Rate
- A dynamic table: consumption range (From-To kWh) + price per row, "+ Add
  tier" button, remove icon per row. Same optional fee fields below.
  "Finish" button.
- Comes from: "13" (EVN tiered).
- Goes to: "Finish" → same behavior as "13a".

13c. Configure Per-Person Flat Rate
- A single input: utility flat fee per person per month, plus the same
  optional fee fields. "Finish" button.
- Comes from: "13" (Per-person flat fee).
- Goes to: "Finish" → same behavior as "13a".

14. Building Detail
- Header + status banner as on Mobile, two-column layout if approved (info
  left, shortcuts right: "Edit Utility Rates", "Configure VietQR", "View
  Room List").
- Comes from: "10".
- Goes to: "Edit Utility Rates" → "13" (reopened). "Configure VietQR" →
  "15". "View Room List" → "16".

15. Configure Building VietQR Account
- Form: bank account/name/holder. "Save" button.
- Comes from: "14" (only if approved).
- Goes to: Save → "14".

16. Room List (Room Map for this Building)
- The Room Map grid by floor, two top buttons: "+ Add Room", "Bulk Meter
  Reading".
- Comes from: "14".
- Goes to: clicking a cell → "18". "+ Add Room" → "17". "Bulk Meter
  Reading" → "28" (Prompt L5).

17. Add New Room
- A modal form: number, size, price, rules, a "Description" textarea, a
  "Keywords" input with a "✨ Generate description with AI" button next to
  it (Description pre-filled with a sample AI-generated Vietnamese
  description by default, still editable).
- Comes from: "16".
- Goes to: Create → "16".

18. Room Detail
- Two-column layout: photo/info left, lease status/actions right. Includes
  a collapsed "Advanced" section: "Custom utility rate for this room" →
  opens room-scoped "13".
- Comes from: "16", or "9b" (Dashboard Room Map).
- Goes to: "Utility Menu" (if leased) → "19". "Create lease" (if not) →
  "20. Create Lease" (Prompt L4). "+ Report issue" → "43. Landlord Creates
  an Issue" (Prompt L8). "Advanced" → room-scoped "13".

19. Room Utility Menu
- A tab/panel inside the Room Detail page: Members / Meter Reading /
  Invoices / Chat / Move-out.
- Comes from: "18".
- Goes to: "Members"→"24" (Prompt L4). "Meter Reading"→"27" (Prompt L5).
  "Invoices"→"34" (Prompt L6). "Chat"→deep-link "50" (Prompt L10).
  "Move-out"→"44" (Prompt L9).
```

---

## Prompt L4/11 — Lease & Members (7 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.

SCREENS TO GENERATE:

20. Create Lease
- Form for the lead tenant only: full name, phone, ID number, address,
  Deposit, Rent, Start date, Term.
- Comes from: "18".
- Goes to: "Continue" → "21".

21. Choose Lease Template
- Grid of template thumbnails, radio selector, "Skip" option.
- Comes from: "20".
- Goes to: "Generate file" → "22".

22. Export Lease PDF
- Brief loading state, auto-downloads the file.
- Comes from: "21".
- Goes to: auto → "23".

23. Upload Signed Lease
- Drag-and-drop the signed file/photo.
- Comes from: "22".
- Goes to: "Confirm & Activate" → "18" (lease Active).

24. Member List
- A full table: Avatar, Full name, Phone, ID number, and a small vehicle
  icon next to members who have a vehicle registered.
- Comes from: "19".
- Goes to: "+ Add" → "25"; "Remove" menu → "26".

25. Add New Member
- Modal form: full name, phone, ID number, and a toggle "Has a vehicle
  (motorbike/car): Yes/No".
- Comes from: "24".
- Goes to: "Add" → "24".

26. Confirm Remove Member
- Confirmation dialog, no special "lead tenant" handling.
- Comes from: "24".
- Goes to: confirm → "24".
```

---

## Prompt L5/11 — Meter Reading (6 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.

CONTEXT: Mobile's camera capture becomes a browser webcam interface or
file upload on Web.

SCREENS TO GENERATE:

27. Single Meter Reading
- Choose "Capture via webcam" or "Upload a file".
- Comes from: "19".
- Goes to: → "31" (webcam) or straight to "32" (uploaded file).

28. Bulk Reading Entry
- A confirmation screen listing the rooms to be read, "Start" button.
- Comes from: a button on "16".
- Goes to: "Start" → "29".

29. Bulk Reading Flow
- A progress panel "Room 3/20", reuses "31/32", Next/Skip buttons.
- Comes from: "28".
- Goes to: list exhausted → "30".

30. Bulk Reading Summary
- List of remaining rooms with reasons, "Done" button.
- Comes from: "29".
- Goes to: "Done" → "16".

31. Webcam — Meter Photo
- A webcam preview frame + capture button, for electricity then water
  meter.
- Comes from: "27" or "29".
- Goes to: both photos captured → "32".

32. OCR Result
- Two photos + editable OCR numbers (tabular figures); "Couldn't read
  this" state if OCR fails (empty input, no fake number). "Confirm"
  button.
- Comes from: "31", or "Upload a file" on "27".
- Goes to: "Confirm" → single flow → "33" (Prompt L6); bulk flow → back to
  "29".
```

---

## Prompt L6/11 — Invoices (5 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.

SCREENS TO GENERATE:

33. Invoice Preview
- Editable breakdown table (Room rent, Electricity, Water, Other
  services), total at bottom, "Issue Invoice" button.
- Comes from: "32".
- Goes to: "Issue Invoice" → "36".

34. Issued Invoice List
- A full table by month with a derived payment state column (Unpaid / Partial / Paid / Overpaid) and an invoice lifecycle column (Draft / Issued / Void). No "Overdue" state.
- Comes from: "19".
- Goes to: unpaid row → "35"; "Confirm cash payment" button → "37".

35. Edit/Cancel Invoice
- Modal, editable breakdown + Cancel button (only when zero payments
  recorded).
- Comes from: "34".
- Goes to: Save → "34"; Cancel → confirmation → "34".

36. Issue Invoice
- Success state + the newly generated VietQR code. "Done" button.
- Comes from: "33".
- Goes to: "Done" → "34".

37. Confirm Cash Payment
- "Confirm FULL payment" button + "enter amount" option revealing an
  amount input.
- Comes from: "34".
- Goes to: confirm → "34".
```

---

## Prompt L7/11 — Billing Cycle & Debt (3 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.

SCREENS TO GENERATE:

38. Billing Cycle & Debt Scan Settings
- Scope selector: Profile/Building/Room. "Continue" button.
- Comes from: "51. Profile" (Prompt L11).
- Goes to: "Continue" → "39".

39. Due Date Settings
- Billing date / due period / reminder timing inputs. "Save" button.
- Comes from: "38".
- Goes to: Save → "38".

40. Debt List
- A strict table: Room/Building, Amount still owed, Days since the expected payment day. Column header must NOT say "Days overdue" — there is no overdue state in this system.
- Comes from: "9b" (Dashboard).
- Goes to: a row → "34" (Prompt L6).
```

---

## Prompt L8/11 — Issues (3 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.

SCREENS TO GENERATE:

41. Issues Tab
- A table with a "Building — Room" column always visible, description,
  status dot, filter chips.
- Comes from: the "Issues" sidebar item.
- Goes to: a row → "42".

42. Issue Detail Popup
- Modal: header Building-Room-Reporter, status control, "View in Room
  Chat" button (deep-link, NO embedded discussion thread here).
- Comes from: "41".
- Goes to: close → "41"; Chat button → "50" (Prompt L10).

43. Landlord Creates an Issue
- Modal form, room context auto-attached.
- Comes from: "18".
- Goes to: Submit → "41".
```

---

## Prompt L9/11 — Move-out / Settlement (5 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.

SCREENS TO GENERATE:

44. Final Meter Reading
- Reuses "31/32". Header retitled "Final meter reading before move-out."
- Comes from: "19".
- Goes to: confirmed → "45".

45. Final Settlement Invoice
- Free-text rent input + suggested pro-rated hint below it. "Continue"
  button.
- Comes from: "44".
- Goes to: "Continue" → "46".

46. Deposit Settlement
- Deduction input + reason, auto-calculated refund shown below. "Continue"
  button.
- Comes from: "45".
- Goes to: "Continue" → "47".

47. Confirm Move-out Complete
- Summary + confirm button.
- Comes from: "46".
- Goes to: confirm → "48".

48. Pending Cleanup Status
- Badge + "Mark room ready" button.
- Comes from: "47".
- Goes to: confirm → "16" (room Vacant).
```

---

## Prompt L10/11 — Chat Inbox (2 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.

CONTEXT: Same 2-column chat layout as Prompt T4/L... (Tenant Zone A).

SCREENS TO GENERATE:

49. Inbox (Chat item)
- Left column thread list, right column empty state by default.
- Comes from: the "Chat" sidebar item.
- Goes to: selecting a thread → shows content of "50".

50. Chat Thread Detail
- Right-column content, shared across all 3 thread types (direct chat /
  room group / building-wide).
- Comes from: "49", or a deep link from "19"/"42".
- Goes to: — .
```

---

## Prompt L11/11 — Settings (2 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.

SCREENS TO GENERATE:

51. Profile
- Settings page: avatar/name/phone (no bank info — that's at building
  level). Menu: "Billing Cycle Settings", "Notification Settings", "Log
  out".
- Comes from: the "Settings" sidebar item.
- Goes to: "Billing Cycle Settings" → "38" (Prompt L7). "Notification
  Settings" → "52". "Log out" → "7" (Prompt L1).

52. Notification Settings
- One single toggle.
- Comes from: "51".
- Goes to: — .
```

---

## ✅ DONE — Zone A (34 screens) + Zone B (55 screens) so far

# ZONE C — "Rentify Admin — Web App" (15 screens, 5 prompts)

> Open a **THIRD, SEPARATE** Stitch project named exactly **"Rentify Admin
> — Web App"**. This is a fully independent back-office console for the
> platform's single Admin account — it shares NO UI, sidebar, or styling
> instance with the Tenant or Landlord apps (only the same design tokens,
> pasted fresh below). Fixed left sidebar: **Dashboard · Users · Property
> Approval · Audit Logs · Log out**.

## Prompt AD1/5 — Auth (5 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.

CONTEXT: The Admin account is a single seeded account (not self-
registered) — there is no Sign Up screen anywhere in this app.

SCREENS TO GENERATE:

1. Login
- A form card centered on the page: Email input, Password input (eye
  icon), full-width "Log in" button, "Forgot password?" link. There is NO
  "Sign up" link anywhere on this screen (Admin accounts are not self-
  registered). Inline error state: red outline + "Incorrect email or
  password" text.
- Comes from: navigating directly to this app's URL (never linked from any
  public page).
- Goes to: correct login → "6. Admin Dashboard" (Prompt AD2). "Forgot
  password?" → "2".

2. Forgot Password — Enter Email
- A centered card: title, description, Email input, "Send reset link"
  button; success state shown in the same card.
- Comes from: "1".
- Goes to: "Back to Login" → "1".

3. Reset Password
- A centered card: New Password + Confirm Password inputs, "Reset
  password" button.
- Comes from: the email link (simulated from "2").
- Goes to: success → "1" with a success banner.

4. Logout Confirmation
- A small centered modal: "Are you sure you want to log out?" buttons "Log
  out" (red) / "Cancel".
- Comes from: the "Log out" sidebar item.
- Goes to: confirm → "1".

5. Generic Error
- A centered error page: icon, error-type title, description, "Try again"
  button.
- Comes from: any page on API failure.
- Goes to: "Try again" → returns to the failed action.
```

---

## Prompt AD2/5 — Dashboard (1 screen)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.

SCREENS TO GENERATE:

6. Admin Dashboard
- Exactly: stat cards only (NO charts, unlike the Landlord Dashboard) —
  total Landlords, total Tenants, number of properties pending approval
  (an Accent-colored badge if >0), and a short recent-activity list. Do
  not add anything else.
- Comes from: logging in as Admin.
- Goes to: clicking the "pending approval" card → "10. Property Approval
  Queue" (Prompt AD4).
```

---

## Prompt AD3/5 — User Management (4 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.

SCREENS TO GENERATE:

7. User List
- A table: Name, Email, Phone, Role (Landlord/Tenant), Status (dot-
  indicator: Active/Locked). Filter by role/status, a search box above the
  table.
- Comes from: the "Users" sidebar item.
- Goes to: clicking a row → "8. User Detail".

8. User Detail
- Basic info; if Landlord → shows their owned properties; if Tenant →
  shows their current lease. A "Lock account" button (if active) or
  "Unlock" (if locked).
- Comes from: "7".
- Goes to: "Lock account" → "9a". "Unlock" → "9b".

9a. Lock Account
- A modal: "Lock [Name]'s account?" + a MANDATORY reason textarea.
  "Confirm lock" button (red).
- Comes from: "8".
- Goes to: confirm → "8", status becomes "Locked", logged to the Audit
  Log.

9b. Unlock Account
- A modal: "Unlock [Name]'s account?" IF a lease is currently Suspended
  (due to a prior Landlord lockout): adds a choice "Restore lease" or
  "Cancel lease".
- Comes from: "8".
- Goes to: confirm → "8", status becomes "Active".
```

---

## Prompt AD4/5 — Property Approval (3 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.

SCREENS TO GENERATE:

10. Property Approval Queue
- A table: Property name, Address, Owning Landlord, Submission date.
- Comes from: the "Property Approval" sidebar item, or the card on "6".
- Goes to: clicking a row → "11. Property Approval Detail".

11. Property Approval Detail
- Full property info + legal-document images (zoomable). Two large
  buttons: "Approve" (green) and "Reject" (red, outline).
- Comes from: "10".
- Goes to: "Approve" → "10" (property becomes "Approved", Landlord
  notified). "Reject" → "12".

12. Reject Property
- A modal: a MANDATORY reason textarea. "Confirm rejection" button.
- Comes from: "11".
- Goes to: confirm → "10", property becomes "Rejected", Landlord notified
  with the reason.
```

---

## Prompt AD5/5 — Audit Logs (2 screens)

```
GROUNDING: Calibrate against real professional products — Stripe's
dashboard, Linear (linear.app), Mercury — NOT generic "AI UI kit" defaults.
Color is almost entirely absent except where it carries real meaning (a
status, a data point, a single primary action). Dense information is shown
as real tables and aligned lists, not everything stuffed into its own
floating rounded card. Numbers look like real data (specific, slightly
irregular values, e.g. "$4,317" not "$5,000"). Hierarchy comes from type
size/weight and spacing, not from wrapping things in boxes or decorative
labels. Icons are small and functional, never decorative illustrations.
This is a FULL-COLOR request (not a grayscale wireframe).

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
- No code-style naming visible in the UI
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
- Background: #F8FBFE (very light pastel blue tint, near-white)
- Primary text: #142A4C (deep navy, not pure black)
- Secondary/muted text: #5C7290
- Border/divider: #D7E3F2
- Primary accent #1E6FD9 — use SPARINGLY: only the single most important
  card on a screen (hero/highlight card), the main CTA button, progress
  bars, and the active sidebar-nav item. Do NOT apply it to every
  button/icon.
- Semantic colors (only for their specific meaning, never decorative):
  - Paid / success: #16A34A
  - Overdue / warning: #DC2626 (a real assertive red — never softened to
    orange/amber)
  - Pending / neutral: #94A3B8
- Typography: ONE typeface only — "Inter" for everything (headings
  semibold/bold, body regular/medium). Numeric data uses tabular figures.
- Shape & elevation (CONTEXTUAL): Hero/highlight card = 24px radius + soft
  shadow tinted toward the background blue, rgba(30,111,217,0.10). Regular
  list/content cards = 14px radius, flat, NO shadow, 1px solid border
  (#D7E3F2) only. Buttons = 12px radius.
- Badges & tags (MANDATORY on every screen with any status or descriptive
  label): live status (room availability, verification, payment/issue
  status) = a small 7px filled dot in the semantic color + plain navy
  text, NO fill, NO pill. Fixed descriptive attributes (Female Only, Max 3
  People, No Pets) = a rectangular outlined tag, 7px radius, 1px border
  (#D7E3F2), no fill, navy text — same style regardless of whether the
  attribute reads positive or negative. NEVER use a filled/colored pill
  badge anywhere.
- Layout: on the Dashboard, cards may overlap/stagger slightly for depth;
  list/data screens (invoices, members, search results, audit logs) use a
  strict aligned grid or a REAL TABLE — on Web, prefer real tables with
  column headers and sorting over cards for any list with several
  attributes.
- Logo (temporary placeholder): a simple stylized roofline-monogram icon in
  #1E6FD9, placed top-left in the sidebar/topbar. Placeholder only — can be
  swapped later via a short Edit prompt.

LANGUAGE (mandatory): All visible on-screen text — labels, buttons,
headings, placeholders, input labels, tags, badges, menu items, empty-
state text, everything a user actually reads on the screen — must be
written in natural, professional Vietnamese. Everything in this document is
written in English purely for internal documentation clarity; when
generating the actual screen, translate the MEANING of every quoted example
string into idiomatic Vietnamese (do not leave any English text on screen).
Keep brand/proper nouns as-is ("Rentify", "VietQR").

Frame size: desktop web, 1440px viewport (responsive down to ~1024px)
unless noted otherwise.

WEB LAYOUT CONVENTIONS:
- Tenant & Landlord apps: a fixed left sidebar (~240px) with the logo +
  main nav (replaces a mobile bottom nav); content fills the rest, using
  two-column layouts (list on the left + detail/preview on the right) for
  screens that combine a list with a quick view.
- Admin console: its own separate fixed sidebar — a completely independent
  project, not sharing any UI with the Tenant/Landlord apps.
- Mobile bottom sheets → become centered MODALS/DIALOGS on Web.
- Mobile camera capture (meter photos, documents) → becomes a BROWSER
  WEBCAM interface (preview frame + capture button) or drag-and-drop file
  upload, always offering both a "Capture via webcam" and an "Upload a
  file" option.

SCREENS TO GENERATE:

13. Audit Logs
- A table: Timestamp, Event type, Target/Object, Actor. Filter by event
  type/date range above the table.
- Comes from: the "Audit Logs" sidebar item.
- Goes to: clicking a row → "14. Audit Log Detail Popup".

14. Audit Log Detail Popup
- A MODAL (consistent with the issue-popup pattern in the other apps):
  shows the before/after data as a 2-column comparison.
- Comes from: "13".
- Goes to: closing → "13".
```

---

## ✅ DONE — Zone A (34) + Zone B (55) + Zone C (15) = 104 screens total for the Web file (3 separate apps)
