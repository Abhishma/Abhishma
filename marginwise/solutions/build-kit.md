# Marginwise solution build kit

One page per solution: what it does, how we build it, the prompt to build or customise it in Claude Code, a demo video script, a pricing proposal, and a case study template.

Where the code lives:
- `marginwise/solutions/leak-audit/` is the store audit crawler (Node + Playwright + axe-core).
- `marginwise/solutions/agents/` holds the AI agents. Each one has `solutions/<name>/prompt.md` (system prompt), `tools.json` (tool definitions), `handlers.py` (integrations, mocked for tests) and `fixtures/`. The shared runner is in `core/`.

How to read "Build here":
- **Here.** Builds and tests fully in this repo with fixtures. Runs live once an `ANTHROPIC_API_KEY` is set.
- **Client access.** Needs the client's admin, API or phone credentials to go live. We build and test against fixtures first, then connect.
- **Partner.** Needs a third party: a law firm, a certified e-invoicing provider, or a telephony provider.

AI model defaults:
- `claude-sonnet-5-5` for conversations and reasoning.
- `claude-haiku-5-5` for high-volume classification.

Every agent that changes money, prices, orders or invoices goes through human approval.

---

## Shared templates

### A. Proposal template (fill the [brackets] for each solution)

```
MARGINWISE PROPOSAL
[Solution name] for [Client legal name]
Prepared by Abhimanyu Sharma, Marginwise | [date] | Valid for 30 days

1. What we heard
[Two or three sentences in the client's words: the problem, what it costs today, and the trigger (deadline, season, incident).]

2. What we will deliver
- [Deliverable 1, specific and testable]
- [Deliverable 2]
- [Deliverable 3]
Not included: [explicit exclusions, e.g. legal advice, ad spend, third-party licence fees, content writing beyond X pages].

3. How we will work (Find, Fix, Grow)
Week 1: Find. Access, baseline measurement, written plan for your sign-off.
Weeks 2-[n]: Fix. Build, test, daily Loom updates, one review call per week.
After launch: Grow (optional). Monitoring, tuning and monthly report.

4. Investment (USD, excl. taxes)
| Option | What is included | Setup | Monthly |
| Essential | [scope] | $[x] | $[y] |
| Recommended | [scope] | $[x] | $[y] |
| Complete | [scope] | $[x] | $[y] |
Third-party costs paid directly by you: [e.g. telephony minutes, app subscriptions, API usage].

5. How we will measure success
Baseline (measured in week 1): [metric] = [value]
Target at [30/60/90] days: [metric] = [value or range]
Acceptance criteria for sign-off: [list of checks, each pass or fail]

6. Timeline
Start: [date]. Go-live: [date]. Depends on access being granted by [date].

7. Terms
- 50% of setup on signing, 50% on go-live acceptance. Monthly fees billed in advance; cancel with 30 days' notice after the first 3 months.
- You own all code, prompts and data built for you. We keep our reusable components and libraries.
- Data handling: we sign your DPA (GDPR AVV, APP, PDPL or CCPA as applicable). Least-privilege access only; access removed at the end.
- [Compliance solutions only:] Marginwise implements the requirements; we do not give legal advice. Your lawyer or adviser confirms the requirements and signs off the result.
- [AI solutions only:] The agent discloses that it is an AI where the law requires it. Actions involving money, prices, orders or invoices require human approval unless you choose otherwise in writing.

8. Next step
Reply "go" and we will send the agreement and the first invoice. We can start on [date].
```

### B. Case study template

```
CASE STUDY: [Client or "an Australian HVAC business"] | [Solution name]
Status: [Demo store / Pilot / Live client]   Permission to name client: [ ] yes [ ] anonymise

Situation
Who: [industry, city, size: staff / revenue band, stack]
Trigger: [what made them act now]
Problem in their words: "[quote from discovery call]"

Baseline (measured before we started, [date range], [method/source])
- [Metric 1]: [value]
- [Metric 2]: [value]
- [Metric 3]: [value]

What we built
- [Component 1]
- [Component 2]
- Integrations: [list]
- Time to launch: [days]

Results ([date range after launch], same method as baseline)
- [Metric 1]: [before] -> [after] ([change])
- [Metric 2]: [before] -> [after]
- What did not change or got worse: [be honest; it builds trust]

Client quote (approved in writing on [date])
"[quote]" - [name, role]

What we would do next
[One or two lines on the next fix.]

Rules: only numbers we measured ourselves, from the stated date range and method. A demo-store case study says "demo store" in the title and uses only demo measurements.
```

### C. Demo video format (applies to every script below)

- Faceless: screen recording plus voiceover, 1080x1920 for reels or 1920x1080 for the website.
- Long cut: 60-90 seconds, for the website, sales emails and LinkedIn.
- Short cut: 10 seconds, for Instagram, Trial Reels and ads.
- Record on the demo Shopify dev store or with fixture data. Never show real client data.
- End card: navy #1F2A44 overlay showing the keyword, e.g. "DM AUDIT".

---

## 1. Revenue Leak Audit crawler

| Item | Detail |
|---|---|
| Problem | Brands do not know where their store leaks revenue or breaks local rules |
| What it does | Loads the homepage and a product page as a mobile shopper. Then it checks speed (LCP, page weight, third-party scripts), accessibility (axe WCAG 2.1 AA), trackers that fire before consent, product page basics (price, add to cart, reviews, shipping, delivery date, BNPL), market rules (AU surcharge text; DE Impressum, withdrawal button, green claims; CA French; SA Arabic and VAT) and AI search readiness (schema, robots rules for AI crawlers, llms.txt). Outputs a scored HTML and JSON report |
| Markets | All |
| Code | `solutions/leak-audit/` (`node audit.mjs <url> --market AU`) |
| Build here | Here. Needs open internet to audit live stores (blocked in this cloud session, so run it on your laptop) |
| Build time | Done. 1 day per new market rule set |
| Feeds | Free 2-minute teardown, $1,500 paid audit, every sprint |

**Claude Code prompt to extend it**
```
In marginwise/solutions/leak-audit, add a new check module for [market or rule], following the pattern of checks/market-de.mjs. Detect [what], mark fail/warn/pass with evidence and a recommended fix, add a fixture page under tests/fixtures that triggers it, add a node:test case, and run npm test until it passes. Update the README check table.
```

**Demo video (75s)**

| Time | Screen | Voiceover |
|---|---|---|
| 0-5s | Terminal: `node audit.mjs demo-store.com --market AU` | "This is how we audit a store in under two minutes." |
| 5-20s | Report opens: score 58/100, red and green rows | "Every check is scored: speed, accessibility, tracking, checkout and local rules." |
| 20-35s | Zoom on "Card surcharge found on checkout" (fail) | "Here is one that matters in Australia right now. The card surcharge ban started on 1 October." |
| 35-50s | Zoom on "Meta pixel fires before consent" and "LCP 4.6s" | "Trackers fire before consent, and the product image takes four and a half seconds." |
| 50-65s | Scroll to "AI search readiness: no Product schema, GPTBot blocked" | "And AI assistants cannot read the product data, so they will not recommend it." |
| 65-75s | End card | "Want this for your store? Comment AUDIT." |

10s cut: 0-3s terminal command, 3-7s report score and the three red rows, 7-10s "Comment AUDIT."

**Proposal tiers**

| Tier | Includes | Price |
|---|---|---|
| Essential | Free 2-minute video teardown (3 findings) | Free |
| Recommended | Revenue Leak Audit: full crawler report, manual review of checkout and tracking, AI search test, written plan with fixes ranked by revenue, 45-minute walkthrough call | $1,500 (credited against a project within 60 days) |
| Complete | Audit plus competitor audit (3 competitors) plus 90-day roadmap | $2,900 |

Acceptance: report delivered with at least 30 checks. Every fail has evidence and a fix. Walkthrough held.

**Case study baseline metrics:**
- Audit score.
- Number of fails.
- Mobile LCP.
- Conversion rate (30 days).
- Accessibility violations.
- Trackers firing before consent.

---

## 2. Surcharge Ban Margin Rescue (Australia)

| Item | Detail |
|---|---|
| Problem | Since 1 Oct 2026, AU merchants cannot surcharge Visa, Mastercard or eftpos cards. The surcharge apps and lines must go, and the cost lands in margin |
| What it does | Removes surcharge logic from the theme, apps and checkout. Builds a payment-fee margin report by SKU and payment method from Shopify Payments, Stripe, Tyro and Afterpay or Zip fee exports. Models three options: absorb, reprice, or steer customers to lower-cost methods. An optional margin agent flags SKUs whose margin falls below target after fees |
| Markets | AU |
| Code | Margin model: `agents/solutions/hs_classifier` landed-cost calculator pattern plus `payout_reconciliation` fee parsing. Check: leak-audit `market-au` |
| Build here | Here for the model and report. Client access to remove the surcharge from the store |
| Build time | 5-8 working days |

**Claude Code prompt**
```
Using marginwise/solutions/agents/solutions/payout_reconciliation as the base, build a payment-fee margin report: read the client's Shopify orders export and payout/fee exports (Shopify Payments, Stripe, Afterpay, Zip), compute fee % by payment method and margin after fees by SKU, and output a CSV plus a one-page HTML summary with three scenarios (absorb, reprice by X%, shift Y% of volume to lower-cost methods). Add fixture CSVs and pytest tests. Never change prices automatically; output recommended price changes for approval.
```

**Demo video (60s)**

| Time | Screen | Voiceover |
|---|---|---|
| 0-6s | Checkout with a "1.5% card surcharge" line, red circle | "Since 1 October, this line is not allowed in Australia." |
| 6-20s | Theme code and app list, surcharge app removed, checkout clean | "We remove it from the theme, the apps and checkout." |
| 20-40s | Margin report: fee % by method, SKUs in red under target | "Then we show what card fees really cost you by product, and where margin went negative." |
| 40-52s | Scenario table: absorb, reprice 1.2%, shift to eftpos | "You pick the fix: absorb, reprice, or steer customers to cheaper ways to pay." |
| 52-60s | End card | "Comment PROFIT for the margin checklist." |

10s cut: surcharge line circled, then clean checkout, then a red SKU list, then "Comment PROFIT."

**Proposal tiers**

| Tier | Includes | Price |
|---|---|---|
| Essential | Surcharge removal from theme, apps and checkout, plus a QA checklist | $1,900 |
| Recommended | Essential plus payment-fee margin report plus 3 scenarios plus recommended price changes | $3,900 |
| Complete | Recommended plus margin agent (weekly alerts) | $3,900 + $750/mo |

Acceptance: no surcharge visible anywhere in checkout across 3 test orders. Margin report reconciles to payout totals within 1%.

**Case study baseline metrics:**
- Surcharge revenue per month before removal.
- Blended card fee %.
- Gross margin after fees.
- Checkout conversion.

---

## 3. AI phone receptionist and missed-call text-back

| Item | Detail |
|---|---|
| Problem | Trades and clinics miss calls. Only 52% of US home-services calls are answered by a person (Invoca 2026). Google now bills LSA advertisers for missed calls (from 1 Oct 2026) |
| What it does | Answers calls and texts 24/7. Says it is an AI. Qualifies the job, checks the service area and the price guide, books into the job system, texts back missed calls within 60 seconds, escalates emergencies to the on-call phone, and logs every lead |
| Markets | AU, NZ, US, CA, DE (German variant with EU AI Act disclosure, EU hosting), KSA (see solution 4 for WhatsApp) |
| Integrations | ServiceM8, simPRO, Tradify (AU/NZ); Jobber, Housecall Pro, ServiceTitan (US/CA); Google Calendar or Doctolib-style booking (DE). Telephony through a voice AI platform (e.g. Twilio, Vapi or Retell). SMS needs A2P 10DLC registration in the US |
| Code | `agents/solutions/receptionist/` (prompt.md, tools.json: check_availability, book_job, create_lead, send_sms, get_service_area, get_price_guide, transfer_to_human) |
| Build here | Here for the prompt, tools and tests. Partner (telephony provider) plus client access (job system) to go live |
| Build time | 7-10 working days |

**Claude Code prompt to customise for a client**
```
Copy marginwise/solutions/agents/solutions/receptionist to clients/[client]/receptionist. Update prompt.md with: business name [x], trade [x], service area postcodes [list], hours [x], emergency rules [x], price guide [paste], booking rules [x], tone [x], language [English/German]. Implement the real adapter in handlers.py for [ServiceM8/Jobber/...] using their API docs, keep the fixture mocks for tests, add 10 test conversations covering booking, out-of-area, price question outside the guide, emergency, angry caller and a caller asking if it is a robot, and run pytest until all pass.
```

**Demo video (80s)**

| Time | Screen | Voiceover |
|---|---|---|
| 0-6s | Phone screen: missed call at 9:47pm, "Unknown caller" | "Every tradie knows this call. It is 9:47pm and you are off the tools." |
| 6-15s | SMS arrives automatically: "Sorry we missed you, this is the [business] assistant..." | "Within a minute, the caller gets a text back." |
| 15-45s | Split screen: transcript of the AI call on the left, the job system calendar filling in on the right | "Or the AI answers the call itself. It tells the caller it is an AI, asks the right questions, checks the suburb, quotes from your price guide only, and books the job." |
| 45-60s | Emergency path: "burst pipe" leads to transfer to the on-call mobile | "Real emergencies go straight to your phone." |
| 60-72s | Dashboard: calls answered 100%, jobs booked, after-hours revenue | "In the morning you see every call, every booking and every lead." |
| 72-80s | End card | "Comment AI and we will set up a test line for your business." |

10s cut: missed call at 9:47pm, then text-back, then the job booked in the calendar, then "Comment AI."

**Proposal tiers**

| Tier | Includes | Setup | Monthly |
|---|---|---|---|
| Essential | Missed-call text-back plus lead capture plus daily summary | $750 | $200 |
| Recommended | AI voice receptionist plus booking into the job system plus emergency transfer plus text-back | $2,500 | $600 |
| Complete | Recommended plus review requests after each job plus monthly call QA and tuning | $3,500 | $900 |

Telephony minutes and SMS are billed at cost.

Acceptance:
- 20 scripted test calls pass: booking, out of area, emergency, price outside the guide, robot question.
- Bookings appear in the job system.
- The AI discloses itself in every call.

**Case study baseline metrics:**
- Answer rate.
- Missed calls per week.
- After-hours calls.
- Jobs booked per week.
- Revenue per booked job.
- LSA missed-call charges.

---

## 4. Arabic WhatsApp commerce and booking agent (Saudi Arabia)

| Item | Detail |
|---|---|
| Problem | Saudi customers expect WhatsApp (92.7% usage). COD orders fail. Since 1 Jan 2026, carriers reject parcels without a National Address. Clinics and AC firms drown in chats |
| What it does | Works in Gulf Arabic and English. Confirms COD orders, captures and validates the National Address short code (4 letters + 4 digits), answers order status, nudges customers to prepay or Tabby/Tamara, starts returns, and books appointments for clinics and AC maintenance. Hands off to a human with the full context |
| Integrations | WhatsApp Business API (Meta Cloud API or a BSP). Salla, Zid or Shopify. SPL National Address API. Clinic or service booking calendar. CRM |
| Code | `agents/solutions/whatsapp_commerce/` |
| Build here | Here (tests with fixtures). Client access plus WhatsApp BSP to go live. **Native Arabic reviewer required** before launch |
| Build time | 10-15 working days |

**Claude Code prompt**
```
Copy marginwise/solutions/agents/solutions/whatsapp_commerce to clients/[client]/whatsapp. Set business [x], platform [Salla/Zid/Shopify], COD rules [x], prepay incentive [x], return policy [paste], booking slots [x], working hours incl. Ramadan [x]. Implement the [platform] adapter in handlers.py, keep fixtures, add 12 test conversations in Arabic and English (COD confirm, wrong address, missing short code, order status, return, booking, angry customer, request for a human), run pytest. Flag every Arabic string for native review in a REVIEW.md list.
```

**Demo video (75s)**

| Time | Screen | Voiceover |
|---|---|---|
| 0-6s | WhatsApp chat, new COD order notification | "A new cash-on-delivery order comes in." |
| 6-25s | The agent messages in Arabic: confirm the order, ask for the short code. Customer replies "RRRD2929" | "The agent confirms it in Arabic and asks for the National Address code, so the courier will accept the parcel." |
| 25-40s | Validation tick, then an offer: "Pay now with Tabby and get free delivery" | "Then it offers prepay or Tabby, which cuts failed deliveries." |
| 40-55s | Second chat: AC maintenance booking for Thursday 5pm | "The same agent books AC maintenance and clinic appointments." |
| 55-68s | Dashboard: COD confirmed %, addresses captured, handoffs | "Your team only sees the chats that need a person." |
| 68-75s | End card (Arabic and English) | "Message ZATCA or WhatsApp to see a demo." |

10s cut: COD order, Arabic confirmation, short code validated, Tabby offer, "Message us for a demo."

**Proposal tiers**

| Tier | Includes | Setup | Monthly |
|---|---|---|---|
| Essential | COD confirmation plus National Address capture | $3,000 | $600 |
| Recommended | Essential plus order status plus prepay/BNPL nudge plus returns | $6,500 | $1,200 |
| Complete | Recommended plus appointment booking plus CRM sync plus monthly Arabic tuning | $12,000 | $2,500 |

WhatsApp conversation fees are billed at cost.

Acceptance:
- 30 test chats pass, reviewed by a native Arabic speaker.
- Address validation is correct on 20 sample codes.
- Handoff works.

**Case study baseline metrics:**
- COD share.
- Failed delivery / return-to-origin rate.
- Orders rejected for address.
- Average first response time.
- Chats per agent per day.

---

## 5. Order-status and returns support agent (WISMO)

| Item | Detail |
|---|---|
| Problem | Most support tickets are "where is my order", returns and address changes |
| What it does | Answers order status from Shopify and the carrier. Starts returns and offers exchanges first. Edits addresses (with approval). Adds ticket notes and escalates. Discloses AI in the EU |
| Integrations | Shopify, Gorgias or Zendesk, Salesforce Service Cloud, AfterShip, Loop or Returnly, carrier APIs (AusPost, NZ Post, UPS, Canada Post, DHL, SMSA) |
| Code | `agents/solutions/support_wismo/` |
| Build here | Here. Client access to the helpdesk and Shopify to go live |
| Build time | 10-15 working days |

**Claude Code prompt**
```
Customise marginwise/solutions/agents/solutions/support_wismo for [client]: helpdesk [Gorgias/Zendesk], carriers [list], return policy [paste], exchange-first rules [x], tone [x], languages [x]. Implement the real adapters in handlers.py, keep mocks, add 15 test tickets from the client's last 100 tickets (anonymised), report the share the agent resolves without a human, and run pytest.
```

**Demo video (70s)**

| Time | Screen | Voiceover |
|---|---|---|
| 0-8s | Helpdesk queue full of "where is my order" tickets | "Most support tickets ask the same three things." |
| 8-30s | Agent reply: order looked up, tracking link, delivery estimate | "The agent answers order status with the real tracking data." |
| 30-48s | Return request leads to an exchange offer, which the customer accepts | "On returns it offers an exchange first, so you keep the revenue." |
| 48-60s | Address change waiting in "Approval needed" | "Anything that changes an order waits for your team to approve." |
| 60-70s | End card | "Comment AI for the 10 AI builds list." |

10s cut: ticket queue, auto-reply with tracking, exchange accepted, "Comment AI."

**Proposal tiers**

| Tier | Includes | Setup | Monthly |
|---|---|---|---|
| Essential | Order-status answers on email and chat | $9,500 | $750 |
| Recommended | Essential plus returns and exchanges plus address edits with approval | $18,000 | $1,500 |
| Complete | Recommended plus Service Cloud or multi-brand plus multilingual | $30,000 | $2,500 |

Acceptance: at least 60% of a held-out set of 100 historical tickets resolved correctly without a human, measured jointly. No order edited without approval.

**Case study baseline metrics:**
- Tickets per month.
- Share that are WISMO.
- First response time.
- Cost per ticket.
- Return-to-exchange rate.

---

## 6. Shopify-to-ERP sync exception agent

| Item | Detail |
|---|---|
| Problem | Orders fail to import, stock drifts, and someone fixes it by hand every morning (Cin7, Unleashed, MYOB, Xero, NetSuite, QuickBooks, DATEV, Odoo) |
| What it does | Reads failed sync records and classifies the root cause (missing SKU, duplicate order, address or tax error, stock mismatch, payout mismatch). Auto-applies only whitelisted safe fixes, queues the rest for approval, retries, and posts a Slack summary |
| Code | `agents/solutions/sync_exception/` |
| Build here | Here. Client access to the ERP and Shopify |
| Build time | 10-20 working days (more if the connector itself needs rebuilding) |

**Claude Code prompt**
```
Customise marginwise/solutions/agents/solutions/sync_exception for [client]: ERP [x], connector [x], whitelisted auto-fixes [list], Slack channel [x]. Export the last 30 days of failed syncs, add them as anonymised fixtures, measure the classifier against a hand-labelled sample of 50, implement the real ERP adapter, and run pytest. Never auto-apply a fix outside the whitelist.
```

**Demo video (70s)**

| Time | Screen | Voiceover |
|---|---|---|
| 0-8s | Error list: "Order #10423 failed: SKU not found" times 14 | "Every morning, someone fixes these by hand." |
| 8-30s | Agent classifies each error: missing SKU, duplicate, tax code | "The agent reads each failure and works out why." |
| 30-48s | Safe fixes applied and retried; two SKU mappings waiting for approval | "Safe fixes run automatically. Anything risky waits for approval." |
| 48-60s | Slack summary at 7am: 12 fixed, 2 need you | "At 7am your team gets one message: what was fixed, and what needs them." |
| 60-70s | End card | "Comment AUDIT and tell us your ERP." |

10s cut: wall of errors, agent labels, "12 fixed, 2 need you" in Slack, "Comment AUDIT."

**Proposal tiers**

| Tier | Includes | Setup | Monthly |
|---|---|---|---|
| Essential | Monitoring plus classification plus Slack alerts | $7,500 | $900 |
| Recommended | Essential plus whitelisted auto-fixes plus retry plus approval queue | $14,000 | $1,500 |
| Complete | Recommended plus connector rebuild or repair plus inventory reconciliation | $25,000 | $2,000 |

Acceptance: classifier at least 90% correct on the labelled sample. Zero non-whitelisted auto-fixes. Daily summary delivered for 10 business days.

**Case study baseline metrics:**
- Failed syncs per week.
- Staff hours on fixes.
- Oversells per month.
- Time from order to ERP.

---

## 7. Payout reconciliation agent

| Item | Detail |
|---|---|
| Problem | Shopify Payments, PayPal, Afterpay, Zip, Klarna and Stripe payouts never match the bank feed. Month-end takes days |
| What it does | Deterministic matcher: payouts to bank lines to accounting entries, with fees, refunds, chargebacks and FX split out. An LLM then writes a plain-English exceptions summary for the bookkeeper |
| Integrations | Xero, MYOB, QuickBooks, NetSuite, DATEV (CSV export first, API later) |
| Code | `agents/solutions/payout_reconciliation/` (matcher is pure Python and fully tested) |
| Build here | Here. Client exports to run it |
| Build time | 5-10 working days |

**Claude Code prompt**
```
Run marginwise/solutions/agents/solutions/payout_reconciliation on [client]'s exports for [month]: [list of files]. If a column mapping fails, add a mapping for that provider's export format with a fixture and a test. Output the reconciliation CSV, the unmatched list and the exceptions summary. Report the match rate.
```

**Demo video (60s)**

| Time | Screen | Voiceover |
|---|---|---|
| 0-8s | Bank feed and Shopify payouts side by side, nothing lines up | "This is why month-end takes three days." |
| 8-30s | Matcher runs: 412 of 418 matched, fees and refunds split out | "We match every payout to the bank, and split out fees, refunds and chargebacks." |
| 30-48s | Exceptions summary: "6 items: 2 Afterpay timing, 1 chargeback, 3 FX" | "What is left comes with a plain-English explanation." |
| 48-60s | End card | "DM Xero to see it on your data." |

10s cut: mismatched lists, "412/418 matched", the summary, "DM Xero."

**Proposal tiers**

| Tier | Includes | Setup | Monthly |
|---|---|---|---|
| Essential | Monthly reconciliation run on your exports | $2,500 | $450 |
| Recommended | Essential plus API connection plus weekly runs plus exceptions summary | $4,500 | $750 |
| Complete | Recommended plus multi-entity and multi-currency plus accounting journal drafts for approval | $6,000 | $1,000 |

Acceptance: match rate at least 98% on a closed month. Totals tie to the bank within $1.

**Case study baseline metrics:**
- Days to close.
- Bookkeeper hours.
- Unreconciled balance at month-end.

---

## 8. Purchase-order-to-order agent (B2B wholesale)

| Item | Detail |
|---|---|
| Problem | Trade customers email PDFs, and someone re-keys every order |
| What it does | Extracts order lines from emailed POs. Validates them against the price list and customer terms. Flags discrepancies (price, MOQ, discontinued SKU). Creates a draft order for approval in Shopify B2B or the ERP |
| Code | `agents/solutions/po_to_order/` |
| Build here | Here. Client mailbox and ERP access to go live |
| Build time | 7-12 working days |

**Claude Code prompt**
```
Customise marginwise/solutions/agents/solutions/po_to_order for [client]: price list [file], customer terms [file], target system [Shopify B2B/NetSuite/MYOB/...]. Add 20 anonymised real POs as fixtures with expected outputs, measure line-level extraction accuracy, implement the target adapter (draft orders only), and run pytest.
```

**Demo video (60s)**

| Time | Screen | Voiceover |
|---|---|---|
| 0-8s | Inbox with PDF purchase orders | "Your trade customers still order like this." |
| 8-30s | PDF lines turn into a structured table, one price mismatch flagged | "The agent reads the order, checks your price list and flags anything that does not match." |
| 30-48s | Draft order in Shopify B2B, "Approve" button | "You approve, and the order is in." |
| 48-60s | End card | "Comment AUDIT and tell us how you take trade orders." |

10s cut: PDF, then table with a flag, then draft order, then "Comment AUDIT."

**Proposal tiers**

| Tier | Includes | Setup | Monthly |
|---|---|---|---|
| Essential | Extraction plus validation plus draft order email | $6,000 | $500 |
| Recommended | Essential plus direct draft orders in Shopify B2B or the ERP | $11,000 | $900 |
| Complete | Recommended plus B2B portal plus customer price lists plus net terms | $18,000+ | $1,500 |

Acceptance: line-level accuracy at least 97% on 20 held-out POs. Every discrepancy flagged.

**Case study baseline metrics:**
- POs per week.
- Minutes per PO.
- Keying errors per month.
- Order-to-dispatch time.

---

## 9. Compliance copy auditor

| Item | Detail |
|---|---|
| Problem | Copy that breaks rules: German green claims (EmpCo, since 27 Sep 2026), strike-through price wording (PAngV), AU drip pricing and fee display, and ad claims Meta rejects |
| What it does | Scans product pages, ads and email copy. Returns each finding with the quote, the rule, a risk level and a suggested rewrite. Not legal advice; a lawyer signs off |
| Code | `agents/solutions/compliance_copy_auditor/` |
| Build here | Here. Partner law firm for sign-off |
| Build time | 3-5 working days per client |

**Claude Code prompt**
```
Run marginwise/solutions/agents/solutions/compliance_copy_auditor over [client]'s exported product and ad copy ([files]) for rule sets [EmpCo, PAngV, AU drip pricing, Meta claims]. Output findings CSV and a summary for the client's lawyer. If you find a pattern the rules miss, add it to the rule list with a fixture and test.
```

**Demo video (60s)**

| Time | Screen | Voiceover |
|---|---|---|
| 0-8s | Product page: "klimaneutral" badge | "Since 27 September, this badge is a problem in Germany." |
| 8-35s | Findings list: quote, rule, risk, suggested rewrite | "We scan every product page, ad and email and show each risky claim with a safer rewrite." |
| 35-50s | Lawyer sign-off column | "Your lawyer approves the final wording. We make the changes." |
| 50-60s | End card | "DM EmpCo for the checklist." |

**Proposal tiers**

| Tier | Includes | Price |
|---|---|---|
| Essential | Scan of up to 500 pages or ads plus findings report | $4,000 |
| Recommended | Essential plus rewrites plus implementation in the store | $8,500 |
| Complete | Recommended plus quarterly re-scan plus ad pre-check | $15,000/yr |

Acceptance: every flagged item has a rule reference and a rewrite. Implementation is matched against the lawyer-approved list.

**Case study baseline metrics:**
- Risky claims found.
- Pages affected.
- Ads rejected per month.
- Warning letters received.

---

## 10. GPSR product-safety data extractor (EU)

| Item | Detail |
|---|---|
| Problem | Every EU listing needs manufacturer and EU-responsible-person details, plus warnings. Warning letters for missing data are documented |
| What it does | Extracts the GPSR fields from supplier PDFs into Shopify metafields JSON, and flags missing fields per SKU |
| Code | `agents/solutions/gpsr_extractor/` |
| Build here | Here. Client catalogue and supplier documents |
| Build time | 5-10 working days |

**Claude Code prompt**
```
Run marginwise/solutions/agents/solutions/gpsr_extractor over [client]'s supplier documents ([folder]) and product export. Produce the metafields import file and a missing-fields report by SKU. Add any new document layout as a fixture with a test.
```

**Demo video (45s):** supplier PDF, then extracted fields, then a missing-fields report (12 SKUs missing an EU contact), then Shopify product showing a "Product safety" block, then end card "DM GPSR".

**Proposal tiers**

| Tier | Includes | Price |
|---|---|---|
| Essential | Up to 500 SKUs | $5,000 |
| Recommended | Up to 2,000 SKUs plus theme block | $11,000 |
| Complete | Up to 10,000 SKUs plus marketplace feeds plus monthly updates | $20,000 + $500/mo |

**Case study baseline metrics:**
- SKUs missing GPSR data.
- Hours per SKU done by hand.
- Marketplace listing suppressions.

---

## 11. HS-code classifier and landed-cost calculator (US and Canada)

| Item | Detail |
|---|---|
| Problem | De minimis is suspended, tariffs keep changing, and 50% US tariffs apply to many Canadian goods. Brands price on stale landed costs |
| What it does | Suggests HS codes with confidence and a rationale, always for human or broker review. A deterministic landed-cost calculator (duty, tariff surcharge, freight, FX) feeds a SKU margin table and duties-included pricing |
| Code | `agents/solutions/hs_classifier/` (calculator fully tested) |
| Build here | Here. Customs broker confirms the codes |
| Build time | 8-15 working days |

**Claude Code prompt**
```
Using marginwise/solutions/agents/solutions/hs_classifier, classify [client]'s product list ([file]) and compute landed cost per SKU with duty rates [file or broker input], tariff surcharges [x], freight [x] and FX [x]. Output a margin table flagging SKUs below [target]% and a broker review sheet. Never mark a code final; status stays "for broker review".
```

**Demo video (60s):** product list, then suggested HS codes with confidence, then a "broker review" column, then landed cost per SKU, then SKUs in red below margin, then a proposed duties-included price, then end card "Comment PROFIT".

**Proposal tiers**

| Tier | Includes | Setup | Monthly |
|---|---|---|---|
| Essential | Landed-cost model for up to 200 SKUs | $7,500 | none |
| Recommended | Essential plus HS suggestions plus broker sheet plus margin alerts | $12,000 | $2,000 |
| Complete | Recommended plus duties-included checkout (Shopify Managed Markets or Zonos) plus monthly tariff updates | $18,000 | $3,500 |

**Case study baseline metrics:**
- SKUs below margin floor.
- Average landed cost error.
- Brokerage complaints.
- Cross-border conversion.

---

## 12. AI search visibility tracker (AEO/GEO)

| Item | Detail |
|---|---|
| Problem | 45% of US consumers use AI tools to find local businesses (BrightLocal 2026), and shoppers ask ChatGPT what to buy. Brands do not know whether they are named |
| What it does | Asks AI assistants a fixed set of buying questions per category and market, parses which brands are named and in what position, and tracks share of voice monthly. Paired with schema, feed and content fixes |
| Code | `agents/solutions/aeo_visibility/` (parser tested; adapters for OpenAI, Perplexity and Anthropic need API keys) |
| Build here | Here. API keys to run live |
| Build time | 3 days to set up per client |

**Claude Code prompt**
```
Configure marginwise/solutions/agents/solutions/aeo_visibility for [client]: category [x], markets [x], competitors [list], 20 buying questions (use the templates, adapt to [market] language). Run against the available assistants, save raw answers, compute share of voice, and produce the monthly report. Add any new answer format to the parser tests.
```

**Demo video (60s):** a question typed into an AI assistant ("best running socks to buy in Australia"), then the answer naming three brands, then the tracker table showing the client at 0/20, then the fixes list (schema, reviews, comparison page), then month 3 showing 6/20 (demo data, labelled), then end card "Comment GEO".

**Proposal tiers**

| Tier | Includes | Monthly |
|---|---|---|
| Essential | Monthly tracking, 20 questions, 1 market | $1,500 |
| Recommended | Tracking plus schema and feed fixes plus 2 content pieces a month | $2,500 |
| Complete | 3 markets plus competitor tracking plus monthly fixes sprint | $4,000 |

**Case study baseline metrics:**
- Share of voice across 20 questions.
- Mentions per assistant.
- Product schema coverage.
- Organic and AI referral sessions.

---

## 13. Lead triage and speed-to-lead agent

| Item | Detail |
|---|---|
| Problem | Inbound leads wait hours. CRM data is dirty: 76% say less than half their CRM data is accurate (Validity 2025) |
| What it does | Enriches and scores each lead against the ICP, routes it to an owner, drafts a first reply in the market's tone (sent after approval), respects consent rules (Spam Act, CASL, UWG), and logs the activity |
| Integrations | Salesforce Sales Cloud, HubSpot |
| Code | `agents/solutions/lead_triage/` |
| Build here | Here. Client CRM access |
| Build time | 10-20 working days |

**Claude Code prompt**
```
Customise marginwise/solutions/agents/solutions/lead_triage for [client]: CRM [Salesforce/HubSpot], ICP [x], routing rules [x], markets and consent rules [x]. Implement the CRM adapter, add 25 anonymised historical leads with the expected score and route, and run pytest. Drafts are never sent without approval.
```

**Demo video (60s):** web form lead arrives, then enrichment (company, stack, revenue band), then score 82 and routed to the AU owner, then a drafted reply waiting for approval, then response time on the dashboard, then end card "Comment AUDIT".

**Proposal tiers**

| Tier | Includes | Setup | Monthly |
|---|---|---|---|
| Essential | Scoring plus routing plus alerts | $9,500 | $1,000 |
| Recommended | Essential plus enrichment plus drafted replies plus activity logging | $18,000 | $1,800 |
| Complete | Recommended plus CRM dedupe and cleanup plus fractional admin | $30,000 | $3,500 |

**Case study baseline metrics:**
- Median time to first response.
- Lead-to-meeting rate.
- Duplicate records.
- Leads without an owner.

---

## 14. Instant quote builder (trades)

| Item | Detail |
|---|---|
| Problem | Customers want a price now. Owners quote at night. Aggregators win the click |
| What it does | Asks the minimum questions, applies the price book with ranges, produces a quote (German "Angebot" variant with mandatory fields), and books a site visit |
| Code | `agents/solutions/quote_builder/` |
| Build here | Here. Client price book and booking system |
| Build time | 7-12 working days |

**Claude Code prompt**
```
Customise marginwise/solutions/agents/solutions/quote_builder for [client]: trade [x], price book [file], minimum and maximum ranges [x], questions [x], language [x], booking system [x]. Add 15 test scenarios with the expected price range, embed the web widget on a test page, and run pytest. Never quote outside the price book; out-of-range jobs go to a site visit.
```

**Demo video (60s):** website "Get a price in 60 seconds", then 4 questions (roof size, storeys, material, suburb), then a price range shown, then a site visit booked, then the owner's phone showing the quote and booking, then end card "Comment AUDIT".

**Proposal tiers**

| Tier | Includes | Setup | Monthly |
|---|---|---|---|
| Essential | Quote calculator for 1 service | $2,000 | $150 |
| Recommended | Up to 3 services plus site-visit booking plus CRM | $3,500 | $300 |
| Complete | Recommended plus conversational quote agent (web and SMS) plus German Angebot output | $9,000 | $800 |

**Case study baseline metrics:**
- Quote requests per month.
- Time to quote.
- Quote-to-booking rate.
- Share of leads from aggregators.

---

## 15. Review engine and local presence (Google Business Profile)

| Item | Detail |
|---|---|
| Problem | 68% of consumers only use businesses rated 4+, 74% want recent reviews, 89% expect replies (BrightLocal 2026). Most trades have fewer than 10 reviews |
| What it does | SMS or WhatsApp review request after each completed job. AI-drafted replies (approved before posting). GBP optimisation, suburb or district landing pages, and review velocity reporting |
| Integrations | Job system (ServiceM8, Jobber, etc.), Google Business Profile API, SMS (A2P 10DLC in the US) |
| Code | Uses the receptionist `send_sms` tool and the support agent's drafting pattern. Landing pages are built in the client's site |
| Build here | Here for the templates and flows. Client GBP access |
| Build time | 5-10 working days |

**Claude Code prompt**
```
For [client] ([trade], [city]), build: (1) review request SMS/WhatsApp flow triggered by job completion in [system], with timing and opt-out; (2) a reply-drafting prompt that writes specific, non-templated replies in [tone], queued for approval; (3) [n] suburb landing pages using the client's real services and photos, with LocalBusiness schema. Add tests for the flow logic and validate the schema.
```

**Demo video (45s):** job marked complete, then SMS "How did we do?", then a 5-star review posted, then an AI-drafted reply waiting for approval, then the review count chart rising (demo data, labelled), then end card "Comment AUDIT".

**Proposal tiers**

| Tier | Includes | Setup | Monthly |
|---|---|---|---|
| Essential | Review requests plus reply drafting | $500 | $150 |
| Recommended | Essential plus GBP optimisation plus 5 suburb pages | $2,500 | $800 |
| Complete | Recommended plus 15 pages plus AI search visibility plus monthly content | $4,000 | $1,500 |

**Case study baseline metrics:**
- Reviews in last 90 days.
- Rating.
- Reply rate.
- Map pack rank for 5 target searches.
- Calls from GBP.

---

## 16. E-invoicing hookup (Germany E-Rechnung, Saudi ZATCA)

| Item | Detail |
|---|---|
| Problem | Germany: B2B e-invoices mandatory from 1 Jan 2027 above EUR 800K turnover (XRechnung or ZUGFeRD; PDF no longer counts). Saudi Arabia: ZATCA Phase 2 Wave 25 due 1 Feb 2027 above SAR 187.5K |
| What it does | Germany: generates XRechnung/ZUGFeRD from Shopify, Shopware or trade software, plus DATEV or lexoffice export and payout matching. Saudi Arabia: connects Shopify, Woo, Magento or the ERP to a certified e-invoicing provider (cleared B2B, reported B2C), with exception monitoring |
| Build here | Partner. Uses a certified provider or a validated library. We build the integration, mapping, tests and monitoring |
| Build time | 8-20 working days |

**Claude Code prompt**
```
For [client] on [platform], build the e-invoicing integration for [Germany XRechnung/ZUGFeRD | Saudi ZATCA Phase 2 via provider X]: map order and customer fields to the required invoice fields, generate or submit invoices through [library/provider API], store the response IDs, alert on rejections, and add tests with sample orders covering B2B, B2C, refunds/credit notes and multi-currency. Validate generated files with the official validator before marking any test as passed.
```

**Demo video (60s):** B2B order placed, then an invoice generated as XRechnung (or ZATCA cleared with QR), then the validator showing pass, then the DATEV export (or provider dashboard), then the rejection alert flow, then end card "DM E-Rechnung" or "DM ZATCA".

**Proposal tiers**

| Tier | Includes | Price |
|---|---|---|
| Essential | Invoice generation or submission for one channel | $1,500-4,000 + $100-250/mo |
| Recommended | Essential plus DATEV or ERP export plus credit notes plus rejection alerts | $8,500-15,000 + $300/mo |
| Complete | Multi-channel (store, B2B, POS) plus payout matching plus monitoring | $15,000-29,000 + $500/mo |

For legal requirements, the client's tax adviser confirms them; we implement.

**Case study baseline metrics:**
- Invoices per month.
- Hours to produce or export.
- Rejection rate.
- Days to get paid.

---

## Build order (what to make demo-ready first)

| Order | Solution | Why first |
|---|---|---|
| 1 | Revenue Leak Audit crawler | Powers every free teardown and the $1,500 audit in all markets |
| 2 | AI phone receptionist | Biggest local market (trades in Phoenix, Houston, DFW, Brisbane, Sydney). Google missed-call billing gives it an ROI story |
| 3 | Surcharge Ban Margin Rescue | Live AU trigger, fastest sale |
| 4 | Payout reconciliation | Fully buildable here, easy demo, partner channel (bookkeepers) |
| 5 | Review engine + local presence | Cheap entry for local businesses, leads into the receptionist |
| 6 | Arabic WhatsApp agent | KSA wave 3, needs a native reviewer |
| 7 | E-invoicing hookup | Germany and KSA deadlines Jan and Feb 2027 |
| 8-16 | The rest | Build to order after the first sale of each |
