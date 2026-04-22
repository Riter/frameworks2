"""HTTP client for interacting with the local Ollama server."""

from __future__ import annotations

import json
from dataclasses import dataclass

import httpx
from pydantic import ValidationError

from app.prompting import SYSTEM_PROMPT, build_user_prompt
from app.schemas import LLMClassificationPayload, build_classification_format_schema


class OllamaClientError(RuntimeError):
    """Raised when the Ollama server returns an unusable response."""


@dataclass(slots=True)
class OllamaSettings:
    """Stores runtime settings required for accessing the Ollama server."""

    base_url: str
    model: str
    timeout_seconds: float = 120.0


class OllamaClient:
    """Wraps Ollama HTTP calls needed by the SMS spam classification service."""

    def __init__(self, settings: OllamaSettings) -> None:
        """Initialize the client with immutable runtime settings."""

        self._settings = settings

    async def classify_message(self, message: str) -> LLMClassificationPayload:
        """Classify an SMS message by calling Ollama structured generation."""

        payload = {
            "model": self._settings.model,
            "prompt": build_user_prompt(message),
            "system": SYSTEM_PROMPT,
            "stream": False,
            "format": build_classification_format_schema(),
        }

        try:
            async with httpx.AsyncClient(timeout=self._settings.timeout_seconds) as client:
                response = await client.post(
                    f"{self._settings.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise OllamaClientError(f"Failed to reach Ollama: {exc}") from exc

        return self._parse_response(response)

    def _parse_response(self, response: httpx.Response) -> LLMClassificationPayload:
        """Validate and convert the Ollama HTTP response into a typed payload."""

        try:
            body = response.json()
        except ValueError as exc:
            raise OllamaClientError("Ollama returned a non-JSON HTTP response.") from exc

        llm_response = body.get("response")
        if not isinstance(llm_response, str):
            raise OllamaClientError("Ollama response does not contain a string 'response' field.")

        try:
            parsed_payload = json.loads(llm_response)
        except json.JSONDecodeError as exc:
            raise OllamaClientError("Ollama returned invalid JSON in the generated response.") from exc

        try:
            return LLMClassificationPayload.model_validate(parsed_payload)
        except ValidationError as exc:
            raise OllamaClientError("Ollama returned JSON that does not match the schema.") from exc

