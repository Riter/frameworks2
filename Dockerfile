FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    curl \
    python3 \
    python3-pip \
    python3-venv \
    zstd \
    && rm -rf /var/lib/apt/lists/*

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN arch="$(dpkg --print-architecture)" \
    && case "${arch}" in \
        amd64) ollama_arch="amd64" ;; \
        arm64) ollama_arch="arm64" ;; \
        *) echo "Unsupported architecture: ${arch}" >&2; exit 1 ;; \
      esac \
    && curl --fail --location --progress-bar \
      "https://ollama.com/download/ollama-linux-${ollama_arch}.tar.zst" \
      --output /tmp/ollama.tar.zst \
    && tar --use-compress-program=unzstd -xf /tmp/ollama.tar.zst -C /usr \
    && rm -f /tmp/ollama.tar.zst \
    && command -v ollama \
    && ollama --version

COPY requirements.txt ./requirements.txt

RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY docker ./docker

RUN chmod +x /app/docker/entrypoint.sh

EXPOSE 8000 11434

CMD ["/app/docker/entrypoint.sh"]
