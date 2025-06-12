#!/bin/bash

echo "🛑 Stopping Intelligent Agent services..."

# Find and kill processes on specific ports
kill_port() {
  local port=$1
  local pids=$(lsof -ti:$port 2>/dev/null)
  if [ -n "$pids" ]; then
    echo "⏹️ Stopping service on port $port (PID: $pids)"
    kill -9 $pids 2>/dev/null
  else
    echo "ℹ️ No service running on port $port"
  fi
}

# Kill backend and frontend
kill_port 5000
kill_port 5001  # Alternate port
kill_port 3000

echo "✅ All services stopped"
