#!/bin/bash
# Reflectly Dataset Import Script
# This script imports the IEMOCAP and Mental Health Conversations datasets to HDFS

set -e  # Exit on any error

# Set variables
BASE_DIR=$(cd "$(dirname "$0")/.." && pwd)
DATA_DIR="$BASE_DIR/data/datasets"
IEMOCAP_RAW_DIR="$DATA_DIR/iemocap/raw"
MENTAL_HEALTH_RAW_DIR="$DATA_DIR/mental_health/raw"
HDFS_BASE_PATH="/user/reflectly/datasets"
HDFS_IEMOCAP_PATH="$HDFS_BASE_PATH/iemocap"
HDFS_MENTAL_HEALTH_PATH="$HDFS_BASE_PATH/mental_health"

echo "Starting dataset import process..."
echo "Base directory: $BASE_DIR"
echo "Data directory: $DATA_DIR"
echo "HDFS base path: $HDFS_BASE_PATH"

# Function to check if dataset is ready for import
dataset_ready() {
    local dir=$1
    local name=$2
    if [ -d "$dir" ] && [ "$(ls -A "$dir")" ]; then
        echo "Dataset $name is ready for import from $dir"
        return 0
    else
        echo "Dataset $name is not ready for import. Run dataset_download.sh first."
        return 1
    fi
}

# Function to create HDFS directories
create_hdfs_directories() {
    echo "Creating HDFS directories..."
    
    # Create HDFS directories for datasets
    hdfs dfs -mkdir -p $HDFS_BASE_PATH
    hdfs dfs -mkdir -p $HDFS_IEMOCAP_PATH
    hdfs dfs -mkdir -p $HDFS_MENTAL_HEALTH_PATH
    
    # Set appropriate permissions
    hdfs dfs -chmod -R 755 $HDFS_BASE_PATH
    
    echo "HDFS directories created successfully."
}

# Function to import IEMOCAP dataset to HDFS
import_iemocap() {
    echo "Importing IEMOCAP dataset to HDFS..."
    
    # First, clean the destination directory if it exists
    hdfs dfs -rm -r -f $HDFS_IEMOCAP_PATH/* 2>/dev/null || true
    
    # Copy the dataset to HDFS
    hdfs dfs -put $IEMOCAP_RAW_DIR/* $HDFS_IEMOCAP_PATH
    
    # Verify the import
    echo "Verifying IEMOCAP dataset import..."
    HDFS_FILES=$(hdfs dfs -ls $HDFS_IEMOCAP_PATH | wc -l)
    if [ $HDFS_FILES -gt 1 ]; then
        echo "IEMOCAP dataset imported to HDFS successfully."
    else
        echo "Error: IEMOCAP dataset import failed. No files found in HDFS."
        exit 1
    fi
}

# Function to import Mental Health Conversations dataset to HDFS
import_mental_health() {
    echo "Importing Mental Health Conversations dataset to HDFS..."
    
    # First, clean the destination directory if it exists
    hdfs dfs -rm -r -f $HDFS_MENTAL_HEALTH_PATH/* 2>/dev/null || true
    
    # Copy the dataset to HDFS
    hdfs dfs -put $MENTAL_HEALTH_RAW_DIR/* $HDFS_MENTAL_HEALTH_PATH
    
    # Verify the import
    echo "Verifying Mental Health Conversations dataset import..."
    HDFS_FILES=$(hdfs dfs -ls $HDFS_MENTAL_HEALTH_PATH | wc -l)
    if [ $HDFS_FILES -gt 1 ]; then
        echo "Mental Health Conversations dataset imported to HDFS successfully."
    else
        echo "Error: Mental Health Conversations dataset import failed. No files found in HDFS."
        exit 1
    fi
}

# Main execution
echo "Checking if datasets are ready for import..."

# Check IEMOCAP dataset
if dataset_ready "$IEMOCAP_RAW_DIR" "IEMOCAP"; then
    # Continue with import
    echo "IEMOCAP dataset is ready for import."
else
    echo "Error: IEMOCAP dataset is not ready for import. Run dataset_download.sh first."
    exit 1
fi

# Check Mental Health Conversations dataset
if dataset_ready "$MENTAL_HEALTH_RAW_DIR" "Mental Health Conversations"; then
    # Continue with import
    echo "Mental Health Conversations dataset is ready for import."
else
    echo "Error: Mental Health Conversations dataset is not ready for import. Run dataset_download.sh first."
    exit 1
fi

# Create HDFS directories
create_hdfs_directories

# Import datasets to HDFS
import_iemocap
import_mental_health

echo "Dataset import process completed (simulated)."
echo "Next steps:"
echo "1. Run Spark jobs to process the datasets"
echo "2. Train models using the processed datasets"

# Make this script executable
chmod +x "$0"
