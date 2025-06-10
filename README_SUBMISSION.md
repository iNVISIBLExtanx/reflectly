# Reflection: Emotional Wellbeing Through AI-Guided Journaling

## Project Overview
Reflection implements a personal journaling application with advanced AI capabilities for emotional pathfinding, probabilistic reasoning, and intelligent agency. The system is built using a microservices architecture deployed via Docker containers.

## Repository
https://github.com/iNVISIBLExtanx/reflectly/tree/feat_phase_2

## Technical Stack
- **Backend**: Python/Flask
- **Frontend**: React.js
- **Database**: MongoDB
- **Cache**: Redis
- **Message Broker**: Kafka
- **Storage**: HDFS
- **Processing**: Spark
- **Containerization**: Docker/Docker Compose

## Setup Instructions

### Prerequisites
- Docker and Docker Compose
- Git

### Installation Steps

1. Clone the repository and checkout the feature branch:
   ```bash
   git clone https://github.com/iNVISIBLExtanx/reflectly.git
   cd reflectly
   git checkout feat_phase_2
   ```

2. Start the application using Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5002
   - Test credentials:
     - Email: test@example.com
     - Password: password123

4. To stop the application:
   ```bash
   docker-compose down
   ```

## Container Architecture

### Container Structure
- `frontend`: React application for user interface
- `backend`: Flask API server for main application logic
- `mongodb`: Database for persistent storage
- `redis`: In-memory cache for session management and frequent data
- `kafka`: Message broker for real-time event streaming
- `zookeeper`: Manages Kafka cluster state
- `namenode` & `datanode`: HDFS components for distributed storage
- `spark-master` & `spark-worker`: Distributed processing

### Container Interaction
```
User → Frontend → Backend → [MongoDB/Redis/Kafka] → Spark → HDFS
                                 ↑
                          Event Streaming
```

The containers interact through defined network interfaces:
- Frontend communicates with backend via REST API (port 5002)
- Backend persists data to MongoDB (port 27017)
- Backend caches frequent data in Redis (port 6379)
- Backend publishes emotional events to Kafka (port 9092)
- Kafka relies on Zookeeper for coordination (port 2181)
- Spark jobs consume data from Kafka and HDFS
- Processed data is stored back in HDFS (port 9000)

### Why Containers?
1. **Isolation**: Each component runs in its own environment, preventing dependency conflicts and enabling independent scaling.

2. **Reproducibility**: Ensures consistent behavior across development, testing, and production environments.

3. **Scalability**: Individual services can be scaled horizontally based on demand (particularly important for Kafka, Spark, and HDFS components).

4. **Resource Efficiency**: Containers share the host OS kernel while maintaining isolation, requiring fewer resources than VMs.

5. **Orchestration**: Docker Compose enables declarative definition of service relationships, network configurations, and volume mappings.

6. **Technology Heterogeneity**: Allows integration of components with different technology stacks (Python, JavaScript, JVM-based systems) without conflict.

The containerization approach is particularly valuable for Reflectly's big data components, enabling the Kafka-HDFS-Spark pipeline to operate efficiently while maintaining clear service boundaries and communication protocols.
