#!/usr/bin/env node
/*
 * demo-returns: sample returns, RTO and cancellations for the DEMO tracker, drawn from the demo store's
 * own sample sales (the skus-<date>.json files demo-data.mjs wrote). Never for the live tracker.
 *
 *   node demo-returns.mjs <demo-dir> [--today 2026-10-04]
 *
 * Writes into <demo-dir>:
 *   returns-<date>.json   store-wide tracker records: { date, rows: [sku, title, kind, reason, units, value, [orders], {hour: [units, value]}] }
 *   r4r_ret-lines-<month>.json, r4r_ret-info-<k>.json   All categories tracker records (lines, plus per-order notes it reads reasons from)
 *   returns.json           an ArtifactData batch list for all of them
 * Rates: about 3% of units cancelled, 2.5% RTO and 2% returned by customers, a little higher on sale days.
 */
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

const KINDS = [
  { kind: 'Cancelled', rate: 0.030, lag: [0, 1], reasons: [['Changed mind', 'customer_changed_mind'], ['Found a better price elsewhere', 'better_price_elsewhere'], ['Ordered by mistake', 'ordered_by_mistake'], ['Delivery date too late', 'delivery_too_late']] },
  { kind: 'RTO (not delivered)', rate: 0.025, lag: [3, 6], reasons: [['Customer declined delivery', 'RTO - customer declined delivery'], ['Customer not reachable', 'RTO - customer not reachable'], ['Address incomplete', 'RTO - address incomplete']] },
  { kind: 'Customer return', rate: 0.020, lag: [5, 9], reasons: [['Size too small', 'Customer returned the product: size too small'], ['Size too large', 'Customer returned the product: size too large'], ['Quality not as expected', 'Customer returned the product: quality not as expected'], ['Colour different from photo', 'Customer returned the product: colour different from photo']] },
];

let seed = 4242;
const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
const pick = a => a[Math.floor(rnd() * a.length)];
const addD = (s, n) => { const d = new Date(s + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
const r2 = x => Math.round(x * 100) / 100;

export function demoReturns(dir, today) {
  const files = readdirSync(dir).filter(f => /^skus-\d{4}-\d{2}-\d{2}\.json$/.test(f)).sort();
  const lastDay = addD(today, -1);
  const bfd = {}, lines = [], info = {};
  let n = 5000;
  for (const f of files) {
    const sold = JSON.parse(readFileSync(join(dir, f), 'utf8'));
    const saleDay = sold.date >= '2026-10-01' ? 1.25 : 1;
    for (const [sku, title, ch, , net, units] of sold.rows) {
      if (!units || ch === 'd') continue;
      const unitVal = net / units;
      for (const K of KINDS) {
        let q = 0; for (let i = 0; i < units; i++) if (rnd() < K.rate * saleDay) q++;
        if (!q) continue;
        const day = addD(sold.date, K.lag[0] + Math.floor(rnd() * (K.lag[1] - K.lag[0] + 1)));
        if (day > lastDay) continue;                          // not booked yet
        const [reason, note] = pick(K.reasons), order = `#DS${++n}`, val = r2(q * unitVal), hour = 9 + Math.floor(rnd() * 14);
        (bfd[day] || (bfd[day] = [])).push([sku, title, K.kind, reason, q, val, [order], { [hour]: [q, val] }]);
        lines.push([day, order, sku, ch, q, val]);
        info[order] = K.kind === 'Cancelled' ? { c: note, t: ['Cancelled'], f: [['Order cancelled', day, [sku]]] }
          : { c: '', t: [K.kind.startsWith('RTO') ? 'RTO-Delivered' : 'Return'], f: [[note, day, [sku]]] };
      }
    }
  }
  const now = Date.now(), out = [], write = (name, doc, collection, id) => { const p = join(dir, name); writeFileSync(p, JSON.stringify(doc)); out.push({ op: 'set', collection, doc_id: id, file_path: p }); };
  for (const [d, rows] of Object.entries(bfd).sort()) write(`returns-${d}.json`, { date: d, rows, fetchedAt: now, demo: true }, 'returns', d);
  const months = {}; for (const l of lines) (months[l[0].slice(0, 7)] || (months[l[0].slice(0, 7)] = [])).push(l);
  for (const [m, rows] of Object.entries(months)) write(`r4r_ret-lines-${m}.json`, { v: 1, month: m, fetchedAt: now, rows: rows.sort((a, b) => (a[0] < b[0] ? -1 : 1)), demo: true }, 'r4r_ret', 'lines-' + m);
  const byK = {}; for (const [o, v] of Object.entries(info)) (byK[o.slice(-1)] || (byK[o.slice(-1)] = {}))[o] = v;
  for (const [k, orders] of Object.entries(byK)) write(`r4r_ret-info-${k}.json`, { v: 1, orders, demo: true }, 'r4r_ret', 'info-' + k);
  writeFileSync(join(dir, 'returns.json'), JSON.stringify(out));
  const units = lines.reduce((s, l) => s + l[4], 0);
  return { docs: out.length, lines: lines.length, units, days: Object.keys(bfd).length };
}

if (process.argv[1] && process.argv[1].endsWith('demo-returns.mjs')) {
  const args = process.argv.slice(2), ti = args.indexOf('--today');
  const today = ti >= 0 ? args.splice(ti, 2)[1] : new Date(Date.now() + 19800000).toISOString().slice(0, 10);
  if (!args[0]) { console.error('usage: demo-returns.mjs <demo-dir> [--today YYYY-MM-DD]'); process.exit(1); }
  console.log(demoReturns(args[0], today));
}
