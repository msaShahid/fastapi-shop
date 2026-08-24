FROM python:3.12-slim

WORKDIR /code

# System deps needed to build some Python packages
# (e.g. asyncpg, argon2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install project dependencies first so Docker can cache
# this layer when only application code changes.
COPY pyproject.toml ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir . \
    && pip install --no-cache-dir pytest

# Copy application source
COPY ./app ./app
COPY ./tests ./tests

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
