# Lovable prompt: mobile speed and real booking check (31 Oct 2026)

Send after Margin Check phase 1 (queued in Lovable) has run. Text below is sent as is.

```
After the Margin Check phase 1 message, finish the two open items from the build. Do not publish.

1. Mobile loading speed: the main heading is the LCP element (3.3 s live). Make it render on first paint: preload the display font's woff2 with font-display: swap (or optional) and a size-adjusted fallback, inline the critical CSS for the hero, defer non-critical scripts and third-party code, and make sure no hydration or client-only wrapper delays the hero text. Target LCP under 2.5 s on a mobile Lighthouse run against a production-like build if you can; otherwise report the dev numbers and what you changed.
2. Real booking check: make one test booking, confirm a second booking for the same slot is refused with the "Someone just booked that time" message, then delete the test booking row and its Google Calendar event and confirm the slot is free again.
3. Re-run the internal link check and axe on / at 1280px (light and dark) after last turn's anchor and link fixes.

Report results. Do not publish.
```
