import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHandler } from '../src/server.mjs';
import { bucketOf } from '../src/clickpost.mjs';

const TOKEN = 'a'.repeat(40);
const ENV = {
  MCP_PATH_TOKEN: TOKEN, UNICOMMERCE_TENANT: 'demo', UNICOMMERCE_USERNAME: 'u', UNICOMMERCE_PASSWORD: 'p',
  UNICOMMERCE_FACILITY: 'WH1', CLICKPOST_USERNAME: 'cu', CLICKPOST_KEY: 'zq-secret-key-77', CLICKPOST_CP_IDS: '{"Delhivery": 4}',
};
const res = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

/* Fake upstreams: records every call, answers by URL. */
function upstream(overrides = {}) {
  const calls = [];
  let logins = 0;
  const f = async (url, init = {}) => {
    const u = new URL(url);
    const body = init.body ? JSON.parse(init.body) : null;
    calls.push({ url: u, init, body });
    if (u.pathname === '/oauth/token') { logins++; return res({ access_token: 'tok' + logins, expires_in: 43200 }); }
    for (const [k, fn] of Object.entries(overrides)) if (u.pathname.endsWith(k)) return fn(u, init, body, calls);
    if (u.pathname.endsWith('/inventorySnapshot/get')) return res({ successful: true, inventorySnapshots: (body.itemTypeSKUs || ['ALL']).map(s => ({ itemTypeSKU: s, inventory: 5, openSale: 1, note: 'x' })) });
    if (u.pathname.endsWith('/saleOrder/search')) return res({ successful: true, totalRecords: 1, elements: [{ code: 'SO1', channel: 'SHOPIFY', status: 'COMPLETE', created: 1, junk: 'y' }] });
    if (u.pathname.endsWith('/saleorder/get')) return res({ successful: true, saleOrderDTO: { code: body.code, displayOrderCode: '#1001', status: 'COMPLETE', saleOrderItems: [{ itemSku: 'SKU1', status: 'DISPATCHED' }], shippingPackages: [{ code: 'PK1', status: 'DISPATCHED', shippingProvider: 'Delhivery', trackingNumber: 'AWB1' }, { code: 'PK2', status: 'CREATED', shippingProvider: 'Ekart' }] } });
    if (u.hostname === 'api.clickpost.in') {
      const result = {};
      for (const wb of u.searchParams.get('waybill').split(',')) if (wb !== 'MISSING') result[wb] = { latest_status: { clickpost_status_code: wb === 'AWB9' ? 9 : 8, clickpost_status_description: wb === 'AWB9' ? 'FailedDelivery' : 'Delivered', timestamp: '2026-10-03T10:00:00Z', location: 'Jaipur' } };
      return res({ meta: { success: true }, result });
    }
    return res({}, 404);
  };
  f.calls = calls; f.logins = () => logins;
  return f;
}

async function rpc(handle, method, params, { token = TOKEN, env = ENV, id = 1 } = {}) {
  const r = await handle(new Request(`https://x.dev/mcp/${token}`, { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json, text/event-stream' }, body: JSON.stringify({ jsonrpc: '2.0', id, method, params }) }), env);
  return { status: r.status, body: r.status === 202 || r.status === 404 ? null : await r.json() };
}
const call = async (handle, name, args) => (await rpc(handle, 'tools/call', { name, arguments: args })).body.result;

test('rejects a wrong or missing path token', async () => {
  const h = createHandler({ fetchImpl: upstream() });
  assert.equal((await rpc(h, 'tools/list', {}, { token: 'b'.repeat(40) })).status, 404);
  assert.equal((await rpc(h, 'tools/list', {}, { env: { ...ENV, MCP_PATH_TOKEN: '' } })).status, 404);
});

test('initialize negotiates the protocol and lists read-only tools', async () => {
  const h = createHandler({ fetchImpl: upstream() });
  const init = (await rpc(h, 'initialize', { protocolVersion: '2025-03-26', capabilities: {}, clientInfo: { name: 't', version: '1' } })).body.result;
  assert.equal(init.protocolVersion, '2025-03-26');
  assert.equal((await rpc(h, 'initialize', { protocolVersion: '1999-01-01' })).body.result.protocolVersion, '2025-06-18');
  const tools = (await rpc(h, 'tools/list', {})).body.result.tools;
  assert.deepEqual(tools.map(t => t.name), ['unicommerce_inventory_snapshot', 'unicommerce_search_sale_orders', 'unicommerce_get_sale_order', 'clickpost_track', 'order_delivery_status']);
  assert.ok(tools.every(t => t.annotations.readOnlyHint === true && !('run' in t)));
});

test('notifications get 202, unknown methods an error', async () => {
  const h = createHandler({ fetchImpl: upstream() });
  const r = await h(new Request(`https://x.dev/mcp/${TOKEN}`, { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'notifications/initialized' }) }), ENV);
  assert.equal(r.status, 202);
  assert.equal((await rpc(h, 'resources/list', {})).body.error.code, -32601);
});

test('inventory snapshot batches SKUs, sends facility, keeps numbers only', async () => {
  const f = upstream(); const h = createHandler({ fetchImpl: f });
  const skus = Array.from({ length: 1200 }, (_, i) => 'S' + i);
  const out = (await call(h, 'unicommerce_inventory_snapshot', { skus })).structuredContent;
  assert.equal(out.count, 1200);
  assert.deepEqual(out.rows[0], { sku: 'S0', facility: 'WH1', inventory: 5, openSale: 1 });
  const inv = f.calls.filter(c => c.url.pathname.endsWith('/inventorySnapshot/get'));
  assert.equal(inv.length, 3);
  assert.equal(inv[0].init.headers.Facility, 'WH1');
  assert.equal(inv[0].init.headers.Authorization, 'bearer tok1');
  assert.equal(f.logins(), 1);
});

test('order search sends IST day bounds and trims fields', async () => {
  const f = upstream(); const h = createHandler({ fetchImpl: f });
  const out = (await call(h, 'unicommerce_search_sale_orders', { from: '2026-10-01', to: '2026-10-03' })).structuredContent;
  assert.deepEqual(out.orders[0], { code: 'SO1', channel: 'SHOPIFY', status: 'COMPLETE', created: 1 });
  const b = f.calls.find(c => c.url.pathname.endsWith('/saleOrder/search')).body;
  assert.equal(b.fromDate, '2026-09-30T18:30:00.000Z');
  assert.equal(b.toDate, '2026-10-03T18:29:59.999Z');
  assert.equal(b.dateType, 'CREATED');
});

test('re-logs in once on 401', async () => {
  let first = true;
  const f = upstream({ '/saleorder/get': (u, init, body) => {
    if (first) { first = false; return res({}, 401); }
    return res({ successful: true, saleOrderDTO: { code: body.code } });
  } });
  const h = createHandler({ fetchImpl: f });
  const out = await call(h, 'unicommerce_get_sale_order', { code: 'SO1' });
  assert.equal(out.isError, undefined);
  assert.equal(f.logins(), 2);
});

test('clickpost groups by courier, 10 waybills per request, buckets statuses', async () => {
  const f = upstream(); const h = createHandler({ fetchImpl: f });
  const shipments = [...Array.from({ length: 12 }, (_, i) => ({ waybill: 'W' + i, cp_id: 4 })), { waybill: 'AWB9', cp_id: 5 }, { waybill: 'MISSING', cp_id: 5 }];
  const out = (await call(h, 'clickpost_track', { shipments })).structuredContent;
  assert.equal(f.calls.filter(c => c.url.hostname === 'api.clickpost.in').length, 3);
  assert.deepEqual(out.summary, { delivered: 12, ndr: 1, not_found: 1 });
  assert.equal(out.rows.find(r => r.waybill === 'MISSING').found, false);
  assert.ok(!JSON.stringify(out).includes('zq-secret-key-77'), 'credentials never echoed');
});

test('order delivery status joins Unicommerce packages to ClickPost', async () => {
  const h = createHandler({ fetchImpl: upstream() });
  const out = (await call(h, 'order_delivery_status', { codes: ['SO1'] })).structuredContent;
  assert.equal(out.count, 2);
  assert.equal(out.rows[0].tracking.bucket, 'delivered');
  assert.equal(out.rows[0].cp_id, 4);
  assert.match(out.rows[1].tracking.note, /No AWB/);
  assert.deepEqual(out.summary, { delivered: 1, untracked: 1 });
});

test('upstream failures come back as tool errors without secrets', async () => {
  const f = upstream({ '/oauth/token': () => res({}, 401) });
  const h = createHandler({ fetchImpl: async (url, init) => new URL(url).pathname === '/oauth/token' ? res({ error: 'bad' }, 401) : f(url, init) });
  const out = await call(h, 'unicommerce_get_sale_order', { code: 'SO1' });
  assert.equal(out.isError, true);
  assert.match(out.content[0].text, /login failed/);
  assert.ok(!out.content[0].text.includes('password=p'));
});

test('status buckets fall back to the description for undocumented codes', () => {
  assert.equal(bucketOf(12), 'rto');
  assert.equal(bucketOf(99, 'RTO-Delivered'), 'rto');
  assert.equal(bucketOf(99, 'Shipment Lost'), 'lost');
  assert.equal(bucketOf(99, 'Something new'), 'other');
});
