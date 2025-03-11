# Reflectly - Personal Journaling Application

Reflectly is a comprehensive personal journaling application designed to help users engage in meaningful self-reflection through a conversational interface. The app combines the familiarity of a chat interface with the emotional intelligence of a personal journal, fostering self-awareness and growth.

## Key Features

1. **Conversational Journaling Interface**
   - Chat-like UI where users can type or speak their thoughts
   - AI-powered responses with emotion-aware interactions

2. **Emotion Tracking and Support System**
   - Dual-path emotional processing (Happy and Support flows)
   - Advanced emotion detection using BERT and RoBERTa

3. **Goal Setting and Progress Analysis**
   - Set personal goals and track progress
   - Progress charts and milestone celebrations

4. **Memory Management System**
   - Multi-tier storage for journal entries and emotions
   - Intelligent retrieval of past positive experiences

## Tech Stack

### Frontend
- React.js with Material-UI
- Context API for state management
- Responsive design for all devices

### Backend
- Python/Flask for RESTful services
- MongoDB for primary storage
- Redis for caching
- Kafka for message streaming

### AI/ML Components
- BERT for sentiment analysis
- GPT for response generation

### Deployment
- Docker containers for all services

## Getting Started

### Prerequisites
- Docker and Docker Compose installed on your machine

### Installation and Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd Refection
   ```

2. Start the application using Docker Compose:
   ```
   docker-compose up
   ```

3. Access the application:
   - Frontend: http://localhost
   - Backend API: http://localhost:5000

### Development

#### Frontend Development
The frontend code is located in the `frontend` directory and is built with React.js and Material-UI.

To run the frontend separately:
```
cd frontend
npm install
npm start
```

#### Backend Development
The backend code is located in the `backend` directory and is built with Python/Flask.

To run the backend separately:
```
cd backend
pip install -r requirements.txt
python app.py
```

## Project Structure

```
Refection/
├── backend/                # Flask backend
│   ├── app.py              # Main application file
│   ├── models/             # AI/ML models
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── public/             # Static files
│   └── src/                # React source code
│       ├── components/     # Reusable components
│       ├── context/        # Context providers
│       └── pages/          # Application pages
├── docker/                 # Docker configuration files
└── docker-compose.yml      # Docker Compose configuration
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Material-UI for the UI components
- MongoDB, Redis, and Kafka for the data infrastructure
- BERT and GPT models for AI capabilities
