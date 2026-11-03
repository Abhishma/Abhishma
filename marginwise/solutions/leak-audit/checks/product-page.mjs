// Product page (PDP): the conversion basics on a mobile viewport. Price and
// add-to-cart visibility above the fold, social proof, shipping cost clarity,
// delivery estimate and buy-now-pay-later messaging near the price.
//
// The `probes` export tells the collector which elements to locate in the
// browser; the run() function only reads their positions.

import { finding, STATUS, snippet } from '../lib/util.mjs';

const CURRENCY = String.raw`(?:A\$|NZ\$|C\$|CA\$|US\$|AU\$|\$|€|£|SAR|SR|ر\.س|﷼)\s?\d|\d[\d.,]*\s?(?:€|SAR|SR|ر\.س|﷼|AUD|NZD|USD|CAD|EUR)\b`;

// BNPL providers: name, selector for their widgets/logos, and text pattern.
export const BNPL = [
  { name: 'Afterpay', selector: 'afterpay-placement, square-placement, [class*="afterpay" i], img[alt*="afterpay" i]', text: String.raw`\bafterpay\b|clearpay` },
  { name: 'Zip', selector: '[id*="zip-widget" i], [class*="zip-widget" i], [class*="zippay" i], img[alt^="zip" i]', text: String.raw`\bzip\s?(pay|money)\b|\bwith zip\b|\bzip it\b` },
  { name: 'Klarna', selector: 'klarna-placement, [class*="klarna" i], img[alt*="klarna" i]', text: String.raw`\bklarna\b` },
  { name: 'Tabby', selector: '#tabbyPromo, [class*="tabby" i], img[alt*="tabby" i]', text: String.raw`\btabby\b|تابي` },
  { name: 'Tamara', selector: 'tamara-widget, [class*="tamara" i], img[alt*="tamara" i]', text: String.raw`\btamara\b|تمارا` },
  { name: 'Affirm', selector: '.affirm-as-low-as, [class*="affirm" i], img[alt*="affirm" i]', text: String.raw`\baffirm\b` },
  { name: 'Shop Pay Installments', selector: 'shopify-payment-terms, [class*="payment-terms" i]', text: String.raw`shop pay installments|pay in 4 interest-free` },
];

export const probes = {
  pdp: {
    price: { selector: '[itemprop="price"], .price, [class*="price" i]:not([class*="compare" i]), [data-price], [data-product-price]', text: CURRENCY },
    atc: {
      selector: 'form[action*="/cart/add"] [type="submit"], button[name="add"], [data-testid*="add-to-cart" i], [id*="add-to-cart" i], [class*="add-to-cart" i], [class*="addtocart" i], #AddToCart, [data-action="add-to-cart"]',
      text: String.raw`^\s*(add to (cart|bag|basket)|buy now|in den warenkorb|jetzt kaufen|ajouter au panier|أضف (إلى|الى) السلة|إضافة (إلى|الى) السلة)\s*$`,
    },
    reviews: {
      selector: '.jdgm-widget, .jdgm-prev-badge, .yotpo, .yotpo-widget-instance, [class*="okendo" i], .stamped-badge, .loox-rating, .trustpilot-widget, [data-bv-show], .pr-snippet, [class*="star-rating" i], [class*="rating" i][aria-label], [aria-label*="out of 5" i]',
      text: String.raw`\b\d(\.\d)?\s*(out of 5|/\s*5\b|stars?)\b|\(\d+\s*(reviews?|bewertungen|avis)\)|\b\d+\s+(reviews?|bewertungen|avis|تقييمات?)\b`,
    },
    ...Object.fromEntries(BNPL.map((b) => [`bnpl_${b.name}`, { selector: b.selector, text: b.text }])),
  },
};

const SHIPPING_RE = /free (shipping|delivery|returns? and shipping)|shipping|delivery (fee|cost|charge)|versand(kostenfrei|kosten)?|kostenlose? (lieferung|versand)|livraison|الشحن|توصيل مجاني/i;
const THRESHOLD_RE = /free (shipping|delivery)[^.\n]{0,25}(on|over|above|from|orders? over)\s*[^\s]{0,4}\d|ab\s*\d+[.,]?\d*\s*€?\s*(versandkostenfrei|kostenlos)|versandkostenfrei ab|livraison gratuite (dès|à partir)/i;
const DELIVERY_RE = /(arrives?|delivered|get it|delivery|ships?|dispatch(ed|es)?)\s+(by|in|between|within|on|today|tomorrow)|\d+\s*[-–]\s*\d+\s*(business |working )?days|lieferzeit|lieferung in|in \d+[-–]\d+ werktagen|order (within|in the next)|التوصيل خلال/i;

/**
 * Pick the product price: prefer price-classed elements, fall back to short
 * currency text. Skips "$0.00" cart badges and long promo lines such as
 * "Free shipping over $100" in an announcement bar.
 */
function pickPrice(matches = []) {
  const ok = (m) => /[1-9]/.test(m.text) && !/shipping|delivery|versand|off\b|save/i.test(m.text);
  return matches.find((m) => m.how === 'selector' && ok(m) && m.text.length < 40)
    || matches.find((m) => m.how === 'text' && ok(m) && m.text.length < 25)
    || null;
}

export default {
  id: 'pdp',
  title: 'Product page',
  offer: 'Core of the Revenue Leak Audit (PDP conversion leaks)',
  weight: 20,
  probes,
  run(ctx) {
    const p = ctx.pdp;
    if (!p?.ok) {
      return [finding('pdp.loaded', 'Product page loaded', STATUS.ERROR,
        ctx.pdpSource ? `Could not load PDP ${ctx.pdpSource}: ${p?.errors?.join('; ') || 'unknown error'}` : 'No product page found (pass --pdp <url>).')];
    }
    const fold = p.viewport?.height || 664;
    const pr = p.probes || {};
    const out = [];

    const price = pickPrice(pr.price);
    out.push(finding('pdp.price', 'Price visible above the fold', price ? (price.top < fold ? STATUS.PASS : STATUS.WARN) : STATUS.FAIL,
      price ? `"${price.text}" at ${price.top}px (fold ${fold}px)` : 'No visible price element found.',
      price && price.top < fold ? '' : 'Move the price directly under the product title so it shows in the first mobile screen.'));

    const atc = (pr.atc || [])[0];
    out.push(finding('pdp.atc', 'Add to cart visible above the fold', atc ? (atc.top < fold ? STATUS.PASS : STATUS.FAIL) : STATUS.FAIL,
      atc ? `"${atc.text}" at ${atc.top}px (fold ${fold}px)` : 'No visible add-to-cart button found.',
      atc && atc.top < fold ? '' : 'Bring the add-to-cart button into the first mobile screen (shrink the gallery) or add a sticky add-to-cart bar.'));

    const reviews = (pr.reviews || [])[0];
    const ldRating = p.jsonLd.some((n) => n.aggregateRating || n.offers?.aggregateRating);
    let revStatus = STATUS.FAIL;
    let revEvidence = 'No reviews widget or star rating found on the PDP.';
    if (reviews) {
      const nearTop = reviews.top < fold;
      revStatus = nearTop ? STATUS.PASS : STATUS.WARN;
      revEvidence = `"${reviews.text}" at ${reviews.top}px (${nearTop ? 'above' : 'below'} the fold${price ? `, ${reviews.top < price.top ? 'above' : 'below'} the price` : ''})`;
    } else if (ldRating) {
      revStatus = STATUS.WARN;
      revEvidence = 'aggregateRating exists in JSON-LD but no visible rating on the page.';
    }
    out.push(finding('pdp.reviews', 'Reviews / star rating', revStatus, revEvidence,
      revStatus === STATUS.PASS ? '' : 'Show a star rating and review count next to the title (Judge.me, Okendo, Yotpo etc.), with the full reviews further down.'));

    const text = p.visibleText || '';
    const ship = SHIPPING_RE.test(text);
    const threshold = THRESHOLD_RE.test(text);
    out.push(finding('pdp.shipping', 'Shipping cost or free-shipping threshold on PDP', threshold ? STATUS.PASS : ship ? STATUS.WARN : STATUS.FAIL,
      threshold ? snippet(text, THRESHOLD_RE, 40) : ship ? 'Shipping is mentioned but no cost or threshold: ' + snippet(text, SHIPPING_RE, 40) : 'No shipping information on the product page.',
      threshold ? '' : 'State the shipping cost or "Free shipping over $X" near the add-to-cart; surprise costs at checkout are the top abandonment reason.'));

    out.push(finding('pdp.delivery', 'Delivery estimate', DELIVERY_RE.test(text) ? STATUS.PASS : STATUS.WARN,
      DELIVERY_RE.test(text) ? snippet(text, DELIVERY_RE, 40) : 'No delivery time estimate found.',
      DELIVERY_RE.test(text) ? '' : 'Add a delivery estimate ("Order today, arrives Tue-Thu") under the add-to-cart button.'));

    // BNPL: which providers appear, and is any within ~250px of the price?
    const bnplHits = BNPL.map((b) => ({ name: b.name, m: (pr[`bnpl_${b.name}`] || [])[0] })).filter((x) => x.m);
    ctx.bnpl = bnplHits.map((b) => b.name);
    const near = price ? bnplHits.filter((b) => Math.abs(b.m.top - price.top) <= 250) : [];
    out.push(finding('pdp.bnpl', 'BNPL messaging near the price', bnplHits.length ? (near.length ? STATUS.PASS : STATUS.WARN) : STATUS.WARN,
      bnplHits.length
        ? `${bnplHits.map((b) => `${b.name} at ${b.m.top}px`).join(', ')}${price ? `; price at ${price.top}px` : ''}${near.length ? '' : ' (not near price)'}`
        : 'No BNPL messaging (Afterpay, Zip, Klarna, Tabby, Tamara, Affirm, Shop Pay Installments).',
      near.length ? '' : 'Place the BNPL instalment line ("or 4 payments of $X") directly under the price.'));
    return out;
  },
};
