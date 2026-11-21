import json

from src.fintech_service import PaymentEvent, serve_receipt
from src.infrai_client import InfraiClient


event = PaymentEvent("ord_1042", "cust_88", "receipts/ord_1042.pdf", 1299, 18)
print(json.dumps(serve_receipt(event, InfraiClient(), "storefront-receipts"), indent=2))

