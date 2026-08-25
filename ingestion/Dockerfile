FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project metadata
COPY pyproject.toml uv.lock README.md ./

# Copy Python source BEFORE uv sync
COPY src ./src

# Install dependencies + project
RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "-m", "idfm_ingestion.main"]