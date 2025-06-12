#!/bin/bash

echo "🤖 Intelligent Agent - Fixed Startup"
echo "===================================="

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
    echo "❌ Python3 not found"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found"
    exit 1
fi

echo "✅ Python3: $(python3 --version)"
echo "✅ Node.js: $(node --version)"
echo ""

# On macOS, port 5000 is often used by AirPlay Receiver / Control Center
# Default to port 5001 to avoid conflicts
BACKEND_PORT=5001
echo "🔍 Using port $BACKEND_PORT for backend..."

# Check if port 5001 is available
PORT_USER=$(lsof -ti:$BACKEND_PORT)
if [ ! -z "$PORT_USER" ]; then
    echo "⚠️  Port $BACKEND_PORT is in use by process: $PORT_USER"
    echo "🔧 Killing process on port $BACKEND_PORT..."
    kill -9 $PORT_USER 2>/dev/null || true
    sleep 2
    
    # Check again
    if lsof -ti:$BACKEND_PORT >/dev/null 2>&1; then
        echo "❌ Still can't free port $BACKEND_PORT. Using port 5002 instead..."
        BACKEND_PORT=5002
    else
        echo "✅ Port $BACKEND_PORT is now free"
    fi
else
    echo "✅ Port $BACKEND_PORT is available"
fi

# Kill anything on port 3000
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 1

echo ""
echo "🔧 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "📥 Installing Flask and Flask-CORS..."
pip install Flask Flask-CORS --quiet

# Use environment variable for port configuration
echo "🔧 Setting backend port to $BACKEND_PORT..."
echo "🚀 Starting backend on port $BACKEND_PORT..."
PORT=$BACKEND_PORT python3 intelligent_agent.py &
BACKEND_PID=$!

cd ..

# Wait and test backend
echo "⏳ Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:$BACKEND_PORT/api/health >/dev/null 2>&1; then
        echo "✅ Backend running on port $BACKEND_PORT"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    sleep 1
done

# Update frontend to use correct backend port
echo ""
echo "🔧 Setting up frontend..."
cd frontend

# Update package.json proxy if using different port
if [ "$BACKEND_PORT" != "5000" ]; then
    echo "🔧 Updating frontend to use port $BACKEND_PORT..."
    # Create a temporary package.json with correct proxy
    jq ".proxy = \"http://localhost:$BACKEND_PORT\"" package.json > package_temp.json
    mv package_temp.json package.json
fi

if [ ! -d "node_modules" ]; then
    echo "📦 Installing React dependencies..."
    npm install --silent
fi

echo "🚀 Starting frontend..."
BROWSER=none npm start &
FRONTEND_PID=$!
cd ..

sleep 8

echo ""
echo "🎉 SUCCESS! Intelligent Agent is running!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "📡 Backend:  http://localhost:$BACKEND_PORT"
echo ""
echo "🔍 Test backend:"
echo "curl http://localhost:$BACKEND_PORT/api/health"
echo ""
echo "🤖 Usage:"
echo "   😊 Happy input → Agent asks for steps → Learns"
echo "   😢 Sad input → Agent suggests actions → A* search"
echo ""
echo "💡 Press Ctrl+C to stop both services"
echo ""

# Keep running
wait $BACKEND_PID $FRONTEND_PID