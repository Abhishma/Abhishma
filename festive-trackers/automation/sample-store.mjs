#!/usr/bin/env node
/*
 * sample-store: a made-up catalogue for any category template, for demos only.
 *
 *   node sample-store.mjs <template-id> <out-dir> [--name "Demo Streetwear Co."] [--per 8]
 *
 * Writes <out-dir>/catalog.csv (sku, title, product_handle, focus_groups: no category column, so the
 * template sorts it exactly as it would a real store's export) and <out-dir>/prices.json (a rough
 * selling price per category, for automation/demo-data.mjs --prices). Product names are invented
 * from the template's own keywords; they are not any brand's products.
 */
import { writeFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const P = require('../tools/presets.cjs');

const STYLE = ['Washed Black', 'Off White', 'Olive', 'Sand', 'Charcoal', 'Sky Blue', 'Maroon', 'Ecru', 'Forest Green', 'Rust', 'Navy', 'Lavender'];
const THEME = ['Midnight Wave', 'Concrete Bloom', 'Neon Static', 'Desert Run', 'Monsoon', 'Paper Planes', 'Night Shift', 'Tidal', 'Low Orbit', 'Sunday Club'];
/* Rough selling prices (INR) by keyword in the category name; anything else uses DEFAULT. */
const PRICE_BY_WORD = [
  ['oversized', 899], ['t shirt', 799], ['polo', 1199], ['hoodie', 1599], ['sweater', 1499], ['knit', 1899], ['jean', 1699], ['cargo', 1599],
  ['jogger', 1199], ['trouser', 1499], ['short', 799], ['co ord', 1999], ['jacket', 2499], ['blazer', 5999], ['overshirt', 1999], ['shirt', 1299],
  ['kurta set', 2499], ['kurta', 1299], ['saree', 2999], ['lehenga', 6999], ['dress', 1599], ['top', 899], ['footwear', 2299], ['sneaker', 2999],
  ['accessor', 499], ['jewellery', 799], ['earring', 699], ['gift', 1000], ['combo', 1799], ['mattress', 14999], ['rug', 9999], ['earbud', 1499],
  ['headphone', 1999], ['smartwatch', 2499], ['speaker', 2499], ['face', 449], ['hair', 399], ['lip', 499], ['perfume', 699], ['protein', 2299],
];
const DEFAULT = 1500;
const priceOf = cat => { const n = P.norm(cat); const hit = PRICE_BY_WORD.find(([w]) => n.includes(' ' + w)); return hit ? hit[1] : DEFAULT; };
const title = s => s.replace(/\b[a-z]/g, c => c.toUpperCase()).replace(/\bT Shirt/g, 'T-Shirt').replace(/\bCo Ord/g, 'Co-ord');
const slug = s => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

export function sampleStore(templateId, { per = 8, seed = 7 } = {}) {
  const t = P.template(templateId);
  if (!t) throw new Error(`Unknown template "${templateId}"`);
  let s = seed; const rnd = () => ((s = (s * 1103515245 + 12345) >>> 0) / 4294967296);
  const rows = [], prices = {}, focus = t.focus;
  let n = 0;
  for (const [cat, kws, subs] of t.cats) {
    if (t.noStock.includes(cat) && cat === 'Gift Cards') continue;
    prices[cat] = priceOf(cat);
    for (let i = 0; i < per; i++) {
      const noun = kws[i % kws.length];
      const sub = subs.length ? subs[i % subs.length][1][0] + ' ' : '';
      const name = title(`${i % 2 ? THEME[(n + i) % THEME.length] + ' ' : ''}${sub}${noun}`.trim()) + ` - ${STYLE[(n * 3 + i) % STYLE.length]}`;
      const handle = slug(name) + '-' + (n + 1);
      const fx = focus.filter((f, j) => (j === 0 && rnd() < 0.2) || (j === 1 && rnd() < 0.15) || (j === 2 && rnd() < 0.1)).join(';');
      for (const size of i % 3 === 0 ? ['S', 'M', 'L', 'XL'] : ['FS']) rows.push([`DS-${String(n + 1).padStart(4, '0')}-${size}`, name, handle, fx]);
      n++;
    }
  }
  const csv = ['sku,title,product_handle,focus_groups', ...rows.map(r => r.map(v => (/[",]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v)).join(','))].join('\n') + '\n';
  return { csv, prices, products: n, skus: rows.length };
}

if (process.argv[1] && process.argv[1].endsWith('sample-store.mjs')) {
  const args = process.argv.slice(2);
  const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args.splice(i, 2)[1] : d; };
  const per = Number(opt('--per', 8));
  const [id, dir] = args;
  if (!id || !dir) { console.error('usage: sample-store.mjs <template-id> <out-dir> [--per 8]'); process.exit(1); }
  const out = sampleStore(id, { per });
  mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, 'catalog.csv'), out.csv);
  writeFileSync(join(dir, 'prices.json'), JSON.stringify(out.prices, null, 1));
  console.log(`${out.products} products, ${out.skus} SKUs`);
}
