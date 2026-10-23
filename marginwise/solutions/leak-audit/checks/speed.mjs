// Speed: mobile LCP, page weight, request count, third-party scripts and
// render-blocking scripts, measured on the homepage and (if loaded) the PDP.

import { finding, STATUS, fmtBytes } from '../lib/util.mjs';

// Thresholds as [warnAbove, failAbove].
export const THRESHOLDS = {
  lcpMs: [2500, 4000],
  transferBytes: [3 * 1024 * 1024, 6 * 1024 * 1024],
  requestCount: [100, 200],
  thirdPartyScripts: [10, 20],
  renderBlockingScripts: [0, 3],
};

/** Grade a numeric value against [warn, fail] thresholds. */
export function grade(value, [warn, fail]) {
  if (value == null || !Number.isFinite(value)) return STATUS.INFO;
  if (value > fail) return STATUS.FAIL;
  if (value > warn) return STATUS.WARN;
  return STATUS.PASS;
}

function pageFindings(tag, snap) {
  const m = snap.metrics;
  const out = [];
  const lcpStatus = m.lcpMs == null ? STATUS.INFO : grade(m.lcpMs, THRESHOLDS.lcpMs);
  out.push(finding(`speed.${tag}.lcp`, `${tag} LCP (mobile)`, lcpStatus,
    m.lcpMs == null ? 'LCP not reported by the browser.' : `${(m.lcpMs / 1000).toFixed(2)}s (warn > 2.5s, fail > 4s)`,
    lcpStatus === STATUS.PASS ? '' : 'Preload and properly size the hero/product image (fetchpriority="high", modern formats), defer non-critical JS, remove lazy-loading from the LCP image.'));

  const tb = grade(m.transferBytes, THRESHOLDS.transferBytes);
  out.push(finding(`speed.${tag}.weight`, `${tag} transfer size`, tb, `${fmtBytes(m.transferBytes)} over the wire`,
    tb === STATUS.PASS ? '' : 'Compress images (AVIF/WebP, responsive srcset), drop unused apps/fonts, lazy-load below-the-fold media and video.'));

  const rc = grade(m.requestCount, THRESHOLDS.requestCount);
  out.push(finding(`speed.${tag}.requests`, `${tag} request count`, rc, `${m.requestCount} requests`,
    rc === STATUS.PASS ? '' : 'Audit installed apps and tags; consolidate via a tag manager with load rules; remove dead pixels.'));

  const tp = m.thirdPartyScripts.length;
  const tps = grade(tp, THRESHOLDS.thirdPartyScripts);
  out.push(finding(`speed.${tag}.thirdparty`, `${tag} third-party scripts`, tps,
    `${tp} third-party script(s)${tp ? ': ' + m.thirdPartyScripts.slice(0, 6).map(shortHost).join(', ') + (tp > 6 ? ', ...' : '') : ''}`,
    tps === STATUS.PASS ? '' : 'Remove unused apps, load chat/review/upsell widgets on interaction, move marketing tags server-side where possible.'));

  const rb = m.renderBlockingScripts.length;
  const rbs = grade(rb, THRESHOLDS.renderBlockingScripts);
  out.push(finding(`speed.${tag}.blocking`, `${tag} render-blocking scripts`, rbs,
    rb ? `${rb} blocking script(s): ${m.renderBlockingScripts.slice(0, 4).map(shortHost).join(', ')}` : 'No synchronous scripts in <head>.',
    rbs === STATUS.PASS ? '' : 'Add defer/async to head scripts or move them to the end of <body>; inline only critical code.'));
  return out;
}

function shortHost(u) {
  try { const x = new URL(u); return x.hostname + x.pathname.slice(0, 30); } catch { return u.slice(0, 50); }
}

export default {
  id: 'speed',
  title: 'Speed (mobile)',
  offer: 'Teardown headline metric; full fix plan in the Revenue Leak Audit',
  weight: 20,
  run(ctx) {
    if (!ctx.home?.ok) return [finding('speed.home', 'Homepage load', STATUS.ERROR, 'Homepage could not be loaded: ' + (ctx.home?.errors?.join('; ') || 'unknown'))];
    const out = pageFindings('Homepage', ctx.home);
    if (ctx.pdp?.ok) out.push(...pageFindings('PDP', ctx.pdp));
    return out;
  },
};
