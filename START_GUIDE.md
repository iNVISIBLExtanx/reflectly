# Reflectly Application Startup Guide

This guide explains how to start the Reflectly application with all the latest fixes and features.

## Starting the Application

### Option 1: Using Docker (Recommended)

The easiest way to start the application is using the `start_reflectly.sh` script with Docker:

```bash
# First, update the Docker images with the latest code changes
./start_reflectly.sh --update-docker

# Then start the application
./start_reflectly.sh
```

This will:
1. Apply all fixes to the codebase
2. Rebuild the Docker images with the latest code
3. Start all necessary services including MongoDB, Redis, Kafka, HDFS, Spark, backend, and frontend

### Option 2: Running Backend and Frontend Separately

If you prefer to run the backend and frontend separately:

```bash
# Start the backend
cd backend
./start_backend.sh

# In a separate terminal, start the frontend
cd frontend
npm start
```

## Available Options for start_reflectly.sh

The `start_reflectly.sh` script supports several options:

```
Usage: ./start_reflectly.sh [options]

Options:
  --help                Display this help message
  --skip-docker         Skip starting Docker containers
  --skip-backend        Skip starting the backend
  --skip-frontend       Skip starting the frontend
  --skip-copy-jobs      Skip copying Spark jobs
  --update-docker       Update Docker images before starting
  --cleanup-docker      Clean up all Docker resources (containers, images, volumes)

Example:
  ./start_reflectly.sh                    Start everything
  ./start_reflectly.sh --skip-docker      Start everything except Docker containers
  ./start_reflectly.sh --update-docker    Update Docker images before starting
  ./start_reflectly.sh --cleanup-docker   Clean up all Docker resources
```

## Managing Docker Disk Space

Docker images can consume significant disk space over time. The Reflectly application includes several tools to help you manage disk space:

1. **Automatic Cleanup During Updates**: When you run `./update_docker_images.sh` or use the `--update-docker` option, old images are automatically removed after building new ones.

2. **Full Cleanup**: To perform a complete cleanup of all Docker resources:
   ```bash
   ./start_reflectly.sh --cleanup-docker
   ```
   Or use the dedicated cleanup script:
   ```bash
   ./cleanup_docker.sh
   ```

3. **Check Docker Disk Usage**:
   ```bash
   docker system df
   ```

4. **Manual Cleanup Commands**:
   - Remove unused containers: `docker container prune`
   - Remove unused images: `docker image prune`
   - Remove unused volumes: `docker volume prune`
   - Remove all unused resources: `docker system prune`

## Troubleshooting

If you encounter issues with the application:

1. **Docker Images Out of Date**: Run `./update_docker_images.sh` or `./start_reflectly.sh --update-docker` to rebuild the Docker images with the latest code.

2. **Unknown Emotions Issue**: If the application suggests inappropriate action plans for emotional transitions, make sure you've run the fix scripts by executing `python fix_all_issues.py` or by using the `--update-docker` option.

3. **Backend or Frontend Not Starting**: Check the logs for errors and make sure all dependencies are installed.

4. **Database Connection Issues**: Ensure that MongoDB and Redis are running properly in Docker.

5. **Disk Space Issues**: If you're running low on disk space, use the cleanup tools described in the "Managing Docker Disk Space" section above.

## Accessing the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:5002
- Spark Master: http://localhost:8080
- Hadoop NameNode: http://localhost:9870
