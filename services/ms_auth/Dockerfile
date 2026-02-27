FROM python:3.13-slim AS builder
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_NO_INTERACTION=1 \
    VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl build-essential && \
    rm -rf /var/lib/apt/lists/*
RUN pip install poetry
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN python -m venv $VIRTUAL_ENV
RUN poetry install --only main --no-root


FROM builder AS dev
RUN poetry install --no-root
# ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app/src
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM python:3.13-slim AS prod
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"
COPY --from=builder /opt/venv /opt/venv
COPY src /app/src
WORKDIR /app/src
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser
CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]