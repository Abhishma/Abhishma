# R4R festive trackers

Live trackers for R for Rabbit's Big Festive Days sale, Lowest Price of the Year: 1 Oct to 8 Nov 2026, 39 sale days, D2C web and app. The repo also holds the automation that keeps them current.

**Public copy.** The client's store data (SKU and page maps, and the marketing-calendar uplift forecast) is not included. Categories come from the Categories panel on the page, a CSV (see `tools/sample-categories-home-store.csv`), or Shopify. Built with `tools/sanitize.py`.

## Trackers

| File | What it tracks | Scope |
|---|---|---|
| `trackers/big-festive-days.html` | The whole sale, store-wide: day view, categories, SKUs, returns, D0 projection, sale vs baseline | All categories. Web 10% / app 12% sitewide; flash days web 12% / app 15% plus free gift |
| `trackers/r4r-all-categories.html` | The same sale through a segment lens: D0, summary, segments, SKU, stock, sales loss, sources | Whole store, with Ride-Ons, Toys and Project Dolphin (249 SKUs) as focus segments |

Calendar shared by both: baseline 17 to 30 Sep; Flash Sale 1 on 7 to 8 Oct; Flash Sale 2 on 17 to 18 Oct; payday week 28 Oct to 7 Nov.

### Combined page

`trackers/festive-trackers.html` is the one page to publish and share. It holds both trackers behind a switcher (Store-wide, All categories); one runs per page load, and the choice is remembered per viewer. Rebuild it with `python3 tools/combine.py` after editing either tracker. Published at https://claude.ai/artifact/HwcS4prgQq6hFhEzBqvmD8 (private until shared).

Both trackers share that artifact's database. The store-wide tracker keeps the original collection names. The All Categories tracker's collections are prefixed `r4r_` (`r4r_days`, `r4r_skus`, `r4r_proj`, `r4r_live`, `r4r_inv`, `r4r_ret`, `r4r_ga4`), because the two save different record shapes under the same names.

### Demo copy

`trackers/festive-trackers-demo.html` (`python3 tools/combine.py --demo`) is the same page with a sample-data banner and no connector access, published at https://claude.ai/artifact/P3tL6JhmRdgFbjpJeGiic2. Its database holds illustrative numbers from `automation/demo-data.mjs` for 17 Sep to 3 Oct 2026: the real catalogue, with made-up sales, traffic and funnels. Every sample record carries `demo: true`. Never load demo data into the live tracker.

`trackers/snapshots/` holds the plain-text header of each page as exported, kept for reference.

### How they run

Each tracker is a single-file claude.ai artifact. It asks the runtime for four capabilities:

| Capability | Used for |
|---|---|
| `mcp` | Shopify (`run-analytics-query`, `graphql_query`) and Linkrunner (`run_funnel`) |
| `db` | Shared saved data: `days`, `skus`, `proj/latest`, `live/d0`, `ga4`, `returns`/`ret`, and `inv` (All Categories only) |
| `user` | Write permission check: read-only viewers follow along without saving |
| `downloads` | Excel export |

Refresh tiers while the page is open: a full pull every hour (two months of history for curves and weekday factors), a today-only tick every 2 minutes, and stock every 10 minutes (All Categories). Viewers without the connectors follow `live/d0` as long as one connected viewer has the page open.

GA4 is a manual CSV import on the page. It is not pulled automatically.

## Connectors

| Source | How it connects |
|---|---|
| Shopify | Directory connector at claude.ai/customize/connectors |
| Unicommerce, ClickPost | `connectors/ops-mcp`: our own read-only connector. Deploy steps are in its README |
| Linkrunner | Linkrunner's own MCP server, added as a custom connector (ask Linkrunner for the URL) |
| GA4 | CSV import on the page, or Supermetrics or Windsor.ai if a live pull is needed |

## Automation

The pages only stay fresh while someone with the connectors has them open. `automation/` closes that gap:

| Piece | Role |
|---|---|
| `day-builder.mjs` | Builds the exact `days`/`skus` records each page saves, by running the tracker's own query and shaping code against connector payloads (two passes: `plan`, then `build`) |
| `digest.mjs` | Turns saved records into a morning Markdown summary: GMV, orders and units vs baseline and vs the same day last week, channel split, web and app funnels, top 10 SKUs, landing groups, flags |
| `ROUTINES.md` | Schedules, prompts and setup checklist for the refresh routine (06:10 and 14:10 IST) and the digest routine (08:50 IST) |
| `config.json` | Tracker artifact URLs and backfill window |

Run the tests with `npm test` (Node 20+, no dependencies).

### What the automation does not do

- It does not write today's numbers, the D0 projection, stock, sales loss or returns. Those stay with the page's live tier.
- All Categories days are written non-final. The page re-pulls them once to apply product-handle mapping that needs a live stock lookup. See `ROUTINES.md`.
- If a tracker's code changes in a way the extractor cannot parse, the scripts fail loudly instead of writing a guessed shape.
