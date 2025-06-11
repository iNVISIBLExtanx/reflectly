# Reflectly AI - Emotional Pathfinding & Visualization

> **AI-Focused Version**: This branch contains only the core AI functionality for emotional analysis, pathfinding algorithms, and frontend visualization - streamlined without big data dependencies.

## 🧠 Core AI Features

### **Emotional Analysis Engine**
- Advanced emotion detection from text using transformers
- Support for 7 core emotions: joy, sadness, anger, fear, disgust, surprise, neutral
- Real-time emotional state classification

### **A* Pathfinding Algorithm**
- **Innovative AI**: Uses A* search algorithm to find optimal paths between emotional states
- Personalized heuristics based on user's emotional transition history
- Cost-based optimization for emotional journey planning

### **Emotional Graph Mapping**
- Graph-based representation of emotional transitions
- Weighted edges based on transition success rates
- Personalized action recommendations

### **Visual Analytics**
- Interactive emotional journey graphs
- Real-time path visualization
- Historical emotion tracking

## 🏗️ Simplified Architecture

```
├── frontend/                    # React.js visualization layer
│   ├── src/pages/EmotionalJourneyGraph.js  # Main AI visualization
│   └── src/components/         # UI components
├── backend/                     # Flask API for AI services
│   ├── models/
│   │   ├── search_algorithm.py # A* pathfinding implementation
│   │   ├── emotional_graph.py  # Core graph operations
│   │   └── emotion_analyzer.py # AI emotion detection
│   └── app.py                  # Simplified AI-focused API
└── docker-compose.yml          # Core services only
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 16+ (for local frontend development)
- Python 3.9+ (for local backend development)

### Option 1: Docker (Recommended)
```bash
# Clone and switch to AI-focused branch
git clone https://github.com/iNVISIBLExtanx/reflectly.git
cd reflectly
git checkout ai-frontend-focused

# Start core services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:5002
```

### Option 2: Local Development
```bash
# Backend setup
cd backend
pip install -r requirements.txt
python app.py

# Frontend setup (in new terminal)
cd frontend
npm install
npm start
```

## 🔧 API Endpoints (AI-Focused)

### **Emotion Analysis**
```http
POST /api/emotions/analyze
Content-Type: application/json

{
  "text": "I'm feeling really excited about this new project!",
  "user_email": "user@example.com"
}
```

### **Pathfinding (Core AI Feature)**
```http
POST /api/emotions/path
Content-Type: application/json

{
  "user_email": "user@example.com",
  "current_emotion": "sadness",
  "target_emotion": "joy",
  "max_depth": 10
}
```

### **Graph Visualization Data**
```http
GET /api/emotions/graph-data/{user_email}
```

### **Action Suggestions**
```http
POST /api/emotions/suggestions
Content-Type: application/json

{
  "user_email": "user@example.com",
  "current_emotion": "anger"
}
```

## 🧮 AI Algorithm Details

### **A* Search Implementation**
- **Heuristic Function**: Custom emotional distance calculation
- **Cost Function**: Based on historical transition success rates
- **Optimization**: Personalized pathfinding using user's emotional patterns
- **Graph Traversal**: Efficient exploration of emotional state space

### **Emotion Classification**
- **Model**: Transformer-based emotion detection
- **Input**: Natural language text (journal entries, messages)
- **Output**: Emotion probabilities + primary emotion classification
- **Accuracy**: Optimized for 7-emotion classification

### **Graph Theory Application**
- **Nodes**: Emotional states (joy, sadness, anger, etc.)
- **Edges**: Possible transitions with weights
- **Weights**: Success probability + user history
- **Algorithms**: A*, Dijkstra's shortest path, graph clustering

## 🎯 Use Cases

1. **Emotional Journey Planning**: Find optimal paths from negative to positive emotions
2. **Therapeutic Insights**: Visualize emotional patterns over time
3. **Personalized Recommendations**: AI-driven action suggestions
4. **Mental Health Research**: Graph-based emotional transition analysis

## 📊 Frontend Features

### **Interactive Emotional Graph**
- Real-time visualization of emotional transitions
- Clickable nodes and edges
- Path highlighting for optimal routes
- Historical data overlay

### **AI Search Interface**
- Input current and target emotions
- Display optimal path with steps
- Show success probability
- Provide actionable recommendations

## 🔬 Technical Details

### **Core Dependencies**
- **Backend**: Flask, PyMongo, Transformers, PyTorch, scikit-learn
- **Frontend**: React.js, D3.js/Chart.js for visualizations
- **Database**: MongoDB (lightweight, no big data cluster)
- **AI/ML**: Hugging Face Transformers, NLTK, TextBlob

### **Removed from Original**
- ❌ Apache Kafka streaming
- ❌ Apache Spark distributed computing  
- ❌ Hadoop HDFS storage
- ❌ Complex big data orchestration
- ❌ Enterprise authentication systems

### **What's Kept**
- ✅ A* pathfinding algorithm (core innovation)
- ✅ Emotional graph theory implementation
- ✅ AI emotion analysis
- ✅ Interactive frontend visualization
- ✅ MongoDB for data persistence
- ✅ REST API for AI services

## 🧪 Testing AI Features

### Test Emotional Pathfinding
```bash
curl -X POST http://localhost:5002/api/emotions/path \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "test@example.com",
    "current_emotion": "sadness", 
    "target_emotion": "joy",
    "max_depth": 5
  }'
```

### Test Emotion Analysis
```bash
curl -X POST http://localhost:5002/api/emotions/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I am feeling overwhelmed and anxious about work",
    "user_email": "test@example.com"
  }'
```

## 🎨 Frontend AI Visualization

The EmotionalJourneyGraph component provides:
- **Node-edge graph** of emotional states
- **Path highlighting** for A* search results  
- **Interactive exploration** of emotional transitions
- **Real-time updates** as new emotional data is analyzed

## 🛠️ Development & Customization

### Modify AI Algorithm
- Edit `backend/models/search_algorithm.py` for A* customization
- Adjust heuristic functions in the `AStarSearch` class
- Modify cost calculations for different optimization goals

### Customize Emotions
- Update emotion lists in `emotional_graph.py`
- Retrain emotion classification model
- Adjust graph visualization in frontend

### Extend Visualizations  
- Add new chart types in `EmotionalJourneyGraph.js`
- Implement 3D graph visualizations
- Create dashboard views for emotional analytics

## 📈 Performance

- **Lightweight**: Runs on single machine (no cluster required)
- **Fast**: A* pathfinding completes in milliseconds
- **Scalable**: MongoDB handles thousands of emotional transitions
- **Responsive**: Real-time emotion analysis and visualization

## 🔮 Future AI Enhancements

- **Deep Learning**: Train custom emotion models on user data
- **Reinforcement Learning**: Optimize pathfinding based on user feedback
- **Graph Neural Networks**: Advanced pattern recognition in emotional graphs
- **Predictive Analytics**: Forecast emotional states using historical patterns

---

**This AI-focused version demonstrates the core innovation of Reflectly: applying computer science algorithms to emotional intelligence and mental health.**
