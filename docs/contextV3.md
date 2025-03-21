# Reflectly Technical Documentation - Phase Two

**Version:** 2.0.0  
**Last Updated:** March 14, 2025  
**Author:** Reflectly Development Team

## Table of Contents
- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Directory Structure](#directory-structure)
- [Backend Components](#backend-components)
  - [Emotional Graph](#emotional-graph)
  - [Response Generator](#response-generator)
  - [Journal Entry Processing](#journal-entry-processing)
  - [Big Data Integration](#big-data-integration)
  - [Message Processing Pipeline](#message-processing-pipeline)
- [Frontend Components](#frontend-components)
- [Data Flow](#data-flow)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Authentication](#authentication)
- [Deployment](#deployment)
- [Environment Variables](#environment-variables)

## Project Overview

Reflectly is a personal journaling application with a conversational interface designed to help users engage in meaningful self-reflection. The application combines a chat-like interface with intelligent emotional support and goal tracking features. The system uses emotional analysis to provide personalized responses and help users navigate from negative emotional states to positive ones.

### Core Functionality
- **Conversational Journaling**: Users interact with the application through a chat interface
- **Emotion Analysis**: The system analyzes user emotions from journal entries using distributed processing
- **Emotional Graph**: Tracks transitions between emotional states and suggests personalized interventions based on user history
- **Personalized Responses**: Generates responses tailored to the user's emotional context and history
- **Goal Tracking**: Users can set and track personal goals
- **Big Data Processing**: Processes journal entries using Hadoop, Spark, and Kafka for scalable analysis
- **Advanced Search**: Uses A* search algorithm to find optimal paths between emotional states

## System Architecture

Reflectly now follows a distributed microservices architecture with big data processing capabilities:

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│    Frontend     │◄────►│    Backend      │◄────►│    Database     │
│    (React.js)   │      │    (Flask)      │      │    (MongoDB)    │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                  ▲                        ▲
                                  │                        │
                                  ▼                        │
                         ┌─────────────────┐              │
                         │                 │              │
                         │     Redis       │              │
                         │    (Cache)      │              │
                         │                 │              │
                         └─────────────────┘              │
                                                          │
┌─────────────────┐      ┌─────────────────┐      ┌──────┴──────────┐
│                 │      │                 │      │                 │
│     Kafka       │◄────►│     Spark       │◄────►│     HDFS        │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
        ▲
        │
        ▼
┌─────────────────┐
│                 │
│   Zookeeper     │
│                 │
└─────────────────┘
```

- **Frontend**: React.js application providing the user interface
- **Backend**: Flask application handling business logic, emotion analysis, and response generation
- **Database**: MongoDB for persistent storage of user data, journal entries, and emotional states
- **Cache**: Redis for temporary data storage and session management
- **Kafka**: Message broker for handling journal entry streams
- **Spark**: Distributed processing for emotion analysis and graph computations
- **HDFS**: Distributed file system for storing datasets and processed data
- **Zookeeper**: Coordination service for Kafka

## Technology Stack

### Frontend
- **Framework**: React.js
- **UI Library**: Material-UI
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Date Handling**: date-fns

### Backend
- **Framework**: Flask (Python)
- **Authentication**: JWT (JSON Web Tokens)
- **Database ORM**: PyMongo
- **Message Processing**: Kafka Python client
- **Emotion Analysis**: Custom implementation with BERT/RoBERTa models
- **Response Generation**: Template-based with personalization logic
- **Graph Processing**: NetworkX for emotional graph implementation
- **Search Algorithms**: A* implementation for finding optimal emotional paths

### Big Data Infrastructure
- **Distributed Storage**: Hadoop HDFS
- **Distributed Processing**: Apache Spark
- **Stream Processing**: Apache Kafka
- **Coordination**: Apache Zookeeper
- **Dataset Processing**: PySpark for processing IEMOCAP and mental health datasets

### Database
- **Primary Database**: MongoDB
- **Caching**: Redis
- **Long-term Storage**: HDFS

### DevOps
- **Containerization**: Docker and Docker Compose
- **Version Control**: Git
- **CI/CD**: GitHub Actions

## Directory Structure

```
/
├── backend/                # Flask backend application
│   ├── models/             # Business logic models
│   │   ├── emotional_graph.py     # Emotional state tracking and transitions
│   │   ├── response_generator.py  # AI response generation
│   │   ├── search_algorithm.py    # NEW: A* search implementation
│   │   └── ...
│   ├── services/           # NEW: External service integrations
│   │   ├── kafka_service.py       # NEW: Kafka integration
│   │   ├── spark_service.py       # NEW: Spark job submission
│   │   └── hdfs_service.py        # NEW: HDFS operations
│   ├── utils/              # Utility functions
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration settings
│   ├── requirements.txt    # Python dependencies
│   └── start_backend.sh    # Script to start the backend server
│
├── spark/                  # NEW: Spark job definitions
│   ├── jobs/               # Spark job implementations
│   │   ├── emotion_analysis.py    # Emotion analysis job
│   │   ├── graph_processing.py    # Emotional graph processing
│   │   └── dataset_import.py      # Dataset import and processing
│   ├── utils/              # Spark utility functions
│   └── submit_job.sh       # Script to submit Spark jobs
│
├── data/                   # NEW: Data directory
│   ├── datasets/           # Raw datasets
│   │   ├── iemocap/        # IEMOCAP dataset
│   │   └── mental_health/  # Mental health conversations dataset
│   └── preprocessing/      # Data preprocessing scripts
│
├── frontend/               # React frontend application
│   ├── public/             # Static assets
│   ├── src/                # Source code
│   │   ├── components/     # Reusable UI components
│   │   │   ├── journal/    # Journal-related components
│   │   │   └── layout/     # Layout components
│   │   ├── context/        # React context providers
│   │   ├── pages/          # Application pages
│   │   │   └── EmotionalJourneyGraph.js # NEW: Emotional path visualization
│   │   ├── utils/          # Utility functions
│   │   ├── App.js          # Main application component
│   │   └── index.js        # Entry point
│   ├── package.json        # NPM dependencies
│   └── README.md           # Frontend documentation
│
├── docker/                 # Docker configuration
│   ├── backend/            # Backend Docker configuration
│   ├── frontend/           # Frontend Docker configuration
│   └── hadoop/             # NEW: Hadoop configuration files
│
├── docker-compose.yml      # Multi-container orchestration
├── docs/                   # Project documentation
│   ├── technical_documentation.md  # Technical documentation
│   └── context.md          # Project context and requirements
└── README.md               # Project overview
```

## Backend Components

### Emotional Graph

The `EmotionalGraph` class has been enhanced to leverage big data processing for more sophisticated analysis:

#### Key Enhancements

- **Distributed Storage**: Emotional graph data is now stored in both MongoDB (for quick access) and HDFS (for long-term storage and analytics)
- **Spark Processing**: Graph computations now use Spark for distributed processing
- **A* Search Integration**: Uses A* search algorithm to find optimal paths between emotional states
- **Dataset Integration**: Incorporates insights from the IEMOCAP and mental health datasets

#### Implementation

The enhanced `EmotionalGraph` class now integrates with Spark and HDFS:

1. **Recording Emotions with Kafka**: The `record_emotion` method now publishes emotion data to Kafka for asynchronous processing.

```python
def record_emotion(self, user_email, emotion_data, entry_id=None):
    # Store the emotional state in MongoDB
    # Publish emotion data to Kafka for processing
    # Return the stored emotion document
```

2. **Finding Optimal Emotional Paths**: The `find_optimal_path` method uses A* search to find the optimal path from the current emotional state to a target positive state.

```python
def find_optimal_path(self, user_email, current_emotion, target_emotion="joy"):
    # Use A* search algorithm to find the optimal path
    # Consider past successful transitions as heuristics
    # Return the optimal path and suggested actions
```

3. **Retrieving Insights from Datasets**: The `get_dataset_insights` method retrieves insights from the processed IEMOCAP and mental health datasets.

```python
def get_dataset_insights(self, emotion):
    # Get insights from processed datasets in HDFS
    # Use Spark to query the datasets efficiently
    # Return relevant insights for the given emotion
```

### Response Generator

The `ResponseGenerator` class has been enhanced to incorporate insights from big data processing:

#### Key Enhancements

- **Dataset-Driven Responses**: Incorporates insights from processed datasets
- **Optimal Path Suggestions**: Suggests actions based on optimal emotional paths
- **Personalized Heuristics**: Uses personalized heuristics for response generation

#### Implementation

The enhanced `ResponseGenerator` class now integrates with the big data processing pipeline:

1. **Generating Responses with Dataset Insights**: The `generate_with_insights` method incorporates insights from processed datasets.

```python
def generate_with_insights(self, text, emotion_data, dataset_insights=None):
    # Generate a response incorporating dataset insights
    # Use a more sophisticated template system
    # Return a response with insights from datasets
```

2. **Generating Responses with Optimal Paths**: The `generate_with_optimal_path` method suggests actions based on the optimal emotional path.

```python
def generate_with_optimal_path(self, text, emotion_data, optimal_path=None):
    # Generate a response suggesting actions from the optimal path
    # Incorporate insights from A* search results
    # Return a response with suggested actions
```

### Journal Entry Processing

The journal entry processing logic has been enhanced to use the big data infrastructure:

#### Key Enhancements

- **Kafka Integration**: Journal entries are published to Kafka for asynchronous processing
- **Spark Processing**: Emotion analysis is performed using Spark jobs
- **HDFS Storage**: Processed journal entries are stored in HDFS for long-term analytics
- **A* Search Integration**: Uses A* search to find optimal emotional paths

#### Implementation

The enhanced journal entry processing logic now integrates with the big data infrastructure:

1. **Asynchronous Processing**: Journal entries are published to Kafka for asynchronous processing.
2. **Distributed Emotion Analysis**: Emotion analysis is performed using Spark jobs.
3. **Optimal Path Finding**: A* search is used to find optimal emotional paths.
4. **Dataset Insight Integration**: Insights from processed datasets are incorporated into responses.

### Big Data Integration

This new component integrates the Flask backend with the big data infrastructure:

#### Key Features

- **Kafka Integration**: Publishes and consumes messages from Kafka topics
- **Spark Job Submission**: Submits Spark jobs for distributed processing
- **HDFS Operations**: Reads from and writes to HDFS
- **Dataset Processing**: Processes and analyzes datasets using Spark

#### Implementation

The big data integration component consists of several services:

1. **Kafka Service**: Manages Kafka producers and consumers.

```python
class KafkaService:
    def __init__(self, bootstrap_servers="kafka:9092"):
        # Initialize Kafka producer and consumer configurations
        
    def publish_message(self, topic, key, value):
        # Publish a message to a Kafka topic
        
    def consume_messages(self, topic, callback):
        # Consume messages from a Kafka topic and process them
```

2. **Spark Service**: Manages Spark job submissions.

```python
class SparkService:
    def __init__(self, spark_master="spark://spark-master:7077"):
        # Initialize Spark configuration
        
    def submit_job(self, job_path, job_args=None):
        # Submit a PySpark job to the Spark cluster
        
    def get_job_status(self, job_id):
        # Get the status of a submitted job
```

3. **HDFS Service**: Manages HDFS operations.

```python
class HDFSService:
    def __init__(self, namenode="namenode:9000"):
        # Initialize HDFS configuration
        
    def read_file(self, hdfs_path):
        # Read a file from HDFS
        
    def write_file(self, local_path, hdfs_path):
        # Write a file to HDFS
        
    def list_directory(self, hdfs_path):
        # List files in an HDFS directory
```

### Message Processing Pipeline

This new component processes messages from Kafka topics:

#### Key Features

- **Journal Entry Processing**: Processes journal entries from the journal-entries topic
- **Emotion Analysis**: Analyzes emotions using PySpark jobs
- **Emotional Graph Updates**: Updates the emotional graph with processed data
- **Response Generation**: Generates responses based on processed data

#### Implementation

The message processing pipeline consists of several Kafka consumers:

1. **Journal Entry Consumer**: Processes journal entries from the journal-entries topic.

```python
def process_journal_entry(message):
    # Extract journal entry data from message
    # Submit a Spark job for emotion analysis
    # Update the emotional graph
    # Generate a response
    # Store the processed data in HDFS and MongoDB
```

2. **Emotion Analysis Consumer**: Processes emotion analysis results from the emotion-analysis topic.

```python
def process_emotion_analysis(message):
    # Extract emotion analysis data from message
    # Update the emotional graph
    # Generate insights based on the analysis
    # Store the processed data in HDFS and MongoDB
```

## Frontend Components

The frontend has been enhanced to visualize the emotional journey and optimal paths:

### Key Enhancements

- **Emotional Journey Graph**: Visualizes the user's emotional journey over time
- **Optimal Path Visualization**: Displays optimal paths between emotional states
- **Action Suggestions**: Displays suggested actions from the A* search results
- **Dataset Insights**: Displays insights from processed datasets

### Implementation

The enhanced frontend implementation includes:

1. **Emotional Journey Graph**: Visualizes the user's emotional journey using a graph.

```jsx
<EmotionalJourneyGraph 
  emotionalStates={emotionalStates} 
  transitions={transitions} 
  optimalPaths={optimalPaths} 
/>
```

2. **Suggested Actions Display**: Displays suggested actions from the A* search results.

```jsx
<SuggestedActions 
  actions={suggestedActions} 
  onActionSelect={handleActionSelect} 
/>
```

3. **Dataset Insights Display**: Displays insights from processed datasets.

```jsx
<DatasetInsights 
  insights={datasetInsights} 
/>
```

## Data Flow

The enhanced data flow in Reflectly follows these steps:

1. **User Input**: The user enters a journal entry in the frontend.
2. **API Request**: The frontend sends the journal entry to the backend API.
3. **Kafka Publishing**: The backend publishes the journal entry to the journal-entries Kafka topic.
4. **Spark Processing**: A Spark job analyzes emotions from the journal entry text.
5. **Emotional Graph Update**: The emotional graph is updated with the new emotional state.
6. **A* Search**: A* search finds the optimal path from the current to a target positive emotional state.
7. **Dataset Integration**: Insights from processed datasets are incorporated.
8. **Response Generation**: A personalized response is generated based on emotional context, history, optimal path, and dataset insights.
9. **API Response**: The backend sends the response back to the frontend.
10. **UI Update**: The frontend displays the response with suggested actions and visualizations.

## API Endpoints

### Authentication

#### POST /api/auth/register
Registers a new user.

**Request:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user_id": "60a1e2c3d4e5f6a7b8c9d0e1"
}
```

#### POST /api/auth/login
Authenticates a user and returns a JWT token.

**Request:**
```json
{
  "email": "john.doe@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "60a1e2c3d4e5f6a7b8c9d0e1",
    "name": "John Doe",
    "email": "john.doe@example.com"
  }
}
```

### Journal Entries

#### GET /api/journal/entries
Retrieves all journal entries for the authenticated user.

**Response:**
```json
[
  {
    "_id": "60a1e2c3d4e5f6a7b8c9d0e2",
    "user_email": "john.doe@example.com",
    "content": "I had a great day today!",
    "created_at": "2025-03-14T12:00:00Z",
    "emotion": {
      "primary_emotion": "joy",
      "is_positive": true,
      "emotion_scores": {
        "joy": 0.8,
        "sadness": 0.1,
        "anger": 0.05,
        "fear": 0.03,
        "disgust": 0.02
      }
    }
  }
]
```

#### POST /api/journal/entries
Creates a new journal entry and returns an AI response.

**Request:**
```json
{
  "content": "I had a great day today!"
}
```

**Response:**
```json
{
  "message": "Journal entry created",
  "entry_id": "60a1e2c3d4e5f6a7b8c9d0e3",
  "response_id": "60a1e2c3d4e5f6a7b8c9d0e4",
  "response": {
    "text": "That's wonderful to hear! What made your day so great?",
    "suggested_actions": [
      "Share your positive experience with others",
      "Practice gratitude",
      "Savor the moment",
      "Set new goals"
    ],
    "dataset_insights": {
      "common_followups": [
        "Express gratitude for specific events",
        "Plan more activities that bring joy"
      ],
      "success_rate": 0.85
    },
    "optimal_path": {
      "current_emotion": "joy",
      "target_emotion": "joy",
      "path": ["joy"],
      "actions": [
        "Continue practicing gratitude",
        "Share your positive experiences"
      ]
    }
  }
}
```

### NEW: Emotional Path Endpoints

#### GET /api/emotions/optimal-path
Retrieves the optimal path from the current emotional state to a target positive state.

**Request:**
```json
{
  "current_emotion": "sadness",
  "target_emotion": "joy"
}
```

**Response:**
```json
{
  "optimal_path": {
    "current_emotion": "sadness",
    "target_emotion": "joy",
    "path": ["sadness", "neutral", "joy"],
    "actions": [
      {
        "from": "sadness",
        "to": "neutral",
        "action": "Practice mindfulness",
        "success_rate": 0.75
      },
      {
        "from": "neutral",
        "to": "joy",
        "action": "Engage in a favorite activity",
        "success_rate": 0.8
      }
    ],
    "total_cost": 2.45,
    "estimated_success_rate": 0.6
  }
}
```

#### GET /api/emotions/dataset-insights
Retrieves insights from processed datasets for a specific emotion.

**Request:**
```json
{
  "emotion": "sadness"
}
```

**Response:**
```json
{
  "emotion": "sadness",
  "insights": {
    "common_causes": [
      "Interpersonal conflicts",
      "Loss or disappointment",
      "Failure or setback"
    ],
    "effective_interventions": [
      "Social support",
      "Physical activity",
      "Expressive writing"
    ],
    "average_duration": "3.2 days",
    "common_transitions": [
      {
        "to_emotion": "neutral",
        "probability": 0.65
      },
      {
        "to_emotion": "joy",
        "probability": 0.25
      }
    ]
  }
}
```

### NEW: Big Data Status Endpoints

#### GET /api/bigdata/status
Retrieves the status of the big data infrastructure.

**Response:**
```json
{
  "kafka": {
    "status": "online",
    "topics": [
      "journal-entries",
      "emotion-analysis",
      "emotional-graph-updates"
    ]
  },
  "spark": {
    "status": "online",
    "active_jobs": 2,
    "completed_jobs": 145,
    "failed_jobs": 3
  },
  "hdfs": {
    "status": "online",
    "total_space": "100GB",
    "used_space": "45GB",
    "free_space": "55GB"
  }
}
```

#### GET /api/bigdata/datasets
Retrieves information about processed datasets.

**Response:**
```json
{
  "datasets": [
    {
      "name": "IEMOCAP",
      "status": "processed",
      "size": "5.2GB",
      "last_updated": "2025-03-10T15:30:00Z",
      "emotions": [
        "anger",
        "sadness",
        "happiness",
        "neutrality",
        "excitement",
        "frustration"
      ]
    },
    {
      "name": "Mental Health Conversations",
      "status": "processed",
      "size": "2.8GB",
      "last_updated": "2025-03-12T09:45:00Z",
      "topics": [
        "depression",
        "anxiety",
        "stress",
        "coping mechanisms",
        "support strategies"
      ]
    }
  ]
}
```

## Database Schema

### Users Collection

```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e1"),
  "name": "John Doe",
  "email": "john.doe@example.com",
  "password": "hashed_password",
  "created_at": ISODate("2025-03-14T12:00:00Z"),
  "updated_at": ISODate("2025-03-14T12:00:00Z")
}
```

### Journal Entries Collection

```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e2"),
  "user_email": "john.doe@example.com",
  "content": "I had a great day today!",
  "created_at": ISODate("2025-03-14T12:00:00Z"),
  "emotion": {
    "primary_emotion": "joy",
    "is_positive": true,
    "emotion_scores": {
      "joy": 0.8,
      "sadness": 0.1,
      "anger": 0.05,
      "fear": 0.03,
      "disgust": 0.02
    }
  },
  "hdfs_path": "hdfs://namenode:9000/user/reflectly/journal-entries/60a1e2c3d4e5f6a7b8c9d0e2"
}
```

### AI Responses Collection

```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e3"),
  "user_email": "john.doe@example.com",
  "entry_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e2"),
  "content": "That's wonderful to hear! What made your day so great?",
  "suggested_actions": [
    "Share your positive experience with others",
    "Practice gratitude",
    "Savor the moment",
    "Set new goals"
  ],
  "dataset_insights": {
    "common_followups": [
      "Express gratitude for specific events",
      "Plan more activities that bring joy"
    ],
    "success_rate": 0.85
  },
  "optimal_path": {
    "current_emotion": "joy",
    "target_emotion": "joy",
    "path": ["joy"],
    "actions": [
      "Continue practicing gratitude",
      "Share your positive experiences"
    ]
  },
  "created_at": ISODate("2025-03-14T12:00:00Z")
}
```

### Emotional States Collection

```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e4"),
  "user_email": "john.doe@example.com",
  "primary_emotion": "joy",
  "is_positive": true,
  "emotion_scores": {
    "joy": 0.8,
    "sadness": 0.1,
    "anger": 0.05,
    "fear": 0.03,
    "disgust": 0.02
  },
  "entry_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e2"),
  "timestamp": ISODate("2025-03-14T12:00:00Z"),
  "hdfs_path": "hdfs://namenode:9000/user/reflectly/emotional-states/60a1e2c3d4e5f6a7b8c9d0e4"
}
```

### Emotional Transitions Collection

```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0f2"),
  "user_email": "john.doe@example.com",
  "from_emotion": "sadness",
  "to_emotion": "joy",
  "from_state_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e5"),
  "to_state_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e4"),
  "actions": [
    {
      "description": "Called a friend",
      "success_rate": 0.75
    },
    {
      "description": "Went for a walk",
      "success_rate": 0.8
    }
  ],
  "timestamp": ISODate("2025-03-14T12:00:00Z"),
  "hdfs_path": "hdfs://namenode:9000/user/reflectly/emotional-transitions/60a1e2c3d4e5f6a7b8c9d0f2"
}
```

### NEW: A* Path Cache Collection

```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0f3"),
  "user_email": "john.doe@example.com",
  "from_emotion": "sadness",
  "to_emotion": "joy",
  "path": ["sadness", "neutral", "joy"],
  "actions": [
    {
      "from": "sadness",
      "to": "neutral",
      "action": "Practice mindfulness",
      "success_rate": 0.75
    },
    {
      "from": "neutral",
      "to": "joy",
      "action": "Engage in a favorite activity",
      "success_rate": 0.8
    }
  ],
  "total_cost": 2.45,
  "estimated_success_rate": 0.6,
  "created_at": ISODate("2025-03-14T12:00:00Z"),
  "expires_at": ISODate("2025-03-15T12:00:00Z")
}
```

### NEW: Dataset Insights Collection

```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0f4"),
  "dataset": "IEMOCAP",
  "emotion": "sadness",
  "insights": {
    "common_causes": [
      "Interpersonal conflicts",
      "Loss or disappointment",
      "Failure or setback"
    ],
    "effective_interventions": [
      "Social support",
      "Physical activity",
      "Expressive writing"
    ],
    "average_duration": "3.2 days",
    "common_transitions": [
      {
        "to_emotion": "neutral",
        "probability": 0.65
      },
      {
        "to_emotion": "joy",
        "probability": 0.25
      }
    ]
  },
  "created_at": ISODate("2025-03-10T15:30:00Z"),
  "updated_at": ISODate("2025-03-10T15:30:00Z")
}
```

## Authentication

Reflectly continues to use JWT (JSON Web Tokens) for authentication. The authentication flow remains the same:

1. **Registration**: The user registers with their name, email, and password.
2. **Login**: The user logs in with their email and password, and receives a JWT token.
3. **Authentication**: The JWT token is included in the Authorization header for authenticated requests.
4. **Verification**: The backend verifies the JWT token for protected routes.

## Deployment

Reflectly is now deployed using Docker Compose with additional containers for the big data infrastructure:

```yaml
version: '3'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    networks:
      - reflectly_network

  backend:
    build: ./backend
    ports:
      - "5002:5002"
    depends_on:
      - mongodb
      - redis
      - kafka
    environment:
      - MONGODB_URI=mongodb://mongodb:27017/reflectly
      - REDIS_URI=redis://redis:6379/0
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - HDFS_NAMENODE=namenode:9000
      - SPARK_MASTER=spark://spark-master:7077
    networks:
      - reflectly_network
      - hadoop_network

  mongodb:
    image: mongo:4.4
    ports:
    mongodb:
    image: mongo:4.4
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    networks:
      - reflectly_network

  redis:
    image: redis:6.2
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - reflectly_network

  namenode:
    image: bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8
    container_name: namenode
    hostname: namenode
    volumes:
      - hadoop_namenode:/hadoop/dfs/name
    environment:
      - CLUSTER_NAME=reflectly
      - CORE_CONF_fs_defaultFS=hdfs://namenode:9000
    ports:
      - "9870:9870"
      - "9000:9000"
    networks:
      - hadoop_network

  datanode:
    image: bde2020/hadoop-datanode:2.0.0-hadoop3.2.1-java8
    container_name: datanode
    hostname: datanode
    volumes:
      - hadoop_datanode:/hadoop/dfs/data
    environment:
      - CORE_CONF_fs_defaultFS=hdfs://namenode:9000
    depends_on:
      - namenode
    networks:
      - hadoop_network
    ports:
      - "9864:9864"

  spark-master:
    image: bde2020/spark-master:3.3.0-hadoop3.3
    container_name: spark-master
    hostname: spark-master
    ports:
      - "8080:8080"
      - "7077:7077"
    environment:
      - CORE_CONF_fs_defaultFS=hdfs://namenode:9000
    volumes:
      - spark_data:/spark/data
    networks:
      - hadoop_network

  spark-worker:
    image: bde2020/spark-worker:3.3.0-hadoop3.3
    container_name: spark-worker
    hostname: spark-worker
    environment:
      - SPARK_MASTER=spark://spark-master:7077
      - CORE_CONF_fs_defaultFS=hdfs://namenode:9000
    volumes:
      - spark_data:/spark/data
    depends_on:
      - spark-master
    networks:
      - hadoop_network
    ports:
      - "8081:8081"

  zookeeper:
    image: wurstmeister/zookeeper
    container_name: zookeeper
    hostname: zookeeper
    ports:
      - "2181:2181"
    networks:
      - hadoop_network

  kafka:
    image: wurstmeister/kafka
    container_name: kafka
    hostname: kafka
    ports:
      - "9092:9092"
    environment:
      - KAFKA_ADVERTISED_HOST_NAME=kafka
      - KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
      - KAFKA_CREATE_TOPICS=journal-entries:3:1,emotion-analysis:3:1,emotional-graph-updates:3:1
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    depends_on:
      - zookeeper
    networks:
      - hadoop_network

networks:
  reflectly_network:
    driver: bridge
  hadoop_network:
    driver: bridge

volumes:
  mongodb_data:
  redis_data:
  hadoop_namenode:
  hadoop_datanode:
  spark_data:
```

The deployment process involves:

1. **Building Docker Images**: Build Docker images for the frontend and backend components.
2. **Starting the Infrastructure**: Start the MongoDB, Redis, Hadoop, Spark, and Kafka containers.
3. **Initializing HDFS**: Create necessary directories in HDFS for storing journal entries, emotional states, and processed datasets.
4. **Importing Datasets**: Import the IEMOCAP and mental health datasets into HDFS.
5. **Processing Datasets**: Process the datasets using Spark jobs.
6. **Starting the Application**: Start the frontend and backend containers.

## Environment Variables

### Backend Environment Variables

```
# MongoDB Configuration
MONGODB_URI=mongodb://mongodb:27017/reflectly

# Redis Configuration
REDIS_URI=redis://redis:6379/0

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ACCESS_TOKEN_EXPIRES=3600

# Admin Configuration
ADMIN_SECRET=your_admin_secret

# Server Configuration
PORT=5002
DEBUG=True

# Big Data Configuration
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
HDFS_NAMENODE=namenode:9000
SPARK_MASTER=spark://spark-master:7077

# Kafka Topics
KAFKA_TOPIC_JOURNAL_ENTRIES=journal-entries
KAFKA_TOPIC_EMOTION_ANALYSIS=emotion-analysis
KAFKA_TOPIC_EMOTIONAL_GRAPH_UPDATES=emotional-graph-updates

# Dataset Paths
DATASET_IEMOCAP_PATH=hdfs://namenode:9000/user/reflectly/datasets/iemocap
DATASET_MENTAL_HEALTH_PATH=hdfs://namenode:9000/user/reflectly/datasets/mental_health
```

### Frontend Environment Variables

```
# API Configuration
REACT_APP_API_URL=http://localhost:5002

# Feature Flags
REACT_APP_ENABLE_VOICE_INPUT=true
REACT_APP_ENABLE_GOAL_TRACKING=true
REACT_APP_ENABLE_EMOTIONAL_JOURNEY_GRAPH=true
REACT_APP_ENABLE_OPTIMAL_PATH_VISUALIZATION=true

# Big Data Status
REACT_APP_SHOW_BIG_DATA_STATUS=true
```

## Setup and Installation

### Prerequisites
- Docker and Docker Compose
- Git
- Web browser

### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/reflectly.git
cd reflectly
```

2. Download the datasets (optional - needed for full functionality):
```bash
mkdir -p data/datasets/iemocap
mkdir -p data/datasets/mental_health
# Download datasets from Kaggle and place them in the respective directories
```

3. Start the infrastructure:
```bash
docker-compose up -d namenode datanode spark-master spark-worker zookeeper kafka mongodb redis
```

4. Initialize HDFS directories:
```bash
docker exec -it namenode hdfs dfs -mkdir -p /user/reflectly/journal-entries
docker exec -it namenode hdfs dfs -mkdir -p /user/reflectly/emotional-states
docker exec -it namenode hdfs dfs -mkdir -p /user/reflectly/emotional-transitions
docker exec -it namenode hdfs dfs -mkdir -p /user/reflectly/datasets
```

5. Import datasets to HDFS (if downloaded):
```bash
docker exec -it namenode hdfs dfs -put /path/to/data/datasets/iemocap /user/reflectly/datasets/
docker exec -it namenode hdfs dfs -put /path/to/data/datasets/mental_health /user/reflectly/datasets/
```

6. Start the application:
```bash
docker-compose up -d frontend backend
```

7. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5002
- Hadoop UI: http://localhost:9870
- Spark UI: http://localhost:8080