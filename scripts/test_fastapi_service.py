"""Smoke-test script for the FastAPI SMS spam classification endpoint via curl."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys


DEFAULT_MESSAGES = [
    "URGENT: You won a cash prize! Open http://spam.test and claim now.",
    "Yo, i will be back in 5 minutes.",
]


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the FastAPI smoke test."""

    parser = argparse.ArgumentParser(description="Send test requests to the FastAPI classifier.")
    parser.add_argument(
        "--base-url",
        default=os.getenv("FASTAPI_URL", "http://localhost:8000"),
        help="Base URL of the FastAPI service.",
    )
    parser.add_argument(
        "--message",
        action="append",
        default=[],
        help="SMS message to classify. Can be passed multiple times.",
    )
    return parser.parse_args()


def send_classification_request(base_url: str, message: str) -> dict:
    """Send a classification request to the FastAPI service using curl."""

    request_body = json.dumps({"message": message})
    completed_process = subprocess.run(
        [
            "curl",
            "--silent",
            "--show-error",
            "--fail",
            f"{base_url}/classify",
            "-H",
            "Content-Type: application/json",
            "-d",
            request_body,
        ],
        capture_output=True,
        check=True,
        text=True,
    )
    return json.loads(completed_process.stdout)


def main() -> int:
    """Execute the FastAPI smoke test for one or more SMS samples."""

    args = parse_args()
    messages = args.message or DEFAULT_MESSAGES

    for message in messages:
        try:
            response = send_classification_request(args.base_url, message)
        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as exc:
            print(f"Failed to call FastAPI service: {exc}", file=sys.stderr)
            return 1

        print(json.dumps({"message": message, "response": response}, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
