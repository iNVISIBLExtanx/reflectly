#!/bin/bash

echo "🚀 Starting Reflectly AI - Emotional Pathfinding Demo"
echo "================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Make cleanup script executable
chmod +x cleanup-for-ai.sh

echo ""
echo "🧹 Running cleanup to remove big data components..."
./cleanup-for-ai.sh

echo ""
echo "🔧 Starting core AI services..."

# Stop any existing containers
docker-compose down

# Build and start services
docker-compose up -d --build

echo ""
echo "⏳ Waiting for services to be ready..."

# Wait for backend to be ready
echo "Checking backend health..."
for i in {1..30}; do
    if curl -s http://localhost:5002/health >/dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start. Check logs with: docker-compose logs backend"
        exit 1
    fi
    sleep 2
done

# Wait for frontend to be ready
echo "Checking frontend..."
for i in {1..20}; do
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        echo "✅ Frontend is ready!"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "⚠️  Frontend might still be starting. Check logs with: docker-compose logs frontend"
    fi
    sleep 3
done

echo ""
echo "🎉 Reflectly AI is now running!"
echo ""
echo "🌐 Access Points:"
echo "   Frontend (AI Demo): http://localhost:3000"
echo "   Backend API:        http://localhost:5002"
echo "   Health Check:       http://localhost:5002/health"
echo ""
echo "🧠 Core AI Features Available:"
echo "   ✅ A* Emotional Pathfinding"
echo "   ✅ Emotion Analysis from Text"
echo "   ✅ Interactive Graph Visualization"
echo "   ✅ Personalized Action Suggestions"
echo ""
echo "🔬 Test the AI API:"
echo ""
echo "1. Analyze emotion from text:"
echo "   curl -X POST http://localhost:5002/api/emotions/analyze \\"
echo "        -H 'Content-Type: application/json' \\"
echo "        -d '{\"text\": \"I feel excited about this new project!\", \"user_email\": \"demo@example.com\"}'"
echo ""
echo "2. Find optimal emotional path:"
echo "   curl -X POST http://localhost:5002/api/emotions/path \\"
echo "        -H 'Content-Type: application/json' \\"
echo "        -d '{\"user_email\": \"demo@example.com\", \"current_emotion\": \"sadness\", \"target_emotion\": \"joy\"}'"
echo ""
echo "3. Get graph visualization data:"
echo "   curl http://localhost:5002/api/emotions/graph-data/demo@example.com"
echo ""
echo "📊 To view logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose down"
echo ""
echo "🎯 Focus Areas:"
echo "   - A* search algorithm in backend/models/search_algorithm.py"
echo "   - Emotional graph theory in backend/models/emotional_graph.py"
echo "   - AI visualization in frontend/src/pages/EmotionalJourneyGraph.js"
echo ""
echo "Happy pathfinding! 🎯✨"
