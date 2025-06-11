#!/bin/bash

echo "🤖 Starting Intelligent Agent with Memory Map"
echo "============================================"
echo "🧠 Features: Learning + A* Search + Memory Evolution"
echo ""

# Make scripts executable
chmod +x start-agent.sh

# Check requirements
echo "🔍 Checking requirements..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.7+ first."
    exit 1
fi
echo "✅ Python3: $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi
echo "✅ Node.js: $(node --version)"

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
pip install Flask Flask-CORS

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
echo "🎯 Starting Intelligent Agent..."
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
echo "🤖 Starting Intelligent Agent Backend..."
cd backend
source venv/bin/activate
python intelligent_agent.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "🗺️  Starting Memory Map Frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 Intelligent Agent is now running!"
echo ""
echo "🌐 Access Points:"
echo "   Frontend (Memory Map): http://localhost:3000"
echo "   Backend API:           http://localhost:5000"
echo ""
echo "🤖 How it works:"
echo "   😊 Share happy emotions → Agent asks for steps → Learns for future"
echo "   😢 Share sad emotions → Agent suggests actions using A* search"
echo "   🗺️  Memory map grows and evolves with each interaction"
echo ""
echo "🔬 Try these examples:"
echo "   • 'I'm feeling really happy and excited today!'"
echo "   • 'I'm sad and don't know what to do'"
echo "   • 'I'm anxious about my presentation tomorrow'"
echo ""
echo "💡 Press Ctrl+C to stop both services"

# Wait for background processes
wait $BACKEND_PID $FRONTEND_PID
