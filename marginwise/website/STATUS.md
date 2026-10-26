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
