FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.7 /uv /uvx /bin/

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    make \
    findutils \
    && rm -rf /var/lib/apt/lists/*

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked

COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini Makefile ./
