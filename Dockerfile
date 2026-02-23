FROM python:3.13-slim AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"
WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# ИЗМЕНЕНИЕ 3: Устанавливаем зависимости
RUN poetry install --only main --no-interaction --no-ansi --no-root

# -------------------------------------------------------------------------
# Stage 2: Development
# -------------------------------------------------------------------------
FROM builder AS dev

# Доустанавливаем dev-зависимости
RUN poetry install --only dev --no-interaction --no-ansi --no-root

COPY . .

# Добавляем venv в PATH
ENV PATH="/opt/venv/bin:$PATH"

# Теперь uvicorn можно вызывать просто по имени, без полного пути
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# -------------------------------------------------------------------------
# Stage 3: Production
# -------------------------------------------------------------------------
FROM python:3.13-slim AS prod

WORKDIR /app

# Копируем venv из builder
COPY --from=builder /opt/venv /opt/venv

COPY . .

# Добавляем venv в PATH
ENV PATH="/opt/venv/bin:$PATH"

RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Запускаем через gunicorn (он уже будет в PATH)
CMD ["gunicorn", "src.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]