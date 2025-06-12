#!/bin/bash

echo "🧹 Cleaning up redundant script files..."

# Create a backup directory just in case
mkdir -p .script_backups

# Scripts to keep
KEEP=(
  "start_fixed.sh"  # Main startup script (renamed version)
  "stop.sh"         # Will create this as a cleaner version of stop_reflectly
  "cleanup.sh"      # Main cleanup script
)

# Backup and remove redundant scripts
backup_and_remove() {
  if [ -f "$1" ]; then
    echo "📦 Backing up $1 to .script_backups/"
    cp "$1" ".script_backups/"
    echo "🗑️ Removing redundant script: $1"
    rm "$1"
  fi
}

# Backup and remove all *.sh files except those in KEEP
for script in *.sh; do
  if [[ ! " ${KEEP[@]} " =~ " ${script} " ]]; then
    backup_and_remove "$script"
  fi
done

# Create a cleaner stop script (if it doesn't exist)
if [ ! -f "stop.sh" ]; then
  echo "📝 Creating a clean stop.sh script"
  cat > stop.sh << 'EOF'
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
EOF

  chmod +x stop.sh
fi

# Rename main script
if [ -f "start_fixed.sh" ]; then
  echo "🔄 Renaming start_fixed.sh to start.sh for simplicity"
  mv start_fixed.sh start.sh
fi

echo "✅ Cleanup complete!"
echo "The following scripts are now available:"
echo "  - start.sh     (Start the Intelligent Agent)"
echo "  - stop.sh      (Stop all services)"
echo "  - cleanup.sh   (Clean up application data)"
echo ""
echo "Original scripts are backed up in the .script_backups directory."
