#!/bin/bash

echo "⚛️  Starting Simple React Frontend for Algorithm Development"
echo "=========================================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Node.js and npm are available"

# Navigate to frontend directory
cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing React dependencies..."
    npm install
else
    echo "✅ Dependencies already installed"
fi

echo ""
echo "🚀 Starting React development server..."
echo "🌐 Frontend will be available at: http://localhost:3000"
echo "🔗 Make sure backend is running at: http://localhost:5000"
echo ""
echo "💡 To stop: Press Ctrl+C"
echo ""

# Start the React development server
npm start
