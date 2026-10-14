"""Builds the checklist PDFs (as HTML) for each Instagram comment keyword. Render with Chromium --print-to-pdf."""
import html, os, sys

OUT = sys.argv[1]
E = html.escape


def page(title, lede, sections, box=None, cta=None, sources="", keyword=""):
    parts = [f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{E(title)}</title>
<link rel="stylesheet" href="style.css"><style>h2{{margin-top:6mm}}</style></head><body>
<div class="brand"><b>Marginwise</b> &nbsp;|&nbsp; Growth for D2C and Shopify brands{(' &nbsp;|&nbsp; Keyword: ' + E(keyword)) if keyword else ''}</div>
<h1>{E(title)}</h1>
<p class="lede">{lede}</p>"""]
    if box:
        parts.append(f'<div class="box">{box}</div>')
    for head, intro, items in sections:
        parts.append(f"<h2>{E(head)}</h2>")
        if intro:
            parts.append(f"<p>{intro}</p>")
        parts.append('<ul class="check">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>")
    parts.append(f"""<div class="cta"><h3>{E(cta[0])}</h3><p>{cta[1]}</p></div>""")
    parts.append(f'<p class="src">{sources}</p></body></html>')
    return "\n".join(parts)


CTA_AUDIT = ("Want a second pair of eyes?",
             "Comment <b>AUDIT</b> on any @marginwise.in post or send your store link by DM. We send back a free "
             "2-minute video teardown within one working day. Or book a free 30-minute call at <b>marginwise.in</b>.")

docs = {}

docs["marginwise-store-leak-audit"] = page(
    "The D2C store leak audit: 30 checks before you spend more on ads",
    "Most stores lose revenue in the same places. Tick each check your store passes today. The ones you cannot "
    "tick are where your ad spend is leaking.",
    [
        ("1. Tracking you can trust", "If the numbers are wrong, every other decision is a guess.", [
            "Purchases in GA4 roughly match orders in Shopify for the same week",
            "Every paid link carries UTM tags, so you can see which campaign drove which order",
            "The Meta pixel and Conversions API record each purchase once, not twice",
            "You report revenue after returns and refunds, not just gross sales",
        ]),
        ("2. Landing and product page", "", [
            "Price, the main benefit and a delivery estimate are visible without scrolling on a phone",
            "Reviews or a star rating sit near the price, not only at the bottom of the page",
            "Size, fit or variant guidance is one tap away",
            "Shipping cost or the free-shipping threshold is shown before the cart",
            "The return or exchange policy is one tap away",
            "Add to cart stays visible (sticky) as the shopper scrolls on mobile",
            "Product images load quickly on a mobile connection",
        ]),
        ("3. Cart", "", [
            "The cart shows the full total including shipping before checkout",
            "Quantity and variant can be changed without leaving the cart",
            "Any upsell in the cart is relevant and does not push the shopper away from checkout",
            "Discount code field does not dominate the cart and send people off to search for codes",
        ]),
        ("4. Checkout", "Baymard Institute puts average cart abandonment at 70.22%; unexpected extra costs are among the most common reasons shoppers give.", [
            "Guest checkout is available; no forced account creation",
            "Express payment is offered: Shop Pay, Apple Pay or Google Pay; UPI for India",
            "No new cost appears at the last step",
            "Only the fields you really need are asked for",
            "Trust signals (secure payment, returns) sit close to the pay button",
            "A delivery date or window is shown before payment",
        ]),
        ("5. Speed", "", [
            "You have tested a product page on pagespeed.web.dev (mobile) in the last month",
            "Apps you no longer use are uninstalled and their leftover code removed",
            "Large images are compressed and below-the-fold images load lazily",
        ]),
        ("6. India: COD and RTO", "", [
            "You know your RTO rate on COD orders, by state or pin code",
            "Prepaid has a reason to choose it: a small discount, faster dispatch or a gift",
            "Risky COD orders are confirmed by WhatsApp or call before dispatch",
        ]),
        ("7. After the first order", "", [
            "The order confirmation email does more than show a receipt",
            "A review request goes out once the customer has had time to use the product",
            "A repeat-purchase or replenishment email is set up for your best repeat product",
        ]),
    ],
    box="<b>How to score it.</b> 26 to 30 ticks: your store is in good shape; look at ads and retention next. "
        "18 to 25: fix the checkout and product page items first. Under 18: start with tracking, because the other "
        "numbers cannot be trusted yet.",
    cta=CTA_AUDIT,
    sources="Sources: Baymard Institute, cart abandonment rate (average of 50 studies) and checkout usability research. "
            "This checklist is a starting point; the right order of fixes depends on your traffic and margins.",
    keyword="AUDIT")

docs["marginwise-shopify-speed-checklist"] = page(
    "Shopify speed checklist: 15 fixes, in order",
    "Fix speed before you buy more traffic. In a Deloitte and Google study of 37 brands, a 0.1-second improvement "
    "in mobile site speed lifted retail conversions by 8.4%.",
    [
        ("1. Measure first", "", [
            "Run pagespeed.web.dev on mobile for your home page, one collection page and your best-selling product page",
            "Write down the score and the Largest Contentful Paint (LCP) time for each",
            "Re-test after every change below, so you know which change helped",
        ]),
        ("2. Apps and scripts (usually the biggest win)", "", [
            "List every installed app and uninstall the ones you no longer use",
            "After uninstalling, check your theme code for leftover app snippets that still load",
            "Load chat widgets, pop-ups and survey tools after the shopper interacts, not on page load",
            "Check that each tracking pixel is installed once; duplicates slow the page and double-count sales",
        ]),
        ("3. Images and media", "", [
            "Compress large images before upload; product images rarely need to be wider than 2048 px",
            "Lazy-load images below the fold",
            "Avoid an autoplay video as the first thing on mobile; use a still image with a play button",
        ]),
        ("4. Theme", "", [
            "Use an up-to-date Online Store 2.0 theme and apply its updates",
            "Limit custom fonts to two families and the weights you actually use",
            "Avoid sliders and carousels at the top of the page on mobile",
        ]),
        ("5. Keep it fast", "", [
            "Check Core Web Vitals in Google Search Console once a month",
            "Test speed before and after installing any new app",
        ]),
    ],
    box="Shopify reports that almost 80% of Shopify stores pass all Core Web Vitals thresholds. If yours does not, "
        "the cause is usually apps and scripts added over time, not the platform.",
    cta=("Want us to check yours?",
         "Comment <b>SPEED</b> or send your store link by DM. We run the test and send you the top three things "
         "slowing it down within one working day."),
    sources="Sources: Deloitte Digital and Google, Milliseconds Make Millions (2020), via The Drum; Shopify, "
            "Ecommerce Growth Guide 2026 (Core Web Vitals figure).",
    keyword="SPEED")

docs["marginwise-roas-to-profit-checklist"] = page(
    "ROAS to profit: the 10-step checklist",
    "A 3x ROAS can still lose money. Use this with the Marginwise Profit Calculator to find what your ads "
    "actually earn after every cost.",
    [
        ("Gather your numbers (last full month)", "", [
            "Ad spend and the ROAS each platform reports",
            "Average order value after discounts",
            "Return and refund rate",
            "Product cost (COGS) as a percentage of revenue",
            "Shipping and fulfilment cost per order, and payment processing fees",
        ]),
        ("Run the calculator", "", [
            "Enter the numbers on the ROAS to Profit tab",
            "Set over-attribution to your own estimate; vendor estimates range from 20% to 40%",
            "Read three outputs: true ROAS, contribution per order after ads, and break-even platform ROAS",
        ]),
        ("Act on it", "", [
            "Set every campaign's target ROAS above your break-even, not at a round number",
            "Review contribution after ads every week alongside ROAS",
        ]),
    ],
    box="<b>Check over-attribution with your own data.</b> Compare platform-reported revenue with Shopify orders "
        "from the same campaigns, run a post-purchase 'how did you hear about us' survey, or hold out a region "
        "for two weeks.",
    cta=("Want us to run it with you?",
         "Comment <b>PROFIT</b> for the calculator, or book a free 30-minute call at <b>marginwise.in</b> and "
         "we will go through your numbers together."),
    sources="Over-attribution range: vendor estimates (Luca, citing the Ecom CFO 2026 report); not independently "
            "verified. Calculator defaults are an example store, not benchmarks.",
    keyword="PROFIT")

docs["marginwise-contribution-margin-checklist"] = page(
    "Contribution margin checklist for Indian D2C brands",
    "Revenue tells you how big you are. Contribution margin tells you whether each order makes money. Use this "
    "with the Marginwise Margin Calculator.",
    [
        ("Count every cost per order", "", [
            "Revenue excluding GST, at the price the customer actually paid",
            "Product cost (COGS) for delivered orders",
            "Ad cost per order placed, including orders that later return to origin",
            "Forward shipping and packaging on every order",
            "Return shipping and damaged stock on every RTO",
            "COD handling fees on delivered COD orders",
            "Payment gateway fees on prepaid orders",
            "Discounts and prepaid incentives",
        ]),
        ("Plan the cash", "", [
            "Add 18% GST to your ad budget in the cash-flow plan; if Meta or Google Ireland bills you, it is paid under reverse charge before you claim credit",
            "Confirm the GST treatment with your CA",
        ]),
        ("Decide", "", [
            "Work out contribution per SKU and per channel, not only for the store as a whole",
            "Test a prepaid incentive with the scenario column before rolling it out",
            "Review price or stop promoting SKUs with negative contribution",
        ]),
    ],
    box="Investors now ask Indian D2C founders for repeat rate, LTV:CAC and contribution margin rather than GMV "
        "(Inc42, D2C 3.0 report, 2026).",
    cta=("Want us to check your numbers?",
         "Comment <b>MARGIN</b> for the calculator, or book a free 30-minute call at <b>marginwise.in</b>."),
    sources="Sources: growthlife.in (GST reverse charge on foreign ad billing, Sep 2026); Inc42 D2C 3.0 report, via "
            "Backstage with Millionaires (Jun 2026). Not tax advice.",
    keyword="MARGIN")

docs["marginwise-cod-rto-playbook"] = page(
    "COD and RTO playbook: cut returns without killing COD",
    "Shipway's FY25 data shows 26% of cash-on-delivery orders in India return to origin, against under 2% of "
    "prepaid orders. Switching COD off everywhere loses good customers. Fix it where it hurts.",
    [
        ("1. Measure", "", [
            "Export the last 90 days of shipped orders with pin code, state, payment method and final status",
            "Run the Marginwise RTO Finder to rank states and pin codes by RTO rate and cost",
            "Only act on areas with enough orders to trust the rate (the sheet flags small samples)",
        ]),
        ("2. Prevent at checkout", "", [
            "Offer a reason to prepay: a small discount, a free gift or faster dispatch",
            "Validate addresses and pin codes before the order is placed",
            "Show a clear delivery date so buyers know when to expect it",
            "Consider a small advance (partial COD) for high-RTO pin codes",
        ]),
        ("3. Confirm before dispatch", "", [
            "Confirm COD orders by WhatsApp or automated call; hold unconfirmed orders",
            "Flag repeat refusers and suspicious orders (incomplete address, many units, new pin code)",
        ]),
        ("4. Recover in transit", "", [
            "Act on failed-delivery (NDR) alerts within 24 hours: call or message the buyer and request a reattempt",
        ]),
        ("5. Decide per area", "", [
            "Restrict COD or require confirmation only in the pin codes the RTO Finder flags",
            "Re-check the numbers every month; RTO patterns change with seasons and sales",
        ]),
    ],
    box="<b>What one RTO costs:</b> forward shipping, return shipping, packaging, the ad spend that won the order, "
        "and sometimes damaged stock. The RTO Finder adds these up per state and pin code.",
    cta=("Want us to read your RTO data?",
         "Comment <b>RTO</b> for the RTO Finder sheet, or book a free 30-minute call at <b>marginwise.in</b>."),
    sources="Source: Shipway ShipNotes FY25, via MediaBrief (26% RTO on COD orders; under 2% on prepaid).",
    keyword="RTO")

docs["marginwise-black-friday-checklist"] = page(
    "Black Friday checkout checklist: 7 fixes before 27 November",
    "Sale traffic is the most expensive traffic you will buy all year. These fixes need no redesign and can ship "
    "before the sale.",
    [
        ("The 7 fixes", "", [
            "Show shipping cost or the free-shipping threshold on the product page and in the cart",
            "Turn on guest checkout",
            "Turn on express payment: Shop Pay, Apple Pay and Google Pay",
            "Show a delivery date that accounts for sale-week carrier delays",
            "Make stock and offer messaging honest and clear: what is discounted and until when",
            "Run a mobile speed test and remove any app added since the last one",
            "Add a post-purchase upsell that keeps margin: a complementary product, not a deeper discount",
        ]),
        ("Timeline", "", [
            "Three weeks out: speed test, app clean-up, checkout settings",
            "Two weeks out: offer pages live in draft, delivery cut-off dates set",
            "Week of the sale: freeze theme changes; watch checkout conversion daily",
            "After the sale: send the delivered and how-to-use email, then a review request",
        ]),
        ("Protect margin", "", [
            "Check each offer against contribution per order, not just revenue",
            "Avoid stacking site-wide discounts with discount codes",
        ]),
    ],
    box="Baymard Institute estimates the average large ecommerce site can gain 35% higher conversion through "
        "better checkout design alone.",
    cta=("Want a check before the sale?",
         "Comment <b>BFCM</b> or send your store link by DM for a free 2-minute teardown, or book a call at "
         "<b>marginwise.in</b>."),
    sources="Source: Baymard Institute, checkout usability research. Black Friday 2026 falls on Friday 27 November.",
    keyword="BFCM")

for name, body in docs.items():
    with open(os.path.join(OUT, name + ".html"), "w") as fh:
        fh.write(body)
print(len(docs), "checklists")
