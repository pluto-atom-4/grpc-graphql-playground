#!/bin/bash
# Entrypoint script to start both gRPC server and Kafka consumer

set -e

echo "Starting Recommender Service..."

# Wait for database
echo "Initializing database..."
python -m app.entry.main &
GRPC_PID=$!

# Wait for gRPC server to start
sleep 2

echo "Starting Kafka consumer..."
python -m app.entry.sync &
CONSUMER_PID=$!

# Wait for both processes
wait $GRPC_PID $CONSUMER_PID

echo "Recommender Service stopped"
