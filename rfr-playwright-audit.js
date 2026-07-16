const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const TARGET_URLS = ['https://www.rforrabbit.com'];
const REPORT_DIR = path.join(__dirname, 'audit-results');
const CHROMIUM_EXECUTABLE = process.env.PLAYWRIGHT_CHROMIUM_PATH || '/opt/pw-browsers/chromium';

async function auditUrl(browser, url) {
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });

  const axeSource = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
  await page.evaluate(axeSource);
  const results = await page.evaluate(async () => window.axe.run());

  await page.close();
  return results;
}

async function main() {
  fs.mkdirSync(REPORT_DIR, { recursive: true });

  const browser = await chromium.launch({ executablePath: CHROMIUM_EXECUTABLE });
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const summary = [];

  for (const url of TARGET_URLS) {
    console.log(`Auditing ${url} ...`);
    const results = await auditUrl(browser, url);

    const slug = new URL(url).hostname.replace(/\W+/g, '-');
    const reportPath = path.join(REPORT_DIR, `${slug}-${timestamp}.json`);
    fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));

    summary.push({
      url,
      reportPath,
      violations: results.violations.length,
      incomplete: results.incomplete.length,
      passes: results.passes.length,
    });

    console.log(
      `  violations: ${results.violations.length}, incomplete: ${results.incomplete.length}, passes: ${results.passes.length}`
    );
    for (const violation of results.violations) {
      console.log(`  [${violation.impact}] ${violation.id}: ${violation.help} (${violation.nodes.length} nodes)`);
    }
  }

  await browser.close();

  const summaryPath = path.join(REPORT_DIR, `summary-${timestamp}.json`);
  fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));
  console.log(`\nSummary written to ${summaryPath}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
