// Audit orchestration: load pages, discover a PDP, run every check in
// isolation, score the result. Used by the CLI and by the tests.

import { CHECKS, collectProbes } from '../checks/index.mjs';
import { launchBrowser, newMobileContext, snapshotPage, fetchText } from './collect.mjs';
import { finding, STATUS, POINTS, parseUrl, siteOf } from './util.mjs';

export const MARKETS = ['AU', 'NZ', 'US', 'CA', 'DE', 'SA'];

// Same-site links that look like product pages, most specific first.
const PRODUCT_LINK_RES = [/\/products\/[^/?#]+/i, /\/product\/[^/?#]+/i, /\/p\/[^/?#]+/i, /\/produkt\/[^/?#]+/i, /\/item\/[^/?#]+/i, /-p-?\d+(\.html)?$/i];

/** Find a product URL: Shopify /products.json first, then the first product-like link. */
export async function discoverPdp(fetchFn, home) {
  const origin = parseUrl(home.finalUrl)?.origin;
  if (!origin) return null;
  const pj = await fetchFn(`${origin}/products.json?limit=1`);
  if (pj.ok) {
    try {
      const handle = JSON.parse(pj.text)?.products?.[0]?.handle;
      if (handle) return { url: `${origin}/products/${handle}`, via: '/products.json' };
    } catch { /* not JSON: not Shopify or blocked */ }
  }
  const site = siteOf(parseUrl(origin).hostname);
  for (const re of PRODUCT_LINK_RES) {
    const link = (home.links || []).find((l) => {
      const u = parseUrl(l.href);
      return u && siteOf(u.hostname) === site && re.test(u.pathname);
    });
    if (link) return { url: link.href.split('#')[0], via: 'first product link' };
  }
  return null;
}

/**
 * Weighted score out of 100. Each check scores the mean of its pass/warn/fail
 * points; info and error findings are ignored. US doubles accessibility.
 */
export function score(results, market) {
  let num = 0;
  let den = 0;
  for (const r of results) {
    const pts = r.findings.map((f) => POINTS[f.status]).filter((p) => p != null);
    let w = r.weight;
    if (market === 'US' && r.id === 'accessibility') w *= 2;
    r.effectiveWeight = w;
    r.score = pts.length ? Math.round((pts.reduce((a, b) => a + b, 0) / pts.length) * 100) : null;
    if (!pts.length || !w) continue;
    num += (r.score / 100) * w;
    den += w;
  }
  return den ? Math.round((num / den) * 100) : 0;
}

/** Top findings: fails before warns, heavier checks first. */
export function topFindings(results, n = 5) {
  const rank = { fail: 0, warn: 1 };
  return results
    .flatMap((r) => r.findings.filter((f) => f.status in rank).map((f) => ({ ...f, check: r.title, w: r.effectiveWeight ?? r.weight })))
    .sort((a, b) => rank[a.status] - rank[b.status] || b.w - a.w)
    .slice(0, n);
}

/**
 * Run checks against a prepared context. Each check is isolated: an
 * exception becomes a single "error" finding and the loop continues.
 */
export async function runChecks(ctx, checks = CHECKS, log = () => {}) {
  const results = [];
  for (const check of checks) {
    if (check.markets && !check.markets.includes(ctx.market)) continue;
    let findings;
    try {
      findings = await check.run(ctx);
      if (!Array.isArray(findings)) throw new Error('check returned no findings array');
    } catch (err) {
      findings = [finding(`${check.id}.error`, `${check.title} could not run`, STATUS.ERROR, String(err?.message || err).split('\n')[0])];
    }
    results.push({ id: check.id, title: check.title, offer: check.offer, weight: check.weight, findings });
    log(`  ${check.title}: ${findings.map((f) => f.status).join(' ')}`);
  }
  return results;
}

/**
 * Run a full audit.
 * @param {string} url homepage URL
 * @param {object} [opts] { market, pdp, stubExternal, settleMs, log }
 */
export async function runAudit(url, opts = {}) {
  const market = (opts.market || 'US').toUpperCase();
  const log = opts.log || (() => {});
  const startedAt = new Date().toISOString();
  const probes = collectProbes(CHECKS);
  const browser = await launchBrowser(url);
  try {
    const fetchCtx = await newMobileContext(browser);
    const fetchFn = (u) => fetchText(fetchCtx, u);
    const snapOpts = { stubExternal: opts.stubExternal, settleMs: opts.settleMs ?? 2500 };

    log(`Loading homepage ${url}`);
    const home = await snapshotPage(browser, url, { ...snapOpts, probes: probes.home });

    let pdpSource = opts.pdp || null;
    let pdpVia = opts.pdp ? '--pdp' : null;
    if (!pdpSource && home.ok) {
      const found = await discoverPdp(fetchFn, home).catch(() => null);
      if (found) { pdpSource = found.url; pdpVia = found.via; }
    }
    let pdp = null;
    if (pdpSource) {
      log(`Loading product page ${pdpSource} (${pdpVia})`);
      pdp = await snapshotPage(browser, pdpSource, { ...snapOpts, probes: probes.pdp });
    }

    const ctx = { market, home, pdp, pdpSource, origin: parseUrl(home.finalUrl || url)?.origin, fetch: fetchFn };
    const results = await runChecks(ctx, CHECKS, log);
    await fetchCtx.close().catch(() => {});

    const total = score(results, market);
    return {
      tool: 'marginwise-leak-audit',
      version: '1.0.0',
      url,
      finalUrl: home.finalUrl,
      market,
      startedAt,
      finishedAt: new Date().toISOString(),
      device: 'iPhone 13 (Chromium emulation)',
      platform: ctx.platform || null,
      pdp: pdpSource ? { url: pdpSource, via: pdpVia, loaded: !!pdp?.ok } : null,
      score: total,
      counts: countStatuses(results),
      top: topFindings(results),
      checks: results,
      pageErrors: { home: home.errors, pdp: pdp?.errors || [] },
    };
  } finally {
    await browser.close().catch(() => {});
  }
}

function countStatuses(results) {
  const c = { pass: 0, warn: 0, fail: 0, info: 0, error: 0 };
  for (const r of results) for (const f of r.findings) c[f.status] = (c[f.status] || 0) + 1;
  return c;
}
