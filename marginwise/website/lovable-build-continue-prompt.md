# Lovable prompt: finish the store check build and verify (updated 30 Oct 2026)

Logo (commit 1dd051d) and positioning (commit 0c3ee32) are done. Send this when credits are added. Text below is sent as is.

```
Thanks, logo and positioning look right. Now finish the remaining items from the store check request, then verify everything. Keep the logo, positioning, booking (one booking per slot), prices by market, lead form, calculators, team area and emails working. Do not publish.

1. Home hero store URL box posting to /free-store-check?url=..., which runs the check on load.
2. Home page order: hero with URL box -> "Where should I start?" guide -> the 5 services -> "What's different here" -> facts bar with the source line -> Where revenue leaks -> pricing -> AI solutions block -> calculators teaser -> teardown form -> how we work -> team -> FAQ -> booking. Scannable on a phone.
3. Unit tests for every store check with saved HTML fixtures, and for the URL guard (rejects http, localhost, 10.x, 127.x, 169.254.x, 172.16-31.x, 192.168.x, internal hostnames).
4. Add the "Not a fit" box to /working-with-us if it isn't there. sitemap.xml and llms.txt cover every public page, including /free-store-check and /working-with-us.
5. Quality:
- Mobile Lighthouse on the home page: Largest Contentful Paint under 2.5 s; report the four scores and fix the main issues.
- axe on /, /pricing, /free-store-check and /working-with-us at 375px and 1280px, light and dark: no serious or critical findings, no horizontal scroll.
- Every internal link resolves; every JSON-LD block parses.
- Type check clean, build OK, full test suite passing.
- One real booking check: a second booking for the same slot is refused; then delete the test booking row and its calendar event.

Report files changed, test results, Lighthouse scores and axe results. Do not publish.
```
