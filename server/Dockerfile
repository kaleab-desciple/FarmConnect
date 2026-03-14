FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies required for PostgreSQL adapters (psycopg2/asyncpg)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for quicktype (TypeScript generation)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Python tools for model generation
RUN pip install --no-cache-dir datamodel-code-generator "pydantic[dotenv]" jsonschema

# Install quicktype globally for TypeScript generation
RUN npm install -g quicktype

COPY server/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy shared schemas and scripts for model generation
COPY shared/schemas /app/shared/schemas
COPY shared/scripts /app/shared/scripts

# Generate Python and TypeScript models from schemas
# Models are generated to /app/shared/py/shared_models and /app/shared/ts
RUN cd /app/shared/scripts && bash generate_models.sh

# Copy server application code to /app
COPY server/ /app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
