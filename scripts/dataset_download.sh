#!/bin/bash
# Reflectly Dataset Download Script
# This script downloads the IEMOCAP and Mental Health Conversations datasets

set -e  # Exit on any error

# Set variables
BASE_DIR=$(cd "$(dirname "$0")/.." && pwd)
DATA_DIR="$BASE_DIR/data/datasets"
IEMOCAP_DIR="$DATA_DIR/iemocap/raw"
MENTAL_HEALTH_DIR="$DATA_DIR/mental_health/raw"

echo "Starting dataset download process..."
echo "Base directory: $BASE_DIR"
echo "Data directory: $DATA_DIR"

# Create directories if they don't exist
mkdir -p "$IEMOCAP_DIR"
mkdir -p "$MENTAL_HEALTH_DIR"

# Function to check if dataset already exists
dataset_exists() {
    local dir=$1
    local name=$2
    if [ -d "$dir" ] && [ "$(ls -A "$dir")" ]; then
        echo "Dataset $name already exists in $dir"
        return 0
    else
        echo "Dataset $name does not exist in $dir"
        return 1
    fi
}

# Download IEMOCAP dataset
download_iemocap() {
    echo "Downloading IEMOCAP dataset from Kaggle..."
    
    # Ensure kaggle command is available
    if ! command -v kaggle &> /dev/null; then
        echo "Error: kaggle command not found. Please install the Kaggle API:"
        echo "pip install kaggle"
        exit 1
    fi
    
    # Ensure Kaggle API key is configured
    if [ ! -f ~/.kaggle/kaggle.json ]; then
        echo "Error: Kaggle API credentials not found."
        echo "Please create ~/.kaggle/kaggle.json with your API key."
        exit 1
    fi
    
    # Set proper permissions for Kaggle API key
    chmod 600 ~/.kaggle/kaggle.json
    
    # Download the IEMOCAP dataset from Kaggle
    kaggle datasets download -d ejlok1/iemocap -p "$IEMOCAP_DIR"
    
    # Extract the dataset if it's a ZIP file
    find "$IEMOCAP_DIR" -name "*.zip" -exec unzip -o {} -d "$IEMOCAP_DIR" \;
    
    echo "IEMOCAP dataset downloaded and extracted successfully."
}

# Download Mental Health Conversations dataset
download_mental_health() {
    echo "Downloading Mental Health Conversations dataset from Kaggle..."
    
    # Ensure kaggle command is available
    if ! command -v kaggle &> /dev/null; then
        echo "Error: kaggle command not found. Please install the Kaggle API:"
        echo "pip install kaggle"
        exit 1
    fi
    
    # Ensure Kaggle API key is configured
    if [ ! -f ~/.kaggle/kaggle.json ]; then
        echo "Error: Kaggle API credentials not found."
        echo "Please create ~/.kaggle/kaggle.json with your API key."
        exit 1
    fi
    
    # Set proper permissions for Kaggle API key
    chmod 600 ~/.kaggle/kaggle.json
    
    # Download the Mental Health Conversations dataset from Kaggle
    kaggle datasets download -d narendrageek/mental-health-conversational-data -p "$MENTAL_HEALTH_DIR"
    
    # Extract the dataset if it's a ZIP file
    find "$MENTAL_HEALTH_DIR" -name "*.zip" -exec unzip -o {} -d "$MENTAL_HEALTH_DIR" \;
    
    echo "Mental Health Conversations dataset downloaded and extracted successfully."
}

# Main execution
echo "Checking for existing datasets..."

if ! dataset_exists "$IEMOCAP_DIR" "IEMOCAP"; then
    download_iemocap
else
    echo "Skipping IEMOCAP download."
fi

if ! dataset_exists "$MENTAL_HEALTH_DIR" "Mental Health Conversations"; then
    download_mental_health
else
    echo "Skipping Mental Health Conversations download."
fi

echo "Dataset download process completed."
echo "Next steps:"
echo "1. Run dataset_import.sh to import datasets to HDFS"
echo "2. Run Spark jobs to process the datasets"

# Make this script executable
chmod +x "$0"
