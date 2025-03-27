# Reflectly Technical Documentation

**Version:** 1.1.0  
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
- **Emotional Graph**: Tracks transitions between emotional states and suggests personalized interventions based on user history
- **Personalized Responses**: Generates responses tailored to the user's emotional context and history
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
                         │     Redis       │
                         │    (Cache)      │
                         │                 │
                         └─────────────────┘
```

- **Frontend**: React.js application providing the user interface
- **Backend**: Flask application handling business logic, emotion analysis, and response generation
- **Database**: MongoDB for persistent storage of user data, journal entries, and emotional states
- **Cache**: Redis for temporary data storage and session management

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

### Database
- **Primary Database**: MongoDB
- **Caching**: Redis

### DevOps
- **Containerization**: Docker
- **Version Control**: Git
- **CI/CD**: GitHub Actions

## Directory Structure

```
/
├── backend/                # Flask backend application
│   ├── models/             # Business logic models
│   │   ├── emotional_graph.py  # Emotional state tracking and transitions
│   │   ├── response_generator.py  # AI response generation
│   │   └── ...
│   ├── utils/              # Utility functions
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration settings
│   ├── requirements.txt    # Python dependencies
│   └── start_backend.sh    # Script to start the backend server
│
├── frontend/               # React frontend application
│   ├── public/             # Static assets
│   ├── src/                # Source code
│   │   ├── components/     # Reusable UI components
│   │   │   ├── journal/    # Journal-related components
│   │   │   └── layout/     # Layout components
│   │   ├── context/        # React context providers
│   │   ├── pages/          # Application pages
│   │   ├── utils/          # Utility functions
│   │   ├── App.js          # Main application component
│   │   └── index.js        # Entry point
│   ├── package.json        # NPM dependencies
│   └── README.md           # Frontend documentation
│
└── docs/                   # Project documentation
    ├── technical_documentation.md  # Technical documentation
    └── context.md          # Project context and requirements
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

## Deployment

Reflectly can be deployed using Docker containers for both the frontend and backend components. The deployment process involves:

1. **Building Docker Images**: Building Docker images for the frontend and backend components.
2. **Running Containers**: Running Docker containers for the frontend, backend, MongoDB, and Redis.
3. **Configuring Environment Variables**: Setting environment variables for the containers.
4. **Setting Up Networking**: Configuring networking between the containers.

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
```

### Frontend Environment Variables

```
# API Configuration
REACT_APP_API_URL=http://localhost:5002

# Feature Flags
REACT_APP_ENABLE_VOICE_INPUT=true
REACT_APP_ENABLE_GOAL_TRACKING=true
```