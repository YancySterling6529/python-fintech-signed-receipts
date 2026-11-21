from src.fintech_service import PaymentEvent, decide_download


def test_high_risk_payment_is_held_before_link_issuance():
    event = PaymentEvent("ord_risky", "cust_7", "receipts/risky.pdf", 5000, 82)
    assert decide_download(event) == "review"

