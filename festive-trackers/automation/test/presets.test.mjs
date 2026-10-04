import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const P = require('../../tools/presets.cjs');
const C = require('../../tools/catalog.cjs');

test('every template and brand starter is well formed', () => {
  const ids = new Set();
  for (const t of P.TEMPLATES) {
    assert.ok(!ids.has(t.id), `duplicate template ${t.id}`); ids.add(t.id);
    const names = t.cats.map(c => c[0]);
    assert.equal(new Set(names).size, names.length, `${t.id}: duplicate category`);
    assert.ok(t.focus.length <= C.MAX_SEGMENTS, `${t.id}: too many focus groups`);
    t.noStock.forEach(n => assert.ok(names.includes(n), `${t.id}: no-stock category ${n} is not a category`));
    for (const [cat, kws, subs] of t.cats) {
      assert.ok(kws.length, `${t.id}/${cat}: no keywords`);
      [...kws, ...subs.flatMap(s => s[1])].forEach(k => assert.ok(P.norm(k).trim(), `${t.id}/${cat}: empty keyword`));
    }
  }
  const brands = P.choices().brands;
  assert.equal(new Set(brands.map(b => b.id)).size, brands.length, 'duplicate brand');
  for (const b of brands) assert.ok(P.template(b.id), `${b.name} points at a missing template`);
  assert.ok(P.TEMPLATES.length >= 25 && brands.length >= 110);
});

const CASES = {
  'brand:bonkers-corner': [
    ['Oversized T-Shirt: Naruto Sage Mode', 'Oversized T-shirts'], ['Men Solid Polo T-shirt', 'T-shirts'], ['Black Hooded Sweatshirt', 'Hoodies and Sweatshirts'],
    ['Relaxed Fit Baggy Jeans', 'Jeans'], ['Printed Resort Shirt', 'Shirts'], ['Parachute Cargo Pants', 'Cargo Pants'], ['Co-ord Set: Beige', 'Co-ord Sets'],
    ['Puffer Jacket', 'Jackets'], ['Women Crop Top', 'Women Tops'], ['Chunky Sneakers', 'Footwear'], ['E-Gift Card', 'Gift Cards'],
  ],
  'brand:the-bear-house': [
    ['Linen Shirt - Sage', 'Shirts'], ['Knit Polo - Navy', 'Polos'], ['Pleated Trousers', 'Trousers'], ['Nehru Jacket', 'Blazers and Suits'],
    ['Merino Crew Sweater', 'Knitwear'], ['Suede Loafers', 'Footwear'], ['Overshirt Olive', 'Overshirts'],
  ],
  'brand:libas': [['Anarkali Kurta Set with Dupatta', 'Kurta Sets'], ['Cotton Straight Kurti', 'Kurtas and Kurtis'], ['Banarasi Silk Saree', 'Sarees'], ['Floral Maxi Dress', 'Dresses']],
  'brand:mamaearth': [['Vitamin C Face Wash', 'Face Care'], ['Onion Hair Oil', 'Hair Care'], ['Ubtan Body Lotion', 'Body Care'], ['Matte Lipstick', 'Lips']],
  'brand:boat': [['Airdopes 141 TWS Earbuds', 'True Wireless Earbuds'], ['Rockerz 450 Headphones', 'Headphones'], ['Stone 350 Speaker', 'Speakers']],
  'brand:jaipur-rugs': [['Hand-Knotted Wool Rug 5x8', 'Rugs'], ['Velvet Cushion Cover', 'Cushions'], ['Brass Table Lamp', 'Lighting']],
  'brand:wakefit': [['Orthopaedic Memory Foam Mattress', 'Mattresses'], ['Sheesham Wood Bed', 'Beds'], ['Microfiber Pillow', 'Pillows']],
  'brand:mokobara': [['The Transit Backpack', 'Backpacks'], ['Cabin Trolley', 'Cabin Luggage']],
  'brand:manyavar': [['Ivory Silk Sherwani', 'Sherwanis'], ['Kurta Pyjama Set', 'Kurta Sets'], ['Printed Nehru Jacket', 'Nehru Jackets'], ['Embroidered Mojari', 'Footwear']],
  'brand:beardo': [['Beard Growth Oil', 'Beard Care'], ['Matte Hair Wax', 'Hair Styling'], ['Charcoal Face Wash', 'Face Care']],
  'brand:boldfit': [['PVC Dumbbell Set', 'Home Gym Equipment'], ['TPE Yoga Mat 6mm', 'Yoga and Pilates'], ['Resistance Loop Bands', 'Resistance and Recovery'], ['Gym Shaker Bottle', 'Gym Accessories']],
  'brand:fastrack': [['Reflex Smartwatch', 'Smartwatches'], ['Analog Watch for Men', 'Men Watches'], ['Leather Strap', 'Straps']],
  'brand:ferns-n-petals': [['Red Roses Bouquet', 'Flowers'], ['Chocolate Truffle Cake', 'Cakes'], ['Personalised Photo Mug', 'Personalised Gifts'], ['Diwali Dry Fruit Hamper', 'Hampers']],
  'brand:ugaoo': [['Snake Plant with Pot', 'Indoor Plants'], ['Potting Mix 5kg', 'Soil and Fertilisers'], ['Ceramic Planter', 'Pots and Planters']],
  'brand:smartivity': [['Robotic Arm STEM Kit', 'STEM and Science Kits'], ['Wooden Jigsaw Puzzle', 'Puzzles'], ['Strategy Board Game', 'Board Games']],
  'brand:giva': [['Silver Hoop Earrings', 'Earrings'], ['Rose Gold Pendant with Chain', 'Necklaces and Pendants']],
};
test('sample titles sort into the expected categories', () => {
  for (const [id, rows] of Object.entries(CASES)) {
    const t = P.template(id);
    for (const [title, want] of rows) assert.equal(P.classify(t, '', title, [])[0], want, `${id}: "${title}"`);
  }
  assert.deepEqual(P.classify(P.template('streetwear'), '', 'Something unrelated', []), ['Unmapped', '']);
  // product type wins over the title
  assert.equal(P.classify(P.template('streetwear'), 'Hoodie', 'Graphic Tee Print', [])[0], 'Hoodies and Sweatshirts');
});

test('a CSV with only sku and title sorts by template', () => {
  const csv = 'sku,title\nBC-1,Oversized T-Shirt: Naruto\nBC-2,Baggy Jeans Light Wash\nBC-3,Hooded Sweatshirt\nBC-4,Mystery item';
  const c = C.fromCsv(csv, { template: P.slug('Bonkers Corner'), name: 'Bonkers Corner' });
  assert.deepEqual(C.validate(c), []);
  assert.deepEqual(c.cats, ['Oversized T-shirts', 'Hoodies and Sweatshirts', 'Jeans']);   // template order
  assert.equal(c.skus['BC-2'][1], 'Jeans');
  assert.equal(c.skus['BC-2'][2], 'Baggy and Wide');
  assert.equal(c.skus['BC-4'][1], 'Unmapped');
  assert.equal(c.source, 'csv:template:brand:bonkers-corner');
  assert.throws(() => C.fromCsv('sku\nA', { template: 'streetwear' }), /title/);
  assert.throws(() => C.fromCsv('sku,title\nA,B', { template: 'nope' }), /Unknown category template/);
});

test('Shopify products sort by template', () => {
  const products = [
    { handle: 'naruto-tee', title: 'Naruto Oversized Tee', productType: '', tags: ['Bestsellers'], variants: { nodes: [{ sku: 'N-S' }, { sku: 'N-M' }] } },
    { handle: 'linen-shirt', title: 'Linen Shirt', productType: 'Shirts', tags: [], variants: { nodes: [{ sku: 'L-1' }] } },
  ];
  const c = C.fromShopify(products, [{ handle: 'shirts', title: 'Shirts' }], { groupBy: 'template', template: 'streetwear', focusTags: ['Bestsellers'] });
  assert.deepEqual(c.cats, ['Oversized T-shirts', 'Shirts']);
  assert.deepEqual(c.skus['N-M'], ['Naruto Oversized Tee', 'Oversized T-shirts', '', '0']);
  assert.deepEqual(c.skus['L-1'].slice(1, 3), ['Shirts', 'Solid']);
  assert.equal(c.collections.shirts, 'Shirts');
  assert.throws(() => C.fromShopify(products, [], { groupBy: 'template', template: 'nope' }), /Pick a category template/);
});

test('every template sorts its own sample store back into its categories', async () => {
  const { sampleStore } = await import('../sample-store.mjs');
  for (const t of P.TEMPLATES) {
    const { csv } = sampleStore(t.id, { per: 4 });
    const c = C.fromCsv(csv, { template: t.id });
    const rows = Object.values(c.skus), unmapped = rows.filter(s => s[1] === 'Unmapped').length;
    assert.ok(unmapped / rows.length < 0.05, `${t.id}: ${unmapped} of ${rows.length} SKUs unmapped`);
    assert.ok(c.cats.length >= t.cats.length * 0.7, `${t.id}: only ${c.cats.length} of ${t.cats.length} categories reached`);
  }
});
