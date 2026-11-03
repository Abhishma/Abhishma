// Shared helpers used by the collector, the checks and the report renderer.

/** Status values a finding can carry. "info" and "error" are not scored. */
export const STATUS = Object.freeze({ PASS: 'pass', WARN: 'warn', FAIL: 'fail', INFO: 'info', ERROR: 'error' });

/** Points per status when computing a check's score (null = excluded). */
export const POINTS = { pass: 1, warn: 0.5, fail: 0, info: null, error: null };

/**
 * Build one finding. Every check returns an array of these.
 * @param {string} id      stable machine id, e.g. "speed.lcp"
 * @param {string} label   human label shown in the report
 * @param {string} status  one of STATUS
 * @param {string} evidence what we observed
 * @param {string} [fix]   recommended fix (empty for passes)
 */
export function finding(id, label, status, evidence, fix = '') {
  return { id, label, status, evidence: String(evidence ?? ''), fix: String(fix ?? '') };
}

// Second-level labels that act like public suffixes when paired with a ccTLD
// (com.au, co.nz, com.sa, co.uk ...). Good enough without a full PSL.
const SLD = new Set(['com', 'co', 'net', 'org', 'gov', 'edu', 'ac', 'id', 'asn', 'gen', 'ltd', 'plc']);

/** Approximate registrable domain (eTLD+1) for first/third-party decisions. */
export function siteOf(hostname) {
  const host = String(hostname || '').toLowerCase().replace(/\.$/, '');
  if (/^\d+\.\d+\.\d+\.\d+$/.test(host) || host === 'localhost' || host.includes(':')) return host;
  const parts = host.split('.');
  if (parts.length <= 2) return host;
  const tld = parts.at(-1);
  const sld = parts.at(-2);
  if (tld.length === 2 && SLD.has(sld)) return parts.slice(-3).join('.');
  return parts.slice(-2).join('.');
}

/** Safe URL parse; returns null instead of throwing. */
export function parseUrl(u, base) {
  try { return new URL(u, base); } catch { return null; }
}

/** Escape text for HTML output. */
export function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

/** Return a short snippet of `text` around the first regex match, for evidence. */
export function snippet(text, re, radius = 60) {
  const m = re.exec(String(text || ''));
  if (!m) return '';
  const start = Math.max(0, m.index - radius);
  const end = Math.min(text.length, m.index + m[0].length + radius);
  return (start > 0 ? '...' : '') + text.slice(start, end).replace(/\s+/g, ' ').trim() + (end < text.length ? '...' : '');
}

/** Format bytes as KB/MB. */
export function fmtBytes(n) {
  if (!Number.isFinite(n)) return 'n/a';
  if (n >= 1024 * 1024) return (n / 1024 / 1024).toFixed(2) + ' MB';
  return Math.round(n / 1024) + ' KB';
}

/** Concatenate the searchable text of the homepage and PDP snapshots. */
export function allText(ctx) {
  return [ctx.home?.signalText, ctx.pdp?.signalText].filter(Boolean).join('\n');
}

/** All links from both pages. */
export function allLinks(ctx) {
  return [...(ctx.home?.links || []), ...(ctx.pdp?.links || [])];
}
