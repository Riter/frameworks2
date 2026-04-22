"""Smoke-test script for direct access to the Ollama HTTP API via curl."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the Ollama smoke test."""

    parser = argparse.ArgumentParser(description="Send a direct test request to Ollama.")
    parser.add_argument(
        "--base-url",
        default=os.getenv("OLLAMA_URL", "http://localhost:11434"),
        help="Base URL of the Ollama server.",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b"),
        help="Model name to invoke on the Ollama server.",
    )
    parser.add_argument(
        "--prompt",
        default="Classify this SMS as spam or ham: WIN a free iPhone now! Click http://scam.test",
        help="Prompt to send to the model.",
    )
    return parser.parse_args()


def send_generate_request(base_url: str, model: str, prompt: str) -> dict:
    """Send a non-streaming generate request to the Ollama HTTP API using curl."""

    request_body = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
    )
    completed_process = subprocess.run(
        [
            "curl",
            "--silent",
            "--show-error",
            "--fail",
            f"{base_url}/api/generate",
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
    """Execute the Ollama smoke test and print the JSON response."""

    args = parse_args()

    try:
        response = send_generate_request(args.base_url, args.model, args.prompt)
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Failed to call Ollama: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
