# marginwise.in status, 26 Oct 2026

## Live now (published 22 Oct, commit 6cffd58)
- Booking with Google Calendar and Meet.
- Calculators (10).
- Prices by market (AUD, USD, GBP, INR).
- Free teardown lead form and the team Leads tab.
- India market.

## Built in Lovable but not live (preview has build errors), about 15 credits used 25-26 Oct
| Request | Commit | Done | Left |
|---|---|---|---|
| Site fixes from the audit | 99c6143 | Privacy and terms pages, shared header and footer on every page, booking link fixes, metadata, sitemap (6 URLs), llms.txt, self-hosted fonts, security headers in preview, 58 tests passing, no broken links | 16 serious accessibility findings; type check stale |
| Full customer-friendly site | 20567b2 | Content config, templates, the 5 service pages, AI solution pages, industry pages, /au /us /uk /in, how-we-work, about, refunds, service delivery, "Where should I start?" guide, new nav and footer | Build errors in content-pages.tsx; free store check, home page reorder, tests, Lighthouse and accessibility checks |
| Booking: new slots and one booking per slot | 50d002d | Slots 6:30-7:30 AM and 6:00-9:30 PM IST, Mon-Sat; unique slot rule in the database (5 old duplicate bookings marked cancelled, nothing deleted); slot reserved before the calendar invite; taken-slots function; "Booked" in the picker; hours copy updated | Test file still imports nextWeekdays (type error); .no-slots style; tests; real test booking and refusal check |

## Not sent yet (Lovable out of credits)
1. The finish-up message (fix the build, finish booking, accessibility, store check, tests). Text: in this repo's chat log; summary in this file.
2. Logo (option B): marginwise/brand/logo/README.md. The files have to be uploaded again.
3. Positioning update: marginwise/website/lovable-positioning-prompt.md.

## Publish rule
Publish only after the build is clean, tests pass and the booking double-check passes.

## Update 27 Oct 2026
- Fix round 1 done (commit ab8c2ed, 2.5 credits): type check clean, build passes, 59+ tests, new booking-slots tests. The database refuses a second active booking for the same slot (unique index booking_requests_one_active_per_slot, verified), and cancelling a booking frees its slot. A real test booking created a Calendar invite with a Meet link and showed the slot as "Booked"; the calendar event and the database row have been deleted.
- Incident: the migration made slot_start NOT NULL, so the live 22 Oct code (which doesn't send slot_start) would have failed every booking from 25 Oct. Fixed on 27 Oct by dropping NOT NULL. The live form works again, but the live site has no double-booking protection until the new build is published.
- Still left: 16 serious accessibility findings, final test run; then the build items (free store check, home page order, Lighthouse), the logo and positioning. Lovable is out of credits; the next message to send is the accessibility fix (see chat).

## Update 29 Oct 2026
- Fix stage complete in Lovable (commit 7ba3d69, not published): type check clean, build OK, 70/70 tests across 9 files, 0 serious or critical axe findings (11 pages x 375/1280 px x light/dark), no horizontal scroll. Booking verified end to end: second booking for the same slot refused, test row and calendar event deleted, slot free again.
- Next, in order: build items (free store check, home page order, Lighthouse); logo option B (re-upload files); positioning prompt; then Desk tiers, currency on every page and the persona entry from marginwise/strategy/global-growth-plan-2026-10.md once prices are approved. Publish after that build passes tests and the booking check.
- 29 Oct: sent to Lovable, in order: (1) store check, home order, Lighthouse (running); (2) logo option B with 9 files (queued); (3) positioning brief (queued). Nothing published.
- 29 Oct 00:55 UTC: store check build half done (commit db6e337, 4.6 credits): URL guard, 11 checks, scoring, server fetch with rate limit and redirect checks, results UI on /free-store-check. Not done: hero URL box, home order, fixture tests, sitemap/llms.txt, Lighthouse, axe, full test run. Workspace then ran out of credits; logo and positioning messages are queued but paused. Continuation prompt: lovable-build-continue-prompt.md.
- 30 Oct: logo done (commit 1dd051d, 3.4 credits): files used unchanged, header, footer, favicons, manifest, share image, email headers, Organization logo; 70 tests pass; header axe clean at 375/1280 light/dark. Positioning done (commit 0c3ee32, 1.6 credits): hero line, market-aware size range, "What's different here", AI block, source line, /working-with-us with 4 FAQs, Not a fit on /pricing, llms.txt and sitemap; 74 tests pass; type check and axe not yet run. Out of credits again. Next message: lovable-build-continue-prompt.md (updated). Nothing published.
- 31 Oct 00:16 UTC: sent (1) store check build continuation (running, umsg_01m67n0rnteebbw17mc10c6mr4) and (2) Margin Check phase 1 (queued, umsg_01m67n17hkfxgbh17gtj6yndj2). Phase 1 falls back to "Couldn't tell" for speed until PAGESPEED_API_KEY is added. Nothing published.
- 31 Oct 01:08 UTC: build continuation done (commit b54e00b, 5 credits). Hero URL box works (shopify.com scored 88), home order as specified, 25 new store-check tests, 99 tests pass in 11 files, type check and build clean, axe clean on /, /pricing, /free-store-check, /working-with-us at 375/1280 light/dark, JSON-LD parses, llms.txt now lists every page. Not done: mobile LCP (live 3.3 s, preview 3.1 s, target 2.5 s; Lighthouse live 82/100/100/100), real double-booking check, re-run of link check after anchor fix. Out of credits again: Margin Check phase 1 is queued but paused. Next after it: lovable-speed-booking-prompt.md. Nothing published.
