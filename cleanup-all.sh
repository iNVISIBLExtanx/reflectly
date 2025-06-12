#!/bin/bash

echo "🧹 Cleaning up unnecessary files for simple AI-focused setup..."
echo "============================================================"

# Remove complex backend models (keep only simple_app.py)
echo "Removing complex backend models..."
rm -f backend/models/emotional_graph.py
rm -f backend/models/emotional_graph_bigdata.py
rm -f backend/models/emotion_analyzer.py
rm -f backend/models/memory_manager.py
rm -f backend/models/goal_tracker.py
rm -f backend/models/response_generator.py
rm -f backend/models/search_algorithm.py
rm -rf backend/models/

# Remove all services
echo "Removing backend services..."
rm -rf backend/services/

# Remove complex backend files
echo "Removing complex backend files..."
rm -f backend/app.py  # Keep only simple_app.py
rm -f backend/requirements.txt  # Keep only simple_requirements.txt
rm -f backend/user_management.py
rm -f backend/admin_viewer.py
rm -f backend/start_backend.sh
rm -f backend/Dockerfile

# Remove all Spark components
echo "Removing Spark components..."
rm -rf spark/
rm -f run_spark_jobs.sh
rm -f copy_spark_jobs.sh

# Remove complex frontend components (keep only SimpleAIDemo.js and App.js)
echo "Removing complex frontend components..."
rm -f frontend/src/pages/EmotionalJourneyGraph.js
rm -f frontend/src/pages/Goals.js
rm -f frontend/src/pages/Home.js
rm -f frontend/src/pages/Journal.js
rm -f frontend/src/pages/Login.js
rm -f frontend/src/pages/Memories.js
rm -f frontend/src/pages/NotFound.js
rm -f frontend/src/pages/Profile.js
rm -f frontend/src/pages/Register.js
rm -rf frontend/src/pages/

rm -rf frontend/src/components/
rm -rf frontend/src/context/
rm -rf frontend/src/utils/

# Remove Docker files
echo "Removing Docker configurations..."
rm -f backend/Dockerfile
rm -f frontend/Dockerfile

# Remove complex documentation
echo "Removing complex documentation..."
rm -f README_BIGDATA.md
rm -f docs/context.md
rm -f docs/contextV2.md
rm -f docs/contextV3.md
rm -f docs/technical_documentation_V2.md
rm -f docs/technical_documentation.md
rm -rf docs/

# Remove unnecessary scripts
echo "Removing unnecessary scripts..."
rm -f start_reflectly.sh
rm -f stop_reflectly.sh
rm -f start-ai-demo.sh
rm -f cleanup-for-ai.sh

# Remove repomix files
echo "Removing repomix files..."
rm -f repomix-output.md
rm -f .repomixignore
rm -f repomix.config.json

# Create a simple .gitignore for the simplified project
echo "Creating simple .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
.env
venv/
env/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.DS_Store

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log

# OS
Thumbs.db
EOF

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📁 Remaining files:"
echo "├── backend/"
echo "│   ├── simple_app.py           # 🧠 Complete AI backend"
echo "│   └── simple_requirements.txt # 📦 Minimal dependencies"
echo "├── frontend/"
echo "│   ├── src/"
echo "│   │   ├── SimpleAIDemo.js     # 🎨 Complete demo interface"
echo "│   │   ├── App.js              # ⚛️ Simple wrapper"
echo "│   │   └── index.js            # ⚛️ React entry point"
echo "│   └── package.json            # 📦 React dependencies"
echo "├── start-simple.sh             # 🚀 One-command startup"
echo "├── start-backend.sh            # 🐍 Backend only"
echo "├── start-frontend.sh           # ⚛️ Frontend only"
echo "└── README.md                   # 📖 Simple setup guide"
echo ""
echo "🎯 Ready for algorithm development!"
echo "🚀 Run: ./start-simple.sh"
