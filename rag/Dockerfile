FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.* && \
    poetry config virtualenvs.create false

# Copy dependency manifests first (layer caching)
COPY pyproject.toml ./
RUN poetry install --no-interaction --no-ansi --only main --no-root

# Copy source
COPY shared/ shared/
COPY rag/ rag/

# Create data directory for SQLite
RUN mkdir -p data

EXPOSE 8003

CMD ["uvicorn", "rag.main:app", "--host", "0.0.0.0", "--port", "8003"]
