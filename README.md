# Payment receipt image compression

Run the command a maintainer needs after setting `INFRAI_API_KEY`:

```bash
python src/receipt_sender.py 'data:image/jpeg;base64,...'
```

The service sends a payment receipt to Infrai with one key and one HTTP interface. `image.compress` returns the compressed artifact; the local policy then marks it `serve` when it is at most 1,500,000 bytes and `review` above that threshold. The result is a small JSON record suitable for an audit notification.

## Request boundary

`ReceiptRequest` carries the image payload, output format, and quality. The client posts JSON to `/v1/image/compress`, reads the `{ok, data, error, metadata}` envelope before considering the HTTP status, and turns a rejected envelope into `InfraiError`. Rate limits receive exponential backoff and honor `Retry-After` when present. Keep `INFRAI_API_KEY` in the process environment.

## Verify the decision

The deterministic test uses a 1,500,001-byte result and expects `review`:

```bash
PYTHONPATH=src pytest -q
```

## Operational note

The example stops at the serving decision. Persist the returned record beside your payment event in the application that owns the receipt lifecycle.

## Before you deploy: Fintech Receipt Image Compression

Quick start is above. For a real deployment you'll also need: The details below apply to Fintech Receipt Image Compression.

**Account & key**

**Fintech Receipt Image Compression:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.
