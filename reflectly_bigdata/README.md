# Reflectly Big Data Architecture

This archive contains the Big Data implementation for the Reflectly personal journaling application.

## Directory Structure

```
reflectly_bigdata/
├── backend/
│   ├── models/
│   │   └── emotional_graph_bigdata.py  # Main BigData integration model
│   └── services/
│       ├── hdfs_service.py             # HDFS interaction service
│       ├── kafka_service.py            # Kafka messaging service
│       └── spark_service.py            # Spark job submission service
├── spark/
│   └── jobs/
│       ├── dataset_import.py           # Import external datasets
│       ├── emotion_analysis.py         # Analyze user emotions
│       ├── graph_processing.py         # Process emotional state transitions
│       └── path_finding.py             # Find optimal emotional paths
├── data/
│   ├── input/
│   │   └── sample_emotional_states.json # Sample input data
│   └── output/                         # Directory for job outputs
└── docs/
    └── big_data_architecture.md        # Architecture documentation
```

## Prerequisites

- Apache Kafka (>= 2.8.0)
- Apache Hadoop (>= 3.3.0)
- Apache Spark (>= 3.1.2)
- Python (>= 3.8)
- Python libraries: kafka-python, pyspark, pymongo, requests

## Running the Sample Code

### 1. Setup Environment

```bash
# Install required Python dependencies
pip install kafka-python pyspark pymongo requests
```

### 2. Configure Connections

By default, the services will attempt to connect to:
- Kafka: localhost:9092
- HDFS: namenode:9000
- Spark: spark://spark-master:7077
- MongoDB: localhost:27017

You can modify these in the service class initializers if needed.

### 3. Sample Workflow

```python
# Example Python code to use the services
from backend.services.kafka_service import KafkaService
from backend.services.hdfs_service import HDFSService
from backend.services.spark_service import SparkService
from backend.models.emotional_graph_bigdata import EmotionalGraphBigData

# Initialize services
kafka_service = KafkaService()
hdfs_service = HDFSService()
spark_service = SparkService()

# Create emotional graph with big data support
emotional_graph = EmotionalGraphBigData(
    kafka_service=kafka_service,
    hdfs_service=hdfs_service,
    spark_service=spark_service
)

# Process sample data
# (Normally this would happen through the application's journal entries)
emotional_graph.process_emotional_state(
    user_email="user1@example.com",
    primary_emotion="joy",
    emotion_scores={"joy": 0.8, "sadness": 0.1, "anger": 0.05, "fear": 0.03, "disgust": 0.02}
)

# Run a Spark job to process emotional transitions
job_id = spark_service.submit_job(
    "spark/jobs/graph_processing.py",
    job_args=["--input", "data/input/sample_emotional_states.json", 
              "--output", "data/output/emotional_transitions",
              "--patterns", "data/output/patterns"]
)
```

### 4. Running a Spark Job Directly

```bash
# Submit a Spark job to process the sample data
spark-submit spark/jobs/graph_processing.py \
  --input data/input/sample_emotional_states.json \
  --output data/output/emotional_transitions \
  --patterns data/output/patterns
```

## Notes 

- This is a simplified version of the full system. Full system is in the git repository. I will share the full code if needed. 
- The sample data provides enough information to demonstrate the functionality
- For a complete understanding of the architecture, please refer to the documentation in docs/big_data_architecture.md
