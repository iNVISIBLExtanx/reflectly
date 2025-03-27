#!/bin/bash

# Script to fix Docker build context issues

echo "Fixing Docker build context issues..."

# Create a temporary directory for the build context
echo "Creating temporary build context..."
mkdir -p /tmp/reflectly_build_context

# Copy backend files to the temp directory
echo "Copying backend files..."
cp -r backend/* /tmp/reflectly_build_context/

# Copy AI modules to the temp directory
echo "Copying AI modules..."
mkdir -p /tmp/reflectly_build_context/ai
cp -r ai/* /tmp/reflectly_build_context/ai/

# Ensure proper Python package structure
echo "Creating Python package structure..."
touch /tmp/reflectly_build_context/ai/__init__.py
touch /tmp/reflectly_build_context/ai/search/__init__.py
touch /tmp/reflectly_build_context/ai/probabilistic/__init__.py
touch /tmp/reflectly_build_context/ai/agent/__init__.py

# Update the Dockerfile to use the correct paths
echo "Updating Dockerfile..."
cat > /tmp/reflectly_build_context/Dockerfile << EOF
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Run the fix script
RUN python /app/docker_fix_unknown_emotions.py

EXPOSE 5002

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5002"]
EOF

# Build the Docker image from the temp directory
echo "Building Docker image from fixed context..."
docker build -t refection_backend:latest /tmp/reflectly_build_context

# Tag the image for docker-compose
echo "Tagging the image for docker-compose..."
docker tag refection_backend:latest refection-backend:latest

echo "Docker build context fixed and image built successfully!"
echo "You can now run ./start_reflectly.sh to start the application."
