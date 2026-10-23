#!/usr/bin/env node
// Marginwise Revenue Leak Audit CLI.
// Usage: node audit.mjs <url> [--market AU|NZ|US|CA|DE|SA] [--pdp <product-url>] [--out dir]

import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { parseArgs } from 'node:util';
import { runAudit, MARKETS } from './lib/run.mjs';
import { renderHtml } from './lib/report.mjs';

const USAGE = 'Usage: node audit.mjs <url> [--market AU|NZ|US|CA|DE|SA] [--pdp <product-url>] [--out dir] [--quiet]';

async function main() {
  let args;
  try {
    args = parseArgs({
      allowPositionals: true,
      options: {
        market: { type: 'string', default: 'US' },
        pdp: { type: 'string' },
        out: { type: 'string', default: 'out' },
        quiet: { type: 'boolean', default: false },
        help: { type: 'boolean', short: 'h' },
      },
    });
  } catch (err) {
    console.error(err.message + '\n' + USAGE);
    process.exit(2);
  }
  const { values, positionals } = args;
  if (values.help || !positionals[0]) { console.log(USAGE); process.exit(values.help ? 0 : 2); }

  let url = positionals[0];
  if (!/^https?:\/\//i.test(url)) url = 'https://' + url;
  const market = values.market.toUpperCase();
  if (!MARKETS.includes(market)) { console.error(`Unknown market "${values.market}". ${USAGE}`); process.exit(2); }

  const log = values.quiet ? () => {} : (m) => console.error(m);
  const report = await runAudit(url, { market, pdp: values.pdp, log });

  const outDir = path.resolve(values.out);
  await mkdir(outDir, { recursive: true });
  await writeFile(path.join(outDir, 'report.json'), JSON.stringify(report, null, 2));
  await writeFile(path.join(outDir, 'report.html'), renderHtml(report));

  console.log(`\nScore: ${report.score}/100  (${report.counts.pass} pass, ${report.counts.warn} warn, ${report.counts.fail} fail)`);
  report.top.forEach((f, i) => console.log(`${i + 1}. [${f.status.toUpperCase()}] ${f.label}: ${f.evidence}`));
  console.log(`\nWrote ${path.join(outDir, 'report.json')} and report.html`);
}

main().catch((err) => {
  console.error('Audit failed:', err?.message || err);
  process.exit(1);
});
