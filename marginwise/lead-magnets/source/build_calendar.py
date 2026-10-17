"""Builds the Marginwise Instagram content calendar (5 weeks from 14 Oct 2026)."""
import sys
from datetime import date, datetime, timedelta, timezone
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation

OUT = sys.argv[1]
FONT = "Arial"
NAVY = "1F2A44"
BLUE = "0000FF"
HEAD = PatternFill("solid", start_color=NAVY)
INPUT = PatternFill("solid", start_color="FFF6CC")
WEEKFILL = PatternFill("solid", start_color="E8ECF4")
thin = Side(style="thin", color="C9CED8")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
WRAP = Alignment(wrap_text=True, vertical="top")


def f(bold=False, color="000000", size=10, italic=False):
    return Font(name=FONT, bold=bold, color=color, size=size, italic=italic)


def header(ws, row, heads, widths):
    for i, (h, w) in enumerate(zip(heads, widths), 1):
        c = ws.cell(row=row, column=i, value=h)
        c.font = f(True, "FFFFFF")
        c.fill = HEAD
        c.alignment = Alignment(wrap_text=True, vertical="center")
        c.border = BOX
        ws.column_dimensions[c.column_letter].width = w
    ws.row_dimensions[row].height = 32


def local_times(d, market):
    """Posting slot by market. Posts from 18 Oct aimed at Australia/NZ go out at 13:30 IST; India and Saudi
    posts at 19:30 IST. Shows Riyadh (UTC+3), Sydney (AEDT, UTC+11) and Auckland (NZDT, UTC+13)."""
    anz = d >= date(2026, 10, 18) and market not in ("India", "India + Saudi")
    utc = datetime(d.year, d.month, d.day, 8 if anz else 14, 0, tzinfo=timezone.utc)
    fmt = lambda h: (utc + timedelta(hours=h)).strftime("%H:%M")
    return ("13:30" if anz else "19:30"), fmt(3), fmt(11), fmt(13)


# ------------------------------------------------------------------ posts
# (date, format, pillar, market, hook, outline, caption, cta, magnet, trial, pin, film_batch)
P = []


def post(d, fmt, pillar, market, hook, outline, caption, cta, magnet, trial="No", pin="No", batch=""):
    P.append((d, fmt, pillar, market, hook, outline, caption, cta, magnet, trial, pin, batch))


D = lambda m, dd: date(2026, m, dd)

# Week 1
post(D(10, 14), "Reel (60s)", "Proof and trust", "All",
     "Every agency sells you ROAS. We sell you margin. This is what that looks like.",
     "Screen walkthrough of a Marginwise audit on a demo store (your own Shopify dev store or a public store, no client data): "
     "1) funnel numbers, 2) three leaks ranked by revenue impact, 3) the one fix to ship this week, 4) the written summary "
     "the founder gets. Close on the four services and who it is not for.",
     "Most agencies report ROAS. We report what you keep.\n\nThis is what a Marginwise audit looks like: your funnel, "
     "your three biggest leaks ranked by revenue impact, one fix to ship this week, and a written summary.\n\n"
     "CRO, performance marketing, UX and app development for D2C and Shopify brands in India, the US and the UK.\n\n"
     "Comment AUDIT and we will send you a 2-minute teardown of your store.\n\n#d2c #shopify #ecommercegrowth",
     "AUDIT", "marginwise-store-leak-audit.pdf + free 2-min teardown", "No", "Yes", "Batch 1")
post(D(10, 16), "Reel (45s)", "Margin math", "Intl",
     "Your ROAS says 3x. Your bank account disagrees.",
     "Show 3x ROAS on screen. Remove over-attribution, returns, COGS, shipping, payment fees one by one. "
     "Land on contribution after ads. End: track contribution margin per order, not ROAS.",
     "ROAS is not profit. Here is what a 3x ROAS can actually leave you with once over-attribution, returns, "
     "product cost, shipping and fees come out.\n\nComment PROFIT and we will send you the calculator to run it on "
     "your own numbers.\n\n#shopify #metaads #dtc",
     "PROFIT", "marginwise-profit-calculator-usd.xlsx + marginwise-roas-to-profit-checklist.pdf", "Yes", "Yes", "Batch 1")
post(D(10, 17), "Carousel (7 slides)", "Margin math", "All",
     "Where D2C revenue leaks: 4 numbers every founder should know",
     "S1 hook. S2 70.22% of carts abandoned (Baymard). S3 35% conversion gain from better checkout design (Baymard). "
     "S4 8.4% more conversions from 0.1s faster mobile (Deloitte/Google). S5 26% RTO on COD vs under 2% prepaid "
     "(Shipway FY25). S6 what to fix first. S7 CTA.",
     "Four published numbers that explain where most D2C stores lose revenue, and what to fix first for each. "
     "Sources on every slide.\n\nSave this for your next growth review. Comment AUDIT if you want us to check "
     "your store against them.\n\n#ecommerce #cro #d2cbrands",
     "AUDIT", "marginwise-store-leak-audit.pdf + free 2-min teardown", "No", "No", "Design")
post(D(10, 18), "Reel (50s)", "COD/RTO", "India + Saudi",
     "26% of your COD orders come back.",
     "Shipway FY25: 26% RTO on COD vs under 2% prepaid. What one RTO costs: forward and return shipping, "
     "packaging, wasted ad spend. Three fixes: prepaid incentive, WhatsApp confirmation for risky COD, "
     "switch off COD only in high-RTO pin codes.",
     "Switching off COD everywhere is the wrong fix. Find the pin codes where it loses money and act only there.\n\n"
     "Comment RTO and we will send you the sheet that ranks your states and pin codes by RTO cost.\n\n"
     "#d2cindia #rto #shopifyindia",
     "RTO", "marginwise-rto-finder.xlsx + marginwise-cod-rto-playbook.pdf", "Yes", "Yes", "Batch 1")

# Week 2
post(D(10, 20), "Reel (60s)", "Teardown", "ANZ",
     "[Brand] does everything right on this page except one thing.",
     "Screen-record a well-known Australian or New Zealand brand's mobile product page. Two strengths, one leak "
     "(shipping cost hidden until checkout, Afterpay messaging buried, review placement, or a slow image). What that leak costs in margin.",
     "A product page teardown with a margin lens: what converts, what leaks, and what the leak costs.\n\n"
     "Want this for your store? Comment AUDIT.\n\n#shopifyaustralia #ecommerceaustralia #nzbusiness",
     "AUDIT", "marginwise-store-leak-audit.pdf + free 2-min teardown", "Yes", "No", "Batch 1")
post(D(10, 22), "Reel (60s)", "Margin math", "India",
     "Your revenue is growing. Your profit isn't. Here's why.",
     "Break down a ₹1,000 order: GST, COGS, ad cost per order, shipping, RTO, gateway fees, discounts. "
     "Land on contribution margin per order. Investors now ask for this, not GMV.",
     "Contribution margin per order, explained with a real ₹1,000 example.\n\nComment MARGIN and we will send you "
     "the calculator, including a what-if for pushing more buyers to prepaid.\n\n#d2cindia #unitEconomics #founders",
     "MARGIN", "marginwise-margin-calculator-inr.xlsx + marginwise-contribution-margin-checklist.pdf", "No", "No", "Batch 1")
post(D(10, 24), "Carousel (8 slides)", "Margin math", "India",
     "What a ₹1,000 order actually earns you",
     "One cost per slide: GST, product cost, ad cost, shipping and packaging, RTO, COD fees, gateway fees. "
     "Final slide: contribution per order and the one lever that moves it most.",
     "Line by line, what is left of a ₹1,000 order once every cost is counted. Numbers are an example store; "
     "run your own with the calculator.\n\nComment MARGIN for the sheet.\n\n#d2cindia #ecommerceindia #margin",
     "MARGIN", "marginwise-margin-calculator-inr.xlsx + marginwise-contribution-margin-checklist.pdf", "No", "No", "Design")
post(D(10, 25), "Reel (45s)", "Teardown", "All",
     "Save these 5 checkout pages before you redesign yours.",
     "Five public checkouts: two Australian or NZ, one Saudi, two Indian. One thing each does well: delivery date, "
     "express pay (Apple Pay, Afterpay, mada, UPI), COD/prepaid nudge, trust badges, order summary clarity.",
     "Five checkouts worth studying before your next redesign, and the one thing each gets right.\n\n"
     "Save this. Comment AUDIT if you want yours reviewed.\n\n#checkout #shopify #cro",
     "AUDIT", "marginwise-store-leak-audit.pdf + free 2-min teardown", "Yes", "No", "Batch 1")
# Week 3
post(D(10, 27), "Reel (45s)", "CRO", "ANZ",
     "7 out of 10 people who add to cart never buy.",
     "Baymard: 70.22% average cart abandonment across 50 studies. Three fixable reasons: surprise costs, "
     "forced account creation, too many steps. Show one fix for each on a Shopify checkout.",
     "Cart abandonment averages 70% (Baymard Institute). Three fixes that do not need a redesign.\n\n"
     "Save this for your next checkout review.\n\n#checkout #shopifytips #ecommerce",
     "Save", "None", "Yes", "No", "Batch 2")
post(D(10, 29), "Reel (60s)", "Teardown", "India",
     "[Indian Brand] is losing mobile buyers here.",
     "Screen-record an Indian D2C brand's mobile product page. Two strengths, one leak "
     "(COD/prepaid messaging, delivery date clarity, size guidance). The fix.",
     "A mobile product page teardown of an Indian D2C brand, and one fix that lifts conversion without a "
     "redesign.\n\nComment AUDIT for a teardown of your store.\n\n#d2cindia #cro #shopifyindia",
     "AUDIT", "marginwise-store-leak-audit.pdf + free 2-min teardown", "Yes", "No", "Batch 2")
post(D(10, 31), "Carousel (6 slides)", "Proof and trust", "ANZ + Saudi",
     "How Australian, NZ and Saudi brands work with a team in India",
     "S1 hook. S2 overlap hours: Riyadh is 2.5 hours behind India, so the whole working day overlaps; Sydney and "
     "Auckland afternoons are India's morning. S3 weekly written update, with redacted example. S4 one senior contact. "
     "S5 billing in AUD, NZD or SAR, NDA, 30-day notice. S6 CTA.",
     "The three things founders worry about with an offshore team, and exactly how we handle each one.\n\n"
     "Comment CHECKLIST for the questions to ask any agency, us included.\n\n#ecommerceaustralia #saudibusiness #dtc",
     "CHECKLIST", "marginwise-agency-checklist.pdf", "No", "No", "Design")
post(D(11, 1), "Reel (50s)", "Proof and trust", "ANZ + Saudi",
     "Why founders worry about hiring an agency in India.",
     "Communication, time zones, quality. How each should be handled by any agency: overlap hours (Riyadh shares "
     "India's working day; Sydney and Auckland afternoons are India's morning), weekly written update, one senior "
     "point of contact. 'Ask any agency for these three.'",
     "What to ask any offshore agency before you sign, ourselves included.\n\nComment CHECKLIST for the full "
     "agency hiring checklist.\n\n#ecommerceagency #shopifyaustralia #saudibusiness",
     "CHECKLIST", "marginwise-agency-checklist.pdf", "No", "No", "Batch 2")
# Week 4
post(D(11, 3), "Reel (45s)", "Retention", "All",
     "Rating post-purchase emails. This one is a 2/10.",
     "Rate three order confirmation emails (public or redacted) with a score and one reason each. "
     "End on what a 9/10 email contains.",
     "Your order confirmation email is the most-opened email you send. Most brands waste it on a receipt.\n\n"
     "Comment FLOWS for the post-purchase checklist and a 10-point scorecard.\n\n#klaviyo #emailmarketing #dtc",
     "FLOWS", "marginwise-post-purchase-email-checklist.pdf", "Yes", "No", "Batch 2")
post(D(11, 5), "Reel (45s)", "CRO", "All",
     "A tenth of a second changed conversions by 8.4%.",
     "Deloitte/Google study of 37 brands. Run a public store through PageSpeed. Show the three usual culprits: "
     "app scripts, oversized images, third-party widgets. Fix speed before buying more traffic.",
     "Fix speed before you buy more traffic. The three culprits on most Shopify stores.\n\n"
     "Comment SPEED and we will check your store.\n\n#shopifyspeed #cro #ecommerce",
     "SPEED", "marginwise-shopify-speed-checklist.pdf + speed check", "No", "No", "Batch 2")
post(D(11, 7), "Carousel (8 slides)", "CRO", "ANZ + Saudi",
     "Sale-season checkout checklist: 7 fixes before Click Frenzy, White Friday and Black Friday",
     "One fix per slide: shipping cost shown early, guest checkout, express pay (Apple Pay, Afterpay, mada, Tabby or "
     "Tamara), delivery date, honest offer messaging, mobile speed, post-purchase upsell that keeps margin. Final slide CTA.",
     "Seven checkout fixes you can still ship before the November sales, none of which need a redesign.\n\n"
     "Comment BFCM for the full checklist with a sale timeline.\n\n#blackfriday #clickfrenzy #whitefriday",
     "BFCM", "marginwise-black-friday-checklist.pdf", "No", "No", "Design")
post(D(11, 8), "Reel (50s)", "Proof and trust", "India",
     "Five questions to ask before you hire a D2C agency.",
     "Who works on my account? Whose name is the ad account in? Show a redacted report with CPA. "
     "Notice period? Which one metric in month one?",
     "Most founders pick an agency from the pitch deck. Ask these five questions instead, including to us.\n\n"
     "Comment CHECKLIST for the full list.\n\n#d2c #marketingagency #founders",
     "CHECKLIST", "marginwise-agency-checklist.pdf", "No", "No", "Batch 2")

# Week 5
post(D(11, 10), "Reel (50s)", "Margin math", "ANZ + Saudi",
     "Buy now, pay later is not free. Here's what it costs you.",
     "Afterpay in Australia and NZ, Tabby and Tamara in Saudi: every BNPL order carries a merchant fee. Enter your "
     "own BNPL fee in the PROFIT calculator's payment fee line and show contribution per order before and after. "
     "Three levers: show BNPL only above a minimum order value, price bundles to lift AOV, steer repeat buyers to cheaper payment.",
     "BNPL can lift conversion, but every order pays a merchant fee. Know what it does to your margin before you push it.\n\n"
     "Comment PROFIT for the calculator and run it with your own fee.\n\n#afterpay #tabby #ecommerceaustralia",
     "PROFIT", "marginwise-profit-calculator-usd.xlsx + marginwise-roas-to-profit-checklist.pdf", "Yes", "No", "Batch 3")
post(D(11, 12), "Reel (40s)", "Margin math", "India",
     "Your ₹1 lakh ad budget costs ₹1.18 lakh.",
     "Meta Ireland billing means 18% GST under reverse charge, paid in cash before credit. Show the cash timing. "
     "Add 18% to the ad budget in your cash-flow plan. Confirm with your CA.",
     "The GST line that catches founders short on cash. Not tax advice; confirm with your CA.\n\n"
     "Comment MARGIN for the calculator, which includes a GST-on-ads tab.\n\n#d2cindia #metaads #gst",
     "MARGIN", "marginwise-margin-calculator-inr.xlsx + marginwise-contribution-margin-checklist.pdf", "No", "No", "Batch 3")
post(D(11, 14), "Carousel (7 slides)", "Retention", "All",
     "After the sale: turn festive and Black Friday buyers into repeat buyers",
     "S1 hook. S2 why sale buyers churn. S3 the delivered + how-to-use email. S4 review request timing. "
     "S5 replenishment timed to your data. S6 win-back without a discount first. S7 CTA.",
     "Sale buyers are the easiest to lose. Five emails that bring them back without giving away margin.\n\n"
     "Comment FLOWS for the full checklist.\n\n#retention #emailmarketing #d2c",
     "FLOWS", "marginwise-post-purchase-email-checklist.pdf", "No", "No", "Design")
post(D(11, 15), "Reel (60s)", "Proof and trust", "All",
     "We audited [N] D2C stores this month. The same 3 leaks showed up in [X] of them.",
     "Only post if the audits are real; use the actual count. Three most common leaks, anonymised. "
     "If fewer than 5 audits are done, swap for a second Indian teardown.",
     "What we keep finding when we audit D2C stores, with no names attached.\n\nComment AUDIT to get yours.\n\n"
     "#d2c #cro #ecommercegrowth",
     "AUDIT", "marginwise-store-leak-audit.pdf + free 2-min teardown", "No", "No", "Batch 3")


# ------------------------------------------------------------------ faceless production steps
POST_SETTINGS = ("Post: paste caption from this sheet, add the location-free cover, turn on the auto-DM keyword, "
                 "publish at 19:30 IST{trial}. Reply to every comment in the first hour.")


def reel_steps(record, script, edit_extra="", trial=False):
    t = " as a Trial Reel (share to followers only if 3-second hold beats your average)" if trial else ""
    return "\n".join([
        "1. Record: " + record,
        "2. Script the voiceover (about 130 words for 60s): hook, the work, the takeaway, CTA. " + script,
        "3. Voiceover: record in a quiet room on your phone (Voice Memos or CapCut > Audio > Record). One clean take; no AI voice.",
        "4. Edit in CapCut (9:16): drop in recordings, lay voiceover, Auto captions on (white, bold, lower third), "
        "hook text on screen for the first 2 seconds. " + edit_extra,
        "5. Cover: freeze a frame of the work with the hook text on it; keep text inside the centre 1080x1080 so it crops cleanly on the grid.",
        "6. " + POST_SETTINGS.format(trial=t),
    ])


def carousel_steps(design):
    return "\n".join([
        "1. Canva > Instagram Post (portrait) 1080x1350. Use one template for every carousel: navy background, white text, one idea per slide.",
        "2. Slide copy: take it from the Outline column. Max 25 words per slide. " + design,
        "3. Put a source line (small, bottom) on every slide with a statistic.",
        "4. Last slide: CTA with the comment keyword in large text.",
        "5. Export as PNG, upload in order, add alt text to slide 1.",
        "6. " + POST_SETTINGS.format(trial=""),
    ])


STEPS = {
    D(10, 14): reel_steps(
        "Screen-record (desktop, QuickTime or OBS, 1080p) a walkthrough of an audit on a demo store: GA4 funnel, "
        "three leaks marked in a doc, the one-page written summary. Use a Shopify dev store or public pages only.",
        "Open with: 'This is what we look at before we touch your ads.'",
        "Zoom (keyframes) on each leak as you name it; red box highlights. Pin this post after publishing."),
    D(10, 16): reel_steps(
        "Screen-record the PROFIT calculator (ROAS to Profit tab) at 150% zoom, typing in a 3x ROAS store and "
        "watching contribution turn negative.",
        "Say each cost as it is subtracted; end on the break-even ROAS cell.",
        "Highlight the cell being changed each time; end frame on the verdict cell.", trial=True),
    D(10, 17): carousel_steps("Big number top half, one-line meaning and 'what to fix' bottom half."),
    D(10, 18): reel_steps(
        "Screen-record the RTO finder with sample orders loaded: the By State tab sorting by cost, one state flagged "
        "'Restrict COD or verify'.",
        "Use the Shipway 26% vs under 2% figure in the first line.",
        "Text callout for each of the three fixes as you say it.", trial=True),
    D(10, 20): reel_steps(
        "Phone screen-record (iOS Control Centre > Screen Recording, or Android quick settings) the brand's mobile "
        "product page: scroll slowly, add to cart, open cart. 40 seconds, no notifications (Do Not Disturb on).",
        "Two things it does well, then the one leak and what it costs.",
        "Red circle on the leak; slow-zoom into it. Blur any personal data.", trial=True),
    D(10, 22): reel_steps(
        "Screen-record the MARGIN calculator, Margin per Order tab, stepping through each cost line of a ₹1,000 order.",
        "One sentence per cost line; end on contribution per order.",
        "Running total as on-screen text in the top corner."),
    D(10, 24): carousel_steps("One cost per slide with the running total shown on every slide."),
    D(10, 25): reel_steps(
        "Phone screen-record five public checkouts (stop before payment). 6-8 seconds each.",
        "One line per checkout: what it does well.",
        "Numbered label 1-5 on screen; 'Save this' text on the final frame.", trial=True),
    D(10, 27): reel_steps(
        "Phone screen-record a checkout showing a surprise shipping cost, a forced account screen and a long form "
        "(public stores).",
        "Lead with Baymard's 70.22%; one fix per problem.",
        "Split screen: problem on top, fix described as text below.", trial=True),
    D(10, 29): reel_steps(
        "Phone screen-record the Indian brand's mobile product page: price, delivery date, COD/prepaid messaging, size guide.",
        "Two strengths, one leak, the fix.",
        "Red circle on the leak; ₹ figures as on-screen text."),
    D(10, 31): carousel_steps("Slide 3 shows a redacted sample weekly update; build it from a blank template, not client data."),
    D(11, 1): reel_steps(
        "Screen-record the agency checklist PDF scrolling to the 'If the agency is in another country' section, "
        "plus a world clock showing Riyadh, India, Sydney and Auckland side by side.",
        "Name the three worries, then the three answers.",
        "Text list builds one line at a time."),
    D(11, 3): reel_steps(
        "Screenshot three order confirmation emails (your own inbox; blur names, order numbers, addresses).",
        "Score each out of 10 with one reason; end on what a 9/10 has.",
        "Big score number appears on each email; slow scroll down each one."),
    D(11, 5): reel_steps(
        "Screen-record pagespeed.web.dev running on a public Shopify store, then the opportunities list.",
        "Lead with Deloitte/Google 0.1s = 8.4%; name the three culprits.",
        "Highlight the three culprits in the report as you name them."),
    D(11, 7): carousel_steps("One fix per slide with a small mock of the checkout element it refers to."),
    D(11, 8): reel_steps(
        "Screen-record the agency checklist PDF, top table (five questions, good answer, red flag).",
        "Read each question and its red flag.",
        "Highlight each row as you read it."),
    D(11, 10): reel_steps(
        "Screen-record the PROFIT calculator: raise the payment fee line to your BNPL fee, then raise AOV to show margin recovering.",
        "Before vs after contribution per order; three levers.",
        "Before/after numbers side by side as text.", trial=True),
    D(11, 12): reel_steps(
        "Screen-record the MARGIN calculator, GST on Ads tab, typing ₹1,00,000.",
        "Explain reverse charge in one sentence; say 'confirm with your CA'.",
        "Show '₹1,18,000 leaves your account' as the final frame."),
    D(11, 14): carousel_steps("Each email slide shows when to send it and one line of example copy."),
    D(11, 15): reel_steps(
        "Screen-record a tally sheet of the audits you actually ran (store names hidden) and anonymised screenshots of the three leaks.",
        "Use the real count. If under 5 audits, swap for a second Indian teardown and follow that recipe.",
        "Counter animation for each leak's tally."),
}

SOP = [
    ("Kit", "Laptop with QuickTime (Mac) or OBS (Windows) for desktop recording; phone screen recorder; CapCut (free); "
            "Canva (free); wired earphones with mic or any USB mic. No camera needed."),
    ("Before recording", "Do Not Disturb on, browser in a clean profile (no bookmarks, no logged-in personal accounts), "
                         "zoom browser to 125-150% so text is readable on a phone."),
    ("Recording", "Move the cursor slowly and pause 1 second on anything you will talk about. Record 20% more than you need."),
    ("Voiceover", "Your own voice, phone held 15 cm away, in a room with soft furnishings. Read from the script, then do one "
                  "natural take without reading; use whichever sounds less scripted. Instagram rewards real human content; "
                  "skip AI voices."),
    ("If you do not want to use your voice", "Text-only version: put each script line as a caption block (3-4 words per screen), "
                                             "add quiet background music from CapCut's commercial library. Expect lower watch time; "
                                             "test it as a Trial Reel first."),
    ("Editing", "CapCut: 9:16, Auto captions, hook text in the first 2 seconds, cut every pause over half a second, "
                "zoom and red-box highlights on whatever you name. Length 30-60 seconds."),
    ("Privacy", "Blur names, emails, order numbers and any client data. Teardowns use public pages only."),
    ("Carousels", "Canva 1080x1350, one template for all, max 25 words per slide, source line on stat slides, CTA slide last."),
    ("After posting", "Reply to every comment in the first hour; check the auto-DM fired; log numbers in the Calendar tab after 7 days."),
]

# ------------------------------------------------------------------ workbook
wb = Workbook()
rm = wb.active
rm.title = "Read me"
rm.column_dimensions["A"].width = 110
rm.sheet_view.showGridLines = False
lines = [
    ("h", "Marginwise Instagram content calendar: 14 Oct to 15 Nov 2026"),
    ("t", "Five weeks, 20 posts: 3 reels and 1 carousel a week, plus Stories on 4 days. Built from "
          "marginwise/instagram-playbook.md."),
    ("h", "Tabs"),
    ("t", "Calendar: every post with hook, outline, step-by-step production (faceless), caption, CTA keyword and lead magnet. Fill the yellow "
          "columns after posting."),
    ("t", "Stories: the weekly Stories rhythm."),
    ("t", "How to make (no face): the kit and the step-by-step method used for every post. No camera needed."),
    ("t", "Recording batches: what to record in each session so you are never recording the night before."),
    ("t", "Weekly review: totals per week, calculated from the Calendar tab."),
    ("t", "Setup before 14 Oct: the checklist to finish before the first post."),
    ("h", "Rules"),
    ("t", "From 18 Oct, posts for Australia, NZ or all markets go out at 13:30 IST (11:00 Riyadh, 19:00 Sydney, "
          "21:00 Auckland). India and Saudi posts go out at 19:30 IST (17:00 Riyadh). The Calendar tab shows each date."),
    ("t", "No holiday greetings, memes or office posts. They underperformed for every competitor reviewed."),
    ("t", "Replace [Brand] placeholders with public pages only. Keep the tone constructive and keep logos out of thumbnails."),
    ("t", "Post Trial Reels first where marked; share to followers only if they hold viewers past 3 seconds."),
    ("t", "Do not publish a CTA keyword until its auto-DM and lead-magnet link work."),
    ("input", "Yellow cells are for you to fill in after posting (link, reach, saves, shares, DMs, calls)."),
]
r = 1
for kind, text in lines:
    c = rm.cell(row=r, column=1, value=text)
    c.alignment = Alignment(wrap_text=True, vertical="top")
    if kind == "h":
        c.font = f(True, NAVY, 14 if r == 1 else 11)
        r += 1 if r == 1 else 0
    elif kind == "input":
        c.font = f(color=BLUE)
        c.fill = INPUT
    else:
        c.font = f()
    r += 1

cal = wb.create_sheet("Calendar")
heads = ["Week", "Date", "Day", "IST", "Riyadh", "Sydney", "Auckland", "Format", "Pillar", "Market", "Hook (on screen)",
         "Outline", "Step by step (no face)", "Caption", "CTA keyword", "Lead magnet", "Trial Reel first?", "Pin?", "Recording batch",
         "Status", "Post link", "Reach", "Saves", "Shares", "Comments", "DMs", "Calls booked"]
widths = [7, 12, 6, 7, 8, 8, 9, 15, 14, 8, 34, 45, 70, 55, 12, 30, 10, 6, 11, 11, 24, 9, 8, 8, 10, 8, 9]
header(cal, 1, heads, widths)
cal.freeze_panes = "D2"
start = date(2026, 10, 12)
status_dv = DataValidation(type="list", formula1='"Planned,Filmed,Edited,Scheduled,Posted,Skipped"', allow_blank=True)
cal.add_data_validation(status_dv)
for i, (d, fmt, pillar, market, hook, outline, caption, cta, magnet, trial, pin, batch) in enumerate(P, 2):
    week = (d - start).days // 7 + 1
    ist, riy, syd, akl = local_times(d, market)
    vals = [week, d, d.strftime("%a"), ist, riy, syd, akl, fmt, pillar, market, hook, outline, STEPS[d], caption, cta, magnet,
            trial, pin, batch, "Planned"]
    for col, v in enumerate(vals, 1):
        c = cal.cell(row=i, column=col, value=v)
        c.font = f(bold=(col == 11))
        c.alignment = WRAP
        c.border = BOX
        if week % 2 == 0:
            c.fill = WEEKFILL
    cal.cell(row=i, column=2).number_format = "dd mmm yyyy"
    status_dv.add(f"T{i}")
    for col in range(21, 28):
        c = cal.cell(row=i, column=col)
        c.fill = INPUT
        c.font = f(color=BLUE)
        c.border = BOX
        if col >= 22:
            c.number_format = "#,##0"
    cal.row_dimensions[i].height = 230
last = len(P) + 1
cal.auto_filter.ref = f"A1:AA{last}"

st = wb.create_sheet("Stories")
header(st, 1, ["Day", "Story type", "What to post", "Sticker", "Why"], [10, 18, 60, 18, 45])
stories = [
    ("Monday", "Poll", "One question for founders, alternating markets. Examples: 'What is your COD share? Under 30% / "
     "Over 30%'; 'Do you track contribution margin weekly? Yes / No'.", "Poll", "Two-way interaction now ranks; poll answers tell you what to post next."),
    ("Wednesday", "Behind the scenes", "15 seconds from a teardown in progress: the store on screen, one thing you spotted. "
     "No client names.", "Question box: 'Want yours next?'", "Shows the work, feeds AUDIT requests."),
    ("Friday", "Reel share", "Share the week's best-performing reel with a one-line takeaway.", "Link: marginwise.in booking", "Stories with link stickers are the highest-intent surface."),
    ("Sunday", "Answer", "Answer one question from DMs as 2-3 text frames over a screen recording or screenshot of the relevant page.", "None", "Turns DMs into content and shows you reply."),
]
for i, row in enumerate(stories, 2):
    for col, v in enumerate(row, 1):
        c = st.cell(row=i, column=col, value=v)
        c.font = f(bold=(col == 1))
        c.alignment = WRAP
        c.border = BOX
    st.row_dimensions[i].height = 60

sop = wb.create_sheet("How to make (no face)")
header(sop, 1, ["Step", "How"], [26, 110])
for i, (k, v) in enumerate(SOP, 2):
    for col, val in ((1, k), (2, v)):
        c = sop.cell(row=i, column=col, value=val)
        c.font = f(bold=(col == 1))
        c.alignment = WRAP
        c.border = BOX
    sop.row_dimensions[i].height = 45

fb = wb.create_sheet("Recording batches")
header(fb, 1, ["Batch", "Film on", "Posts covered", "What to prepare", "Time needed"], [10, 14, 50, 60, 12])
batches = [
    ("Batch 1", date(2026, 10, 13), "Founder intro; ROAS 3x; COD RTO 26%; US/UK product page teardown; ₹1,000 order margin; 5 checkout pages",
     "Pick the US/UK brand and 5 checkouts (public pages). Record all screen captures first, then write and record every voiceover in one sitting.", "3 hours"),
    ("Batch 2", date(2026, 10, 24), "Cart abandonment; Indian teardown; offshore trust; email ratings; site speed; agency questions",
     "Pick the Indian brand and three order confirmation emails (your own inbox or public examples). Run PageSpeed on one public store.", "3 hours"),
    ("Batch 3", date(2026, 11, 7), "Tariffs; GST on ads; audit roundup",
     "Count real audits done so far. If fewer than 5, film a second Indian teardown instead of the roundup.", "2 hours"),
    ("Design", date(2026, 10, 15), "All five carousels",
     "Use the same template: navy and white, one idea per slide, source line on every stat slide. Canva or Figma.", "4 hours"),
]
for i, row in enumerate(batches, 2):
    for col, v in enumerate(row, 1):
        c = fb.cell(row=i, column=col, value=v)
        c.font = f(bold=(col == 1))
        c.alignment = WRAP
        c.border = BOX
    fb.cell(row=i, column=2).number_format = "dd mmm yyyy"
    fb.row_dimensions[i].height = 60

wr = wb.create_sheet("Weekly review")
header(wr, 1, ["Week", "Week starting", "Posts planned", "Posts posted", "Reach", "Saves", "Shares", "Comments",
               "DMs", "Calls booked", "Shares per 1,000 reach", "What to change next week"],
       [7, 14, 10, 10, 10, 9, 9, 10, 8, 10, 12, 50])
rng = lambda col: f"Calendar!${col}$2:${col}${last}"
for w in range(1, 6):
    r = w + 1
    wr.cell(row=r, column=1, value=w)
    wr.cell(row=r, column=2, value=start + timedelta(days=7 * (w - 1))).number_format = "dd mmm yyyy"
    wr.cell(row=r, column=3, value=f"=COUNTIF({rng('A')},A{r})")
    wr.cell(row=r, column=4, value=f'=COUNTIFS({rng("A")},A{r},{rng("T")},"Posted")')
    for col, src in zip("EFGHIJ", ["V", "W", "X", "Y", "Z", "AA"]):
        wr[f"{col}{r}"] = f"=SUMIF({rng('A')},A{r},{rng(src)})"
        wr[f"{col}{r}"].number_format = "#,##0"
    wr[f"K{r}"] = f"=IFERROR(G{r}/E{r}*1000,0)"
    wr[f"K{r}"].number_format = "0.0"
    wr[f"L{r}"].fill = INPUT
    for col in range(1, 13):
        c = wr.cell(row=r, column=col)
        c.font = f(color=BLUE) if col == 12 else f()
        c.border = BOX
tr = 7
wr.cell(row=tr, column=1, value="Total").font = f(True)
for col in "CDEFGHIJ":
    wr[f"{col}{tr}"] = f"=SUM({col}2:{col}6)"
    wr[f"{col}{tr}"].font = f(True)
    wr[f"{col}{tr}"].number_format = "#,##0"
wr[f"K{tr}"] = f"=IFERROR(G{tr}/E{tr}*1000,0)"
wr[f"K{tr}"].number_format = "0.0"
wr[f"K{tr}"].font = f(True)
wr["A9"] = "Judge the account on calls booked and DMs, not reach. Shares per 1,000 reach is the best early signal of what Instagram will push."
wr["A9"].font = f(False, "555555", 9, True)

su = wb.create_sheet("Setup before 14 Oct")
header(su, 1, ["Done?", "Task", "Why"], [8, 70, 55])
tasks = [
    ("Switch to Business account, category Marketing Agency, contact email set", "Unlocks insights, contact button and approved DM tools"),
    ("Bio, name field and website link with UTM added", "Profile visits convert from here"),
    ("Two-factor authentication on, backup codes saved", "A hacked brand account is hard to recover"),
    ("All lead magnets (3 sheets, 8 PDFs) uploaded to Drive or the website with share links", "Every CTA keyword depends on these"),
    ("Auto-DM tool connected and the 8 keywords tested from a second account", "Broken DMs waste the first reels"),
    ("Highlight covers made: Teardowns, How we work, US/UK clients, COD/RTO, Book a call", "Profile looks complete from day one"),
    ("GA4 check that utm_source=instagram shows up", "So calls can be traced to reels"),
    ("Employment-contract check done", "Before posting anything publicly"),
    ("UK decision made (keep in bio and site, or remove)", "Bio and website must match"),
]
for i, (t, why) in enumerate(tasks, 2):
    su.cell(row=i, column=1).fill = INPUT
    su.cell(row=i, column=1).border = BOX
    for col, v in ((2, t), (3, why)):
        c = su.cell(row=i, column=col, value=v)
        c.font = f()
        c.alignment = WRAP
        c.border = BOX
dv = DataValidation(type="list", formula1='"Yes,No"', allow_blank=True)
su.add_data_validation(dv)
dv.add(f"A2:A{len(tasks) + 1}")

wb.save(OUT)
print(len(P), "posts")
