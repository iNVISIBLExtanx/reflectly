#!/bin/bash

echo "🤖 Intelligent Agent - Debug Startup"
echo "===================================="

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

# Kill existing processes
echo "🧹 Killing processes on ports 3000 and 5000..."
lsof -ti:5000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 2

# Setup backend with full output
echo "🔧 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "📥 Installing dependencies..."
pip install Flask Flask-CORS

echo ""
echo "🔍 Checking if intelligent_agent.py exists..."
if [ ! -f "intelligent_agent.py" ]; then
    echo "❌ intelligent_agent.py not found in backend directory!"
    echo "📁 Files in backend/:"
    ls -la
    exit 1
fi

echo "✅ intelligent_agent.py found"
echo ""

echo "🚀 Starting backend (showing all output)..."
echo "📡 Backend should start on http://localhost:5000"
echo "---"

# Start backend and show output
python3 intelligent_agent.py &
BACKEND_PID=$!

# Wait a bit and check if process is still running
sleep 5

if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo ""
    echo "❌ Backend process died! Check for Python errors above."
    exit 1
fi

echo ""
echo "🔍 Testing backend connection..."

# Test connection with more verbose output
for i in {1..10}; do
    echo "Attempt $i: Testing http://localhost:5000/api/health"
    
    RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}\n" http://localhost:5000/api/health)
    
    if echo "$RESPONSE" | grep -q "healthy"; then
        echo "✅ Backend is responding correctly!"
        echo "Response: $RESPONSE"
        break
    else
        echo "❌ No response or invalid response"
        echo "Full response: '$RESPONSE'"
        
        if [ $i -eq 10 ]; then
            echo ""
            echo "❌ Backend failed to respond after 10 attempts"
            echo ""
            echo "🔍 Let's check what's running on port 5000:"
            lsof -i :5000 || echo "Nothing running on port 5000"
            
            echo ""
            echo "🔍 Backend process status:"
            if kill -0 $BACKEND_PID 2>/dev/null; then
                echo "Backend process is still running (PID: $BACKEND_PID)"
            else
                echo "Backend process has died"
            fi
            
            echo ""
            echo "🔍 Let's try to see what the backend is doing:"
            echo "Backend working directory: $(pwd)"
            echo "Python path: $(which python3)"
            
            kill $BACKEND_PID 2>/dev/null
            exit 1
        fi
    fi
    
    sleep 2
done

echo ""
echo "✅ Backend is working! Continuing with frontend..."

cd ..

# Setup frontend
echo "🔧 Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Installing React dependencies..."
    npm install
fi

echo "🚀 Starting frontend..."
BROWSER=none npm start &
FRONTEND_PID=$!

cd ..

sleep 5

echo ""
echo "🎉 Both services should be running now!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "📡 Backend:  http://localhost:5000"
echo ""
echo "🔍 Quick test command:"
echo "curl http://localhost:5000/api/health"
echo ""

# Keep running
echo "💡 Press Ctrl+C to stop both services"
wait $BACKEND_PID $FRONTEND_PID