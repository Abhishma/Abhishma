/*
 * ClickPost read-only tracking client.
 * Docs: https://docs.clickpost.ai/reference/tracking-shipment-using-polling-1
 *
 * Verified: GET https://api.clickpost.in/api/v2/track-order/?username=&key=&waybill=&cp_id=, at most 10 waybills
 * per request, latest_status.clickpost_status_code. Codes 1-13 below are from ClickPost's status code page.
 * VERIFY on first live call: that several waybills go comma separated, and the result keying.
 */

const BASE = 'https://api.clickpost.in/api/v2/track-order/';
const PER_REQUEST = 10;

const CODES = {
  1: ['OrderPlaced', 'pre_transit'], 2: ['PickupPending', 'pre_transit'], 3: ['PickupFailed', 'pre_transit'],
  4: ['PickedUp', 'in_transit'], 5: ['InTransit', 'in_transit'], 6: ['OutForDelivery', 'out_for_delivery'],
  7: ['NotServiceable', 'exception'], 8: ['Delivered', 'delivered'], 9: ['FailedDelivery', 'ndr'],
  10: ['Cancelled', 'cancelled'], 11: ['RTO-Requested', 'rto'], 12: ['RTO-Marked', 'rto'], 13: ['RTO-OutForDelivery', 'rto'],
};

/** Bucket for a status: documented code first, then the description for codes not in the table. */
export function bucketOf(code, description = '') {
  if (CODES[code]) return CODES[code][1];
  const d = String(description).toLowerCase();
  if (d.includes('rto')) return 'rto';
  if (d.includes('lost')) return 'lost';
  if (d.includes('damage')) return 'damaged';
  if (d.includes('deliver') && !d.includes('fail') && !d.includes('out for')) return 'delivered';
  return 'other';
}

export class ClickPostError extends Error {}

export function clickpost(env, fetchImpl = fetch) {
  return {
    /** Latest status for up to 50 shipments: [{ waybill, cp_id }]. */
    async track(shipments) {
      if (!env.CLICKPOST_USERNAME || !env.CLICKPOST_KEY) throw new ClickPostError('CLICKPOST_USERNAME and CLICKPOST_KEY are not set.');
      const byCp = {};
      for (const s of shipments) (byCp[s.cp_id] || (byCp[s.cp_id] = [])).push(String(s.waybill));
      const out = [];
      for (const [cp, wbs] of Object.entries(byCp)) {
        for (let i = 0; i < wbs.length; i += PER_REQUEST) {
          const batch = wbs.slice(i, i + PER_REQUEST);
          const q = new URLSearchParams({ username: env.CLICKPOST_USERNAME, key: env.CLICKPOST_KEY, waybill: batch.join(','), cp_id: cp });
          const r = await fetchImpl(`${BASE}?${q}`, { method: 'GET' });
          if (!r.ok) throw new ClickPostError(`ClickPost tracking failed (HTTP ${r.status}).`);
          const j = await r.json();
          if (j.meta && j.meta.success === false) throw new ClickPostError(`ClickPost tracking error: ${j.meta.message || 'unknown'}.`);
          const res = j.result || {};
          for (const wb of batch) {
            const x = res[wb];
            const ls = x && x.latest_status;
            if (!ls) { out.push({ waybill: wb, cp_id: Number(cp), found: false, bucket: 'not_found' }); continue; }
            const code = Number(ls.clickpost_status_code);
            out.push({
              waybill: wb, cp_id: Number(cp), found: true,
              status_code: code,
              status: ls.clickpost_status_description || (CODES[code] && CODES[code][0]) || null,
              bucket: bucketOf(code, ls.clickpost_status_description),
              at: ls.timestamp || null, location: ls.location || null, remark: ls.remark || null,
            });
          }
        }
      }
      return out;
    },
  };
}
