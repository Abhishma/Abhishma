// Browser collector: loads a URL in an emulated iPhone 13 (Chromium) and
// returns a plain-data "snapshot" that the checks analyse. All browser work
// lives here so that checks stay small, synchronous-ish and easy to test.
//
// Every step is wrapped in try/catch: a failed sub-step leaves a field empty
// and records a note in snapshot.errors, it never aborts the snapshot.

import { createRequire } from 'node:module';
import { readFileSync, existsSync } from 'node:fs';
import { chromium, devices } from 'playwright-core';
import { CMPS } from './trackers.mjs';
import { siteOf, parseUrl } from './util.mjs';

const require = createRequire(import.meta.url);
const AXE_SOURCE = readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');

// Hosts that belong to the store platform itself; scripts from these are not
// counted as "third-party" because the merchant cannot remove them.
const PLATFORM_HOSTS = /(^|\.)(cdn\.shopify\.com|shopifycdn\.net|shopify\.com|cdn\.salla\.network|salla\.sa|zid\.store|zidcdn\.com|bigcommerce\.com|demandware\.static|shopware\.store)$/i;

const FALLBACK_CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';

const isLoopback = (u) => /^(localhost|127\.\d+\.\d+\.\d+|\[::1\])$/i.test(parseUrl(u)?.hostname || '');

/**
 * Launch Chromium, honouring HTTPS_PROXY and falling back to the known binary
 * path. Loopback targets (the test fixtures) skip the proxy entirely, because
 * Playwright forces loopback traffic through a configured proxy.
 */
export async function launchBrowser(targetUrl = '') {
  const opts = { headless: true };
  const proxy = process.env.HTTPS_PROXY || process.env.https_proxy;
  if (proxy && !isLoopback(targetUrl)) opts.proxy = { server: proxy, bypass: 'localhost,127.0.0.1,::1' };
  if (process.env.LEAK_AUDIT_CHROME) opts.executablePath = process.env.LEAK_AUDIT_CHROME;
  try {
    return await chromium.launch(opts);
  } catch (err) {
    if (!opts.executablePath && existsSync(FALLBACK_CHROME)) {
      return chromium.launch({ ...opts, executablePath: FALLBACK_CHROME });
    }
    throw err;
  }
}

/** Create a fresh mobile context (clean cache and cookies per page). */
export async function newMobileContext(browser) {
  return browser.newContext({ ...devices['iPhone 13'], bypassCSP: true, locale: 'en-US' });
}

/**
 * Fetch a text resource (robots.txt, llms.txt, products.json) through the
 * browser's network stack so proxy settings apply. Never throws.
 */
export async function fetchText(context, url, timeout = 10000) {
  try {
    const res = await context.request.get(url, { timeout, maxRedirects: 5, failOnStatusCode: false });
    return { url, status: res.status(), ok: res.ok(), text: await res.text() };
  } catch (err) {
    return { url, status: 0, ok: false, text: '', error: String(err.message || err).split('\n')[0] };
  }
}

/**
 * Load `url` and capture everything the checks need.
 * @param {import('playwright-core').Browser} browser
 * @param {string} url
 * @param {object} opts
 * @param {object} opts.probes     element probes declared by checks ({key: {selector, text}})
 * @param {number} [opts.settleMs] extra wait after load so late trackers fire
 * @param {boolean} [opts.stubExternal] answer non-local requests with empty 200s (tests/offline)
 * @param {boolean} [opts.axe]     run axe-core (default true)
 */
export async function snapshotPage(browser, url, opts = {}) {
  const { probes = {}, settleMs = 2500, stubExternal = false, axe = true, timeout = 45000 } = opts;
  const snap = {
    url, finalUrl: url, ok: false, status: 0, headers: {}, errors: [],
    title: '', metaDescription: '', lang: '', dir: '', hreflangs: [], links: [], scripts: [],
    jsonLd: [], visibleText: '', signalText: '', html: '', requests: [], viewport: null,
    metrics: { lcpMs: null, transferBytes: 0, requestCount: 0, thirdPartyScripts: [], renderBlockingScripts: [] },
    axe: null, probes: {}, strike: [], cmpDom: [], genericBanner: null, globals: {},
  };
  const note = (step, err) => snap.errors.push(`${step}: ${String(err?.message || err).split('\n')[0]}`);

  const context = await newMobileContext(browser);
  const page = await context.newPage();
  snap.viewport = page.viewportSize();
  const started = Date.now();

  try {
    // Optional stub for tests: keeps the run offline but still records the
    // request (the 'request' event fires before the route handler).
    if (stubExternal) {
      await page.route('**/*', (route) => {
        const host = parseUrl(route.request().url())?.hostname || '';
        if (host === '127.0.0.1' || host === 'localhost') return route.continue();
        return route.fulfill({ status: 200, contentType: 'text/javascript', body: '' });
      });
    }

    // LCP observer must be registered before any page script runs.
    await page.addInitScript(() => {
      window.__mwLcp = null;
      try {
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const last = entries[entries.length - 1];
          if (last) window.__mwLcp = last.startTime;
        }).observe({ type: 'largest-contentful-paint', buffered: true });
      } catch { /* unsupported */ }
    });

    // Record every request with its timing relative to navigation start.
    page.on('request', (req) => {
      snap.requests.push({ url: req.url(), type: req.resourceType(), t: Date.now() - started });
    });

    // Transfer size via CDP (encodedDataLength counts bytes on the wire).
    try {
      const cdp = await context.newCDPSession(page);
      await cdp.send('Network.enable');
      cdp.on('Network.loadingFinished', (e) => { snap.metrics.transferBytes += e.encodedDataLength || 0; });
    } catch (err) { note('cdp', err); }

    const resp = await page.goto(url, { waitUntil: 'domcontentloaded', timeout });
    snap.status = resp?.status() ?? 0;
    snap.headers = resp ? await resp.allHeaders().catch(() => ({})) : {};
    snap.finalUrl = page.url();
    snap.ok = snap.status > 0 && snap.status < 400;
    if (!snap.ok) note('navigation', `HTTP ${snap.status}${snap.status === 403 || snap.status === 405 ? ' (blocked by the site or a proxy)' : ''}`);
    await page.waitForLoadState('load', { timeout: 20000 }).catch((e) => note('load', e));
    await page.waitForLoadState('networkidle', { timeout: 6000 }).catch(() => {});
    await page.waitForTimeout(settleMs);
  } catch (err) {
    note('navigation', err);
    await context.close().catch(() => {});
    return snap;
  }

  // ---- DOM extraction (one evaluate keeps it fast) ----
  try {
    const dom = await page.evaluate(({ probes, cmpSelectors }) => {
      const visible = (el) => {
        if (!el || !el.getBoundingClientRect) return false;
        const r = el.getBoundingClientRect();
        if (r.width < 1 || r.height < 1) return false;
        const cs = getComputedStyle(el);
        return cs.visibility !== 'hidden' && cs.display !== 'none' && Number(cs.opacity) > 0.05;
      };
      const pos = (el) => {
        const r = el.getBoundingClientRect();
        return { top: Math.round(r.top + scrollY), bottom: Math.round(r.bottom + scrollY), left: Math.round(r.left) };
      };
      const clip = (s, n = 120) => String(s || '').replace(/\s+/g, ' ').trim().slice(0, n);

      // Probe runner: selector matches plus text-node regex matches.
      const runProbe = (spec) => {
        const out = [];
        const seen = new Set();
        const push = (el, how) => {
          if (!el || seen.has(el) || !visible(el) || out.length >= 15) return;
          seen.add(el);
          out.push({ ...pos(el), text: clip(el.innerText || el.getAttribute('aria-label') || el.getAttribute('alt') || el.tagName), how });
        };
        if (spec.selector) {
          try { document.querySelectorAll(spec.selector).forEach((el) => push(el, 'selector')); } catch { /* bad selector */ }
        }
        if (spec.text) {
          const re = new RegExp(spec.text, 'i');
          const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
          let n;
          while ((n = walker.nextNode()) && out.length < 15) {
            const t = n.nodeValue;
            if (t && t.length < 200 && re.test(t)) {
              const p = n.parentElement;
              if (p && !['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE'].includes(p.tagName)) push(p, 'text');
            }
          }
        }
        out.sort((a, b) => a.top - b.top);
        return out;
      };
      const probeResults = {};
      for (const [k, spec] of Object.entries(probes)) probeResults[k] = runProbe(spec);

      // Searchable "signal" text: visible text plus alt/aria/title attributes,
      // so logo-only payment badges (Apple Pay, mada, Afterpay) still count.
      const attrText = [];
      document.querySelectorAll('img[alt], [aria-label], svg title, [title]').forEach((el) => {
        const v = el.tagName.toLowerCase() === 'title' ? el.textContent : (el.getAttribute('alt') || el.getAttribute('aria-label') || el.getAttribute('title'));
        if (v && v.length < 120) attrText.push(v);
      });

      // Strike-through prices (s/del/strike or CSS line-through) with digits.
      const strike = [];
      document.querySelectorAll('s, del, strike, [class*="compare" i], [class*="was-price" i], [class*="strike" i], [class*="price" i]').forEach((el) => {
        if (strike.length >= 10 || !visible(el)) return;
        const tag = el.tagName.toLowerCase();
        const lt = getComputedStyle(el).textDecorationLine.includes('line-through');
        const txt = clip(el.innerText, 40);
        if ((['s', 'del', 'strike'].includes(tag) || lt) && /\d/.test(txt)) strike.push(txt);
      });

      // Generic consent banner: an accept-style button inside a fixed/sticky
      // container or dialog that mentions cookies / consent.
      let genericBanner = null;
      const acceptRe = /^(accept|accept all|allow|allow all|agree|i agree|ok|got it|alle akzeptieren|akzeptieren|zustimmen|accepter|tout accepter|قبول|موافق)/i;
      const cookieRe = /cookie|consent|datenschutz|privacy|tracking|ملفات تعريف/i;
      for (const b of document.querySelectorAll('button, a, [role="button"], input[type="button"], input[type="submit"]')) {
        const label = clip(b.innerText || b.value || b.getAttribute('aria-label'), 40);
        if (!acceptRe.test(label) || !visible(b)) continue;
        let el = b;
        for (let i = 0; i < 8 && el; i++, el = el.parentElement) {
          const cs = getComputedStyle(el);
          if ((cs.position === 'fixed' || cs.position === 'sticky' || el.getAttribute('role') === 'dialog' || el.tagName === 'DIALOG') && cookieRe.test(el.innerText || '')) {
            genericBanner = clip(el.innerText, 160);
            break;
          }
        }
        if (genericBanner) break;
      }

      const cmpDom = cmpSelectors.filter(([, sel]) => { try { return !!document.querySelector(sel); } catch { return false; } }).map(([n]) => n);

      // JSON-LD blocks (raw text; parsed in Node so errors are recorded).
      const jsonLd = [...document.querySelectorAll('script[type="application/ld+json"]')].map((s) => s.textContent);

      const headScripts = [...document.querySelectorAll('head script[src]')]
        .filter((s) => !s.async && !s.defer && s.type !== 'module')
        .map((s) => s.src);
      const blockingRes = performance.getEntriesByType('resource')
        .filter((e) => e.renderBlockingStatus === 'blocking' && e.initiatorType === 'script')
        .map((e) => e.name);

      return {
        title: document.title || '',
        metaDescription: document.querySelector('meta[name="description" i]')?.getAttribute('content') || '',
        lang: document.documentElement.getAttribute('lang') || '',
        dir: document.documentElement.getAttribute('dir') || document.body?.getAttribute('dir') || '',
        hreflangs: [...document.querySelectorAll('link[rel="alternate"][hreflang]')].map((l) => ({ lang: l.getAttribute('hreflang'), href: l.href })),
        links: [...document.querySelectorAll('a[href]')].slice(0, 1500).map((a) => ({ href: a.href, text: clip(a.innerText || a.getAttribute('aria-label') || a.title, 80) })),
        scripts: [...document.querySelectorAll('script[src]')].map((s) => ({ src: s.src, async: s.async, defer: s.defer, module: s.type === 'module' })),
        jsonLd,
        visibleText: document.body ? document.body.innerText : '',
        attrText: attrText.join('\n'),
        html: document.documentElement.outerHTML.slice(0, 3_000_000),
        probes: probeResults,
        strike,
        genericBanner,
        cmpDom,
        renderBlocking: [...new Set([...headScripts, ...blockingRes])],
        lcp: window.__mwLcp,
        globals: {
          Shopify: !!window.Shopify,
          BCData: !!window.BCData,
          salla: !!(window.salla || window.Salla),
          zid: !!(window.zid || window.Zid),
          woocommerce: !!(window.wc || window.woocommerce_params || window.wc_add_to_cart_params),
          Mage: !!(window.require && window.require.s && window.require.s.contexts && window.require.s.contexts._ && window.require.s.contexts._.config && window.require.s.contexts._.config.baseUrl && /static\/version|\/static\//.test(window.require.s.contexts._.config.baseUrl)),
        },
      };
    }, { probes, cmpSelectors: CMPS.map((c) => [c.name, c.dom]) });

    Object.assign(snap, {
      title: dom.title, metaDescription: dom.metaDescription, lang: dom.lang, dir: dom.dir,
      hreflangs: dom.hreflangs, links: dom.links, scripts: dom.scripts, visibleText: dom.visibleText,
      signalText: dom.visibleText + '\n' + dom.attrText, html: dom.html, probes: dom.probes,
      strike: dom.strike, genericBanner: dom.genericBanner, cmpDom: dom.cmpDom, globals: dom.globals,
    });
    snap.metrics.lcpMs = typeof dom.lcp === 'number' ? Math.round(dom.lcp) : null;
    snap.metrics.renderBlockingScripts = dom.renderBlocking;

    // Parse JSON-LD in Node; flatten arrays and @graph.
    for (const raw of dom.jsonLd) {
      try {
        const data = JSON.parse(raw);
        const stack = Array.isArray(data) ? [...data] : [data];
        while (stack.length) {
          const node = stack.shift();
          if (!node || typeof node !== 'object') continue;
          if (Array.isArray(node['@graph'])) stack.push(...node['@graph']);
          snap.jsonLd.push(node);
        }
      } catch (err) { note('json-ld', err); }
    }
  } catch (err) { note('dom', err); }

  // ---- Request-derived metrics ----
  try {
    const pageSite = siteOf(parseUrl(snap.finalUrl)?.hostname);
    snap.metrics.requestCount = snap.requests.length;
    for (const r of snap.requests) {
      const host = parseUrl(r.url)?.hostname || '';
      r.thirdParty = !!host && siteOf(host) !== pageSite && !PLATFORM_HOSTS.test(host);
    }
    snap.metrics.thirdPartyScripts = [...new Set(snap.requests.filter((r) => r.type === 'script' && r.thirdParty).map((r) => r.url))];
  } catch (err) { note('metrics', err); }

  // ---- Accessibility (axe-core, WCAG 2.1 A/AA) ----
  if (axe) {
    try {
      // page.evaluate runs via CDP, so a strict CSP cannot block the injection.
      await page.evaluate(AXE_SOURCE);
      snap.axe = await page.evaluate(async () => {
        const r = await window.axe.run(document, {
          runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'] },
          resultTypes: ['violations'],
        });
        return {
          violations: r.violations.map((v) => ({
            id: v.id, impact: v.impact, help: v.help, helpUrl: v.helpUrl, nodes: v.nodes.length,
            sample: v.nodes[0]?.target?.join(' ') || '',
          })),
        };
      });
    } catch (err) { snap.axe = { error: String(err.message || err).split('\n')[0] }; }
  }

  await context.close().catch(() => {});
  return snap;
}
