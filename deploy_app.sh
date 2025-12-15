#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed, please install Docker first"
    exit 1
fi

# Build the image
echo "Building Docker image..."
docker build -t visco-secure-app:v1 .

# Stop and remove the old container
if docker ps -a --format '{{.Names}}' | grep -q 'visco-app'; then
    echo "Stopping old container..."
    docker stop visco-app
    docker rm visco-app
fi

# Start the new container (production environment)
echo "Starting new container..."
docker run -d \
  -p 5001:5001 \
  -e FLASK_ENV=prod \
  -e SECRET_KEY=$(cat .env | grep SECRET_KEY | cut -d '=' -f2) \
  -e ENCRYPTION_KEY=$(cat .env | grep ENCRYPTION_KEY | cut -d '=' -f2) \
  -e DATABASE_URL=sqlite:///visco_prod.db \
  -v $(pwd)/visco_prod.db:/app/visco_prod.db \
  --user 1001:1001 \
  --name visco-app \
  visco-secure-app:v1

echo "Deployment successful! Application address: http://localhost:5001"