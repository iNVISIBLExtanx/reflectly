#!/bin/bash

echo "🤖 Enhanced Reflectly AI with IEMOCAP Integration"
echo "================================================="

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
    echo "❌ Python3 not found. Install Python 3.8+ first."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Install Node.js 16+ first."
    exit 1
fi

echo "✅ Python3: $(python3 --version)"
echo "✅ Node.js: $(node --version)"
echo ""

# Backend port (avoid macOS AirPlay port 5000)
BACKEND_PORT=5001
echo "🔍 Using port $BACKEND_PORT for backend..."

# Kill existing processes
lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 2

# Setup backend
echo "🔧 Setting up enhanced backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "📥 Installing enhanced dependencies..."
pip install -r requirements.txt --quiet

# Download NLTK data
python3 -c "
import nltk
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
    print('✅ NLTK data downloaded')
except Exception as e:
    print(f'⚠️ NLTK download warning: {e}')
"

# Generate synthetic IEMOCAP data if not exists
if [ ! -f "../data/iemocap_validation_data.json" ]; then
    echo "📊 Generating synthetic IEMOCAP data for testing..."
    mkdir -p ../data
    python3 -c "
from iemocap_loader import IEMOCAPDatasetLoader
import json
import os

loader = IEMOCAPDatasetLoader('.')
synthetic_data = loader.generate_synthetic_iemocap_data()

os.makedirs('../data', exist_ok=True)
with open('../data/iemocap_validation_data.json', 'w') as f:
    json.dump(synthetic_data, f, indent=2)

print('✅ Synthetic IEMOCAP data generated')
"
fi

# Start backend
echo "🚀 Starting enhanced backend on port $BACKEND_PORT..."
export PORT=$BACKEND_PORT
python3 intelligent_agent.py &
BACKEND_PID=$!
cd ..

# Wait for backend
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

# Setup frontend
echo "🔧 Setting up enhanced frontend..."
cd frontend

# Update package.json proxy
if command -v jq &> /dev/null; then
    jq ".proxy = \"http://localhost:$BACKEND_PORT\"" package.json > package_temp.json
    mv package_temp.json package.json
fi

if [ ! -d "node_modules" ]; then
    echo "📦 Installing React dependencies..."
    npm install --silent
fi

# Start frontend
echo "🚀 Starting enhanced frontend..."
BROWSER=none npm start &
FRONTEND_PID=$!
cd ..

sleep 8

echo ""
echo "🎉 ENHANCED REFLECTLY AI IS RUNNING!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "📡 Backend:  http://localhost:$BACKEND_PORT"
echo ""
echo "🧠 Enhanced Features:"
echo "   ✅ ML-based Emotion Recognition"
echo "   ✅ IEMOCAP Dataset Integration"
echo "   ✅ Algorithm Performance Validation"
echo "   ✅ Comprehensive Analytics"
echo ""
echo "🔬 Quick Start:"
echo "   1. Open http://localhost:3000"
echo "   2. Go to 'IEMOCAP Integration' tab"
echo "   3. Load: data/iemocap_validation_data.json"
echo "   4. Run validation tests"
echo ""
echo "🧪 Run comprehensive tests:"
echo "   python3 comprehensive_test_script.py --backend-url http://localhost:$BACKEND_PORT"
echo ""
echo "💡 Press Ctrl+C to stop all services"

# Keep running
wait $BACKEND_PID $FRONTEND_PID
