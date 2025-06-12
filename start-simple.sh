#!/bin/bash

echo "🚀 Simple Reflectly AI - Algorithm Development Setup"
echo "=================================================="
echo "🎯 Focus: Pure Algorithm Development"
echo "🏗️  Architecture: Python Flask + React (No Docker, No Database)"
echo ""

# Make scripts executable
chmod +x start-backend.sh
chmod +x start-frontend.sh

# Check requirements
echo "🔍 Checking requirements..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.7+ first."
    echo "   Download from: https://www.python.org/downloads/"
    exit 1
fi
echo "✅ Python3: $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    echo "   Download from: https://nodejs.org/"
    exit 1
fi
echo "✅ Node.js: $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi
echo "✅ npm: $(npm --version)"

echo ""
echo "🔧 Setting up backend..."

# Setup backend
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install requirements
echo "📥 Installing backend dependencies..."
source venv/bin/activate
pip install -r simple_requirements.txt

cd ..

echo ""
echo "🔧 Setting up frontend..."

# Setup frontend
cd frontend

# Install npm dependencies
if [ ! -d "node_modules" ]; then
    echo "📦 Installing React dependencies..."
    npm install
else
    echo "✅ React dependencies already installed"
fi

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Starting both backend and frontend..."
echo ""

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup INT

# Start backend in background
echo "🐍 Starting Python backend..."
cd backend
source venv/bin/activate
python simple_app.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "⚛️  Starting React frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 Simple Reflectly AI is now running!"
echo ""
echo "🌐 Access Points:"
echo "   Frontend (AI Demo): http://localhost:3000"
echo "   Backend API:        http://localhost:5000"
echo "   Algorithm Test:     http://localhost:5000/api/test-algorithm"
echo ""
echo "🧠 Core Features:"
echo "   ✅ A* Emotional Pathfinding"
echo "   ✅ Simple Emotion Analysis"
echo "   ✅ Interactive Visualization"
echo "   ✅ Real-time Algorithm Testing"
echo ""
echo "📁 Key Files for Development:"
echo "   🔬 backend/simple_app.py           - Main AI algorithms"
echo "   🎨 frontend/src/SimpleAIDemo.js    - React interface"
echo "   📊 AStarPathfinder class           - A* implementation"
echo "   🧮 SimpleEmotionAnalyzer class     - Emotion detection"
echo ""
echo "🔬 Quick API Tests:"
echo ""
echo "# Test emotion analysis:"
echo "curl -X POST http://localhost:5000/api/emotions/analyze \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"text\": \"I feel excited about this!\", \"user_email\": \"demo@example.com\"}'"
echo ""
echo "# Test pathfinding:"
echo "curl -X POST http://localhost:5000/api/emotions/path \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"current_emotion\": \"sadness\", \"target_emotion\": \"joy\"}'"
echo ""
echo "# Test algorithm:"
echo "curl http://localhost:5000/api/test-algorithm"
echo ""
echo "💡 Press Ctrl+C to stop both services"
echo "🔄 Both services will restart automatically on file changes"

# Wait for background processes
wait $BACKEND_PID $FRONTEND_PID
