#!/bin/bash

# Script to stop the entire Reflectly application with big data infrastructure

echo "Stopping Reflectly application..."

# Find and kill frontend process (npm)
echo "Stopping frontend..."
pkill -f "node.*start"

# Find and kill backend process (Flask)
echo "Stopping backend..."
pkill -f "python.*app.py"

# Stop Docker containers
echo "Stopping Docker containers..."
docker-compose down

echo "All Reflectly components have been stopped."
