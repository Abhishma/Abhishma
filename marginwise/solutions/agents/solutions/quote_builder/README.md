# Quote Builder: instant estimates and site-visit booking for trades

## What it does
An instant quote agent for trade businesses (air-con installs, roofing repairs, electrical work). It maps the customer's job to price book items, asks only the required questions, calculates a price range deterministically (quote.py: ranges, minimum charges, GST/USt), produces a PDF-ready JSON estimate, and books a site visit. For German businesses it produces a formal "Angebot" (binding offer) when every line has a fixed price, validating the mandatory fields of the template (Angebotsnummer, Datum, Gueltig bis, Anbieter with Steuernummer/USt-IdNr, Kunde, Positionen, Netto, USt-Satz and Betrag, Brutto, Zahlungsbedingungen, Kleinunternehmer note where applicable).

## Integrations
- AU/NZ: ServiceM8, simPRO, Tradify (quotes and jobs)
- US/CA: Jobber, Housecall Pro, ServiceTitan (estimates)
- DE: lexoffice, sevDesk, Billomat (Angebote)
- Web chat widget, SMS, Facebook/Instagram messages; PDF rendering via template service

## KPIs
- Quote requests answered instantly (target 100%, 24/7)
- Estimate-to-site-visit conversion rate
- Quote accept rate and average job value
- Estimator hours saved; price disputes from instant quotes (target: 0)

## Setup
1. Build the price book with the owner: items, units, low/high ex-tax prices, required questions, minimum charges, site-visit flags.
2. Configure business details (ABN / USt-IdNr / Steuernummer, licences, validity, tax).
3. Implement TODO adapters in handlers.py for the FSM / invoicing platform and calendar.
4. German businesses: native review of the German phrases and the Angebot template; confirm template fields with their Steuerberater.

## Guardrails
- Prices only from the deterministic calculator; no discounts or off-book figures.
- Angebot only with fixed prices; ranged jobs go out as estimates with a site visit.
- Safety issues and complex/commercial jobs transfer to a human.
- AI disclosure at the start of every conversation.

## Price (USD)
$3,000-9,000 setup + $300-800/month.
