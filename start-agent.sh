#!/bin/bash

echo "🤖 Starting Intelligent Agent Backend"
echo "===================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

echo "✅ Python3 is available"

# Navigate to backend directory
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing requirements..."
pip install Flask Flask-CORS

echo ""
echo "🚀 Starting Intelligent Agent Backend..."
echo "📡 Backend will be available at: http://localhost:5000"
echo "🧠 Features: Memory Learning + A* Search + Emotion Analysis"
echo ""
echo "💡 To stop: Press Ctrl+C"
echo ""

# Start the intelligent agent
python intelligent_agent.py
