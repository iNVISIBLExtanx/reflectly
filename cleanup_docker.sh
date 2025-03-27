#!/bin/bash

# Script to clean up Docker resources and free disk space

echo "Cleaning up Docker resources to free disk space..."

# Stop all containers
echo "Stopping all containers..."
docker-compose down

# Remove all application images
echo "Removing application images..."
docker rmi $(docker images -q refection_backend refection_frontend) 2>/dev/null || true

# Remove dangling images
echo "Removing dangling images..."
docker image prune -f

# Remove unused volumes
echo "Removing unused volumes..."
docker volume prune -f

# Remove unused networks
echo "Removing unused networks..."
docker network prune -f

# Show disk space before and after
echo "Docker system pruning (removing all unused containers, networks, images, and volumes)..."
docker system prune -f

# Show disk space information
echo "Current Docker disk usage:"
docker system df

echo "All Docker resources cleaned up successfully!"
echo "Disk space has been freed."
