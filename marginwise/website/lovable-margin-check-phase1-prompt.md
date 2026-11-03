# Lovable prompt: Margin Check, phase 1 (30 Oct 2026)

Send after the store-check build continuation (lovable-build-continue-prompt.md) has finished. Source: marginwise/strategy/lead-magnet-research-2026-10-30.md. Text below is sent as is.

```
Margin Check, phase 1. Turn the free store check into a check people trust. Keep the URL guard, rate limit, booking, prices by market, logo, positioning and every existing test working. No invented results. Do not publish.

1. NAME AND COPY
Rename the visible tool to "Free Margin Check" (keep the /free-store-check route and add /margin-check as an alias). Line: "See what your store's pages are telling shoppers, in 60 seconds. No signup."

2. "I'M A..." TAP (before the URL box, optional, one tap)
Founder, Ecommerce manager, Ops or finance, Growth lead, IT lead, Trades or service business. Remember it with the result. Support ?persona= in the URL. Order and wording of findings follow the persona; nothing is hidden.

3. MEASURED SPEED
Replace the server response-time check with Google PageSpeed Insights API (mobile strategy): LCP, CLS and INP, plus Chrome UX field data when Google returns it. Use a server-side API key secret (PAGESPEED_API_KEY). If the API fails or times out (15 s), show "couldn't tell" instead of a score. Keep server response time as a minor, secondary line.

4. MARKET-AWARE CHECKS
Use the visitor's market (existing resolvePricingMarket):
- AU: surcharge text check stays; BNPL check stays.
- US and UK: BNPL check stays; no surcharge check.
- India: no BNPL check. Add: COD mentioned; prepaid incentive mentioned (e.g. "prepaid", "extra off on prepaid"); WhatsApp contact link (wa.me or api.whatsapp.com); prices in INR.
The surcharge detail must say: "The page mentions a card surcharge. From 1 October 2026, Australian businesses can't surcharge Visa, Mastercard or eftpos payments (RBA). Check what applies to you with your adviser."

5. PLATFORM IS INFORMATION
Detect platform: Shopify (and Plus hints), Magento 2 or Adobe Commerce (Magento_ or mage/ asset paths, X-Magento headers), WooCommerce, BigCommerce, Salesforce Commerce Cloud, Wix, Squarespace. Show it as information, never a penalty, and never lower the score. If Magento is found, add: "Adobe Commerce on Cloud switches off unsupported versions from 1 June 2027. Ask us about a migration scope."

6. EVIDENCE, CONFIDENCE AND WHO FIXES IT
Every finding gets:
- evidence: the page URL and a short snippet or measured value
- confidence: "Measured", "Likely" or "Couldn't tell"
- who fixes it: "You (about 10 minutes)", "A developer" or "Marginwise"
Checks that couldn't be read never count against the score. Show a short "How this check works" note: public pages only, nothing stored unless you ask.

7. RESULT GOES WITH THE TEARDOWN
When the visitor clicks "Get the free 2-minute video teardown", pre-fill the lead form with the URL and attach the check summary (score, persona, market, failed and warned check ids) to the lead row in a new nullable JSON column store_check_summary. Show it in the team Leads tab. The visitor sees a line: "We'll attach this check to your request so we start with context."

8. FUNNEL EVENTS (no store URL, no personal data)
Log anonymous events to a new table funnel_events (id, created_at, event, persona, market, score_band, utm_source, utm_medium, utm_campaign, ref): check_started, check_completed, check_failed, teardown_clicked, teardown_submitted, book_clicked. Insert-only for visitors via a server function; the team can read. Add a small "Margin Check funnel" panel to the team area with counts for the last 7 and 30 days by persona and market. Support ?ref= (partner code) and carry it into events and the lead row (new nullable column ref).

9. "NOT A FIT" ON /working-with-us if it isn't there yet.

10. TESTS AND CHECKS
Unit tests with saved HTML fixtures for: India checks, platform detection (Shopify, Magento, WooCommerce), persona ordering, "couldn't tell" never lowering the score, surcharge wording. Mock the PageSpeed API in tests. Type check clean, build OK, full suite passing. axe on /free-store-check at 375px and 1280px, light and dark: no serious or critical findings, no horizontal scroll.

Report files changed, new tables and columns with their RLS policies, test results and axe results. Do not publish.
```

Before sending: create a PageSpeed Insights API key in Google Cloud (APIs and Services, enable PageSpeed Insights API, create an API key restricted to that API) and add it in Lovable as the secret PAGESPEED_API_KEY.
