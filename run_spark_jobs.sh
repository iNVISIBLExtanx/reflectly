#!/bin/bash

# Script to run Spark jobs for Reflectly

# Default values
USER_EMAIL=""
CURRENT_EMOTION=""
TARGET_EMOTION=""
MAX_DEPTH=10
HDFS_BASE_PATH="/reflectly"
SPARK_MASTER="spark://spark-master:7077"
SPARK_SUBMIT="/spark/bin/spark-submit"

# Function to display usage
function display_usage {
    echo "Usage: $0 [options] <job_name>"
    echo ""
    echo "Options:"
    echo "  --user-email <email>         User email (required for all jobs)"
    echo "  --current-emotion <emotion>  Current emotion (required for path_finding)"
    echo "  --target-emotion <emotion>   Target emotion (required for path_finding)"
    echo "  --max-depth <depth>          Maximum path depth (default: 10)"
    echo "  --hdfs-base-path <path>      Base path in HDFS (default: /reflectly)"
    echo "  --spark-master <url>         Spark master URL (default: spark://spark-master:7077)"
    echo "  --help                       Display this help message"
    echo ""
    echo "Available jobs:"
    echo "  emotion_analysis   - Analyze emotions from journal entries"
    echo "  graph_processing   - Process emotional transitions and build graph"
    echo "  dataset_import     - Import and process IEMOCAP and mental health datasets"
    echo "  path_finding       - Find optimal emotional paths"
    echo "  all                - Run all jobs in sequence"
    echo ""
    echo "Example:"
    echo "  $0 --user-email user@example.com path_finding --current-emotion sadness --target-emotion joy"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --user-email)
            USER_EMAIL="$2"
            shift 2
            ;;
        --current-emotion)
            CURRENT_EMOTION="$2"
            shift 2
            ;;
        --target-emotion)
            TARGET_EMOTION="$2"
            shift 2
            ;;
        --max-depth)
            MAX_DEPTH="$2"
            shift 2
            ;;
        --hdfs-base-path)
            HDFS_BASE_PATH="$2"
            shift 2
            ;;
        --spark-master)
            SPARK_MASTER="$2"
            shift 2
            ;;
        --help)
            display_usage
            exit 0
            ;;
        *)
            JOB_NAME="$1"
            shift
            ;;
    esac
done

# Check if job name is provided
if [ -z "$JOB_NAME" ]; then
    echo "Error: Job name is required"
    display_usage
    exit 1
fi

# Check if user email is provided
if [ -z "$USER_EMAIL" ]; then
    echo "Error: User email is required"
    display_usage
    exit 1
fi

# Function to run emotion analysis job
function run_emotion_analysis {
    echo "Running emotion analysis job..."
    
    # Define paths
    INPUT_PATH="${HDFS_BASE_PATH}/journal_entries/${USER_EMAIL}"
    OUTPUT_PATH="${HDFS_BASE_PATH}/emotion_analysis/${USER_EMAIL}"
    
    # Run job
    docker exec -it spark-master ${SPARK_SUBMIT} \
        --master ${SPARK_MASTER} \
        --py-files /spark/data/spark/jobs/emotion_analysis.py \
        /spark/data/spark/jobs/emotion_analysis.py \
        --user-email ${USER_EMAIL} \
        --input-path ${INPUT_PATH} \
        --output-path ${OUTPUT_PATH}
        
    echo "Emotion analysis job completed"
}

# Function to run graph processing job
function run_graph_processing {
    echo "Running graph processing job..."
    
    # Define paths
    INPUT_PATH="${HDFS_BASE_PATH}/emotion_analysis/${USER_EMAIL}"
    OUTPUT_PATH="${HDFS_BASE_PATH}/emotional_graph/${USER_EMAIL}"
    
    # Run job
    docker exec -it spark-master ${SPARK_SUBMIT} \
        --master ${SPARK_MASTER} \
        --py-files /spark/data/spark/jobs/graph_processing.py \
        /spark/data/spark/jobs/graph_processing.py \
        --user-email ${USER_EMAIL} \
        --input-path ${INPUT_PATH} \
        --output-path ${OUTPUT_PATH}
        
    echo "Graph processing job completed"
}

# Function to run dataset import job
function run_dataset_import {
    echo "Running dataset import job..."
    
    # Define paths
    IEMOCAP_PATH="${HDFS_BASE_PATH}/datasets/iemocap"
    MENTAL_HEALTH_PATH="${HDFS_BASE_PATH}/datasets/mental_health"
    OUTPUT_PATH="${HDFS_BASE_PATH}/datasets/processed"
    
    # Run job
    docker exec -it spark-master ${SPARK_SUBMIT} \
        --master ${SPARK_MASTER} \
        --py-files /spark/data/spark/jobs/dataset_import.py \
        /spark/data/spark/jobs/dataset_import.py \
        --iemocap-path ${IEMOCAP_PATH} \
        --mental-health-path ${MENTAL_HEALTH_PATH} \
        --output-path ${OUTPUT_PATH}
        
    echo "Dataset import job completed"
}

# Function to run path finding job
function run_path_finding {
    echo "Running path finding job..."
    
    # Check if current and target emotions are provided
    if [ -z "$CURRENT_EMOTION" ] || [ -z "$TARGET_EMOTION" ]; then
        echo "Error: Current emotion and target emotion are required for path finding job"
        display_usage
        exit 1
    fi
    
    # Define paths
    INPUT_PATH="${HDFS_BASE_PATH}/emotional_graph/${USER_EMAIL}"
    OUTPUT_PATH="${HDFS_BASE_PATH}/emotional_paths/${USER_EMAIL}/${CURRENT_EMOTION}_to_${TARGET_EMOTION}"
    
    # Run job
    docker exec -it spark-master ${SPARK_SUBMIT} \
        --master ${SPARK_MASTER} \
        --py-files /spark/data/spark/jobs/path_finding.py \
        /spark/data/spark/jobs/path_finding.py \
        --user-email ${USER_EMAIL} \
        --current-emotion ${CURRENT_EMOTION} \
        --target-emotion ${TARGET_EMOTION} \
        --max-depth ${MAX_DEPTH} \
        --input-path ${INPUT_PATH} \
        --output-path ${OUTPUT_PATH}
        
    echo "Path finding job completed"
}

# Function to run all jobs
function run_all_jobs {
    echo "Running all jobs..."
    
    run_dataset_import
    run_emotion_analysis
    run_graph_processing
    
    # Check if current and target emotions are provided for path finding
    if [ -n "$CURRENT_EMOTION" ] && [ -n "$TARGET_EMOTION" ]; then
        run_path_finding
    else
        echo "Skipping path finding job (current and target emotions not provided)"
    fi
    
    echo "All jobs completed"
}

# Run the specified job
case $JOB_NAME in
    emotion_analysis)
        run_emotion_analysis
        ;;
    graph_processing)
        run_graph_processing
        ;;
    dataset_import)
        run_dataset_import
        ;;
    path_finding)
        run_path_finding
        ;;
    all)
        run_all_jobs
        ;;
    *)
        echo "Error: Invalid job name: $JOB_NAME"
        display_usage
        exit 1
        ;;
esac

exit 0
