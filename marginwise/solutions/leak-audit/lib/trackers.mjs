// Known tracker, consent-platform and overlay signatures, matched against
// network request URLs. Kept in one place so checks share the same lists.

export const TRACKERS = [
  { name: 'Meta pixel', re: /connect\.facebook\.net\/.*fbevents|facebook\.com\/tr[/?]/i },
  { name: 'GA4 / gtag', re: /googletagmanager\.com\/gtag\/js\?id=G-|google-analytics\.com\/(g\/collect|analytics\.js)|analytics\.google\.com\/g\/collect/i },
  { name: 'Google Ads', re: /googletagmanager\.com\/gtag\/js\?id=AW-|googleadservices\.com|googleads\.g\.doubleclick\.net|google\.com\/pagead|google\.[a-z.]+\/ads\/ga-audiences/i },
  { name: 'Google Tag Manager', re: /googletagmanager\.com\/gtm\.js/i },
  { name: 'TikTok pixel', re: /analytics\.tiktok\.com/i },
  { name: 'Klaviyo', re: /(static|a|fast|static-tracking)\.klaviyo\.com/i },
  { name: 'Hotjar', re: /(static|script|vars)\.hotjar\.(com|io)|hotjar\.com\/c\/hotjar/i },
];

// Consent management platforms. `dom` selectors are checked in the page,
// `net` patterns against request URLs.
export const CMPS = [
  { name: 'OneTrust', dom: '#onetrust-banner-sdk, #onetrust-consent-sdk', net: /cdn\.cookielaw\.org|optanon|onetrust/i },
  { name: 'Cookiebot', dom: '#CybotCookiebotDialog', net: /consent\.cookiebot\.(com|eu)/i },
  { name: 'Usercentrics', dom: '#usercentrics-root, #usercentrics-cmp-ui, #uc-banner', net: /usercentrics\.eu|app\.usercentrics/i },
  { name: 'Shopify consent', dom: '#shopify-pc__banner, .shopify-pc__banner__dialog', net: /consent-tracking-api|shopify-privacy-banner/i },
];

export const OVERLAYS = [
  { name: 'accessiBe', re: /acsbapp\.com|accessibe\.com/i },
  { name: 'UserWay', re: /userway\.org/i },
  { name: 'AudioEye', re: /audioeye\.com/i },
  { name: 'EqualWeb', re: /equalweb\.com|nagich\.co/i },
];

/** Group request URLs by tracker name. Returns [{name, count, sample}]. */
export function matchTrackers(requests) {
  const hits = new Map();
  for (const r of requests || []) {
    for (const t of TRACKERS) {
      if (t.re.test(r.url)) {
        const h = hits.get(t.name) || { name: t.name, count: 0, sample: r.url };
        h.count += 1;
        hits.set(t.name, h);
      }
    }
  }
  return [...hits.values()];
}
