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


def local_times(d):
    """19:30 IST on date d, shown in US Eastern and UK time with 2026 DST changes."""
    utc = datetime(d.year, d.month, d.day, 14, 0, tzinfo=timezone.utc)
    et_off = -4 if d < date(2026, 11, 1) else -5      # US DST ends Sun 1 Nov 2026
    uk_off = 1 if d < date(2026, 10, 25) else 0        # UK BST ends Sun 25 Oct 2026
    et = (utc + timedelta(hours=et_off)).strftime("%H:%M")
    uk = (utc + timedelta(hours=uk_off)).strftime("%H:%M")
    return "19:30", et, uk


# ------------------------------------------------------------------ posts
# (date, format, pillar, market, hook, outline, caption, cta, magnet, trial, pin, film_batch)
P = []


def post(d, fmt, pillar, market, hook, outline, caption, cta, magnet, trial="No", pin="No", batch=""):
    P.append((d, fmt, pillar, market, hook, outline, caption, cta, magnet, trial, pin, batch))


D = lambda m, dd: date(2026, m, dd)

# Week 1
post(D(10, 14), "Reel (60s)", "Proof and trust", "Both",
     "Every agency sells you ROAS. I sell you margin.",
     "1) Who I am: 10 years building D2C, omnichannel and loyalty products. 2) The four services in one line each. "
     "3) Who it is not for: pre-launch ideas, single theme tweaks, guaranteed-results deals. "
     "4) How the free 30-min call works and what you leave with.",
     "Most agencies report ROAS. We report what you keep.\n\nMarginwise runs CRO, performance marketing, UX and app "
     "development for D2C and Shopify brands in India, the US and the UK. Every engagement starts with a free "
     "30-minute call: you leave with your top three leaks and a written summary.\n\nComment AUDIT and I will send "
     "you a 2-minute teardown of your store.\n\n#d2c #shopify #ecommercegrowth",
     "AUDIT", "Free 2-min teardown (manual)", "No", "Yes", "Batch 1")
post(D(10, 16), "Reel (45s)", "Margin math", "Intl",
     "Your ROAS says 3x. Your bank account disagrees.",
     "Show 3x ROAS on screen. Remove over-attribution, returns, COGS, shipping, payment fees one by one. "
     "Land on contribution after ads. End: track contribution margin per order, not ROAS.",
     "ROAS is not profit. Here is what a 3x ROAS can actually leave you with once over-attribution, returns, "
     "product cost, shipping and fees come out.\n\nComment PROFIT and I will send you the calculator to run it on "
     "your own numbers.\n\n#shopify #metaads #dtc",
     "PROFIT", "marginwise-profit-calculator-usd.xlsx", "Yes", "Yes", "Batch 1")
post(D(10, 17), "Carousel (7 slides)", "Margin math", "Both",
     "Where D2C revenue leaks: 4 numbers every founder should know",
     "S1 hook. S2 70.22% of carts abandoned (Baymard). S3 35% conversion gain from better checkout design (Baymard). "
     "S4 8.4% more conversions from 0.1s faster mobile (Deloitte/Google). S5 26% RTO on COD vs under 2% prepaid "
     "(Shipway FY25). S6 what to fix first. S7 CTA.",
     "Four published numbers that explain where most D2C stores lose revenue, and what to fix first for each. "
     "Sources on every slide.\n\nSave this for your next growth review. Comment AUDIT if you want us to check "
     "your store against them.\n\n#ecommerce #cro #d2cbrands",
     "AUDIT", "Free 2-min teardown (manual)", "No", "No", "Design")
post(D(10, 18), "Reel (50s)", "COD/RTO", "India",
     "26% of your COD orders come back.",
     "Shipway FY25: 26% RTO on COD vs under 2% prepaid. What one RTO costs: forward and return shipping, "
     "packaging, wasted ad spend. Three fixes: prepaid incentive, WhatsApp confirmation for risky COD, "
     "switch off COD only in high-RTO pin codes.",
     "Switching off COD everywhere is the wrong fix. Find the pin codes where it loses money and act only there.\n\n"
     "Comment RTO and I will send you the sheet that ranks your states and pin codes by RTO cost.\n\n"
     "#d2cindia #rto #shopifyindia",
     "RTO", "marginwise-rto-finder.xlsx", "Yes", "Yes", "Batch 1")

# Week 2
post(D(10, 20), "Reel (60s)", "Teardown", "Intl",
     "[Brand] does everything right on this page except one thing.",
     "Screen-record a well-known US/UK brand's mobile product page. Two strengths, one leak "
     "(hidden shipping cost, review placement, or slow image). What that leak costs in margin.",
     "A product page teardown with a margin lens: what converts, what leaks, and what the leak costs.\n\n"
     "Want this for your store? Comment AUDIT.\n\n#shopifycro #productpage #ecommerce",
     "AUDIT", "Free 2-min teardown (manual)", "Yes", "No", "Batch 1")
post(D(10, 22), "Reel (60s)", "Margin math", "India",
     "Your revenue is growing. Your profit isn't. Here's why.",
     "Break down a ₹1,000 order: GST, COGS, ad cost per order, shipping, RTO, gateway fees, discounts. "
     "Land on contribution margin per order. Investors now ask for this, not GMV.",
     "Contribution margin per order, explained with a real ₹1,000 example.\n\nComment MARGIN and I will send you "
     "the calculator, including a what-if for pushing more buyers to prepaid.\n\n#d2cindia #unitEconomics #founders",
     "MARGIN", "marginwise-margin-calculator-inr.xlsx", "No", "No", "Batch 1")
post(D(10, 24), "Carousel (8 slides)", "Margin math", "India",
     "What a ₹1,000 order actually earns you",
     "One cost per slide: GST, product cost, ad cost, shipping and packaging, RTO, COD fees, gateway fees. "
     "Final slide: contribution per order and the one lever that moves it most.",
     "Line by line, what is left of a ₹1,000 order once every cost is counted. Numbers are an example store; "
     "run your own with the calculator.\n\nComment MARGIN for the sheet.\n\n#d2cindia #ecommerceindia #margin",
     "MARGIN", "marginwise-margin-calculator-inr.xlsx", "No", "No", "Design")
post(D(10, 25), "Reel (45s)", "Teardown", "Both",
     "Save these 5 checkout pages before you redesign yours.",
     "Five public checkouts (mix of US/UK and Indian). One thing each does well: trust badges placement, "
     "delivery date, COD/prepaid nudge, express pay, order summary clarity.",
     "Five checkouts worth studying before your next redesign, and the one thing each gets right.\n\n"
     "Save this. Comment AUDIT if you want yours reviewed.\n\n#checkout #shopify #cro",
     "AUDIT", "Free 2-min teardown (manual)", "Yes", "No", "Batch 1")

# Week 3
post(D(10, 27), "Reel (45s)", "CRO", "Intl",
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
     "AUDIT", "Free 2-min teardown (manual)", "Yes", "No", "Batch 2")
post(D(10, 31), "Carousel (6 slides)", "Proof and trust", "Intl",
     "How a US or UK brand works with a team in India",
     "S1 hook. S2 overlap hours (your morning, our evening). S3 weekly written update, with redacted example. "
     "S4 one senior contact. S5 billing in USD/GBP, NDA, 30-day notice. S6 CTA.",
     "The three things founders worry about with an offshore team, and exactly how we handle each one.\n\n"
     "See how we work at the link in bio.\n\n#ecommerceagency #shopifyexperts #dtc",
     "Link in bio", "None", "No", "No", "Design")
post(D(11, 1), "Reel (50s)", "Proof and trust", "Intl",
     "Why US brands are scared to hire an agency in India.",
     "Communication, time zones, quality. How each should be handled by any agency: overlap hours, "
     "weekly written update, one senior point of contact. 'Ask any agency for these three.'",
     "What to ask any offshore agency before you sign, ourselves included.\n\nComment CHECKLIST for the full "
     "agency hiring checklist.\n\n#ecommerceagency #shopify #dtcbrands",
     "CHECKLIST", "marginwise-agency-checklist.pdf", "No", "No", "Batch 2")

# Week 4
post(D(11, 3), "Reel (45s)", "Retention", "Both",
     "Rating post-purchase emails. This one is a 2/10.",
     "Rate three order confirmation emails (public or redacted) with a score and one reason each. "
     "End on what a 9/10 email contains.",
     "Your order confirmation email is the most-opened email you send. Most brands waste it on a receipt.\n\n"
     "Comment FLOWS for the post-purchase checklist and a 10-point scorecard.\n\n#klaviyo #emailmarketing #dtc",
     "FLOWS", "marginwise-post-purchase-email-checklist.pdf", "Yes", "No", "Batch 2")
post(D(11, 5), "Reel (45s)", "CRO", "Both",
     "A tenth of a second changed conversions by 8.4%.",
     "Deloitte/Google study of 37 brands. Run a public store through PageSpeed. Show the three usual culprits: "
     "app scripts, oversized images, third-party widgets. Fix speed before buying more traffic.",
     "Fix speed before you buy more traffic. The three culprits on most Shopify stores.\n\n"
     "Comment SPEED and I will check your store.\n\n#shopifyspeed #cro #ecommerce",
     "SPEED", "Speed check (manual)", "No", "No", "Batch 2")
post(D(11, 7), "Carousel (8 slides)", "CRO", "Intl",
     "Black Friday checkout checklist: 7 fixes before 27 November",
     "One fix per slide: shipping cost shown early, guest checkout, express pay, delivery date, "
     "stock and promo messaging, mobile speed, post-purchase upsell that keeps margin. Final slide CTA.",
     "Seven checkout fixes you can still ship before Black Friday, none of which need a redesign.\n\n"
     "Save this. Comment AUDIT if you want us to check yours before the sale.\n\n#blackfriday #bfcm #shopify",
     "AUDIT", "Free 2-min teardown (manual)", "No", "No", "Design")
post(D(11, 8), "Reel (50s)", "Proof and trust", "India",
     "Five questions to ask before you hire a D2C agency.",
     "Who works on my account? Whose name is the ad account in? Show a redacted report with CPA. "
     "Notice period? Which one metric in month one?",
     "Most founders pick an agency from the pitch deck. Ask these five questions instead, including to us.\n\n"
     "Comment CHECKLIST for the full list.\n\n#d2c #marketingagency #founders",
     "CHECKLIST", "marginwise-agency-checklist.pdf", "No", "No", "Batch 2")

# Week 5
post(D(11, 10), "Reel (50s)", "Margin math", "Intl",
     "Tariffs went up. Your prices didn't. Here's the gap.",
     "Since the $800 de minimis exemption ended, landed costs rose. Landed cost before and after (illustrative). "
     "Three levers besides price: AOV bundles, free-shipping threshold, push higher-margin products.",
     "Rising import costs hit contribution margin first. Three ways to protect it without a price rise.\n\n"
     "Comment PROFIT for the margin calculator.\n\n#dtc #tariffs #shopify",
     "PROFIT", "marginwise-profit-calculator-usd.xlsx", "Yes", "No", "Batch 3")
post(D(11, 12), "Reel (40s)", "Margin math", "India",
     "Your ₹1 lakh ad budget costs ₹1.18 lakh.",
     "Meta Ireland billing means 18% GST under reverse charge, paid in cash before credit. Show the cash timing. "
     "Add 18% to the ad budget in your cash-flow plan. Confirm with your CA.",
     "The GST line that catches founders short on cash. Not tax advice; confirm with your CA.\n\n"
     "Comment MARGIN for the calculator, which includes a GST-on-ads tab.\n\n#d2cindia #metaads #gst",
     "MARGIN", "marginwise-margin-calculator-inr.xlsx", "No", "No", "Batch 3")
post(D(11, 14), "Carousel (7 slides)", "Retention", "Both",
     "After the sale: turn festive and Black Friday buyers into repeat buyers",
     "S1 hook. S2 why sale buyers churn. S3 the delivered + how-to-use email. S4 review request timing. "
     "S5 replenishment timed to your data. S6 win-back without a discount first. S7 CTA.",
     "Sale buyers are the easiest to lose. Five emails that bring them back without giving away margin.\n\n"
     "Comment FLOWS for the full checklist.\n\n#retention #emailmarketing #d2c",
     "FLOWS", "marginwise-post-purchase-email-checklist.pdf", "No", "No", "Design")
post(D(11, 15), "Reel (60s)", "Proof and trust", "Both",
     "I audited [N] D2C stores this month. The same 3 leaks showed up in [X] of them.",
     "Only post if the audits are real; use the actual count. Three most common leaks, anonymised. "
     "If fewer than 5 audits are done, swap for a second Indian teardown.",
     "What we keep finding when we audit D2C stores, with no names attached.\n\nComment AUDIT to get yours.\n\n"
     "#d2c #cro #ecommercegrowth",
     "AUDIT", "Free 2-min teardown (manual)", "No", "No", "Batch 3")

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
    ("t", "Calendar: every post with hook, outline, caption, CTA keyword and lead magnet. Fill the yellow "
          "columns after posting."),
    ("t", "Stories: the weekly Stories rhythm."),
    ("t", "Filming batches: what to film in each session so you are never filming the night before."),
    ("t", "Weekly review: totals per week, calculated from the Calendar tab."),
    ("t", "Setup before 14 Oct: the checklist to finish before the first post."),
    ("h", "Rules"),
    ("t", "All posts go out at 19:30 IST. That is 10:00 US Eastern and 15:00 UK until the clocks change "
          "(UK 25 Oct, US 1 Nov); the Calendar tab shows the exact local times for each date."),
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
heads = ["Week", "Date", "Day", "IST", "US Eastern", "UK", "Format", "Pillar", "Market", "Hook (on screen)",
         "Outline", "Caption", "CTA keyword", "Lead magnet", "Trial Reel first?", "Pin?", "Filming batch",
         "Status", "Post link", "Reach", "Saves", "Shares", "Comments", "DMs", "Calls booked"]
widths = [7, 12, 6, 7, 9, 7, 15, 14, 8, 34, 50, 60, 12, 30, 10, 6, 11, 11, 24, 9, 8, 8, 10, 8, 9]
header(cal, 1, heads, widths)
cal.freeze_panes = "D2"
start = date(2026, 10, 12)
status_dv = DataValidation(type="list", formula1='"Planned,Filmed,Edited,Scheduled,Posted,Skipped"', allow_blank=True)
cal.add_data_validation(status_dv)
for i, (d, fmt, pillar, market, hook, outline, caption, cta, magnet, trial, pin, batch) in enumerate(P, 2):
    week = (d - start).days // 7 + 1
    ist, et, uk = local_times(d)
    vals = [week, d, d.strftime("%a"), ist, et, uk, fmt, pillar, market, hook, outline, caption, cta, magnet,
            trial, pin, batch, "Planned"]
    for col, v in enumerate(vals, 1):
        c = cal.cell(row=i, column=col, value=v)
        c.font = f(bold=(col == 10))
        c.alignment = WRAP
        c.border = BOX
        if week % 2 == 0:
            c.fill = WEEKFILL
    cal.cell(row=i, column=2).number_format = "dd mmm yyyy"
    status_dv.add(f"R{i}")
    for col in range(19, 26):
        c = cal.cell(row=i, column=col)
        c.fill = INPUT
        c.font = f(color=BLUE)
        c.border = BOX
        if col >= 20:
            c.number_format = "#,##0"
    cal.row_dimensions[i].height = 150
last = len(P) + 1
cal.auto_filter.ref = f"A1:Y{last}"

st = wb.create_sheet("Stories")
header(st, 1, ["Day", "Story type", "What to post", "Sticker", "Why"], [10, 18, 60, 18, 45])
stories = [
    ("Monday", "Poll", "One question for founders, alternating markets. Examples: 'What is your COD share? Under 30% / "
     "Over 30%'; 'Do you track contribution margin weekly? Yes / No'.", "Poll", "Two-way interaction now ranks; poll answers tell you what to post next."),
    ("Wednesday", "Behind the scenes", "15 seconds from a teardown in progress: the store on screen, one thing you spotted. "
     "No client names.", "Question box: 'Want yours next?'", "Shows the work, feeds AUDIT requests."),
    ("Friday", "Reel share", "Share the week's best-performing reel with a one-line takeaway.", "Link: marginwise.in booking", "Stories with link stickers are the highest-intent surface."),
    ("Sunday", "Answer", "Answer one question from DMs or the question box on camera (30-45s).", "None", "Turns DMs into content and shows you reply."),
]
for i, row in enumerate(stories, 2):
    for col, v in enumerate(row, 1):
        c = st.cell(row=i, column=col, value=v)
        c.font = f(bold=(col == 1))
        c.alignment = WRAP
        c.border = BOX
    st.row_dimensions[i].height = 60

fb = wb.create_sheet("Filming batches")
header(fb, 1, ["Batch", "Film on", "Posts covered", "What to prepare", "Time needed"], [10, 14, 50, 60, 12])
batches = [
    ("Batch 1", date(2026, 10, 13), "Founder intro; ROAS 3x; COD RTO 26%; US/UK product page teardown; ₹1,000 order margin; 5 checkout pages",
     "Pick the US/UK brand and 5 checkouts (public pages). Screen recordings done before filming. Same shirt across takes to batch-edit.", "3 hours"),
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
    wr.cell(row=r, column=4, value=f'=COUNTIFS({rng("A")},A{r},{rng("R")},"Posted")')
    for col, src in zip("EFGHIJ", "TUVWXY"):
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
    ("Five lead magnets uploaded (Drive or website) with share links", "Every CTA keyword depends on these"),
    ("Auto-DM tool connected and the 7 keywords tested from a second account", "Broken DMs waste the first reels"),
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
