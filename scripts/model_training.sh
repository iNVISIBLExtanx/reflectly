#!/bin/bash
# Reflectly Model Training Script
# This script trains models using the processed IEMOCAP and Mental Health Conversations datasets

set -e  # Exit on any error

# Set variables
BASE_DIR=$(cd "$(dirname "$0")/.." && pwd)
SPARK_SUBMIT="spark-submit --master spark://spark-master:7077"
SPARK_JOBS_DIR="$BASE_DIR/spark/jobs"
HDFS_BASE_PATH="/user/reflectly"
HDFS_DATASETS_PATH="$HDFS_BASE_PATH/datasets"
HDFS_MODELS_PATH="$HDFS_BASE_PATH/models"
HDFS_KNOWLEDGE_PATH="$HDFS_BASE_PATH/knowledge"

echo "Starting model training process..."
echo "Base directory: $BASE_DIR"
echo "Spark jobs directory: $SPARK_JOBS_DIR"
echo "HDFS datasets path: $HDFS_DATASETS_PATH"
echo "HDFS models path: $HDFS_MODELS_PATH"
echo "HDFS knowledge path: $HDFS_KNOWLEDGE_PATH"

# Function to check if processed datasets exist in HDFS
datasets_processed() {
    local path=$1
    local name=$2
    
    echo "Checking if $name datasets exist in HDFS..."
    
    # Check if directory exists and is not empty
    if hdfs dfs -test -d $path && hdfs dfs -ls $path | grep -q .; then
        echo "$name datasets found in HDFS at $path"
        return 0
    else
        echo "$name datasets not found in HDFS at $path"
        return 1
    fi
}

# Function to create necessary HDFS directories
create_hdfs_directories() {
    echo "Creating HDFS directories for trained models and knowledge..."
    
    # Create necessary HDFS directories
    hdfs dfs -mkdir -p $HDFS_MODELS_PATH
    hdfs dfs -mkdir -p $HDFS_KNOWLEDGE_PATH
    
    # Create subdirectories for specific knowledge types
    hdfs dfs -mkdir -p "$HDFS_MODELS_PATH/emotion_detection"
    hdfs dfs -mkdir -p "$HDFS_MODELS_PATH/transitions"
    hdfs dfs -mkdir -p "$HDFS_MODELS_PATH/heuristics"
    hdfs dfs -mkdir -p "$HDFS_MODELS_PATH/bayesian"
    hdfs dfs -mkdir -p "$HDFS_KNOWLEDGE_PATH/response_templates"
    hdfs dfs -mkdir -p "$HDFS_KNOWLEDGE_PATH/interventions"
    
    # Set appropriate permissions
    hdfs dfs -chmod -R 755 $HDFS_MODELS_PATH
    hdfs dfs -chmod -R 755 $HDFS_KNOWLEDGE_PATH
    
    echo "HDFS directories created successfully."
}

# Function to train emotion detection model
train_emotion_detection() {
    echo "Training emotion detection model using IEMOCAP dataset..."
    
    # Run the PySpark job to process the IEMOCAP dataset and train models
    $SPARK_SUBMIT \
        --conf "spark.driver.memory=4g" \
        --conf "spark.executor.memory=4g" \
        $SPARK_JOBS_DIR/process_iemocap.py \
        --input "$HDFS_DATASETS_PATH/iemocap" \
        --output "$HDFS_MODELS_PATH/emotion_detection" \
        --emotion_map_output "$HDFS_KNOWLEDGE_PATH/emotion_mapping.json"
    
    echo "Emotion detection model trained successfully."
}

# Function to train response template extraction
train_response_templates() {
    echo "Extracting response templates from Mental Health Conversations dataset..."
    
    # Run the PySpark job to process the Mental Health Conversations dataset
    $SPARK_SUBMIT \
        --conf "spark.driver.memory=4g" \
        --conf "spark.executor.memory=4g" \
        $SPARK_JOBS_DIR/process_mental_health.py \
        --input "$HDFS_DATASETS_PATH/mental_health" \
        --templates_output "$HDFS_KNOWLEDGE_PATH/response_templates" \
        --interventions_output "$HDFS_KNOWLEDGE_PATH/interventions"
    
    echo "Response templates extracted successfully."
}

# Function to train emotional transition model
train_emotional_transitions() {
    echo "Training emotional transition model using IEMOCAP dataset..."
    
    # Use the outputs from process_iemocap.py to build transition models
    $SPARK_SUBMIT \
        --conf "spark.driver.memory=4g" \
        --conf "spark.executor.memory=4g" \
        $SPARK_JOBS_DIR/process_iemocap.py \
        --input "$HDFS_DATASETS_PATH/iemocap" \
        --output "$HDFS_MODELS_PATH/emotion_detection" \
        --transitions_output "$HDFS_MODELS_PATH/transitions" \
        --mode "transitions"
    
    echo "Emotional transition model trained successfully."
}

# Function to analyze intervention effectiveness
analyze_interventions() {
    echo "Analyzing intervention effectiveness from Mental Health Conversations dataset..."
    
    # Run the PySpark job to analyze intervention effectiveness
    $SPARK_SUBMIT \
        --conf "spark.driver.memory=4g" \
        --conf "spark.executor.memory=4g" \
        $SPARK_JOBS_DIR/process_mental_health.py \
        --input "$HDFS_DATASETS_PATH/mental_health" \
        --interventions_output "$HDFS_KNOWLEDGE_PATH/interventions" \
        --effectiveness_output "$HDFS_KNOWLEDGE_PATH/effectiveness" \
        --mode "effectiveness"
    
    echo "Intervention effectiveness analyzed successfully."
}

# Function to generate A* search heuristics
generate_heuristics() {
    echo "Generating A* search heuristics from emotional transition data..."
    
    # Run the PySpark job to generate A* search heuristics
    $SPARK_SUBMIT \
        --conf "spark.driver.memory=4g" \
        --conf "spark.executor.memory=4g" \
        $SPARK_JOBS_DIR/process_iemocap.py \
        --input "$HDFS_DATASETS_PATH/iemocap" \
        --transitions_input "$HDFS_MODELS_PATH/transitions" \
        --heuristics_output "$HDFS_MODELS_PATH/heuristics" \
        --mode "heuristics"
    
    echo "A* search heuristics generated successfully."
}

# Main execution
echo "Checking if processed datasets exist in HDFS..."

# Check if processed IEMOCAP dataset exists
if datasets_processed "$HDFS_DATASETS_PATH/iemocap/processed" "IEMOCAP"; then
    echo "Processed IEMOCAP dataset found."
else
    echo "Error: Processed IEMOCAP dataset not found. Process datasets first."
    exit 1
fi

# Check if processed Mental Health dataset exists
if datasets_processed "$HDFS_DATASETS_PATH/mental_health/processed" "Mental Health Conversations"; then
    echo "Processed Mental Health Conversations dataset found."
else
    echo "Error: Processed Mental Health Conversations dataset not found. Process datasets first."
    exit 1
fi

# Create HDFS directories for models and knowledge
create_hdfs_directories

# Train models and analyze data
train_emotion_detection
train_response_templates
train_emotional_transitions
analyze_interventions
generate_heuristics

echo "Model training process completed (simulated)."
echo "Next steps:"
echo "1. Set up dataset-specific models in the backend"
echo "2. Enhance existing AI components with dataset-derived models"
echo "3. Implement new API endpoints for dataset insights"

# Make this script executable
chmod +x "$0"
