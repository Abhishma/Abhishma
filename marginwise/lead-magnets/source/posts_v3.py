"""Posts from 18 Oct 2026 for Australia, US and UK. Services: performance marketing, CRO, website development,
SEO/AEO/GEO, and AI solutions (built for brands and used in our own delivery). Imported by build_calendar.py."""

AUDIT = "marginwise-store-leak-audit.pdf + free 2-min teardown"
PROFIT = "marginwise-profit-calculator-usd.xlsx + marginwise-roas-to-profit-checklist.pdf"
GEO = "marginwise-ai-search-visibility-checklist.pdf"
AI = "marginwise-ai-for-ecommerce-builds.pdf"
SPEED = "marginwise-shopify-speed-checklist.pdf + speed check"
FLOWS = "marginwise-post-purchase-email-checklist.pdf"
CHECK = "marginwise-agency-checklist.pdf"
BFCM = "marginwise-black-friday-checklist.pdf"

# (month, day, format, pillar, market, hook, outline, caption, cta, magnet, trial, pin, batch)
POSTS = [
    # Week 1
    (10, 18, "Reel (10s)", "SEO/AEO/GEO", "All",
     "We asked ChatGPT to recommend a brand in your category. Were you in the answer?",
     "Screen-record asking ChatGPT, Perplexity and Google (AI Overview) the same buying question for one category, "
     "for example 'best running socks in Australia'. Show which brands get named and which don't. Takeaway: AI search "
     "is a new shelf, and you can work on getting onto it.",
     "Shoppers now ask ChatGPT, Perplexity and Google's AI answers what to buy. Some brands get named. Most don't.\n\n"
     "Getting into those answers is a mix of SEO, clear product pages and being mentioned in the right places.\n\n"
     "Comment GEO and we will send you the AI search visibility checklist.\n\n#aisearch #seo #shopify",
     "GEO", GEO, "Yes", "Yes", "Batch 1"),

    # Week 2
    (10, 20, "Reel (10s)", "CRO", "AU",
     "[Brand] does everything right on this page except one thing.",
     "Phone screen-record a well-known Australian brand's mobile product page. Two strengths, one leak (shipping cost "
     "hidden until checkout, Afterpay message buried, reviews too low, or a slow image). What that leak costs.",
     "A product page teardown of an Australian brand: what converts, what leaks, and what the leak costs.\n\n"
     "Want this for your store? Comment AUDIT.\n\n#shopifyaustralia #ecommerceaustralia #cro",
     "AUDIT", AUDIT, "Yes", "No", "Batch 1"),
    (10, 22, "Reel (10s)", "Performance marketing", "US/UK",
     "Before you raise your Meta budget, check these 3 numbers.",
     "Screen-record the PROFIT calculator. 1) Break-even ROAS, 2) contribution per order after ads, 3) new vs returning "
     "customer share in Shopify. If any is off, more budget scales the loss.",
     "More budget does not fix a campaign that loses money on every order. It scales it.\n\n"
     "Check break-even ROAS, contribution after ads and your new-customer share first.\n\n"
     "Comment PROFIT for the calculator.\n\n#metaads #performancemarketing #shopify",
     "PROFIT", PROFIT, "No", "No", "Batch 1"),
    (10, 24, "Carousel (7 slides)", "SEO/AEO/GEO", "All",
     "How to show up when shoppers ask AI what to buy",
     "S1 hook. S2 AI answers pull from pages they can read: check your robots.txt and site speed. S3 product pages that "
     "answer real questions (sizing, materials, delivery, returns). S4 structured data: Product, Offer, Review and FAQ "
     "schema. S5 reviews and mentions on other sites, not only your own. S6 test it monthly: ask ChatGPT, Perplexity and "
     "Google the same 5 buying questions and log who appears. S7 CTA.",
     "SEO still matters. AI search adds a second test: can an AI answer engine read your pages, trust them and quote them?\n\n"
     "Five things you control, and a simple monthly test.\n\n"
     "Comment GEO for the full checklist.\n\n#aeo #geo #seo",
     "GEO", GEO, "No", "No", "Design"),
    (10, 25, "Reel (10s)", "CRO", "All",
     "Save these 5 checkout pages before you redesign yours.",
     "Phone screen-record five public checkouts from US, UK and Australian brands. One thing each does well: delivery "
     "date, express pay (Shop Pay, Apple Pay, Afterpay, Klarna), guest checkout, trust near the pay button, order summary.",
     "Five checkouts worth studying before your next redesign, and the one thing each gets right.\n\n"
     "Save this. Comment AUDIT if you want yours reviewed.\n\n#checkout #shopify #cro",
     "AUDIT", AUDIT, "Yes", "No", "Batch 1"),

    # Week 3
    (10, 27, "Reel (10s)", "CRO", "US/UK",
     "7 out of 10 people who add to cart never buy.",
     "Baymard: 70.22% average cart abandonment across 50 studies. Three fixable reasons: surprise costs, forced account "
     "creation, too many steps. One fix for each on a Shopify checkout.",
     "Cart abandonment averages 70% (Baymard Institute). Three fixes that do not need a redesign.\n\n"
     "Comment AUDIT for the 30-point store leak audit.\n\n#checkout #shopifytips #ecommerce",
     "AUDIT", AUDIT, "Yes", "No", "Batch 2"),
    (10, 29, "Reel (10s)", "AI solutions", "All",
     "This is what an AI support assistant for a Shopify store looks like.",
     "Screen-record a demo on a Shopify development store: a shopper asks 'where is my order' and 'can I return this', "
     "the assistant answers from store policies and order status, and hands over to a person when it is unsure. "
     "Demo store only, no client data.",
     "Most support tickets are the same five questions. An AI assistant can answer them in seconds, from your own "
     "policies, and pass anything unusual to your team.\n\n"
     "Comment AI for 10 AI builds worth starting with for ecommerce brands.\n\n#aiforbusiness #shopify #ecommerce",
     "AI", AI, "Yes", "No", "Batch 2"),
    (10, 31, "Carousel (6 slides)", "Proof and trust", "All",
     "How US, UK and Australian brands work with a team in India",
     "S1 hook. S2 overlap hours: London afternoons and US mornings are India's evening; Sydney evenings are India's "
     "afternoon. S3 weekly written update, with a redacted example. S4 one senior contact. S5 billing in USD, GBP or "
     "AUD, NDA, 30-day notice. S6 CTA.",
     "The three things founders worry about with an offshore team, and exactly how we handle each one.\n\n"
     "Comment CHECKLIST for the questions to ask any agency, us included.\n\n#ecommerceagency #shopifyexperts #dtc",
     "CHECKLIST", CHECK, "No", "No", "Design"),
    (11, 1, "Reel (10s)", "AI solutions", "All",
     "How we use AI in a store audit, and what we never hand to it.",
     "Screen-record: AI summarises 500 product reviews into the top objections, drafts test ideas and writes the first "
     "pass of the report. Then show what a person does: checks the data, decides priorities, writes the recommendation.",
     "AI makes our audits faster: it reads every review, drafts test ideas and does the first pass of the report.\n\n"
     "It does not decide what to fix first. A person who has built D2C products does that.\n\n"
     "Comment AUDIT for a free 2-minute teardown of your store.\n\n#ai #cro #ecommerce",
     "AUDIT", AUDIT, "No", "No", "Batch 2"),

    # Week 4
    (11, 3, "Reel (10s)", "Retention", "All",
     "Rating post-purchase emails. This one is a 2/10.",
     "Screenshot three order confirmation emails (your own inbox, details blurred). Score each with one reason; end on "
     "what a 9/10 contains.",
     "Your order confirmation email is the most-opened email you send. Most brands waste it on a receipt.\n\n"
     "Comment FLOWS for the post-purchase checklist and a 10-point scorecard.\n\n#klaviyo #emailmarketing #dtc",
     "FLOWS", FLOWS, "Yes", "No", "Batch 2"),
    (11, 5, "Reel (10s)", "Website development", "All",
     "A tenth of a second changed conversions by 8.4%.",
     "Deloitte/Google study of 37 brands. Run a public store through PageSpeed and show the three usual culprits: app "
     "scripts, oversized images, third-party widgets. Fix speed before buying more traffic.",
     "Fix speed before you buy more traffic. The three culprits on most Shopify stores.\n\n"
     "Comment SPEED and we will check your store.\n\n#shopifyspeed #webdevelopment #cro",
     "SPEED", SPEED, "No", "No", "Batch 2"),
    (11, 7, "Carousel (8 slides)", "CRO", "All",
     "Black Friday checklist: 7 checkout fixes before 27 November",
     "One fix per slide: shipping cost shown early, guest checkout, express pay (Shop Pay, Apple Pay, Afterpay, Klarna), "
     "delivery date, honest offer messaging, mobile speed, post-purchase upsell that keeps margin. Final slide CTA.",
     "Seven checkout fixes you can still ship before Black Friday and Click Frenzy, none of which need a redesign.\n\n"
     "Comment BFCM for the full checklist with a sale timeline.\n\n#blackfriday #bfcm #clickfrenzy",
     "BFCM", BFCM, "No", "No", "Design"),
    (11, 8, "Reel (10s)", "Website development", "US/UK",
     "Theme, custom build or headless? Most stores pick the wrong one.",
     "Screen-record three stores side by side. Theme: fastest and cheapest, fine for most stores under a certain size. "
     "Custom Shopify build: when the brand or the funnel needs it. Headless: when you have the team to maintain it. "
     "One question to decide: who will maintain it next year?",
     "A new website is a business decision, not a design one. Pick the build you can afford to maintain.\n\n"
     "Comment AUDIT and we will tell you which one your store needs.\n\n#shopify #webdevelopment #headless",
     "AUDIT", AUDIT, "No", "No", "Batch 3"),

    # Week 5
    (11, 10, "Reel (10s)", "Performance marketing", "All",
     "Buy now, pay later is not free. Here's what it costs you.",
     "Afterpay, Klarna, Clearpay and Affirm all charge a merchant fee on every order. Enter your own BNPL fee in the "
     "PROFIT calculator's payment fee line and show contribution per order before and after. Three levers: show BNPL "
     "above a minimum order value, bundle to lift AOV, steer repeat buyers to cheaper payment.",
     "BNPL can lift conversion, but every order pays a merchant fee. Know what it does to your margin before you push it.\n\n"
     "Comment PROFIT for the calculator and run it with your own fee.\n\n#afterpay #klarna #ecommerce",
     "PROFIT", PROFIT, "Yes", "No", "Batch 3"),
    (11, 12, "Reel (10s)", "AI solutions", "US/UK",
     "AI-written product descriptions: 3 rules so they sell, rank and get cited.",
     "Screen-record an AI tool drafting a product description from a spec sheet, then edit it live: 1) add the facts "
     "shoppers ask about (size, material, care, delivery), 2) write for the questions people search, 3) a person checks "
     "every claim before it goes live.",
     "AI can write 500 product descriptions in an hour. Without rules, they all sound the same and answer nothing.\n\n"
     "Three rules we use so they sell, rank in search and get quoted by AI answers.\n\n"
     "Comment AI for 10 AI builds worth starting with.\n\n#ai #seo #shopify",
     "AI", AI, "No", "No", "Batch 3"),
    (11, 14, "Carousel (7 slides)", "Retention", "All",
     "After Black Friday: turn sale buyers into repeat buyers",
     "S1 hook. S2 why sale buyers churn. S3 the delivered and how-to-use email. S4 review request timing. S5 replenishment "
     "timed to your data. S6 win-back without a discount first. S7 CTA.",
     "Sale buyers are the easiest to lose. Five emails that bring them back without giving away margin.\n\n"
     "Comment FLOWS for the full checklist.\n\n#retention #emailmarketing #dtc",
     "FLOWS", FLOWS, "No", "No", "Design"),
    (11, 15, "Reel (10s)", "Proof and trust", "All",
     "We audited [N] stores this month. The same 3 leaks showed up in [X] of them.",
     "Only post if the audits are real; use the actual count. Three most common leaks, anonymised. If fewer than 5 audits "
     "are done, swap for a second Australian teardown.",
     "What we keep finding when we audit ecommerce stores, with no names attached.\n\nComment AUDIT to get yours.\n\n"
     "#ecommerce #cro #shopify",
     "AUDIT", AUDIT, "No", "No", "Batch 3"),
]

# Faceless production steps for the posts above (record, voiceover, edit, cover, post).
REC = {
    (10, 18): ("Screen-record (desktop) ChatGPT, Perplexity and Google with the same buying question; scroll the answers slowly.",
               "Open: 'We asked AI what to buy.' End on 'Comment GEO'.",
               "Highlight each brand name the AI mentions; blur nothing needed, these are public answers."),
    (10, 20): ("Phone screen-record the Australian brand's mobile product page: scroll, add to cart, open cart. Do Not Disturb on.",
               "Two things it does well, then the one leak and what it costs.",
               "Red circle on the leak; slow zoom."),
    (10, 22): ("Screen-record the PROFIT calculator at 150% zoom, then Shopify's new vs returning customer report (demo store).",
               "One sentence per number; end on 'more budget scales the loss'.",
               "Highlight each number as you name it."),
    (10, 25): ("Phone screen-record five public checkouts (US, UK, AU); stop before payment. 2 seconds each.",
               "One line per checkout: what it does well.",
               "Numbered labels 1-5; 'Save this' on the final frame."),
    (10, 27): ("Phone screen-record a checkout with a surprise shipping cost, a forced account screen and a long form (public stores).",
               "Lead with Baymard's 70.22%; one fix per problem.",
               "Problem on top, fix as text below."),
    (10, 29): ("Screen-record a support assistant demo on a Shopify development store (Shopify Inbox, or the tool you use). Demo data only.",
               "Two shopper questions, the answers, then the hand-over to a person.",
               "Text callouts: 'answers from your policies', 'hands over when unsure'."),
    (11, 1): ("Screen-record an AI tool summarising public reviews of a demo product, then your audit doc where you set priorities.",
              "What AI does, then what a person does.",
              "Split screen: 'AI' on top, 'Person' below."),
    (11, 3): ("Screenshot three order confirmation emails from your own inbox; blur names, order numbers and addresses.",
              "Score each out of 10 with one reason.",
              "Big score number on each email."),
    (11, 5): ("Screen-record pagespeed.web.dev on a public Shopify store, then the opportunities list.",
              "Lead with 0.1s = 8.4%; name the three culprits.",
              "Highlight the three culprits as you name them."),
    (11, 8): ("Screen-record three public stores: one on a standard theme, one custom, one headless.",
              "One line per option and who it suits; end on the maintenance question.",
              "Labels: Theme, Custom, Headless."),
    (11, 10): ("Screen-record the PROFIT calculator: raise the payment fee to your BNPL fee, then raise AOV to recover margin.",
               "Before vs after contribution per order; three levers.",
               "Before/after numbers side by side."),
    (11, 12): ("Screen-record an AI tool drafting a product description for a demo product, then your edits in the Shopify editor.",
               "The three rules, one per edit.",
               "Strike-through on generic lines, highlight on added facts."),
    (11, 15): ("Screen-record a tally of audits you actually ran (store names hidden) and anonymised screenshots of the three leaks.",
               "Use the real count; if under 5, record a second Australian teardown instead.",
               "Counter for each leak's tally."),
}

BATCHES = [
    ("Batch 1", (10, 18), "AI search test (GEO); Australian product page teardown; Meta budget numbers; 5 checkouts",
     "Pick the category question for the AI test, the Australian brand and five public checkouts. Record screens first, "
     "then all voiceovers in one sitting.", "2 hours"),
    ("Batch 2", (10, 24), "Cart abandonment; AI support assistant demo; how we use AI in an audit; email ratings; site speed",
     "Set up the Shopify development store with demo products and policies for the AI demos.", "3 hours"),
    ("Batch 3", (11, 6), "Theme vs custom vs headless; BNPL fees; AI product descriptions; audit roundup",
     "Count the real audits done so far. If fewer than 5, record a second Australian teardown instead of the roundup.", "2 hours"),
    ("Design", (10, 19), "Carousels: AI search visibility, offshore trust, Black Friday checklist, after-the-sale retention",
     "Same template as the first carousel: navy, white text, green numbers, one idea per slide.", "3 hours"),
]
