# Receptionist: AI phone/SMS receptionist and missed-call text-back

## What it does
Answers inbound calls and SMS for trades and clinics, books jobs into the field-service or practice system, captures leads, sends missed-call text-backs within 60 seconds, and warm-transfers emergencies to the on-call person. Discloses that it is an AI in every conversation (EU AI Act Art. 50 for Germany). English and German variants.

## Integrations
- AU/NZ: ServiceM8, simPRO, Tradify
- US/CA: Jobber, Housecall Pro, ServiceTitan
- DE: Doctolib-style booking calendars (clinics), Google Calendar / Outlook for small trades
- Voice and SMS: Twilio, Vapi / Retell (voice layer), MessageMedia (AU), sipgate (DE)

## KPIs
- Missed-call rate (target: under 5% of calls without a next step)
- Speed to text-back (target: under 60 seconds)
- Booking conversion from inbound calls and texts
- After-hours jobs booked per month
- Emergency transfer time (target: under 30 seconds)
- Price-guide compliance (quotes outside guide: 0)

## Setup
1. Load the client's price guide, service area postcodes, hours and emergency keywords into the business profile (see fixtures/businesses.json for the shape).
2. Implement the TODO adapters in handlers.py for the client's platform (book_job, check_availability, create_lead) and SMS provider.
3. Register SMS sender IDs per market (AU sender ID register, US A2P 10DLC) and confirm call-recording notices in the telephony layer.
4. Have a native speaker review the German phrases in prompt.md.
5. Run the scripted test calls in tests/ plus 20 live test calls before go-live.

## Guardrails
- AI disclosure in the first message; never claims to be human.
- Prices only from get_price_guide; no estimates.
- Emergency keywords trigger transfer_to_human with safety instructions first.
- No payment details taken; SMS only to the caller's own number, transactional only.
- Transcripts are PII-redacted by the core runner.

## Price (USD)
$2,500-6,000 setup + $300-900/month (plus telephony and model usage at cost).
