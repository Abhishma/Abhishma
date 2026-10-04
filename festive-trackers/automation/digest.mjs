#!/usr/bin/env node
/*
 * digest: turns a tracker's saved `days` and `skus` records into the morning summary (Markdown).
 *
 *   node digest.mjs <bfd|r4r> records.json [YYYY-MM-DD]
 *
 * records.json = { "days": { "<date>": <days doc>, ... }, "skus": { "<date>": <skus doc>, ... } }
 * (what ArtifactData returns for the two collections, keyed by doc id). The date defaults to
 * yesterday in IST. Totals follow the page: GMV is net sales, Total includes Draft Orders.
 * The D0 projection, stock and sales-loss views stay on the page; they need live pulls.
 */
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { loadTracker, istToday } from './day-builder.mjs';

const CH = { w: 'Web', a: 'App', o: 'Other', d: 'Draft' };
const inr = n => 'Rs ' + Math.round(n).toLocaleString('en-IN');
const pct = (a, b) => (b ? ((a / b - 1) * 100).toFixed(1) + '%' : 'n/a');
const rate = (a, b) => (b ? ((a / b) * 100).toFixed(2) + '%' : 'n/a');

function totals(day) {
  const t = { orders: 0, net: 0, units: 0 };
  for (const k of Object.keys(CH)) {
    const x = day.shop[k]; if (!x) continue;
    t.orders += x.orders; t.net += x.net; t.units += x.units;
  }
  return t;
}
const mean = list => {
  const s = { orders: 0, net: 0, units: 0 };
  list.forEach(t => { s.orders += t.orders; s.net += t.net; s.units += t.units; });
  const n = list.length || 1;
  return { orders: s.orders / n, net: s.net / n, units: s.units / n, n: list.length };
};

export function digest(key, records, date) {
  const T = loadTracker(key, async () => { throw new Error('digest makes no connector calls'); });
  const { days, skus } = records;
  const day = days[date];
  const name = key === 'bfd' ? 'Big Festive Days' : 'All Categories';
  if (!day || !day.shop) return `# ${name} digest, ${date}\n\nNo saved record for ${date}. Open the tracker or let the refresh routine run, then retry.\n`;

  const t = totals(day);
  const baseDates = Object.keys(days).filter(d => d >= T.BASE.start && d <= T.BASE.end && days[d].shop);
  const base = mean(baseDates.map(d => totals(days[d])));
  const wk = days[T.addD(date, -7)];
  const wkT = wk && wk.shop ? totals(wk) : null;
  const inSale = date >= T.SALE.start && date <= T.SALE.end;

  const L = [];
  L.push(`# ${name} digest, ${date}`, '');
  L.push(inSale ? `Sale day ${Math.round((Date.parse(date) - Date.parse(T.SALE.start)) / 864e5) + 1} of ${Math.round((Date.parse(T.SALE.end) - Date.parse(T.SALE.start)) / 864e5) + 1}.` : 'Outside the sale window.', '');
  L.push('## Headline', '');
  L.push('| Metric | Day | vs baseline avg | vs same day last week |', '|---|---|---|---|');
  L.push(`| GMV (net sales) | ${inr(t.net)} | ${pct(t.net, base.net)} | ${wkT ? pct(t.net, wkT.net) : 'n/a'} |`);
  L.push(`| Orders | ${t.orders} | ${pct(t.orders, base.orders)} | ${wkT ? pct(t.orders, wkT.orders) : 'n/a'} |`);
  L.push(`| Units | ${t.units} | ${pct(t.units, base.units)} | ${wkT ? pct(t.units, wkT.units) : 'n/a'} |`);
  L.push('', `Baseline: ${base.n} saved day(s) in ${T.BASE.start} to ${T.BASE.end}${base.n < 14 ? ' (incomplete, read the comparison with care)' : ''}.`, '');

  L.push('## By channel', '', '| Channel | Orders | GMV | AOV |', '|---|---|---|---|');
  for (const [k, label] of Object.entries(CH)) {
    const x = day.shop[k]; if (!x || !x.orders) continue;
    L.push(`| ${label} | ${x.orders} | ${inr(x.net)} | ${inr(x.net / x.orders)} |`);
  }
  L.push('');

  L.push('## Funnels', '');
  if (day.sess) L.push(`- Web: ${day.sess.sessions.toLocaleString('en-IN')} sessions, add to cart ${rate(day.sess.atc, day.sess.sessions)}, checkout ${rate(day.sess.checkout, day.sess.sessions)}, conversion ${rate(day.sess.completed, day.sess.sessions)}`);
  if (day.app) L.push(`- App: ${day.app.open.toLocaleString('en-IN')} opens, add to cart ${rate(day.app.atc, day.app.open)}, checkout ${rate(day.app.checkout, day.app.open)}, purchase ${rate(day.app.purchase, day.app.open)}`);
  L.push('');

  const rows = skus[date] && skus[date].rows;
  if (rows && rows.length) {
    const agg = {};
    for (const [sku, title, , orders, net, units] of rows) {
      const k = sku || title; const x = agg[k] || (agg[k] = { sku, title, orders: 0, net: 0, units: 0 });
      x.orders += orders; x.net += net; x.units += units;
    }
    const top = Object.values(agg).sort((a, b) => b.net - a.net).slice(0, 10);
    L.push('## Top 10 SKUs by GMV', '', '| SKU | Product | Units | GMV |', '|---|---|---|---|');
    top.forEach(x => L.push(`| ${x.sku || '(no SKU)'} | ${x.title.replace(/\|/g, '/')} | ${x.units} | ${inr(x.net)} |`));
    L.push('');
  }

  if (day.lp && Object.keys(day.lp).length) {
    const lp = Object.entries(day.lp).sort((a, b) => b[1][0] - a[1][0]).slice(0, 8);
    L.push('## Landing traffic (web)', '', '| Landing group | Sessions | Add to cart | Conversion |', '|---|---|---|---|');
    lp.forEach(([k, [s, atc, done]]) => L.push(`| ${k} | ${s} | ${rate(atc, s)} | ${rate(done, s)} |`));
    L.push('');
  }

  const flags = [];
  if (base.n && t.net < base.net) flags.push(`GMV is below the pre-sale baseline average (${pct(t.net, base.net)}).`);
  if (day.sess && base.n) {
    const bc = baseDates.map(d => days[d].sess).filter(Boolean);
    const bConv = bc.reduce((s, x) => s + x.completed, 0) / (bc.reduce((s, x) => s + x.sessions, 0) || 1);
    const conv = day.sess.completed / (day.sess.sessions || 1);
    if (bConv && conv < bConv * 0.85) flags.push(`Web conversion ${rate(day.sess.completed, day.sess.sessions)} is more than 15% under baseline ${(bConv * 100).toFixed(2)}%.`);
  }
  if (day.final === false) flags.push('This day is not final yet; Shopify adds late sessions for 2 to 3 days.');
  L.push('## Flags', '', ...(flags.length ? flags.map(f => '- ' + f) : ['- None.']), '');
  L.push('Projection, stock and sales loss: see the tracker page.');
  return L.join('\n') + '\n';
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const [key, file, date] = process.argv.slice(2);
  if (!key || !file) { console.error('usage: digest.mjs <bfd|r4r> records.json [YYYY-MM-DD]'); process.exit(1); }
  const d = date || new Date(Date.parse(istToday()) - 864e5).toISOString().slice(0, 10);
  process.stdout.write(digest(key, JSON.parse(readFileSync(file, 'utf8')), d));
}
