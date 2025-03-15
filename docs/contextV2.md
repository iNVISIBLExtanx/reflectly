# Reflectly Technical Documentation - Phase One

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Directory Structure](#directory-structure)
5. [Backend Components](#backend-components)
6. [Frontend Components](#frontend-components)
7. [Data Flow](#data-flow)
8. [Key Features Implementation](#key-features-implementation)
9. [Authentication and User Management](#authentication-and-user-management)
10. [Deployment Instructions](#deployment-instructions)
11. [Development Workflow](#development-workflow)
12. [API Documentation](#api-documentation)

## Project Overview

Reflectly is a personal journaling application with a conversational interface designed to help users engage in meaningful self-reflection. The application combines a chat-like interface with intelligent emotional support, memory management, and goal tracking features. The system uses emotional analysis to provide personalized responses and help users navigate from negative emotional states to positive ones.

### Core Functionality
- **Conversational Journaling**: Users interact with the application through a chat interface
- **Emotion Analysis**: The system analyzes user emotions from journal entries
- **Emotional Graph**: Tracks transitions between emotional states and effective interventions
- **Memory Management**: Past positive experiences are stored and retrieved when needed
- **Goal Tracking**: Users can set and track personal goals

## System Architecture

Reflectly follows a modern microservices architecture with containerized components:

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│    Frontend     │◄────►│    Backend      │◄────►│    Database     │
│    (React.js)   │      │    (Flask)      │      │    (MongoDB)    │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                  ▲
                                  │
                                  ▼
                         ┌─────────────────┐
                         │                 │
                         │  Cache Layer    │
                         │    (Redis)      │
                         │                 │
                         └─────────────────┘
```

## Technology Stack

### Frontend
- **Framework**: React.js
- **UI Library**: Material-UI
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Containerization**: Docker

### Backend
- **Framework**: Flask (Python)
- **API**: RESTful endpoints
- **Authentication**: JWT (JSON Web Tokens)
- **Containerization**: Docker
- **ML Framework**: Transformers (Hugging Face) for emotion detection

### Database
- **Primary Database**: MongoDB
- **Caching**: Redis
- **Data Persistence**: Docker volumes

### AI/ML Components
- **Emotion Analysis**: BERT-based model from Hugging Face
- **Emotional Graph**: In-memory graph structure with MongoDB persistence
- **Response Generation**: Template-based with contextual awareness
- **Memory Management**: Multi-tier storage with intelligent retrieval

## Directory Structure

```
/Refection/
├── backend/                  # Backend Flask application
│   ├── models/               # Core business logic components
│   │   ├── emotion_analyzer.py  # Enhanced emotion analysis module
│   │   ├── emotional_graph.py   # NEW: Emotional state graph representation
│   │   ├── goal_tracker.py      # Goal tracking functionality
│   │   ├── memory_manager.py    # Memory storage and retrieval
│   │   └── response_generator.py # AI response generation
│   ├── app.py                # Main Flask application
│   ├── admin_viewer.py       # Admin interface for database viewing
│   ├── user_management.py    # User authentication and management
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Environment variables
├── frontend/                 # React frontend application
│   ├── public/               # Static assets
│   ├── src/                  # Source code
│   │   ├── components/       # Reusable UI components
│   │   ├── context/          # React context providers
│   │   ├── pages/            # Application pages
│   │   │   └── EmotionalJourney.js # NEW: Emotional state visualization
│   │   ├── services/         # API service integrations
│   │   └── utils/            # Utility functions
│   ├── package.json          # NPM dependencies
│   └── Dockerfile            # Frontend container definition
├── docker/                   # Docker configuration files
├── data/                     # NEW: Data directory for datasets
│   └── emotion_datasets/     # NEW: Directory for emotional datasets
├── docker-compose.yml        # Multi-container orchestration
├── docs/                     # Documentation
│   └── context.md            # Project context and specifications
└── README.md                 # Project overview
```

## Backend Components

### Flask Application (app.py)
The main application entry point that defines API routes, initializes components, and handles HTTP requests.

Key endpoints:
- `/api/auth/login`: User authentication
- `/api/auth/register`: User registration
- `/api/journal/entries`: CRUD operations for journal entries
- `/api/emotions/graph`: NEW: Endpoints for emotional graph data
- `/api/goals`: Goal management endpoints
- `/api/admin/*`: Administrative endpoints

### Emotion Analyzer (emotion_analyzer.py)
Enhanced to use a pre-trained BERT model for more accurate emotion detection:
- Detects primary emotion (joy, sadness, anger, fear, disgust, surprise)
- Determines if the emotion is positive or negative
- Calculates confidence scores for each emotion
- Uses Hugging Face Transformers library for inference
- Optionally utilizes a fine-tuned model on IEMOCAP dataset

### Emotional Graph (emotional_graph.py)
NEW component that represents and manages the emotional state transitions:
- Graph structure with emotional states as nodes
- Edges represent transitions between states with weights
- Stores actions that led to emotional state changes
- Simple pathfinding to suggest actions for emotional improvement
- Persistence layer to save graph to MongoDB

### Memory Manager (memory_manager.py)
Manages the storage and retrieval of journal entries and memories:
- Multi-tier storage system (short-term, medium-term, long-term)
- Redis caching for frequently accessed memories
- Intelligent retrieval of relevant memories based on emotional context
- Stores positive memories for future encouragement
- NEW: Associates memories with emotional state transitions

### Response Generator (response_generator.py)
Generates AI responses to user journal entries:
- Template-based responses customized to emotional context
- Incorporates past memories when appropriate
- Provides encouragement during negative emotional states
- Reinforces positive experiences
- NEW: Suggests actions based on emotional graph pathfinding

### Goal Tracker (goal_tracker.py)
Manages user goals and tracks progress:
- Goal creation and update functionality
- Progress tracking and milestone recognition
- Pattern recognition for achievement analysis
- NEW: Relates goals to emotional states

### User Management (user_management.py)
Handles user authentication and account management:
- User registration and login
- Password hashing with bcrypt
- JWT token generation and validation
- User profile management

## Frontend Components

### App Structure
- **App.js**: Main application component with routing
- **index.js**: Entry point that renders the React application

### Pages
- **Login.js**: User authentication interface
- **Register.js**: New user registration
- **Journal.js**: Main journaling interface with chat functionality
- **Goals.js**: Goal setting and tracking interface
- **Profile.js**: User profile management
- **Dashboard.js**: Overview of journal entries and emotions
- **EmotionalJourney.js**: NEW: Visualization of user's emotional journey

### Components
- **journal/MemoryCard.js**: Displays memory cards in the journal chat
- **journal/ChatBubble.js**: Individual chat message bubbles
- **journal/EmotionIndicator.js**: NEW: Visual indication of detected emotions
- **common/Navbar.js**: Application navigation
- **goals/GoalItem.js**: Individual goal display and tracking
- **emotional/StateGraph.js**: NEW: Visual representation of emotional states

### Context Providers
- **AuthContext.js**: Authentication state management
- **JournalContext.js**: Journal entries and chat state
- **EmotionContext.js**: NEW: Emotion tracking and graph state

## Data Flow

### Journal Entry Creation
1. User enters text in the journal interface
2. Frontend sends entry to backend via API
3. Backend processes the entry:
   - Analyzes emotions using the enhanced emotion analyzer
   - Updates the emotional graph with the new state
   - Finds potential paths to better emotional states
   - Generates an AI response using the response generator
   - Stores the entry in MongoDB
   - Caches positive memories in Redis
4. Response is sent back to frontend with:
   - AI-generated text response
   - Memory card data (if applicable)
   - Suggested actions based on emotional graph
5. Frontend displays the response and any memory cards

### Emotional Graph Update Logic
1. When a user submits a journal entry:
   - The system detects the current emotional state
   - Adds it to the emotional graph if new
   - Updates transition weights based on frequency
   - Records actions mentioned in the entry
2. When suggesting responses:
   - The system finds paths from current emotion to positive emotions
   - Suggests actions based on successful past transitions
   - Prioritizes actions with higher success rates

## Key Features Implementation

### Conversational Journaling Interface
The journal interface mimics a chat application with:
- User messages displayed on the right
- AI responses displayed on the left
- Memory cards appearing inline when triggered
- Real-time emotion analysis feedback
- NEW: Suggested actions based on emotional graph

### Emotion Tracking System
- **Enhanced Emotion Detection**: BERT-based model identifies emotions
- **Emotion Storage**: Emotions are stored with journal entries
- **Emotion Trends**: Patterns are analyzed over time
- **NEW: Emotional Graph**: Tracks transitions between emotional states

### Memory Management System
- **Short-term Memory**: Recent entries cached in Redis (7 days)
- **Medium-term Memory**: Active entries in MongoDB (30 days)
- **Long-term Memory**: Historical entries for pattern analysis (365 days)
- **Memory Retrieval**: Intelligent retrieval based on emotional context
- **NEW: Action Association**: Memories linked to successful emotional transitions

### Goal Setting and Tracking
- **Goal Creation**: Users define goals with measurable criteria
- **Progress Tracking**: System tracks progress through user updates
- **Achievement Recognition**: Milestones are celebrated with notifications
- **NEW: Emotional Impact**: Goals are linked to emotional states

## Authentication and User Management

### User Registration
1. User provides email and password
2. Password is hashed using bcrypt
3. User account is created in MongoDB
4. JWT token is generated and returned

### User Authentication
1. User submits login credentials
2. Backend verifies email and password
3. JWT token is generated with user information
4. Token is returned to frontend and stored in local storage

### Admin Functionality
- List all users in the system
- Create new users with specified credentials
- Delete users from the system
- View database structure and contents
- NEW: View emotional graphs and transitions

## Deployment Instructions

### Prerequisites
- Docker and Docker Compose installed
- Git for version control
- Node.js and npm for frontend development
- Python for backend development

### Development Environment Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Refection
   ```

2. Download and place emotion datasets in the data directory:
   ```bash
   mkdir -p data/emotion_datasets
   # Place IEMOCAP dataset files here (if available)
   ```

3. Start the application using Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5002
   - MongoDB Viewer: http://localhost:5003

### Manual Backend Setup (Alternative)
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the Flask application:
   ```bash
   python app.py
   ```

### Manual Frontend Setup (Alternative)
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

## Development Workflow

### Code Organization
- **Backend**: Modular Python code with clear separation of concerns
- **Frontend**: Component-based React architecture
- **Shared**: Docker configuration for consistent environments

### Version Control
- Use feature branches for new development
- Pull requests for code review
- Semantic versioning for releases

### Testing
- Unit tests for backend components
- Integration tests for API endpoints
- End-to-end tests for critical user flows

## API Documentation

### Authentication Endpoints

#### POST /api/auth/login
Authenticates a user and returns a JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "email": "user@example.com",
    "name": "User Name"
  }
}
```

#### POST /api/auth/register
Registers a new user.

**Request:**
```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "name": "New User"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "email": "newuser@example.com",
    "name": "New User"
  }
}
```

### Journal Endpoints

#### POST /api/journal/entries
Creates a new journal entry.

**Request:**
```json
{
  "content": "I'm feeling sad today because I had an argument with a friend."
}
```

**Response:**
```json
{
  "entry": {
    "id": "60c72b2f9b1d8a1234567890",
    "content": "I'm feeling sad today because I had an argument with a friend.",
    "created_at": "2023-06-14T12:30:45Z",
    "emotion": {
      "primary_emotion": "sadness",
      "is_positive": false,
      "emotion_scores": {
        "joy": 0.05,
        "sadness": 0.85,
        "anger": 0.02,
        "fear": 0.03,
        "disgust": 0.01,
        "surprise": 0.04
      }
    }
  },
  "response": {
    "text": "I'm sorry to hear you're feeling sad about the argument. In the past, talking things through has helped you resolve conflicts. Would you like to think about how to approach your friend for a conversation?",
    "memory": {
      "id": "60c72b2f9b1d8a1234567880",
      "content": "I called my friend and apologized for the misunderstanding. I feel much better now.",
      "created_at": "2023-05-20T15:45:30Z"
    },
    "suggested_actions": [
      "Reach out to your friend",
      "Take some time for self-care",
      "Journal about what you learned from the situation"
    ]
  }
}
```

#### GET /api/journal/entries
Retrieves journal entries for the authenticated user.

**Response:**
```json
{
  "entries": [
    {
      "id": "60c72b2f9b1d8a1234567890",
      "content": "I'm feeling sad today because I had an argument with a friend.",
      "created_at": "2023-06-14T12:30:45Z",
      "emotion": {
        "primary_emotion": "sadness",
        "is_positive": false
      }
    },
    {
      "id": "60c72b2f9b1d8a1234567891",
      "content": "I'm feeling happy today because I resolved the issue with my friend.",
      "created_at": "2023-06-15T10:15:30Z",
      "emotion": {
        "primary_emotion": "joy",
        "is_positive": true
      }
    }
  ]
}
```

### NEW: Emotion Graph Endpoints

#### GET /api/emotions/graph
Retrieves the user's emotional state graph.

**Response:**
```json
{
  "nodes": [
    {
      "id": "joy",
      "count": 25,
      "last_experienced": "2023-06-15T10:15:30Z"
    },
    {
      "id": "sadness",
      "count": 15,
      "last_experienced": "2023-06-14T12:30:45Z"
    },
    {
      "id": "anger",
      "count": 8,
      "last_experienced": "2023-06-10T09:20:15Z"
    }
  ],
  "edges": [
    {
      "source": "sadness",
      "target": "joy",
      "weight": 0.7,
      "actions": [
        {
          "description": "Reached out to friend",
          "count": 5
        },
        {
          "description": "Practiced self-care",
          "count": 3
        }
      ]
    },
    {
      "source": "anger",
      "target": "joy",
      "weight": 0.5,
      "actions": [
        {
          "description": "Took a walk",
          "count": 2
        },
        {
          "description": "Practiced deep breathing",
          "count": 4
        }
      ]
    }
  ]
}
```

#### GET /api/emotions/suggestions
Retrieves suggestions for transitioning from current emotional state.

**Request:**
```json
{
  "current_emotion": "sadness"
}
```

**Response:**
```json
{
  "target_emotion": "joy",
  "path": ["sadness", "joy"],
  "suggested_actions": [
    {
      "description": "Reach out to friend",
      "success_rate": 0.85
    },
    {
      "description": "Practice self-care",
      "success_rate": 0.75
    },
    {
      "description": "Listen to uplifting music",
      "success_rate": 0.65
    }
  ]
}
```

### Admin Endpoints

#### GET /api/admin/users
Retrieves all users (requires admin authentication).

**Response:**
```json
{
  "users": [
    {
      "email": "user1@example.com",
      "name": "User One",
      "created_at": "2023-05-01T09:00:00Z"
    },
    {
      "email": "user2@example.com",
      "name": "User Two",
      "created_at": "2023-05-02T10:30:00Z"
    }
  ]
}
```

#### NEW: GET /api/admin/emotions/graphs
Retrieves all user emotional graphs (requires admin authentication).

**Response:**
```json
{
  "graphs": [
    {
      "user_id": "user1@example.com",
      "node_count": 6,
      "edge_count": 12,
      "most_common_emotion": "joy"
    },
    {
      "user_id": "user2@example.com",
      "node_count": 5,
      "edge_count": 8,
      "most_common_emotion": "sadness"
    }
  ]
}
```