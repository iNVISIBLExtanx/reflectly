#!/bin/bash

# Script to update Docker images with the latest code changes and clean up old images

echo "Updating Docker images with latest code changes..."

# Apply all fixes first
echo "Applying all fixes..."
python fix_all_issues.py

# Save list of current images before building
echo "Saving list of current images..."
OLD_IMAGES=$(docker images -q refection_backend refection_frontend)

# Rebuild and update Docker images
echo "Rebuilding Docker images..."

# Fix Docker build context for backend
echo "Fixing Docker build context for backend..."
./fix_docker_build.sh

# Build frontend
echo "Building frontend..."
docker-compose build --no-cache frontend

# Clean up old images (dangling images)
echo "Cleaning up old and dangling images..."

# Remove old backend and frontend images
if [ ! -z "$OLD_IMAGES" ]; then
    echo "Removing old application images..."
    for img in $OLD_IMAGES; do
        docker rmi $img 2>/dev/null || true
    done
fi

# Remove dangling images (untagged images)
echo "Removing dangling images..."
docker image prune -f

echo "Docker images updated successfully and old images cleaned up!"
echo "Disk space freed. You can now run ./start_reflectly.sh to start the application with the updated images."
