// Renders the audit result as a self-contained HTML page (inline CSS, no
// external fonts, scripts or images) in Marginwise colours.

import { esc } from './util.mjs';

const C = { navy: '#1F2A44', green: '#2E9E7E', red: '#C0533A', amber: '#C98A2B', grey: '#6B7280' };
const PILL = { pass: C.green, warn: C.amber, fail: C.red, info: C.grey, error: C.grey };

function scoreColor(s) {
  return s >= 80 ? C.green : s >= 55 ? C.amber : C.red;
}

function pill(status) {
  return `<span class="pill" style="background:${PILL[status] || C.grey}">${esc(status.toUpperCase())}</span>`;
}

export function renderHtml(r) {
  const top = r.top.length
    ? r.top.map((f) => `<li>${pill(f.status)} <strong>${esc(f.label)}</strong> <span class="muted">(${esc(f.check)})</span><div class="ev">${esc(f.evidence)}</div>${f.fix ? `<div class="fix"><b>Fix:</b> ${esc(f.fix)}</div>` : ''}</li>`).join('')
    : '<li>No failures or warnings.</li>';

  const sections = r.checks.map((c) => `
    <section class="card">
      <div class="card-h">
        <h2>${esc(c.title)}</h2>
        <span class="cscore">${c.score == null ? 'not scored' : `${c.score}/100`}</span>
      </div>
      <p class="offer">Marginwise offer: ${esc(c.offer || '')}</p>
      <table>
        <thead><tr><th>Status</th><th>Check</th><th>Evidence</th><th>Recommended fix</th></tr></thead>
        <tbody>
          ${c.findings.map((f) => `<tr><td>${pill(f.status)}</td><td>${esc(f.label)}</td><td class="ev">${esc(f.evidence)}</td><td>${esc(f.fix) || '<span class="muted">-</span>'}</td></tr>`).join('')}
        </tbody>
      </table>
    </section>`).join('');

  const k = r.counts;
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Revenue Leak Audit - ${esc(new URL(r.finalUrl || r.url).hostname)}</title>
<style>
  :root { --navy:${C.navy}; --green:${C.green}; --red:${C.red}; }
  * { box-sizing: border-box; }
  body { margin:0; background:#F4F6F9; color:#1B1F2A; font:15px/1.5 -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
  header { background:var(--navy); color:#fff; padding:28px 16px; }
  .wrap { max-width:1100px; margin:0 auto; padding:0 16px; }
  header .wrap { display:flex; gap:24px; align-items:center; flex-wrap:wrap; padding:0; }
  .brand { font-size:13px; letter-spacing:.12em; text-transform:uppercase; opacity:.8; }
  h1 { margin:4px 0 6px; font-size:24px; }
  .meta { font-size:13px; opacity:.85; overflow-wrap:anywhere; }
  .score { margin-left:auto; text-align:center; background:#fff; color:var(--navy); border-radius:12px; padding:12px 22px; }
  .score b { display:block; font-size:44px; line-height:1; }
  .counts { display:flex; gap:8px; flex-wrap:wrap; margin:18px 0; }
  .counts span { background:#fff; border-radius:8px; padding:6px 12px; font-size:13px; border:1px solid #E2E6EC; }
  .card { background:#fff; border:1px solid #E2E6EC; border-radius:12px; padding:18px; margin:16px 0; overflow-x:auto; }
  .card-h { display:flex; justify-content:space-between; align-items:baseline; gap:12px; }
  h2 { margin:0; font-size:18px; color:var(--navy); }
  .cscore { font-weight:600; color:var(--navy); white-space:nowrap; }
  .offer { margin:4px 0 12px; font-size:13px; color:${C.grey}; }
  table { width:100%; border-collapse:collapse; font-size:14px; }
  th { text-align:left; font-size:12px; text-transform:uppercase; letter-spacing:.05em; color:${C.grey}; border-bottom:2px solid #E2E6EC; padding:6px 8px; }
  td { vertical-align:top; border-bottom:1px solid #EEF1F5; padding:8px; }
  td:first-child { width:70px; }
  .pill { display:inline-block; color:#fff; font-size:11px; font-weight:700; border-radius:999px; padding:2px 9px; letter-spacing:.04em; }
  .ev { color:#3A4252; word-break:break-word; }
  .muted { color:${C.grey}; }
  .top ol { margin:0; padding-left:20px; }
  .top li { margin:10px 0; }
  .fix { margin-top:2px; }
  footer { font-size:12px; color:${C.grey}; padding:24px 16px 40px; }
  @media (max-width: 640px) {
    thead { display:none; }
    tr, td { display:block; width:100% !important; }
    tr { border-bottom:1px solid #E2E6EC; padding:8px 0; }
    td { border:0; padding:3px 0; }
    .score { margin-left:0; }
  }
</style>
</head>
<body>
<header>
  <div class="wrap">
    <div>
      <div class="brand">Marginwise / Revenue Leak Audit</div>
      <h1>${esc(new URL(r.finalUrl || r.url).hostname)}</h1>
      <div class="meta">Market ${esc(r.market)} | Platform ${esc(r.platform || 'unknown')} | ${esc(r.device)}<br>
      Home: ${esc(r.finalUrl || r.url)}<br>
      PDP: ${r.pdp ? `${esc(r.pdp.url)} (${esc(r.pdp.via)}${r.pdp.loaded ? '' : ', failed to load'})` : 'none found'}<br>
      Run: ${esc(r.startedAt)}</div>
    </div>
    <div class="score"><b style="color:${scoreColor(r.score)}">${r.score}</b>out of 100</div>
  </div>
</header>
<main class="wrap">
  <div class="counts">
    <span style="color:${C.green}">${k.pass} pass</span>
    <span style="color:${C.amber}">${k.warn} warn</span>
    <span style="color:${C.red}">${k.fail} fail</span>
    <span>${k.info} info</span>${k.error ? `<span>${k.error} error</span>` : ''}
  </div>
  <section class="card top">
    <h2>Top findings</h2>
    <ol>${top}</ol>
  </section>
  ${sections}
</main>
<footer class="wrap">
  Automated heuristic checks on a single mobile page load (no consent interaction). Text detection can miss content rendered in images,
  iframes or after interaction, and can match unrelated wording. Compliance items are indicators for review, not legal advice.
</footer>
</body>
</html>`;
}
