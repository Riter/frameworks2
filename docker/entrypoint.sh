#!/usr/bin/env sh
set -eu

export OLLAMA_HOST="${OLLAMA_HOST:-0.0.0.0:11434}"
export OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11434}"
export OLLAMA_MODEL="${OLLAMA_MODEL:-qwen2.5:0.5b}"

echo "Starting Ollama on ${OLLAMA_HOST}..."
ollama serve >/tmp/ollama.log 2>&1 &

echo "Waiting for Ollama HTTP API..."
until curl --silent --fail "${OLLAMA_BASE_URL}/api/tags" >/dev/null; do
  sleep 2
done

echo "Pulling model ${OLLAMA_MODEL}..."
ollama pull "${OLLAMA_MODEL}"

echo "Starting FastAPI service on 0.0.0.0:8000..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

