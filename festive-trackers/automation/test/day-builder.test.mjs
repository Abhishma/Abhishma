import { test } from 'node:test';
import assert from 'node:assert/strict';
import { plan, build } from '../day-builder.mjs';

const D = '2026-10-02';
// The public copy of this project ships with the built-in store map stripped (tools/sanitize.py).
const HAS_BUILTIN = !/^const SKUMAP = \{\};/m.test((await import('node:fs')).readFileSync(new URL('../../trackers/big-festive-days.html', import.meta.url), 'utf8'));
const table = (cols, rows) => ({ columns: cols.map(name => ({ name })), rows });

/* Synthetic connector payloads keyed by what each planned call asks for. */
function respond(calls) {
  const out = {};
  for (const c of calls) {
    const q = c.input.query || '';
    const D = (q.match(/SINCE (\S+)/) || [])[1] || c.input.from;   // each call answers for the day it asks about
    if (c.tool === 'run_funnel') out[c.id] = JSON.stringify({ steps: [{ users: 900 }, { users: 120 }, { users: 60 }, { users: 25 }] });
    else if (q.startsWith('FROM sales SHOW orders, net_sales, average_order_value')) out[c.id] = table(
      ['day', 'sales_channel', 'orders', 'net_sales', 'average_order_value', 'quantity_ordered', 'gross_sales', 'sales_reversals', 'customers', 'new_customers', 'returning_customers'],
      [[D, 'Online Store', 10, 20000, 2000, 14, 22000, -500, 9, 6, 3],
       [D, 'Appmaker.xyz - Mobile app', 5, 9000, 1800, 6, 9500, 0, 5, 2, 3],
       [D, 'Draft Orders', 1, 4000, 4000, 2, 4000, 0, 1, 1, 0]]);
    else if (q.startsWith('FROM sessions SHOW sessions, online_store_visitors')) out[c.id] = { data: table(
      ['day', 'sessions', 'online_store_visitors', 'sessions_with_cart_additions', 'sessions_that_reached_checkout', 'sessions_that_completed_checkout'],
      [[D, 5000, 4200, 300, 120, 40]]) };
    else if (q.includes('GROUP BY product_variant_sku')) out[c.id] = table(
      ['product_variant_sku', 'product_title', 'sales_channel', 'orders', 'net_sales', 'quantity_ordered', 'gross_sales', 'sales_reversals'],
      [['TEST-SKU-1', 'Test product', 'Online Store', 2, 3999.456, 2, 4200, -100]]);
    else if (q.includes('GROUP BY landing_page_path')) out[c.id] = table(
      ['landing_page_path', 'sessions', 'sessions_with_cart_additions', 'sessions_that_completed_checkout'],
      [['/products/little-jack-baby-car-seat', 100, 10, 2], ['/products/no-such-handle', 7, 0, 0], ['/collections/no-such-collection', 3, 1, 0]]);
    else throw new Error('Unplanned query: ' + q);
  }
  return out;
}

for (const key of ['bfd', 'r4r']) {
  test(`${key}: plan then build produces page-shaped records`, async () => {
    const calls = await plan(key, [D]);
    assert.equal(calls.length, 5);
    const writes = await build(key, respond(calls), [D], { today: '2026-10-04', now: 1 });
    const ns = key === 'r4r' ? 'r4r_' : '';
    assert.deepEqual(writes.map(w => `${w.collection}/${w.doc_id}`), [`${ns}skus/${D}`, `${ns}days/${D}`]);

    const sku = writes[0].data;
    assert.deepEqual(sku.rows[0], ['TEST-SKU-1', 'Test product', 'w', 2, 3999.46, 2, 4200, 100]);

    const day = writes[1].data;
    assert.equal(day.v, 4);
    assert.equal(day.hasSku, true);
    assert.equal(day.shop.w.orders, 10);
    assert.equal(day.shop.a.net, 9000);
    assert.equal(day.shop.d.orders, 1);
    assert.equal(day.shop.w.rev, 500);
    assert.deepEqual(day.sess, { sessions: 5000, visitors: 4200, atc: 300, checkout: 120, completed: 40 });
    assert.deepEqual(day.app, { open: 900, atc: 120, checkout: 60, purchase: 25 });
    const lpTotal = Object.values(day.lp).reduce((s, x) => s + x[0], 0);
    assert.equal(lpTotal, 110);

    if (key === 'bfd') {
      assert.equal(day.final, true);
      assert.equal(day.shop.w.aovSum, 20000);          // AOV x orders
      if (HAS_BUILTIN) {   // the public copy ships without the built-in map
        assert.deepEqual(day.lp['Baby Gear'], [100, 10, 2]);
        assert.deepEqual(day.lp['Unmapped product pages'], [7, 0, 0]);
      }
    } else {
      assert.equal(day.final, false);
      assert.equal(day.lpv, 3);
      assert.equal(day.shop.w.aovSum, 20000);          // net sales
      assert.deepEqual(day.lp.X, HAS_BUILTIN ? [10, 1, 0] : [110, 11, 2]);
    }
  });
}

test('refuses to write today', async () => {
  const calls = await plan('bfd', ['2026-10-04']);
  await assert.rejects(build('bfd', respond(calls), ['2026-10-04'], { today: '2026-10-04' }), /live tier/);
});

test('reports missing responses', async () => {
  await assert.rejects(build('bfd', {}, [D], { today: '2026-10-04' }), /Missing responses/);
});

test('digest reads saved records', async () => {
  const { digest } = await import('../digest.mjs');
  const calls = await plan('bfd', [D, '2026-09-25']);
  const r = respond(calls);
  const writes = await build('bfd', r, [D, '2026-09-25'], { today: '2026-10-04', now: 1 });
  const records = { days: {}, skus: {} };
  writes.forEach(w => { records[w.collection][w.doc_id] = w.data; });
  const md = digest('bfd', records, D);
  assert.match(md, /Big Festive Days digest, 2026-10-02/);
  assert.match(md, /Sale day 2 of 39/);
  assert.match(md, /\| GMV \(net sales\) \| Rs 33,000 \| 0\.0% \|/);
  assert.match(md, /TEST-SKU-1/);
  assert.match(md, /Baseline: 1 saved day\(s\).*incomplete/);
  assert.match(digest('r4r', records, '2026-10-03'), /No saved record/);
});

test('a saved catalogue regroups landing pages by the store\'s own categories', async () => {
  const { createRequire } = await import('node:module');
  const C = createRequire(import.meta.url)('../../tools/catalog.cjs');
  const catalog = C.fromCsv([
    'sku,title,category,subcategory,product_handle,focus_groups,collection_handle',
    'RUG-1,Kashmir Rug,Rugs,Hand-knotted,little-jack-baby-car-seat,Bestsellers,',
    'LMP-1,Brass Lamp,Lighting,,no-such-handle,,',
  ].join('\n'), { excludePages: [] });
  for (const key of ['bfd', 'r4r']) {
    const calls = await plan(key, [D], { catalog });
    assert.ok(calls.some(c => (c.input.query || '').includes("NOT IN ('/__no-excluded-page__')")), 'no parenting pages in the query');
    const writes = await build(key, respond(calls), [D], { today: '2026-10-04', now: 1, catalog });
    const lp = writes[1].data.lp;
    if (key === 'bfd') { assert.deepEqual(lp.Rugs, [100, 10, 2]); assert.deepEqual(lp.Lighting, [7, 0, 0]); }
    else { assert.deepEqual(lp['Rugs|R'], [100, 10, 2]); assert.deepEqual(lp['Lighting|'], [7, 0, 0]); }
  }
});
