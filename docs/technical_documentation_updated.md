# Reflectly Technical Documentation

**Version:** 1.0.0  
**Last Updated:** March 14, 2025  
**Author:** Reflectly Development Team

## Table of Contents
- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Directory Structure](#directory-structure)
- [Backend Components](#backend-components)
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
- **Emotion Analysis**: The system analyzes user emotions from journal entries
- **Emotional Graph**: Tracks transitions between emotional states and suggests effective interventions
- **Goal Tracking**: Users can set and track personal goals

## System Architecture

Reflectly follows a client-server architecture with separate frontend and backend components:

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

The application is designed to run with:

1. **Backend**: Flask server running on port 5002
   - Located at `/Users/manodhyaopallage/Refection/backend`
   - Can be started with the `start_backend.sh` script

2. **Frontend**: React application running on port 3000
   - Located at `/Users/manodhyaopallage/Refection/frontend`
   - Started with `npm start` in the frontend directory

Both components need to be running for the full application to work properly.

## Technology Stack

### Frontend
- **Framework**: React.js
- **UI Library**: Material-UI
- **State Management**: React Context API
- **HTTP Client**: Axios

### Backend
- **Framework**: Flask (Python)
- **API**: RESTful endpoints
- **Authentication**: JWT (JSON Web Tokens)
- **ML Framework**: Transformers (Hugging Face) for emotion detection

### Database
- **Primary Database**: MongoDB Atlas (cloud-based)
- **Caching**: Redis

### AI/ML Components
- **Emotion Analysis**: BERT-based model from Hugging Face
- **Emotional Graph**: Graph structure with MongoDB persistence
- **Response Generation**: Template-based with contextual awareness

## Directory Structure

```
/Refection/
├── backend/                  # Backend Flask application
│   ├── models/               # Core business logic components
│   │   ├── emotion_analyzer.py  # Emotion analysis module
│   │   ├── emotional_graph.py   # Emotional state graph representation
│   │   ├── goal_tracker.py      # Goal tracking functionality
│   │   ├── memory_manager.py    # Memory storage and retrieval 
│   │   └── response_generator.py # AI response generation
│   ├── app.py                # Main Flask application
│   ├── user_management.py    # User authentication and management
│   ├── admin_viewer.py       # Admin functionalitydata
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Environment variables
├── frontend/                 # React frontend application
│   ├── public/               # Static assets
│   ├── src/                  # Source code
│   │   ├── components/       # Reusable UI components
│   │   │   ├── journal/      # Journal-related components
│   │   │   └── layout/       # Layout components
│   │   ├── context/          # React context providers
│   │   ├── pages/            # Application pages
│   │   ├── services/         # API service functions
│   │   ├── utils/            # Utility functions
│   │   └── assets/           # Static assets
│   └── package.json          # NPM dependencies
├── docs/                     # Documentation
│   └── technical_documentation.md # Project technical documentation
└── README.md                 # Project overview
```

## Backend Components

### Flask Application (app.py)
The main application entry point that defines API routes, initializes components, and handles HTTP requests.

Key endpoints:
- `/api/auth/login`: User authentication
- `/api/auth/register`: User registration
- `/api/journal/entries`: CRUD operations for journal entries
- `/api/goals`: Goal management endpoints
- `/api/admin/*`: Administrative endpoints

### Emotion Analyzer (emotion_analyzer.py)
Analyzes text to identify emotions and sentiment:
- Detects primary emotion (joy, sadness, anger, fear, disgust, surprise)
- Determines if the emotion is positive or negative
- Calculates confidence scores for each emotion
- Uses Hugging Face Transformers library for inference

### Emotional Graph (emotional_graph.py)
Represents and manages emotional state transitions:
- Graph structure with emotional states as nodes
- Edges represent transitions between states with weights
- Stores actions that led to emotional state changes
- Suggests actions for emotional improvement
- Persistence layer to save graph to MongoDB

### Response Generator (response_generator.py)
Generates AI responses to user journal entries:
- Template-based responses customized to emotional context
- Provides encouragement during negative emotional states
- Reinforces positive experiences
- Suggests actions based on emotional graph pathfinding

### Goal Tracker (goal_tracker.py)
Manages user goals and tracks progress:
- Goal creation and update functionality
- Progress tracking and milestone recognition
- Pattern recognition for achievement analysis
- Relates goals to emotional states

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
- **Home.js**: Landing page
- **Memories.js**: Memory display page (deprecated)

### Components
- **journal/MemoryCard.js**: Displays memory cards in the journal chat (deprecated)
- **layout/Header.js**: Application header with navigation
- **layout/Footer.js**: Application footer

### Context Providers
- **AuthContext.js**: Authentication state management
- **JournalContext.js**: Journal entries and chat state

## Data Flow

### Journal Entry Creation
1. User enters text in the journal interface
2. Frontend sends entry to backend via API
3. Backend processes the entry:
   - Analyzes emotions using the emotion analyzer
   - Updates the emotional graph with the new state
   - Finds potential paths to better emotional states
   - Generates an AI response using the response generator
   - Stores the entry in MongoDB
4. Response is sent back to frontend with:
   - AI-generated text response
   - Suggested actions based on emotional graph
5. Frontend displays the response and suggested actions

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

## API Endpoints

### Authentication Endpoints

#### POST /api/auth/register
Creates a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

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
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

### Journal Endpoints

#### POST /api/journal/entries
Creates a new journal entry.

**Request:**
```json
{
  "content": "I had a great day today, feeling happy about my progress.",
  "isUserMessage": true
}
```

**Response:**
```json
{
  "message": "Journal entry created",
  "entry_id": "60a1e2c3d4e5f6a7b8c9d0e1",
  "response_id": "60a1e2c3d4e5f6a7b8c9d0e2",
  "response": {
    "text": "I'm glad to hear you're feeling happy about your progress! What specific achievements are you most proud of?",
    "suggested_actions": [
      "Reflect on what contributed to your success",
      "Set a new goal to maintain momentum",
      "Share your achievement with someone"
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
      "_id": "60a1e2c3d4e5f6a7b8c9d0e1",
      "content": "I had a great day today, feeling happy about my progress.",
      "emotion": {
        "primary_emotion": "joy",
        "is_positive": true,
        "emotion_scores": {
          "joy": 0.85,
          "sadness": 0.02,
          "anger": 0.01,
          "fear": 0.01,
          "disgust": 0.01,
          "surprise": 0.1
        }
      },
      "created_at": "2025-03-14T10:30:00.000Z",
      "isUserMessage": true
    },
    {
      "_id": "60a1e2c3d4e5f6a7b8c9d0e2",
      "content": "I'm glad to hear you're feeling happy about your progress! What specific achievements are you most proud of?",
      "created_at": "2025-03-14T10:30:01.000Z",
      "isUserMessage": false,
      "parent_entry_id": "60a1e2c3d4e5f6a7b8c9d0e1"
    }
  ]
}
```

### Goal Endpoints

#### POST /api/goals
Creates a new goal.

**Request:**
```json
{
  "title": "Learn to meditate",
  "description": "Practice meditation for 10 minutes daily",
  "target_date": "2025-04-14T00:00:00.000Z"
}
```

**Response:**
```json
{
  "message": "Goal created successfully",
  "goal_id": "60a1e2c3d4e5f6a7b8c9d0e3",
  "goal": {
    "title": "Learn to meditate",
    "description": "Practice meditation for 10 minutes daily",
    "target_date": "2025-04-14T00:00:00.000Z",
    "progress": 0,
    "created_at": "2025-03-14T10:35:00.000Z"
  }
}
```

#### GET /api/goals
Retrieves goals for the authenticated user.

**Response:**
```json
{
  "goals": [
    {
      "_id": "60a1e2c3d4e5f6a7b8c9d0e3",
      "title": "Learn to meditate",
      "description": "Practice meditation for 10 minutes daily",
      "target_date": "2025-04-14T00:00:00.000Z",
      "progress": 0,
      "created_at": "2025-03-14T10:35:00.000Z"
    }
  ]
}
```

#### PUT /api/goals/:goal_id
Updates goal progress.

**Request:**
```json
{
  "progress": 30
}
```

**Response:**
```json
{
  "message": "Goal progress updated",
  "goal": {
    "_id": "60a1e2c3d4e5f6a7b8c9d0e3",
    "title": "Learn to meditate",
    "description": "Practice meditation for 10 minutes daily",
    "target_date": "2025-04-14T00:00:00.000Z",
    "progress": 30,
    "created_at": "2025-03-14T10:35:00.000Z",
    "updated_at": "2025-03-14T11:00:00.000Z"
  }
}
```

## Database Schema

### Users Collection
```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e0"),
  "email": "user@example.com",
  "password_hash": "$2b$12$...",
  "name": "John Doe",
  "created_at": ISODate("2025-03-14T10:00:00.000Z"),
  "last_login": ISODate("2025-03-14T10:05:00.000Z")
}
```

### Journal Entries Collection
```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e1"),
  "user_email": "user@example.com",
  "content": "I had a great day today, feeling happy about my progress.",
  "emotion": {
    "primary_emotion": "joy",
    "is_positive": true,
    "emotion_scores": {
      "joy": 0.85,
      "sadness": 0.02,
      "anger": 0.01,
      "fear": 0.01,
      "disgust": 0.01,
      "surprise": 0.1
    },
    "emotion_state_id": "60a1e2c3d4e5f6a7b8c9d0f1"
  },
  "created_at": ISODate("2025-03-14T10:30:00.000Z"),
  "isUserMessage": true
}
```

### Emotional States Collection
```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0f1"),
  "user_email": "user@example.com",
  "primary_emotion": "joy",
  "is_positive": true,
  "emotion_scores": {
    "joy": 0.85,
    "sadness": 0.02,
    "anger": 0.01,
    "fear": 0.01,
    "disgust": 0.01,
    "surprise": 0.1
  },
  "entry_id": "60a1e2c3d4e5f6a7b8c9d0e1",
  "timestamp": ISODate("2025-03-14T10:30:00.000Z")
}
```

### Emotional Transitions Collection
```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0f2"),
  "user_email": "user@example.com",
  "from_emotion": "sadness",
  "to_emotion": "joy",
  "from_state_id": "60a1e2c3d4e5f6a7b8c9d0f0",
  "to_state_id": "60a1e2c3d4e5f6a7b8c9d0f1",
  "timestamp": ISODate("2025-03-14T10:30:00.000Z")
}
```

### Goals Collection
```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e3"),
  "user_email": "user@example.com",
  "title": "Learn to meditate",
  "description": "Practice meditation for 10 minutes daily",
  "target_date": ISODate("2025-04-14T00:00:00.000Z"),
  "progress": 30,
  "created_at": ISODate("2025-03-14T10:35:00.000Z"),
  "updated_at": ISODate("2025-03-14T11:00:00.000Z")
}
```

## Authentication

Reflectly uses JSON Web Tokens (JWT) for authentication:

1. **Token Generation**: When a user logs in or registers, the server generates a JWT token signed with a secret key
2. **Token Storage**: The token is stored in the client's localStorage
3. **Token Usage**: The token is included in the Authorization header for API requests
4. **Token Validation**: The server validates the token for protected routes
5. **Token Expiration**: Tokens expire after 24 hours, requiring re-authentication

## Deployment

The application is currently set up for development with local deployment:

1. **Backend Deployment**:
   - Navigate to `/Users/manodhyaopallage/Refection/backend`
   - Run `./start_backend.sh` to start the Flask server
   - The server will be available at `http://localhost:5002`

2. **Frontend Deployment**:
   - Navigate to `/Users/manodhyaopallage/Refection/frontend`
   - Run `npm start` to start the React development server
   - The application will be available at `http://localhost:3000`

## Environment Variables

The application uses environment variables stored in `.env` files:

### Backend Environment Variables
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/reflectly
REDIS_URI=redis://localhost:6379/0
JWT_SECRET_KEY=your-jwt-secret-key
ADMIN_SECRET=your-admin-secret-key
```

### Frontend Environment Variables
```
REACT_APP_API_URL=http://localhost:5002
REACT_APP_VERSION=1.0.0
```