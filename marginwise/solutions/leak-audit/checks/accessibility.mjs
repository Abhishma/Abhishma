// Accessibility: axe-core WCAG 2.1 AA results (serious and critical only),
// grouped by rule, plus detection of accessibility overlay widgets, which do
// not fix underlying issues and are frequently cited in US ADA complaints.

import { finding, STATUS } from '../lib/util.mjs';
import { OVERLAYS } from '../lib/trackers.mjs';

/** Merge axe violations from several snapshots, keeping serious/critical. */
export function summarise(snaps) {
  const byRule = new Map();
  for (const s of snaps) {
    for (const v of s?.axe?.violations || []) {
      if (v.impact !== 'serious' && v.impact !== 'critical') continue;
      const r = byRule.get(v.id) || { id: v.id, impact: v.impact, help: v.help, nodes: 0, sample: v.sample };
      r.nodes += v.nodes;
      if (v.impact === 'critical') r.impact = 'critical';
      byRule.set(v.id, r);
    }
  }
  return [...byRule.values()].sort((a, b) => (a.impact === b.impact ? b.nodes - a.nodes : a.impact === 'critical' ? -1 : 1));
}

export default {
  id: 'accessibility',
  title: 'Accessibility (WCAG 2.1 AA)',
  offer: 'Teardown flags the count; the Revenue Leak Audit lists every fix by template',
  weight: 15, // doubled for US in the scorer
  run(ctx) {
    const snaps = [ctx.home, ctx.pdp].filter((s) => s?.ok);
    const out = [];
    const errs = snaps.filter((s) => s.axe?.error).map((s) => s.axe.error);
    if (!snaps.length || errs.length === snaps.length) {
      out.push(finding('a11y.axe', 'axe-core scan', STATUS.ERROR, errs.join('; ') || 'No page loaded.'));
    } else {
      const rules = summarise(snaps);
      const critical = rules.filter((r) => r.impact === 'critical');
      const status = critical.length ? STATUS.FAIL : rules.length ? STATUS.WARN : STATUS.PASS;
      const total = rules.reduce((n, r) => n + r.nodes, 0);
      out.push(finding('a11y.violations', 'Serious/critical WCAG 2.1 AA violations', status,
        rules.length
          ? `${rules.length} rule(s), ${total} element(s): ` + rules.slice(0, 8).map((r) => `${r.id} [${r.impact}] x${r.nodes}`).join('; ')
          : 'No serious or critical violations detected by axe-core (automated checks cover roughly a third of WCAG).',
        rules.length ? 'Fix at theme/template level: ' + rules.slice(0, 4).map((r) => `${r.id} (${r.help})`).join('; ') + '. Re-test with a screen reader.' : ''));
      ctx.a11yRules = rules;
    }

    const scriptUrls = snaps.flatMap((s) => [...(s.requests || []).map((r) => r.url), ...(s.scripts || []).map((x) => x.src)]);
    const overlays = OVERLAYS.filter((o) => scriptUrls.some((u) => o.re.test(u))).map((o) => o.name);
    out.push(finding('a11y.overlay', 'Accessibility overlay widget', overlays.length ? STATUS.WARN : STATUS.PASS,
      overlays.length ? `Overlay detected: ${overlays.join(', ')}` : 'No known overlay (accessiBe, UserWay, AudioEye, EqualWeb).',
      overlays.length ? 'Overlays do not make a site conformant and are named in many US lawsuits; fix the underlying markup and keep the overlay only if it adds user value.' : ''));
    return out;
  },
};
