# Reflectly Big Data Infrastructure

This document provides information on the big data infrastructure integrated with the Reflectly project, which includes Kafka, Hadoop, and Spark.

## Overview

The Reflectly project has been enhanced with big data capabilities to improve emotional analysis, path finding, and data processing. The following components have been integrated:

- **Kafka**: Message broker for streaming emotional states and transitions
- **Hadoop (HDFS)**: Distributed file system for storing datasets and results
- **Spark**: Distributed processing engine for emotion analysis and path finding

## Directory Structure

- `/Users/manodhyaopallage/Refection/spark/jobs/`: Contains Spark jobs for various data processing tasks
- `/Users/manodhyaopallage/Refection/backend/models/emotional_graph_bigdata.py`: Enhanced emotional graph with big data integration
- `/Users/manodhyaopallage/Refection/backend/models/search_algorithm.py`: A* search algorithm for emotional path finding

## Setup Instructions

1. Start the Docker containers for the big data infrastructure:

```bash
cd /Users/manodhyaopallage/Refection
docker-compose up -d
```

2. Copy the Spark jobs to the Spark data volume:

```bash
./copy_spark_jobs.sh
```

3. Start the Reflectly backend:

```bash
cd /Users/manodhyaopallage/Refection/backend
./start_backend.sh
```

4. Start the Reflectly frontend:

```bash
cd /Users/manodhyaopallage/Refection/frontend
npm start
```

## Spark Jobs

The following Spark jobs have been implemented:

### 1. Emotion Analysis

Analyzes emotions from journal entries.

```bash
./run_spark_jobs.sh --user-email <email> emotion_analysis
```

### 2. Graph Processing

Processes emotional transitions and builds the emotional graph.

```bash
./run_spark_jobs.sh --user-email <email> graph_processing
```

### 3. Dataset Import

Imports and processes the IEMOCAP and mental health datasets.

```bash
./run_spark_jobs.sh dataset_import
```

### 4. Path Finding

Finds optimal emotional paths using the A* search algorithm.

```bash
./run_spark_jobs.sh --user-email <email> --current-emotion <emotion> --target-emotion <emotion> path_finding
```

## Running All Jobs

To run all jobs in sequence:

```bash
./run_spark_jobs.sh --user-email <email> --current-emotion <emotion> --target-emotion <emotion> all
```

## Accessing Web Interfaces

- **Spark Master**: http://localhost:8080
- **Spark Worker**: http://localhost:8081
- **Hadoop NameNode**: http://localhost:9870
- **Hadoop DataNode**: http://localhost:9864

## Integration with Reflectly

The big data infrastructure is integrated with the Reflectly application through the `EmotionalGraphBigData` class, which extends the original `EmotionalGraph` class with Kafka, HDFS, and Spark integration.

Key features include:
- Publishing emotional states and transitions to Kafka
- Storing and retrieving data from HDFS
- Processing emotional data using Spark
- Finding optimal emotional paths using A* search algorithm

## Troubleshooting

If you encounter issues with the big data infrastructure, try the following:

1. Check if all Docker containers are running:

```bash
docker ps
```

2. Restart the Docker containers:

```bash
docker-compose down
docker-compose up -d
```

3. Check the logs for any errors:

```bash
docker logs namenode
docker logs spark-master
docker logs kafka
```

4. Ensure that the Spark jobs have been copied to the Spark data volume:

```bash
./copy_spark_jobs.sh
```

5. If you're having issues with HDFS, try formatting the namenode:

```bash
docker exec -it namenode hdfs namenode -format
```

## Next Steps

1. Implement more advanced emotion analysis using deep learning models
2. Enhance the emotional graph with more sophisticated path finding algorithms
3. Integrate real-time processing of emotional data
4. Develop more personalized recommendations based on emotional transitions
