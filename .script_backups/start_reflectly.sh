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
    echo ""
    echo "Example:"
    echo "  $0                    Start everything"
    echo "  $0 --skip-docker      Start everything except Docker containers"
}

# Parse command line arguments
SKIP_DOCKER=false
SKIP_BACKEND=false
SKIP_FRONTEND=false
SKIP_COPY_JOBS=false

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
        *)
            echo "Error: Unknown option: $key"
            display_usage
            exit 1
            ;;
    esac
done

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
