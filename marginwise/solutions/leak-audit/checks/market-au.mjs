// Australia: card surcharges (banned by the RBA from 1 Oct 2026) and Afterpay,
// the dominant local BNPL.

import { finding, STATUS, snippet, allText } from '../lib/util.mjs';

const SURCHARGE_RE = /surcharge|card fee|%\s*(card\s*|processing\s*|payment\s*)?fee/i;
const AFTERPAY_RE = /\bafterpay\b/i;

export default {
  id: 'market-au',
  title: 'Market rules: Australia',
  markets: ['AU'],
  offer: 'Teardown compliance flag; Revenue Leak Audit checkout review',
  weight: 15,
  run(ctx) {
    const text = allText(ctx);
    const out = [];
    const hit = SURCHARGE_RE.test(text);
    out.push(finding('au.surcharge', 'Card surcharge text', hit ? STATUS.FAIL : STATUS.PASS,
      hit ? `Found: ${snippet(text, SURCHARGE_RE)}` : 'No surcharge or card-fee wording on the homepage or PDP.',
      hit ? 'Remove card surcharges and the wording: the RBA ban on debit and credit card surcharges applies from 1 Oct 2026. Price the cost into margins or offer free payment methods instead. (Not legal advice; confirm with the payment provider.)' : ''));

    const ap = AFTERPAY_RE.test(text) || (ctx.bnpl || []).includes('Afterpay') || [ctx.home, ctx.pdp].some((s) => (s?.requests || []).some((r) => /afterpay|squarecdn.*afterpay|static\.afterpay/i.test(r.url)));
    out.push(finding('au.afterpay', 'Afterpay messaging', ap ? STATUS.PASS : STATUS.WARN,
      ap ? 'Afterpay is mentioned or its widget loads.' : 'No Afterpay messaging found.',
      ap ? '' : 'Afterpay is the default BNPL expectation for AU shoppers; add the instalment widget under the price.'));
    return out;
  },
};
