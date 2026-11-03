// Saudi Arabia: Arabic storefront, VAT-inclusive pricing, local BNPL (Tabby,
// Tamara), WhatsApp contact and local payment methods (mada, Apple Pay).

import { finding, STATUS, snippet, allText, allLinks, parseUrl } from '../lib/util.mjs';

export default {
  id: 'market-sa',
  title: 'Market rules: Saudi Arabia',
  markets: ['SA'],
  offer: 'Revenue Leak Audit (KSA market readiness)',
  weight: 15,
  run(ctx) {
    const snaps = [ctx.home, ctx.pdp].filter((s) => s?.ok);
    const text = allText(ctx);
    const links = allLinks(ctx);
    const out = [];

    const langAr = snaps.find((s) => /^ar/i.test(s.lang) || /rtl/i.test(s.dir));
    const arLink = links.find((l) => /^\/ar([-_][a-z]+)?\//i.test((parseUrl(l.href)?.pathname || '') + '/') || /^(العربية|عربي)$/.test(l.text.trim()));
    const arHref = snaps.flatMap((s) => s.hreflangs).find((h) => /^ar/i.test(h.lang || ''));
    const ar = langAr || arLink || arHref;
    out.push(finding('sa.arabic', 'Arabic version available', ar ? STATUS.PASS : STATUS.FAIL,
      langAr ? `Page served with lang="${langAr.lang}" dir="${langAr.dir}"` : arHref ? `hreflang ${arHref.lang}` : arLink ? `Arabic link ${arLink.href}` : 'No lang=ar, dir=rtl, /ar path or Arabic switcher found.',
      ar ? '' : 'Launch an Arabic RTL storefront (Shopify Markets + RTL theme, or Salla/Zid native) with hreflang ar-SA.'));

    const vatRe = /incl(\.|uding|usive of)? ?(15% )?vat|vat incl|prices? include vat|tax included|شامل(ة)? (ل)?(ضريبة|الضريبة)|السعر شامل/i;
    out.push(finding('sa.vat', 'Prices shown incl. VAT', vatRe.test(text) ? STATUS.PASS : STATUS.WARN,
      vatRe.test(text) ? snippet(text, vatRe, 30) : 'No "incl. VAT" wording found.',
      vatRe.test(text) ? '' : 'Show "Prices include 15% VAT" / "السعر شامل الضريبة" next to prices (ZATCA expects VAT-inclusive consumer pricing).'));

    const bnpl = new Set((ctx.bnpl || []).filter((n) => n === 'Tabby' || n === 'Tamara'));
    if (/\btabby\b|تابي/i.test(text)) bnpl.add('Tabby');
    if (/\btamara\b|تمارا/i.test(text)) bnpl.add('Tamara');
    out.push(finding('sa.bnpl', 'Tabby / Tamara', bnpl.size ? STATUS.PASS : STATUS.WARN,
      bnpl.size ? `Found: ${[...bnpl].join(', ')}` : 'Neither Tabby nor Tamara found.',
      bnpl.size ? '' : 'Add Tabby and/or Tamara with the "split in 4" widget under the price; they are standard in KSA checkout.'));

    const wa = links.find((l) => /wa\.me|api\.whatsapp\.com|whatsapp/i.test(l.href)) || /whatsapp|واتساب/i.test(text);
    out.push(finding('sa.whatsapp', 'WhatsApp contact', wa ? STATUS.PASS : STATUS.WARN,
      wa ? 'WhatsApp contact found.' : 'No WhatsApp link or mention.',
      wa ? '' : 'Add a WhatsApp click-to-chat button (wa.me link); it is the primary support channel for KSA shoppers.'));

    const pay = [/\bmada\b|مدى/i.test(text) && 'mada', /apple ?pay/i.test(text) && 'Apple Pay'].filter(Boolean);
    out.push(finding('sa.payments', 'mada / Apple Pay shown', pay.length === 2 ? STATUS.PASS : STATUS.WARN,
      pay.length ? `Found: ${pay.join(', ')}` : 'Neither mada nor Apple Pay mentioned.',
      pay.length === 2 ? '' : 'Show mada and Apple Pay badges on the PDP and cart; mada is the national debit network.'));
    return out;
  },
};
