FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Node.js 20 (for Gemini CLI and other Node-based tools)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g @google/gemini-cli && \
    apt-get purge -y curl && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.* && \
    poetry config virtualenvs.create false

# Copy dependency manifests first (layer caching)
COPY pyproject.toml ./
RUN poetry install --no-interaction --no-ansi --only main --no-root

# Copy source
COPY shared/ shared/
COPY cli_bridge/ cli_bridge/

EXPOSE 8002

CMD ["uvicorn", "cli_bridge.main:app", "--host", "0.0.0.0", "--port", "8002"]
