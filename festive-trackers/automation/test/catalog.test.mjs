import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const require = createRequire(import.meta.url);
const C = require('../../tools/catalog.cjs');

/* The All Categories tracker's built-in constants, read from its HTML. */
function builtInConsts() {
  const L = readFileSync(new URL('../../trackers/r4r-all-categories.html', import.meta.url), 'utf8').replace(/\r\n/g, '\n').split('\n');
  const get = n => vm.runInNewContext(L.find(x => x.startsWith(`const ${n} = `)).replace(/^const /, 'var ') + '\n' + n);
  return { SCOPE: get('SCOPE'), CATS: get('CATS'), HMAP: get('HMAP'), FOCUS: get('FOCUS'), TOOL_PAGES: get('TOOL_PAGES') };
}
/* The tracker's generic focusOf, as patched by tools/combine.py. */
const focusOf = (o, sku) => { const x = o.SCOPE[sku]; if (!x) return []; const code = {}; o.FOCUS.forEach((g, i) => { code[g] = 'RTD'[i]; });
  return o.FOCUS.filter(g => String(x[1] || '').includes(code[g]) || (code[g] === 'D' && x[2])); };

test('built-in R for Rabbit map survives the round trip through the generic catalogue', { skip: Object.keys(builtInConsts().SCOPE).length ? false : 'built-in map not included in this copy' }, () => {
  const orig = builtInConsts();
  const cat = C.fromBuiltIn(orig);
  assert.deepEqual(C.validate(cat), []);
  const o = C.apply('r4r', cat);
  assert.deepEqual(o.FOCUS, orig.FOCUS);
  assert.deepEqual(new Set(o.CATS), new Set(orig.CATS));
  for (const sku of Object.keys(orig.SCOPE)) {
    assert.equal(o.SCOPE[sku][4], orig.SCOPE[sku][4], `category of ${sku}`);
    assert.equal(o.SCOPE[sku][3], orig.SCOPE[sku][3], `sub-category of ${sku}`);
    assert.deepEqual(focusOf(o, sku), focusOf(orig, sku), `focus groups of ${sku}`);
  }
  const norm = v => { const [c, k = ''] = String(v).split('|'); return c + '|' + [...k].sort().join(''); };
  for (const h of Object.keys(orig.HMAP.p)) assert.equal(norm(o.HMAP.p[h]), norm(orig.HMAP.p[h]), `page ${h}`);
  assert.deepEqual(o.TOOL_PAGES, orig.TOOL_PAGES);
});

const RUGS_CSV = [
  'sku,title,category,subcategory,product_handle,focus_groups,collection_handle',
  'RUG-001,"Hand-knotted Rug, 5x8",Rugs,Hand-knotted,kashmir-rug,Bestsellers;New launch,',
  'RUG-002,Flatweave Rug,Rugs,Flatweave,dhurrie-rug,,',
  'LMP-010,Brass Lamp,Lighting,Table lamps,brass-lamp,Bestsellers,',
  'GFT-1,Gift card,Gift Cards,,gift-card,,',
  ',,Rugs,,,,rugs-collection',
  ',,,,,,sale-collection',
].join('\n');

test('a CSV for a home-decor store maps to both trackers', () => {
  const cat = C.fromCsv(RUGS_CSV, { name: 'Jaipur Rugs', noStockCats: ['Gift Cards'] });
  assert.deepEqual(C.validate(cat), []);
  assert.deepEqual(cat.cats, ['Rugs', 'Lighting', 'Gift Cards']);
  assert.deepEqual(cat.segments, ['Bestsellers', 'New launch']);
  assert.deepEqual(cat.skus['RUG-001'], ['Hand-knotted Rug, 5x8', 'Rugs', 'Hand-knotted', '01']);

  const b = C.apply('bfd', cat);
  assert.deepEqual(b.CATS, ['Rugs', 'Lighting', 'Gift Cards', 'Unmapped']);
  assert.equal(b.CATS[b.SKUMAP['LMP-010']], 'Lighting');
  assert.equal(b.CATS[b.HMAP.p['kashmir-rug']], 'Rugs');
  assert.equal(b.HMAP.c['rugs-collection'], 0);
  assert.equal(b.HMAP.c['sale-collection'], -1);
  assert.deepEqual(b.TOOL_PAGES, ['/__no-excluded-page__']);

  const r = C.apply('r4r', cat);
  assert.deepEqual(r.FOCUS, ['Bestsellers', 'New launch']);
  assert.deepEqual(r.SCOPE['RUG-001'], ['Hand-knotted Rug, 5x8', 'RT', 0, 'Hand-knotted', 'Rugs']);
  assert.deepEqual(focusOf(r, 'RUG-001'), ['Bestsellers', 'New launch']);
  assert.deepEqual(focusOf(r, 'LMP-010'), ['Bestsellers']);
  assert.equal(r.HMAP.p['brass-lamp'], 'Lighting|R');
  assert.equal(r.HMAP.c['rugs-collection'], 'Rugs|');
  assert.equal(r.NO_STOCK_RE, null);
  assert.deepEqual(r.NO_STOCK_CATS, ['Gift Cards']);
});

test('CSV round trip and guard rails', () => {
  const cat = C.fromCsv(RUGS_CSV, {});
  const again = C.fromCsv(C.toCsv(cat), {});
  assert.deepEqual(again.skus, cat.skus);
  assert.deepEqual(again.collections, cat.collections);
  assert.throws(() => C.fromCsv('sku,title\nA,B'), /category/);
  assert.throws(() => C.fromCsv('sku,category,focus_groups\nA,X,a;b;c;d'), /at most 3/);
  assert.match(C.validate({ cats: ['A'], skus: { S: ['t', 'B', '', ''] } }).join(' '), /not in the category list/);
  assert.match(C.validate({ cats: ['A'], skus: { S: ['t', 'A', '', ''] }, noStockSkuPattern: '(' }).join(' '), /regular expression/);
});

test('Shopify products group by product type or by tag prefix', () => {
  const products = [
    { handle: 'kashmir-rug', title: 'Kashmir Rug', productType: 'Rugs', tags: ['Category: Floor', 'Bestsellers'], variants: { nodes: [{ sku: 'R1' }, { sku: 'R2' }] } },
    { handle: 'brass-lamp', title: 'Brass Lamp', productType: 'Lighting', tags: ['Category: Decor'], variants: { nodes: [{ sku: 'L1' }] } },
    { handle: 'mystery', title: 'Mystery', productType: '', tags: [], variants: { nodes: [{ sku: 'M1' }, { sku: '' }] } },
  ];
  const collections = [{ handle: 'all-rugs', title: 'rugs' }, { handle: 'diwali', title: 'Diwali Edit' }];
  const byType = C.fromShopify(products, collections, { focusTags: ['bestsellers'] });
  assert.deepEqual(byType.cats, ['Lighting', 'Rugs']);
  assert.deepEqual(byType.skus.R2, ['Kashmir Rug', 'Rugs', '', '0']);
  assert.equal(byType.skus.M1[1], 'Unmapped');
  assert.ok(!('' in byType.skus));
  assert.deepEqual(byType.collections, { 'all-rugs': 'Rugs', diwali: '' });
  assert.deepEqual(byType.handles['kashmir-rug'], ['Rugs', '0']);

  const byTag = C.fromShopify(products, [], { groupBy: 'tag_prefix', tagPrefix: 'Category:' });
  assert.deepEqual(byTag.cats.sort(), ['Decor', 'Floor']);
  assert.deepEqual(byTag.skus.R1.slice(1, 3), ['Floor', 'Rugs']);   // product type becomes the sub-category
  assert.equal(byTag.source, 'shopify:tag_prefix:Category:');
});

test('large catalogues split across documents and join back', () => {
  const skus = {}; for (let i = 0; i < 4000; i++) skus['S' + i] = ['t', 'A', '', ''];
  const cat = { cats: ['A'], segments: [], skus, handles: { h1: ['A', ''] }, collections: {} };
  const { meta, parts } = C.toDocs(cat);
  assert.equal(meta.parts, 3);
  assert.equal(meta.skuCount, 4000);
  assert.ok(parts.every(p => JSON.stringify(p).length < 900000));
  const back = C.fromDocs(meta, parts);
  assert.equal(Object.keys(back.skus).length, 4000);
  assert.deepEqual(back.handles, { h1: ['A', ''] });
});
