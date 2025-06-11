#!/bin/bash

echo "🔍 Testing Intelligent Agent Backend"
echo "=================================="

# Check if backend is running
echo "1. Checking if backend is running..."
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ Backend is running on port 5000"
else
    echo "❌ Backend is NOT running on port 5000"
    echo "💡 Start it with: ./start-agent.sh or python backend/intelligent_agent.py"
    exit 1
fi

echo ""
echo "2. Testing health endpoint..."
curl -s http://localhost:5000/api/health | python -m json.tool

echo ""
echo ""
echo "3. Testing emotion analysis..."
curl -X POST http://localhost:5000/api/process-input \
  -H "Content-Type: application/json" \
  -d '{"text": "I am feeling really happy today!", "user_id": "test_user"}' \
  | python -m json.tool

echo ""
echo ""
echo "4. Testing memory map..."
curl -s http://localhost:5000/api/memory-map | python -m json.tool

echo ""
echo ""
echo "5. Testing memory stats..."
curl -s http://localhost:5000/api/memory-stats | python -m json.tool

echo ""
echo ""
echo "✅ Backend testing complete!"
echo "If you see JSON responses above, the backend is working correctly."
echo "If you see errors, check the backend logs for details."
