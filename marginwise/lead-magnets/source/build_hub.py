"""Build Marginwise HQ: one artifact page that holds every Marginwise asset.

Output: marginwise/hub/index.html and marginwise/hub/calendar.html.
Lead magnet PDFs and the profit calculator are published alongside as files.
"""
import html
import re
from pathlib import Path

import markdown
import openpyxl
from markdown.extensions.toc import TocExtension, slugify

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "hub"
OUT.mkdir(exist_ok=True)


def render(md_text, prefix):
    """Markdown to HTML with heading ids prefixed per tab so they never collide."""
    toc = TocExtension(slugify=lambda v, sep: prefix + "-" + slugify(v, sep))
    body = markdown.markdown(md_text, extensions=["tables", "fenced_code", toc])
    body = body.replace("<table>", '<div class="tw"><table>').replace("</table>", "</table></div>")
    body = body.replace("<pre><code>", '<div class="cb"><button class="copy" type="button">Copy</button><pre><code>')
    body = body.replace("</code></pre>", "</code></pre></div>")
    body = body.replace('<a href="http', '<a target="_blank" rel="noopener" href="http')
    return body


def subnav(body):
    items = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body)
    links = "".join(f'<a href="#{i}">{re.sub(r"<.*?>", "", t)}</a>' for i, t in items)
    return f'<div class="subnav">{links}</div>' if links else ""


def section(md_path, start=None, end=None, drop_h1=True):
    text = (ROOT / md_path).read_text()
    if start:
        text = text[text.index(start):]
    if end and end in text:
        text = text[:text.index(end)]
    if drop_h1:
        text = re.sub(r"^# .*\n", "", text, count=1)
    return text


# ---------- content ----------
market_md = section("market-research-boring-problems.md")
decision_md = section("market-research-boring-problems.md", "## 0. The decision", "## 1. Where the money")
kit_md = section("solutions/build-kit.md")
playbook_md = section("instagram-playbook.md")
profile_md = section("instagram-profile.md")
dms_md = section("auto-dm-messages.md")

market = render(market_md, "mk")
kit = render(kit_md, "kit")
playbook = render(playbook_md, "ig")
profile = render("## Instagram profile, updated 18 Oct\n\n" + profile_md.replace("## ", "### "), "igp")
dms = render(dms_md, "dm")
decision = render(decision_md.replace("## 0. The decision in ten lines", "## The decision in ten lines"), "st")

# Calendar summary table from the workbook
ws = openpyxl.load_workbook(ROOT / "instagram-content-calendar.xlsx", data_only=True)["Calendar"]
rows = list(ws.iter_rows(values_only=True))
head = rows[0]
col = {name: i for i, name in enumerate(head)}
cal_rows = []
for r in rows[1:]:
    if not r[col["Date"]]:
        continue
    d = r[col["Date"]]
    date = d.strftime("%a %d %b") if hasattr(d, "strftime") else str(d)
    cal_rows.append(
        "<tr>" + "".join(f"<td>{html.escape(str(x or ''))}</td>" for x in [
            date, r[col["IST"]], r[col["Format"]], r[col["Market"]],
            r[col["Hook (on screen)"]], r[col["CTA keyword"]], r[col["Status"]],
        ]) + "</tr>"
    )
cal_table = (
    '<div class="tw"><table><thead><tr><th>Date</th><th>IST</th><th>Format</th><th>Market</th>'
    "<th>Hook</th><th>Keyword</th><th>Status</th></tr></thead><tbody>"
    + "".join(cal_rows) + "</tbody></table></div>"
)

# Lead magnets: active ones only (INR and RTO assets are retired with the India market)
MAGNETS = [
    ("AUDIT", "marginwise-store-leak-audit.pdf", "30-point store leak audit", "All"),
    ("PROFIT", "marginwise-roas-to-profit-checklist.pdf", "ROAS to profit checklist", "AU, US, UK"),
    ("PROFIT", "marginwise-profit-calculator-usd.xlsx", "Profit calculator (USD spreadsheet)", "AU, US, UK"),
    ("GEO", "marginwise-ai-search-visibility-checklist.pdf", "AI search visibility checklist", "All"),
    ("AI", "marginwise-ai-for-ecommerce-builds.pdf", "10 AI builds worth starting with", "All"),
    ("SPEED", "marginwise-shopify-speed-checklist.pdf", "Shopify speed checklist", "All"),
    ("FLOWS", "marginwise-post-purchase-email-checklist.pdf", "Post-purchase email checklist", "All"),
    ("CHECKLIST", "marginwise-agency-checklist.pdf", "Agency hiring checklist", "All"),
    ("BFCM", "marginwise-black-friday-checklist.pdf", "Black Friday, Cyber Monday and Click Frenzy checklist", "AU, US, UK"),
]
magnet_rows = "".join(
    f'<tr><td><span class="kw">{k}</span></td><td>{html.escape(t)}</td><td>{m}</td>'
    + (f'<td><a href="lead-magnets/{f}" target="_blank" rel="noopener">Open PDF</a></td></tr>' if f.endswith(".pdf")
       else f'<td>In the repo: <code>marginwise/lead-magnets/{f}</code> (upload to Google Sheets)</td></tr>')
    for k, f, t, m in MAGNETS
)
TODO_MAGNETS = [
    ("SURCHARGE or PROFIT", "AU surcharge-ban margin one-pager", "AU", "Needed for Meta ads (section 11 of the market map)"),
    ("ZATCA", "ZATCA Wave 25 readiness checklist", "KSA", "Needed for WhatsApp ads, wave 3"),
    ("Form, no keyword", "Widerrufsbutton and E-Rechnung checklist (German)", "DE", "Needed for German instant-form ads, wave 2; native review"),
]
todo_rows = "".join(f"<tr><td><span class=\"kw\">{k}</span></td><td>{t}</td><td>{m}</td><td>{n}</td></tr>" for k, t, m, n in TODO_MAGNETS)

ASSETS = [
    ("Market map", "Research, city scan, offers and pricing, competitors, forecast, 30-day plan, outreach, LinkedIn, Meta ads", "markets", "Live"),
    ("Solution kit", "16 solutions with build prompts, demo scripts, proposals and case studies", "solutions", "Live"),
    ("Instagram playbook and calendar", "Positioning, competitor review, 20 posts 14 Oct to 15 Nov", "instagram", "Live"),
    ("Auto-DM messages", "ManyChat replies for 8 keywords plus fallbacks", "dms", "Live"),
    ("Lead magnets", "8 PDFs and the USD profit calculator", "magnets", "Live; 3 new ones needed"),
    ("Tools and code", "Store audit crawler and 12 AI agents", "tools", "Built and tested offline"),
    ("Booking website", "Landing page with prices and a Sydney, London and US slot picker", "tools", "Live, updated 18 Oct"),
]
asset_rows = "".join(
    f'<tr><td><a href="#{tab}" data-tab="{tab}">{n}</a></td><td>{d}</td><td><span class="pill {"warn" if "Out" in s or "needed" in s else "ok"}">{s}</span></td></tr>'
    for n, d, tab, s in ASSETS
)

start = f"""
<p class="lede">Everything for Marginwise in one place: the plan, the markets, the offers and prices, the solutions we build, the Instagram engine and the tools. Updated 17 Oct 2026.</p>
<h2 id="st-assets">What is in here</h2>
<div class="tw"><table><thead><tr><th>Asset</th><th>What it holds</th><th>Status</th></tr></thead><tbody>{asset_rows}</tbody></table></div>
{decision}
<h2 id="st-next">Next actions</h2>
<ol>
<li>Run the store audit crawler on your laptop against 3 real stores (the cloud session blocks outside sites). Fix any false flags before using it on prospects.</li>
<li>Add an Anthropic API key and run the receptionist and payout reconciliation agents on the demo data. Record those two demo videos from the Solution kit.</li>
<li>Start wave 1 outreach from day 1 of the 30-day plan (Mon 19 Oct): Australia surcharge offer and US tariff offer.</li>
<li>Build the 3 missing lead magnets and their ManyChat flows before launching Meta ads.</li>
<li>Paste the new Instagram profile (Instagram tab) and make sure marginwise.in shows the updated website.</li>
</ol>
"""

tools = """
<h2 id="tl-audit">Store audit crawler</h2>
<p>Folder: <code>marginwise/solutions/leak-audit/</code>. 15 of 15 tests pass on local fixture sites. Not yet run on a live store.</p>
<div class="cb"><button class="copy" type="button">Copy</button><pre><code>cd marginwise/solutions/leak-audit
npm install
node audit.mjs https://example-store.com --market AU --out reports/example
npm test</code></pre></div>
<p>Checks: platform, speed (LCP, page weight, scripts), accessibility (axe WCAG 2.1 AA), trackers before consent, product page basics, market rules (AU surcharge; DE Impressum, withdrawal button, green claims, strike-through prices; CA French; SA Arabic, VAT, Tabby/Tamara; US accessibility weight), AI search readiness (schema, AI crawler rules, llms.txt). Outputs report.html and report.json with a score out of 100.</p>
<p>Limits: text-based detection, so review every finding; one page load and the cookie banner is never clicked; homepage and one product page only (no cart or checkout); NZ has general checks only; compliance flags are not legal advice.</p>

<h2 id="tl-agents">AI agents package</h2>
<p>Folder: <code>marginwise/solutions/agents/</code>. 203 tests pass offline. No live model call or live integration yet.</p>
<div class="cb"><button class="copy" type="button">Copy</button><pre><code>cd marginwise/solutions/agents
pip install -r requirements.txt
python -m pytest
export ANTHROPIC_API_KEY=...   # then run an agent for real</code></pre></div>
<div class="tw"><table><thead><tr><th>Agent</th><th>Job</th><th>Approval needed for</th></tr></thead><tbody>
<tr><td>receptionist</td><td>Phone and SMS receptionist, missed-call text-back, booking</td><td>none (books only within rules)</td></tr>
<tr><td>whatsapp_commerce</td><td>Arabic and English WhatsApp: COD confirm, National Address, order status, BNPL nudge, returns</td><td>handoff to a person</td></tr>
<tr><td>support_wismo</td><td>Order status, returns, exchanges</td><td>address edits</td></tr>
<tr><td>sync_exception</td><td>Shopify to ERP sync failures, safe auto-fixes</td><td>SKU mapping, non-whitelisted fixes</td></tr>
<tr><td>payout_reconciliation</td><td>Payout to bank to ledger matching (plain code) plus summary</td><td>none (read only)</td></tr>
<tr><td>po_to_order</td><td>Emailed purchase orders to draft orders</td><td>draft order creation</td></tr>
<tr><td>compliance_copy_auditor</td><td>EmpCo, PAngV, AU drip pricing and green claims, Meta claims</td><td>none (report only)</td></tr>
<tr><td>gpsr_extractor</td><td>EU product safety fields from supplier PDFs</td><td>writing metafields</td></tr>
<tr><td>hs_classifier</td><td>HS code suggestions plus landed-cost calculator</td><td>codes stay "for broker review"</td></tr>
<tr><td>aeo_visibility</td><td>AI assistant share-of-voice tracking</td><td>none</td></tr>
<tr><td>lead_triage</td><td>Score, route and draft first replies</td><td>sending emails</td></tr>
<tr><td>quote_builder</td><td>Instant quotes from a price book, site-visit booking</td><td>none (price book only)</td></tr>
</tbody></table></div>
<p>Limits: all integrations are mock adapters until connected with client access; OpenAI and Perplexity adapters for the AI search tracker are stubs; German and Arabic wording needs native review; compliance rules are a first screen, not legal advice. The optional server-side refusal fallback is off by default.</p>

<h2 id="tl-site">Booking website</h2>
<p>The Marginwise landing page with the booking desk: <a href="https://claude.ai/artifact/VMnKegZXec8AFS6SZd3krg" target="_blank" rel="noopener">open it</a>. Anyone with the link can open it.</p>
<p><span class="pill ok">Updated 18 Oct</span> Australia, US and UK; five services; Find, Fix, Grow; published prices ($1,500 audit, sprints from $3,900, retainers from $1,500 a month); slot picker in Sydney, London and US Eastern time that only offers daytime slots; calculator in AUD, USD or GBP; the AU surcharge ban replaces the India COD stat.</p>
<p>To host it on marginwise.in, upload <code>marginwise/website/marginwise-site.html</code> as the home page. Bookings still go to abhimanyu.btti@gmail.com; change <code>HOST_EMAIL</code> in the script if you want them at your marginwise.in address.</p>
<h2 id="tl-repo">Where the source files are</h2>
<div class="tw"><table><thead><tr><th>File</th><th>What</th></tr></thead><tbody>
<tr><td><code>marginwise/market-research-boring-problems.md</code></td><td>Market map source</td></tr>
<tr><td><code>marginwise/solutions/build-kit.md</code></td><td>Solution kit source</td></tr>
<tr><td><code>marginwise/instagram-playbook.md</code></td><td>Instagram playbook</td></tr>
<tr><td><code>marginwise/instagram-content-calendar.xlsx</code></td><td>Calendar workbook (built by <code>lead-magnets/source/build_calendar.py</code>)</td></tr>
<tr><td><code>marginwise/auto-dm-messages.md</code></td><td>Auto-DM messages</td></tr>
<tr><td><code>marginwise/lead-magnets/</code></td><td>PDFs and spreadsheets (sources in <code>lead-magnets/source/</code>)</td></tr>
<tr><td><code>marginwise/lead-magnets/source/build_hub.py</code></td><td>Rebuilds this page</td></tr>
</tbody></table></div>
"""

instagram = f"""
{profile}
<h2 id="ig-calendar">Content calendar, 14 Oct to 13 Dec</h2>
<p>The summary is below. The <a href="calendar.html">full calendar</a> has the step-by-step recording instructions, captions with copy buttons, and the tracking columns.</p>
{cal_table}
{playbook}
"""

magnets = f"""
<h2 id="lm-active">Active lead magnets</h2>
<p>Each keyword triggers its ManyChat flow (see Auto-DMs). Upload these to Drive and paste the share links into the DM messages.</p>
<div class="tw"><table><thead><tr><th>Keyword</th><th>Lead magnet</th><th>Markets</th><th>File</th></tr></thead><tbody>{magnet_rows}</tbody></table></div>
<h2 id="lm-todo">Still to build</h2>
<div class="tw"><table><thead><tr><th>Keyword</th><th>Lead magnet</th><th>Market</th><th>Why</th></tr></thead><tbody>{todo_rows}</tbody></table></div>
<h2 id="lm-retired">Retired</h2>
<p>INR margin calculator, RTO finder, COD/RTO playbook and contribution margin checklist (India market, retired 17 Oct 2026). Keywords RTO and MARGIN are no longer used. The files stay in the repo.</p>
"""

TABS = [
    ("start", "Start", start),
    ("markets", "Plan and markets", subnav(market) + market),
    ("solutions", "Solutions", subnav(kit) + kit),
    ("instagram", "Instagram", subnav(instagram) + instagram),
    ("dms", "Auto-DMs", subnav(dms) + dms),
    ("magnets", "Lead magnets", magnets),
    ("tools", "Tools and code", subnav(tools) + tools),
]
tabbar = "".join(
    f'<button type="button" role="tab" id="t-{k}" aria-controls="p-{k}" data-tab="{k}">{label}</button>'
    for k, label, _ in TABS
)
panels = "".join(
    f'<section class="panel" role="tabpanel" id="p-{k}" aria-labelledby="t-{k}"{"" if k == "start" else " hidden"}>{body}</section>'
    for k, _, body in TABS
)

page = f"""<title>Marginwise HQ</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;800&family=Public+Sans:wght@400;600&family=IBM+Plex+Mono:wght@400&display=swap">
<style>
/* Layout: brand header, sticky tab bar, one reading column per tab with a chip row of that tab's sections */
:root {{
  --bg: #f6f7f9; --surface: #ffffff; --fg: #1b2333; --muted: #5b6577;
  --navy: #1F2A44; --green: #2E9E7E; --red: #C0533A; --line: #dde2ea; --code: #eef1f5; --soft: #e6f3ee;
  --display: "Archivo", "Helvetica Neue", Arial, sans-serif;
  --body: "Public Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #11161f; --surface: #171d29; --fg: #e4e8ef; --muted: #9aa4b5;
  --navy: #9fb3e0; --green: #4cc29f; --red: #e07a62; --line: #2a3242; --code: #1e2533; --soft: #173029; color-scheme: dark }} }}
:root[data-theme="dark"] {{
  --bg: #11161f; --surface: #171d29; --fg: #e4e8ef; --muted: #9aa4b5;
  --navy: #9fb3e0; --green: #4cc29f; --red: #e07a62; --line: #2a3242; --code: #1e2533; --soft: #173029; color-scheme: dark }}
body {{ background: var(--bg); color: var(--fg); font: 15px/1.6 var(--body); }}
body::before {{ content: ""; position: fixed; inset: 0 0 auto; height: env(safe-area-inset-top, 0px); z-index: 10; background: var(--surface); }}
.gut {{ padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }}
header.top {{ background: var(--surface); border-bottom: 1px solid var(--line); padding-block: 18px 6px; }}
.brand {{ max-width: 920px; margin: 0 auto; display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; }}
.brand h1 {{ font: 800 26px/1.1 var(--display); color: var(--navy); margin: 0; letter-spacing: -.01em; }}
.brand h1 i {{ font-style: normal; color: var(--green); }}
.brand span {{ color: var(--muted); font-size: 13px; }}
nav.tabs {{ position: sticky; top: env(safe-area-inset-top, 0px); z-index: 6; background: var(--surface); border-bottom: 1px solid var(--line); }}
nav.tabs .row {{ max-width: 920px; margin: 0 auto; display: flex; gap: 4px; overflow-x: auto; padding-block: 8px; scrollbar-width: thin; }}
nav.tabs button {{ flex: none; font: 600 14px var(--body); color: var(--muted); background: transparent; border: 0; border-radius: 6px; padding: 8px 12px; cursor: pointer; }}
nav.tabs button[aria-selected="true"] {{ background: var(--navy); color: var(--surface); }}
nav.tabs button:focus-visible {{ outline: 2px solid var(--green); outline-offset: 2px; }}
main {{ max-width: 920px; margin: 0 auto; padding-block: 20px 72px; }}
.subnav {{ display: flex; gap: 6px; flex-wrap: wrap; margin: 4px 0 8px; }}
.subnav a {{ font: 600 12.5px var(--body); color: var(--navy); text-decoration: none; border: 1px solid var(--line); border-radius: 999px; padding: 4px 10px; background: var(--surface); }}
.subnav a:hover, .subnav a:focus-visible {{ border-color: var(--green); color: var(--green); outline: none; }}
.lede {{ font-size: 17px; color: var(--muted); max-width: 64ch; }}
h2 {{ font: 800 22px/1.25 var(--display); color: var(--navy); margin: 40px 0 10px; padding-top: 14px; border-top: 3px solid var(--green); text-wrap: balance; scroll-margin-top: 70px; }}
h3 {{ font: 700 17px/1.3 var(--display); margin: 24px 0 8px; scroll-margin-top: 70px; }}
p, li {{ max-width: 70ch; }}
a {{ color: var(--green); }}
.tw {{ overflow-x: auto; margin: 10px 0 18px; border: 1px solid var(--line); border-radius: 6px; background: var(--surface); }}
table {{ border-collapse: collapse; font-size: 13.5px; min-width: 620px; width: 100%; font-variant-numeric: tabular-nums; }}
th {{ text-align: left; background: var(--navy); color: var(--surface); font: 600 12.5px var(--body); padding: 8px 10px; }}
td {{ padding: 8px 10px; border-top: 1px solid var(--line); vertical-align: top; }}
.cb {{ position: relative; margin: 10px 0 18px; }}
pre {{ background: var(--code); border: 1px solid var(--line); border-radius: 6px; padding: 14px; overflow-x: auto; white-space: pre-wrap; font: 13px/1.55 var(--mono); }}
code {{ font-family: var(--mono); font-size: .92em; }}
.copy {{ position: absolute; top: 8px; right: 8px; font: 600 12px var(--body); background: var(--green); color: #fff; border: 0; border-radius: 4px; padding: 5px 10px; cursor: pointer; }}
.kw {{ font: 600 12px var(--mono); background: var(--soft); color: var(--green); padding: 2px 6px; border-radius: 4px; white-space: nowrap; }}
.pill {{ font: 600 12px var(--body); padding: 2px 8px; border-radius: 999px; white-space: nowrap; }}
.pill.ok {{ background: var(--soft); color: var(--green); }}
.pill.warn {{ background: color-mix(in srgb, var(--red) 14%, transparent); color: var(--red); }}
hr {{ border: 0; margin: 0; }}
@media (prefers-reduced-motion: no-preference) {{ html {{ scroll-behavior: smooth; }} }}
</style>
<header class="top gut"><div class="brand"><h1>Margin<i>wise</i> HQ</h1><span>Plan, markets, solutions, Instagram, DMs, lead magnets and tools. 17 Oct 2026.</span></div></header>
<nav class="tabs gut" aria-label="Sections"><div class="row" role="tablist">{tabbar}</div></nav>
<main class="gut">{panels}</main>
<script>
(function () {{
  const tabs = [...document.querySelectorAll('[role="tab"]')];
  function show(key, scrollTo) {{
    if (!document.getElementById('p-' + key)) return;
    tabs.forEach(t => t.setAttribute('aria-selected', String(t.dataset.tab === key)));
    document.querySelectorAll('.panel').forEach(p => p.hidden = p.id !== 'p-' + key);
    try {{ localStorage.setItem('mw-tab', key); }} catch (e) {{}}
    if (scrollTo !== false) window.scrollTo(0, 0);
  }}
  tabs.forEach(t => t.addEventListener('click', () => show(t.dataset.tab)));
  document.querySelectorAll('a[data-tab]').forEach(a => a.addEventListener('click', e => {{ e.preventDefault(); show(a.dataset.tab); }}));
  let first = 'start';
  const h = location.hash.slice(1);
  if (h && document.getElementById('p-' + h)) first = h;
  else {{ try {{ const s = localStorage.getItem('mw-tab'); if (s) first = s; }} catch (e) {{}} }}
  show(first, false);
  document.querySelectorAll('.copy').forEach(b => b.addEventListener('click', () => {{
    const pre = b.nextElementSibling;
    const done = () => {{ b.textContent = 'Copied'; setTimeout(() => b.textContent = 'Copy', 1500); }};
    const sel = () => {{ const r = document.createRange(); r.selectNodeContents(pre); const s = getSelection(); s.removeAllRanges(); s.addRange(r); b.textContent = 'Selected'; }};
    try {{ navigator.clipboard.writeText(pre.innerText).then(done, sel); }} catch (e) {{ sel(); }}
  }}));
}})();
</script>
"""
(OUT / "index.html").write_text(page)

# Full calendar as its own page inside the same artifact
cal = (ROOT / "instagram-content-calendar.html").read_text()
back = '<a href="index.html#instagram" style="position:fixed;right:max(16px,env(safe-area-inset-right,0px));bottom:calc(16px + env(safe-area-inset-bottom,0px));z-index:20;font:600 13px system-ui,sans-serif;background:#1F2A44;color:#fff;padding:9px 14px;border-radius:999px;text-decoration:none">Back to Marginwise HQ</a>'
i = cal.index("</style>") + len("</style>")
cal = cal[:i] + back + cal[i:]
(OUT / "calendar.html").write_text(
    '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
    '<style>body{margin:0}</style>' + cal + "</html>"
)
print(OUT / "index.html", (OUT / "index.html").stat().st_size)
