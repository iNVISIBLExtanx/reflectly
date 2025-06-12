#!/bin/bash

echo "🤖 Intelligent Agent - Single Startup Script"
echo "============================================"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}
trap cleanup INT

# Check requirements
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Install Python 3.7+ first."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Install Node.js 16+ first."
    exit 1
fi

echo "✅ Python3: $(python3 --version)"
echo "✅ Node.js: $(node --version)"
echo ""

# Kill any existing processes on these ports
echo "🧹 Cleaning up existing processes..."
lsof -ti:5000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 2

# Setup backend
echo "🔧 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "📥 Installing Flask and Flask-CORS..."
pip install Flask Flask-CORS --quiet

# Start backend
echo "🚀 Starting backend..."
python3 intelligent_agent.py &
BACKEND_PID=$!
cd ..

# Wait and test backend
echo "⏳ Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:5000/api/health >/dev/null 2>&1; then
        echo "✅ Backend running on port 5000"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start after 30 seconds"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    sleep 1
done

# Test backend API specifically
echo "🔍 Testing backend API..."
HEALTH_RESPONSE=$(curl -s http://localhost:5000/api/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✅ Backend API responding correctly"
else
    echo "❌ Backend API not responding properly"
    echo "Response: $HEALTH_RESPONSE"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Setup frontend
echo ""
echo "🔧 Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Installing React dependencies..."
    npm install --silent
fi

# Start frontend
echo "🚀 Starting frontend..."
BROWSER=none npm start &
FRONTEND_PID=$!
cd ..

# Wait for frontend
echo "⏳ Waiting for frontend to start..."
sleep 8

echo ""
echo "🎉 SUCCESS! Intelligent Agent is running!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "📡 Backend:  http://localhost:5000"
echo ""
echo "🔍 Quick test:"
echo "curl http://localhost:5000/api/health"
echo ""
echo "🤖 Usage:"
echo "   😊 Happy input → Agent asks for steps → Learns"
echo "   😢 Sad input → Agent suggests actions → Uses A* search"
echo ""
echo "🧪 Try these inputs:"
echo "   'I feel amazing and excited today!'"
echo "   'I'm feeling sad and lost'"
echo ""
echo "💡 Press Ctrl+C to stop both services"
echo ""

# Keep running
wait $BACKEND_PID $FRONTEND_PID