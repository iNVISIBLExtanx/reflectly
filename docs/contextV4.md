# Reflectly Technical Documentation

**Version:** 3.0.0  
**Last Updated:** March 28, 2025  
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
  - [Probabilistic Reasoning](#probabilistic-reasoning)
  - [Intelligent Agent](#intelligent-agent)
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

Reflectly is a personal journaling application with a conversational interface designed to help users engage in meaningful self-reflection. The application combines a chat-like interface with intelligent emotional support and goal tracking features. The system uses advanced AI techniques including A* search algorithms and probabilistic reasoning to analyze emotional states and provide personalized guidance to help users navigate from negative to positive emotional states.

### Core Functionality
- **Conversational Journaling**: Users interact with the application through a chat interface
- **Emotion Analysis**: The system analyzes user emotions from journal entries
- **Emotional Graph**: Tracks transitions between emotional states and suggests personalized interventions based on user history
- **Advanced Search**: A* search algorithm finds optimal paths between emotional states
- **Probabilistic Reasoning**: Uses Bayesian networks and Markov chains to predict emotional transitions
- **Intelligent Agent**: Sophisticated state management and action planning for personalized guidance
- **Personalized Responses**: Generates responses tailored to the user's emotional context and history
- **Goal Tracking**: Users can set and track personal goals

## System Architecture

Reflectly follows an enhanced client-server architecture with separate frontend and backend components, a big data infrastructure for advanced analytics, and new AI components for sophisticated decision-making:

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
          ┌────────────────────┐      ┌────────────────────────────┐
          │                    │      │                            │
          │       Redis        │◄────►│           Kafka            │
          │      (Cache)       │      │        (Messaging)         │
          │                    │      │                            │
          └────────────────────┘      └────────────────────────────┘
                                                    ▲
                                                    │
                                                    ▼
                            ┌────────────────────────────────────────┐
                            │                                        │
                            │           Big Data Platform            │
                            │           (Hadoop & Spark)             │
                            │                                        │
                            └────────────────────────────────────────┘
                                                    ▲
                                                    │
                                                    ▼
          ┌────────────────────┐      ┌────────────────────────────┐
          │                    │      │                            │
          │   A* Search        │◄────►│    Probabilistic Models    │
          │   Engine           │      │    (Bayesian Networks)     │
          │                    │      │                            │
          └────────────────────┘      └────────────────────────────┘
                    ▲                              ▲
                    │                              │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                      ┌─────────────────────────┐
                      │                         │
                      │    Intelligent Agent    │
                      │                         │
                      └─────────────────────────┘
```

- **Frontend**: React.js application providing the user interface
- **Backend**: Flask application handling business logic, emotion analysis, and response generation
- **Database**: MongoDB for persistent storage of user data, journal entries, and emotional states
- **Cache**: Redis for temporary data storage and session management
- **Messaging**: Kafka for event streaming and asynchronous processing
- **Big Data Platform**: Hadoop and Spark for large-scale data processing and analytics
- **A* Search Engine**: Specialized component for finding optimal paths in emotional state graphs
- **Probabilistic Models**: Bayesian networks and Markov chains for emotional state prediction
- **Intelligent Agent**: Sophisticated state management and action planning system

## Technology Stack

### Frontend
- **Framework**: React.js
- **UI Library**: Material-UI
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Date Handling**: date-fns
- **Visualization**: D3.js for emotional graph visualization

### Backend
- **Framework**: Flask (Python)
- **Authentication**: JWT (JSON Web Tokens)
- **Database ORM**: PyMongo
- **Emotion Analysis**: Custom implementation with BERT/RoBERTa models
- **Response Generation**: Template-based with personalization logic
- **Caching**: Redis
- **Message Broker**: Kafka
- **Graph Processing**: NetworkX for graph representation and analysis
- **Search Algorithms**: A* implementation for finding optimal emotional paths
- **Probabilistic Models**: PyMC3 for Bayesian networks, pomegranate for Markov models
- **Agent Framework**: Custom implementation for intelligent agent

### Big Data Infrastructure
- **Distributed Storage**: Hadoop HDFS
- **Distributed Processing**: Apache Spark
- **Stream Processing**: Apache Kafka
- **Machine Learning**: Spark MLlib for distributed machine learning

### Database
- **Primary Database**: MongoDB
- **Caching**: Redis
- **Graph Database**: MongoDB with graph-like collections

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
│   │   ├── emotion_analyzer.py            # Emotion analysis from text
│   │   ├── emotional_graph.py             # Emotional state tracking and transitions
│   │   ├── emotional_graph_bigdata.py     # Big data version of emotional graph
│   │   ├── goal_tracker.py                # Goal tracking functionality
│   │   ├── memory_manager.py              # Memory management for contextual responses
│   │   ├── response_generator.py          # AI response generation
│   │   ├── search_algorithm.py            # NEW: Enhanced with A* search
│   │   ├── probabilistic_reasoning.py     # NEW: Bayesian networks and Markov models
│   │   ├── intelligent_agent.py           # NEW: Agent with state management
│   │   └── uncertainty_handling.py        # NEW: Handling uncertainty in predictions
│   ├── services/           # External service integrations
│   │   ├── hdfs_service.py               # HDFS integration
│   │   ├── kafka_service.py              # Kafka integration
│   │   ├── spark_service.py              # Spark integration
│   │   └── model_service.py              # NEW: Model serving service
│   ├── utils/              # Utility functions
│   │   ├── graph_utils.py               # NEW: Graph utilities
│   │   ├── path_utils.py                # NEW: Path finding utilities
│   │   ├── bayes_utils.py               # NEW: Bayesian utilities
│   │   └── markov_utils.py              # NEW: Markov model utilities
│   ├── app.py              # Main Flask application
│   ├── admin_viewer.py     # Admin interface
│   ├── user_management.py  # User management functionality
│   ├── requirements.txt    # Python dependencies
│   └── start_backend.sh    # Script to start the backend server
│
├── ai/                     # NEW: AI components
│   ├── search/             # A* search implementation
│   │   ├── a_star.py                    # A* search algorithm
│   │   ├── heuristics.py                # Heuristic functions
│   │   ├── path_evaluation.py           # Path evaluation utilities
│   │   └── graph_traversal.py           # Graph traversal algorithms
│   ├── probabilistic/      # Probabilistic models
│   │   ├── bayesian_network.py          # Bayesian network implementation
│   │   ├── markov_chain.py              # Markov chain implementation
│   │   ├── emotion_prediction.py        # Emotion prediction models
│   │   └── uncertainty_models.py        # Uncertainty modeling
│   ├── agent/              # Intelligent agent
│   │   ├── state_manager.py             # Agent state management
│   │   ├── action_planner.py            # Action planning
│   │   ├── decision_maker.py            # Decision making logic
│   │   └── response_builder.py          # Response construction
│   └── training/           # Model training scripts
│       ├── train_bayesian.py            # Bayesian network training
│       ├── train_markov.py              # Markov chain training
│       ├── train_astar_heuristics.py    # A* heuristic training
│       └── emotion_classifier.py        # Emotion classifier training
│
├── frontend/               # React frontend application
│   ├── public/             # Static assets
│   ├── src/                # Source code
│   │   ├── assets/         # Static assets (images, icons)
│   │   ├── components/     # Reusable UI components
│   │   │   ├── journal/    # Journal-related components
│   │   │   ├── layout/     # Layout components
│   │   │   └── ai/         # NEW: AI visualization components
│   │   │       ├── EmotionalPathView.js    # NEW: Path visualization
│   │   │       ├── ProbabilityGraph.js     # NEW: Probability visualization
│   │   │       └── AgentStateView.js       # NEW: Agent state visualization
│   │   ├── context/        # React context providers
│   │   │   ├── AuthContext.js           # Authentication context
│   │   │   └── AIContext.js             # NEW: AI context for decision visibility
│   │   ├── pages/          # Application pages
│   │   │   ├── Journal.js              # Journal page
│   │   │   ├── Profile.js              # User profile page
│   │   │   ├── EmotionalJourney.js     # NEW: Emotional journey visualization
│   │   │   ├── DecisionExplorer.js     # NEW: AI decision process explorer
│   │   │   └── ...                     # Other pages
│   │   ├── services/       # Service integrations
│   │   ├── utils/          # Utility functions
│   │   │   ├── axiosConfig.js          # Axios configuration
│   │   │   └── graphUtils.js           # NEW: Graph utilities for visualization
│   │   ├── App.js          # Main application component
│   │   └── index.js        # Entry point
│   ├── package.json        # NPM dependencies
│   └── Dockerfile          # Frontend Docker configuration
│
├── spark/                  # Spark jobs and utilities
│   ├── jobs/               # Spark job definitions
│   │   ├── dataset_import.py           # Data import job
│   │   ├── emotion_analysis.py         # Emotion analysis job
│   │   ├── graph_processing.py         # Graph processing job
│   │   ├── path_finding.py             # Path finding algorithms
│   │   ├── bayesian_network_job.py     # NEW: Bayesian network processing
│   │   └── markov_chain_job.py         # NEW: Markov chain processing
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
    ├── technical_documentation_V3.md    # NEW: Phase 3 technical documentation
    ├── context.md                       # Project context
    ├── contextV2.md                     # Updated project context
    └── contextV3.md                     # NEW: Phase 3 project context
```

## Backend Components

### Emotional Graph

The `EmotionalGraph` class has been enhanced to support advanced path finding and probabilistic transitions:

#### Key Enhancements

- **Graph Representation**: More sophisticated graph structure with weighted edges and metadata
- **Transition Probabilities**: Edges now include transition probabilities
- **Action Effects**: Edges include data about action effectiveness
- **Temporal Patterns**: Tracking of temporal patterns in emotional transitions
- **Integration with A* Search**: Direct integration with the A* search algorithm
- **Integration with Probabilistic Models**: Connection to Bayesian networks and Markov chains

#### Implementation

The enhanced `EmotionalGraph` class now provides:

1. **Advanced Graph Construction**: Building a more sophisticated graph structure with probabilistic transitions.
2. **Weighted Path Finding**: Finding weighted paths between emotional states considering multiple factors.
3. **Probabilistic Transitions**: Calculating transition probabilities between emotional states.
4. **Optimal Action Identification**: Identifying the most effective actions for emotional state transitions.
5. **Temporal Pattern Analysis**: Analyzing patterns in emotional transitions over time.

### Response Generator

The `ResponseGenerator` class has been enhanced to leverage the A* search results and probabilistic reasoning:

#### Key Enhancements

- **Path-Based Responses**: Generates responses based on optimal paths from A* search
- **Probability-Aware Suggestions**: Suggests actions based on probabilistic effectiveness
- **Uncertainty Handling**: Includes measures of certainty in suggestions
- **Multi-Step Planning**: Provides multi-step plans for emotional improvement
- **Integration with Intelligent Agent**: Coordinates with the intelligent agent for response generation

#### Implementation

The enhanced `ResponseGenerator` class now provides:

1. **Generating Path-Based Responses**: Generating responses based on optimal paths.
2. **Suggesting Probabilistic Actions**: Suggesting actions with probabilistic effectiveness.
3. **Handling Uncertainty**: Including measures of certainty in suggestions.
4. **Providing Multi-Step Plans**: Offering multi-step plans for emotional improvement.
5. **Coordinating with Intelligent Agent**: Working with the intelligent agent for sophisticated response generation.

### Journal Entry Processing

The journal entry processing logic has been enhanced to leverage A* search and probabilistic reasoning:

#### Key Enhancements

- **Sophisticated Emotion Analysis**: More detailed emotion analysis using machine learning
- **State Tracking**: Tracking the user's emotional state over time
- **Optimal Path Identification**: Finding optimal paths to positive emotional states
- **Probabilistic Action Suggestion**: Suggesting actions with probabilistic effectiveness
- **Intelligent Agent Integration**: Coordinating with the intelligent agent for decision-making

#### Implementation

The enhanced journal entry processing flow:

1. **Detailed Emotion Analysis**: Analyzing emotions with greater detail and nuance.
2. **Emotional State Tracking**: Tracking the user's emotional state trajectory.
3. **Optimal Path Finding**: Using A* search to find optimal paths to positive emotions.
4. **Probabilistic Suggestion Generation**: Generating suggestions with probabilistic backing.
5. **Agent-Driven Response Generation**: Using the intelligent agent for sophisticated responses.

### Goal Tracker

The `GoalTracker` class has been enhanced to integrate with the emotional graph and probabilistic reasoning:

#### Key Enhancements

- **Emotional Impact Analysis**: Analyzing the emotional impact of goal progress
- **Probabilistic Goal Achievement**: Predicting goal achievement probability
- **Path-Based Goal Planning**: Planning goals based on emotional paths
- **Integration with Agent**: Coordination with the intelligent agent for goal recommendations

#### Implementation

The enhanced `GoalTracker` class provides:

1. **Analyzing Emotional Impact**: Understanding how goals affect emotional states.
2. **Predicting Achievement**: Using probabilistic models to predict goal achievement.
3. **Planning Goals**: Creating goal plans based on emotional paths.
4. **Recommending Goals**: Working with the intelligent agent to recommend goals.

### Memory Manager

The `MemoryManager` class has been enhanced for more sophisticated memory retrieval:

#### Key Enhancements

- **A* Search Integration**: Using A* search for relevant memory retrieval
- **Probabilistic Memory Selection**: Selecting memories based on probabilistic relevance
- **Pattern-Based Retrieval**: Retrieving memories based on emotional patterns
- **Integration with Agent**: Coordination with the intelligent agent for memory selection

#### Implementation

The enhanced `MemoryManager` class provides:

1. **A* Search for Memories**: Finding memories using path-based searches.
2. **Probabilistic Selection**: Selecting memories based on relevance probabilities.
3. **Pattern Recognition**: Identifying patterns in memories for retrieval.
4. **Agent-Driven Selection**: Using the intelligent agent to guide memory selection.

### Search Algorithm

The `SearchAlgorithm` class has been significantly enhanced with A* search capabilities:

#### Key Enhancements

- **A* Search Implementation**: Implementation of the A* search algorithm
- **Custom Heuristics**: Custom heuristic functions for emotional path finding
- **Path Evaluation**: Sophisticated path evaluation and ranking
- **Multi-Criteria Optimization**: Considering multiple criteria in path selection
- **Uncertainty Handling**: Handling uncertainty in path finding

#### Implementation

The enhanced `SearchAlgorithm` class now provides:

1. **Implementing A* Search**: Core A* search algorithm for finding optimal paths.
2. **Designing Heuristics**: Custom heuristic functions for emotional path finding.
3. **Evaluating Paths**: Sophisticated evaluation of potential paths.
4. **Multi-Criteria Optimization**: Balancing multiple factors in path selection.
5. **Handling Uncertainty**: Managing uncertainty in path finding and selection.

### Emotion Analyzer

The `EmotionAnalyzer` class has been enhanced for more nuanced emotion analysis:

#### Key Enhancements

- **Nuanced Emotion Detection**: Detecting more nuanced emotional states
- **Context-Aware Analysis**: Considering context in emotion analysis
- **Temporal Analysis**: Analyzing emotional changes over time
- **Integration with Probabilistic Models**: Using probabilistic models for emotion prediction

#### Implementation

The enhanced `EmotionAnalyzer` class provides:

1. **Detecting Nuanced Emotions**: Identifying subtle emotional states and mixtures.
2. **Context Consideration**: Taking context into account for emotion analysis.
3. **Temporal Analysis**: Tracking emotional changes over time.
4. **Probabilistic Emotion Prediction**: Using models to predict emotional responses.

### Probabilistic Reasoning

This new component provides probabilistic reasoning capabilities for emotional state prediction and action recommendation:

#### Key Features

- **Bayesian Networks**: Implementation of Bayesian networks for probabilistic reasoning
- **Markov Models**: Implementation of Markov models for sequential reasoning
- **Uncertainty Handling**: Sophisticated handling of uncertainty in predictions
- **Evidence Integration**: Integration of evidence from various sources
- **Decision Theory**: Application of decision theory for action recommendation

#### Implementation

The `ProbabilisticReasoning` component provides:

1. **Bayesian Networks**: Networks for emotional state and action outcomes.
2. **Markov Models**: Models for temporal emotional patterns.
3. **Handling Uncertainty**: Managing uncertainty in predictions and recommendations.
4. **Integrating Evidence**: Combining evidence from multiple sources.
5. **Decision Theory**: Using decision theory for optimal recommendations.

### Intelligent Agent

This new component provides sophisticated state management and action planning:

#### Key Features

- **State Management**: Tracking and managing the user's emotional state
- **Action Planning**: Planning sequences of actions for emotional improvement
- **Decision Making**: Making decisions based on various inputs and models
- **Response Generation**: Generating sophisticated responses and recommendations
- **Learning**: Learning from user interactions and feedback

#### Implementation

The `IntelligentAgent` component provides:

1. **State Management**: Tracking and updating the user's emotional state.
2. **Action Planning**: Creating plans for emotional improvement.
3. **Decision Making**: Making decisions using various inputs and models.
4. **Response Generation**: Creating sophisticated responses.
5. **Learning Capabilities**: Learning and adapting from interactions.

## Frontend Components

The frontend has been enhanced with new visualization components for A* search paths and probabilistic reasoning:

### Key Enhancements

- **Emotional Path Visualization**: Visualization of emotional paths from A* search
- **Probability Visualization**: Visualization of probabilistic predictions and recommendations
- **Agent State Visualization**: Visualization of intelligent agent state and decisions
- **Explainable AI Interface**: Interface for explaining AI decisions and recommendations

### Implementation

The enhanced frontend provides:

1. **Path Visualization**: Displaying optimal emotional paths.
2. **Probability Graphs**: Showing probabilistic predictions and certainty.
3. **Agent State Display**: Revealing agent state and decision-making.
4. **AI Explanation Interface**: Explaining AI decisions in user-friendly ways.

## Data Flow

The enhanced data flow in Reflectly follows these steps:

1. **User Input**: The user enters a journal entry in the frontend.
2. **API Request**: The frontend sends the journal entry to the backend API.
3. **Emotion Analysis**: The backend analyzes emotions from the journal entry text.
4. **State Update**: The intelligent agent updates the user's emotional state.
5. **Emotional Graph**: The emotional graph is updated with the new state.
6. **A* Search**: A* search finds optimal paths to positive emotional states.
7. **Probabilistic Reasoning**: Probabilistic models predict outcomes of different actions.
8. **Action Planning**: The intelligent agent plans actions for emotional improvement.
9. **Response Generation**: A personalized response is generated based on the plan.
10. **API Response**: The backend sends the response back to the frontend.
11. **UI Update**: The frontend displays the response with visualizations and explanations.

## API Endpoints

Several new API endpoints have been added to support the enhanced functionality:

### NEW: A* Search Endpoints

#### GET /api/search/emotional-paths
Finds optimal paths between emotional states using A* search.

**Request:**
```json
{
  "from_emotion": "sadness",
  "to_emotion": "joy",
  "constraints": {
    "max_steps": 3,
    "preferred_actions": ["social", "physical"]
  }
}
```

**Response:**
```json
{
  "paths": [
    {
      "path": ["sadness", "neutral", "joy"],
      "actions": [
        {
          "from": "sadness",
          "to": "neutral",
          "action": "Practice mindfulness meditation",
          "category": "mindfulness",
          "effectiveness": 0.75,
          "certainty": 0.85
        },
        {
          "from": "neutral",
          "to": "joy",
          "action": "Call a close friend",
          "category": "social",
          "effectiveness": 0.82,
          "certainty": 0.90
        }
      ],
      "total_cost": 1.43,
      "effectiveness": 0.68,
      "certainty": 0.77
    }
  ]
}
```

### NEW: Probabilistic Reasoning Endpoints

#### GET /api/probabilistic/emotional-predictions
Gets probabilistic predictions for emotional states.

**Request:**
```json
{
  "current_emotion": "sadness",
  "timeframe": "1d",
  "actions": ["social_interaction", "exercise"]
}
```

**Response:**
```json
{
  "predictions": [
    {
      "emotion": "neutral",
      "probability": 0.45,
      "certainty": 0.80
    },
    {
      "emotion": "joy",
      "probability": 0.30,
      "certainty": 0.75
    },
    {
      "emotion": "sadness",
      "probability": 0.25,
      "certainty": 0.85
    }
  ],
  "action_effects": [
    {
      "action": "social_interaction",
      "effect": {
        "emotion": "joy",
        "probability_increase": 0.15,
        "certainty": 0.80
      }
    },
    {
      "action": "exercise",
      "effect": {
        "emotion": "joy",
        "probability_increase": 0.20,
        "certainty": 0.85
      }
    }
  ]
}
```

### NEW: Intelligent Agent Endpoints

#### GET /api/agent/state
Gets the current state of the intelligent agent.

**Response:**
```json
{
  "current_state": {
    "primary_emotion": "sadness",
    "intensity": 0.65,
    "context": "work-related stress",
    "duration": "3d"
  },
  "goals": [
    {
      "type": "emotional",
      "target": "joy",
      "progress": 0.25,
      "estimated_completion": "2d"
    }
  ],
  "planned_actions": [
    {
      "action": "Practice mindfulness meditation",
      "expected_outcome": "reduced stress",
      "effectiveness": 0.75,
      "timeframe": "today"
    },
    {
      "action": "Call a close friend",
      "expected_outcome": "improved mood",
      "effectiveness": 0.82,
      "timeframe": "tomorrow"
    }
  ]
}
```

#### POST /api/agent/feedback
Provides feedback to the intelligent agent about action effectiveness.

**Request:**
```json
{
  "action_id": "a123",
  "effectiveness": 0.85,
  "notes": "This really helped me feel better"
}
```

**Response:**
```json
{
  "message": "Feedback recorded successfully",
  "updated_effectiveness": 0.78,
  "learning_impact": "high"
}
```

## Database Schema

New collections have been added to support the enhanced functionality:

### NEW: A* Paths Collection

```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0f5"),
  "user_email": "john.doe@example.com",
  "from_emotion": "sadness",
  "to_emotion": "joy",
  "path": ["sadness", "neutral", "joy"],
  "actions": [
    {
      "from": "sadness",
      "to": "neutral",
      "action": "Practice mindfulness meditation",
      "category": "mindfulness",
      "effectiveness": 0.75,
      "certainty": 0.85
    },
    {
      "from": "neutral",
      "to": "joy",
      "action": "Call a close friend",
      "category": "social",
      "effectiveness": 0.82,
      "certainty": 0.90
    }
  ],
  "total_cost": 1.43,
  "effectiveness": 0.68,
  "certainty": 0.77,
  "created_at": ISODate("2025-03-28T12:00:00Z"),
  "expires_at": ISODate("2025-03-31T12:00:00Z")
}
```

### NEW: Probabilistic Models Collection

```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0f6"),
  "user_email": "john.doe@example.com",
  "model_type": "bayesian_network",
  "model_data": {
    "nodes": ["sadness", "neutral", "joy"],
    "edges": [
      {
        "from": "sadness",
        "to": "neutral",
        "probability": 0.35
      },
      {
        "from": "neutral",
        "to": "joy",
        "probability": 0.65
      }
    ],
    "conditional_probabilities": {
      "neutral|sadness": {
        "social_interaction": 0.45,
        "exercise": 0.55,
        "mindfulness": 0.40
      },
      "joy|neutral": {
        "social_interaction": 0.70,
        "exercise": 0.65,
        "creative_activity": 0.55
      }
    }
  },
  "created_at": ISODate("2025-03-28T12:00:00Z"),
  "updated_at": ISODate("2025-03-28T12:00:00Z")
}
```

### NEW: Agent States Collection

```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0f7"),
  "user_email": "john.doe@example.com",
  "current_state": {
    "primary_emotion": "sadness",
    "intensity": 0.65,
    "context": "work-related stress",
    "duration": "3d"
  },
  "goals": [
    {
      "type": "emotional",
      "target": "joy",
      "progress": 0.25,
      "estimated_completion": "2d"
    }
  ],
  "planned_actions": [
    {
      "action_id": "a123",
      "action": "Practice mindfulness meditation",
      "expected_outcome": "reduced stress",
      "effectiveness": 0.75,
      "timeframe": "today",
      "status": "pending"
    },
    {
      "action_id": "a124",
      "action": "Call a close friend",
      "expected_outcome": "improved mood",
      "effectiveness": 0.82,
      "timeframe": "tomorrow",
      "status": "pending"
    }
  ],
  "created_at": ISODate("2025-03-28T12:00:00Z"),
  "updated_at": ISODate("2025-03-28T12:00:00Z")
}
```

### NEW: Action Feedback Collection

```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0f8"),
  "user_email": "john.doe@example.com",
  "action_id": "a123",
  "action": "Practice mindfulness meditation",
  "effectiveness": 0.85,
  "notes": "This really helped me feel better",
  "created_at": ISODate("2025-03-29T12:00:00Z")
}
```

## Authentication

Authentication remains unchanged from the previous version.

## Big Data Infrastructure

The big data infrastructure has been enhanced to support the new A* search and probabilistic reasoning components:

### Hadoop

Enhanced for storing more sophisticated data:

- **Path Data**: Storage of optimal path data
- **Model Data**: Storage of probabilistic model data
- **Agent Data**: Storage of intelligent agent state data

### Spark

Enhanced with new jobs for A* search and probabilistic reasoning:

- **A* Search Jobs**: Distributed implementation of A* search
- **Bayesian Network Jobs**: Jobs for Bayesian network training and inference
- **Markov Chain Jobs**: Jobs for Markov chain training and inference
- **Path Optimization Jobs**: Jobs for optimizing emotional paths
- **Agent Learning Jobs**: Jobs for intelligent agent learning

### Kafka

Enhanced with new topics for the advanced AI components:

- **Topics**:
  - `astar-search-requests`: Requests for A* search
  - `astar-search-results`: Results from A* search
  - `probabilistic-reasoning-requests`: Requests for probabilistic reasoning
  - `probabilistic-reasoning-results`: Results from probabilistic reasoning
  - `agent-state-updates`: Updates to intelligent agent state
  - `action-feedback`: Feedback on action effectiveness
- **Consumers**: New consumers for processing messages from the new topics
- **Producers**: New producers for publishing messages to the new topics

### Spark Jobs

Several new Spark jobs have been added for the advanced AI components:

1. **A* Search Job**: Performs A* search for optimal emotional paths
   ```python
   # Perform A* search for optimal emotional paths
   def astar_search_job(graph_path, request_path, result_path):
       # Load graph from HDFS
       # Process search requests
       # Apply A* search algorithm
       # Save results to HDFS
   ```

2. **Bayesian Network Training Job**: Trains Bayesian networks from emotional data
   ```python
   # Train Bayesian networks from emotional data
   def train_bayesian_network_job(data_path, model_path):
       # Load emotional data from HDFS
       # Train Bayesian network models
       # Save models to HDFS
   ```

3. **Bayesian Network Inference Job**: Performs inference with Bayesian networks
   ```python
   # Perform inference with Bayesian networks
   def bayesian_inference_job(model_path, request_path, result_path):
       # Load models from HDFS
       # Process inference requests
       # Apply Bayesian inference
       # Save results to HDFS
   ```

4. **Markov Chain Training Job**: Trains Markov chains from emotional sequences
   ```python
   # Train Markov chains from emotional sequences
   def train_markov_chain_job(data_path, model_path):
       # Load emotional sequences from HDFS
       # Train Markov chain models
       # Save models to HDFS
   ```

5. **Markov Chain Inference Job**: Performs inference with Markov chains
   ```python
   # Perform inference with Markov chains
   def markov_inference_job(model_path, request_path, result_path):
       # Load models from HDFS
       # Process inference requests
       # Apply Markov chain inference
       # Save results to HDFS
   ```

6. **Agent Learning Job**: Trains the intelligent agent from interaction data
   ```python
   # Train the intelligent agent from interaction data
   def agent_learning_job(data_path, model_path):
       # Load interaction data from HDFS
       # Update agent models
       # Save updated models to HDFS
   ```

## Deployment

The deployment process has been enhanced to support the new A* search and probabilistic reasoning components:

### Local Development

For local development, additional scripts have been added:

1. **Start A* Search Service**: Start the A* search service
   ```bash
   ./start_astar_service.sh
   ```

2. **Start Probabilistic Reasoning Service**: Start the probabilistic reasoning service
   ```bash
   ./start_probabilistic_service.sh
   ```

3. **Start Intelligent Agent Service**: Start the intelligent agent service
   ```bash
   ./start_agent_service.sh
   ```

4. **Start All Services**: Start all services including the new ones
   ```bash
   ./start_all_services.sh
   ```

### Docker Deployment

For Docker deployment, new containers have been added:

1. **A* Search Container**: Container for the A* search service
   ```yaml
   astar-search:
     build: ./ai/search
     ports:
       - "5010:5010"
     depends_on:
       - kafka
       - namenode
     environment:
       - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
       - HDFS_NAMENODE=namenode:9000
     networks:
       - reflectly_network
       - hadoop_network
   ```

2. **Probabilistic Reasoning Container**: Container for the probabilistic reasoning service
   ```yaml
   probabilistic-reasoning:
     build: ./ai/probabilistic
     ports:
       - "5011:5011"
     depends_on:
       - kafka
       - namenode
     environment:
       - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
       - HDFS_NAMENODE=namenode:9000
     networks:
       - reflectly_network
       - hadoop_network
   ```

3. **Intelligent Agent Container**: Container for the intelligent agent service
   ```yaml
   intelligent-agent:
     build: ./ai/agent
     ports:
       - "5012:5012"
     depends_on:
       - kafka
       - namenode
       - astar-search
       - probabilistic-reasoning
     environment:
       - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
       - HDFS_NAMENODE=namenode:9000
       - ASTAR_SEARCH_URL=http://astar-search:5010
       - PROBABILISTIC_REASONING_URL=http://probabilistic-reasoning:5011
     networks:
       - reflectly_network
       - hadoop_network
   ```

## Environment Variables

New environment variables have been added for the A* search and probabilistic reasoning components:

### Backend Environment Variables

```
# A* Search Configuration
ASTAR_SEARCH_URL=http://localhost:5010
ASTAR_SEARCH_TIMEOUT=30

# Probabilistic Reasoning Configuration
PROBABILISTIC_REASONING_URL=http://localhost:5011
PROBABILISTIC_REASONING_TIMEOUT=30

# Intelligent Agent Configuration
INTELLIGENT_AGENT_URL=http://localhost:5012
INTELLIGENT_AGENT_TIMEOUT=30

# Kafka Topics
KAFKA_TOPIC_ASTAR_SEARCH_REQUESTS=astar-search-requests
KAFKA_TOPIC_ASTAR_SEARCH_RESULTS=astar-search-results
KAFKA_TOPIC_PROBABILISTIC_REASONING_REQUESTS=probabilistic-reasoning-requests
KAFKA_TOPIC_PROBABILISTIC_REASONING_RESULTS=probabilistic-reasoning-results
KAFKA_TOPIC_AGENT_STATE_UPDATES=agent-state-updates
KAFKA_TOPIC_ACTION_FEEDBACK=action-feedback

# Model Paths
MODEL_PATH_BAYESIAN_NETWORKS=hdfs://namenode:9000/user/reflectly/models/bayesian
MODEL_PATH_MARKOV_CHAINS=hdfs://namenode:9000/user/reflectly/models/markov
MODEL_PATH_AGENT=hdfs://namenode:9000/user/reflectly/models/agent
```

### Frontend Environment Variables

```
# A* Search Visualization
REACT_APP_ENABLE_ASTAR_VISUALIZATION=true

# Probabilistic Reasoning Visualization
REACT_APP_ENABLE_PROBABILISTIC_VISUALIZATION=true

# Intelligent Agent Visualization
REACT_APP_ENABLE_AGENT_VISUALIZATION=true

# Explainable AI
REACT_APP_ENABLE_EXPLAINABLE_AI=true
```

## Maintenance and Troubleshooting

New maintenance and troubleshooting procedures have been added for the A* search and probabilistic reasoning components:

### A* Search Service

1. **Checking Status**: Check the status of the A* search service
   ```bash
   curl http://localhost:5010/status
   ```

2. **Restarting**: Restart the A* search service
   ```bash
   docker restart astar-search
   ```

3. **Logs**: View logs from the A* search service
   ```bash
   docker logs astar-search
   ```

### Probabilistic Reasoning Service

1. **Checking Status**: Check the status of the probabilistic reasoning service
   ```bash
   curl http://localhost:5011/status
   ```

2. **Restarting**: Restart the probabilistic reasoning service
   ```bash
   docker restart probabilistic-reasoning
   ```

3. **Logs**: View logs from the probabilistic reasoning service
   ```bash
   docker logs probabilistic-reasoning
   ```

### Intelligent Agent Service

1. **Checking Status**: Check the status of the intelligent agent service
   ```bash
   curl http://localhost:5012/status
   ```

2. **Restarting**: Restart the intelligent agent service
   ```bash
   docker restart intelligent-agent
   ```

3. **Logs**: View logs from the intelligent agent service
   ```bash
   docker logs intelligent-agent
   ```

### Common Issues

1. **A* Search Performance**: If A* search is slow, try these solutions:
   - Increase the number of Spark workers for distributed search
   - Optimize the heuristic functions
   - Reduce the graph size by pruning rarely used edges

2. **Probabilistic Model Training**: If model training is failing, try these solutions:
   - Check the input data format
   - Increase the amount of training data
   - Adjust the learning parameters
   - Monitor Spark resource usage

3. **Agent Learning**: If the agent is not learning effectively, try these solutions:
   - Check the feedback data quality
   - Increase the amount of interaction data
   - Adjust the learning rate
   - Consider retraining from scratch

## Implementation Steps

To implement Phase Three of Reflectly, follow these high-level steps:

1. **Setup AI Directory Structure**:
   - Create the `ai` directory with subdirectories for search, probabilistic models, and agent
   - Set up the necessary files and modules

2. **Implement A* Search**:
   - Implement the core A* search algorithm
   - Develop heuristic functions for emotional path finding
   - Create utilities for graph traversal and path evaluation
   - Set up the A* search service with Kafka integration

3. **Implement Probabilistic Reasoning**:
   - Implement Bayesian network models for emotional state prediction
   - Develop Markov chain models for emotional sequence analysis
   - Create utilities for uncertainty handling and evidence integration
   - Set up the probabilistic reasoning service with Kafka integration

4. **Implement Intelligent Agent**:
   - Implement state management for tracking emotional states
   - Develop action planning for suggesting interventions
   - Create decision-making logic for selecting optimal actions
   - Set up the intelligent agent service with integration to other services

5. **Enhance Frontend**:
   - Add components for visualizing A* search paths
   - Develop interfaces for displaying probabilistic predictions
   - Create views for showing agent state and decisions
   - Implement an explainable AI interface

6. **Update Backend**:
   - Enhance existing components to integrate with new AI services
   - Update API endpoints to expose new functionality
   - Modify data processing logic to leverage new capabilities
   - Implement new data models and database schemas

7. **Set Up Spark Jobs**:
   - Develop Spark jobs for A* search
   - Create jobs for Bayesian network and Markov chain training
   - Implement jobs for agent learning and model updating
   - Set up job scheduling and coordination

8. **Configure Kafka**:
   - Create new topics for AI service communication
   - Set up producers and consumers for message handling
   - Implement message processing logic
   - Configure proper message routing

9. **Update Deployment**:
   - Add new containers to Docker Compose
   - Update environment variables
   - Create startup and management scripts
   - Implement monitoring and logging

10. **Documentation and Testing**:
    - Document all new components and APIs
    - Create test cases for AI functionality
    - Develop integration tests for the entire system
    - Update user documentation with new features

## Conclusion

Phase Three of Reflectly enhances the application with advanced AI capabilities, specifically focusing on A* search algorithms, probabilistic reasoning, and intelligent agent functionality. These enhancements allow the application to provide more personalized and effective guidance for users navigating from negative to positive emotional states.

The integration of A* search enables the application to find optimal paths through the emotional state graph, while probabilistic reasoning allows for uncertainty handling and evidence-based predictions. The intelligent agent ties everything together with sophisticated state management and action planning, creating a cohesive and powerful user experience.

Future phases could focus on further enhancing the AI capabilities, implementing more sophisticated learning algorithms, and improving the user interface for a more intuitive and engaging experience.