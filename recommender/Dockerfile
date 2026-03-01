FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY recommender/pyproject.toml .
COPY recommender/app ./app
COPY recommender/generated ./generated
COPY recommender/tests ./tests

# Install Python dependencies with uv
RUN pip install uv && uv sync --no-dev

# Expose gRPC port
EXPOSE 50051

# Start the gRPC server
CMD ["python", "-m", "app.entry.main"]
