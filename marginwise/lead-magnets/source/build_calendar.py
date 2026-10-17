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
    """Australia-only posts go out at 13:30 IST; US/UK and all-market posts at 19:30 IST.
    Shows Sydney (AEDT, UTC+11), London (BST until 24 Oct, then GMT) and New York (EDT until 31 Oct, then EST)."""
    au = market == "AU"
    utc = datetime(d.year, d.month, d.day, 8 if au else 14, 0, tzinfo=timezone.utc)
    fmt = lambda h: (utc + timedelta(hours=h)).strftime("%H:%M")
    lon = 1 if d < date(2026, 10, 25) else 0
    ny = -4 if d < date(2026, 11, 1) else -5
    return ("13:30" if au else "19:30"), fmt(11), fmt(lon), fmt(ny)


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
from posts_v3 import POSTS, REC, BATCHES
for (m, dd, fmt_, pillar_, market_, hook_, outline_, caption_, cta_, magnet_, trial_, pin_, batch_) in POSTS:
    post(D(m, dd), fmt_, pillar_, market_, hook_, outline_, caption_, cta_, magnet_, trial_, pin_, batch_)


# ------------------------------------------------------------------ faceless production steps
POST_SETTINGS = ("Post: paste caption from this sheet, add the location-free cover, turn on the auto-DM keyword, "
                 "publish at 19:30 IST{trial}. Reply to every comment in the first hour.")


def reel_steps(record, script, edit_extra="", trial=False):
    t = " as a Trial Reel (share to followers only if 3-second hold beats your average)" if trial else ""
    return "\n".join([
        "1. Record: " + record,
        "2. Script the voiceover (about 25 words for 10 seconds): hook, the work, the CTA. " + script,
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

for (m, dd, fmt_, *_rest) in POSTS:
    trial_ = _rest[-3] == "Yes"
    if "Carousel" in fmt_:
        STEPS[D(m, dd)] = carousel_steps("Same template as the first carousel. Check every claim against its source line.")
    else:
        rec, scr, ed = REC[(m, dd)]
        STEPS[D(m, dd)] = reel_steps(rec, scr, ed, trial=trial_)

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
                "zoom and red-box highlights on whatever you name. Length 10 seconds; Google Flow clips work as b-roll."),
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
    ("t", "From 18 Oct the account targets Australia, the US and the UK. Australia posts go out at 13:30 IST "
          "(19:00 Sydney); US/UK and all-market posts at 19:30 IST (afternoon in London, morning in New York). "
          "The Calendar tab shows each date's local times."),
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
heads = ["Week", "Date", "Day", "IST", "Sydney", "London", "New York", "Format", "Pillar", "Market", "Hook (on screen)",
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
    ist, syd, lon, nyc = local_times(d, market)
    vals = [week, d, d.strftime("%a"), ist, syd, lon, nyc, fmt, pillar, market, hook, outline, STEPS[d], caption, cta, magnet,
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
batches = [(n, D(*md), c, w, t) for (n, md, c, w, t) in BATCHES]
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
    ("All lead magnets (1 sheet, 8 PDFs) uploaded to Drive or the website with share links", "Every CTA keyword depends on these"),
    ("Auto-DM tool connected and the 8 keywords tested from a second account", "Broken DMs waste the first reels"),
    ("Highlight covers made: Teardowns, How we work, US/UK clients, COD/RTO, Book a call", "Profile looks complete from day one"),
    ("GA4 check that utm_source=instagram shows up", "So calls can be traced to reels"),
    ("Employment-contract check done", "Before posting anything publicly"),
    ("Website updated for Australia, US and UK (hours, currency, services)", "Bio and website must match"),
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
