#!/usr/bin/env node
/*
 * returns-builder: the store-wide tracker's `returns/<date>` records, built from Shopify on a schedule.
 *
 * The store-wide tracker only reads these records; it never fetches returns itself. This builds them in three passes
 * around the Shopify connector (whose tools only Claude can call), the same way day-builder.mjs does:
 *
 *   node returns-builder.mjs plan-lines  <date> [<date> ...]                  > calls.json
 *       One ShopifyQL call per day: returned quantity and value by order, SKU and hour (IST).
 *   node returns-builder.mjs plan-orders responses.json <date> [<date> ...]   > calls.json
 *       Order lookups (50 orders a call) for refund notes, cancellation reasons and tags, for the orders found.
 *   node returns-builder.mjs build       responses.json <date> [<date> ...]   > writes.json
 *       ArtifactData batch: set returns/<date> = { date, rows, hrs, fetchedAt } for each date.
 *
 * Responses from both plan passes go in one responses.json ({ "<call id>": payload }).
 * Reasons use the All categories tracker's own retReason(), lifted from its HTML, so both tabs read returns alike.
 * Row shape the tracker reads: [sku, title, kind, reason, units, value ex-GST, [order names], { hour: [units, value] }].
 */
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import vm from 'node:vm';
import { callId } from './day-builder.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const SHOP = 'Shopify';
export const KINDS = ['Customer return', 'RTO (not delivered)', 'Cancelled', 'Other refund'];
/* the All categories tracker's reason groups, mapped onto the store-wide tracker's four types */
const KIND_OF = { return: 'Customer return', rto: 'RTO (not delivered)', cancel: 'Cancelled', mind: 'Cancelled', courier: 'Cancelled', stock: 'Cancelled', lost: 'Other refund', other: 'Other refund' };
const BATCH = 50;

function lift() {
  const html = readFileSync(join(HERE, '..', 'trackers', 'r4r-all-categories.html'), 'utf8').replace(/\r\n/g, '\n');
  const L = html.split('<script>\n')[1].split('\n');
  const line = n => { const l = L.find(x => x.startsWith(`const ${n} = `)); if (!l) throw new Error(`Tracker has no const ${n}`); return l; };
  const fn = n => { const i = L.findIndex(x => x.startsWith(`function ${n}(`)); if (i < 0) throw new Error(`Tracker has no function ${n}`); return L.slice(i, L.findIndex((x, k) => k > i && x === '}') + 1).join('\n'); };
  const S = { retInfo: {} };
  const api = vm.runInNewContext([line('OQ'), line('baseSku'), line('pretty'), fn('retReason'), '({ OQ, retReason })'].join('\n'), { S });
  return { ...api, S };
}

const day = d => { if (!/^\d{4}-\d{2}-\d{2}$/.test(d)) throw new Error(`Dates must be YYYY-MM-DD, got "${d}"`); return d; };
// Clause order follows the trackers' own queries (GROUP BY ... HAVING ... SINCE). VERIFY on the first live run that
// ShopifyQL accepts TIMESERIES hour together with HAVING; if not, drop HAVING and filter zero rows here (already done below).
const linesQuery = d => `FROM sales SHOW quantity_returned, returns WHERE sales_channel != 'Draft Orders' GROUP BY order_name, product_variant_sku, product_title TIMESERIES hour HAVING quantity_returned != 0 SINCE ${d} UNTIL ${d} LIMIT 20000`;
const num = v => { const n = parseFloat(v); return Number.isFinite(n) ? n : 0; };
function rowsOf(payload) {
  let p = payload;
  if (typeof p === 'string') { try { p = JSON.parse(p); } catch { return []; } }
  if (p && !p.rows && p.data) p = p.data;
  if (!p || !Array.isArray(p.rows) || !Array.isArray(p.columns)) throw new Error('Unexpected ShopifyQL response shape.');
  const cols = p.columns.map(c => c.name);
  return p.rows.map(r => Object.fromEntries(cols.map((c, i) => [c, r[i]])));
}
const istHour = ts => new Date(Date.parse(ts) + 19800000).getUTCHours();

export function planLines(dates) {
  return dates.map(day).map(d => { const input = { query: linesQuery(d) }; return { id: callId(SHOP, 'run-analytics-query', input), server: SHOP, tool: 'run-analytics-query', input }; });
}

function linesFor(responses, dates) {
  const out = {};
  for (const call of planLines(dates)) {
    if (!(call.id in responses)) throw new Error(`Missing response for returned lines call ${call.id}`);
    const d = call.input.query.match(/SINCE (\S+)/)[1];
    out[d] = rowsOf(responses[call.id])
      .filter(r => num(r.quantity_returned) !== 0)
      .map(r => ({ order: r.order_name, sku: r.product_variant_sku || '', title: String(r.product_title || '').slice(0, 90), hour: istHour(r.hour), q: -num(r.quantity_returned), v: Math.round(-num(r.returns) * 100) / 100 }));
  }
  return out;
}

export function planOrders(responses, dates) {
  const { OQ } = lift();
  const orders = [...new Set(Object.values(linesFor(responses, dates)).flat().map(l => l.order).filter(Boolean))].sort();
  const calls = [];
  for (let i = 0; i < orders.length; i += BATCH) {
    const input = { query: OQ, variables: { q: orders.slice(i, i + BATCH).map(o => 'name:' + o.replace('#', '')).join(' OR ') } };
    calls.push({ id: callId(SHOP, 'graphql_query', input), server: SHOP, tool: 'graphql_query', input });
  }
  return calls;
}

export function build(responses, dates, { now = Date.now() } = {}) {
  const { retReason, S } = lift();
  // order notes, cancellation reason and tags, in the shape the tracker keeps them (S.retInfo)
  for (const call of planOrders(responses, dates)) {
    if (!(call.id in responses)) throw new Error(`Missing response for order lookup call ${call.id}`);
    let p = responses[call.id]; if (typeof p === 'string') p = JSON.parse(p);
    const nodes = p && (p.data || p).orders && (p.data || p).orders.nodes;
    if (!Array.isArray(nodes)) throw new Error('Unexpected order lookup response shape.');
    for (const n of nodes) {
      const ctag = ((n.tags || []).find(t => /^cancel-/i.test(t)) || '').slice(7);
      S.retInfo[n.name] = {
        c: ctag || (n.cancelReason ? String(n.cancelReason).toLowerCase() : ''),
        t: (n.tags || []).filter(x => /^(Cancelled|Return|customer_requested_cancellation)$/.test(x) || /^(RTO-|R_)/.test(x)).slice(0, 4),
        f: (n.refunds || []).map(f => [(f.note || '').slice(0, 140), String(f.createdAt || '').slice(0, 10), ((f.refundLineItems && f.refundLineItems.nodes) || []).map(x => (x.lineItem && x.lineItem.sku) || '')]),
      };
    }
  }
  const writes = [];
  for (const [d, lines] of Object.entries(linesFor(responses, dates))) {
    const byKey = new Map();
    const hrs = Object.fromEntries(['All', ...KINDS].map(k => [k, Array.from({ length: 24 }, () => [0, 0, 0])]));
    const ordersAt = Object.fromEntries(['All', ...KINDS].map(k => [k, Array.from({ length: 24 }, () => new Set())]));
    for (const l of lines) {
      const [group, detail] = retReason(l.order, l.sku);
      const kind = KIND_OF[group] || 'Other refund';
      const key = [l.sku, kind, detail].join('|');
      const r = byKey.get(key) || [l.sku, l.title, kind, detail, 0, 0, [], {}];
      r[4] += l.q; r[5] = Math.round((r[5] + l.v) * 100) / 100;
      if (!r[6].includes(l.order)) r[6].push(l.order);
      const h = r[7][l.hour] || (r[7][l.hour] = [0, 0]); h[0] += l.q; h[1] = Math.round((h[1] + l.v) * 100) / 100;
      byKey.set(key, r);
      for (const k of ['All', kind]) { hrs[k][l.hour][0] += l.q; hrs[k][l.hour][1] += l.v; ordersAt[k][l.hour].add(l.order); }
    }
    for (const k of Object.keys(hrs)) hrs[k].forEach((s, h) => { s[1] = Math.round(s[1]); s[2] = ordersAt[k][h].size; });
    writes.push({ op: 'set', collection: 'returns', doc_id: d, data: { date: d, rows: [...byKey.values()].sort((a, b) => b[4] - a[4]), hrs, fetchedAt: now } });
  }
  return writes;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const [cmd, ...rest] = process.argv.slice(2);
  const fail = m => { console.error(m); process.exit(1); };
  try {
    if (cmd === 'plan-lines') console.log(JSON.stringify(planLines(rest), null, 2));
    else if (cmd === 'plan-orders' || cmd === 'build') {
      const [file, ...dates] = rest;
      if (!file || !dates.length) fail(`usage: ${cmd} responses.json <YYYY-MM-DD> ...`);
      const responses = JSON.parse(readFileSync(file, 'utf8'));
      console.log(JSON.stringify(cmd === 'build' ? build(responses, dates) : planOrders(responses, dates), null, cmd === 'build' ? 0 : 2));
    } else fail('usage: returns-builder.mjs plan-lines|plan-orders|build ...');
  } catch (e) { fail(e && e.message ? e.message : String(e)); }
}
