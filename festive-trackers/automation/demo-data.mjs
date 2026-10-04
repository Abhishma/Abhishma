#!/usr/bin/env node
/*
 * demo-data: illustrative sample records for the DEMO copy of the combined page only.
 * The catalogue (SKUs, titles, product handles) is the real one so every view maps cleanly;
 * all sales, traffic and funnel numbers are generated. Never write these to the live tracker.
 *
 *   node demo-data.mjs <out-dir> [from] [to] [--catalog catalog.json] [--prices prices.json] [--orders 210] [--aov 2350]
 *
 * With --catalog (the generic shape from the page's Categories panel) the sample sales follow that store's
 * categories, SKUs and product pages, with GMV spread by each category's share of SKUs.
 *
 * Writes <out-dir>/bfd.json and <out-dir>/r4r.json, each an ArtifactData batch list.
 * Days are written non-final, so a real refresh would always replace them.
 */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import vm from 'node:vm';
import { createRequire } from 'node:module';

const HERE = dirname(fileURLToPath(import.meta.url));
const lines = f => readFileSync(join(HERE, '..', 'trackers', f), 'utf8').replace(/\r\n/g, '\n').split('\n');
const constOf = (L, n) => vm.runInNewContext(L.find(x => x.startsWith(`const ${n} `)).replace(/^const /, 'var ') + '\n' + n);

const ARGS = process.argv.slice(2);
const opt = k => { const i = ARGS.indexOf(k); return i >= 0 ? ARGS.splice(i, 2)[1] : null; };
const PRICES_FILE = opt('--prices'), AOV = Number(opt('--aov')) || 0, ORDERS = Number(opt('--orders')) || 0;
const CI = ARGS.indexOf('--catalog');
const TK = createRequire(import.meta.url)('../tools/catalog.cjs');
const BUILTIN_EMPTY = /^const SCOPE = \{\};/m.test(readFileSync(join(HERE, '..', 'trackers', 'r4r-all-categories.html'), 'utf8'));
// Without --catalog: the built-in store map, or (in the public copy, which has none) the sample home store.
const CATALOG = CI >= 0 ? JSON.parse(readFileSync(ARGS.splice(CI, 2)[1], 'utf8'))
  : BUILTIN_EMPTY ? TK.fromCsv(readFileSync(join(HERE, '..', 'tools', 'sample-categories-home-store.csv'), 'utf8'), { name: 'Sample Home Store' }) : null;
if (CATALOG && TK.validate(CATALOG).length) { console.error('Catalogue is not usable: ' + TK.validate(CATALOG).join(' ')); process.exit(1); }
const OB = CATALOG && TK.apply('bfd', CATALOG), OR = CATALOG && TK.apply('r4r', CATALOG);

const BFD = lines('big-festive-days.html'), R4R = lines('r4r-all-categories.html');
const CATS = OB ? OB.CATS : constOf(BFD, 'CATS');
const HB = OB ? OB.HMAP : constOf(BFD, 'HMAP'), HR = OR ? OR.HMAP : constOf(R4R, 'HMAP');
const SCOPE = OR ? OR.SCOPE : constOf(R4R, 'SCOPE');

let seed = 20261001;
const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
const jitter = (x, pct) => x * (1 + (rnd() * 2 - 1) * pct);
const addD = (s, n) => { const d = new Date(s + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
const r2 = x => Math.round(x * 100) / 100;

const PRICE_DEFAULT = 2500;
const PRICE = CATALOG ? (PRICES_FILE ? JSON.parse(readFileSync(PRICES_FILE, 'utf8')) : {}) : { 'Baby Gear': 6200, 'Ride ons and Toys': 4800, Furniture: 9800, 'Feeding Nursing and Nursery': 1400, Clothing: 750, Diapering: 950, 'Baby and Kids Care': 420, 'Combos and Bundles': 3100, 'Gift Cards': 2000, Services: 500, Unmapped: 1500 };
// Share of GMV by category: a plausible mix for a baby and kids D2C store.
const MIX = CATALOG ? mixByCount() : { 'Baby Gear': 0.30, 'Ride ons and Toys': 0.24, 'Furniture': 0.12, 'Feeding Nursing and Nursery': 0.12, Clothing: 0.10, Diapering: 0.05, 'Combos and Bundles': 0.04, 'Baby and Kids Care': 0.03 };
const pick = Object.keys(MIX).flatMap(cat => Object.entries(SCOPE).filter(([s, v]) => v[4] === cat && s !== '(no SKU)')
  .sort(() => rnd() - 0.5).slice(0, 40)
  .map(([sku, v], i) => ({ sku, title: v[0].slice(0, 90), cat, w: 1 / Math.pow(i + 1, 0.9), price: jitter(PRICE[cat] || PRICE_DEFAULT, 0.35) })));
/* For any other store: GMV share follows each category's SKU count and menu position (no-stock categories left out). */
function mixByCount() {
  const n = {}; Object.values(SCOPE).forEach(v => { if (v[4] !== 'Unmapped' && !(CATALOG.noStockCats || []).includes(v[4])) n[v[4]] = (n[v[4]] || 0) + 1; });
  // Earlier categories in the catalogue (the template's menu order) sell more, as a store's lead lines do.
  const w = Object.fromEntries(Object.entries(n).map(([k, v]) => [k, v / Math.pow(CATALOG.cats.indexOf(k) + 1, 0.75)]));
  const tot = Object.values(w).reduce((a, b) => a + b, 0) || 1;
  return Object.fromEntries(Object.entries(w).map(([k, v]) => [k, v / tot]));
}
const handles = Object.keys(HB.p).filter(h => h in HR.p).sort(() => rnd() - 0.5).slice(0, 320).map((h, i) => ({ h, w: 1 / Math.pow(i + 1, 0.9) }));

function factor(d) {
  const dow = new Date(d + 'T00:00:00Z').getUTCDay();
  let f = dow === 0 || dow === 6 ? 1.12 : 1;
  if (d >= '2026-10-01') f *= 1.38;
  return jitter(f, 0.08);
}
function chan(orders, aov) {
  const net = orders * jitter(aov, 0.06), gross = net * jitter(1.17, 0.02);
  const cust = Math.round(orders * 0.97), newC = Math.round(cust * jitter(0.58, 0.08));
  return { orders, net: r2(net), aovSum: r2(net), units: Math.round(orders * jitter(1.45, 0.06)), gross: r2(gross), rev: r2(net * jitter(0.03, 0.3)), cust, newC, retC: cust - newC };
}
/* SKU lines per channel; the channel's GMV, units and reversals are then taken from its lines so they reconcile. */
function skuRows(shop) {
  const rows = [];
  for (const ch of ['w', 'a', 'o']) {
    const target = shop[ch].net; if (!target) continue;
    let net = 0, units = 0, rev = 0;
    for (const cat of Object.keys(MIX)) {
      const items = pick.filter(p => p.cat === cat), ws = items.map(p => p.w * jitter(1, 0.6)), tot = ws.reduce((x, y) => x + y, 0);
      items.forEach((p, i) => {
        const u = Math.round(target * MIX[cat] * jitter(1, 0.15) * ws[i] / tot / p.price); if (!u) return;
        const n = r2(u * p.price), rv = r2(n * jitter(0.025, 0.5));
        rows.push([p.sku, p.title, ch, Math.max(1, Math.round(u / 1.15)), n, u, r2(n * 1.17), rv]);
        net += n; units += u; rev += rv;
      });
    }
    Object.assign(shop[ch], { net: r2(net), aovSum: r2(net), units, gross: r2(net * 1.17), rev: r2(rev) });
  }
  return rows.sort((a, b) => b[4] - a[4]);
}
function landing(sessions, map, keyOf) {
  const lp = {}, ws = handles.map(x => x.w * jitter(1, 0.5)), tot = ws.reduce((a, b) => a + b, 0);
  handles.forEach((x, i) => {
    const s = Math.round(sessions * 0.46 * ws[i] / tot); if (!s) return;
    const k = keyOf(map.p[x.h]); const v = lp[k] || (lp[k] = [0, 0, 0]);
    v[0] += s; v[1] += Math.round(s * jitter(0.08, 0.3)); v[2] += Math.round(s * jitter(0.012, 0.35));
  });
  return lp;
}

export function generate(from = '2026-09-17', to = '2026-10-03', now = Date.now()) {
  const out = { bfd: [], r4r: [] };
  for (let d = from; d <= to; d = addD(d, 1)) {
    const f = factor(d);
    // --orders sets web orders on a normal day (app runs at two thirds of web); --aov the web order value.
    const wo = ORDERS || 210, aov = AOV || 2350;
    const shop = { w: chan(Math.round(wo * f), aov), a: chan(Math.round(wo * 0.67 * f), aov * 0.9), o: chan(Math.round(jitter(wo / 26, 0.4)), aov * 0.8), d: chan(Math.round(jitter(2, 0.5)), aov * 2.5) };
    const sessions = Math.round(shop.w.orders / jitter(0.011, 0.07));
    const sess = { sessions, visitors: Math.round(sessions * 0.84), atc: Math.round(sessions * jitter(0.075, 0.06)), checkout: Math.round(sessions * jitter(0.032, 0.06)), completed: Math.round(shop.w.orders * 0.98) };
    const open = Math.round(shop.a.orders / jitter(0.028, 0.07));
    const app = { open, atc: Math.round(open * jitter(0.14, 0.05)), checkout: Math.round(open * jitter(0.06, 0.05)), purchase: Math.round(shop.a.orders * 0.95) };
    const rows = skuRows(shop);
    const base = { date: d, shop, sess, app, hasSku: true, v: 4, final: false, fetchedAt: now, demo: true };
    const bfdDay = { ...base, lp: landing(sessions, HB, i => CATS[i]) };
    const r4rDay = { ...base, lpv: 3, lp: landing(sessions, HR, v => v) };
    const skus = { date: d, rows, fetchedAt: now, demo: true };
    out.bfd.push({ op: 'set', collection: 'skus', doc_id: d, data: skus }, { op: 'set', collection: 'days', doc_id: d, data: bfdDay });
    out.r4r.push({ op: 'set', collection: 'r4r_skus', doc_id: d, data: skus }, { op: 'set', collection: 'r4r_days', doc_id: d, data: r4rDay });
  }
  return out;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const [dir, from, to] = ARGS;
  if (!dir) { console.error('usage: demo-data.mjs <out-dir> [from] [to]'); process.exit(1); }
  mkdirSync(dir, { recursive: true });
  const out = generate(from, to);
  for (const [k, writes] of Object.entries(out)) {
    // ArtifactData batches take file_path per entry: one JSON file per document.
    const list = writes.map(w => {
      const p = join(dir, `${w.collection}-${w.doc_id}.json`);
      writeFileSync(p, JSON.stringify(w.data));
      return { op: w.op, collection: w.collection, doc_id: w.doc_id, file_path: p };
    });
    writeFileSync(join(dir, `${k}.json`), JSON.stringify(list, null, 1));
    console.log(k, list.length, 'writes');
  }
}
