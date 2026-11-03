// Check registry. Order matters a little: platform runs first and the
// tracking/PDP checks share results (ctx.preConsentTrackers, ctx.bnpl) with
// the market modules that follow.
//
// To add a check: create checks/<name>.mjs exporting a default object
//   { id, title, offer, weight, markets?, probes?, run(ctx) => finding[] }
// and add it to this list. `markets` limits it to certain --market values;
// `probes` asks the collector to locate elements on the home/pdp pages.

import platform from './platform.mjs';
import speed from './speed.mjs';
import accessibility from './accessibility.mjs';
import tracking from './tracking.mjs';
import productPage from './product-page.mjs';
import marketAU from './market-au.mjs';
import marketUS from './market-us.mjs';
import marketCA from './market-ca.mjs';
import marketDE from './market-de.mjs';
import marketSA from './market-sa.mjs';
import aiSearch from './ai-search.mjs';

export const CHECKS = [platform, speed, accessibility, tracking, productPage, marketAU, marketUS, marketCA, marketDE, marketSA, aiSearch];

/** Merge probe specs declared by checks into {home: {...}, pdp: {...}}. */
export function collectProbes(checks = CHECKS) {
  const merged = { home: {}, pdp: {} };
  for (const c of checks) {
    for (const page of ['home', 'pdp']) Object.assign(merged[page], c.probes?.[page] || {});
  }
  return merged;
}
