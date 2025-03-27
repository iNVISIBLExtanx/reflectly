# Reflectly Testing Guide

This document provides instructions for testing the Reflectly application and fixing any issues that may arise.

## Prerequisites

1. Make sure both the backend and frontend are running:
   - Backend: Run `./start_backend.sh` in the `/Users/manodhyaopallage/Refection/backend` directory
   - Frontend: Run `npm start` in the `/Users/manodhyaopallage/Refection/frontend` directory

2. Use the test user credentials:
   - Email: test_user@example.com
   - Password: TestPassword123

## Testing Process

### 1. User Registration and Authentication

```bash
# Register a new user
curl -X POST http://localhost:5002/api/auth/register -H "Content-Type: application/json" -d '{
  "email": "new_test_user@example.com",
  "password": "TestPassword123",
  "name": "New Test User"
}'

# Login with existing user
curl -X POST http://localhost:5002/api/auth/login -H "Content-Type: application/json" -d '{
  "email": "test_user@example.com",
  "password": "TestPassword123"
}'
```

### 2. Journal Entries

```bash
# Create a new journal entry
curl -X POST http://localhost:5002/api/journal/entries -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_TOKEN" -d '{
  "content": "Today I felt really happy because I accomplished my goals.",
  "tags": ["happiness", "achievement"]
}'

# Get all journal entries
curl -X GET http://localhost:5002/api/journal/entries -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Emotional Analysis

```bash
# Get emotional graph
curl -X GET http://localhost:5002/api/probabilistic/emotional-graph -H "Authorization: Bearer YOUR_TOKEN"

# Predict next emotion
curl -X POST http://localhost:5002/api/predict/emotion -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_TOKEN" -d '{
  "current_emotion": "joy"
}'

# Predict emotional sequence
curl -X POST http://localhost:5002/api/predict/emotional-sequence -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_TOKEN" -d '{
  "current_emotion": "fear",
  "sequence_length": 5
}'
```

### 4. Path Finding and Decision Making

```bash
# Find emotional path
curl -X POST http://localhost:5002/api/emotional-path -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_TOKEN" -d '{
  "current_emotion": "sadness",
  "target_emotion": "joy"
}'

# Get agent state
curl -X GET http://localhost:5002/api/agent/state -H "Authorization: Bearer YOUR_TOKEN"

# Analyze decision
curl -X POST http://localhost:5002/api/agent/analyze-decision -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_TOKEN" -d '{
  "current_emotion": "neutral",
  "decision": "Should I take the new job offer or stay at my current position?",
  "options": ["Take the new job", "Stay at current job"]
}'
```

## Fixing Issues

If you encounter any issues during testing, you can run the fix scripts:

```bash
# Fix all issues at once
python /Users/manodhyaopallage/Refection/fix_all_issues.py

# Or run individual fix scripts
python /Users/manodhyaopallage/Refection/backend/ai/probabilistic/fix_markov_model.py
python /Users/manodhyaopallage/Refection/backend/ai/search/fix_astar_search.py
python /Users/manodhyaopallage/Refection/backend/ai/agent/fix_agent_state.py
python /Users/manodhyaopallage/Refection/backend/ai/agent/fix_decision_analysis.py
```

## Testing Report

A detailed testing report is available at `/Users/manodhyaopallage/Refection/testing_report.md`. This report includes:

1. Status of each feature (working, partially working, not working)
2. Details of any issues encountered
3. Suggested fixes for each issue
4. Next steps for development

## Frontend Testing

After fixing the backend issues, you can test the frontend components by visiting:

- Journal: http://localhost:3000/journal
- Emotional Journey: http://localhost:3000/emotional-journey
- Decision Explorer: http://localhost:3000/decision-explorer

## Known Issues

1. MarkovModel missing predict_sequence method
2. A* search algorithm issues with emotion coordinates
3. AgentState initialization not handling user_email parameter
4. Decision analysis not properly handling options
5. Emotional graph showing default transitions for new users without any journal entries
6. Emotion prediction providing predictions for users without any journal entries
7. Intelligent agent providing action plans for users without any journal entries
8. Unknown emotions (like "stressed") not properly mapped to standard emotions in action plans

All these issues can be fixed by running the fix scripts provided.
