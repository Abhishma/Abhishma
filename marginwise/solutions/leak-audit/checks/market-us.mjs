// United States: ADA demand-letter exposure. Accessibility weight is doubled
// by the scorer for US; this module checks for an accessibility statement.

import { finding, STATUS, allLinks } from '../lib/util.mjs';

const STATEMENT_RE = /accessibility/i;

export default {
  id: 'market-us',
  title: 'Market rules: United States',
  markets: ['US'],
  offer: 'Revenue Leak Audit (ADA risk section)',
  weight: 10,
  run(ctx) {
    const link = allLinks(ctx).find((l) => STATEMENT_RE.test(l.text) || /accessibility/i.test(l.href));
    return [
      finding('us.statement', 'Accessibility statement link', link ? STATUS.PASS : STATUS.WARN,
        link ? `Link: "${link.text || link.href}"` : 'No accessibility statement link found on the homepage or PDP.',
        link ? '' : 'Publish an accessibility statement (conformance target WCAG 2.1 AA, contact route, known issues) and link it in the footer.'),
      finding('us.weight', 'Accessibility weighting', STATUS.INFO, 'Accessibility counts double in the US score because of ADA lawsuit volume.'),
    ];
  },
};
