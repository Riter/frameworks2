"""FastAPI application exposing SMS spam classification backed by Ollama."""

from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException

from app.ollama_client import OllamaClient, OllamaClientError, OllamaSettings
from app.schemas import ClassificationRequest, ClassificationResponse


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""

    settings = OllamaSettings(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
        model=os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b"),
    )
    ollama_client = OllamaClient(settings)

    application = FastAPI(
        title="SMS Spam Detection PoC",
        description="FastAPI wrapper around Ollama Qwen2.5:0.5B for SMS spam classification.",
        version="1.0.0",
    )

    @application.post("/classify", response_model=ClassificationResponse)
    async def classify_sms(payload: ClassificationRequest) -> ClassificationResponse:
        """Classify an SMS message as spam or ham using the local Ollama model."""

        try:
            result = await ollama_client.classify_message(payload.message)
        except OllamaClientError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        return ClassificationResponse(
            label=result.label,
            explanation=result.explanation,
            model=settings.model,
        )

    return application


app = create_app()

