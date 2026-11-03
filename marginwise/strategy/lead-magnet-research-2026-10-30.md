# Free store check: user-side gaps, personas and the plan to make it the main lead magnet (30 Oct 2026)

Inputs:
- the store check code as built in Lovable (commit 0c3ee32: `store-check.ts`, `store-check.tsx`, `/free-store-check`)
- 6 competing free audit tools and the merchant feedback threads about them (Shopify Community, Aug-Oct 2026)
- the 7 personas from the global growth plan, plus 2 added here

Competitor claims are their own. Numbers marked "assumption" are planning targets, not benchmarks.

## 1. The finding in one paragraph
A free home-page audit is no longer a lead magnet on its own. At least six free Shopify audit tools launched in 2026; most are free, need no signup and check more than ours (Core Web Vitals from Google PageSpeed, product pages, conversion elements, AI visibility). Ours checks one page with 11 technical tests, scores everything the same way for every visitor, and says nothing about money, even though the brand promise is "profit-first". Merchants in the feedback threads say the same thing: they don't want a score, they want 3 to 5 ranked fixes with evidence, the likely impact, and who has to do the fix. The opening for Marginwise is a **Margin Check**: the only free check that answers "what is this costing me, in my currency" and changes its checks for who you are and where you sell.

## 2. What competitors offer (free)

| Tool | Pages | What it checks | Gate | What stands out |
|---|---|---|---|---|
| Zib Digital (AU agency) | Up to 10 | 25 checks in 7 categories, SEO and AI-search readiness, plus a "senior strategist read" and a sample social ad | URL, work email and phone | Speed (30 s) and the sample ad |
| Golden Digital | Home, product, collection | 6 categories: conversion, brand, SEO, UX/speed, email retention, paid-ad readiness; evidence per finding; "Inferred" labels | Email required | Report link by email, "My audits" history, linked calculators |
| ExtensionsMarket (Shopify Partner) | Home | PageSpeed Core Web Vitals, SEO, schema, script bloat, conversion elements | None | Ranks by business impact; findings marked "measured" or "suggestion" |
| Eastside Co (UK agency) | Crawl | SEO health score | Form | SEO only |
| Dripshipper | Home | Trust and conversion review | None | 60 seconds |
| Auditify / Solkendo / Summi | Varies | CRO, speed, AI visibility, PDF download | Mostly none | AI-visibility score out of 100 |

**What merchants asked for** (Shopify Community threads):
- **Prioritised, few fixes:** 3 to 5 ranked fixes with likely impact, not an exhaustive list or a bare score.
- **Evidence:** proof for each finding (page, snippet, screenshot) and a plain "why it matters".
- **No false positives:** they destroy trust. Say "couldn't tell" rather than guess.
- **Who does the fix:** separate "you can fix this" from "needs a developer".
- **Re-check after fixing:** see what improved.
- **Shopify-specific checks:** theme or app bloat, image formats, AI shopping visibility.

**Agency side** (r/agency): blanket "free audit" offers are ignored. What works is a specific observation that shows you actually looked at their business.

## 3. Gaps in the current check, seen from the user's side

| # | Gap | Why it matters to the user | Severity |
|---|---|---|---|
| 1 | No money anywhere. The score is technical. | The brand promise is profit; the check never says what a problem costs. Same as every free tool. | High |
| 2 | Home page only | Most buying problems sit on the product page, cart and policies (delivery, returns, price, reviews near the buy button). | High |
| 3 | "Speed" is server response time from our server, not what a shopper sees | Can show a fast result for a slow store, or the other way round. A false reading in the first finding costs trust. | High |
| 4 | Same checks and wording for every visitor | An Indian founder is told to add Afterpay; a trades business gets Shopify advice; a Magento CTO is marked down for "not Shopify". | High |
| 5 | "Shopify detected" scores as a warning when absent | It penalises P6, the persona with the biggest projects (Magento migrations). | Medium |
| 6 | No evidence or confidence on findings | Merchants say false positives make them dismiss the whole report. | Medium |
| 7 | Nothing to keep or share | No report link, no email copy, no re-check. The visitor leaves with nothing and we get no second touch. | High |
| 8 | Result is not attached to the teardown request | The team gets a URL but not what the check found; the teardown starts from zero. | Medium |
| 9 | No analytics on the funnel | Results aren't stored (correctly), but no events either, so we can't see checks run, teardowns asked for, or which persona converts. | High |
| 10 | Ops, finance and trades problems are invisible from a home page | P3 and P4 get nothing relevant, though AI agents are our clearest differentiator. | Medium |
| 11 | Fix text is generic ("Add structured data") | No "who fixes it" label and no time estimate. | Low |
| 12 | Free checks compete with 6+ no-signup tools | Without a reason to choose ours, it gets no traffic. | High |

**Site-wide gaps** (from earlier audits; still true):
- **No proof yet:** no case studies or testimonials. A sample report and a sample teardown video are the fastest stand-ins.
- **Few Australian call slots:** 3 a day (Sydney lunchtime only), for the priority market.
- **Stale live site:** it is still the 22 Oct build, with no double-booking protection, no store check and no positioning.

## 4. Personas
P1 to P7 come from the global plan, sharpened here around what each needs from a free check. P8 and P0 are new.

| # | Persona | Region and size | Trigger that brings them | What the check must answer for them | Best next step after the check |
|---|---|---|---|---|---|
| P1 | Founder-operator | AU, A$2-10M, Shopify, Klaviyo, Xero, Afterpay | Ad costs rising, profit flat; surcharge ban from 1 Oct 2026 | "Are my ads making money after product cost, fees and returns? Is my surcharge text gone?" | Profit-after-ads calculator with their numbers, then Margin Audit |
| P2 | Ecommerce manager | AU, A$10-50M, Shopify Plus | Conversion target, mobile checkout drop | "Which 3 product page and cart fixes first, with evidence I can show my boss?" | Teardown video, then CRO page rebuild + A/B |
| P3 | Ops or finance manager | AU, A$15-50M, Cin7 or NetSuite, Xero or MYOB | Month-end takes a week; failed syncs fixed by hand | "How many hours a month do we lose, and which can an AI agent take?" (can't be read from a website) | 6-question ops quiz, then AI scoping session |
| P4 | Trades or home-services owner | AU, A$1-5M, ServiceM8, Xero | Missed calls, few Google reviews | "How many jobs am I losing to missed calls and a weak Google profile?" | Missed-call calculator, then AI receptionist (A$290/mo) |
| P5 | Head of growth | US, US$10-50M DTC, Shopify Plus | AI answers naming competitors; rising CAC | "Can ChatGPT, Perplexity and Google AI read and recommend my products?" | AI Visibility Snapshot ($750) |
| P6 | CTO or IT lead | UK, £10-40M, Magento | Adobe Commerce unsupported versions switched off from 1 June 2027 | "What platform and version am I on, how big is the migration, will I lose rankings?" | Migration scoping call, then sprint |
| P7 | D2C founder | India, ₹10-100 crore, Shopify, Razorpay, Shiprocket | High RTO on COD orders; marketplace dependence | "How much am I losing to cash-on-delivery returns, and does my store push prepaid?" | RTO calculator, then performance marketing with RTO focus |
| P8 (new) | Referral partner: ecommerce accountant, app developer, small agency | AU first | Clients ask them for growth help they don't offer | "Can I give clients a useful free check under my name, and get credit for referrals?" | Partner link with referral tracking (10-15% fee) |
| P0 (anti-persona) | Pre-revenue or hobby store | Any | Wants a free fix list | Serve them well with self-fix guidance; don't spend team time on teardowns | Self-fix guide and newsletter only |

**Indian RTO context for P7:** Indian D2C brands typically see 20-35% RTO, and 40%+ in fashion (ClickPost 2026). The Shipway figure of 26% on COD orders is already cited on the site.

## 5. The redesign: from "store check" to Margin Check

**Positioning line:** "Free Margin Check. See what your store is costing you, in your currency, in 60 seconds. No signup."

**Flow**
1. **Inputs:**
   - Store URL plus one tap on "I'm a...": founder, ecommerce manager, ops or finance, growth lead, IT lead, trades owner.
   - Market comes from the visitor's location.
   - Optional: monthly online revenue band, which turns findings into money.
2. **Crawl:**
   - **Shopify stores:** home page, one product page (auto-found from the sitemap or the store's public product feed, `/products.json`), the cart page, the shipping and returns policy pages, robots.txt, sitemap.xml and llms.txt.
   - **Speed:** Google PageSpeed Insights API for real mobile LCP and CLS, plus field data where Google has it.
3. **Results, above the fold:**
   - "What this is likely costing you": a range in local currency, only from sourced ratios applied to their own revenue band, labelled as a planning scenario. Example: speed, using 0.1 s faster mobile = 8.4% more retail conversions (Deloitte and Google 2020).
   - With no revenue band, show the 3 fixes without money.
4. **Each finding:**
   - **Evidence:** page and snippet.
   - **Confidence:** "measured", "likely" or "couldn't tell".
   - **Why it matters:** one line.
   - **Who fixes it:** "you, 10 minutes", "a developer" or "us".
   - **Persona fit:** the finding only appears if it is relevant to the persona and market chosen.
5. **Keep it:**
   - "Email me this report and re-check in 30 days" (optional, consented). This is the main lead capture, offered after value is shown, never before.
   - The report gets a private link. A re-check compares against the last result.
6. **Next step:** depends on persona and score (see section 4). The teardown request carries the check result, so the team starts with context.

**Checks by persona** (all run, but ordering and wording follow the persona)

| Module | Checks | Main persona |
|---|---|---|
| Profit and ads readiness | Meta Pixel and Conversions API hints, GA4, consent banner, card surcharge text (AU), ad landing basics (price and delivery above the fold on mobile), plus a link to the profit-after-ads calculator pre-filled from the revenue band | P1 |
| Product page and cart | Price, delivery estimate and returns near Add to cart; reviews; BNPL shown on the product page (AU, US, UK only); sticky mobile Add to cart; image weight and format (WebP or AVIF); free-shipping threshold message; surprise-cost wording | P2 |
| Speed (measured) | PageSpeed mobile LCP, CLS, INP; third-party script count; app bloat | P2, P5 |
| AI and search visibility | AI crawlers in robots.txt, llms.txt, Product schema completeness (price, availability, GTIN, brand, reviews), Organization schema, sitemap health | P5 |
| Platform and migration | Platform and version detection (Shopify, Shopify Plus hints, Magento 2 or Adobe Commerce, WooCommerce, BigCommerce, Salesforce Commerce); URL count from the sitemap as a migration-size signal; the June 2027 Adobe date when Magento is found. Platform is information, never a penalty | P6 |
| India checkout | COD visible, prepaid incentive, WhatsApp contact, checkout provider hints (GoKwik, Shiprocket, Razorpay Magic), returns policy clarity, INR pricing; then the RTO calculator | P7 |
| Local service | Click-to-call link, after-hours booking, LocalBusiness schema, review widget, service-area pages; then the missed-call calculator | P4 |
| Ops leak quiz (no crawl) | 6 questions: orders a day, failed syncs a week, hours on payout matching, support tickets a day, after-hours enquiries, systems used. Output: hours a month and cost in local currency, and the AI agent that fits | P3 |

**Rules**
- Nothing is stored unless the visitor asks for the report by email or requests a teardown.
- Anonymous funnel events are always logged, without the URL, so we can measure the funnel.
- Every money figure links to its source and says "planning scenario".
- No score is shown for checks we couldn't read.

## 6. How the magnet brings leads (distribution)

| Channel | How | Persona |
|---|---|---|
| Instagram and Meta ads to /au | "Comment CHECK" and story link stickers point to the check with `?market=au&persona=founder`. The ad creatives already end in a teardown offer; switch them to the instant check | P1, P2 |
| Trigger outreach | Run the check ourselves on the 150-store AU list. The first email quotes one real finding from their store ("your product page shows a 1.5% card surcharge line"), which is the specific observation r/agency says works. Link to their saved report | P1, P2 |
| Referral partners | Partner link `?ref=partner-name`: their clients run the check, and the partner is credited if a project follows. A one-page partner kit | P8 |
| Search pages, one per problem | "Is my Shopify store blocking ChatGPT?", "Australian card surcharge checker", "Shopify RTO calculator India", "Magento end of support checker". Each runs one module of the check | P5, P1, P7, P6 |
| Data story | Anonymous totals from consented checks, e.g. "Share of Australian Shopify stores still showing surcharge text in November 2026". For the Add To Cart podcast pitch, LinkedIn and PR. Publish only with a sample size and method | All |
| Monthly re-check email | Opt-in only. "3 things changed on your store this month." Keeps the brand present until they're ready to buy | All |
| Shopify Community and r/shopify | Post the data story, not the tool link. The forums are already full of tool launches | All |

## 7. Measuring it
Events: `check_started`, `check_completed` (with persona, market and score band), `report_emailed`, `recheck_opt_in`, `teardown_requested`, `call_booked`, `partner_ref`. Each carries UTM source.

**First-90-day targets (assumptions):**
- 60% of checks started finish
- 15% of finished checks ask for the emailed report
- 25% of those request a teardown
- 30% of teardowns book a call

**Review:** weekly. Drop modules nobody reads.

## 8. Build plan (Lovable), in phases
- **Phase 1 (fixes the trust problems):**
  1. PageSpeed API speed in place of server time.
  2. Platform as information, not a penalty.
  3. Market-aware checks (no BNPL advice in India, COD checks instead).
  4. Evidence and confidence per finding.
  5. "Who fixes it" labels.
  6. Persona tap.
  7. Funnel events.
  8. Check result attached to the teardown request.
  9. "Not a fit" on /working-with-us.
- **Phase 2 (makes it worth keeping):**
  1. Product page, cart and policy crawl.
  2. Money estimate from the revenue band.
  3. Emailed report with a private link and a 30-day re-check (with consent).
  4. Partner `?ref=` tracking.
- **Phase 3 (persona modules and distribution):**
  1. The 4 persona modules.
  2. The ops leak quiz.
  3. One-problem search pages.
  4. Anonymous totals for the data story.

## 9. What could go wrong
- **False positives.** One wrong finding ends trust. Mitigations:
  - "couldn't tell" over guessing
  - saved HTML test fixtures for every check
  - a weekly manual review of 10 random reports
- **Money estimates read as promises.** Mitigations:
  - always a range, always "planning scenario", always sourced
  - nothing shown without the visitor's own revenue band
- **Crawling stores we don't own.** Mitigations:
  - only public pages, a few requests a check, an honest user agent, robots.txt respected
  - the rate limit stays (10 checks per visitor per hour)
- **Privacy.** Mitigations:
  - no store data kept without consent
  - totals published only in aggregate, never naming a store
  - Australian Privacy Act, UK GDPR and India DPDP consent wording on the email capture
- **Costs.** PageSpeed API is free within Google's quota. AI-answer checks (asking ChatGPT and others live) cost money per query, so they stay in the paid AI Visibility Snapshot.
- **Team time.** Teardowns at scale could swamp two people. Mitigations:
  - offer teardowns only to persona-fit stores above a revenue band
  - everyone else gets the self-fix report
