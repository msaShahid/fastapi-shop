FROM python:3.12-slim

WORKDIR /code

# System deps needed to build some Python packages (e.g. asyncpg, argon2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first (separate layer) so Docker can cache this
# step and skip it on rebuilds where only application code changed.
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
