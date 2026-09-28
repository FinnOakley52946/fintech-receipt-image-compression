import argparse
import json

from fintech_image_service import process_receipt


def main() -> None:
    parser = argparse.ArgumentParser(description="Compress a payment receipt image")
    parser.add_argument("image", help="base64 image payload or a data URL")
    args = parser.parse_args()
    print(json.dumps(process_receipt(args.image), indent=2))


if __name__ == "__main__":
    main()

