# Australia problem/solution ads (Meta and Instagram)

Six creatives, each one Australian store problem and the fix. Every creative has a feed version (`*-feed.png`, 1080 x 1350) and a Story/Reel version (`*-story.png`, 1080 x 1920, with text clear of the top 270 px and bottom 300 px). Edit the copy in `build.py`, then re-render.

Offer on every ad: free 2-minute store teardown. Landing page: the teardown form on marginwise.in with Australian prices.

Landing URL pattern (change `utm_content` per ad):

```
https://marginwise.in/?market=au&utm_source=meta&utm_medium=paid&utm_campaign=au_problem_solution&utm_content=surcharge#teardown
```

## Ad copy

All six share these settings:

| Field | Value |
|---|---|
| CTA button | Learn more (or Get quote) |
| Display link | marginwise.in |
| Description | Free. Video within 3 working days. |

### 1. surcharge (Card fees)
- Primary text: The surcharge is gone. The card fee isn't. Since 1 October, Australian businesses can't surcharge Visa, Mastercard or eftpos payments, so the fee now comes out of margin. We'll check your store for leftover surcharge text and show which products need repricing. Free 2-minute video teardown.
- Headline: Who pays the card fee now?
- Source: Reserve Bank of Australia, media release 2026-10.

### 2. shipping (Sendle)
- Primary text: Sendle has closed. If your store relied on it, your rates, delivery promises and checkout options may be out of date. We'll look at your shipping set-up and show what to fix first. Free 2-minute video teardown.
- Headline: Is your shipping still set up right?
- Source: The New Daily, 12 Jan 2026.

### 3. checkout (Cart abandonment)
- Primary text: On average, 7 in 10 carts never become orders (Baymard Institute). The usual causes are fixable: surprise costs, forced sign-up and too many steps. We'll record a 2-minute video of your checkout and show the one change we'd make first.
- Headline: Where your checkout loses orders.

### 4. speed (Site speed)
- Primary text: In a Deloitte study for Google, a 0.1 second faster mobile site lifted retail conversions by 8.4% on average across 37 brands. We'll check what slows your store on a phone and show what to remove. Free 2-minute video teardown.
- Headline: Is your store slow on a phone?

### 5. sync (Xero, MYOB, Cin7)
- Primary text: Failed Shopify syncs, missing SKUs, payouts that don't match the bank feed. If someone fixes these by hand every morning, we can connect Shopify to Xero, MYOB or Cin7 and set up an AI agent that fixes the safe errors and flags the rest for a person.
- Headline: Stop fixing orders by hand.
- CTA button: Book now. Landing URL ends `#book` instead of `#teardown`.

### 6. aisearch (AI search)
- Primary text: Ask ChatGPT for the best brand in your category. Is your store in the answer? We make product pages easy for Google and AI assistants to read, trust and quote. Free 2-minute teardown of your store's AI search readiness.
- Headline: Is your store in the AI answer?

## Campaign set-up (test)

1. **Before launch, set up tracking. The site has no Meta Pixel yet.** Choose one:
   - **A, recommended for week 1:** a Meta Lead campaign with an Instant Form.
     - Questions: name, email, store URL, monthly online revenue band, biggest problem, and a consent line matching the site's privacy note.
     - Leads land in Meta. Export them daily into the team Leads tab, or connect them with Zapier.
   - **B:** add the Meta Pixel and Conversions API to marginwise.in (a Lovable change, so it needs credits). Fire `Lead` on a successful teardown form submission, with no personal data. Then run a Sales/Leads campaign optimising for that event.
2. **Structure:** one campaign, one ad set, all six ads.
   - Advantage+ placements.
   - Use the feed creative for Feed and the story creative for Stories and Reels (asset customisation).
3. **Location:** Australia only.
   - Age 25-60.
   - Advantage+ audience, with suggestions: Shopify, e-commerce, Afterpay, Xero, small business owners, online shopping business.
   - Exclude existing leads and clients once you have a list.
4. **Budget:** A$40 a day for 7 days (about A$280).
   - Don't touch it for the first 3 days while Meta learns.
   - On day 4, pause any ad with click-through rate below 0.6% or cost per lead above twice the average.
   - On day 7, move budget to the best two ads and make two new variations of the winner.
5. **What a good week looks like:** some teardown requests and a cost per lead you can afford. With an audit at A$2,300 and sprints from A$5,900, even A$60-100 per qualified lead is worth it if 1 in 10 books a call and converts. Treat these as targets to test, not benchmarks.
6. **Follow-up speed decides the result:**
   - Send every teardown video within 3 working days.
   - End it with the booking link and the audit price.

## Organic Instagram use

- Post the feed creatives as single-image posts, one every 2-3 days. Use the primary text as the caption and the keyword AUDIT ("Comment AUDIT for a free teardown").
- Use the story creatives in Stories with a link sticker to the landing URL. Set `utm_source=instagram` and `utm_medium=story`.

## Policy and claim checks

- **Sources:** every statistic has its source on the creative and in the copy.
  - Surcharge: RBA.
  - Cart abandonment: Baymard 70.22%.
  - Speed: Deloitte and Google 2020.
  - Sendle: The New Daily.
- **No invented results:** no client results, no promised outcomes, no "guaranteed".
- **Meta personal-attributes policy:** the copy talks about the store, not the person. No "Are you struggling...".
- **Surcharge rules:** the ads say what the RBA decision covers. Merchants' own advisers decide what applies to them.
