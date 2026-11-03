// AI search readiness: structured data that answer engines and AI shopping
// agents read (Product, Organization, FAQPage JSON-LD), robots.txt rules for
// AI crawlers, /llms.txt, and basic title/meta description hygiene.

import { finding, STATUS } from '../lib/util.mjs';

export const AI_BOTS = ['GPTBot', 'OAI-SearchBot', 'ClaudeBot', 'PerplexityBot', 'Google-Extended'];

const typeOf = (n) => [].concat(n?.['@type'] || []).map(String);
const isType = (n, ...t) => typeOf(n).some((x) => t.includes(x));

/**
 * Minimal robots.txt evaluation: find the group for `agent` (or "*") and
 * report whether the site root is disallowed.
 * @returns {'allowed'|'blocked'|'partial'}
 */
export function robotsVerdict(robots, agent) {
  const groups = [];
  let cur = null;
  let lastWasAgent = false;
  for (const raw of String(robots || '').split(/\r?\n/)) {
    const line = raw.replace(/#.*/, '').trim();
    const m = /^([a-z-]+)\s*:\s*(.*)$/i.exec(line);
    if (!m) continue;
    const key = m[1].toLowerCase();
    const val = m[2].trim();
    if (key === 'user-agent') {
      if (!lastWasAgent) { cur = { agents: [], rules: [] }; groups.push(cur); }
      cur.agents.push(val.toLowerCase());
      lastWasAgent = true;
    } else {
      lastWasAgent = false;
      if (cur && (key === 'allow' || key === 'disallow')) cur.rules.push({ type: key, path: val });
    }
  }
  const a = agent.toLowerCase();
  const group = groups.find((g) => g.agents.includes(a)) || groups.find((g) => g.agents.includes('*'));
  if (!group) return 'allowed';
  const disallowRoot = group.rules.some((r) => r.type === 'disallow' && (r.path === '/' || r.path === '/*'));
  const allowRoot = group.rules.some((r) => r.type === 'allow' && (r.path === '/' || r.path === '/*'));
  if (disallowRoot && !allowRoot) return 'blocked';
  if (group.rules.some((r) => r.type === 'disallow' && r.path && r.path !== '/')) return 'partial';
  return 'allowed';
}

export default {
  id: 'ai-search',
  title: 'AI search readiness',
  offer: 'Teardown hook ("are you visible in ChatGPT?"); full schema fix in the Revenue Leak Audit',
  weight: 15,
  async run(ctx) {
    const out = [];
    const nodes = [ctx.home, ctx.pdp].filter((s) => s?.ok).flatMap((s) => s.jsonLd);

    // Product schema and its key fields.
    const product = (ctx.pdp?.jsonLd || []).find((n) => isType(n, 'Product', 'ProductGroup')) || nodes.find((n) => isType(n, 'Product', 'ProductGroup'));
    if (!product) {
      out.push(finding('ai.product', 'Product JSON-LD', ctx.pdp?.ok ? STATUS.FAIL : STATUS.INFO,
        ctx.pdp?.ok ? 'No Product schema on the product page.' : 'No PDP loaded; Product schema not checked.',
        ctx.pdp?.ok ? 'Add Product JSON-LD with name, brand, gtin, offers (price, priceCurrency, availability) and aggregateRating.' : ''));
    } else {
      const offers = [].concat(product.offers || product.hasVariant?.[0]?.offers || []);
      const o = offers[0] || {};
      const fields = {
        name: !!product.name,
        price: o.price != null || o.lowPrice != null || o.priceSpecification?.price != null,
        availability: !!o.availability,
        aggregateRating: !!product.aggregateRating,
        brand: !!product.brand,
        gtin: ['gtin', 'gtin8', 'gtin12', 'gtin13', 'gtin14', 'mpn'].some((k) => product[k] || product.hasVariant?.[0]?.[k]),
      };
      const missing = Object.entries(fields).filter(([, v]) => !v).map(([k]) => k);
      out.push(finding('ai.product', 'Product JSON-LD key fields', !missing.length ? STATUS.PASS : missing.length <= 2 ? STATUS.WARN : STATUS.FAIL,
        `Present: ${Object.keys(fields).filter((k) => fields[k]).join(', ') || 'none'}${missing.length ? `; missing: ${missing.join(', ')}` : ''}`,
        missing.length ? `Add ${missing.join(', ')} to the Product schema (review app or theme snippet); AI shopping results rely on them.` : ''));
    }

    const org = nodes.some((n) => isType(n, 'Organization', 'Corporation', 'OnlineStore', 'Store', 'LocalBusiness'));
    out.push(finding('ai.org', 'Organization schema', org ? STATUS.PASS : STATUS.WARN, org ? 'Organization schema found.' : 'No Organization schema.',
      org ? '' : 'Add Organization JSON-LD on the homepage (name, logo, url, sameAs social profiles, contactPoint).'));

    const faq = nodes.some((n) => isType(n, 'FAQPage'));
    out.push(finding('ai.faq', 'FAQPage schema', faq ? STATUS.PASS : STATUS.WARN, faq ? 'FAQPage schema found.' : 'No FAQPage schema on homepage or PDP.',
      faq ? '' : 'Add a short FAQ (shipping, returns, sizing) on PDPs with FAQPage JSON-LD; answer engines quote these directly.'));

    // robots.txt and llms.txt (fetched live; failures become "error"/"info").
    const origin = ctx.origin;
    const robots = await ctx.fetch(`${origin}/robots.txt`);
    if (!robots.ok) {
      out.push(finding('ai.robots', 'robots.txt AI crawler rules', STATUS.INFO, `robots.txt not readable (HTTP ${robots.status}${robots.error ? ', ' + robots.error : ''}); all bots allowed by default.`));
    } else {
      const verdicts = Object.fromEntries(AI_BOTS.map((b) => [b, robotsVerdict(robots.text, b)]));
      const blocked = AI_BOTS.filter((b) => verdicts[b] === 'blocked');
      // Blocking OAI-SearchBot/PerplexityBot removes the store from AI answers;
      // blocking GPTBot/Google-Extended (training only) is a business choice.
      const searchBlocked = blocked.filter((b) => ['OAI-SearchBot', 'PerplexityBot', 'ClaudeBot'].includes(b));
      out.push(finding('ai.robots', 'robots.txt AI crawler rules', searchBlocked.length ? STATUS.FAIL : blocked.length ? STATUS.WARN : STATUS.PASS,
        AI_BOTS.map((b) => `${b}: ${verdicts[b]}`).join(', '),
        blocked.length ? `Unblock ${blocked.join(', ')} unless blocking is a deliberate choice; search-type bots (OAI-SearchBot, PerplexityBot, ClaudeBot) must be allowed to appear in AI answers.` : ''));
    }

    const llms = await ctx.fetch(`${origin}/llms.txt`);
    const llmsOk = llms.ok && llms.text.trim().length > 0 && !/<html/i.test(llms.text.slice(0, 500));
    out.push(finding('ai.llms', '/llms.txt', llmsOk ? STATUS.PASS : STATUS.WARN,
      llmsOk ? `Present (${llms.text.length} chars)` : `Not found (HTTP ${llms.status})`,
      llmsOk ? '' : 'Publish /llms.txt summarising the brand, key collections, shipping/returns policy and contact links in Markdown.'));

    // Title and meta description length on each loaded page.
    for (const [tag, s] of [['Homepage', ctx.home], ['PDP', ctx.pdp]]) {
      if (!s?.ok) continue;
      const t = s.title.trim().length;
      const d = s.metaDescription.trim().length;
      const tStatus = t >= 30 && t <= 65 ? STATUS.PASS : t === 0 ? STATUS.FAIL : STATUS.WARN;
      const dStatus = d >= 70 && d <= 160 ? STATUS.PASS : d === 0 ? STATUS.FAIL : STATUS.WARN;
      out.push(finding(`ai.title.${tag}`, `${tag} title length`, tStatus, `${t} chars: "${s.title.trim().slice(0, 80)}"`,
        tStatus === STATUS.PASS ? '' : 'Keep titles 30-65 characters: product/category, key attribute, brand.'));
      out.push(finding(`ai.meta.${tag}`, `${tag} meta description`, dStatus, d ? `${d} chars` : 'Missing',
        dStatus === STATUS.PASS ? '' : 'Write a 70-160 character meta description with the value proposition and shipping/returns hook.'));
    }
    return out;
  },
};
