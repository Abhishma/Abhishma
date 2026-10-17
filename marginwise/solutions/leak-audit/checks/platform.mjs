// Platform detection: fingerprints the store platform from HTML, script URLs,
// response headers and page globals. Informational only (not scored), but it
// decides which fixes are realistic and feeds product-page discovery.

import { finding, STATUS } from '../lib/util.mjs';

// Each signature lists regexes tested against a combined haystack of HTML,
// script URLs and header lines, plus an optional page-global flag.
const SIGNATURES = [
  { name: 'Shopify', global: 'Shopify', re: [/cdn\.shopify\.com/i, /Shopify\.theme/, /myshopify\.com/i, /x-shopid:/i, /shopify-digital-wallet/i] },
  { name: 'Shopware', re: [/shopware/i, /\/bundles\/storefront\//i, /sw-plugin|data-sw-/i] },
  { name: 'Magento', global: 'Mage', re: [/Magento_[A-Z]/, /\/static\/version\d+\//i, /mage\/cookies|x-magento-/i, /text\/x-magento-init/i] },
  { name: 'WooCommerce', global: 'woocommerce', re: [/wp-content\/plugins\/woocommerce/i, /woocommerce-(page|cart|no-js)/i, /wc-block/i] },
  { name: 'Salla', global: 'salla', re: [/cdn\.salla\.(network|sa)/i, /salla\.sa/i, /salla-/i] },
  { name: 'Zid', global: 'zid', re: [/zid\.store/i, /zidcdn|media\.zid\./i, /zid-/i] },
  { name: 'BigCommerce', global: 'BCData', re: [/cdn\d*\.bigcommerce\.com/i, /stencil-utils/i, /bigcommerce/i] },
  { name: 'SFCC (Demandware)', re: [/demandware\.static/i, /\/on\/demandware\.store\//i, /dwanalytics|dw\/shop\//i, /demandware/i] },
];

/** Pure detector so tests and other checks can reuse it. */
export function detectPlatform(snap) {
  if (!snap) return [];
  const headers = Object.entries(snap.headers || {}).map(([k, v]) => `${k}: ${v}`).join('\n');
  const hay = [snap.html || '', (snap.scripts || []).map((s) => s.src).join('\n'), headers].join('\n');
  const results = [];
  for (const sig of SIGNATURES) {
    const hits = sig.re.filter((r) => r.test(hay)).map((r) => r.source);
    const g = sig.global && snap.globals?.[sig.global];
    const score = hits.length + (g ? 2 : 0);
    if (score > 0) results.push({ name: sig.name, score, signals: [...(g ? [`window.${sig.global}`] : []), ...hits] });
  }
  return results.sort((a, b) => b.score - a.score);
}

export default {
  id: 'platform',
  title: 'Platform detection',
  offer: 'Free 2-minute teardown (context for every fix)',
  weight: 0,
  run(ctx) {
    const found = detectPlatform(ctx.home);
    ctx.platform = found[0]?.name || null; // shared with later checks
    if (!found.length) {
      return [finding('platform.detected', 'Store platform', STATUS.INFO, 'No known platform fingerprint found (custom build or headless).', 'Confirm the stack with the client before scoping fixes.')];
    }
    const top = found[0];
    const others = found.slice(1).map((f) => f.name).join(', ');
    return [finding('platform.detected', 'Store platform', STATUS.INFO,
      `${top.name} (signals: ${top.signals.slice(0, 3).join(', ')})${others ? `; weaker matches: ${others}` : ''}`)];
  },
};
