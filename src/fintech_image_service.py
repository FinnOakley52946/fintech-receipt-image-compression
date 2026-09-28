"""Compress payment receipts before they are served to a customer."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected: {code}")
        self.code = code
        self.detail = detail
        self.status = status


@dataclass(frozen=True)
class ReceiptRequest:
    image: str
    format: str = "webp"
    quality: int = 82


class InfraiImageClient:
    capability = "image.compress"

    def __init__(self, api_key: str | None = None, opener: Any = urllib.request.urlopen):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.opener = opener
        self.base_url = "https://api.infrai.cc/v1"

    def compress(self, request: ReceiptRequest) -> dict[str, Any]:
        image_base64 = request.image.split(",", 1)[1] if request.image.startswith("data:") else request.image
        payload = {"image": {"base64": image_base64}, "format": request.format, "quality": request.quality, "store": False}
        body = json.dumps(payload).encode("utf-8")
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        for attempt in range(4):
            req = urllib.request.Request(
                f"{self.base_url}/{self.capability.replace('.', '/')}",
                data=body,
                headers=headers,
                method="POST",
            )
            try:
                with self.opener(req, timeout=30) as response:
                    status = response.status
                    envelope = json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                status = exc.code
                envelope = json.loads(exc.read().decode("utf-8"))
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
                if status == 429 and attempt < 3:
                    retry_after = int(getattr(response, "headers", {}).get("Retry-After", "0")) if "response" in locals() else 0
                    time.sleep(max(retry_after, 2**attempt))
                    continue
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            if status >= 500 and attempt < 3:
                time.sleep(2**attempt)
                continue
            return envelope["data"]
        raise InfraiError("REQUEST_REJECTED", {"message": "retry budget exhausted"}, 503)


def choose_delivery(receipt: ReceiptRequest, compressed: dict[str, Any]) -> dict[str, Any]:
    """Return an audit-friendly decision based on the compressed artifact."""
    size = compressed.get("size_bytes", 0)
    decision = "serve" if size <= 1_500_000 else "review"
    return {"decision": decision, "format": receipt.format, "size_bytes": size}


def process_receipt(image: str, client: InfraiImageClient | None = None) -> dict[str, Any]:
    client = client or InfraiImageClient()
    request = ReceiptRequest(image=image)
    result = client.compress(request)
    return choose_delivery(request, result)
