# Marginwise Leak Audit

A command-line tool that runs the automated part of the Marginwise **free 2-minute teardown** and the **$1,500 Revenue Leak Audit** for ecommerce stores in Australia, New Zealand, the US, Canada, Germany and Saudi Arabia.

It loads a store's homepage and one product page (PDP) in Chromium, emulating an iPhone 13. It then runs a set of small, independent checks and writes two files:

- `report.json`: machine-readable results, for CRM import or follow-up scripts
- `report.html`: a self-contained client report in Marginwise colours. It uses no external assets, so it can be emailed or attached as-is.

Each finding is marked **pass**, **warn** or **fail** and comes with the evidence and a recommended fix. The run ends with a weighted score out of 100 and the top 5 findings.

## Install

Requires Node 20+ and a Chromium build compatible with Playwright 1.56.

```bash
cd marginwise/solutions/leak-audit
npm install
```

The tool uses `playwright-core` pinned to 1.56.1, which does not download browsers. It launches the Chromium from `PLAYWRIGHT_BROWSERS_PATH`. If that fails, it falls back to `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`. You can point it at another binary with `LEAK_AUDIT_CHROME=/path/to/chrome`. On a normal machine, `npx playwright@1.56.1 install chromium` provides one. If `HTTPS_PROXY` is set, the browser uses it.

## Usage

```bash
node audit.mjs <url> [--market AU|NZ|US|CA|DE|SA] [--pdp <product-url>] [--out dir] [--quiet]

# examples
node audit.mjs https://www.example.com.au --market AU
node audit.mjs shop.example.de --market DE --pdp https://shop.example.de/p/wandersocke --out reports/example-de
npm run audit -- https://www.example.com --market US
```

- `--market` defaults to `US`. It enables that market's rule module and adjusts severities.
- If `--pdp` is not given, the tool finds a product page itself. It tries `/products.json` first (Shopify), then the first same-site link that looks like a product (`/products/`, `/product/`, `/p/` and similar).
- `--out` defaults to `./out`.
- If the homepage cannot be loaded, the run stops with exit code 1 and no report, so that a partial score never reaches a client.

## Checks and how they map to Marginwise offers

Each check is a module in `checks/` and is registered in `checks/index.mjs`.

| Check | What it looks at | Offer use |
|---|---|---|
| `platform` | Fingerprints Shopify, Shopware, Magento, WooCommerce, Salla, Zid, BigCommerce and SFCC from HTML, scripts, headers and page globals. Not scored. | Teardown context; decides which fixes are realistic |
| `speed` | Mobile LCP (warn above 2.5s, fail above 4s), bytes transferred, request count, third-party scripts, render-blocking head scripts. Measured on the homepage and the PDP. | Headline teardown number; the Audit adds the fix plan |
| `accessibility` | axe-core WCAG 2.1 A/AA run. Serious and critical violations are summarised by rule. Overlay widgets (accessiBe, UserWay, AudioEye, EqualWeb) get a warning. Weight is doubled for the US. | Teardown shows the count; the Audit lists template-level fixes |
| `tracking` | Meta pixel, GA4/gtag, Google Ads, GTM, TikTok, Klaviyo and Hotjar requests that fire before any consent interaction. Consent banner detection: OneTrust, Cookiebot, Usercentrics, Shopify, generic. Trackers before consent are a fail for DE and CA. | Teardown red flag; the Audit includes a consent-mode plan |
| `pdp` | Price and add to cart above the fold. Reviews/rating and their position. Shipping cost or free-shipping threshold. Delivery estimate. BNPL messaging (Afterpay, Zip, Klarna, Tabby, Tamara, Affirm, Shop Pay Installments) and whether it sits within 250px of the price. | Core of the Revenue Leak Audit |
| `market-au` | Surcharge or card-fee wording (fail; RBA surcharge ban from 1 Oct 2026). Afterpay messaging. | Teardown compliance flag |
| `market-us` | Accessibility statement link. Accessibility weight is doubled in the score. | Audit: ADA risk section |
| `market-ca` | French locale (`/fr`, `hreflang fr-CA`, language switcher). Shows pre-consent tracking again for reference; it is scored in `tracking`. | Audit: market readiness |
| `market-de` | Impressum, "Vertrag widerrufen" withdrawal function, Kündigungsbutton when subscription signals exist, Kauf auf Rechnung, strike-through prices (30-day lowest price rule), klimaneutral/CO2-neutral claims (EmpCo from 27 Sep 2026), Barrierefreiheit statement. | Teardown compliance flags; Audit legal-UX section |
| `market-sa` | Arabic version (`lang=ar`, `dir=rtl`, `/ar`), prices incl. VAT, Tabby/Tamara, WhatsApp contact, mada / Apple Pay. | Audit: KSA readiness |
| `ai-search` | Product JSON-LD fields (name, price, availability, aggregateRating, brand, gtin), Organization and FAQPage schema. robots.txt rules for GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot and Google-Extended. `/llms.txt`. Title and meta description length. | Teardown hook ("are you visible in ChatGPT?"); the Audit fixes the schema |

NZ has no market-specific module yet. It gets all the generic checks.

### Scoring

- Within each check: pass = 1, warn = 0.5, fail = 0. `info` and `error` findings are not scored.
- The total is the weighted mean of the check scores. Weights: speed 20, PDP 20, accessibility 15 (30 in the US), tracking 15, market 10-15, AI search 15, platform 0.

### Adding a check

1. Create `checks/my-check.mjs` that exports an object like this:

   ```js
   export default {
     id: 'my-check', title: 'My check', offer: 'Revenue Leak Audit', weight: 10,
     markets: ['DE'],            // optional: only run for these markets
     probes: { pdp: { foo: { selector: '.foo', text: 'regex source' } } }, // optional
     run(ctx) { return [finding('my.id', 'Label', STATUS.WARN, 'evidence', 'fix')]; },
   };
   ```

2. Add it to the list in `checks/index.mjs`.

`ctx` gives the check:

- `market`
- `home` and `pdp` snapshots: text, links, scripts, requests, JSON-LD, metrics, axe results, probe positions
- `origin`
- `fetch(url)`

If a check throws, the runner catches it and records a single `error` finding, so the rest of the run continues.

## Tests

```bash
npm test
```

The tests use `node:test`. They start a tiny local HTTP server over `tests/fixtures/`, and all external requests (trackers, CDNs) are stubbed, so the suite runs offline. The fixtures cover:

- **AU store** (Shopify-like): the PDP is found by link discovery. The page has a "1.5% card surcharge" line, no reviews, a Meta pixel that fires before consent under a cookie banner, Afterpay near the price, GPTBot blocked in robots.txt and no llms.txt.
- **DE store**: no Impressum, GA4 loads before consent, a klimaneutral claim, a strike-through price, Kauf auf Rechnung, and an image without alt text (axe `image-alt`, critical).
- Unit tests: error isolation, scoring (including the US accessibility weight), the robots.txt parser, and an unreachable homepage.

## Limitations

- **Heuristic text detection.** Market and PDP checks match visible text, links, alt text and common widget selectors. They can miss content inside images, iframes, shadow DOM, or anything rendered only after interaction (accordions, the cart, checkout). They can also match unrelated wording, for example "surcharge" in a blog post. Review every finding before it goes to a client.
- **Not legal advice.** The DE, AU, CA, US and SA items are indicators that a page needs review against the law, not legal conclusions. Dates referenced: RBA surcharge ban 1 Oct 2026, EU withdrawal button 19 Jun 2026, EmpCo 27 Sep 2026, BFSG 28 Jun 2025.
- **One page load per page, no consent click.** Every request seen counts as "before consent". Lab LCP from a single emulated load on the host's network is not field data (CrUX), and results vary from run to run.
- **Only two pages.** Only the homepage and one PDP are inspected. Collection pages, cart and checkout are not covered.
- **Third-party detection** uses an approximate registrable domain and a short list of platform CDNs.
- **Bot protection.** Some stores (Cloudflare, Akamai) block headless browsers. The tool then stops with a "Homepage could not be loaded" error.
- **Not yet tested against a live store.** The sandbox this was built in blocks outbound traffic to store domains (proxy 403 on allbirds.com and gymshark.com). Only the local fixtures have been run so far. The first runs against real stores should be checked by hand to tune selectors and thresholds.
