"""Calendar update of 17 Oct 2026, after the market research and the solution builds.

- Replaces four unposted posts with research-led ones (AU surcharge ban, audit crawler demo, US tariffs, ERP sync agent).
- Adds weeks 6-9 (16 Nov to 13 Dec): Germany and Canada (wave 2), Black Friday and Cyber Monday, and solution demos.
- Saudi Arabia starts in the next calendar (wave 3, from 18 Dec).
Imported by build_calendar.py on top of posts_v3.
"""
from posts_v3 import POSTS as V3_POSTS, REC as V3_REC, BATCHES as V3_BATCHES
from posts_v3 import AUDIT, PROFIT, GEO, AI, SPEED, FLOWS, CHECK, BFCM

# (month, day, format, pillar, market, hook, outline, caption, cta, magnet, trial, pin, batch)
REPLACE = {
    (10, 20): (10, 20, "Reel (10s)", "CRO", "AU",
     "[Brand] does everything right on this page except one thing.",
     "Phone screen-record a well-known Australian brand's mobile product page. Two strengths, one leak (card surcharge "
     "still showing after the 1 Oct ban, shipping cost hidden until checkout, Afterpay message buried, reviews too low, "
     "or a slow image). What that leak costs. Set the store to Australia and A$ before recording.",
     "A product page teardown of an Australian brand: what converts, what leaks, and what the leak costs.\n\n"
     "Want this for your store? Comment AUDIT.\n\n#shopifyaustralia #ecommerceaustralia #cro",
     "AUDIT", AUDIT, "Yes", "No", "Batch 1"),
    (10, 27): (10, 27, "Reel (10s)", "Performance marketing", "AU",
     "Since 1 October, this line is banned in Australian checkouts.",
     "Phone screen-record a checkout (demo store) showing a '1.5% card surcharge' line, then the same checkout without it. "
     "The RBA ban on surcharging Visa, Mastercard and eftpos started 1 Oct 2026. Two things follow: the line must go, "
     "and the fee lands in your margin unless prices or payment mix change. Show a payment-fee margin table with one SKU "
     "in red.",
     "The RBA ban on card surcharges started on 1 October. If your checkout still adds a card fee, it has to go.\n\n"
     "Then the real question: who pays the fee now? Absorb it, reprice, or steer customers to cheaper ways to pay.\n\n"
     "Comment PROFIT for the calculator and run your own card fees through it.\n\n#ecommerceaustralia #shopifyaustralia #payments",
     "PROFIT", PROFIT, "Yes", "No", "Batch 2"),
    (11, 1): (11, 1, "Reel (10s)", "AI solutions", "All",
     "We built a tool that audits a store in two minutes.",
     "Screen-record the Marginwise audit crawler running on the demo store (terminal command, then the report): score out "
     "of 100, red rows for speed, trackers firing before consent, missing product schema, and one market rule (AU surcharge "
     "or German Impressum). End: a person checks every finding before it goes to you.",
     "Every free teardown starts with our audit tool: speed, accessibility, tracking, checkout, local rules and AI search "
     "readiness, scored in two minutes.\n\nThen a person checks every finding and picks the one fix that matters most.\n\n"
     "Comment AUDIT and we will run it on your store.\n\n#ai #cro #shopify",
     "AUDIT", AUDIT, "Yes", "Yes", "Batch 2"),
    (11, 8): (11, 8, "Reel (10s)", "Performance marketing", "US",
     "Four tariff changes in twelve months. Is your price still right?",
     "Screen-record a landed-cost table for 5 demo SKUs: product cost, duty, tariff surcharge, freight, then margin. Change "
     "the tariff input and watch two SKUs turn red. Point: price on today's landed cost, not last quarter's. No legal or "
     "customs advice; rates come from your broker.",
     "De minimis is gone and tariffs changed four times in a year. Most brands are still pricing on an old landed cost.\n\n"
     "Run your SKUs through today's numbers before Black Friday discounts eat what is left.\n\n"
     "Comment PROFIT for the calculator.\n\n#tariffs #ecommerce #shopify",
     "PROFIT", PROFIT, "No", "No", "Batch 3"),
    (11, 12): (11, 12, "Reel (10s)", "AI solutions", "All",
     "Every morning, someone fixes these by hand.",
     "Screen-record the sync exception agent demo (fixture data): a list of failed Shopify-to-ERP orders, the agent labelling "
     "each cause (missing SKU, duplicate, tax code), safe fixes retried, two waiting for approval, then a 7am Slack summary "
     "'12 fixed, 2 need you'.",
     "If your Shopify orders fail to reach Cin7, NetSuite, Xero or MYOB, someone is fixing them by hand every morning.\n\n"
     "An AI agent can sort the failures, fix the safe ones and leave the rest for a person to approve.\n\n"
     "Comment AI for 10 AI builds worth starting with.\n\n#ai #shopify #erp",
     "AI", AI, "Yes", "No", "Batch 3"),
}

NEW_POSTS = [
    # Week 6
    (11, 17, "Reel (10s)", "CRO", "DE",
     "Selling to Germany? Since 19 June your shop needs this button.",
     "Phone screen-record a German shop's footer and account area looking for the withdrawal button (Widerrufsbutton), "
     "then the two-step withdrawal flow on the demo store. Mention: public pages only, no shop named, and your lawyer "
     "confirms the wording.",
     "Since 19 June 2026, online shops selling to German consumers need a withdrawal button: a two-step way to cancel a "
     "purchase during the withdrawal period.\n\nMissing it is an easy target for warning letters. Your lawyer confirms "
     "the wording; we build it into the theme.\n\nComment AUDIT and we will check your shop.\n\n#ecommercegermany #shopify #berlinstartups",
     "AUDIT", AUDIT, "Yes", "No", "Batch 4"),
    (11, 19, "Reel (10s)", "Performance marketing", "CA",
     "Shipping to the US from Canada? Your customer might be paying at the door.",
     "Screen-record a demo checkout for a US customer from a Canadian store: no duties shown, then a mock delivery notice "
     "with brokerage and duty owed. Then the same checkout with duties-included pricing. Mention de minimis is gone and "
     "tariffs rose on many Canadian goods; your broker confirms rates.",
     "With de minimis gone, US customers of Canadian stores can be hit with duties and brokerage at the door. Many never "
     "order again.\n\nDuties-included pricing fixes the surprise, and shows you which SKUs still make money.\n\n"
     "Comment PROFIT for the calculator.\n\n#shopifycanada #ecommercecanada #crossborder",
     "PROFIT", PROFIT, "Yes", "No", "Batch 4"),
    (11, 21, "Carousel (7 slides)", "CRO", "All",
     "Black Friday week: 5 checks for the night before",
     "S1 hook. S2 place a test order on mobile with each payment method. S3 check discount codes and automatic discounts "
     "stack the way you planned. S4 shipping cut-off dates shown on product and cart pages. S5 tracking fires once per "
     "order (no double purchases in GA4 or Meta). S6 someone on DMs and email on the day. S7 CTA.",
     "Five checks to run the night before Black Friday, Click Frenzy or Cyber Monday. None of them need a developer.\n\n"
     "Save this for next week. Comment BFCM for the full checklist and timeline.\n\n#blackfriday #bfcm #shopify",
     "BFCM", BFCM, "No", "No", "Design 2"),
    (11, 22, "Reel (10s)", "Website development", "All",
     "Your store on Black Friday: test these 3 pages before the traffic does.",
     "Screen-record PageSpeed (mobile) on the demo store's home, collection and product pages, then an app list showing "
     "two unused apps still loading scripts. Fix: remove them before the sale.",
     "Traffic spikes expose slow pages. Test home, collection and product pages on mobile this week, and remove apps you "
     "no longer use.\n\nComment SPEED and we will check your store before the sale.\n\n#shopifyspeed #blackfriday #cro",
     "SPEED", SPEED, "No", "No", "Batch 4"),
    # Week 7
    (11, 24, "Reel (10s)", "AI solutions", "All",
     "This is why month-end takes three days.",
     "Screen-record the payout reconciliation demo (fixture data): Shopify, PayPal and Afterpay payouts next to the bank "
     "feed, nothing lines up; the matcher runs, 412 of 418 matched with fees and refunds split out; the six exceptions "
     "explained in plain English. Demo data only, labelled.",
     "Shopify Payments, PayPal, Afterpay and Klarna payouts rarely match the bank feed line for line. That is why month-end "
     "drags.\n\nWe match every payout to the bank and explain what is left in plain English.\n\n"
     "Comment AI for 10 AI builds worth starting with.\n\n#xero #shopify #ecommercefinance",
     "AI", AI, "Yes", "No", "Batch 5"),
    (11, 26, "Reel (10s)", "Retention", "US",
     "Thanksgiving orders are in. Send this email before the box arrives.",
     "Screenshot an order confirmation and a 'your order is on its way' email from your own inbox (details blurred). Show "
     "one change: tell the customer how to use the product and when to expect it, not just a receipt.",
     "The emails after a Black Friday order decide whether that customer buys again in January.\n\n"
     "Start with the order confirmation and the shipping email.\n\nComment FLOWS for the post-purchase checklist.\n\n"
     "#klaviyo #bfcm #emailmarketing",
     "FLOWS", FLOWS, "No", "No", "Batch 5"),
    (11, 27, "Reel (10s)", "CRO", "All",
     "It's Black Friday. Three fixes you can still ship in an hour.",
     "Phone screen-record three quick fixes on the demo store: free-shipping threshold shown in the cart, express pay "
     "buttons above the fold in checkout, and a delivery cut-off banner. 3 seconds each.",
     "Three changes you can still make today without a developer: show the free-shipping threshold in the cart, put "
     "express pay first, and add a delivery cut-off banner.\n\nComment BFCM for the full checklist.\n\n#blackfriday #bfcm #shopify",
     "BFCM", BFCM, "No", "No", "Batch 5"),
    (11, 29, "Carousel (7 slides)", "Website development", "DE",
     "From 1 January 2027, a PDF invoice is not enough in Germany",
     "S1 hook. S2 who: businesses above EUR 800K turnover must issue B2B e-invoices from 1 Jan 2027, all businesses from "
     "2028. S3 what counts: XRechnung or ZUGFeRD; a plain PDF does not. S4 where Shopify stores get stuck: no native DATEV "
     "link, B2B orders mixed with B2C. S5 what to set up: invoice output, DATEV export, payout matching. S6 confirm the "
     "rules with your tax adviser. S7 CTA. Source line: German Finance Ministry letter of 15 Oct 2025.",
     "Germany's B2B e-invoicing rules start biting on 1 January 2027. If you sell to businesses from a Shopify or Shopware "
     "store, a PDF invoice will no longer count.\n\nYour tax adviser confirms what applies to you; we build the invoice "
     "output and the DATEV export.\n\nComment AUDIT and tell us your setup.\n\n#erechnung #ecommercegermany #shopify",
     "AUDIT", AUDIT, "No", "No", "Design 2"),
    # Week 8
    (12, 1, "Reel (10s)", "Performance marketing", "All",
     "Cyber Monday is over. Read these 4 numbers before you celebrate.",
     "Screen-record the PROFIT calculator with demo BFCM numbers: revenue up, but discount depth, returns allowance, ad "
     "cost and payment fees take contribution per order down. Four numbers: contribution per order, new-customer share, "
     "discount depth, returns rate.",
     "Record revenue does not mean record profit. Before you celebrate, check contribution per order, new-customer share, "
     "discount depth and returns.\n\nComment PROFIT for the calculator.\n\n#cybermonday #bfcm #ecommerce",
     "PROFIT", PROFIT, "Yes", "No", "Batch 6"),
    (12, 3, "Reel (10s)", "AI solutions", "US",
     "Google now charges some businesses for calls they miss.",
     "Screen-record the AI receptionist demo: a missed call at 9:47pm, a text-back within a minute, then the AI answering "
     "a second call, saying it is an AI, checking the suburb and booking a job into a demo calendar. Mention Google Local "
     "Services Ads started billing for missed calls on 1 Oct 2026. Demo line only.",
     "Since 1 October, Google bills Local Services Ads advertisers for missed calls during business hours. Every missed "
     "call now costs twice.\n\nAn AI receptionist answers, says it is an AI, books the job and texts back the calls you "
     "miss.\n\nComment AI to see it on a test line.\n\n#smallbusiness #hvac #ai",
     "AI", AI, "Yes", "No", "Batch 6"),
    (12, 5, "Carousel (6 slides)", "CRO", "CA",
     "Selling into Quebec: what Bill 96 changes for your store",
     "S1 hook. S2 French must be available to Quebec customers on your storefront and product information. S3 since "
     "1 June 2025, generic words on packaging also need French; grace period to 1 June 2027 for older stock. S4 Law 25: "
     "consent before non-essential cookies. S5 what to do: French storefront with human-reviewed translation, consent "
     "banner, packaging to your lawyer. S6 CTA. Not legal advice.",
     "Quebec has its own rules for language and privacy. If you sell there, check your storefront, your product data and "
     "your cookie banner.\n\nPackaging and legal wording go to your lawyer; we build the French store and the consent "
     "setup.\n\nComment AUDIT and we will check your store.\n\n#quebec #shopifycanada #ecommercecanada",
     "AUDIT", AUDIT, "No", "No", "Design 2"),
    (12, 6, "Reel (10s)", "SEO/AEO/GEO", "All",
     "Three page changes that make AI assistants quote your store.",
     "Screen-record the demo store's product page before and after: answers to real questions on the page (sizing, "
     "materials, delivery, returns), Product and FAQ schema validated in Google's Rich Results Test, and robots.txt "
     "allowing AI crawlers. No claims about ranking results.",
     "AI assistants quote pages they can read and trust. Three changes help: answer real questions on the page, add "
     "Product and FAQ schema, and let AI crawlers in.\n\nComment GEO for the full checklist.\n\n#aeo #geo #seo",
     "GEO", GEO, "No", "No", "Batch 6"),
    # Week 9
    (12, 8, "Reel (10s)", "CRO", "DE",
     "'Klimaneutral' is now a risky word on German product pages.",
     "Screen-record the compliance copy auditor demo on fixture copy: a product page with a 'klimaneutral' badge, the "
     "finding (rule, risk, suggested rewrite), and a lawyer sign-off column. Rules since 27 Sep 2026 limit offset-based "
     "climate claims and self-made labels. Not legal advice.",
     "Since 27 September, claims like 'klimaneutral' based on offsetting and self-made eco labels are a risk in Germany.\n\n"
     "We scan your product pages and ads, flag each claim with a safer rewrite, and your lawyer signs off.\n\n"
     "Comment AUDIT and we will scan your shop.\n\n#greenclaims #ecommercegermany #berlinstartups",
     "AUDIT", AUDIT, "Yes", "No", "Batch 7"),
    (12, 10, "Reel (10s)", "AI solutions", "AU",
     "Christmas orders plus Cin7 equals oversells. Here's the 7am fix.",
     "Screen-record the sync exception agent demo again, framed for Christmas peak: stock mismatch errors, the agent "
     "flagging oversell risk and holding those SKUs for approval, then the Slack summary. Demo data only.",
     "Peak season is when Shopify and your inventory system disagree most, and every mismatch is an oversell waiting to "
     "happen.\n\nAn AI agent watches the sync, fixes what is safe and flags the rest before the morning rush.\n\n"
     "Comment AI for 10 AI builds worth starting with.\n\n#shopifyaustralia #cin7 #ecommerceaustralia",
     "AI", AI, "No", "No", "Batch 7"),
    (12, 12, "Carousel (7 slides)", "Proof and trust", "All",
     "What changed for online stores in 2026, by country",
     "S1 hook. S2 Australia: card surcharge ban (1 Oct), subscription and drip-pricing rules from 1 Jul 2027. S3 US: "
     "de minimis gone, tariff changes, accessibility lawsuits. S4 UK: keep this slide general unless a rule is checked "
     "before posting. S5 Germany: withdrawal button (19 Jun), green claims (27 Sep), e-invoicing (1 Jan 2027). S6 Canada: "
     "Quebec French and cookie consent. S7 CTA. Source line on every slide; not legal advice.",
     "The rules for online stores changed a lot this year. One slide per country, with the date each change starts.\n\n"
     "Save this for your 2027 planning. Comment AUDIT and we will check your store against them.\n\n#ecommerce #shopify #compliance",
     "AUDIT", AUDIT, "No", "No", "Design 2"),
    (12, 13, "Reel (10s)", "Proof and trust", "All",
     "What we found auditing stores this quarter.",
     "Only post with real numbers: the count of audits run since October and the three most common findings, anonymised. "
     "If fewer than 5 audits are done, swap for a teardown of a German or Canadian store instead.",
     "The leaks we found most often this quarter, with no names attached.\n\nComment AUDIT to get yours checked before "
     "January.\n\n#ecommerce #cro #shopify",
     "AUDIT", AUDIT, "No", "No", "Batch 7"),
]

NEW_REC = {
    (10, 27): ("Phone screen-record the demo store checkout with a '1.5% card surcharge' line, then without it; then the payment-fee margin table.",
               "Open on the ban date; end on 'who pays the fee now?'.",
               "Red strike-through on the surcharge line; one SKU row highlighted red."),
    (11, 1): ("Screen-record the terminal running the audit crawler on the demo store, then scroll the HTML report.",
              "Tool first, person second: 'a person checks every finding'.",
              "Zoom on the score, then on three red rows."),
    (11, 8): ("Screen-record a landed-cost sheet for 5 demo SKUs; change the tariff input live.",
              "Lead with 'four changes in a year'; end on 'price on today's landed cost'.",
              "Two SKUs flip to red; on-screen note 'rates from your broker'."),
    (11, 12): ("Screen-record the sync exception agent demo output (fixture data) and a mock Slack message.",
               "Problem, what the agent does, what still needs a person.",
               "Labels on each error type; '12 fixed, 2 need you' as the end frame."),
    (11, 17): ("Phone screen-record a German shop footer and account area (public, unnamed), then the demo store's two-step withdrawal flow.",
               "Date first (19 June), then the fix; say 'your lawyer confirms the wording'.",
               "Circle where the button should be; blur the shop's logo."),
    (11, 19): ("Screen-record a US checkout on the demo store without duties, a mock delivery notice, then the duties-included version.",
               "The surprise at the door, then the fix; 'your broker confirms rates'.",
               "Mock notice clearly labelled 'example'."),
    (11, 22): ("Screen-record PageSpeed mobile on three demo store pages and the installed apps list.",
               "Three pages, one culprit, one fix.",
               "Score numbers large on screen."),
    (11, 24): ("Screen-record the payout reconciliation demo: inputs side by side, the match result, the exceptions summary.",
               "Pain, result, what is left.",
               "Counter '412 / 418 matched'; label 'demo data'."),
    (11, 26): ("Screenshot two order emails from your own inbox, blurred; mock up the improved version in Canva.",
               "Before and after; one change.",
               "Before/after split."),
    (11, 27): ("Phone screen-record three quick changes on the demo store.",
               "One line per fix; 'no developer needed'.",
               "Numbered labels 1-3."),
    (12, 1): ("Screen-record the PROFIT calculator with demo BFCM numbers.",
              "Revenue up, contribution down; the four numbers.",
              "Highlight each number as you name it."),
    (12, 3): ("Screen-record the receptionist demo: phone missed-call screen, text-back, call transcript, demo calendar.",
              "Lead with the Google change; the AI says it is an AI.",
              "Time stamp '9:47pm' on screen; 'demo line' label."),
    (12, 6): ("Screen-record the demo product page before and after, Rich Results Test, and robots.txt.",
              "Three changes, one per shot.",
              "Tick on each change."),
    (12, 8): ("Screen-record the compliance copy auditor output on fixture copy.",
              "Date, the risky word, the safer rewrite, lawyer signs off.",
              "Highlight the flagged phrase and the rewrite."),
    (12, 10): ("Screen-record the sync agent demo with stock-mismatch fixtures and the Slack summary.",
               "Peak season framing; what the agent holds for approval.",
               "'Held for approval' label on the risky SKUs."),
    (12, 13): ("Screen-record a tally of real audits (store names hidden) and anonymised screenshots of the top three findings.",
               "Use the real count; if under 5 audits, record a German or Canadian teardown instead.",
               "Counter for each finding."),
}

POSTS = [REPLACE.get((p[0], p[1]), p) for p in V3_POSTS] + NEW_POSTS
REC = {**V3_REC, **NEW_REC}

BATCHES = [b for b in V3_BATCHES if b[0] not in ("Batch 2", "Batch 3")] + [
    ("Batch 2", (10, 24), "AU surcharge ban; AI support assistant demo; audit crawler demo; email ratings; site speed",
     "Set up the Shopify development store with demo products, policies and a surcharge line to remove. Run the audit crawler on it.", "3 hours"),
    ("Batch 3", (11, 6), "US tariffs and landed cost; BNPL fees; ERP sync agent demo; audit roundup",
     "Prepare 5 demo SKUs for the landed-cost sheet. Run the sync exception agent on its fixtures.", "2 hours"),
    ("Batch 4", (11, 14), "Germany withdrawal button; Canada duties at the door; Black Friday page speed",
     "Find one public German shop (unnamed in the post) and set up a US checkout on the demo store.", "2 hours"),
    ("Batch 5", (11, 21), "Payout reconciliation demo; Thanksgiving email; Black Friday quick fixes",
     "Run the payout reconciliation agent on its fixtures; screenshot two order emails.", "2 hours"),
    ("Batch 6", (11, 28), "Cyber Monday numbers; AI receptionist demo; AI search page changes",
     "Set up a demo phone line for the receptionist (or record from fixtures). Add schema to the demo product page.", "3 hours"),
    ("Batch 7", (12, 5), "German green claims; Christmas oversells; quarter roundup",
     "Run the compliance copy auditor and sync agent on fixtures. Count the real audits done.", "2 hours"),
    ("Design 2", (11, 15), "Carousels: Black Friday night-before checks, German e-invoicing, Quebec Bill 96, 2026 rules by country",
     "Same template as earlier carousels. Every rule slide gets a date and a source line; mark 'not legal advice'.", "3 hours"),
]
