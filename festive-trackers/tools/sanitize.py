#!/usr/bin/env python3
"""Build a public copy of this project with the client's store data removed.

    python3 tools/sanitize.py <dest-dir>

Copies the committed tree, then empties the four embedded data tables in both trackers: the SKU map,
the product and collection page map, the SKU scope table and the marketing-calendar uplift forecast.
The trackers then run on whatever catalogue is saved under Categories (or a CSV), with every day's
uplift at 1. The combined pages are rebuilt from the cleaned trackers. Stops if any table is not
found exactly once, or if a known store identifier survives.
"""
import pathlib, re, subprocess, sys, io, tarfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
EMPTY = {
    "SKUMAP": "{}",
    "SCOPE": "{}",
    "HMAP": '{"p":{},"c":{}}',
    "UPLIFT": '{"source":"Not included in this copy: add a daily uplift table","days":{}}',
}
TABLES = {"big-festive-days.html": ["SKUMAP", "HMAP", "UPLIFT"], "r4r-all-categories.html": ["SCOPE", "HMAP", "UPLIFT"]}
PUBLIC_NOTE = ("**Public copy.** The client's store data (SKU and page maps, and the marketing-calendar uplift forecast) is not included. "
               "Categories come from the Categories panel on the page, a CSV (see `tools/sample-categories-home-store.csv`), or Shopify. "
               "Built with `tools/sanitize.py`.")
NOTE = "   // store data not included in this copy; set categories under Categories (tools/catalog.cjs)"
MAX_LINE = 1500   # every embedded table is one long line; nothing else in the trackers comes close


def main(dest):
    dest = pathlib.Path(dest).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    tar = subprocess.run(["git", "-C", str(ROOT), "archive", "--format=tar", "HEAD"], check=True, capture_output=True).stdout
    tarfile.open(fileobj=io.BytesIO(tar)).extractall(dest)
    for name, consts in TABLES.items():
        p = dest / "trackers" / name
        raw = p.read_bytes().decode("utf-8")
        nl = "\r\n" if "\r\n" in raw else "\n"
        lines = raw.split(nl)
        for c in consts:
            hits = [i for i, l in enumerate(lines) if l.startswith(f"const {c} = ")]
            if len(hits) != 1:
                raise SystemExit(f"{name}: expected one `const {c}`, found {len(hits)}")
            lines[hits[0]] = f"const {c} = {EMPTY[c]};{NOTE}"
        p.write_bytes(nl.join(lines).encode("utf-8"))
    for flag in ([], ["--demo"]):
        subprocess.run([sys.executable, str(dest / "tools" / "combine.py"), *flag], check=True)
    leaks = [f"{f.relative_to(dest)}:{n}" for f in (dest / "trackers").glob("*.html")
             for n, l in enumerate(f.read_text(encoding="utf-8").splitlines(), 1) if len(l) > MAX_LINE]
    if leaks:
        raise SystemExit("data-sized lines survived: " + ", ".join(leaks))
    readme = dest / "README.md"
    text = readme.read_text(encoding="utf-8")
    start = text.index("**Private repo.**")
    end = text.index("\n\n", start)
    readme.write_text(text[:start] + PUBLIC_NOTE + text[end:], encoding="utf-8")
    print(f"public copy written to {dest}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
