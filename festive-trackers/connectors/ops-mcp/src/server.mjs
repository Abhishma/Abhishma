/*
 * ops-mcp: a read-only remote MCP server (Streamable HTTP, stateless, JSON responses) exposing
 * Unicommerce and ClickPost to claude.ai as one custom connector.
 *
 * Access: the endpoint is /mcp/<MCP_PATH_TOKEN>. Anyone holding the full URL can read the data the
 * tools return, so treat the URL as a password. Every tool is read-only.
 */
import { unicommerce } from './unicommerce.mjs';
import { clickpost } from './clickpost.mjs';

const SERVER = { name: 'r4r-ops', version: '0.1.0' };
const PROTOCOLS = ['2025-06-18', '2025-03-26', '2024-11-05'];
const RO = { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: true };
const DATE = { type: 'string', pattern: '^\\d{4}-\\d{2}-\\d{2}$', description: 'IST calendar date, YYYY-MM-DD' };

export const TOOLS = [
  {
    name: 'unicommerce_inventory_snapshot',
    title: 'Unicommerce stock by SKU',
    description: 'Warehouse stock per SKU in one Unicommerce facility: inventory, open sale, open purchase, putaway pending, blocked and other counts. Give up to 5000 SKUs, or none with updated_since_minutes for everything changed recently.',
    inputSchema: { type: 'object', additionalProperties: false, properties: {
      skus: { type: 'array', items: { type: 'string' }, maxItems: 5000 },
      facility: { type: 'string', description: 'Facility code; defaults to the configured facility' },
      updated_since_minutes: { type: 'integer', minimum: 1, maximum: 1440 },
    } },
    annotations: RO,
    run: (c, a) => c.uc.inventorySnapshot({ skus: a.skus, facility: a.facility, updatedSinceMinutes: a.updated_since_minutes }).then(rows => ({ count: rows.length, rows })),
  },
  {
    name: 'unicommerce_search_sale_orders',
    title: 'Unicommerce order search',
    description: 'Order headers (code, channel, status, created) for an IST date window, one page at a time.',
    inputSchema: { type: 'object', additionalProperties: false, required: ['from', 'to'], properties: {
      from: DATE, to: DATE,
      date_type: { type: 'string', enum: ['CREATED', 'UPDATED', 'FULFILLMENT_TAT'], default: 'CREATED' },
      status: { type: 'string' }, channel: { type: 'string' },
      facility_codes: { type: 'array', items: { type: 'string' } },
      start: { type: 'integer', minimum: 0, default: 0 },
      limit: { type: 'integer', minimum: 1, maximum: 500, default: 100 },
    } },
    annotations: RO,
    run: (c, a) => c.uc.searchSaleOrders({ from: a.from, to: a.to, dateType: a.date_type, status: a.status, channel: a.channel, facilityCodes: a.facility_codes, start: a.start, limit: a.limit }),
  },
  {
    name: 'unicommerce_get_sale_order',
    title: 'Unicommerce order detail',
    description: 'One order with its items and shipping packages, including AWB (trackingNumber) and courier (shippingProvider).',
    inputSchema: { type: 'object', additionalProperties: false, required: ['code'], properties: { code: { type: 'string' } } },
    annotations: RO,
    run: (c, a) => c.uc.getSaleOrder({ code: a.code }),
  },
  {
    name: 'clickpost_track',
    title: 'ClickPost shipment status',
    description: 'Latest ClickPost status for up to 50 shipments, each { waybill, cp_id }. Every result carries a bucket: pre_transit, in_transit, out_for_delivery, delivered, ndr, rto, cancelled, exception, lost, damaged, other or not_found.',
    inputSchema: { type: 'object', additionalProperties: false, required: ['shipments'], properties: {
      shipments: { type: 'array', minItems: 1, maxItems: 50, items: { type: 'object', additionalProperties: false, required: ['waybill', 'cp_id'], properties: { waybill: { type: 'string' }, cp_id: { type: 'integer' } } } },
    } },
    annotations: RO,
    run: (c, a) => c.cp.track(a.shipments).then(rows => ({ count: rows.length, summary: tally(rows), rows })),
  },
  {
    name: 'order_delivery_status',
    title: 'Delivery status for orders',
    description: 'For up to 20 Unicommerce order codes: each shipping package with its AWB, courier and latest ClickPost status. Couriers are matched to ClickPost ids through the configured CLICKPOST_CP_IDS map.',
    inputSchema: { type: 'object', additionalProperties: false, required: ['codes'], properties: { codes: { type: 'array', items: { type: 'string' }, minItems: 1, maxItems: 20 } } },
    annotations: RO,
    run: async (c, a) => {
      const map = cpMap(c.env);
      const rows = [];
      for (const code of a.codes) {
        const o = await c.uc.getSaleOrder({ code });
        for (const p of o.packages) rows.push({ order: o.code, display_order: o.displayOrderCode, package: p.code, package_status: p.status, courier: p.shippingProvider || null, waybill: p.trackingNumber || null, cp_id: map[(p.shippingProvider || '').toLowerCase()] ?? null });
      }
      const trackable = rows.filter(r => r.waybill && r.cp_id != null);
      const st = trackable.length ? await c.cp.track(trackable.map(r => ({ waybill: r.waybill, cp_id: r.cp_id }))) : [];
      const byWb = Object.fromEntries(st.map(s => [s.waybill, s]));
      for (const r of rows) {
        const s = byWb[r.waybill];
        r.tracking = s ? { bucket: s.bucket, status: s.status, at: s.at, location: s.location } : { bucket: null, note: !r.waybill ? 'No AWB yet' : r.cp_id == null ? `Courier "${r.courier}" is not in CLICKPOST_CP_IDS` : 'Not found in ClickPost' };
      }
      return { count: rows.length, summary: tally(rows.map(r => ({ bucket: r.tracking.bucket || 'untracked' }))), rows };
    },
  },
];

function tally(rows) { const t = {}; for (const r of rows) t[r.bucket] = (t[r.bucket] || 0) + 1; return t; }
function cpMap(env) {
  try { return Object.fromEntries(Object.entries(JSON.parse(env.CLICKPOST_CP_IDS || '{}')).map(([k, v]) => [k.toLowerCase(), Number(v)])); }
  catch { return {}; }
}

/* Constant-time comparison for the path token. */
function sameToken(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string' || !b || a.length !== b.length) return false;
  let d = 0; for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}

const json = (body, status = 200, extra = {}) => new Response(body === null ? null : JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store', ...extra } });
const rpcError = (id, code, message) => json({ jsonrpc: '2.0', id: id ?? null, error: { code, message } });

export function createHandler({ fetchImpl = fetch } = {}) {
  let clients = null;
  const ctx = env => {
    if (!clients) clients = { env, uc: unicommerce(env, fetchImpl), cp: clickpost(env, fetchImpl) };
    return clients;
  };

  return async function handle(request, env) {
    if (env.MCP_PATH_TOKEN && env.MCP_PATH_TOKEN.length < 32) return json({ error: 'MCP_PATH_TOKEN must be at least 32 characters.' }, 500);
    const url = new URL(request.url);
    const m = url.pathname.match(/^\/mcp\/([^/]+)\/?$/);
    if (!m || !sameToken(m[1], env.MCP_PATH_TOKEN)) return json({ error: 'Not found' }, 404);
    if (request.method === 'GET' || request.method === 'DELETE') return json(null, 405, { Allow: 'POST' });
    if (request.method !== 'POST') return json(null, 405, { Allow: 'POST' });

    let msg;
    try { msg = await request.json(); } catch { return rpcError(null, -32700, 'Parse error'); }
    if (Array.isArray(msg)) return rpcError(null, -32600, 'Batch requests are not supported');
    if (!msg || msg.jsonrpc !== '2.0' || typeof msg.method !== 'string') return rpcError(msg && msg.id, -32600, 'Invalid request');
    if (msg.id === undefined) return json(null, 202);   // notification

    const { id, method, params = {} } = msg;
    if (method === 'initialize') {
      const v = PROTOCOLS.includes(params.protocolVersion) ? params.protocolVersion : PROTOCOLS[0];
      return json({ jsonrpc: '2.0', id, result: { protocolVersion: v, capabilities: { tools: { listChanged: false } }, serverInfo: SERVER,
        instructions: 'Read-only access to R for Rabbit operations data: Unicommerce stock and orders, ClickPost shipment status. Dates are IST.' } });
    }
    if (method === 'ping') return json({ jsonrpc: '2.0', id, result: {} });
    if (method === 'tools/list') return json({ jsonrpc: '2.0', id, result: { tools: TOOLS.map(({ run, ...t }) => t) } });
    if (method === 'tools/call') {
      const tool = TOOLS.find(t => t.name === params.name);
      if (!tool) return rpcError(id, -32602, `Unknown tool: ${params.name}`);
      try {
        const out = await tool.run(ctx(env), params.arguments || {});
        return json({ jsonrpc: '2.0', id, result: { content: [{ type: 'text', text: JSON.stringify(out) }], structuredContent: out } });
      } catch (e) {
        // Messages are written by our clients and never include credentials or full URLs.
        const text = e && e.message && /^(Unicommerce|ClickPost|No facility|updated_since|Dates must|CLICKPOST_)/.test(e.message) ? e.message : 'The upstream service could not be reached.';
        return json({ jsonrpc: '2.0', id, result: { content: [{ type: 'text', text }], isError: true } });
      }
    }
    return rpcError(id, -32601, `Method not found: ${method}`);
  };
}
