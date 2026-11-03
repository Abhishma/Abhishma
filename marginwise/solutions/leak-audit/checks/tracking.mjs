// Tracking and consent: which marketing/analytics trackers fire before the
// visitor has interacted with any consent banner, and whether a consent
// banner exists at all. The audit never clicks anything, so every request
// captured is by definition "pre-consent".

import { finding, STATUS } from '../lib/util.mjs';
import { CMPS, matchTrackers } from '../lib/trackers.mjs';

// Markets where firing trackers before consent is treated as a hard fail
// (GDPR/TTDSG in Germany; PIPEDA and Quebec Law 25 in Canada).
const STRICT = new Set(['DE', 'CA']);

/** Detect a consent banner from DOM ids, CMP network calls or a generic banner. */
export function detectConsent(snaps) {
  const names = new Set();
  let generic = null;
  for (const s of snaps) {
    (s.cmpDom || []).forEach((n) => names.add(n));
    for (const c of CMPS) if ((s.requests || []).some((r) => c.net.test(r.url))) names.add(c.name);
    if (s.genericBanner && !generic) generic = s.genericBanner;
  }
  if (!names.size && generic) names.add('Generic banner');
  return { names: [...names], generic };
}

export default {
  id: 'tracking',
  title: 'Tracking and consent',
  offer: 'Teardown red flag; Revenue Leak Audit includes consent-mode and tag-load plan',
  weight: 15,
  run(ctx) {
    const snaps = [ctx.home, ctx.pdp].filter((s) => s?.ok);
    if (!snaps.length) return [finding('tracking', 'Tracking scan', STATUS.ERROR, 'No page loaded.')];
    const strict = STRICT.has(ctx.market);
    const trackers = matchTrackers(snaps.flatMap((s) => s.requests));
    const consent = detectConsent(snaps);
    ctx.preConsentTrackers = trackers; // shared with market checks
    ctx.consent = consent;
    const out = [];

    // Google consent mode "denied" pings (gcs=G100) are cookieless; note them.
    const deniedPings = snaps.flatMap((s) => s.requests).filter((r) => /[?&]gcs=G1[01]0/.test(r.url)).length;

    let status;
    if (!trackers.length) status = STATUS.PASS;
    else if (strict) status = STATUS.FAIL;
    else status = consent.names.length ? STATUS.WARN : STATUS.INFO;
    out.push(finding('tracking.preconsent', 'Trackers firing before consent', status,
      trackers.length
        ? trackers.map((t) => `${t.name} (${t.count} req)`).join(', ') + (deniedPings ? `; ${deniedPings} Google request(s) carry consent-mode denied flags` : '')
        : 'No known trackers (Meta, GA4, Google Ads, TikTok, Klaviyo, Hotjar) fired before interaction.',
      trackers.length
        ? (strict
          ? 'Block all non-essential tags until opt-in: wire the CMP to Google Consent Mode v2 (default denied), gate Meta/TikTok/Klaviyo/Hotjar behind the marketing/statistics categories.'
          : consent.names.length
            ? 'A banner is shown but tags do not wait for it; either gate tags on consent or remove the banner to avoid a misleading consent experience.'
            : 'Acceptable in this market for most tags, but document it in the privacy policy and consider consent mode for future-proofing.')
        : ''));

    const needBanner = strict || ['DE', 'CA'].includes(ctx.market);
    out.push(finding('tracking.banner', 'Consent banner', consent.names.length ? STATUS.PASS : needBanner ? STATUS.FAIL : STATUS.INFO,
      consent.names.length ? `Detected: ${consent.names.join(', ')}` : 'No consent banner detected (OneTrust, Cookiebot, Usercentrics, Shopify, generic).',
      consent.names.length ? '' : needBanner ? 'Install a CMP (Usercentrics, Cookiebot, or Shopify Customer Privacy) with reject-all on the first layer.' : ''));
    return out;
  },
};
