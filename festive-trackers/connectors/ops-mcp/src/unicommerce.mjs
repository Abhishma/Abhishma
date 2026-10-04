/*
 * Unicommerce (Uniware) read-only client.
 * Docs: https://documentation.unicommerce.com/docs/using-the-uniware-apis.html
 *
 * Verified from the docs: bearer token from GET /oauth/token; POST /services/rest/v1/inventory/inventorySnapshot/get
 * with itemTypeSKUs and updatedSinceInMinutes (max 1440); POST /services/rest/v1/oms/saleOrder/search with
 * fromDate/toDate (ISO), dateType (CREATED | UPDATED | FULFILLMENT_TAT), status, channel, facilityCodes.
 * VERIFY on first live call: client_id value, the Facility header name, searchOptions field names,
 * the saleorder/get path and response shape, and the SKU batch size.
 */

const CLIENT_ID = 'my-trusted-client';   // VERIFY: Uniware's documented public client id
const SKU_BATCH = 500;                    // VERIFY: documented maximum SKUs per snapshot call

export class UnicommerceError extends Error {}

export function unicommerce(env, fetchImpl = fetch) {
  const base = `https://${env.UNICOMMERCE_TENANT}.unicommerce.com`;
  let token = null, expiresAt = 0;

  async function login() {
    const q = new URLSearchParams({ grant_type: 'password', client_id: CLIENT_ID, username: env.UNICOMMERCE_USERNAME, password: env.UNICOMMERCE_PASSWORD });
    const r = await fetchImpl(`${base}/oauth/token?${q}`, { method: 'GET' });
    if (!r.ok) throw new UnicommerceError(`Unicommerce login failed (HTTP ${r.status}). Check UNICOMMERCE_USERNAME and UNICOMMERCE_PASSWORD.`);
    const j = await r.json();
    if (!j.access_token) throw new UnicommerceError('Unicommerce login returned no access token.');
    token = j.access_token;
    expiresAt = Date.now() + Math.max(60, (j.expires_in || 3600) - 60) * 1000;
  }

  async function post(path, body, { facility } = {}, retried = false) {
    if (!token || Date.now() > expiresAt) await login();
    const headers = { 'Content-Type': 'application/json', Authorization: `bearer ${token}` };
    if (facility) headers.Facility = facility;   // VERIFY: header name for facility-level APIs
    const r = await fetchImpl(base + path, { method: 'POST', headers, body: JSON.stringify(body) });
    if (r.status === 401 && !retried) { token = null; return post(path, body, { facility }, true); }
    if (!r.ok) throw new UnicommerceError(`Unicommerce ${path} failed (HTTP ${r.status}).`);
    const j = await r.json();
    if (j.successful === false) {
      const msg = (j.errors || []).map(e => e.description || e.message).filter(Boolean).join('; ');
      throw new UnicommerceError(`Unicommerce ${path} returned an error${msg ? ': ' + msg : '.'}`);
    }
    return j;
  }

  return {
    /** Stock by SKU in one facility. */
    async inventorySnapshot({ skus, facility, updatedSinceMinutes }) {
      const fac = facility || env.UNICOMMERCE_FACILITY;
      if (!fac) throw new UnicommerceError('No facility given and UNICOMMERCE_FACILITY is not set.');
      if (updatedSinceMinutes != null && (updatedSinceMinutes < 1 || updatedSinceMinutes > 1440)) throw new UnicommerceError('updated_since_minutes must be between 1 and 1440.');
      const batches = skus && skus.length ? chunk(skus, SKU_BATCH) : [null];
      const out = [];
      for (const b of batches) {
        const body = {};
        if (b) body.itemTypeSKUs = b;
        if (updatedSinceMinutes != null) body.updatedSinceInMinutes = updatedSinceMinutes;
        const j = await post('/services/rest/v1/inventory/inventorySnapshot/get', body, { facility: fac });
        for (const s of j.inventorySnapshots || []) {
          const { itemTypeSKU, ...rest } = s;
          out.push({ sku: itemTypeSKU, facility: fac, ...numbersOnly(rest) });
        }
      }
      return out;
    },

    /** Order headers in a date window (one page). */
    async searchSaleOrders({ from, to, dateType = 'CREATED', status, channel, facilityCodes, start = 0, limit = 100 }) {
      const body = { fromDate: iso(from, false), toDate: iso(to, true), dateType };
      if (status) body.status = status;
      if (channel) body.channel = channel;
      if (facilityCodes && facilityCodes.length) body.facilityCodes = facilityCodes;
      body.searchOptions = { displayStart: start, displayLength: Math.min(limit, 500), getCount: true };   // VERIFY field names
      const j = await post('/services/rest/v1/oms/saleOrder/search', body);
      const rows = (j.elements || []).map(e => pick(e, ['code', 'displayOrderCode', 'channel', 'status', 'created', 'updated', 'fulfillmentTat', 'cashOnDelivery']));
      return { total: j.totalRecords ?? null, start, count: rows.length, orders: rows };
    },

    /** One order with its items and shipping packages (AWB and courier for ClickPost). */
    async getSaleOrder({ code }) {
      const j = await post('/services/rest/v1/oms/saleorder/get', { code });   // VERIFY path casing
      const o = j.saleOrderDTO || {};
      return {
        code: o.code ?? code,
        displayOrderCode: o.displayOrderCode ?? null,
        status: o.status ?? null,
        channel: o.channel ?? null,
        created: o.created ?? null,
        items: (o.saleOrderItems || []).map(i => pick(i, ['itemSku', 'status', 'sellingPrice', 'shippingPackageCode', 'facilityCode', 'returnReason'])),
        packages: (o.shippingPackages || []).map(p => pick(p, ['code', 'status', 'shippingProvider', 'trackingNumber', 'dispatched', 'delivered', 'facilityCode'])),
      };
    },
  };
}

const chunk = (a, n) => { const out = []; for (let i = 0; i < a.length; i += n) out.push(a.slice(i, i + n)); return out; };
const pick = (o, keys) => Object.fromEntries(keys.filter(k => o[k] !== undefined).map(k => [k, o[k]]));
const numbersOnly = o => Object.fromEntries(Object.entries(o).filter(([, v]) => typeof v === 'number'));
function iso(d, endOfDay) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(d)) throw new UnicommerceError(`Dates must be YYYY-MM-DD, got "${d}".`);
  // Whole IST days: 00:00 IST is 18:30 UTC the day before.
  const t = Date.parse(`${d}T${endOfDay ? '23:59:59.999' : '00:00:00.000'}+05:30`);
  return new Date(t).toISOString();
}
