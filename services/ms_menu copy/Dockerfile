ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -m -s /bin/bash appuser

WORKDIR /app

RUN pip install poetry && \
    poetry config virtualenvs.create false

COPY --chown=appuser:appgroup pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY --chown=appuser:appgroup src/ ./src

USER appuser

CMD ["uvicorn", "main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000", "--reload"]