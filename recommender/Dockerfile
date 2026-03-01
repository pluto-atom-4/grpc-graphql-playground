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
COPY recommender/app/entry/start.sh ./start.sh

# Install Python dependencies with uv
RUN pip install uv && uv sync --no-dev

# Make start script executable
RUN chmod +x ./start.sh

# Expose gRPC port
EXPOSE 50051

# Start both gRPC server and Kafka consumer
CMD ["bash", "./start.sh"]
