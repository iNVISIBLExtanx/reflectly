#!/bin/bash

# Script to start the entire Reflectly application with big data infrastructure

# Function to display usage
function display_usage {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --help                Display this help message"
    echo "  --skip-docker         Skip starting Docker containers"
    echo "  --skip-backend        Skip starting the backend"
    echo "  --skip-frontend       Skip starting the frontend"
    echo "  --skip-copy-jobs      Skip copying Spark jobs"
    echo "  --update-docker       Update Docker images before starting"
    echo "  --cleanup-docker      Clean up all Docker resources (containers, images, volumes)"
    echo ""
    echo "Example:"
    echo "  $0                    Start everything"
    echo "  $0 --skip-docker      Start everything except Docker containers"
    echo "  $0 --update-docker    Update Docker images before starting"
    echo "  $0 --cleanup-docker   Clean up all Docker resources"
}

# Parse command line arguments
SKIP_DOCKER=false
SKIP_BACKEND=false
SKIP_FRONTEND=false
SKIP_COPY_JOBS=false
UPDATE_DOCKER=false
CLEANUP_DOCKER=false

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --help)
            display_usage
            exit 0
            ;;
        --skip-docker)
            SKIP_DOCKER=true
            shift
            ;;
        --skip-backend)
            SKIP_BACKEND=true
            shift
            ;;
        --skip-frontend)
            SKIP_FRONTEND=true
            shift
            ;;
        --skip-copy-jobs)
            SKIP_COPY_JOBS=true
            shift
            ;;
        --update-docker)
            UPDATE_DOCKER=true
            shift
            ;;
        --cleanup-docker)
            CLEANUP_DOCKER=true
            shift
            ;;
        *)
            echo "Error: Unknown option: $key"
            display_usage
            exit 1
            ;;
    esac
done

# Clean up all Docker resources if requested
if [ "$CLEANUP_DOCKER" = true ]; then
    echo "Cleaning up all Docker resources..."
    
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
    
    echo "All Docker resources cleaned up successfully!"
    exit 0
fi

# Update Docker images if requested
if [ "$UPDATE_DOCKER" = true ]; then
    echo "Updating Docker images..."
    
    # Fixes have already been applied
    echo "All fixes have already been applied..."
    
    # Save list of current images before building
    echo "Saving list of current images..."
    OLD_IMAGES=$(docker images -q refection_backend refection_frontend)
    
    # Rebuild Docker images
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
fi

# Start Docker containers
if [ "$SKIP_DOCKER" = false ]; then
    echo "Starting Docker containers..."
    docker-compose up -d
    
    # Wait for containers to start
    echo "Waiting for containers to start..."
    sleep 10
else
    echo "Skipping Docker containers startup..."
fi

# Copy Spark jobs
if [ "$SKIP_COPY_JOBS" = false ]; then
    echo "Copying Spark jobs..."
    ./copy_spark_jobs.sh
else
    echo "Skipping copying Spark jobs..."
fi

# Start backend
if [ "$SKIP_BACKEND" = false ]; then
    echo "Starting backend..."
    cd backend
    ./start_backend.sh &
    cd ..
    
    # Wait for backend to start
    echo "Waiting for backend to start..."
    sleep 5
else
    echo "Skipping backend startup..."
fi

# Start frontend
if [ "$SKIP_FRONTEND" = false ]; then
    echo "Starting frontend..."
    cd frontend
    npm start &
    cd ..
else
    echo "Skipping frontend startup..."
fi

echo ""
echo "Reflectly application started!"
echo ""
echo "Access the application at: http://localhost:3000"
echo "Access Spark Master at: http://localhost:8080"
echo "Access Hadoop NameNode at: http://localhost:9870"
echo ""
echo "To stop the application, press Ctrl+C and then run: docker-compose down"
