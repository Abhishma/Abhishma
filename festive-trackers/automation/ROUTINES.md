# Routines

Two scheduled Claude Code Routines keep the trackers current and send a morning summary. Both run in a fresh cloud session with this repo checked out and the Shopify and Linkrunner connectors attached.

Settings for both live in `automation/config.json`. Until `artifactUrl` (the combined page) is filled in, both routines stop at step 1 and report that.

## Why a scheduled refresh is needed

Each tracker page pulls data only while someone who has the Shopify and Linkrunner connectors keeps it open: a full pull every hour and a today-only tick every 2 minutes. The results are saved to the page's shared database. If nobody with the connectors opens the page, nothing gets saved, so viewers without connectors see stale numbers and the next connected viewer has to wait through a long backfill.

The refresh routine fills in and finalises **past days** in that database on a schedule. It does not write anything for today, the projection, stock or returns. The page's live tier owns those, and they rely on state this job does not have.

## What the refresh routine writes

| Record | Big Festive Days (`bfd`) | All Categories (`r4r`) |
|---|---|---|
| `skus/<date>` | Every SKU line for the day, exactly as the page saves it | Same |
| `days/<date>` | Store totals by channel, web sessions, landing-page groups, app funnel. `final: true` from D-2 back | Same, plus `lpv: 3`. Always `final: false` (see below) |

Both records come from `automation/day-builder.mjs`. The script lifts each tracker's own query strings and shaping functions out of its HTML and runs them in a sandbox, so the routine writes byte-for-byte what the page would write. If a tracker's code changes, the next run picks the change up. If the code changes shape in a way the extractor cannot read, the script stops with an error and nothing is written.

**Why `r4r` days stay non-final.** The All Categories page assigns product landing pages that are missing from its built-in map using product handles it learns during a live stock lookup. This job does not run that lookup, so a few unmapped pages fall into the `X` bucket. Because the day is left non-final, the page re-pulls it with full mapping the next time a connected viewer opens it. Until then, every number except that one landing-page split is already correct.

## Refresh routine

Schedule: 06:10 and 14:10 IST daily, 1 Oct to 10 Nov 2026 (2 extra days so the last sale days get finalised). Cron: `CRON_TZ=Asia/Kolkata 10 6,14 * * *`.

Prompt:

```
Refresh the R4R festive trackers. Work in the r4r-festive-trackers repo.

1. Read automation/config.json. If artifactUrl is empty, stop and report that. Both trackers (bfd, r4r) live in that one artifact; each tracker's collection names are under trackers.<key>.collections.
2. For each tracker, list its days collection (config trackers.<key>.collections.days) with ArtifactData. Today = current date in IST. Target dates = every date from config.backfillFrom to today-1 where the days doc is missing, or has v different from DATA_V (from `node automation/day-builder.mjs info <tracker>`), or has final !== true, or is one of today-1 or today-2. Take at most config.maxDatesPerRun dates, oldest first.
3. Run `node automation/day-builder.mjs plan <tracker> <dates...>` for each tracker. Merge the call lists and drop duplicate ids (most calls are shared between the trackers).
4. Make each call with the named connector tool (Shopify run-analytics-query, Linkrunner run_funnel) using the exact input. Save the raw payloads to /tmp/responses.json as {"<id>": payload}. If a connector errors, retry once. If it still fails, skip the trackers that need it and report it.
5. Run `node automation/day-builder.mjs build <tracker> /tmp/responses.json <dates...>` for each tracker. Apply its output to artifactUrl with ArtifactData batches of up to 50 writes, in the order given (skus before days).
6. Report one line per tracker: dates written, dates skipped and why. Do not commit anything.
```

## Daily digest routine

Schedule: 08:50 IST daily, 2 Oct to 9 Nov 2026. Cron: `CRON_TZ=Asia/Kolkata 50 8 * * *`.

Prompt:

```
Write the R4R festive trackers morning digest. Work in the r4r-festive-trackers repo.

1. Read automation/config.json. If artifactUrl is empty, stop and report that.
2. For each tracker, read its days collection and its skus doc for yesterday (IST) from artifactUrl with ArtifactData, using the collection names in config. Save them as /tmp/<tracker>-records.json in the shape {"days": {"<date>": doc}, "skus": {"<date>": doc}}.
3. Run `node automation/digest.mjs <tracker> /tmp/<tracker>-records.json` and save the output to digests/<yesterday>-<tracker>.md.
4. If yesterday's record is missing, run the refresh routine steps for yesterday only, then retry step 2 once.
5. Commit the digests to main with the message "Digest <yesterday>" and push.
6. Reply with the Flags section of each digest and the artifact link.
```

## Setup checklist

1. Connect the Shopify and Linkrunner connectors to the claude.ai account that runs the routines.
2. The combined page is published at https://claude.ai/artifact/HwcS4prgQq6hFhEzBqvmD8. Put that URL in `automation/config.json`. The routines need edit access to it.
3. Create the two routines with the prompts above, attaching only the Shopify and Linkrunner connectors.
4. Run the refresh routine once manually and check that the tracker's status line shows the saved days.
