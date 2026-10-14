FROM python:3.13-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --locked

RUN uv run playwright install --with-deps firefox

COPY . .

EXPOSE 8000

ENV PYTHONPATH=/app/src
CMD ["uv", "run", "fastapi", "run" ,"src/__main__.py", "--host", "0.0.0.0"]
