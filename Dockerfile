FROM python:3.13-slim AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl build-essential && \
    rm -rf /var/lib/apt/lists/*
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"
WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.in-project true
RUN poetry install --only main --no-interaction --no-ansi --no-root

FROM builder AS dev

RUN poetry install --only dev --no-interaction --no-ansi --no-root
COPY . .
ENV PATH="/app/.venv/bin:$PATH"

FROM python:3.13-slim AS prod

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . .
ENV PATH="/app/.venv/bin:$PATH"
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser