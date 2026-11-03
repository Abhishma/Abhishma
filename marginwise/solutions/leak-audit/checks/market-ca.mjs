// Canada: French-language storefront (Quebec Charter of the French Language,
// strengthened by Bill 96) and consent before tracking (Quebec Law 25).

import { finding, STATUS, allLinks, parseUrl } from '../lib/util.mjs';

export default {
  id: 'market-ca',
  title: 'Market rules: Canada',
  markets: ['CA'],
  offer: 'Revenue Leak Audit (market readiness)',
  weight: 15,
  run(ctx) {
    const snaps = [ctx.home, ctx.pdp].filter((s) => s?.ok);
    const hreflang = snaps.flatMap((s) => s.hreflangs).find((h) => /^fr(-ca)?$/i.test(h.lang || ''));
    const frPath = allLinks(ctx).find((l) => /^\/fr(-ca)?\//i.test((parseUrl(l.href)?.pathname || '') + '/'));
    const switcher = allLinks(ctx).find((l) => /^(fran[cç]ais|fr)$/i.test(l.text.trim()));
    const langFr = snaps.some((s) => /^fr/i.test(s.lang));
    const fr = hreflang || frPath || switcher || langFr;
    const evidence = hreflang ? `hreflang ${hreflang.lang} -> ${hreflang.href}` : frPath ? `French link ${frPath.href}` : switcher ? `Switcher "${switcher.text}"` : langFr ? 'Page served in French' : 'No /fr path, fr-CA hreflang or language switcher found.';
    const out = [finding('ca.french', 'French locale available', fr ? STATUS.PASS : STATUS.WARN, evidence,
      fr ? '' : 'Add a French (fr-CA) storefront via Shopify Markets/Translate & Adapt or Weglot, with hreflang tags; required to sell to Quebec consumers.')];

    // Severity is scored in the Tracking check; repeated here for visibility only.
    const t = ctx.preConsentTrackers || [];
    out.push(finding('ca.consent', 'Consent before tracking (Law 25)', STATUS.INFO,
      t.length ? `Trackers fire before consent: ${t.map((x) => x.name).join(', ')} (scored as fail in Tracking and consent).` : 'No trackers before consent.',
      t.length ? 'Gate tags behind opt-in for Quebec visitors; see the Tracking and consent fix.' : ''));
    return out;
  },
};
