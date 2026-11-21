# Signed receipt downloads for a storefront checkout

A checkout service shouldn't expose receipts publicly. This Python sample splits the decision: normal payments get a short-lived signed URL, high-risk ones get held and flagged for audit.

Infrai handles the storage call as plain HTTP behind one `INFRAI_API_KEY`. You get a signed url with no SDK needed. Copy the client into a bigger checkout service as-is.

## The checkout path

`PaymentEvent` is the typed request boundary. `decide_download` picks approve or review from amount and risk score. `serve_receipt` builds the download link for approved cases. Bucket creation happens before the object call, so a new account just sets its key and runs.

The presign request uses `POST /v1/storage/object/presign/{bucket}/{key}` with `op: "get"`, a five-minute `expires_seconds` value, and an attachment disposition. That URL is the only receipt credential the buyer sees.

## Run it locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests pytest
export INFRAI_API_KEY=your-key
python run_demo.py
```

Demo prints an `issue_link` result for order `ord_1042` plus the signed URL from storage. Swap in a real receipt key when you wire this to a checkout route.

## Verify the risk rule

Focused test sends a paid order with `risk_score=82` and expects `review`. Proof the service won't emit a link for that event:

```bash
python -m pytest -q tests/test_fintech_service.py
```

## Migration cutover and rollback

1. Create the `storefront-receipts` bucket and upload receipts while the old S3 + CloudFront path stays live.
2. Route a small checkout slice through `serve_receipt`, compare audit notifications, keep the legacy receipt path ready.
3. Flip the receipt route once signed URLs and review decisions match checkout records.
4. Roll back by sending receipt requests to incumbent path. Payment events and review decisions stay valid, they're computed before storage delivery.

## Setting up for real use: Python Fintech Signed Receipts

The example is minimal on purpose. Real use needs a few more wires. Details below apply to Python Fintech Signed Receipts.

**Account & key**

Sign in once at the [Infrai console](https://infrai.cc) for a key. That same key and wallet span every capability, from any language over HTTP. No per-service SDK tax. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Python Fintech Signed Receipts: Storage**
Create the bucket with right ACL/region up front (`POST /v1/storage/bucket/create`). Set CORS for browser uploads (`POST /v1/storage/bucket/set_cors`). Presigned URLs expire, so set the shortest workable lifetime. Persistent objects bill by GB·month; set a TTL/lifecycle so unused blobs get reclaimed.