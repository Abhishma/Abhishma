"""Mock handlers for the AI receptionist.

Mocks read fixtures/businesses.json and keep bookings/leads/SMS in memory.
Each handler has a TODO pointing at the real adapter to implement per client:
  AU/NZ: ServiceM8, simPRO, Tradify      US/CA: Jobber, Housecall Pro, ServiceTitan
  DE:    Doctolib-style booking API        SMS:   Twilio / MessageMedia / sipgate
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path

from core.fixtures import load_json, not_found

FIXTURES = Path(__file__).parent / "fixtures"
BUSINESSES = load_json(FIXTURES / "businesses.json")

STATE: dict[str, list] = {"jobs": [], "leads": [], "sms": [], "transfers": []}
E164 = re.compile(r"^\+[1-9]\d{7,14}$")


def reset_state() -> None:
    for v in STATE.values():
        v.clear()


def _biz(business_id: str) -> dict | None:
    return BUSINESSES.get(business_id)


def check_availability(business_id: str, service: str, urgency: str = "standard") -> dict:
    # TODO(adapter): ServiceM8 GET /api_1.0/job.json + staff schedule; Jobber GraphQL
    # visits query; ServiceTitan Dispatch capacity API; Doctolib-style slot endpoint.
    biz = _biz(business_id)
    if not biz:
        return not_found("business", business_id)
    booked = {j["slot_id"] for j in STATE["jobs"]}
    slots = [s for s in biz["slots"] if service in s["services"] and s["slot_id"] not in booked]
    return {"found": True, "service": service, "urgency": urgency, "slots": slots[:3],
            "timezone": biz["timezone"], "note": "Offer at most 2-3 options."}


def book_job(business_id: str, slot_id: str, customer_name: str, phone: str,
             address: str, service: str, notes: str = "") -> dict:
    # TODO(adapter): ServiceM8 POST /job.json + /jobactivity.json; simPRO POST jobs;
    # Tradify job create; Housecall Pro POST /jobs; Jobber jobCreate mutation.
    biz = _biz(business_id)
    if not biz:
        return not_found("business", business_id)
    slot = next((s for s in biz["slots"] if s["slot_id"] == slot_id), None)
    if not slot:
        return {"booked": False, "error": "slot not found; call check_availability again"}
    if any(j["slot_id"] == slot_id for j in STATE["jobs"]):
        return {"booked": False, "error": "slot already taken"}
    if service not in slot["services"]:
        return {"booked": False, "error": f"slot does not offer {service}"}
    job = {"job_id": f"JOB-{uuid.uuid4().hex[:6].upper()}", "business_id": business_id,
           "slot_id": slot_id, "start": slot["start"], "customer_name": customer_name,
           "phone": phone, "address": address, "service": service, "notes": notes,
           "source": "ai_receptionist"}
    STATE["jobs"].append(job)
    return {"booked": True, "job_id": job["job_id"], "start": slot["start"], "end": slot["end"]}


def create_lead(business_id: str, name: str, phone: str, summary: str,
                service: str = "", postcode: str = "", channel: str = "phone") -> dict:
    # TODO(adapter): CRM/FSM lead endpoint (ServiceM8 "Quote" status job, Jobber request,
    # HubSpot contact + deal for clinics).
    if not _biz(business_id):
        return not_found("business", business_id)
    lead = {"lead_id": f"LEAD-{uuid.uuid4().hex[:6].upper()}", "business_id": business_id,
            "name": name, "phone": phone, "summary": summary, "service": service,
            "postcode": postcode, "channel": channel}
    STATE["leads"].append(lead)
    return {"created": True, "lead_id": lead["lead_id"]}


def send_sms(business_id: str, to: str, body: str) -> dict:
    # TODO(adapter): Twilio Messages API / MessageMedia (AU) / sipgate (DE). Register
    # alphanumeric sender IDs with the ACMA SMS Sender ID Register (AU) and A2P 10DLC (US)
    # before go-live; confirm current registration rules per market.
    biz = _biz(business_id)
    if not biz:
        return not_found("business", business_id)
    if not E164.match(to):
        return {"sent": False, "error": "phone must be E.164, e.g. +61412345678"}
    if len(body) > 480:
        return {"sent": False, "error": "message too long (max 480 characters / 3 segments)"}
    # Every outbound SMS identifies the business (Spam Act AU, CASL CA, TCPA US hygiene).
    if biz["name"].split()[0].lower() not in body.lower():
        body = f"{biz['name']}: {body}"
    msg = {"sms_id": f"SMS-{uuid.uuid4().hex[:6]}", "to": to, "body": body}
    STATE["sms"].append(msg)
    return {"sent": True, "sms_id": msg["sms_id"], "body": body}


def get_service_area(business_id: str, postcode: str) -> dict:
    biz = _biz(business_id)
    if not biz:
        return not_found("business", business_id)
    pc = postcode.strip().upper().replace(" ", "")
    areas = biz["service_area_postcodes"]
    # Canadian FSA matching uses the first 3 characters.
    in_area = pc in areas or pc[:3] in areas
    return {"postcode": pc, "in_service_area": in_area}


def get_price_guide(business_id: str, service: str) -> dict:
    # Only these prices may be quoted. Anything else: "the technician will confirm on site".
    biz = _biz(business_id)
    if not biz:
        return not_found("business", business_id)
    item = biz["price_guide"].get(service)
    if not item:
        return {"found": False, "service": service, "available_services": sorted(biz["price_guide"]),
                "instruction": "No approved price. Do not estimate; offer a booking or callback."}
    return {"found": True, "service": service, **item}


def transfer_to_human(business_id: str, reason: str, urgency: str = "normal", summary: str = "") -> dict:
    # TODO(adapter): telephony warm transfer (Twilio <Dial>, Aircall, 3CX) or on-call SMS page.
    biz = _biz(business_id)
    if not biz:
        return not_found("business", business_id)
    record = {"transfer_id": f"TR-{uuid.uuid4().hex[:6]}", "reason": reason,
              "urgency": urgency, "summary": summary, "to": biz["on_call_number"]}
    STATE["transfers"].append(record)
    return {"transferred": True, "transfer_id": record["transfer_id"], "urgency": urgency}


HANDLERS = {
    "check_availability": check_availability,
    "book_job": book_job,
    "create_lead": create_lead,
    "send_sms": send_sms,
    "get_service_area": get_service_area,
    "get_price_guide": get_price_guide,
    "transfer_to_human": transfer_to_human,
}
