# Lovable prompt: full customer-friendly site with every service (24 Oct 2026)

Send after the queued audit fixes (privacy, terms, shared header and footer). Text below is sent as is.

```
Make marginwise.in a customer-friendly site that covers every Marginwise service. This builds on the previous request (privacy, terms, shared header and footer). Keep the design language, prices (src/lib/pricing.ts), market switcher, booking, Calendar/Meet, emails, teardown lead form, calculators, auth and team area working. Never invent client results, testimonials, client logos, team size or awards. No superlatives such as "#1" or "best". Plain English, short sentences.

GOAL
A store owner in Australia, the US, the UK or India should be able to: (1) see which service fixes their problem within 10 seconds, (2) understand what they get, how long it takes and what it costs, (3) try something free (instant check, calculator or teardown), (4) book a call. Australia is the first market, so ?market=au and /au must work well.

1. CONTENT AS DATA
Put all service, solution, industry and market content in typed config files (src/content/services.ts, solutions.ts, industries.ts, markets.ts) and render every page from shared templates. This keeps pages consistent and cheap to extend. Each page has its own title, meta description, canonical, Open Graph tags, BreadcrumbList JSON-LD, and appears in sitemap.xml and llms.txt.

2. NAVIGATION
Header: Services (menu: the 5 services below plus "All AI solutions"), Industries, Pricing, Calculators, Free store check, and the button "Book a call". On mobile, one accessible menu. Footer: all service, solution, industry and market pages, plus Pricing, Calculators, Benchmarks and method, How we work, About, Privacy, Terms, Refunds and cancellations, Service delivery, and email abhimanyu@marginwise.in.

3. "WHERE SHOULD I START?" GUIDE (home page, just under the hero, and on /services)
Three quick taps, no typing: "What do you want most?" (More sales from ads / More visitors buying / A faster or new site or app / Show up in Google and AI answers / Less manual work), "Where do you sell?" (the 4 markets), "Monthly online revenue" (the same bands as the lead form, in the market's currency). Result card: the recommended service, the matching calculator link, the plan that usually fits with its price from pricing.ts, and two buttons: "Get a free teardown" and "Book a call". Pure front-end logic, no data stored.

4. SERVICE HUB AND 5 SERVICE PAGES
/services lists the 5 services as cards (problem in one line, what you get, price from, link).
Each service page uses one template, in this order: hero (who it's for, one-line promise, two CTAs); "Sound familiar?" (4 symptoms); "What we do" (deliverables); "How it works" (Find, Fix, Grow with timings); "What it costs" (market-aware plan prices from pricing.ts, plus "larger work quoted after the call"); the related calculator (link to /calculators#id, labelled as a planning scenario); 5 FAQs (visible plus FAQPage JSON-LD); related services; CTA band. Service JSON-LD with areaServed AU, US, GB, IN.

a) /services/performance-marketing — "Paid ads planned around profit, not ROAS."
Symptoms: ROAS looks fine but profit doesn't move; costs per order keep rising; nobody can say which ads make money after product cost, fees and returns; creative is tired.
What we do: profit-after-ads model and break-even ROAS per product; account restructure on Meta, Google and TikTok; creative testing plan and new ad creatives; tracking and conversion API checks; monthly profit report.
Calculator: #profit. FAQs: which platforms (Meta, Google, TikTok); do you need my ad account access (read-only first, then admin if hired); minimum ad spend (we'll say on the call whether ads make sense yet); who owns the account (you do, always); how results are reported (profit after ads each month).

b) /services/cro — "More of your visitors buying, without more ad spend."
Symptoms: traffic but few orders; carts abandoned at checkout; mobile product pages hide price, delivery or Afterpay/Klarna; surprise costs at checkout.
What we do: funnel and checkout audit; product page and checkout fixes; A/B tests with a written hypothesis; market fixes such as the Australian surcharge ban and India COD and returns; accessibility checks.
Facts with sources (already on the site): 70.22% average cart abandonment (Baymard); 35% potential checkout conversion gain (Baymard).
Calculator: #lift, #surcharge, #cod. FAQs: how long tests run; do you work on Shopify only (Shopify, Shopify Plus and custom stores); will tests slow my site (no, we check speed); what if a test loses (we stop it and keep the learning); do you need developer access (collaborator access on Shopify).

c) /services/web-and-app-development — "Shopify, custom builds and apps, delivered at a fixed price."
Symptoms: the theme is slow or hard to change; a migration keeps getting delayed; orders, stock or accounts don't sync; you need an app or customer portal (wholesale ordering, subscriptions, bookings).
What we do: Shopify and Shopify Plus builds and theme rebuilds; migrations (WooCommerce, Magento, custom to Shopify); custom web apps and mobile apps for customer portals, wholesale ordering and internal tools; ERP and accounting integrations (Xero, MYOB, Cin7, NetSuite, QuickBooks); speed and Core Web Vitals work; landed-cost and tariff margin model for US sellers.
Fact: 0.1 s faster mobile site, 8.4% more retail conversions (Deloitte and Google, 2020).
Calculator: #speed, #landed. FAQs: fixed price or hourly (fixed scope and price, 50% upfront, 50% on acceptance); who owns the code (you do); do you build mobile apps (yes, scoped after a call); how long a build takes (quoted per project); support after launch (optional retainer).

d) /services/seo-and-ai-search — "Be found on Google and named in AI answers."
Symptoms: few organic visits; product pages don't rank; ChatGPT, Perplexity or Google AI answers name competitors, not you; no structured data.
What we do: technical SEO audit; product and collection page fixes; structured data (Product, Offer, Review, FAQ, Organization); AI search visibility tracking (a fixed set of buying questions checked monthly across AI assistants); content plan for the questions shoppers ask.
Calculator: #search. FAQs: how long SEO takes (months, not weeks); can you guarantee rankings (no one honestly can); what is AI search visibility; do you write content (yes, reviewed by you before publishing); do you build links (only earned mentions, no paid link schemes).

e) /services/ai-solutions — "AI that takes boring work off your team, with a person approving anything that touches money."
Symptoms: the inbox is full of "where is my order?"; orders fail to sync and get fixed by hand; payouts don't match the bank; calls and leads go unanswered after hours.
What we do: the 9 solutions below as cards, each linking to its own page. Principles box: the AI says it is an AI; it uses only your data and price lists; anything that changes orders, prices or money waits for a person; client data only goes into tools covered by a data processing agreement.
Calculator: #support, #receptionist, #ops.

5. AI SOLUTION PAGES (/ai-solutions/<slug>, one template)
Sections: the problem, what it does, what it connects to, what stays with a person, a short demo description (no fake screenshots of client data), "Quoted after a 30-minute call", FAQs (3), CTA. Pages:
- order-status-support-agent: answers "where is my order", returns and address-change questions from Shopify order data on email and chat; hands anything unusual to your team. Connects: Shopify, Gorgias, Zendesk, Help Scout, email.
- ai-phone-receptionist: answers calls and texts 24/7, says it is an AI, books jobs, texts back missed calls, escalates emergencies. For trades, clinics and service businesses. Fact: only 52% of US home-services calls are answered by a person (Invoca 2026).
- erp-sync-exception-agent: watches Shopify-to-ERP sync, labels each failure (missing SKU, duplicate, tax code), fixes safe ones, queues the rest for approval, sends a morning summary. Connects: Cin7, Unleashed, MYOB, Xero, NetSuite, QuickBooks, Odoo.
- payout-reconciliation-agent: matches Shopify Payments, PayPal, Afterpay, Zip, Klarna and Stripe payouts, fees and refunds to Xero or QuickBooks; drafts journals for approval.
- wholesale-order-agent: reads emailed purchase orders, checks them against your price list and terms, flags mismatches, creates draft orders in Shopify B2B or the ERP.
- lead-response-agent: scores and routes new leads in minutes, drafts the first reply, logs activity in the CRM.
- review-and-local-presence: review requests after each job, reply drafts, Google Business Profile upkeep, suburb pages. Fact: 68% of consumers only use businesses rated 4 stars or more (BrightLocal 2026).
- ai-search-visibility-tracker: checks a fixed list of buying questions across AI assistants each month and reports where you are named, with fixes.
- surcharge-margin-rescue (Australia): removes leftover card surcharge logic and text, models margin by product after card fees, reprices or steers payment mix. Source: RBA media release 2026-10.

6. INDUSTRY PAGES (/industries/<slug>, one template)
fashion-and-apparel, jewellery, beauty-and-skincare, home-and-decor, health-and-supplements, trades-and-home-services. Each: 4 common problems for that category (returns and sizing; high-value trust and photography; subscriptions and reviews; bulky shipping and delivery dates; claims and compliance copy; missed calls and quotes), the services and AI solutions that fit, the most useful calculator, and the CTA. No client names until we have permission.

7. MARKET PAGES (/au, /us, /uk, /in)
Each sets the market (prices, currency, booking time zone) and shows: 3 market problems with sources (AU: surcharge ban, Sendle closure, Afterpay and delivery expectations; US: tariffs and landed cost, accessibility; UK: checkout and tracking consent; IN: COD and returns 26% (Shipway), prepaid incentives); the services that fit; local prices; overlap hours ("Sydney afternoons", "London working day", "US mornings", "same day in India"); CTA. Use these as ad landing pages, so keep each fast and focused, with the teardown form on the page.

8. FREE STORE CHECK (/free-store-check, also a URL box in the home hero)
"Enter your store URL." A server function fetches only the public home page (5 s timeout, max 2 MB, https only, block private and internal IP ranges, rate limit 10 checks per IP per hour) and runs about 10 simple checks: HTTPS; response time; Shopify detected; title and meta description present; Product or Organization structured data; robots.txt allows Googlebot and AI crawlers; viewport tag; a card surcharge mention (Australia); a buy-now-pay-later mention; image count and total size of the largest images. Show a score out of 100, a green, amber or red list, and "The 3 fixes we'd look at first" in plain English. Then two buttons: "Get the free 2-minute video teardown" (pre-fills the lead form with the URL) and "Book a call". Say clearly: "An automated first look at one page. A person reviews your store for the teardown." Don't store the check unless the visitor submits the lead form. Unit-test the checks with saved HTML fixtures.

9. HOW WE WORK (/how-we-work) AND ABOUT (/about)
How we work: discovery call → written scope and fixed price → kickoff → weekly written update → acceptance → optional retainer. Show what the client gets at each step and the response time (one working day). About: Abhimanyu Sharma (lead) and Velmurgan (paid media), based in India, working with 4 markets; "Why fixed prices"; "Why profit, not ROAS"; how we use AI and how we protect data. No invented bios, numbers or logos.

10. TRUST WITHOUT INVENTED PROOF
A facts bar on the home page with only true facts: "4 markets", "Fixed, published prices", "Free teardown within 3 working days", "A person checks every AI output". A testimonial and logo component that stays hidden until real entries are added to config (each needs the client's written permission flag set to true).

11. POLICIES
Add /refunds-and-cancellations (audit: full refund if cancelled before work starts; sprints: 50% upfront covers work started, the remainder due on acceptance; retainers: 3-month minimum, then 30 days' notice) and /service-delivery (services are delivered online; timelines are set in the written proposal; deliverables by email and shared folders). Link both from the footer and the pricing page.

12. HOME PAGE ORDER
Hero with the URL box → "Where should I start?" guide → the 5 services → facts bar → Where revenue leaks (existing sources) → pricing → calculators teaser → teardown form → how we work → team → FAQ → booking. Keep it scannable on a phone.

13. QUALITY BAR
Mobile-first; every page passes axe with no serious or critical issues at 375px and 1280px in light and dark mode; no horizontal scroll; Largest Contentful Paint under 2.5 s on the home page in a mobile Lighthouse run; every internal link resolves; every JSON-LD block parses; every page in the sitemap and llms.txt. Unit tests for the guide's recommendation logic, the store-check functions and the content config (every service, solution and industry has title, meta, FAQs and a CTA).

Report the files changed, the new routes, test results and the Lighthouse and axe results. Do not publish.
```
