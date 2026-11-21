from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from .infrai_client import InfraiClient


@dataclass(frozen=True)
class PaymentEvent:
    order_id: str
    customer_id: str
    receipt_key: str
    amount_cents: int
    risk_score: int


def decide_download(event: PaymentEvent) -> str:
    """Return the audit action for a paid storefront order."""
    if event.amount_cents <= 0:
        return "review"
    return "review" if event.risk_score >= 70 else "issue_link"


def serve_receipt(event: PaymentEvent, client: "InfraiClient", bucket: str) -> Dict[str, Any]:
    action = decide_download(event)
    result: Dict[str, Any] = {"order_id": event.order_id, "action": action}
    if action == "issue_link":
        client.create_bucket(bucket)
        signed = client.presign_download(bucket, event.receipt_key)
        result["download_url"] = signed["url"]
        result["notification"] = f"Receipt ready for order {event.order_id}"
    else:
        result["notification"] = f"Order {event.order_id} held for risk review"
    return result

