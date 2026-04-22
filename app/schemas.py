"""Pydantic schemas used by the FastAPI service and Ollama integration."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, StringConstraints


NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ClassificationRequest(BaseModel):
    """Represents the inbound payload with an SMS message to classify."""

    message: NonEmptyString


class LLMClassificationPayload(BaseModel):
    """Represents the structured JSON payload expected from the LLM."""

    model_config = ConfigDict(extra="forbid")

    label: Literal["spam", "ham"]
    explanation: NonEmptyString


class ClassificationResponse(LLMClassificationPayload):
    """Represents the public API response returned by the FastAPI service."""

    model: str


def build_classification_format_schema() -> dict:
    """Return the JSON schema used by Ollama structured generation."""

    schema = LLMClassificationPayload.model_json_schema()
    schema["title"] = "SmsSpamClassification"
    return schema

