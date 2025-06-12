#!/bin/bash

# Cleanup script for AI-focused Reflectly
# Removes big data components and unnecessary files

echo "🧹 Cleaning up AI-focused Reflectly repository..."

# Remove big data services
echo "Removing big data services..."
rm -rf backend/services/

# Remove Spark jobs
echo "Removing Spark components..."
rm -rf spark/
rm -f run_spark_jobs.sh
rm -f copy_spark_jobs.sh

# Remove big data documentation
echo "Removing big data documentation..."
rm -f README_BIGDATA.md

# Remove big data models
echo "Removing big data models..."
rm -f backend/models/emotional_graph_bigdata.py

# Remove unused scripts
echo "Removing deployment scripts..."
rm -f start_reflectly.sh
rm -f stop_reflectly.sh

# Remove goal tracker (not AI-focused)
echo "Removing non-AI components..."
rm -f backend/models/goal_tracker.py

# Remove admin viewer (not essential for AI demo)
rm -f backend/admin_viewer.py
rm -f backend/user_management.py

# Remove Docker files for big data services
echo "Cleaning up Docker configurations..."
# Note: We've already replaced docker-compose.yml with simplified version

# Keep only essential Dockerfiles
echo "Keeping only essential Docker configurations..."

# Clean up frontend - remove non-AI pages
echo "Cleaning up frontend..."
rm -f frontend/src/pages/Goals.js
rm -f frontend/src/pages/Profile.js
rm -f frontend/src/pages/Memories.js

# Update gitignore for AI-focused development
echo "Updating .gitignore..."
cat >> .gitignore << EOF

# AI-focused development
*.pyc
__pycache__/
.pytest_cache/
*.log

# Node modules
node_modules/
npm-debug.log*

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/

# AI models (if downloaded locally)
models/
*.bin
*.safetensors

EOF

echo "✅ Cleanup complete!"
echo ""
echo "🎯 AI-focused Reflectly is ready!"
echo ""
echo "Core AI components kept:"
echo "  ✅ A* search algorithm (backend/models/search_algorithm.py)"
echo "  ✅ Emotional graph (backend/models/emotional_graph.py)"
echo "  ✅ Emotion analyzer (backend/models/emotion_analyzer.py)"
echo "  ✅ Memory manager (backend/models/memory_manager.py)"
echo "  ✅ AI-focused Flask API (backend/app.py)"
echo "  ✅ Emotional journey visualization (frontend/src/pages/EmotionalJourneyGraph.js)"
echo ""
echo "Removed components:"
echo "  ❌ Kafka streaming service"
echo "  ❌ Spark distributed computing"
echo "  ❌ HDFS storage service"
echo "  ❌ Big data orchestration"
echo "  ❌ Goal tracking system"
echo "  ❌ User management complexity"
echo ""
echo "🚀 Next steps:"
echo "  1. Run: docker-compose up -d"
echo "  2. Open: http://localhost:3000"
echo "  3. Test AI pathfinding endpoints"
