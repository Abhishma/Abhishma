"""Render market-research-boring-problems.md to a phone-friendly HTML page."""
import re, sys, html
from pathlib import Path
import markdown

SRC = Path(__file__).resolve().parents[2] / "market-research-boring-problems.md"
OUT = Path(__file__).resolve().parents[2] / "market-research-boring-problems.html"

md = SRC.read_text()
body = markdown.markdown(md, extensions=["tables", "fenced_code", "toc"])

# wrap tables for horizontal scroll
body = body.replace("<table>", '<div class="tw"><table>').replace("</table>", "</table></div>")
# copy buttons on code blocks
body = re.sub(r"<pre><code>", '<div class="cb"><button class="copy" type="button">Copy</button><pre><code>', body)
body = body.replace("</code></pre>", "</code></pre></div>")
# open links in new tab
body = body.replace('<a href="http', '<a target="_blank" rel="noopener" href="http')

nav = "".join(
    f'<a href="#{i}">{html.escape(re.sub(r"^\d+\.\s*", "", t))}</a>'
    for i, t in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body)
)

page = f"""<title>Marginwise Market Map</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;800&family=Public+Sans:wght@400;600&family=IBM+Plex+Mono:wght@400&display=swap">
<style>
/* Layout: single reading column with a sticky chip nav of sections; wide tables scroll inside their own box */
:root {{
  --bg: #f6f7f9; --surface: #ffffff; --fg: #1b2333; --muted: #5b6577;
  --navy: #1F2A44; --green: #2E9E7E; --red: #C0533A; --line: #dde2ea; --code: #eef1f5;
  --display: "Archivo", "Helvetica Neue", Arial, sans-serif;
  --body: "Public Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #11161f; --surface: #171d29; --fg: #e4e8ef; --muted: #9aa4b5;
  --navy: #9fb3e0; --green: #4cc29f; --red: #e07a62; --line: #2a3242; --code: #1e2533; color-scheme: dark }} }}
:root[data-theme="dark"] {{
  --bg: #11161f; --surface: #171d29; --fg: #e4e8ef; --muted: #9aa4b5;
  --navy: #9fb3e0; --green: #4cc29f; --red: #e07a62; --line: #2a3242; --code: #1e2533; color-scheme: dark }}
body {{ background: var(--bg); color: var(--fg); font: 15px/1.6 var(--body); }}
body::before {{ content: ""; position: fixed; inset: 0 0 auto; height: env(safe-area-inset-top, 0px); z-index: 10; background: var(--surface); }}
nav {{ position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5; background: var(--surface); border-bottom: 1px solid var(--line);
  display: flex; gap: 8px; overflow-x: auto; padding-block: 10px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); scrollbar-width: thin; }}
nav a {{ flex: none; font: 600 13px var(--body); color: var(--navy); text-decoration: none; border: 1px solid var(--line); border-radius: 999px; padding: 5px 12px; white-space: nowrap; }}
nav a:hover, nav a:focus-visible {{ border-color: var(--green); color: var(--green); outline: none; }}
main {{ max-width: 860px; margin: 0 auto; padding-block: 24px 64px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }}
h1 {{ font: 800 clamp(26px, 5vw, 38px)/1.15 var(--display); color: var(--navy); text-wrap: balance; margin: 8px 0 12px; }}
h2 {{ font: 800 24px/1.25 var(--display); color: var(--navy); margin: 48px 0 12px; padding-top: 16px; border-top: 3px solid var(--green); text-wrap: balance; scroll-margin-top: 64px; }}
h3 {{ font: 700 18px/1.3 var(--display); margin: 28px 0 8px; scroll-margin-top: 64px; }}
p, li {{ max-width: 68ch; }}
a {{ color: var(--green); }}
strong {{ color: var(--fg); }}
.tw {{ overflow-x: auto; margin: 12px 0 20px; border: 1px solid var(--line); border-radius: 6px; background: var(--surface); }}
table {{ border-collapse: collapse; font-size: 13.5px; min-width: 640px; width: 100%; font-variant-numeric: tabular-nums; }}
th {{ text-align: left; background: var(--navy); color: var(--surface); font: 600 12.5px var(--body); letter-spacing: .02em; padding: 8px 10px; }}
td {{ padding: 8px 10px; border-top: 1px solid var(--line); vertical-align: top; }}
tr:last-child td strong {{ color: var(--green); }}
.cb {{ position: relative; margin: 10px 0 18px; }}
pre {{ background: var(--code); border: 1px solid var(--line); border-radius: 6px; padding: 14px; overflow-x: auto; white-space: pre-wrap; font: 13px/1.55 var(--mono); }}
code {{ font-family: var(--mono); font-size: 0.92em; }}
.copy {{ position: absolute; top: 8px; right: 8px; font: 600 12px var(--body); background: var(--green); color: #fff; border: 0; border-radius: 4px; padding: 5px 10px; cursor: pointer; }}
.copy:focus-visible {{ outline: 2px solid var(--navy); outline-offset: 2px; }}
hr {{ border: 0; height: 0; margin: 0; }}
@media (prefers-reduced-motion: no-preference) {{ html {{ scroll-behavior: smooth; }} }}
</style>
<nav aria-label="Sections">{nav}</nav>
<main>
{body}
</main>
<script>
document.querySelectorAll('.copy').forEach(b => b.addEventListener('click', () => {{
  const t = b.nextElementSibling.innerText;
  const done = () => {{ b.textContent = 'Copied'; setTimeout(() => b.textContent = 'Copy', 1500); }};
  try {{ navigator.clipboard.writeText(t).then(done, () => sel(b)); }} catch (e) {{ sel(b); }}
}}));
function sel(b) {{ const r = document.createRange(); r.selectNodeContents(b.nextElementSibling); const s = getSelection(); s.removeAllRanges(); s.addRange(r); b.textContent = 'Selected'; }}
</script>
"""
OUT.write_text(page)
print(OUT, len(page))
