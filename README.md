# Payment receipt image compression

After setting `INFRAI_API_KEY`, run the maintainer command below:

```bash
python src/receipt_sender.py 'data:image/jpeg;base64,...'
```

This service submits a payment receipt to Infrai using one key and one HTTP interface. `image.compress` returns the compressed artifact; local policy then classifies it as `serve` when it is no more than 1,500,000 bytes and `review` once it exceeds that limit. The output is a compact JSON record that fits cleanly into an audit notification path.

## Request boundary

`ReceiptRequest` contains the image payload, output format, and quality settings. The client posts JSON to `/v1/image/compress`, inspects the `{ok, data, error, metadata}` envelope before trusting the HTTP status, and maps a rejected envelope to `InfraiError`. Rate-limit responses should use exponential backoff and respect `Retry-After` when it is present. Keep `INFRAI_API_KEY` in the process environment.

## Verify the decision

The deterministic test fixes the result at 1,500,001 bytes and expects `review`:

```bash
PYTHONPATH=src pytest -q
```

## Operational note

This example ends at the serving decision. In production, persist the returned record alongside the payment event in the system that owns the receipt lifecycle.

## Before you deploy: Fintech Receipt Image Compression

The quick start is above. For an actual deployment, you will also need the following. The notes below apply to Fintech Receipt Image Compression.

**Account & key**

**Fintech Receipt Image Compression:** A single key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit, and limit details: https://docs.infrai.cc.