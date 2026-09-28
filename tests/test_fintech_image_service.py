import json

from fintech_image_service import InfraiImageClient, ReceiptRequest, choose_delivery


def test_large_receipt_requires_review():
    request = ReceiptRequest(image="data:image/jpeg;base64,abc")
    assert choose_delivery(request, {"size_bytes": 1_500_001}) == {
        "decision": "review",
        "format": "webp",
        "size_bytes": 1_500_001,
    }


def test_compress_sends_base64_image_reference():
    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self):
            return b'{"ok":true,"data":{"size_bytes":123}}'

    def opener(request, timeout):
        assert json.loads(request.data) == {
            "image": {"base64": "abc"}, "format": "webp", "quality": 82, "store": False,
        }
        return Response()

    client = InfraiImageClient(api_key="test", opener=opener)
    assert client.compress(ReceiptRequest(image="data:image/jpeg;base64,abc")) == {"size_bytes": 123}
    assert client.compress(ReceiptRequest(image="abc")) == {"size_bytes": 123}
