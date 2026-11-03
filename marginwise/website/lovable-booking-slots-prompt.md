# Lovable prompt: booking slots and no double-booking (25 Oct 2026)

Decision (Abhimanyu, 25 Oct): calls 6:00-10:00 PM IST Monday to Saturday, plus three midday slots for Australia (6:30, 7:00 and 7:30 AM IST, which is 12:00-1:00 PM Sydney). No calls on Sunday (IST). Only one booking per slot.

Checked visibility (local time, window 08:00-21:30):
- Sydney: 12:00, 12:30, 13:00
- London: 12:30-16:00
- New York: 08:30-12:00, plus evening 20:00-21:30
- Los Angeles: 08:00-09:00 and 17:00-19:00
- India: 18:00-21:30

```
Urgent booking change. Do this before any other queued work. Keep the Google Calendar/Meet invite, emails, lead storage and team area working.

1. NEW SLOTS (src/components/marginwise/booking-utils.ts)
SLOTS_IST = 06:30, 07:00, 07:30, 18:00, 18:30, 19:00, 19:30, 20:00, 20:30, 21:00, 21:30 (each call is 30 minutes, so the last one ends at 22:00 IST).
Bookable days: Monday to Saturday by the IST date. No slots on Sunday (IST). Offer the next 14 bookable days. A slot must start at least 12 hours from now.
visibleSlots: show a slot when its start time in the displayed time zone is between 08:00 and 21:30 inclusive. If none are visible for a day, show the day as "No times in your daytime" and suggest switching the time zone. Do not show all slots as a fallback.
Default selected slot per market: au 06:30 IST (12:00 Sydney), uk 18:30 IST, us 19:00 IST, in 19:00 IST. If the default isn't available, select the first available slot.
Update every piece of copy that describes hours: "Calls Monday to Saturday. Sydney lunchtime, London afternoons, US mornings, India evenings." Also update the FAQ, llms.txt, the booking confirmation email and the team area.

2. ONLY ONE BOOKING PER SLOT
- Database: add a slot_start timestamptz column to the bookings table (filled from the chosen slot in UTC) and a partial unique index: unique (slot_start) where status is not cancelled. Backfill existing rows from their stored slot. Write a Drizzle migration.
- Server: the booking function inserts in one statement and relies on the unique index. On a conflict, return { ok: false, code: "slot_taken" } and don't create a calendar event or send emails. Create the Google Calendar event only after the insert succeeds. If creating the calendar event fails, keep the booking and flag it for the team (as today).
- Also check the host's Google Calendar busy times for the next 14 days (Calendar freeBusy through the existing connector), and treat busy times as unavailable, so personal events block slots too. Cache this for 5 minutes. If the connector call fails, fall back to database bookings only.
- Public read: a server function returns only the start times (UTC) of taken slots for the next 14 days. No names, emails or other details. RLS stays as it is: anonymous users can't read the bookings table.
- UI: taken slots show "Booked" and are disabled (aria-disabled, not just greyed). The picker refreshes taken slots when the panel opens and just before submitting. If submit returns slot_taken: "Someone just booked that time. Please pick another." Then refresh the slots and keep the visitor's form details.
- Team area: when a booking is cancelled, its slot becomes free again.

3. TESTS
- SLOTS_IST matches the list above; no Sunday (IST) slots; at least 12 hours' notice.
- visibleSlots: Sydney sees 12:00, 12:30, 13:00; London sees 12:30-16:00; New York (EDT and EST dates) sees the morning slots from 08:00; India sees 18:00-21:30 only.
- Defaults per market.
- Two concurrent bookings for the same slot: exactly one succeeds and the other gets slot_taken; only one calendar event is created.
- A cancelled booking frees the slot.
- The public taken-slots function returns times only.

Run the full test suite and the type check. Check the booking panel at 375px and 1280px in light and dark mode for each time zone button (axe, no horizontal scroll). Make one real test booking and confirm that a second booking for the same slot is refused. Then delete the test booking and its calendar event. Report the results. Do not publish.
```
