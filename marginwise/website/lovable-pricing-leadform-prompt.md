# Lovable prompt: prices by location and a lead form

Send this after the calculators fix is done.

```
Two features: prices by visitor location, and a lead form for free teardowns. Keep the existing design, booking, Google Calendar/Meet, emails, auth, team area and calculators working.

1. Prices by location
- Detect the market from the visitor's time zone, the same way booking already does: America/* = us, Europe/* = uk, Asia/Kolkata or Asia/Calcutta = in, everything else = au. No IP lookup and no third-party service.
- Add a small market switcher ("Prices for: Australia / US / UK / India") above the pricing cards on the home page and on /pricing. The choice is saved in localStorage and also sets the booking market, the calculator currency and the lead form market. A ?market=au|us|uk|in URL parameter overrides it (for ads and Instagram links).
- Put the prices in one config file, src/lib/pricing.ts, so they can be changed in one place:

  | Offer | US (USD) | Australia (AUD) | UK (GBP) | India (INR) |
  |---|---|---|---|---|
  | Free 2-minute teardown | Free | Free | Free | Free |
  | Revenue Leak Audit | $1,500 | A$2,300 | £1,200 | ₹35,000 |
  | Fixed-price sprints, from | $3,900 | A$5,900 | £3,100 | ₹95,000 |
  | Monthly retainers, from | $1,500/mo | A$2,300/mo | £1,200/mo | ₹40,000/mo |

- Format with Intl.NumberFormat: en-US, en-AU, en-GB, en-IN (so India shows ₹35,000 and ₹1,00,000 style grouping).
- Tax line under the prices: AU, US and UK "Prices exclude any local taxes." India "Prices exclude GST."
- Replace every hard-coded price on the site with values from pricing.ts: hero, service cards, pricing page, FAQ "How much does it cost?", plan calculator, and the call follow-up email (use the lead's market).
- The JSON-LD FAQ answer stays in USD and adds "or the equivalent in AUD, GBP or INR". public/llms.txt lists all four price columns.
- Unit tests: each time zone maps to the right market; ?market= overrides the time zone; formatPrice gives "$1,500", "A$2,300", "£1,200", "₹35,000", "₹95,000"; the FAQ answer and the pricing cards show the same numbers for each market.

2. Lead form: "Get a free 2-minute teardown"
- New section on the home page, id="teardown", after the services and before booking. Add a hero button "Get a free teardown" that scrolls to it. Also put the form under the results on /calculators, with the title "Want us to look at your numbers?".
- Fields:
  - Name (required)
  - Work email (required, validated)
  - Store URL (required, accept with or without https://)
  - Market (pre-filled from the detected market, editable)
  - Monthly online revenue (select, in the market's currency: under 50k / 50k-250k / 250k-1M / over 1M, with the currency symbol; for India use under ₹10 lakh / ₹10-50 lakh / ₹50 lakh-2 crore / over ₹2 crore)
  - Biggest problem (select: Ads aren't profitable / Visitors don't buy / Site is slow / Not showing in Google or AI search / Too much manual work or support / Something else)
  - Notes (optional, 500 characters)
  - Consent checkbox (required): "I agree to Marginwise contacting me about this request. See our privacy note." Link to a short privacy section explaining what is stored, why, who sees it, and how to ask for deletion (email abhimanyu@marginwise.in).
- Button: "Send my store". Success state: "Got it. You'll get your 2-minute video within 3 working days. Want to talk sooner? Book a call." with a link to #book. Inline errors next to each field, all labelled for screen readers.
- Spam protection: a hidden honeypot field, reject submissions faster than 3 seconds after the form loads, and a server-side limit of 5 submissions per email per day.
- Storage: new Supabase table leads (Drizzle migration) with id, created_at, name, email, store_url, market, currency, revenue_band, problem, notes, consent (bool), consent_text, source_page, utm_source, utm_medium, utm_campaign, utm_content, referrer, status (new / contacted / teardown_sent / call_booked / won / lost, default new). RLS: anonymous visitors can only insert; only team users can read and update. Capture UTMs from the landing URL and keep them in sessionStorage so they survive page changes.
- Emails:
  - Team notification to abhimanyu.btti@gmail.com, velmoorthy65@gmail.com and abhimanyu@marginwise.in, subject "New teardown lead: <store> (<market>)", with all fields and the UTMs.
  - Confirmation to the lead: "Thanks, <name>. We'll record a 2-minute teardown of <store> and send it within 3 working days. If you'd rather talk, book a 30-minute call here: <booking link>." Plain text, from the same sender as the booking emails.
- Team area: a "Leads" tab with a table (newest first): date, name, store link, market, revenue band, problem, source/UTM, status dropdown, and a "Book call" link that opens the booking with the lead's details pre-filled. Filters by market and status. Export CSV.
- If GA4 or another analytics script is installed, fire a generate_lead event with market and problem on success. Never send name, email or store URL to analytics.
- Tests: valid submission is stored and both emails are queued; missing consent is rejected; the honeypot is rejected; the 6th submission from the same email in a day is rejected; anonymous users cannot read leads.

3. Checks: all tests pass, type check clean, no serious axe violations on /, /pricing and /calculators, no horizontal scroll at 375px, dark mode works. Submit one test lead with the email test+lead@marginwise.in, confirm the row and the emails, then delete the row. List files changed and test results. Do not publish.
```

---

## Follow-up to send once credits are added (20 Oct)

Lovable started (commit 5dd1947: src/lib/pricing.ts and pricing tests, checked and correct) and paused to ask about the rate limit. Send this:

```
Yes, use a storage-enforced limit of 5 teardown requests per email per day (count rows in the leads table for that lowercased email in the last 24 hours, checked server-side before insert). pricing.ts looks right; keep it as is.

Please continue and finish everything from the previous request: wire pricing.ts into every price on the site with the market switcher and URL override, A$ everywhere including the calculators, the teardown form on the home page and /calculators with consent and privacy note, the leads table with RLS, both emails, the team Leads tab with filters, status, booking prefill and CSV export, the tests, and the checks (desktop and 375px, light and dark, axe, one test lead submitted and then deleted). Report files changed and test results. Do not publish.
```

---

## Follow-up to send once credits are added (21 Oct)

Lovable built most of it (commit dd40566, 47 tests pass) but stopped with type errors in teardown-form.tsx. Leads migration reviewed: RLS insert-only for visitors, team-only read/update, trigger enforces 5 per email per 24 h and currency matches market. Send this:

```
Yes, please finish:
1. Fix the type errors in src/components/marginwise/teardown-form.tsx and any other build errors so the type check is clean and the preview builds.
2. Run the full test suite.
3. Checks on /, /pricing, /calculators and /team: desktop 1280px and mobile 375px, light and dark mode, no horizontal scroll, no serious or critical axe violations. Confirm the market switcher changes every price on the page and that ?market=in shows the INR prices.
4. Submit one real test lead through the home page form with the email test+lead@marginwise.in, confirm the row is stored with the UTMs and that both emails were queued, confirm an anonymous client cannot read the leads table, then delete the test row.
5. Report the test count, type-check result, and the result of each check. Do not publish.
```

---

## Result (22 Oct)

Finished in commit 6cffd58 and published. 55 tests pass, type check clean, all page checks pass at 1280px and 375px in light and dark mode. The test lead was stored with its UTMs, both emails were sent, an anonymous visitor could read no leads, and the test row was deleted. The confirmation email to test+lead@marginwise.in bounced.
