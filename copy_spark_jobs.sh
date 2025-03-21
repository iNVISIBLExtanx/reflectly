#!/bin/bash

# Script to copy Spark jobs to the Spark data directory in the Docker container

# Create directory structure in Spark data volume
echo "Creating directory structure in Spark data volume..."
docker exec -it spark-master mkdir -p /spark/data/spark/jobs

# Copy Spark jobs to the Spark data volume
echo "Copying Spark jobs to the Spark data volume..."
docker cp /Users/manodhyaopallage/Refection/spark/jobs/emotion_analysis.py spark-master:/spark/data/spark/jobs/
docker cp /Users/manodhyaopallage/Refection/spark/jobs/graph_processing.py spark-master:/spark/data/spark/jobs/
docker cp /Users/manodhyaopallage/Refection/spark/jobs/dataset_import.py spark-master:/spark/data/spark/jobs/
docker cp /Users/manodhyaopallage/Refection/spark/jobs/path_finding.py spark-master:/spark/data/spark/jobs/

# Set permissions
echo "Setting permissions..."
docker exec -it spark-master chmod +x /spark/data/spark/jobs/*.py

echo "Spark jobs copied successfully!"
