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

# Check what's using port 5000
echo "🔍 Checking port 5000..."
PORT_USER=$(lsof -ti:5000)
if [ ! -z "$PORT_USER" ]; then
    echo "⚠️  Port 5000 is in use by process: $PORT_USER"
    echo "🔧 Killing process on port 5000..."
    kill -9 $PORT_USER 2>/dev/null || true
    sleep 2
    
    # Check again
    if lsof -ti:5000 >/dev/null 2>&1; then
        echo "❌ Still can't free port 5000. Using port 5001 instead..."
        BACKEND_PORT=5001
    else
        echo "✅ Port 5000 is now free"
        BACKEND_PORT=5000
    fi
else
    echo "✅ Port 5000 is available"
    BACKEND_PORT=5000
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

# Modify the Python file to use the correct port
echo "🔧 Setting backend port to $BACKEND_PORT..."
if [ "$BACKEND_PORT" != "5000" ]; then
    # Create a temporary file with the correct port
    echo "🔨 Creating temporary Python file with new port"
    cp intelligent_agent.py intelligent_agent_temp.py
    # Use perl for more reliable replacement
    perl -pi -e "s/port=5000/port=$BACKEND_PORT/g" intelligent_agent_temp.py
    
    # Verify the replacement worked
    if grep -q "port=$BACKEND_PORT" intelligent_agent_temp.py; then
        echo "✅ Port successfully changed to $BACKEND_PORT"
        PYTHON_FILE="intelligent_agent_temp.py"
    else
        echo "❌ Failed to change port. Using original file."
        PYTHON_FILE="intelligent_agent.py"
        echo "⚠️ Warning: App will try to use port 5000 which is in use!"
    fi
else
    PYTHON_FILE="intelligent_agent.py"
fi

echo "🚀 Starting backend on port $BACKEND_PORT..."
python3 $PYTHON_FILE &
BACKEND_PID=$!

# Schedule cleanup of temp file on script exit
cleanup_temp() {
    if [ -f "backend/intelligent_agent_temp.py" ]; then
        rm backend/intelligent_agent_temp.py 2>/dev/null || true
    fi
}
trap cleanup_temp EXIT

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