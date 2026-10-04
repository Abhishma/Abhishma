#!/usr/bin/env python3
"""Combine the two tracker pages into one artifact page: trackers/festive-trackers.html.

Each tracker keeps its own markup, styles and script. The script gets a few targeted patches:

- Database: the All Categories tracker's collections are prefixed `r4r_`, because the two trackers
  save different shapes under the same names (days, skus, proj, live, ga4).
- Categories: every taxonomy constant reads `window.__TK_OV` first (built by tools/catalog.cjs from the
  catalogue saved in the page database), so the trackers work on any store's categories. With no
  saved catalogue they fall back to the built-in R for Rabbit map, unchanged.

Every patch must match exactly once, or the build stops: a tracker edit can never be patched silently wrong.
Only one tracker runs per page load; the switcher reloads into the other.

`--demo` builds trackers/festive-trackers-demo.html instead: the same page with a sample-data banner,
published without connector access and filled by automation/demo-data.mjs.
"""
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHELL = ROOT / "tools" / "shell"
TRACKERS = [
    ("bfd", "big-festive-days.html", "Store-wide", "Big Festive Days, every category"),
    ("r4r", "r4r-all-categories.html", "All categories", "Segments, stock and sales loss"),
]
DB_LINE = "  S.db = db; S.mcp = mcp; S.downloads = downloads;"
PREFIX = {"r4r": "r4r_"}

# Taxonomy constants each tracker reads from the catalogue when one is saved.
OVERRIDES = {
    "bfd": ["CATS", "SKUMAP", "HMAP", "TOOL_PAGES"],
    "r4r": ["SCOPE", "CATS", "HMAP", "FOCUS", "TOOL_PAGES", "NO_STOCK_CATS"],
}

R4R_DOLPHIN_LIST = "Category comes from the master marketing calendar SKU map; SKUs not on it use the product's \"Report - &lt;category&gt;\" tag in Shopify, then the product name. Sub-category comes from the Dolphin CM list, then the \"Report - &lt;sub-category&gt;\" tag, then the name. <b>Focus groups</b> sit on top: <b>Ride-Ons</b> and <b>Toys</b> split \"Ride ons and Toys\" by sub-category, and <b>Project Dolphin</b> = the 249 category-manager SKUs (they overlap categories). Every total counts a SKU once."
TOOLS_SENTENCE = "<b>Parenting tools are excluded:</b> sessions that landed on /pages/parenting-tools or any of the 18 tools it links to (gender predictor, nakshatra, numerology, baby names and so on) are left out of every sessions, traffic and conversion figure."
GENERIC_TOOLS = "${__OV.CATS ? (__OV.TOOL_PAGES.length && __OV.TOOL_PAGES[0] !== '/__no-excluded-page__' ? `<b>Excluded pages:</b> sessions that landed on any of the ${__OV.TOOL_PAGES.length} pages listed under Categories are left out of every sessions, traffic and conversion figure.` : '<b>No pages are excluded:</b> every session counts.') : `" + TOOLS_SENTENCE + "`}"

PATCHES = {
    "bfd": [
        ("Category comes from the master marketing calendar's SKU map (1,634 live SKUs).",
         "${__OV.CATS ? `Category comes from the store catalogue (${Object.keys(__OV.SKUMAP).length.toLocaleString('en-IN')} SKUs).` : `Category comes from the master marketing calendar's SKU map (1,634 live SKUs).`}"),
        ("['Category and SKU', 'Shopify order lines, category from the master marketing calendar SKU map. An order with two SKUs from one category counts twice at category level.'],",
         "['Category and SKU', __OV.CATS ? 'Shopify order lines, category from the store catalogue. An order with two SKUs from one category counts twice at category level.' : 'Shopify order lines, category from the master marketing calendar SKU map. An order with two SKUs from one category counts twice at category level.'],"),
        (TOOLS_SENTENCE, GENERIC_TOOLS),
    ],
    "r4r": [
        ("const SEG_CODE = { 'Ride-Ons': 'R', 'Toys': 'T', 'Project Dolphin': 'D' };",
         "const SEG_CODE = {}; FOCUS.forEach((g, i) => { SEG_CODE[g] = ['R', 'T', 'D'][i]; });"),
        ("const SEG_COL = { 'Ride-Ons': 'var(--ride)', 'Toys': 'var(--toy)', 'Project Dolphin': 'var(--dol)' };",
         "const SEG_COL = {}; FOCUS.forEach((g, i) => { SEG_COL[g] = ['var(--ride)', 'var(--toy)', 'var(--dol)'][i]; });"),
        ("const focusOf = sku => { const x = SCOPE[sku]; if (!x) return []; const o = []; if (x[1] === 'R') o.push('Ride-Ons'); if (x[1] === 'T') o.push('Toys'); if (x[2]) o.push('Project Dolphin'); return o; };",
         "const focusOf = sku => { const x = SCOPE[sku]; if (!x) return []; return FOCUS.filter(g => String(x[1] || '').includes(SEG_CODE[g]) || (SEG_CODE[g] === 'D' && x[2])); };   // x[1]: focus codes, x[2]: legacy third-group flag"),
        ("const segPillsOf = codes => [...codes].filter(c => c !== 'C').map(c => `<span class=\"seg-pill ${c}\">${c === 'R' ? 'Ride-Ons' : c === 'T' ? 'Toys' : 'Dolphin'}</span>`).join('');",
         "const segPillsOf = codes => [...codes].filter(c => c !== 'C').map(c => { const g = FOCUS.find(x => SEG_CODE[x] === c) || c; return `<span class=\"seg-pill ${c}\">${g === 'Project Dolphin' ? 'Dolphin' : esc(g)}</span>`; }).join('');"),
        ("for (const ch of codes) add(ch === 'R' ? 'Ride-Ons' : ch === 'T' ? 'Toys' : 'Project Dolphin', v);",
         "for (const ch of codes) { const g = FOCUS.find(x => SEG_CODE[x] === ch); if (g) add(g, v); }"),
        ("const holdsNoStock = s => NO_STOCK_CATS.includes(catOfSku(s)) || /^(combo|codfd|cobw|copb|comf|kits|tgpr)/i.test(s);",
         "const holdsNoStock = s => NO_STOCK_CATS.includes(catOfSku(s)) || ('NO_STOCK_RE' in __OV ? !!(__OV.NO_STOCK_RE && __OV.NO_STOCK_RE.test(s)) : /^(combo|codfd|cobw|copb|comf|kits|tgpr)/i.test(s));"),
        (R4R_DOLPHIN_LIST,
         "${__OV.CATS ? `Category, sub-category and focus groups come from the store catalogue (set under Categories above the tracker).${FOCUS.length ? ` <b>Focus groups</b>: ${FOCUS.map(esc).join(', ')}. They can overlap categories.` : ''} Every total counts a SKU once.` : `" + R4R_DOLPHIN_LIST + "`}"),
        ("['Scope', 'Whole store, every category and SKU. Focus groups: Ride-Ons and Toys (the \"Ride ons and Toys\" category split by sub-category) and Project Dolphin (249 category-manager SKUs, overlapping categories). Totals count each SKU once.'],",
         "['Scope', __OV.CATS ? 'Whole store, every category and SKU, from the store catalogue.' + (FOCUS.length ? ' Focus groups: ' + FOCUS.join(', ') + ' (they can overlap categories).' : '') + ' Totals count each SKU once.' : 'Whole store, every category and SKU. Focus groups: Ride-Ons and Toys (the \"Ride ons and Toys\" category split by sub-category) and Project Dolphin (249 category-manager SKUs, overlapping categories). Totals count each SKU once.'],"),
        (TOOLS_SENTENCE, GENERIC_TOOLS),
    ],
}
SCOPE_LINE_START = "document.getElementById('scopeLine').textContent = "
SCOPE_LINE_NEW = "document.getElementById('scopeLine').textContent = `${SKU_LIST.length.toLocaleString('en-IN')} SKUs in ${CATS.length} categories${FOCUS.length ? ' · focus: ' + FOCUS.map(g => `${g} ${SKU_LIST.filter(k => inSeg(k, g)).length}`).join(', ') : ''}`;"


def once(script, old, new, name):
    n = script.count(old)
    if n != 1:
        raise SystemExit(f"{name}: expected one match for patch, found {n}: {old[:80]}")
    return script.replace(old, new)


def patch(key, script, name):
    script = once(script, "'use strict';\n", "'use strict';\nconst __OV = window.__TK_OV || {};   // catalogue overrides (tools/catalog.cjs); empty = built-in map\n", name)
    lines = script.split("\n")
    for const in OVERRIDES[key]:
        hits = [i for i, l in enumerate(lines) if l.startswith(f"const {const} = ")]
        if len(hits) != 1:
            raise SystemExit(f"{name}: expected one `const {const}`, found {len(hits)}")
        i = hits[0]
        lines[i] = lines[i].replace(f"const {const} = ", f"const {const} = __OV.{const} || ", 1)
    if key == "r4r":
        hits = [i for i, l in enumerate(lines) if l.startswith(SCOPE_LINE_START)]
        if len(hits) != 1:
            raise SystemExit(f"{name}: scope line not found")
        lines[hits[0]] = SCOPE_LINE_NEW
    script = "\n".join(lines)
    for old, new in PATCHES[key]:
        script = once(script, old, new, name)
    return script


def split(key, path):
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    body = text.split("<body>", 1)[1].rsplit("</body>", 1)[0]
    head, rest = body.split("\n<style>\n", 1)
    if "<title>" not in head:
        raise SystemExit(f"{path.name}: unexpected page head")
    markup, script = rest.split("\n<script>\n", 1)
    script = script.rsplit("</script>", 1)[0]
    if "</script" in script or "</template" in markup:
        raise SystemExit(f"{path.name}: cannot embed safely")
    script = once(script, DB_LINE, DB_LINE if key not in PREFIX else DB_LINE.replace(
        "S.db = db;",
        f"S.db = db && {{ collection: p => db.collection('{PREFIX[key]}' + p), doc: p => db.doc('{PREFIX[key]}' + p) }};   // own namespace in the shared database"), path.name)
    return "<style>\n" + markup, patch(key, script, path.name)


DEMO_BANNER = """<p class="tk-demo" role="note"><b>Sample data.</b> Illustrative numbers on the real catalogue, not R for Rabbit sales. Live views (D0, stock, returns) stay empty here.</p>"""


def main(demo=False):
    parts = {key: split(key, ROOT / "trackers" / f) for key, f, *_ in TRACKERS}
    buttons = "\n    ".join(
        f'<button type="button" data-k="{k}" aria-pressed="false"><b>{label}</b><span>{sub}</span></button>'
        for k, _, label, sub in TRACKERS)
    title = "Big Festive Days Demo" if demo else "Big Festive Days Trackers"
    shell = (SHELL / "shell.html").read_text(encoding="utf-8").replace("{{BUTTONS}}", buttons).replace("{{DEMO_BANNER}}", DEMO_BANNER if demo else "")
    catalog_js = (ROOT / "tools" / "presets.cjs").read_text(encoding="utf-8") + "\n" + (ROOT / "tools" / "catalog.cjs").read_text(encoding="utf-8")
    boot_js = (SHELL / "boot.js").read_text(encoding="utf-8").replace("/*DEMO*/false", "true" if demo else "false")
    for js in (catalog_js, boot_js):
        if "</script" in js:
            raise SystemExit("shell script cannot be embedded")
    out = [f"""<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
{(SHELL / "shell.css").read_text(encoding="utf-8")}</style>

{shell}
"""]
    for key, *_ in TRACKERS:
        markup, script = parts[key]
        out.append(f'<template id="tk-{key}-ui">\n{markup}\n</template>\n')
        out.append(f'<script type="text/x-tracker" id="tk-{key}-js">\n{script}</script>\n')
    out.append(f"<script>\n{catalog_js}</script>\n<script>\n{boot_js}</script>\n")
    dest = ROOT / "trackers" / ("festive-trackers-demo.html" if demo else "festive-trackers.html")
    dest.write_text("".join(out), encoding="utf-8")
    print(f"wrote {dest.relative_to(ROOT)} ({dest.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main(demo="--demo" in sys.argv[1:])
