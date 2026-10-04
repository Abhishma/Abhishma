#!/usr/bin/env node
/*
 * day-builder: builds the exact `days/<date>` and `skus/<date>` records a tracker page saves,
 * using the tracker's OWN query and shaping code lifted from its HTML. Nothing is re-implemented,
 * so a change to a tracker's queries or record shape flows through on the next run.
 *
 * The connectors (Shopify, Linkrunner) are only reachable as Claude tool calls, so this runs in
 * two passes around them:
 *
 *   node day-builder.mjs plan  <tracker> <date> [<date> ...]   > calls.json
 *       Prints every connector call needed: [{ id, server, tool, input }].
 *       The routine makes each call and saves { "<id>": <raw payload>, ... } to responses.json.
 *
 *   node day-builder.mjs build <tracker> responses.json <date> [<date> ...]  > writes.json
 *       Replays the tracker's code against the saved payloads and prints the ArtifactData
 *       batch: [{ op: "set", collection, doc_id, data }], skus before days (the page's own order).
 *
 * Add `--catalog catalog.json` to plan and build when the page has a saved catalogue (Categories panel),
 * so landing pages group by the store's own categories.
 *
 *   node day-builder.mjs info <tracker>
 *       Prints the tracker's DATA_V (record version), sale window and baseline window.
 *
 * <tracker> is `bfd` (Big Festive Days) or `r4r` (All Categories).
 */
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import vm from 'node:vm';
import { createRequire } from 'node:module';

const TKCatalog = createRequire(import.meta.url)('../tools/catalog.cjs');

const HERE = dirname(fileURLToPath(import.meta.url));
export const TRACKERS = {
  // `ns` matches the collection prefix each tracker uses inside the combined page (tools/combine.py).
  bfd: { file: 'big-festive-days.html', lpFn: 'catOfPath', ns: '' },
  r4r: { file: 'r4r-all-categories.html', lpFn: 'comboOfPath', ns: 'r4r_' },
};

// LR shares SHOP's line; MIXED and UNMAPPED_PAGES share OTHER_PAGES' line.
const CONSTS = ['SHOP', 'DATA_V', 'SALE', 'BASE', 'CATS', 'HMAP', 'TOOL_PAGES', 'NO_TOOLS', 'OTHER_PAGES', 'addD', 'days', 'chKey', 'num', 'shopQ'];
const FUNCS = ['rowsOf', 'fetchShopRange', 'fetchSkuDay', 'fetchLpDay', 'fetchAppDay'];

function scriptOf(html) {
  const m = html.match(/<script>([\s\S]*?)<\/script>/);
  if (!m) throw new Error('No inline <script> found in tracker');
  return m[1].split(/\r?\n/);
}
function constLine(lines, name) {
  const l = lines.find(x => x.startsWith(`const ${name} `));
  if (!l) throw new Error(`Tracker has no top-level const ${name}`);
  if (!l.trimEnd().endsWith(';') && !l.includes('; ')) throw new Error(`const ${name} spans lines; extractor needs updating`);
  return l;
}
function funcBlock(lines, name) {
  const i = lines.findIndex(x => new RegExp(`^(async )?function ${name}\\(`).test(x));
  if (i < 0) throw new Error(`Tracker has no function ${name}`);
  const j = lines.findIndex((x, k) => k > i && x === '}');
  return lines.slice(i, j + 1).join('\n');
}

/* Loads the tracker's code into a sandbox whose `call` is either a recorder or a replayer.
   With a catalogue (the generic shape saved under Categories on the page), landing pages group by its
   categories exactly as the page does; without one, by the tracker's built-in map. */
const CATALOG_CONSTS = ['CATS', 'HMAP', 'TOOL_PAGES'];
export function loadTracker(key, call, catalog = null) {
  const t = TRACKERS[key];
  if (!t) throw new Error(`Unknown tracker "${key}" (use bfd or r4r)`);
  const lines = scriptOf(readFileSync(join(HERE, '..', 'trackers', t.file), 'utf8'));
  let ov = null;
  if (catalog) {
    const errs = TKCatalog.validate(catalog);
    if (errs.length) throw new Error('Catalogue is not usable: ' + errs.join(' '));
    ov = TKCatalog.apply(key, catalog);
  }
  const src = [
    ...CONSTS.map(n => (ov && CATALOG_CONSTS.includes(n) ? `const ${n} = ${JSON.stringify(ov[n])};` : constLine(lines, n))),
    ...FUNCS.map(n => funcBlock(lines, n)),
    funcBlock(lines, t.lpFn),
    'const S = { handles: {} };',
    `({ SHOP, LR, DATA_V, SALE, BASE, addD, ${FUNCS.join(', ')} })`,
  ].join('\n');
  return vm.runInNewContext(src, { call, console });
}

export const callId = (server, tool, input) =>
  createHash('sha1').update(JSON.stringify([server, tool, input])).digest('hex').slice(0, 12);

const EMPTY = { columns: [], rows: [] };
const EMPTY_FUNNEL = { steps: [{ users: 0 }, { users: 0 }, { users: 0 }, { users: 0 }] };

async function runDays(T, dates) {
  const out = {};
  // One store-level pull per day keeps call ids stable whatever set of dates a run picks.
  for (const d of dates) {
    const range = await T.fetchShopRange(d, d);
    const [rows, lp, app] = await Promise.all([T.fetchSkuDay(d), T.fetchLpDay(d), T.fetchAppDay(d)]);
    out[d] = { range: range[d], rows, lp, app };
  }
  return out;
}

export async function plan(key, dates, { catalog = null } = {}) {
  const calls = [];
  const T = loadTracker(key, async (server, tool, input) => {
    calls.push({ id: callId(server, tool, input), server, tool, input });
    return tool === 'run_funnel' ? EMPTY_FUNNEL : EMPTY;
  }, catalog);
  await runDays(T, dates);
  return calls;
}

export async function build(key, responses, dates, { today, now = Date.now(), catalog = null } = {}) {
  const missing = [];
  const T = loadTracker(key, async (server, tool, input) => {
    const id = callId(server, tool, input);
    if (!(id in responses)) { missing.push(id); return tool === 'run_funnel' ? EMPTY_FUNNEL : EMPTY; }
    return responses[id];
  }, catalog);
  const got = await runDays(T, dates);
  if (missing.length) throw new Error(`Missing responses for call ids: ${missing.join(', ')}`);
  const yesterday = T.addD(today, -1);
  const writes = [];
  for (const d of dates) {
    if (d >= today) throw new Error(`${d} is today or later; the page's live tier owns today`);
    const g = got[d];
    const day = { date: d, shop: g.range.shop, sess: g.range.sess, lp: g.lp, app: g.app, hasSku: true, v: T.DATA_V, fetchedAt: now };
    if (key === 'bfd') day.final = d < yesterday;
    else {
      day.lpv = 3;
      // The page maps product pages missing from its static map through handles it learns from a live
      // stock lookup this job does not run. Leave the day open so the page re-pulls it with full mapping.
      day.final = false;
    }
    const ns = TRACKERS[key].ns;
    writes.push({ op: 'set', collection: ns + 'skus', doc_id: d, data: { date: d, rows: g.rows, fetchedAt: now } });
    writes.push({ op: 'set', collection: ns + 'days', doc_id: d, data: day });
  }
  return JSON.parse(JSON.stringify(writes));   // plain objects, as the database stores them
}

export const istToday = () => new Date(Date.now() + 19800000).toISOString().slice(0, 10);

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  // --catalog <file>: the page's saved catalogue as one JSON object (catalog/meta plus its parts, joined).
  const ci = args.indexOf('--catalog');
  const catalog = ci >= 0 ? JSON.parse(readFileSync(args.splice(ci, 2)[1], 'utf8')) : null;
  const [cmd, key, ...rest] = args;
  const fail = m => { console.error(m); process.exit(1); };
  const isDate = s => /^\d{4}-\d{2}-\d{2}$/.test(s);
  try {
    if (cmd === 'info') {
      const T = loadTracker(key, async () => { throw new Error('info makes no connector calls'); });
      console.log(JSON.stringify({ DATA_V: T.DATA_V, SALE: T.SALE, BASE: T.BASE }));
    } else if (cmd === 'plan') {
      if (!rest.length || !rest.every(isDate)) fail('usage: plan <bfd|r4r> <YYYY-MM-DD> ...');
      console.log(JSON.stringify(await plan(key, rest, { catalog }), null, 2));
    } else if (cmd === 'build') {
      const [file, ...dates] = rest;
      if (!file || !dates.length || !dates.every(isDate)) fail('usage: build <bfd|r4r> <responses.json> <YYYY-MM-DD> ...');
      const responses = JSON.parse(readFileSync(file, 'utf8'));
      console.log(JSON.stringify(await build(key, responses, dates, { today: istToday(), catalog })));
    } else fail('usage: day-builder.mjs info|plan|build ...');
  } catch (e) { fail(e && e.message ? e.message : JSON.stringify(e)); }
}
