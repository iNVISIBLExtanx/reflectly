# Reflectly Technical Documentation

**Version:** 2.0.0  
**Last Updated:** March 21, 2025  
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
  - [Goal Tracker](#goal-tracker)
  - [Memory Manager](#memory-manager)
  - [Search Algorithm](#search-algorithm)
  - [Emotion Analyzer](#emotion-analyzer)
- [Frontend Components](#frontend-components)
- [Data Flow](#data-flow)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Authentication](#authentication)
- [Big Data Infrastructure](#big-data-infrastructure)
  - [Hadoop](#hadoop)
  - [Spark](#spark)
  - [Kafka](#kafka)
  - [Spark Jobs](#spark-jobs)
- [Deployment](#deployment)
  - [Local Development](#local-development)
  - [Docker Deployment](#docker-deployment)
- [Environment Variables](#environment-variables)
- [Maintenance and Troubleshooting](#maintenance-and-troubleshooting)

## Project Overview

Reflectly is a personal journaling application with a conversational interface designed to help users engage in meaningful self-reflection. The application combines a chat-like interface with intelligent emotional support and goal tracking features. The system uses emotional analysis to provide personalized responses and help users navigate from negative emotional states to positive ones.

### Core Functionality
- **Conversational Journaling**: Users interact with the application through a chat interface
- **Emotion Analysis**: The system analyzes user emotions from journal entries
- **Emotional Graph**: Tracks transitions between emotional states and suggests personalized interventions based on user history
- **Personalized Responses**: Generates responses tailored to the user's emotional context and history
- **Goal Tracking**: Users can set and track personal goals

## System Architecture

Reflectly follows a client-server architecture with separate frontend and backend components, enhanced with a big data infrastructure for advanced analytics:

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│    Frontend     │◄────►│    Backend      │◄────►│    Database     │
│    (React.js)   │      │    (Flask)      │      │    (MongoDB)    │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                  ▲                        ▲
                                  │                        │
                                  ▼                        ▼
                         ┌─────────────────┐      ┌─────────────────┐
                         │                 │      │                 │
                         │     Redis       │      │     Kafka       │
                         │    (Cache)      │      │   (Messaging)   │
                         │                 │      │                 │
                         └─────────────────┘      └─────────────────┘
                                                          ▲
                                                          │
                                                          ▼
                                               ┌─────────────────────┐
                                               │                     │
                                               │  Big Data Platform  │
                                               │  (Hadoop & Spark)   │
                                               │                     │
                                               └─────────────────────┘
```

- **Frontend**: React.js application providing the user interface
- **Backend**: Flask application handling business logic, emotion analysis, and response generation
- **Database**: MongoDB for persistent storage of user data, journal entries, and emotional states
- **Cache**: Redis for temporary data storage and session management
- **Messaging**: Kafka for event streaming and asynchronous processing
- **Big Data Platform**: Hadoop and Spark for large-scale data processing and analytics

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
- **Emotion Analysis**: Custom implementation with BERT/RoBERTa models
- **Response Generation**: Template-based with personalization logic
- **Caching**: Redis
- **Message Broker**: Kafka
- **Big Data Processing**: Hadoop, Spark

### Database
- **Primary Database**: MongoDB
- **Caching**: Redis

### DevOps
- **Containerization**: Docker
- **Container Orchestration**: Docker Compose
- **Version Control**: Git
- **CI/CD**: GitHub Actions

## Directory Structure

```
/
├── backend/                # Flask backend application
│   ├── models/             # Business logic models
│   │   ├── emotion_analyzer.py     # Emotion analysis from text
│   │   ├── emotional_graph.py      # Emotional state tracking and transitions
│   │   ├── emotional_graph_bigdata.py  # Big data version of emotional graph
│   │   ├── goal_tracker.py         # Goal tracking functionality
│   │   ├── memory_manager.py       # Memory management for contextual responses
│   │   ├── response_generator.py   # AI response generation
│   │   └── search_algorithm.py     # Search algorithms for memory retrieval
│   ├── services/           # External service integrations
│   │   ├── hdfs_service.py         # HDFS integration
│   │   ├── kafka_service.py        # Kafka integration
│   │   └── spark_service.py        # Spark integration
│   ├── app.py              # Main Flask application
│   ├── admin_viewer.py     # Admin interface
│   ├── user_management.py  # User management functionality
│   ├── requirements.txt    # Python dependencies
│   └── start_backend.sh    # Script to start the backend server
│
├── frontend/               # React frontend application
│   ├── public/             # Static assets
│   ├── src/                # Source code
│   │   ├── assets/         # Static assets (images, icons)
│   │   ├── components/     # Reusable UI components
│   │   │   ├── journal/    # Journal-related components
│   │   │   └── layout/     # Layout components
│   │   ├── context/        # React context providers
│   │   │   ├── AuthContext.js  # Authentication context
│   │   ├── pages/          # Application pages
│   │   │   ├── Journal.js      # Journal page
│   │   │   ├── Profile.js      # User profile page
│   │   │   └── ...             # Other pages
│   │   ├── services/       # Service integrations
│   │   ├── utils/          # Utility functions
│   │   │   └── axiosConfig.js  # Axios configuration
│   │   ├── App.js          # Main application component
│   │   └── index.js        # Entry point
│   ├── package.json        # NPM dependencies
│   └── Dockerfile          # Frontend Docker configuration
│
├── spark/                  # Spark jobs and utilities
│   ├── jobs/               # Spark job definitions
│   │   ├── dataset_import.py     # Data import job
│   │   ├── emotion_analysis.py   # Emotion analysis job
│   │   ├── graph_processing.py   # Graph processing job
│   │   └── path_finding.py       # Path finding algorithms
│   └── utils/              # Spark utilities
│
├── docker/                 # Docker configuration
├── data/                   # Data directory
├── docker-compose.yml      # Docker Compose configuration
├── start_reflectly.sh      # Script to start the entire application
├── stop_reflectly.sh       # Script to stop the application
├── copy_spark_jobs.sh      # Script to copy Spark jobs to HDFS
├── run_spark_jobs.sh       # Script to run Spark jobs
│
└── docs/                   # Project documentation
    ├── technical_documentation.md       # Technical documentation
    ├── technical_documentation_V2.md    # Updated technical documentation
    ├── context.md                       # Project context
    ├── contextV2.md                     # Updated project context
    └── contextV3.md                     # Latest project context
```

## Backend Components

### Emotional Graph

The `EmotionalGraph` class is responsible for tracking and analyzing user emotional states and transitions between them. It provides methods for recording emotions, retrieving emotional history, and suggesting personalized actions based on the user's emotional patterns.

#### Key Features

- **Emotion Recording**: Records user emotional states in MongoDB
- **Transition Tracking**: Tracks transitions between emotional states
- **Personalized Suggestions**: Provides personalized suggestions for transitioning from negative to positive emotional states
- **Emotional History**: Retrieves a user's emotional history for context-aware responses

#### Implementation

The `EmotionalGraph` class uses a graph-like structure to represent emotional states and transitions. Each node in the graph represents an emotional state, and edges represent transitions between states. The class provides methods for:

1. **Recording Emotions**: The `record_emotion` method records a user's emotional state and creates transitions between states.

```python
def record_emotion(self, user_email, emotion_data, entry_id=None):
    # Store the emotional state in MongoDB
    # Create transitions between states
    # Return the stored emotion document
```

2. **Getting Personalized Suggestions**: The `get_suggested_actions` method provides personalized suggestions for transitioning from the current emotional state based on the user's history.

```python
def get_suggested_actions(self, user_email, current_emotion):
    # If current emotion is positive, return generic suggestions
    # Find personalized suggestions based on user's emotional history
    # Return personalized or generic suggestions
```

3. **Finding Personalized Path Suggestions**: The `_find_personalized_path_suggestions` method identifies paths that have previously led from the current emotion to positive emotions.

```python
def _find_personalized_path_suggestions(self, user_email, current_emotion):
    # Get transitions from the current emotion to any positive emotion
    # Extract personalized suggestions based on content analysis
    # Return personalized suggestions
```

4. **Retrieving Emotional History**: The `get_emotion_history` method retrieves a user's emotional history for context-aware responses.

```python
def get_emotion_history(self, user_email, limit=5):
    # Get the most recent emotional states for the user
    # Convert ObjectId to string for serialization
    # Return emotional history
```

### Response Generator

The `ResponseGenerator` class generates personalized responses based on user input, emotion analysis, and emotional history. It provides methods for generating responses with different levels of personalization.

#### Key Features

- **Template-Based Responses**: Uses templates for different emotional states
- **Personalized Responses**: Incorporates user's emotional history for personalized responses
- **Suggested Actions**: Includes suggested actions for emotional improvement

#### Implementation

The `ResponseGenerator` class uses a template-based approach for generating responses, with additional personalization based on the user's emotional history. The class provides methods for:

1. **Generating Basic Responses**: The `generate` method generates a basic response based on user input and emotion analysis.

```python
def generate(self, text, emotion_data):
    # Generate a response based on the primary emotion
    # Return a formatted response
```

2. **Generating Personalized Responses**: The `generate_with_memory` method generates a personalized response incorporating emotional history and suggested actions.

```python
def generate_with_memory(self, text, emotion_data, memories=None, suggested_actions=None, emotion_history=None):
    # Generate a personalized response based on emotional context
    # Use provided suggested actions or generate generic ones
    # Add context about emotional journey
    # Return a response object with text and suggested actions
```

3. **Generating Context-Aware Responses**: The `_generate_personalized_response` method enhances responses with insights from the user's emotional history.

```python
def _generate_personalized_response(self, text, emotion_data, emotion_history=None):
    # Start with a base response
    # Enhance with personalized insights based on emotional history
    # Return a personalized response
```

### Journal Entry Processing

The journal entry processing logic in `app.py` handles the creation of journal entries, emotion analysis, and response generation. It integrates the `EmotionalGraph` and `ResponseGenerator` components to provide a complete journaling experience.

#### Key Features

- **Journal Entry Creation**: Creates journal entries in MongoDB
- **Emotion Analysis**: Analyzes emotions from journal entry text
- **Emotional Graph Integration**: Records emotions and transitions in the emotional graph
- **Personalized Response Generation**: Generates personalized responses based on emotional context and history

#### Implementation

The journal entry processing logic is implemented in the `create_journal_entry` route in `app.py`. The route handles:

1. **Journal Entry Creation**: Creates a journal entry in MongoDB.
2. **Emotion Analysis**: Analyzes emotions from the journal entry text.
3. **Emotional Graph Integration**: Records emotions and transitions in the emotional graph.
4. **Emotional History Retrieval**: Retrieves the user's emotional history for context.
5. **Personalized Suggestion Generation**: Gets personalized suggested actions from the emotional graph.
6. **Personalized Response Generation**: Generates a personalized response based on emotional context and history.

```python
@app.route('/api/journal/entries', methods=['POST'])
def create_journal_entry():
    # Create journal entry
    # Analyze emotions
    # Record emotion in emotional graph
    # Get emotional history
    # Get personalized suggested actions
    # Generate personalized response
    # Return response to frontend
```

### Goal Tracker

The `GoalTracker` class is responsible for managing user goals and tracking progress towards them. It provides methods for creating, retrieving, and updating goals.

#### Key Features

- **Goal Creation**: Creates goals with targets and deadlines
- **Progress Tracking**: Tracks progress towards goals
- **Goal Retrieval**: Retrieves goals for display and analysis

#### Implementation

The `GoalTracker` class provides methods for:

1. **Creating Goals**: The `create_goal` method creates a new goal with a target and deadline.

```python
def create_goal(self, user_email, goal_data):
    # Validate goal data
    # Create goal in MongoDB
    # Return the created goal
```

2. **Updating Goal Progress**: The `update_goal_progress` method updates the progress towards a goal.

```python
def update_goal_progress(self, goal_id, progress_data):
    # Validate progress data
    # Update goal progress in MongoDB
    # Return the updated goal
```

3. **Retrieving Goals**: The `get_goals` method retrieves goals for a user.

```python
def get_goals(self, user_email, status=None):
    # Get goals from MongoDB
    # Filter by status if provided
    # Return goals
```

### Memory Manager

The `MemoryManager` class is responsible for managing memories of past interactions and providing context for personalized responses. It provides methods for storing, retrieving, and searching memories.

#### Key Features

- **Memory Storage**: Stores memories of past interactions
- **Memory Retrieval**: Retrieves memories based on context
- **Memory Search**: Searches memories for relevant information

#### Implementation

The `MemoryManager` class provides methods for:

1. **Storing Memories**: The `store_memory` method stores a memory of a past interaction.

```python
def store_memory(self, user_email, memory_data):
    # Validate memory data
    # Store memory in MongoDB
    # Return the stored memory
```

2. **Retrieving Memories**: The `get_memories` method retrieves memories for a user.

```python
def get_memories(self, user_email, limit=10):
    # Get memories from MongoDB
    # Sort by relevance or recency
    # Return memories
```

3. **Searching Memories**: The `search_memories` method searches memories for relevant information.

```python
def search_memories(self, user_email, query):
    # Search memories in MongoDB
    # Rank by relevance
    # Return matching memories
```

### Search Algorithm

The `SearchAlgorithm` class provides advanced search capabilities for finding relevant information in the user's journal entries and memories. It uses natural language processing techniques to improve search results.

#### Key Features

- **Semantic Search**: Searches based on meaning rather than exact matches
- **Relevance Ranking**: Ranks search results by relevance
- **Context-Aware Search**: Considers context in search results

#### Implementation

The `SearchAlgorithm` class provides methods for:

1. **Searching Entries**: The `search_entries` method searches journal entries for relevant information.

```python
def search_entries(self, user_email, query):
    # Vectorize query
    # Search entries in MongoDB
    # Rank by relevance
    # Return matching entries
```

2. **Searching Memories**: The `search_memories` method searches memories for relevant information.

```python
def search_memories(self, user_email, query):
    # Vectorize query
    # Search memories in MongoDB
    # Rank by relevance
    # Return matching memories
```

### Emotion Analyzer

The `EmotionAnalyzer` class is responsible for analyzing emotions from text. It uses natural language processing techniques to identify emotions and their intensity.

#### Key Features

- **Emotion Detection**: Detects emotions from text
- **Emotion Intensity**: Measures the intensity of emotions
- **Emotion Classification**: Classifies emotions into categories

#### Implementation

The `EmotionAnalyzer` class provides methods for:

1. **Analyzing Emotions**: The `analyze` method analyzes emotions from text.

```python
def analyze(self, text):
    # Preprocess text
    # Apply emotion analysis model
    # Return emotion data
```

2. **Getting Primary Emotion**: The `get_primary_emotion` method gets the primary emotion from emotion data.

```python
def get_primary_emotion(self, emotion_scores):
    # Find the emotion with the highest score
    # Return the primary emotion
```

## Frontend Components

The frontend of Reflectly is built with React.js and Material-UI. It provides a chat-like interface for journaling and displays AI responses with suggested actions.

### Key Components

- **Journal Page**: The main page for journaling, displaying the chat interface and handling user input.
- **Message Bubbles**: Components for displaying user messages and AI responses.
- **Suggested Actions**: Chips displaying suggested actions for emotional improvement.
- **Emotion Icons**: Icons representing different emotional states.

### Implementation

The frontend implementation includes:

1. **Journal Entry Creation**: Sends journal entries to the backend API and displays responses.

```javascript
const handleSubmit = async (e) => {
  // Send journal entry to API
  // Display AI response with suggested actions
};
```

2. **Response Display**: Displays AI responses with suggested actions.

```jsx
<Typography variant="body1">{entry.content}</Typography>

{/* Display suggested actions if available */}
{!entry.isUserMessage && entry.suggested_actions && entry.suggested_actions.length > 0 && (
  <Box sx={{ mt: 2 }}>
    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
      Suggested Actions:
    </Typography>
    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
      {entry.suggested_actions.map((action, index) => (
        <Chip 
          key={index}
          label={action}
          size="small"
          color="primary"
          variant="outlined"
          sx={{ 
            borderRadius: 1,
            '&:hover': { backgroundColor: 'primary.light', color: 'white', cursor: 'pointer' }
          }}
        />
      ))}
    </Box>
  </Box>
)}
```

## Data Flow

The data flow in Reflectly follows these steps:

1. **User Input**: The user enters a journal entry in the frontend.
2. **API Request**: The frontend sends the journal entry to the backend API.
3. **Emotion Analysis**: The backend analyzes emotions from the journal entry text.
4. **Emotional Graph**: The backend records emotions and transitions in the emotional graph.
5. **Emotional History**: The backend retrieves the user's emotional history for context.
6. **Personalized Suggestions**: The backend gets personalized suggested actions from the emotional graph.
7. **Personalized Response**: The backend generates a personalized response based on emotional context and history.
8. **API Response**: The backend sends the response back to the frontend.
9. **UI Update**: The frontend displays the response with suggested actions.

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
    ]
  }
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
  }
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
  "timestamp": ISODate("2025-03-14T12:00:00Z")
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
  "timestamp": ISODate("2025-03-14T12:00:00Z")
}
```

## Authentication

Reflectly uses JWT (JSON Web Tokens) for authentication. The authentication flow is as follows:

1. **Registration**: The user registers with their name, email, and password.
2. **Login**: The user logs in with their email and password, and receives a JWT token.
3. **Authentication**: The JWT token is included in the Authorization header for authenticated requests.
4. **Verification**: The backend verifies the JWT token for protected routes.

## Big Data Infrastructure

Reflectly incorporates a big data infrastructure for advanced analytics and processing of emotional data at scale.

### Hadoop

Hadoop provides distributed storage and processing capabilities:

- **HDFS**: Distributed file system for storing large datasets
- **NameNode**: Manages the file system namespace and regulates access to files
- **DataNode**: Stores and retrieves blocks as directed by the NameNode

### Spark

Spark provides in-memory processing for large-scale data analysis:

- **Spark Master**: Coordinates and manages Spark applications
- **Spark Worker**: Executes tasks assigned by the Spark Master
- **Spark Jobs**: Custom jobs for data processing and analysis

### Kafka

Kafka provides a distributed messaging system for event streaming:

- **Topics**: Categories for organizing messages
  - `journal-entries`: Stream of journal entries
  - `emotion-analysis`: Stream of emotion analysis results
  - `emotional-graph-updates`: Stream of updates to the emotional graph
- **Producers**: Components that publish messages to topics
- **Consumers**: Components that subscribe to topics and process messages

### Spark Jobs

Reflectly includes several Spark jobs for big data processing:

1. **Dataset Import**: Imports datasets into HDFS for analysis
   ```python
   # Import dataset from various sources into HDFS
   def import_dataset(source_path, hdfs_path):
       # Read data from source
       # Process and clean data
       # Write to HDFS
   ```

2. **Emotion Analysis**: Analyzes emotions from journal entries at scale
   ```python
   # Analyze emotions from journal entries
   def analyze_emotions(entries_path):
       # Load entries from HDFS
       # Apply emotion analysis models
       # Save results to HDFS
   ```

3. **Graph Processing**: Processes the emotional graph for pattern recognition
   ```python
   # Process emotional graph for pattern recognition
   def process_graph(graph_path):
       # Load graph from HDFS
       # Apply graph algorithms
       # Save results to HDFS
   ```

4. **Path Finding**: Finds optimal paths between emotional states
   ```python
   # Find optimal paths between emotional states
   def find_paths(graph_path):
       # Load graph from HDFS
       # Apply path finding algorithms
       # Save results to HDFS
   ```

## Deployment

Reflectly can be deployed using different methods depending on the environment.

### Local Development

For local development, the application can be started using the provided scripts:

1. **Start Backend**: Run the backend server
   ```bash
   cd backend
   ./start_backend.sh
   ```

2. **Start Frontend**: Run the frontend development server
   ```bash
   cd frontend
   npm start
   ```

3. **Start Everything**: Use the start_reflectly.sh script
   ```bash
   ./start_reflectly.sh
   ```

### Docker Deployment

For production deployment, Docker Compose is used to orchestrate the containers:

1. **Build and Start Containers**: Start all containers
   ```bash
   docker-compose up -d
   ```

2. **Stop Containers**: Stop all containers
   ```bash
   docker-compose down
   ```

3. **View Logs**: View container logs
   ```bash
   docker-compose logs -f
   ```

## Environment Variables

### Backend Environment Variables

```
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/reflectly

# Redis Configuration
REDIS_URI=redis://localhost:6379/0

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
```

### Frontend Environment Variables

```
# API Configuration
REACT_APP_API_URL=http://localhost:5002

# Feature Flags
REACT_APP_ENABLE_VOICE_INPUT=true
REACT_APP_ENABLE_GOAL_TRACKING=true
```

## Maintenance and Troubleshooting

### Database Management

#### Resetting Databases

To reset the MongoDB and Redis databases, you can use the provided scripts:

1. **Reset Databases**: This will delete all data in MongoDB and Redis
   ```bash
   ./reset_databases.sh
   ```

2. **Initialize Databases**: This will create the necessary collections in MongoDB
   ```bash
   ./initialize_database.sh
   ```

#### Backing Up Databases

To back up the MongoDB database:

```bash
mongodump --uri="mongodb://localhost:27017/reflectly" --out=./backup
```

To restore the MongoDB database:

```bash
mongorestore --uri="mongodb://localhost:27017/reflectly" --dir=./backup/reflectly
```

### Log Management

Logs are available in the following locations:

- **Backend Logs**: Standard output when running the backend server
- **Frontend Logs**: Standard output when running the frontend server
- **Docker Logs**: Available through `docker-compose logs`

### Common Issues

1. **Connection Issues**: If the frontend cannot connect to the backend, check that both are running and that the API URL is correctly configured.

2. **Database Issues**: If there are issues with the database, check the MongoDB connection string and ensure the MongoDB service is running.

3. **Big Data Infrastructure Issues**: If there are issues with the big data infrastructure, check that all required services (Hadoop, Spark, Kafka) are running and properly configured.