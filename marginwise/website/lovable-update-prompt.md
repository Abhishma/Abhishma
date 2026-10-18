# Lovable update prompt for the Marginwise Landing Page project

Project: Marginwise Landing Page (https://lovable.dev/projects/fb7d5643-7f43-4b8c-ba4a-67b233b640e2)

Status, 18 Oct 2026: not sent yet. After credits were added, Lovable still answered "out of credits" on three tries. Items 16 and 17 add Google Meet and confirm the team names.
To apply it, either:
- add credits at https://lovable.dev/settings/billing and ask Claude to send it again, or
- paste everything below the line into the Lovable editor chat.

The same content is already live on the booking artifact (marginwise/website/index.html). The prompt was written against the project's current code: booking-utils.ts, booking.functions.ts, pricing.tsx, case-studies.tsx and the tests.

---

Content and booking update for Marginwise. Marginwise no longer targets India. Markets are now Australia, the US and the UK. Keep the existing design, components, booking storage, Google Calendar invite, lead emails, team area, AI call prep, client portal and auth exactly as they work today; change copy, market logic and pricing as below. Do not invent client results, numbers or testimonials anywhere.

1. Shared header/footer on every public page (home, pricing, case studies, portal if it shows them)
- Brand tagline: "Ecommerce growth, built with AI" (replaces "Growth experts for D2C brands").
- Availability text: "Working with brands in Australia, the US and the UK".
- Footer left: "Marginwise · Led by Abhimanyu Sharma · Performance marketing, CRO, web, SEO and AI search, AI solutions". Footer right: "Based in India · Working with brands in Australia, the US and the UK".
- Update page meta titles/descriptions/og tags to match (no India, INR, COD, UI/UX or app development).

2. Home page hero
- Label: "Ecommerce growth · 30-minute call".
- H1: "Find what is costing your store <em>margin</em>. Fix it in a fixed-price sprint." (keep the highlighted em style on "margin").
- Lede: "Marginwise runs performance marketing, CRO, website development, SEO and AI search, and AI solutions for ecommerce brands in Australia, the US and the UK. Every engagement is led by Abhimanyu Sharma, who has ten years of experience building D2C, omnichannel and loyalty products on Shopify, Salesforce and ERP systems. On the call we look at your store, your funnel and your numbers, and agree where to start."
- Fact chips: "30 min", "Google Meet or Zoom", "Sydney, London and US hours", "No sales pitch".
- Stats: 10 years building D2C and commerce products; 5 services under one team; 3 markets: Australia, the US and the UK; 1 working day to reply to every request.

3. Booking desk (booking-utils.ts, booking.tsx)
- Market type becomes "au" | "us" | "uk".
- Time-zone buttons: Sydney (Australia/Sydney), London (Europe/London), US Eastern (America/New_York), Your time (local). Add these to tzName.
- SLOTS_IST becomes [[7,0],[13,30],[16,30],[19,30],[21,30]] (12:30/19:00 Sydney, 08:00/11:00/14:00/16:00 London in winter, 09:00/11:00 US Eastern).
- Only show slots that fall between 08:00 and 20:00 in the time zone currently shown (so US Eastern shows 10:00 and 12:00, Sydney 12:30 and 19:00, London four daytime slots); if the selected slot becomes hidden, select the first visible one. If none are visible, show all.
- Each slot's second line shows the IST time labelled "IST (our time)".
- slotText: "Mon 19 Oct · 19:00 Sydney / 08:00 London / 03:00 ET / 13:30 IST" format (Sydney, London, ET, IST).
- Default market and time zone from the visitor's time zone: America/* -> US + US Eastern; Europe/* -> UK + London; everything else -> Australia + Sydney. Default slot: AU -> 13:30 IST slot, UK -> 16:30 IST slot, US -> 21:30 IST slot.
- Market select options: Australia, New Zealand, United States, United Kingdom, Canada, Other.
- Topic options: Store leak audit, Performance marketing, Conversion rate optimisation, Website development, SEO and AI search, AI solutions and automation, More than one of these, Not sure yet.
- Brief placeholder: "Example: Our checkout still adds a card surcharge and Meta CAC is up. We sell skincare on Shopify in Australia."
- Under the submit button: "Your details are only used to arrange the call. Times shown in your chosen time zone."
- Keep storage, calendar event creation, team inbox emails and the Google Calendar fallback link working. The server already stores market as free text, so no migration is needed.

4. Conversion calculator: markets au/us/uk with currencies AUD (en-AU), USD (en-US), GBP (en-GB). Example stores: AU 40000 sessions, 1.8%, 110 AOV, 60% margin; US 40000, 2.0%, 75, 60%; UK 40000, 1.9%, 60, 60%. AOV input step 5. The currency label next to "Avg order" follows the market. Apply the same currency logic to plan-calculator and to any figures used in the call follow-up email.

5. "Where ecommerce revenue leaks" section (rename from "Where D2C revenue leaks"): keep the 70.22%, 35% and 8.4% cards. Replace the India COD card with:
- fig "1 Oct" small "2026"
- text "is when Australian merchants had to stop surcharging Visa, Mastercard and eftpos card payments."
- What we do: "remove surcharge logic from the theme, apps and checkout, then show your margin by product after card fees so you can absorb, reprice or steer customers to cheaper ways to pay."
- Source link: https://rba.gov.au/media-releases/2026/mr-26-10.html "Reserve Bank of Australia, media release 2026-10".

6. Services section: market toggle buttons Australia / US / UK. Five service cards (if the last card is alone in its row, make it span the full row):
- Performance marketing: "Paid acquisition that pays back". Campaigns planned around contribution margin and repeat purchase, not just ROAS on the dashboard. Bullets: Account and tracking audit, including server-side tracking; Creative testing plan and campaign structure; Weekly reporting tied to CAC and margin. Stack AU "Meta · Google Ads · Performance Max · profit-based reporting", US "Meta · Google Ads · TikTok · Conversions API", UK "Meta · Google Ads · TikTok · Consent Mode v2".
- CRO: "Conversion rate optimisation". Find where shoppers drop off between landing page and payment, then fix it with tested changes. Bullets: Funnel, session-recording and accessibility audit; Prioritised test backlog with expected impact; A/B tests on product pages, cart and checkout. Stack AU "GA4 · Clarity · Afterpay and Zip in checkout · Shopify Plus", US "GA4 · Hotjar · Shop Pay, Apple Pay and Affirm · WCAG 2.2 fixes", UK "GA4 · Clarity · Klarna and Clearpay · Shopify Plus".
- Website development: "Shopify and custom builds". New stores, migrations and the integrations behind them, scoped as fixed releases. Bullets: Shopify and Shopify Plus builds, B2B and wholesale; Migrations from Magento, WooCommerce and Salesforce Commerce Cloud; ERP, accounting, CRM and carrier integrations. Stack AU "Shopify Plus · Cin7, Unleashed, MYOB and Xero · Shippit and Starshipit", US "Shopify Plus · NetSuite and QuickBooks · Salesforce", UK "Shopify Plus · Xero · Royal Mail, DPD and Evri".
- SEO, AEO and GEO: "Found on Google and in AI answers". Shoppers now ask ChatGPT, Perplexity and Google's AI what to buy. We work on both the search results and the answers. Bullets: Technical SEO and product page content; Product, Offer, Review and FAQ schema; Monthly test of which brands AI assistants name. Stack (all markets): "Google Search Console · schema · AI answer tracking".
- AI solutions: "AI that takes boring work off your team". Agents we build and connect to your stack, with a person approving anything that touches money, prices or orders. Bullets: Support agent for order status, returns and exchanges; ERP sync exception agent and payout reconciliation; Lead triage and AI phone receptionist. Stack AU "Shopify · Gorgias · Xero · Cin7", US "Shopify · Gorgias · NetSuite · Salesforce", UK "Shopify · Gorgias · Xero · Klaviyo".

7. Method section (home and case studies): heading "How we work: Find, Fix, Grow". Keep the formula strip. Three steps:
- Week 1–2, Find: "A paid audit. Our audit tool checks speed, accessibility, tracking, checkout, local rules and AI search readiness; a person reviews every finding and ranks the fixes by revenue."
- Week 2–6, Fix: "A fixed-scope sprint with written acceptance criteria and a daily video update. You know the price before we start."
- Monthly, Grow: "An optional retainer for CRO, performance marketing, AI search and agent monitoring, reported on profit, not ROAS."

8. Plans (home section and the /pricing page, same data). Label: "Prices in USD · billed in USD, AUD or GBP". Pricing page H1: "Three ways to work with us, with <em>prices</em> up front." Pricing lede: "Start with a free 2-minute video teardown, then a fixed-fee audit. Larger builds, migrations and AI agents are quoted after the first call."
- Find: "Revenue Leak Audit". A two-week review of your store, tracking and checkout, with a written plan ranked by revenue. Start with a free 2-minute video teardown if you want to test the fit first. Bullets: 30-point store audit and tracking check; Checkout, speed and accessibility review; AI search visibility test; Written plan and walkthrough call. Price "$1,500", terms "Fixed fee, credited against a sprint within 60 days".
- Fix · most popular (featured): "Fixed-price sprint". One problem, solved end to end with a fixed scope, price and acceptance criteria. Bullets: Checkout and payment fixes, including the Australian surcharge ban; Tracking, consent and accessibility fixes; Shopify and ERP sync repairs with an AI exception agent; Tariff and landed-cost margin model. Price "From $3,900", terms "Fixed fee, 50% upfront and 50% on acceptance".
- Grow: "Monthly retainer". Ongoing growth work from one team, reviewed against profit every month. Builds and migrations are quoted per project. Bullets: Performance marketing on Meta, Google and TikTok; CRO testing roadmap; AI search visibility work; AI agent monitoring and tuning. Price "From $1,500 a month", terms "3-month minimum, then 30 days' notice".
- Note under plans: "Larger builds, migrations and AI agents are quoted after the first call, once we have seen your store and numbers. Compliance work is implementation only: your lawyer or adviser confirms the requirements."
- Keep the existing data-cta attributes, using plan_audit, plan_sprint, plan_retainer on the home page and pricing_audit, pricing_sprint, pricing_retainer on /pricing.

9. Where we work: three cards.
- Australia: "Shopify brands protecting margin". Hours: Sydney midday to evening. Focus: Surcharge ban, Afterpay and shipping costs, Cin7, MYOB and Xero sync. Billing: AUD.
- United States: "Brands growing through tariffs". Hours: US mornings, Eastern and Pacific. Focus: Landed cost and pricing, accessibility, NetSuite and QuickBooks sync. Billing: USD.
- United Kingdom: "Stores fixing checkout and tracking". Hours: The London working day. Focus: Checkout conversion, consent and tracking, Klarna and Clearpay. Billing: GBP.
- Layout: 3 columns on desktop, 1 column on mobile.

10. Team crew row: replace "UI/UX design" and "Engineering" with "Web development: Shopify, custom builds and integrations" and "AI and automation: Agents, sync and reconciliation". Keep the two lead cards as they are.

11. Fit list, good fit:
- "Ecommerce founders and growth leads in Australia, the US and the UK"
- Brands with traffic that is not converting
- Teams spending on ads without clear payback
- "Brands whose Shopify, ERP and accounting tools do not agree"
- "Brands planning a redesign or replatform"

12. FAQ changes:
- Is the call free: replace "in INR or USD" with "in USD, AUD or GBP".
- How much does it cost: "The 2-minute video teardown is free. The Revenue Leak Audit is $1,500. Fixed-price sprints start at $3,900 and monthly retainers at $1,500. Larger builds and AI agents are quoted after the first call, with a written proposal."
- Replace the "Do you work with US brands from India?" question with "Do you work with Australian, UK and US brands from India?": "Yes. Sydney afternoons, the London working day and US mornings all overlap with our hours, so calls happen in your daytime and work moves on overnight. The picker shows each slot in your time zone and ours."
- Add "Do you use AI on client work?": "Yes, for first-pass audits, drafts and the agents we build. A person reviews every finding and approves anything that touches money, prices or orders. Client data only goes into tools covered by a data processing agreement."
- Add "Can you help with rules like the surcharge ban or accessibility?": "We implement the changes: checkout, theme, tracking and invoices. Your lawyer or adviser confirms what applies to you. We do not give legal advice."

13. Case studies page
- Same header/footer/method changes.
- Keep the honest "Result coming soon" placeholders, but change the four placeholder cases to:
  - Australia · CRO · Card surcharge after the 1 Oct 2026 ban
  - US · CRO · Checkout friction (35% Baymard)
  - UK · Performance marketing · Tracking lost to consent (benchmark: "Consent Mode v2 and server-side tracking set-up", no number)
  - US · Website development · Slow mobile store (8.4% Deloitte/Google)
- Replace the India COD benchmark card with the RBA surcharge card from item 5.
- Meta text: no India.

14. AI call prep and emails: in prep.functions, followup.functions and the email templates, remove India/INR/COD/RTO assumptions. Prep should consider the lead's market (Australia, New Zealand, US, UK, Canada, Other) and our services list above. Follow-up email currency follows the market (AUD for Australia and New Zealand, GBP for UK, USD otherwise).

15. Tests and checks
- Update src/test/marginwise.test.ts for the new slots: the 5 IST slots convert to the right UTC times, the daytime filter hides the late-night Sydney slots and the previous-evening 21:30 US Eastern slot, and slotText uses the new format.
- Keep the calendar template test (ctz can stay Asia/Kolkata).
- Run the full test suite and a type check, fix anything that fails, and confirm the home page, /pricing, /case-studies, booking submission and team pages still render on desktop and mobile in light and dark mode.
- At the end, list every file you changed and the test results.

16. Google Meet on every booking
- In submitBooking, create the Google Calendar event with a Google Meet link: conferenceData.createRequest must include conferenceSolutionKey { type: "hangoutsMeet" } plus the existing requestId, and keep conferenceDataVersion=1 and sendUpdates=all.
- Read the created event's response and take the Meet link (hangoutLink, or the video entry point in conferenceData.entryPoints). Store it on the booking_requests row (add a nullable meet_link text column with a migration) and return it from submitBooking.
- Put the Meet link in the new-booking-lead email to the team inboxes.
- Send the lead a short confirmation email ("Your Marginwise call request": slot in their market's time zone and in IST, the Meet link, and "We confirm the time by email within one working day"). Use the existing email system and an idempotency key.
- On the booking success screen, show "Your Google Meet link is in the calendar invite we just sent" with the link itself when available. Keep the existing Google Calendar template link and email-copy fallback for when calendar creation fails, and say the meeting link follows by email in that case.
- If the calendar connector key is missing or the API call fails, the booking must still save and the team email must still send (current behaviour); log the error.
- Hero chip "Google Meet or Zoom" becomes "Google Meet".
- In the team leads view, show the Meet link for each booking that has one.
- Add a test for the Meet link extraction from a sample Calendar API response (hangoutLink present, entryPoints only, and neither).

17. Team names: keep "Velmurgan" as the display name everywhere; the inbox velmoorthy65@gmail.com and the admin setup are correct, do not change them.

18. Quality bar (we audited the HTML version with our own crawler and fixed these; do the same in the app)
- Accessibility: day buttons and the logo link must not carry an aria-label that differs from their visible text (axe rule label-content-name-mismatch). Run an axe check on home, /pricing and /case-studies: zero serious or critical violations.
- Structured data on the home page: JSON-LD with "@type": ["Organization", "ProfessionalService"] (name, url https://marginwise.in/, description, founder Abhimanyu Sharma, areaServed AU/US/GB, offers: Revenue Leak Audit USD 1500, Fixed-price sprint from USD 3900, Monthly retainer from USD 1500 per month) and a FAQPage built from the FAQ items on the page.
- public/robots.txt: allow all, and explicitly allow GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot and Google-Extended; point to the sitemap.
- public/llms.txt: a plain summary of Marginwise, the Find, Fix, Grow offers with prices, the five services, and the booking link (https://marginwise.in/#book).
- Canonical and og:url should use https://marginwise.in/ if that custom domain is connected to this project; otherwise keep the lovable.app URL.
- No horizontal scroll at 375px width; Lighthouse mobile performance 90+ and accessibility 95+ on the home page.

19. India added back (sent to Lovable as a follow-up message on 18 Oct): India as a fourth market with an IST time-zone button, INR calculator, India service stacks, the Shipway COD card as a fifth evidence card, an India "Where we work" card (2x2 layout), INR billing, and IST default for visitors in India.
