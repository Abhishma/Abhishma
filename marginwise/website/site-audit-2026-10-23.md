# marginwise.in audit, 23 Oct 2026

Live site checked with a fresh crawl of /, /pricing, /calculators, /case-studies, robots.txt, sitemap.xml, llms.txt and a missing URL.

## Already good
- Unique titles, meta descriptions and correct canonical tags on every page; lang="en"; viewport set.
- robots.txt allows search engines and AI crawlers (GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot, Google-Extended) and points to the sitemap.
- sitemap.xml lists all 4 pages. llms.txt lists services, prices in four currencies and pages.
- Organization/ProfessionalService and FAQPage JSON-LD on the home page.
- Missing pages return a real 404.
- Sources linked for every statistic.
- Tested earlier: 55 tests, no serious axe violations, no horizontal scroll at 375px.

## Fixes sent to Lovable (message umsg_01m5k892b6eqjrk0prd2w2c4ep)
1. Privacy policy and terms pages (none today, while the site collects leads in AU, UK and India).
2. Same header on every page (inner pages show only two links today), with a mobile menu.
3. Same footer on every page, with email and legal links.
4. FAQ says quotes come in "USD, AUD or GBP": add INR (visible text and JSON-LD).
5. Booking links render as "/" and "#" until JavaScript loads.
6. Generated anchor ids on the privacy note.
7. "Case studies" page has no case studies yet: renamed to "Benchmarks and method".
8. Social tags: twitter:card inconsistent; add og:site_name, og:locale, image size and alt.
9. JSON-LD: WebSite, logo, email, BreadcrumbList.
10. sitemap lastmod and new pages; llms.txt update.
11. Render-blocking Google Fonts (3 families): self-host and preload.
12. Skip link; keyboard focus check.
13. Security headers where the hosting allows.

## For you to do (not code)
- Remove the "Edit with Lovable" badge: Lovable project settings, "Hide Lovable badge" (Pro plan). It shows on every page today.
- Check abhimanyu@marginwise.in receives mail. The privacy policy and form use it, and the test confirmation email bounced.
- Instagram handle: send it and we add it to the footer and the Organization schema (sameAs).
- Google Search Console: the site is verified. Submit the sitemap and request indexing of the 6 pages after this update.
- Analytics for ads: the site has Lovable analytics only. For Meta ads optimised on leads, add the Meta Pixel and GA4 (needs their IDs). UK visitors need a consent banner before those load.
