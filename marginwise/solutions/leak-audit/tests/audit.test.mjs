// End-to-end and unit tests. The fixture sites are served locally and all
// external requests (trackers, CDNs) are stubbed, so the suite runs offline.

import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { startServer } from './server.mjs';
import { runAudit, runChecks, score } from '../lib/run.mjs';
import { renderHtml } from '../lib/report.mjs';
import { robotsVerdict } from '../checks/ai-search.mjs';
import { siteOf } from '../lib/util.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const fx = (name) => path.join(here, 'fixtures', name);
const byId = (report) => Object.fromEntries(report.checks.flatMap((c) => c.findings).map((f) => [f.id, f]));

let au, de, auReport, deReport;

before(async () => {
  au = await startServer(fx('au'));
  de = await startServer(fx('de'));
  // AU: no --pdp, so the product page must be discovered from the homepage.
  auReport = await runAudit(au.url + '/', { market: 'AU', stubExternal: true, settleMs: 300 });
  deReport = await runAudit(de.url + '/', { market: 'DE', pdp: de.url + '/produkte/wandersocke', stubExternal: true, settleMs: 300 });
});

after(async () => {
  await au?.close();
  await de?.close();
});

test('AU: discovers PDP and detects Shopify', () => {
  assert.equal(auReport.pdp.via, 'first product link');
  assert.ok(auReport.pdp.loaded);
  assert.equal(auReport.platform, 'Shopify');
});

test('AU: card surcharge text fails with RBA note', () => {
  const f = byId(auReport)['au.surcharge'];
  assert.equal(f.status, 'fail');
  assert.match(f.evidence, /1\.5% card surcharge/);
  assert.match(f.fix, /1 Oct 2026/);
});

test('AU: missing reviews fail, price/ATC/BNPL/shipping pass', () => {
  const f = byId(auReport);
  assert.equal(f['pdp.reviews'].status, 'fail');
  assert.equal(f['pdp.price'].status, 'pass');
  assert.equal(f['pdp.atc'].status, 'pass');
  assert.equal(f['pdp.bnpl'].status, 'pass');
  assert.equal(f['pdp.shipping'].status, 'pass');
  assert.equal(f['pdp.delivery'].status, 'pass');
  assert.equal(f['au.afterpay'].status, 'pass');
});

test('AU: Meta pixel fires before consent while a banner is shown', () => {
  const f = byId(auReport);
  assert.match(f['tracking.preconsent'].evidence, /Meta pixel/);
  assert.equal(f['tracking.preconsent'].status, 'warn');
  assert.equal(f['tracking.banner'].status, 'pass');
});

test('AU: AI readiness flags GPTBot block, missing llms.txt and Product fields', () => {
  const f = byId(auReport);
  assert.equal(f['ai.robots'].status, 'warn');
  assert.match(f['ai.robots'].evidence, /GPTBot: blocked/);
  assert.equal(f['ai.llms'].status, 'warn');
  assert.match(f['ai.product'].evidence, /missing: .*aggregateRating/);
  assert.equal(f['ai.org'].status, 'pass');
});

test('AU: speed metrics are measured', () => {
  const f = byId(auReport);
  assert.ok(['pass', 'warn', 'fail'].includes(f['speed.Homepage.lcp'].status));
  assert.equal(f['speed.Homepage.blocking'].status, 'warn'); // sync theme.js in <head>
});

test('DE: missing Impressum fails; climate, strike-through and withdrawal warn', () => {
  const f = byId(deReport);
  assert.equal(f['de.impressum'].status, 'fail');
  assert.equal(f['de.climate'].status, 'warn');
  assert.equal(f['de.strike'].status, 'warn');
  assert.equal(f['de.widerruf'].status, 'warn');
  assert.equal(f['de.invoice'].status, 'pass');
  assert.equal(f['de.kuendigung'].status, 'info');
});

test('DE: GA4 before consent is a hard fail', () => {
  const f = byId(deReport);
  assert.equal(f['tracking.preconsent'].status, 'fail');
  assert.match(f['tracking.preconsent'].evidence, /GA4/);
});

test('DE: reviews with rating found on PDP', () => {
  assert.equal(byId(deReport)['pdp.reviews'].status, 'pass');
});

test('accessibility: axe flags the DE image without alt text', () => {
  const f = byId(deReport)['a11y.violations'];
  assert.equal(f.status, 'fail'); // image-alt is a critical rule
  assert.match(f.evidence, /image-alt/);
  assert.equal(byId(auReport)['a11y.violations'].status, 'pass');
});

test('score is 0-100 and HTML report is self-contained', () => {
  for (const r of [auReport, deReport]) {
    assert.ok(r.score >= 0 && r.score <= 100);
    assert.equal(r.top.length, 5);
  }
  const html = renderHtml(auReport);
  assert.match(html, /#1F2A44/);
  assert.match(html, /out of 100/);
  assert.doesNotMatch(html, /<script|<link[^>]+stylesheet|src="http/i);
});

test('a throwing check becomes an error finding and does not abort', async () => {
  const boom = { id: 'boom', title: 'Boom', weight: 10, run() { throw new Error('kaboom'); } };
  const ok = { id: 'ok', title: 'OK', weight: 10, run: () => [{ id: 'ok.1', label: 'ok', status: 'pass', evidence: '', fix: '' }] };
  const results = await runChecks({ market: 'US' }, [boom, ok]);
  assert.equal(results.length, 2);
  assert.equal(results[0].findings[0].status, 'error');
  assert.match(results[0].findings[0].evidence, /kaboom/);
  assert.equal(score(results, 'US'), 100); // errors are not scored
});

test('robotsVerdict and siteOf helpers', () => {
  const robots = 'User-agent: GPTBot\nDisallow: /\n\nUser-agent: *\nDisallow: /cart\n';
  assert.equal(robotsVerdict(robots, 'GPTBot'), 'blocked');
  assert.equal(robotsVerdict(robots, 'ClaudeBot'), 'partial');
  assert.equal(robotsVerdict('', 'PerplexityBot'), 'allowed');
  assert.equal(siteOf('shop.example.com.au'), 'example.com.au');
  assert.equal(siteOf('www.allbirds.com'), 'allbirds.com');
});

test('US market doubles accessibility weight', () => {
  const mk = () => [
    { id: 'accessibility', weight: 15, findings: [{ status: 'fail' }] },
    { id: 'speed', weight: 15, findings: [{ status: 'pass' }] },
  ];
  assert.equal(score(mk(), 'AU'), 50);
  assert.equal(score(mk(), 'US'), 33);
});
