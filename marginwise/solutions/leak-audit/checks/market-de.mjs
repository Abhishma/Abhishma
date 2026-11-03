// Germany: legal-notice and consumer-law signals that are visible on the
// storefront. All detection is text/link based and heuristic.
//   - Impressum (DDG section 5)
//   - Withdrawal function "Vertrag widerrufen" (EU 2023/2673, from 19 Jun 2026)
//   - Kuendigungsbutton for subscriptions (BGB section 312k)
//   - Kauf auf Rechnung (invoice payment, a conversion lever in DE)
//   - Strike-through prices (PAngV section 11, 30-day lowest price)
//   - Climate-neutral claims (EmpCo Directive, applies from 27 Sep 2026)
//   - Accessibility statement (BFSG, since 28 Jun 2025)

import { finding, STATUS, snippet, allText, allLinks } from '../lib/util.mjs';

const has = (links, re) => links.find((l) => re.test(l.text) || re.test(l.href));

export default {
  id: 'market-de',
  title: 'Market rules: Germany',
  markets: ['DE'],
  offer: 'Teardown compliance flags; Revenue Leak Audit legal-UX section (not legal advice)',
  weight: 15,
  run(ctx) {
    const text = allText(ctx);
    const links = allLinks(ctx);
    const out = [];

    const imp = has(links, /impressum|imprint|legal[- ]notice/i);
    out.push(finding('de.impressum', 'Impressum link', imp ? STATUS.PASS : STATUS.FAIL,
      imp ? `Link: "${imp.text || imp.href}"` : 'No Impressum link on the homepage or PDP.',
      imp ? '' : 'Add an "Impressum" link to the footer of every page (DDG section 5); missing imprints are a common Abmahnung trigger.'));

    const widerrufRe = /vertrag(e)? (hier )?widerrufen|widerrufsbutton|widerruf/i;
    const wid = widerrufRe.test(text) || has(links, /widerruf/i);
    const button = /vertrag(e)? (hier )?widerrufen/i.test(text);
    out.push(finding('de.widerruf', 'Withdrawal function ("Vertrag widerrufen")', button ? STATUS.PASS : STATUS.WARN,
      button ? snippet(text, /vertrag(e)? (hier )?widerrufen/i, 40) : wid ? 'Widerruf (policy) is mentioned, but no "Vertrag widerrufen" button text was found.' : 'No withdrawal wording found.',
      button ? '' : 'Add an online withdrawal function labelled "Vertrag widerrufen" (mandatory for online contracts since 19 Jun 2026) in the footer and account area.'));

    const subs = /\babo\b|abonnement|subscription|subscribe (&|and) save|spar-abo|im abo/i.test(text);
    const kuend = /vertr(ä|ae)ge hier k(ü|ue)ndigen|k(ü|ue)ndigungsbutton|k(ü|ue)ndigen/i.test(text) || has(links, /k(ü|ue)ndig/i);
    out.push(finding('de.kuendigung', 'Kuendigungsbutton (subscriptions)', !subs ? STATUS.INFO : kuend ? STATUS.PASS : STATUS.FAIL,
      !subs ? 'No subscription signals found; not applicable.' : kuend ? 'Subscription offered and cancellation wording found.' : 'Subscription signals found but no "Vertraege hier kuendigen" button.',
      subs && !kuend ? 'Add a permanently visible "Vertraege hier kuendigen" button (BGB section 312k) leading to a two-step cancellation form.' : ''));

    const inv = /kauf auf rechnung|rechnungskauf|auf rechnung|pay (later )?by invoice|klarna rechnung/i.test(text);
    out.push(finding('de.invoice', 'Kauf auf Rechnung (invoice payment)', inv ? STATUS.PASS : STATUS.WARN,
      inv ? snippet(text, /kauf auf rechnung|rechnungskauf|auf rechnung|invoice/i, 30) : 'No invoice payment mentioned.',
      inv ? '' : 'Offer and advertise "Kauf auf Rechnung" (e.g. Klarna Pay Later, PayPal Rechnungskauf); it is a top payment preference in Germany.'));

    const strike = [ctx.home, ctx.pdp].flatMap((s) => s?.strike || []);
    out.push(finding('de.strike', 'Strike-through prices (30-day lowest price)', strike.length ? STATUS.WARN : STATUS.PASS,
      strike.length ? `Strike-through prices: ${strike.slice(0, 4).join(' | ')}` : 'No strike-through prices found.',
      strike.length ? 'Check that each reference price is the lowest price of the previous 30 days (PAngV section 11) and label it ("Niedrigster Preis der letzten 30 Tage").' : ''));

    const climateRe = /klimaneutral|co2[- ]?neutral|co₂[- ]?neutral|climate[- ]neutral|carbon[- ]neutral|klimapositiv/i;
    const climate = climateRe.test(text);
    out.push(finding('de.climate', 'Climate-neutral claims', climate ? STATUS.WARN : STATUS.PASS,
      climate ? snippet(text, climateRe, 40) : 'No climate-neutral claims found.',
      climate ? 'Remove offset-based "klimaneutral" claims or substantiate them: the EmpCo Directive bans such generic claims from 27 Sep 2026.' : ''));

    const bf = has(links, /barrierefrei|accessibility/i) || /erkl(ä|ae)rung zur barrierefreiheit|barrierefreiheit/i.test(text);
    out.push(finding('de.bfsg', 'Accessibility statement (Barrierefreiheit)', bf ? STATUS.PASS : STATUS.WARN,
      bf ? 'Barrierefreiheit statement or link found.' : 'No "Barrierefreiheit" statement or link found.',
      bf ? '' : 'Publish a "Barrierefreiheitserklaerung" (BFSG, in force since 28 Jun 2025) and link it in the footer.'));
    return out;
  },
};
