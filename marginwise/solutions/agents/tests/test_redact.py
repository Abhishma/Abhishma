from core.redact import redact, redact_text


def test_redacts_email_phone_card_iban():
    text = ("Mail jo@example.com, call +61 412 345 678 or 0412 345 678, card 4111 1111 1111 1111, "
            "IBAN DE89 3704 0044 0532 0130 00")
    out = redact_text(text)
    for secret in ("jo@example.com", "412 345 678", "4111 1111 1111 1111", "DE89 3704"):
        assert secret not in out
    assert "[REDACTED:EMAIL]" in out and "[REDACTED:CARD]" in out and "[REDACTED:IBAN]" in out


def test_keeps_dates_order_ids_and_amounts():
    text = "Order 5710001042001 on 2026-10-17 for 1,234.50 AUD, payout P-SHP-1001, ref #1042"
    assert redact_text(text) == text


def test_sensitive_keys_masked_recursively():
    data = {"phone": "+966501234567", "nested": [{"email": "x@y.com", "city": "Riyadh"}], "note": "ok"}
    out = redact(data)
    assert out["phone"] == "[REDACTED]"
    assert out["nested"][0]["email"] == "[REDACTED]"
    assert out["nested"][0]["city"] == "Riyadh"
