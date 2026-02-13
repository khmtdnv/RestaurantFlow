FROM python:3.13-slim AS builder

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"
RUN poetry config virtualenvs.in-project true
WORKDIR /app
COPY poetry.lock pyproject.toml /app/
RUN poetry install --only main --no-interaction --no-ansi --no-root

FROM builder AS dev

COPY . /app
RUN poetry install --only dev --no-interaction --no-ansi --no-root
ENV PATH="/app/.venv/bin:$PATH"

FROM builder AS prod

COPY . /app
ENV PATH="/app/.venv/bin:$PATH"

